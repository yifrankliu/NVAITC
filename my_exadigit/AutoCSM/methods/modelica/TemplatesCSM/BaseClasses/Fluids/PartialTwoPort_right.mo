within TemplatesCSM.BaseClasses.Fluids;
partial model PartialTwoPort_right
  extends TemplatesCSM.BaseClasses.Fluids.Medium_Single;
  extends TemplatesCSM.BaseClasses.Fluids.Interface_TwoPort;

  final parameter Boolean allowFlowReversal=false
    "= true to allow flow reversal, false restricts to design direction (port_a -> port_b)"
    annotation (Dialog(tab="Assumptions"), Evaluate=true);
  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_a
    constrainedby TRANSFORM.Fluid.Interfaces.FluidPort(
    redeclare package Medium = Medium,
    m_flow(min=if allowFlowReversal then -Modelica.Constants.inf else 0),
    h_outflow(start=Medium.h_default))
    "Fluid connector a (positive design flow direction is from port_a to port_b)"
    annotation (Placement(transformation(extent={{170,-70},{190,-50}}),
        iconTransformation(extent={{90,-70},{110,-50}})));
  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_b
    constrainedby TRANSFORM.Fluid.Interfaces.FluidPort(
    redeclare package Medium = Medium,
    m_flow(max=if allowFlowReversal then +Modelica.Constants.inf else 0),
    h_outflow(start=Medium.h_default))
    "Fluid connector b (positive design flow direction is from port_a to port_b)"
    annotation (Placement(transformation(extent={{190,50},{170,70}}),
        iconTransformation(extent={{90,50},{110,70}})));

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-180,-100},{180,
            100}})));
end PartialTwoPort_right;
