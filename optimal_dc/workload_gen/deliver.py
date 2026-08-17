"""Delivery layer: generate a synthetic day and write every downstream format.

Outputs per trace (all sharing a base name):
  <name>.csv            drop-in replacement for input_04-07-24.csv -- EXACT
                        schema (time, power[1..25], OA Wetbulb Temp) so anything
                        that consumes the real file consumes this one unchanged.
                        Wet-bulb is SOURCED (real day's column), not synthesized.
  <name>_exogenous.npy  (T, 16) FMU-ready trace from disaggregator.py -- for
                        direct injection into the rollout harness
                        (env.iter_exogenous_var swap, as v0 does).
  <name>_meta.json      provenance sidecar: config + seed, realized stats,
                        trace-tier validation verdict, scheduling-ledger
                        metrics, and the disaggregation convention (/9 vs /15)
                        -- no delivered file can silently mix regimes.

Level conditioning (--mean-band): the two-tier acceptance certifies level only
in distribution, so experiments needing a specific load level ask for it HERE,
at delivery: seeds are advanced until the realized daily mean lands in band
(rejection sampling at delivery keeps the generative model + calibration
unconditional and clean).

Disaggregation convention: DEFAULT = /15 (sustain-lc lineage -- comparable
with every existing run and baseline); pass --faithful for the /9 regime
(source-verified plumbing; needs its own baseline pass -- see disaggregator.py).

Usage:
    python -m workload_gen.deliver --seed 0
    python -m workload_gen.deliver --seed 0 --mean-band 15.0,17.3 --out synth_data
    python -m workload_gen.deliver --seed 0 --faithful     # /9 new regime
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from .config import WorkloadConfig
from .generator import generate, job_metrics
from .validate import validate, load_spec
from .disaggregator import disaggregate

_PKG = Path(__file__).parent
_SPEC = _PKG / "spec" / "regime_A.json"
_CALIB = _PKG / "spec" / "regime_A_calib.json"
_REAL_CSV = _PKG.parent / "external" / "sustain-lc" / "input_04-07-24.csv"
_OUT = _PKG / "synth_data"

MAX_TRIES = 200  # rejection-sampling cap for --mean-band


def load_real_wetbulb(n_steps: int) -> np.ndarray:
    """Real day's OA wet-bulb column (degC), tiled/truncated to n_steps."""
    with open(_REAL_CSV, newline="") as f:
        rows = list(csv.reader(f))
    wb = np.array([float(r[-1]) for r in rows[1:]])
    reps = int(np.ceil(n_steps / len(wb)))
    return np.tile(wb, reps)[:n_steps]


def make_day(config: WorkloadConfig, seed: int, n_steps: int = 5761,
             dt: float = 15.0, mean_band_MW: tuple | None = None,
             require_pass: bool = False, spec_path: Path = _SPEC):
    """Generate one day, rejection-sampling seeds until it meets the delivery
    conditions. Returns (P, jobs, used_seed, n_tries).

    require_pass: only accept a day passing every TRACE-TIER check of the
    frozen spec. This is the ABC accept/reject step made explicit at delivery:
    the calibrated generator PROPOSES days, the pre-committed spec DISPOSES --
    sampling from the generator conditioned on spec satisfaction (posterior-
    predictive draws), not post-hoc cherry-picking. Nothing is written for
    rejected candidates; the sidecar records seeds_tried (~2 expected at the
    current ~48% acceptance rate -- an honest, reported model property).
    mean_band_MW: additionally require the realized daily mean (MW) in band.
    """
    spec = load_spec(spec_path) if require_pass else None
    for k in range(MAX_TRIES):
        s = seed + k
        P, jobs = generate(config, n_steps=n_steps, dt=dt, seed=s, return_jobs=True)
        if mean_band_MW is not None:
            m = P.sum(axis=1).mean() / 1e6
            if not (mean_band_MW[0] <= m <= mean_band_MW[1]):
                continue
        if require_pass and not validate(P, spec).passed_trace:
            continue
        return P, jobs, s, k + 1
    raise RuntimeError(
        f"no seed met the delivery conditions (mean_band={mean_band_MW}, "
        f"require_pass={require_pass}) after {MAX_TRIES} tries")


