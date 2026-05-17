within ORNLSupercomputing.Components.SubComponents.Fluid.Pumps.Examples;
model CTWPTest "Cold Temperature Water Pump Test for a fixed speed and dP"
  extends Modelica.Icons.Example;
  package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium;
  CTWP                          cTWP(
    p_a_start=100000,
    redeclare package Medium = Medium,
    nParallel=3,
    m_flow_start=0.1,
    use_powerCharacteristic=false,
    N_nominal=1780,
    diameter_nominal=10.875*0.0254,
    use_port=true)
    annotation (Placement(transformation(extent={{-38,-12},{-14,12}})));

  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT source(
    redeclare package Medium = Medium,
    p=100000,
    T(displayUnit="degC") = 293.15,
    nPorts=1)
    annotation (Placement(transformation(extent={{-70,-10},{-50,10}})));

  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT sink(
    redeclare package Medium = Medium,
    p=100000,
    T=293.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={70,0})));

  TRANSFORM.Fluid.FittingsAndResistances.PressureLoss resistance(redeclare
      package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater,
      dp0(displayUnit="bar") = 100000)
    annotation (Placement(transformation(extent={{34,-10},{54,10}})));
  TRANSFORM.Fluid.Volumes.SimpleVolume volume(redeclare package Medium = Medium,
                                                          redeclare model
      Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.01))
    annotation (Placement(transformation(extent={{12,-10},{32,10}})));
  Modelica.Blocks.Sources.RealExpression N(y=60)
    annotation (Placement(transformation(extent={{-80,10},{-60,32}})));
  TRANSFORM.Fluid.Sensors.MassFlowRate m_flow(redeclare package Medium = Medium,
      showName=false)
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression V_flow(y=volume.port_a.m_flow/
        volume.Medium.density_ph(volume.port_a.p, volume.port_a.h_outflow)/
        0.00006309019640343866)  "volumetric flow in \"GPM\""
    annotation (Placement(transformation(extent={{-36,-40},{0,-20}})));
  Modelica.Blocks.Sources.RealExpression pumpHead(y=cTWP.head) "pump head in m"
    annotation (Placement(transformation(extent={{-36,-58},{0,-38}})));
  Modelica.Blocks.Interaction.Show.RealValue
                                       V_Flow_Display1(significantDigits=3)
    annotation (Placement(transformation(extent={{12,-43.5},{34,-16.5}})));
  Modelica.Blocks.Interaction.Show.RealValue
                                       V_Flow_Display2(significantDigits=3)
    annotation (Placement(transformation(extent={{12,-61.5},{34,-34.5}})));
equation
  connect(cTWP.port_a, source.ports[1])
    annotation (Line(points={{-38,0},{-50,0}}, color={0,127,255}));
  connect(sink.ports[1], resistance.port_b)
    annotation (Line(points={{60,0},{51,0}}, color={0,127,255}));
  connect(resistance.port_a, volume.port_b)
    annotation (Line(points={{37,0},{28,0}}, color={0,127,255}));
  connect(N.y,cTWP. inputSignal)
    annotation (Line(points={{-59,21},{-26,21},{-26,8.4}}, color={0,0,127}));
  connect(cTWP.port_b, m_flow.port_a)
    annotation (Line(points={{-14,0},{-10,0}}, color={0,127,255}));
  connect(m_flow.port_b, volume.port_a)
    annotation (Line(points={{10,0},{16,0}}, color={0,127,255}));
  connect(V_Flow_Display2.numberPort,pumpHead. y)
    annotation (Line(points={{10.35,-48},{1.8,-48}}, color={0,0,127}));
  connect(V_Flow_Display1.numberPort,V_flow. y)
    annotation (Line(points={{10.35,-30},{1.8,-30}}, color={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,-75},
            {100,75}})),                                         Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-100,-75},{100,75}})),
    conversion(noneFromVersion=""),
    experiment(StopTime=1, __Dymola_Algorithm="Esdirk45a"));
end CTWPTest;
