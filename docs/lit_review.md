# Literature Review: Predictive Control for Data Center Cooling
Literature review to analyze existing gaps and what I could work on.

---

## 0. Closest pieces of work:
1. [Coordinated Cooling and Compute Management for AI Datacenters](https://arxiv.org/html/2601.08113v1)
Joint workload prediction + MPC cooling control with a hierarchical framework. The key differences are that it's air-cooled and targets LLM inference rather than HPC batch jobs, but architecturally closest to what I'm trying to do.

2. [Digital Twin Cooling Optimization on Frontier](https://arxiv.org/html/2601.02275)
Explicitly calls out weather forecast integration as future work - study to see why they stopped

---

## 1. Seminal Work

### Google MPC for Data Center Cooling (NeurIPS 2018)
- **Authors:** Lazic, Boutilier, Lu, Wong, Roy, Ryu, Imwalle
- **Key idea:** Learned a linear model of DC dynamics via safe random exploration, then used MPC to optimize control actions by predicting trajectories and re-optimizing at each timestep. No prior historical data or physics model required — just a few hours of online learning.
- **Limitations:** Air-cooled (AHUs, not liquid cooling). Treated weather (entering water temperature) and server power as *disturbances* — no forecasting. Linear model only.
- **Result:** Successfully controlled temperatures and airflow in a large-scale commercial DC.
- **Links:**
  - [NeurIPS Proceedings](https://papers.nips.cc/paper/7638-data-center-cooling-using-model-predictive-control)
  - [Full PDF (U of Toronto)](https://www.cs.toronto.edu/~cebly/Papers/DCcooling_with_RL_nips18.pdf)
  - [Google Research](https://research.google/pubs/data-center-cooling-using-model-predictive-control/)

---

## 2. MPC for Air-Cooled Data Centers

### Multi-Chiller MPC with LSTM Prediction (Oct 2024)
- **Key idea:** MPC strategy for multi-chiller data centers using LSTM to predict cooling load and server room temperature. PSO solves for optimal chilled water flow rate and supply temperature per chiller. Considers whole-system energy conservation as a constraint.
- **Limitations:** Air-cooled CRAC systems, not liquid cooling. No weather forecasting. No workload prediction from job scheduler.
- **Result:** 11.81% energy savings over PID, 7.58% over fuzzy control. Better temperature stability.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378778824010351)

### CSA-MPC with Multi-Zone Thermal Coupling (Jun 2025)
- **Key idea:** Cooling supply allocation MPC for CRAC systems considering multi-zone thermal coupling. Uses attention mechanism for multi-zone temperature forecasting.
- **Limitations:** Air-cooled, zone-level control only. No workload or weather integration.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1359431125016953)

### Joint Optimization of Cooling + Workload Distribution (Jan 2025)
- **Key idea:** MPC for joint optimization of cooling parameters and workload distributions, considering server heterogeneity within racks. Compares single-variable vs multivariate control.
- **Limitations:** Air-cooled. Workload "distribution" means spatial placement, not temporal forecasting.
- **Result:** >10% energy savings from joint optimization vs cooling-only control.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2352710225000373)

### Real-Time Thermal Symmetry with Fiber Optic Sensing + MPC (Mar 2026)
- **Key idea:** Distributed fiber optic temperature sensing + hybrid physics/TCN-BiGRU deep learning model for spatiotemporal temperature forecasting. Symmetry-aware MPC controller. QP solved via OSQP for real-time performance.
- **Limitations:** Air-cooled. No workload or weather prediction. Focus is on sensing density, not predictive horizon.
- **Link:** [MDPI Symmetry](https://www.mdpi.com/2073-8994/18/3/398)

---

## 3. Proactive / Predictive Cooling (Closest to Proposed Work)

### Proactive Cooling via LSTM + Digital Twin (Jan 2026)
- **Key idea:** LSTM-based forecasting of temperature and humidity to enable *proactive* rather than *reactive* cooling adjustments. Uses MPC + RTDO principles. Neural network digital twin replaces traditional physics model.
- **Limitations:** Air-cooled. No weather forecast integration (predicts from sensor history only). No workload prediction. Purely data-driven — no physics-informed model.
- **Result:** RMSE of 0.25°C, R² of 0.985 for thermal prediction.
- **Link:** [MDPI Thermo](https://www.mdpi.com/2571-5577/9/1/21)

### Digital Twin Cooling Optimization on Frontier-Class System (Mar 2026)
- **Key idea:** Physics-guided ML framework for identifying cooling energy waste in HPC. Monotonicity-constrained gradient boosting surrogate predicts facility accessory power from coolant flows, temperatures, and server power. Uses one year of 10-minute resolution Frontier operational data.
- **Critical detail:** Explicitly lists **"integration of weather forecasting to enable predictive setpoint scheduling"** as *future work* they have NOT done.
- **Result:** MAE of 0.026 MW, identified ~85 MWh of annual inefficiency.
- **Links:**
  - [arXiv](https://arxiv.org/html/2601.02275)
  - [GitHub](https://github.com/m-iml/ML-Optimization-Data-Centers)

---

## 4. Joint Cooling + Compute Control (AI/LLM Focused)

### Coordinated Cooling and Compute for AI Datacenters (Jan 2026)
- **Authors:** (IEEE Transactions on Cloud Computing)
- **Key idea:** Hierarchical framework: LP resource allocation → MILP LLM scheduling → MPC cooling control. LSTM-based workload predictor + DistilBERT job classifier. Multi-timescale: cluster planning every 30 min, pool scheduling every 5 min, cooling control per minute, DVFS per-job.
- **Limitations:** Air-cooled. LLM inference workloads (not HPC batch jobs). Uses Azure LLM inference traces.
- **Result:** 24.2% per-GPU energy reduction, 31.2% cooling energy savings, 17% decrease in mean GPU temperature.
- **Links:**
  - [arXiv Abstract](https://arxiv.org/abs/2601.08113)
  - [arXiv PDF](https://arxiv.org/pdf/2601.08113)
  - [arXiv HTML](https://arxiv.org/html/2601.08113v1)

### TAPAS: Thermal-and-Power-Aware Scheduling (ASPLOS 2025)
- **Key idea:** Thermal-aware workload scheduling for LLM inference in cloud platforms. Tracks GPU temperatures per server and avoids routing to overheating-risk VMs. Enables rack oversubscription by smoothing thermal/power spikes.
- **Limitations:** Reactive (current temperature estimation), not predictive. Cloud LLM inference, not HPC. Air-cooled.
- **Link:** [PDF](https://jovans2.github.io/files/TAPAS_ASPLOS25.pdf)

---

## 5. HPC-Specific Cooling Optimization

### Energy-Aware Cooling for Hot-Water Cooled Supercomputers (2015)
- **Key idea:** Constrained optimal control for liquid-cooled HPC (Eurora supercomputer). Models when free-cooling (chiller-off) is possible vs when chiller must run. Optimizes inlet cooling water temperature based on environmental and workload conditions.
- **Limitations:** Steady-state analysis only — no transient/predictive dynamics. No weather forecasting. No ML. Assumes job schedulers balance workload (treats it as given).
- **Result:** ~12% cooling energy reduction (3.5 kW on 25 kW nominal).
- **Link:** [ResearchGate](https://www.researchgate.net/publication/300711763_Energy-Aware_Cooling_for_Hot-Water_Cooled_Supercomputers)

### LC-Opt: RL for Liquid-Cooled HPC (NeurIPS 2025)
- **Key idea:** RL agents controlling cooling tower and blade group MDPs for Frontier supercomputer. FMU compiled from ExaDigiT Modelica model. Gymnasium interface. Two separate MDPs: CT control (minimize fan/pump power) and blade group control (regulate server temps).
- **Limitations:** **Reactive RL** — agents see current state only, no forecasting. No weather prediction. No workload scheduling integration. Pre-compiled FMU, not open source.
- **Links:**
  - [OpenReview PDF](https://openreview.net/pdf/28b2641d7ee3f811d244578e6b4402a93b25c234.pdf)
  - [HPE sustain-lc GitHub](https://github.com/HewlettPackard/sustain-lc)

---

## 6. Surveys

### Survey on DC Cooling: Technology, Power Modeling, and Control (Jul 2021)
- **Key idea:** Comprehensive survey covering air-cooling, liquid-cooling, and free-cooling technologies. Compares MPC and RL as the two mainstream adaptive control strategies. Reviews data-driven thermal models (SVR, GPR, XGBoost, LightGBM, ANN, LSTM).
- **Relevant finding:** MPC and RL are identified as the two main paradigms, but the survey notes limited work combining physics-based models with ML for control.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1383762121001739)

### GT-SUITE: Digital Twins + MPC for DC Cooling (Mar 2026)
- **Key idea:** Commercial tool (Gamma Technologies) using NARX metamodels trained on physics simulations for MPC. Physics-based simulation → ML surrogate → real-time MPC loop.
- **Relevance:** Validates the architecture pattern of physics model → surrogate → MPC, but as a commercial product, not open research.
- **Link:** [GT-SUITE Blog](https://www.gtisoft.com/blog-post/transforming-data-center-cooling-from-physics-based-simulation-to-ai-powered-control/)

---

## 7. Gap Analysis — Where the Novel Contribution Lives

| Dimension | Existing Work | Proposed Work |
|-----------|--------------|---------------|
| **Cooling type** | Mostly air-cooled (CRAC/AHU) | Liquid-cooled (CDU + cooling tower) |
| **System scale** | Commercial DC or single-rack | Exascale HPC (Frontier-class) |
| **Weather input** | Current measurement or ignored | **Forecast-based** (Towb prediction horizon) |
| **Workload input** | Current load or LLM traces | **HPC job scheduler prediction** (Slurm queue) |
| **Control paradigm** | Reactive RL or short-horizon MPC | **Proactive MPC with forecast-informed pre-cooling** |
| **Model type** | Pure data-driven OR pure physics | **Physics-informed digital twin + ML surrogate** |
| **Open source** | Mostly closed / commercial FMU | Open (OpenModelica-based) |

### What nobody has done yet:
1. **Weather forecast → proactive cooling tower setpoint scheduling** for liquid-cooled HPC (explicitly listed as future work in the Frontier digital twin paper)
2. **HPC job queue prediction → anticipatory CDU/pump adjustment** before compute load actually arrives
3. **Combined weather + workload forecasting** feeding a physics-based digital twin within an MPC loop for liquid-cooled systems
4. **Open-source, reproducible pipeline** from physics model → surrogate → predictive controller for HPC cooling

---
