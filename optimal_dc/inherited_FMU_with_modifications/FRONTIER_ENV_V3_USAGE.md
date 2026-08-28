# FrontierEnv_v3: Pluggable Data Source & Disaggregator

> Last verified against code + FMU: **2026-08-28** (full pipeline smoke +
> end-to-end FMU ingestion tests).

## Overview

`frontier_env_v3.py` extends sustain-lc's `SmallFrontierModel` with two pluggable features:

1. **CSV data source path switching** — real Frontier, delivered synthetic regime-A
   days (`workload_gen_pipeline/synth_data/*.csv`), or any CSV with the same schema.
2. **Disaggregator version selection** — v1 (sustain-lc ÷15 + clip/roll),
   v2 (sustain-lc ÷15 + softmax/smooth), or v3 (NVAITC **÷9**, pass-through).

No code duplication: only `__init__` is overridden to swap the exogenous generator.

**The FMU path is NOT a parameter.** The parent loads the module-level `FMU_PATH`
constant — the FMU sitting next to `frontier_env.py` in `external/sustain-lc/`
(`LC_Frontier_5Cabinet_4_17_25.fmu`). Making it pluggable would mean
reimplementing the parent's `__init__`; do that in the fork if ever needed.

---

## Architecture

```
SmallFrontierModel (parent, sustain-lc)
  ├─ FMU binary interface (do_step, set, get)
  ├─ Observation/action spaces (normalized [-1,1])
  ├─ Reward shaping (reward_shaping_v0/v1/v2)
  └─ get_exogenous_var() -> next(self.iter_exogenous_var)
         ↑
         └─ SmallFrontierModel_v3 (subclass, NVAITC)
              ├─ __init__(csv_path, disaggregator_version, ...)
              ├─ patches frontier_env.EXOGENOUS_VAR_PATH around super().__init__
              │  (parent hardcodes a cwd-relative CSV; patch makes construction
              │   cwd-independent, restored in a finally)
              └─ replaces self.iter_exogenous_var with the pluggable generator
                    ↓
                    exogenous_generators.py (same directory)
                    ├─ ExogenousGeneratorV1 (sustain-lc v1, ÷15 + clip + roll)
                    ├─ ExogenousGeneratorV2 (sustain-lc v2, ÷15 + softmax + smooth; lazy scipy)
                    └─ ExogenousGeneratorV3 (NVAITC, ÷9 via workload_gen_pipeline/disaggregator.py)
```

---

## Usage

### Basic: real Frontier CSV with the v3 disaggregator (recommended)

```python
from optimal_dc.inherited_FMU_with_modifications.frontier_env_v3 import SmallFrontierModel_v3

env = SmallFrontierModel_v3(
    csv_path="optimal_dc/external/sustain-lc/input_04-07-24.csv",
    disaggregator_version="v3",          # NVAITC /9 (the settled convention)
)

obs = env.reset()                        # dict of 5 cabinet obs (6,) + CT obs (4,)
for _ in range(1000):
    action = agent.predict(obs)          # dict: 5x np.ndarray(5,) + int in [0,8]
    obs, reward, done, info = env.step(action)   # 4-tuple (old gym API)
```

Note the parent uses the **old gym 4-tuple** `(obs, reward, done, info)` API with
dict-valued reward/done, and `reset()` returns `obs` only — not the gymnasium
5-tuple.

### Switching data sources (e.g. a delivered synthetic day)

```python
env_real = SmallFrontierModel_v3(
    csv_path="optimal_dc/external/sustain-lc/input_04-07-24.csv",
    disaggregator_version="v3",
)

env_synthetic = SmallFrontierModel_v3(
    csv_path="optimal_dc/workload_gen_pipeline/synth_data/certified_demo.csv",
    disaggregator_version="v3",
)
# Same /9 thermal regime, different data. Verified: the env's v3 iterator
# reproduces the delivered <name>_exogenous.npy row-for-row.
```

### Comparing disaggregators (ablation)

```python
env_v1 = SmallFrontierModel_v3(csv_path=csv_path, disaggregator_version="v1")
env_v2 = SmallFrontierModel_v3(csv_path=csv_path, disaggregator_version="v2")
env_v3 = SmallFrontierModel_v3(csv_path=csv_path, disaggregator_version="v3")
```

### Convenience factories

