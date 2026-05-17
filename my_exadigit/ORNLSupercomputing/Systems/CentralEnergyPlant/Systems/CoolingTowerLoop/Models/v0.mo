within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Models;
model v0
  extends BaseClasses.BaseClasses_A.PartialModel_A(
    port_a_nominal(
      p=2.6e5,
      T=297.95,
      m_flow=500.0),
    port_b_nominal(p=2.9e5, T=293.15),
    redeclare replaceable Data.Data data(res_from_CTWP_dp=25000),
    redeclare replaceable Controls.CS_PumpAndStagingControl
      controls(nCTs=nCoolingTowers*4,
                                    nCTWPs=nPumpTrains),
    redeclare replaceable Sources.v0 sources,
    summary(
      m_flow_ctw=port_a.m_flow,
      p_fac_ctw_r=TP_CTWR.p,
      p_fac_ctw_s=TP_CTWS.p,
      T_fac_ctw_r=TP_CTWR.T,
      T_fac_ctw_s=TP_CTWS.T,
      W_flow_CTWP=sum(pumpTrain[:].pump.W),
      W_flow_CT=sum(coolingTower.cell[:].CT.PFan),
      Q_flow_CT=-1*sum(coolingTower.cell[:].CT.Q_flow),
      N_CTWP=controls.switch_setpoint.y,
      n_CTWPs=controls.CTWP_Staging.nPUMP,
      n_CTs=controls.CT_Staging.nCT));

  parameter Integer nCoolingTowers=4;
  parameter Integer nPumpTrains=4;

  TRANSFORM.Fluid.Volumes.MixingVolume volCTWS2(
    redeclare package Medium = Medium,
    p_start=data.volCTWS2_pinit,
    T_start=data.volCTWS2_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=data.volCTWS2_vol),
    nPorts_b=1,
    nPorts_a=nPumpTrains)
                annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={100,0})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    res_from_CTWP(redeclare package Medium = Medium, R=data.res_from_CTWP_dp/
        port_a_nominal.m_flow)                      annotation (
      Placement(transformation(extent={{120,-10},{140,10}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature TP_CTWS(
    redeclare package Medium = Medium,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    redeclare function iconUnit2 =
        TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degF)
    annotation (Placement(transformation(extent={{140,12},{160,32}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature TP_CTWR(
    redeclare package Medium = Medium,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    redeclare function iconUnit2 =
        TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degF)
    annotation (Placement(transformation(extent={{-120,10},{-140,30}})));
  Components.CoolingTower coolingTower[nCoolingTowers](redeclare package Medium =
        Medium)
    annotation (Placement(transformation(extent={{-90,-10},{-70,10}})));
  TRANSFORM.Fluid.Volumes.MixingVolume volCTWR(
    redeclare package Medium = Medium,
    p_start=data.volCTWR_pinit,
    T_start=data.volCTWR_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=data.volCTWR_vol),
    nPorts_b=nCoolingTowers,
    nPorts_a=1) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,0})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet(
    redeclare package Medium = Medium,
    p_start=data.volCTWS1_pinit,
    T_start=data.volCTWS1_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=1),
    nPorts_a=nCoolingTowers,
    nPorts_b=2) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-50,0})));
  TRANSFORM.Fluid.Volumes.MixingVolume volCTWS1(
    redeclare package Medium = Medium,
    p_start=data.volCTWS1_pinit,
    T_start=data.volCTWS1_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=data.volCTWS1_vol),
    nPorts_b=nPumpTrains,
    nPorts_a=1) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={10,0})));
  Modelica.Blocks.Routing.Replicator replicator(nout=
        nCoolingTowers) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=90,
        origin={-60,40})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance res_to_CT(
      redeclare package Medium = Medium, R=data.res_to_CT_dp/port_a_nominal.m_flow)
    annotation (Placement(transformation(extent={{-160,-10},{-140,10}})));
  ORNLSupercomputing.Components.SubComponents.Fluid.Pumps.PumpTrain pumpTrain[
    nPumpTrains](
    redeclare package Medium = Medium,
    port_a_nominal={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_a_nominal.p,
        T=port_a_nominal.T,
        h=port_a_nominal.h,
        m_flow=port_a_nominal.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    port_b_nominal={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_b_nominal.p,
        T=port_b_nominal.T,
        h=port_b_nominal.h,
        m_flow=port_b_nominal.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    port_a_start={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_a_start.p,
        T=port_a_start.T,
        h=port_a_start.h,
        m_flow=port_a_start.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    port_b_start={TRANSFORM.Examples.Utilities.Record_fluidPorts(
        p=port_b_start.p,
        T=port_b_start.T,
        h=port_b_start.h,
        m_flow=port_b_start.m_flow/nPumpTrains) for i in 1:nPumpTrains},
    redeclare ORNLSupercomputing.Components.SubComponents.Fluid.Pumps.CTWP pump)
    annotation (Placement(transformation(extent={{50,-10},{70,10}})));
  TRANSFORM.Fluid.Volumes.ExpansionTank_1Port basin_reservoir(
    redeclare package Medium = Medium,
    A=Modelica.Constants.pi*1.0^2,
    V0=20.0,
    p_surface(displayUnit="bar"),
    p_start(displayUnit="bar") = data.basin_reservoir_p + 0.5e5,
    level_start=0.5,
    use_T_start=true,
    T_start=data.basin_reservoir_Tinit)
    "Basin reservoir at Atmospheric pressure" annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-30,60})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance res_basin(
      redeclare package Medium = Medium, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1e5)/
        port_a_nominal.m_flow) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={-30,30})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance res_to_CTWP(
      redeclare package Medium = Medium, R=data.res_to_CTWP_dp/port_a_nominal.m_flow)
    annotation (Placement(transformation(extent={{-30,-10},{-10,10}})));
