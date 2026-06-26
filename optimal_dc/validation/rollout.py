"""FMU rollout engine for prize-sizing.

Design contract (see prize_sizing memory):
  * A *policy* is a callable (obs, t_s, step_idx) -> action dict in the
    SmallFrontierModel action format.
  * Each policy gets its OWN independent rollout (its own FMU instance via a fresh
    SmallFrontierModel + reset()), so every run starts from the same initial state
    and replays the same exogenous trace. This is required for a clean ΔE and makes
    the runs trivially parallelizable later (Pool.map over run_policy).
  * The energy objective P_cooling is defined ONCE here and shared by baseline /
    static / oracle (and, later, the RL reward refactor). Single source of truth.

NOTE on what this measures: the "real trace" the FMU sees is already transformed by
frontier_env's exogenous_variable_generator (clipping / rolling / disaggregation).
Prize-sizing therefore measures the prize on that *processed* load. Record which
exogen_gen_v you used (1 vs 2) in the writeup.
"""
import os
import sys
import pathlib
import contextlib

import numpy as np
import pandas as pd

# --- make the forked sustain-lc submodule importable (repo-relative, move-safe) ---
_SUSTAIN = pathlib.Path(__file__).resolve().parent.parent / "external" / "sustain-lc"
sys.path.insert(0, str(_SUSTAIN))
from frontier_env import SmallFrontierModel  # noqa: E402

# ---------------------------------------------------------------------------------
# OBJECTIVE: total controllable facility cooling power, in watts. SINGLE SOURCE OF TRUTH.
# Terms verified vs modelDescription.xml 2026-06-12; documented §6.5 of
# docs/sustain-lc_FMU_analysis.md. η=0.85 is baked into the pump terms (§5), so these
# are INPUT/shaft power (efficiency included), NOT raw thermodynamic flow work.
#
# !! ASSUMPTION TO VERIFY !!  These name strings are taken from the analysis doc. If
# fmu.get(POWER_VARS) raises, run  list_power_vars(env)  and correct the names below.
# ---------------------------------------------------------------------------------
POWER_VARS = (
    [f"simulator[1].datacenter[1].computeBlock[{k}].cdu[1].summary.W_flow_CDUP" for k in range(1, 6)]
    + [
        "simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.W_flow_HTWP",
        "simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.W_flow_CTWP",
        "simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.W_flow_CT",  # 2-cell tower, already aggregated
    ]
)
POWER_LABELS = [f"CDUP_{k}" for k in range(1, 6)] + ["HTWP", "CTWP", "CT"]

CABINET_KEYS = [f"cdu-cabinet-{k}" for k in range(1, 6)]


@contextlib.contextmanager
def _chdir(path):
    """frontier_env reads EXOGENOUS_VAR_PATH ('input_04-07-24.csv') RELATIVE to CWD,
    and only at construction time. Build the env from inside the sustain-lc dir so the
    CSV is found, then restore CWD."""
    old = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(old)


# input_04-07-24.csv is 5760 steps = 24 h @ 15 s. v2 folds the 25 CDU columns into the
# 5-cabinet structure as 5 sequential time-blocks -> one full v2 pass is 5x longer (120 h).
_BASE_PASS_STEPS = 5760


def full_pass_stop_time(exogen_gen_v=2, step_size=15.0):
    """Seconds for ONE full pass of the chosen exogenous pipeline (v1 -> 24 h, v2 -> 120 h)."""
    folds = 5 if exogen_gen_v == 2 else 1
    return _BASE_PASS_STEPS * folds * step_size


def make_env(stop_time=None, step_size=15.0, exogen_gen_v=2, subsample_rate=1):
    # PROJECT STANDARD is v2: every sustain-lc train/eval script overrides the constructor
    # default (=1) to exogen_gen_v=2, so prize-sizing must use v2 for ΔE to be comparable
    # to their baselines/agents.
    # CAVEAT: v2 flattens load (softmax branch redistribution + 50-step mean filter) ->
    # conservatively UNDERSTATES the load-following prize. The smoothing kernel (=50) is
    # hardcoded in SmallFrontierModel's v2 call and not exposed via __init__; to probe the
    # flattening effect, instantiate exogenous_variable_generator_2 directly with a smaller
    # smoothing_kernel_size. See prize_sizing memory.
    if stop_time is None:
        stop_time = full_pass_stop_time(exogen_gen_v, step_size)
    with _chdir(_SUSTAIN):
        env = SmallFrontierModel(
            stop_time=stop_time,
            step_size=step_size,
            exogen_gen_v=exogen_gen_v,
            subsample_rate=subsample_rate,
        )
    return env


