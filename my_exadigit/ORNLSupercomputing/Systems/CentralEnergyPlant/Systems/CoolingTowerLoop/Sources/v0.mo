within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Sources;
model v0
  extends BaseClasses.PartialSources(redeclare Data.NULL data);
  input SI.Temperature Towb=298.15 "Wet bulb temperature"
    annotation (Dialog(group="Inputs"));
//   parameter SI.Temperature Towb=298.15 "Wet bulb temperature"
//     annotation (Dialog(group="Inputs"), Evaluate=false);
//     Modelica.Blocks.Interfaces.RealInput Towb(start=298.15) "Wet bulb temperature"
//     annotation (Dialog(group="Inputs"), Evaluate=false);
  Modelica.Blocks.Sources.RealExpression Towb_int(y=Towb)
    annotation (Placement(transformation(extent={{-40,-70},{-20,-50}})));

equation
  connect(controlBus.Towb, Towb_int.y) annotation (Line(
      points={{0,-100},{0,-60},{-19,-60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
end v0;
