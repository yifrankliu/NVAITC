within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Controls;
model CS_FixedPumpAndValveControl
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
          extent={{-120,-10},{-100,10}})));
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
    deadband=db_CV,
    deadbandRatio=dbr_CV) annotation (Placement(transformation(
          extent={{-80,10},{-60,-10}})));

  Modelica.Blocks.Sources.Constant delay(k=1.0) annotation (
      Placement(transformation(extent={{-20,80},{0,100}})));
  Modelica.Blocks.Sources.ContinuousClock clock(offset=0,
      startTime=0) annotation (Placement(transformation(
          extent={{-20,50},{0,70}})));
  Modelica.Blocks.Logical.Greater delayControl annotation (
      Placement(transformation(extent={{20,80},{40,60}})));
  Modelica.Blocks.Logical.Switch switch_setpoint annotation (
      Placement(transformation(extent={{100,-60},{120,-40}})));
  Modelica.Blocks.Sources.Constant Pump_start(k=
        CDUP_Nrel_start) annotation (Placement(transformation(
          extent={{-20,-80},{0,-60}})));
  Modelica.Blocks.Logical.Switch switch_setpoint1 annotation (
     Placement(transformation(extent={{100,-18},{120,2}})));
  Modelica.Blocks.Sources.Constant valve_start(k=0.5)
    annotation (Placement(transformation(extent={{60,-36},{80,-16}})));
  Modelica.Blocks.Math.Add add(k2=-1) annotation (Placement(
        transformation(extent={{-100,20},{-80,40}})));
  Modelica.Blocks.Sources.Constant conv_to_degC(k=273.15)
    annotation (Placement(transformation(extent={{-150,10},{-130,30}})));
  Modelica.Blocks.Continuous.Filter filter(filterType=
        Modelica.Blocks.Types.FilterType.LowPass, f_cut=5e-4)
    annotation (Placement(transformation(extent={{-40,10},{-20,-10}})));
  Modelica.Blocks.Noise.UniformNoise uniformNoise(
    samplePeriod=100,
    y_min=0.2,
    y_max=-0.2)
             annotation (Placement(transformation(extent={{-20,-30},{0,-50}})));
  Modelica.Blocks.Math.Add add_noise
    annotation (Placement(transformation(extent={{20,-30},{40,-50}})));
equation
  connect(Tsec_setpoint.y, PID_CDUCV.u_s) annotation (Line(
        points={{-99,0},{-82,0}},    color={0,0,127}));
  connect(clock.y, delayControl.u1) annotation (Line(points={{1,60},{12,60},{12,
          70},{18,70}},                          color={0,0,127}));
  connect(delay.y, delayControl.u2) annotation (Line(points={{1,90},{10,90},{10,
          78},{18,78}},        color={0,0,127}));
  connect(Pump_start.y, switch_setpoint.u3) annotation (Line(
        points={{1,-70},{52,-70},{52,-58},{98,-58}},    color
        ={0,0,127}));
  connect(switch_setpoint.u2, delayControl.y) annotation (
      Line(points={{98,-50},{54,-50},{54,70},{41,70}},  color
        ={255,0,255}));
  connect(switch_setpoint1.u2, delayControl.y) annotation (
      Line(points={{98,-8},{54,-8},{54,70},{41,70}},
        color={255,0,255}));
  connect(valve_start.y, switch_setpoint1.u3) annotation (
      Line(points={{81,-26},{90,-26},{90,-16},{98,-16}},
        color={0,0,127}));
  connect(add.u2, conv_to_degC.y) annotation (Line(points={{-102,24},{-120,24},
          {-120,20},{-129,20}},           color={0,0,127}));
  connect(add.y, PID_CDUCV.u_m) annotation (Line(points={{-79,30},{-70,30},{-70,
          12}},                 color={0,0,127}));
  connect(filter.u, PID_CDUCV.y) annotation (Line(points={{-42,0},{-59,0}},
                        color={0,0,127}));
  connect(filter.y, switch_setpoint1.u1) annotation (Line(
        points={{-19,0},{98,0}},
        color={0,0,127}));

  connect(controlBus.T_CabSup, add.u1) annotation (Line(
      points={{0,-100},{-180,-100},{-180,36},{-102,36}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.opening_CDUOut, switch_setpoint1.y)
    annotation (Line(
      points={{0,-100},{180,-100},{180,-8},{121,-8}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(controlBus.CDUP_Nrel, switch_setpoint.y) annotation (Line(
      points={{0,-100},{180,-100},{180,-50},{121,-50}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(uniformNoise.y, add_noise.u2) annotation (Line(points={{1,-40},{10,
          -40},{10,-34},{18,-34}},        color={0,0,127}));
  connect(add_noise.y, switch_setpoint.u1) annotation (Line(points={{41,-40},{
          48,-40},{48,-42},{98,-42}},             color={0,0,127}));
  connect(Pump_start.y, add_noise.u1) annotation (Line(points={{1,-70},{10,-70},
          {10,-46},{18,-46}},            color={0,0,127}));
end CS_FixedPumpAndValveControl;
