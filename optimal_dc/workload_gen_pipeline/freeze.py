"""Freeze the regime-A spec from the real day's trace.

Supersedes the freeze cell in workload_analysis.ipynb (schema v1): the spec is
now built THROUGH validate.compute_stats, so the freeze and the acceptance test
share one code path and cannot disagree on conventions (the v1 bug: ramps were
frozen from the facility TOTAL but validated per-rack pooled -- 17.7x apart).

Schema v2 changes vs v1:
  - ramps split into two labeled families (total_ramp_* / rack_ramp_*) plus
    their ratio `ramp_sync_ratio` (ramp-coincidence statistic; day = 17.7,
    between sqrt(25)=5 independent and 25 lockstep);
  - pooled quantiles, autocorr tau, and the capacity ceiling become CHECKED
    tolerances (v1 froze them but never tested them);
  - PC1 share defined on the correlation matrix in both freeze and check.

Decisions recorded (Frank, 2026-08-16):
  - Calibration day KEPT = 2024-04-07 despite being the 98.8th percentile of
    2023 daily means: same day as the LC-Opt paper (comparability), and a
    high-activity day is forward-looking given compute scaling.
  - 2023 year envelope ACCEPTED (with staleness caveat: envelope is 2023, day
    is 2024); its role = physical capacity ceiling + regime-family context,
    NOT a workload-seasonality source (2023 compute shows no season: monthly
    means 10.2-12.8 MW; seasonality lives in the cooling channel).

Usage:
    python -m workload_gen.freeze            # default paths
    python -m workload_gen.freeze <csv> <out_json>
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

from .validate import compute_stats

# Physical capacity ceiling: max of 'Frontier Compute Power', sheet Frontier2023
# of data/Frontier HPC & Facility Data.xlsx (49869 rows @ 10 min, full 2023).
# Distribution there: p01 6.87 / p50 10.99 / p99 21.68 / max 27.70 MW.
# OWNED by envelope.py (spec/envelope.json); this constant is only the fallback
# when the envelope has not been built yet.
CAPACITY_W = 27.70e6
_ENVELOPE = Path(__file__).parent / "spec" / "envelope.json"


def _capacity_W() -> float:
    """Capacity from spec/envelope.json when built, else the pinned fallback."""
    if _ENVELOPE.is_file():
        return float(json.loads(_ENVELOPE.read_text(encoding="utf-8"))["capacity_W"])
    return CAPACITY_W

_DEFAULT_CSV = Path(__file__).parents[1] / "external" / "sustain-lc" / "input_04-07-24.csv"
_DEFAULT_OUT = Path(__file__).parent / "spec" / "regime_A.json"


def load_day_csv(path: str | Path) -> tuple[np.ndarray, float]:
    """Read the real day's per-CDU-group power columns -> (n_steps, n_racks) watts, dt_s."""
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    hdr = rows[0]
    p_idx = [i for i, h in enumerate(hdr) if h.startswith("power")]
    t_idx = hdr.index("time")
    P = np.array([[float(r[i]) for i in p_idx] for r in rows[1:]], dtype=float)
    t = np.array([float(r[t_idx]) for r in rows[1:]])
    dt = float(np.unique(np.diff(t))[0])
    return P, dt