equation

  connect(controlBus.pColdReturn, TP_CTWR.p) annotation (Line(
      points={{0,100},{-180,100},{-180,22.4},{-136,22.4}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(port_b, res_from_CTWP.port_b) annotation (Line(points={{
          180,0},{137,0}}, color={0,127,255}));

  connect(TP_CTWS.port, res_from_CTWP.port_b)
    annotation (Line(points={{150,12},{150,0},{137,0}}, color={0,127,255}));
  connect(coolingTower.port_b, plenum_outlet.port_a) annotation (
      Line(points={{-70,0},{-56,0}}, color={0,127,255}));
  connect(volCTWS2.port_b[1], res_from_CTWP.port_a) annotation (
      Line(points={{106,0},{123,0}}, color={0,127,255}));
  connect(controlBus.Tset_CT, coolingTower.waterSPTLvg)
    annotation (Line(
      points={{0,100},{-80,100},{-80,12}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(replicator.y, coolingTower.Towb) annotation (Line(
        points={{-60,29},{-60,20},{-74,20},{-74,12}}, color={0,0,127}));
  connect(controlBus.Towb, replicator.u) annotation (Line(
      points={{0,100},{-60,100},{-60,52}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.valve_CT, coolingTower.opening) annotation (
      Line(
      points={{0,100},{-86,100},{-86,12}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(volCTWR.port_b, coolingTower.port_a) annotation (Line(
        points={{-104,0},{-90,0}},color={0,127,255}));
  connect(controlBus.valve_CTWP, pumpTrain.opening) annotation (Line(
      points={{0,100},{56,100},{56,12}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.Nrel_CTWP, pumpTrain.N) annotation (Line(
      points={{0,100},{64,100},{64,12}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(volCTWS1.port_b, pumpTrain.port_a)
    annotation (Line(points={{16,0},{50,0}}, color={0,127,255}));
  connect(pumpTrain.port_b, volCTWS2.port_a)
    annotation (Line(points={{70,0},{94,0}}, color={0,127,255}));
  connect(res_to_CTWP.port_a, plenum_outlet.port_b[1]) annotation (Line(points=
          {{-27,0},{-40,0},{-40,0.25},{-44,0.25}}, color={0,127,255}));
  connect(res_to_CTWP.port_b, volCTWS1.port_a[1])
    annotation (Line(points={{-13,0},{4,0}}, color={0,127,255}));
  connect(res_basin.port_a, plenum_outlet.port_b[2]) annotation (Line(points={{
          -30,23},{-30,-0.25},{-44,-0.25}}, color={0,127,255}));
  connect(res_basin.port_b, basin_reservoir.port)
    annotation (Line(points={{-30,37},{-30,51.6}}, color={0,127,255}));
  connect(res_to_CT.port_b, volCTWR.port_a[1])
    annotation (Line(points={{-143,0},{-116,0}}, color={0,127,255}));
  connect(res_to_CT.port_a, port_a)
    annotation (Line(points={{-157,0},{-180,0}}, color={0,127,255}));
  connect(TP_CTWR.port, res_to_CT.port_b)
    annotation (Line(points={{-130,10},{-130,0},{-143,0}}, color={0,127,255}));
  annotation (experiment(StopTime=1, __Dymola_Algorithm="Dassl"));
end v0;
