"""The two sustain-lc RL baselines, wired to the v3 pluggable-data envs.

sustain-lc ships exactly two trained RL baselines (verified 2026-08-28 against
train_multiagent_ca_ppo.py / train_mh_ma_ca_ppo.py; ca_ppo.py and
multihead_ca_ppo.py are their building blocks, not separate baselines):

  MA_CA_PPO     multiagent_ppo_dtde(agent_type='CA_PPO')
                CDUCAB agent: CA_PPO, continuous (5,) action per cabinet, one
                shared net over 5 centralized actions; CT agent: CA_PPO,
                discrete 9. Env: SmallFrontierModel.
  MH_MA_CA_PPO  multiagent_ppo_dtde(agent_type='MultiHead_CA_PPO')
                CDUCAB agent: MultiHead_CA_PPO — top-level (2,) tanh-Gaussian
                + valve-level (3,) Dirichlet heads on a shared backbone; CT
                agent: CA_PPO discrete 9. Env: MH_SmallFrontierModel
                (subsample_rate=40, do_valve_softmax=False).

This module REUSES the sustain-lc classes from the submodule (no copies) and
ports the two training loops faithfully — hyperparameter defaults below are
the exact values in the upstream train scripts. Only the env is swapped for
the v3 pluggable version (csv_path + disaggregator selection); with
disaggregator_version="v2" and the upstream CSV, training conditions match
upstream bit-for-bit in structure.

Checkpoint format: one .pth per agent, ``{name}_agent_{CDUCAB,CT}.pth`` in the
checkpoint dir — same tensors as sustain-lc's preTrained files, so
``load_checkpoint`` also accepts the shipped preTrained weights via
``load_sustainlc_pretrained()``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

_OPTIMAL_DC = Path(__file__).resolve().parents[1]
_REPO_ROOT = _OPTIMAL_DC.parent
_SUSTAIN_LC = _OPTIMAL_DC / "external" / "sustain-lc"
for _p in (str(_REPO_ROOT), str(_SUSTAIN_LC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ca_ppo import device as _sustainlc_device  # noqa: E402  (prints device banner once)
from multiagent_ca_ppo import multiagent_ppo_dtde  # noqa: E402

from optimal_dc.ML_algos.base_algorithm import BaseAlgorithm  # noqa: E402

CABINET_KEYS = [f"cdu-cabinet-{i}" for i in range(1, 6)]
CT_KEY = "cooling-tower-1"

# Exact hyperparameters of the upstream train scripts (train_multiagent_ca_ppo.py
# / train_mh_ma_ca_ppo.py). config keys of the same name override them.
SUSTAINLC_DEFAULTS = dict(
    max_ep_len=200,
    K_epochs=50,
    eps_clip=0.2,
    gamma=0.80,
    lr_actor=3.0e-4,
    lr_critic=1.0e-3,
    action_std_init=0.6,
    action_std_decay_rate=0.05,
    min_action_std=0.1,
    action_std_decay_freq=int(2.5e5),
)


def batchify_observations(observation_dict):
    """Env obs dict -> {'CDUCAB': (5, 6) array, 'CT': (1, 4) array} (upstream helper)."""
    batch = {"CDUCAB": [], "CT": []}
    for key, value in observation_dict.items():
        (batch["CT"] if key == CT_KEY else batch["CDUCAB"]).append(value)
    return {k: np.array(v) for k, v in batch.items()}


class _SustainLCBaseline(BaseAlgorithm):
    """Shared train/eval/checkpoint machinery for both baselines.

    Subclasses set AGENT_TYPE / UPDATE_TIMESTEP_FACTOR and implement the
    action assembly (_env_action) and buffer-free deterministic/stochastic
    prediction (_predict_cducab).
    """

    AGENT_TYPE: str = None
    ALGO_NAME: str = None
    UPDATE_TIMESTEP_FACTOR: int = None  # update every factor * update_ep_len steps

    def __init__(self, config: dict, env):
        super().__init__(config, env)
        self.hp = {k: config.get(k, v) for k, v in SUSTAINLC_DEFAULTS.items()}
        self.max_ep_len = int(self.hp["max_ep_len"])
        # PPO update cadence is DECOUPLED from episode length (2026-08-30,
        # full-day-episode decision): the update window is FACTOR x
        # `update_ep_len` (default 200 = upstream's ep_len, so short-episode
        # configs behave exactly as before). With max_ep_len 5760 one update
        # per episode would collapse 2500 updates into 86; keeping ~200-step
        # windows inside the long episode preserves the optimization regime —
        # bootstrapping via next_state makes mid-episode updates sound.
        update_ep_len = int(config.get("update_ep_len", 200))
        self.update_timestep = int(config.get(
            "update_timestep", self.UPDATE_TIMESTEP_FACTOR * update_ep_len))
        # resume snapshots fire at episode ends that land on update boundaries;
        # warn if the chosen geometry makes that rare (crash rewinds far)
        _ep, _up = self.max_ep_len, self.update_timestep
        import math
        _coincide_every = _up // math.gcd(_ep, _up)
        if _coincide_every > 5:
            logger.warning(
                f"max_ep_len={_ep} and update_timestep={_up} only align every "
                f"{_coincide_every} episodes — resume snapshots will be that "
                f"infrequent; pick values where one divides the other")

        self.agent_mdp_dict = self._build_agent_mdp_dict(env)
        self.agent = multiagent_ppo_dtde(self.agent_mdp_dict, agent_type=self.AGENT_TYPE)
        self._action_std = self.hp["action_std_init"]

    # ---------------------------------------------------------------- spaces
    def _common_mdp(self):
        return dict(lr_actor=self.hp["lr_actor"], lr_critic=self.hp["lr_critic"],
                    gamma=self.hp["gamma"], K_epochs=self.hp["K_epochs"],
                    eps_clip=self.hp["eps_clip"],
                    action_std_init=self.hp["action_std_init"])

    def _ct_mdp(self, env):
        return dict(state_dim=env.observation_space[CT_KEY].shape[0],
                    action_dim=env.action_space[CT_KEY].n,
                    num_centralized_actions=1,
                    has_continuous_action_space=False,
                    **self._common_mdp())

    def _build_agent_mdp_dict(self, env) -> dict:
        raise NotImplementedError

    # ---------------------------------------------------------------- actions
    def _select_actions_training(self, batch_state):
        """Sample via agent.select_action (fills the rollout buffers)."""
        raise NotImplementedError

    def _predict_cducab(self, states: np.ndarray, deterministic: bool):
        """Buffer-free CDUCAB action for evaluation."""
        raise NotImplementedError

    def _predict_ct(self, state: np.ndarray, deterministic: bool) -> int:
        ct = self.agent.agents["CT"]
        with torch.no_grad():
            s = torch.FloatTensor(state).to(_sustainlc_device)
            probs = ct.policy_old.actor(s).squeeze(0)
            if deterministic:
                return int(probs.argmax().item())
            return int(torch.distributions.Categorical(probs).sample().item())

    def _env_action(self, cducab_action, ct_action) -> dict:
        """Pack per-agent actions into the env's action dict."""
        raise NotImplementedError

    def predict(self, obs: dict, deterministic: bool = False) -> dict:
        """Env-format action from an env observation dict. Buffer-free (safe for eval)."""
        batch = batchify_observations(obs)
        cducab = self._predict_cducab(batch["CDUCAB"], deterministic)
        ct = self._predict_ct(batch["CT"], deterministic)
        return self._env_action(cducab, ct)

    # ---------------------------------------------------------------- training
    def learn(self, env, n_steps: int, eval_env=None, eval_interval: int = None) -> dict:
        """Faithful port of the upstream training loop (episode structure,
        update cadence, action-std decay, best-reward checkpointing).

        Resumable AND reproducible: counters start from load_resume_state()'s
        snapshot if one was loaded; a full snapshot is written at every
        episode end that coincides with a PPO-update boundary (every episode
        for MA, every 2nd for MH). Only there is the ENTIRE state consistent —
        buffers empty, nets untouched since the update, episode stats folded
        in, RNG + day-sampler exactly as the run carries them into the next
        reset() — so a resumed run replays the uninterrupted run bit-for-bit
        (modulo FMU solver nondeterminism). Any interrupt or crash loses at
        most the steps since that boundary (< one update window + one episode);
        deliberately NO mid-window/exit-time save exists, because a snapshot
        taken off-boundary would resume soundly but not reproducibly."""
        hp = self.hp
        rs = getattr(self, "_resume_counters", None) or {}
        best_reward = rs.get("best_reward", {"CDUCAB": float("-inf"), "CT": float("-inf")})
        running_reward = rs.get("running_reward", {"CDUCAB": 0.0, "CT": 0.0})
        running_episodes = rs.get("running_episodes", 0)
        save_freq = int(self.config.get("save_model_freq", 2000))
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
            batch_state = batchify_observations(state)
            ep_reward = {"CDUCAB": 0.0, "CT": 0.0}

            for _ in range(self.max_ep_len):
                actions = self._select_actions_training(batch_state)
                state, rewards, done, _info = env.step(actions)
                batch_state = batchify_observations(state)

                # bootstrap state for the non-terminating env's advantage calc
                self.agent.agents["CDUCAB"].next_state = batch_state["CDUCAB"]
                self.agent.agents["CT"].next_state = batch_state["CT"]
                self.agent.collect_rewards_and_terminals(rewards, done)

                ep_reward["CDUCAB"] += sum(rewards[k] for k in CABINET_KEYS) / 5.0
                ep_reward["CT"] += rewards[CT_KEY]
                time_step += 1

                if time_step % self.update_timestep == 0:
                    loss_cdu = float(self.agent.update("CDUCAB"))
                    loss_ct = float(self.agent.update("CT"))
                    self.log_training_step(time_step, {
                        "loss_CDUCAB": loss_cdu, "loss_CT": loss_ct})

                if time_step % hp["action_std_decay_freq"] == 0:
                    self.agent.decay_action_std(
                        hp["action_std_decay_rate"], hp["min_action_std"], "CDUCAB")

                if time_step % save_freq == 0 and hasattr(self, "checkpoint_dir"):
                    avg = ({k: running_reward[k] / running_episodes for k in running_reward}
                           if running_episodes else None)
                    if avg is not None:
                        for aid in ("CDUCAB", "CT"):
                            if avg[aid] > best_reward[aid]:
                                best_reward[aid] = avg[aid]
                                self.agent.save(str(
                                    self.checkpoint_dir / f"best_agent_{aid}.pth"), aid)

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

            # Boundary snapshot: episode ended exactly on an update boundary
            # (default cadence guarantees this every UPDATE_TIMESTEP_FACTOR
            # episodes), so buffers are empty, this episode's stats are folded
            # in, and RNG/sampler are exactly what the next reset() consumes.
            if time_step % self.update_timestep == 0 and hasattr(self, "checkpoint_dir"):
                self.save_resume_state(env, counters=_counters())

        self.logger.info(f"[{self.ALGO_NAME}] done: {time_step} steps, {i_episode} episodes")
        return {"log": self.train_log}

    # ---------------------------------------------------------------- resume state
    def _agent_state(self) -> dict:
        out = {}
        for aid, a in self.agent.agents.items():
            d = {"policy": a.policy.state_dict(),
                 "policy_old": a.policy_old.state_dict(),
                 "optimizer": a.optimizer.state_dict()}
            if hasattr(a, "action_std"):      # discrete CT CA_PPO has none
                d["action_std"] = a.action_std
            out[aid] = d
        return out

    def _load_agent_state(self, state: dict) -> None:
        for aid, d in state.items():
            a = self.agent.agents[aid]
            a.policy.load_state_dict(d["policy"])
            a.policy_old.load_state_dict(d["policy_old"])
            a.optimizer.load_state_dict(d["optimizer"])
            if "action_std" in d:
                # set_action_std also rebuilds action_var on BOTH nets — the
                # tensor state_dict() omits (the eval-only-checkpoint gap)
                a.set_action_std(d["action_std"])
                self._action_std = d["action_std"]

    # ---------------------------------------------------------------- evaluation
    def evaluate(self, eval_env, n_episodes: int = 5, deterministic: bool = True,
                 max_steps: int = None, t_max_K: float = None,
                 warmup: int = 10) -> dict:
        """Roll out and report physical metrics from the env's RAW info dict.

        info[cabinet][0:3] = boundary temps (K), [3:6] = blade powers (W);
        info[CT][0:2] = the two CT fan cell powers (W).
        warmup: steps excluded from the temperature/fan/violation metrics —
        every reset() re-triggers the FMU's initialization transient (~139 C
        peak in the first ~5 steps on ANY input, settled by ~step 25); rewards
        still accumulate over all steps.
        t_max_K: optional violation threshold. Deliberately no default — the
        /15-era 313 K constant does not transfer to the hotter /9 regime; set
        it from the /9 rule-based baseline pass.
        """
        max_steps = max_steps or self.max_ep_len
        if warmup >= max_steps:
            raise ValueError(f"warmup ({warmup}) must be < max_steps ({max_steps})")
        ep_metrics = []
        for _ in range(n_episodes):
            obs = eval_env.reset()
            rew = {"CDUCAB": 0.0, "CT": 0.0}
            temps, fan_W, violations = [], [], 0
            for _t in range(max_steps):
                action = self.predict(obs, deterministic=deterministic)
                obs, rewards, _done, info = eval_env.step(action)
                rew["CDUCAB"] += sum(rewards[k] for k in CABINET_KEYS) / 5.0
                rew["CT"] += rewards[CT_KEY]
                if _t < warmup:
                    continue
                step_temps = np.array([info[k][0:3] for k in CABINET_KEYS])
                temps.append(step_temps)
                fan_W.append(float(np.sum(info[CT_KEY][0:2])))
                if t_max_K is not None and step_temps.max() > t_max_K:
                    violations += 1
            temps = np.array(temps)
            ep_metrics.append({
                "return_CDUCAB": rew["CDUCAB"],
                "return_CT": rew["CT"],
                "mean_cab_temp_C": float(temps.mean() - 273.15),
                "max_cab_temp_C": float(temps.max() - 273.15),
                "mean_ct_fan_kW": float(np.mean(fan_W) / 1e3),
                "violation_rate": (violations / (max_steps - warmup)
                                   if t_max_K is not None else None),
            })

        summary = {"episodes_completed": n_episodes,
                   "deterministic": deterministic,
                   "steps_per_episode": max_steps}
        for key in ("return_CDUCAB", "return_CT", "mean_cab_temp_C",
                    "max_cab_temp_C", "mean_ct_fan_kW"):
            vals = np.array([m[key] for m in ep_metrics])
            summary[f"mean_{key}"] = float(vals.mean())
            summary[f"std_{key}"] = float(vals.std())
        if t_max_K is not None:
            summary["mean_violation_rate"] = float(
                np.mean([m["violation_rate"] for m in ep_metrics]))
        return summary

    # ---------------------------------------------------------------- checkpoints
    def save_checkpoint(self, name: str) -> Path:
        if not hasattr(self, "checkpoint_dir"):
            raise RuntimeError("Call setup_checkpointing() first")
        for aid in ("CDUCAB", "CT"):
            self.agent.save(str(self.checkpoint_dir / f"{name}_agent_{aid}.pth"), aid)
        marker = self.checkpoint_dir / f"{name}_agent_CDUCAB.pth"
        self.logger.info(f"Saved {self.ALGO_NAME} checkpoint pair: {marker} (+CT)")
        return marker

    def load_checkpoint(self, path: str | Path) -> None:
        """Accepts the CDUCAB .pth of a saved pair; loads both agents.

        Works for our own checkpoints and for sustain-lc preTrained files —
        anything ending in `_agent_CDUCAB.pth` with a CT sibling.
        """
        path = str(path)
        if "_agent_CDUCAB" not in path:
            raise ValueError(f"expected a *_agent_CDUCAB.pth path, got {path}")
        self.agent.load(path, "CDUCAB")
        self.agent.load(path.replace("_agent_CDUCAB", "_agent_CT"), "CT")
        self.logger.info(f"Loaded {self.ALGO_NAME} checkpoint pair from {path}")

    def load_sustainlc_pretrained(self, run_num_pretrained: int, seed: int = 123) -> None:
        """Load the submodule's shipped preTrained weights (MA: run 3, MH: run 2)."""
        d = _SUSTAIN_LC / f"{self.ALGO_NAME}_preTrained" / self.ENV_NAME
        self.load_checkpoint(
            d / f"PPO_{self.ENV_NAME}_{seed}_{run_num_pretrained}_agent_CDUCAB.pth")


