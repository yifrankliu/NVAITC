=============================================================
EXADIGIT REPO — FILE CATEGORIZATION
=============================================================

-------------------------------------------------------------
TIER 1: CORE SYSTEM MODELS (Most Significant)
Top-level assembly files — these wire everything together.
These are your blueprints for the rebuild.
-------------------------------------------------------------

Models/v1.mo (21 connects)
  → Top-level full system model — master assembly of everything

Models/v0.mo (14 connects)
  → Earlier version of the full system

Systems/CentralEnergyPlant/Models/v0.mo (20 connects)
  → Full central energy plant assembly

Systems/CentralEnergyPlant/Systems/HotWaterLoop/Models/v0.mo (29 connects)
  → HIGHEST CONNECT COUNT — hot water loop assembly

Systems/CentralEnergyPlant/Systems/CoolingTowerLoop/Models/v0.mo (21 connects)
  → Cooling tower loop assembly

Systems/Datacenter/Models/v0.mo (16 connects)
  → Datacenter-side assembly

Systems/Datacenter/Systems/CoolingBlock/Models/v0.mo (18 connects)
  → Cooling block assembly

Systems/Datacenter/Systems/CoolingBlock/Systems/CDU/Models/v0.mo (21 connects)
  → CDU assembly

Systems/Datacenter/Systems/CoolingBlock/Systems/Cabinet/Models/v0.mo (6 connects)
  → Cabinet/rack assembly


-------------------------------------------------------------
TIER 2: CONTROL SYSTEMS (Significant)
Rule-based controllers that your ML layer will eventually replace.
Critical to understand before building the ML interface.
-------------------------------------------------------------

Systems/CentralEnergyPlant/Systems/CoolingTowerLoop/Controls/CS_PumpAndStagingControl.mo (27)
  → Cooling tower pump staging logic

Systems/CentralEnergyPlant/Systems/HotWaterLoop/Controls/CS_PumpAndStagingControl.mo (14)
  → Hot water loop pump staging

Systems/Datacenter/Systems/CoolingBlock/Systems/CDU/Controls/CS_PumpAndValveControl.mo (21)
  → CDU pump and valve control

Systems/Datacenter/Systems/CoolingBlock/Systems/CDU/Controls/CS_FixedPumpAndValveControl.mo (17)
  → Fixed (static) CDU control — the baseline rule-based controller

Systems/CentralEnergyPlant/Systems/CoolingTowerLoop/Controls/CS_Constant.mo (11)
  → Constant setpoint controller — simplest baseline

Systems/CentralEnergyPlant/Systems/HotWaterLoop/Controls/CS_Constant.mo (8)
  → Same for hot water loop

Components/SubComponents/Controls/LimPID_Deadband_dbr.mo (13)
  → PID controller with deadband — used throughout the system

Components/SubComponents/Controls/LimPID_Hysteresis.mo (9)
  → PID controller with hysteresis


-------------------------------------------------------------
TIER 3: PHYSICAL COMPONENTS (Significant)
The actual physical component models — building blocks of the twin.
-------------------------------------------------------------

Components/SubComponents/Fluid/HeatExchangers/BaseClasses/Simple_ITD_HX.mo (18)
  → Core heat exchanger model

Components/SubComponents/Fluid/HeatExchangers/CDU_HEX.mo (6)
  → CDU-specific heat exchanger

Components/SubComponents/Fluid/CoolingTowers/PartialStaticTwoPortCoolingTower.mo (14)
  → Base cooling tower model

Components/SubComponents/Fluid/CoolingTowers/coolingTower.mo (7)
  → Concrete cooling tower implementation

Components/SubComponents/Fluid/CoolingTowers/coolingTower_Towb.mo (6)
  → Cooling tower with WET BULB TEMP INPUT
  → *** THIS IS WHERE AMBIENT WEATHER DATA ENTERS THE MODEL ***
  → Key file for your research question about environmental inputs

Components/SubComponents/Fluid/Pumps/PumpTrain.mo (6)
  → Pump train model

Components/SubComponents/Fluid/ColdPlate/coldPlate.mo (8)
  → Server cold plate — direct server cooling surface

Components/SubComponents/DataCenter/Blade/Blade_coldplates.mo (10)
  → Blade with cold plates — server heat generation model

Components/SubComponents/DataCenter/Blade/BaseClasses/chip_3D.mo (10)
  → 3D chip thermal model — finest granularity in the system

Components/SubComponents/DataCenter/Rectifier/Rectifier_simple_volume.mo (6)
  → Power rectifier thermal model


-------------------------------------------------------------
TIER 4: GLUE / TEST / BOILERPLATE (Low Priority)
Test harnesses and parameterization files.
Not part of the core model — skip for now.
-------------------------------------------------------------

Controls/Testing/CTW_Loop/BaseClasses/p_CTWR_setpoint.mo (28)
  → Test parameterization — high connect count but it's a test base class

Controls/Testing/CT_Loop/BaseClasses/p_CTWR_setpoint.mo (23)
  → Same

All Tests/Test_dynamic.mo files
  → Test harnesses — useful for understanding but not part of your rebuild

All Examples/ files (HTWPTest, CTWPTest, CDUPTest, etc.)
  → Isolated component tests

All BaseClasses/ files under Testing/
  → Parameter stubs for tests only


-------------------------------------------------------------
KEY INSIGHT
-------------------------------------------------------------

coolingTower_Towb.mo contains a dynamic WET BULB TEMPERATURE input.
