within ORNLSupercomputing.Components.SubComponents.Fluid.Pumps;
model CTWP "CTW Pump"

  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_bar;
  import TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;

  extends TRANSFORM.Fluid.Machines.Pump_Controlled(
    redeclare replaceable package Medium =
        ORNLSupercomputing.Components.SubComponents.Media.Medium,
    diameter_nominal=10.875*0.0254,
    p_a_start=from_bar(1.5),
    p_b_start=from_psi(43.0),
    T_a_start=from_degC(20.0),
    m_flow_start=200,
    redeclare replaceable model FlowChar =
        TRANSFORM.Fluid.Machines.BaseClasses.PumpCharacteristics.Flow.CombiTableCurve
        (flowChar=[17.07658179,0.521605893; 19.11097601,0.498855438;
            21.88514995,0.460386486; 24.04284079,0.421917535; 26.0155867,
            0.383448583; 27.86503599,0.345393276; 29.59118867,0.306924324;
            31.13239641,0.268455373; 32.24206598,0.230400066; 32.61195584,
            0.191517469; 33.04349401,0.11499321; 33.10514232,0.060392118;
            33.16679063,0.000413645]),
    redeclare replaceable model EfficiencyChar =
        TRANSFORM.Fluid.Machines.BaseClasses.PumpCharacteristics.Efficiency.Constant
        (eta_constant=0.612),
    N_nominal=1780,
    m_flow_nominal=m_flow_start/nParallel,
    use_port=true,
    k_inputSignal=N_nominal/100);

end CTWP;
