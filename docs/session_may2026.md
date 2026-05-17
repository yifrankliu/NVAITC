# Session Log — May 2026
Context document for future Claude sessions. Records key decisions, understanding, and open directions from May 13-16 2026 working sessions.

---

## Project Status Summary

### What exists

| Layer | Status |
|---|---|
| OpenModelica custom model | Partially unblocked — see OpenModelica thread below |
| LC-Opt FMU (`LC_Frontier_5Cabinet_4_17_25.fmu`) | Present in `sustain-lc/`, runs inside Docker only. Never run to completion (log file is 0 bytes) |
| Docker image (`sustain-lc-env:latest`, 17.2 GB) | Built and verified present on local Mac machine |
| PyFMI in `sustain-lc` conda env | Installed (v2.13.0), fails on Mac ARM64 natively — Docker required |
| Gymnasium environment (`frontier_env.py`) | Present — ORNL's LC-Opt code, wraps FMU |
| PPO training scripts | Present — LC-Opt's multi-agent CA-PPO baseline |
| Own ML architecture | Early formulation stage |
| Workload data | sustain-lc CSV (blade-level, 15s resolution); no ORNL workload trace yet |

---

## How to Start the FMU (Every Session)

```bash
# Step 1 — on Mac: start Linux container
docker run --platform linux/amd64 -it --rm \
  -v ~/Desktop/NVAITC_files/sustain-lc:/workspace \
  -w /workspace sustain-lc-env:latest bash

# Step 2 — inside container: activate conda environment
conda activate sustain-lc

# Step 3 — verify FMU loads
python -c "
from pyfmi import load_fmu
fmu = load_fmu('LC_Frontier_5Cabinet_4_17_25.fmu')
print('Loaded:', fmu.get_name())
"

# Step 4 — run the gymnasium environment
python -c "
from frontier_env import SmallFrontierModel
import numpy as np
env = SmallFrontierModel()
obs = env.reset()
action = {
    'cdu-cabinet-1': np.zeros(5),
    'cdu-cabinet-2': np.zeros(5),
    'cdu-cabinet-3': np.zeros(5),
    'cdu-cabinet-4': np.zeros(5),
    'cdu-cabinet-5': np.zeros(5),
    'cooling-tower-1': 4,
}
obs, reward, done, info = env.step(action)
print('Reward:', reward)
"
```

---

## Physical System Understanding

### Frontier Supercomputer Architecture

```
CHIP LEVEL
  Cold plate (one per chip — 1 CPU + 4 GPUs per blade = 5 cold plates per blade)
        ↓ flexible hose
BLADE/NODE LEVEL  (blade and node used interchangeably; 1 blade = 1 node on Frontier)
  Blade manifold (collects 5 cold plates per blade)
        ↓
CHASSIS LEVEL  (chassis = sub-enclosure inside cabinet holding 2 blades + power/network/cooling hub)
  Chassis manifold (collects 2 blades)
        ↓
CABINET/RACK LEVEL  (cabinet and rack used interchangeably; 8 chassis × 2 blades = 16 blades per cabinet)
  Cabinet manifold → CDU heat exchanger (heat handoff: secondary loop → hot water loop)
        ↓ building supply/return headers
CEP (Central Energy Plant — dedicated mechanical room/building housing EHX trains, pump trains, chillers)
  EHX — 4 parallel heat exchanger trains (heat handoff: hot water loop → cooling tower loop)
  Pump trains — 4 parallel pump trains drive hot water loop flow
        ↓ vertical piping
ROOFTOP
  Cooling towers — evaporative cooling rejects heat to atmosphere
```

Frontier totals: 74 cabinets, ~1,184 blades, ~4,736 GPUs, ~5,920 cold plates, 74 CDUs.

---

### Three Cooling Loops

**Loop 1 — Secondary (deionized water)**
- Runs: cold plates → blade manifold → chassis manifold → cabinet manifold → CDU heat exchanger → back to cold plates
- Fluid: fully deionized water (electrically safe, non-corrosive, no ions)
- Purpose: extract chip heat at source

**Loop 2 — Hot Water Loop (treated water)**
- Runs: CDU heat exchanger → building supply headers → CEP → EHX → building return headers → back to CDUs
- Fluid: treated water with corrosion inhibitors (closed loop, not fully deionized)
- Purpose: transport heat across building from CDUs to CEP
- Infrastructure: 4 parallel pump trains, 4 parallel EHX trains (redundancy + partial load efficiency)

