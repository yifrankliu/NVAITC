"""
Benchmark suite: train and evaluate the sustain-lc baselines on variant A data.

Algorithms (the two RL baselines sustain-lc ships, reused from the submodule):
  ma_ca_ppo     DTDE multi-agent CA-PPO (CDUCAB continuous + CT discrete)
  mh_ma_ca_ppo  multi-head CDUCAB (top-level Gaussian + valve Dirichlet) + CT

Usage:
    python -m optimal_dc.ML_algos.benchmarks train \
        --algo ma_ca_ppo \
        --config optimal_dc/ML_algos/config/variant_a_frontier.yaml \
        --output checkpoints/variant_a/ \
        --n_steps 100_000

    python -m optimal_dc.ML_algos.benchmarks eval \
        --checkpoint checkpoints/variant_a/ma_ca_ppo_final_agent_CDUCAB.pth \
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

# Repo root (NVAITC/) so `optimal_dc.*` namespace imports resolve:
# this file is optimal_dc/ML_algos/benchmarks.py -> parents[2] is the repo root.
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from optimal_dc.ML_algos.sustainlc_baselines import MA_CA_PPO, MH_MA_CA_PPO
from optimal_dc.ML_algos.unified_mlp import Unified_MLP
from optimal_dc.inherited_FMU_with_modifications.frontier_env_v3 import (
    SmallFrontierModel_v3, MH_SmallFrontierModel_v3,
)

# algo name -> (env class, algorithm class). "ppo" (the in-repo unified stub) is
# deliberately NOT listed: its update rule is a placeholder (policy_loss =
# value_loss) and its env API is wrong — see the module docstring of ppo.py.
# "unified_mlp" wraps the REAL June-2026 Unified_PPO (unified_mlp_baseline.py).
ALGOS = {
    "ma_ca_ppo": (SmallFrontierModel_v3, MA_CA_PPO),
    "mh_ma_ca_ppo": (MH_SmallFrontierModel_v3, MH_MA_CA_PPO),
    "unified_mlp": (SmallFrontierModel_v3, Unified_MLP),
}


def build_env_and_agent(algo: str, config: dict, csv_path, disaggregator_version: str):
    """Instantiate the algo's env variant + agent from one registry entry.

    Train-on-synthetic: a `synthetic_day_sampler` dict in the config (kwargs
    for RegimeADaySampler, e.g. {seed: 0, wetbulb: "replay", require_pass:
    true}) attaches a per-reset day sampler -- every episode then starts on a
    freshly generated certified regime-A day at a random offset, so the policy
    trains on the workload DISTRIBUTION. Without it, behavior is unchanged
    (static csv_path trace)."""
    if algo not in ALGOS:
        raise ValueError(f"unknown algo {algo!r}; choose from {sorted(ALGOS)}")
    env_cls, agent_cls = ALGOS[algo]

    sampler_cfg = config.get("synthetic_day_sampler")
    day_sampler = None
    if sampler_cfg is not None:
        from optimal_dc.ML_algos.data_loader import RegimeADaySampler
        day_sampler = RegimeADaySampler(**sampler_cfg)
        logger.info(f"Per-reset synthetic day sampler: {sampler_cfg}")

    env = env_cls(csv_path=csv_path, disaggregator_version=disaggregator_version,
                  day_sampler=day_sampler,
                  min_horizon=int(config.get("max_ep_len", 200)),
                  use_reward_shaping=config.get("use_reward_shaping", "reward_shaping_v2"),
                  # optional overrides for the facility_energy reward constants
                  # (energy_T_max_K / energy_P_ref_W / energy_lambda_per_K)
                  **config.get("energy_reward", {}))
    agent = agent_cls(config, env)
    return env, agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def train_variant_a(config_path: str | Path, output_dir: str | Path, n_steps: int,
                    seed: int = 0, algo: str = "ma_ca_ppo"):
    """
    Train variant A (Frontier CSV data source).

    Args:
        config_path: path to hyperparameter YAML
        output_dir: checkpoint directory
        n_steps: total training steps (sustain-lc used 3M for MA, 5M for MH)
        seed: random seed
        algo: "ma_ca_ppo" | "mh_ma_ca_ppo" (the two sustain-lc baselines)
    """
    logger.info("="*80)
    logger.info(f"VARIANT A TRAINING: {algo} on Frontier CSV")
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

    # Create environment + agent from the algo registry
    csv_path = Path(config.get("csv_path", "optimal_dc/external/sustain-lc/input_04-07-24.csv"))
    if not csv_path.is_absolute():
        csv_path = _REPO_ROOT / csv_path
    disaggregator_version = config.get("disaggregator_version", "v3")

    env, agent = build_env_and_agent(algo, config, csv_path, disaggregator_version)
    logger.info(f"Data source: {csv_path} (disaggregator: {disaggregator_version})")
    agent.setup_checkpointing(output_dir)

    # Train
    logger.info(f"\nTraining for {n_steps} steps...")
    try:
        agent.learn(env, n_steps=n_steps)
        logger.info("Training complete!")
    except KeyboardInterrupt:
        logger.info("Training interrupted")

    # Save checkpoint
    final_checkpoint = agent.save_checkpoint(f"{algo}_final")
    logger.info(f"Saved: {final_checkpoint}")

    # Save metadata
    metadata = {
        "variant": config.get("variant", "a_frontier"),
        "algorithm": algo,
        "n_steps": n_steps,
        "seed": seed,
        "config": str(config_path),
        "total_episodes": agent.total_episodes,
        "data_source": str(csv_path),
        "disaggregator": disaggregator_version,
        "checkpoint": str(final_checkpoint),
    }
    # provenance of the synthetic training distribution, if a sampler was used
    inner = getattr(env, "env", env)          # MH wraps the real env
    sampler = getattr(inner, "day_sampler", None)
    if sampler is not None:
        log = sampler.day_log
        metadata["synthetic_day_sampler"] = {
            **config.get("synthetic_day_sampler", {}),
            "n_days_drawn": len(log),
            "first_day": list(log[0]) if log else None,
            "last_day": list(log[-1]) if log else None,
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

    # Load metadata to retrieve algo, data source, and disaggregator
    metadata_path = checkpoint_path.parent / "metadata.json"
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)

    logger.info(f"Checkpoint: {checkpoint_path}")
    logger.info(f"Config: {config_path}")

    # Create environment and agent with same algo + data source
    algo = metadata.get("algorithm", "ma_ca_ppo")
    csv_path = Path(metadata.get("data_source", "optimal_dc/external/sustain-lc/input_04-07-24.csv"))
    if not csv_path.is_absolute():
        csv_path = _REPO_ROOT / csv_path
    disaggregator_version = metadata.get("disaggregator", "v3")

    env, agent = build_env_and_agent(algo, config, csv_path, disaggregator_version)
    agent.load_checkpoint(checkpoint_path)

    # Evaluate
    logger.info(f"\nEvaluating over {n_episodes} episodes...")
    summary = agent.evaluate(env, n_episodes=n_episodes, deterministic=True)

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
        # default = the train-on-synthetic protocol config (fresh certified day
        # per episode; real day held out). Pass variant_a_frontier.yaml
        # explicitly for the trained-on-real ablation arm.
        default=Path(__file__).parent / "config/variant_a_synth.yaml",
        help="Hyperparameter config (default: synthetic-day training)"
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
    train_parser.add_argument(
        "--algo",
        choices=sorted(ALGOS),
        default="ma_ca_ppo",
        help="Which sustain-lc baseline to train (default: ma_ca_ppo)"
    )
    train_parser.set_defaults(func=lambda args: train_variant_a(
        args.config, args.output, args.n_steps, args.seed, args.algo
    ))

    # Eval subcommand
    eval_parser = subparsers.add_parser("eval", help="Evaluate variant A")
    eval_parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
        help="Path to the <algo>_final_agent_CDUCAB.pth of a saved pair"
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
