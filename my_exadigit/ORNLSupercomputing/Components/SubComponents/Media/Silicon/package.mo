within ORNLSupercomputing.Components.SubComponents.Media;
package Silicon
    extends TRANSFORM.Media.Interfaces.Solids.PartialSimpleAlloy(
    mediumName="Silicon",
    T_min=Modelica.Units.Conversions.from_degC(0),
    T_max=Modelica.Units.Conversions.from_degC(1500));

  redeclare function extends specificEnthalpy
    "Specific enthalpy"
  algorithm
    h := h_reference + 577.7784*(state.T - T_reference); //Doesn't matter
  end specificEnthalpy;

  redeclare function extends density
    "Density"
  algorithm
    d := 2329.0; //kg/m^3
  end density;

  redeclare function extends thermalConductivity
    "Thermal conductivity"
  algorithm
    lambda := 148.0; //W/m*K
  end thermalConductivity;

  redeclare function extends specificHeatCapacityCp
    "Specific heat capacity"
  algorithm
    cp := 710.0; //(J/kg*k)
  end specificHeatCapacityCp;
annotation (Documentation(info="<html>
<p>Properties for bulk silicon and silicon wafers. info="<html));              //www.el-cat.com/silicon-properties.htm</p>
end Silicon;
