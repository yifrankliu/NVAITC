"""Per-CDU-group power -> FMU exogenous channels.

Maps a (T, 25) per-CDU-group watt array (synthetic from generate(), or the real
CSV's power columns) to the (T, 16) exogenous trace the 5-cabinet FMU consumes:
15 branch heat inputs (5 cabinets x 3 branches, cabinet-major) + Towb.

Pass-through by design: no clipping, time-rolls, softmax, or smoothing. Shaping
belongs upstream in the generator; this module only slices and rescales.

MAGNITUDE -- /9, from two independent divisions:
  1. /CABINET_PARALLEL (3): a CSV column is one CDU GROUP, ~3 real cabinets. The
     FMU instantiates ONE representative cabinet (nParallel=3), so it takes one
     cabinet's share.
  2. /N_BRANCHES (3): that cabinet's load splits across its 3 blade groups,
     which is what ComputePowerBlade{1,2,3} take.
  np.repeat COPIES, it does not divide -- both divisions must precede it.
  Checks out on the real trace: 645 kW column /9 = 71.7 kW/branch, 215 kW per
  cabinet, vs a physical 645/(74/25) = 217.9 kW. self_test() pins this.

  EMPIRICALLY VERIFIED (energy-balance test, 2026-07-16): constant 60 kW per
  blade (180 kW/cabinet), 3 h to steady state -> CDU HEX Q_flow = 3.019x the
  injection (+1.9% = CDU pump heat). The FMU's x3 heat recovery via the flow
  scalers is real and happens exactly once, so inputs are per-cabinet and /9
  is the faithful constant -- no hidden heat-side xN.

branch_split "equal" is the max-entropy choice (no branch-level ground truth
exists), but it makes the FMU's 15 Valve_Stpts inputs inert: with identical
branch loads the optimal split is uniform by symmetry, so the effective action
space is 11, not 26. State this in any writeup.

slice_mode picks 5 of the 25 columns. On the rank-1 real day this is a LEVEL
choice, not a shape one -- subsets differ by up to ~15% in level but all track
the fleet total at r >= 0.998.
"""

from __future__ import annotations

import csv
import pathlib

import numpy as np

N_BRANCHES = 3          # blade-group branches per cabinet (FMU structure)
CABINET_PARALLEL = 3    # 3 real cabinets per CDU group; FMU instantiates 1 with nParallel=3
N_FMU_CABINETS = 5      # the FMU slice consumes 5 CDU-group columns
TOWB_OFFSET_K = 15.0    # env convention before the FMU (prevents CT saturation)

DIVISOR = CABINET_PARALLEL * N_BRANCHES     # both divisions; see module docstring
CONVENTION = f"/{DIVISOR} (/{CABINET_PARALLEL} cabinets per CDU group x /{N_BRANCHES} branches)"

ROUND_DECIMALS = 2
# Worst-case watts a branches -> cabinet -> group round-trip loses to rounding.
ROUND_BUDGET_W = N_BRANCHES * CABINET_PARALLEL * 0.5 * 10.0 ** -ROUND_DECIMALS


def select_columns(P: np.ndarray, mode: str = "first5",
                   n: int = N_FMU_CABINETS) -> list[int]:
    """Choose which n of P's columns feed the FMU slice.

    'first5'          : columns 0..n-1 -- matches upstream frontier_env.
    'representative'  : the n columns closest to the fleet in (mean, CoV, corr
        with total). Selects for TYPICAL, so outlier columns are dropped; pass
        an explicit list if you want the range covered instead.
    list[int]         : your own columns, recorded in the metadata.
    """
    if isinstance(mode, (list, tuple)):
        idx = list(mode)
        if len(idx) != n:
            raise ValueError(f"explicit column list must have length {n}")
        return idx
    if mode == "first5":
        return list(range(n))
    if mode == "representative":
        total = P.sum(axis=1)
        mean = P.mean(axis=0)
        cov = P.std(axis=0) / mean
        corr = np.array([np.corrcoef(P[:, r], total)[0, 1] for r in range(P.shape[1])])
        feats = np.stack([mean, cov, corr])                      # (3, n_cols)
        center = feats.mean(axis=1, keepdims=True)
        scale = feats.std(axis=1, keepdims=True)
        scale[scale == 0] = 1.0
        score = (((feats - center) / scale) ** 2).sum(axis=0)    # distance to fleet
        return sorted(np.argsort(score)[:n].tolist())
    raise ValueError(f"unknown slice mode {mode!r}")


