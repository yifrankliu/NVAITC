# Quick Start: sustain-lc Baselines on Variant A

Train/evaluate the two sustain-lc RL baselines (`ma_ca_ppo`, `mh_ma_ca_ppo`)
on the real Frontier CSV with the ÷9 v3 disaggregator. See `README.md` for
architecture; everything below was smoke-tested 2026-08-28.

## 1. Setup

```bash
cd /path/to/NVAITC_files/NVAITC

# ML_workspace conda env has: torch (cu128), pyfmi, numpy, pandas, scipy, pyyaml
# Sanity-check the inputs exist:
ls optimal_dc/external/sustain-lc/frontier_env.py
ls optimal_dc/external/sustain-lc/input_04-07-24.csv
ls optimal_dc/workload_gen_pipeline/spec/regime_A_calib.json
```

## 2. Quick test (~1 min, 1 PPO update)

```bash
python -m optimal_dc.ML_algos.benchmarks train \
  --algo ma_ca_ppo --n_steps 250 --output /tmp/test_ma
```

Expected: FMU loads, `[V3] ... /9` banner, one `loss_CDUCAB=... loss_CT=...`
line at step 200, then `Saved ... ma_ca_ppo_final_agent_CDUCAB.pth (+CT)`.

## 3. Full training

```bash
# MA baseline (upstream budget 3M steps, ~18 h; FMU stepping is CPU-bound)
python -m optimal_dc.ML_algos.benchmarks train \
  --algo ma_ca_ppo --n_steps 3_000_000 --seed 0 \
  --output optimal_dc/ML_algos/checkpoints/variant_a_ma

# MH baseline (upstream budget 5M steps; v3 forces subsample_rate=1 — the
# upstream 40x compression is deliberately NOT reproduced)
python -m optimal_dc.ML_algos.benchmarks train \
  --algo mh_ma_ca_ppo --n_steps 5_000_000 --seed 0 \
  --output optimal_dc/ML_algos/checkpoints/variant_a_mh
```

## 4. Evaluation

```bash
python -m optimal_dc.ML_algos.benchmarks sanity_eval \
  --checkpoint optimal_dc/ML_algos/checkpoints/variant_a_ma/ma_ca_ppo_final_agent_CDUCAB.pth \
  --n_episodes 5 --max_steps 200
```

This is a SANITY CHECK in the checkpoint's own training-reward units — not the
judged metric (that is evaluation/rollout.py: energy + violations on a fixed
trace). Reports per-agent returns, cabinet temps (warm-up-discarded), and CT
fan power; writes `sanity_eval_results.json` next to the checkpoint. The algo
+ data source come from `metadata.json`, so eval matches training conditions.
Without `--max_steps`, episodes run the config's `max_ep_len` — a full day
(5760 steps, ~25 min each) under the 2026-08-30 protocol. (`eval` still works
as a hidden alias.)

Reference points from the smoke run (rule-based-ish behavior, ÷9 regime, real
day): settled cabinet temps ~45–57 °C. Thermal limits for ÷9 are TBD — set
`t_max_K` after the ÷9 rule-based baseline pass; do NOT reuse the ÷15-era
40 °C figure.

## 5. Loading the shipped sustain-lc weights (optional)

```python
from optimal_dc.ML_algos.benchmarks import build_env_and_agent
env, agent = build_env_and_agent("ma_ca_ppo", {}, "optimal_dc/external/sustain-lc/input_04-07-24.csv", "v3")
agent.load_sustainlc_pretrained(run_num_pretrained=3)   # MA: run 3, MH: run 2
```

Caveat: those weights were trained on v2 ÷15 data — running them on ÷9 input
is out-of-distribution. Use only for plumbing checks, not comparisons.

## 6. Synthetic data source

Any delivered day from `workload_gen_pipeline/synth_data/` is a drop-in CSV:

```bash
# point the config's csv_path at a delivered day, e.g.
#   csv_path: "optimal_dc/workload_gen_pipeline/synth_data/certified_demo.csv"
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `regime_A_calib.json not found` | `python -m optimal_dc.workload_gen_pipeline.calibrate` |
| `No module named yaml` | `pip install pyyaml` in the env |
| >100 °C temps in first steps | FMU init transient (input-independent); `evaluate()` already discards 10 warm-up steps |
| Energy/temps ~3–5× off vs an old run | ÷9 vs ÷15 regime mix — check `metadata.json` / trace sidecars |
