"""Frontier workload synthesizer.

Job-superposition (marked point process) generator for per-rack compute power,
calibrated to a frozen regime-A spec via simulation-based inference (MSM/ABC).

Public API:
    WorkloadConfig, DistSpec       -- generative knobs (theta)           [config.py]
    generate                       -- job-superposition core             [generator.py]
    validate, compute_stats        -- per-trace accept test + stats      [validate.py]
    validate_ensemble, pass_rate   -- MSM objective + shipping gate      [validate.py]
    freeze                         -- re-freeze the spec from the day    [freeze.py]

Typical use:
    from workload_gen import WorkloadConfig, generate, validate_ensemble, pass_rate
    cfg    = WorkloadConfig.regime_A_starting("workload_gen/spec/regime_A.json")
    traces = [generate(cfg, seed=s) for s in range(20)]
    rep    = validate_ensemble(traces, "workload_gen/spec/regime_A.json")  # MSM objective
    rate, _ = pass_rate(traces, "workload_gen/spec/regime_A.json")         # shipping gate

Internals (leading-underscore helpers in each module) are private and may change.
"""

from .config import WorkloadConfig, DistSpec
from .generator import generate
from .validate import validate, validate_ensemble, pass_rate, compute_stats
from .freeze import freeze

__all__ = [
    "WorkloadConfig",
    "DistSpec",
    "generate",
    "validate",
    "validate_ensemble",
    "pass_rate",
    "compute_stats",
    "freeze",
]
