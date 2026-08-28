"""Job-superposition core for the Frontier workload synthesizer.

`generate()` produces per-rack COMPUTE POWER only -- a `(n_steps, n_racks)`
array in watts. It does NOT source weather (wet-bulb is joined in deliver.py)
and does NOT disaggregate to FMU channels (disaggregator.py). It is also trace-
agnostic: external HPC priors (PM100/PWA) enter by setting the `DistSpec` knobs
in the WorkloadConfig, never by reaching into a trace here.

Mechanism = marked point process under a CAPACITY CONSTRAINT (blocking, not
clipping -- power is always the honest sum of jobs actually running):

    power_r(t) = scale_r * ( floor + sum_j c_j(t) * 1[r in S_j] ) + noise
    c_j(t)     = ( p_j + w_shared_j(t) + w_idio_jr(t) ) * env_j(t)

Jobs arrive as a homogeneous Poisson process and are SCHEDULED in arrival order
against a per-rack availability clock (at most one job per rack):
  - 'queue' (default): FCFS gang scheduling, job waits until its k racks are
    simultaneously free (what Slurm does; work-conserving, so
    busy_frac = lambda*E[frac]*E[d] for offered load < 1);
  - 'loss': job is dropped if blocked at arrival (Erlang-B: a/(1+a)).
No backfill: a small job cannot jump the queue (EASY-backfill = later knob;
utilization runs slightly below a real scheduler's at equal lambda).

Each job carries marks (duration d_j, size k_j racks, per-rack power p_j,
placement S_j) plus intra-job dynamics:
  - env_j: linear ramp-up/-down envelope over `ramp_time_s` (flat pulses are
    impossible -- a single-step 756 kW edge exceeds the day's observed max);
  - w_shared: AR(1) power wander COMMON to all the job's racks (gang-
    synchronized MPI phases) -- the ramp-coincidence knob;
  - w_idio: independent AR(1) wander per rack.

Cross-rack correlation, the bimodal marginal, ramp statistics, and the peak
ceiling are all EMERGENT from job overlap + blocking, not stored params.
Pure + fully seeded.
"""

from __future__ import annotations

import numpy as np

from .config import WorkloadConfig, DistSpec

# Arrivals are sampled starting BURN_FACTOR * E[d] before t=0 so jobs already
# running at t=0 are present AND the queue state is warm -- otherwise the early
# marginal is under-filled and occupancy / correlation stats come out wrong.
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


