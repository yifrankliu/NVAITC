within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Controls;
model CS_PumpAndValveControl
  extends BaseClasses.PartialControls(redeclare Data.v0 data);

  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // Two CDUPs are always set to be operational
  // The CDUPs are staged up when the operational pump speeds touch Nrel_max
  // and staged down when the operational pump speeds touch Nrel_min.
  // The PID controller for the pump speeds is controlled by the dP setpoint.
  // The setpoint is fixed at 27.5 psi.
  // The primary flow control valve is controlled by the sec. temp. setpoint of
  // 28.0 deg C.
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  parameter Real dp_nom=27.5;
  parameter Real Tsec_supply_nom=28.0;
  //deg. C
  parameter Real CDUP_Nrel_min=52.0;
  parameter Real CDUP_Nrel_max=75.0;
  parameter Real CDUP_Nrel_start=64.0;
  parameter Real CDU_CV_min=0.05;
  parameter Real CDU_CV_max=1.0;
  parameter Real CDU_CV_start=0.5;
  // Control System tuning parameters
  parameter Real gain_CDUP=0.1;
  parameter Real Ti_CDUP=100.0;
  // s
  parameter Real Td_CDUP=30.0;
  // s
  //
  parameter Real gain_CV=-0.9;
  parameter Real Ti_CV=35.0;
  // s
  parameter Real Td_CV=9.0;
  // s
  parameter Real db_CV=0.3;
  //deg. C
  parameter Real dbr_CV=0.1;

  Modelica.Blocks.Sources.Constant Tsec_setpoint(k=
        Tsec_supply_nom) annotation (Placement(transformation(
          extent={{-70,20},{-50,40}})));
  ORNLSupercomputing.Components.SubComponents.Controls.LimPID_Deadband_dbr
    PID_CDUCV(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    k=gain_CV,
    Ti=Ti_CV,
    Td=Td_CV,
    yMax=CDU_CV_max,
    yMin=CDU_CV_min,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=CDU_CV_start,
    strict=true,
    deadband=db_CV,
    deadbandRatio=dbr_CV) annotation (Placement(transformation(
          extent={{-30,20},{-10,40}})));

  Modelica.Blocks.Sources.Constant delay(k=1.0) annotation (
      Placement(transformation(extent={{-80,80},{-60,100}})));
  Modelica.Blocks.Sources.ContinuousClock clock(offset=0,
      startTime=0) annotation (Placement(transformation(
          extent={{-80,50},{-60,70}})));
  Modelica.Blocks.Logical.Greater delayControl annotation (
      Placement(transformation(extent={{20,90},{40,70}})));
  Modelica.Blocks.Logical.Switch switch_setpoint annotation (
      Placement(transformation(extent={{80,-48},{100,-28}})));
  Modelica.Blocks.Sources.Constant Pump_start(k=
        CDUP_Nrel_start) annotation (Placement(transformation(
          extent={{10,-70},{30,-50}})));
  Modelica.Blocks.Logical.Switch switch_setpoint1 annotation (
     Placement(transformation(extent={{80,12},{100,32}})));
  Modelica.Blocks.Sources.Constant valve_start(k=0.5)
    annotation (Placement(transformation(extent={{20,-10},{40,10}})));
  Modelica.Blocks.Math.Add add(k2=-1) annotation (Placement(
        transformation(extent={{-100,10},{-80,-10}})));
  Modelica.Blocks.Sources.Constant conv_to_degC(k=273.15)
    annotation (Placement(transformation(extent={{-140,0},{-120,20}})));
  Modelica.Blocks.Continuous.Filter filter(filterType=
        Modelica.Blocks.Types.FilterType.LowPass, f_cut=5e-4)
    annotation (Placement(transformation(extent={{20,40},{40,20}})));
  Modelica.Blocks.Math.Add dP(k1=-1, k2=+1)
    annotation (Placement(transformation(extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-130,-60})));
  Modelica.Blocks.Sources.Constant       dPSetPoint(k=dp_nom)
    annotation (Placement(transformation(extent={{-60,-40},{-40,-20}})));
  Modelica.Blocks.Math.Gain gain(k=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(1.0))
    annotation (Placement(transformation(extent={{-100,-70},{-80,-50}})));
  Modelica.Blocks.Continuous.LimPID PID_CDUP(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    k=gain_CDUP,
    Ti=Ti_CDUP,
    Td=Td_CDUP,
    yMax=CDUP_Nrel_max,
    yMin=CDUP_Nrel_min,
    withFeedForward=false,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=CDUP_Nrel_start)
    annotation (Placement(transformation(extent={{-20,-40},{0,-20}})));
  Modelica.Blocks.Continuous.Filter filter_CDUP(filterType=Modelica.Blocks.Types.FilterType.LowPass,
      f_cut=1e-3)
    annotation (Placement(transformation(extent={{10,-20},{30,-40}})));
