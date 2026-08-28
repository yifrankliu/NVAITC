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
    from workload_gen import WorkloadConfig, generate, validate_ensemble, pass_rate
    cfg    = WorkloadConfig.regime_A_starting("workload_gen/spec/regime_A.json")
    traces = [generate(cfg, seed=s) for s in range(20)]
    rep    = validate_ensemble(traces, "workload_gen/spec/regime_A.json")  # MSM objective
    rate, _ = pass_rate(traces, "workload_gen/spec/regime_A.json")         # shipping gate

Internals (leading-underscore helpers in each module) are private and may change.
"""

from .config import WorkloadConfig, DistSpec
from .generator import generate, job_metrics
from .validate import validate, validate_ensemble, pass_rate, compute_stats
from .freeze import freeze
from .disaggregator import disaggregate

__all__ = [
    "WorkloadConfig",
    "DistSpec",
    "generate",
    "job_metrics",
    "validate",
    "validate_ensemble",
    "pass_rate",
    "compute_stats",
    "freeze",
    "disaggregate",
]

# calibrate.py (scipy) and envelope.py (pandas/openpyxl) are import-on-demand:
#   from workload_gen.calibrate import calibrate
#   from workload_gen.envelope import build_envelope
