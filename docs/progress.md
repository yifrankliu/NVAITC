# Work Log
Documenting progress, findings, and architectural decisisons

## Mar 17th Processing and understanding exadigit — oak ridge laboratory's frontier super computer & data centers
- Found most significant (connected) .mo files in exadigit repo
- Installed required packages in openmodelica IDE environment by recursively searching through .mo files
    - Requirements: Modelica(version="4.0.0"), TRANSFORM(version="0.5"), Buildings(version="11.0.1");
    - Modelica pre-installed, Buildings come with OpenModelica, Transform requires cloning from exadigit.

Important TRANsient Simulation Framework of Reconfigurable Models (Transform) library documentation: https://github.com/ORNL-Modelica/TRANSFORM-Library?tab=readme-ov-file

Loading Buildings Package from hidden OpenModelica folder: /Users/yhkd/.openmodelica/libraries/Buildings 11.0.0/package.mo (after installing pkg)

To access hidden folder .openmodelica: 
1. Cmd + Shift + G and type ~/.openmodelica/ in Finder
2. ls ~/.openmodelica/libraries/ in terminal

**Modifications made to original Exadigit Repo**
1. In Components/SubComponents/Controls/Testing/HTW_Loop/BaseClasses/EHX_Staging.mo:
    Replaced
    ```bash
    parameter Real nCT_crit[nEHX_max] = {1, 4, 8, 12}[1:nEHX_max] "no of cooling towers for staging EHXs" annotation(Dialog(group="Inputs"))
    ```
    with:
    ```bash
    parameter Real nCT_crit[nEHX_max] = {1, 4, 8, 12} "no of cooling towers for staging EHXs" annotation(Dialog(group="Inputs")). 
    ```
    Because original array slicing syntax is valid in Dymola but not suitable for openmodelica

2. In highest level package.mo:
    Replaced Transform 0.5 to 1.0 and Buildings 11.0.1 to 11.0.0 to accomodate for package version mismatches.

3. In /Users/yhkd/Desktop/NVAITC_files/exadigit/ORNLSupercomputing/Models/NULL.mo:
    Replaced
    ```bash
    within ORNLSupercomputing.Models;
    model NULL
        extends ORNLSupercomputing.BaseClasses.PartialModel(
            redeclare replaceable Controls.NULL controls,
            redeclare replaceable Data.NULL data,
            redeclare replaceable Sources.NULL sources);
    extends TemplatesCSM.Icons.NULL;
    end NULL;
    ```
    with:
    ```bash
    within ORNLSupercomputing.Models;
    model NULL
    end NULL;
    ```
    because original null file was triggering errors when loading the exadigit model, it can't find ORNLSupercomputing.BaseClasses.PartialModel in scope. TemplateCSM also seems to be an internal template that the original developers forgot to leave out.

4. TemplateCSM is a private library dependency that we don't have access to, but the entire model is heavily dependent on TemplateCSM, including inheritance & cosmetic purposes.
    Created a stub templateCSM library of our own, created "TemplatesCSM" folder in my_exadigit folder and then created package.mo in folder with following code:
    ```bash
    package TemplatesCSM

    package Icons
        model BaseClassesPackage end BaseClassesPackage;
        model ComponentsPackage end ComponentsPackage;
        model ControlsPackage end ControlsPackage;
        model DataPackage end DataPackage;
        model ModelsPackage end ModelsPackage;
        model NULL end NULL;
        model SourcesPackage end SourcesPackage;
        model Structure end Structure;
        model SystemPackage end SystemPackage;
    end Icons;

    package Templates
        record Structure
        parameter Integer n = 1;
        parameter Integer n_int = 1;
        parameter Boolean useParallel = false;
        end Structure;
    end Templates;

    package BaseClasses

        expandable connector PartialControlBus
        end PartialControlBus;

        package Systems
            partial model PartialModel
            end PartialModel;
            partial model PartialControls
            end PartialControls;
            partial model PartialData
            end PartialData;
            partial model PartialSources
            end PartialSources;
            partial model PartialSummary
            end PartialSummary;
        end Systems;

        package Fluids
            partial model Medium_Single
                replaceable package Medium =
                    Modelica.Media.Interfaces.PartialMedium;
                    #ignored indenting for the following
            end Medium_Single;
            partial model Interface_TwoPort
        replaceable package Medium =
          Modelica.Media.Interfaces.PartialMedium;
        Modelica.Fluid.Interfaces.FluidPort_a port_a(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_b port_b(
          redeclare package Medium = Medium);
      end Interface_TwoPort;
      partial model Interface_FourPort
        replaceable package Medium =
          Modelica.Media.Interfaces.PartialMedium;
        Modelica.Fluid.Interfaces.FluidPort_a port_a1(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_b port_b1(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_a port_a2(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_b port_b2(
          redeclare package Medium = Medium);
      end Interface_FourPort;
      partial model PartialTwoPort_across
        replaceable package Medium =
          Modelica.Media.Interfaces.PartialMedium;
        Modelica.Fluid.Interfaces.FluidPort_a port_a(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_b port_b(
          redeclare package Medium = Medium);
      end PartialTwoPort_across;
      partial model PartialFourPort_across
        replaceable package Medium =
          Modelica.Media.Interfaces.PartialMedium;
        Modelica.Fluid.Interfaces.FluidPort_a port_a1(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_b port_b1(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_a port_a2(
          redeclare package Medium = Medium);
        Modelica.Fluid.Interfaces.FluidPort_b port_b2(
          redeclare package Medium = Medium);
      end PartialFourPort_across;
    end Fluids;

    package Tests
      partial model PartialTest
        parameter Integer n = 1;
      end PartialTest;
      partial model PartialTest_TwoPort_across_mT_pT
        parameter Integer n = 1;
      end PartialTest_TwoPort_across_mT_pT;
      partial model PartialTest_TwoPort_across_pT_pT
        parameter Integer n = 1;
      end PartialTest_TwoPort_across_pT_pT;
      partial model PartialTest_FourPort_across_mT_pT_mT_pT
        parameter Integer n = 1;
      end PartialTest_FourPort_across_mT_pT_mT_pT;
    end Tests;

  end BaseClasses;

end TemplatesCSM;
```

5. Solution 4 does not work unfortunately, too many inheritance instances and dependencies — currently reached out to Yale center for research computing & Vineet Kumar from Oakridge National Laboratory, will continue developing OpenModelica in parallel but also trying to see if I can gain licensing to Dymola


Significant files are mostly stored in models of a component, v0.mo. Exadigit file paths, significant files & high-level structure broken down in exadigit.

Significant physical formulations & constraints are also broken down in exadigit folder.

To setup OMEdit:
1. docker-om, OMEdit
2. load transform library in my_exadigit using file -> load_library
3. load installed buildings library using direct function
4. load highest level package.mo in my_exadigit (versions altered from original version to accomodate for Transform 1.0 instead of 0.5 and Buildings 11.0.0 isntead of 11.0.1)

## Feb
Setup docker img, openmodelica IDE, explored repos of LC-opt and exadigit. Decided to: build my own digital twin using free OpenModelica and develop my strategy & run tests based on my own digital twin.

Running OpenModelica
1. docker-om
2. OMEdit

## Jan
Literature review, project proposals, meetings with Cliff, agreement on research topic & direction