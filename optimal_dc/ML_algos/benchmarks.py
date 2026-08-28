"""
Benchmark suite: train and evaluate variant A (Frontier only, no OneAsia).

This script provides an end-to-end workflow:
  1. Load variant A data (Frontier CSV + regime-A synthetic)
  2. Train PPO agent
  3. Evaluate on held-out data
  4. Compare to baseline

Usage:
    python -m optimal_dc.ML_algos.benchmarks train \
        --config optimal_dc/ML_algos/config/variant_a_frontier.yaml \
        --output checkpoints/variant_a/ \
        --n_steps 100_000

    python -m optimal_dc.ML_algos.benchmarks eval \
        --checkpoint checkpoints/variant_a/ppo_final.pt \
        --n_episodes 5
"""

import argparse
import json
import logging
from pathlib import Path
import sys
import yaml

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parents[3]))

from optimal_dc.ML_algos.ppo import PPO
from optimal_dc.ML_algos.evaluate import evaluate_policy, print_comparison_table
from optimal_dc.inherited_FMU_with_modifications.frontier_env_v3 import SmallFrontierModel_v3, create_env_v3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def train_variant_a(config_path: str | Path, output_dir: str | Path, n_steps: int, seed: int = 0):
    """
    Train variant A (Frontier + regime-A synthetic).

    Args:
        config_path: path to hyperparameter YAML
        output_dir: checkpoint directory
        n_steps: total training steps
        seed: random seed
    """
    logger.info("="*80)
    logger.info("VARIANT A TRAINING: Frontier CSV + Regime-A Synthetic")
    logger.info("="*80)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    config["seed"] = seed
    config["device"] = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info(f"Device: {config['device']}")
    logger.info(f"Config: {config_path}")

    # Set seeds
    np.random.seed(seed)
    torch.manual_seed(seed)

    # Create environment with pluggable CSV path and disaggregator
    logger.info("\nInitializing FrontierEnv_v3...")
    csv_path = config.get("csv_path", "optimal_dc/external/sustain-lc/input_04-07-24.csv")
    disaggregator_version = config.get("disaggregator_version", "v3")
    fmu_path = config.get("fmu_path")

    env = SmallFrontierModel_v3(
        fmu_path=fmu_path,
        csv_path=csv_path,
        disaggregator_version=disaggregator_version,
        max_steps=5761,
    )
    logger.info(f"Data source: {csv_path} (disaggregator: v{disaggregator_version[-1]})")

    # Create algorithm
    logger.info("Creating PPO agent...")
    agent = PPO(config, env)
    agent.setup_checkpointing(output_dir)

    # Train
    logger.info(f"\nTraining for {n_steps} steps...")
    try:
        train_log = agent.learn(env, n_steps=n_steps, eval_interval=10000)
        logger.info("Training complete!")
    except KeyboardInterrupt:
        logger.info("Training interrupted")

    # Save checkpoint
    final_checkpoint = agent.save_checkpoint("ppo_final")
    logger.info(f"Saved: {final_checkpoint}")

    # Save metadata
    metadata = {
        "variant": "a_frontier_regime_a",
        "algorithm": "ppo",
        "n_steps": n_steps,
        "seed": seed,
        "config": config_path,
        "total_episodes": agent.total_episodes,
        "data_source": csv_path,
        "disaggregator": disaggregator_version,
        "checkpoint": str(final_checkpoint),
    }
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata: {metadata_path}")

    return str(final_checkpoint)


def eval_variant_a(checkpoint_path: str | Path, n_episodes: int = 5):
    """
    Evaluate trained variant A agent.

    Args:
        checkpoint_path: path to ppo_final.pt
        n_episodes: evaluation episodes
    """
    logger.info("="*80)
    logger.info("VARIANT A EVALUATION")
    logger.info("="*80)

    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    # Load config from checkpoint directory
    config_path = checkpoint_path.parent / "config.json"
    with open(config_path) as f:
        config = json.load(f)

    # Load metadata to retrieve data source and disaggregator
    metadata_path = checkpoint_path.parent / "metadata.json"
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)

    logger.info(f"Checkpoint: {checkpoint_path}")
    logger.info(f"Config: {config_path}")

    # Create environment and agent with same data source
    csv_path = metadata.get("data_source", "optimal_dc/external/sustain-lc/input_04-07-24.csv")
    disaggregator_version = metadata.get("disaggregator", "v3")
    fmu_path = config.get("fmu_path")

    env = SmallFrontierModel_v3(
        fmu_path=fmu_path,
        csv_path=csv_path,
        disaggregator_version=disaggregator_version,
        max_steps=5761,
    )

    agent = PPO(config, env)
    agent.load_checkpoint(checkpoint_path)

    # Evaluate
    logger.info(f"\nEvaluating over {n_episodes} episodes...")
    summary = evaluate_policy(agent, env, n_episodes=n_episodes, deterministic=True)

    # Print results
    logger.info("\n" + "="*80)
    logger.info("RESULTS")
    logger.info("="*80)
    for key, value in summary.items():
        if isinstance(value, float):
            logger.info(f"{key:40s}: {value:12.2f}")
        else:
            logger.info(f"{key:40s}: {value}")

    # Save results
    results_path = checkpoint_path.parent / "eval_results.json"
    with open(results_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"\nSaved: {results_path}")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark suite for variant A (Frontier + regime-A)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Train subcommand
    train_parser = subparsers.add_parser("train", help="Train variant A")
    train_parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "config/variant_a_frontier.yaml",
        help="Hyperparameter config"
    )
    train_parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "checkpoints/variant_a",
        help="Output directory"
    )
    train_parser.add_argument(
        "--n_steps",
        type=int,
        default=100_000,
        help="Training steps (default 100k for quick test; use 500k for full)"
    )
    train_parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed"
    )
    train_parser.set_defaults(func=lambda args: train_variant_a(
        args.config, args.output, args.n_steps, args.seed
    ))

    # Eval subcommand
    eval_parser = subparsers.add_parser("eval", help="Evaluate variant A")
    eval_parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
        help="Path to ppo_final.pt"
    )
    eval_parser.add_argument(
        "--n_episodes",
        type=int,
        default=5,
        help="Evaluation episodes"
    )
    eval_parser.set_defaults(func=lambda args: eval_variant_a(args.checkpoint, args.n_episodes))

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
