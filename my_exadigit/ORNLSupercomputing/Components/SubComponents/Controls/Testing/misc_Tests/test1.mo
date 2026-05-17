within ORNLSupercomputing.Components.SubComponents.Controls.Testing.misc_Tests;
model test1
  extends Modelica.Icons.Example;
  Real temperature(start=20);
  Real heaterPower(start=0);
  Boolean heaterOn(start=false);

equation
  der(temperature) = if heaterOn then 5 else -1;

  when temperature > 25 then
    heaterOn = false;
  elsewhen temperature < 15 then
    heaterOn = true;
  end when;

  when heaterOn then
    heaterPower = 100;
  elsewhen not heaterOn then
    heaterPower = 0;
  end when;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end test1;
