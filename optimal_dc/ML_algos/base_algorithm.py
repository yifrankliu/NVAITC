"""
Base algorithm class for all RL agents.

Provides common functionality: environment setup, logging, checkpointing,
evaluation. Concrete algorithms (PPO, SAC) inherit from this.
"""

import numpy as np
from pathlib import Path
import json
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)


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
        Run policy on evaluation environment.

        Returns metrics: mean_return, mean_episode_length, constraint_violations
        """
        episode_returns = []
        episode_lengths = []
        total_violations = 0

        for ep in range(n_episodes):
            obs, info = eval_env.reset()
            done = False
            episode_return = 0.0
            episode_length = 0
            violations = 0

            while not done:
                action = self.predict(obs, deterministic=deterministic)
                obs, reward, terminated, truncated, info = eval_env.step(action.to_dict())
                done = terminated or truncated
                episode_return += reward
                episode_length += 1

                # Track constraint violations (from info if available)
                if "constraint_violations" in info:
                    violations += info["constraint_violations"]

            episode_returns.append(episode_return)
            episode_lengths.append(episode_length)
            total_violations += violations

        return {
            "mean_return": float(np.mean(episode_returns)),
            "std_return": float(np.std(episode_returns)),
            "mean_episode_length": float(np.mean(episode_lengths)),
            "total_constraint_violations": int(total_violations),
        }

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
