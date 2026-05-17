within ORNLSupercomputing.Components.SubComponents.DataCenter.Rectifier.Data;
record Data
  extends TRANSFORM.Icons.Record;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_bar;
  import TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;

  parameter Modelica.Units.SI.Temperature coolingChannels_T_a_start = from_degC(30.0);
  parameter Modelica.Units.SI.Temperature coolingChannels_T_b_start = from_degC(40.0);
  parameter Modelica.Units.SI.Pressure coolingChannels_pinit = from_psi(64.7);
  parameter TRANSFORM.Units.HydraulicResistance R_Rectifier = 11000.0;
  annotation (
    defaultComponentName="data",
    Icon(coordinateSystem(preserveAspectRatio=false), graphics={Text(
          lineColor={0,0,0},
          extent={{-100,-90},{100,-70}})}),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Documentation(info="<html>
</html>"));
end Data;
