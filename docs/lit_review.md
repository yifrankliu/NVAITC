# Literature Review: Predictive Control for Data Center Cooling
Literature review to analyze existing gaps and what I could work on.

---

## 0. Closest Pieces of Work

1. [Coordinated Cooling and Compute Management for AI Datacenters](https://arxiv.org/html/2601.08113v1)
Joint workload prediction + MPC cooling control with a hierarchical framework. The key differences are that it's air-cooled and targets LLM inference rather than HPC batch jobs, but architecturally closest to what I'm trying to do.

They use LSTM for workload & weather prediction, which is outdated 2015 architecture, fits their problem though.

2. [Digital Twin Cooling Optimization on Frontier](https://arxiv.org/html/2601.02275)
Explicitly calls out weather forecast integration as future work — study to see why they stopped.

Deploys LightGBM and XGBoost via Gradient Boosted Trees.

3. [Phyllis: Physics-Informed Lifelong RL for Data Center Cooling](https://tanrui.github.io/pub/Phyllis-eEnergy23.pdf)
Closest existing paper to the proposed approach. Same problem (DC cooling RL), same physics-informed framing. Uses a learned thermodynamic transition model to supervise safe RL adaptation. Does NOT address liquid-cooled HPC or proactive/forecast-driven control — that is the gap this work fills.

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

### DeepMind Deployed RL for Commercial Cooling (arXiv 2022)
- **Authors:** Luo, Paduraru et al. (DeepMind + Trane Technologies)
- **Key idea:** Live RL deployment at two real commercial buildings in partnership with Trane Technologies. Addresses the full deployment stack: offline data bootstrapping, constraint satisfaction, safe exploration, and evaluation under distribution shift. Candidly documents real-world challenges that lab papers omit.
- **Limitations:** Commercial buildings (not data centers or HPC). Air-cooled HVAC. Reactive — no weather or load forecasting.
- **Result:** ~9% and ~13% energy savings at the two live sites. The widely-cited 40% figure is from an earlier Google DC internal deployment (2016 blog), not this paper.
- **Significance:** The authoritative peer-reviewed paper behind the "DeepMind 40%" result. Defines the deployment challenges any real RL cooling system must solve — constraint satisfaction, offline initialization, evaluation methodology.
- **Links:**
  - [arXiv 2211.07357](https://arxiv.org/abs/2211.07357)
  - [DeepMind blog (40% result)](https://deepmind.google/blog/deepmind-ai-reduces-google-data-centre-cooling-bill-by-40/)

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

## 3. Proactive / Predictive Cooling

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

## 4. Joint Cooling + Compute Control

### Coordinated Cooling and Compute for AI Datacenters (Jan 2026)
- **Authors:** (IEEE Transactions on Cloud Computing)
- **Key idea:** Hierarchical framework: LP resource allocation → MILP LLM scheduling → MPC cooling control. LSTM-based workload predictor + DistilBERT job classifier. Multi-timescale: cluster planning every 30 min, pool scheduling every 5 min, cooling control per minute, DVFS per-job.
- **Limitations:** Air-cooled. LLM inference workloads (not HPC batch jobs). Uses Azure LLM inference traces.
- **Result:** 24.2% per-GPU energy reduction, 31.2% cooling energy savings, 17% decrease in mean GPU temperature.
- **Links:**
  - [arXiv Abstract](https://arxiv.org/abs/2601.08113)
  - [arXiv PDF](https://arxiv.org/pdf/2601.08113)

### TAPAS: Thermal-and-Power-Aware Scheduling (ASPLOS 2025)
- **Key idea:** Thermal-aware workload scheduling for LLM inference in cloud platforms. Tracks GPU temperatures per server and avoids routing to overheating-risk VMs. Enables rack oversubscription by smoothing thermal/power spikes.
- **Limitations:** Reactive (current temperature estimation), not predictive. Cloud LLM inference, not HPC. Air-cooled.
- **Link:** [PDF](https://jovans2.github.io/files/TAPAS_ASPLOS25.pdf)

### Hierarchical Multi-Agent RL for Carbon-Efficient Liquid-Cooled DC Clusters (Feb 2025)
- **Key idea:** Multi-agent RL framework jointly optimizing workload scheduling, liquid cooling setpoints, and carbon intensity across a data center cluster. Hierarchical controller allocates compute across sites while each site's cooling agent optimizes CDU/pump settings. Incorporates real-time carbon grid signal.
- **Limitations:** DC cluster focus (not single HPC system like Frontier). No weather forecasting. Carbon intensity signal, not weather-forecast-driven pre-cooling.
- **Significance:** Closest existing work combining liquid-cooled RL + workload control. Must differentiate: this work addresses single-system predictive control via FMU physics simulation, not multi-site carbon-aware dispatch.
- **Link:** [arXiv 2502.08337](https://arxiv.org/pdf/2502.08337)

---

## 5. HPC-Specific Cooling Optimization

### Energy-Aware Cooling for Hot-Water Cooled Supercomputers (2015)
- **Key idea:** Constrained optimal control for liquid-cooled HPC (Eurora supercomputer). Models when free-cooling (chiller-off) is possible vs when chiller must run. Optimizes inlet cooling water temperature based on environmental and workload conditions.
- **Limitations:** Steady-state analysis only — no transient/predictive dynamics. No weather forecasting. No ML. Assumes job schedulers balance workload (treats it as given).
- **Result:** ~12% cooling energy reduction (3.5 kW on 25 kW nominal).
- **Link:** [ResearchGate](https://www.researchgate.net/publication/300711763_Energy-Aware_Cooling_for_Hot-Water_Cooled_Supercomputers)

### Enhancing Sustainability in Liquid-Cooled Data Centers with RL (NeurIPS 2024 Workshop)
- **Key idea:** Early version of the LC-Opt work. RL control strategies for the same Frontier-class liquid cooling digital twin (HPE/ORNL). Demonstrates centralized RL agents improving operational carbon footprint vs. rule-based baselines. First peer-reviewed RL result on a Frontier-class FMU.
- **Limitations:** Workshop paper — no full multi-agent benchmarking yet. Reactive (no forecasting).
- **Significance:** Direct predecessor to LC-Opt (NeurIPS 2025 main track). Establishes the sustain-lc lineage: 2024 workshop → 2025 main track. Must cite both to accurately represent the baseline.
- **Link:** [Climate Change AI @ NeurIPS 2024](https://www.climatechange.ai/papers/neurips2024/28)

### LC-Opt: RL for Liquid-Cooled HPC (NeurIPS 2025)
- **Key idea:** RL agents controlling cooling tower and blade group MDPs for Frontier supercomputer. FMU compiled from ExaDigiT Modelica model. Gymnasium interface. Two separate MDPs: CT control (minimize fan/pump power) and blade group control (regulate server temps). Also benchmarks agentic LLM-based control and policy distillation into decision trees.
- **Limitations:** **Reactive RL** — agents see current state only, no forecasting. No weather prediction. No workload scheduling integration. Pre-compiled FMU, not open source.
- **Links:**
  - [OpenReview PDF](https://openreview.net/pdf/28b2641d7ee3f811d244578e6b4402a93b25c234.pdf)
  - [HPE sustain-lc GitHub](https://github.com/HewlettPackard/sustain-lc)

---

## 6. Deployed RL at Industrial Scale

### Meta Simulator-Based RL for Data Center Cooling (NeurIPS 2024)
- **Key idea:** Physics-based building simulator (predicts cold-aisle temps within 1°F MAE) used to train RL agent offline, then deploy to production. Simulator takes weather data, IT load, and setpoint schedules as inputs. Trained in simulation, validated against real sensors before live rollout.
- **Limitations:** Air-cooled (supply fan control, not liquid cooling). Single-facility, not HPC. No workload forecasting.
- **Result:** 20% reduction in supply fan energy and 4% reduction in water usage across various weather conditions at a production facility.
- **Significance:** Direct methodological analog to using an FMU for RL training — simulation fidelity → safe deployment. Shows simulator-based RL works at production scale. Validates the sustain-lc FMU-based training strategy.
- **Links:**
  - [OpenReview](https://openreview.net/forum?id=3hZL9Vv0Ay)
  - [Meta Engineering Blog](https://engineering.fb.com/2024/09/10/data-center-engineering/simulator-based-reinforcement-learning-for-data-center-cooling-optimization/)

### Physics-Informed Offline RL for DC Cooling (ICLR 2025)
- **Key idea:** Offline RL framework that encodes physical dependencies via a graph neural network (modeling server room thermal topology). Trained entirely from historical operational data — no simulator required. Deployed in a large-scale commercial DC for production validation (2000+ hours) and a small-scale testbed for ablation.
- **Limitations:** Commercial DC (not HPC). Offline — policy cannot adapt online. No weather or workload forecasting.
- **Result:** 14–21% energy savings validated in production.
- **Significance:** Establishes physics-informed RL as viable at deployment scale. Defines the offline RL paradigm contrast: their approach uses historical data; the FMU-based approach (this work) uses a physics simulator for online interaction — a key differentiator to articulate clearly.
- **Links:**
  - [arXiv 2501.15085](https://arxiv.org/abs/2501.15085)
  - [Project page](https://thu-air-dream.github.io/AIDC/)

---

## 7. Physics-Informed Thermal Dynamics Modeling

### Phyllis: Physics-Informed Lifelong RL for DC Cooling (ACM e-Energy 2023)
- **Key idea:** Two-stage framework: (1) offline, identify a physics transition model that captures data hall thermodynamics (power usage model + residual thermal model); (2) online, use this model to supervise safe data collection, pretrain the RL agent via model interaction, then fine-tune on the live system. Enables safe and fast adaptation when the DC environment changes (e.g., hardware upgrades, layout changes).
- **Limitations:** Air-cooled (CRAC-based) DC, not liquid-cooled HPC. Reactive — no weather or workload forecasting. Transition model is fit to a single DC and does not generalize across systems.
- **Result:** 5.7–13.8% energy savings vs. rule-based feedback control. 8–10× faster adaptation to environment changes with ≤0.74°C temperature overshoot.
- **Significance:** **The single closest existing paper to this work.** Same problem (DC cooling RL) + same physics-informed framing. Extending Phyllis's approach to liquid-cooled HPC with a higher-fidelity physics FMU and a proactive forecasting component is essentially the design brief for this project. If a reviewer asks "how is this different from Phyllis?" the answer must be crisp: liquid cooling, HPC scale, FMU physics, and proactive horizon.
- **Links:**
  - [ACM DL](https://dl.acm.org/doi/10.1145/3575813.3595189)
  - [PDF](https://tanrui.github.io/pub/Phyllis-eEnergy23.pdf)

### Adaptive Physically Consistent Neural Networks for DC Thermal Dynamics (Applied Energy 2025)
- **Key idea:** Physics-consistent neural network (PCNN) for data center thermal dynamics that replaces static preset coefficients with adaptive ones, allowing the model to fit different DC configurations without manual re-tuning. Enforces energy conservation as a hard mathematical constraint (not just a regularization term). Outperforms standard PCNN on both real and simulation DC datasets.
- **Limitations:** Thermal modeling only — no control policy. Air-cooled focus. Does not model hydraulic dynamics (flow rates, pressure) relevant to liquid-cooled systems.
- **Significance:** If a neural surrogate of the FMU is built, this is the architecture to benchmark against for the thermal component. Demonstrates that physics consistency can be enforced *adaptively* — relevant to a model that must generalize across different workload regimes.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0306261924020208)

### Graph Neural ODE Digital Twins for Thermal-Hydraulic Forecasting (arXiv 2026)
- **Key idea:** Physics-informed GNN coupled with a Neural ODE (GNN-ODE) for real-time supervisory control of nuclear reactor coolant loops. Graph nodes = sensors/components; edges = hydraulic connectivity with flow- and heat-transfer-aware message passing. Continuous-time ODE integrator advances latent dynamics between observations. Topology-guided initialization reconstructs temperatures at uninstrumented (unmeasured) nodes from sparse sensors. Pretrained on simulation, then fine-tuned to real experimental facility data with only 30 sequences.
- **Limitations:** Nuclear reactor domain (not DC); partial observability handled via graph initialization heuristic, not a learned inference network. Real-to-sim gap managed by fine-tuning, not zero-shot.
- **Result:** MAE of 0.91 K at 60 s horizon and 2.18 K at 300 s for uninstrumented nodes. 105× faster than simulation on a single GPU, enabling 64-member ensemble rollouts.
- **Significance:** **The most architecturally relevant paper for this project's dynamics model component.** The Frontier cooling system has the same structure — cabinets, CDU heat exchangers, primary loop, cooling tower — as a directed hydraulic graph with uninstrumented internal states (fluid temperatures inside CDU HEX volumes). The GNN-ODE architecture maps directly onto this topology. Key capability: rollouts at 105× real-time means it could support MPC-style planning over a forecast horizon within a control loop.
- **Link:** [arXiv 2604.07292](https://arxiv.org/html/2604.07292v1)

### High Temporal-Resolution HVAC Control in GPU-Centric DCs via RL + PINN (ScienceDirect 2026)
- **Key idea:** Combines RL control policy with a physics-informed neural network thermal surrogate for GPU-dense data centers. PINN encodes heat transfer and airflow PDEs as soft constraints during training. High-resolution (sub-minute) control of supply air temperature and flow for GPU halls.
- **Limitations:** Air-cooled. GPU inference workloads, not HPC batch. No workload forecasting component.
- **Significance:** Validates that RL + PINN is deployable at GPU-dense DC scale (directly comparable to Frontier's GPU hardware), and establishes that sub-minute control granularity is achievable with physics-informed surrogates.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2352710226003207)

---

## 8. World Models and Model-Based RL

### DreamerV3: Mastering Diverse Domains through World Models (Nature 2025)
- **Authors:** Hafner, Lillicrap, Norouzi, Ba
- **Key idea:** General model-based RL algorithm based on a Recurrent State Space Model (RSSM) that learns a compact latent world model from observations and imagines future rollouts entirely in latent space for policy optimization. Single hyperparameter configuration works across 150+ diverse tasks. Key components: symlog predictions, KL balancing with free bits, block GRU, adaptive gradient clipping.
- **Limitations:** Designed for image-based or vector observation spaces — no inductive bias for graph-structured physical systems. Physics is learned implicitly from data, not embedded as constraints. Sample efficiency on real physical systems with slow dynamics (thermal inertia timescales of minutes) is untested.
- **Significance:** **The foundational architecture for the world model direction.** If this project builds a world model, the question must be answered: why not just apply DreamerV3 to the FMU observation vector? The answer is that DreamerV3 has no graph inductive bias and no physics constraints — both of which matter for the multi-component, thermodynamically structured Frontier cooling system.
- **Links:**
  - [arXiv 2301.04104](https://arxiv.org/abs/2301.04104)
  - [Nature](https://www.nature.com/articles/s41586-025-08744-2)

### Graph Dreamer: Temporal Graph World Models for RL (NeurIPS 2025 Workshop)
- **Key idea:** Extends DreamerV3 to graph-structured environments by replacing the RSSM's flat latent state with a latent graph representation. Learns the inherent spatial relationships governing dynamics via graph message passing in latent space, enabling generalization across environments with different topologies and scales (zero-shot transfer to unseen graph sizes). Explicitly targets HVAC control in multi-zone buildings as an evaluation task.
- **Limitations:** Workshop paper — HVAC evaluation results not yet published. Zero-shot transfer benefit depends on sufficient zone connectivity for gradient flow (noted limitation in paper). Does not incorporate physics constraints.
- **Significance:** **The most architecturally aligned world model paper to this project.** The Frontier cooling system is a graph: five cabinet groups → CDU HEX → primary loop → cooling tower. Graph Dreamer's latent graph world model could represent this topology explicitly, unlike flat DreamerV3. If this project takes the world model direction, Graph Dreamer is the primary baseline to compare against.
- **Link:** [OpenReview](https://openreview.net/forum?id=pHmgNUZixd)

### PO-Dreamer: Memory-Guided World Models for Partial Observability (OpenReview)
- **Key idea:** Extends DreamerV3 for partially observable environments (POMDPs) by augmenting the RSSM with an explicit memory module that tracks which parts of the state have been directly observed vs. inferred. Improves latent state estimation under information hiding.
- **Limitations:** General domain; not evaluated on physical systems with structured partial observability (e.g., thermal states hidden inside pipe volumes).
- **Significance:** The Frontier FMU observation vector does not expose internal fluid temperatures inside CDU HEX volumes or pipe segments — the system is a POMDP. A world model for this system must handle partial observability. PO-Dreamer is the relevant extension of DreamerV3 for this case.
- **Link:** [OpenReview](https://openreview.net/pdf/88e81f4f6a4eaf9a77f49bfba4c9a40edf6c159c.pdf)

### HVAC-GRACE: Transferable Building Control via Heterogeneous Graph RL (NeurIPS 2025 Workshop)
- **Key idea:** Graph RL policy that models buildings as heterogeneous graphs (zones as nodes, thermal/airflow connections as edges), integrating spatial message passing directly into GRU gates. Each zone's control action is informed by its own history and its neighbors' states. Achieves zero-shot transfer across buildings with different topologies by learning topology-agnostic message passing functions.
- **Limitations:** Building HVAC (not liquid-cooled HPC). Air-cooled. Zero-shot transfer benefit requires sufficient graph connectivity. No physics-informed constraints.
- **Significance:** Demonstrates graph RL (not just graph dynamics models) for structured thermal systems. The GRU-integrated message passing is directly applicable to the CDU-cabinet graph in Frontier: each CDU cabinet could be a node, with hydraulic edges encoding coolant flow coupling. Relevant if the policy architecture (not just the dynamics model) is graph-structured.
- **Link:** [OpenReview](https://openreview.net/forum?id=8dRnWXy8jq)

---

## 9. Surveys

### Survey on DC Cooling: Technology, Power Modeling, and Control (Jul 2021)
- **Key idea:** Comprehensive survey covering air-cooling, liquid-cooling, and free-cooling technologies. Compares MPC and RL as the two mainstream adaptive control strategies. Reviews data-driven thermal models (SVR, GPR, XGBoost, LightGBM, ANN, LSTM).
- **Relevant finding:** MPC and RL are identified as the two main paradigms, but the survey notes limited work combining physics-based models with ML for control.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1383762121001739)

### RL for Data Center Energy Efficiency: Systematic Literature Review (Applied Energy 2025)
- **Key idea:** PRISMA-protocol systematic review of 65 RL/DRL studies for data center energy efficiency, covering cooling systems (CRAC, chillers, cooling towers) and ICT systems (task scheduling, VM placement, network control). Identifies critical research gaps: lack of real-time validation, absence of multi-scale standardized metrics.
- **Relevant finding:** Gaps identified align directly with the proposed work — validated online RL on a physics simulator, with multi-scale energy metrics (component-level PUE components). More current and comprehensive than the 2021 survey.
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0306261925004647)

### Survey on Physics-Informed Reinforcement Learning (ACM Expert Systems 2025)
- **Key idea:** Comprehensive review of physics-informed RL (PI-RL) approaches across domains: physics as reward shaping, physics as constraints, physics as world model structure, and hybrid approaches. Identifies open problems including partial observability, sim-to-real transfer, and scalability to multi-component physical systems.
- **Relevant finding:** The open problems map directly onto this project's challenges — the FMU is the physics source, but bridging FMU-trained policy to the real Frontier system requires handling the sim-to-real gap. The survey frames the design space for choosing how physics informs the architecture.
- **Link:** [ACM DL](https://dl.acm.org/doi/10.1016/j.eswa.2025.128166)

### GT-SUITE: Digital Twins + MPC for DC Cooling (Mar 2026)
- **Key idea:** Commercial tool (Gamma Technologies) using NARX metamodels trained on physics simulations for MPC. Physics-based simulation → ML surrogate → real-time MPC loop.
- **Relevance:** Validates the architecture pattern of physics model → surrogate → MPC, but as a commercial product, not open research.
- **Link:** [GT-SUITE Blog](https://www.gtisoft.com/blog-post/transforming-data-center-cooling-from-physics-based-simulation-to-ai-powered-control/)

---

## 10. Gap Analysis — Where the Novel Contribution Lives

| Dimension | Existing Work | Proposed Work |
|-----------|--------------|---------------|
| **Cooling type** | Mostly air-cooled (CRAC/AHU) | Liquid-cooled (CDU + cooling tower) |
| **System scale** | Commercial DC or single-rack | Exascale HPC (Frontier-class) |
| **Weather input** | Current measurement or ignored | **Forecast-based** (Towb prediction horizon) |
| **Workload input** | Current load or LLM traces | **HPC job scheduler prediction** (Slurm queue) |
| **Control paradigm** | Reactive RL or short-horizon MPC | **Proactive RL with forecast-informed pre-cooling** |
| **RL paradigm** | Model-free online (LC-Opt), offline from data (ICLR 2025), sim-based air-cooled (Meta) | **Online RL via physics FMU, liquid-cooled HPC** |
| **Physics grounding** | Hard constraints (Adaptive PCNN), soft PINN, or no physics (DreamerV3) | **FMU as ground-truth physics; optional neural surrogate with physics inductive bias** |
| **Dynamics model** | Flat RSSM (DreamerV3), graph RL (HVAC-GRACE), GNN-ODE for reactors | **GNN-ODE or graph world model on CDU/CT hydraulic topology** |
| **Reproducibility** | sustain-lc open (LC-Opt); most others closed | Open FMU + open training pipeline (extends sustain-lc) |

### What nobody has done yet:
1. **Weather forecast → proactive cooling tower setpoint scheduling** for liquid-cooled HPC (explicitly listed as future work in the Frontier digital twin paper)
2. **HPC job queue prediction → anticipatory CDU/pump adjustment** before compute load actually arrives
3. **Combined weather + workload forecasting** feeding a physics-based digital twin within a predictive RL loop for liquid-cooled systems
4. **Online RL with a physics FMU** validated against real Frontier operational data, with proactive horizon

### Architectural Decision Space

The FMU already *is* a world model — it rolls forward in time given actions. The core design question is how physics grounding enters the architecture:

| Approach | Representative Papers | Trade-off |
|---|---|---|
| Use FMU directly for MPC planning | Google NeurIPS 2018, ICLR 2025 offline RL | Physically accurate but CPU-bound; 1-step FMU ~30ms makes lookahead expensive |
| Learn a fast neural surrogate of the FMU | Meta NeurIPS 2024, Adaptive PCNN 2025 | Fast rollouts for planning, but surrogate error compounds over horizon |
| Physics-informed RL (no explicit world model) | Phyllis, ICLR 2025 offline RL | Simpler, proven at DC scale; no planning loop needed |
| Graph world model on FMU topology | Graph Dreamer, HVAC-GRACE, GNN-ODE | Latent graph dynamics with physics inductive bias; plannable in latent space |
| GNN-ODE surrogate of FMU hydraulics | GNN-ODE arXiv 2604.07292 | Strongest physics fit to liquid cooling topology; 105× faster than simulation; enables ensemble rollouts for uncertainty |

**Most defensible novel contribution:** GNN-ODE or graph world model trained on FMU rollout data, with proactive forecasting (weather + workload) as exogenous inputs to the latent dynamics. Not done for liquid-cooled HPC. Supported directly by the hydraulic graph structure of the Frontier FMU. Positions against both Phyllis (no graph, no forecasting) and Graph Dreamer (no physics constraints, no liquid cooling).

---