def exogenous_trace(exogen_gen_v=2):
    """Return the processed exogenous array that would be fed to the FMU, WITHOUT running
    it — for inspecting/plotting the v1 vs v2 preprocessing. Shape (T, 16): 15 branch
    powers (5 cabinets x 3 branches; cabinet c = cols 3c:3c+3) + 1 wet-bulb column.
    T = 5761 for v1, ~28805 for v2 (folded 5x)."""
    from frontier_env import (exogenous_variable_generator,
                              exogenous_variable_generator_2, EXOGENOUS_VAR_PATH)
    with _chdir(_SUSTAIN):
        if exogen_gen_v == 1:
            gen = exogenous_variable_generator(EXOGENOUS_VAR_PATH)
        elif exogen_gen_v == 2:
            gen = exogenous_variable_generator_2(EXOGENOUS_VAR_PATH)
        else:
            raise ValueError("exogen_gen_v must be 1 or 2")
    return np.asarray(gen.exogenous_var_final)


def list_power_vars(env):
    """Helper to verify POWER_VARS against the loaded FMU: returns every model
    variable whose name contains 'W_flow'."""
    return sorted(n for n in env.fmu.get_model_variables().keys() if "W_flow" in n)


def compute_P_cooling(fmu):
    """Sum of all controllable cooling-power terms (watts)."""
    return float(np.sum([float(np.ravel(v)[0]) for v in fmu.get(POWER_VARS)]))


def _cabinet_temps_K(info):
    """(5, 3) array of cabinet boundary-port temps (Kelvin) from env.step info.
    info['cdu-cabinet-k'] = [boundary_1.T, boundary_2.T, boundary_3.T, blade1, blade2, blade3]."""
    return np.array([info[k][0:3] for k in CABINET_KEYS], dtype=float)


def run_policy(policy, *, stop_time=None, step_size=15.0, exogen_gen_v=2,
               subsample_rate=1, name="policy"):
    """Run ONE independent rollout of `policy` over the real exogenous trace.

    policy : callable(obs, t_s, step_idx) -> dict
        {'cdu-cabinet-1..5': np.ndarray shape (5,) in [-1, 1],
         'cooling-tower-1': int in 0..8}
        CDU layout per cabinet: [Tsec_supply, dp, valve1, valve2, valve3].

    Returns a tidy per-step DataFrame: P_cooling_W, per-term W_<label>_W,
    T_cab_max_K, T_cab_mean_K. The env's own reward is ignored on purpose.
    """
    if stop_time is None:
        stop_time = full_pass_stop_time(exogen_gen_v, step_size)
    env = make_env(stop_time=stop_time, step_size=step_size,
                   exogen_gen_v=exogen_gen_v, subsample_rate=subsample_rate)
    obs = env.reset()
    n_steps = int(stop_time // step_size)

    rows = []
    for i in range(n_steps):
        t = i * step_size
        action = policy(obs, t, i)
        obs, _reward, _done, info = env.step(action)   # reward deliberately discarded
        p_terms = [float(np.ravel(v)[0]) for v in env.fmu.get(POWER_VARS)]
        temps = _cabinet_temps_K(info)

        row = {"policy": name, "step": i, "t_s": t, "P_cooling_W": float(np.sum(p_terms))}
        row.update({f"W_{lab}_W": p for lab, p in zip(POWER_LABELS, p_terms)})
        row["T_cab_max_K"] = float(temps.max())
        row["T_cab_mean_K"] = float(temps.mean())
        rows.append(row)

    return pd.DataFrame(rows)


def integrate_energy_J(df, step_size=15.0):
    """Energy (J) under ZOH power: E = Σ P · Δt."""
    return float(df["P_cooling_W"].sum() * step_size)


def feasible(df, T_max_K):
    """True iff cabinet temps stay within the performance/safety limit for the whole run."""
    return bool((df["T_cab_max_K"] <= T_max_K).all())


def summarize(df, T_max_K, step_size=15.0):
    """One-row summary of a rollout: energy, feasibility, peak temp."""
    return {
        "policy": df["policy"].iloc[0],
        "E_cooling_J": integrate_energy_J(df, step_size),
        "E_cooling_kWh": integrate_energy_J(df, step_size) / 3.6e6,
        "feasible": feasible(df, T_max_K),
        "T_cab_max_K": float(df["T_cab_max_K"].max()),
        "T_cab_margin_K": float(T_max_K - df["T_cab_max_K"].max()),
    }
