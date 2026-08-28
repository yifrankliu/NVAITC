# workload_gen_pipeline

Frontier workload synthesizer: a job-superposition (marked point process)
generator for per-rack compute power, calibrated to a frozen regime-A spec via
simulation-based inference (MSM/ABC), delivered in FMU-ready formats.

Module names are stable API (imported here and from
`inherited_FMU_with_modifications/`); this file is the stage map — the run
order lives here, not in filename prefixes.

## Stage map

Two kinds of modules: **runnable stages** (have a CLI, run in order) and
**libraries** (only imported; no stage of their own).

### Stage A — spec building (real data → frozen targets, run once)

| Order | Module | Kind | Role |
|---|---|---|---|
| A1 | `envelope.py` | runnable | Full-year Frontier2023 xlsx → `spec/envelope.json`: capacity ceiling (27.70 MW), daily-regime percentiles over operational days, where the calibration day sits (98.8th pct). |
| A2 | `freeze.py` | runnable | Real day CSV (`input_04-07-24.csv`) → `spec/regime_A.json`, computed **through** `validate.compute_stats` so freeze and acceptance share one code path. Reads the capacity ceiling from `envelope.json` when built. |

### Stage B — generative model + calibration

| Order | Module | Kind | Role |
|---|---|---|---|
| — | `config.py` | library | `WorkloadConfig` (the calibration target θ) + `DistSpec`. `regime_A_starting()` seeds θ from the frozen spec. |
| — | `generator.py` | library | The core: `generate(θ)` → (n_steps, 25) watts. Poisson arrivals, FCFS gang scheduling under a capacity constraint, ramp envelopes, shared + idiosyncratic AR(1) wander. Correlation/bimodality/ramps are emergent. |
| — | `validate.py` | library | Summary stats `s(P)` (convention definition), per-trace accept test, MSM distance Q, `validate_ensemble` (N-seed objective), `pass_rate` (ship gate). Also used in stage A: freeze runs through it. |
| B1 | `calibrate.py` | runnable | DE search over 10 shape knobs, CRN ensemble objective, λ re-derived from the mean constraint, out-of-sample ship gate → `spec/regime_A_calib.json`. |

### Stage C — exogenous sourcing + delivery

| Order | Module | Kind | Role |
|---|---|---|---|
| — | `weather.py` | library (self-test CLI) | NOAA LCD v2 wet-bulb for KTYS, cached + manifested. Certified vs the ORNL on-site sensor (bias −0.13 °C, RMSE 0.63 °C). The seasonal axis. |
| — | `disaggregator.py` | library (self-test CLI) | (T, 25) CDU-group watts → (T, 16) FMU exogenous: slice 5 columns, **÷9** (÷3 cabinets × ÷3 branches), fan out, + Towb in K (+15 K offset). Pure pass-through; `self_test()` pins conservation and magnitude. |
| C1 | `deliver.py` | runnable | Generate a day (optional rejection sampling: `--require-pass`, `--mean-band`) and write the three delivery files. |

## Run order (CLI)

```
python -m workload_gen_pipeline.envelope                     # A1 (needs pandas/openpyxl)
python -m workload_gen_pipeline.freeze                       # A2
python -m workload_gen_pipeline.calibrate                    # B1 (needs scipy; ~10-15 min)
python -m workload_gen_pipeline.deliver --seed 0 --require-pass   # C1 → synth_data/
python -m workload_gen_pipeline.weather                      # weather certification self-test
python -m workload_gen_pipeline.disaggregator                # disaggregation self-test
```

## Artifacts

| Path | Written by | Consumed by |
|---|---|---|
| `spec/envelope.json` | envelope | freeze (capacity ceiling) |
| `spec/regime_A.json` | freeze | validate/calibrate/deliver (targets + tolerances) |
| `spec/regime_A_calib.json` | calibrate | deliver (default `--config`) |
| `weather_cache/` | weather | deliver (`--wetbulb noaa:YYYY-MM-DD`) |
| `synth_data/<name>.csv` | deliver | `SmallFrontierModel_v3` (canonical interface; exact real-CSV schema) |
| `synth_data/<name>_exogenous.npy` | deliver | FMU-only harness scripts (bypassing the gym env) |
| `synth_data/<name>_meta.json` | deliver | provenance: config, seed, validation verdict, disaggregation convention |

## Import dependencies (edges to keep in mind when refactoring)

Inside the package: `generator → config`; `freeze → validate`;
`calibrate → config, generator, validate`;
`deliver → config, generator, validate, disaggregator` and **lazily** `weather`
(inside `resolve_wetbulb`, only on `--wetbulb noaa:`).
`envelope` and `weather` are standalone.

Outside the package:
`inherited_FMU_with_modifications/exogenous_generators.py` **lazily** imports
`workload_gen_pipeline.disaggregator.disaggregate` inside
`ExogenousGeneratorV3.__init__` — a rename here breaks env construction at
runtime, not at import time.

## Conventions that must not silently drift

- Disaggregation is **÷9** (÷3 cabinets per CDU group × ÷3 branches). Never
  compare a ÷9 number to a ÷15 (sustain-lc lineage) number.
- Wet-bulb is **sourced** (replay or NOAA), never synthesized.
- The spec is frozen through `validate.compute_stats`; real and synthetic
  traces are always measured by the same code path.
- Calibration reporting: ensemble objective on CRN seeds, ship gate on fresh
  seeds (out-of-sample).
