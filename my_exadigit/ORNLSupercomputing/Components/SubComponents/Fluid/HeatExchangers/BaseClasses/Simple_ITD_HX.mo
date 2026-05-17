within ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.BaseClasses;
model Simple_ITD_HX "Simple HEX using ITD for UA Calc."
import TRANSFORM.Math.linspace_1D;
import TRANSFORM.Math.linspaceRepeat_1D;

  import
    TRANSFORM.Units.Conversions.Functions.Volume_m3.from_galUS;

  replaceable package Medium_1 = Modelica.Media.Interfaces.PartialMedium "Fluid 1 medium"
    annotation (choicesAllMatching=true);
  replaceable package Medium_2 = Modelica.Media.Interfaces.PartialMedium "Fluid 2 medium"
    annotation (choicesAllMatching=true);

  parameter Integer nV = 1 "# of fluid volumes on each side";

  // parallel flow not currently implmented
  parameter Boolean counterCurrent=true "Swap side 2 heatPort vector" annotation (Evaluate=true, Dialog(enable=false));
  Modelica.Units.SI.TemperatureDifference dT_ITD;

  constant Modelica.Units.SI.Volume V_1=from_galUS(48.3-21.9) "Fluid volume";
  constant Modelica.Units.SI.Volume V_2=from_galUS(48.3-21.9) "Fluid volume";

  input Modelica.Units.SI.ThermalConductance UA
    "Overall heat transfer coefficient" annotation (Dialog(group="Inputs"));
  constant TRANSFORM.Units.NonDim CF=1.0 "Correction factor"
    annotation (Dialog(group="Inputs"));
  parameter TRANSFORM.Units.NonDim CFs[nV]=fill(CF, nV) "if non-uniform then set"
    annotation (Dialog(group="Inputs"));

