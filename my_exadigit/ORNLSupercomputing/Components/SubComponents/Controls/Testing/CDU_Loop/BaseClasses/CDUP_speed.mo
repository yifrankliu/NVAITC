within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CDU_Loop.BaseClasses;
model CDUP_speed
extends Modelica.Blocks.Icons.Block;
  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // Two CDUPs are always set to be operational
  // The CDUPs are staged up when the operational pump speeds touch Nrel_max
  // and staged down when the operational pump speeds touch Nrel_min.
  // The PID controller for the pump speeds is controlled by the dP setpoint.
  // The setpoint is fixed at 27.5 psi.
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  parameter Real dp_nom = 27.5;
  parameter Real CDUP_Nrel_min = 52.0;
  parameter Real CDUP_Nrel_max = 75.0;
  parameter Real CDUP_Nrel_start = 63.9;
  // Control Systems tuning parameters
  parameter Real Ti = 100; // s
  parameter Real Td = 30; // s
  parameter Real gain = 0.1;
  Modelica.Blocks.Interfaces.RealInput p_CabS "Cab. Supply pressure"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,60}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Continuous.LimPID PID_CDUP(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    k=gain,
    Ti=Ti,
    Td=Td,
    yMax=CDUP_Nrel_max,
    yMin=CDUP_Nrel_min,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=CDUP_Nrel_start)
    annotation (Placement(transformation(extent={{-10,10},{10,-10}})));
  Modelica.Blocks.Sources.Constant       dPSetPoint(k=dp_nom)
    annotation (Placement(transformation(extent={{-60,-8},{-44,8}})));
  Modelica.Blocks.Math.Add dP(k1=-1, k2=+1)
    annotation (Placement(transformation(extent={{8,-8},{-8,8}},
        rotation=180,
        origin={-36,38})));
  Modelica.Blocks.Interfaces.RealInput p_CabR "Cab. return pressure"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,20}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));

  Modelica.Blocks.Interfaces.RealOutput CDUP_Nrel "CDUP Nrel" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,0}),  iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Continuous.Filter filter(filterType=Modelica.Blocks.Types.FilterType.LowPass,
      f_cut=1)
    annotation (Placement(transformation(extent={{-20,45},{-6,31}})));
  Modelica.Blocks.Sources.RealExpression p_CabS_psi(y=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(p_CabS))
    "p CabS in psi"
    annotation (Placement(transformation(extent={{-70,36},{-54,52}})));
  Modelica.Blocks.Sources.RealExpression p_CabR_psi(y=
        TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi(p_CabR))
    "p CabR in psi"
    annotation (Placement(transformation(extent={{-70,18},{-54,34}})));
equation
  connect(dPSetPoint.y,PID_CDUP. u_s)
    annotation (Line(points={{-43.2,0},{-12,0}},   color={0,0,127}));
  connect(PID_CDUP.y,CDUP_Nrel)
    annotation (Line(points={{11,0},{96,0},{96,1.77636e-15},{113.8,1.77636e-15}},
                                                   color={0,0,127}));
  connect(PID_CDUP.u_m, filter.y)
    annotation (Line(points={{0,12},{0,38},{-5.3,38}}, color={0,0,127}));
  connect(filter.u, dP.y)
    annotation (Line(points={{-21.4,38},{-27.2,38}}, color={0,0,127}));
  connect(p_CabS_psi.y, dP.u2) annotation (Line(points={{-53.2,44},{-53.2,42.8},
          {-45.6,42.8}}, color={0,0,127}));
  connect(p_CabR_psi.y, dP.u1) annotation (Line(points={{-53.2,26},{-52,26},{-52,
          33.2},{-45.6,33.2}}, color={0,0,127}));
end CDUP_speed;
