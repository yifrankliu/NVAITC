# FrontierEnv_v3: Pluggable Data Source & Disaggregator

## Overview

`frontier_env_v3.py` extends sustain-lc's `SmallFrontierModel` with two pluggable features:

1. **CSV data source path switching** — Load real Frontier or synthetic regime-A data without hardcoded paths
2. **Disaggregator version selection** — Use v1 (sustain-lc ÷15), v2 (sustain-lc ÷15 smoothed), or v3 (NVAITC ÷3)

No code duplication: only overrides `__init__` to swap the exogenous generator.

---

## Architecture

```
SmallFrontierModel (parent, sustain-lc)
  ├─ FMU binary interface (do_step, set, get)
  ├─ Observation/action spaces (normalized [-1,1])
  ├─ Reward shaping (energy_only)
  └─ get_exogenous_var() method (uses self.iter_exogenous_var)
         ↑
         └─ SmallFrontierModel_v3 (subclass, NVAITC)
              ├─ __init__: accept csv_path, disaggregator_version
              ├─ Create pluggable exogenous generator
              └─ Inherit all else from parent
                    ↓
                    exogenous_generators.py (separate module)
                    ├─ ExogenousGeneratorV1 (sustain-lc v1, ÷15 + clipping)
                    ├─ ExogenousGeneratorV2 (sustain-lc v2, ÷15 + softmax + smooth)
                    └─ ExogenousGeneratorV3 (NVAITC v3, ÷3)
```

---

## Usage

### Basic: Real Frontier CSV with v3 Disaggregator (Recommended)

```python
from optimal_dc.inherited_FMU_with_modifications.frontier_env_v3 import SmallFrontierModel_v3

env = SmallFrontierModel_v3(
    fmu_path="path/to/LC_Frontier_5Cabinet_4_17_25.fmu",
    csv_path="optimal_dc/external/sustain-lc/input_04-07-24.csv",  # Real Frontier data
    disaggregator_version="v3",  # New ÷3 cabinet disaggregator
    max_steps=5761,
)

# Standard Gym interface
obs, info = env.reset()
for _ in range(1000):
    action = agent.predict(obs)  # Your RL agent
    obs, reward, terminated, truncated, info = env.step(action.to_dict())
    if terminated or truncated:
        break
```

### Switching Data Sources

```python
# Same v3 disaggregator, different CSV
env_real = SmallFrontierModel_v3(
    fmu_path=fmu_path,
    csv_path="optimal_dc/external/sustain-lc/input_04-07-24.csv",  # Real Frontier
    disaggregator_version="v3",
)

env_synthetic = SmallFrontierModel_v3(
    fmu_path=fmu_path,
    csv_path="optimal_dc/workload_gen/regime_a_data.csv",  # Synthetic regime-A
    disaggregator_version="v3",
)

# Both use same thermal regime (÷3) but different data
```

### Comparing Disaggregators (Ablation)

```python
# sustain-lc v1 (÷15, clipping)
env_v1 = SmallFrontierModel_v3(
    fmu_path=fmu_path,
    csv_path=csv_path,
    disaggregator_version="v1",
)

# sustain-lc v2 (÷15, softmax + smooth)
env_v2 = SmallFrontierModel_v3(
    fmu_path=fmu_path,
    csv_path=csv_path,
    disaggregator_version="v2",
)

# NVAITC v3 (÷3, no preprocessing)
env_v3 = SmallFrontierModel_v3(
    fmu_path=fmu_path,
    csv_path=csv_path,
    disaggregator_version="v3",
)
```

### Using Convenience Functions

```python
from optimal_dc.inherited_FMU_with_modifications.frontier_env_v3 import create_env_v1, create_env_v2, create_env_v3

# All three are equivalent:
env = create_env_v3(fmu_path, csv_path)
env = SmallFrontierModel_v3(fmu_path, csv_path, disaggregator_version="v3")
```

---

## Thermal Regime Awareness

When instantiated, each environment prints its configuration:

```
[SmallFrontierModel_v3] Configuring data pipeline
  CSV path: optimal_dc/external/sustain-lc/input_04-07-24.csv
  Disaggregator: v3
  Towb offset: 15K

[V3] Loaded ...: (5761, 16)
     180 kW/cabinet (60 kW per blade group)
     Columns: [0, 1, 2, 3, 4], Split: equal
```

### Key Differences

| Version | Divisor | Thermal Regime | Preprocessing | Use Case |
|---------|---------|----------------|---------------|----------|
| **v1** | ÷15 (÷5×÷3) | 36 kW/blade | clipping + roll | sustain-lc baseline |
| **v2** | ÷15 (÷5×÷3) | 36 kW/blade | softmax + smooth | sustain-lc enhanced |
| **v3** | ÷3 | 60 kW/blade | none (matched to FMU) | NVAITC new baseline |

**⚠️ Critical:** v1/v2 and v3 have **5× difference** in energy consumption due to different thermal regimes.  
When comparing results, **always record which version** was used, or normalize by regime.

