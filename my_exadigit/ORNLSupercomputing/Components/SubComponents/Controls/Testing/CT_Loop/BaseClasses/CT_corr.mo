within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CT_Loop.BaseClasses;
function CT_corr "Cooling tower Temperature setpoint"

  input Modelica.Units.SI.Temperature TWetBul "Air wet-bulb inlet temperature in F";
  input TRANSFORM.Units.NonDim adj
    "User adjustable parameter (in deg. F) in the approach temperature calculation";

  output Modelica.Units.SI.TemperatureDifference TApp "Approach temperature";

  //   Modelica.Constants.c
protected
  constant Real c[:] = {25.0 - 0.6*(27 - 17*adj),
                        0.73 + 0.0067*(27 - 17*adj),
                        -1}
    "Polynomial coefficients";

algorithm
  TApp := (
          c[1] +
          c[2] * TWetBul +
          c[3] * TWetBul);
  annotation (
    Documentation(info="<html>
<p>
Correlation for approach temperature used in the Frontier Control systems.
</p>
</html>"),
smoothOrder=5);
end CT_corr;