class MA_CA_PPO(_SustainLCBaseline):
    """sustain-lc baseline 1: DTDE multi-agent CA-PPO on SmallFrontierModel(_v3)."""

    AGENT_TYPE = "CA_PPO"
    ALGO_NAME = "MA_CA_PPO"
    ENV_NAME = "SmallFrontierModel"
    UPDATE_TIMESTEP_FACTOR = 1        # upstream: update every 1 * max_ep_len

    def _build_agent_mdp_dict(self, env) -> dict:
        return {
            "CDUCAB": dict(
                state_dim=env.observation_space[CABINET_KEYS[0]].shape[0],
                action_dim=env.action_space[CABINET_KEYS[0]].shape[0],
                num_centralized_actions=5,
                has_continuous_action_space=True,
                **self._common_mdp()),
            "CT": self._ct_mdp(env),
        }

    def _select_actions_training(self, batch_state):
        # CA_PPO.select_action returns a 1-tuple for the batched CDUCAB case
        cducab = self.agent.select_action(batch_state["CDUCAB"], "CDUCAB")[0]  # (5, 5)
        ct = self.agent.select_action(batch_state["CT"], "CT")                 # int
        return self._env_action(cducab, ct)

    def _predict_cducab(self, states, deterministic):
        cdu = self.agent.agents["CDUCAB"]
        with torch.no_grad():
            s = torch.FloatTensor(states).to(_sustainlc_device)
            mean = cdu.policy_old.actor(s)                       # (5, 5) tanh means
            if deterministic:
                out = mean
            else:
                cov = torch.diag(cdu.policy_old.action_var)
                out = torch.distributions.MultivariateNormal(mean, cov).sample()
        return out.cpu().numpy()

    def _env_action(self, cducab_action, ct_action) -> dict:
        action = {key: cducab_action[i] for i, key in enumerate(CABINET_KEYS)}
        action[CT_KEY] = ct_action
        return action


