within TemplatesCSM.BaseClasses.Tests;
partial model PartialTest_FourPort_across_pT_mT_pT_mT
  extends Modelica.Icons.Example;
  extends TemplatesCSM.BaseClasses.Fluids.Mediums_Two;

  parameter Integer n=1
    "# of parallel instances of the model to be simulated";

  replaceable Fluids.PartialFourPort_across simulator[n] constrainedby
    Fluids.PartialFourPort_across(redeclare package Medium_1 = Medium_1,
      redeclare package Medium_2 = Medium_2) annotation (Placement(
        transformation(extent={{-10,-10},{10,10}})), choicesAllMatching=true);
  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT boundary_inlet_1(
    redeclare package Medium = Medium_1,
    p=simulator[1].port_a1_start.p,
    T=simulator[1].port_a1_start.T,
    nPorts=n) annotation (Placement(transformation(extent={{-80,30},{-60,50}})));

  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT boundary_inlet_2(
    redeclare package Medium = Medium_2,
    p=simulator[1].port_a2_start.p,
    T=simulator[1].port_a2_start.T,
    nPorts=n) annotation (Placement(transformation(extent={{80,-50},{60,-30}})));
  TRANSFORM.Fluid.BoundaryConditions.MassFlowSource_T boundary_outlet_2(
    redeclare package Medium = Fluids.Mediums_Two.Medium_2,
    m_flow=simulator[1].port_b2_start.m_flow,
    T=simulator[1].port_b2_start.T,
    nPorts=1)
    annotation (Placement(transformation(extent={{-80,-50},{-60,-30}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet_2(
    redeclare package Medium = Fluids.Mediums_Two.Medium_2,
    p_start=simulator[1].port_b2_start.p,
    T_start=simulator[1].port_b2_start.T,
    redeclare replaceable model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.1),
    nPorts_b=1,
    nPorts_a=n)
    annotation (Placement(transformation(extent={{-30,-50},{-50,-30}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet_1(
    redeclare package Medium = Fluids.Mediums_Two.Medium_1,
    p_start=simulator[1].port_b1_start.p,
    T_start=simulator[1].port_b1_start.T,
    redeclare replaceable model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.1),
    nPorts_b=1,
    nPorts_a=n)  annotation (Placement(transformation(extent={{30,30},{50,
            50}})));
  TRANSFORM.Fluid.BoundaryConditions.MassFlowSource_T boundary_outlet_1(
    redeclare package Medium = Fluids.Mediums_Two.Medium_1,
    m_flow=simulator[1].port_b1_start.m_flow,
    T=simulator[1].port_b1_start.T,
    nPorts=1) annotation (Placement(transformation(extent={{90,30},{70,50}})));
equation

  connect(boundary_inlet_2.ports, simulator.port_a2) annotation (Line(points={{
          60,-40},{20,-40},{20,-6},{10,-6}}, color={0,127,255}));
  connect(boundary_inlet_1.ports, simulator.port_a1) annotation (Line(points={{
          -60,40},{-20,40},{-20,6},{-10,6}}, color={0,127,255}));
  connect(boundary_outlet_2.ports[1], plenum_outlet_2.port_b[1])
    annotation (Line(points={{-60,-40},{-46,-40}}, color={0,127,255}));
  connect(plenum_outlet_2.port_a, simulator.port_b2) annotation (Line(
        points={{-34,-40},{-20,-40},{-20,-6},{-10,-6}}, color={0,127,255}));
  connect(plenum_outlet_1.port_b[1], boundary_outlet_1.ports[1])
    annotation (Line(points={{46,40},{70,40}}, color={0,127,255}));
  connect(plenum_outlet_1.port_a, simulator.port_b1) annotation (Line(
        points={{34,40},{20,40},{20,6},{10,6}}, color={0,127,255}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-140,-100},
            {140,100}})),
    experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
end PartialTest_FourPort_across_pT_mT_pT_mT;
