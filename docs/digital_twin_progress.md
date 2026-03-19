# Digital twin work Log
Documenting progress, findings, and architectural decisisons

## Mar 19th Bug fixes & TemplatesCSM library integration
- Contacted Dr. Kumar ORNL, located TemplatesCSM: https://code.ornl.gov/exadigit/AutoCSM, communications revealed a bug in OpenModelica & apparently a bug needs to be resolved before it could work on OpenModelica
- Cloned "AutoCSM" library into my_exadigt

### New Loading Process
1. TRANSFORM: in my_exadigit
2. Buildings: /Users/yhkd/.openmodelica/libraries/Buildings 11.0.0/package.mo (hidden .openmodelica, needs direct command)
3. TemplatesCSM: in my_exadigit autocsm: /Users/yhkd/Desktop/NVAITC_files/my_exadigit/AutoCSM/methods/modelica/TemplatesCSM/package.mo
4. ORNL package.mo

### New Errors
Loaded TemplatesCSM from autoCSM library. Now OMEdit can be navigated and symbols & modules are appearing. However there are many reported errors due to the mismatched Transform library. Mismatched Transform library is due to a private v0.5 Transform library, currently using v1.0. Errors reported include:

```bash
[1] 17:11:42 Translation Error
[ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.BaseClasses.Simple_ITD_HX: 27:3-28:40]: Component CFs of variability constant has binding 'fill(datacenter.computeBlock.cdu.HEX.CDU_HEX.CF, datacenter.computeBlock.cdu.HEX.CDU_HEX.nV)' of higher variability parameter.

[2] 17:11:42 Translation Error
[ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.EHX: 9:3-9:117]: Non-array modification '"Pa"' for array component 'displayUnit', possibly due to missing 'each'.

[3] 17:11:42 Translation Error
[TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance: 4:3-4:94]: Non-array modification 'centralEnergyPlant.hotWaterLoop.data.res_to_EHX_dP / (centralEnergyPlant.hotWaterLoop.port_a1_nominal.m_flow / centralEnergyPlant.hotWaterLoop.nHeatExchangerTrains)' for array component 'R', possibly due to missing 'each'.

[4] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.BaseClasses.PartialTwoPortTransport: 10:3-12:41]: Non-array modification '75' for array component 'm_flow_start', possibly due to missing 'each'.

[5] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.BaseClasses.PartialTwoPortTransport: 7:3-9:41]: Non-array modification '50' for array component 'dp_start', possibly due to missing 'each'.

[6] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.BaseClasses.PartialTwoPortTransport: 7:3-9:41]: Non-array modification '"Pa"' for array component 'displayUnit', possibly due to missing 'each'.

[7] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.ValveLinear: 4:3-6:56]: Non-array modification '"Pa"' for array component 'displayUnit', possibly due to missing 'each'.

[8] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.ValveLinear: 7:3-8:44]: Non-array modification '125' for array component 'm_flow_nominal', possibly due to missing 'each'.

[9] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.BaseClasses.PartialTwoPortTransport: 7:3-9:41]: Non-array modification '50000000' for array component 'dp_start', possibly due to missing 'each'.

[10] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.BaseClasses.PartialTwoPortTransport: 10:3-12:41]: Non-array modification '100' for array component 'm_flow_start', possibly due to missing 'each'.

[11] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.ValveLinear: 7:3-8:44]: Non-array modification '150' for array component 'm_flow_nominal', possibly due to missing 'each'.

[12] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.BaseClasses.PartialTwoPortTransport: 10:3-12:41]: Non-array modification '31.25' for array component 'm_flow_start', possibly due to missing 'each'.

[13] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.ValveLinear: 4:3-6:56]: Non-array modification '100' for array component 'dp_nominal', possibly due to missing 'each'.

[14] 17:11:42 Translation Error
[TRANSFORM.Fluid.Valves.ValveLinear: 7:3-8:44]: Non-array modification '100' for array component 'm_flow_nominal', possibly due to missing 'each'.

[15] 17:11:42 Translation Error
[ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers.coolingTower_Towb: 8:3-8:74]: Non-array modification '55' for array component 'CT_mflow_nom', possibly due to missing 'each'.

[16] 17:11:42 Translation Error
[ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers.coolingTower_Towb: 11:3-11:107]: Non-array modification 'centralEnergyPlant.coolingTowerLoop.coolingTower.data.cooling_tower_p' for array component 'CT_pinit', possibly due to missing 'each'.

[17] 17:11:42 Translation Error
[TRANSFORM.Fluid.Volumes.BaseClasses.PartialVolume: 23:3-24:75]: Non-array modification 'centralEnergyPlant.coolingTowerLoop.coolingTower.data.volCTWS2_pinit' for array component 'p_start', possibly due to missing 'each'.

[18] 17:11:42 Translation Error
[TRANSFORM.Fluid.Volumes.BaseClasses.PartialVolume: 28:3-32:27]: Non-array modification 'centralEnergyPlant.coolingTowerLoop.coolingTower.data.volCTWS2_Tinit' for array component 'T_start', possibly due to missing 'each'.

[19] 17:11:42 Translation Error
[ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.BaseClasses.Simple_ITD_HX: 27:3-28:40]: Component CFs of variability constant has binding 'fill(datacenter_1.computeBlock.cdu.HEX.CDU_HEX.CF, datacenter_1.computeBlock.cdu.HEX.CDU_HEX.nV)' of higher variability parameter.

[20] 17:11:42 Translation Error
[ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.EHX: 72:9-86:50]: Variable showName not found in scope EHX.

[21] 17:11:42 Translation Error
[TRANSFORM.HeatExchangers.Simple_HX: 328:55-341:50]: Variable showName not found in scope Simple_HX.

[22] 17:11:42 Translation Error
[ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.CDU_HEX: 125:9-139:50]: Variable showName not found in scope CDU_HEX.

[23] 17:11:42 Translation Error
[TRANSFORM.Fluid.FittingsAndResistances.BaseClasses.PartialResistance: 44:65-55:27]: Function iconUnit not found in scope <top>.
```

