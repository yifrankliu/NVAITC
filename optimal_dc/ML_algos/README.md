# ML Algorithms: Datacenter Cooling Control via RL

Training suite for the sustain-lc RL baselines on the v3 pluggable-data envs
(real Frontier CSV or delivered synthetic regime-A days, ÷9 disaggregation).

## Algorithms

The two RL baselines sustain-lc ships, reused from the submodule (no copies)
and wired into this repo's env/data plumbing — see `sustainlc_baselines.py`:

| `--algo` | CDUCAB agent | CT agent | Env |
|---|---|---|---|
| `ma_ca_ppo` | `CA_PPO`: continuous (5,) action, one net over 5 centralized cabinet actions | `CA_PPO` discrete-9 | `SmallFrontierModel_v3` |
| `mh_ma_ca_ppo` | `MultiHead_CA_PPO`: top-level (2,) tanh-Gaussian + valve (3,) Dirichlet heads | `CA_PPO` discrete-9 | `MH_SmallFrontierModel_v3` (subsample 40, valve softmax off) |

Hyperparameter defaults are the exact upstream train-script values (ep_len 200,
update every 1×/2× ep_len, K=50, γ=0.80, clip 0.2, lr 3e-4/1e-3, action-std
0.6→0.1 at 0.05/250k, `reward_shaping_v2`); any config key of the same name
overrides them.

A third, unified single-network baseline exists as Frank's
`optimal_dc/unified_mlp_baseline.py` (Unified_PPO, 34-dim flat state) — not yet
wrapped into this registry.

## Files

- **`sustainlc_baselines.py`** — `MA_CA_PPO` / `MH_MA_CA_PPO` classes: faithful
  training loops, buffer-free `predict()` (with deterministic mode),
  physical-metrics `evaluate()` (warm-up discard, optional `t_max_K`),
  per-agent checkpoint pairs compatible with the shipped preTrained weights
  (`load_sustainlc_pretrained()`).
- **`benchmarks.py`** — the CLI: `train` / `eval` subcommands, `ALGOS` registry.
- **`base_algorithm.py`** — shared config/logging/checkpoint-dir scaffolding.
- **`data_loader.py`** — CSV + synthetic loading, canonical ÷9 disaggregation
  (delegates to `workload_gen_pipeline/disaggregator.py`). NOTE: the
  variant-A stacking path is not yet consumed by `benchmarks.py` (open seam);
  the env currently ingests a CSV directly.
- **`io_contract.py`** — the documented data/action interface: (T, 16)
  exogenous trace in, (5, 5) cabinet + discrete-9 CT actions out; flat
  observation is **34-dim** (5×6 cabinet + 4 CT).
- **`config/`** — YAML hyperparameters. `csv_path` and `disaggregator_version`
  are the data-pipeline keys `benchmarks.py` reads (relative paths resolve
  against the repo root `NVAITC/`).

## Usage

```bash
# from NVAITC/  (ML_workspace conda env: torch + pyfmi + pyyaml)
python -m optimal_dc.ML_algos.benchmarks train \
  --algo ma_ca_ppo \
  --config optimal_dc/ML_algos/config/variant_a_frontier.yaml \
  --output optimal_dc/ML_algos/checkpoints/variant_a_ma \
  --n_steps 3_000_000 --seed 0

python -m optimal_dc.ML_algos.benchmarks eval \
  --checkpoint optimal_dc/ML_algos/checkpoints/variant_a_ma/ma_ca_ppo_final_agent_CDUCAB.pth \
  --n_episodes 5
```

Checkpoints are per-agent pairs (`*_agent_CDUCAB.pth` + `*_agent_CT.pth`);
`metadata.json` records algo, data source, and disaggregator version, and
`eval` restores all three.

Upstream training budgets: 3M steps for MA (~18 h on an RTX 5060 laptop GPU;
FMU stepping is CPU-bound), 5M for MH.

## Caveats

- The shipped preTrained weights were trained on v2 ÷15 data — evaluating them
  on v3 ÷9 input is out-of-distribution. Retrain for ÷9 comparisons.
- `evaluate()` discards a 10-step warm-up (the FMU's ~139 °C init transient)
  and takes `t_max_K` with **no default**: the ÷15-era 313 K limit does not
  transfer to the hotter ÷9 regime; set it from the ÷9 rule-based baseline.
- TensorBoard logging is not ported; metrics go to the logger + `train_log`.

## History

A from-scratch unified `ppo.py` + `train.py` + `evaluate.py` scaffold was
removed 2026-08-28: its update rule was a placeholder (no policy gradient),
its env API was wrong (gymnasium 5-tuple vs the env's 4-tuple/dict), and its
network input was 30-dim vs the actual 34-dim observation.

## References

- **PPO:** Schulman et al., 2017
- **sustain-lc / LC-Opt:** HPE+ORNL, arXiv:2511.00116 (NeurIPS 2025 D&B)
- **Env:** `optimal_dc/external/sustain-lc/frontier_env.py` (+ v3 wrappers in
  `optimal_dc/inherited_FMU_with_modifications/`)
