"""MSM calibration driver: search the shape knobs until the ensemble passes.

    theta* = argmin_theta  Q( mean_seeds s(generate(theta)) , s(real) )

Method notes (why each choice):
  - ENSEMBLE objective (`validate_ensemble`, N seeds): single-seed Q is
    realization-noise dominated (~8-20 jobs/day); averaging stats over N=20
    puts stat noise ~4%, below the tightest tolerance, so Q responds to theta.
  - COMMON RANDOM NUMBERS: the same seed list is used for every theta, so the
    objective surface is deterministic and DE compares thetas, not luck draws
    (standard MSM variance reduction).
  - LAMBDA IS NOT SEARCHED: it is re-derived each eval from the mean
    constraint (two-stage pinning). Queue discipline is work-conserving, so
      lambda = busy_frac_target / (E[frac] * E[d]),
      busy_frac_target = (grand_mean - floor) / E[p]
    with an empirical horizon-loss correction factor: FCFS waits push some
    delivered work past the finite window, so lambda is inflated by
    LAMBDA_HORIZON_BOOST (fit once at the starting theta; DE absorbs residue).
  - OBJECTIVE = Q_feasible + 0.01 * Q_faithful: feasibility first (0 exactly
    when every check passes), faithfulness as the tie-break gradient so the
    search keeps improving inside the feasible set.
  - SHIP GATE is pass_rate >= 0.8 on FRESH seeds (never the CRN seeds), so the
    reported number is out-of-sample w.r.t. the search.

Usage:
    python -m optimal_dc.workload_gen_pipeline.calibrate            # full search (~10-15 min)
    python -m optimal_dc.workload_gen_pipeline.calibrate --quick    # smoke search (~2 min)
Writes spec/regime_A_calib.json including a _provenance block.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

from .config import WorkloadConfig, DistSpec
from .generator import generate
from .validate import load_spec, validate_ensemble, pass_rate

_SPEC = Path(__file__).parent / "spec" / "regime_A.json"
_OUT = Path(__file__).parent / "spec" / "regime_A_calib.json"

N_SEEDS = 32                 # CRN ensemble size per objective eval (raised 20->32: 20 was few enough for DE to overfit seed quirks -- CRN 80% vs fresh 40%)
GATE_SEEDS = range(1000, 1040)   # fresh seeds for the ship gate (out-of-sample)
LAMBDA_HORIZON_BOOST = 1.10  # delivered/offered shortfall at start theta (~0.49/0.547)

# search space: (name, lo, hi, log-scale?) -- lambda deliberately absent
BOUNDS = [
    ("dur_mean_s",        1200.0, 20000.0, True),   # E[d]; tau band is the constraint
    ("dur_sigma",         0.3,    1.5,     False),  # lognormal shape (bucket B)
    ("power_std_frac",    0.01,   0.15,    False),  # p_j spread / mean
    ("size_a",            2.0,    300.0,   True),   # job-size beta(a, b)
    ("size_b",            0.5,    20.0,    True),
    ("ramp_time_s",       15.0,   600.0,   True),   # edge slew
    ("wander_std_W",      5e3,    1.5e5,   True),   # within-job wander
    ("wander_phi",        0.5,    0.99,    False),
    ("wander_shared_frac", 0.0,   1.0,     False),  # sync knob
    ("noise_amp_W",       0.0,    2e4,     False),  # residual only
]


def _theta_to_config(x: np.ndarray, spec: dict,
                     frozen: dict | None = None) -> WorkloadConfig:
    """Decode a DE vector into a WorkloadConfig, deriving lambda from the mean.

    frozen: {knob_name: value in natural units} -- knobs REMOVED from the DE
    vector and pinned (used by the held-out-statistics check, where knobs
    identified only by held-out stats must not be searched)."""
    frozen = frozen or {}
    free = [b for b in BOUNDS if b[0] not in frozen]
    v = {name: (np.exp(xi) if lg else xi)
         for (name, _lo, _hi, lg), xi in zip(free, x)}
    v.update(frozen)
    marg = spec["marginal"]
    floor = float(marg["idle_floor_W"])
    p_mean = float(marg["busy_level_W"]) - floor
    mu = np.log(v["dur_mean_s"]) - v["dur_sigma"] ** 2 / 2.0
    frac_mean = v["size_a"] / (v["size_a"] + v["size_b"])
    busy_target = (float(marg["grand_mean_W"]) - floor) / p_mean
    lam = LAMBDA_HORIZON_BOOST * busy_target / (frac_mean * v["dur_mean_s"])
    return WorkloadConfig(
        idle_floor_W=floor,
        per_rack_scale=list(marg["per_rack_scale"]),
        job_power=DistSpec("normal", {"mean": p_mean, "std": v["power_std_frac"] * p_mean}),
        arrival_rate_per_s=lam,
        duration=DistSpec("lognormal", {"mu": mu, "sigma": v["dur_sigma"]}),
        discipline="queue",
        ramp_time_s=v["ramp_time_s"],
        wander_std_W=v["wander_std_W"],
        wander_phi=v["wander_phi"],
        wander_shared_frac=v["wander_shared_frac"],
        job_size=DistSpec("beta", {"a": v["size_a"], "b": v["size_b"]}),
        placement="scattered",
        noise_amp_W=v["noise_amp_W"],
    )


def _encode(cfg_values: dict) -> np.ndarray:
    """Encode named knob values into DE space (log where flagged)."""
    return np.array([np.log(cfg_values[n]) if lg else cfg_values[n]
                     for n, _lo, _hi, lg in BOUNDS])


def _q_subset(rep, fit_stats: set | None):
    """(Q_feasible, Q_faithful) over the named checks only (None = all).
    The held-out-statistics check scores DE on fitted checks alone; held-out
    checks must contribute NOTHING to the search objective."""
    cs = [c for c in rep.checks if fit_stats is None or c.name in fit_stats]
    return (float(sum(c.feas_dev ** 2 for c in cs)),
            float(sum(c.norm_dev ** 2 for c in cs)))


def _pass_rate_subset(reports, fit_stats: set | None):
    """Trace-tier pass rate counting only the named checks (None = all).
    Filtering here matters: the gate term would otherwise leak held-out stats
    into the objective through the pass-rate."""
    def ok(r):
        return all(c.passed for c in r.checks
                   if c.tier == "trace" and (fit_stats is None or c.name in fit_stats))
    return sum(ok(r) for r in reports) / len(reports)


def _objective(x: np.ndarray, spec: dict, seeds: range,
               frozen: dict | None = None, fit_stats: set | None = None) -> float:
    """Ensemble feasibility + faithfulness tie-break + trace-tier gate shortfall.

    The gate term (squared shortfall below 0.9 = the 0.8 ship gate plus 0.1
    margin, weight 1.0) makes DE optimize the actual ship criterion, not only
    the ensemble bias -- CRN keeps the rate deterministic per theta so the term
    is a valid objective.
    With fit_stats given, every term (ensemble Q AND the gate rate) is computed
    over the fitted checks only."""
    try:
        cfg = _theta_to_config(x, spec, frozen)
    except ValueError:          # e.g. job_size mean out of (0,1] at extreme a/b
        return 1e6
    traces = [generate(cfg, seed=s) for s in seeds]
    rep = validate_ensemble(traces, spec)
    q_feas, q_faith = _q_subset(rep, fit_stats)
    _rate_all, reports = pass_rate(traces, spec)
    rate = _pass_rate_subset(reports, fit_stats)
    return (q_feas + 0.01 * q_faith
            + max(0.0, 0.9 - rate) ** 2)  # gate margin term. NOTE: DE#4 tried 4x weight/0.95 target -> WORSE (traded ensemble feasibility, gate still 40%): ensemble + per-seed tau/corr floors + 80% gate are jointly unreachable at ~30 jobs/day (Pareto frontier confirmed)


def starting_theta(spec: dict) -> np.ndarray:
    """Seed DE at the analytic starting point (regime_A_starting equivalents)."""
    return _encode({
        "dur_mean_s": 5553.0, "dur_sigma": 0.7, "power_std_frac": 0.05,
        "size_a": 40.0, "size_b": 1.5, "ramp_time_s": 75.0,
        "wander_std_W": 38e3, "wander_phi": 0.9, "wander_shared_frac": 0.6,
        "noise_amp_W": 2e3,
    })


def calibrate(quick: bool = False, out_path: str | Path = _OUT) -> WorkloadConfig:
    spec = load_spec(_SPEC)
    seeds = range(N_SEEDS)
    lo_hi = [(np.log(lo) if lg else lo, np.log(hi) if lg else hi)
             for _n, lo, hi, lg in BOUNDS]

    # init population = latin hypercube + the analytic starting point
    popsize = 3 if quick else 8
    maxiter = 8 if quick else 60
    rng = np.random.default_rng(0)
    n_pop = popsize * len(BOUNDS)
    init = rng.uniform([b[0] for b in lo_hi], [b[1] for b in lo_hi],
                       size=(n_pop, len(BOUNDS)))
    init[0] = starting_theta(spec)

    t0 = time.time()
    best_hist: list[float] = []

    def _cb(xk, convergence=None):
        q = _objective(xk, spec, seeds)
        best_hist.append(q)
        print(f"  gen {len(best_hist):3d}  Q = {q:.5g}   ({time.time()-t0:.0f}s)", flush=True)

    res = differential_evolution(
        _objective, bounds=lo_hi, args=(spec, seeds),
        init=init, maxiter=maxiter, tol=1e-8, seed=0,
        mutation=(0.4, 1.0), recombination=0.8, polish=False,
        workers=-1, updating="deferred",  # parallel across cores; CRN keeps it fair
        callback=_cb,
    )

    cfg = _theta_to_config(res.x, spec)

    # ship gate on FRESH seeds (out-of-sample w.r.t. the CRN search seeds):
    # ensemble report must pass BOTH tiers on averaged stats, AND >= 80% of
    # individual traces must pass every trace-tier (shape/dynamics) check
    gate_traces = [generate(cfg, seed=s) for s in GATE_SEEDS]
    rep = validate_ensemble(gate_traces, spec)
    rate, _ = pass_rate(gate_traces, spec)
    ship = rep.passed and rate >= 0.8
    print(res.message)
    print(f"search Q = {res.fun:.5g} after {res.nfev} evals, {time.time()-t0:.0f}s")
    print(rep)
    print(f"ship gate: ensemble {'pass' if rep.passed else 'FAIL'} + trace-tier "
          f"pass rate {rate*100:.0f}% on {len(gate_traces)} fresh seeds "
          f"(need both, rate >= 80%): {'SHIP' if ship else 'NOT YET'}")

    data = json.loads(json.dumps(  # plain-dict round trip of the dataclass
        cfg.__dict__, default=lambda o: o.__dict__))
    data["_provenance"] = {
        "method": ("MSM via scipy differential_evolution (CRN, lambda pinned to mean, "
                   "two-tier acceptance: level=ensemble bias, shape/dynamics=per-trace)"),
        "ship": ship,
        "date": time.strftime("%Y-%m-%d"),
        "spec": str(_SPEC.name),
        "n_seeds_objective": N_SEEDS,
        "gate_seeds": [int(s) for s in GATE_SEEDS],
        "gate_pass_rate": rate,
        "search_Q": float(res.fun),
        "gate_Q_feasible": rep.distance_feasible,
        "gate_Q_faithful": rep.distance_faithful,
        "n_evals": int(res.nfev),
        "quick": quick,
        "bounds": {n: [lo, hi] for n, lo, hi, _ in BOUNDS},
    }
    Path(out_path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    return cfg


if __name__ == "__main__":
    calibrate(quick="--quick" in sys.argv)