def _job_envelope(n_active: int, ramp_steps: int) -> np.ndarray:
    """Intra-job power envelope in [0, 1]: linear ramp-up over `ramp_steps`,
    flat plateau, linear ramp-down. Short jobs get a symmetric triangle."""
    env = np.ones(n_active)
    r = min(ramp_steps, n_active // 2)
    if r > 0:
        ramp = np.arange(1, r + 1) / r
        env[:r] = ramp
        env[n_active - r:] = ramp[::-1]
    return env


def _ar1(n: int, k: int | None, phi: float, sigma: float,
         rng: np.random.Generator) -> np.ndarray:
    """Stationary zero-mean AR(1) with marginal std `sigma`, over n steps.
    k=None -> shape (n,); else shape (n, k) of k independent paths."""
    shape = (n,) if k is None else (n, k)
    if sigma <= 0 or n == 0:
        return np.zeros(shape)
    innov_sd = sigma * np.sqrt(1.0 - phi ** 2)
    x = np.empty(shape)
    x[0] = rng.normal(0.0, sigma, size=None if k is None else k)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal(0.0, innov_sd, size=None if k is None else k)
    return x


def _rack_scales(config: WorkloadConfig, n_racks: int, rng: np.random.Generator) -> np.ndarray:
    """Per-rack hardware scale of length n_racks. Exact spec vector when sizes
    match (regime A); resampled from its empirical distribution for transfer
    experiments (n_racks != 25) so the outlier statistics carry over."""
    scales = np.asarray(config.per_rack_scale, dtype=float)
    if len(scales) == n_racks:
        return scales
    return rng.choice(scales, size=n_racks, replace=True)


def _place(free: np.ndarray, k: int, placement: str, rng: np.random.Generator) -> np.ndarray:
    """Choose the k racks a job lands on, from the currently FREE racks.
    'contiguous' = a contiguous window of the sorted free list (contiguity
    among free racks, not guaranteed physical adjacency under fragmentation)."""
    if placement == "contiguous":
        start = rng.integers(0, free.size - k + 1)
        return free[start:start + k]
    return rng.choice(free, size=k, replace=False)  # scattered


def generate(
    config: WorkloadConfig,
    n_racks: int = 25,
    n_steps: int = 5761,
    dt: float = 15.0,
    seed: int | None = None,
    return_jobs: bool = False,
):
    """Synthesize a per-rack compute-power trace.

    Returns
    -------
    np.ndarray, shape (n_steps, n_racks), dtype float, units WATTS.
    If `return_jobs`, returns (power, jobs) where jobs is the scheduling ledger:
    a list of dicts with t_arrival, t_start, wait_s, duration_s, k, p_W, racks,
    dropped -- feed it to `job_metrics()` for utilization / wait / slowdown.
    """
    rng = np.random.default_rng(seed)

    # Start every cell at the idle floor; jobs add on top.
    power = np.full((n_steps, n_racks), config.idle_floor_W, dtype=float)

    # --- 1. sample the job stream over [-burn, T] (homogeneous Poisson) ---
    T = n_steps * dt
    burn = BURN_FACTOR * config.duration.mean
    expected = config.arrival_rate_per_s * (T + burn)
    n_jobs = rng.poisson(expected)
    # SORTED: scheduling is stateful, jobs must be processed in arrival order
    arrivals = np.sort(rng.uniform(-burn, T, size=n_jobs))

    ramp_steps = max(0, int(round(config.ramp_time_s / dt)))
    sig_shared = config.wander_std_W * np.sqrt(config.wander_shared_frac)
    sig_idio = config.wander_std_W * np.sqrt(1.0 - config.wander_shared_frac)

    # --- 2. schedule (blocking) + superpose, in arrival order ---
    rack_free = np.full(n_racks, -np.inf)  # time each rack becomes free
    jobs: list[dict] = []
    for t_arr in arrivals:
        d_j = float(_sample(config.duration, rng))       # seconds
        frac = float(_sample(config.job_size, rng))      # fraction of machine
        k_j = max(1, min(n_racks, int(round(frac * n_racks))))
        p_j = float(_sample(config.job_power, rng))      # per-rack watts

        # earliest time k_j racks are simultaneously free: k-th order statistic
        # of rack_free (already accounts for every earlier job -- FCFS, no
        # backfill, so no separate event queue is needed)
        t_ready = np.partition(rack_free, k_j - 1)[k_j - 1]
        if config.discipline == "loss" and t_ready > t_arr:
            jobs.append(dict(t_arrival=t_arr, t_start=np.nan, wait_s=np.nan,
                             duration_s=d_j, k=k_j, p_W=p_j, racks=None, dropped=True))
            continue
        t_start = max(t_arr, t_ready)

        free = np.nonzero(rack_free <= t_start)[0]       # >= k_j by construction
        racks = _place(free, k_j, config.placement, rng)
        rack_free[racks] = t_start + d_j
        jobs.append(dict(t_arrival=t_arr, t_start=t_start, wait_s=t_start - t_arr,
                         duration_s=d_j, k=k_j, p_W=p_j, racks=racks, dropped=False))

        # active step window in ABSOLUTE step indices (may start before 0)
        a0 = int(np.ceil(t_start / dt))
        a1 = int(np.ceil((t_start + d_j) / dt))
        s0, s1 = max(0, a0), min(n_steps, a1)
        if s1 <= s0:
            continue  # sub-step job or entirely outside the window

        n_active = a1 - a0
        env = _job_envelope(n_active, ramp_steps)
        w_sh = _ar1(n_active, None, config.wander_phi, sig_shared, rng)
        w_id = _ar1(n_active, k_j, config.wander_phi, sig_idio, rng)
        # wander scales with the envelope too: suppressed during ramps, so
        # edge slew stays p/R-shaped and power is continuous at the edges
        seg = (p_j + w_sh[:, None] + w_id) * env[:, None]
        power[s0:s1, racks] += seg[s0 - a0: s1 - a0]

    # --- 3. per-rack hardware scale, residual noise, floor at zero ---
    power *= _rack_scales(config, n_racks, rng)[None, :]
    if config.noise_amp_W > 0:
        power += rng.normal(0.0, config.noise_amp_W, power.shape)
    np.maximum(power, 0.0, out=power)

    return (power, jobs) if return_jobs else power


def job_metrics(jobs: list[dict], n_racks: int, T_s: float) -> dict:
    """Power-use vs performance accounting over the visible window [0, T_s].

    utilization : delivered node-seconds / (n_racks * T_s)  -- vs offered load
    wait/slowdown over jobs ARRIVING in [0, T_s] (bounded slowdown, the
    standard HPC scheduling metric); loss_rate for the 'loss' discipline.
    Not a reward term: the workload is exogenous to the cooling controller.
    This ledger is generator diagnostics now, Pareto instrumentation later
    (power capping / thermal-aware scheduling extensions).
    """
    delivered = 0.0
    for j in jobs:
        if j["dropped"] or j["t_start"] is None:
            continue
        lo = max(0.0, j["t_start"])
        hi = min(T_s, j["t_start"] + j["duration_s"])
        if hi > lo:
            delivered += j["k"] * (hi - lo)

    win = [j for j in jobs if 0.0 <= j["t_arrival"] <= T_s]
    ran = [j for j in win if not j["dropped"]]
    waits = np.array([j["wait_s"] for j in ran]) if ran else np.array([0.0])
    slowdowns = (np.array([(j["wait_s"] + j["duration_s"]) / j["duration_s"] for j in ran])
                 if ran else np.array([1.0]))
    offered = sum(j["k"] * j["duration_s"] for j in win)

    return {
        "n_arrived": len(win),
        "n_dropped": sum(j["dropped"] for j in win),
        "loss_rate": (sum(j["dropped"] for j in win) / len(win)) if win else 0.0,
        "utilization": delivered / (n_racks * T_s),
        "offered_load": offered / (n_racks * T_s),
        "wait_mean_s": float(waits.mean()),
        "wait_p95_s": float(np.percentile(waits, 95)),
        "slowdown_mean": float(slowdowns.mean()),
    }
