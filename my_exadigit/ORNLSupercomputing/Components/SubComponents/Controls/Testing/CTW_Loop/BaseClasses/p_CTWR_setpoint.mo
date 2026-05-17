within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses;
model p_CTWR_setpoint "CTWR pressure setpoint for CTWP PID"
  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // CTWP1 is always set to be operational.
  // CTWP2 - CTWP4 are staged up when the operational pump speeds touch Nrel_max
  // and staged down when the operational pump speeds touch Nrel_min
  // The PID controller for the pump speeds is controlled by the CTWR static
  // pressure (gauge) setpoint.
  // The setpoint is fed the measured value and restricted to [22.3, 24.2] psi.
  // It is also informed by the HTWS temperature setpoint on page 16 of s1.
  // The CT temperature setpoint is a summation of the Towb and a manual
  // approach temperature of 17 degF.
  // Four CTs (4a-d) are always set to be open as the model is not
  // started from cold start.
  // The other CTs are staged up if HTWS is increasing and ps CTWR is at max
  // pressure and is set to stage down when HTWS is decreasing and ps CTWR is
  // at its min pressure.
extends Modelica.Blocks.Icons.Block;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi;
  import
  TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degF;
  import TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degF;
  Real TApp_Wat(start= 6.0) "Approach temperature in deg. F";
  Real p_CTWR_calculated(start=ps_start) "Gauge CTWR pressure in psi";
//   Real p_CTWR_calculated_int(start=ps_start);
//   Real p_CTWR_setpoint_int(start=ps_start);
  parameter Real adj=1.1  "Adjustable parameter for approach temp. in deg. F";
  parameter Real ps_start = 23.0 "Init. pressure boundary in psi";
  parameter Real ps_min = 22.3 "Min. pressure boundary in psi";
  parameter Real ps_max = 24.2 "Max. pressure boundary in psi";
  parameter Real ps_stage_up = 23.9 "Staging up pressure in psi";
  parameter Real ps_stage_down = 22.9 "Staging down pressure in psi";
  parameter Real CT_Offset=4.0 "PT-04 offset in deg F";
  parameter Real ctsp_tmp_deadband=0.5 "Deadband Temp. in deg F";
  parameter Real gain = 0.01 "Gain for delta T";
  parameter Real minPT_04Calc = 54.0 "Min. PT-04 Temp. in deg. F";
  parameter Real maxPT_04Calc = 84.0 "Min. PT-04 Temp. in deg. F";
  parameter Boolean conv_p_CTWR_gauge = false "Switch for gauge conversion";

  Modelica.Blocks.Sources.Constant offset(k=CT_Offset)
    "Temp. offset for CT App."
    annotation (Placement(transformation(extent={{-88,-10},{-80,-2}})));
  Modelica.Blocks.Math.Add add_offset "Add EHX Approach fixed -- 4.0 deg F"
    annotation (Placement(transformation(extent={{-66,-8},{-52,6}})));
  Modelica.Blocks.Sources.Constant zero_switch(k=0.0)
    annotation (Placement(transformation(extent={{7,-7},{-7,7}},
        rotation=180,
        origin={17,-25})));
  Modelica.Blocks.Math.Add     diff(k2=-1)
    annotation (Placement(transformation(extent={{-34,-64},{-18,-48}})));
  Modelica.Blocks.Math.Abs Abs
    annotation (Placement(transformation(extent={{-12,-64},{4,-48}})));
  Modelica.Blocks.Logical.GreaterThreshold Threshold(threshold=ctsp_tmp_deadband)
    "Check if diff is greater than threshold"
    annotation (Placement(transformation(extent={{12,-64},{28,-48}})));
  Modelica.Blocks.Logical.Switch switch
    annotation (Placement(transformation(extent={{44,-26},{58,-12}})));
  Modelica.Blocks.Math.Gain PT04_gain1(k=gain)
    annotation (Placement(transformation(extent={{68,-25.5},{82,-12.5}})));
  Modelica.Blocks.Math.Add ps_setpoint "ps setpoint based on measured ps"
    annotation (Placement(transformation(extent={{6,34},{20,48}})));
  Modelica.Blocks.Sources.Constant gaugeMin(k=ps_max)
    "max. gauge pressure"
    annotation (Placement(transformation(extent={{24,24},{34,34}})));
  Modelica.Blocks.Sources.Constant gaugeMax(k=ps_min)
    "min. gauge pressure"
    annotation (Placement(transformation(extent={{46,6},{58,18}})));
  Modelica.Blocks.Math.Min gaugeMinFilter
    annotation (Placement(transformation(extent={{42,40},{54,28}})));
  Modelica.Blocks.Math.Max gaugeMaxFilter
    annotation (Placement(transformation(extent={{70,36.5},{82,24}})));
  Modelica.Blocks.Interfaces.RealInput Towb "Towb" annotation (Placement(
        transformation(
        extent={{13.8,-14},{-13.8,14}},
        rotation=180,
        origin={-114.2,0}),iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,-40})));
  Modelica.Blocks.Interfaces.RealInput T_HTWS "T_HTWS" annotation (Placement(
        transformation(
        extent={{16,-16},{-16,16}},
        rotation=180,
        origin={-114,-60}),iconTransformation(
        extent={{10.2,-10},{-10.2,10}},
        rotation=180,
        origin={-110.2,0})));
  Modelica.Blocks.Interfaces.RealOutput p_CTWR_setpoint
    "CTWR header pressure setpoint" annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,0}),  iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,0})));
  Modelica.Blocks.Math.Min PT_04CalcMinFilter
    annotation (Placement(transformation(extent={{-78,-22},{-68,-32}})));
  Modelica.Blocks.Math.Max PT_04CalcMaxFilter
    annotation (Placement(transformation(extent={{-60,-55.5},{-50,-66}})));
  Modelica.Blocks.Sources.Constant maxPT_04(k=maxPT_04Calc)
    annotation (Placement(transformation(extent={{-98,-36},{-86,-24}})));
  Modelica.Blocks.Sources.Constant minPT_04(k=minPT_04Calc)
    annotation (Placement(transformation(extent={{-80,-70},{-68,-58}})));
  Modelica.Blocks.Sources.RealExpression CTApp(y=TApp_Wat)
    annotation (Placement(transformation(extent={{-98,20},{-86,32}})));
  Modelica.Blocks.Sources.RealExpression p_CTWR_psi(y=p_CTWR_calculated)
    "p CTWR gauge in psi"
    annotation (Placement(transformation(extent={{-22,38},{-6,54}})));
  Modelica.Blocks.Sources.RealExpression T_HTWS_F(y=
        TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degF(T_HTWS))
    "HTWS Temp. in deg. F"
    annotation (Placement(transformation(extent={{-58,-36},{-42,-20}})));
  Modelica.Blocks.Interfaces.RealOutput T_CT_setpoint "CT Temp. setpoint"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,-40}), iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,-40})));
  Modelica.Blocks.Math.Add CT_temp_setpoint
    "Add EHX Approach fixed -- 4.0 deg F"
    annotation (Placement(transformation(extent={{-78,14},{-64,28}})));
  Modelica.Blocks.Sources.RealExpression Towb_F(y=
        TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degF(Towb))
    "Towb in deg F"
    annotation (Placement(transformation(extent={{-98,6},{-86,18}})));
  Modelica.Blocks.Interfaces.RealOutput p_CTWR_measured
    "CTWR header pressure measured" annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,40}), iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,40})));
  Modelica.Blocks.Math.Sign sign
    annotation (Placement(transformation(extent={{-8,0},{6,14}})));
  Modelica.Blocks.Math.Product
                            PT04_gain2
    annotation (Placement(transformation(extent={{16,-3.5},{30,9.5}})));
  Modelica.Blocks.Interfaces.RealInput p_CTWR "CTWR header pressure"
    annotation (Placement(transformation(
        extent={{13.8,-14},{-13.8,14}},
        rotation=180,
        origin={-114.2,60}),iconTransformation(
        extent={{10.2,-10},{-10.2,10}},
        rotation=180,
        origin={-110.2,40})));
  Modelica.Blocks.Math.Max THTWSMaxFilter
    annotation (Placement(transformation(extent={{-36,-25.5},{-24,-38}})));
  Modelica.Blocks.Sources.Constant T_HTWSMin(k=minPT_04Calc) "min. T_HTWS"
    annotation (Placement(transformation(extent={{-58,-46},{-48,-36}})));
