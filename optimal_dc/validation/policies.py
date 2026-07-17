"""Prize-sizing strategies.

A policy is a callable (obs, t_s, step_idx) -> action dict in SmallFrontierModel format:
    {'cdu-cabinet-1..5': np.ndarray shape (5,) in [-1, 1], 'cooling-tower-1': int 0..8}

CDU per-cabinet action layout (all in [-1, 1], mapped linearly to raw ranges by the env):
    [Tsec_supply, dp, valve1, valve2, valve3]
      a=-1 -> range min,  a=0 -> midpoint,  a=+1 -> range max
      Tsec_supply: 20..40 °C   (a=0 -> 30 °C)
      dp:          25..38 psi  (a=0 -> 31.5 psi)
      valves:      softmaxed across the 3 -> a=0 for all -> balanced (1/3 each)

CT discrete action -> delta added to the built-in rule setpoint (wetbulb + 10 °F):
    index 4 -> delta 0.0 -> setpoint = wetbulb + 10 °F   (== the baseline rule)
    0..3 colder, 5..8 warmer (steps of 0.05 in the env's decoding table)
"""
import numpy as np

CABINET_KEYS = [f"cdu-cabinet-{k}" for k in range(1, 6)]
CT_NEUTRAL = 4          # cooling_tower_action_decoding[4] == 0.0 -> wetbulb+10°F rule
N_CT_ACTIONS = 9        # Discrete(9)


def _action_dict(cdu_vec, ct_action):
    cdu_vec = np.asarray(cdu_vec, dtype=float)
    assert cdu_vec.shape == (5,), "cdu_vec must be shape (5,)"
    return {**{k: cdu_vec.copy() for k in CABINET_KEYS}, "cooling-tower-1": int(ct_action)}


def make_cdu_vec(tsec_a=0.0, dp_a=0.0, valve_a=0.0):
    """Build one cabinet's CDU action from interpretable [-1,1] knobs (valves balanced)."""
    return np.array([tsec_a, dp_a, valve_a, valve_a, valve_a], dtype=float)


def make_constant_policy(cdu_vec, ct_action=CT_NEUTRAL):
    """Policy returning the same action every step (used for the static-setpoint sweep)."""
    cdu_vec = np.asarray(cdu_vec, dtype=float)

    def policy(obs, t_s, step_idx):
        return _action_dict(cdu_vec, ct_action)

    return policy


# --------------------------------------------------------------------------------
# BASELINE (static-nominal) — the FMU's built-in nominal operation: CDU PID tracks the
# FMU's nominal start setpoints, CT on the wetbulb+10°F rule (delta 0). The "no RL" bar.
# Values SOURCED from modelDescription.xml `start` attributes (causality=input):
#   Tsec_supply_nom_RL = 28.0 C  (range 20-40 -> a = 2*(28-20)/20   - 1 = -0.20)
#   dp_nom_RL          = 27.5 psi (range 25-38 -> a = 2*(27.5-25)/13 - 1 = -0.615)
#   Valve_Stpts        = 0.33/0.33/0.34 balanced -> a = 0.0 (env softmaxes to ~1/3 each)
#
# CAVEAT: this STATIC-NOMINAL baseline is WEAKER than the LC-Opt paper's ASHRAE G36
# "trim and respond" baseline (Appendix K of arXiv:2511.00116; not in released code), so
# ΔE measured against it OVERSTATES the prize vs a good rule-based controller. For the
# honest/comparable number, also implement G36 and report ΔE against both. See memory.
# --------------------------------------------------------------------------------
BASELINE_CDU = make_cdu_vec(tsec_a=-0.20, dp_a=-0.615, valve_a=0.0)
baseline_policy = make_constant_policy(BASELINE_CDU, ct_action=CT_NEUTRAL)


