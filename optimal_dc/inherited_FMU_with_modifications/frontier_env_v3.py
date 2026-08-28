"""
FrontierEnv_v3: Subclass of sustain-lc's SmallFrontierModel with pluggable disaggregators.

Extends frontier_env.py with:
  - CSV data source path switching (no hardcoded paths)
  - Pluggable disaggregator version selection (v1, v2, v3)
  - Clean separation via exogenous_generators module

No code duplication: only overrides __init__ to swap disaggregator.
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

import frontier_env as _frontier_env_module
from frontier_env import SmallFrontierModel

from optimal_dc.inherited_FMU_with_modifications.exogenous_generators import create_exogenous_generator


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
                 **kwargs):
        """
        Initialize with pluggable disaggregator and CSV data source.

        Args:
            csv_path: Path to CSV file (real or synthetic workload data)
            disaggregator_version: Which disaggregator to use ("v1", "v2", "v3")
            Towb_offset_in_K: Wet-bulb temperature offset in Kelvin (default 15)
            subsample_rate: Subsample the exogenous data (default 1 = no subsampling)
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

    # No need to override other methods—they're inherited from parent
    # The exogenous variable is fetched via get_exogenous_var() in step(),
    # which we didn't override, so it uses the same interface


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
