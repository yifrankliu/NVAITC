within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CDU_Loop.BaseClasses;
model CDUP_speed_simple
extends Modelica.Blocks.Icons.Block;
  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // Two CDUPs are always set to be operational
  // This simpler model just assumes a constant speed with some random noise
  // to mimic actual pump motor
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  parameter Real dp_nom = 27.5;
  parameter Real CDUP_Nrel_min = 52.0;
  parameter Real CDUP_Nrel_max = 75.0;
  parameter Real CDUP_Nrel_start = 63.9;
  // Control Systems tuning parameters
  parameter Real Ti = 100; // s
  parameter Real Td = 30; // s
  parameter Real gain = 0.1;
  Modelica.Blocks.Interfaces.RealInput p_CabS "Cab. Supply pressure"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,60}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Sources.Constant       dPSetPoint(k=CDUP_Nrel_start)
    annotation (Placement(transformation(extent={{-32,-16},{-16,0}})));
  Modelica.Blocks.Interfaces.RealInput p_CabR "Cab. return pressure"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,20}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));

  Modelica.Blocks.Interfaces.RealOutput CDUP_Nrel "CDUP Nrel" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,0}),  iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Noise.UniformNoise uniformNoise(
    samplePeriod=100,
    y_min=0.2,
    y_max=-0.2)
             annotation (Placement(transformation(extent={{-30,23},{-18,12}})));
  Modelica.Blocks.Math.Add add
    annotation (Placement(transformation(extent={{26,5.5},{38,-5.5}})));
equation
  connect(dPSetPoint.y, add.u1) annotation (Line(points={{-15.2,-8},{24.8,-8},{
          24.8,-3.3}}, color={0,0,127}));
  connect(uniformNoise.y, add.u2) annotation (Line(points={{-17.4,17.5},{24.8,
          17.5},{24.8,3.3}}, color={0,0,127}));
  connect(add.y, CDUP_Nrel)
    annotation (Line(points={{38.6,0},{113.8,0}}, color={0,0,127}));
end CDUP_speed_simple;
