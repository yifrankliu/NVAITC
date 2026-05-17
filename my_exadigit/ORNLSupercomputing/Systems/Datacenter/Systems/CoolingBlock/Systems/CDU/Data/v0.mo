within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Data;
record v0
  extends BaseClasses.PartialData;

  import
    TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import
    TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_bar;
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  // Pressures
  parameter TRANSFORM.Units.HydraulicResistance R_Cab_Tot=11000.0;
  parameter TRANSFORM.Units.HydraulicResistance R_CTW=dP_CTW/(
      275.0*0.063);
  parameter TRANSFORM.Units.HydraulicResistance R_HTWR=2000.0;
  parameter TRANSFORM.Units.HydraulicResistance R_HTWS=2000.0;
  parameter Modelica.Units.SI.Pressure coolingChannels_pinit=
      from_psi(64.7);
  parameter Modelica.Units.SI.Pressure dP_CTW=from_psi(8.0);
  parameter Modelica.Units.SI.Pressure press_CDU_p=from_psi(30.5);
  parameter Modelica.Units.SI.Pressure dP_valve_CDU=50000;
  // Temperatures
  parameter Modelica.Units.SI.Temperature
    coolingChannels_T_a_start=from_degC(30.0);
  parameter Modelica.Units.SI.Temperature
    coolingChannels_T_b_start=from_degC(40.0);
  parameter Modelica.Units.SI.Temperature press_CDU_T=
      from_degC(30.0);
  // Mass flow rates
  parameter Modelica.Units.SI.MassFlowRate
    coolingChannels_m_start=15.0;
  parameter Modelica.Units.SI.MassFlowRate valve_m_flow_nom=11.0;
  // Volumes
  parameter Modelica.Units.SI.Volume ccVolTotal=0.3
    "Cabinet(s) piping volume";
  //
  parameter Real UA_corr_mod=1.0 "UA mod. correlation";

  annotation (defaultComponentName="data");
end v0;
