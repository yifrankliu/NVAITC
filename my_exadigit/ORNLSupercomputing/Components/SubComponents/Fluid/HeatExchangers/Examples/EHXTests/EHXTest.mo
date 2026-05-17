within ORNLSupercomputing.Components.SubComponents.Fluid.HeatExchangers.Examples.EHXTests;
model EHXTest "Test EHX"
  extends Modelica.Icons.Example;
  package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium;
  Modelica.Fluid.Sources.MassFlowSource_T HTWPSource(
    redeclare package Medium = Medium,
    use_m_flow_in=false,
    m_flow=162,
    T=308.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{-8,-8},{8,8}},
        rotation=0,
        origin={-72,20})));
  Modelica.Fluid.Sources.Boundary_pT CTWPSink(
    redeclare package Medium = Medium,
    p(displayUnit="bar") = 99999.99999999999*(38.7*0.0689476),
    T(displayUnit="degC") = 303.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{7,-7},{-7,7}},
        rotation=180,
        origin={-71,-21})));
  Modelica.Fluid.Sources.MassFlowSource_T CTWPSource(
    redeclare package Medium = Medium,
    m_flow=250,
    T=293.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{-8,-8},{8,8}},
        rotation=180,
        origin={72,-20})));
  Modelica.Fluid.Sources.Boundary_pT CabinetSink(
    redeclare package Medium = Medium,
    p(displayUnit="bar") = 99999.99999999999*(84.7*0.0689476),
    T(displayUnit="degC") = 309.15,
    nPorts=1) annotation (Placement(transformation(
        extent={{7,7},{-7,-7}},
        rotation=0,
        origin={71,21})));
  TRANSFORM.Fluid.Sensors.PressureTemperature HWTP_pT2(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{20,36},{40,56}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature CWTP_pT2(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{-38,-30},{-18,-50}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature HWTP_pT1(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{-38,36},{-18,56}})));
  TRANSFORM.Fluid.Sensors.PressureTemperature CWTP_pT1(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2)
    annotation (Placement(transformation(extent={{22,-30},{42,-50}})));
  SubComponents.Fluid.HeatExchangers.EHX EHX
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
equation
  connect(HTWPSource.ports[1], EHX.port_a1) annotation (Line(points={{-64,20},{
          -28,20},{-28,4},{-10,4}},                        color={0,127,255}));
  connect(EHX.port_a2, CTWPSource.ports[1]) annotation (Line(points={{10,-4},{
          32,-4},{32,-20},{64,-20}},  color={0,127,255}));
  connect(EHX.port_b1, CabinetSink.ports[1]) annotation (Line(points={{10,4},{
          30,4},{30,21},{64,21}},           color={0,127,255}));
  connect(EHX.port_b2, CTWPSink.ports[1]) annotation (Line(points={{-10,-4},{
          -28,-4},{-28,-21},{-64,-21}},  color={0,127,255}));
  connect(HWTP_pT1.port, EHX.port_a1) annotation (Line(points={{-28,36},{-28,4},
          {-10,4}},                              color={0,127,255}));
  connect(HWTP_pT2.port, EHX.port_b1)
    annotation (Line(points={{30,36},{30,4},{10,4}},
                                              color={0,127,255}));
  connect(CWTP_pT2.port, EHX.port_b2) annotation (Line(points={{-28,-30},{-28,
          -4},{-10,-4}},                                       color={0,127,
          255}));
  connect(CWTP_pT1.port, EHX.port_a2) annotation (Line(points={{32,-30},{32,-4},
          {10,-4}},                                       color={0,127,255}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    experiment(StopTime=100, __Dymola_Algorithm="Dassl"));
end EHXTest;
