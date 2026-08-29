"""
FrontierEnv_v3: Subclass of sustain-lc's SmallFrontierModel with pluggable disaggregators.

Extends frontier_env.py with:
  - CSV data source path switching (no hardcoded paths)
  - Pluggable disaggregator version selection (v1, v2, v3)
  - Clean separation via exogenous_generators module

No code duplication: only overrides __init__ (disaggregator swap) and reset()
(optional per-reset synthetic-day resampling).

OBSERVATION NORMALIZATION UNDER /9 -- VERIFIED, NO CHANGES NEEDED (2026-08-28):
an instrumented full 24 h baseline pass on the /9 real day showed 0 of 34
observation variables breach their `variable_ranges` post-warmup (temps peak
56.75 C inside the [0, 100] C bands; blade power maxes 121 kW vs the 340 kW
cap). Only the action-independent warm-up transient (~139 C, first 30 min)
exceeds the temperature ranges -- pre-existing at /15, excluded by the
standard WARMUP_STEPS=120 window. Re-verify if the exogenous magnitude
convention or an aggressive trained policy changes the operating envelope.
"""

import sys
from pathlib import Path

# The sustain-lc submodule directory name contains a hyphen, so it cannot be a
# package path; put it (and the repo root, for optimal_dc.* namespace imports)
# on sys.path directly.
_OPTIMAL_DC = Path(__file__).resolve().parents[1]
_REPO_ROOT = _OPTIMAL_DC.parent
_SUSTAIN_LC = _OPTIMAL_DC / "external" / "sustain-lc"
for _p in (str(_REPO_ROOT), str(_SUSTAIN_LC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import functools

import numpy as np

import frontier_env as _frontier_env_module
from frontier_env import SmallFrontierModel
import mh_frontier_env as _mh_frontier_env_module
from mh_frontier_env import MH_SmallFrontierModel

from optimal_dc.inherited_FMU_with_modifications.exogenous_generators import create_exogenous_generator


def _cyclic_rows(trace: np.ndarray, offset: int = 0):
    """Infinite row iterator over a (T, 16) trace, starting at `offset`, wrapping."""
    i = offset % len(trace)
    while True:
        yield trace[i]
        i = (i + 1) % len(trace)


class SmallFrontierModel_v3(SmallFrontierModel):
    """
    Subclass of SmallFrontierModel with pluggable data source and disaggregator.

    Inherits all FMU interaction, reward shaping, observation/action spaces from parent.
    Only overrides exogenous variable generation to support pluggability.

    Note: the FMU path is NOT a parameter — the parent loads the module-level
    FMU_PATH constant (the FMU sitting next to frontier_env.py in the
    sustain-lc submodule). Making it pluggable would mean reimplementing the
    parent's __init__; do that in the fork if ever needed.

    Args:
        csv_path (str): Path to CSV data (real Frontier or synthetic regime-A)
        disaggregator_version (str): "v1" (sustain-lc original), "v2" (sustain-lc v2),
                                     or "v3" (NVAITC ÷9)
        **kwargs: Additional arguments passed to parent SmallFrontierModel
                  (start_time, stop_time, step_size, use_reward_shaping, ...)

    Example:
        >>> env = SmallFrontierModel_v3(
        ...     csv_path="real_frontier_data.csv",
        ...     disaggregator_version="v3"
        ... )
        >>> obs = env.reset()
        >>> obs, reward, done, info = env.step(action)
    """

    def __init__(self,
                 csv_path,
                 disaggregator_version="v3",
                 Towb_offset_in_K=15.0,
                 subsample_rate=1,
                 day_sampler=None,
                 sampler_seed=0,
                 min_horizon=200,
                 **kwargs):
        """
        Initialize with pluggable disaggregator and CSV data source.

        Args:
            csv_path: Path to CSV file (real or synthetic workload data)
            disaggregator_version: Which disaggregator to use ("v1", "v2", "v3")
            Towb_offset_in_K: Wet-bulb temperature offset in Kelvin (default 15)
            subsample_rate: Subsample the exogenous data (default 1 = no subsampling)
            day_sampler: optional callable -> (T, 16) FMU-ready exogenous trace
                (e.g. ML_algos.data_loader.RegimeADaySampler). When given, EVERY
                reset() draws a FRESH day and a uniform-random start offset, so
                training samples the workload DISTRIBUTION instead of cycling
                one trace -- the train-on-synthetic requirement. csv_path then
                only feeds the parent's discarded constructor-time generator.
            sampler_seed: seed for the per-reset start-offset draws
            min_horizon: offsets are drawn from [0, T - min_horizon) so an
                episode of up to this many steps never wraps the day boundary
                (default 200 = the sustain-lc max_ep_len)
            **kwargs: Additional arguments for parent class (start_time, stop_time, etc.)
        """
        csv_path = str(Path(csv_path).resolve())
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV data source not found: {csv_path}")

        # The parent has no data-path parameter: its __init__ always builds a
        # v1/v2 generator from the module-level, cwd-relative EXOGENOUS_VAR_PATH
        # (and would crash from any other working directory). Point it at our
        # CSV for the duration of the call, then restore. The generator the
        # parent builds is discarded when we override iter_exogenous_var below.
        _orig_path = _frontier_env_module.EXOGENOUS_VAR_PATH
        _frontier_env_module.EXOGENOUS_VAR_PATH = csv_path
        try:
            super().__init__(**kwargs)
        finally:
            _frontier_env_module.EXOGENOUS_VAR_PATH = _orig_path

        # Override the exogenous generator with our pluggable version
        print(f"\n[SmallFrontierModel_v3] Configuring data pipeline")
        print(f"  CSV path: {csv_path}")
        print(f"  Disaggregator: {disaggregator_version}")
        print(f"  Towb offset: {Towb_offset_in_K}K")

        self.iter_exogenous_var = create_exogenous_generator(
            csv_path=csv_path,
            version=disaggregator_version,
            Towb_offset_in_K=Towb_offset_in_K,
            subsample_rate=subsample_rate
        )

        # Store configuration for reference
        self.csv_path = csv_path
        self.disaggregator_version = disaggregator_version
        self.Towb_offset_in_K = Towb_offset_in_K

        # per-reset synthetic-day resampling (see __init__ docstring)
        self.day_sampler = day_sampler
        self._min_horizon = int(min_horizon)
        self._offset_rng = np.random.default_rng(sampler_seed)
        if day_sampler is not None:
            print(f"  Day sampler: {type(day_sampler).__name__} "
                  f"(fresh day + random offset per reset)")

    def reset(self):
        """Parent reset (FMU re-init), plus: with a day_sampler, swap in a
        freshly drawn day at a uniform-random start offset FIRST, so the
        episode's exogenous stream comes from the new day. This also fixes the
        upstream quirk that reset() never re-initialized the exogenous
        iterator (episodes silently continued mid-trace)."""
        if self.day_sampler is not None:
            trace = np.asarray(self.day_sampler())
            if trace.ndim != 2 or trace.shape[1] != 16:
                raise ValueError(f"day_sampler must return (T, 16), got {trace.shape}")
            hi = max(1, len(trace) - self._min_horizon)
            offset = int(self._offset_rng.integers(0, hi))
            self.iter_exogenous_var = _cyclic_rows(trace, offset)
        return super().reset()

    # Other methods are inherited from parent. The exogenous variable is
    # fetched from iter_exogenous_var in step(), which we didn't override.


class MH_SmallFrontierModel_v3(MH_SmallFrontierModel):
    """
    Multi-head env wrapper (split top-level/valve-level CDU action space, the
    MH MA CA-PPO baseline's env) with pluggable data source + disaggregator.

    The upstream MH_SmallFrontierModel builds its inner env by calling the
    module-level SmallFrontierModel symbol, so we temporarily rebind that
    symbol to a SmallFrontierModel_v3 partial while the parent constructor
    runs — same pattern as the EXOGENOUS_VAR_PATH patch. Upstream defaults
    (subsample_rate=40, do_valve_softmax=False) are preserved by the parent.
    """

    def __init__(self,
                 csv_path,
                 disaggregator_version="v3",
                 Towb_offset_in_K=15.0,
                 day_sampler=None,
                 sampler_seed=0,
                 min_horizon=200,
                 **kwargs):
        _orig = _mh_frontier_env_module.SmallFrontierModel
        _mh_frontier_env_module.SmallFrontierModel = functools.partial(
            SmallFrontierModel_v3,
            csv_path=csv_path,
            disaggregator_version=disaggregator_version,
            Towb_offset_in_K=Towb_offset_in_K,
            day_sampler=day_sampler,
            sampler_seed=sampler_seed,
            min_horizon=min_horizon,
        )
        try:
            super().__init__(**kwargs)
        finally:
            _mh_frontier_env_module.SmallFrontierModel = _orig

        self.csv_path = self.env.csv_path
        self.disaggregator_version = self.env.disaggregator_version


# Convenience aliases for different disaggregators
def create_env_v1(csv_path, **kwargs):
    """Create FrontierEnv with sustain-lc v1 disaggregator (÷15)."""
    return SmallFrontierModel_v3(
        csv_path=csv_path,
        disaggregator_version="v1",
        **kwargs
    )


def create_env_v2(csv_path, **kwargs):
    """Create FrontierEnv with sustain-lc v2 disaggregator (÷15 with softmax+smooth)."""
    return SmallFrontierModel_v3(
        csv_path=csv_path,
        disaggregator_version="v2",
        **kwargs
    )


def create_env_v3(csv_path, **kwargs):
    """Create FrontierEnv with NVAITC v3 disaggregator (÷9)."""
    return SmallFrontierModel_v3(
        csv_path=csv_path,
        disaggregator_version="v3",
        **kwargs
    )
