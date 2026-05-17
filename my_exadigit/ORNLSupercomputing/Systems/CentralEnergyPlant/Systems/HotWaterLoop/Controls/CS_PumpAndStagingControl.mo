within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.HotWaterLoop.Controls;
model CS_PumpAndStagingControl
  extends BaseClasses.PartialControls(redeclare Data.NULL data);

  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // HTWP1 is always set to be operational
  // HTWP2 - HTWP4 are staged up when the operational pump speeds touch Nrel_max
  // and staged down when the operational pump speeds touch Nrel_min.
  // The PID controller for the pump speeds is controlled by the dP setpoint.
  // The setpoint is fixed at 23.8 psi.
  // The EHXs are stage up depending upon the no. of CTs.
  import
    TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  parameter Real dp_nom=23.8 "Nominal dP in psi";
  parameter Real HTWP_Nrel_min=53.0 "Min. %N HTWP";
  parameter Real HTWP_Nrel_max=72.0 "Max. %N HTWP";
  parameter Real HTWP_Nrel_start=55.0 "Starting %N HTWP";
  parameter Integer nHTWPs = 4 "Maximum no. of HTWPs";
  parameter Integer nEHXs = 4 "Maximum no. of EHXs";
  parameter Integer nHTWP_start=min(2, nHTWPs) "Starting no. of HTWPs";
  parameter Integer nEHX_start=min(3, nEHXs) "Starting no. of EHXs";
  // Control Systems
  parameter Real k_s=1.0;
  parameter Real Ti=30;
  // s
  parameter Real gain=14.8;

  ORNLSupercomputing.Components.SubComponents.Controls.Testing.HTW_Loop.BaseClasses.EHX_Staging
    EHX_Staging(nEHX_start=nEHX_start, nEHX_max=nEHXs)
                              annotation (Placement(transformation(
          extent={{-10,-60},{10,-40}})));
  ORNLSupercomputing.Components.SubComponents.Controls.Testing.HTW_Loop.BaseClasses.HTWP_Staging
    HTWP_Staging(
    nPUMP_start=nHTWP_start,
    nPUMP_max=nHTWPs,
                 PUMP_Nrel_min=HTWP_Nrel_min, PUMP_Nrel_max=
        HTWP_Nrel_max) annotation (Placement(transformation(extent={
            {90,-20},{110,0}})));
  Modelica.Blocks.Sources.Constant delay1(k=1) annotation (
      Placement(transformation(extent={{-80,50},{-60,70}})));
  Modelica.Blocks.Sources.ContinuousClock clock(offset=0,
      startTime=0) annotation (Placement(transformation(extent={{-80,
            20},{-60,40}})));
  Modelica.Blocks.Logical.Greater delayControl annotation (
      Placement(transformation(extent={{-40,50},{-20,30}})));
  Modelica.Blocks.Sources.Constant Pump_start(k=60.0) annotation (
     Placement(transformation(extent={{10,20},{30,40}})));
  Modelica.Blocks.Logical.Switch switch_setpoint annotation (
      Placement(transformation(extent={{40,20},{60,0}})));
  ORNLSupercomputing.Components.SubComponents.Controls.Testing.HTW_Loop.BaseClasses.HTWP_speed_simple
    HTWP_speed(
    dp_nom=dp_nom,
    HTWP_Nrel_min=HTWP_Nrel_min,
    HTWP_Nrel_max=HTWP_Nrel_max,
    HTWP_Nrel_start=HTWP_Nrel_start) annotation (Placement(
        transformation(extent={{-40,-10},{-20,10}})));

  Modelica.Blocks.Routing.Replicator replicator(nout=nHTWPs)
    annotation (Placement(transformation(extent={{90,20},{110,40}})));
equation
  connect(controlBus.valveHTWP, HTWP_Staging.valvePUMP)
    annotation (Line(
      points={{0,-100},{180,-100},{180,-13},{111,-13}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.numCTs, EHX_Staging.nCT) annotation (Line(
      points={{0,-100},{-180,-100},{-180,-50},{-11,-50}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.valveEHX, EHX_Staging.valveEHXs) annotation (
     Line(
      points={{0,-100},{180,-100},{180,-50},{11,-50}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.valveEHXb, EHX_Staging.valveEHXs)
    annotation (Line(
      points={{0,-100},{180,-100},{180,-50},{11,-50}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(clock.y, delayControl.u1) annotation (Line(points={{-59,
          30},{-50,30},{-50,40},{-42,40}}, color={0,0,127}));
  connect(delay1.y, delayControl.u2) annotation (Line(points={{-59,
          60},{-50,60},{-50,48},{-42,48}}, color={0,0,127}));
  connect(Pump_start.y, switch_setpoint.u3) annotation (Line(
        points={{31,30},{33.65,30},{33.65,18},{38,18}}, color={0,0,
          127}));
  connect(delayControl.y, switch_setpoint.u2) annotation (Line(
        points={{-19,40},{0,40},{0,10},{38,10}}, color={255,0,255}));
  connect(controlBus.Nrel_HTWP, replicator.y) annotation (Line(
      points={{0,-100},{180,-100},{180,30},{111,30}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(switch_setpoint.u1, HTWP_speed.HTWP_Nrel) annotation (
      Line(points={{38,2},{0,2},{0,0},{-19,0}}, color={0,0,127}));
  connect(controlBus.pHotSupply, HTWP_speed.p_HTWS) annotation (
      Line(
      points={{0,-100},{-180,-100},{-180,-3},{-41.02,-3}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.pHotReturn, HTWP_speed.p_HTWR) annotation (
      Line(
      points={{0,-100},{-180,-100},{-180,3},{-41.02,3}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(switch_setpoint.y, HTWP_Staging.PUMP_Nrel) annotation (
      Line(points={{61,10},{70,10},{70,-10},{89,-10}}, color={0,0,
          127}));
  connect(replicator.u, switch_setpoint.y) annotation (Line(
        points={{88,30},{76,30},{76,10},{61,10}}, color={0,0,127}));

end CS_PumpAndStagingControl;
