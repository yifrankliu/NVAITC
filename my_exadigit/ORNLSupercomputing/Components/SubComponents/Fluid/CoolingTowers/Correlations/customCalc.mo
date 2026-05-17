within ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers.Correlations;
function customCalc
  "Cooling tower performance custom performance correlation for the Frontier cooling system CTs"

//   input Modelica.Units.SI.TemperatureDifference TRan
//     "Range temperature (water in - water out)"
//    annotation (Dialog(group="Nominal condition"));
  input Modelica.Units.SI.Temperature TWetBul "Air wet-bulb inlet temperature";
  input Modelica.Units.SI.MassFraction FRWat
    "Ratio actual over design water mass flow ratio";
  input Modelica.Units.SI.MassFraction FRAir
    "Ratio actual over design air mass flow ratio";
  input TRANSFORM.Units.NonDim adj
    "User adjustable parameter (in deg. F) in the approach temperature calculation";

  output Modelica.Units.SI.TemperatureDifference TApp "Approach temperature";

protected
  Modelica.Units.NonSI.Temperature_degF TWetBul_degF
    "Air wet-bulb inlet temperature in deg F";
  Modelica.Units.SI.MassFraction liqGasRat "Liquid to gas mass flow ratio";
//   Modelica.Constants.c
  constant Real c[:] = {25.0 - 0.6*(27 - 17*adj),
                        0.73 + 0.0067*(27 - 17*adj),
                        -1}
    "Polynomial coefficients";

algorithm
  TWetBul_degF := Modelica.Units.Conversions.to_degF(TWetBul);
  // smoothMax is added to the numerator and denominator so that
  // liqGasRat -> 1, as both FRWat -> 0 and FRAir -> 0
  liqGasRat := Buildings.Utilities.Math.Functions.smoothMax(x1=1E-4, x2=FRWat, deltaX=1E-5)/
               Buildings.Utilities.Math.Functions.smoothMax(x1=1E-4, x2=FRAir, deltaX=1E-5);
  TApp := (5./9.)*(
          c[1] +
          c[2] * TWetBul_degF +
          c[3] * TWetBul_degF);
  annotation (
    Documentation(info="<html>
<p>
Correlation for approach temperature for YorkCalc cooling tower model.
See <a href=\"modelica://Buildings.Fluid.HeatExchangers.CoolingTowers.Correlations.Examples.YorkCalc\">
Buildings.Fluid.HeatExchangers.CoolingTowers.Correlations.Examples.YorkCalc</a> for the graph.
</p>
</html>", revisions="<html>
<ul>
<li>
July 12, 2011, by Michael Wetter:<br/>
Added <code>smoothMax</code> function to prevent division by zero.
</li>
<li>
May 14, 2008, by Michael Wetter:<br/>
First implementation.
</li>
</ul>
</html>"),
smoothOrder=5);
end customCalc;
