within ORNLSupercomputing.Components.SubComponents;
package Media "This will hold all the medium models used in the other packages"
   extends TRANSFORM.Icons.MediaPackage;
  replaceable package Medium = TRANSFORM.Media.Fluids.Water.LinearWaterHot_pT
    constrainedby Modelica.Media.Interfaces.PartialMedium
    "Coolant medium for all components -
  Use package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater for base properties 
  Use package Medium = TRANSFORM.Media.Fluids.Water.LinearWaterHot_pT for temp. dep. properties"
                            annotation (choicesAllMatching=true);
end Media;
