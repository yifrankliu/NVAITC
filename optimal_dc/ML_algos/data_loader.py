"""
Data loader: CSV + synthetic workload_gen_pipeline -> exogenous traces for FrontierEnv.

Handles loading real Frontier data and optional regime-A synthetic extension.
"""

import csv
import sys
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

# Repo root (NVAITC/) so `optimal_dc.*` namespace imports resolve when this
# module is loaded standalone (there is no optimal_dc/__init__.py).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logger = logging.getLogger(__name__)


def load_frontier_csv(csv_path: str | Path) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Load Frontier power CSV.

    Args:
        csv_path: path to input_04-07-24.csv

    Returns:
        P: (n_steps, 25) per-CDU-group power in watts
        towb: (n_steps,) wet-bulb temperature in Celsius
        dt: timestep in seconds
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    logger.info(f"Loading Frontier CSV: {csv_path}")

    with open(csv_path, newline="") as f:
        rows = list(csv.reader(f))

    hdr = rows[0]
    p_idx = [i for i, h in enumerate(hdr) if h.startswith("power")]
    t_idx = hdr.index("time")
    towb_idx = hdr.index("OA Wetbulb Temp")

    P = np.array([[float(r[i]) for i in p_idx] for r in rows[1:]], dtype=np.float32)
    t = np.array([float(r[t_idx]) for r in rows[1:]])
    towb = np.array([float(r[towb_idx]) for r in rows[1:]], dtype=np.float32)

    dt = float(np.unique(np.diff(t))[0])
    logger.info(f"Loaded: {P.shape[0]} steps, {P.shape[1]} CDU groups, dt={dt}s, towb range {towb.min():.1f}–{towb.max():.1f}°C")

    return P, towb, dt


def disaggregate_to_fmu(
    P: np.ndarray,
    towb_C: np.ndarray,
    selected_columns: list = None,
    branch_split: str = "equal",
    towb_offset_K: float = 15.0,
) -> Tuple[np.ndarray, dict]:
    """
    Disaggregate per-CDU power to per-blade-group + wet-bulb (FMU inputs).

    Thin wrapper around the canonical workload_gen_pipeline.disaggregator (/9
    convention). Do NOT reimplement the divisor here: np.repeat copies, it does
    not divide, and a /3-only version runs the FMU 3x too hot.

    Args:
        P: (n_steps, 25) per-CDU power in watts
        towb_C: (n_steps,) wet-bulb in Celsius
        selected_columns: which 5 CDU columns to use (default: first5)
        branch_split: "equal" (only option for now)
        towb_offset_K: CT offset (default: 15 K)

    Returns:
        exog: (n_steps, 16) blade-group power + towb in kelvin
        meta: disaggregation metadata (canonical sidecar dict + n_steps)
    """
    from optimal_dc.workload_gen_pipeline.disaggregator import disaggregate

    slice_mode = "first5" if selected_columns is None else list(selected_columns)
    logger.info(f"Disaggregating to FMU inputs: slice_mode={slice_mode}, branch_split={branch_split}")

    exog, meta = disaggregate(
        P,
        towb_C,
        slice_mode=slice_mode,
        branch_split=branch_split,
        towb_offset_K=towb_offset_K,
    )
    exog = exog.astype(np.float32)
    meta = {**meta, "n_steps": exog.shape[0]}

    logger.info(f"Disaggregated: {exog.shape} exogenous trace ({meta['convention']})")
    return exog, meta


