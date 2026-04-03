# Feasibility of Spatial Field Reconstruction for the ExaDigiT Data Center Digital Twin

**Subject:** Constructing spatial-temporal thermal fields from discrete sensor outputs
**System:** ORNL Frontier Supercomputer — ExaDigiT Modelica Digital Twin
**Scope:** Data center cooling layer (CDU-level and above)

---

## 1. Motivation

The ExaDigiT digital twin produces time-series sensor outputs at each of its 25 Cooling Distribution Units (CDUs), generating per-CDU scalar readings for temperature, pressure, flow rate, and power dissipation. These outputs are inherently 1-dimensional — a time series per sensor node. However, because CDUs occupy fixed, known physical positions on the Frontier data center floor, each scalar reading is implicitly a point observation in 2-D space. The question this report addresses is: **can these discrete 1-D sensor streams be combined with known spatial geometry to reconstruct a continuous spatial-temporal field over the data center?**

The answer is affirmative in principle, with clearly bounded limitations. The following sections characterize the data structure available from the model, the spatial information required from outside the model, the reconstruction methodology, and the conditions under which the resulting field is physically meaningful.

---

## 2. Sensor Inventory and Spatial Structure

### 2.1 Available Sensor Nodes

The model instantiates 25 CDUs as fully independent objects (`cdu[1..25]` in `Systems/Datacenter/Systems/CoolingBlock/Models/v0.mo`). Each CDU exposes the following scalar sensor outputs on the control bus at every simulation timestep:

| Variable | Physical Quantity | Units |
|---|---|---|
| `T_CabSup` | Server coolant supply temperature | °C |
| `T_CabRet` | Server coolant return temperature | °C |
| `Q_CDU` | Heat transferred through CDU heat exchanger | W |
| `m_flow_CDUP` | CDU pump mass flow rate | kg/s |
| `W_CDUP` | CDU pump electrical power | W |
| `p_CabSup` | Server coolant supply pressure | Pa |
| `p_CabRet` | Server coolant return pressure | Pa |

These 7 variables, sampled across 25 spatial nodes over T timesteps, yield a data tensor of shape `(25, 7, T)`. Any single variable — most usefully `T_CabSup` as the primary thermal safety signal — can be treated as a spatial scalar field evolving in time.

### 2.2 Spatial Indexing in the Model

The 25 CDUs are indexed by integer `i ∈ {1, ..., 25}`. The structure records (`Tests/Records/Datacenter/S_Frontier.mo`, `S_DataCenter_Uniform.mo`) define the system hierarchy in terms of **counts only** — number of CDUs, cabinets per block, blades per chassis, etc. No metric coordinates `(x, y)` are assigned to CDU positions within these records. The model is therefore topologically aware (connectivity is encoded) but not geometrically aware (physical distances are not).

This is the missing ingredient for spatial field reconstruction: a mapping from CDU index to floor coordinate.

---

## 3. Reconstruction Methodology

Given a coordinate map `{i → (x_i, y_i)}` derived from the physical data center layout, the reconstruction pipeline is as follows.

### 3.1 Coordinate Assignment

At each CDU index `i`, assign a 2-D floor coordinate based on known rack positions:

```
cdu_coords = { i : (x_i, y_i) }   for i in 1..25
```

For a regular grid arrangement, these coordinates follow a structured pattern (e.g., 5 rows × 5 columns at fixed spacing). For irregular arrangements, coordinates must be sourced from facility blueprints or the ORNL Frontier documentation.

### 3.2 Spatial Interpolation

At each timestep `t`, the 25 scalar readings `{T_CabSup_i(t)}` form a scattered point set over the floor plane. A continuous field is reconstructed by interpolation onto a regular `M × N` grid:

```
grid_T(x, y, t) = Interpolate( {(x_i, y_i, T_i(t))} )
```

Suitable interpolation methods in order of increasing smoothness:

- **Linear triangulation (Delaunay):** Fast, no smoothness assumptions, exact at sensor locations. Appropriate as a baseline.
- **Radial Basis Functions (RBF):** Smooth, handles irregular point sets well. Recommended for visualization.
- **Kriging (Gaussian Process interpolation):** Provides interpolation uncertainty estimates alongside the field estimate. Recommended if spatial covariance structure is known or learnable from simulation data.

The output is a spatial-temporal tensor of shape `(M, N, T)` — a thermal map of the data center floor evolving over time.

### 3.3 Physical Priors Available for Regularization

The physics of the system provide regularization constraints that can improve reconstruction quality, particularly in under-sampled regions:

