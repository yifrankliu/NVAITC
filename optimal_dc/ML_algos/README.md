# ML Algorithms: Datacenter Cooling Control via RL

Training suite for RL algorithms (PPO, SAC) on FrontierEnv with preprocessed exogenous traces.

## Input/Output Contract

**See `io_contract.py` for the stable interface.**

### Input: Exogenous Trace
- **Shape:** `(T, 16)` array (T timesteps, 16 channels)
- **Columns 0-14:** Blade-group power (watts), from disaggregator.py
- **Column 15:** Wet-bulb temperature (kelvin)
- **Resolution:** 15s per timestep (zero-order-hold)
- **Units:** SI (watts, kelvin) — no normalization at input; algorithms normalize internally

### Output: Normalized Actions
- **Cabinet actions:** `(5, 5)` array, values in `[-1, 1]`
  - 5 cabinets × 5 actions each (2 PID setpoints + 3 valve fractions)
- **Cooling tower action:** integer in `[0, 8]` (discrete fan speed)

The contract is **independent of:**
- Whether data is real (Frontier, OneAsia) or synthetic (regime-A, regime-B)
- Which stacking mode was used (none, phase-shift, regime-A synthetic)
- Column selection (first5, representative, etc.)

Algorithms see only the `(T, 16)` trace and metadata for transparency.

---

## Quick Start

### 1. Training Variant A (Frontier only)

```bash
cd /path/to/NVAITC

python -m optimal_dc.ML_algos.train \
  --config optimal_dc/ML_algos/config/variant_a_frontier.yaml \
  --output optimal_dc/ML_algos/checkpoints/variant_a/ \
  --n_steps 500_000 \
  --algo ppo \
  --seed 0
```

**Output:**
```
optimal_dc/ML_algos/checkpoints/variant_a/
├── ppo_final.pt         # final trained weights
├── config.json          # hyperparameters used
├── metadata.json        # run metadata
└── train.log           # training metrics
```

### 2. Training Variant B (Frontier + OneAsia, when available)

```bash
python -m optimal_dc.ML_algos.train \
  --config optimal_dc/ML_algos/config/variant_b_oneasia.yaml \
  --output optimal_dc/ML_algos/checkpoints/variant_b/ \
  --n_steps 1_000_000 \
  --algo ppo \
  --seed 0
```

### 3. Compare Ablation Results

```python
# analysis/ablation_study.ipynb
import numpy as np
from optimal_dc.ML_algos import PPO

# Load checkpoints
agent_a = PPO(config_a, env)
agent_a.load_checkpoint("optimal_dc/ML_algos/checkpoints/variant_a/ppo_final.pt")

agent_b = PPO(config_b, env)
agent_b.load_checkpoint("optimal_dc/ML_algos/checkpoints/variant_b/ppo_final.pt")

# Evaluate on held-out real data
eval_a = agent_a.evaluate(eval_env, n_episodes=10)
eval_b = agent_b.evaluate(eval_env, n_episodes=10)

print(f"Variant A mean return: {eval_a['mean_return']:.2f}")
print(f"Variant B mean return: {eval_b['mean_return']:.2f}")
print(f"Improvement: {(eval_b['mean_return'] - eval_a['mean_return']) / abs(eval_a['mean_return']) * 100:.1f}%")
```

---

## Architecture

### Files

- **`io_contract.py`**: Input/output interface (stable, never changes unless FMU changes)
- **`base_algorithm.py`**: Abstract base class for all algorithms
- **`ppo.py`**: PPO implementation (policy gradient with clipped objective)
- **`train.py`**: Training script (loads config, creates env, trains agent)
- **`config/`**: Hyperparameter configs
  - `default.yaml`: Base settings
  - `variant_a_frontier.yaml`: Ablation A (Frontier only)
  - `variant_b_oneasia.yaml`: Ablation B (Frontier + OneAsia)

### Network Architecture

