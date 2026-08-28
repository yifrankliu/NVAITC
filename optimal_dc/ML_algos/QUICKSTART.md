# Quick Start: Variant A Benchmark

**Variant A** = Frontier CSV (real, 1 day) + regime-A synthetic (extended)

This is your baseline to establish single-cluster performance while waiting for OneAsia data.

---

## 1. Setup

```bash
# Navigate to project root
cd /path/to/NVAITC

# Ensure dependencies are installed
pip install torch numpy pyyaml gymnasium

# Verify frontier_env exists
ls optimal_dc/external/sustain-lc/frontier_env.py
ls optimal_dc/external/sustain-lc/input_04-07-24.csv
ls optimal_dc/workload_gen_pipeline/spec/regime_A_calib.json
```

---

## 2. Quick Test (100 steps, ~5 min)

```bash
python -m optimal_dc.ML_algos.benchmarks train \
  --output /tmp/test_variant_a \
  --n_steps 100
```

**Expected output:**
```
[...training logs...]
Training complete!
Saved checkpoint: /tmp/test_variant_a/ppo_final.pt
```

If this works, proceed to full training.

---

## 3. Full Training (500k steps, ~4-6 hours on GPU)

```bash
python -m optimal_dc.ML_algos.benchmarks train \
  --output optimal_dc/ML_algos/checkpoints/variant_a \
  --n_steps 500_000 \
  --seed 0
```

**What happens:**
1. Loads Frontier CSV (real, 1 day)
2. Generates 2 days regime-A synthetic
3. Disaggregates to FMU inputs (16 channels)
4. Trains PPO for 500k steps (~24h simulated time)
5. Saves checkpoint + metadata

**Monitoring:**
- Check `checkpoints/variant_a/train.log` for convergence
- Look for **decreasing loss** and **increasing return** over time
- If stuck, interrupt (Ctrl+C) and reduce `--n_steps` to debug

---

## 4. Evaluation (10 episodes, ~10 min)

```bash
python -m optimal_dc.ML_algos.benchmarks eval \
  --checkpoint optimal_dc/ML_algos/checkpoints/variant_a/ppo_final.pt \
  --n_episodes 10
```

**Expected output:**
```
VARIANT A EVALUATION
================================================================================
Checkpoint: .../ppo_final.pt

Evaluating over 10 episodes...
Episode 1/10: energy=2850 kWh, violations=0.0%
Episode 2/10: energy=2820 kWh, violations=0.1%
...

RESULTS
================================================================================
mean_energy_kWh:                        2835.00
std_energy_kWh:                           25.50
mean_constraint_violation_rate:           0.05
worst_case_violation_rate:                0.15
mean_max_temp_C:                         39.50
episodes_completed:                        10
```

Save this; you'll compare it to variant B later.

---

## 5. Manual Testing (optional)

Test the pipeline step-by-step:

```python
# test_variant_a.py
from optimal_dc.ML_algos.data_loader import load_data_variant_a
from optimal_dc.ML_algos.ppo import PPO
from optimal_dc.external.sustain_lc.frontier_env import FrontierEnv

# Load data
data = load_data_variant_a(n_synthetic_days=2)
print(f"Train shape: {data['train']['power'].shape}")
print(f"Eval shape: {data['eval']['power'].shape}")

# Create env and agent
env = FrontierEnv()
config = {"learning_rate": 3e-4, "batch_size": 64, ...}
agent = PPO(config, env)

# One training step
obs, _ = env.reset()
action = agent.predict(obs)
print(f"Action: {action.cabinet_actions.shape}, {action.cooling_tower_action}")

# One eval step
import json
with open("checkpoints/variant_a/config.json") as f:
    config = json.load(f)
agent_loaded = PPO(config, env)
agent_loaded.load_checkpoint("checkpoints/variant_a/ppo_final.pt")
```

---

## 6. Understanding Results

### Key Metrics