Above reported errors fall into 4 categories:
1. Errors 2-18: Missing "each" keyword
2. Errors 20-22: "showName" not found
3. Error 23: "iconUnit" function not found
4. Errors 1 & 19: "CFs" constant binding variability

### Resolutions (Dymola -> Openmodelica compatability fixes with v1.0 Transform):

-------------------------------------------------------------
1. ERROR 1 & 19 — CFs constant binding
-------------------------------------------------------------
File: Components/SubComponents/Fluid/HeatExchangers/BaseClasses/Simple_ITD_HX.mo

Problem: Dymola allows constants sized by parameters. OpenModelica does not.

```bash
Change:
  constant TRANSFORM.Units.NonDim CFs[nV]=fill(CF, nV)
To:
  parameter TRANSFORM.Units.NonDim CFs[nV]=fill(CF, nV)

Command used:
  sed -i '' 's/constant TRANSFORM.Units.NonDim CFs\[nV\]=fill(CF, nV)/parameter TRANSFORM.Units.NonDim CFs[nV]=fill(CF, nV)/' \
  .../Simple_ITD_HX.mo
```

-------------------------------------------------------------
2. ERRORS 2-18 — Missing 'each' keyword on array components
-------------------------------------------------------------
Root cause: Dymola infers scalar values apply to all array elements.
OpenModelica requires explicit 'each' keyword.

