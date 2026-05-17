within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Data;
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
  parameter Modelica.Units.SI.Pressure volCTWR_pinit=from_bar(2.6);
  parameter Modelica.Units.SI.Pressure res_to_CT_dp=from_bar(0.25);
  parameter Modelica.Units.SI.Pressure res_to_CTWP_dp=100.0;
  parameter Modelica.Units.SI.Pressure volCTWS1_pinit=from_bar(2.0);
  parameter Modelica.Units.SI.Pressure volCTWS2_pinit=from_bar(2.92);
  parameter Modelica.Units.SI.Pressure res_from_CTWP_dp=from_bar(0.02);
  parameter Modelica.Units.SI.Pressure cooling_tower_p=from_bar(
       2.45);
  parameter Modelica.Units.SI.Pressure basin_reservoir_p=from_bar(
       2.0);
  // Init Temperatures
  parameter Modelica.Units.SI.Temperature volCTWR_Tinit=from_degC(
       25.0);
  parameter Modelica.Units.SI.Temperature volCTWS1_Tinit=
      from_degC(20.0);
  parameter Modelica.Units.SI.Temperature volCTWS2_Tinit=
      from_degC(20.0);
  parameter Modelica.Units.SI.Temperature basin_reservoir_Tinit=
      from_degC(20.0);
  // Volumes
  parameter Modelica.Units.SI.Volume volCTWR_vol=50.0;
  parameter Modelica.Units.SI.Volume volCTWS1_vol=50.0;
  parameter Modelica.Units.SI.Volume volCTWS2_vol=10.0;
  annotation (
    defaultComponentName="data",
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Documentation(info="<html>
</html>"));
end Data;
