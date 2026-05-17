within ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers;
model coolingTower_Towb
  "Cooling Tower SS component from the buildings with Towb as input"
  replaceable package Medium_W =
      ORNLSupercomputing.Components.SubComponents.Media.Medium;
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
    annotation (Placement(transformation(extent={{-16,-15},{12,15}})));
  Buildings.Controls.Continuous.LimPID conFan(
    k=1,
    Ti=60,
    Td=10,
    reverseActing=false,
    initType=Modelica.Blocks.Types.Init.InitialState)
    "Controller for tower fan"
    annotation (Placement(transformation(extent={{-70,60},{-50,80}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow
                    port_a(redeclare package Medium = Medium_W)
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_State
                                        port_b(redeclare package Medium =
        Medium_W)
    annotation (Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Blocks.Interfaces.RealInput waterSPTLvg
    "Enter Leaving water temperature setpoint" annotation (Placement(
        transformation(extent={{-132,54},{-100,86}}),
                                                    iconTransformation(extent={{-16,-16},
            {16,16}},
        rotation=270,
        origin={-40,102})));
  Modelica.Blocks.Interfaces.RealInput Towb "Enter wet bulb temperature"
    annotation (Placement(transformation(extent={{-132,24},{-100,56}}),
        iconTransformation(extent={{-16,-16},{16,16}},
        rotation=270,
        origin={40,102})));
equation
  connect(conFan.y, CT.y) annotation (Line(
      points={{-49,70},{-40,70},{-40,12},{-18.8,12}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(CT.TLvg, conFan.u_m) annotation (Line(
      points={{13.4,-9},{20,-9},{20,-20},{-60,-20},{-60,58}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(CT.port_b, port_b)
    annotation (Line(points={{12,0},{100,0}}, color={0,127,255}));
  connect(CT.port_a, port_a)
    annotation (Line(points={{-16,0},{-100,0}}, color={0,127,255}));
  connect(waterSPTLvg, conFan.u_s)
    annotation (Line(points={{-116,70},{-72,70}},color={0,0,127}));
  connect(Towb, CT.TAir) annotation (Line(points={{-116,40},{-80,40},{-80,6},{
          -18.8,6}},  color={0,0,127}));
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
end coolingTower_Towb;
