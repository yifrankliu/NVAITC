# Work Log
Documenting progress, findings, and architectural decisisons

## Mar 17th Processing and understanding exadigit — oak ridge laboratory's frontier super computer & data centers
- Found most significant (connected) .mo files in exadigit repo
- Installed required packages in openmodelica IDE environment by recursively searching through .mo files
    - Requirements: Modelica(version="4.0.0"), TRANSFORM(version="0.5"), Buildings(version="11.0.1");
    - Modelica pre-installed, Buildings come with OpenModelica, Transform requires cloning from exadigit.

Important TRANsient Simulation Framework of Reconfigurable Models (Transform) library documentation: https://github.com/ORNL-Modelica/TRANSFORM-Library?tab=readme-ov-file

To access hidden folder .openmodelica: 
1. Cmd + Shift + G and type ~/.openmodelica/ in Finder
2. ls ~/.openmodelica/libraries/ in terminal

Error found while loading exadigit model, replaced:
- parameter Real nCT_crit[nEHX_max] = {1, 4, 8, 12}[1:nEHX_max] "no of cooling towers for staging EHXs" annotation(Dialog(group="Inputs"));
with:
- parameter Real nCT_crit[nEHX_max] = {1, 4, 8, 12} "no of cooling towers for staging EHXs" annotation(Dialog(group="Inputs"));
because original array slicing syntax is valid in Dymola but not suitable for openmodelica

Significant files are mostly stored in models of a component, v0.mo. Exadigit file paths, significant files & high-level structure broken down in exadigit.

Significant physical formulations & constraints are also broken down in exadigit folder.

## Feb
Setup docker img, openmodelica IDE, explored repos of LC-opt and exadigit. Decided to: build my own digital twin using free OpenModelica and develop my strategy & run tests based on my own digital twin.

## Jan
Literature review, project proposals, meetings with Cliff, agreement on research topic & direction