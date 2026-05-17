within ORNLSupercomputing.Components.SubComponents.Fluid.Pumps.Examples;
model CDUPTest "CDU Pump Test for a fixed speed and dP"
  extends Modelica.Icons.Example;
  package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium;
  CDUP cDUP(redeclare package Medium = Medium)
    annotation (Placement(transformation(extent={{-40,-10.5},{-20,10.5}})));

  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT source(
    redeclare package Medium = Medium,
    p=100000,
    T(displayUnit="degC") = 293.15,
    nPorts=1)
    annotation (Placement(transformation(extent={{-76,-10},{-56,10}})));

  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT sink(
    redeclare package Medium = Medium,
    p=100000,
    T=293.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={82,0})));

  TRANSFORM.Fluid.FittingsAndResistances.PressureLoss resistance(redeclare
      package Medium = Medium, dp0=230000)
    annotation (Placement(transformation(extent={{46,-10},{66,10}})));
  TRANSFORM.Fluid.Volumes.SimpleVolume volume(redeclare package Medium =
        Medium,                                           redeclare model
      Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.01))
    annotation (Placement(transformation(extent={{20,-10},{40,10}})));
  TRANSFORM.Fluid.Sensors.MassFlowRate m_flow(redeclare package Medium = Medium,
      showName=false)
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression V_flow(y=volume.port_a.m_flow/
        volume.Medium.density_ph(volume.port_a.p, volume.port_a.h_outflow)
        /0.00006309019640343866) "volumetric flow in \"GPM\""
    annotation (Placement(transformation(extent={{-36,-42},{0,-22}})));
  Modelica.Blocks.Sources.RealExpression pumpHead(y=cDUP.head) "pump head in m"
    annotation (Placement(transformation(extent={{-36,-60},{0,-40}})));
  Modelica.Blocks.Sources.RealExpression N(y=60.0)
    "Pump relative speed in \"%\""
    annotation (Placement(transformation(extent={{-78,10},{-60,30}})));
  Modelica.Blocks.Interaction.Show.RealValue
                                       V_Flow_Display1(significantDigits=
        3)
    annotation (Placement(transformation(extent={{12,-45.5},{34,-18.5}})));
  Modelica.Blocks.Interaction.Show.RealValue
                                       V_Flow_Display2(significantDigits=
        3)
    annotation (Placement(transformation(extent={{12,-63.5},{34,-36.5}})));
equation
  connect(sink.ports[1], resistance.port_b) annotation (Line(points={{72,0},{63,
          0}},                         color={0,127,255}));
  connect(resistance.port_a, volume.port_b)
    annotation (Line(points={{49,0},{36,0}}, color={0,127,255}));
  connect(cDUP.port_a, source.ports[1])
    annotation (Line(points={{-40,0},{-56,0}}, color={0,127,255}));
  connect(m_flow.port_a, cDUP.port_b)
    annotation (Line(points={{-10,0},{-20,0}}, color={0,127,255}));
  connect(m_flow.port_b, volume.port_a)
    annotation (Line(points={{10,0},{24,0}}, color={0,127,255}));
  connect(V_Flow_Display2.numberPort, pumpHead.y)
    annotation (Line(points={{10.35,-50},{1.8,-50}}, color={0,0,127}));
  connect(V_Flow_Display1.numberPort, V_flow.y)
    annotation (Line(points={{10.35,-32},{1.8,-32}}, color={0,0,127}));
  connect(N.y, cDUP.inputSignal) annotation (Line(points={{-59.1,20},{-30,20},{
          -30,7.35}}, color={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,
            -75},{100,75}})),                                    Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-100,-75},{100,75}})),
    conversion(noneFromVersion=""),
    experiment(StopTime=1, __Dymola_Algorithm="Esdirk45a"));
end CDUPTest;
