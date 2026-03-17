# Work Log
Documenting progress, findings, and architectural decisisons

## Mar 17th
Reverse engineering repos:
- Found most significant (connected) .mo files in exadigit repo
- Installed required packages in openmodelica IDE environment by recursively searching through .mo files
    - Requirements: Modelica(version="4.0.0"), TRANSFORM(version="0.5"), Buildings(version="11.0.1");
    - Modelica pre-installed, Buildings come with OpenModelica, Transform requires cloning from exadigit.
- 

## Feb
Setup docker img, openmodelica IDE, explored repos of LC-opt and exadigit. Decided to: build my own digital twin using free OpenModelica and develop my strategy & run tests based on my own digital twin.

## Jan
Literature review, project proposals, meetings with Cliff, agreement on research topic & direction