**PPONetwork:**
```
Input (30,)  [normalized flat obs]
  ↓
Backbone: MLP([256, 256])
  ↓
Policy Head: Linear(256 → 25 + 9)  [cabinet + tower logits]
Value Head:  Linear(256 → 1)       [value estimate]
```

Cabinet actions are continuous (tanh-squashed); cooling tower is discrete (softmax).

---

## Configuration

All hyperparameters are in YAML configs. Key parameters:

| Parameter | Default | Notes |
|-----------|---------|-------|
| `learning_rate` | 3e-4 | Adam learning rate |
| `batch_size` | 64 | PPO minibatch size |
| `n_epochs` | 10 | Policy update epochs per rollout |
| `clip_ratio` | 0.2 | PPO clip range (ε in original paper) |
| `entropy_coef` | 0.01 | Entropy bonus weight |
| `gamma` | 0.99 | Discount factor |
| `gae_lambda` | 0.95 | GAE variance-bias parameter |
| `n_steps` | 2048 | Rollout length before update |

**To override**, modify the YAML or pass `--config custom.yaml`.

---

## Training Dynamics

### Variant A (Frontier only, ~500k steps)
- **Data:** 16h real Frontier + regime-A synthetic (2 days)
- **Expected training time:** ~2-4 hours on GPU
- **Expected return:** TBD (baseline)
- **Use case:** Establish single-cluster performance; validates regime-A synthetic

### Variant B (Frontier + OneAsia, ~1M steps, pending data)
- **Data:** Frontier (real) + OneAsia (real, N days TBD)
- **Expected training time:** ~4-8 hours on GPU
- **Expected improvement over A:** TBD (hypothesis: ±5-15% better energy)
- **Use case:** Multi-cluster validation; shows value of additional real data

---

## Evaluation

### Post-Training Metrics

After training, evaluate the policy:

```python
from optimal_dc.ML_algos import PPO
from optimal_dc.external.sustain_lc import FrontierEnv

agent = PPO(config, env)
agent.load_checkpoint("checkpoints/variant_a/ppo_final.pt")

metrics = agent.evaluate(eval_env, n_episodes=10, deterministic=True)
print(f"Mean return: {metrics['mean_return']:.2f}")
print(f"Mean episode length: {metrics['mean_episode_length']:.0f}")
print(f"Constraint violations: {metrics['total_constraint_violations']}")
```

### Energy Calculation

Cooling energy is the primary metric:

```
Energy (kWh/day) = ∫ P_facility(t) dt / 3600
                  = mean(facility_power_kW) * 24
```

This is tracked during rollout and reported in the reward.

---

## Troubleshooting

### Training is slow
- Reduce `n_steps` for faster rollout, or increase `batch_size` for faster gradient updates
- Ensure CUDA is available: `torch.cuda.is_available()`

### Policy doesn't improve
- Check reward function in FrontierEnv (is it actually incentivizing low energy?)
- Increase `entropy_coef` to encourage exploration
- Reduce `learning_rate` if gradients are too noisy

### Out of memory (CUDA)
- Reduce `batch_size` (64 → 32)
- Reduce `hidden_sizes` ([256, 256] → [128, 128])
- Use `--device cpu` (slow but works)

---

## Future Work

- [ ] Implement SAC (off-policy, potentially more sample-efficient)
- [ ] Vectorized environments (parallel rollout collectors)
- [ ] Model-based RL (dynamics prediction + planning)
- [ ] Imitation learning initialization (bootstrap from model-predictive baseline)
- [ ] Multi-agent extension (separate policy per cabinet for emergent control)

---

## References

- **PPO:** Schulman et al., "Proximal Policy Optimization Algorithms" (2017)
- **GAE:** Schulman et al., "High-Dimensional Continuous Control Using Generalized Advantage Estimation" (2016)
- **sustain-lc:** HPE/ORNL LC-Opt baseline (https://github.com/HewlettPackard/sustain-lc)
- **FrontierEnv:** FMU wrapper in `optimal_dc/external/sustain-lc/frontier_env.py`