// Initialization: Fluid 1
  parameter Modelica.Units.SI.AbsolutePressure[nV] ps_start_1=linspace_1D(
      p_a_start_1,
      p_b_start_1,
      nV) "Pressure" annotation (Dialog(tab="Initialization: Fluid 1", group="Start Value: Absolute Pressure"));
  parameter Modelica.Units.SI.AbsolutePressure p_a_start_1=Medium_1.p_default
    "Pressure at port a" annotation (Dialog(tab="Initialization: Fluid 1",
        group="Start Value: Absolute Pressure"));
  parameter Modelica.Units.SI.AbsolutePressure p_b_start_1=p_a_start_1 + (if
      m_flow_start_1 > 0 then -1e3 elseif m_flow_start_1 < 0 then -1e3 else 0)
    "Pressure at port b" annotation (Dialog(tab="Initialization: Fluid 1",
        group="Start Value: Absolute Pressure"));
  parameter Boolean use_Ts_start_1=true
    "Use T_start if true, otherwise h_start" annotation (Evaluate=true, Dialog(
        tab="Initialization: Fluid 1", group="Start Value: Temperature"));
  parameter Modelica.Units.SI.Temperature Ts_start_1[nV]=linspace_1D(
      T_a_start_1,
      T_b_start_1,
      nV) "Temperature" annotation (Evaluate=true, Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Temperature",
      enable=use_Ts_start_1));
  parameter Modelica.Units.SI.Temperature T_a_start_1=Medium_1.T_default
    "Temperature at port a" annotation (Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Temperature",
      enable=use_Ts_start_1));
  parameter Modelica.Units.SI.Temperature T_b_start_1=T_a_start_1
    "Temperature at port b" annotation (Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Temperature",
      enable=use_Ts_start_1));
  parameter Modelica.Units.SI.SpecificEnthalpy[nV] hs_start_1=if not
      use_Ts_start_1 then linspace_1D(
      h_a_start_1,
      h_b_start_1,
      nV) else {Medium_1.specificEnthalpy_pTX(
      ps_start_1[i],
      Ts_start_1[i],
      Xs_start_1[i, 1:Medium_1.nX]) for i in 1:nV} "Specific enthalpy"
    annotation (Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Specific Enthalpy",
      enable=not use_Ts_start_1));
  parameter Modelica.Units.SI.SpecificEnthalpy h_a_start_1=
      Medium_1.specificEnthalpy_pTX(
      p_a_start_1,
      T_a_start_1,
      X_a_start_1) "Specific enthalpy at port a" annotation (Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Specific Enthalpy",
      enable=not use_Ts_start_1));
  parameter Modelica.Units.SI.SpecificEnthalpy h_b_start_1=
      Medium_1.specificEnthalpy_pTX(
      p_b_start_1,
      T_b_start_1,
      X_b_start_1) "Specific enthalpy at port b" annotation (Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Specific Enthalpy",
      enable=not use_Ts_start_1));
  parameter Modelica.Units.SI.MassFraction Xs_start_1[nV,Medium_1.nX]=
      linspaceRepeat_1D(
      X_a_start_1,
      X_b_start_1,
      nV) "Mass fraction" annotation (Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Species Mass Fraction",
      enable=Medium_1.nXi > 0));
  parameter Modelica.Units.SI.MassFraction X_a_start_1[Medium_1.nX]=Medium_1.X_default
    "Mass fraction at port a" annotation (Dialog(tab="Initialization: Fluid 1",
        group="Start Value: Species Mass Fraction"));
  parameter Modelica.Units.SI.MassFraction X_b_start_1[Medium_1.nX]=X_a_start_1
    "Mass fraction at port b" annotation (Dialog(tab="Initialization: Fluid 1",
        group="Start Value: Species Mass Fraction"));
  parameter TRANSFORM.Units.ExtraProperty Cs_start_1[nV,Medium_1.nC]=
      linspaceRepeat_1D(
      C_a_start_1,
      C_b_start_1,
      nV) "Mass-Specific value" annotation (Dialog(
      tab="Initialization: Fluid 1",
      group="Start Value: Trace Substances",
      enable=Medium_1.nC > 0));
  parameter TRANSFORM.Units.ExtraProperty C_a_start_1[Medium_1.nC]=fill(0,
      Medium_1.nC) "Mass-Specific value at port a" annotation (Dialog(tab="Initialization: Fluid 1",
        group="Start Value: Trace Substances"));
  parameter TRANSFORM.Units.ExtraProperty C_b_start_1[Medium_1.nC]=C_a_start_1
    "Mass-Specific value at port b" annotation (Dialog(tab="Initialization: Fluid 1",
        group="Start Value: Trace Substances"));
  parameter Modelica.Units.SI.MassFlowRate m_flow_start_1=0 "Mass flow rate"
    annotation (Dialog(tab="Initialization: Fluid 1"));

