within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.HotWaterLoop.Data;
record Data
  extends BaseClasses.PartialData;
  // Note: The (total) volumes are approximated from CAD files.
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  import
    TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import
    TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_bar;
  // Init and res. pressures
  parameter Modelica.Units.SI.Pressure volHTWR1_pinit=from_psi(59.7);
  parameter Modelica.Units.SI.Pressure volHTWR2_pinit=from_psi(83.7);
  parameter Modelica.Units.SI.Pressure volHTWS_pinit=from_psi(81.7);
  parameter Modelica.Units.SI.Pressure res_to_EHX_dP=100.0;
  parameter Modelica.Units.SI.Pressure press_HTWP_p=from_psi(81.7);
  parameter Modelica.Units.SI.Pressure res_from_E102_dP=from_psi(4.0);
  parameter Modelica.Units.SI.Pressure res_to_E102_dP=
      res_from_E102_dP;
  parameter TRANSFORM.Units.HydraulicResistance res_from_E102_R=
      res_from_E102_dP/250.0;
  parameter TRANSFORM.Units.HydraulicResistance res_to_E102_R=
      res_to_E102_dP/250.0;
  // Temperatures
  parameter Modelica.Units.SI.Temperature volHTWR1_Tinit=
      from_degC(30.0);
  parameter Modelica.Units.SI.Temperature volHTWR2_Tinit=
      from_degC(30.0);
  parameter Modelica.Units.SI.Temperature volHTWS_Tinit=from_degC(
       22.5);
  parameter Modelica.Units.SI.Temperature press_HTWP_T=from_degC(21.0);
  // Volumes
  parameter Modelica.Units.SI.Volume volHTWR1_vol=100.0;
  parameter Modelica.Units.SI.Volume volHTWR2_vol=25.0;
  parameter Modelica.Units.SI.Volume volHTWS_vol=100.0;
  // Thermal Conductance
  parameter Modelica.Units.SI.ThermalConductance UA_base=(923.4*5.6783)
      *(8287*0.092903);
  // EHX UA modification parameter
  parameter Real UA_corr_mod=1.0;
  annotation (
    defaultComponentName="data",
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Documentation(info="<html>
</html>"));
end Data;
