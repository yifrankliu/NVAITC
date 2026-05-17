within ORNLSupercomputing.Components.SubComponents.Controls.Testing.EHX_Loop.BaseClasses;
model HTWP_speed_simple
  "The simplified PID controller model for setting the HTWP Speed"
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi;
  parameter Real dp_nom = 23.8 "Nominal dp setpoint in psi" annotation(Dialog(group="General Inputs"));
//   parameter Modelica.Units.SI.Frequency f_cut = 1.0 "Low pass filter cut-off freq." annotation(Dialog(group="General Inputs"));
  parameter Real HTWP_Nrel_min = 53.0 "HTWP min. Nrel %" annotation(Dialog(group="General Inputs"));
  parameter Real HTWP_Nrel_max = 75.0 "HTWP max. Nrel %" annotation(Dialog(group="General Inputs"));
  parameter Real HTWP_Nrel_start = 53.0 "HTWP start Nrel %" annotation(Dialog(group="General Inputs"));
  parameter Real k_s = 1.0 "PID setpoint input scaling" annotation(Dialog(group="PID Inputs"));
  parameter Real k_m = 1.0 "PID measurement input scaling" annotation(Dialog(group="PID Inputs"));
  parameter Real Ti = 35 "PID integral time" annotation(Dialog(group="PID Inputs"));
  parameter Real gain = 0.7 "PID gain" annotation(Dialog(group="PID Inputs"));
  parameter Real yb = HTWP_Nrel_min "PID output bias" annotation(Dialog(group="PID Inputs"));
  parameter Real db = 2.0 "PID deadband in psi" annotation(Dialog(group="PID Inputs"));
  parameter Real dbr = 0.5 "PID deadband ratio" annotation(Dialog(group="PID Inputs"));
extends Modelica.Blocks.Icons.Block;
  Modelica.Blocks.Interfaces.RealInput p_HTWS "HTWS pressure" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,46}),iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,40})));
  LimPID_Deadband_dbr PID_HTWP(
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    k=gain,
    Ti=Ti,
    Td=4*Ti,
    yb=yb,
    k_s=k_s,
    k_m=k_s,
    yMax=HTWP_Nrel_max,
    yMin=HTWP_Nrel_min,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=HTWP_Nrel_start,
    deadbandRatio=dbr)
    annotation (Placement(transformation(extent={{-10,10},{10,-10}})));
  Modelica.Blocks.Sources.Constant       dPSetPoint(k=dp_nom)
    annotation (Placement(transformation(extent={{-50,-8},{-34,8}})));
  Modelica.Blocks.Math.Add dP(k1=-1, k2=+1)
    annotation (Placement(transformation(extent={{8,-8},{-8,8}},
        rotation=180,
        origin={-36,30})));
  Modelica.Blocks.Interfaces.RealInput p_HTWR "HTWR header pressure"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,12}),iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,-40})));

  Modelica.Blocks.Interfaces.RealOutput HTWP_Nrel "HTWP Nrel" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,0}),  iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,0})));
  Modelica.Blocks.Sources.RealExpression p_HTWS_psi(y=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(p_HTWS))
    "p HTWS in psi"
    annotation (Placement(transformation(extent={{-70,28},{-54,44}})));
  Modelica.Blocks.Sources.RealExpression p_HTWR_psi(y=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(p_HTWR))
    "p HTWR in psi"
    annotation (Placement(transformation(extent={{-70,12},{-54,28}})));
  Modelica.Blocks.Continuous.Filter     filter(f_cut=0.001)
                                                         annotation (Placement(
        transformation(
        extent={{-9,-9},{9,9}},
        rotation=0,
        origin={47,0})));
equation
  connect(dPSetPoint.y, PID_HTWP.u_s)
    annotation (Line(points={{-33.2,0},{-12,0}},     color={0,0,127}));
  connect(p_HTWS_psi.y, dP.u2) annotation (Line(points={{-53.2,36},{-53.2,34.8},
          {-45.6,34.8}}, color={0,0,127}));
  connect(p_HTWR_psi.y, dP.u1) annotation (Line(points={{-53.2,20},{-45.6,20},{
          -45.6,25.2}}, color={0,0,127}));
  connect(PID_HTWP.u_m, dP.y)
    annotation (Line(points={{0,12},{0,30},{-27.2,30}}, color={0,0,127}));
  connect(PID_HTWP.y, filter.u)
    annotation (Line(points={{11,0},{36.2,0}}, color={0,0,127}));
  connect(filter.y, HTWP_Nrel)
    annotation (Line(points={{56.9,0},{113.8,0}}, color={0,0,127}));
end HTWP_speed_simple;
