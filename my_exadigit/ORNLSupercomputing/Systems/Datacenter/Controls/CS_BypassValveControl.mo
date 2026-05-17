within ORNLSupercomputing.Systems.Datacenter.Controls;
model CS_BypassValveControl
  extends
    ORNLSupercomputing.Systems.Datacenter.BaseClasses.PartialControls(
     redeclare Data.Data data);

  parameter Real bypass_CV_min=0.2;
  parameter Real bypass_CV_max=1.0;
  parameter Real bypass_CV_start=0.25;
  // Control System tuning parameters
  parameter Real gain=0.1;
  parameter Real Ti=100.0;
  // s
  parameter Real Td=10.0;
  // s
  parameter Real db=2.0;
  //kg/s
  parameter Real dbr=0.5;

  Modelica.Blocks.Sources.RealExpression maxValue(y=max(PID_bypassCV.u_m,
        3000*0.063)) annotation (Placement(transformation(extent={{-50,0},{-30,
            20}})));
  ORNLSupercomputing.Components.SubComponents.Controls.LimPID_Deadband_dbr
    PID_bypassCV(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    k=gain,
    Ti=Ti,
    Td=Td,
    yb=0.0,
    k_s=1.0,
    k_m=1.0,
    yMax=bypass_CV_max,
    yMin=bypass_CV_min,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=bypass_CV_start,
    deadband=db,
    deadbandRatio=dbr)
    annotation (Placement(transformation(extent={{-10,0},{10,20}})));
  Modelica.Blocks.Continuous.Filter filter(filterType=Modelica.Blocks.Types.FilterType.LowPass,
      f_cut=1e-3) annotation (Placement(transformation(extent={{20,20},{40,0}})));
equation
  connect(maxValue.y, PID_bypassCV.u_s)
    annotation (Line(points={{-29,10},{-12,10}}, color={0,0,127}));
  connect(filter.u, PID_bypassCV.y) annotation (Line(points={{18,10},{11,10}},
                                     color={0,0,127}));
  connect(controlBus.m_flow_supply, PID_bypassCV.u_m) annotation (
      Line(
      points={{0,-100},{0,-2}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(controlBus.opening_bypass, filter.y) annotation (Line(
      points={{0,-100},{60,-100},{60,10},{41,10}},
      color={255,204,51},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end CS_BypassValveControl;
