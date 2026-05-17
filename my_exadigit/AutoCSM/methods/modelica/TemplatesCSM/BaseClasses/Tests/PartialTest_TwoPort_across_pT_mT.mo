within TemplatesCSM.BaseClasses.Tests;
partial model PartialTest_TwoPort_across_pT_mT
  extends Modelica.Icons.Example;
  extends TemplatesCSM.BaseClasses.Fluids.Medium_Single;

  parameter Integer n=1
    "# of parallel instances of the model to be simulated";

  replaceable Fluids.PartialTwoPort_across simulator[n] constrainedby
    Fluids.PartialTwoPort_across(redeclare package Medium = Medium) annotation (
     Placement(transformation(extent={{-10,-10},{10,10}})), choicesAllMatching=
        true);
  TRANSFORM.Fluid.BoundaryConditions.MassFlowSource_T boundary_outlet(
    redeclare package Medium = Medium,
    m_flow=simulator[1].port_b_start.m_flow,
    T=simulator[1].port_b_start.T,
    nPorts=1) annotation (Placement(transformation(extent={{90,-10},{70,10}})));
  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT boundary_inlet(
    redeclare package Medium = Medium,
    p=simulator[1].port_a_start.p,
    T=simulator[1].port_a_start.T,
    nPorts=n)
    annotation (Placement(transformation(extent={{-70,-10},{-50,10}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet(
    redeclare package Medium = Medium,
    p_start=simulator[1].port_b_start.p,
    T_start=simulator[1].port_b_start.T,
    redeclare replaceable model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.1),
    nPorts_a=n,
    nPorts_b=1)
    annotation (Placement(transformation(extent={{30,-10},{50,10}})));

equation

  connect(boundary_inlet.ports, simulator.port_a)
    annotation (Line(points={{-50,0},{-10,0}}, color={0,127,255}));
  connect(simulator.port_b, plenum_outlet.port_a)
    annotation (Line(points={{10,0},{34,0}}, color={0,127,255}));
  connect(plenum_outlet.port_b[1], boundary_outlet.ports[1])
    annotation (Line(points={{46,0},{70,0}}, color={0,127,255}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-140,-100},
            {140,100}})),
    experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
end PartialTest_TwoPort_across_pT_mT;
