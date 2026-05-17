within ORNLSupercomputing.Components.SubComponents.Fluid.Pumps;
model CDUP "CDU Pump"

  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;

  extends TRANSFORM.Fluid.Machines.Pump_Controlled(
    redeclare replaceable package Medium =
        ORNLSupercomputing.Components.SubComponents.Media.Medium,
    nParallel=2,
    p_a_start=from_psi(30.5),
    p_b_start=p_a_start + dp_nominal,
    T_a_start=303.15,
    m_flow_start=15,
    redeclare replaceable model FlowChar =
        TRANSFORM.Fluid.Machines.BaseClasses.PumpCharacteristics.Flow.CombiTableCurve
        (flowChar=[0,0.0573; 38.5036,0.04; 53.2157,0.03; 62.3878,0.02; 66.0815,0.008;
            68,0]),
    redeclare replaceable model EfficiencyChar =
        TRANSFORM.Fluid.Machines.BaseClasses.PumpCharacteristics.Efficiency.Constant
        (eta_constant=0.85),
    N_nominal=3500,
    dp_nominal=100000,
    m_flow_nominal=m_flow_start/nParallel,
    use_port=true,
    k_inputSignal=N_nominal/100);

end CDUP;