- **Thermal diffusion smoothness:** Temperature fields in liquid-cooled systems are spatially smooth at the floor scale. Sharp discontinuities between adjacent CDUs are physically implausible unless there is a documented boundary in the cooling circuit topology.
- **Hydraulic symmetry:** CDUs within the same cooling block share a common supply/return plenum. CDUs connected to the same plenum are expected to have correlated thermal states, providing a graph-structured covariance prior.
- **Energy balance constraint:** The sum of `Q_CDU` across all 25 CDUs must equal the total facility heat load `Q_flow` injected via the control bus. This global conservation law constrains the spatial field integral.

---

## 4. Limitations

### 4.1 Uniform Heat Load (Current Model)

The most significant practical limitation is that the current model broadcasts a **single scalar `Q_flow`** to all 25 CDUs simultaneously via the control bus (`Cabinet/Models/v0.mo`, line 348). This means all CDUs are thermally driven identically. Under this configuration, spatial variation in `T_CabSup` across CDUs arises only from hydraulic imbalance — differences in local flow resistance or valve state — and is expected to be small. The reconstructed spatial field will be nearly flat, and spatial reconstruction adds limited value.

This is a model configuration choice, not a structural limitation. The fix is targeted: the `Q_flow` connection in `CoolingBlock/Models/v0.mo` must be changed from a scalar broadcast to a per-CDU array input, enabling spatially heterogeneous workload injection. This change is confined to one connection statement and an update to the control bus type definition.

### 4.2 Lumped Cabinet Model

Each CDU's cabinet is modeled as a single well-mixed fluid volume (`Systems/Datacenter/Systems/CoolingBlock/Systems/Cabinet/Models/v0.mo`). The model has one temperature node per cabinet — all blades within a cabinet are thermally indistinguishable. Sub-CDU spatial resolution (blade-level or rack-unit-level) is therefore unavailable without restructuring the cabinet model, which would require non-trivial changes to the component hierarchy.

### 4.3 Chip-Level Spatial Resolution

The chip thermal model (`chip_3D.mo`) supports a 3-D conduction mesh parameterized by `(nX, nY, nZ)`, defaulting to `(1, 1, 1)`. Setting these parameters greater than 1 produces spatially resolved intra-chip temperature gradients at centimeter scale. However, this spatial information does not propagate upward through the hierarchy — the cabinet above still receives a single aggregated `Q_flow` scalar. Furthermore, the computational cost of un-lumping the chip model at full system scale is prohibitive: at `nX=nY=nZ=3`, the 76,800 chips in the full Frontier model would require approximately 2 million coupled thermal nodes, increasing solver time by an estimated 10–30×.

Chip-level un-lumping is therefore suitable only for targeted single-blade or single-CDU studies, not for system-scale spatial field reconstruction.

### 4.4 No Spatial Variation in Environmental Boundary Conditions

Ambient wet bulb temperature (`Towb`) is a single scalar replicated identically to all 4 cooling towers via a `Replicator` component (`CoolingTowerLoop/Models/v0.mo`). There is no spatial weather field over the site. Spatial variation in heat rejection capacity across the cooling tower array is therefore absent from the current model.

---

## 5. Summary of Requirements for Full Spatial Reconstruction

| Requirement | Source | Status |
|---|---|---|
| Per-CDU sensor time series (`T_CabSup`, `Q_CDU`, etc.) | Model output — already disaggregated across `cdu[1..25]` | Available |
| Physical `(x, y)` coordinates per CDU | Facility blueprints or ORNL Frontier layout documentation | **External — must be supplied** |
| Spatial interpolation implementation | Python (`scipy.interpolate`, `sklearn`, `PyKrige`) | Straightforward post-processing |
| Per-CDU independent `Q_flow` inputs | One connection change in `CoolingBlock/Models/v0.mo` | **Small model modification required for meaningful spatial variation** |
| Sub-CDU (blade/chip) spatial resolution | Structural refactoring of cabinet model | Not recommended — high cost, low return at facility scale |

---

## 6. Conclusion

Spatial-temporal field reconstruction over the Frontier data center floor is feasible using existing model outputs, provided that physical CDU coordinates are supplied externally and that the heat load input is made spatially heterogeneous per CDU. The reconstruction pipeline — coordinate assignment, scattered-point interpolation, and optional physics-informed regularization — is implementable entirely in Python as a post-processing layer, requiring no structural changes to the Modelica model beyond the single `Q_flow` broadcast-to-array modification.

The resulting spatial field, at 25 sensor nodes, yields a coarse but physically grounded thermal map of the facility. Its primary utility is in identifying spatial hot spot patterns, validating hydraulic balance across the CDU array, and providing spatial context for surrogate model training or reinforcement learning reward shaping. Higher spatial resolution within individual CDUs is structurally inaccessible at the cabinet level under the current model architecture.

---

*Codebase: ORNL ExaDigiT (`my_exadigit`) | Reference: LC-Opt (NeurIPS 2025)*
