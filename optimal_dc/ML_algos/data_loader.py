"""
Data loader: CSV + synthetic workload_gen -> exogenous traces for FrontierEnv.

Handles loading real Frontier data and optional regime-A synthetic extension.
"""

import csv
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def load_frontier_csv(csv_path: str | Path) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Load Frontier power CSV.

    Args:
        csv_path: path to input_04-07-24.csv

    Returns:
        P: (n_steps, 25) per-CDU-group power in watts
        towb: (n_steps,) wet-bulb temperature in Celsius
        dt: timestep in seconds
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    logger.info(f"Loading Frontier CSV: {csv_path}")

    with open(csv_path, newline="") as f:
        rows = list(csv.reader(f))

    hdr = rows[0]
    p_idx = [i for i, h in enumerate(hdr) if h.startswith("power")]
    t_idx = hdr.index("time")
    towb_idx = hdr.index("OA Wetbulb Temp")

    P = np.array([[float(r[i]) for i in p_idx] for r in rows[1:]], dtype=np.float32)
    t = np.array([float(r[t_idx]) for r in rows[1:]])
    towb = np.array([float(r[towb_idx]) for r in rows[1:]], dtype=np.float32)

    dt = float(np.unique(np.diff(t))[0])
    logger.info(f"Loaded: {P.shape[0]} steps, {P.shape[1]} CDU groups, dt={dt}s, towb range {towb.min():.1f}–{towb.max():.1f}°C")

    return P, towb, dt


def disaggregate_to_fmu(
    P: np.ndarray,
    towb_C: np.ndarray,
    selected_columns: list = None,
    branch_split: str = "equal",
    towb_offset_K: float = 15.0,
) -> Tuple[np.ndarray, dict]:
    """
    Disaggregate per-CDU power to per-blade-group + wet-bulb (FMU inputs).

    Args:
        P: (n_steps, 25) per-CDU power in watts
        towb_C: (n_steps,) wet-bulb in Celsius
        selected_columns: which 5 CDU columns to use (default: [0,1,2,3,4])
        branch_split: "equal" | "decorrelated" (default: "equal")
        towb_offset_K: CT offset (default: 15 K)

    Returns:
        exog: (n_steps, 16) blade-group power + towb in kelvin
        meta: disaggregation metadata
    """
    if selected_columns is None:
        selected_columns = [0, 1, 2, 3, 4]

    n_branches = 3
    cabinet_parallel = 3  # 3 real cabinets per CDU group

    logger.info(f"Disaggregating to FMU inputs: {len(selected_columns)} columns, branch_split={branch_split}")

    # Select columns and divide by cabinet factor
    power_selected = P[:, selected_columns] / cabinet_parallel  # (T, 5) per-cabinet power

    # Distribute across blade groups
    if branch_split == "equal":
        blade_power = np.repeat(power_selected, n_branches, axis=1)  # (T, 15)
    else:
        raise NotImplementedError(f"branch_split={branch_split}")

    # Convert wet-bulb to Kelvin
    towb_K = towb_C + 273.15 + towb_offset_K

    # Concatenate
    exog = np.concatenate([blade_power, towb_K.reshape(-1, 1)], axis=1)
    exog = exog.astype(np.float32)

    meta = {
        "divisor": cabinet_parallel,
        "thermal_regime": "180 kW/cabinet (60 kW per blade group)",
        "columns": selected_columns,
        "branch_split": branch_split,
        "towb_offset_K": float(towb_offset_K),
        "n_steps": exog.shape[0],
    }

    logger.info(f"Disaggregated: {exog.shape} exogenous trace")
    return exog, meta


