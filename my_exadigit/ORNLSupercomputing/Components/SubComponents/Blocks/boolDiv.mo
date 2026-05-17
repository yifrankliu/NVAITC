within ORNLSupercomputing.Components.SubComponents.Blocks;
block boolDiv
  extends Modelica.Blocks.Interfaces.SI2SO;
equation
    y = min(integer(u1/u2), 1.0);
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end boolDiv;
