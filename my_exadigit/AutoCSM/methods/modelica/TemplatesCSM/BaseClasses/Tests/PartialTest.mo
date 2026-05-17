within TemplatesCSM.BaseClasses.Tests;
partial model PartialTest
  extends Modelica.Icons.Example;

  parameter Integer n=1
    "# of parallel instances of the model to be simulated";

  replaceable Systems.PartialModel simulator[n] constrainedby
    Systems.PartialModel annotation (Placement(transformation(extent={{-10,
            -10},{10,10}})), choicesAllMatching=true);

equation

  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-140,-100},
            {140,100}})),
    experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
end PartialTest;
