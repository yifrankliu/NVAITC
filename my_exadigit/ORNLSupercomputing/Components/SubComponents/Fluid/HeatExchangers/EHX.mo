within ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers;
model EHX "EHX Heat Exchanger"
  replaceable package Medium_1 =
      ORNLSupercomputing.Components.SubComponents.Media.Medium;
  replaceable package Medium_2 =
      ORNLSupercomputing.Components.SubComponents.Media.Medium;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  parameter Modelica.Units.SI.Pressure EHX_p_a_start_1 =  from_psi(83.7) annotation(Dialog(group="Initialization1"));
  parameter Modelica.Units.SI.Pressure EHX_p_b_start_1 =  EHX_p_a_start_1-0.001 annotation(Dialog(group="Initialization1"));
  parameter Modelica.Units.SI.Pressure EHX_p_a_start_2 =  from_psi(42.7) annotation(Dialog(group="Initialization2"));
  parameter Modelica.Units.SI.Pressure EHX_p_b_start_2 =  EHX_p_a_start_2-0.001 annotation(Dialog(group="Initialization2"));
  parameter Modelica.Units.SI.Temperature EHX_T_a_start_1 =  from_degC(30.0) annotation(Dialog(group="Initialization1"));
  parameter Modelica.Units.SI.Temperature EHX_T_b_start_1 =  from_degC(22.5) annotation(Dialog(group="Initialization1"));
  parameter Modelica.Units.SI.Temperature EHX_T_a_start_2 =  from_degC(20.0) annotation(Dialog(group="Initialization2"));
  parameter Modelica.Units.SI.Temperature EHX_T_b_start_2 =  from_degC(25.0) annotation(Dialog(group="Initialization2"));
  parameter Modelica.Units.SI.MassFlowRate EHX_m_flow_start1 = 100.0 annotation(Dialog(group="Initialization1"));
  parameter Modelica.Units.SI.MassFlowRate EHX_m_flow_start2 = 150.0 annotation(Dialog(group="Initialization2"));
  parameter TRANSFORM.Units.HydraulicResistance R_1 = 2.3*6894.76/(2572*0.063) annotation(Dialog(group="HEX Parameters"));
  parameter TRANSFORM.Units.HydraulicResistance R_2 = 5.3*6894.76/(3992*0.063) annotation(Dialog(group="HEX Parameters"));
  parameter Modelica.Units.SI.ThermalConductance UA = (923.4*5.6783)*(8287*0.092903) annotation(Dialog(group="HEX Parameters"));
  TRANSFORM.Fluid.Interfaces.FluidPort_State
                                        port_b2(redeclare package Medium =
        Medium_2)
    annotation (Placement(transformation(extent={{-110,-50},{-90,-30}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_State
                                        port_b1(redeclare package Medium =
        Medium_1)
    annotation (Placement(transformation(extent={{90,30},{110,50}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow
                                  port_a1(redeclare package Medium = Medium_1)
    annotation (Placement(transformation(extent={{-110,30},{-90,50}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow
                                  port_a2(redeclare package Medium = Medium_2)
    annotation (Placement(transformation(extent={{90,-50},{110,-30}})));
  TRANSFORM.HeatExchangers.Simple_HX HTWP_EHX_HEX(
    redeclare package Medium_1 = Medium_1,
    redeclare package Medium_2 = Medium_2,
    nV=5,
    V_1=0.1,
    V_2=0.1,
    UA=UA,
    p_a_start_1=EHX_p_a_start_1,
    p_b_start_1=EHX_p_b_start_1,
    T_a_start_1=EHX_T_a_start_1,
    T_b_start_1=EHX_T_b_start_1,
    m_flow_start_1=EHX_m_flow_start1,
    p_a_start_2=EHX_p_a_start_2,
    p_b_start_2=EHX_p_b_start_2,
    T_a_start_2=EHX_T_a_start_2,
    T_b_start_2=EHX_T_b_start_2,
    m_flow_start_2=EHX_m_flow_start2,
    R_1=R_1,
    R_2=R_2)
    annotation (Placement(transformation(extent={{-28,-30},{26,28}})));
equation
  connect(port_a1, HTWP_EHX_HEX.port_a1) annotation (Line(points={{-100,40},{
          -34,40},{-34,10.6},{-28,10.6}},
                                color={0,127,255}));
  connect(port_b2, HTWP_EHX_HEX.port_b2) annotation (Line(points={{-100,-40},
          {-42,-40},{-42,-12.6},{-28,-12.6}},
                                   color={0,127,255}));
  connect(port_b1, HTWP_EHX_HEX.port_b1) annotation (Line(points={{100,40},{
          42,40},{42,10.6},{26,10.6}},
                             color={0,127,255}));
  connect(port_a2, HTWP_EHX_HEX.port_a2) annotation (Line(points={{100,-40},{
          42,-40},{42,-12.6},{26,-12.6}},
                                color={0,127,255}));
  annotation (defaultComponentName="heatExchanger",
              Diagram(coordinateSystem(preserveAspectRatio=false)),
        Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{100,100}}),
        graphics={
        Rectangle(
          extent={{-100,60},{100,-60}},
          lineColor={0,0,0},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Line(points={{-88,-40},{-60,-40},{-30,0},{0,-40},{30,0},{60,-40},{
              88,-40}},
            color={28,108,200}),
        Line(points={{-88,40},{-30,40},{0,0},{30,40},{88,40}}, color={238,46,47}),
        Text(
          extent={{-149,-68},{151,-108}},
          lineColor={0,0,255},
          textString="%name",
          visible=DynamicSelect(true, showName))}));
end EHX;
