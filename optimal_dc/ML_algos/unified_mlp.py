"""Unified single-agent MLP baseline (PPO), wrapped for the ML_algos registry.

Baseline 3 of 3: one network sees the full concatenated 34-dim state and emits
both the CDU continuous actions (25 = 5 cabinets x [Tsec, dp, v1, v2, v3]) and
the CT discrete action (9). The agent itself is the June-2026 Unified_PPO in
ML_algos/unified_mlp_baseline.py (the one sent to Cliff) -- this module only
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

# unified_mlp_baseline.py (moved into ML_algos/, 2026-08-30) imports from the
# sustain-lc submodule (RolloutBuffer from ca_ppo), so that dir must be on
# path BEFORE the import; the repo root enables the optimal_dc.* namespace.
_OPTIMAL_DC = Path(__file__).resolve().parents[1]
for _p in (str(_OPTIMAL_DC.parent), str(_OPTIMAL_DC / "external" / "sustain-lc")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from optimal_dc.ML_algos.unified_mlp_baseline import Unified_PPO  # noqa: E402

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
        # upstream: update every 1 x 200 steps. Cadence is decoupled from
        # episode length via `update_ep_len` (see sustainlc_baselines) so
        # full-day episodes keep ~200-step PPO windows.
        self.update_timestep = int(config.get(
            "update_timestep", int(config.get("update_ep_len", 200))))
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
        """Action for one observation dict, buffer-free (safe for eval).

        deterministic=True bypasses the sampling distributions: CDU = the
        actor's mean, CT = argmax over the categorical -- matching the
        sustainlc baselines' eval convention."""
        import torch
        flat = flatten_state(obs)
        if deterministic:
            with torch.no_grad():
                s = torch.FloatTensor(flat).to(next(
                    self.agent.policy_old.cdu_actor.parameters()).device)
                cdu = self.agent.policy_old.cdu_actor(s).reshape(5, 5).cpu().numpy()
                ct = int(self.agent.policy_old.ct_actor(s).argmax().item())
            return env_action(cdu, ct)
        cdu, ct = self.agent.select_action(flat)
        for buf in self.agent.buffer_dict.values():   # select_action pushes; eval must not pollute
            buf.clear()
        return env_action(cdu, ct)

    # -------------------------------------------------------------- training
    def learn(self, env, n_steps: int, eval_env=None, eval_interval: int = None) -> dict:
        """Resumable AND reproducible — same snapshot scheme as the sustainlc
        baselines: counters continue from load_resume_state(); a full snapshot
        is written at every episode end that coincides with an update boundary
        (every episode at the default 1 x ep_len cadence). See
        _SustainLCBaseline.learn() for why boundary-only snapshots make a
        resumed run bit-identical to an uninterrupted one."""
        hp = self.hp
        rs = getattr(self, "_resume_counters", None) or {}
        best_reward = rs.get("best_reward", float("-inf"))
        running_reward = rs.get("running_reward", {"CDUCAB": 0.0, "CT": 0.0})
        running_episodes = rs.get("running_episodes", 0)
        save_freq = int(hp["save_model_freq"])
        time_step = rs.get("time_step", 0)
        i_episode = rs.get("i_episode", 0)

        def _counters():
            return {"time_step": time_step,
                    "i_episode": i_episode,
                    "best_reward": best_reward,
                    "running_reward": running_reward,
                    "running_episodes": running_episodes}

        if rs:
            self.logger.info(f"[{self.ALGO_NAME}] RESUMING at step {time_step} "
                             f"(episode {i_episode}) toward {n_steps}")
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

            # Boundary snapshot — see _SustainLCBaseline.learn() for the
            # reproducibility argument.
            if time_step % self.update_timestep == 0 and hasattr(self, "checkpoint_dir"):
                self.save_resume_state(env, counters=_counters())

        self.logger.info(f"[{self.ALGO_NAME}] done: {time_step} steps, {i_episode} episodes")
        return {"log": self.train_log}

    # ---------------------------------------------------------- resume state
    def _agent_state(self) -> dict:
        a = self.agent
        return {"policy": a.policy.state_dict(),
                "policy_old": a.policy_old.state_dict(),
                "optimizer": a.optimizer.state_dict(),
                "cdu_action_std": a.cdu_action_std}

    def _load_agent_state(self, state: dict) -> None:
        a = self.agent
        # restores BOTH nets — Unified_PPO.load() only restores policy_old,
        # which is why plain .pth checkpoints cannot resume training
        a.policy.load_state_dict(state["policy"])
        a.policy_old.load_state_dict(state["policy_old"])
        a.optimizer.load_state_dict(state["optimizer"])
        a.set_action_std(state["cdu_action_std"])

    # ------------------------------------------------------------ evaluation
    def evaluate(self, eval_env, n_episodes: int = 5, deterministic: bool = True,
                 max_steps: int = None) -> dict:
        """Reward-summary evaluation, mirroring the sustainlc baselines.
        NOTE: every reset() re-triggers the FMU init transient; energy-metric
        scoring belongs to evaluation/rollout.py, not here."""
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
        path = (_OPTIMAL_DC / "archive" / "Unified_MLP_preTrained" / "SmallFrontierModel"
                / f"PPO_SmallFrontierModel_{seed}_{run_num_pretrained}_unified.pth")
        self.agent.load(str(path))
        self.logger.info(f"Loaded pretrained (/15-regime) unified MLP: {path}")