def generate_regime_a_synthetic(
    n_days: int = 2,
    n_racks: int = 25,
    seed: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate regime-A synthetic workload + constant wet-bulb.

    Args:
        n_days: number of synthetic days to generate
        n_racks: 25 CDU groups
        seed: RNG seed

    Returns:
        P_syn: (T, 25) synthetic per-CDU power
        towb_syn: (T,) constant wet-bulb in Celsius (~15.6°C, the real day's mean)
    """
    try:
        from optimal_dc.workload_gen_pipeline import generate, WorkloadConfig
    except ImportError:
        logger.error("workload_gen_pipeline not importable; ensure the repo root (NVAITC/) is on sys.path")
        raise

    logger.info(f"Generating {n_days} synthetic regime-A days (seed={seed})")

    spec_path = Path(__file__).parents[1] / "workload_gen_pipeline/spec/regime_A.json"

    # Load calibrated config; fall back to the spec-derived starting config
    config_path = Path(__file__).parents[1] / "workload_gen_pipeline/spec/regime_A_calib.json"
    if config_path.exists():
        config = WorkloadConfig.from_json(config_path)
    else:
        logger.warning(f"regime_A_calib.json not found at {config_path}; "
                       "falling back to regime_A_starting (uncalibrated)")
        config = WorkloadConfig.regime_A_starting(spec_path)

    # Generate N independent days
    n_steps_per_day = 5761  # 24h at 15s resolution
    P_list = []
    for day_idx in range(n_days):
        day_seed = seed + day_idx * 1000  # independent seed per day
        P_day = generate(config, n_racks=n_racks, n_steps=n_steps_per_day, seed=day_seed)
        P_list.append(P_day)

    P_syn = np.concatenate(P_list, axis=0)  # (T*n_days, 25)

    # Constant wet-bulb (typical Frontier facility, ~60°F = 15.6°C)
    # Use the mean from the real day for consistency
    towb_syn = np.full(P_syn.shape[0], 15.6, dtype=np.float32)

    logger.info(f"Generated {P_syn.shape[0]} synthetic steps ({n_days} days)")
    return P_syn, towb_syn


class RegimeADaySampler:
    """Draw a fresh certified regime-A day per call -> (5761, 16) FMU trace.

    The per-reset day source for train-on-synthetic: each call generates a new
    day (new seed), optionally rejection-samples until it passes every
    trace-tier spec check (same ABC-accept framing as deliver.py
    --require-pass), and disaggregates at the canonical /9. The policy
    therefore never sees the same trajectory twice.

    Wet-bulb (`wetbulb`):
      "replay"            -- the real 2024-04-07 facility column (default)
      "noaa:YYYY-MM-DD"   -- one KTYS day via workload_gen_pipeline.weather
      ["noaa:...", ...]   -- a pool; one entry drawn uniformly per day

    Reproducibility: generation seeds advance sequentially from `seed`; every
    accepted (seed, wetbulb) pair is appended to `self.day_log`.
    """

    def __init__(self, seed: int = 0, wetbulb="replay", require_pass: bool = True,
                 max_tries: int = 40, config_path=None, spec_path=None):
        from optimal_dc.workload_gen_pipeline import WorkloadConfig, load_spec

        pipeline = Path(__file__).parents[1] / "workload_gen_pipeline"
        self.config = WorkloadConfig.from_json(config_path or pipeline / "spec" / "regime_A_calib.json")
        self.spec = load_spec(spec_path or pipeline / "spec" / "regime_A.json")
        self.require_pass = require_pass
        self.max_tries = max_tries
        self._next_seed = seed
        self._rng = np.random.default_rng(seed)
        self.day_log: list = []

        sources = [wetbulb] if isinstance(wetbulb, str) else list(wetbulb)
        self._towb_pool = [(src, self._resolve_wetbulb(src)) for src in sources]

    def _resolve_wetbulb(self, src: str) -> np.ndarray:
        if src == "replay":
            _P, towb, _dt = load_frontier_csv(
                Path(__file__).parents[1] / "external/sustain-lc/input_04-07-24.csv")
            return towb
        if src.startswith("noaa:"):
            from optimal_dc.workload_gen_pipeline.weather import wetbulb_for
            return np.asarray(wetbulb_for(src.split(":", 1)[1]), dtype=np.float32)
        raise ValueError(f"unknown wetbulb source {src!r}")

    def __call__(self) -> np.ndarray:
        from optimal_dc.workload_gen_pipeline import generate, validate

        for _ in range(self.max_tries):
            seed = self._next_seed
            self._next_seed += 1
            P = generate(self.config, seed=seed)
            if self.require_pass and not validate(P, self.spec).passed_trace:
                continue
            src, towb = self._towb_pool[self._rng.integers(len(self._towb_pool))]
            exog, _meta = disaggregate_to_fmu(P.astype(np.float32), towb)
            self.day_log.append((seed, src))
            return exog
        raise RuntimeError(
            f"no generated day passed trace-tier checks in {self.max_tries} tries "
            "(acceptance is ~48%; this indicates a broken config, not bad luck)")


def load_data_variant_a(
    csv_path: str | Path = None,
    n_synthetic_days: int = 2,
    train_frac: float = 0.67,
    stacking: str = "regime_a_synthetic",
    seed: int = 0,
) -> dict:
    """
    Load variant A data: real Frontier CSV + regime-A synthetic.

    Args:
        csv_path: path to Frontier CSV (default: standard location)
        n_synthetic_days: how many regime-A days to append
        train_frac: fraction of data for training (rest for eval)
        stacking: "none" | "regime_a_synthetic" (how to combine real + synthetic)
        seed: random seed for synthetic generation

    Returns:
        {
            'train': {
                'power': (T_train, 16) exogenous trace,
                'steps': T_train
            },
            'eval': {
                'power': (T_eval, 16) exogenous trace,
                'steps': T_eval
            },
            'meta': metadata dict
        }
    """
    if csv_path is None:
        # this file is optimal_dc/ML_algos/data_loader.py -> parents[1] is optimal_dc/
        csv_path = Path(__file__).parents[1] / "external/sustain-lc/input_04-07-24.csv"

    logger.info(f"Loading variant A data (stacking={stacking})")

    # Load real Frontier data
    P_real, towb_real, dt = load_frontier_csv(csv_path)

    # Disaggregate real data
    exog_real, meta_real = disaggregate_to_fmu(P_real, towb_real)

    if stacking == "none":
        # Use only real data
        exog = exog_real
        n_real_days = 1
        n_synthetic_days_used = 0

    elif stacking == "regime_a_synthetic":
        # Append synthetic regime-A days
        P_syn, towb_syn = generate_regime_a_synthetic(n_days=n_synthetic_days, seed=seed)
        exog_syn, _ = disaggregate_to_fmu(P_syn, towb_syn)
        exog = np.concatenate([exog_real, exog_syn], axis=0)
        n_real_days = 1
        n_synthetic_days_used = n_synthetic_days

    else:
        raise ValueError(f"Unknown stacking: {stacking}")

    # Split into train/eval
    n_total = exog.shape[0]
    n_train = int(n_total * train_frac)

    exog_train = exog[:n_train]
    exog_eval = exog[n_train:]

    logger.info(f"Split: {exog_train.shape[0]} train, {exog_eval.shape[0]} eval steps")

    data = {
        "train": {
            "power": exog_train,
            "steps": exog_train.shape[0],
        },
        "eval": {
            "power": exog_eval,
            "steps": exog_eval.shape[0],
        },
        "meta": {
            "variant": "a_frontier_regime_a",
            "stacking": stacking,
            "n_real_days": n_real_days,
            "n_synthetic_days": n_synthetic_days_used,
            "total_days": n_real_days + n_synthetic_days_used,
            "train_frac": train_frac,
            "dt_s": dt,
            **meta_real,
        },
    }

    return data
