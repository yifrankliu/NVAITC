# Sustain-LC FMU Physical Analysis
**Reference:** `LC_Frontier_5Cabinet_4_17_25.fmu` · `frontier_env.py` · `datacenterCoolingModel` Modelica sources · ExaDigiT documentation  
**Date:** 2026-05-18

---

## 1. Overview

The pre-built FMU is a compiled snapshot of a subset of the ExaDigiT digital twin for ORNL's Frontier supercomputer. It models the liquid cooling system as a co-simulation FMU (FMI 2.0), interfaced to a Gymnasium RL environment via PyFMI.

**Scope of the FMU:**
- 5 CDU-cabinet pairs (Frontier has ~74 total)
- 3 blade groups per cabinet (15 blade groups total)
- 1 cooling tower with 4 cells
- Does NOT model: per-chip thermal resistance, HRU/hot water loop in detail, inter-cabinet coolant coupling

**What is simplified relative to full ExaDigiT:**
- Blade groups are lumped thermal masses (not per-blade or per-chip)
- Cabinets are treated as hydraulically independent (no shared HTW manifold dynamics)
- Cooling tower is a York-correlation model, not a full CFD/film model

---

## 2. System Hierarchy

```
simulator[1]
├── datacenter[1]
│   └── computeBlock[1..5]  (5 CoolingBlocks in sustain-lc, 25 in full Frontier config)
│       ├── cdu[1]           (1 CDU per compute block)
│       └── cabinet[1..3]    (3 parallel cabinets per compute block, 3 blade groups each)
└── centralEnergyPlant[1]
    └── coolingTowerLoop[1]
        └── coolingTower[1]  (4 cells in parallel)
```

Each `computeBlock` models one CDU serving three parallel cabinets. The CDU connects to a facility hot water loop (primary side) and distributes cooled fluid to the cabinets (secondary side).

---

## 3. Blade Group & Cabinet Level

### 3.1 Physical Interpretation

A **blade group** is a lumped thermal aggregation of ~5–6 physical blades sharing one coolant branch in the CDU secondary loop. Each cabinet has 3 blade groups, each with its own coolant branch port (`boundary_1`, `boundary_2`, `boundary_3`).

### 3.2 Governing Equations

**Heat capacitor (blade group thermal dynamics):**

$$C \frac{dT}{dt} = Q_{\text{port}}(t)$$

where $T$ is blade group temperature (K), $C$ is thermal capacitance (J/K), and $Q_{\text{port}} = P_{\text{branch}}$ is the server compute power (W).

**Cooling plate conduction (solid → fluid heat transfer):**

$$Q_{\text{flow}} = G_c \left( T_{\text{solid}} - T_{\text{fluid}} \right)$$

where $G_c$ is convective conductance (W/K), a function of coolant mass flow rate $\dot{m}$ and fluid properties.

**Overall energy balance with nonlinearity:**

$$\Phi(Q_{\text{port}}) + Q_{\text{flow}} = C \frac{dT_{\text{server}}}{dt}$$

$\Phi(\cdot)$ is a polynomial fit (quadratic coefficient 0.015, linear coefficient 1) added to expose nonlinearity for RL vs. heuristic controller comparison.

### 3.3 Cabinet Fluid Model Parameters

| Parameter | Value | Units |
|---|---|---|
| Coolant volume | 0.0827 | m³ (21.9 US gal) |
| Hydraulic resistance | 11,000 | Pa·s/kg |
| Resistance split | 50/50 | inlet / outlet |
| Heat input variable | `Q_flow_total` | W (exogenous) |

### 3.4 Assumptions

1. Each blade group is a single lumped thermal node — no spatial temperature gradient within the group
2. Convective conductance $G_c$ varies with flow rate but uses a simplified linear relation
3. Polynomial nonlinearity $\Phi$ is a calibration fit, not derived from first principles
4. Cabinets are hydraulically parallel — equal pressure drop, no cross-coupling
5. No heat loss to environment (perfect insulation assumed)

---

## 4. CDU Level

### 4.1 Architecture

Each CDU sits between the facility hot water loop (primary) and the cabinet coolant loop (secondary). It contains:
- A counter-current plate heat exchanger (CDU_HEX)
- A pump train (CDUP) with 2 parallel units on the secondary side
- A linear control valve on the primary (HTW) side
- An expansion tank to maintain secondary loop pressure
- A cascaded PID control system

### 4.2 Heat Exchanger (CDU_HEX)

