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
