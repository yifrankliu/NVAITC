within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Data;
record v0
  extends BaseClasses.PartialData;

  import
    TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  import
    TRANSFORM.Units.Conversions.Functions.Volume_m3.from_galUS;

  parameter SI.MassFlowRate m_flow_nominal=17;
  parameter Modelica.Units.SI.Pressure p_a_nominal=from_psi(64.7);
  parameter Modelica.Units.SI.Temperature T_a_nominal=
      from_degC(30.0);

//   parameter Modelica.Units.SI.Volume ccVolCabinet=0.3
//     "Fluid Volume per cabinet";
  parameter Modelica.Units.SI.Volume ccVolCabinet=from_galUS(21.9)
    "Fluid Volume per cabinet";
  parameter TRANSFORM.Units.HydraulicResistance R_Cab=11000
    "Hydraulic resistance per cabinet";

  //   parameter Integer nBladesPerCab=1 "No. of blades per cabinet";
  //   parameter Integer nRectifiersPerCab=1 "No. of rectifiers per cabinet";
  //   parameter Integer nCPUsPerBlade=1 "No. of CPUs per blade";
  //   parameter Integer nGPUsPerBlade=1 "No. of GPUs per blade";

  annotation (defaultComponentName="data");
end v0;
