# NVAITC
Optimizing coupled cooling systems for large-scale data centers and supercomputers. Going beyond basic reactive controllers and implementing proactive cooling with added predictive consideration to exogenous weather/environmental variables & workload scheduling. Thermal model built on the framework laid by Oakridge National Laboratory's ExaDigit democratized Frontier Supercomputer digital twin project & sustain-lc.


## Contents
### 1. optimal_dc
All of current progress. workload_gen is the synthetical workload data generator pipeline, ingested into the inherited FMU after some modifications, use to train baseline and own ML algorithms in ML_algos, evaluated in evaluation.

### 2. data
Contains helpful data files for training & testing, some are not in there yet.

### 3. docs
Contains all relevant documentation of project progress.

### 4. exadigit_analysis
Contains the tracing & analysis of ORNL's exadigit model, including the governing physical equations, assumptions made, and module-wise interactions between the three coolant loops (cold-plate <-> CDU <-> hot water loop/CT loop).

### 5. my_exadigit
A partial clone of the exadigit repo.

### 6. sustain-lc
A clone of Hewit Packet's sustain-lc to use their FMU for initial testing.
