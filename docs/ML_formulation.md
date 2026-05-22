# ML_formulation
initial ideas for ML layer architecture formulation.

## TODO:
1. Ask nicely for ORNL workload trace data, try to setup a call with Dr. Kumar.

## Analyze and/or Answer - Directions to find the most optimal strategy
1. ORNL Frontier supercomputer architecture. From their Dymola physical model, FMU wrapping, to Python interactions.
    - Will ultimately need to build my own open-sourced OpenModelica compiler.
2. Have a physics-analysis file compiled. Understand their system down to every assumption. 
    - What knobs are built in? What knobs am I allowed to turn? 
    - What action variables/exogeneous variables are significant but are not present?
    - What physical assumptions are they making? What is the physics framework/formulation they are using?
3. Examine existing, most relevant literature:
    - LC-Opt: Carefully examine LC-Opt, what kinds of optimization do they deploy specifically? What meaninful, novel contributions can I make based on their multi-agent LLM foundation?
    - What ML architecture do other researchers deploy?

## Possible High-Level ML Architectures:
check google documentation


## Current data we have
1. Figshare dataset: gives compute power at 10-minute resolutions for 2023.
2. sustain-lc CSV gives blade-level power at 15-second resolution
3. We need to get workload data, either:
    - Top: directly get ORNL workload tracing data
    - Mid: Adapt some other similar data source
    - Bottom: Generate synthetic data
        - Exadigit will enable us to generate workload data if we get it running & compiling on OpenModelica, or somehow attain a dymola license.
