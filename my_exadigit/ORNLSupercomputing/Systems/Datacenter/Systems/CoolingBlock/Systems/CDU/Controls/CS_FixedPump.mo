within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Controls;
model CS_FixedPump
  extends BaseClasses.PartialControls(redeclare Data.v0 data);
  Modelica.Blocks.Sources.Constant const(k=1) annotation (
      Placement(transformation(extent={{-40,-70},{-20,-50}})));
equation
  connect(controlBus.Nrel_pump, const.y) annotation (Line(
      points={{0,-100},{0,-60},{-19,-60}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));
end CS_FixedPump;