// Initialization: Fluid 2
  parameter Modelica.Units.SI.AbsolutePressure[nV] ps_start_2=linspace_1D(
      p_a_start_2,
      p_b_start_2,
      nV) "Pressure" annotation (Dialog(tab="Initialization: Fluid 2", group="Start Value: Absolute Pressure"));
  parameter Modelica.Units.SI.AbsolutePressure p_a_start_2=Medium_2.p_default
    "Pressure at port a" annotation (Dialog(tab="Initialization: Fluid 2",
        group="Start Value: Absolute Pressure"));
  parameter Modelica.Units.SI.AbsolutePressure p_b_start_2=p_a_start_2 + (if
      m_flow_start_2 > 0 then -2e3 elseif m_flow_start_2 < 0 then -2e3 else 0)
    "Pressure at port b" annotation (Dialog(tab="Initialization: Fluid 2",
        group="Start Value: Absolute Pressure"));
  parameter Boolean use_Ts_start_2=true
    "Use T_start if true, otherwise h_start" annotation (Evaluate=true, Dialog(
        tab="Initialization: Fluid 2", group="Start Value: Temperature"));
  parameter Modelica.Units.SI.Temperature Ts_start_2[nV]=linspace_1D(
      T_a_start_2,
      T_b_start_2,
      nV) "Temperature" annotation (Evaluate=true, Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Temperature",
      enable=use_Ts_start_2));
  parameter Modelica.Units.SI.Temperature T_a_start_2=Medium_2.T_default
    "Temperature at port a" annotation (Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Temperature",
      enable=use_Ts_start_2));
  parameter Modelica.Units.SI.Temperature T_b_start_2=T_a_start_2
    "Temperature at port b" annotation (Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Temperature",
      enable=use_Ts_start_2));
  parameter Modelica.Units.SI.SpecificEnthalpy[nV] hs_start_2=if not
      use_Ts_start_2 then linspace_1D(
      h_a_start_2,
      h_b_start_2,
      nV) else {Medium_2.specificEnthalpy_pTX(
      ps_start_2[i],
      Ts_start_2[i],
      Xs_start_2[i, 1:Medium_2.nX]) for i in 1:nV} "Specific enthalpy"
    annotation (Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Specific Enthalpy",
      enable=not use_Ts_start_2));
  parameter Modelica.Units.SI.SpecificEnthalpy h_a_start_2=
      Medium_2.specificEnthalpy_pTX(
      p_a_start_2,
      T_a_start_2,
      X_a_start_2) "Specific enthalpy at port a" annotation (Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Specific Enthalpy",
      enable=not use_Ts_start_2));
  parameter Modelica.Units.SI.SpecificEnthalpy h_b_start_2=
      Medium_2.specificEnthalpy_pTX(
      p_b_start_2,
      T_b_start_2,
      X_b_start_2) "Specific enthalpy at port b" annotation (Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Specific Enthalpy",
      enable=not use_Ts_start_2));
  parameter Modelica.Units.SI.MassFraction Xs_start_2[nV,Medium_2.nX]=
      linspaceRepeat_1D(
      X_a_start_2,
      X_b_start_2,
      nV) "Mass fraction" annotation (Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Species Mass Fraction",
      enable=Medium_2.nXi > 0));
  parameter Modelica.Units.SI.MassFraction X_a_start_2[Medium_2.nX]=Medium_2.X_default
    "Mass fraction at port a" annotation (Dialog(tab="Initialization: Fluid 2",
        group="Start Value: Species Mass Fraction"));
  parameter Modelica.Units.SI.MassFraction X_b_start_2[Medium_2.nX]=X_a_start_2
    "Mass fraction at port b" annotation (Dialog(tab="Initialization: Fluid 2",
        group="Start Value: Species Mass Fraction"));
  parameter TRANSFORM.Units.ExtraProperty Cs_start_2[nV,Medium_2.nC]=
      linspaceRepeat_1D(
      C_a_start_2,
      C_b_start_2,
      nV) "Mass-Specific value" annotation (Dialog(
      tab="Initialization: Fluid 2",
      group="Start Value: Trace Substances",
      enable=Medium_2.nC > 0));
  parameter TRANSFORM.Units.ExtraProperty C_a_start_2[Medium_2.nC]=fill(0,
      Medium_2.nC) "Mass-Specific value at port a" annotation (Dialog(tab="Initialization: Fluid 2",
        group="Start Value: Trace Substances"));
  parameter TRANSFORM.Units.ExtraProperty C_b_start_2[Medium_2.nC]=C_a_start_2
    "Mass-Specific value at port b" annotation (Dialog(tab="Initialization: Fluid 2",
        group="Start Value: Trace Substances"));
    parameter Modelica.Units.SI.MassFlowRate m_flow_start_2=0 "Mass flow rate"
    annotation (Dialog(tab="Initialization: Fluid 2"));
