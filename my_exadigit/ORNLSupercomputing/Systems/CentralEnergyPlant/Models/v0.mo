within ORNLSupercomputing.Systems.CentralEnergyPlant.Models;
model v0
  extends BaseClasses.BaseClasses_A.PartialModel_A(
    port_a_nominal(
      p=hotWaterLoop[1].port_a1_nominal.p,
      T=hotWaterLoop[1].port_a1_nominal.T,
      m_flow=hotWaterLoop[1].port_a1_nominal.m_flow),
    port_b_nominal(p=hotWaterLoop[1].port_b1_nominal.p, T=hotWaterLoop[1].port_b1_nominal.T),
    redeclare replaceable Controls.v0 controls,
    redeclare replaceable Data.NULL data,
    redeclare replaceable Sources.NULL sources);

  replaceable package Medium_inner =
      TRANSFORM.Media.Fluids.Water.LinearWaterHot_pT                                 constrainedby
    Modelica.Media.Interfaces.PartialMedium  annotation (
      choicesAllMatching=true);
  replaceable Systems.HotWaterLoop.Models.v0 hotWaterLoop[structure.hotWaterLoop.n_int]
    constrainedby Systems.HotWaterLoop.BaseClasses.BaseClasses_A.PartialModel_A(
      redeclare package Medium_1 = Medium, redeclare package Medium_2 =
        Medium_inner) annotation (Placement(transformation(extent={{-10,-16},{
            10,4}})), choicesAllMatching=true);
  replaceable Systems.CoolingTowerLoop.Models.v0 coolingTowerLoop[structure.coolingTowerLoop.n_int]
    constrainedby
    Systems.CoolingTowerLoop.BaseClasses.BaseClasses_A.PartialModel_A(
      redeclare package Medium = Medium_inner) annotation (Placement(
        transformation(extent={{-10,-70},{10,-50}})), choicesAllMatching=true);
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
                                                      resistance_inlet_intermediateLoop(
      redeclare package Medium = Medium, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1)/
        port_a_nominal.m_flow)
    annotation (Placement(transformation(extent={{-100,-10},{-80,10}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_inlet_intermediateLoop(
    redeclare package Medium = Medium,
    p_start=port_a_start.p,
    T_start=port_a_start.T,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=1),
    nPorts_a=1,
    nPorts_b=structure.hotWaterLoop.n_int)
    annotation (Placement(transformation(extent={{-70,-10},{-50,10}})));
  TRANSFORM.Fluid.Pipes.parallelFlow nFlow_inlet_intermediateLoop(redeclare
      package Medium = Medium, final nParallel=structure.hotWaterLoop.n)
    if structure.hotWaterLoop.useParallel
    annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
  TRANSFORM.Fluid.Pipes.parallelFlow nFlow_outlet_intermediateLoop(redeclare
      package Medium = Medium, final nParallel=structure.hotWaterLoop.n)
    if structure.hotWaterLoop.useParallel
    annotation (Placement(transformation(extent={{40,-10},{20,10}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet_intermediateLoop(
    redeclare package Medium = Medium,
    p_start=port_b_start.p,
    T_start=port_b_start.T,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=1),
    nPorts_a=structure.hotWaterLoop.n_int,
    nPorts_b=1)
    annotation (Placement(transformation(extent={{50,-10},{70,10}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
                                                      resistance_outlet_intermediateLoop(
      redeclare package Medium = Medium, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1)/
        port_a_nominal.m_flow)
    annotation (Placement(transformation(extent={{80,-10},{100,10}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet_coolingTowerLoop(
    redeclare package Medium = Medium_inner,
    p_start=coolingTowerLoop[1].port_b_start.p,
    T_start=coolingTowerLoop[1].port_b_start.T,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=10),
    nPorts_a=structure.coolingTowerLoop.n_int,
    nPorts_b=structure.hotWaterLoop.n_int)
    annotation (Placement(transformation(extent={{50,-70},{70,-50}})));
  TRANSFORM.Fluid.Pipes.parallelFlow nFlow_outlet_coolingTowerLoop(redeclare
      package Medium = Medium_inner,
                               final nParallel=structure.coolingTowerLoop.n)
    if structure.coolingTowerLoop.useParallel
    annotation (Placement(transformation(extent={{40,-70},{20,-50}})));
  TRANSFORM.Fluid.Pipes.parallelFlow nFlow_inlet_coolingTowerLoop(redeclare
      package Medium = Medium_inner,
                               final nParallel=structure.coolingTowerLoop.n)
    if structure.coolingTowerLoop.useParallel
    annotation (Placement(transformation(extent={{-40,-70},{-20,-50}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_inlet_coolingTowerLoop(
    redeclare package Medium = Medium_inner,
    p_start=coolingTowerLoop[1].port_a_start.p,
    T_start=coolingTowerLoop[1].port_a_start.T,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=10),
    nPorts_b=structure.coolingTowerLoop.n_int,
    nPorts_a=structure.hotWaterLoop.n_int)
    annotation (Placement(transformation(extent={{-70,-70},{-50,-50}})));

equation
        if structure.coolingTowerLoop.useParallel then
    connect(plenum_inlet_coolingTowerLoop.port_b[1], nFlow_inlet_coolingTowerLoop.port_1);
    connect(nFlow_inlet_coolingTowerLoop.port_n,coolingTowerLoop [1].port_a);

    connect(coolingTowerLoop[1].port_b, nFlow_outlet_coolingTowerLoop.port_n);
    connect(nFlow_outlet_coolingTowerLoop.port_1, plenum_outlet_coolingTowerLoop.port_a[1]);
  else
    connect(plenum_inlet_coolingTowerLoop.port_b,coolingTowerLoop. port_a);

    connect(coolingTowerLoop.port_b, plenum_outlet_coolingTowerLoop.port_a);
  end if;

  connect(resistance_inlet_intermediateLoop.port_a, port_a)
    annotation (Line(points={{-97,0},{-180,0}}, color={0,127,255}));
  connect(resistance_inlet_intermediateLoop.port_b, plenum_inlet_intermediateLoop.port_a[1])
    annotation (Line(points={{-83,0},{-66,0}}, color={0,127,255}));
  connect(resistance_outlet_intermediateLoop.port_b, port_b)
    annotation (Line(points={{97,0},{180,0}}, color={0,127,255}));
  connect(resistance_outlet_intermediateLoop.port_a, plenum_outlet_intermediateLoop.port_b[1])
    annotation (Line(points={{83,0},{66,0}}, color={0,127,255}));
  if structure.hotWaterLoop.useParallel then
    connect(plenum_inlet_intermediateLoop.port_b[1], nFlow_inlet_intermediateLoop.port_1);
    connect(nFlow_inlet_intermediateLoop.port_n, hotWaterLoop[1].port_a1);

    connect(hotWaterLoop[1].port_b1, nFlow_outlet_intermediateLoop.port_n);
    connect(nFlow_outlet_intermediateLoop.port_1, plenum_outlet_intermediateLoop.port_a[1]);
  else
    connect(plenum_inlet_intermediateLoop.port_b, hotWaterLoop.port_a1);

    connect(hotWaterLoop.port_b1, plenum_outlet_intermediateLoop.port_a);
  end if;
  connect(hotWaterLoop.port_b2, plenum_inlet_coolingTowerLoop.port_a)
    annotation (Line(points={{-10,-12},{-80,-12},{-80,-60},{-66,-60}}, color={0,
          127,255}));
  connect(plenum_outlet_coolingTowerLoop.port_b, hotWaterLoop.port_a2)
    annotation (Line(points={{66,-60},{80,-60},{80,-12},{10,-12}}, color={0,127,
          255}));
  connect(controlBus.intermediateLoop, hotWaterLoop[1].controlBus) annotation (
      Line(
      points={{0,100},{0,4}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(coolingTowerLoop[1].controlBus, controlBus.coolingTowerLoop)
    annotation (Line(
      points={{0,-50},{0,-40},{16,-40},{16,20},{0,20},{0,100}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (experiment(StopTime=1, __Dymola_Algorithm="Dassl"));
end v0;
