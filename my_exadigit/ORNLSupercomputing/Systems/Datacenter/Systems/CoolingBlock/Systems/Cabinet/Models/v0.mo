within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Models;
model v0
  extends BaseClasses.BaseClasses_A.PartialModel_A(
    port_b_nominal(
      p=data.p_a_nominal,
      T=data.T_a_nominal),
    port_a_nominal(
      p=data.p_a_nominal,
      T=data.T_a_nominal,
      m_flow=data.m_flow_nominal),
    redeclare replaceable Data.v0 data(R_Cab=33000),
    redeclare replaceable Sources.v0 sources,
    redeclare replaceable Controls.NULL controls);

  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.HeatFlow
    boundary(use_port=true) annotation (Placement(
        transformation(
        extent={{10,10},{-10,-10}},
        rotation=90,
        origin={0,30})));
  TRANSFORM.Fluid.Volumes.SimpleVolume coolingChannels(
    redeclare package Medium = Medium,
    p_start=port_a_start.p,
    T_start=port_a_start.T,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=data.ccVolCabinet),
    use_HeatPort=true) annotation (Placement(transformation(
          extent={{-10,10},{10,-10}}, rotation=0)));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    dp_inlet(redeclare package Medium = Medium, R=data.R_Cab*0.5)
    annotation (Placement(transformation(extent={{-70,-10},{-50,
            10}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    dp_outlet(redeclare package Medium = Medium, R=data.R_Cab*0.5)
             annotation (Placement(transformation(extent={{50,
            -10},{70,10}})));

equation
  connect(boundary.port, coolingChannels.heatPort)
    annotation (Line(points={{0,20},{0,6}}, color={191,0,0}));
  connect(port_a, dp_inlet.port_a) annotation (Line(points={{-180,
          0},{-67,0}}, color={0,127,255}));
  connect(dp_inlet.port_b, coolingChannels.port_a)
    annotation (Line(points={{-53,0},{-6,0}}, color={0,127,255}));
  connect(coolingChannels.port_b, dp_outlet.port_a)
    annotation (Line(points={{6,0},{53,0}}, color={0,127,255}));
  connect(dp_outlet.port_b, port_b) annotation (Line(points={{
          67,0},{180,0}}, color={0,127,255}));
  connect(controlBus.Q_flow, boundary.Q_flow_ext) annotation (
     Line(
      points={{0,100},{0,34}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (experiment(StopTime=1, __Dymola_Algorithm="Dassl"));
end v0;
