within ORNLSupercomputing.Components.SubComponents.DataCenter.Blade;
model Blade_simple_pipe
  extends BaseClasses.PartialBlademodel(
  redeclare package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium);

  TRANSFORM.Fluid.Pipes.GenericPipe_MultiTransferSurface coolingChannels(
    m_flow_a_start=10,
    redeclare package Medium = Medium,
    use_HeatTransfer=true,
    redeclare model HeatTransfer =
        TRANSFORM.Fluid.ClosureRelations.HeatTransfer.Models.DistributedPipe_1D_MultiTransferSurface.Nus_SinglePhase_2Region
        (Nus_turb={{1e8} for i in 1:coolingChannels.geometry.nV}),
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.DistributedVolume_1D.StraightPipe
        (
        dimension=0.1,
        length=0.5,
        nV=1),
    p_a_start(displayUnit="bar") = 200000) annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0)));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.HeatFlow boundary(use_port=
        true)
    annotation (Placement(transformation(
        extent={{8,8},{-8,-8}},
        rotation=90,
        origin={0,18})));
  Data.Data data
    annotation (Placement(transformation(extent={{78,80},{94,98}})));
equation
  connect(boundary.port, coolingChannels.heatPorts[1, 1])
    annotation (Line(points={{-4.44089e-16,10},{-4.44089e-16,7.5},{0,7.5},{0,5}},
                                                            color={191,0,0}));
  connect(boundary.Q_flow_ext, Q_flow_ext) annotation (Line(points={{1.11022e-16,
          21.2},{1.11022e-16,60.6},{0,60.6},{0,100}}, color={0,0,127}));
  connect(port_a, coolingChannels.port_a)
    annotation (Line(points={{-100,0},{-10,0}}, color={0,127,255}));
  connect(coolingChannels.port_b, port_b)
    annotation (Line(points={{10,0},{100,0}}, color={0,127,255}));
  annotation (Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{
            100,100}})),
    experiment(StopTime=22000, __Dymola_Algorithm="Esdirk45a"));
end Blade_simple_pipe;
