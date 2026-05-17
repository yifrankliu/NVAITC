within TemplatesCSM.BaseClasses.Fluids;
partial model PartialFourPort_left_right
  extends TemplatesCSM.BaseClasses.Fluids.Mediums_Two;
  extends TemplatesCSM.BaseClasses.Fluids.Interface_FourPort;

  final parameter Boolean allowFlowReversal=false
    "= true to allow flow reversal, false restricts to design direction (port_a -> port_b)"
    annotation (Dialog(tab="Assumptions"), Evaluate=true);
  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_a1
    constrainedby TRANSFORM.Fluid.Interfaces.FluidPort_Flow(
    redeclare package Medium = Medium_1,
    m_flow(min=if allowFlowReversal then -Modelica.Constants.inf else 0),
    h_outflow(start=Medium_1.h_default)) annotation (Placement(transformation(
          extent={{-190,50},{-170,70}}), iconTransformation(extent={{-110,50},
            {-90,70}})));
  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_b1
    constrainedby TRANSFORM.Fluid.Interfaces.FluidPort_Flow(
    redeclare package Medium = Medium_1,
    m_flow(max=if allowFlowReversal then +Modelica.Constants.inf else 0),
    h_outflow(start=Medium_1.h_default)) annotation (Placement(transformation(
          extent={{-170,-70},{-190,-50}}), iconTransformation(extent={{-110,
            -70},{-90,-50}})));

  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_a2
    constrainedby TRANSFORM.Fluid.Interfaces.FluidPort_Flow(
    redeclare package Medium = Medium_2,
    m_flow(min=if allowFlowReversal then -Modelica.Constants.inf else 0),
    h_outflow(start=Medium_2.h_default)) annotation (Placement(transformation(
          extent={{170,-70},{190,-50}}), iconTransformation(extent={{90,-70},
            {110,-50}})));
  replaceable TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_b2
    constrainedby TRANSFORM.Fluid.Interfaces.FluidPort_Flow(
    redeclare package Medium = Medium_2,
    m_flow(max=if allowFlowReversal then +Modelica.Constants.inf else 0),
    h_outflow(start=Medium_2.h_default)) annotation (Placement(transformation(
          extent={{190,50},{170,70}}), iconTransformation(extent={{90,52},{110,
            72}})));

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-180,-100},{180,
            100}})));
end PartialFourPort_left_right;
