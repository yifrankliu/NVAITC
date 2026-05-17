within ORNLSupercomputing.Components.SubComponents.Controls.Testing.EHX_Loop.BaseClasses;
model HTWP_speed
  "The PID controller model for setting the HTWP Speed"
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi;
  Real HTWP_Nmin_set;
  parameter Boolean switch_HTWP_Nset = true "Switch between modified (true) vs. direct PID output" annotation(Dialog(group="General Inputs"));
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
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
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
    annotation (Placement(transformation(extent={{-48,-6},{-34,8}})));
  Modelica.Blocks.Math.Add dP(k1=-1, k2=+1)
    annotation (Placement(transformation(extent={{8,-8},{-8,8}},
        rotation=180,
        origin={-36,30})));
  Modelica.Blocks.Interfaces.RealInput p_HTWR "HTWR header pressure"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,12}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));

  Modelica.Blocks.Interfaces.RealOutput HTWP_Nrel "HTWP Nrel" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,0}),  iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Logical.Timer OnTimer
    annotation (Placement(transformation(extent={{52,-38},{62,-28}})));
  Modelica.Blocks.Math.RealToBoolean Crit1(threshold=0.001)
    annotation (Placement(transformation(extent={{8,-34},{18,-24}})));
  Modelica.Blocks.Math.Feedback feeBac
    annotation (Placement(transformation(extent={{-38,-26},{-18,-46}})));
  Modelica.Blocks.Math.RealToBoolean Crit2(threshold=db)
    "Hysteresis element to switch controller on and off"
    annotation (Placement(transformation(extent={{8,-52},{18,-42}})));
  Modelica.Blocks.Logical.GreaterEqualThreshold greaterEqualThreshold(threshold=
       3500)
    annotation (Placement(transformation(extent={{68,-38},{78,-28}})));
  Modelica.Blocks.Logical.And and1
    annotation (Placement(transformation(extent={{36,-38},{46,-28}})));
  Modelica.Blocks.Logical.Not and2
    annotation (Placement(transformation(extent={{22,-52},{32,-42}})));
  Modelica.Blocks.Sources.RealExpression p_HTWS_psi(y=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(p_HTWS))
    "p HTWS in psi"
    annotation (Placement(transformation(extent={{-70,28},{-54,44}})));
  Modelica.Blocks.Sources.RealExpression p_HTWR_psi(y=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(p_HTWR))
    "p HTWR in psi"
    annotation (Placement(transformation(extent={{-70,12},{-54,28}})));
initial equation
  HTWP_Nmin_set=HTWP_Nrel_min;
equation
  when greaterEqualThreshold.y then
     HTWP_Nmin_set = PID_HTWP.y;
  end when;
  if switch_HTWP_Nset then
      HTWP_Nrel = max(PID_HTWP.y, HTWP_Nmin_set);
  else
      HTWP_Nrel = max(PID_HTWP.y, HTWP_Nrel_min);
  end if;
  connect(dPSetPoint.y, PID_HTWP.u_s)
    annotation (Line(points={{-33.3,1},{-28,1},{-28,0},{-12,0}},
                                                     color={0,0,127}));
  connect(dPSetPoint.y, feeBac.u2)
    annotation (Line(points={{-33.3,1},{-28,1},{-28,-28}}, color={0,0,127}));
  connect(OnTimer.y, greaterEqualThreshold.u) annotation (Line(points={{62.5,-33},
          {67,-33}},            color={0,0,127}));
  connect(Crit2.y, and2.u)
    annotation (Line(points={{18.5,-47},{21,-47}}, color={255,0,255}));
  connect(and2.y, and1.u2)
    annotation (Line(points={{32.5,-47},{32.5,-48},{35,-48},{35,-37}},
                                                       color={255,0,255}));
  connect(Crit1.y, and1.u1) annotation (Line(points={{18.5,-29},{26,-29},{26,-33},
          {35,-33}}, color={255,0,255}));
  connect(and1.y, OnTimer.u) annotation (Line(points={{46.5,-33},{51,-33}},
                 color={255,0,255}));
  connect(feeBac.y, Crit1.u) annotation (Line(points={{-19,-36},{2,-36},{2,-29},
          {7,-29}}, color={0,0,127}));
  connect(feeBac.y, Crit2.u) annotation (Line(points={{-19,-36},{2,-36},{2,-47},
          {7,-47}}, color={0,0,127}));
  connect(p_HTWS_psi.y, dP.u2) annotation (Line(points={{-53.2,36},{-53.2,34.8},
          {-45.6,34.8}}, color={0,0,127}));
  connect(p_HTWR_psi.y, dP.u1) annotation (Line(points={{-53.2,20},{-45.6,20},{
          -45.6,25.2}}, color={0,0,127}));
  connect(PID_HTWP.u_m, dP.y)
    annotation (Line(points={{0,12},{0,30},{-27.2,30}}, color={0,0,127}));
  connect(feeBac.u1, dP.y) annotation (Line(points={{-36,-36},{-52,-36},{-52,16},
          {0,16},{0,30},{-27.2,30}}, color={0,0,127}));
  annotation (Diagram(graphics={
        Text(
          extent={{26,-12},{60,-26}},
          textColor={0,0,0},
          textString="Maintain HTWP N")}));
end HTWP_speed;