Model type: `Simple_ITD_HX` — counter-current heat exchanger with $n_V = 5$ lumped volumes per side.

**Heat duty:**

$$\dot{Q}_{\text{HEX}} = UA \cdot \Delta T_{\text{lm}}$$

**Log-mean temperature difference (counter-flow):**

$$\Delta T_{\text{lm}} = \frac{(T_{h,\text{in}} - T_{c,\text{out}}) - (T_{h,\text{out}} - T_{c,\text{in}})}{\ln\left(\dfrac{T_{h,\text{in}} - T_{c,\text{out}}}{T_{h,\text{out}} - T_{c,\text{in}}}\right)}$$

**UA lookup table:** 2D function of primary and secondary volumetric flow rates.

| Parameter | Value | Units |
|---|---|---|
| Volume per side | 0.051 | m³ |
| Number of segments $n_V$ | 5 | — |
| UA range | 1,870 – 73,890 | W/K |
| UA correction modifier | 1.2 | — |
| Primary flow range | 0.00126 – 0.0227 | m³/s |
| Secondary flow range | 0.001 – 0.0227 | m³/s |
| Primary hydraulic resistance | 8,000 | Pa·s/kg |
| Secondary hydraulic resistance | 11,000 | Pa·s/kg |

**Initial conditions:**

| Side | $T_{\text{supply}}$ | $T_{\text{return}}$ | $\dot{m}$ | $p_{\text{supply}}$ |
|---|---|---|---|---|
| Primary (HTW) | 22.5°C (295.65 K) | 35°C (308.15 K) | 12 kg/s | 549 kPa |
| Secondary (cabinet) | 30°C (303.15 K) | 40°C (313.15 K) | 15 kg/s | 446 kPa |

### 4.3 CDU Pump (CDUP)

Two parallel identical centrifugal pumps on the secondary loop.

**Power equation:**

$$P_{\text{pump}} = \frac{\Delta p \cdot \dot{m}}{\eta \cdot n_{\text{parallel}}}$$

| Parameter | Value | Units |
|---|---|---|
| Units in parallel | 2 | — |
| Nominal speed | 3500 | RPM |
| Nominal flow per unit | 7.5 | kg/s |
| Nominal pressure rise | 100,000 | Pa |
| Efficiency $\eta$ | 0.85 | — |
| Speed control range | 52 – 75 | % of nominal |

Flow characteristic: CombiTableCurve (pressure rise vs. flow rate, lookup table).

### 4.4 Control Valve (valveCDU)

Linear valve on the primary (HTW) side, modulating primary flow to regulate secondary supply temperature.

| Parameter | Value | Units |
|---|---|---|
| Type | Linear | — |
| Nominal $\Delta p$ | 50,000 | Pa |
| Nominal $\dot{m}$ | 11 | kg/s |
| Opening range | 0.05 – 1.0 | — |

### 4.5 Expansion Tank

Maintains constant pressure on secondary loop.

| Parameter | Value | Units |
|---|---|---|
| Volume | 0.1 | m³ |
| Cross-sectional area | $\pi \times 0.02^2 = 0.001256$ | m² |
| Initial level | 0.3 | m |
| Pressure | 210,264 (30.5 psi) | Pa |

### 4.6 CDU Control System (CS_PumpAndValveControl)

Cascaded PID controllers:

| Controller | Controlled variable | Setpoint | $k$ | $T_i$ (s) | $T_d$ (s) |
|---|---|---|---|---|---|
| CDUP pump | Secondary $\Delta p$ | 27.5 psi (189,629 Pa) | 0.1 | 100 | 30 |
| CDU valve | Secondary supply $T$ | 28°C (301.15 K) | −0.9 | 35 | 9 |

Valve control includes deadband: $\pm 0.3$°C (ratio 0.1).

**RL override:** The RL agent provides setpoint signals that override the base controller setpoints for pump speed and supply temperature.

### 4.7 Assumptions

1. Counter-current HEX with uniform UA valid for off-design within ±20% of nominal flow
2. Coolant properties (density, specific heat, viscosity) constant at nominal state values
3. Hydraulic resistance concentrated at inlet/outlet; negligible within volumes
4. Pump speed directly follows input signal (no mechanical lag modeled)
5. No cavitation, two-phase flow, or thermal stratification
6. Expansion tank maintains perfect constant pressure (isothermal)
7. No CDU heat loss to ambient

---

