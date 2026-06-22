"""Frontier workload synthesizer.

Job-superposition (marked point process) generator for per-rack compute power,
calibrated to a frozen regime-A spec via simulation-based inference (MSM/ABC).

Public API:
    WorkloadConfig, DistSpec   -- generative knobs (theta)         [config.py]
    generate                   -- job-superposition core           [generator.py]
    validate, compute_stats    -- acceptance test + MSM objective  [validate.py]

Typical use:
    from workload_gen import WorkloadConfig, generate, validate
    cfg = WorkloadConfig.regime_A_starting("workload_gen/spec/regime_A.json")
    P   = generate(cfg, seed=0)
    rep = validate(P, "workload_gen/spec/regime_A.json")

Internals (leading-underscore helpers in each module) are private and may change.
"""

from .config import WorkloadConfig, DistSpec
from .generator import generate
from .validate import validate, compute_stats

__all__ = [
    "WorkloadConfig",
    "DistSpec",
    "generate",
    "validate",
    "compute_stats",
]
