within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Controls;
model CS_PumpAndStagingControl
  "CS for CTWP pump, CT staging and CTWP staging"
  extends BaseClasses.PartialControls(redeclare Data.Data data);

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
  import
    TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import
    TRANSFORM.Units.Conversions.Functions.TemperatureDifference_dK.from_degForR_diff;
  parameter Modelica.Units.SI.Pressure ps_conv=from_psi(14.698);
  parameter Modelica.Units.SI.Pressure ps_min=from_psi(22.3);
  parameter Modelica.Units.SI.Pressure ps_max=from_psi(24.2);
  parameter Modelica.Units.SI.Pressure ps_stage_up=from_psi(23.9);
  parameter Modelica.Units.SI.Pressure ps_stage_down=from_psi(22.9);
  parameter Modelica.Units.SI.Pressure ps_nom=(ps_min + ps_max)*0.5;
  parameter Modelica.Units.SI.TemperatureDifference
    CT_Approach_man=from_degForR_diff(17.0);
  parameter Modelica.Units.SI.TemperatureDifference
    EHX_Approach_man=from_degForR_diff(4.0);
  parameter Modelica.Units.SI.TemperatureDifference
    ctsp_tmp_deadband=from_degForR_diff(0.5);
  parameter Real CTWP_Nrel_min=45.0;
  parameter Real CTWP_Nrel_max=70.0;
  parameter Real CTWP_Nrel_start=50.0;
  parameter Real CTWP_Nrel_stageUp = 50.0;
  parameter Real CTWP_Nrel_stageDown = 70.0;
  parameter Real wp=1.0;
  parameter Modelica.Units.SI.Time delayStart=0.0;
  parameter Real k_s=1e-1;
  // 1.0/psi
  parameter Real Ti=30;
  // s
  parameter Real gain=14.8;
  // deg. C
  parameter Real yb=0.01*CTWP_Nrel_min;
  parameter Integer nCTs=16;
  parameter Integer nCTWPs=4;
  parameter Integer nCT_start=min(11,nCTs);
  parameter Integer nCTWP_start=min(3,nCTWPs);
  parameter Integer nCTWP_min=min(2,nCTWPs);
  parameter Real dp_nom=24.0;
  parameter Modelica.Units.SI.Frequency f_cut=100.0
    "Low pass filter cut-off freq.";

  Modelica.Blocks.Continuous.LimPID PID_CTWP(
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    k=gain,
    Ti=Ti,
    yMax=CTWP_Nrel_max,
    yMin=CTWP_Nrel_min,
    wp=wp,
    withFeedForward=false,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=CTWP_Nrel_start) annotation (Placement(transformation(
          extent={{0,30},{20,10}})));

  ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses.p_CTWR_setpoint
    p_CTWR_Setpoint_Model(adj=1.09,
                          conv_p_CTWR_gauge=true) annotation (
      Placement(transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={-70,-10})));
  Modelica.Blocks.Continuous.Filter filter(filterType=Modelica.Blocks.Types.FilterType.LowPass,
      f_cut=f_cut) annotation (Placement(transformation(extent={{-30,
            50},{-10,30}})));
  ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses.CTWP_Staging
    CTWP_Staging(
    nPUMP_start=nCTWP_start,
    nPUMP_min=nCTWP_min,
    nPUMP_max=nCTWPs,
    PUMP_Nrel_min=CTWP_Nrel_stageUp,
    PUMP_Nrel_max=CTWP_Nrel_stageDown,
    tolerance=0.1) annotation (Placement(transformation(extent={{70,30},{90,10}})));
  ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses.CT_staging
    CT_Staging(
    nCT_start=min(nCT_start, nCTs),
    nCT_min=min(7, nCTs),
    nCT_max=nCTs)                   annotation (Placement(transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={-70,-50})));

  Modelica.Blocks.Sources.Constant delay1(k=1) annotation (
      Placement(transformation(extent={{-100,70},{-80,90}})));
  Modelica.Blocks.Sources.ContinuousClock clock(offset=0,
      startTime=0) annotation (Placement(transformation(extent={{-100,
            40},{-80,60}})));
  Modelica.Blocks.Logical.Greater delayControl annotation (
      Placement(transformation(extent={{-70,70},{-50,50}})));
  Modelica.Blocks.Logical.Switch switch_setpoint annotation (
      Placement(transformation(extent={{40,50},{60,30}})));
  Modelica.Blocks.Sources.Constant Pump_start(k=CTWP_Nrel_start)
    annotation (Placement(transformation(extent={{-10,70},{10,90}})));
  Modelica.Blocks.Math.Add gaugeConv(k1=-1, k2=+1)
    "Convert to gauge pressure" annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-126,-50})));
  Modelica.Blocks.Sources.RealExpression atm_press(y=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_atm(
         1.0)) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-164,-60})));
  TRANSFORM.Blocks.ArrayToMatrix arrayToMatrix(
    n=replicator.nout,
    nrows=integer(nCTs/arrayToMatrix.ncolumns),
    ncolumns=4)
    annotation (Placement(transformation(extent={{-20,-70},{0,-50}})));
  Modelica.Blocks.Routing.Replicator replicator(nout=nCTs)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-10,-20})));
  TRANSFORM.Blocks.ArrayToMatrix arrayToMatrix1(
    n=replicator.nout,
    nrows=arrayToMatrix.nrows,
    ncolumns=arrayToMatrix.ncolumns)
    annotation (Placement(transformation(extent={{20,-30},{40,-10}})));
  Modelica.Blocks.Routing.Replicator replicator1(nout=nCTWPs)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={80,60})));
  Modelica.Blocks.Math.Gain psiConv(k=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(1.0))
    "Convert to psi" annotation (Placement(transformation(
        extent={{8,-8},{-8,8}},
        rotation=180,
        origin={-100,-50})));
