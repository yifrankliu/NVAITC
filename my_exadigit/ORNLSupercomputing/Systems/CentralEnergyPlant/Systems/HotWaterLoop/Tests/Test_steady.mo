within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.HotWaterLoop.Tests;
model Test_steady
  extends
    TemplatesCSM.BaseClasses.Tests.PartialTest_FourPort_across_mT_pT_mT_pT(
      redeclare Models.v0 simulator);
  Modelica.Blocks.Sources.RealExpression numCTs(y=12) annotation (
     Placement(transformation(extent={{-30,50},{-10,70}})));
protected
  BaseClasses.ControlBus controlBus annotation (Placement(
        transformation(extent={{-20,20},{20,60}})));
equation
  connect(controlBus, simulator[1].controlBus) annotation (Line(
      points={{0,40},{0,10}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.numCTs, numCTs.y) annotation (Line(
      points={{0,40},{0,60},{-9,60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (experiment(
      StopTime=86400,
      __Dymola_NumberOfIntervals=100,
      __Dymola_Algorithm="Sdirk34hw"),
      __Dymola_experimentSetupOutput);
end Test_steady;
