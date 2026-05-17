within ORNLSupercomputing.Components.SubComponents.DataCenter.Blade;
model Blade_coldplates
  extends BaseClasses.PartialBlademodel(
  redeclare package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium);

  BaseClasses.GPU_3D gPU_3D annotation (Placement(transformation(
        extent={{-7,-7},{7,7}},
        rotation=270,
        origin={-42,55})));
  Fluid.ColdPlate.coldPlate coldPlate(use_HeatTransferOuter=true)
    annotation (Placement(transformation(extent={{-52,16},{-32,36}})));
  BaseClasses.GPU_3D gPU_3D4 annotation (Placement(transformation(
        extent={{-7,-7},{7,7}},
        rotation=270,
        origin={42,55})));
  Fluid.ColdPlate.coldPlate coldPlate1
    annotation (Placement(transformation(extent={{32,16},{52,36}})));
  BaseClasses.CPU_3D cPU_3D annotation (Placement(transformation(
        extent={{-7,-7},{7,7}},
        rotation=270,
        origin={-42,-17})));
  Fluid.ColdPlate.coldPlate coldPlate2
    annotation (Placement(transformation(extent={{-52,-50},{-32,-30}})));
  Fluid.ColdPlate.coldPlate coldPlate3
    annotation (Placement(transformation(extent={{32,-50},{52,-30}})));
  BaseClasses.CPU_3D cPU_3D1 annotation (Placement(transformation(
        extent={{-7,-7},{7,7}},
        rotation=270,
        origin={42,-17})));
equation
  connect(port_a, coldPlate.port_a) annotation (Line(points={{-100,0},{-80,0},{
          -80,26},{-52,26}},
                         color={0,127,255}));
  connect(port_a, coldPlate1.port_a) annotation (Line(points={{-100,0},{0,0},{0,
          26},{32,26}}, color={0,127,255}));
  connect(cPU_3D1.port_b, coldPlate3.heatPorts[1])
    annotation (Line(points={{42,-24},{42,-35}}, color={191,0,0}));
  connect(coldPlate.port_b, coldPlate2.port_a) annotation (Line(points={{-32,26},
          {0,26},{0,0},{-80,0},{-80,-40},{-52,-40}},         color={0,127,255}));
  connect(cPU_3D.port_b, coldPlate2.heatPorts[1])
    annotation (Line(points={{-42,-24},{-42,-35}}, color={191,0,0}));
  connect(coldPlate1.port_b, coldPlate3.port_a) annotation (Line(points={{52,26},
          {78,26},{78,0},{0,0},{0,-40},{32,-40}},       color={0,127,255}));
  connect(coldPlate2.port_b, port_b) annotation (Line(points={{-32,-40},{0,-40},
          {0,0},{100,0}}, color={0,127,255}));
  connect(coldPlate3.port_b, port_b) annotation (Line(points={{52,-40},{78,-40},
          {78,0},{100,0}}, color={0,127,255}));
  connect(coldPlate1.heatPorts[1], gPU_3D4.port_b[1, 1])
    annotation (Line(points={{42,31},{42,48}}, color={191,0,0}));
  connect(coldPlate.heatPorts[1], gPU_3D.port_b[1, 1])
    annotation (Line(points={{-42,31},{-42,48}}, color={191,0,0}));
  annotation (Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{
            100,100}})),
    experiment(StopTime=22000, __Dymola_Algorithm="Esdirk45a"));
end Blade_coldplates;