equation

  connect(controlBus.numCTs, CT_Staging.nCT) annotation (Line(
      points={{0,-100},{180,-100},{180,-47},{-59,-47}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.valve_CTWP, CTWP_Staging.valvePUMP)
    annotation (Line(
      points={{0,-100},{180,-100},{180,23},{91,23}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.T_EHX_HotSupply, CT_Staging.T) annotation (
      Line(
      points={{0,-100},{-90,-100},{-90,-53},{-81,-53}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(filter.y, PID_CTWP.u_m) annotation (Line(points={{-9,40},
          {10,40},{10,32}}, color={0,0,127}));
  connect(controlBus.Towb, p_CTWR_Setpoint_Model.Towb)
    annotation (Line(
      points={{0,-100},{-180,-100},{-180,-14},{-81,-14}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.T_EHX_HotSupply, p_CTWR_Setpoint_Model.T_HTWS)
    annotation (Line(
      points={{0,-100},{-180,-100},{-180,-10},{-81.02,-10}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.pColdReturn, p_CTWR_Setpoint_Model.p_CTWR)
    annotation (Line(
      points={{0,-100},{-180,-100},{-180,-6},{-81.02,-6}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(delay1.y, delayControl.u2) annotation (Line(points={{-79,
          80},{-76,80},{-76,68},{-72,68}}, color={0,0,127}));
  connect(clock.y, delayControl.u1) annotation (Line(points={{-79,
          50},{-72,50},{-72,60}}, color={0,0,127}));
  connect(delayControl.y, switch_setpoint.u2) annotation (Line(
        points={{-49,60},{20,60},{20,40},{38,40}}, color={255,0,255}));
  connect(PID_CTWP.y, switch_setpoint.u1) annotation (Line(points
        ={{21,20},{28,20},{28,32},{38,32}}, color={0,0,127}));
  connect(Pump_start.y, switch_setpoint.u3) annotation (Line(
        points={{11,80},{30,80},{30,48},{38,48}}, color={0,0,127}));
  connect(switch_setpoint.y, CTWP_Staging.PUMP_Nrel) annotation (
      Line(points={{61,40},{64,40},{64,23},{69,23}}, color={0,0,127}));
  connect(controlBus.pColdReturn, gaugeConv.u2) annotation (Line(
      points={{0,-100},{-180,-100},{-180,-44},{-138,-44}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(atm_press.y, gaugeConv.u1) annotation (Line(points={{-153,-60},{-148,
          -60},{-148,-56},{-138,-56}},            color={0,0,127}));
  connect(CT_Staging.valveCTs, arrayToMatrix.u) annotation (Line(
        points={{-59,-53},{-40,-53},{-40,-60},{-22,-60}}, color={0,
          0,127}));
  connect(controlBus.valve_CT, arrayToMatrix.y) annotation (Line(
      points={{0,-100},{180,-100},{180,-60},{1,-60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(replicator.y, arrayToMatrix1.u) annotation (Line(points
        ={{1,-20},{18,-20}}, color={0,0,127}));
  connect(controlBus.Tset_CT, arrayToMatrix1.y) annotation (Line(
      points={{0,-100},{180,-100},{180,-20},{41,-20}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(switch_setpoint.y, replicator1.u) annotation (Line(
        points={{61,40},{64,40},{64,60},{68,60}}, color={0,0,127}));
  connect(controlBus.Nrel_CTWP, replicator1.y) annotation (Line(
      points={{0,-100},{180,-100},{180,60},{91,60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(CTWP_Staging.nCT, CT_Staging.nCT) annotation (Line(points={{69,17},{52,
          17},{52,-40},{-40,-40},{-40,-47},{-59,-47}}, color={0,0,127}));
  connect(gaugeConv.y, psiConv.u)
    annotation (Line(points={{-115,-50},{-109.6,-50}}, color={0,0,127}));
  connect(psiConv.y, CT_Staging.p) annotation (Line(points={{-91.2,-50},{-90,
          -50},{-90,-47},{-81,-47}}, color={0,0,127}));
  connect(p_CTWR_Setpoint_Model.p_CTWR_measured, filter.u) annotation (Line(
        points={{-59,-6},{-50,-6},{-50,40},{-32,40}},          color={0,0,127}));
  connect(p_CTWR_Setpoint_Model.T_CT_setpoint, replicator.u) annotation (Line(
        points={{-59,-14},{-50,-14},{-50,-20},{-22,-20}}, color={0,0,127}));
  connect(p_CTWR_Setpoint_Model.p_CTWR_setpoint, PID_CTWP.u_s) annotation (Line(
        points={{-59,-10},{-46,-10},{-46,20},{-2,20}}, color={0,0,127}));
end CS_PumpAndStagingControl;