```bash
File 1: Systems/CentralEnergyPlant/Systems/HotWaterLoop/Models/v0.mo
  Affected components: res_to_EHX[], valveEHX1a[], valveEHX1b[], pumpTrain[]

  Change res_to_EHX instantiation:
    R=data.res_to_EHX_dP/(...)
  To:
    each R=data.res_to_EHX_dP/(...)
###ERROR FIXING STOPPED HERE — WILL NEED TO FIX OPENMODELICA COMPILER, WHICH SCOTT GREENWOOD FILED A TICKET FOR. CURRENT STRATEGY IS TO USE LC-OPT's FMU, DEVELOP ML LAYER & EXPLORE VIABLE ML STRATEGIES WHILE TRYING TO FIX OPENMODELICA COMPILER IN PARALLEL. REFER TO EMAIL FOR MORE DETAIL.
  Change valveEHX1a instantiation:
    dp_start(displayUnit="Pa") = 50,
    m_flow_start=75,
    dp_nominal(displayUnit="Pa") = 100,
    m_flow_nominal=100
  To:
    each dp_start(displayUnit="Pa") = 50,
    each m_flow_start=75,
    each dp_nominal(displayUnit="Pa") = 100,
    each m_flow_nominal=100

  Change valveEHX1b instantiation:
    dp_start(displayUnit="Pa") = 50,
    m_flow_start=100,
    dp_nominal(displayUnit="Pa") = 100,
    m_flow_nominal=125
  To:
    each dp_start(displayUnit="Pa") = 50,
    each m_flow_start=100,
    each dp_nominal(displayUnit="Pa") = 100,
    each m_flow_nominal=125

  Change pumpTrain instantiation:
    dp_start=50000000,
    m_flow_start=100,
    m_flow_nominal=150
  To:
    each dp_start=50000000,
    each m_flow_start=100,
    each m_flow_nominal=150

File 2: Systems/CentralEnergyPlant/Systems/CoolingTowerLoop/Components/CoolingTower.mo
  Affected components: valve arrays, volume arrays

  Add 'each' to all scalar parameters assigned to array component instances.
  Pattern: any parameter assignment inside a [...] array instantiation needs 'each'.

File 3: Components/SubComponents/Fluid/CoolingTowers/coolingTower_Towb.mo
  Change:
    CT_mflow_nom = 55
    CT_pinit = ...
  To:
    each CT_mflow_nom = 55
    each CT_pinit = ...

File 4: Components/SubComponents/Fluid/HeatExchangers/EHX.mo
  Change:
    EHX_p_a_start_1(displayUnit="Pa")
  To:
    EHX_p_a_start_1(each displayUnit="Pa")
```

-------------------------------------------------------------
3. ERRORS 20-22 — showName variable not found
-------------------------------------------------------------
```bash
Files:
  Components/SubComponents/Fluid/HeatExchangers/EHX.mo
  Components/SubComponents/Fluid/HeatExchangers/CDU_HEX.mo

Problem: showName was removed between TRANSFORM v0.5 and v1.0.

Fix: Find any annotation block referencing showName and remove
the showName condition. Example:
  Change: visible=DynamicSelect(true, showName)
  To:     visible=true
```

-------------------------------------------------------------
4. ERROR 23 — iconUnit function not found
-------------------------------------------------------------
```bash
File: Affects sensor components with redeclared iconUnit functions

Problem: TRANSFORM v1.0 removed or renamed the iconUnit function
used in PressureTemperature sensor annotations.

Fix: Remove or comment out the redeclare function iconUnit lines
in any sensor instantiation that references it. These are purely
cosmetic (display unit formatting) and do not affect simulation.
```

-------------------------------------------------------------
GENERAL RULE FOR DYMOLA → OPENMODELICA PORTING
-------------------------------------------------------------
1. constant -> parameter  when sized by a parameter
2. Add 'each' before any scalar assigned to array component parameter
3. Remove showName references (removed in TRANSFORM v1.0)
4. Remove iconUnit redeclarations (removed in TRANSFORM v1.0)
5. Remove array slicing syntax {a,b,c}[1:n] → {a,b,c}
=============================================================


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