within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses;
model CTWP_speed "The PID controller model for setting the CTWP Speed"
  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // CTWP1 is always set to be operational.
  // CTWP2 - CTWP4 are staged up when the operational pump speeds touch Nrel_max
  // and staged down when the operational pump speeds touch Nrel_min
  // The PID controller for the pump speeds is controlled by the CTWR static
  // pressure (gauge) setpoint.
  // The setpoint is fed the measured value and restricted to [22.3, 24.2] psi.
  // It is also informed by the HTWS temperature setpoint on page 16 of s1.
  // The CT temperature setpoint is a summation of the Towb and a manual
  // approach temperature of 17 degF.
  // Four CTs (4a-d) are always set to be open as the model is not
  // started from cold start.
  // The other CTs are staged up if HTWS is increasing and ps CTWR is at max
  // pressure and is set to stage down when HTWS is decreasing and ps CTWR is
  // at its min pressure.
  extends Modelica.Blocks.Icons.Block;
  parameter Modelica.Units.SI.Frequency f_cut = 100.0 "Low pass filter cut-off freq." annotation(Dialog(group="General Inputs"));
  parameter Real CTWP_Nrel_min = 45.0 "min. CTWP Nrel %" annotation(Dialog(group="General Inputs"));
  parameter Real CTWP_Nrel_max = 70.0 "max. CTWP Nrel %" annotation(Dialog(group="General Inputs"));
  parameter Real CTWP_Nrel_start = 50.0 "starting CTWP Nrel %" annotation(Dialog(group="General Inputs"));
  parameter Real Ti = 30.0 "PID integral time" annotation(Dialog(group="PID Inputs"));
  parameter Real gain = 14.8 "PID gain" annotation(Dialog(group="PID Inputs"));
  parameter Real wp = 1.0 "PID setpoint weighting" annotation(Dialog(group="PID Inputs"));

//   Real delayed_p_setpoint;
  Modelica.Blocks.Continuous.LimPID
                        PID_CTWP(
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    k=gain,
    Ti=Ti,
    yMax=CTWP_Nrel_max,
    yMin=CTWP_Nrel_min,
    wp=wp,
    withFeedForward=false,
    initType=Modelica.Blocks.Types.Init.InitialOutput,
    y_start=CTWP_Nrel_start)
    annotation (Placement(transformation(extent={{4,-2},{22,-20}})));
  Modelica.Blocks.Interfaces.RealInput p_CTWR "CTWR header pressure"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=180,
        origin={-100.2,60}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));

  BaseClasses.p_CTWR_setpoint
    p_CTWR_Setpoint_Model(adj=1.05)
                                   annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={-30,1})));
  Modelica.Blocks.Interfaces.RealInput Towb "Towb" annotation (Placement(
        transformation(
        extent={{-14.8,-15},{14.8,15}},
        rotation=180,
        origin={-99.2,1}),   iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Interfaces.RealInput T_HTWS "T_HTWS" annotation (Placement(
        transformation(
        extent={{-15,-15},{15,15}},
        rotation=180,
        origin={-99,-61}), iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Interfaces.RealOutput CTWP_Nrel "CTWP Nrel" annotation (
      Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,60}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Interfaces.RealOutput p_CTWR_setpoint "CTWP Nrel" annotation (
     Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,1}),  iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Interfaces.RealOutput T_CT_setpoint "CT Temp. setpoint"
    annotation (Placement(transformation(
        extent={{-13.8,-14},{13.8,14}},
        rotation=0,
        origin={113.8,-61}), iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Continuous.Filter filter(filterType=Modelica.Blocks.Types.FilterType.LowPass,
      f_cut=f_cut)
    annotation (Placement(transformation(extent={{-6,23},{8,9}})));
equation
  //   delayed_p_setpoint = delay(p_CTWR_setpoint, data.delay);
  connect(PID_CTWP.y, CTWP_Nrel);
  connect(Towb,p_CTWR_Setpoint_Model. Towb);
  connect(T_HTWS,p_CTWR_Setpoint_Model. T_HTWS);
  connect(p_CTWR_setpoint,p_CTWR_Setpoint_Model. p_CTWR_setpoint);
  connect(T_CT_setpoint,p_CTWR_Setpoint_Model. T_CT_setpoint);
  connect(p_CTWR,p_CTWR_Setpoint_Model. p_CTWR);
  connect(filter.y, PID_CTWP.u_m)
    annotation (Line(points={{8.7,16},{13,16},{13,-0.2}}, color={0,0,127}));
  connect(p_CTWR_Setpoint_Model.p_CTWR_measured, filter.u) annotation (Line(
        points={{-41,-3},{-24,-3},{-24,-2},{-10,-2},{-10,16},{-7.4,16}},
        color={0,0,127}));
  connect(PID_CTWP.u_s, p_CTWR_Setpoint_Model.p_CTWR_setpoint) annotation (Line(
        points={{2.2,-11},{-14,-11},{-14,1},{-41,1}},          color={0,0,127}));
end CTWP_speed;