```python
from optimal_dc.inherited_FMU_with_modifications.frontier_env_v3 import (
    create_env_v1, create_env_v2, create_env_v3,
)
env = create_env_v3(csv_path)   # == SmallFrontierModel_v3(csv_path, disaggregator_version="v3")
```

---

## Thermal Regime Awareness

On instantiation each environment prints its configuration:

```
[SmallFrontierModel_v3] Configuring data pipeline
  CSV path: .../input_04-07-24.csv
  Disaggregator: v3
  Towb offset: 15.0K
[V3] Loaded ...: (5761, 16)
     /9 (/3 cabinets per CDU group x /3 branches)
     Columns: [0, 1, 2, 3, 4], Split: equal
```

### Key differences

| Version | Divisor | Mean branch heat (real day) | Preprocessing | Use case |
|---------|---------|------------------------------|---------------|----------|
| **v1** | ÷15 (÷5×÷3) | ~34 kW (post-clip) | asymmetric clip + time-roll | sustain-lc lineage replication |
| **v2** | ÷15 (÷5×÷3) | ~lower, flattened | clip + roll + 5× stack + softmax + smooth (total becomes time-constant) | sustain-lc lineage replication |
| **v3** | **÷9 (÷3×÷3)** | **~72 kW** | none (pass-through) | **the settled faithful convention** |

The ÷9 is physically derived (a CSV column = one CDU group ≈ 3 cabinets; the
FMU's one representative cabinet takes 1/3, split over 3 blade groups) and was
**empirically verified** by an FMU energy-balance test (2026-07-16): injected
heat is recovered ×3.019 across the CDU secondary, so /9 is faithful. See
`workload_gen_pipeline/disaggregator.py` for the full derivation and self-test.

**Never compare a /9 number against a /15 number.** Every delivered trace
carries a `_meta.json` sidecar declaring its convention.

### FMU warm-up transient

The compiled-in FMU initial state produces a ~139 °C cabinet-temperature spike
in the first ~5 steps on ANY input (verified identical on the real day and on
synthetic days), decaying to a ~46 °C steady state within ~25 steps. Discard a
~10-step warm-up window before computing metrics or asserting thermal bounds.

---

## Training with the benchmarks CLI

```bash
python -m optimal_dc.ML_algos.benchmarks train \
  --output optimal_dc/ML_algos/checkpoints/variant_a \
  --n_steps 500_000 --seed 0
```

The YAML config supplies `csv_path` and `disaggregator_version` (relative paths
resolve against the repo root `NVAITC/`); both are recorded in the checkpoint's
`metadata.json` and restored on `eval`.

---

## For Developers

### Adding a new disaggregator

1. Add a class in `exogenous_generators.py` exposing `exogenous_var_final`
   (a `(T, 16)` array) and `iterate_cyclically()`.
2. Register it in `create_exogenous_generator()`.
3. Use it: `SmallFrontierModel_v3(csv_path, disaggregator_version="v4")`.

Keep any new version's kwargs compatible with what the env forwards
(`Towb_offset_in_K`, `subsample_rate`).

### CSV format contract

- Column 0: `time` (seconds, 15 s grid)
- Columns 1–25: `power[1]`..`power[25]` — per-CDU-group power in **watts**
- Column 26: `OA Wetbulb Temp` — **Celsius** (the generator adds +273.15 + offset)

`workload_gen_pipeline/deliver.py` writes exactly this schema, so delivered
synthetic days are drop-in replacements for the real CSV.

---

## Validation checklist (verified 2026-08-28)

- `disaggregator.py` self-test: conservation exact, 72.2 kW/branch,
  216.5 kW/cabinet vs physical 217.9 kW.
- Env v3 iterator == delivered `_exogenous.npy` (sub-watt agreement).
- `data_loader.disaggregate_to_fmu` == `ExogenousGeneratorV3` (both delegate to
  the canonical `disaggregate()`).
- 30 FMU steps on real + synthetic days: settled temps 41–56 °C, rewards finite.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: optimal_dc...` | repo root not on `sys.path` | the modules add it themselves from `__file__`; if importing manually, `sys.path.insert(0, "<...>/NVAITC")` |
| `TypeError: unexpected keyword 'fmu_path'` | pre-2026-08-28 call site | remove `fmu_path` / `max_steps` — neither is a parameter |
| Energy ~3–5× off between runs | mixing /9 and /15 regimes | check the `_meta.json` sidecar / checkpoint metadata |
| >100 °C temps in the first steps | FMU warm-up transient (input-independent) | discard a ~10-step warm-up window |