equation
  connect(Tsec_setpoint.y, PID_CDUCV.u_s) annotation (Line(
        points={{-49,30},{-32,30}},  color={0,0,127}));
  connect(clock.y, delayControl.u1) annotation (Line(points={{-59,60},{-40,60},
          {-40,80},{18,80}},                     color={0,0,127}));
  connect(delay.y, delayControl.u2) annotation (Line(points={{-59,90},{-40,90},
          {-40,88},{18,88}},   color={0,0,127}));
  connect(Pump_start.y, switch_setpoint.u3) annotation (Line(
        points={{31,-60},{50,-60},{50,-46},{78,-46}},   color
        ={0,0,127}));
  connect(switch_setpoint.u2, delayControl.y) annotation (
      Line(points={{78,-38},{54,-38},{54,80},{41,80}},  color
        ={255,0,255}));
  connect(switch_setpoint1.u2, delayControl.y) annotation (
      Line(points={{78,22},{54,22},{54,80},{41,80}},
        color={255,0,255}));
  connect(valve_start.y, switch_setpoint1.u3) annotation (
      Line(points={{41,0},{60,0},{60,14},{78,14}},
        color={0,0,127}));
  connect(add.u2, conv_to_degC.y) annotation (Line(points={{-102,6},{-110,6},{
          -110,10},{-119,10}},            color={0,0,127}));
  connect(add.y, PID_CDUCV.u_m) annotation (Line(points={{-79,0},{-20,0},{-20,
          18}},                 color={0,0,127}));
  connect(filter.u, PID_CDUCV.y) annotation (Line(points={{18,30},{-9,30}},
                        color={0,0,127}));
  connect(filter.y, switch_setpoint1.u1) annotation (Line(
        points={{41,30},{78,30}},
        color={0,0,127}));

  connect(controlBus.T_CabSup, add.u1) annotation (Line(
      points={{0,-100},{-180,-100},{-180,-6},{-102,-6}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.opening_CDUOut, switch_setpoint1.y)
    annotation (Line(
      points={{0,-100},{180,-100},{180,22},{101,22}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(controlBus.CDUP_Nrel, switch_setpoint.y) annotation (Line(
      points={{0,-100},{180,-100},{180,-38},{101,-38}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(dP.y, gain.u)
    annotation (Line(points={{-119,-60},{-102,-60}},color={0,0,127}));
  connect(gain.y, PID_CDUP.u_m)
    annotation (Line(points={{-79,-60},{-10,-60},{-10,-42}},
                                                         color={0,0,127}));
  connect(dPSetPoint.y, PID_CDUP.u_s)
    annotation (Line(points={{-39,-30},{-22,-30}}, color={0,0,127}));
  connect(PID_CDUP.y, filter_CDUP.u)
    annotation (Line(points={{1,-30},{8,-30}},     color={0,0,127}));
  connect(filter_CDUP.y, switch_setpoint.u1) annotation (Line(points={{31,-30},
          {78,-30}},                   color={0,0,127}));
  connect(controlBus.p_CabSup, dP.u2) annotation (Line(
      points={{0,-100},{-180,-100},{-180,-54},{-142,-54}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.p_CabRet, dP.u1) annotation (Line(
      points={{0,-100},{-180,-100},{-180,-66},{-142,-66}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
end CS_PumpAndValveControl;
