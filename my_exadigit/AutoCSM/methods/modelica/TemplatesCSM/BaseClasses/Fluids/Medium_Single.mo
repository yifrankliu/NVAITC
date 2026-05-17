within TemplatesCSM.BaseClasses.Fluids;
record Medium_Single
  replaceable package Medium =
      TRANSFORM.Media.Fluids.Water.LinearWaterHot_pT constrainedby
    Modelica.Media.Interfaces.PartialMedium "Medium in the component"
    annotation (choicesAllMatching=true);
end Medium_Single;
