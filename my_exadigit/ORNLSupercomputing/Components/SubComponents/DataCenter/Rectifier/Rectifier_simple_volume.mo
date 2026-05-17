within ORNLSupercomputing.Components.SubComponents.DataCenter.Rectifier;
model Rectifier_simple_volume
  extends BaseClasses.PartialRectifiermodel(
  redeclare package Medium = ORNLSupercomputing.Components.SubComponents.Media.Medium,
  allowFlowReversal=true,
  port_a_nominal(
      p=TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi(64.60),
      T=303.15,
      m_flow=15.0),
  port_b_nominal(
      p=TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi(41.00),
      T=313.15));

  parameter Modelica.Units.SI.Volume ccVolRect = 0.3;
  parameter TRANSFORM.Units.HydraulicResistance R_Rectifier = 11000;

  TRANSFORM.Fluid.Interfaces.FluidPort_Flow
                                  port_a(redeclare package Medium = Medium)
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_State
                                        port_b(redeclare package Medium =
        Medium)
    annotation (Placement(transformation(extent={{90,-10},{110,10}})));
  TRANSFORM.Fluid.Volumes.SimpleVolume                   coolingChannels(
    redeclare package Medium = Medium,
    p_start=data.coolingChannels_pinit,
    T_start=data.coolingChannels_T_a_start,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
        (V=0.005),
    use_HeatPort=true)                     annotation (Placement(
        transformation(
        extent={{-10,10},{10,-10}},
        rotation=0)));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.HeatFlow boundary(use_port=
        true)
    annotation (Placement(transformation(
        extent={{8,8},{-8,-8}},
        rotation=90,
        origin={0,28})));
  Data.Data data
    annotation (Placement(transformation(extent={{78,82},{94,100}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance dP_Rectifier_in(
      redeclare package Medium = Medium, R=R_Rectifier*0.5)
    annotation (Placement(transformation(extent={{-70,-10},{-50,10}})));
  TRANSFORM.Fluid.FittingsAndResistances.SpecifiedResistance dP_Rectifier_out(
      redeclare package Medium = Medium, R=R_Rectifier*0.5)
    annotation (Placement(transformation(extent={{48,-10},{68,10}})));
equation
  connect(boundary.port, coolingChannels.heatPort) annotation (Line(points={{-4.996e-16,
          20},{-4.996e-16,13},{0,13},{0,6}}, color={191,0,0}));
  connect(boundary.Q_flow_ext, Q_flow_ext) annotation (Line(points={{1.11022e-16,
          31.2},{1.11022e-16,65.6},{0,65.6},{0,100}}, color={0,0,127}));
  connect(port_a, dP_Rectifier_in.port_a)
    annotation (Line(points={{-100,0},{-67,0}}, color={0,127,255}));
  connect(dP_Rectifier_in.port_b, coolingChannels.port_a)
    annotation (Line(points={{-53,0},{-6,0}}, color={0,127,255}));
  connect(coolingChannels.port_b, dP_Rectifier_out.port_a)
    annotation (Line(points={{6,0},{51,0}}, color={0,127,255}));
  connect(dP_Rectifier_out.port_b, port_b)
    annotation (Line(points={{65,0},{100,0}}, color={0,127,255}));
  annotation (Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{
            100,100}})),
    experiment(StopTime=22000, __Dymola_Algorithm="Esdirk45a"));
end Rectifier_simple_volume;
