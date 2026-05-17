within ORNLSupercomputing.Components.SubComponents.DataCenter.Blade.BaseClasses;
model chip_3D
  parameter Integer nX = 1 "No. of nodes in X" annotation(Dialog(tab="Inputs"));
  parameter Integer nY = 1 "No. of nodes in Y" annotation(Dialog(tab="Inputs"));
  parameter Integer nZ = 1 "No. of nodes in Z" annotation(Dialog(tab="Inputs"));
  parameter Real length_x = 0.5 "Dimension in X in m" annotation(Dialog(tab="Inputs"));
  parameter Real length_y = 0.2 "Dimension in Y in m" annotation(Dialog(tab="Inputs"));
  parameter Real length_z = 0.1 "Dimension in Z in m" annotation(Dialog(tab="Inputs"));
  parameter Modelica.Units.SI.Temperature Tamb = 298.15 "Ambient air temperature in the blade" annotation(Dialog(tab="Inputs"));
  parameter Modelica.Units.SI.Temperature htc = 10.0 "Ambient HTC in W/m**2-K" annotation(Dialog(tab="Inputs"));

  TRANSFORM.HeatAndMassTransfer.DiscritizedModels.Conduction_3D conduction(
    redeclare package Material = ORNLSupercomputing.Components.SubComponents.Media.Silicon,
    redeclare model Geometry =
        TRANSFORM.HeatAndMassTransfer.ClosureRelations.Geometry.Models.Plane_3D
        (
        nX=nX,
        nY=nY,
        nZ=nZ,
        length_x=length_x,
        length_y=length_y,
        length_z=length_z),
    redeclare model InternalHeatModel =
        TRANSFORM.HeatAndMassTransfer.DiscritizedModels.BaseClasses.Dimensions_3.GenericHeatGeneration)
    annotation (Placement(transformation(extent={{-16,4},{4,24}})));

  TRANSFORM.HeatAndMassTransfer.Resistances.Heat.Convection convectionX1[nY,nZ](
      each alpha=htc, surfaceArea=conduction.geometry.crossAreas_1[1, :, :])
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={-46,14})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Temperature T_infX1[nY,nZ](
      each T=Tamb)
    annotation (Placement(transformation(extent={{-88,4},{-68,24}})));
  TRANSFORM.HeatAndMassTransfer.Resistances.Heat.Convection convectionY2[nX,nZ](
      each alpha=htc, surfaceArea=conduction.geometry.crossAreas_2[end, :, :])
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={-6,40})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Temperature T_infY2[nX,nZ](
      each T=Tamb) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=270,
        origin={-6,68})));
  TRANSFORM.HeatAndMassTransfer.Resistances.Heat.Convection convectionX2[nY,nZ](
      each alpha=htc, surfaceArea=conduction.geometry.crossAreas_1[end, :, :])
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={28,10})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Temperature T_infX2[nY,nZ](
      each T=Tamb) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={58,10})));
  TRANSFORM.HeatAndMassTransfer.Resistances.Heat.Convection convectionY1[nY,nZ](
      each alpha=htc, surfaceArea=conduction.geometry.crossAreas_2[1, :, :])
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=-90,
        origin={-6,-10})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Temperature T_infY1[nX,nZ](
      each T=Tamb) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={-6,-42})));

  TRANSFORM.HeatAndMassTransfer.Interfaces.HeatPort_Flow port_b[nX,nY]
    annotation (Placement(transformation(extent={{90,-10},{110,10}})));
  TRANSFORM.HeatAndMassTransfer.Interfaces.HeatPort_Flow port_a[nX,nY]
    "Input Heating Input Power in W"
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
equation
  connect(T_infY2.port, convectionY2.port_b) annotation (Line(points={{-6,58},{-6,
          52.5},{-6,52.5},{-6,47}}, color={191,0,0}));
  connect(T_infX2.port, convectionX2.port_b)
    annotation (Line(points={{48,10},{35,10}}, color={191,0,0}));
  connect(convectionX1.port_a, conduction.port_a1)
    annotation (Line(points={{-39,14},{-16,14}}, color={191,0,0}));
  connect(convectionX2.port_a, conduction.port_b1) annotation (Line(points={{21,
          10},{12,10},{12,14},{4,14}}, color={191,0,0}));
  connect(convectionY2.port_a, conduction.port_b2)
    annotation (Line(points={{-6,33},{-6,24}}, color={191,0,0}));
  connect(T_infX1.port, convectionX1.port_b) annotation (Line(points={{-68,14},{
          -60.5,14},{-60.5,14},{-53,14}}, color={191,0,0}));
  connect(convectionY1.port_b, T_infY1.port)
    annotation (Line(points={{-6,-17},{-6,-32}}, color={191,0,0}));
  connect(conduction.port_a2, convectionY1.port_a) annotation (Line(points={{-6,
          4},{-6,0.5},{-6,0.5},{-6,-3}}, color={191,0,0}));
  connect(port_a, conduction.port_a3) annotation (Line(points={{-100,0},{-16,0},
          {-16,6},{-14,6}}, color={191,0,0}));
  connect(conduction.port_b3, port_b)
    annotation (Line(points={{2,22},{86,22},{86,0},{100,0}}, color={191,0,0}));
  annotation (
      experiment(StopTime=10500, __Dymola_Algorithm="Dassl"));
end chip_3D;