## 5. Cooling Tower Level

### 5.1 Architecture

One cooling tower system with 4 parallel cells, each independently controlled. Each cell has:
- A linear control valve (opening signal)
- A York-correlation tower model (`coolingTower_Towb`)
- A LimPID fan controller

Shared inlet/outlet plenums (mixing volumes, $V = 1$ m³ each) connect all cells.

### 5.2 Governing Equations

**Mass continuity (no bleed/blow-down):**

$$\dot{m}_{w,\text{in}} = \dot{m}_{w,\text{out}} = \dot{m}_w$$

**Energy balance:**

$$\dot{m}_w c_{p,w} (T_{w,\text{in}} - T_{w,\text{out}}) = Q_{\text{tower}}$$

where $c_{p,w} \approx 4{,}184$ J/(kg·K).

**Overall heat transfer:**

$$Q_{\text{tower}} = UA \cdot \Delta T_{\text{lm}}$$

**Log-mean temperature difference (counter-flow, wet-bulb as air temperature):**

$$\Delta T_{\text{lm}} = \frac{(T_{w,\text{out}} - T_{a,\text{in}}) - (T_{w,\text{in}} - T_{a,\text{out}})}{\ln\left(\dfrac{T_{w,\text{out}} - T_{a,\text{in}}}{T_{w,\text{in}} - T_{a,\text{out}}}\right)}$$

**York correlation (approach temperature, off-design):**

$$T_{\text{App,act}} = \text{yorkCalc}(T_{\text{Ran}},\, T_{\text{wb}},\, FR_w,\, FR_a)$$

where:
- $T_{\text{App}} = T_{w,\text{out}} - T_{\text{wb}}$ (approach temperature, K)
- $T_{\text{Ran}} = T_{w,\text{in}} - T_{w,\text{out}}$ (range, K)
- $FR_w = \dot{m}_w / \dot{m}_{w,\text{nom}}$ (fractional water flow)
- $FR_a = y$ (fan control signal, fractional air flow)

**Free convection mode** (when fan off, $y < 0.9 \cdot y_{\min}$):

$$T_{\text{App,FreeConv}} = (1 - f_{\text{fc}}) \Delta T_{\max} + f_{\text{fc}} \cdot \text{yorkCalc}(T_{\text{Ran}},\, T_{\text{wb}},\, FR_w,\, 1)$$

where $\Delta T_{\max} = T_{w,\text{in}} - T_{\text{wb}}$.

**Evaporative mass loss:**

$$\dot{m}_{\text{evap}} = \frac{Q_{\text{tower}}}{h_{fg}}, \quad h_{fg} \approx 2.26 \times 10^6 \text{ J/kg}$$

**Fan power (forced convection):**

$$P_{\text{fan}} = f_{\text{relPow}}(y) \cdot P_{\text{fan,nom}}, \quad f_{\text{relPow}}(y) = y^3 \text{ (cubic law)}$$

In free convection mode: $P_{\text{fan}} = 0$.

### 5.3 Cooling Tower Cell Parameters

| Parameter | Value | Units |
|---|---|---|
| Number of cells | 4 | — |
| Design approach temperature | 3.89 | K |
| Design range temperature | 5.56 | K |
| Nominal water flow per cell | 62.82 | kg/s |
| Nominal fan power per cell | 37,285 | W |
| Nominal pressure drop | 19,995 | Pa |
| Plenum inlet volume | 1.0 | m³ |
| Plenum outlet volume | 1.0 | m³ |

**Fan PID controller (per cell):**

| Parameter | Value |
|---|---|
| Gain $k$ | 1.0 |
| Integral time $T_i$ | 60 s |
| Derivative time $T_d$ | 10 s |
| Reverse acting | false |

### 5.4 RL Agent Interaction

The RL agent provides a discrete action (9 states) that adjusts the cooling tower water leaving temperature setpoint relative to a rule-based baseline:

| Action | $\Delta T$ (K) |
|---|---|
| 0 | −0.20 |
| 1 | −0.15 |
| 2 | −0.10 |
| 3 | −0.05 |
| 4 | 0.00 |
| 5 | +0.05 |
| 6 | +0.10 |
| 7 | +0.15 |
| 8 | +0.20 |

Base setpoint: $T_{\text{CT,set}} = T_{\text{wb}} + 10 \times (5/9) + \Delta T_{\text{action}}$

### 5.5 Assumptions