def disaggregate(
    P: np.ndarray,
    towb_C: np.ndarray | None = None,
    *,
    slice_mode="first5",
    branch_split: str = "equal",
    towb_offset_K: float = TOWB_OFFSET_K,
) -> tuple[np.ndarray, dict]:
    """(T, 25) watts [+ wet-bulb degC] -> ((T, 15|16) exogenous trace, metadata).

    Returns the trace (15 branch powers, + Towb in KELVIN with the env offset
    if towb_C is given) and a metadata dict declaring every convention used --
    written into trace sidecars so no output can silently mix regimes.

    Conservation: (sum of a cabinet's 3 branches) * CABINET_PARALLEL == column.
    """
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[1] < N_FMU_CABINETS:
        raise ValueError(f"P must be (T, >={N_FMU_CABINETS}) watts, got {P.shape}")
    if branch_split != "equal":
        raise ValueError("only branch_split='equal' is implemented (see docstring)")

    cols = select_columns(P, slice_mode)

    power = P[:, cols] / DIVISOR                       # per-BRANCH watts (/3 cabinets, /3 branches)
    power = np.repeat(power, N_BRANCHES, axis=1)       # fan out to 3 equal branches, cabinet-major
    power = power.round(ROUND_DECIMALS)                # precision (see ROUND_BUDGET_W)

    meta = {
        "divisor": DIVISOR,
        "convention": CONVENTION,
        "thermal_regime": f"/{DIVISOR}: ~215 kW/cabinet, ~72 kW/branch at the "
                          "real day's 645 kW column mean",
        "columns": cols,
        "slice_mode": str(slice_mode),
        "branch_split": branch_split,
        "towb_offset_K": towb_offset_K if towb_C is not None else None,
        "warning": "never compare a /9 number against a /15 (sustain-lc lineage) number",
    }

    if towb_C is None:
        return power, meta
    towb_K = np.asarray(towb_C, dtype=float) + 273.15 + towb_offset_K
    return np.concatenate([power, towb_K.reshape(-1, 1)], axis=1), meta


def self_test(csv_path: str | None = None) -> bool:
    """Pin the two properties that must hold, so a divisor edit cannot pass silently.

    1. CONSERVATION (exact, synthetic input): the 3 branches of a cabinet sum to
       one cabinet's share, and times CABINET_PARALLEL they recover the original
       CDU-group column. This is what fails if either /3 is dropped.
    2. MAGNITUDE (real trace, if reachable): per-branch heat must land in the
       [50, 100] kW band implied by sustain-lc's own commented-out clip, and the
       implied per-cabinet load must match column_mean / 2.96 within 2%.
    """
    ok = True

    T, n_cols = 40, 25
    rng = np.random.default_rng(0)
    P = rng.uniform(4e5, 9e5, size=(T, n_cols))
    exo, _ = disaggregate(P, slice_mode="first5")

    if exo.shape != (T, N_FMU_CABINETS * N_BRANCHES):
        print(f"  [FAIL] shape {exo.shape}, expected {(T, N_FMU_CABINETS * N_BRANCHES)}")
        ok = False

    cab = exo.reshape(T, N_FMU_CABINETS, N_BRANCHES).sum(axis=2)   # per-cabinet watts
    recovered = cab * CABINET_PARALLEL                             # back to group level
    if not np.allclose(recovered, P[:, :N_FMU_CABINETS], rtol=0, atol=ROUND_BUDGET_W):
        worst = np.abs(recovered - P[:, :N_FMU_CABINETS]).max()
        ratio = float(np.median(recovered / P[:, :N_FMU_CABINETS]))
        print(f"  [FAIL] conservation: max abs err {worst:.4g} W, median ratio {ratio:.4f}")
        print(f"         (ratio {ratio:.2f} means the divisor is off by that factor)")
        ok = False
    else:
        print(f"  [pass] conservation: 3 branches x {CABINET_PARALLEL} cabinets == group column")

    if csv_path is None:
        here = pathlib.Path(__file__).resolve().parents[1]
        csv_path = here / "external" / "sustain-lc" / "input_04-07-24.csv"
    csv_path = pathlib.Path(csv_path)
    if not csv_path.exists():
        print(f"  [skip] magnitude check: {csv_path.name} not found")
        return ok

    with open(csv_path, newline="") as f:
        rows = list(csv.reader(f))
    pidx = [i for i, h in enumerate(rows[0]) if h.startswith("power")]
    real = np.array([[float(r[i]) for i in pidx] for r in rows[1:]])
    exo_r, _ = disaggregate(real, slice_mode="first5")
    per_branch_kW = exo_r.mean() / 1e3
    per_cabinet_kW = per_branch_kW * N_BRANCHES
    expected_kW = real.mean() / 1e3 / (74 / 25)     # true cabinets per CDU group

    if not 50.0 <= per_branch_kW <= 100.0:
        print(f"  [FAIL] magnitude: {per_branch_kW:.1f} kW/branch outside [50, 100]")
        ok = False
    elif abs(per_cabinet_kW / expected_kW - 1) > 0.02:
        print(f"  [FAIL] magnitude: {per_cabinet_kW:.1f} kW/cabinet vs physical "
              f"{expected_kW:.1f} kW ({per_cabinet_kW/expected_kW:.3f}x)")
        ok = False
    else:
        print(f"  [pass] magnitude: {per_branch_kW:.1f} kW/branch, "
              f"{per_cabinet_kW:.1f} kW/cabinet (physical {expected_kW:.1f} kW)")
    return ok


if __name__ == "__main__":
    print(f"disaggregator self-test  [{CONVENTION}]")
    raise SystemExit(0 if self_test() else 1)
