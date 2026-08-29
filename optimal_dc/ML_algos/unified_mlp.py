"""Unified single-agent MLP baseline (PPO), wrapped for the ML_algos registry.

Baseline 3 of 3: one network sees the full concatenated 34-dim state and emits
both the CDU continuous actions (25 = 5 cabinets x [Tsec, dp, v1, v2, v3]) and
the CT discrete action (9). The agent itself is the June-2026 Unified_PPO in
optimal_dc/unified_mlp_baseline.py (the one sent to Cliff) -- this module only
adapts it to the BaseAlgorithm learn/evaluate/checkpoint contract so
`benchmarks train --algo unified_mlp` works, incl. the synthetic day sampler.

The training loop is a faithful port of train_unified_mlp.py: same episode
structure, update cadence, action-std decay, best-reward checkpointing, and
the same upstream hyperparameter defaults (overridable via the config YAML).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# unified_mlp_baseline.py sits in optimal_dc/ and itself imports from the
# sustain-lc submodule (RolloutBuffer from ca_ppo), so both need to be on path.
_OPTIMAL_DC = Path(__file__).resolve().parents[1]
for _p in (str(_OPTIMAL_DC.parent), str(_OPTIMAL_DC), str(_OPTIMAL_DC / "external" / "sustain-lc")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from unified_mlp_baseline import Unified_PPO  # noqa: E402

from optimal_dc.ML_algos.base_algorithm import BaseAlgorithm  # noqa: E402

CABINET_KEYS = [f"cdu-cabinet-{k}" for k in range(1, 6)]
CT_KEY = "cooling-tower-1"

# upstream train_unified_mlp.py values; config YAML keys of the same name override
UNIFIED_DEFAULTS = dict(
    max_ep_len=200,
    K_epochs=50,
    eps_clip=0.2,
    gamma=0.80,
    lr_cdu_actor=3.0e-4,
    lr_ct_actor=3.0e-4,
    lr_critic=1.0e-3,
    action_std_init=0.6,
    action_std_decay_rate=0.05,
    action_std_decay_freq=int(2.5e5),
    min_action_std=0.1,
    save_model_freq=2000,
)


def flatten_state(state_dict) -> np.ndarray:
    """All component observations -> one 34-dim vector (train_unified_mlp.py)."""
    return np.concatenate([state_dict[k] for k in CABINET_KEYS] + [state_dict[CT_KEY]])


def env_action(cdu_action: np.ndarray, ct_action: int) -> dict:
    """(5,5) CDU array + CT int -> the env's per-component action dict
    (train_unified_mlp.py's categorize_actions, flattened)."""
    out = {k: cdu_action[i] for i, k in enumerate(CABINET_KEYS)}
    out[CT_KEY] = ct_action
    return out


class Unified_MLP(BaseAlgorithm):
    """Unified single-agent MLP PPO on SmallFrontierModel(_v3)."""

    ALGO_NAME = "Unified_MLP"
    ENV_NAME = "SmallFrontierModel"

    def __init__(self, config: dict, env):
        super().__init__(config, env)
        self.hp = {k: config.get(k, v) for k, v in UNIFIED_DEFAULTS.items()}
        self.max_ep_len = int(self.hp["max_ep_len"])
        # upstream: update every 1 x ep_len steps
        self.update_timestep = int(config.get("update_timestep", self.max_ep_len))
        self.agent = Unified_PPO(
            state_dim=34, cdu_action_dim=25, ct_action_dim=9,
            num_centralized_actions=1,
            lr_cdu_actor=self.hp["lr_cdu_actor"],
            lr_ct_actor=self.hp["lr_ct_actor"],
            lr_critic=self.hp["lr_critic"],
            gamma=self.hp["gamma"],
            K_epochs=self.hp["K_epochs"],
            eps_clip=self.hp["eps_clip"],
            cdu_action_std_init=self.hp["action_std_init"],
        )

    # ------------------------------------------------------------- inference
    def predict(self, obs: dict, deterministic: bool = False) -> dict:
        """Action for one observation dict. select_action() also pushes to the
        rollout buffers; outside learn() that is pollution, so clear them."""
        cdu, ct = self.agent.select_action(flatten_state(obs))
        for buf in self.agent.buffer_dict.values():
            buf.clear()
        return env_action(cdu, ct)

    # -------------------------------------------------------------- training
    def learn(self, env, n_steps: int, eval_env=None, eval_interval: int = None) -> dict:
        hp = self.hp
        best_reward = float("-inf")
        running_reward = {"CDUCAB": 0.0, "CT": 0.0}
        running_episodes = 0
        save_freq = int(hp["save_model_freq"])
        time_step = 0
        i_episode = 0

        self.logger.info(
            f"[{self.ALGO_NAME}] training for {n_steps} steps "
            f"(ep_len={self.max_ep_len}, update every {self.update_timestep}, "
            f"K={hp['K_epochs']}, gamma={hp['gamma']}, clip={hp['eps_clip']})")

        while time_step <= n_steps:
            state = env.reset()
            flat = flatten_state(state)
            ep_reward = {"CDUCAB": 0.0, "CT": 0.0}

            for _ in range(self.max_ep_len):
                cdu, ct = self.agent.select_action(flat)
                state, rewards, done, _info = env.step(env_action(cdu, ct))
                flat = flatten_state(state)

                # bootstrap state for the non-terminating env's advantage calc
                self.agent.next_state = flat

                r_cdu = sum(rewards[k] for k in CABINET_KEYS) / 5.0
                r_ct = rewards[CT_KEY]
                self.agent.buffer_dict["cdu_action"].rewards.append(r_cdu)
                self.agent.buffer_dict["cdu_action"].is_terminals.append(done[CABINET_KEYS[0]])
                self.agent.buffer_dict["ct_action"].rewards.append(r_ct)
                self.agent.buffer_dict["ct_action"].is_terminals.append(done[CT_KEY])
                ep_reward["CDUCAB"] += r_cdu
                ep_reward["CT"] += r_ct
                time_step += 1

                if time_step % self.update_timestep == 0:
                    loss = float(self.agent.update())
                    self.log_training_step(time_step, {"loss": loss})

                if time_step % hp["action_std_decay_freq"] == 0:
                    self.agent.decay_action_std(
                        hp["action_std_decay_rate"], hp["min_action_std"])

                if time_step % save_freq == 0 and hasattr(self, "checkpoint_dir"):
                    if running_episodes:
                        avg = running_reward["CDUCAB"] / running_episodes
                        if avg > best_reward:
                            best_reward = avg
                            self.agent.save(str(self.checkpoint_dir / "best_unified.pth"))

                if time_step > n_steps:
                    break

            running_reward["CDUCAB"] += ep_reward["CDUCAB"]
            running_reward["CT"] += ep_reward["CT"]
            running_episodes += 1
            i_episode += 1
            self.total_episodes = i_episode
            self.total_timesteps = time_step
            self.log_training_step(time_step, {
                "episode": i_episode,
                "ep_reward_CDUCAB": ep_reward["CDUCAB"],
                "ep_reward_CT": ep_reward["CT"]})

        self.logger.info(f"[{self.ALGO_NAME}] done: {time_step} steps, {i_episode} episodes")
        return {"log": self.train_log}

    # ------------------------------------------------------------ evaluation
    def evaluate(self, eval_env, n_episodes: int = 5, deterministic: bool = True,
                 max_steps: int = None) -> dict:
        """Reward-summary evaluation, mirroring the sustainlc baselines.
        NOTE: every reset() re-triggers the FMU init transient; energy-metric
        scoring belongs to validation/rollout.py, not here."""
        max_steps = max_steps or self.max_ep_len
        totals = {"CDUCAB": [], "CT": []}
        for _ in range(n_episodes):
            obs = eval_env.reset()
            ep = {"CDUCAB": 0.0, "CT": 0.0}
            for _ in range(max_steps):
                obs, rewards, _done, _info = eval_env.step(self.predict(obs, deterministic))
                ep["CDUCAB"] += sum(rewards[k] for k in CABINET_KEYS) / 5.0
                ep["CT"] += rewards[CT_KEY]
            totals["CDUCAB"].append(ep["CDUCAB"])
            totals["CT"].append(ep["CT"])
        return {
            "n_episodes": n_episodes,
            "ep_len": max_steps,
            "mean_ep_reward_CDUCAB": float(np.mean(totals["CDUCAB"])),
            "mean_ep_reward_CT": float(np.mean(totals["CT"])),
            "std_ep_reward_CDUCAB": float(np.std(totals["CDUCAB"])),
            "std_ep_reward_CT": float(np.std(totals["CT"])),
        }

    # ---------------------------------------------------------- checkpointing
    def save_checkpoint(self, name: str) -> Path:
        path = self.checkpoint_dir / f"{name}_unified.pth"
        self.agent.save(str(path))
        self.logger.info(f"Saved {self.ALGO_NAME} checkpoint: {path}")
        return path

    def load_checkpoint(self, path: str | Path) -> None:
        self.agent.load(str(path))

    def load_sustainlc_pretrained(self, run_num_pretrained: int, seed: int = 123) -> None:
        """Load a checkpoint from the June-2026 Unified_MLP_preTrained lineage
        (e.g. Cliff's cluster run). NOTE: those weights were trained on the /15
        v2-processed trace -- comparable only within that regime."""
        path = (_OPTIMAL_DC / "Unified_MLP_preTrained" / "SmallFrontierModel"
                / f"PPO_SmallFrontierModel_{seed}_{run_num_pretrained}_unified.pth")
        self.agent.load(str(path))
        self.logger.info(f"Loaded pretrained (/15-regime) unified MLP: {path}")
