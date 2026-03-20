# ML_formulation
initial ideas for ML layer architecture formulation.

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
