within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Data;
record v0_CS
  extends BaseClasses.PartialData;

  // OLCF-5 SOOs 221116 : SEQUENCES OF OPERATIONS FOR OLCF-5 MECHANICAL SYSTEMS,
  // JOHNSON CONTROLS (s1)
  // Two CDUPs are always set to be operational
  // The CDUPs are staged up when the operational pump speeds touch Nrel_max
  // and staged down when the operational pump speeds touch Nrel_min.
  // The PID controller for the pump speeds is controlled by the dP setpoint.
  // The setpoint is fixed at 27.5 psi.
  // The primary flow control valve is controlled by the sec. temp. setpoint of
  // 28.0 deg C.
  import
    TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;
  parameter Real dp_nom=27.5;
  parameter Real Tsec_supply_nom=28.0;
  //deg. C
  parameter Real CDUP_Nrel_min=52.0;
  parameter Real CDUP_Nrel_max=75.0;
  parameter Real CDUP_Nrel_start=64.0;
  parameter Real CDU_CV_min=0.05;
  parameter Real CDU_CV_max=1.0;
  parameter Real CDU_CV_start=0.5;
  // Control System tuning parameters
  parameter Real gain_CDUP=0.1;
  parameter Real Ti_CDUP=100.0;
  // s
  parameter Real Td_CDUP=30.0;
  // s
  //
  parameter Real gain_CV=-0.9;
  parameter Real Ti_CV=35.0;
  // s
  parameter Real Td_CV=9.0;
  // s
  parameter Real db_CV=0.3;
  //deg. C
  parameter Real dbr_CV=0.1;

  annotation (defaultComponentName="data");
end v0_CS;
