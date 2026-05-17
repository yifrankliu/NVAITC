within ORNLSupercomputing.Systems.Datacenter.Data;
record Data
  extends BaseClasses.PartialData;
  // Note: The (total) volumes are approximated from CAD files.
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_bar;
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  import
    TRANSFORM.Units.Conversions.Functions.VolumeFlowRate_m3_s.from_gpm;
  //
  // Pressures
  parameter Modelica.Units.SI.Pressure volHTWS_pinit=from_psi(79.7);
  parameter Modelica.Units.SI.Pressure volHTWR_pinit=from_psi(59.7);
  parameter Modelica.Units.SI.Pressure dP_valve_bypass=from_psi(10.0);
  parameter Modelica.Units.SI.Pressure dP_bypass=from_bar(1.15);
  // Temperatures
  parameter Modelica.Units.SI.Temperature volHTWS_Tinit=from_degC(22.5);
  parameter Modelica.Units.SI.Temperature volHTWR_Tinit=from_degC(35.0);
  // Mass flow rates
  parameter Modelica.Units.SI.MassFlowRate bypass_nom_flow=from_gpm(1900.0)
  *1000.0;
  annotation (
    defaultComponentName="data",
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Documentation(info="<html>
</html>"));
end Data;
