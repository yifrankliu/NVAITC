within ORNLSupercomputing.Components.SubComponents.Controls.Testing.misc_Tests;
model test2
  extends Modelica.Icons.Example;
  Integer flag(start=0);
  Real temperature(start=20);
  Modelica.Blocks.Interfaces.RealInput p "CTWR header pressure (gauge)"
                                                                annotation (
      Placement(transformation(
        extent={{-19.8,-20},{19.8,20}},
        rotation=180,
        origin={-100.2,0}),  iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
equation
  der(temperature) = if flag >= 1 then 5 else -1;

  if p < 22.9 then
    flag =+ 1;
  else
    flag = 0;
  end if;

//   when heaterOn then
//     heaterPower = 100;
//   elsewhen not heaterOn then
//     heaterPower = 0;
//   end when;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end test2;
