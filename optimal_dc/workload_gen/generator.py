"""Job-superposition core for the Frontier workload synthesizer.

`generate()` produces per-rack COMPUTE POWER only -- a `(n_steps, n_racks)`
array in watts. It does NOT source weather (wet-bulb is joined later in cli.py)
and does NOT disaggregate to FMU channels (disaggregator.py). It is also trace-
agnostic: external HPC priors (PM100/PWA) enter by setting the `DistSpec` knobs
in the WorkloadConfig, never by reaching into a trace here.

Mechanism = marked point process / shot noise (see calibration notes):

    power_r(t) = scale_r * ( floor + sum_j p_j * 1[r in S_j] * 1[t in active_j] ) + noise

Jobs arrive as a homogeneous Poisson process; each carries marks (duration d_j,
size k_j racks, per-rack power p_j, placement S_j). Cross-rack correlation and
the bimodal idle/busy marginal are EMERGENT from job overlap, not stored params.
Pure + fully seeded.
"""

from __future__ import annotations

import numpy as np

from .config import WorkloadConfig, DistSpec

# Arrivals are sampled starting BURN_FACTOR * E[d] before t=0 so jobs already
# running at t=0 are present -- otherwise the early marginal is under-filled and
# the occupancy / correlation stats come out wrong. See generate() step 1.
BURN_FACTOR = 5.0


def _sample(spec: DistSpec, rng: np.random.Generator, size=None):
    """Draw from a DistSpec. This is the sampling deliberately kept out of config."""
    f, p = spec.family, spec.params
    if f == "deterministic":
        return np.full(size, p["value"]) if size is not None else float(p["value"])
    if f == "normal":
        return rng.normal(p["mean"], p["std"], size)
    if f == "lognormal":
        return rng.lognormal(p["mu"], p["sigma"], size)
    if f == "beta":
        return rng.beta(p["a"], p["b"], size)
    raise ValueError(f"unsupported family {f!r}")  # config guards this earlier


def _job_profile(n_active: int) -> np.ndarray:
    """Intra-job power shape over its active steps. Flat for now; swap here for
    ramp-up/down later (a bucket-B / PM100 refinement) without touching generate()."""
    return np.ones(n_active)


def _rack_scales(config: WorkloadConfig, n_racks: int, rng: np.random.Generator) -> np.ndarray:
    """Per-rack hardware scale of length n_racks. Exact spec vector when sizes
    match (regime A); resampled from its empirical distribution for transfer
    experiments (n_racks != 25) so the outlier statistics carry over."""
    scales = np.asarray(config.per_rack_scale, dtype=float)
    if len(scales) == n_racks:
        return scales
    return rng.choice(scales, size=n_racks, replace=True)


def _place(n_racks: int, k: int, placement: str, rng: np.random.Generator) -> np.ndarray:
    """Choose the k racks a job lands on."""
    if placement == "contiguous":
        start = rng.integers(0, n_racks)
        return (start + np.arange(k)) % n_racks  # wrap around
    return rng.choice(n_racks, size=k, replace=False)  # scattered


def generate(
    config: WorkloadConfig,
    n_racks: int = 25,
    n_steps: int = 5761,
    dt: float = 15.0,
    seed: int | None = None,
) -> np.ndarray:
    """Synthesize a per-rack compute-power trace.

    Returns
    -------
    np.ndarray, shape (n_steps, n_racks), dtype float, units WATTS.
    """
    rng = np.random.default_rng(seed)

    # Start every cell at the idle floor; jobs add on top.
    power = np.full((n_steps, n_racks), config.idle_floor_W, dtype=float)

    # --- 1. sample the job stream over [-burn, T] (homogeneous Poisson) ---
    T = n_steps * dt
    burn = BURN_FACTOR * config.duration.mean
    expected = config.arrival_rate_per_s * (T + burn)
    n_jobs = rng.poisson(expected)
    arrivals = rng.uniform(-burn, T, size=n_jobs)

    # --- 2. for each job, draw marks and superpose ---
    for t_j in arrivals:
        d_j = _sample(config.duration, rng)              # seconds
        frac = _sample(config.job_size, rng)             # fraction of machine
        k_j = max(1, min(n_racks, int(round(frac * n_racks))))
        p_j = _sample(config.job_power, rng)             # per-rack watts (per-job scalar)
        racks = _place(n_racks, k_j, config.placement, rng)

        s0 = max(0, int(np.ceil(t_j / dt)))
        s1 = min(n_steps, int(np.ceil((t_j + d_j) / dt)))
        if s1 <= s0:
            continue
        power[s0:s1][:, racks] += p_j * _job_profile(s1 - s0)[:, None]

    # --- 3. per-rack hardware scale, noise, floor at zero ---
    power *= _rack_scales(config, n_racks, rng)[None, :]
    if config.noise_amp_W > 0:
        power += rng.normal(0.0, config.noise_amp_W, power.shape)
    np.maximum(power, 0.0, out=power)

    return power
