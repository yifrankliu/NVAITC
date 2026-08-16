"""Per-CDU-group power -> FMU exogenous channels (the redesigned disaggregator).

Maps a `(T, 25)` per-CDU-group watt array (synthetic from generate(), or the
real CSV's power columns) to the `(T, 16)` exogenous trace the 5-cabinet FMU
consumes: 15 branch heat inputs (5 cabinets x 3 branches, cabinet-major) + Towb.

Inherits v0_exogenous's SHAPE-faithfulness (the settled part): NO mean+sigma
clipping, NO branch time-rolls, NO softmax redistribution, NO smoothing --
those sustain-lc transforms either fabricate structure (rolls: branch 3 is
branch 1's past -> fake learnable lag) or destroy it (softmax + 50-step mean
filter: cabinet-CV 0.484 -> 0.01).

What it FIXES vs v0 (which froze these for comparability with v1/v2):

  MAGNITUDE is an explicit two-convention knob (DEFAULT ÷15, decided by Frank
  2026-08-16 for continuity: every existing run, baseline, and prize-sizing
  number lives in the ÷15 regime, so deliveries stay comparable by default):
    - compat_v0=True  (DEFAULT): ÷15 = sustain-lc's ÷5 cabinet slot x ÷3
      branches -- the lineage convention. Under-loads the FMU at 9/15 = 0.6x
      of the faithful heat.
    - compat_v0=False (opt-in "faithful"): ÷9. Source-verified plumbing: the
      compiled FMU cabinet is REPRESENTATIVE of 3 parallel cabinets
      (parallelFlow nParallel=3, inlet/3 outlet*3, forced identical) -> ÷3
      cabinets, then ÷3 branches. Column mean 645 kW ÷9 = 72 kW/branch,
      inside the [50, 100] kW band sustain-lc's own (commented-out) clip
      implies; ÷15 gives 43 kW, below it. Opting in = entering a NEW thermal
      regime that needs its own baseline pass (T_max, feasibility corners).
  NEVER compare a ÷9 number against a ÷15 number.

  EXPLICIT knobs for the two invented-structure defaults (REVISIT notes in
  memory; improvements queued behind branch-level data / the 25-block FMU):
    - branch split "equal": each cabinet's 3 branches get identical thirds.
      Imposes PERFECT intra-cabinet correlation (freezes the FMU's sub-cabinet
      spatial axis) -- the max-entropy choice, since branch-level ground truth
      does not exist in the CSV. Documented, not hidden.
    - slice "first5": FMU consumes 5 of 25 columns; first5 matches upstream
      frontier_env behavior exactly (bit-comparability). "representative"
      instead picks the 5 columns statistically closest to the fleet
      (mean level, CoV, correlation with the facility total).

  RESIDUAL APPROXIMATION: ÷9 inherits the FMU's own nParallel=3 rounding;
  the real ratio is 74 cabinets / 25 CDU groups ~= 2.96 (~1.3% off).

Proof obligation (test_compat_identity): disaggregate(real CSV, compat_v0=True)
must reproduce v0_exogenous(...) EXACTLY, pinning this code to the audited
behavior so the only new trust needed is the ÷9 constant.
"""

from __future__ import annotations

import numpy as np

N_BRANCHES = 3          # blade-group branches per cabinet (FMU structure)
CABINET_PARALLEL = 3    # FMU cabinet represents 3 parallel cabinets (nParallel=3)
V0_CABINET_DIV = 5      # sustain-lc's constant in the same slot (compat only)
N_FMU_CABINETS = 5      # the FMU slice consumes 5 CDU-group columns
TOWB_OFFSET_K = 15.0    # env convention before the FMU (prevents CT saturation)


