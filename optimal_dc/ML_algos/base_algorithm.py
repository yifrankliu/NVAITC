"""
Base algorithm class for all RL agents.

Provides common functionality: environment setup, logging, checkpointing,
evaluation. Concrete algorithms (PPO, SAC) inherit from this.
"""

from pathlib import Path
import json
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# Full training-state snapshot for resumable runs; lives next to the checkpoints.
# torch/numpy are imported lazily inside the resume methods so this module stays
# importable in torch-less environments (see ML_algos/__init__.py).
RESUME_FILENAME = "resume_state.pt"


class BaseAlgorithm:
    """
    Abstract base class for RL algorithms.

    Subclasses must implement:
      - _build_networks(obs_space, action_space)
      - _compute_loss(batch)
      - predict(obs, deterministic=False)
    """

    def __init__(self, config: dict, env):
        """
        Initialize algorithm.

        Args:
            config: hyperparameter dict (learning rate, network size, etc.)
            env: Gym environment (FrontierEnv)
        """
        self.config = config
        self.env = env
        self.device = config.get("device", "cpu")
        self.logger = logger

        # Derived from config
        self.learning_rate = config.get("learning_rate", 3e-4)
        self.batch_size = config.get("batch_size", 64)
        self.n_epochs = config.get("n_epochs", 10)
        self.gamma = config.get("gamma", 0.99)
        self.gae_lambda = config.get("gae_lambda", 0.95)

        # Training state
        self.total_timesteps = 0
        self.total_episodes = 0
        self.train_log = []

    def setup_checkpointing(self, checkpoint_dir: str | Path) -> None:
        """Create checkpoint directory and metadata file."""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Save config alongside checkpoints
        config_path = self.checkpoint_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=2)
        self.logger.info(f"Checkpoint directory: {self.checkpoint_dir}")

    # ------------------------------------------------------------------ resume
    # The eval-only .pth checkpoints persist just policy_old weights (upstream
    # format). These methods snapshot EVERYTHING a paused/killed run needs to
    # continue: nets + optimizer + action_std, loop counters, RNG states, and
    # the day-sampler position (so a resumed run continues the day sequence
    # instead of replaying days it already trained on).

    def _agent_state(self) -> dict:
        """Subclass hook: full learnable state (nets, optimizers, action stds)."""
        raise NotImplementedError

    def _load_agent_state(self, state: dict) -> None:
        """Subclass hook: inverse of _agent_state()."""
        raise NotImplementedError

    def save_resume_state(self, env=None, counters: dict = None) -> Path:
        """Atomically write the resume snapshot to checkpoint_dir. Call only at
        episode-end PPO-update boundaries (rollout buffers empty, episode stats
        folded in, RNG/sampler exactly as the run carries them into the next
        reset) — learn() does this. Snapshotting ONLY at such boundaries is
        what makes resume bit-identical to an uninterrupted run."""
        import os
        import torch
        state = {
            "algo": getattr(self, "ALGO_NAME", type(self).__name__),
            "config_fingerprint": self._config_fingerprint(self.config),
            "counters": dict(counters or {}),
            "agents": self._agent_state(),
            "rng": self._rng_state(),
            "env": self._env_state(env) if env is not None else {},
            "train_log": self.train_log,
        }
        path = self.checkpoint_dir / RESUME_FILENAME
        tmp = path.with_suffix(".tmp")
        torch.save(state, tmp)
        os.replace(tmp, path)      # atomic: a crash mid-write never corrupts the snapshot
        return path

    def load_resume_state(self, path: str | Path = None, env=None) -> dict:
        """Restore a snapshot written by save_resume_state; returns the counters
        dict for learn() to continue from. Trusted local artifact, hence
        weights_only=False (the snapshot holds RNG tuples, not just tensors)."""
        import torch
        path = Path(path) if path is not None else self.checkpoint_dir / RESUME_FILENAME
        state = torch.load(path, map_location="cpu", weights_only=False)
        if state.get("algo") not in (None, getattr(self, "ALGO_NAME", type(self).__name__)):
            raise ValueError(f"resume state is for {state['algo']!r}, not this algorithm")
        fp = state.get("config_fingerprint")
        if fp is not None and fp != self._config_fingerprint(self.config):
            raise ValueError(
                f"resume state {path} was written under a different config/seed "
                "than this invocation. Restore the original config (and seed), "
                "or pass --fresh to discard the snapshot and start over.")
        self._load_agent_state(state["agents"])
        self._restore_rng(state.get("rng", {}))
        if env is not None:
            self._restore_env_state(env, state.get("env", {}))
        self.train_log = state.get("train_log", [])
        self._resume_counters = state.get("counters", {})
        self.total_timesteps = self._resume_counters.get("time_step", 0)
        self.total_episodes = self._resume_counters.get("i_episode", 0)
        return self._resume_counters

    @staticmethod
    def _config_fingerprint(config: dict) -> str:
        """Hash of everything in the config that must match for a resume to be
        valid (the seed is in here — benchmarks writes it into the config).
        'device' is excluded so a run may move between CPU and GPU hosts; note
        that switching device mid-run keeps resume SOUND but not bit-identical
        (CPU and CUDA consume different RNG streams when sampling actions)."""
        import hashlib
        clean = {k: v for k, v in config.items() if k != "device"}
        return hashlib.sha256(
            json.dumps(clean, sort_keys=True, default=str).encode()).hexdigest()

    @staticmethod
    def _rng_state() -> dict:
        import random
        import numpy as np
        import torch
        return {
            "python": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
            "torch_cuda": (torch.cuda.get_rng_state_all()
                           if torch.cuda.is_available() else None),
        }

    @staticmethod
    def _restore_rng(rng: dict) -> None:
        import random
        import numpy as np
        import torch
        if "python" in rng:
            random.setstate(rng["python"])
        if "numpy" in rng:
            np.random.set_state(rng["numpy"])
        if "torch" in rng:
            torch.set_rng_state(rng["torch"].cpu())
        cuda = rng.get("torch_cuda")
        if cuda is not None and torch.cuda.is_available() \
                and len(cuda) == torch.cuda.device_count():
            torch.cuda.set_rng_state_all([s.cpu() for s in cuda])

    @staticmethod
    def _env_state(env) -> dict:
        inner = getattr(env, "env", env)          # MH wraps the real env
        out = {}
        sampler = getattr(inner, "day_sampler", None)
        if sampler is not None:
            out["sampler_next_seed"] = sampler._next_seed
            out["sampler_day_log"] = list(sampler.day_log)
            out["sampler_rng"] = sampler._rng.bit_generator.state
        if getattr(inner, "_offset_rng", None) is not None:
            out["offset_rng"] = inner._offset_rng.bit_generator.state
        return out

    @staticmethod
    def _restore_env_state(env, state: dict) -> None:
        inner = getattr(env, "env", env)
        sampler = getattr(inner, "day_sampler", None)
        if sampler is not None and "sampler_next_seed" in state:
            sampler._next_seed = state["sampler_next_seed"]
            sampler.day_log = list(state["sampler_day_log"])
            sampler._rng.bit_generator.state = state["sampler_rng"]
        if getattr(inner, "_offset_rng", None) is not None and "offset_rng" in state:
            inner._offset_rng.bit_generator.state = state["offset_rng"]

    def log_training_step(self, step: int, metrics: dict) -> None:
        """Log training metrics."""
        self.train_log.append({"step": step, **metrics})
        if step % self.config.get("log_interval", 10) == 0:
            msg = f"step {step:6d} | "
            for k, v in metrics.items():
                if isinstance(v, float):
                    msg += f"{k}={v:.4f} | "
                else:
                    msg += f"{k}={v} | "
            self.logger.info(msg)

    def save_checkpoint(self, name: str) -> Path:
        """
        Save policy, value network, optimizer state.

        Subclasses override to save their specific artifacts (weights, etc.)
        """
        raise NotImplementedError

    def load_checkpoint(self, path: str | Path) -> None:
        """Load policy from checkpoint."""
        raise NotImplementedError

    def evaluate(self, eval_env, n_episodes: int = 5, deterministic: bool = True) -> dict:
        """
        Run the policy on an evaluation environment and return summary metrics.

        Subclasses implement this against the REAL env API: reset() returns the
        obs dict only, step() returns a 4-tuple (obs, reward_dict, done_dict,
        info) where info holds the raw (unscaled) observations. See
        sustainlc_baselines for the reference implementation.
        """
        raise NotImplementedError

    def predict(self, obs: dict, deterministic: bool = False):
        """
        Predict action given observation.

        Subclasses override with concrete implementation.
        """
        raise NotImplementedError

    def learn(self, env, n_steps: int, eval_env=None, eval_interval: int = 5000):
        """
        Train the algorithm.

        Args:
            env: training environment
            n_steps: total environment steps
            eval_env: optional evaluation environment
            eval_interval: frequency of evaluation
        """
        raise NotImplementedError