equation
  TApp_Wat =
    BaseClasses.CT_corr(
    TWetBul=to_degF(Towb), adj=adj);
  T_CT_setpoint =from_degF(max(CT_temp_setpoint.y, minPT_04Calc));

  // Original
//   p_CTWR_calculated = delay(p_CTWR_setpoint, 1.0);

 // approximation to avoid numerical jacobian
  der(p_CTWR_calculated) = (p_CTWR_setpoint-p_CTWR_calculated)/1;

// more accurate but no work
//   der(p_CTWR_setpoint_int) = (p_CTWR_setpoint-p_CTWR_setpoint_int)/(1.0/100);
//   p_CTWR_calculated = delay(p_CTWR_setpoint_int, 1.0);

// more accurate but no work
//     p_CTWR_calculated_int = delay(p_CTWR_setpoint, 1.0);
//   der(p_CTWR_calculated) = (p_CTWR_calculated_int-p_CTWR_calculated)/(1.0/100);


  p_CTWR_measured = if conv_p_CTWR_gauge then to_psi(p_CTWR) - 14.6959 else to_psi(p_CTWR);
  connect(offset.y, add_offset.u2) annotation (Line(points={{-79.6,-6},{-79.6,-5.2},
          {-67.4,-5.2}}, color={0,0,127}));
  connect(diff.y, Abs.u)
    annotation (Line(points={{-17.2,-56},{-13.6,-56}}, color={0,0,127}));
  connect(Abs.y, Threshold.u)
    annotation (Line(points={{4.8,-56},{10.4,-56}}, color={0,0,127}));
  connect(Threshold.y, switch.u2) annotation (Line(points={{28.8,-56},{32,-56},
          {32,-19},{42.6,-19}}, color={255,0,255}));
  connect(switch.y, PT04_gain1.u)
    annotation (Line(points={{58.7,-19},{66.6,-19}}, color={0,0,127}));
  connect(gaugeMinFilter.u1, gaugeMin.y) annotation (Line(points={{40.8,30.4},{
          37.65,30.4},{37.65,29},{34.5,29}},
                                 color={0,0,127}));
  connect(gaugeMax.y, gaugeMaxFilter.u1) annotation (Line(points={{58.6,12},{60,
          12},{60,26},{68,26},{68,26.5},{68.8,26.5}},
                                 color={0,0,127}));
  connect(gaugeMinFilter.y, gaugeMaxFilter.u2) annotation (Line(points={{54.6,34},
          {68.8,34}},                      color={0,0,127}));
  connect(ps_setpoint.y, gaugeMinFilter.u2) annotation (Line(points={{20.7,41},
          {20.7,37.6},{40.8,37.6}},                 color={0,0,127}));
  connect(zero_switch.y, switch.u3) annotation (Line(points={{24.7,-25},{24,-25},
          {24,-24.6},{42.6,-24.6}}, color={0,0,127}));
  connect(Abs.y, switch.u1) annotation (Line(points={{4.8,-56},{4.8,-14},{42.6,
          -14},{42.6,-13.4}}, color={0,0,127}));
  connect(gaugeMaxFilter.y, p_CTWR_setpoint) annotation (Line(points={{82.6,
          30.25},{92,30.25},{92,0},{113.8,0}},             color={0,0,127}));
  connect(maxPT_04.y, PT_04CalcMinFilter.u1)
    annotation (Line(points={{-85.4,-30},{-79,-30}}, color={0,0,127}));
  connect(add_offset.y, PT_04CalcMinFilter.u2) annotation (Line(points={{-51.3,
          -1},{-46,-1},{-46,-16},{-79,-16},{-79,-24}}, color={0,0,127}));
  connect(PT_04CalcMinFilter.y, PT_04CalcMaxFilter.u2) annotation (Line(points={{-67.5,
          -27},{-61,-27},{-61,-57.6}},            color={0,0,127}));
  connect(minPT_04.y, PT_04CalcMaxFilter.u1) annotation (Line(points={{-67.4,-64},
          {-67.4,-63.9},{-61,-63.9}},         color={0,0,127}));
  connect(p_CTWR_psi.y, ps_setpoint.u1) annotation (Line(points={{-5.2,46},{-5.2,
          45.2},{4.6,45.2}}, color={0,0,127}));
  connect(CTApp.y, CT_temp_setpoint.u1) annotation (Line(points={{-85.4,26},{-85.4,
          25.2},{-79.4,25.2}}, color={0,0,127}));
  connect(Towb_F.y, CT_temp_setpoint.u2) annotation (Line(points={{-85.4,12},{-84,
          12},{-84,16.8},{-79.4,16.8}}, color={0,0,127}));
  connect(CT_temp_setpoint.y, add_offset.u1) annotation (Line(points={{-63.3,21},
          {-58,21},{-58,10},{-72,10},{-72,3.2},{-67.4,3.2}}, color={0,0,127}));
  connect(PT_04CalcMaxFilter.y, diff.u2) annotation (Line(points={{-49.5,-60.75},
          {-49.5,-60.8},{-35.6,-60.8}}, color={0,0,127}));
  connect(diff.y, sign.u) annotation (Line(points={{-17.2,-56},{-16,-56},{-16,7},
          {-9.4,7}}, color={0,0,127}));
  connect(PT04_gain1.y, PT04_gain2.u2) annotation (Line(points={{82.7,-19},{86,-19},
          {86,-6},{14.6,-6},{14.6,-0.9}}, color={0,0,127}));
  connect(sign.y, PT04_gain2.u1)
    annotation (Line(points={{6.7,7},{6.7,6.9},{14.6,6.9}}, color={0,0,127}));
  connect(PT04_gain2.y, ps_setpoint.u2) annotation (Line(points={{30.7,3},{30.7,
          2},{34,2},{34,20},{4.6,20},{4.6,36.8}}, color={0,0,127}));
  connect(T_HTWS_F.y, THTWSMaxFilter.u2)
    annotation (Line(points={{-41.2,-28},{-37.2,-28}}, color={0,0,127}));
  connect(THTWSMaxFilter.y, diff.u1) annotation (Line(points={{-23.4,-31.75},{
          -20,-31.75},{-20,-44},{-42,-44},{-42,-51.2},{-35.6,-51.2}}, color={0,
          0,127}));
  connect(T_HTWSMin.y, THTWSMaxFilter.u1) annotation (Line(points={{-47.5,-41},
          {-47.5,-40},{-42,-40},{-42,-35.5},{-37.2,-35.5}}, color={0,0,127}));
end p_CTWR_setpoint;
