within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Controls;
model CS_Constant
  extends BaseClasses.PartialControls(redeclare Data.Data data);

  TRANSFORM.Blocks.ArrayToMatrix arrayToMatrix(
    n=16,
    nrows=4,
    ncolumns=4)
    annotation (Placement(transformation(extent={{-20,-70},{0,-50}})));
  Modelica.Blocks.Routing.Replicator replicator(nout=16)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-50,-14})));
  TRANSFORM.Blocks.ArrayToMatrix arrayToMatrix1(
    n=16,
    nrows=4,
    ncolumns=4)
    annotation (Placement(transformation(extent={{-20,-24},{0,-4}})));
  Modelica.Blocks.Routing.Replicator replicator1(nout=4)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-10,64})));
  Modelica.Blocks.Sources.Constant Nrel_CTWP(k=1) annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-38,64})));
  Modelica.Blocks.Sources.Constant opening_valve(k=0.5) annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-40,24})));
  Modelica.Blocks.Routing.Replicator replicator2(nout=4)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-10,24})));
  Modelica.Blocks.Sources.Constant T_set_CT(k=32 + 273.15) annotation (
      Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-86,-14})));
  Modelica.Blocks.Sources.Constant opening_CT(k=1) annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-74,-60})));
  Modelica.Blocks.Routing.Replicator replicator3(nout=16)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-44,-60})));
  Modelica.Blocks.Sources.Constant nCTs(k=11) annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={24,-44})));
equation

  connect(controlBus.valve_CT, arrayToMatrix.y) annotation (Line(
      points={{0,-100},{180,-100},{180,-60},{1,-60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(replicator.y, arrayToMatrix1.u) annotation (Line(points={{-39,-14},{-22,
          -14}},             color={0,0,127}));
  connect(controlBus.Tset_CT, arrayToMatrix1.y) annotation (Line(
      points={{0,-100},{180,-100},{180,-14},{1,-14}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.Nrel_CTWP, replicator1.y) annotation (Line(
      points={{0,-100},{180,-100},{180,64},{1,64}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(Nrel_CTWP.y, replicator1.u)
    annotation (Line(points={{-27,64},{-22,64}}, color={0,0,127}));
  connect(opening_valve.y, replicator2.u)
    annotation (Line(points={{-29,24},{-22,24}}, color={0,0,127}));
  connect(controlBus.valve_CTWP, replicator2.y) annotation (Line(
      points={{0,-100},{72,-100},{72,-98},{134,-98},{134,24},{1,24}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(T_set_CT.y, replicator.u)
    annotation (Line(points={{-75,-14},{-62,-14}}, color={0,0,127}));
  connect(replicator3.y, arrayToMatrix.u)
    annotation (Line(points={{-33,-60},{-22,-60}}, color={0,0,127}));
  connect(opening_CT.y, replicator3.u)
    annotation (Line(points={{-63,-60},{-56,-60}}, color={0,0,127}));
  connect(controlBus.numCTs, nCTs.y) annotation (Line(
      points={{0,-100},{44,-100},{44,-98},{68,-98},{68,-44},{35,-44}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
end CS_Constant;
