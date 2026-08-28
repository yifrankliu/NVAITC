"""
Input/Output Contract: ML Model Interface

This module defines the stable contract between the preprocessing pipeline
(disaggregator) and ML algorithms. All algorithms must respect this interface.

INVARIANTS:
  - Input shape and units are fixed
  - Algorithms are independent of preprocessing choices (real vs synthetic data)
  - Algorithms are independent of stacking mode
  - Only the (T, 16) exogenous trace matters to the algorithm
"""

import numpy as np
from typing import NamedTuple

# ============================================================================
# INPUT CONTRACT: Exogenous Trace from Disaggregator
# ============================================================================

class ExogenousTrace(NamedTuple):
    """
    Preprocessed exogenous trace from disaggregator.py.

    This is the stable interface between data pipeline and ML algorithms.
    All algorithms accept this as input; they do NOT care how it was created
    (real Frontier, real OneAsia, synthetic regime-A, etc.).
    """

    power_and_towb: np.ndarray  # shape (T, 16), dtype float32
    # Columns 0-14: blade-group power (ComputePowerBlade[1..15]) in WATTS
    # Column 15: wet-bulb temperature (Towb) in KELVIN
    # Time resolution: 15 seconds per step (ZOH)
    # Units: SI (watts, kelvin) — no normalization; ML normalizes internally

    metadata: dict
    # Provenance and preprocessing choices (documented for transparency)
    # Keys: "divisor", "thermal_regime", "columns", "slice_mode",
    #       "branch_split", "stacking", "towb_offset_K", ...
    # ML algorithms MUST ignore this; it's for logging/debugging only

    def validate(self) -> bool:
        """Check that the trace respects the contract."""
        T, n_cols = self.power_and_towb.shape
        assert n_cols == 16, f"Expected 16 columns, got {n_cols}"
        assert T >= 100, f"Trace too short: {T} steps (need ≥100 for 25 min)"
        assert np.all(np.isfinite(self.power_and_towb)), "Contains NaN/inf"

        # Sanity checks (not hard constraints, but warnings)
        power = self.power_and_towb[:, :15]
        towb = self.power_and_towb[:, 15]
        assert power.min() >= -1e3, f"Negative power detected (min={power.min()})"
        assert power.max() <= 1e6, f"Unrealistic power (max={power.max()} W)"
        assert 250 < towb.mean() < 330, f"Unrealistic wet-bulb (mean={towb.mean()} K)"
        return True


# ============================================================================
# OUTPUT CONTRACT: Normalized Actions for FrontierEnv
# ============================================================================

class NormalizedAction(NamedTuple):
    """
    Actions output by ML algorithm, normalized to [-1, 1].

    FrontierEnv expects Dict action space:
      'cdu-cabinet-1': Box(-1, 1, (5,))  # 5 actions per cabinet
      'cdu-cabinet-2': Box(-1, 1, (5,))
      ...
      'cdu-cabinet-5': Box(-1, 1, (5,))
      'cooling-tower-1': Discrete(9)     # 9 setpoint options
    """

    cabinet_actions: np.ndarray  # shape (5, 5), dtype float32, values in [-1, 1]
    # cabinet_actions[i, j] is the j-th action for cabinet i
    # Cabinet indices: 0-4 correspond to CDU-cabinets 1-5
    # Action indices per cabinet:
    #   0: Tsec_supply_nom_RL setpoint (temperature)
    #   1: dp_nom_RL setpoint (pressure drop)
    #   2-4: Valve_Stpts[1-3] (flow fractions, will sum to 1.0 via softmax in env)

    cooling_tower_action: int  # discrete choice in [0, 8]
    # Discrete setpoint for cooling tower fan speed
    # 0: -0.20 (slowest)
    # 4: 0.00 (nominal)
    # 8: +0.20 (fastest)
    # See frontier_env.py::cooling_tower_action_decoding

    def to_dict(self) -> dict:
        """Convert to FrontierEnv's Dict action format."""
        return {
            'cdu-cabinet-1': self.cabinet_actions[0, :],
            'cdu-cabinet-2': self.cabinet_actions[1, :],
            'cdu-cabinet-3': self.cabinet_actions[2, :],
            'cdu-cabinet-4': self.cabinet_actions[3, :],
            'cdu-cabinet-5': self.cabinet_actions[4, :],
            'cooling-tower-1': self.cooling_tower_action,
        }

    def validate(self) -> bool:
        """Check that actions respect bounds."""
        assert self.cabinet_actions.shape == (5, 5), \
            f"Cabinet actions shape {self.cabinet_actions.shape}, expected (5, 5)"
        assert np.all(self.cabinet_actions >= -1.0) and np.all(self.cabinet_actions <= 1.0), \
            f"Cabinet actions out of bounds [-1, 1]: min={self.cabinet_actions.min()}, " \
            f"max={self.cabinet_actions.max()}"
        assert 0 <= self.cooling_tower_action < 9, \
            f"Cooling tower action {self.cooling_tower_action}, expected in [0, 8]"
        return True


# ============================================================================
# NORMALIZATION UTILITIES (ML-internal, not part of contract)
# ============================================================================

def normalize_observation_dict(obs_dict: dict) -> dict:
    """
    Convert FrontierEnv's Dict observation to a flat normalized vector.

    FrontierEnv already returns normalized obs in [-1, 1].
    This unpacks the Dict and flattens it for algorithms that prefer flat input.

    obs_dict: {'cdu-cabinet-1': (6,), ..., 'cooling-tower-1': (4,)}
    returns: (34,) normalized flat observation (5 cabinets x 6 + 4 CT dims)
    """
    cabinet_obs = []
    for i in range(1, 6):
        key = f'cdu-cabinet-{i}'
        cabinet_obs.append(obs_dict[key].flatten())
    ct_obs = obs_dict['cooling-tower-1'].flatten()
    return np.concatenate(cabinet_obs + [ct_obs])


def denormalize_observation_dict(flat_obs: np.ndarray) -> dict:
    """Reverse of normalize_observation_dict."""
    obs_dict = {}
    idx = 0
    for i in range(1, 6):
        key = f'cdu-cabinet-{i}'
        obs_dict[key] = flat_obs[idx:idx+6].reshape((6,))
        idx += 6
    obs_dict['cooling-tower-1'] = flat_obs[idx:idx+4].reshape((4,))
    return obs_dict


# ============================================================================
# ALGORITHM INTERFACE
# ============================================================================

class MLAlgorithm:
    """
    Base interface for ML algorithms.

    All RL algorithms (PPO, SAC, etc.) must implement this interface.
    They accept ExogenousTrace as input and produce NormalizedAction as output.
    """

    def __init__(self, config: dict):
        """
        Initialize algorithm with config dict.

        config: hyperparameters, network architecture, learning rates, etc.
               algorithm-specific; see config/default.yaml for structure
        """
        self.config = config

    def learn(self, env, n_steps: int) -> dict:
        """
        Train the algorithm on the environment.

        Returns: training metrics (loss, return, constraint violations, etc.)
        """
        raise NotImplementedError

    def predict(self, obs: dict, deterministic: bool = False) -> NormalizedAction:
        """
        Predict action given observation.

        obs: FrontierEnv observation (normalized Dict)
        deterministic: if True, return greedy action; else sample

        Returns: NormalizedAction (validated)
        """
        raise NotImplementedError

    def save(self, path: str) -> None:
        """Save policy checkpoint."""
        raise NotImplementedError

    def load(self, path: str) -> None:
        """Load policy checkpoint."""
        raise NotImplementedError
