within TemplatesCSM.BaseClasses.Fluids;
record Interface_TwoPort
  extends TemplatesCSM.BaseClasses.Fluids.Medium_Single;

  /* Nominal Conditions */
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_a_nominal(
      redeclare package Medium = Medium, h=Medium.specificEnthalpy(
        Medium.setState_pT(port_a_nominal.p, port_a_nominal.T))) "port_a"
    annotation (Dialog(tab="Nominal Conditions"));
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_b_nominal(
    redeclare package Medium = Medium,
    p=port_a_nominal.p,
    T=port_a_nominal.T,
    h=Medium.specificEnthalpy(Medium.setState_pT(port_b_nominal.p,
        port_b_nominal.T)),
    m_flow=-port_a_nominal.m_flow) "port_b"
    annotation (Dialog(tab="Nominal Conditions"));

  /* Initialization */
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_a_start(
    redeclare package Medium = Medium,
    p=port_a_nominal.p,
    T=port_a_nominal.T,
    h=Medium.specificEnthalpy(Medium.setState_pT(port_a_start.p, port_a_start.T)),
    m_flow=port_a_nominal.m_flow) "port_a"
    annotation (Dialog(tab="Initialization"));
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_b_start(
    redeclare package Medium = Medium,
    p=port_a_start.p,
    T=port_a_start.T,
    h=Medium.specificEnthalpy(Medium.setState_pT(port_b_start.p, port_b_start.T)),
    m_flow=-port_a_start.m_flow) "port_b"
    annotation (Dialog(tab="Initialization"));

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end Interface_TwoPort;