---

## Training with Benchmarks CLI

The `benchmarks.py` script now automatically uses `frontier_env_v3`:

```bash
# Train on real Frontier data with v3 disaggregator
python -m optimal_dc.ML_algos.benchmarks train \
  --output checkpoints/variant_a \
  --n_steps 500_000 \
  --seed 0

# The config file specifies:
# fmu_path: path/to/fmu
# csv_path: optimal_dc/external/sustain-lc/input_04-07-24.csv
# disaggregator_version: v3
```

Config file (`config/variant_a_frontier.yaml`):

```yaml
fmu_path: "optimal_dc/external/sustain-lc/LC_Frontier_5Cabinet_4_17_25.fmu"
csv_path: "optimal_dc/external/sustain-lc/input_04-07-24.csv"
disaggregator_version: "v3"

learning_rate: 3e-4
batch_size: 64
# ... other hyperparams
```

---

## What Changed

### Before (Hardcoded v1/v2)
```python
# frontier_env.py (sustain-lc)
class SmallFrontierModel:
    def __init__(self, fmu_path):
        self.iter_exogenous_var = exogenous_variable_generator(...)  # v1, hardcoded
        # No way to switch data source or disaggregator
```

### After (Pluggable v1/v2/v3)
```python
# frontier_env_v3.py (NVAITC)
class SmallFrontierModel_v3(SmallFrontierModel):
    def __init__(self, fmu_path, csv_path, disaggregator_version="v3"):
        super().__init__(fmu_path)
        self.iter_exogenous_var = create_exogenous_generator(
            csv_path, version=disaggregator_version
        )
        # Now pluggable: any data source + any disaggregator
```

---

## For Developers

### Adding a New Disaggregator

1. Create a new class in `exogenous_generators.py`:
   ```python
   class ExogenousGeneratorV4:
       def __init__(self, csv_path, ...):
           # Load CSV, process, store in self.exogenous_var_final
           pass
       
       def iterate_cyclically(self):
           while True:
               for row in self.exogenous_var_final:
                   yield row
   ```

2. Register in factory:
   ```python
   def create_exogenous_generator(csv_path, version="v3", **kwargs):
       elif version == "v4":
           return ExogenousGeneratorV4(csv_path, **kwargs).iterate_cyclically()
   ```

3. Use immediately:
   ```python
   env = SmallFrontierModel_v3(fmu_path, csv_path, disaggregator_version="v4")
   ```

### Adding a New Data Source

Just pass a different CSV path — no code changes needed:

```python
env_new_data = SmallFrontierModel_v3(
    fmu_path=fmu_path,
    csv_path="path/to/new_data.csv",  # Any format, same (T, 26) structure
    disaggregator_version="v3",
)
```

---

## CSV Format Expectations

All CSVs must have structure:
- **Column 0:** time (ignored)
- **Columns 1–25:** per-CDU power (Watts) or CDU group power
- **Column 26:** wet-bulb temperature (Celsius)

Total: 27 columns, T rows (any T ≥ 1440 steps for meaningful training)

### Example (input_04-07-24.csv)
```
time,power_1,power_2,...,power_25,towb_celsius
0.0,50000,52000,...,49500,20.5
15.0,50100,51900,...,49600,20.6
...
```

---

## Validation Checklist

After training an agent, verify it used correct thermal regime:

```json
{
  "metadata.json": {
    "data_source": "optimal_dc/external/sustain-lc/input_04-07-24.csv",
    "disaggregator": "v3",
    ...
  },
  "eval_results.json": {
    "mean_energy_kWh": 2835,  // v3 should be ~2.5-3.0k kWh/day
    "mean_max_temp_C": 39.8,  // should be <40°C
    ...
  }
}
```

✅ **Energy ~2800-3000 kWh** (v3 regime, real Frontier data)  
❌ **Energy ~600-800 kWh** (something wrong; check disaggregator)  
❌ **Max temp >41°C** (thermal violations; policy needs tuning)

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: exogenous_generators` | Import path wrong | Check `PYTHONPATH` includes `optimal_dc/` |
| `CSV not found` | Path is relative | Use absolute path or config file |
| `Energy way too low` | Using v1/v2 (÷15) when should use v3 (÷3) | Check `disaggregator_version` in config |
| `disagreement with sustain-lc baseline` | Comparing v3 (÷3) to v1 (÷15) directly | Normalize by regime factor (5×) |

---

## Next: One-Shot Validation

To verify the new pipeline works end-to-end:

```bash
python -c "
from optimal_dc.external.frontier_env_v3 import create_env_v3

env = create_env_v3(
    fmu_path='optimal_dc/external/sustain-lc/LC_Frontier_5Cabinet_4_17_25.fmu',
    csv_path='optimal_dc/external/sustain-lc/input_04-07-24.csv'
)

obs, info = env.reset()
print(f'Obs shape: {obs}')
print(f'✅ frontier_env_v3 works!')
"
```

If that passes, you're ready to train.
