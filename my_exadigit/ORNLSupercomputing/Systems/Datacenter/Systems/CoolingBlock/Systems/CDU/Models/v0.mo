within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Models;
model v0
  extends BaseClasses.BaseClasses_A.PartialModel_A(
    port_b2_nominal(p=data.coolingChannels_pinit, T=data.coolingChannels_T_b_start),
    port_b1_nominal(p=data.press_CDU_p, T=data.press_CDU_T),
    port_a2_nominal(
      p=data.coolingChannels_pinit,
      T=data.coolingChannels_T_a_start,
      m_flow=data.coolingChannels_m_start),
    port_a1_nominal(
      p=data.press_CDU_p,
      T=data.press_CDU_T,
      m_flow=data.valve_m_flow_nom),
    redeclare replaceable Controls.CS_PumpAndValveControl      controls,
    redeclare replaceable Data.v0 data(UA_corr_mod=1.2),
    redeclare replaceable Sources.NULL sources,
    summary(
      m_flow_prim=port_a1.m_flow,
      m_flow_sec=HEX.port_a1.m_flow,
      W_flow_CDUP=CDUP.W*CDUP.nParallel,
      T_prim_s=FacSup_pT.T,
      T_prim_r=FacRet_pT.T,
      T_sec_s=CabSup_pT.T,
      T_sec_r=CabRet_pT.T,
      p_prim_s=FacSup_pT.p,
      p_prim_r=FacRet_pT.p,
      p_sec_s=CabSup_pT.p,
      p_sec_r=CabRet_pT.p));

  ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.CDU_HEX
    HEX(
    redeclare package Medium_1 = Medium_2,
    redeclare package Medium_2 = Medium_1,
    R_Sec=data.R_CTW,
    CDU_p_a_start_1(displayUnit="Pa") =
      TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi(
       39.80),
    UA_corr_mod=data.UA_corr_mod) annotation (Placement(
        transformation(extent={{40,66},{20,46}})));

  TRANSFORM.Fluid.Sensors.PressureTemperature CabRet_pT(
    redeclare package Medium = Medium_2,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2) annotation (Placement(transformation(extent
          ={{130,-50},{150,-30}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature FacSup_pT(
    redeclare package Medium = Medium_1,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2) annotation (Placement(transformation(extent
          ={{-150,70},{-130,90}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature FacRet_pT(
    redeclare package Medium = Medium_1,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2) annotation (Placement(transformation(extent
          ={{130,70},{150,90}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    dP_HTWR(redeclare package Medium = Medium_1, R=data.R_HTWR)
    annotation (Placement(transformation(extent={{100,50},{120,
            70}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    dP_HTWS(redeclare package Medium = Medium_1, R=data.R_HTWS)
    annotation (Placement(transformation(extent={{-120,50},{-100,
            70}})));
  TRANSFORM.Fluid.Valves.ValveLinear valveCDU(
    redeclare package Medium = Medium_1,
    dp_start(displayUnit="Pa") = 50,
    m_flow_start=10,
    dp_nominal(displayUnit="Pa") = data.dP_valve_CDU,
    m_flow_nominal=data.valve_m_flow_nom) annotation (
      Placement(transformation(extent={{-40,50},{-20,70}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature CabSup_pT(
    redeclare package Medium = Medium_2,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    redeclare function iconUnit2 =
        TRANSFORM.Units.Conversions.Functions.Temperature_K.to_degC)
    annotation (Placement(transformation(extent={{-130,-50},{-150,
            -30}})));

  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    dP_CTW1(redeclare package Medium = Medium_2, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1)/
        port_a2_nominal.m_flow)
    annotation (Placement(transformation(extent={{120,-70},{100,
            -50}})));
  TRANSFORM.Fluid.Volumes.ExpansionTank_1Port press_CDU(
    redeclare package Medium = Medium_2,
    A=Modelica.Constants.pi*0.02^2,
    V0=0.1,
    p_start=data.press_CDU_p,
    level_start=0.3,
    h_start=Medium_2.specificEnthalpy_pT(press_CDU.p_start, data.press_CDU_T))
    annotation (Placement(transformation(extent={{-50,-14},{-70,6}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance resistance_tank(
      redeclare package Medium = Medium_2, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1e5)/
        port_a2_nominal.m_flow) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={-60,-30})));
  TRANSFORM.Fluid.FittingsAndResistances.TeeJunctionVolume tee(
    redeclare package Medium = Medium_2,
    V=0.001,
    p_start=data.press_CDU_p,
    T_start=data.press_CDU_T,
    h_start=Medium_2.specificEnthalpy_pT(press_CDU.p_start, port_a1_start.T))
    annotation (Placement(transformation(extent={{-50,-70},{-70,-50}})));
  ORNLSupercomputing.Components.SubComponents.Fluid.Pumps.CDUP CDUP(redeclare
      package Medium = Medium_2)
    annotation (Placement(transformation(extent={{-90,-70},{-110,-50}})));
equation

  connect(HEX.port_b2, dP_HTWR.port_a) annotation (Line(
        points={{40,60},{103,60}}, color={0,127,255}));
  connect(dP_HTWS.port_b, valveCDU.port_a) annotation (Line(
        points={{-103,60},{-40,60}}, color={0,127,255}));
  connect(valveCDU.port_b, HEX.port_a2) annotation (Line(
        points={{-20,60},{20,60}}, color={0,127,255}));
  connect(dP_HTWR.port_b, port_b1) annotation (Line(points={{117,
          60},{180,60}}, color={0,127,255}));
  connect(FacRet_pT.port, port_b1) annotation (Line(points={{140,
          70},{140,60},{180,60}}, color={0,127,255}));
  connect(controlBus.p_CabRet, CabRet_pT.p) annotation (Line(
      points={{0,100},{180,100},{180,-37.6},{146,-37.6}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.T_CabSup, CabSup_pT.T) annotation (Line(
      points={{0,100},{-180,100},{-180,-42},{-164,-42},{-164,-42.2},
          {-146,-42.2}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(controlBus.p_CabSup, CabSup_pT.p) annotation (Line(
      points={{0,100},{-180,100},{-180,-38},{-164,-38},{-164,-37.6},
          {-146,-37.6}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(controlBus.opening_CDUOut, valveCDU.opening)
    annotation (Line(
      points={{0,100},{-30,100},{-30,68}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(port_a1, dP_HTWS.port_a) annotation (Line(points={{-180,
          60},{-117,60}}, color={0,127,255}));
  connect(FacSup_pT.port, dP_HTWS.port_a) annotation (Line(
        points={{-140,70},{-140,60},{-117,60}}, color={0,127,255}));
  connect(CabRet_pT.port, port_a2) annotation (Line(points={{140,
          -50},{140,-60},{180,-60}}, color={0,127,255}));

  connect(CabRet_pT.port, dP_CTW1.port_a) annotation (Line(
        points={{140,-50},{140,-60},{117,-60}}, color={0,127,255}));
  connect(dP_CTW1.port_b, HEX.port_a1) annotation (Line(
        points={{103,-60},{60,-60},{60,52},{40,52}}, color={0,
          127,255}));

  connect(resistance_tank.port_a, tee.port_3)
    annotation (Line(points={{-60,-37},{-60,-50}}, color={0,127,255}));
  connect(resistance_tank.port_b, press_CDU.port)
    annotation (Line(points={{-60,-23},{-60,-12.4}}, color={0,127,255}));
  connect(HEX.port_b1, tee.port_1) annotation (Line(points={{20,52},{0,52},{0,
          -60},{-50,-60},{-50,-60}}, color={0,127,255}));
  connect(CabSup_pT.port, port_b2) annotation (Line(points={{-140,-50},{-140,
          -60},{-180,-60}}, color={0,127,255}));
  connect(controlBus.CDUP_Nrel, CDUP.inputSignal) annotation (Line(
      points={{0,100},{-180,100},{-180,-20},{-100,-20},{-100,-53}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(CDUP.port_a, tee.port_2)
    annotation (Line(points={{-90,-60},{-70,-60}}, color={0,127,255}));
  connect(CDUP.port_b, port_b2)
    annotation (Line(points={{-110,-60},{-180,-60}}, color={0,127,255}));
  annotation (experiment(StopTime=1, __Dymola_Algorithm="Dassl"));
end v0;
