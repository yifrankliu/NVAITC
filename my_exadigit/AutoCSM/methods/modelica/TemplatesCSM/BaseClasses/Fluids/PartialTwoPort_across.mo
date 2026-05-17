within TemplatesCSM.BaseClasses.Fluids;
partial model PartialTwoPort_across
  extends TemplatesCSM.BaseClasses.Fluids.Medium_Single;
  extends TemplatesCSM.BaseClasses.Fluids.Interface_TwoPort;

  final parameter Boolean allowFlowReversal=false
    "= true to allow flow reversal, false restricts to design direction (port_a -> port_b)"
    annotation (Dialog(tab="Assumptions"), Evaluate=true);
  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_a constrainedby
    TRANSFORM.Fluid.Interfaces.FluidPort(
    redeclare package Medium = Medium,
    m_flow(min=if allowFlowReversal then -Modelica.Constants.inf else 0),
    h_outflow(start=Medium.h_default))
    "Fluid connector a (positive design flow direction is from port_a to port_b)"
    annotation (Placement(transformation(extent={{-190,-10},{-170,10}}),
        iconTransformation(extent={{-110,-10},{-90,10}})));
  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_b constrainedby
    TRANSFORM.Fluid.Interfaces.FluidPort(
    redeclare package Medium = Medium,
    m_flow(max=if allowFlowReversal then +Modelica.Constants.inf else 0),
    h_outflow(start=Medium.h_default))
    "Fluid connector b (positive design flow direction is from port_a to port_b)"
    annotation (Placement(transformation(extent={{190,-10},{170,10}}),
        iconTransformation(extent={{90,-10},{110,10}})));

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-180,-100},{180,
            100}})));
end PartialTwoPort_across;
