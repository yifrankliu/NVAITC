"""Frontier workload synthesizer.

Job-superposition (marked point process) generator for per-rack compute power,
calibrated to a frozen regime-A spec via simulation-based inference (MSM/ABC).

Public API:
    WorkloadConfig, DistSpec       -- generative knobs (theta)           [config.py]
    generate, job_metrics          -- scheduling core + perf ledger      [generator.py]
    validate, compute_stats        -- per-trace accept test + stats      [validate.py]
    validate_ensemble, pass_rate   -- MSM objective + shipping gate      [validate.py]
    freeze                         -- re-freeze the spec from the day    [freeze.py]
    disaggregate                   -- (T,25) -> FMU exogenous (/9)      [disaggregator.py]
    calibrate                      -- MSM/DE search -> calib JSON        [calibrate.py]
    build_envelope                 -- year xlsx -> spec/envelope.json    [envelope.py]
    deliver                        -- delivery: CSV + .npy + sidecar     [deliver.py]
                                      (envelope/calibrate import lazily -- heavy deps)

Typical use:
    from workload_gen_pipeline import WorkloadConfig, generate, validate_ensemble, pass_rate
    cfg    = WorkloadConfig.regime_A_starting("workload_gen_pipeline/spec/regime_A.json")
    traces = [generate(cfg, seed=s) for s in range(20)]
    rep    = validate_ensemble(traces, "workload_gen_pipeline/spec/regime_A.json")  # MSM objective
    rate, _ = pass_rate(traces, "workload_gen_pipeline/spec/regime_A.json")         # shipping gate

Internals (leading-underscore helpers in each module) are private and may change.
"""

from .config import WorkloadConfig, DistSpec
from .generator import generate, job_metrics
from .validate import validate, validate_ensemble, pass_rate, compute_stats, load_spec
from .freeze import freeze
from .disaggregator import disaggregate

# --- Seed-space partition (2026-08-30) ---------------------------------------
# One generator + one calibration serve calibration, training, AND evaluation;
# an identical (config, seed) pair produces a bit-identical day, so
# "held-out" is enforced at the SEED level. Reserved ranges:
#   0-31          calibration CRN seeds (DE audited these every iteration ->
#                 in-sample; pass rates measured on them read high) [calibrate.py]
#   1000-1039     shipping-gate seeds (fresh-seed pass rate)        [calibrate.py]
#   2000-999_999  TRAINING (RegimeADaySampler)             [ML_algos/data_loader.py]
#   >= 1_000_000  EVAL DELIVERY (held-out test days)                [deliver.py]
# Legacy deliveries at seeds < 2000 (e.g. certified_demo, seed 508) remain
# disjoint from training automatically. Note: held-out synthetic days test
# REALIZATION generalization only (same generator/calibration); the real day
# is the sole distribution-level test.
TRAIN_SEED_RANGE = (2000, 1_000_000)   # [lo, hi)
EVAL_DELIVERY_SEED_MIN = 1_000_000

__all__ = [
    "WorkloadConfig",
    "DistSpec",
    "generate",
    "job_metrics",
    "validate",
    "validate_ensemble",
    "pass_rate",
    "compute_stats",
    "load_spec",
    "freeze",
    "disaggregate",
    "TRAIN_SEED_RANGE",
    "EVAL_DELIVERY_SEED_MIN",
]

# calibrate.py (scipy) and envelope.py (pandas/openpyxl) are import-on-demand:
#   from workload_gen_pipeline.calibrate import calibrate
#   from workload_gen_pipeline.envelope import build_envelope
