within ORNLSupercomputing.Components.SubComponents.Fluid.ColdPlate.Examples;
model Test
  extends Modelica.Icons.Example;
  package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium;

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    experiment(StopTime=100, __Dymola_Algorithm="Dassl"));
end Test;
