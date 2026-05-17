within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CDU_Loop.BaseClasses;
model CDU_CV
  extends Modelica.Blocks.Icons.Block;
  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // The primary flow control valve is controlled by the sec. temp. setpoint of
  // 28.0 deg C. The PID parameters as the same as that used in the actual system.
  parameter Real Tsec_return_nom = 28.0;
  parameter Real CDU_CV_min = 0.1;
  parameter Real CDU_CV_max = 1.0;
  parameter Real CDU_CV_start = 0.5;
  // Control Systems tuning parameters
  parameter Real Ti = 35; // s
  parameter Real Td = 9; // s
  parameter Real gain = 0.9;
  parameter Real db = 0.3; // deg. C
  parameter Real dbr = 0.5;
  parameter Real yb = 0.0;
  parameter Real k_s = 1.0;
  parameter Real k_m = 1.0;

  LimPID_Deadband_dbr PID_CDUCV(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    k=gain,
    Ti=Ti,
    Td=Td,
    yb=yb,
    k_s=k_s,
    k_m=k_m,
    yMax=CDU_CV_max,
    yMin=CDU_CV_min,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=CDU_CV_start,
    deadband=db,
    deadbandRatio=dbr)
    annotation (Placement(transformation(extent={{-10,10},{10,-10}})));
  Modelica.Blocks.Sources.Constant Tsec_setpoint(k=Tsec_return_nom)
    annotation (Placement(transformation(extent={{-56,-8},{-40,8}})));
  Modelica.Blocks.Interfaces.RealInput T_sec "Sec. return Temp" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-48.2,36}), iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));

  Modelica.Blocks.Interfaces.RealOutput CDU_CV "CDU CV" annotation (Placement(
        transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={41.8,0}), iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
equation
  connect(Tsec_setpoint.y, PID_CDUCV.u_s)
    annotation (Line(points={{-39.2,0},{-12,0}},color={0,0,127}));
  connect(PID_CDUCV.y, CDU_CV)
    annotation (Line(points={{11,0},{41.8,0}}, color={0,0,127}));
  connect(T_sec, PID_CDUCV.u_m)
    annotation (Line(points={{-48.2,36},{0,36},{0,12}}, color={0,0,127}));
end CDU_CV;
