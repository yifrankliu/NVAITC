within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CDU_Loop.BaseClasses;
model bypass_CV
  extends Modelica.Blocks.Icons.Block;
  // The bypass valve should maintain atleast 3000 GPM thorughout the loop.
  parameter Real bypass_CV_min = 0.22;
  parameter Real bypass_CV_max = 1.0;
  parameter Real bypass_CV_start = 0.22;
  // Control Systems tuning parameters
  parameter Real Ti = 35; // s
  parameter Real Td = 9; // s
  parameter Real gain = 0.9;
  parameter Real db = 1.0; // kg/s
  parameter Real dbr = 0.5;
  parameter Real yb = 0.0;
  parameter Real k_s = 1.0;
  parameter Real k_m = 1.0;

  LimPID_Deadband_dbr PID_CDUCV(
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    k=gain,
    Ti=Ti,
    Td=Td,
    yb=yb,
    k_s=k_s,
    k_m=k_m,
    yMax=bypass_CV_max,
    yMin=bypass_CV_min,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=bypass_CV_start,
    deadband=db,
    deadbandRatio=dbr)
    annotation (Placement(transformation(extent={{-10,10},{10,-10}})));
  Modelica.Blocks.Interfaces.RealInput mdot "Mass flow rate" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-48.2,36}), iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));

  Modelica.Blocks.Interfaces.RealOutput bypass_CV "bypass CV" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={79.8,0}), iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
public
  Modelica.Blocks.Sources.RealExpression maxValue(y=max(mdot, 3000*0.063))
    annotation (Placement(transformation(extent={{-60,-13},{-34,13}})));
  Modelica.Blocks.Continuous.Filter filter(filterType=Modelica.Blocks.Types.FilterType.LowPass,
      f_cut=1e-3)
    annotation (Placement(transformation(extent={{28,8.5},{46,-8.5}})));
equation
  connect(mdot, PID_CDUCV.u_m)
    annotation (Line(points={{-48.2,36},{0,36},{0,12}}, color={0,0,127}));
  connect(maxValue.y, PID_CDUCV.u_s)
    annotation (Line(points={{-32.7,0},{-12,0}}, color={0,0,127}));
  connect(PID_CDUCV.y, filter.u)
    annotation (Line(points={{11,0},{26.2,0}}, color={0,0,127}));
  connect(filter.y, bypass_CV)
    annotation (Line(points={{46.9,0},{79.8,0}}, color={0,0,127}));
end bypass_CV;
