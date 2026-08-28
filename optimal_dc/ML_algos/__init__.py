"""
Machine learning algorithms for optimal datacenter cooling control.

This module provides baseline RL algorithms (PPO, SAC) trained on preprocessed
exogenous traces (disaggregator output) using the FrontierEnv environment.

The input/output contract is defined in io_contract.py:
  - Input: (T, 16) exogenous trace from disaggregator
  - Output: normalized actions for 5 CDU-cabinets + 1 cooling tower
"""

# PPO/BaseAlgorithm need torch; import them lazily (PEP 562) so numpy-only
# consumers (data_loader, io_contract) work in envs without torch installed.
_LAZY = {"BaseAlgorithm": ".base_algorithm", "PPO": ".ppo"}

__all__ = ["BaseAlgorithm", "PPO"]


def __getattr__(name):
    if name in _LAZY:
        from importlib import import_module
        return getattr(import_module(_LAZY[name], __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
