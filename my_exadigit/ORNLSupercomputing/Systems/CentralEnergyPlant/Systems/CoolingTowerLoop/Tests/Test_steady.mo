within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Tests;
model Test_steady
  extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across_pT_pT(
      redeclare Models.v0 simulator);
protected
  BaseClasses.ControlBus controlBus annotation (Placement(
        transformation(extent={{-20,20},{20,60}})));
public
  Modelica.Blocks.Sources.RealExpression HTWS_temp(y=298.15)
    annotation (Placement(transformation(extent={{-30,50},{-10,70}})));
equation
  connect(controlBus, simulator[1].controlBus) annotation (Line(
      points={{0,40},{0,10}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.T_EHX_HotSupply, HTWS_temp.y) annotation (Line(
      points={{0,40},{0,60},{-9,60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (experiment(StopTime=86400, __Dymola_Algorithm="Sdirk34hw"));
end Test_steady;
