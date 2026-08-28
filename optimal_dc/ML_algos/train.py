"""
Training script: train ML algorithm on FrontierEnv with preprocessed exogenous data.

Usage:
    python -m optimal_dc.ML_algos.train \
        --config optimal_dc/ML_algos/config/variant_a_frontier.yaml \
        --output optimal_dc/ML_algos/checkpoints/variant_a/ \
        --n_steps 1000000 \
        --algo ppo
"""

import argparse
import json
import logging
from pathlib import Path
import sys
import yaml
import numpy as np

import torch

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parents[3]))

from optimal_dc.external.sustain_lc.frontier_env import FrontierEnv
from optimal_dc.workload_gen_pipeline import generate, validate, load_spec
from optimal_dc.ML_algos import PPO
from optimal_dc.ML_algos.io_contract import ExogenousTrace

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config(config_path: str | Path) -> dict:
    """Load hyperparameter config from YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def prepare_exogenous_trace(
    data_source: str,
    spec_path: str | Path = None,
    config_path: str | Path = None,
    stacking: str = "none",
) -> ExogenousTrace:
    """
    Load exogenous trace from data source.

    Args:
        data_source: "frontier_csv" | "regime_a_synthetic"
        spec_path: path to frozen regime_A.json
        config_path: path to regime_A_calib.json
        stacking: "none" | "phase_shift" | "regime_a_synthetic"

    Returns:
        ExogenousTrace with (T, 16) power + towb
    """
    if data_source == "frontier_csv":
        logger.info("Loading real Frontier CSV data")
        csv_path = Path(__file__).parents[2] / "external/sustain-lc/input_04-07-24.csv"
        # TODO: implement CSV loading + disaggregation
        raise NotImplementedError("CSV loader not yet implemented; use regime_a_synthetic for now")

    elif data_source == "regime_a_synthetic":
        logger.info("Generating regime-A synthetic data")
        spec = load_spec(spec_path or Path(__file__).parent / "spec/regime_A.json")
        # TODO: load calibrated config and generate
        raise NotImplementedError("Need regime_A_calib.json; see disaggregator design")

    else:
        raise ValueError(f"Unknown data source: {data_source}")


def main():
    parser = argparse.ArgumentParser(
        description="Train ML algorithm on datacenter cooling control."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to hyperparameter config (YAML)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Checkpoint output directory"
    )
    parser.add_argument(
        "--n_steps",
        type=int,
        default=1_000_000,
        help="Total environment steps to train"
    )
    parser.add_argument(
        "--algo",
        type=str,
        default="ppo",
        choices=["ppo", "sac"],
        help="Algorithm to train"
    )
    parser.add_argument(
        "--data_source",
        type=str,
        default="regime_a_synthetic",
        choices=["frontier_csv", "regime_a_synthetic"],
        help="Exogenous trace source"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="PyTorch device (cuda, cpu, mps)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed"
    )
    args = parser.parse_args()

    # Load config
    logger.info(f"Loading config from {args.config}")
    config = load_config(args.config)
    config["device"] = args.device
    config["seed"] = args.seed

    # Set random seeds
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    # Create environment
    logger.info("Initializing FrontierEnv")
    env = FrontierEnv(
        fmu_path=config.get("fmu_path"),
        max_steps=config.get("max_steps", 5761),
        reward_fn=config.get("reward_fn", "energy_only")
    )

    # Prepare exogenous trace
    # NOTE: For now, FrontierEnv handles exogenous data internally via iter_exogenous_var.
    # This will be updated to accept disaggregator output.
    # See disaggregator design for the data flow.

    # Create algorithm
    logger.info(f"Creating {args.algo.upper()} agent")
    if args.algo == "ppo":
        agent = PPO(config, env)
    else:
        raise NotImplementedError(f"Algorithm {args.algo} not yet implemented")

    # Setup checkpointing
    agent.setup_checkpointing(args.output)

    # Train
    logger.info(f"Training for {args.n_steps} steps")
    try:
        train_log = agent.learn(
            env,
            n_steps=args.n_steps,
            eval_interval=config.get("eval_interval", 10000)
        )
        logger.info("Training complete!")
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")

    # Save final checkpoint
    final_path = agent.save_checkpoint(f"{args.algo}_final")
    logger.info(f"Saved final checkpoint: {final_path}")

    # Save training metadata
    metadata = {
        "algorithm": args.algo,
        "n_steps": args.n_steps,
        "seed": args.seed,
        "config_path": str(args.config),
        "data_source": args.data_source,
        "device": args.device,
        "total_episodes": agent.total_episodes,
        "final_checkpoint": str(final_path),
    }
    metadata_path = args.output / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata: {metadata_path}")


if __name__ == "__main__":
    main()
