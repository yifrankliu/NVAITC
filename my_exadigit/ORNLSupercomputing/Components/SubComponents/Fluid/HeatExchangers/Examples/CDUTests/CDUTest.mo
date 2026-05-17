within ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.Examples.CDUTests;
model CDUTest "Test CDU HEX"
  extends Modelica.Icons.Example;
  package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium;
  Modelica.Fluid.Sources.MassFlowSource_T CabinetSource(
    redeclare package Medium = Medium,
    use_m_flow_in=false,
    use_T_in=false,
    m_flow=15.36,
    T=322.45,
    nPorts=1) annotation (Placement(transformation(
        extent={{-8,-8},{8,8}},
        rotation=0,
        origin={-79,18})));
  Modelica.Fluid.Sources.Boundary_pT FacilitySink(
    redeclare package Medium = Medium,
    use_p_in=false,
    use_T_in=false,
    p(displayUnit="bar") = 500000,
    T(displayUnit="degC") = 320.75,
    nPorts=1) annotation (Placement(transformation(
        extent={{7,-7},{-7,7}},
        rotation=180,
        origin={-79,-20})));
  Modelica.Fluid.Sources.MassFlowSource_T FacilitySource(
    redeclare package Medium = Medium,
    use_m_flow_in=false,
    use_T_in=false,
    m_flow=11.62,
    T=303.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{-8,-8},{8,8}},
        rotation=180,
        origin={76,-20})));
  Modelica.Fluid.Sources.Boundary_pT CabinetSink(
    redeclare package Medium = Medium,
    use_p_in=false,
    use_T_in=false,
    p(displayUnit="bar") = 400000,
    T(displayUnit="degC") = 309.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{7,7},{-7,-7}},
        rotation=0,
        origin={75,19})));
  TRANSFORM.Fluid.Sensors.PressureTemperature CabSin_pT(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{10,30},{30,50}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature FacSin_pT(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{-30,-36},{-10,-56}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature CabSou_pT(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{-30,30},{-10,50}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature FacSou_pT(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{10,-36},{30,-56}})));
  CDU_HEX cDU_HEX
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
equation
  connect(CabinetSource.ports[1], cDU_HEX.port_a1) annotation (Line(points={{-71,18},
          {-20,18},{-20,4},{-10,4}},          color={0,127,255}));
  connect(cDU_HEX.port_a2, FacilitySource.ports[1]) annotation (Line(points={{10,-4},
          {20,-4},{20,-20},{68,-20}},       color={0,127,255}));
  connect(cDU_HEX.port_b1, CabinetSink.ports[1]) annotation (Line(points={{10,4},{
          20,4},{20,19},{68,19}},       color={0,127,255}));
  connect(cDU_HEX.port_b2, FacilitySink.ports[1]) annotation (Line(points={{-10,-4},
          {-20,-4},{-20,-20},{-72,-20}}, color={0,127,255}));
  connect(CabSou_pT.port, cDU_HEX.port_a1) annotation (Line(points={{-20,30},{
          -20,4},{-10,4}},                            color={0,127,255}));
  connect(CabSin_pT.port, cDU_HEX.port_b1)
    annotation (Line(points={{20,30},{20,4},{10,4}},
                                               color={0,127,255}));
  connect(FacSin_pT.port, cDU_HEX.port_b2) annotation (Line(points={{-20,-36},{
          -20,-4},{-10,-4}},                                   color={0,127,
          255}));
  connect(FacSou_pT.port, cDU_HEX.port_a2) annotation (Line(points={{20,-36},{
          20,-4},{10,-4}},                                color={0,127,255}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    experiment(StopTime=100, __Dymola_Algorithm="Dassl"));
end CDUTest;