**Loop 3 — Cooling Tower Loop (chemically treated open water)**
- Runs: EHX at CEP → vertical piping → rooftop cooling towers → back to EHX
- Fluid: chemically dosed water (open to atmosphere, subject to evaporation/mineral concentration)
- Purpose: reject heat from EHX to outdoor atmosphere via evaporation
- Heat rejection mechanism: primarily evaporative cooling (latent heat), secondarily convection

Heat exits the system permanently only at the cooling tower. Atmosphere is the ultimate sink.

---

### Key Physics Concepts

**CDU Heat Exchanger**
- Type: plate heat exchanger, counter-flow, 5-node discretization
- Counter-flow maximizes temperature difference along entire exchanger length → maximizes heat transfer
- 5 nodes: discretizes spatial temperature profile along flow path; balance of accuracy vs computational cost
- UA (thermal conductance, W/K): governs Q = UA × ΔT
- **UA is a 2D empirical table** — function of BOTH primary and secondary volumetric flow rates
- UA table found in: `my_exadigit/ORNLSupercomputing/Components/SubComponents/Fluid/HeatExchangers/CDU_HEX.mo` line 34
- UA values in table are in kW/K, multiplied by ×1000 at runtime; saturates ~73 kW/K at high flow rates
- UA_corr_mod = 1.2 applied in CDU v0.mo (calibration correction factor)

**Cooling Tower**
- Primary mechanism: evaporative cooling (latent heat) — small fraction of water evaporates, pulling heat from remaining liquid
- Binding constraint: wet-bulb temperature (`Towb`) — tower cannot cool water below outdoor wet-bulb
- ORNL adds 15K offset to wet-bulb to keep system safely above this floor
- Fan power (`CT.PFan`) is the agent's energy cost lever — faster fans = more evaporation = more heat rejection = more electricity

**Cold Plate**
- Copper block pressed directly onto chip surface with thermal paste
- Internal microchannels maximize surface area for convection into coolant
- One cold plate per chip package (~cm scale)
- Chip-to-coolant heat transfer abstracted in FMU as direct boundary condition (Q_flow input from CSV)

**Why loops are separated**
- Pressure isolation: each loop operates at different design pressures
- Contamination: deionized water must not contact mineral-laden or biologically active water
- Operational independence: each loop's flow rate can be tuned independently
- Redundancy and maintenance: trains can be isolated without shutting down facility

---

## FMU Details

### Which FMU is in use
**LC-Opt's FMU** — `LC_Frontier_5Cabinet_4_17_25.fmu`. Confirmed from `modelDescription.xml`:
- `generationTool: Dymola Version 2024x`
- `generationDate: 2025-04-17`
- 46,452 scalar variables total
- This is NOT ExaDigiT's FMU. ExaDigiT has never been compiled.

### What the FMU models
- 5-cabinet slice of Frontier's cooling system (not full 74 cabinets)
- Physics: thermal-hydraulic equations from CDU level upward
- Chip-to-cold-plate heat transfer: abstracted as Q_flow boundary condition — **no chip-level thermal state**
- Compiled with Dymola (commercial), contains linux64/win32/win64 binaries only — no Mac ARM64

### Granularity of LC-Opt's FMU — confirmed from modelDescription.xml
The FMU uses **lumped cabinet model** (SimpleVolume), NOT chip or blade level. Confirmed:
- No chip/GPU/CPU junction temperature state variables exist in the FMU
- No cold plate thermal variables exist
- Blade power IS tracked as separate inputs per cabinet: `ComputePowerBlade1/2/3` per cabinet (3 blades × 5 cabinets = 15 inputs)
- Each blade's power is an **exogenous input** (fed from CSV), not a simulated thermal state
- Cabinet internal variables: only `ccVolCabinet`, `R_Cab`, port_a/b, coolingChannels (lumped fluid volume)

This means LC-Opt's RL agent has no visibility into individual chip temperatures — it only sees cabinet-level coolant temperatures. Whether blade/chip granularity matters for control quality is an open research question requiring experimental validation.

### Relationship between ExaDigiT and LC-Opt
- ExaDigiT: full Modelica source of Frontier digital twin (74 racks, open source, ORNL)
- LC-Opt: separate RL framework with independently compiled 5-cabinet FMU
- Variable naming conventions match closely, suggesting derivation from or heavy inspiration by ExaDigiT
- Exact relationship unclear — confirm with Dr. Kumar (ORNL contact already established)