def build_spec(P: np.ndarray, dt_s: float, source_csv: str, date: str,
               capacity_W: float | None = None) -> dict:
    """Assemble the frozen spec dict from the real trace."""
    if capacity_W is None:
        capacity_W = _capacity_W()
    n_steps, n_racks = P.shape
    s = compute_stats(P, dt_s)  # the shared convention path

    # freeze-only extras (targets/reference, not recomputed per validation)
    rack_mean = P.mean(axis=0)
    rack_std = P.std(axis=0)
    scale = rack_mean / rack_mean.mean()
    cov = rack_std / rack_mean                      # per-rack CoV, unitless
    C = np.corrcoef(P, rowvar=False)
    # residual correlation after removing PC1 (block-structure probe)
    Z = (P - P.mean(axis=0)) / P.std(axis=0)
    w, V = np.linalg.eigh(np.cov(Z, rowvar=False))
    v1 = V[:, -1]
    Cr = np.corrcoef((Z - np.outer(Z @ v1, v1)), rowvar=False)
    iu = np.triu_indices(n_racks, 1)

    tau = int(s["autocorr_1e_tau_steps"])

    return {
        "meta": {
            "schema_version": 2,
            "source_csv": source_csv,
            "date": date,
            "n_racks": int(n_racks),
            "dt_s": dt_s,
            "n_steps": int(n_steps),
            "units": "watts",
            "provenance": (
                "frozen by workload_gen/freeze.py via validate.compute_stats "
                "(shared freeze/check conventions). Day kept deliberately: "
                "LC-Opt precedent + forward-looking high activity "
                "(98.8th pct of 2023 daily means). Capacity ceiling from the "
                "2023 year envelope (staleness caveat: envelope 2023, day 2024)."
            ),
        },
        "marginal": {
            "grand_mean_W": float(P.mean()),
            "per_rack_scale": scale.tolist(),
            "per_rack_CoV": cov.tolist(),
            "idle_floor_W": float(s["pooled_norm_quantiles_W"][0]),   # ~p05 of pooled
            "busy_level_W": float(s["pooled_norm_quantiles_W"][-1]),  # ~p95 of pooled
            "pooled_norm_quantiles_pct": [5, 25, 50, 75, 95],
            "pooled_norm_quantiles_W": np.asarray(s["pooled_norm_quantiles_W"]).tolist(),
        },
        "temporal": {
            "total_ramp_excess_kurtosis": s["total_ramp_excess_kurtosis"],
            "total_ramp_abs_mean_W": s["total_ramp_abs_mean_W"],
            "total_ramp_abs_p99_W": s["total_ramp_abs_p99_W"],
            "total_ramp_abs_max_W": s["total_ramp_abs_max_W"],
            "rack_ramp_excess_kurtosis": s["rack_ramp_excess_kurtosis"],
            "rack_ramp_abs_mean_W": s["rack_ramp_abs_mean_W"],
            "rack_ramp_abs_p99_W": s["rack_ramp_abs_p99_W"],
            "rack_ramp_abs_max_W": s["rack_ramp_abs_max_W"],
            "ramp_sync_ratio": s["ramp_sync_ratio"],
            "autocorr_1e_tau_steps": tau,
        },
        "cross_rack": {
            "offdiag_corr_mean": s["offdiag_corr_mean"],
            "offdiag_corr_min": s["offdiag_corr_min"],
            "offdiag_corr_max": s["offdiag_corr_max"],
            "pc1_var_share": s["pc1_var_share"],
            "residual_offdiag_absmax": float(np.abs(Cr[iu]).max()),
            "corr_matrix": C.tolist(),  # 25x25, reference only (not tolerance-checked)
        },
        "aggregate": {
            "total_min_W": s["total_min_W"],
            "total_max_W": s["total_max_W"],
            "total_mean_W": s["total_mean_W"],
            "total_std_W": s["total_std_W"],
        },
        "envelope": {
            "capacity_W": capacity_W,
            "source": "spec/envelope.json (envelope.py) when built, else pinned fallback; Frontier2023 sheet max",
            "note": "physical ceiling for the machine; owned by envelope.py",
        },
        # committed judgment of "what counts as faithful" -- every key here maps
        # to one check in validate._check_stats.
        # TWO-TIER ACCEPTANCE (decided 2026-08-16): "tier" says where a check
        # applies. "trace" = every generated day must pass it individually
        # (shape/dynamics -- what the control experiments consume). "ensemble" =
        # checked on seed-averaged stats only (level = calibrated BIAS): with
        # ~26 near-full-machine jobs/day the per-seed daily-mean CV is ~21%,
        # while REAL 2023 operational daily means scatter CV~15% -- demanding
        # per-seed level replication would be stricter than the real machine's
        # own day-to-day variability.
        "tolerances": {
            "per_rack_mean": {
                "kind": "relative", "rel": 0.05, "tier": "ensemble",
                "note": "level stat -> bias test on the ensemble mean (see tier note above)",
            },
            "total_mean": {
                "kind": "relative", "rel": 0.07, "tier": "ensemble",
                "note": "level stat -> bias test on the ensemble mean (see tier note above)",
            },
            "pooled_modes": {
                "kind": "relative_vector", "rel": [0.08, 0.08], "pcts": [5, 95],
                "tier": "trace",
                "note": ("idle/busy mode POSITIONS (p5/p95 of the pooled marginal) = "
                         "hardware shape -- must hold on every trace"),
            },
            "pooled_mix": {
                "kind": "relative_vector", "rel": [0.25, 0.25, 0.25], "pcts": [25, 50, 75],
                "tier": "ensemble",
                "note": ("mixing quantiles (p25/p50/p75) track the day's occupancy "
                         "level -> same realization scatter as the mean -> ensemble tier"),
            },
            "pc1_var_share": {"kind": "floor", "min": 0.98, "tier": "trace"},
            "total_ramp_excess_kurtosis": {"kind": "floor", "min": 15, "tier": "trace"},
            "rack_ramp_excess_kurtosis": {"kind": "floor", "min": 50, "tier": "trace"},
            "rack_ramp_abs_mean": {
                "kind": "relative", "rel": 0.5, "tier": "trace",
                "note": ("order-of-magnitude guard on per-rack ramp level -- kills "
                         "white-noise ramp faking; total ramp level is implied by "
                         "rack level x sync ratio, so it has no separate check"),
            },
            "ramp_sync_ratio": {
                "kind": "band", "lo": 10.0, "hi": 25.0, "tier": "trace",
                "note": "sqrt(25)=5 if racks jump independently, 25 lockstep; day = 17.7",
            },
            "offdiag_corr_mean": {
                "kind": "band", "lo": 0.98, "hi": 0.999, "tier": "trace",
                "note": ("lo RAISED 0.95->0.98 (2026-08-16) for consistency with the "
                         "pc1 floor: rank-1 identity pc1 ~ (1+24*corr)/25 means "
                         "pc1>=0.98 <=> corr>=0.979; the old lo admitted configs "
                         "the pc1 floor rejects. Day value 0.994."),
            },
            "autocorr_tau": {
                "kind": "band", "lo": 87, "hi": 348, "tier": "trace",
                "note": "0.5x-2x of the day's tau=174 steps (trend-inflated upper bound)",
            },
            "total_max": {
                "kind": "ceiling", "max": capacity_W, "tier": "trace",
                "note": "peak must respect the machine's physical capacity (2023 envelope max)",
            },
        },
    }


def freeze(csv_path: str | Path = _DEFAULT_CSV, out_path: str | Path = _DEFAULT_OUT) -> dict:
    """Compute and write the frozen spec; returns it. Sanity-asserts finiteness."""
    P, dt = load_day_csv(csv_path)
    spec = build_spec(P, dt, source_csv=Path(csv_path).name, date="2024-04-07")

    flat = [v for sec in ("marginal", "temporal", "cross_rack", "aggregate")
            for v in spec[sec].values()
            if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert all(np.isfinite(flat)), "non-finite target in spec"

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    # closure check: the real day must pass its own acceptance test exactly
    from .validate import validate
    rep = validate(P, spec, dt)
    print(f"froze {out_path}  (schema v2, {len(flat)} scalar targets finite)")
    print(f"self-check (real day vs its own spec): {'pass' if rep.passed else 'FAIL'}"
          f"   Q_faithful = {rep.distance_faithful:.4g}")
    if not rep.passed:
        print(rep)
        raise AssertionError("real day fails its own frozen spec -- convention bug")
    return spec


if __name__ == "__main__":
    args = sys.argv[1:]
    freeze(*args) if args else freeze()
