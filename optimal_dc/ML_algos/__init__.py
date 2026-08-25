"""
Machine learning algorithms for optimal datacenter cooling control.

This module provides baseline RL algorithms (PPO, SAC) trained on preprocessed
exogenous traces (disaggregator output) using the FrontierEnv environment.

The input/output contract is defined in io_contract.py:
  - Input: (T, 16) exogenous trace from disaggregator
  - Output: normalized actions for 5 CDU-cabinets + 1 cooling tower
"""

from .base_algorithm import BaseAlgorithm
from .ppo import PPO

__all__ = ["BaseAlgorithm", "PPO"]