### ExaDigiT model granularity — from source code analysis
ExaDigiT has THREE blade model implementations (swappable):
1. `Blade_coldplates.mo` — full chip_3D + GPU_3D + CPU_3D + coldPlate (high fidelity, 3D heat conduction in silicon)
2. `Blade_simple_volume.mo` — lumped SimpleVolume + Q_flow (same abstraction as cabinet model)
3. `Blade_simple_pipe.mo` — 1D pipe with Nusselt number convection (intermediate)

Default system simulation uses the lumped cabinet abstraction (skips blade models entirely). High-fidelity chip models exist but are not wired into the default system model. To get chip-level granularity, must compile ExaDigiT with `Blade_coldplates.mo` instantiated.

### FMU Inputs and Outputs

**Controllable actions (26 total):**
- Per cabinet ×5: coolant supply temperature setpoint (20–40°C), differential pressure setpoint (25–38), valve openings for 3 blade branches (0–1)
- Cooling tower ×1: leaving water temperature setpoint (discrete, 9 levels, ±0.20 offset from wet-bulb rule)

**Observations:**
- Per cabinet ×5: temperatures at 3 blade branches (K), compute power at 3 blade branches (W)
- Cooling tower: fan power cells 1-2 (W), leaving water temp (K), wet-bulb temp (K)

**Exogenous inputs (uncontrollable):**
- Blade compute power per branch per cabinet (15 values) — driven by real Frontier workload CSV
- Outdoor wet-bulb temperature — driven by real weather data

### LC-Opt's existing RL implementation
- `frontier_env.py` — gymnasium environment wrapping the FMU
- `ca_ppo.py`, `train_multiagent_ca_ppo.py`, `multihead_ca_ppo.py` — multi-agent PPO
- `MA_CA_PPO_preTrained/`, `MH_MA_CA_PPO_preTrained/` — pre-trained policy weights
- Reward (CDU): `(3 - scaled_T_blade_branches.sum()) / 3` — minimize branch temperatures
- Reward (CT): `(2 - scaled_fan_power.sum()) / 2` — minimize fan power
- Rule-based CT setpoint: `wetbulb + 10.0 * 5/9` — fixed offset, no dynamic optimization
- **Gap**: reward is a heuristic proxy, not direct minimization of total facility energy `E = W_CT + W_CTWP + W_HTWP + W_CDUP`

---

## Open Questions & Future Directions

### Immediate next steps
1. Actually run the FMU end-to-end inside Docker and verify simulation produces output (log file currently 0 bytes — never run to completion)
2. Run LC-Opt's existing PPO baseline to establish performance benchmark
3. Obtain ORNL workload trace data — contact Dr. Kumar; current data is sustain-lc CSV only
4. Attempt OpenModelica compilation on Windows machine (see OpenModelica thread below)

### OpenModelica compiler thread — current state (May 16 2026)

**What is and isn't blocked:**

| Blocker | Status |
|---|---|
| TemplatesCSM private dependency | **RESOLVED** — real library at `my_exadigit/AutoCSM/methods/modelica/TemplatesCSM/package.mo`. Already loaded in OMEdit, symbols appear. Stub library in `my_exadigit/TemplatesCSM/` is outdated and should not be used. |
| TRANSFORM v0.5 → v1.0 compatibility | **Partially fixed, stopped mid-way** — fix list documented in `docs/digital_twin_progress.md`. Fixes are mechanical: add `each` keywords, `constant`→`parameter`, remove `showName`/`iconUnit`, fix array slicing. Stopped at `HotWaterLoop/Models/v0.mo` valve arrays. |
| OpenModelica compiler bug | **Unknown if fixed** — Scott Greenwood filed perost ticket ~2 years ago. perost has made updates since. Not re-tested on latest version. |
| Dymola license | **Blocked** — no fast access path found |
| Pre-compiled ExaDigiT FMU from ORNL | **Blocked** — Dr. Kumar cannot provide one |

**Recommended next action — try Windows machine:**
OpenModelica is primarily developed and tested on Windows. The compiler bug may already be fixed in the latest Windows release even if macOS build lags. Steps:
1. Install latest OpenModelica on Windows (openmodelica.org)
2. Load library stack in OMEdit in this order:
   - TRANSFORM v1.0: `my_exadigit/TRANSFORM_Library/`
   - Buildings v11.0.0: hidden `.openmodelica/libraries/` folder
   - TemplatesCSM: `my_exadigit/AutoCSM/methods/modelica/TemplatesCSM/package.mo`
   - ORNLSupercomputing: `my_exadigit/ORNLSupercomputing/package.mo`
