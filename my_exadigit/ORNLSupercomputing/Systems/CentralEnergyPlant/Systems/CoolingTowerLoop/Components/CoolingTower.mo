within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Components;
model CoolingTower
  extends TemplatesCSM.BaseClasses.Fluids.PartialTwoPort_across(
    port_b_nominal(p=data.cooling_tower_p, T=data.volCTWS2_Tinit),
    port_a_nominal(
      p=data.cooling_tower_p,
      T=data.volCTWS2_Tinit,
      m_flow=100),
    final port_a,
    final port_b);
  parameter Integer nCells=4;
  TRANSFORM.Fluid.Valves.ValveLinear valve[nCells](
    redeclare package Medium = Medium,
    m_flow_start=31.25,
    dp_nominal=100,
    m_flow_nominal=100) annotation (Placement(transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={-60,0})));
  ORNLSupercomputing.Components.SubComponents.Fluid.CoolingTowers.coolingTower_Towb
    cell[nCells](CT_mflow_nom=55, CT_pinit=data.cooling_tower_p)
                                     annotation (Placement(
        transformation(extent={{-6,-10},{14,10}}, rotation=0)));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_inlet(
    redeclare package Medium = Medium,
    p_start=data.volCTWS2_pinit,
    T_start=data.volCTWS2_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=1),
    nPorts_a=1,
    nPorts_b=nCells) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-100,0})));
  TRANSFORM.Fluid.Volumes.MixingVolume plenum_outlet(
    redeclare package Medium = Medium,
    p_start=data.volCTWS2_pinit,
    T_start=data.volCTWS2_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=1),
    nPorts_b=1,
    nPorts_a=nCells) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={80,0})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
                                                      res_inlet(
      redeclare package Medium = Medium, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1)/
        port_a_nominal.m_flow)
    annotation (Placement(transformation(extent={{-140,-10},{-120,10}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance
                                                      res_outlet(
      redeclare package Medium = Medium, R=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_Pa(1)/
        port_a_nominal.m_flow)
    annotation (Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Routing.Replicator replicator(nout=nCells)
    annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=90,
        origin={30,70})));
  Modelica.Blocks.Interfaces.RealInput Towb
    "Connector of Real input signal" annotation (Placement(
        transformation(
        extent={{-20,-20},{20,20}},
        rotation=270,
        origin={60,120})));
  Modelica.Blocks.Interfaces.RealInput waterSPTLvg[nCells]
    "Enter Leaving water temperature setpoint" annotation (
      Placement(transformation(
        extent={{-20,-20},{20,20}},
        rotation=270,
        origin={0,120})));
  Modelica.Blocks.Interfaces.RealInput opening[nCells]
    "=1: completely open, =0: completely closed" annotation (
      Placement(transformation(
        extent={{-20,-20},{20,20}},
        rotation=270,
        origin={-60,120})));
  Data.Data data(cooling_tower_p=245000)
                 annotation (Placement(transformation(extent={{80,
            80},{100,100}})));
  TRANSFORM.Fluid.Volumes.SimpleVolume plenum_cell[nCells](
    redeclare package Medium = Medium,
    p_start=data.volCTWS2_pinit,
    T_start=data.volCTWS2_Tinit,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.01)) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-30,0})));
equation
  connect(cell.Towb, replicator.y) annotation (Line(points={{8,10.2},{8,40},{30,
          40},{30,59}},             color={0,0,127}));
  connect(replicator.u, Towb) annotation (Line(points={{30,82},{30,
          94},{60,94},{60,120}}, color={0,0,127}));
  connect(cell.waterSPTLvg, waterSPTLvg) annotation (Line(points={{0,10.2},{0,
          120}},                             color={0,0,127}));
  connect(valve.opening, opening) annotation (Line(points={{-60,8},{-60,120}},
                                        color={0,0,127}));
  connect(res_inlet.port_b, plenum_inlet.port_a[1]) annotation (
      Line(points={{-123,0},{-106,0}},
                                     color={0,127,255}));
  connect(res_inlet.port_a, port_a) annotation (Line(points={{-137,0},{-180,0}},
                        color={0,127,255}));
  connect(plenum_outlet.port_b[1], res_outlet.port_a)
    annotation (Line(points={{86,0},{103,0}},color={0,127,255}));
  connect(res_outlet.port_b, port_b) annotation (Line(points={{117,0},{180,0}},
                       color={0,127,255}));
  connect(plenum_inlet.port_b, valve.port_a) annotation (Line(
        points={{-94,0},{-70,0}}, color={0,127,255}));
  connect(valve.port_b, plenum_cell.port_a)
    annotation (Line(points={{-50,0},{-36,0}}, color={0,127,255}));
  connect(plenum_cell.port_b, cell.port_a)
    annotation (Line(points={{-24,0},{-6,0}}, color={0,127,255}));
  connect(cell.port_b, plenum_outlet.port_a)
    annotation (Line(points={{14,0},{74,0}}, color={0,127,255}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false),
        graphics={Rectangle(
          extent={{-100,100},{100,-100}},
          lineColor={28,108,200},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid), Bitmap(extent={{-100,-100},
              {100,100}}, fileName=
              "modelica://ORNLSupercomputing/Resources/Icons/coolingTower_cellType.svg")}),
      Diagram(coordinateSystem(preserveAspectRatio=false, extent={
            {-180,-100},{180,100}})));
end CoolingTower;
