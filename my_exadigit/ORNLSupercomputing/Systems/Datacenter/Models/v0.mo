within ORNLSupercomputing.Systems.Datacenter.Models;
model v0
  extends
    ORNLSupercomputing.Systems.Datacenter.BaseClasses.BaseClasses_A.PartialModel_A(
    port_b_nominal(p=data.volHTWR_pinit, T=data.volHTWR_Tinit),
    port_a_nominal(
      p=data.volHTWS_pinit,
      T=data.volHTWS_Tinit,
      m_flow=data.bypass_nom_flow),
    redeclare replaceable Controls.CS_BypassValveControl controls,
    redeclare replaceable Data.Data data,
    redeclare replaceable Sources.NULL sources,
    summary(m_flow_bypass=bypassPipe.port_a.m_flow));

  TRANSFORM.Fluid.Volumes.MixingVolume plenum_inlet(
    redeclare package Medium = Medium,
    p_start=data.volHTWS_pinit,
    T_start=data.volHTWS_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=6.5),
    nPorts_a=1,
    nPorts_b=structure.computeBlock.n_int + 1)
    annotation (Placement(transformation(extent={{-70,-10},{-50,10}})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet(
    redeclare package Medium = Medium,
    p_start=data.volHTWR_pinit,
    T_start=data.volHTWR_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=6.5),
    nPorts_a=structure.computeBlock.n_int + 1,
    nPorts_b=1)
    annotation (Placement(transformation(extent={{50,-10},{70,10}})));
  replaceable Systems.CoolingBlock.Models.v0 computeBlock[structure.computeBlock.n_int](
     redeclare Systems.CoolingBlock.Systems.CDU.Models.v0 cdu) constrainedby
    Systems.CoolingBlock.BaseClasses.BaseClasses_A.PartialModel_A(redeclare
      package Medium = Medium) annotation (Placement(transformation(extent={{-10,
            -10},{10,10}})), choicesAllMatching=true);

  TRANSFORM.Fluid.Valves.ValveLinear valveBypass(
    redeclare package Medium = Medium,
    dp_start(displayUnit="Pa") = 50,
    m_flow_start=10,
    dp_nominal(displayUnit="Pa") = data.dP_valve_bypass,
    m_flow_nominal=data.bypass_nom_flow)
    annotation (Placement(transformation(extent={{-30,40},{-10,60}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    resistance_inlet(redeclare package Medium = Medium, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1)/
        port_a_nominal.m_flow) annotation (Placement(transformation(
          extent={{-100,-10},{-80,10}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
    resistance_outlet(redeclare package Medium = Medium, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1)/
        port_a_nominal.m_flow) annotation (Placement(transformation(
          extent={{80,-10},{100,10}})));
  TRANSFORM.Fluid.Pipes.parallelFlow nFlow_toComputeBlocks(redeclare package
      Medium =         Medium, final nParallel=structure.computeBlock.n)
    if structure.computeBlock.useParallel
    annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
  TRANSFORM.Fluid.Pipes.parallelFlow nFlow_fromComputeBlocks(redeclare package
      Medium =         Medium, final nParallel=structure.computeBlock.n)
    if structure.computeBlock.useParallel
    annotation (Placement(transformation(extent={{40,-10},{20,10}})));
  TRANSFORM.Fluid.FittingsAndResistances.PressureLoss
                                   bypassPipe(redeclare package Medium = Medium, dp0=data.dP_bypass)
                                            annotation (Placement(
        transformation(extent={{10,40},{30,60}},   rotation=0)));

  TRANSFORM.Fluid.Sensors.MassFlowRate sensor_m_flow(redeclare package Medium
      = Medium)
    annotation (Placement(transformation(extent={{-140,-10},{-120,10}})));
equation
  connect(resistance_inlet.port_b, plenum_inlet.port_a[1])
    annotation (Line(points={{-83,0},{-66,0}}, color={0,127,255}));
  connect(controlBus.opening_bypass, valveBypass.opening) annotation (
     Line(
      points={{0,100},{-20,100},{-20,58}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(plenum_outlet.port_b[1], resistance_outlet.port_a)
    annotation (Line(points={{66,0},{83,0}}, color={0,127,255}));
  connect(port_b, resistance_outlet.port_b)
    annotation (Line(points={{180,0},{97,0}}, color={0,127,255}));

  connect(plenum_inlet.port_b[1], valveBypass.port_a);
  connect(plenum_outlet.port_a[1], bypassPipe.port_b);
  for i in 1:structure.computeBlock.n_int loop
    if structure.computeBlock.useParallel then
      connect(plenum_inlet.port_b[i + 1], nFlow_toComputeBlocks.port_1);
      connect(nFlow_toComputeBlocks.port_n, computeBlock[i].port_a);

      connect(computeBlock[i].port_b, nFlow_fromComputeBlocks.port_n);
      connect(nFlow_fromComputeBlocks.port_1, plenum_outlet.port_a[i +
        1]);
    else
      connect(plenum_inlet.port_b[i + 1], computeBlock[i].port_a);

      connect(computeBlock[i].port_b, plenum_outlet.port_a[i + 1]);
    end if;
  end for;

  connect(valveBypass.port_b, bypassPipe.port_a)
    annotation (Line(points={{-10,50},{13,50}},color={0,127,255}));
  connect(port_a, sensor_m_flow.port_a)
    annotation (Line(points={{-180,0},{-140,0}}, color={0,127,255}));
  connect(sensor_m_flow.port_b, resistance_inlet.port_a)
    annotation (Line(points={{-120,0},{-97,0}}, color={0,127,255}));
  connect(controlBus.m_flow_supply, sensor_m_flow.m_flow) annotation (Line(
      points={{0,100},{-130,100},{-130,3.6}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (experiment(StopTime=1, __Dymola_Algorithm="Dassl"));
end v0;
