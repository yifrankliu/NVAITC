"""Generative knobs for the Frontier workload synthesizer.

`WorkloadConfig` is the calibration target `theta` in

    theta* = argmin_theta  || s(generate(theta)) - s(real) ||

It holds ONLY the statistical knobs the generator draws from. Output *shape*
(`n_racks`, `n_steps`, `seed`) is passed to `generate()` directly, never stored
here, so the same config generates 25 / 50 / 100 racks for transfer experiments.

This is the generative counterpart to `spec/regime_A.json` (descriptive targets
you validate against). Different files, different numbers, different roles:
  - spec   = what a faithful trace must look like (frozen acceptance test)
  - config = the knobs you tune until the trace passes that test

Each knob is tagged by where its value comes from (the three-way split):
  (A) pinned by the frozen spec / Frontier specs  -> recoverable from regime A
  (B) needs external HPC priors (PM100/PWA/F-DATA) -> flat directions at rank-1
  (C) forward-synthesized, loyal to Frontier       -> never imported from traces

Calibration is simulation-based (MSM/ABC), not gradient training: the point
process has an intractable likelihood, so `validate.py` measures output stats vs
the frozen spec and you search this small knob space.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Distribution families the generator knows how to sample. Kept here so the
# config can fail fast on an unknown family instead of deep inside generate().
KNOWN_FAMILIES = {"deterministic", "normal", "lognormal", "beta"}

# Names of the WorkloadConfig fields that are DistSpec (used by JSON round-trip).
_DIST_FIELDS = ("duration", "job_size", "job_power")


@dataclass
class DistSpec:
    """A swappable parametric distribution: a family name + its parameters.

    Keeping the family itself a field is what lets regime B replace a *shape*
    (placeholder -> PM100-fitted) without changing the config schema. The
    generator dispatches on `family`; this object stays pure data.

    Conventions for `params` per family:
      deterministic : {"value": x}
      normal        : {"mean": m, "std": s}
      lognormal     : {"mu": mu, "sigma": sigma}   # of the underlying normal
      beta          : {"a": a, "b": b}             # support (0, 1)
    """

    family: str
    params: dict

    def __post_init__(self) -> None:
        if self.family not in KNOWN_FAMILIES:
            raise ValueError(
                f"unknown distribution family {self.family!r}; "
                f"expected one of {sorted(KNOWN_FAMILIES)}"
            )
        if not isinstance(self.params, dict):
            raise TypeError(f"DistSpec.params must be a dict, got {type(self.params)}")

    @property
    def mean(self) -> float:
        """Closed-form mean, for sanity-checking a config against the spec."""
        p = self.params
        if self.family == "deterministic":
            return float(p["value"])
        if self.family == "normal":
            return float(p["mean"])
        if self.family == "lognormal":
            import math

            return math.exp(p["mu"] + p["sigma"] ** 2 / 2.0)
        if self.family == "beta":
            return p["a"] / (p["a"] + p["b"])
        raise AssertionError("unreachable")  # guarded by __post_init__


@dataclass
class WorkloadConfig:
    """All generative knobs for one workload regime.

    Build regime A by calibrating these to `spec/regime_A.json`; build regime B
    by widening the shift-axis knobs (job_size spread, duration tail, burstiness,
    mean load) and re-using the identical generator code.
    """

    # --- (A) marginal level, pinned by spec / Frontier hardware ---
    idle_floor_W: float
    """Per-rack baseline power when no job runs. spec.marginal.idle_floor_W (~253 kW)."""

    per_rack_scale: list[float]
    """Per-rack multiplicative scale (hardware homogeneity). spec.marginal.per_rack_scale;
    rack 14 is the 0.652 outlier. Length must match n_racks at generate() time
    (or be tiled/regenerated for n_racks != len)."""

    job_power: DistSpec
    """Per-rack power added by one active job. Mean ~= busy - floor ~= 756 kW.
    Tight spread keeps the marginal sharply bimodal (idle ~0.25 / busy ~1.0 MW)."""

    # --- arrival + duration (A: occupancy via lambda*E[d], scale via tau) ---
    arrival_rate_per_s: float
    """Job arrival rate lambda (jobs/second), Poisson at regime A. Start from the
    occupancy constraint lambda*E[d] ~= ln2 ~= 0.69 and E[d] ~= tau = 2610 s
    -> lambda ~= 2.6e-4 /s (~23 jobs/day). A calibration start, not a fixed value."""

    duration: DistSpec
    """Job duration (seconds). Mean E[d] pinned by autocorr tau (174 steps = 2610 s);
    the TAIL SHAPE is bucket B (PM100/PWA) and only matters for ramps / regime B."""

    # --- (B) shift axes needing external priors (placeholder shapes for now) ---
    burstiness: float = 0.0
    """Arrival clustering beyond Poisson. 0.0 = pure Poisson (regime A). Reserved
    for regime B (e.g. Hawkes / negative-binomial arrivals); a no-op while 0."""

    # --- (C) co-placement / synchronization, forward-synthesized to spec ---
    job_size: DistSpec = field(
        default_factory=lambda: DistSpec("beta", {"a": 40.0, "b": 1.5})
    )
    """Job size as a FRACTION of the machine (then * n_racks, rounded, >=1). This is
    THE synchronization knob: concentrated near 1.0 -> full-machine gang -> the
    0.994 cross-rack correlation. NEVER collapse to a constant (the rank-1 trap);
    widening its spread is how regime B desynchronizes for the GNN experiment."""

    placement: str = "scattered"
    """How a job's racks are chosen: 'scattered' (uniform subset) or 'contiguous'
    (a block). Matters for residual block structure (none on the real day)."""

    # --- (A) residual noise ---
    noise_amp_W: float = 0.0
    """Std of additive per-rack Gaussian noise (W). Calibrate to the residual
    scatter left after the job superposition; keep small."""

    def __post_init__(self) -> None:
        if self.idle_floor_W < 0:
            raise ValueError("idle_floor_W must be >= 0")
        if self.noise_amp_W < 0:
            raise ValueError("noise_amp_W must be >= 0")
        if self.arrival_rate_per_s <= 0:
            raise ValueError("arrival_rate_per_s must be > 0")
        if self.burstiness < 0:
            raise ValueError("burstiness must be >= 0")
        if self.placement not in ("scattered", "contiguous"):
            raise ValueError(
                f"placement must be 'scattered' or 'contiguous', got {self.placement!r}"
            )
        if not self.per_rack_scale or any(s <= 0 for s in self.per_rack_scale):
            raise ValueError("per_rack_scale must be non-empty and all > 0")
        for name in _DIST_FIELDS:
            if not isinstance(getattr(self, name), DistSpec):
                raise TypeError(f"{name} must be a DistSpec")
        # job_size is a fraction in (0, 1]; flag obviously broken means early.
        if not (0.0 < self.job_size.mean <= 1.0):
            raise ValueError(
                f"job_size mean (fraction of machine) must be in (0, 1], "
                f"got {self.job_size.mean:.3f}"
            )

    # ------------------------------------------------------------------ IO ---
    def to_json(self, path: str | Path) -> None:
        """Dump to JSON so each regime is a committed, diffable artifact."""
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> "WorkloadConfig":
        """Load a regime config, reconstructing the nested DistSpec fields."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for name in _DIST_FIELDS:
            if name in data and isinstance(data[name], dict):
                data[name] = DistSpec(**data[name])
        return cls(**data)

    # ----------------------------------------------------- starting config ---
    @classmethod
    def regime_A_starting(cls, spec_path: str | Path) -> "WorkloadConfig":
        """Build a CALIBRATION STARTING POINT for regime A from the frozen spec.

        Bucket-A knobs (floor, per-rack scale, job-power level) are read straight
        from the spec; arrival/duration are seeded from the MEAN and tau
        constraints. These are starting values for the MSM/ABC search, NOT the
        calibrated answer -- run generate() -> validate.py and adjust.
        """
        import math

        spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
        marg = spec["marginal"]
        floor = float(marg["idle_floor_W"])
        busy = float(marg["busy_level_W"])
        grand_mean = float(marg["grand_mean_W"])
        job_power_mean = busy - floor

        # E[d] ~= tau (1/e autocorrelation), converted steps -> seconds.
        tau_steps = float(spec["temporal"]["autocorr_1e_tau_steps"])
        dt_s = float(spec["meta"]["dt_s"])
        mean_dur_s = tau_steps * dt_s  # 174 * 15 = 2610 s
        # lognormal placeholder shape (sigma is bucket B; refine from PM100).
        sigma = 0.7
        mu = math.log(mean_dur_s) - sigma ** 2 / 2.0

        # job size as a fraction of the machine (near full-machine for regime A).
        a_size, b_size = 40.0, 1.5
        frac_mean = a_size / (a_size + b_size)  # E[job_size_frac] ~= 0.964

        # Seed arrival rate from the MEAN constraint, NOT busy-fraction. The M/G/inf
        # mean is  E[power_r] = floor + occupancy * job_power_mean, so to hit
        # grand_mean we need occupancy = (grand_mean - floor) / job_power_mean; and
        # per-rack occupancy = lambda * E[job_size_frac] * E[d]. (Deriving lambda from
        # busy-fraction = 0.5 -> ln2 instead overshoots the mean by ~18%; the mean
        # and busy-fraction constraints are not mutually consistent under this model.)
        occupancy = (grand_mean - floor) / job_power_mean
        lam = occupancy / (frac_mean * mean_dur_s)

        return cls(
            idle_floor_W=floor,
            per_rack_scale=list(marg["per_rack_scale"]),
            job_power=DistSpec("normal", {"mean": job_power_mean, "std": 0.05 * job_power_mean}),
            arrival_rate_per_s=lam,
            duration=DistSpec("lognormal", {"mu": mu, "sigma": sigma}),
            burstiness=0.0,
            job_size=DistSpec("beta", {"a": a_size, "b": b_size}),  # mean ~0.96 -> near full-machine
            placement="scattered",
            noise_amp_W=0.0,
        )
