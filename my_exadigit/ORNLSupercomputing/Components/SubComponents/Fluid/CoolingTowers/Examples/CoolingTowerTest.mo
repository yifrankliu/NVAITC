within ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers.Examples;
model CoolingTowerTest "Replicate York CC Test for generalized media"
  extends Modelica.Icons.Example;
  extends
    Buildings.Fluid.HeatExchangers.CoolingTowers.Examples.BaseClasses.PartialStaticTwoPortCoolingTower(
    m_flow_nominal=3992*0.063,
    redeclare BaseClasses.YorkCalc                                  tow(
      m_flow_nominal=3993*0.063*0.25,
      dp_nominal=20000,
      fraPFan_nominal=0.25*149140/m_flow_nominal,
      PFan_nominal=0.25*149140),
    weaDat(filNam=Modelica.Utilities.Files.loadResource(
          "modelica://Buildings/Resources/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos"),
           final computeWetBulbTemperature=true),
    TSwi(k=273.15 + 5/9*(90 - 32)),
    exp(T=(5/9*(110 - 32)) + 273.15),
    fixHeaFlo(Q_flow=0.01*3593*3516.8528420667));

  Modelica.Blocks.Sources.Constant TSetLea(k=273.15 + 5/9*(65 - 32))
    "Setpoint for leaving temperature"
    annotation (Placement(transformation(extent={{-80,0},{-60,20}})));
  Buildings.Controls.Continuous.LimPID conFan(
    k=1,
    Ti=60,
    Td=10,
    reverseActing=false,
    initType=Modelica.Blocks.Types.Init.InitialState)
    "Controller for tower fan"
    annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
equation
  connect(TSetLea.y, conFan.u_s) annotation (Line(
      points={{-59,10},{-42,10}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(conFan.y, tow.y) annotation (Line(
      points={{-19,10},{10,10},{10,-42},{20,-42}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(tow.TLvg, conFan.u_m) annotation (Line(
      points={{43,-56},{50,-56},{50,-20},{-30,-20},{-30,-2}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(weaBus.TWetBul, tow.TAir) annotation (Line(
      points={{-59.95,50.05},{8,50.05},{8,-46},{20,-46}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%first",
      index=-1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
annotation(Diagram(coordinateSystem(preserveAspectRatio=true, extent={{-140,-260},
            {140,100}})),
experiment(
      StopTime=86400,
      Tolerance=1e-06,
      __Dymola_Algorithm="Esdirk45a"),
__Dymola_Commands(file="modelica://Buildings/Resources/Scripts/Dymola/Fluid/HeatExchangers/CoolingTowers/Examples/YorkCalc.mos"
        "Simulate and plot"),
    Icon(coordinateSystem(preserveAspectRatio=true, extent={{-100,-100},{100,
            100}})),
    Documentation(info="<html>
<p>
This example illustrates the use of the cooling tower model
<a href=\"modelica://Buildings.Fluid.HeatExchangers.CoolingTowers.YorkCalc\">
Buildings.Fluid.HeatExchangers.CoolingTowers.YorkCalc</a>.
Heat is injected into the volume <code>vol</code>. An on/off controller
switches the cooling loop water pump on or off based on the temperature of
this volume.
The cooling tower outlet temperature is controlled to track a fixed temperature.
</p>
</html>", revisions="<html>
<ul>
<li>
July 12, 2011, by Michael Wetter:<br/>
First implementation.
</li>
</ul>
</html>"));
end CoolingTowerTest;