def deliver(P: np.ndarray, jobs: list, used_seed: int, *, config_path: Path,
            out_dir: Path = _OUT, name: str | None = None, dt: float = 15.0,
            compat_v0: bool = True, slice_mode="first5",
            spec_path: Path = _SPEC, extra_meta: dict | None = None) -> dict:
    """Write the three delivery files for one generated day. Returns the metadata."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    n_steps, n_racks = P.shape
    name = name or f"synth_seed{used_seed}"

    towb = load_real_wetbulb(n_steps)

    # 1. drop-in CSV (exact input_04-07-24.csv schema; wet-bulb in degC, raw)
    csv_path = out_dir / f"{name}.csv"
    hdr = ["time"] + [f"power[{k}]" for k in range(1, n_racks + 1)] + ["OA Wetbulb Temp"]
    t = np.arange(n_steps) * dt
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(hdr)
        for i in range(n_steps):
            w.writerow([t[i], *P[i].tolist(), towb[i]])

    # 2. FMU-ready exogenous trace
    exo, disagg_meta = disaggregate(P, towb, compat_v0=compat_v0, slice_mode=slice_mode)
    exo_path = out_dir / f"{name}_exogenous.npy"
    np.save(exo_path, exo)

    # 3. provenance sidecar
    rep = validate(P, load_spec(spec_path))
    tot = P.sum(axis=1)
    meta = {
        "name": name,
        "seed": used_seed,
        "config": str(config_path),
        "spec": str(spec_path),
        "n_steps": n_steps, "n_racks": n_racks, "dt_s": dt,
        "wetbulb_source": str(_REAL_CSV.name) + " (sourced, not synthesized)",
        "realized": {
            "total_mean_MW": float(tot.mean() / 1e6),
            "total_max_MW": float(tot.max() / 1e6),
            "total_std_MW": float(tot.std() / 1e6),
        },
        "validation": {
            "trace_tier_pass": rep.passed_trace,
            "failed_checks": [c.name for c in rep.checks if not c.passed],
        },
        "scheduling": job_metrics(jobs, n_racks, (n_steps - 1) * dt),
        "disaggregation": disagg_meta,
        **(extra_meta or {}),
    }
    meta_path = out_dir / f"{name}_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"delivered {name}: mean {meta['realized']['total_mean_MW']:.2f} MW, "
          f"max {meta['realized']['total_max_MW']:.2f} MW, "
          f"trace-tier {'PASS' if rep.passed_trace else 'FAIL'} "
          f"({meta['disaggregation']['convention']})")
    print(f"  -> {csv_path}\n  -> {exo_path}\n  -> {meta_path}")
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate + deliver a synthetic Frontier day")
    ap.add_argument("--config", default=str(_CALIB), help="WorkloadConfig JSON")
    ap.add_argument("--spec", default=str(_SPEC))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-steps", type=int, default=5761)
    ap.add_argument("--out", default=str(_OUT))
    ap.add_argument("--name", default=None)
    ap.add_argument("--mean-band", default=None,
                    help="MW band 'lo,hi': rejection-sample seeds until the daily mean lands inside")
    ap.add_argument("--require-pass", action="store_true",
                    help="only deliver a day passing every trace-tier spec check "
                         "(ABC accept step at delivery; ~2 seed tries expected)")
    ap.add_argument("--faithful", action="store_true",
                    help="faithful /9 magnitude (NEW thermal regime; needs its own "
                         "baseline pass) instead of the default /15 lineage convention")
    ap.add_argument("--slice", default="first5", help="first5 | representative")
    args = ap.parse_args(argv)

    cfg = WorkloadConfig.from_json(args.config)
    band = tuple(float(x) for x in args.mean_band.split(",")) if args.mean_band else None
    P, jobs, used_seed, tries = make_day(cfg, args.seed, n_steps=args.n_steps,
                                         mean_band_MW=band,
                                         require_pass=args.require_pass,
                                         spec_path=Path(args.spec))
    deliver(P, jobs, used_seed, config_path=Path(args.config), out_dir=Path(args.out),
            name=args.name, compat_v0=not args.faithful, slice_mode=args.slice,
            spec_path=Path(args.spec),
            extra_meta={"mean_band_MW": band, "require_pass": args.require_pass,
                        "seeds_tried": tries})


if __name__ == "__main__":
    main()