def select_columns(P: np.ndarray, mode: str = "first5",
                   n: int = N_FMU_CABINETS) -> list[int]:
    """Choose which n of P's columns feed the FMU slice.

    'first5'         : columns 0..n-1 -- upstream frontier_env behavior.
    'representative' : the n columns statistically closest to the fleet:
        score = normalized distance in (mean level, CoV, corr with total).
        Note: excludes-by-score, so the rack-14-group outlier (scale 0.652)
        is naturally dropped -- this is representative-of-TYPICAL. Pass an
        explicit list for representative-of-range designs.
    explicit list[int]: your own columns (documented in the metadata).
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
    compat_v0: bool = True,
    branch_split: str = "equal",
    towb_offset_K: float = TOWB_OFFSET_K,
) -> tuple[np.ndarray, dict]:
    """(T, 25) watts [+ wet-bulb degC] -> ((T, 15|16) exogenous trace, metadata).

    Returns the trace (15 branch powers, + Towb column in KELVIN with the env
    offset if towb_C is given) and a metadata dict declaring every convention
    used -- written into trace sidecars so no output can silently mix regimes.
    """
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[1] < N_FMU_CABINETS:
        raise ValueError(f"P must be (T, >={N_FMU_CABINETS}) watts, got {P.shape}")
    if branch_split != "equal":
        raise ValueError("only branch_split='equal' is implemented (see docstring)")

    cols = select_columns(P, slice_mode)
    cab_div = V0_CABINET_DIV if compat_v0 else CABINET_PARALLEL
    divisor = cab_div * N_BRANCHES

    power = P[:, cols] / divisor                       # per-branch watts
    power = np.repeat(power, N_BRANCHES, axis=1)       # 3 EQUAL branches, cabinet-major
    power = power.round(2)                             # v0 convention (identity test)

    meta = {
        "divisor": divisor,
        "convention": "compat_v0 (/15, sustain-lc lineage)" if compat_v0
                      else "faithful (/9 = /3 nParallel x /3 branches)",
        "columns": cols,
        "slice_mode": str(slice_mode),
        "branch_split": branch_split,
        "towb_offset_K": towb_offset_K if towb_C is not None else None,
        "warning": "never compare /9 results against /15 results",
    }

    if towb_C is None:
        return power, meta
    towb_K = np.asarray(towb_C, dtype=float) + 273.15 + towb_offset_K
    return np.concatenate([power, towb_K.reshape(-1, 1)], axis=1), meta


def test_compat_identity() -> bool:
    """disaggregate(real CSV, compat_v0=True, first5) must equal v0_exogenous().

    Pins this module to the audited harness behavior; run after any edit here.
    """
    import csv as _csv
    import pathlib
    import sys

    val_dir = pathlib.Path(__file__).parents[1] / "validation"
    sys.path.insert(0, str(val_dir))
    from rollout import v0_exogenous  # noqa: E402

    csv_path = pathlib.Path(__file__).parents[1] / "external" / "sustain-lc" / "input_04-07-24.csv"
    with open(csv_path, newline="") as f:
        rows = list(_csv.reader(f))
    hdr = rows[0]
    p_idx = [i for i, h in enumerate(hdr) if h.startswith("power")]
    P = np.array([[float(r[i]) for i in p_idx] for r in rows[1:]])
    towb = np.array([float(r[-1]) for r in rows[1:]])

    ours, meta = disaggregate(P, towb, compat_v0=True, slice_mode="first5")
    ref = v0_exogenous(use_all_columns=False)
    same = ours.shape == ref.shape and np.allclose(ours, ref, rtol=0, atol=1e-9)
    print(f"compat identity vs v0_exogenous: {'PASS' if same else 'FAIL'} "
          f"(shape {ours.shape} vs {ref.shape}, divisor {meta['divisor']})")
    if not same and ours.shape == ref.shape:
        d = np.abs(ours - ref)
        print(f"  max abs diff {d.max():.6g} at {np.unravel_index(d.argmax(), d.shape)}")
    return same


if __name__ == "__main__":
    ok = test_compat_identity()
    raise SystemExit(0 if ok else 1)
