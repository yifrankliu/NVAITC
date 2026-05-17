within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Sources;
model v0
  extends BaseClasses.PartialSources(redeclare Data.NULL data);
  input SI.HeatFlowRate Q_flow_total=0.0
    "Total heat flow to the cabinet"
    annotation (Dialog(group="Input"));
  Modelica.Blocks.Sources.RealExpression Q_flow_int(y=
        Q_flow_total) annotation (Placement(transformation(
          extent={{-40,-70},{-20,-50}})));
equation

  connect(controlBus.Q_flow, Q_flow_int.y) annotation (Line(
      points={{0,-100},{0,-60},{-19,-60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
end v0;