# --------------------------------------------------------------------------------
# ORACLE (time-varying upper bound) — SCAFFOLD.
# Piecewise-constant schedule over `n_segments` time segments. Because FMU state
# carries across segments, the schedule must be optimized as a whole via repeated full
# rollouts (you cannot optimize segments independently). This is the heavy piece: build
# it only after the static-sweep floor looks promising, and parallelize the inner
# rollouts (Pool.map over candidate evaluations) before scaling up.
# --------------------------------------------------------------------------------
def make_schedule_policy(params, n_segments, n_steps):
    """Map a flat parameter vector to a piecewise-constant time-varying policy.

    params layout (length 3*n_segments): per segment [tsec_a, dp_a, ct_continuous]
        tsec_a, dp_a in [-1, 1];  ct_continuous in [-1, 1] -> mapped to int 0..8.
    Valves held balanced (a=0) for tractability; extend if branch balancing matters.
    """
    params = np.asarray(params, dtype=float).reshape(n_segments, 3)
    seg_len = int(np.ceil(n_steps / n_segments))

    def policy(obs, t_s, step_idx):
        seg = min(step_idx // seg_len, n_segments - 1)
        tsec_a, dp_a, ct_c = params[seg]
        ct_idx = int(np.clip(round((ct_c + 1) / 2 * (N_CT_ACTIONS - 1)), 0, N_CT_ACTIONS - 1))
        return _action_dict(make_cdu_vec(tsec_a, dp_a, valve_a=0.0), ct_idx)

    return policy


def optimize_oracle(run_policy, summarize, *, n_segments=6, T_max_K, step_size=15.0,
                    stop_time=None, exogen_gen_v=2, infeasible_penalty=1e12,
                    maxiter=10, popsize=15, seed=0, init_seeds=None,
                    checkpoint_path="oracle_checkpoint.npz", verbose=True):
    """Search a piecewise-constant schedule that minimizes E_cooling subject to the
    temperature constraint. Uses scipy.differential_evolution; each candidate costs a
    FULL rollout, so budget = popsize * 3*n_segments * (maxiter+1) rollouts. Returns
    (best_params, best_df, result).

    popsize : DE population multiplier (scipy default 15 -> 270 rollouts/generation at
        n_segments=6; use ~5 for an overnight run).
    init_seeds : optional list of [tsec_a, dp_a, ct_continuous] triples; each is tiled
        across all segments and injected into the initial population (rest random).
        Seeding with the baseline + best feasible static guarantees ceiling >= floor
        from generation zero.
    checkpoint_path : best-so-far FEASIBLE candidate is saved here after every
        generation (np.savez), so an interrupted run still yields a valid lower-bound
        ceiling. Set None to disable.
    """
    from scipy.optimize import differential_evolution
    from rollout import full_pass_stop_time

    if stop_time is None:
        stop_time = full_pass_stop_time(exogen_gen_v, step_size)
    n_steps = int(stop_time // step_size)
    n_params = 3 * n_segments
    bounds = [(-1.0, 1.0)] * n_params

    best = {"E_cooling_J": np.inf, "params": None, "n_evals": 0}

    def _save_checkpoint():
        if checkpoint_path and best["params"] is not None:
            np.savez(checkpoint_path, params=best["params"],
                     E_cooling_J=best["E_cooling_J"], n_evals=best["n_evals"],
                     n_segments=n_segments, exogen_gen_v=exogen_gen_v,
                     stop_time=stop_time)

    def objective(params):
        pol = make_schedule_policy(params, n_segments, n_steps)
        df = run_policy(pol, stop_time=stop_time, step_size=step_size,
                        exogen_gen_v=exogen_gen_v, name="oracle_candidate")
        s = summarize(df, T_max_K, step_size)
        best["n_evals"] += 1
        if not s["feasible"]:
            # soft penalty proportional to overshoot so the optimizer is guided back
            overshoot = float((df["T_cab_max_K"] - T_max_K).clip(lower=0).sum()) if len(df) else 0.0
            # crashed runs (FMU flow-reversal assertion) carry E_cooling=NaN; score them
            # on the penalty alone so NaN cannot poison differential_evolution
            E = s["E_cooling_J"] if np.isfinite(s["E_cooling_J"]) else 0.0
            return E + infeasible_penalty * (1 + overshoot)
        if s["E_cooling_J"] < best["E_cooling_J"]:
            best["E_cooling_J"] = s["E_cooling_J"]
            best["params"] = np.asarray(params, dtype=float).copy()
            _save_checkpoint()   # save on every improvement: covers the initial-population
                                 # evaluation and mid-generation crashes, not just gen ends
        return s["E_cooling_J"]

    def _checkpoint(xk, convergence=None):
        _save_checkpoint()
        return False   # never request early termination

    init = "latinhypercube"
    if init_seeds:
        rng = np.random.default_rng(seed)
        n_pop = max(popsize * n_params, len(init_seeds), 5)
        init = rng.uniform(-1.0, 1.0, size=(n_pop, n_params))
        for i, triple in enumerate(init_seeds[:n_pop]):
            init[i] = np.tile(np.asarray(triple, dtype=float), n_segments)

    result = differential_evolution(objective, bounds, maxiter=maxiter, seed=seed,
                                    popsize=popsize, init=init, polish=False,
                                    disp=verbose, callback=_checkpoint)
    # prefer the best FEASIBLE candidate seen (result.x can be an infeasible/penalized
    # point if the final population converged badly)
    final_params = best["params"] if best["params"] is not None else result.x
    best_pol = make_schedule_policy(final_params, n_segments, n_steps)
    best_df = run_policy(best_pol, stop_time=stop_time, step_size=step_size,
                         exogen_gen_v=exogen_gen_v, name="oracle")
    return final_params, best_df, result