// End Initialization

  TRANSFORM.Fluid.Interfaces.FluidPort_State port_a1(
    redeclare package Medium = Medium_1,
    m_flow(start=m_flow_start_1),
    p(start=volume_1[1].p_start),
    h_outflow(start=volume_1[1].h_start)) annotation (Placement(transformation(
          extent={{-110,30},{-90,50}}), iconTransformation(extent={{-110,30},{-90,
            50}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_b1(redeclare package
      Medium =
        Medium_1, m_flow(start=-m_flow_start_1)) annotation (Placement(
        transformation(extent={{90,30},{110,50}}), iconTransformation(extent={{90,
            30},{110,50}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_State port_a2(
    redeclare package Medium = Medium_2,
    m_flow(start=m_flow_start_2),
    p(start=volume_2[1].p_start),
    h_outflow(start=volume_2[1].h_start)) annotation (Placement(transformation(
          extent={{90,-50},{110,-30}}), iconTransformation(extent={{90,-50},{110,
            -30}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_b2(redeclare package
      Medium =
        Medium_2, m_flow(start=-m_flow_start_2)) annotation (Placement(
        transformation(extent={{-110,-50},{-90,-30}}), iconTransformation(
          extent={{-110,-50},{-90,-30}})));
  TRANSFORM.Fluid.Volumes.SimpleVolume volume_1[nV](
    redeclare package Medium = Medium_1,
    each energyDynamics=energyDynamics_1,
    p_start=ps_start_1,
    each use_T_start=false,
    T_start=Ts_start_1,
    h_start=hs_start_1,
    X_start=Xs_start_1,
    C_start=Cs_start_1,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        ( each V=V_1/nV),
    each use_HeatPort=true)
    annotation (Placement(transformation(extent={{-40,30},{-20,50}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance resistance_1[nV](
      redeclare package Medium = Medium_1, each R=R_1/nV)
    annotation (Placement(transformation(extent={{20,30},{40,50}})));
  TRANSFORM.Fluid.Volumes.SimpleVolume volume_2[nV](
    redeclare package Medium = Medium_2,
    each energyDynamics=energyDynamics_2,
    p_start=ps_start_2,
    each use_T_start=false,
    T_start=Ts_start_2,
    h_start=hs_start_2,
    X_start=Xs_start_2,
    C_start=Cs_start_2,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        ( each V=V_2/nV),
    each use_HeatPort=true)
    annotation (Placement(transformation(extent={{40,-30},{20,-50}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance resistance_2[nV](
      redeclare package Medium = Medium_2, each R=R_2/nV)
    annotation (Placement(transformation(extent={{-20,-50},{-40,-30}})));
  TRANSFORM.Fluid.Sensors.TemperatureTwoPort sensor_T_a1(redeclare package
              Medium =
               Medium_1)
    annotation (Placement(transformation(extent={{-80,30},{-60,50}})));
  TRANSFORM.Fluid.Sensors.TemperatureTwoPort sensor_T_b1(redeclare package
              Medium =
               Medium_1)
    annotation (Placement(transformation(extent={{60,30},{80,50}})));
  TRANSFORM.Fluid.Sensors.TemperatureTwoPort sensor_T_a2(redeclare package
              Medium =
               Medium_2)
    annotation (Placement(transformation(extent={{80,-50},{60,-30}})));
  TRANSFORM.Fluid.Sensors.TemperatureTwoPort sensor_T_b2(redeclare package
              Medium =
               Medium_2)
    annotation (Placement(transformation(extent={{-60,-50},{-80,-30}})));
  input TRANSFORM.Units.HydraulicResistance R_1=(p_a_start_1 - p_b_start_1)/
      m_flow_start_1 "Hydraulic resistance" annotation (Dialog(group="Inputs"));
  input TRANSFORM.Units.HydraulicResistance R_2=(p_a_start_2 - p_b_start_2)/
      m_flow_start_2 "Hydraulic resistance" annotation (Dialog(group="Inputs"));

  Modelica.Units.SI.Power Q_flow;

  parameter Modelica.Fluid.Types.Dynamics energyDynamics_1=Modelica.Fluid.Types.Dynamics.DynamicFreeInitial
    "Formulation of energy balances"
    annotation (Dialog(tab="Advanced", group="Dynamics"));
  parameter Modelica.Fluid.Types.Dynamics energyDynamics_2=energyDynamics_1
    "Formulation of energy balances"
    annotation (Dialog(tab="Advanced", group="Dynamics"));
  input Modelica.Units.SI.ThermalResistance R_val[nV]={1/(UA/nV*CFs[i]) for i in
          1:nV} "Thermal resistance";
  Modelica.Blocks.Sources.RealExpression boundary_1_input[nV](each y=-Q_flow/nV)
    annotation (Placement(transformation(extent={{30,80},{10,100}})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.HeatFlow boundary_1[nV](each
      use_port=true) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=90,
        origin={0,76})));
  Modelica.Blocks.Sources.RealExpression boundary_2_input[nV](each y=Q_flow/nV)
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.HeatFlow boundary_2[nV](each
      use_port=true) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=90,
        origin={30,-14})));
equation
  Q_flow = UA*dT_ITD;
  dT_ITD = smooth(1, if abs(sensor_T_a1.T - sensor_T_a2.T) <= 1e-4 then 0 else (sensor_T_a1.T - sensor_T_a2.T)) "Inlet Temperature Difference";
  connect(sensor_T_a1.port_b, volume_1[1].port_a);
  connect(volume_1[1].port_b, resistance_1[1].port_a);
  for i in 2:nV loop
    connect(resistance_1[i - 1].port_b, volume_1[i].port_a);
    connect(volume_1[i].port_b, resistance_1[i].port_a);
  end for;
  connect(resistance_1[nV].port_b, sensor_T_b1.port_a);

  connect(sensor_T_a2.port_b, volume_2[1].port_a);
  connect(volume_2[1].port_b, resistance_2[1].port_a);
  for i in 2:nV loop
    connect(resistance_2[i - 1].port_b, volume_2[i].port_a);
    connect(volume_2[i].port_b, resistance_2[i].port_a);
  end for;
  connect(resistance_2[nV].port_b, sensor_T_b2.port_a);
  connect(volume_1[1:nV].heatPort, boundary_1[1:nV].port)
    annotation (Line(points={{-30,34},{-30,26},{0,26},{0,58},{-6.10623e-16,58},{
          -6.10623e-16,66}},                     color={191,0,0}));
  connect(port_a1, sensor_T_a1.port_a)
    annotation (Line(points={{-100,40},{-80,40}}, color={0,127,255}));
  connect(sensor_T_b1.port_b, port_b1)
    annotation (Line(points={{80,40},{100,40}}, color={0,127,255}));
  connect(port_a2, sensor_T_a2.port_a)
    annotation (Line(points={{100,-40},{80,-40}}, color={0,127,255}));
  connect(sensor_T_b2.port_b, port_b2)
    annotation (Line(points={{-80,-40},{-100,-40}}, color={0,127,255}));
  connect(boundary_2[1:nV].port, volume_2[1:nV].heatPort)
    annotation (Line(points={{30,-24},{30,-34}}, color={191,0,0}));
  connect(boundary_1_input.y, boundary_1.Q_flow_ext) annotation (Line(points={{9,90},{
          0,90},{0,80},{3.33067e-16,80}},      color={0,0,127}));
  connect(boundary_2_input.y, boundary_2.Q_flow_ext) annotation (Line(points={{11,0},{
          30,0},{30,-10}},                     color={0,0,127}));
  annotation (
    defaultComponentName="lmtd_HX",
    Icon(coordinateSystem(preserveAspectRatio=false), graphics={
        Rectangle(
          extent={{-100,60},{100,-60}},
          lineColor={0,0,0},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Line(points={{-88,-40},{-60,-40},{-30,0},{0,-40},{30,0},{60,-40},{88,-40}},
            color={28,108,200}),
        Line(points={{-88,40},{-30,40},{0,0},{30,40},{88,40}}, color={238,46,47}),
        Text(
          extent={{-149,-68},{151,-108}},
          lineColor={0,0,255},
          textString="%name")}),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Documentation(info="<html>
<p>Assumption:</p>
<p>Side 1 is hot side (i.e,. if Q_flow &lt; 0 then heat is going from Side 1 to Side 2)</p>
</html>"));
end Simple_ITD_HX;
