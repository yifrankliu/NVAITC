within TemplatesCSM.BaseClasses.Tests;
partial model PartialTest_TwoPort_across_mT_pT
  extends Modelica.Icons.Example;
  extends TemplatesCSM.BaseClasses.Fluids.Medium_Single;

  parameter Integer n=1
    "# of parallel instances of the model to be simulated";

  replaceable Fluids.PartialTwoPort_across simulator[n] constrainedby
    Fluids.PartialTwoPort_across(redeclare package Medium = Medium) annotation (
     Placement(transformation(extent={{-10,-10},{10,10}})), choicesAllMatching=
        true);
  TRANSFORM.Fluid.BoundaryConditions.MassFlowSource_T boundary_inlet(
    redeclare package Medium = Medium,
    m_flow=simulator[1].port_a_start.m_flow,
    T=simulator[1].port_a_start.T,
    nPorts=1)
    annotation (Placement(transformation(extent={{-80,-10},{-60,10}})));
  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT boundary_outlet(
    redeclare package Medium = Medium,
    p=simulator[1].port_b_start.p,
    T=simulator[1].port_b_start.T,
    nPorts=n)
    annotation (Placement(transformation(extent={{80,-10},{60,10}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_inlet(
    redeclare package Medium = Medium,
    p_start=simulator[1].port_a_start.p,
    T_start=simulator[1].port_a_start.T,
    redeclare replaceable model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.1),
    nPorts_a=1,
    nPorts_b=n)
    annotation (Placement(transformation(extent={{-50,-10},{-30,10}})));

equation

  connect(boundary_inlet.ports[1], plenum_inlet.port_a[1])
    annotation (Line(points={{-60,0},{-54,0},{-54,0},{-46,0}},
                                               color={0,127,255}));
  connect(plenum_inlet.port_b, simulator.port_a)
    annotation (Line(points={{-34,0},{-10,0}}, color={0,127,255}));
  connect(simulator.port_b, boundary_outlet.ports)
    annotation (Line(points={{10,0},{60,0}}, color={0,127,255}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-140,-100},
            {140,100}})),
    experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
end PartialTest_TwoPort_across_mT_pT;
