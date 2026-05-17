# User Memory — Claude Context Document
Persistent memory file for Claude sessions. Synced across devices via git. Last updated: May 2026.

---

## Who I Am

- Researcher working on RL-based cooling optimization for the Frontier supercomputer (ORNL)
- Working under faculty advisor Cliff, affiliated with NVAITC
- Running on a Mac (ARM64) as primary machine, Windows as secondary
- Comfortable with ML/RL concepts, Python, git, Docker; learning systems-level HPC infrastructure as the project progresses
- Familiarity with data structures and CS fundamentals (makes analogies to linked lists, trees, pointers naturally)

---

## Project Overview

Goal: develop a novel RL architecture to optimize energy efficiency of Frontier's liquid cooling system, improving on the existing LC-Opt baseline.

The approach sits on top of LC-Opt's FMU simulation environment and aims to directly minimize total facility energy rather than LC-Opt's heuristic temperature proxy.

---

## Codebase Structure

```
NVAITC_files/
├── NVAITC/
│   ├── sustain-lc/              # LC-Opt code + FMU
│   │   ├── LC_Frontier_5Cabinet_4_17_25.fmu
│   │   ├── fmu_extracted/       # unzipped FMU (modelDescription.xml, binaries, docs)
│   │   ├── frontier_env.py      # gymnasium env wrapping FMU
│   │   ├── mh_frontier_env.py   # multi-head variant
│   │   ├── ca_ppo.py            # multi-agent CA-PPO
│   │   └── readme.md            # full obs/action/reward documentation
│   ├── my_exadigit/             # ExaDigiT Modelica source
│   │   ├── ORNLSupercomputing/  # main system model
│   │   ├── TRANSFORM_Library/   # TRANSFORM v1.0 dependency
│   │   └── AutoCSM/             # contains TemplatesCSM (real library — use this, not stub)
│   ├── docs/
│   │   ├── session_may2026.md   # detailed session log with physics notes
│   │   ├── ML_progress.md
│   │   └── digital_twin_progress.md  # TRANSFORM compatibility fix list
│   └── lc-opt-quickstart.ipynb
└── user_memory.md               # this file
```

---

## Current Project Status (May 2026)

| Layer | Status |
|---|---|
| LC-Opt FMU (`LC_Frontier_5Cabinet_4_17_25.fmu`) | Present, runs inside Docker only. Never run to completion (log file is 0 bytes) |
| Docker image (`sustain-lc-env:latest`, 17.2 GB) | Built and verified on local Mac |
| PyFMI in `sustain-lc` conda env | Installed (v2.13.0), fails on Mac ARM64 natively — Docker required |
| `frontier_env.py` | Present — ORNL's LC-Opt gymnasium env |
| PPO training scripts | Present — LC-Opt's multi-agent CA-PPO baseline |
| Own ML architecture | Early formulation stage |
| ExaDigiT OpenModelica compilation | Partially unblocked — stopped mid TRANSFORM compatibility fixes |
| Workload data | sustain-lc CSV only (blade-level, 15s resolution); no ORNL trace yet |

---

## How to Start the FMU (Every Session)

```bash
# Step 1 — on Mac: start Linux container
docker run --platform linux/amd64 -it --rm \
  -v ~/Desktop/NVAITC_files/sustain-lc:/workspace \
  -w /workspace sustain-lc-env:latest bash

# Step 2 — inside container
conda activate sustain-lc

# Step 3 — verify FMU loads
python -c "
from pyfmi import load_fmu
fmu = load_fmu('LC_Frontier_5Cabinet_4_17_25.fmu')
print('Loaded:', fmu.get_name())
"
```

---

## Physical System — Frontier Cooling Architecture

```
CHIP → cold plate (1 per chip, 5 per blade)
BLADE → blade manifold (collects 5 cold plates)
CHASSIS → chassis manifold (2 blades per chassis)
CABINET/RACK → cabinet manifold → CDU heat exchanger (secondary → hot water loop)
CEP (Central Energy Plant) → EHX trains (hot water → cooling tower loop)
ROOFTOP → cooling towers (reject heat to atmosphere via evaporation)
```

Frontier totals: 74 cabinets, ~1,184 blades, ~4,736 GPUs, 74 CDUs.

