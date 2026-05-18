# NVAITC
Optimizing coupled cooling systems for large-scale data centers and supercomputers. Thermal model built on the framework laid by Oakridge National Laboratory's ExaDigit democratized Frontier Supercomputer digital twin project & sustain-lc.

## Current ML Formulation
1. GAT/GINE on the blade-group nodes, which can then be made more granular to chip-wise when a more detailed, customized thermal model can be compiled via exadigit.
2. DeepONet on fluid dynamics/fluid thermal dynamics once we traverse out of the cabinet racks' spatial domain.

## Contents
### 1. cooling_model_workspace
Contains my attempts at constructing a customized super-computer/data center setup using ORNL's exadigit groundwork. However, to successfully compile my own FMU, I would either need a Dymola license (either via institution/paid, both of which I do not have immediate access to), or fix an OpenModelica compiler bug documented in [ticket #13067](https://github.com/OpenModelica/OpenModelica/issues/13067#issuecomment-4477086215).

Currently, moved on to building my initial ML architecture first & testing on the already-compiled sustain-lc FMU.

Will ultimately need to compile a more granular thermal digital model after ML architecture has been built to a certain extent to realize version. Sustain-lc simplifies blade-groups into point-wise temperatures (no gradient), would be best to get temperature gradient on a chip-wise granular model.

### 2. data
Contains helpful data files for training & testing, some are not in there yet.

### 3. docs
Contains all relevant documentation of progress.

### 4. exadigit_analysis
Contains the tracing & analysis of ORNL's exadigit model, including the governing physical equations, assumptions made, and module-wise interactions between the three coolant loops (cold-plate <-> CDU <-> hot water loop/CT loop).

### 5. my_exadigit
A partial clone of the exadigit repo.

### 6. sustain-lc
A clone of Hewit Packet's sustain-lc to use their FMU for initial testing.