1. York correlation valid within ±20% of nominal design point
2. Steady-state water/air contact at each timestep — no dynamic accumulation in fill media
3. All 4 cells are identical; differences arise only from control signals
4. Fan power follows cubic law ($y^3$) — standard fan affinity approximation
5. Evaporative makeup water not tracked; mass conservation assumed
6. Wet-bulb temperature is an exogenous input — not computed from humidity model
7. Smooth interpolation between forced and free convection modes

---

## 6. RL Environment Interface

### 6.1 Observation Space

All observations normalized to $[-1, 1]$ via:

$$x_{\text{norm}} = 2 \cdot \frac{x - x_{\min}}{x_{\max} - x_{\min}} - 1$$

**Per CDU-cabinet pair (5 pairs × 6 variables = 30):**

| Variable | FMU variable name | Range (raw) | Units |
|---|---|---|---|
| Blade group 1 temp | `boundary_1.port.T` | 273.15 – 373.15 | K |
| Blade group 2 temp | `boundary_2.port.T` | 273.15 – 373.15 | K |
| Blade group 3 temp | `boundary_3.port.T` | 273.15 – 373.15 | K |
| Blade group 1 power | `ComputePowerBlade1` | 0 – 340,000 | W |
| Blade group 2 power | `ComputePowerBlade2` | 0 – 340,000 | W |
| Blade group 3 power | `ComputePowerBlade3` | 0 – 340,000 | W |

**Cooling tower (1 × 4 variables = 4):**

| Variable | FMU variable name | Range (raw) | Units |
|---|---|---|---|
| Cell 1 fan power | `coolingTower[1].cell[1].CT.PFan` | 0 – 37,285 | W |
| Cell 2 fan power | `coolingTower[1].cell[2].CT.PFan` | 0 – 37,285 | W |
| Water leaving setpoint | `waterSPTLvg` | 273.15 – 373.15 | K |
| Outside wet-bulb temp | `Towb` | 270.15 – 373.15 | K |

**Total observation dimension: 34** (5 × 6 + 4)

### 6.2 Action Space

**Per CDU-cabinet pair (5 × 5 continuous = 25):** `spaces.Box(low=-1, high=1, shape=(5,))`

| Action | FMU variable | Physical mapping | Range (physical) |
|---|---|---|---|
| Supply temp setpoint | `Tsec_supply_nom_RL` | $T_{\text{supply}} = 20 + 10(a+1)$ → setpoint for `PID_CDUCV`, which actuates `valveCDU` (primary side) | 20 – 40°C |
| Pressure differential | `dp_nom_RL` | $\Delta p = 25 + 6.5(a+1)$ → setpoint for `PID_CDUP`, which sets pump speed `CDUP_Nrel` | 25 – 38 psi |
| Valve 1 (blade group 1) | `Valve_Stpts[1]` | Direct branch flow fraction (softmax with valves 2 & 3, sum = 1) | 0 – 1 |
| Valve 2 (blade group 2) | `Valve_Stpts[2]` | Direct branch flow fraction (softmax with valves 1 & 3, sum = 1) | 0 – 1 |
| Valve 3 (blade group 3) | `Valve_Stpts[3]` | Direct branch flow fraction (softmax with valves 1 & 2, sum = 1) | 0 – 1 |

Note: supply temp and ΔP are **indirect** (setpoints fed into PIDs). Valve fractions are **direct** (set without a PID intermediary). `Valve_Stpts` are FMU-specific additions not present in the upstream ExaDigiT Modelica source.

**Cooling tower (1 discrete = 1):** `spaces.Discrete(9)`

| Action index | $\Delta T$ (K) | FMU variable | Physical mapping |
|---|---|---|---|
| 0 | −0.20 | `CT_RL_stpt` | Setpoint for CT fan PID; CT fan PID adjusts all 4 cell fan speeds to hit the leaving water temperature |
| 1 | −0.15 | | |
| 2 | −0.10 | | |
| 3 | −0.05 | | |
| 4 | 0.00 | | Rule-based baseline: $T_{\text{CT,set}} = T_{\text{wb}} + 5.556\text{K}$ |
| 5 | +0.05 | | |
| 6 | +0.10 | | |
| 7 | +0.15 | | |
| 8 | +0.20 | | |

CT setpoint is always relative: $T_{\text{CT,set}} = T_{\text{wb}} + 5.556\text{K} + \Delta T_{\text{action}}$. Like the CDU, the fan speed is **indirect** — the CT fan PID actuates fan speed; you only command the water leaving temperature setpoint.

