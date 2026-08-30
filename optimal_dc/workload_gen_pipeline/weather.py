"""NOAA wet-bulb sourcing (stage 1c): real weather for synthetic workload days.

Wet-bulb is the second exogenous FMU driver (cooling-tower side). Design rule:
weather is SOURCED from real observations, never synthesized -- one channel
folds dry-bulb + humidity physics no simple generator reproduces honestly.

Source: KTYS (Knoxville McGhee Tyson, WBAN 13891), NCEI LCD v2 station-year
CSVs cached in weather_cache/ (committed to the repo by decision -- the data
is part of the claim). Chosen over the closer Oak Ridge ATDD station because
ATDD's public record is GHCN-Daily: no hourly humidity exists there, so
wet-bulb is underivable regardless of distance.

CERTIFICATION (2026-08-17, n=1 day -- the only day of facility sensor data we
own; rerun `python -m optimal_dc.workload_gen_pipeline.weather` anytime): KTYS vs ORNL's on-site
OA Wetbulb sensor on 2024-04-07: bias -0.13 C, RMSE 0.63 C, corr 0.986 -> GO.
The gate also fixed two implementation traps, encoded below:
  1. LCD v2 temperatures are ALREADY degC (v1 was degF). Applying the F->C
     conversion produces a -21 C bias at corr 0.98 -- do NOT convert.
  2. LCD DATE is Local STANDARD Time year-round (UTC-5 here); the facility
     day runs on local CIVIL time -> +1 h correction during DST (best-fit
     alignment -1.0 h on the April validation day, exactly the LST/EDT gap).
     DST-transition days carry a <=1 h edge ambiguity; accepted, documented.

Interpolation hourly -> 15 s is linear: wet-bulb is slow-moving, but note the
sub-hourly variance of a real sensor is removed (provenance caveat).

API:
    wetbulb_for("2023-07-19")     -> (5761,) degC on the 15 s civil-day grid
    day_stats(2023)               -> per-day min/mean/max wet-bulb table
    percentile_day(2023, 95)      -> the date whose daily-mean wb sits at p95
    validate_gate()               -> the certification numbers (self-test)
"""

from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from datetime import date as _date, timedelta
from pathlib import Path

import numpy as np

STATION = "USW00013891"          # KTYS / McGhee Tyson (WBAN 13891, WMO 723260)
URL_FMT = ("https://www.ncei.noaa.gov/oa/local-climatological-data/v2/access/"
           "{year}/LCD_{station}_{year}.csv")
CACHE = Path(__file__).parent / "weather_cache"
MANIFEST = CACHE / "manifest.json"
REPORT_TYPES = ("FM-15", "FM-16")   # hourly METAR + specials; SOD/SOM rows dropped
_REAL_CSV = Path(__file__).parents[1] / "external" / "sustain-lc" / "input_04-07-24.csv"