3. Attempt compilation — note which errors remain
4. If compiler bug fixed → resume TRANSFORM compatibility fixes from where they stopped
5. If compiler bug persists → report to Scott Greenwood with new version number

**Why Windows matters:**
Compiling on Windows produces a `win64` binary — loadable with PyFMI directly without Docker. Eliminates entire Linux emulation layer. Can also compile with `Blade_coldplates.mo` instantiated to get blade/chip-level granularity absent from LC-Opt's FMU.

### ML architecture direction
- Current baseline: LC-Opt multi-agent CA-PPO (one agent per cabinet + one cooling tower agent)
- Spatial field reconstruction: treat 25 CDU sensor outputs as spatial-temporal tensor (25, 7, T), reconstruct 2D thermal map via interpolation — documented in `exadigit/spatial_field_feasibility.md`
- Novel contribution candidates:
  - Direct facility energy minimization: `E = W_CT + W_CTWP + W_HTWP + W_CDUP` rather than LC-Opt's heuristic temperature proxy
  - Physics-informed reward shaping using UA table constraints (UA saturates ~73 kW/K — pushing flow beyond saturation wastes energy)
  - Blade/chip-level thermal granularity — requires own ExaDigiT FMU; whether it improves control quality is an open experimental question requiring trials
  - Joint optimization incorporating HVAC coupling (currently ignored — defensible since Frontier is ~95% liquid cooled)
  - Spatial field reconstruction as auxiliary input to RL policy
  - Generalizing from 5-cabinet FMU to full 74-cabinet system

### Known simplifications in current LC-Opt model (gaps to address or acknowledge)
- HVAC system not modeled — Frontier is ~95% liquid cooled so air-side coupling is weak but nonzero
- Chip-to-cold-plate heat transfer abstracted away — no chip junction temperatures, no hot spot detection
- 5-cabinet slice not full facility — generalization to full 74-cabinet system unvalidated
- No workload scheduling — compute load is exogenous input, not a control variable
- York correlation valid only within measured bounds — no extrapolation guarantee in extreme weather
- All 4 cooling towers see identical wet-bulb (single scalar replicated) — spatial variation ignored
- No fouling, degradation, or make-up water modeling

### Data needs
- ORNL workload trace data (direct ask to Dr. Kumar — not yet received)
- Frontier floor layout / CDU coordinates for spatial field reconstruction
- Yale HPC access for native linux64 FMU execution without Docker overhead (email sent, pending)

---

## Plenum & System Architecture (confirmed from Modelica source)

Plenums act as mixing volumes at every scale. Complete hierarchy:

| Level | Plenums | File |
|---|---|---|
| Chip/blade | None — cold plates connect in series | `Blade_coldplates.mo` |
| Cabinet secondary loop | `plenum_inlet_cabinet`, `plenum_outlet_cabinet` | `CoolingBlock/Models/v0.mo` |
| Cabinet primary loop | `plenum_inlet_cdu`, `plenum_outlet_cdu` | `CoolingBlock/Models/v0.mo` |
| Datacenter | `plenum_inlet`, `plenum_outlet` | `Datacenter/Models/v0.mo` |
| Facility top level | `plenum_inlet_datacenter` (150 m³), `plenum_outlet_datacenter` (150 m³) | `Models/v1.mo` |
| Hot Water Loop | `plenum_inlet_a2`, `plenum_outlet_b2` + 3 mixing volumes | `HotWaterLoop/Models/v0.mo` |
| Cooling Tower Loop | `plenum_outlet` + 3 mixing volumes | `CoolingTowerLoop/Models/v0.mo` |

Key naming clarification: in ExaDigiT code, `CoolingBlock` = one physical rack; `cabinet[]` = array of lumped thermal sub-units within that rack. One CDU serves multiple `cabinet[]` instances within one `CoolingBlock`. Do not confuse code `cabinet` with physical rack/cabinet.

---

## Key Contacts
- **Dr. Vineet Kumar** — ORNL, ExaDigiT project lead. Helpful but cannot provide pre-compiled FMU or Dymola access. Key remaining ask: workload trace data, ExaDigiT/LC-Opt relationship clarification
- **Scott Greenwood** — ORNL, filed perost ticket for OpenModelica compiler bug. Contact if Windows compilation still fails on latest OpenModelica version
- **Yale Center for Research Computing** — HPC access for native linux64 FMU execution (email sent, pending response)
- **Cliff** — Faculty advisor, agreed on research direction