| Metric | Target | What It Means |
|--------|--------|---|
| **energy_kWh** | Minimize | Daily cooling energy; goal is <2800 kWh |
| **violations (%)** | <0.5% | Thermal constraint violations; goal is near 0 |
| **max_temp_C** | <40°C | Maximum inlet temperature; hard limit is ~41°C |
| **return** | Higher is better | Cumulative reward (negative = energy + penalties) |

### Sanity Checks

- **Energy too low (<2000 kWh):** Policy may be under-cooling (constraint violations?)
- **Energy too high (>3500 kWh):** Policy may be over-conservative
- **Max temp >41°C:** Constraint violations; control is unstable
- **Loss not decreasing:** Bad hyperparameters or broken data flow

---

## 7. Troubleshooting

### Error: "input_04-07-24.csv not found"
```bash
# Check file exists
ls optimal_dc/external/sustain-lc/input_04-07-24.csv

# If missing, download from sustain-lc repo
# https://github.com/HewlettPackard/sustain-lc
```

### Error: "regime_A_calib.json not found"
```bash
# Run calibration first (one-time setup)
python -m optimal_dc.workload_gen_pipeline.calibrate

# Or copy from a prior run if available
```

### CUDA out of memory
```bash
# Reduce batch size in config/default.yaml
batch_size: 32  # was 64

# Or train on CPU (slower)
--device cpu
```

### Training is slow
```bash
# Reduce n_steps for testing
--n_steps 10_000  # quick test

# Increase after verifying it works
--n_steps 500_000  # full training
```

---

## 8. Next Steps (When OneAsia Arrives)

Once OneAsia data is available:

```bash
# Train variant B with the same script
python -m optimal_dc.ML_algos.benchmarks train \
  --config optimal_dc/ML_algos/config/variant_b_oneasia.yaml \
  --output optimal_dc/ML_algos/checkpoints/variant_b \
  --n_steps 1_000_000

# Evaluate variant B
python -m optimal_dc.ML_algos.benchmarks eval \
  --checkpoint optimal_dc/ML_algos/checkpoints/variant_b/ppo_final.pt \
  --n_episodes 10

# Compare in a notebook
# (See comparison_notebook.ipynb template)
```

---

## 9. Directory Structure After Training

```
optimal_dc/ML_algos/
├── checkpoints/
│   └── variant_a/
│       ├── config.json               # hyperparams used
│       ├── ppo_final.pt              # trained weights
│       ├── metadata.json             # run metadata
│       ├── eval_results.json         # evaluation metrics
│       └── train.log                 # training curves (optional)
└── ...
```

---

## Commands Reference

```bash
# Quick test (100 steps, ~5 min)
python -m optimal_dc.ML_algos.benchmarks train --n_steps 100 --output /tmp/test

# Full training (500k steps, ~4-6 hours)
python -m optimal_dc.ML_algos.benchmarks train --n_steps 500_000

# Evaluation
python -m optimal_dc.ML_algos.benchmarks eval --checkpoint <checkpoint.pt> --n_episodes 10

# With custom seed (for ablation)
python -m optimal_dc.ML_algos.benchmarks train --n_steps 500_000 --seed 1

# Check device
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"
```

---

## FAQ

**Q: How long will training take?**  
A: ~4-6 hours on GPU (NVIDIA A100/RTX), ~24 hours on CPU.

**Q: Can I interrupt and resume?**  
A: Not yet (would need checkpoint/resume logic). Just restart. Or reduce n_steps to finish faster.

**Q: How do I know if training is working?**  
A: Watch for loss decreasing and return increasing. First 100 steps should show immediate improvement.

**Q: What if results are bad (high energy, many violations)?**  
A: Likely hyperparameter issue or data flow bug. Start with quick test (100 steps) to verify pipeline, then debug.

**Q: When should I run variant B?**  
A: Only after OneAsia data arrives. For now, focus on getting variant A working solidly.

---

## Support

- Check `README.md` for architecture details
- Check `io_contract.py` for input/output shapes
- Check `data_loader.py` for data pipeline
- Check `evaluate.py` for metric definitions
