within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.HotWaterLoop.Models;
model v0
  extends BaseClasses.BaseClasses_A.PartialModel_A(
    final port_a1,
    final port_b1,
    final port_a2,
    final port_b2,
    port_a1_nominal(
      p=3.837e5,
      T=302.15,
      m_flow=300.0),
    port_b1_nominal(p=5.4951e5, T=294.15),
    port_a2_nominal(
      p=2.9e5,
      T=293.15,
      m_flow=500.0),
    port_b2_nominal(p=2.6e5, T=297.95),
    redeclare replaceable Controls.CS_PumpAndStagingControl controls(nHTWPs=
          nPumpTrains, nEHXs=nHeatExchangerTrains),
    redeclare replaceable Sources.NULL sources,
    redeclare replaceable Data.Data data,
    summary(
      m_flow_htw=port_a1.m_flow,
      p_fac_htw_r=TP_HTWR.p,
      p_fac_htw_s=TP_HTWS.p,
      T_fac_htw_r=TP_HTWR.T,
      T_fac_htw_s=TP_HTWS.T,
      W_flow_HTWP=sum(pumpTrain[:].pump.W),
      N_HTWP=controls.HTWP_speed.HTWP_Nrel,
      n_HTWPs=controls.HTWP_Staging.nPUMP,
      n_EHXs=controls.EHX_Staging.nEHX));

    parameter Integer nPumpTrains = 4;
    parameter Integer nHeatExchangerTrains = 4;

  ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.EHX EHX1[
    nHeatExchangerTrains](
    redeclare package Medium_1 = Medium_1,
    redeclare package Medium_2 = Medium_2,
    EHX_p_a_start_1(displayUnit="Pa"))
    annotation (Placement(transformation(extent={{-10,-66},{10,-46}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance res_to_EHX[
    nHeatExchangerTrains](redeclare package Medium = Medium_1, each R=data.res_to_EHX_dP
        /(port_a1_nominal.m_flow/nHeatExchangerTrains))
    annotation (Placement(transformation(extent={{-74,-10},{-54,10}})));
  TRANSFORM.Fluid.Valves.ValveLinear valveEHX1a[nHeatExchangerTrains](
    redeclare package Medium = Medium_1,
    dp_start(displayUnit="Pa") = 50,
    m_flow_start=75,
    dp_nominal(displayUnit="Pa") = 100,
    m_flow_nominal=100)
    annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature TP_HTWS(
    redeclare package Medium = Medium_1,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    redeclare function iconUnit2 =
        TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degF)
    annotation (Placement(transformation(extent={{130,70},{150,90}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature TP_HTWR(
    redeclare package Medium = Medium_1,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    redeclare function iconUnit2 =
        TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degF)
    annotation (Placement(transformation(extent={{-130,70},{-150,90}})));
  TRANSFORM.Fluid.Volumes.MixingVolume volHTWR2(
    redeclare package Medium = Medium_1,
    p_start=data.volHTWR2_pinit,
    T_start=data.volHTWR2_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=data.volHTWR2_vol),
    nPorts_a=nPumpTrains,
    nPorts_b=nHeatExchangerTrains)
                annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=0,
        origin={-28,60})));
  TRANSFORM.Fluid.Volumes.MixingVolume volHTWS(
    redeclare package Medium = Medium_1,
    p_start=data.volHTWS_pinit,
    T_start=data.volHTWS_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=data.volHTWS_vol),
    nPorts_b=2,
    nPorts_a=nHeatExchangerTrains)
                annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={50,0})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    res_from_E102(redeclare package Medium = Medium_1, R=data.res_from_E102_R)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-120,60})));
  TRANSFORM.Fluid.Volumes.MixingVolume volHTWR1(
    redeclare package Medium = Medium_1,
    p_start=data.volHTWR1_pinit,
    T_start=data.volHTWR1_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=data.volHTWR1_vol),
    nPorts_a=1,
    nPorts_b=nPumpTrains)
                annotation (Placement(transformation(
        extent={{10.5,-10.25},{-10.5,10.25}},
        rotation=180,
        origin={-91.5,59.75})));
  TRANSFORM.Fluid.Valves.ValveLinear valveEHX1b[nHeatExchangerTrains](
    redeclare package Medium = Medium_2,
    dp_start(displayUnit="Pa") = 50,
    m_flow_start=100,
    dp_nominal(displayUnit="Pa") = 100,
    m_flow_nominal=125)
    annotation (Placement(transformation(extent={{50,-70},{30,-50}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_inlet_a2(
    redeclare package Medium = Medium_2,
    p_start=data.volHTWS_pinit,
    T_start=data.volHTWS_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.01),
    nPorts_a=1,
    nPorts_b=nHeatExchangerTrains)
                annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=0,
        origin={70,-60})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet_b2(
    redeclare package Medium = Medium_2,
    p_start=data.volHTWS_pinit,
    T_start=data.volHTWS_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.01),
    nPorts_b=1,
    nPorts_a=nHeatExchangerTrains)
                annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=0,
        origin={-50,-60})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    res_outlet_b2(redeclare package Medium = Medium_2, R=0.01/port_a2_nominal.m_flow)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=0,
        origin={-80,-60})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance res_inlet_a2(
      redeclare package Medium = Medium_2, R=0.01/port_a2_nominal.m_flow)
                                                   annotation (
      Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=0,
        origin={100,-60})));
  ORNLSupercomputing.Components.SubComponents.Fluid.Pumps.PumpTrain pumpTrain[
    nPumpTrains](
    redeclare package Medium = Medium_1,
    port_a_nominal={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_a1_nominal.p,
        T=port_a1_nominal.T,
        h=port_a1_nominal.h,
        m_flow=port_a1_nominal.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    port_b_nominal={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_a1_nominal.p,
        T=port_a1_nominal.T,
        h=port_a1_nominal.h,
        m_flow=port_a1_nominal.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    port_a_start={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_a1_start.p,
        T=port_a1_start.T,
        h=port_a1_start.h,
        m_flow=port_a1_start.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    port_b_start={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_a1_start.p,
        T=port_a1_start.T,
        h=port_a1_start.h,
        m_flow=port_a1_start.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    valve(
      dp_start=50000000,
      m_flow_start=100,
      m_flow_nominal=150),
    redeclare ORNLSupercomputing.Components.SubComponents.Fluid.Pumps.HTWP pump)
    annotation (Placement(transformation(extent={{-70,50},{-50,70}})));
  TRANSFORM.Fluid.Volumes.ExpansionTank_1Port press_HTWP(
    redeclare package Medium = Medium_1,
    A=Modelica.Constants.pi*0.75^2,
    V0=10,
    p_surface(displayUnit="bar"),
    p_start(displayUnit="bar") = data.press_HTWP_p + 1.0e4,
    level_start=1.0,
    use_T_start=true,
    T_start=data.press_HTWP_T) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={70,70})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance res_outlet(
      redeclare package Medium = Medium_1, R=data.res_to_E102_R)
    annotation (Placement(transformation(extent={{110,50},{130,70}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance res_press(
      redeclare package Medium = Medium_1, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1e5)/
        port_a1_nominal.m_flow) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={70,40})));
equation
  connect(valveEHX1a.port_b, EHX1.port_a1) annotation (Line(points={{-20,0},{-14,
          0},{-14,-52},{-10,-52}}, color={0,127,255}));

  connect(TP_HTWS.p, controlBus.pHotSupply) annotation (Line(
      points={{146,82.4},{164,82.4},{164,82},{180,82},{180,100},{0,100}},
      color={255,215,136},
      thickness=0.5,
      pattern=LinePattern.Dash));

  connect(TP_HTWR.p, controlBus.pHotReturn) annotation (Line(
      points={{-146,82.4},{-180,82.4},{-180,100},{0,100}},
      color={255,215,136},
      thickness=0.5,
      pattern=LinePattern.Dash));

  connect(TP_HTWS.T, controlBus.T_EHX_HotSupply) annotation (Line(
      points={{146,77.8},{180,77.8},{180,100},{0,100}},
      color={255,215,136},
      thickness=0.5,
      pattern=LinePattern.Dash));

  connect(TP_HTWR.T, controlBus.T_EHX_HotReturn) annotation (Line(
      points={{-146,77.8},{-180,77.8},{-180,100},{0,100}},
      color={255,215,136},
      thickness=0.5,
      pattern=LinePattern.Dash));

  connect(EHX1.port_a2, valveEHX1b.port_b)
    annotation (Line(points={{10,-60},{30,-60}}, color={0,127,255}));
  connect(res_from_E102.port_a, port_a1) annotation (Line(points={
          {-127,60},{-180,60}}, color={0,127,255}));
  connect(TP_HTWR.port, port_a1) annotation (Line(points={{-140,70},{-140,60},{
          -180,60}}, color={0,127,255}));
  connect(volHTWR1.port_a[1], res_from_E102.port_b) annotation (
      Line(points={{-97.8,59.75},{-97.8,60},{-113,60}},   color={0,
          127,255}));

  connect(TP_HTWS.port, port_b1)
    annotation (Line(points={{140,70},{140,60},{180,60}}, color={0,127,255}));
  connect(controlBus.valveEHX, valveEHX1a.opening) annotation (
      Line(
      points={{0,100},{-180,100},{-180,30},{-30,30},{-30,8}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.valveEHXb, valveEHX1b.opening) annotation (
      Line(
      points={{0,100},{180,100},{180,-40},{40,-40},{40,-52}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(res_outlet_b2.port_b, port_b2) annotation (Line(points={{-87,-60},{-180,
          -60}},                 color={0,127,255}));
  connect(res_outlet_b2.port_a, plenum_outlet_b2.port_b[1])
    annotation (Line(points={{-73,-60},{-56,-60}}, color={0,127,255}));
  connect(port_a2, res_inlet_a2.port_a) annotation (Line(points={{180,
          -60},{107,-60}}, color={0,127,255}));
  connect(res_inlet_a2.port_b, plenum_inlet_a2.port_a[1])
    annotation (Line(points={{93,-60},{76,-60}}, color={0,127,255}));
  connect(controlBus.valveHTWP, pumpTrain.opening) annotation (Line(
      points={{0,100},{-64,100},{-64,72}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.Nrel_HTWP, pumpTrain.N) annotation (Line(
      points={{0,100},{-56,100},{-56,72}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(volHTWR1.port_b, pumpTrain.port_a) annotation (Line(points={{-85.2,
          59.75},{-86,60},{-70,60}},                 color={0,127,255}));
  connect(volHTWR2.port_a, pumpTrain.port_b)
    annotation (Line(points={{-34,60},{-50,60}}, color={0,127,255}));
  connect(volHTWS.port_b[1], res_outlet.port_a) annotation (Line(points={{56,
          -0.25},{100,-0.25},{100,60},{113,60}}, color={0,127,255}));
  connect(res_outlet.port_b, port_b1)
    annotation (Line(points={{127,60},{180,60}}, color={0,127,255}));
  connect(res_press.port_a, volHTWS.port_b[2])
    annotation (Line(points={{70,33},{70,0.25},{56,0.25}}, color={0,127,255}));
  connect(res_press.port_b, press_HTWP.port)
    annotation (Line(points={{70,47},{70,61.6}}, color={0,127,255}));
  connect(EHX1.port_b1, volHTWS.port_a) annotation (Line(points={{10,-52},{14,-52},
          {14,0},{44,0}}, color={0,127,255}));
  connect(valveEHX1b.port_a, plenum_inlet_a2.port_b)
    annotation (Line(points={{50,-60},{64,-60}}, color={0,127,255}));
  connect(plenum_outlet_b2.port_a, EHX1.port_b2)
    annotation (Line(points={{-44,-60},{-10,-60}}, color={0,127,255}));
  connect(res_to_EHX.port_b, valveEHX1a.port_a)
    annotation (Line(points={{-57,0},{-40,0}}, color={0,127,255}));
  connect(res_to_EHX.port_a, volHTWR2.port_b) annotation (Line(points={{-71,0},{
          -88,0},{-88,20},{0,20},{0,60},{-22,60}}, color={0,127,255}));
  annotation (experiment(StopTime=1, __Dymola_Algorithm="Dassl"));
end v0;