### 6.3 Exogenous Inputs (Not Controlled)

| Variable | Description | Update frequency |
|---|---|---|
| `ComputePowerBlade[1/2/3]` | Per-blade-group compute power | Every agent step (15s) |
| `Towb` | Outside air wet-bulb temperature | Every agent step (15s) |

These are read from a pre-recorded workload trace CSV (`input_04-07-24.csv`) and fed into the FMU at each step.

### 6.4 Reward Functions

Three shaping variants are implemented:

**v0 — Temperature minimization (per cabinet):**

$$R_{\text{cab}}^{v0} = \frac{3 - \sum_{j=1}^{3} T_{\text{norm},j}}{3}$$

**Cooling tower reward:**

$$R_{\text{CT}} = \frac{2 - \sum_{j=1}^{2} P_{\text{fan,norm},j}}{2}$$

**v1 — Valve-power balancing (per cabinet):**

$$R_{\text{cab}}^{v1} = 6 - \sum_{j=1}^{3} |a_{\text{valve},j} - P_{\text{norm},j}|$$

Rewards matching valve openings to proportional blade group power demands.

**v2 — Combined (default):**

$$R_{\text{cab}}^{v2} = 1.0 \cdot R_{\text{cab}}^{v1} + 3.0 \cdot R_{\text{cab}}^{v0}$$

Temperature reduction weighted 3× over load balancing.

---

## 7. Simulation Numerics

| Parameter | Value | Notes |
|---|---|---|
| FMI version | 2.0 | Co-simulation type |
| Agent step size | 15 s | Time between RL decisions |
| FMU internal solver | DASSL (implied) | Differential-algebraic |
| FMU tolerance | FMU default | Set at Dymola compile time |
| Episode horizon | configurable | Typically 24 hours = 5,760 steps |
| do_step calls per agent step | `step_size / sim_time_step` | ~1–15 internal steps |

**Data preprocessing pipeline (before FMU input):**
1. Load outlier clipping: cap at mean ± threshold (0.1–1.75 std)
2. Wet-bulb offset: $T_{\text{wb}} + 15$ K to prevent tower saturation
3. Moving average smoothing: 50-sample kernel
4. Staggered flow profiles via `numpy.roll` shifts per blade group (mimics asynchronous operation)

---

## 8. Key Limitations Relative to Full ExaDigiT

| Aspect | Sustain-LC FMU | Full ExaDigiT |
|---|---|---|
| Number of cabinets | 5 | ~74 |
| Blade resolution | 3 lumped groups/cabinet | Per-blade (possible) |
| Chip resolution | Not modeled | Not modeled (ExaDigiT default) |
| Hot water loop | Not exposed to RL | Full HotWaterLoop modeled |
| Inter-cabinet coupling | None (hydraulically independent) | Shared manifold dynamics |
| Cooling tower | 4-cell York correlation | Same |
| Workload data | Pre-recorded 15s CSV trace | Real telemetry or SST-Macro |
| FMU solver control | Fixed at compile time | Configurable in Dymola |

---

## 9. Sources

| Source | Path |
|---|---|
| Blade group & CDU docs | `sustain-lc/docs/_sources/modeling/blade_group_modeling.rst.txt` |
| Cooling tower docs | `sustain-lc/docs/_sources/modeling/cooling_tower.rst.txt` |
| Environment docs | `sustain-lc/docs/_sources/environment.rst.txt` |
| RL environment code | `sustain-lc/frontier_env.py` |
| Cabinet Modelica model | `datacenterCoolingModel/ORNLSupercomputing/.../Cabinet/Models/v0.mo` |
| CDU Modelica model | `datacenterCoolingModel/ORNLSupercomputing/.../CDU/Models/v0.mo` |
| CDU HEX model | `datacenterCoolingModel/.../HeatExchangers/CDU_HEX.mo` |
| CDU pump model | `datacenterCoolingModel/.../Pumps/CDUP.mo` |
| CDU controls | `datacenterCoolingModel/.../CDU/Controls/CS_PumpAndValveControl.mo` |
| Cooling tower model | `datacenterCoolingModel/.../CoolingTower.mo` |
| York calculation | `datacenterCoolingModel/.../CoolingTowers/BaseClasses/YorkCalc.mo` |
| Frontier topology JSON | `datacenterCoolingModel/python/data/input_specification_frontier_test.json` |
