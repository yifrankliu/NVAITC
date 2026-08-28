"""Year-envelope module: makes the 2023 year data load-bearing.

Reads the full-year Frontier2023 sheet once and emits `spec/envelope.json`:

  - capacity_W: the machine's demonstrated peak compute power (27.70 MW).
    OWNS the number freeze.py pins as the total_max ceiling tolerance.
  - daily-regime percentiles over OPERATIONAL days: the distribution of daily
    mean/std/min/max/range. Turns "regime A" from one day into a family, and
    lets regime-B shifts be specified in year-percentile units instead of
    guesses (e.g. "shift to the 99th pct of daily means").
  - context: where the frozen calibration day (2024-04-07) sits in that family.

Operational-day filter (data-driven, 2026-08-16 investigation):
  - 2023-04-01/02 are a genuine outage (daily means 2.8 / 5.6 MW, min 0.76 MW,
    PUE rising to ~1.2 as accessory power dominates) -> EXCLUDED by the
    `daily mean >= 7 MW` rule (the only 2 days below 7; next lowest ~8).
  - ~12 other dates contain brief sub-3 MW dips (single 10-min scrubs) but are
    otherwise normal -> KEPT for daily stats, listed separately as `dip_days`.
  - capacity is taken over ALL rows (a demonstrated peak is a peak regardless).

Decisions carried (Frank, 2026-08-16): 2023 envelope ACCEPTED with staleness
caveat (envelope 2023, calibration day 2024; the day sits at the 98.8th pct of
2023 daily means -- deliberate, LC-Opt precedent + forward-looking).

Usage:
    python -m optimal_dc.workload_gen_pipeline.envelope          # writes spec/envelope.json
Requires pandas + openpyxl (run under the ML_workspace env; the module itself
only imports them lazily so the rest of workload_gen_pipeline stays dependency-light).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_XLSX = Path(__file__).parents[2] / "data" / "Frontier HPC & Facility Data.xlsx"
_OUT = Path(__file__).parent / "spec" / "envelope.json"

OP_DAY_MIN_MEAN_MW = 7.0   # operational-day rule (see module docstring)
MIN_ROWS_PER_DAY = 100     # 10-min rows; full day = 144

# the frozen calibration day's aggregate numbers (from spec/regime_A.json),
# repeated here only for the percentile-context computation
_DAY_MEAN_MW = 16.12
_DAY_STD_MW = 7.90
_DAY_MAX_MW = 26.61

_PCTS = [1, 5, 25, 50, 75, 95, 99]


def load_year(xlsx_path: str | Path = _XLSX):
    """-> (t, compute_MW) as pandas Series (lazy pandas import)."""
    import pandas as pd

    d = pd.read_excel(xlsx_path, sheet_name="Frontier2023", skiprows=[1])
    t = pd.to_datetime(d["Date/Time"], errors="coerce")
    c = pd.to_numeric(d["Frontier Compute Power"], errors="coerce")
    ok = t.notna() & c.notna()
    return t[ok], c[ok]


def build_envelope(xlsx_path: str | Path = _XLSX, out_path: str | Path = _OUT,
                   write: bool = True) -> dict:
    import pandas as pd

    t, c = load_year(xlsx_path)
    df = pd.DataFrame({"t": t, "MW": c})
    day = df.groupby(df["t"].dt.date)["MW"].agg(["count", "mean", "std", "min", "max"])
    day = day[day["count"] >= MIN_ROWS_PER_DAY]
    day["range"] = day["max"] - day["min"]

    op = day[day["mean"] >= OP_DAY_MIN_MEAN_MW]
    outage_days = [str(d) for d in day.index[day["mean"] < OP_DAY_MIN_MEAN_MW]]
    dip_days = sorted({str(d) for d in df.loc[df["MW"] < 3.0, "t"].dt.date}
                      - set(outage_days))

    def pcts(s) -> dict:
        return {f"p{p:02d}": float(np.percentile(s, p)) for p in _PCTS}

    env = {
        "meta": {
            "source": f"{Path(xlsx_path).name} / sheet Frontier2023",
            "rows": int(len(df)),
            "dt_s": 600,
            "year": 2023,
            "n_days_total": int(len(day)),
            "n_days_operational": int(len(op)),
            "op_day_rule": f"daily mean >= {OP_DAY_MIN_MEAN_MW} MW (excludes the Apr 1-2 outage only)",
            "outage_days": outage_days,
            "dip_days": dip_days,
            "provenance": "built by workload_gen_pipeline/envelope.py; staleness caveat: envelope 2023, calibration day 2024-04-07",
        },
        "capacity_W": float(c.max() * 1e6),   # demonstrated peak, ALL rows
        "compute_all_rows_MW": {"min": float(c.min()), **pcts(c), "max": float(c.max())},
        "daily_operational_MW": {
            "mean": pcts(op["mean"]),
            "std": pcts(op["std"]),
            "min": pcts(op["min"]),
            "max": pcts(op["max"]),
            "range": pcts(op["range"]),
        },
        "calibration_day_context": {
            "date": "2024-04-07",
            "mean_MW": _DAY_MEAN_MW,
            "mean_pct_of_op_days": float((op["mean"] < _DAY_MEAN_MW).mean() * 100),
            "std_MW": _DAY_STD_MW,
            "std_pct_of_op_days": float((op["std"] < _DAY_STD_MW).mean() * 100),
            "max_MW": _DAY_MAX_MW,
            "max_pct_of_op_days": float((op["max"] < _DAY_MAX_MW).mean() * 100),
            "note": "high-activity day kept deliberately (LC-Opt precedent, forward-looking)",
        },
    }

    if write:
        Path(out_path).write_text(json.dumps(env, indent=2), encoding="utf-8")
        print(f"wrote {out_path}")
    print(f"capacity {env['capacity_W']/1e6:.2f} MW | operational days "
          f"{env['meta']['n_days_operational']}/{env['meta']['n_days_total']} "
          f"(outage: {outage_days}) | dip days: {len(dip_days)}")
    print(f"daily mean MW p50 {env['daily_operational_MW']['mean']['p50']:.2f}  "
          f"p99 {env['daily_operational_MW']['mean']['p99']:.2f} | "
          f"calib day mean pct {env['calibration_day_context']['mean_pct_of_op_days']:.1f}%")
    return env


if __name__ == "__main__":
    build_envelope(*sys.argv[1:])