# ----------------------------------------------------------------- fetch ---
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fetch(year: int) -> Path:
    """Cache-on-demand: return the station-year CSV, downloading if absent.
    Hand-placed files are used as-is (pre-warmed cache). Every file gets a
    manifest entry {url, size, sha256, recorded} for provenance."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"LCD_{STATION}_{year}.csv"
    url = URL_FMT.format(year=year, station=STATION)
    if not path.exists():
        print(f"downloading {url} ...")
        urllib.request.urlretrieve(url, path)

    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    if path.name not in manifest or manifest[path.name]["sha256"] != _sha256(path):
        manifest[path.name] = {
            "url": url,
            "size": path.stat().st_size,
            "sha256": _sha256(path),
            "recorded": _date.today().isoformat(),
        }
        MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


# ----------------------------------------------------------------- parse ---
def _is_dst(d: _date) -> bool:
    """US DST rule (date-level; the <=1 h ambiguity on the two transition
    days themselves is accepted): second Sunday of March .. first Sunday of
    November."""
    def nth_sunday(year, month, n):
        d0 = _date(year, month, 1)
        return d0 + timedelta(days=(6 - d0.weekday()) % 7 + 7 * (n - 1))
    return nth_sunday(d.year, 3, 2) <= d < nth_sunday(d.year, 11, 1)


def load_hourly(year: int) -> tuple[np.ndarray, np.ndarray]:
    """-> (t_lst_s, wb_C): observation times (seconds since Jan 1 00:00 LST)
    and wet-bulb degC, sorted, FM-15/16 only. Suspect-flagged values are KEPT
    (the trailing 's' flag is stripped, the value retained)."""
    t, wb = [], []
    with open(_fetch(year), newline="") as f:
        for r in csv.DictReader(f):
            if r["REPORT_TYPE"].strip() not in REPORT_TYPES:
                continue
            raw = r["HourlyWetBulbTemperature"].strip().rstrip("s")  # 's' = suspect
            if raw in ("", "*"):
                continue
            d = r["DATE"]                     # YYYY-MM-DDTHH:MM:SS, LST
            day = _date.fromisoformat(d[:10])
            doy = (day - _date(year, 1, 1)).days
            t.append(doy * 86400 + int(d[11:13]) * 3600 + int(d[14:16]) * 60)
            wb.append(float(raw))             # LCD v2 is ALREADY degC -- no conversion
    t, wb = np.asarray(t, float), np.asarray(wb, float)
    order = np.argsort(t)
    return t[order], wb[order]


# ------------------------------------------------------------------- API ---
def wetbulb_for(day: str, n_steps: int = 5761, dt: float = 15.0) -> np.ndarray:
    """Wet-bulb (degC) for civil-time day 'YYYY-MM-DD' on the 15 s grid.

    Obs are shifted LST -> civil (+1 h when DST) so index 0 = 00:00:00 civil
    time, matching the facility CSV convention. Neighbor-day obs are included
    so interpolation has support at the day's edges.
    """
    d = _date.fromisoformat(day)
    t_lst, wb = load_hourly(d.year)
    # pull in adjacent-year data if the day is at a year boundary
    if d.month == 1 and d.day == 1:
        t0, wb0 = load_hourly(d.year - 1)
        t_lst = np.concatenate([t0 - (_date(d.year, 1, 1) - _date(d.year - 1, 1, 1)).days * 86400, t_lst])
        wb = np.concatenate([wb0, wb])
    if d.month == 12 and d.day == 31:
        t1, wb1 = load_hourly(d.year + 1)
        t_lst = np.concatenate([t_lst, t1 + (_date(d.year + 1, 1, 1) - _date(d.year, 1, 1)).days * 86400])
        wb = np.concatenate([wb, wb1])

    day_start_lst = (d - _date(d.year, 1, 1)).days * 86400
    t_civil = t_lst - day_start_lst + (3600.0 if _is_dst(d) else 0.0)
    grid = np.arange(n_steps) * dt
    lo, hi = grid[0] - 86400, grid[-1] + 86400   # +/-1 day support window
    m = (t_civil >= lo) & (t_civil <= hi)
    if m.sum() < 12:
        raise ValueError(f"only {int(m.sum())} wet-bulb obs near {day} -- station gap?")
    return np.interp(grid, t_civil[m], wb[m])


def day_stats(year: int) -> list[dict]:
    """Per-day wet-bulb summary for regime selection: [{date, min, mean, max}]."""
    t, wb = load_hourly(year)
    out = []
    days = (_date(year, 12, 31) - _date(year, 1, 1)).days + 1
    for doy in range(days):
        m = (t >= doy * 86400) & (t < (doy + 1) * 86400)
        if m.sum() < 12:                       # station gap -> skip the day
            continue
        out.append({
            "date": (_date(year, 1, 1) + timedelta(days=doy)).isoformat(),
            "min": float(wb[m].min()),
            "mean": float(wb[m].mean()),
            "max": float(wb[m].max()),
        })
    return out


def percentile_day(year: int, q: float, stat: str = "mean") -> dict:
    """The day whose daily `stat` wet-bulb is closest to the q-th percentile
    of the year -- e.g. percentile_day(2023, 95) = a hot-humid summer day,
    percentile_day(2023, 5) = a cold winter day. Regime-selection helper."""
    stats = day_stats(year)
    vals = np.array([s[stat] for s in stats])
    target = np.percentile(vals, q)
    return stats[int(np.argmin(np.abs(vals - target)))]


# -------------------------------------------------------------- self-test ---
def validate_gate(day: str = "2024-04-07", tol_rmse_C: float = 1.0) -> dict:
    """Re-run the certification: sourced wet-bulb vs the ORNL facility sensor
    (the one day of on-site data we own; n=1 caveat documented above)."""
    with open(_REAL_CSV, newline="") as f:
        rows = list(csv.reader(f))
    fac = np.array([float(r[-1]) for r in rows[1:]])
    ours = wetbulb_for(day, n_steps=len(fac))
    dvt = ours - fac
    res = {
        "day": day,
        "bias_C": float(dvt.mean()),
        "rmse_C": float(np.sqrt((dvt ** 2).mean())),
        "maxabs_C": float(np.abs(dvt).max()),
        "corr": float(np.corrcoef(ours, fac)[0, 1]),
    }
    res["go"] = res["rmse_C"] <= tol_rmse_C
    return res


if __name__ == "__main__":
    r = validate_gate()
    print("certification vs ORNL facility sensor (n=1 day):")
    print("  bias %+0.2f C | RMSE %.2f C | max|dev| %.2f C | corr %.4f -> %s"
          % (r["bias_C"], r["rmse_C"], r["maxabs_C"], r["corr"],
             "GO" if r["go"] else "NO-GO"))
    for q in (5, 50, 95):
        s = percentile_day(2023, q)
        print(f"  2023 p{q:02d} day: {s['date']}  wb mean {s['mean']:+.1f} C "
              f"(min {s['min']:+.1f} / max {s['max']:+.1f})")
