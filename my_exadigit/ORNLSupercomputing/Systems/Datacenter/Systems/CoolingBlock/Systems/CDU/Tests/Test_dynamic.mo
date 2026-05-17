within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Tests;
model Test_dynamic "dynamic test of a CDU"
  extends Test_steady(
    boundary_inlet_1(use_m_flow_in=true, use_T_in=true),
    boundary_outlet_1(use_p_in=true, use_T_in=true),
    boundary_outlet_2(use_p_in=true, use_T_in=true),
    boundary_inlet_2(use_m_flow_in=true, use_T_in=true));

  Modelica.Blocks.Sources.ExpSine        fac_supply_mdot(
    amplitude=0.5,
    f=0.01,
    damping=0.0001,
    offset=5.0)
               annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-110,62})));
  Modelica.Blocks.Sources.ExpSine        fac_supply_temp(
    amplitude=5,
    f=0.01,
    damping=0.0001,
    offset=22 + 273.15)
                annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-110,30})));
  Modelica.Blocks.Sources.ExpSine        fac_return_temp(
    amplitude=5,
    f=0.01,
    damping=0.0001,
    offset=28 + 273.15)
                annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={110,30})));
  Modelica.Blocks.Sources.ExpSine        fac_return_press(
    amplitude=0.1e5,
    f=0.01,
    damping=0.0001,
    offset=3.5e5)          annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={110,62})));
  Modelica.Blocks.Sources.ExpSine        cab_mflow(
    amplitude=1,
    f=0.01,
    damping=0.0001,
    offset=8)
    annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={110,-16})));
  Modelica.Blocks.Sources.ExpSine        cab_source_temp(
    amplitude=3,
    f=0.01,
    damping=0.0001,
    offset=35 + 273.15)
                annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={110,-52})));
  Modelica.Blocks.Sources.ExpSine        cab_sink_temp(
    amplitude=2,
    f=0.01,
    damping=0.0001,
    offset=28 + 273.15)
                annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-110,-52})));
  Modelica.Blocks.Sources.ExpSine        cab_sink_press(
    amplitude=0.1e5,
    f=0.01,
    damping=0.0001,
    offset=5.5e5)       annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-110,-16})));
equation
  connect(fac_supply_mdot.y, boundary_inlet_1.m_flow_in) annotation (Line(
        points={{-99,62},{-90,62},{-90,48},{-80,48}},  color={0,0,127}));
  connect(fac_supply_temp.y, boundary_inlet_1.T_in) annotation (Line(points={{-99,30},
          {-90,30},{-90,44},{-82,44}},     color={0,0,127}));
  connect(boundary_outlet_1.p_in, fac_return_press.y) annotation (Line(points={{82,48},
          {82,50},{92,50},{92,62},{99,62}},        color={0,0,127}));
  connect(boundary_outlet_1.T_in, fac_return_temp.y) annotation (Line(points={{82,44},
          {92,44},{92,30},{99,30}},     color={0,0,127}));
  connect(boundary_inlet_2.m_flow_in, cab_mflow.y) annotation (Line(points={{80,-32},
          {94,-32},{94,-16},{99,-16}},      color={0,0,127}));
  connect(boundary_inlet_2.T_in, cab_source_temp.y) annotation (Line(points={{82,-36},
          {92,-36},{92,-52},{99,-52}},      color={0,0,127}));
  connect(cab_sink_temp.y, boundary_outlet_2.T_in) annotation (Line(points={{-99,-52},
          {-88,-52},{-88,-36},{-82,-36}},      color={0,0,127}));
  connect(cab_sink_press.y, boundary_outlet_2.p_in) annotation (Line(points={{-99,-16},
          {-90,-16},{-90,-32},{-82,-32}},      color={0,0,127}));
  annotation (experiment(StopTime=86400, __Dymola_Algorithm="Sdirk34hw"));
end Test_dynamic;
