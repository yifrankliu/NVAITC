within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.HotWaterLoop.Controls;
model CS_Constant
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
  parameter Integer HTWP_nPUMP_start=1 "Starting no. of HTWPs";
  // Control Systems
  parameter Real k_s=1.0;
  parameter Real Ti=30;
  // s
  parameter Real gain=14.8;

  Modelica.Blocks.Routing.Replicator replicator(nout=4)
    annotation (Placement(transformation(extent={{0,36},{20,56}})));
  Modelica.Blocks.Sources.Constant opening_valve_heatExchanger_cold(k=0.5)
    annotation (Placement(transformation(extent={{-38,-60},{-18,-40}})));
  Modelica.Blocks.Routing.Replicator replicator2(nout=4)
    annotation (Placement(transformation(extent={{2,-60},{22,-40}})));
  Modelica.Blocks.Sources.Constant opening_valve(k=0.5)
    annotation (Placement(transformation(extent={{-40,6},{-20,26}})));
  Modelica.Blocks.Routing.Replicator replicator1(nout=4)
    annotation (Placement(transformation(extent={{0,6},{20,26}})));
  Modelica.Blocks.Sources.Constant Nrel_pump(k=1)
    annotation (Placement(transformation(extent={{-36,36},{-16,56}})));
  Modelica.Blocks.Sources.Constant opening_valve_heatExchanger_hot(k=0.5)
    annotation (Placement(transformation(extent={{-34,-26},{-14,-6}})));
  Modelica.Blocks.Routing.Replicator replicator3(nout=4)
    annotation (Placement(transformation(extent={{6,-26},{26,-6}})));
equation
  connect(controlBus.Nrel_HTWP, replicator.y) annotation (Line(
      points={{0,-100},{180,-100},{180,46},{21,46}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));

  connect(controlBus.valveEHXb, replicator2.y) annotation (Line(
      points={{0,-100},{122,-100},{122,-50},{23,-50}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(opening_valve_heatExchanger_cold.y, replicator2.u)
    annotation (Line(points={{-17,-50},{0,-50}}, color={0,0,127}));
  connect(opening_valve.y, replicator1.u)
    annotation (Line(points={{-19,16},{-2,16}}, color={0,0,127}));
  connect(controlBus.valveHTWP, replicator1.y) annotation (Line(
      points={{0,-100},{130,-100},{130,16},{21,16}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(Nrel_pump.y, replicator.u)
    annotation (Line(points={{-15,46},{-2,46}}, color={0,0,127}));
  connect(opening_valve_heatExchanger_hot.y, replicator3.u)
    annotation (Line(points={{-13,-16},{4,-16}}, color={0,0,127}));
  connect(controlBus.valveEHX, replicator3.y) annotation (Line(
      points={{0,-100},{98,-100},{98,-16},{27,-16}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
end CS_Constant;
