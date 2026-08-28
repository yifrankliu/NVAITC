"""
Pluggable exogenous variable generators (disaggregators).

Three versions:
  v1: sustain-lc original (÷15, with clipping)
  v2: sustain-lc v2 (÷15, with softmax + smoothing)
  v3: NVAITC new (÷9, no preprocessing)

All accept CSV (real Frontier or synthetic regime-A) and output (T, 16) array.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
# scipy is imported lazily inside ExogenousGeneratorV2 (softmax) so that
# v1/v3 users don't need it installed.

# Make `optimal_dc.*` namespace imports work even when this module is loaded
# standalone (there is no optimal_dc/__init__.py; repo root must be on sys.path).
_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


class ExogenousGeneratorV1:
    """sustain-lc original: ÷15 divisor with clipping."""

    def __init__(self, csv_path, Towb_offset_in_K=10, nCDUs=5, nBranches=3,
                 parallel_nCabinets=5, subsample_rate=1):
        """
        Load CSV and apply sustain-lc v1 preprocessing.

        Args:
            csv_path: path to CSV (time, power[1..25], Towb)
            Towb_offset_in_K: wet-bulb offset (default 10K)
            parallel_nCabinets: cabinet parallelization factor (default 5, creates ÷15)
        """
        self.exogenous_var = pd.read_csv(csv_path)

        # Clipping: remove values beyond mean ± 1.75σ
        for col in self.exogenous_var.columns[1:1+nCDUs]:
            mean = self.exogenous_var[col].mean()
            std = self.exogenous_var[col].std()
            upper_limit = mean + 0.1 * std
            lower_limit = mean - 1.75 * std
            self.exogenous_var[col] = self.exogenous_var[col].clip(lower=lower_limit, upper=upper_limit)

        # Convert wet-bulb to Kelvin
        self.exogenous_var.iloc[:, -1] += 273.15 + Towb_offset_in_K

        # Convert to numpy
        self.exogenous_var = self.exogenous_var.to_numpy()

        # Disaggregation: ÷5 cabinets × ÷3 branches = ÷15
        Q_flow_totals = self.exogenous_var[:, 1:1+nCDUs] / parallel_nCabinets
        Q_flow_totals /= nBranches
        Q_flow_totals = Q_flow_totals.repeat(nBranches, axis=1).round(2)

        # Time-shifting (fake periodicity)
        columns_to_roll_dict = {1: 1800, 2: 3600, 4: 1800, 5: 3600, 7: 1800, 8: 3600, 10: 1800, 11: 3600, 13: 1800, 14: 3600}
        for col, roll in columns_to_roll_dict.items():
            Q_flow_totals[:, col] = np.roll(Q_flow_totals[:, col], roll, axis=0)

        self.exogenous_var_final = np.concatenate([Q_flow_totals, self.exogenous_var[:, -1].reshape(-1, 1)], axis=1)
        self.exogenous_var_final = self.exogenous_var_final[::subsample_rate]

        print(f"[V1] Loaded {csv_path}: {self.exogenous_var_final.shape} (÷15 divisor, clipping + roll)")

    def iterate_cyclically(self):
        """Yield rows cyclically."""
        while True:
            for row in self.exogenous_var_final:
                yield row


class ExogenousGeneratorV2:
    """sustain-lc v2: ÷15 divisor with softmax + smoothing."""

    def __init__(self, csv_path, Towb_offset_in_K=10, nCDUs=5, nBranches=3,
                 parallel_nCabinets=5, smoothing_kernel_size=50, subsample_rate=1,
                 hru_e_ntu=0.90, use_hru=False):
        """
        Load CSV and apply sustain-lc v2 preprocessing.

        Args:
            csv_path: path to CSV (time, power[1..25], Towb)
            smoothing_kernel_size: convolution kernel size (default 50)
        """
        from scipy.special import softmax

        total_num_cabinets = 25
        self.exogenous_var = pd.read_csv(csv_path)

        # Clipping
        for col in self.exogenous_var.columns[1:1+total_num_cabinets]:
            mean = self.exogenous_var[col].mean()
            std = self.exogenous_var[col].std()
            upper_limit = mean + 0.1 * std
            lower_limit = mean - 1.75 * std
            self.exogenous_var[col] = self.exogenous_var[col].clip(lower=lower_limit, upper=upper_limit)

        # Convert wet-bulb to Kelvin
        self.exogenous_var.iloc[:, -1] += 273.15 + Towb_offset_in_K

        # Convert to numpy
        self.exogenous_var = self.exogenous_var.to_numpy()

        # Disaggregation: ÷5 × ÷3 = ÷15
        Q_flow_totals = self.exogenous_var[:, 1:1+total_num_cabinets] / parallel_nCabinets
        Q_flow_totals /= nBranches
        Q_flow_totals = Q_flow_totals.repeat(nBranches, axis=1).round(2)

        # Time-shifting
        columns_to_roll_dict = {}
        for i in range(1, total_num_cabinets * nBranches):
            if i % 3 != 0:
                columns_to_roll_dict[i] = 1800 * (i % nBranches)
        for col, roll in columns_to_roll_dict.items():
            Q_flow_totals[:, col] = np.roll(Q_flow_totals[:, col], roll, axis=0)

        # Stacking: split into 5-cabinet chunks
        Q_flow_totals = np.concatenate([Q_flow_totals[:, i:i+15] for i in range(0, total_num_cabinets*nBranches, 15)], axis=0)

        # Softmax + smoothing
        kernel_size = smoothing_kernel_size
        kernel = np.ones(kernel_size) / kernel_size
        for i in range(0, Q_flow_totals.shape[1], 3):
            max_value = np.max(Q_flow_totals[:, i:i+3])
            Q_flow_totals[:, i:i+3] = softmax(Q_flow_totals[:, i:i+3], axis=1) * max_value
            Q_flow_totals[:, i] = np.convolve(Q_flow_totals[:, i], kernel, mode='same')
            Q_flow_totals[:, i+1] = np.convolve(Q_flow_totals[:, i+1], kernel, mode='same')
            Q_flow_totals[:, i+2] = np.convolve(Q_flow_totals[:, i+2], kernel, mode='same')

        if use_hru:
            Q_flow_totals = Q_flow_totals * hru_e_ntu

        towb = self.exogenous_var[:, -1].repeat(5).reshape(-1, 1)
        self.exogenous_var_final = np.concatenate([Q_flow_totals, towb], axis=1)
        self.exogenous_var_final = self.exogenous_var_final[::subsample_rate]

        print(f"[V2] Loaded {csv_path}: {self.exogenous_var_final.shape} (÷15 divisor, softmax + smoothing)")

    def iterate_cyclically(self):
        """Yield rows cyclically."""
        while True:
            for row in self.exogenous_var_final:
                yield row


class ExogenousGeneratorV3:
    """NVAITC new: ÷9 divisor, no preprocessing, uses NVAITC disaggregator."""

    def __init__(self, csv_path, Towb_offset_in_K=15.0,
                 selected_columns=None, branch_split="equal", subsample_rate=1):
        """
        Load CSV and apply NVAITC disaggregator (÷9 = ÷3 cabinets × ÷3 branches).

        Args:
            csv_path: path to CSV (time, power[1..25], Towb)
            Towb_offset_in_K: wet-bulb offset (default 15K)
            selected_columns: which 5 CDU groups to use (default: [0,1,2,3,4])
            branch_split: "equal" (only option for now)
            subsample_rate: keep every k-th row (default 1 = no subsampling)
        """
        from optimal_dc.workload_gen_pipeline.disaggregator import disaggregate

        # Load CSV
        df = pd.read_csv(csv_path)

        # Extract power and wet-bulb columns
        # Assume format: time, power[1], power[2], ..., power[25], Towb
        P = df.iloc[:, 1:26].values.astype(np.float32)  # (T, 25)
        towb_C = df.iloc[:, -1].values.astype(np.float32)  # (T,)

        # Apply NVAITC disaggregator
        exog, meta = disaggregate(
            P,
            towb_C,
            slice_mode="first5" if selected_columns is None else selected_columns,
            branch_split=branch_split,
            towb_offset_K=Towb_offset_in_K
        )

        self.exogenous_var_final = exog.astype(np.float32)[::subsample_rate]  # (T, 16)
        self.meta = meta

        print(f"[V3] Loaded {csv_path}: {self.exogenous_var_final.shape}")
        print(f"     {meta['convention']}")
        print(f"     Columns: {meta['columns']}, Split: {meta['branch_split']}")

    def iterate_cyclically(self):
        """Yield rows cyclically."""
        while True:
            for row in self.exogenous_var_final:
                yield row


def create_exogenous_generator(csv_path, version="v3", **kwargs):
    """
    Factory function for pluggable disaggregators.

    Args:
        csv_path: path to CSV data
        version: "v1", "v2", or "v3"
        **kwargs: additional arguments passed to the generator

    Returns:
        Generator iterator that yields (T, 16) exogenous rows
    """
    if version == "v1":
        return ExogenousGeneratorV1(csv_path, **kwargs).iterate_cyclically()
    elif version == "v2":
        return ExogenousGeneratorV2(csv_path, **kwargs).iterate_cyclically()
    elif version == "v3":
        return ExogenousGeneratorV3(csv_path, **kwargs).iterate_cyclically()
    else:
        raise ValueError(f"Unknown disaggregator version: {version}")
