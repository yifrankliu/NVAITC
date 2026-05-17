within ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers;
model coolingTower "Cooling Tower SS component from the buildings library"
  package Medium_W =  ORNLSupercomputing.Components.SubComponents.Media.Medium;
  import TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_bar;
  parameter Modelica.Units.SI.MassFlowRate CT_mflow_nom = 3992*0.063*0.25;
  parameter Modelica.Units.SI.Pressure CT_dp_nom = 19994.8;
  parameter Modelica.Units.SI.Power CT_fan_power_nom = 0.25*149140;
  parameter Modelica.Units.SI.Pressure CT_pinit = from_bar(2.0) annotation(Dialog(group="Initialization"));
  parameter Modelica.Units.SI.Temperature CT_Tinit = from_degC(20.0) annotation(Dialog(group="Initialization"));
  ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers.BaseClasses.YorkCalc
    CT(
    p_start=CT_pinit,
    T_start=CT_Tinit,
    fraPFan_nominal=CT_fan_power_nom/CT.m_flow_nominal,
    PFan_nominal=CT_fan_power_nom,
    redeclare package Medium = Medium_W,
    m_flow_nominal=CT_mflow_nom,
    dp_nominal=CT_dp_nom,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
    show_T=true) "Cooling tower"
    annotation (Placement(transformation(extent={{-18,-17},{10,13}})));
  Buildings.Controls.Continuous.LimPID conFan(
    k=1,
    Ti=60,
    Td=10,
    reverseActing=false,
    initType=Modelica.Blocks.Types.Init.InitialState)
    "Controller for tower fan"
    annotation (Placement(transformation(extent={{-22,36},{-2,56}})));
  Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(final
      computeWetBulbTemperature=true, filNam=
        Modelica.Utilities.Files.loadResource("modelica://Buildings/Resources/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos"))
    annotation (Placement(transformation(extent={{-98,68},{-78,88}})));
  Buildings.BoundaryConditions.WeatherData.Bus weaBus "Weather data bus"
    annotation (Placement(transformation(extent={{-68,68},{-48,88}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow
                    port_a(redeclare package Medium = Medium_W)
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_State
                                        port_b(redeclare package Medium =
        Medium_W)
    annotation (Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Blocks.Interfaces.RealInput waterSPTLvg
    "Enter Leaving water temperature setpoint" annotation (Placement(
        transformation(extent={{-72,30},{-40,62}}), iconTransformation(extent={{
            -78,20},{-46,52}})));
equation
  connect(conFan.y, CT.y) annotation (Line(
      points={{-1,46},{18,46},{18,18},{-20.8,18},{-20.8,10}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(CT.TLvg, conFan.u_m) annotation (Line(
      points={{11.4,-11},{18,-11},{18,24},{-12,24},{-12,34}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(weaDat.weaBus,weaBus)
   annotation (Line(points={{-78,78},{-58,78}},color={255,204,51}));
  connect(CT.port_b, port_b)
    annotation (Line(points={{10,-2},{56,-2},{56,0},{100,0}},
                                              color={0,127,255}));
  connect(CT.port_a, port_a)
    annotation (Line(points={{-18,-2},{-58,-2},{-58,0},{-100,0}},
                                                color={0,127,255}));
  connect(waterSPTLvg, conFan.u_s)
    annotation (Line(points={{-56,46},{-24,46}}, color={0,0,127}));
  connect(weaBus.TWetBul, CT.TAir) annotation (Line(
      points={{-57.95,78.05},{-57.95,4},{-20.8,4}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%first",
      index=-1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,
            -100},{100,100}}), graphics={
        Text(
          extent={{-50,4},{42,-110}},
          textColor={255,255,255},
          fillColor={0,127,0},
          fillPattern=FillPattern.Solid,
          textString="York"),
        Rectangle(
          extent={{-70,86},{70,-80}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={95,95,95},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-102,5},{99,-5}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{76,-58},{100,-62}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{76,-60},{80,-4}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-100,81},{-70,78}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{70,56},{82,52}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{78,54},{82,80}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{0,62},{54,50}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{-54,62},{0,50}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{78,82},{100,78}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid)}));
end coolingTower;