class MH_MA_CA_PPO(_SustainLCBaseline):
    """sustain-lc baseline 2: multi-head CDUCAB (top-level Gaussian + valve
    Dirichlet) + CA-PPO CT, on MH_SmallFrontierModel(_v3)."""

    AGENT_TYPE = "MultiHead_CA_PPO"
    ALGO_NAME = "MH_MA_CA_PPO"
    ENV_NAME = "MH_SmallFrontierModel"
    UPDATE_TIMESTEP_FACTOR = 2        # upstream: update every 2 * max_ep_len

    def _build_agent_mdp_dict(self, env) -> dict:
        cab_space = env.action_space[CABINET_KEYS[0]]
        return {
            "CDUCAB": dict(
                state_dim=env.observation_space[CABINET_KEYS[0]].shape[0],
                action_dim={"top-level": cab_space["top-level"].shape[0],
                            "valve-level": cab_space["valve-level"].shape[0]},
                num_centralized_actions=5,
                **self._common_mdp()),     # MultiHead_CA_PPO takes no continuous flag
            "CT": self._ct_mdp(env),
        }

    def _select_actions_training(self, batch_state):
        top, valve = self.agent.select_action(batch_state["CDUCAB"], "CDUCAB")
        ct = self.agent.select_action(batch_state["CT"], "CT")
        return self._env_action({"top-level": top, "valve-level": valve}, ct)

    def _predict_cducab(self, states, deterministic):
        cdu = self.agent.agents["CDUCAB"]
        with torch.no_grad():
            s = torch.FloatTensor(states).to(_sustainlc_device)
            pol = cdu.policy_old
            x = pol.backbone(s)
            top_mean = pol.top_level_actions(pol.top_level_action_features(x))  # (5, 2)
            conc = torch.nn.functional.softplus(pol.valve_level_features(x)) + 1e-3
            if deterministic:
                top = top_mean
                valve = conc / conc.sum(dim=-1, keepdim=True)    # Dirichlet mean
            else:
                cov = torch.diag(pol.action_var)
                top = torch.distributions.MultivariateNormal(top_mean, cov).sample()
                valve = torch.distributions.Dirichlet(conc).sample()
        return {"top-level": top.cpu().numpy(), "valve-level": valve.cpu().numpy()}

    def _env_action(self, cducab_action, ct_action) -> dict:
        action = {}
        for i, key in enumerate(CABINET_KEYS):
            action[key] = {"top-level": cducab_action["top-level"][i],
                           "valve-level": cducab_action["valve-level"][i]}
        action[CT_KEY] = ct_action
        return action
