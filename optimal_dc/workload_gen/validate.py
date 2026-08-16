"""Acceptance test + calibration objective for the workload synthesizer.

`validate(P, spec)` measures the summary statistics `s(P)` of a generated trace
and compares them to the FROZEN spec (`spec/regime_A.json`). It returns both:

  - a pass/fail report against the spec TOLERANCES (the acceptance test), and
  - a scalar `distance` = the MSM objective  Q = sum_i ((s_i - target_i)/target_i)^2
    that the calibration search minimizes.

So this single module is the `||s(generate(theta)) - s(real)||` in
    theta* = argmin_theta || s(generate(theta)) - s(real) ||
and the ABC accept test (tolerances = per-stat epsilon). See the calibration
notes for why this is simulation-based rather than likelihood-based.

CONVENTIONS are enforced structurally: `freeze.py` builds the spec from the real
day using THIS module's `compute_stats`, so the same code path measures real and
synthetic traces and a freeze-vs-check convention mismatch cannot re-occur.
The conventions themselves:

  - Ramps come in TWO families, both first differences over one dt step:
      total_ramp_* : diff of the FACILITY TOTAL (what the cooling plant feels;
                     day: abs_mean 125.8 kW, excess kurt 25.2)
      rack_ramp_*  : per-rack diffs POOLED across racks and time (what the job
                     mechanism produces at one CDU; day: 7.1 kW, kurt 82.3)
    Their ratio `ramp_sync_ratio = total/rack abs-mean` measures ramp
    COINCIDENCE: sqrt(n_racks)=5 if racks jump independently, 25 in lockstep;
    the real day sits at 17.7. Correlation measures co-LEVEL; this measures
    co-JUMPING -- independent axes.
  - PC1 share is of the CORRELATION matrix (z-scored racks), matching the freeze.
  - Pooled quantiles are scale-normalized by the trace's OWN per-rack means
    (self-normalized, exactly as the day was frozen).

SINGLE SEED vs ENSEMBLE: one 24 h trace contains ~20 jobs, so per-seed
realization noise on total_mean is ~18% -- larger than the +/-7% tolerance.
`validate()` on one trace is therefore the per-trace ABC accept test only;
the MSM objective for calibration must be `validate_ensemble()` over N >= 20
seeds (sd of the mean ~ 18%/sqrt(N) ~ 4% at N=20), and the shipping gate is
`pass_rate()` (e.g. >= 80% of seeds pass individually).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


# --------------------------------------------------------------- statistics ---
def _excess_kurtosis(x: np.ndarray) -> float:
    """Fisher (excess) kurtosis; 0 for a Gaussian. No scipy dependency."""
    x = x.ravel()
    mu = x.mean()
    var = x.var()
    if var == 0:
        return 0.0
    return float(((x - mu) ** 4).mean() / var ** 2 - 3.0)


def compute_stats(P: np.ndarray, dt: float = 15.0) -> dict:
    """Summary statistics of a (n_steps, n_racks) watt trace.

    This is THE convention definition: freeze.py freezes the spec through this
    function, and validate() checks synthetic traces through it.
    """
    n_steps, n_racks = P.shape
    total = P.sum(axis=1)

    # self-normalized pooled marginal (reveals the idle/busy bimodality)
    rack_mean = P.mean(axis=0)
    scale = rack_mean / rack_mean.mean()
    pooled = (P / scale).ravel()
    quant = np.percentile(pooled, [5, 25, 50, 75, 95])

    # ramp family 1: facility total (5760 samples)
    tramps = np.diff(total)
    # ramp family 2: per-rack, pooled across racks and time (5760 * n_racks)
    rramps = np.diff(P, axis=0).ravel()
    tr_abs_mean = float(np.abs(tramps).mean())
    rr_abs_mean = float(np.abs(rramps).mean())

    # autocorrelation of the total; 1/e crossing in steps (persistence)
    x = total - total.mean()
    ac = np.correlate(x, x, "full")[n_steps - 1:]
    ac = ac / ac[0]
    below = np.nonzero(ac < 1.0 / np.e)[0]
    tau = int(below[0]) if below.size else n_steps  # never crosses -> saturate

    corr = np.corrcoef(P, rowvar=False)
    offdiag = corr[~np.eye(n_racks, dtype=bool)]

    # PC1: fraction of variance carried by PC1 of the CORRELATION matrix
    # (z-scored racks -- matches the frozen day; NOT the raw covariance)
    Z = (P - P.mean(axis=0)) / P.std(axis=0)
    eig = np.linalg.eigvalsh(np.cov(Z, rowvar=False))
    pc1_share = float(eig[-1] / eig.sum())

    return {
        "per_rack_mean_W": rack_mean,
        "total_mean_W": float(total.mean()),
        "total_min_W": float(total.min()),
        "total_max_W": float(total.max()),
        "total_std_W": float(total.std()),
        "pooled_norm_quantiles_W": quant,
        "total_ramp_excess_kurtosis": _excess_kurtosis(tramps),
        "total_ramp_abs_mean_W": tr_abs_mean,
        "total_ramp_abs_p99_W": float(np.percentile(np.abs(tramps), 99)),
        "total_ramp_abs_max_W": float(np.abs(tramps).max()),
        "rack_ramp_excess_kurtosis": _excess_kurtosis(rramps),
        "rack_ramp_abs_mean_W": rr_abs_mean,
        "rack_ramp_abs_p99_W": float(np.percentile(np.abs(rramps), 99)),
        "rack_ramp_abs_max_W": float(np.abs(rramps).max()),
        "ramp_sync_ratio": tr_abs_mean / rr_abs_mean if rr_abs_mean > 0 else 0.0,
        "autocorr_1e_tau_steps": tau,
        "offdiag_corr_mean": float(offdiag.mean()),
        "offdiag_corr_min": float(offdiag.min()),
        "offdiag_corr_max": float(offdiag.max()),
        "pc1_var_share": pc1_share,
    }


# ------------------------------------------------------------------ report ---
@dataclass
class Check:
    name: str
    kind: str          # "relative" | "relative_vector" | "floor" | "band" | "ceiling"
    value: float
    bound: str         # human-readable target/bound
    passed: bool
    norm_dev: float    # signed normalized deviation from the point target (-> Q_faithful)
    target: float = 0.0  # the spec point value this stat should match (for comparison)
    feas_dev: float = 0.0  # normalized distance OUTSIDE the tolerance (-> Q_feasible); 0 if passing
    bias: float | None = None    # vector checks only: signed mean % dev (systematic over/undershoot)
    spread: float | None = None  # vector checks only: std of % devs (sampling scatter)

    def __str__(self) -> str:
        mark = "pass" if self.passed else "fail"
        return (f"  [{mark}] {self.name:<26} = {self.value:< 12.5g}  "
                f"target {self.target:< 12.5g}  ({self.bound})")


@dataclass
class Report:
    checks: list[Check]
    distance_feasible: float   # Q measuring distance OUTSIDE the tolerances (0 <=> all pass)
    distance_faithful: float   # Q measuring distance to the spec POINT targets (full faithfulness)
    stats: dict = field(repr=False, default_factory=dict)
    n_traces: int = 1          # 1 = per-trace accept test; >1 = ensemble-averaged MSM objective

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def distance(self) -> float:
        """Default Q for the calibration search = the feasibility objective
        (Q -> 0 exactly when every check passes)."""
        return self.distance_feasible

    def __str__(self) -> str:
        head = (f"Validation ({'ensemble n=%d' % self.n_traces if self.n_traces > 1 else 'single trace'}): "
                f"{'pass' if self.passed else 'fail'}   "
                f"Q_feasible = {self.distance_feasible:.4g}   "
                f"Q_faithful = {self.distance_faithful:.4g}")
        return "\n".join([head, *map(str, self.checks)])


# ---------------------------------------------------------------- validate ---
def load_spec(spec: str | Path | dict) -> dict:
    if isinstance(spec, dict):
        return spec
    return json.loads(Path(spec).read_text(encoding="utf-8"))


def _rel_dev(value: float, target: float) -> float:
    return (value - target) / target if target != 0 else 0.0


def _check_stats(stats: dict, spec: dict, n_traces: int = 1) -> Report:
    """Build the check list from an (already computed, possibly ensemble-averaged)
    stats dict. All checks are driven by which keys exist in spec['tolerances']."""
    tol = spec["tolerances"]
    checks: list[Check] = []

    # --- per-rack mean (vector relative check) ---
    if "per_rack_mean" in tol:
        rel = tol["per_rack_mean"]["rel"]
        targets = spec["marginal"]["grand_mean_W"] * np.asarray(spec["marginal"]["per_rack_scale"])
        vals = np.asarray(stats["per_rack_mean_W"])
        devs = (vals - targets) / targets
        worst = float(np.abs(devs).max())
        bias = float(devs.mean())   # signed: + racks run high, - run low
        spread = float(devs.std())  # rack-to-rack scatter -> sampling-noise magnitude
        checks.append(Check(
            "per_rack_mean_dev", "relative_vector", worst * 100,
            f"max|dev| {worst*100:.1f}% (bias {bias*100:+.1f}% +/- {spread*100:.1f}% sd) <= {rel*100:.0f}%",
            worst <= rel,
            float(np.sqrt((devs ** 2).mean())),  # RMS rel dev -> Q_faithful
            target=0.0,  # value is a % deviation; 0% is the ideal
            feas_dev=max(0.0, worst - rel),
            bias=bias * 100,
            spread=spread * 100,
        ))

    # --- total mean (relative) ---
    if "total_mean" in tol:
        rel = tol["total_mean"]["rel"]
        target = spec["aggregate"]["total_mean_W"]
        val = stats["total_mean_W"]
        d = _rel_dev(val, target)
        checks.append(Check(
            "total_mean_W", "relative", val,
            f"{val/1e6:.2f} MW vs {target/1e6:.2f} +/-{rel*100:.0f}%", abs(d) <= rel, d,
            target=target,
            feas_dev=max(0.0, abs(d) - rel),
        ))

    # --- pooled normalized quantiles (vector, per-quantile tolerance) ---
    if "pooled_quantiles" in tol:
        rels = np.asarray(tol["pooled_quantiles"]["rel"])
        targets = np.asarray(spec["marginal"]["pooled_norm_quantiles_W"])
        vals = np.asarray(stats["pooled_norm_quantiles_W"])
        devs = (vals - targets) / targets
        excess = np.abs(devs) - rels             # per-quantile distance beyond its band
        worst = float(excess.max())
        worst_i = int(np.argmax(excess))
        pcts = spec["marginal"]["pooled_norm_quantiles_pct"]
        checks.append(Check(
            "pooled_quantiles_dev", "relative_vector", float(np.abs(devs).max()) * 100,
            f"worst p{pcts[worst_i]}: {vals[worst_i]/1e6:.2f} MW vs {targets[worst_i]/1e6:.2f} "
            f"+/-{rels[worst_i]*100:.0f}%",
            worst <= 0.0,
            float(np.sqrt((devs ** 2).mean())),
            target=0.0,
            feas_dev=max(0.0, worst),
            bias=float(devs.mean()) * 100,
            spread=float(devs.std()) * 100,
        ))

    # --- pc1 var share (floor) ---
    if "pc1_var_share" in tol:
        lo = tol["pc1_var_share"]["min"]
        target = spec["cross_rack"]["pc1_var_share"]
        val = stats["pc1_var_share"]
        checks.append(Check(
            "pc1_var_share", "floor", val, f">= {lo}", val >= lo, _rel_dev(val, target),
            target=target,
            feas_dev=max(0.0, (lo - val) / target),
        ))

    # --- ramp kurtosis floors, one per family ---
    if "total_ramp_excess_kurtosis" in tol:
        lo = tol["total_ramp_excess_kurtosis"]["min"]
        target = spec["temporal"]["total_ramp_excess_kurtosis"]
        val = stats["total_ramp_excess_kurtosis"]
        checks.append(Check(
            "total_ramp_excess_kurt", "floor", val, f">= {lo}", val >= lo,
            _rel_dev(val, target),
            target=target,
            feas_dev=max(0.0, (lo - val) / target),
        ))

    if "rack_ramp_excess_kurtosis" in tol:
        lo = tol["rack_ramp_excess_kurtosis"]["min"]
        target = spec["temporal"]["rack_ramp_excess_kurtosis"]
        val = stats["rack_ramp_excess_kurtosis"]
        checks.append(Check(
            "rack_ramp_excess_kurt", "floor", val, f">= {lo}", val >= lo,
            _rel_dev(val, target),
            target=target,
            feas_dev=max(0.0, (lo - val) / target),
        ))

    # --- per-rack ramp level (relative; guards against white-noise faking) ---
    if "rack_ramp_abs_mean" in tol:
        rel = tol["rack_ramp_abs_mean"]["rel"]
        target = spec["temporal"]["rack_ramp_abs_mean_W"]
        val = stats["rack_ramp_abs_mean_W"]
        d = _rel_dev(val, target)
        checks.append(Check(
            "rack_ramp_abs_mean_W", "relative", val,
            f"{val/1e3:.1f} kW vs {target/1e3:.1f} +/-{rel*100:.0f}%", abs(d) <= rel, d,
            target=target,
            feas_dev=max(0.0, abs(d) - rel),
        ))

    # --- ramp synchronization ratio (band); total ramp level is implied by
    #     rack level x this ratio, so it gets no separate check ---
    if "ramp_sync_ratio" in tol:
        lo, hi = tol["ramp_sync_ratio"]["lo"], tol["ramp_sync_ratio"]["hi"]
        target = spec["temporal"]["ramp_sync_ratio"]
        val = stats["ramp_sync_ratio"]
        checks.append(Check(
            "ramp_sync_ratio", "band", val, f"in [{lo}, {hi}]", lo <= val <= hi,
            _rel_dev(val, target),
            target=target,
            feas_dev=max(0.0, lo - val, val - hi) / target,
        ))

    # --- off-diagonal correlation mean (band) ---
    if "offdiag_corr_mean" in tol:
        lo, hi = tol["offdiag_corr_mean"]["lo"], tol["offdiag_corr_mean"]["hi"]
        target = spec["cross_rack"]["offdiag_corr_mean"]
        val = stats["offdiag_corr_mean"]
        checks.append(Check(
            "offdiag_corr_mean", "band", val, f"in [{lo}, {hi}]", lo <= val <= hi,
            _rel_dev(val, target),
            target=target,
            feas_dev=max(0.0, lo - val, val - hi) / target,
        ))

    # --- persistence: 1/e autocorrelation time of the total (band) ---
    if "autocorr_tau" in tol:
        lo, hi = tol["autocorr_tau"]["lo"], tol["autocorr_tau"]["hi"]
        target = spec["temporal"]["autocorr_1e_tau_steps"]
        val = float(stats["autocorr_1e_tau_steps"])
        checks.append(Check(
            "autocorr_tau_steps", "band", val, f"in [{lo}, {hi}]", lo <= val <= hi,
            _rel_dev(val, target),
            target=target,
            feas_dev=max(0.0, lo - val, val - hi) / target,
        ))

    # --- physical capacity ceiling on the peak (from the year envelope) ---
    if "total_max" in tol:
        cap = tol["total_max"]["max"]
        target = spec["aggregate"]["total_max_W"]  # the day's own peak, for Q_faithful
        val = stats["total_max_W"]
        checks.append(Check(
            "total_max_W", "ceiling", val,
            f"{val/1e6:.2f} MW <= capacity {cap/1e6:.2f} MW", val <= cap,
            _rel_dev(val, target),
            target=target,
            feas_dev=max(0.0, (val - cap) / cap),
        ))

    return Report(
        checks=checks,
        distance_feasible=float(sum(c.feas_dev ** 2 for c in checks)),
        distance_faithful=float(sum(c.norm_dev ** 2 for c in checks)),
        stats=stats,
        n_traces=n_traces,
    )


def validate(P: np.ndarray, spec: str | Path | dict, dt: float = 15.0) -> Report:
    """Per-trace acceptance test (ABC accept) + single-seed distances.

    NOTE: single-seed Q is realization-noise dominated (~20 jobs/day); use
    `validate_ensemble` as the calibration objective, this only as the per-trace
    accept test.
    """
    return _check_stats(compute_stats(P, dt), load_spec(spec), n_traces=1)


def validate_ensemble(traces: list, spec: str | Path | dict, dt: float = 15.0) -> Report:
    """MSM objective: average s(P) across seeds FIRST, then compare once.

    E[s] estimated over N traces has sd ~ single-seed-sd / sqrt(N); at N=20 the
    total_mean noise (~18%) drops to ~4%, below the +/-7% tolerance, so Q
    measures theta rather than the seed. This is the objective `calibrate.py`
    minimizes; the tolerances then act on the ensemble MEAN (a bias test),
    while per-seed acceptance is `pass_rate`.
    """
    if not traces:
        raise ValueError("validate_ensemble needs at least one trace")
    stats_list = [compute_stats(np.asarray(P), dt) for P in traces]
    avg = {}
    for k, v0 in stats_list[0].items():
        vals = [s[k] for s in stats_list]
        if isinstance(v0, np.ndarray):
            avg[k] = np.mean(np.stack(vals), axis=0)
        else:
            avg[k] = float(np.mean(vals))
    return _check_stats(avg, load_spec(spec), n_traces=len(traces))


def pass_rate(traces: list, spec: str | Path | dict, dt: float = 15.0):
    """Shipping gate: fraction of individual traces passing the accept test.

    Returns (rate, reports). Gate on e.g. rate >= 0.8 -- ensemble-mean checks
    alone would accept a theta whose typical realization fails.
    """
    spec = load_spec(spec)
    reports = [validate(np.asarray(P), spec, dt) for P in traces]
    return sum(r.passed for r in reports) / len(reports), reports
