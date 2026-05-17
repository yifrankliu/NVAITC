within TemplatesCSM.BaseClasses.Fluids;
record Mediums_Two
  replaceable package Medium_1 =
      TRANSFORM.Media.Fluids.Water.LinearWaterHot_pT constrainedby
    Modelica.Media.Interfaces.PartialMedium
    "Medium in the component for side 1" annotation (choicesAllMatching=true);
  replaceable package Medium_2 = Medium_1 constrainedby
    Modelica.Media.Interfaces.PartialMedium
    "Medium in the component for side 2" annotation (choicesAllMatching=true);
end Mediums_Two;
