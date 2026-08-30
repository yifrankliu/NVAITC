"""
Data loader: CSV + synthetic workload_gen_pipeline -> exogenous traces for FrontierEnv.

Handles loading real Frontier data and optional regime-A synthetic extension.
"""

import csv
import sys
import numpy as np
from pathlib import Path
from typing import Tuple
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

    mean_band_MW: optionally also require the realized daily-mean total power
    (MW) inside [lo, hi] -- the SAME conditioning deliver.py --mean-band applies
    to delivered eval traces, so training and eval days come from one
    conditional distribution ("band both", 2026-08-30). Without it, accepted
    days scatter ~17 +/- 2 MW and ~57% fall outside the eval band.

    Reproducibility: generation seeds advance sequentially from `seed`; every
    accepted (seed, wetbulb) pair is appended to `self.day_log`.

    Seed partition (2026-08-30): training seeds MUST come from
    TRAIN_SEED_RANGE = [2000, 1e6) — disjoint from calibration CRN (0-31),
    gate (1000-1039), and eval-delivery (>= 1e6) seeds — so a delivered
    held-out test day is provably never a training day.
    """

    def __init__(self, seed: int = 2000, wetbulb="replay", require_pass: bool = True,
                 max_tries: int = 100, config_path=None, spec_path=None,
                 mean_band_MW=None):
        from optimal_dc.workload_gen_pipeline import (WorkloadConfig, load_spec,
                                                      TRAIN_SEED_RANGE)

        lo, hi = TRAIN_SEED_RANGE
        if not (lo <= seed < hi):
            raise ValueError(
                f"training sampler seed {seed} is outside the reserved training "
                f"range [{lo}, {hi}): 0-31 are calibration CRN seeds (in-sample, "
                f"overfitted), 1000-1039 gate seeds, >= {hi} eval-delivery seeds "
                f"(held-out test days). Use a seed in [{lo}, {hi}).")
        self._seed_hi = hi

        pipeline = Path(__file__).parents[1] / "workload_gen_pipeline"
        self.config = WorkloadConfig.from_json(config_path or pipeline / "spec" / "regime_A_calib.json")
        self.spec = load_spec(spec_path or pipeline / "spec" / "regime_A.json")
        self.require_pass = require_pass
        self.max_tries = max_tries
        self.mean_band_MW = tuple(mean_band_MW) if mean_band_MW is not None else None
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
            if seed >= self._seed_hi:
                raise RuntimeError(
                    f"training seed stream reached {seed}, the eval-delivery "
                    f"boundary (>= {self._seed_hi} is reserved for held-out test "
                    "days) — should be unreachable in any realistic run")
            P = generate(self.config, seed=seed)
            if self.mean_band_MW is not None:
                m = P.sum(axis=1).mean() / 1e6   # cheap check first, mirrors deliver.py
                if not (self.mean_band_MW[0] <= m <= self.mean_band_MW[1]):
                    continue
            if self.require_pass and not validate(P, self.spec).passed_trace:
                continue
            src, towb = self._towb_pool[self._rng.integers(len(self._towb_pool))]
            exog, _meta = disaggregate_to_fmu(P.astype(np.float32), towb)
            self.day_log.append((seed, src))
            return exog
        raise RuntimeError(
            f"no generated day met the acceptance conditions in {self.max_tries} tries "
            f"(mean_band_MW={self.mean_band_MW}, require_pass={self.require_pass}; "
            "fresh-seed acceptance measured 2026-08-30 on seeds 2000-2099: ~51% "
            "trace-tier alone, ~20-25% with the band — this many straight failures "
            "means a broken config, not bad luck)")