def generate_regime_a_synthetic(
    n_days: int = 2,
    n_racks: int = 25,
    seed: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate regime-A synthetic workload + constant wet-bulb.

    Args:
        n_days: number of synthetic days to generate
        n_racks: 25 CDU groups
        seed: RNG seed

    Returns:
        P_syn: (T, 25) synthetic per-CDU power
        towb_syn: (T,) constant wet-bulb (Fahrenheit, typical ~60°F)
    """
    try:
        from optimal_dc.workload_gen import generate, load_spec
    except ImportError:
        logger.error("workload_gen not importable; ensure PYTHONPATH includes optimal_dc")
        raise

    logger.info(f"Generating {n_days} synthetic regime-A days (seed={seed})")

    spec_path = Path(__file__).parents[1] / "workload_gen/spec/regime_A.json"
    spec = load_spec(spec_path)

    # Load calibrated config
    config_path = Path(__file__).parents[1] / "workload_gen/spec/regime_A_calib.json"
    if not config_path.exists():
        logger.warning(f"regime_A_calib.json not found at {config_path}; using regime_A_starting")
        # Fallback: use starting config (less tuned, but works for prototyping)
        # For now, we'll just generate with default regime_A
        # In production, regime_A_calib.json should exist after calibration runs

        from optimal_dc.workload_gen.config import WorkloadConfig
        config = WorkloadConfig.from_spec(spec_path)
    else:
        from optimal_dc.workload_gen.config import WorkloadConfig
        config = WorkloadConfig.from_json(config_path)

    # Generate N independent days
    n_steps_per_day = 5761  # 24h at 15s resolution
    P_list = []
    for day_idx in range(n_days):
        day_seed = seed + day_idx * 1000  # independent seed per day
        P_day = generate(config, n_racks=n_racks, n_steps=n_steps_per_day, seed=day_seed)
        P_list.append(P_day)

    P_syn = np.concatenate(P_list, axis=0)  # (T*n_days, 25)

    # Constant wet-bulb (typical Frontier facility, ~60°F = 15.6°C)
    # Use the mean from the real day for consistency
    towb_syn = np.full(P_syn.shape[0], 15.6, dtype=np.float32)

    logger.info(f"Generated {P_syn.shape[0]} synthetic steps ({n_days} days)")
    return P_syn, towb_syn


def load_data_variant_a(
    csv_path: str | Path = None,
    n_synthetic_days: int = 2,
    train_frac: float = 0.67,
    stacking: str = "regime_a_synthetic",
    seed: int = 0,
) -> dict:
    """
    Load variant A data: real Frontier CSV + regime-A synthetic.

    Args:
        csv_path: path to Frontier CSV (default: standard location)
        n_synthetic_days: how many regime-A days to append
        train_frac: fraction of data for training (rest for eval)
        stacking: "none" | "regime_a_synthetic" (how to combine real + synthetic)
        seed: random seed for synthetic generation

    Returns:
        {
            'train': {
                'power': (T_train, 16) exogenous trace,
                'steps': T_train
            },
            'eval': {
                'power': (T_eval, 16) exogenous trace,
                'steps': T_eval
            },
            'meta': metadata dict
        }
    """
    if csv_path is None:
        csv_path = Path(__file__).parents[2] / "external/sustain-lc/input_04-07-24.csv"

    logger.info(f"Loading variant A data (stacking={stacking})")

    # Load real Frontier data
    P_real, towb_real, dt = load_frontier_csv(csv_path)

    # Disaggregate real data
    exog_real, meta_real = disaggregate_to_fmu(P_real, towb_real)

    if stacking == "none":
        # Use only real data
        exog = exog_real
        n_real_days = 1
        n_synthetic_days_used = 0

    elif stacking == "regime_a_synthetic":
        # Append synthetic regime-A days
        P_syn, towb_syn = generate_regime_a_synthetic(n_days=n_synthetic_days, seed=seed)
        exog_syn, _ = disaggregate_to_fmu(P_syn, towb_syn)
        exog = np.concatenate([exog_real, exog_syn], axis=0)
        n_real_days = 1
        n_synthetic_days_used = n_synthetic_days

    else:
        raise ValueError(f"Unknown stacking: {stacking}")

    # Split into train/eval
    n_total = exog.shape[0]
    n_train = int(n_total * train_frac)

    exog_train = exog[:n_train]
    exog_eval = exog[n_train:]

    logger.info(f"Split: {exog_train.shape[0]} train, {exog_eval.shape[0]} eval steps")

    data = {
        "train": {
            "power": exog_train,
            "steps": exog_train.shape[0],
        },
        "eval": {
            "power": exog_eval,
            "steps": exog_eval.shape[0],
        },
        "meta": {
            "variant": "a_frontier_regime_a",
            "stacking": stacking,
            "n_real_days": n_real_days,
            "n_synthetic_days": n_synthetic_days_used,
            "total_days": n_real_days + n_synthetic_days_used,
            "train_frac": train_frac,
            "dt_s": dt,
            **meta_real,
        },
    }

    return data