### Three Cooling Loops
- **Loop 1 — Secondary (deionized water):** cold plates → CDU HEX → back to cold plates
- **Loop 2 — Hot Water (treated water):** CDU HEX → CEP → EHX → back to CDUs
- **Loop 3 — Cooling Tower (open, chemically dosed):** EHX → rooftop cooling towers → back to EHX

Heat exits permanently only at the cooling tower (atmosphere is the ultimate sink).

---

## FMU Details

- **File:** `LC_Frontier_5Cabinet_4_17_25.fmu` — LC-Opt's FMU, NOT ExaDigiT's
- **Tool:** Dymola 2024x, compiled 2025-04-17
- **Scope:** 5-cabinet slice (not full 74 cabinets), 46,452 scalar variables
- **Granularity:** Lumped cabinet model — no chip/blade thermal states; blade power is exogenous CSV input
- **Platform:** linux64/win32/win64 only — Mac ARM64 requires Docker

### FMU Inputs/Outputs

**Actions (26 total):**
- Per CDU ×5: supply temp setpoint (20–40°C), differential pressure setpoint (25–38)
- Per cabinet valve ×5 cabinets ×3 branches = 15 valve positions (0–1)
- Cooling tower ×1: leaving water temp setpoint (discrete, 9 levels)

**Observations:**
- Per cabinet ×5: temperatures at 3 blade branches (K), compute power at 3 blade branches (W)
- Cooling tower: fan power cells 1–2 (W), leaving water temp (K), wet-bulb temp (K)

**Exogenous (uncontrollable):**
- Blade compute power per branch per cabinet (15 values) — from CSV
- Outdoor wet-bulb temperature — from weather data

### LC-Opt Reward (heuristic — key gap to address)
- CDU agents: `(3 - scaled_T_blade_branches.sum()) / 3` — minimize branch temperatures
- CT agent: `(2 - scaled_fan_power.sum()) / 2` — minimize fan power
- **Gap:** proxy reward, not direct minimization of `E = W_CT + W_CTWP + W_HTWP + W_CDUP`

---

## ExaDigiT — Modelica Source

- Full Frontier digital twin (74 cabinets, open source, ORNL)
- Three swappable blade models: `Blade_coldplates.mo` (high fidelity), `Blade_simple_volume.mo` (lumped), `Blade_simple_pipe.mo` (1D pipe)
- Default system model uses lumped cabinet abstraction (blade models not wired in)
- Chip-level granularity requires compiling with `Blade_coldplates.mo`

### OpenModelica Compilation Status
| Blocker | Status |
|---|---|
| TemplatesCSM dependency | Resolved — use `my_exadigit/AutoCSM/methods/modelica/TemplatesCSM/package.mo` |
| TRANSFORM v0.5→v1.0 compatibility | Partially fixed — stopped at `HotWaterLoop/Models/v0.mo` valve arrays |
| OpenModelica compiler bug | Unknown — needs re-test on latest version, especially on Windows |
| Dymola license | Blocked |

**Next action on ExaDigiT:** try Windows machine (OpenModelica better supported on Windows). Load order: TRANSFORM → Buildings v11 → TemplatesCSM → ORNLSupercomputing.

---

## ML Architecture Direction

- Baseline: LC-Opt multi-agent CA-PPO (one agent per cabinet + one CT agent)
- Novel contribution candidates:
  - Direct facility energy minimization (`E = W_CT + W_CTWP + W_HTWP + W_CDUP`)
  - Physics-informed reward shaping using UA table constraints (saturates ~73 kW/K)
  - Spatial field reconstruction: treat 25 CDU outputs as spatial-temporal tensor (25, 7, T)
  - Generalization from 5-cabinet to full 74-cabinet system

---

## Key Contacts

- **Dr. Vineet Kumar** — ORNL, ExaDigiT project lead. Cannot provide pre-compiled FMU or Dymola. Remaining ask: workload trace data, ExaDigiT/LC-Opt relationship
- **Scott Greenwood** — ORNL, filed OpenModelica compiler bug ticket. Contact if Windows compilation still fails
- **Yale Center for Research Computing** — HPC access for native linux64 FMU execution (email sent, pending)
- **Cliff** — Faculty advisor, agreed on research direction

---

## Immediate Next Steps

1. Run FMU end-to-end inside Docker — verify simulation produces output (log currently 0 bytes)
2. Run LC-Opt PPO baseline to establish performance benchmark
3. Obtain ORNL workload trace data (contact Dr. Kumar)
4. Attempt OpenModelica compilation on Windows machine
