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

    python -m optimal_dc.ML_algos.benchmarks sanity_eval \
        --checkpoint checkpoints/variant_a/ma_ca_ppo_final_agent_CDUCAB.pth \
        --n_episodes 5 --max_steps 200

sanity_eval reports returns in the checkpoint's OWN training-reward units — a
"did training work" check, not comparable across reward arms. The judged
metric (kWh + violations on a fixed trace) lives in evaluation/rollout.py.
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

from optimal_dc.ML_algos.base_algorithm import RESUME_FILENAME
from optimal_dc.ML_algos.sustainlc_baselines import MA_CA_PPO, MH_MA_CA_PPO
from optimal_dc.ML_algos.unified_mlp import Unified_MLP
from optimal_dc.inherited_FMU_with_modifications.frontier_env_v3 import (
    SmallFrontierModel_v3, MH_SmallFrontierModel_v3,
)

# algo name -> (env class, algorithm class). The three registered algos are the
# two sustain-lc baselines plus the unified single-agent MLP; "unified_mlp"
# wraps the REAL June-2026 Unified_PPO (unified_mlp_baseline.py). (A stub ppo.py
# with a placeholder update rule was deleted 2026-08-28.)
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
                    seed: int = 0, algo: str = "ma_ca_ppo", fresh: bool = False):
    """
    Train variant A (Frontier CSV data source).

    Resumable: learn() snapshots full training state (nets + optimizer +
    action_std + counters + RNG + day-sampler position) to resume_state.pt at
    every episode-end PPO-update boundary. If that file exists in output_dir,
    training AUTO-RESUMES from it toward the same total n_steps — so re-running
    the identical command after a crash/interrupt continues the run (this is
    what train_all.py's retry loop relies on), and the resumed run is
    bit-identical to an uninterrupted one (modulo FMU nondeterminism) at the
    cost of losing at most the steps since the last boundary. The snapshot
    carries a config/seed fingerprint; resuming under a changed config raises
    instead of silently mixing settings. Pass fresh=True to discard the
    snapshot and start over. metadata.json is written only on completion.

    Args:
        config_path: path to hyperparameter YAML
        output_dir: checkpoint directory
        n_steps: TOTAL training steps, not additional (sustain-lc: 3M MA, 5M MH)
        seed: random seed
        algo: "ma_ca_ppo" | "mh_ma_ca_ppo" | "unified_mlp"
        fresh: discard any existing resume_state.pt in output_dir
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

    # Auto-resume from a previous interrupted/crashed run in this output dir
    resume_path = output_dir / RESUME_FILENAME
    resumed_from_step = None
    if resume_path.exists() and fresh:
        resume_path.unlink()
        logger.info("--fresh: discarded existing resume state, starting over")
    if resume_path.exists():
        counters = agent.load_resume_state(resume_path, env=env)
        resumed_from_step = counters.get("time_step", 0)
        logger.info(f"AUTO-RESUMING from step {resumed_from_step} "
                    f"({resume_path.name}; pass --fresh for a clean start)")

    # Train. On KeyboardInterrupt / crash, the last boundary snapshot already
    # on disk is the resume point; re-raise so no metadata.json marks this run
    # complete — re-running the same command continues it.
    logger.info(f"\nTraining for {n_steps} steps...")
    try:
        agent.learn(env, n_steps=n_steps)
        logger.info("Training complete!")
    except KeyboardInterrupt:
        logger.info("Training interrupted -- re-run the same command to "
                    "continue from the last boundary snapshot")
        raise

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
    if resumed_from_step is not None:
        metadata["resumed_from_step"] = resumed_from_step
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


def sanity_eval_variant_a(checkpoint_path: str | Path, n_episodes: int = 5,
                          max_steps: int = None):
    """
    Sanity-check a trained checkpoint: roll it out and report returns in its
    OWN training-reward units plus quick physical summaries. This answers
    "did training achieve what it optimized" — it is NOT the judged
    evaluation (that is evaluation/rollout.py: energy + violations on a fixed
    trace, comparable across all algos and reward arms), and its numbers must
    never be compared across reward arms.

    Args:
        checkpoint_path: path to the <algo>_final_agent_CDUCAB.pth of a pair
        n_episodes: evaluation episodes
        max_steps: steps per episode (default: the config's max_ep_len — a
            full day under the 2026-08-30 protocol; pass ~200 for a quick check)
    """
    logger.info("="*80)
    logger.info("SANITY EVAL (training-reward units; judged metric = evaluation/rollout.py)")
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
    summary = agent.evaluate(env, n_episodes=n_episodes, deterministic=True,
                             max_steps=max_steps)

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
    results_path = checkpoint_path.parent / "sanity_eval_results.json"
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
    train_parser.add_argument(
        "--fresh",
        action="store_true",
        help="Discard any resume_state.pt in the output dir and start over "
             "(default: auto-resume an interrupted run from it)"
    )
    train_parser.set_defaults(func=lambda args: train_variant_a(
        args.config, args.output, args.n_steps, args.seed, args.algo, args.fresh
    ))

    # Sanity-eval subcommand ("eval" kept as a hidden alias for old habits/docs)
    eval_parser = subparsers.add_parser(
        "sanity_eval", aliases=["eval"],
        help="Sanity-check a checkpoint in its own training-reward units "
             "(the judged energy metric lives in evaluation/rollout.py)")
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
    eval_parser.add_argument(
        "--max_steps",
        type=int,
        default=None,
        help="Steps per episode (default: config max_ep_len = a full day; "
             "pass 200 for a quick check)"
    )
    eval_parser.set_defaults(func=lambda args: sanity_eval_variant_a(
        args.checkpoint, args.n_episodes, args.max_steps))

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
