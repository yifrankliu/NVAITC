within ORNLSupercomputing.Systems.Datacenter.Data;
record Data_pipes
  extends BaseClasses.PartialData;
  // Source 1 (s1):
  // REVIT files: 6434-OLCF_5-IMC-CSB_SECT_3-HVAC_&_PIPE18.rvt
  //              6434-OLCF_5-IMC-ETF_SECT_6-HVAC_&_PIPE18.rvt
  //              A18_1200900_CBRE_SECT 3_Oakridge East Campus.rvt
  //              A18_1200900_CBRE_SECT 6_Oakridge East Campus.rvt
  // Drawing : 5.10-VPC
  // Notes:
  // a. All distances are approximations. Elbows have been accounted through loss coefficients.
  // b. Some od the piping sections are ignored and yet to be incorporated.
  import from_inch =
    TRANSFORM.Units.Conversions.Functions.Distance_m.from_in;
  import from_feet =
    TRANSFORM.Units.Conversions.Functions.Distance_m.from_ft;
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degF;
  import from_feet3 =
    TRANSFORM.Units.Conversions.Functions.Volume_m3.from_ft3;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_bar;
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  //
  parameter Modelica.Units.SI.Length inner_dia_sch40_12=from_inch(10.98)
    "12 inch Nominal Dia. aquatherm Schedule 40 pipe (s1)";
  // Supply Pipe Lengths
  parameter Modelica.Units.SI.Length length_HTWS1=from_feet(119.7)
    "length HTWS1 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS2=from_feet(122.7)
    "length HTWS2 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS3=from_feet(122.7)
    "length HTWS3 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS4=from_feet(122.7)
    "length HTWS4 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS5=from_feet(122.7)
    "length HTWS5 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS6=from_feet(122.7)
    "length HTWS6 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS7=from_feet(122.7)
    "length HTWS7 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS8=from_feet(122.7)
    "length HTWS8 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS9=from_feet(122.7)
    "length HTWS9 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS10=from_feet(122.7)
    "length HTWS10 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS11=from_feet(122.7)
    "length HTWS11 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS12=from_feet(122.7)
    "length HTWS12 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS13=from_feet(122.7)
    "length HTWS13 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS14=from_feet(122.7)
    "length HTWS14 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS15=from_feet(122.7)
    "length HTWS15 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS16=from_feet(122.7)
    "length HTWS16 (s1)";
  parameter Modelica.Units.SI.Length length_HTWS17=from_feet(122.7)
    "length HTWS17 (s1)";
  annotation (
    defaultComponentName="data",
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Documentation(info="<html>
</html>"));
end Data_pipes;
