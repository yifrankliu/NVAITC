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

IMPORTANT: the statistics here must be computed the SAME way the spec was frozen
in workload_analysis.ipynb -- in particular ramps are PER-RACK first differences
pooled across racks and time (spec ramp_abs_mean_W ~= 0.126 MW is per-rack), and
correlation/PCA are over the 25 racks as variables.
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
    """Summary statistics of a (n_steps, n_racks) watt trace, matched to the spec."""
    n_steps, n_racks = P.shape
    total = P.sum(axis=1)

    # per-rack first differences, pooled (the spec's ramp convention)
    ramps = np.diff(P, axis=0).ravel()

    corr = np.corrcoef(P, rowvar=False)
    offdiag = corr[~np.eye(n_racks, dtype=bool)]

    # PCA: fraction of total variance carried by PC1 (covariance eigenspectrum)
    cov = np.cov(P, rowvar=False)
    eig = np.linalg.eigvalsh(cov)
    pc1_share = float(eig[-1] / eig.sum())

    return {
        "per_rack_mean_W": P.mean(axis=0),
        "total_mean_W": float(total.mean()),
        "total_min_W": float(total.min()),
        "total_max_W": float(total.max()),
        "total_std_W": float(total.std()),
        "ramp_excess_kurtosis": _excess_kurtosis(ramps),
        "ramp_abs_mean_W": float(np.abs(ramps).mean()),
        "ramp_abs_p99_W": float(np.percentile(np.abs(ramps), 99)),
        "ramp_abs_max_W": float(np.abs(ramps).max()),
        "offdiag_corr_mean": float(offdiag.mean()),
        "offdiag_corr_min": float(offdiag.min()),
        "offdiag_corr_max": float(offdiag.max()),
        "pc1_var_share": pc1_share,
    }


# ------------------------------------------------------------------ report ---
@dataclass
class Check:
    name: str
    kind: str          # "relative" | "floor" | "band"
    value: float
    bound: str         # human-readable target/bound
    passed: bool
    norm_dev: float    # signed normalized deviation from the point target (for Q)

    def __str__(self) -> str:
        mark = "PASS" if self.passed else "FAIL"
        return f"  [{mark}] {self.name:<22} = {self.value:< 12.5g}  ({self.bound})"


@dataclass
class Report:
    checks: list[Check]
    distance: float           # MSM objective Q(theta)
    stats: dict = field(repr=False, default_factory=dict)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def __str__(self) -> str:
        head = f"Validation: {'PASS' if self.passed else 'FAIL'}   Q(theta) = {self.distance:.4g}"
        return "\n".join([head, *map(str, self.checks)])


# ---------------------------------------------------------------- validate ---
def load_spec(spec: str | Path | dict) -> dict:
    if isinstance(spec, dict):
        return spec
    return json.loads(Path(spec).read_text(encoding="utf-8"))


def validate(P: np.ndarray, spec: str | Path | dict, dt: float = 15.0) -> Report:
    """Run the acceptance test and compute the MSM distance for trace `P`."""
    spec = load_spec(spec)
    stats = compute_stats(P, dt)
    tol = spec["tolerances"]
    checks: list[Check] = []
    sq_devs: list[float] = []

    def rel_dev(value: float, target: float) -> float:
        return (value - target) / target if target != 0 else 0.0

    # --- per-rack mean (vector relative check) ---
    if "per_rack_mean" in tol:
        rel = tol["per_rack_mean"]["rel"]
        targets = spec["marginal"]["grand_mean_W"] * np.asarray(spec["marginal"]["per_rack_scale"])
        vals = stats["per_rack_mean_W"]
        devs = (vals - targets) / targets
        worst = float(np.abs(devs).max())
        checks.append(Check(
            "per_rack_mean", "relative", worst * 100,
            f"max |dev| {worst*100:.1f}% <= {rel*100:.0f}%", worst <= rel,
            float(np.sqrt((devs ** 2).mean())),  # RMS rel dev into Q
        ))
        sq_devs.append(checks[-1].norm_dev ** 2)

    # --- total mean (relative) ---
    if "total_mean" in tol:
        rel = tol["total_mean"]["rel"]
        target = spec["aggregate"]["total_mean_W"]
        val = stats["total_mean_W"]
        d = rel_dev(val, target)
        checks.append(Check(
            "total_mean_W", "relative", val,
            f"{val/1e6:.2f} MW vs {target/1e6:.2f} +/-{rel*100:.0f}%", abs(d) <= rel, d,
        ))
        sq_devs.append(d ** 2)

    # --- pc1 var share (floor) ---
    if "pc1_var_share" in tol:
        lo = tol["pc1_var_share"]["min"]
        target = spec["cross_rack"]["pc1_var_share"]
        val = stats["pc1_var_share"]
        checks.append(Check(
            "pc1_var_share", "floor", val, f">= {lo}", val >= lo, rel_dev(val, target),
        ))
        sq_devs.append(checks[-1].norm_dev ** 2)

    # --- ramp excess kurtosis (floor) ---
    if "ramp_excess_kurtosis" in tol:
        lo = tol["ramp_excess_kurtosis"]["min"]
        target = spec["temporal"]["ramp_excess_kurtosis"]
        val = stats["ramp_excess_kurtosis"]
        checks.append(Check(
            "ramp_excess_kurtosis", "floor", val, f">= {lo}", val >= lo, rel_dev(val, target),
        ))
        sq_devs.append(checks[-1].norm_dev ** 2)

    # --- off-diagonal correlation mean (band) ---
    if "offdiag_corr_mean" in tol:
        lo, hi = tol["offdiag_corr_mean"]["lo"], tol["offdiag_corr_mean"]["hi"]
        target = spec["cross_rack"]["offdiag_corr_mean"]
        val = stats["offdiag_corr_mean"]
        checks.append(Check(
            "offdiag_corr_mean", "band", val, f"in [{lo}, {hi}]", lo <= val <= hi,
            rel_dev(val, target),
        ))
        sq_devs.append(checks[-1].norm_dev ** 2)

    return Report(checks=checks, distance=float(sum(sq_devs)), stats=stats)
