within ORNLSupercomputing.Systems.CentralEnergyPlant.Controls;
model v0
  extends BaseClasses.PartialControls(redeclare Data.NULL data);
protected
  Modelica.Blocks.Continuous.FirstOrder firstOrder_intermediateLoop(T=1)
    annotation (Placement(transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={-30,-40})));
protected
  Modelica.Blocks.Continuous.FirstOrder firstOrder_coolingTowerLoop(T=1)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-30,-70})));
equation
  connect(controlBus.coolingTowerLoop.numCTs,
    firstOrder_intermediateLoop.u) annotation (Line(
      points={{0,-100},{-60,-100},{-60,-40},{-42,-40}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.intermediateLoop.T_EHX_HotSupply,
    firstOrder_coolingTowerLoop.u) annotation (Line(
      points={{0,-100},{-60,-100},{-60,-70},{-42,-70}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.intermediateLoop.numCTs,
    firstOrder_intermediateLoop.y) annotation (Line(
      points={{0,-100},{0,-40},{-19,-40}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.coolingTowerLoop.T_EHX_HotSupply,
    firstOrder_coolingTowerLoop.y) annotation (Line(
      points={{0,-100},{0,-70},{-19,-70}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
end v0;
