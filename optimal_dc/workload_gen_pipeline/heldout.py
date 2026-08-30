"""Held-out-statistics check (overidentification test) -- SPLIT 1: cross-rack facet.

The circularity rebuttal for train-on-synthetic / test-on-real: calibrate the
generator WITHOUT the cross-rack statistics, then measure whether they emerge
anyway. Fitting 10 targets with 10 knobs proves flexibility; reproducing
statistics that were never in the objective can only come from the MECHANISM
(jobs landing on many racks simultaneously force cross-rack correlation).
Econometrics name: overidentification / Hansen J-test -- surplus moment
conditions become testable predictions.

PRE-REGISTERED DESIGN (committed before the first run; do not tune after):
  HELD OUT (never scored, in objective OR gate term):
      offdiag_corr_mean, pc1_var_share, ramp_sync_ratio
      -- all three are cross-rack synchronization statistics.
  FROZEN KNOBS (identified only by held-out stats -> flat directions of the
  reduced objective; DE must not choose them):
      size_a=40, size_b=1.5     job-size beta: mean 0.964, "leadership-class
                                capability jobs span most of the machine" --
                                the pre-calibration analytic prior.
      wander_shared_frac=0.5    max-entropy midpoint of [0, 1].
  FIT: the remaining 9 checks, searched over the remaining 7 knobs.
  PASS CRITERION: the EXISTING spec tolerance bands on the held-out checks,
      evaluated on fresh gate seeds (never the CRN search seeds). No new bands.

LEAKAGE CAVEAT (stated, not hidden): the frozen job-size prior is defensible
as external domain knowledge, but was historically written down by someone who
had already seen this day's rank-1 structure. The strict version re-derives it
from external traces (PM100/F-DATA). Until then this check rebuts tuning
circularity, not knowledge circularity.

Usage:
    python -m workload_gen_pipeline.heldout            # full run
    python -m workload_gen_pipeline.heldout --quick    # smoke run
Writes spec/regime_A_partial_split1.json (never touches regime_A_calib.json).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

from .calibrate import (BOUNDS, GATE_SEEDS, N_SEEDS, _objective, _pass_rate_subset,
                        _q_subset, _theta_to_config, starting_theta)
from .generator import generate
from .validate import load_spec, pass_rate, validate, validate_ensemble

_SPEC = Path(__file__).parent / "spec" / "regime_A.json"
_OUT = Path(__file__).parent / "spec" / "regime_A_partial_split1.json"

HELD_OUT = {"offdiag_corr_mean", "pc1_var_share", "ramp_sync_ratio"}
FROZEN = {"size_a": 40.0, "size_b": 1.5, "wander_shared_frac": 0.5}


def run_split1(quick: bool = False, out_path: str | Path = _OUT) -> bool:
    spec = load_spec(_SPEC)
    seeds = range(N_SEEDS)

    all_names = {c.name for c in validate(generate(
        _theta_to_config(starting_theta(spec), spec), seed=0), spec).checks}
    fit_stats = all_names - HELD_OUT
    print(f"fit on   : {sorted(fit_stats)}")
    print(f"held out : {sorted(HELD_OUT)}")
    print(f"frozen   : {FROZEN}  (7 free knobs of {len(BOUNDS)})\n")

    free = [b for b in BOUNDS if b[0] not in FROZEN]
    lo_hi = [(np.log(lo) if lg else lo, np.log(hi) if lg else hi)
             for _n, lo, hi, lg in free]

    # init population = latin hypercube + the analytic start (free knobs only)
    popsize = 3 if quick else 8
    maxiter = 8 if quick else 60
    rng = np.random.default_rng(0)
    init = rng.uniform([b[0] for b in lo_hi], [b[1] for b in lo_hi],
                       size=(popsize * len(free), len(free)))
    start_full = starting_theta(spec)
    free_idx = [i for i, b in enumerate(BOUNDS) if b[0] not in FROZEN]
    init[0] = start_full[free_idx]

    t0 = time.time()
    gen_count = [0]

    def _cb(xk, convergence=None):
        gen_count[0] += 1
        q = _objective(xk, spec, seeds, FROZEN, fit_stats)
        print(f"  gen {gen_count[0]:3d}  Q_fit = {q:.5g}   ({time.time()-t0:.0f}s)",
              flush=True)

    res = differential_evolution(
        _objective, bounds=lo_hi, args=(spec, seeds, FROZEN, fit_stats),
        init=init, maxiter=maxiter, tol=1e-8, seed=0,
        mutation=(0.4, 1.0), recombination=0.8, polish=False,
        workers=-1, updating="deferred",
        callback=_cb,
    )
    cfg = _theta_to_config(res.x, spec, FROZEN)
    print(f"\nsearch Q_fit = {res.fun:.5g} after {res.nfev} evals, "
          f"{time.time()-t0:.0f}s")

    # ------- the test: held-out stats on FRESH gate seeds, existing bands -------
    gate_traces = [generate(cfg, seed=s) for s in GATE_SEEDS]
    rep = validate_ensemble(gate_traces, spec)
    _rate_all, reports = pass_rate(gate_traces, spec)

    print("\nensemble report on fresh gate seeds (F=fitted, H=HELD OUT):")
    held_checks = []
    for c in rep.checks:
        tag = "H" if c.name in HELD_OUT else "F"
        mark = "pass" if c.passed else "FAIL"
        print(f"  [{tag}|{mark}] {c.name:<26} = {c.value:< 12.5g} "
              f"target {c.target:< 12.5g} ({c.bound})")
        if c.name in HELD_OUT:
            held_checks.append(c)

    # per-seed spread of the held-out stats (mean +/- sd across gate seeds)
    print("\nheld-out stats, per-seed distribution over gate seeds:")
    for name in sorted(HELD_OUT):
        vals = [next(c.value for c in r.checks if c.name == name) for r in reports]
        print(f"  {name:<22} {np.mean(vals):.4f} +/- {np.std(vals):.4f}   "
              f"(target {next(c.target for c in rep.checks if c.name == name):.4f})")

    q_feas_held, _ = _q_subset(rep, HELD_OUT)
    rate_held = _pass_rate_subset(reports, HELD_OUT)
    passed = all(c.passed for c in held_checks)
    print(f"\nheld-out ensemble Q_feasible = {q_feas_held:.5g}   "
          f"per-seed held-out pass rate = {rate_held*100:.0f}%")
    verdict = ("PASS -- the mechanism predicts the cross-rack statistics it was never shown"
               if passed else
               "FAIL -- dependence mechanism does not reproduce held-out coupling")
    print(f"SPLIT-1 VERDICT (ensemble held-out checks in existing bands): {verdict}")

    data = json.loads(json.dumps(cfg.__dict__, default=lambda o: o.__dict__))
    data["_provenance"] = {
        "method": "held-out-statistics check (overidentification), SPLIT 1: cross-rack facet",
        "held_out": sorted(HELD_OUT),
        "frozen_knobs": FROZEN,
        "frozen_rationale": {
            "size": "pre-calibration analytic prior beta(40,1.5): capability jobs "
                    "span most of the machine (see leakage caveat in module docstring)",
            "wander_shared_frac": "max-entropy midpoint of [0,1]",
        },
        "fit_stats": sorted(fit_stats),
        "pass_criterion": "existing spec tolerance bands, ensemble over fresh gate seeds",
        "verdict_pass": bool(passed),
        "held_out_ensemble_values": {c.name: c.value for c in held_checks},
        "held_out_targets": {c.name: c.target for c in held_checks},
        "held_out_Q_feasible": q_feas_held,
        "held_out_per_seed_pass_rate": rate_held,
        "search_Q_fit": float(res.fun),
        "n_evals": int(res.nfev),
        "n_seeds_objective": N_SEEDS,
        "gate_seeds": [int(s) for s in GATE_SEEDS],
        "quick": quick,
        "date": time.strftime("%Y-%m-%d"),
    }
    Path(out_path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    return passed


if __name__ == "__main__":
    ok = run_split1(quick="--quick" in sys.argv)
    raise SystemExit(0 if ok else 1)
