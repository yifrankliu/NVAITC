within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.BaseClasses;
model Summary
  extends TemplatesCSM.BaseClasses.Systems.PartialSummary;
  input SI.MassFlowRate m_flow_ctw = 0.0 "CTW mass flow rate" annotation(Dialog(group="Inputs"));
  output Real V_flow_ctw_GPM = m_flow_ctw/0.063 "CTW primary volume flow rate in GPM"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Pressure p_fac_ctw_r = 0.0 "Fac ctw return pressure" annotation(Dialog(group="Inputs"));
  output Real p_fac_ctw_r_psig = p_fac_ctw_r*1e-5*14.503773773 - 14.503773773 "Fac. ctw return pressure in psig"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Pressure p_fac_ctw_s = 0.0 "Fac ctw supply pressure" annotation(Dialog(group="Inputs"));
  output Real p_fac_ctw_s_psig = p_fac_ctw_s*1e-5*14.503773773 - 14.503773773 "Fac. ctw supply pressure in psig"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Temperature T_fac_ctw_r = 0.0 "Fac. ctw return temperature" annotation(Dialog(group="Inputs"));
  output Real T_fac_ctw_r_C = T_fac_ctw_r - 273.15 "Fac. ctw return temperature in C"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Temperature T_fac_ctw_s = 0.0 "Fac. ctw supply temperature" annotation(Dialog(group="Inputs"));
  output Real T_fac_ctw_s_C = T_fac_ctw_s - 273.15 "Fac. ctw supply temperature in C"  annotation(Dialog(group="Outputs", enable=false));

  input SI.HeatFlowRate W_flow_CTWP = 0.0 "CTWP power consumption" annotation(Dialog(group="Inputs"));
  output Real W_flow_CTWP_kW = W_flow_CTWP*1e-3 "CTWP power consumption in kW"  annotation(Dialog(group="Outputs", enable=false));

  input SI.HeatFlowRate W_flow_CT = 0.0 "CT power consumption" annotation(Dialog(group="Inputs"));
  output Real W_flow_CT_kW = W_flow_CT*1e-3 "CT power consumption in kW"  annotation(Dialog(group="Outputs", enable=false));

  input SI.HeatFlowRate Q_flow_CT = 0.0 "Cooling tower heat removed" annotation(Dialog(group="Inputs"));
  output Real m_flow_evap = Q_flow_CT/(2260*1e3) "Cooling tower water evaporation rate in kg/s"  annotation(Dialog(group="Outputs", enable=false));

  input Real N_CTWP = 0 "% speed of CTWP pump" annotation(Dialog(group="Inputs"));

  input Integer n_CTWPs = 0 "No. of CTWP pumps in operation" annotation(Dialog(group="Inputs"));

  input Real n_CTs = 0 "No. of EHXs in operation" annotation(Dialog(group="Inputs"));
end Summary;
