within TemplatesCSM.BaseClasses.Fluids;
record Interface_FourPort
  extends TemplatesCSM.BaseClasses.Fluids.Mediums_Two;

  /* Nominal Conditions */
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_a1_nominal(
      redeclare package Medium = Medium_1, h=Medium_1.specificEnthalpy(
        Medium_1.setState_pT(port_a1_nominal.p, port_a1_nominal.T)))
    "port_a" annotation (Dialog(tab="Nominal Conditions"));
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_b1_nominal(
    redeclare package Medium = Medium_1,
    p=port_a1_nominal.p,
    T=port_a1_nominal.T,
    h=Medium_1.specificEnthalpy(Medium_1.setState_pT(port_b1_nominal.p,
        port_b1_nominal.T)),
    m_flow=-port_a1_nominal.m_flow) "port_b"
    annotation (Dialog(tab="Nominal Conditions"));

  /* Initialization */
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_a1_start(
    redeclare package Medium = Medium_1,
    p=port_a1_nominal.p,
    T=port_a1_nominal.T,
    h=Medium_1.specificEnthalpy(Medium_1.setState_pT(port_a1_start.p,
        port_a1_start.T)),
    m_flow=port_a1_nominal.m_flow) "port_a"
    annotation (Dialog(tab="Initialization"));

  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_b1_start(
    redeclare package Medium = Medium_1,
    p=port_a1_start.p,
    T=port_a1_start.T,
    h=Medium_1.specificEnthalpy(Medium_1.setState_pT(port_b1_start.p,
        port_b1_start.T)),
    m_flow=-port_a1_start.m_flow) "port_b"
    annotation (Dialog(tab="Initialization"));

  /* Nominal Conditions */
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_a2_nominal(
      redeclare package Medium = Medium_2, h=Medium_2.specificEnthalpy(
        Medium_2.setState_pT(port_a2_nominal.p, port_a2_nominal.T)))
    "port_a" annotation (Dialog(tab="Nominal Conditions"));
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_b2_nominal(
    redeclare package Medium = Medium_2,
    p=port_a2_nominal.p,
    T=port_a2_nominal.T,
    h=Medium_2.specificEnthalpy(Medium_2.setState_pT(port_b2_nominal.p,
        port_b2_nominal.T)),
    m_flow=-port_a2_nominal.m_flow) "port_b"
    annotation (Dialog(tab="Nominal Conditions"));

  /* Initialization */
  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_a2_start(
    redeclare package Medium = Medium_2,
    p=port_a2_nominal.p,
    T=port_a2_nominal.T,
    h=Medium_2.specificEnthalpy(Medium_2.setState_pT(port_a2_start.p,
        port_a2_start.T)),
    m_flow=port_a2_nominal.m_flow) "port_a"
    annotation (Dialog(tab="Initialization"));

  parameter TRANSFORM.Examples.Utilities.Record_fluidPorts port_b2_start(
    redeclare package Medium = Medium_2,
    p=port_a2_start.p,
    T=port_a2_start.T,
    h=Medium_2.specificEnthalpy(Medium_2.setState_pT(port_b2_start.p,
        port_b2_start.T)),
    m_flow=-port_a2_start.m_flow) "port_b"
    annotation (Dialog(tab="Initialization"));

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end Interface_FourPort;
