within ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers;
model CDU_HEX "Cooling Distribution Unit HEX"
  replaceable package Medium_1 =
      ORNLSupercomputing.Components.SubComponents.Media.Medium;
  replaceable package Medium_2 =
      ORNLSupercomputing.Components.SubComponents.Media.Medium;

  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  parameter TRANSFORM.Units.HydraulicResistance R_Sec = 11000
  "Sec. side hydraulic resistance";
  parameter TRANSFORM.Units.HydraulicResistance R_Pri = 8000
  "Pri. side hydraulic resistance";
  parameter Modelica.Units.SI.Pressure CDU_p_a_start_1 =  from_psi(64.7) annotation(Dialog(group="Init_Sec_side"));
  parameter Modelica.Units.SI.Pressure CDU_p_b_start_1 =  from_psi(36.5) annotation(Dialog(group="Init_Sec_side"));
  parameter Modelica.Units.SI.Pressure CDU_p_a_start_2 =  from_psi(79.7) annotation(Dialog(group="Init_Pri_side"));
  parameter Modelica.Units.SI.Pressure CDU_p_b_start_2 =  from_psi(59.7) annotation(Dialog(group="Init_Pri_side"));
  parameter Modelica.Units.SI.Temperature CDU_T_a_start_1 =  from_degC(40.0) annotation(Dialog(group="Init_Sec_side"));
  parameter Modelica.Units.SI.Temperature CDU_T_b_start_1 =  from_degC(30.0) annotation(Dialog(group="Init_Sec_side"));
  parameter Modelica.Units.SI.Temperature CDU_T_a_start_2 =  from_degC(22.5) annotation(Dialog(group="Init_Pri_side"));
  parameter Modelica.Units.SI.Temperature CDU_T_b_start_2 =  from_degC(35.0) annotation(Dialog(group="Init_Pri_side"));
  parameter Modelica.Units.SI.MassFlowRate CDU_m_flow_start1 = 15.0 annotation(Dialog(group="Init_Sec_side"));
  parameter Modelica.Units.SI.MassFlowRate CDU_m_flow_start2 = 12.0 annotation(Dialog(group="Init_Pri_side"));
  parameter Real UA_corr_mod = 1.0 annotation(Dialog(group="UA correlation"));

  TRANSFORM.Fluid.Interfaces.FluidPort_State
                                        port_b2(redeclare package Medium =
        Medium_2)
    annotation (Placement(transformation(extent={{-110,-50},{-90,-30}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_State
                                        port_b1(redeclare package Medium =
        Medium_1)
    annotation (Placement(transformation(extent={{90,30},{110,50}})));
  Modelica.Blocks.Tables.CombiTable2Ds UATable(table=[0,0.001261804,0.002523608,
        0.003785412,0.005047216,0.00630902,0.007570824,0.008832627,0.010094431,0.011356235,
        0.012618039,0.013879843,0.015141647,0.016403451,0.017665255,0.018927059,
        0.021450667,0.025236079; 0.001261804,1.8685,3.2825,4.3935,5.2015,5.757,5.959,
        6.06,6.06,6.06,6.06,6.06,6.06,6.06,6.06,6.06,6.06,6.06; 0.002523608,3.737,
        6.565,8.787,10.403,11.514,11.918,12.12,12.12,12.12,12.12,12.12,12.12,12.12,
        12.12,12.12,12.12,12.12; 0.003785412,4.545,9.09,12.625,14.847,16.48341816,
        17.17,17.17,17.17,17.17,17.17,17.17,17.17,17.17,17.17,17.17,17.17,17.17;
        0.005047216,6.229706228,11.0418366,14.66070692,17.29216133,19.19,20.503,
        20.907,21.21,21.412,21.513,21.513,21.513,21.513,21.513,21.513,21.51204333,
        21.513; 0.00630902,6.565,11.615,17.05134633,20.34648588,22.927,24.393823,
        25.527952,26.2000969,26.462,26.664,26.664,26.664,26.664,26.6351443,26.664,
        26.65770568,26.664; 0.007570824,6.565,12.524,17.17,21.614,24.442,26.7754943,
        28.40885338,29.55284757,30.4153921,30.84646268,31.01740316,31.44488623,31.36545078,
        31.39631121,31.55723378,31.64910047,31.714; 0.008832627,6.565,12.524,17.271,
        21.917,25.452,28.53682199,30.70646925,32.3747862,33.64248471,34.4385373,
        34.9301851,35.53981593,35.70385802,35.90495937,36.16218237,36.45556361,36.5430806;
        0.010094431,6.565,12.524,17.372,22.119,25.856,29.76867213,32.48863283,34.70803172,
        36.41105267,37.61214661,38.46681669,39.28388439,39.73142072,40.13370388,
        40.51062231,41.04643103,41.34070075; 0.011356235,6.565,12.524,17.372,22.22,
        26.058,30.56191078,33.82317734,36.59470307,38.74652132,40.37633069,41.62089713,
        42.66829202,43.42684015,44.05515986,44.57649754,45.39103862,45.94429457;
        0.012618039,6.565,12.524,17.372,22.22,26.058,31.007404,34.777936,38.0769192,
        40.674316,42.7401296,44.3860256,45.6842392,46.7688176,47.6419424,48.333752,
        49.45872232,50.3244216; 0.015141647,6.565,12.524,17.372,22.321,26.159,31.108,
        35.81942861,39.99646153,43.40858477,46.30273217,48.72382337,50.57555382,
        52.30725166,53.70194757,54.81817436,56.64066167,58.29651352; 0.017665255,
        6.565,12.524,17.342811,22.422,26.159,31.12924394,36.15577638,40.80361022,
        44.81726166,48.37227485,51.42900349,53.8874314,56.17633316,58.09464022,59.75544091,
        62.3469364,65.02145292; 0.020188863,6.565,12.524,17.372,22.44307264,26.159,
        31.46620902,36.32964506,40.83531679,45.10374938,49.02107817,52.45035945,
        55.54947512,58.20567235,60.60094116,62.93710316,66.33223383,70.2637162;
        0.021450667,6.565,12.524,17.372,22.422,26.159,31.512,36.41657939,40.804,
        45.1773,49.0759,52.621,55.9439,58.74097235,61.307,63.94710316,67.78663383,
        72.3039162; 0.022712471,6.565,12.524,17.372,22.422,26.159,31.512,36.36,40.804,
        45.1874,49.0961,52.6715,56.156,59.02377235,61.711,64.55310316,68.82693383,
        73.8896162])
    annotation (Placement(transformation(extent={{2,42},{22,62}})));
  Modelica.Blocks.Sources.RealExpression port_a1_volFlow(y=port_a1.m_flow/
        CDU_HEX.Medium_1.density_ph(port_b1.p, port_a1.h_outflow))
    annotation (Placement(transformation(extent={{-34,50},{-14,70}})));
  Modelica.Blocks.Sources.RealExpression port_a2_volFlow(y=port_a2.m_flow/
        CDU_HEX.Medium_2.density_ph(port_b2.p, port_a2.h_outflow))
    annotation (Placement(transformation(extent={{-34,32},{-14,52}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow
                                  port_a1(redeclare package Medium = Medium_1)
    annotation (Placement(transformation(extent={{-110,30},{-90,50}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow
                                  port_a2(redeclare package Medium = Medium_2)
    annotation (Placement(transformation(extent={{90,-50},{110,-30}})));
  BaseClasses.Simple_ITD_HX CDU_HEX(
    redeclare package Medium_1 = Medium_1,
    redeclare package Medium_2 = Medium_2,
    nV=5,
    counterCurrent=true,
    p_a_start_1=CDU_p_a_start_1,
    p_b_start_1=CDU_p_b_start_1,
    p_a_start_2=CDU_p_a_start_2,
    p_b_start_2=CDU_p_b_start_2,
    V_1=0.051,
    V_2=0.051,
    UA=UATable.y*1e3*UA_corr_mod,
    T_a_start_1=CDU_T_a_start_1,
    T_b_start_1=CDU_T_b_start_1,
    m_flow_start_1=CDU_m_flow_start1,
    T_a_start_2=CDU_T_a_start_2,
    T_b_start_2=CDU_T_b_start_2,
    m_flow_start_2=CDU_m_flow_start2,
    R_1=R_Sec,
    R_2=R_Pri)
    annotation (Placement(transformation(extent={{-28,-32},{30,24}})));
equation
  connect(port_a1_volFlow.y, UATable.u1) annotation (Line(points={{-13,60},{
          -6,60},{-6,58},{0,58}}, color={0,0,127}));
  connect(port_a2_volFlow.y, UATable.u2) annotation (Line(points={{-13,42},{
          -6,42},{-6,46},{0,46}}, color={0,0,127}));
  connect(port_a1,CDU_HEX. port_a1) annotation (Line(points={{-100,40},{-40,
          40},{-40,7.2},{-28,7.2}},
                            color={0,127,255}));
  connect(port_b2,CDU_HEX. port_b2) annotation (Line(points={{-100,-40},{-34,
          -40},{-34,-15.2},{-28,-15.2}},
                              color={0,127,255}));
  connect(port_b1,CDU_HEX. port_b1) annotation (Line(points={{100,40},{40,40},
          {40,7.2},{30,7.2}},
                      color={0,127,255}));
  connect(port_a2,CDU_HEX. port_a2) annotation (Line(points={{100,-40},{40,
          -40},{40,-15.2},{30,-15.2}},
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
          visible=true)}));
end CDU_HEX;
