"""
FrontierEnv_v3: Subclass of sustain-lc's SmallFrontierModel with pluggable disaggregators.

Extends frontier_env.py with:
  - CSV data source path switching (no hardcoded paths)
  - Pluggable disaggregator version selection (v1, v2, v3)
  - Clean separation via exogenous_generators module

No code duplication: only overrides __init__ to swap disaggregator.
"""

from optimal_dc.external.sustain_lc.frontier_env import SmallFrontierModel
from optimal_dc.inherited_FMU_with_modifications.exogenous_generators import create_exogenous_generator


class SmallFrontierModel_v3(SmallFrontierModel):
    """
    Subclass of SmallFrontierModel with pluggable data source and disaggregator.

    Inherits all FMU interaction, reward shaping, observation/action spaces from parent.
    Only overrides exogenous variable generation to support pluggability.

    Args:
        fmu_path (str): Path to FMU binary
        csv_path (str): Path to CSV data (real Frontier or synthetic regime-A)
        disaggregator_version (str): "v1" (sustain-lc original), "v2" (sustain-lc v2),
                                     or "v3" (NVAITC ÷3)
        **kwargs: Additional arguments passed to parent SmallFrontierModel

    Example:
        >>> env = SmallFrontierModel_v3(
        ...     fmu_path="path/to/fmu",
        ...     csv_path="real_frontier_data.csv",
        ...     disaggregator_version="v3"
        ... )
        >>> obs = env.reset()
        >>> obs, reward, done, info = env.step(action)
    """

    def __init__(self,
                 fmu_path,
                 csv_path,
                 disaggregator_version="v3",
                 Towb_offset_in_K=15.0,
                 subsample_rate=1,
                 **kwargs):
        """
        Initialize with pluggable disaggregator and CSV data source.

        Args:
            fmu_path: Path to FMU binary (LC_Frontier_5Cabinet_4_17_25.fmu)
            csv_path: Path to CSV file (real or synthetic workload data)
            disaggregator_version: Which disaggregator to use ("v1", "v2", "v3")
            Towb_offset_in_K: Wet-bulb temperature offset in Kelvin (default 15)
            subsample_rate: Subsample the exogenous data (default 1 = no subsampling)
            **kwargs: Additional arguments for parent class (start_time, stop_time, etc.)
        """

        # Call parent init (sets up FMU, observation/action spaces, etc.)
        # We need to be careful here: parent __init__ expects exogenous variable setup
        # We'll set a placeholder and override it after init
        super().__init__(fmu_path, **kwargs)

        # Override the exogenous generator with our pluggable version
        print(f"\n[SmallFrontierModel_v3] Configuring data pipeline")
        print(f"  CSV path: {csv_path}")
        print(f"  Disaggregator: v{disaggregator_version[-1]}")
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
def create_env_v1(fmu_path, csv_path, **kwargs):
    """Create FrontierEnv with sustain-lc v1 disaggregator (÷15)."""
    return SmallFrontierModel_v3(
        fmu_path=fmu_path,
        csv_path=csv_path,
        disaggregator_version="v1",
        **kwargs
    )


def create_env_v2(fmu_path, csv_path, **kwargs):
    """Create FrontierEnv with sustain-lc v2 disaggregator (÷15 with softmax+smooth)."""
    return SmallFrontierModel_v3(
        fmu_path=fmu_path,
        csv_path=csv_path,
        disaggregator_version="v2",
        **kwargs
    )


def create_env_v3(fmu_path, csv_path, **kwargs):
    """Create FrontierEnv with NVAITC v3 disaggregator (÷3)."""
    return SmallFrontierModel_v3(
        fmu_path=fmu_path,
        csv_path=csv_path,
        disaggregator_version="v3",
        **kwargs
    )
