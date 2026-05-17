within ORNLSupercomputing.Systems.CentralEnergyPlant.Systems.HotWaterLoop.BaseClasses;
model Summary
  extends TemplatesCSM.BaseClasses.Systems.PartialSummary;
  input SI.MassFlowRate m_flow_htw = 0.0 "HTW mass flow rate" annotation(Dialog(group="Inputs"));
  output Real V_flow_htw_GPM = m_flow_htw/0.063 "HTW primary volume flow rate in GPM"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Pressure p_fac_htw_r = 0.0 "Fac HTW return pressure" annotation(Dialog(group="Inputs"));
  output Real p_fac_htw_r_psig = p_fac_htw_r*1e-5*14.503773773 - 14.503773773 "Fac. HTW return pressure in psig"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Pressure p_fac_htw_s = 0.0 "Fac HTW supply pressure" annotation(Dialog(group="Inputs"));
  output Real p_fac_htw_s_psig = p_fac_htw_s*1e-5*14.503773773 - 14.503773773 "Fac. HTW supply pressure in psig"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Temperature T_fac_htw_r = 0.0 "Fac. HTW return temperature" annotation(Dialog(group="Inputs"));
  output Real T_fac_htw_r_C = T_fac_htw_r - 273.15 "Fac. HTW return temperature in C"  annotation(Dialog(group="Outputs", enable=false));

  input SI.Temperature T_fac_htw_s = 0.0 "Fac. HTW supply temperature" annotation(Dialog(group="Inputs"));
  output Real T_fac_htw_s_C = T_fac_htw_s - 273.15 "Fac. HTW supply temperature in C"  annotation(Dialog(group="Outputs", enable=false));

  input SI.HeatFlowRate W_flow_HTWP = 0.0 "HTWP power consumption" annotation(Dialog(group="Inputs"));
  output Real W_flow_HTWP_kW = W_flow_HTWP*1e-3 "HTWP power consumption in kW"  annotation(Dialog(group="Outputs", enable=false));

  input Real N_HTWP = 0 "% speed of HTWP pump" annotation(Dialog(group="Inputs"));

  input Integer n_HTWPs = 0 "No. of HTWP pumps in operation" annotation(Dialog(group="Inputs"));

  input Integer n_EHXs = 0 "No. of EHXs in operation" annotation(Dialog(group="Inputs"));

end Summary;
