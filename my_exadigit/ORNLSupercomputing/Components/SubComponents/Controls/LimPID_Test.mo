within ORNLSupercomputing.Components.SubComponents.Controls;
model LimPID_Test
  import TRANSFORM;
  extends TRANSFORM.Icons.Example;
  Modelica.Blocks.Sources.Sine  sine(f=10)
    annotation (Placement(transformation(extent={{-62,4},{-42,24}})));
  LimPID_Deadband_dbr limPID_deadband(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    Ti=1,
    Td=1,
    yMax=1,
    yMin=-1,
    initType=Modelica.Blocks.Types.Init.InitialState,
    derMeas=false,
    k=-1,
    deadband=0.5,
    deadbandRatio=0.5) "Controller with deadband"
    annotation (Placement(transformation(extent={{-2,-38},{18,-18}})));
  Modelica.Blocks.Sources.Constant const(k=0.5)
    annotation (Placement(transformation(extent={{-62,-26},{-42,-6}})));
  Modelica.Blocks.Continuous.LimPID limPID_original(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    k=-1,
    Ti=1,
    Td=1,
    yMax=1,
    yMin=-1,
    initType=Modelica.Blocks.Types.Init.InitialState)
    annotation (Placement(transformation(extent={{-2,44},{18,64}})));
  LimPID_Hysteresis limPID_hysteresis(
    controllerType=Modelica.Blocks.Types.SimpleController.PID,
    k=-1,
    Ti=1,
    Td=1,
    yMax=1,
    yMin=-1,
    initType=Modelica.Blocks.Types.Init.InitialState)
    "Controller with hysteresis"
    annotation (Placement(transformation(extent={{-2,4},{18,24}})));
equation
  connect(sine.y, limPID_deadband.u_s) annotation (Line(points={{-41,14},{-27.5,
          14},{-27.5,-28},{-4,-28}}, color={0,0,127}));
  connect(const.y, limPID_deadband.u_m) annotation (Line(points={{-41,-16},{-28,
          -16},{-28,-56},{8,-56},{8,-40}}, color={0,0,127}));
  connect(sine.y, limPID_original.u_s) annotation (Line(points={{-41,14},{-27.5,
          14},{-27.5,54},{-4,54}}, color={0,0,127}));
  connect(const.y, limPID_original.u_m) annotation (Line(points={{-41,-16},{-28,
          -16},{-28,36},{8,36},{8,42}},     color={0,0,127}));
  connect(limPID_hysteresis.u_s, sine.y)
    annotation (Line(points={{-4,14},{-41,14}}, color={0,0,127}));
  connect(limPID_hysteresis.u_m, const.y) annotation (Line(points={{8,2},{8,-4},
          {-28,-4},{-28,-16},{-41,-16}}, color={0,0,127}));
 annotation (experiment(Tolerance=1e-6, StopTime=1.0),
    Documentation(revisions="<html>
</html>", info="<html>
<p>This model tests the implementation of the PID controller with optional reverse action.</p>
</html>"));
end LimPID_Test;
