within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Tests;
model Test_dynamic "dynamic test of a cooling block with 3 cabinets"
  extends Test_steady(
    boundary_inlet(use_m_flow_in=true, use_T_in=true),
    boundary_outlet(use_p_in=true, use_T_in=true),
    simulator(cabinet(sources(Q_flow_total=data_external.y[1]/(50*simulator[1].structure.cabinet.n))),
        structure(cabinet(n=3, useParallel=true))));
  TRANSFORM.Fluid.Sensors.PressureTemperature HTWS_pT(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2) annotation (Placement(transformation(
        extent={{-8,-8},{8,8}},
        rotation=0,
        origin={-20,16})));
  TRANSFORM.Fluid.Sensors.PressureTemperature HTWR_pT(
    redeclare package Medium = Medium,
    precision=2,
    redeclare function iconUnit =
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi,
    precision2=2) annotation (Placement(transformation(
        extent={{-8.5,-8},{8.5,8}},
        rotation=0,
        origin={20.5,16})));
  Modelica.Blocks.Sources.CombiTimeTable data_external(
    tableOnFile=true,
    tableName="table",
    fileName=Modelica.Utilities.Files.loadResource("modelica://ORNLSupercomputing/../python/data/input_synthetic_data_comb.txt"),
    columns={2,3},
    extrapolation=Modelica.Blocks.Types.Extrapolation.HoldLastPoint)
    annotation (Placement(transformation(extent={{-10,38},{10,58}})));

  Modelica.Blocks.Sources.ExpSine fac_supply_mdot(
    amplitude=0.5,
    f=0.01,
    damping=0.0001,
    offset=5.0) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-110,22})));
  Modelica.Blocks.Sources.ExpSine fac_supply_temp(
    amplitude=5,
    f=0.01,
    damping=0.0001,
    offset=22 + 273.15) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-110,-10})));
  Modelica.Blocks.Sources.ExpSine fac_return_press(
    amplitude=0.1e5,
    f=0.01,
    damping=0.0001,
    offset=3.5e5) annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={110,22})));
  Modelica.Blocks.Sources.ExpSine fac_return_temp(
    amplitude=5,
    f=0.01,
    damping=0.0001,
    offset=28 + 273.15) annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={110,-10})));
equation
  connect(HTWS_pT.port, simulator[1].port_a)
    annotation (Line(points={{-20,8},{-20,0},{-10,0}}, color={0,127,255}));
  connect(HTWR_pT.port, simulator[1].port_b)
    annotation (Line(points={{20.5,8},{20.5,0},{10,0}}, color={0,127,255}));
  connect(fac_supply_mdot.y, boundary_inlet.m_flow_in) annotation (Line(points={
          {-99,22},{-90,22},{-90,8},{-80,8}}, color={0,0,127}));
  connect(fac_supply_temp.y, boundary_inlet.T_in) annotation (Line(points={{-99,
          -10},{-90,-10},{-90,4},{-82,4}}, color={0,0,127}));
  connect(boundary_outlet.p_in, fac_return_press.y)
    annotation (Line(points={{82,8},{90,8},{90,22},{99,22}}, color={0,0,127}));
  connect(boundary_outlet.T_in, fac_return_temp.y) annotation (Line(points={{82,
          4},{90,4},{90,-10},{99,-10}}, color={0,0,127}));
  annotation (experiment(StopTime=86400, __Dymola_Algorithm="Sdirk34hw"));
end Test_dynamic;
