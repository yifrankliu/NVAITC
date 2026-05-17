within ORNLSupercomputing.Systems.Datacenter.BaseClasses;
model Summary
  extends TemplatesCSM.BaseClasses.Systems.PartialSummary;

  input SI.MassFlowRate m_flow_bypass = 0.0 "Bypass mass flow rate" annotation(Dialog(group="Inputs"));
  output Real V_flow_bypass_GPM = m_flow_bypass/0.063 "Bypass volume flow rate in GPM"  annotation(Dialog(group="Outputs", enable=false));

end Summary;
