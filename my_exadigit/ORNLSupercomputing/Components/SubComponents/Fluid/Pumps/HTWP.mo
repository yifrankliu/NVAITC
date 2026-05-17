within ORNLSupercomputing.Components.SubComponents.Fluid.Pumps;
model HTWP "HTW Pump"

  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  import TRANSFORM.Units.Conversions.Functions.Temperature_K.from_degC;

  extends TRANSFORM.Fluid.Machines.Pump_Controlled(
    redeclare replaceable package Medium =
        ORNLSupercomputing.Components.SubComponents.Media.Medium,
    diameter_nominal=16*0.0254,
    p_a_start=from_psi(59.7),
    p_b_start=from_psi(87.7),
    T_a_start=from_degC(30.0),
    m_flow_start=100,
    redeclare replaceable model FlowChar =
        TRANSFORM.Fluid.Machines.BaseClasses.PumpCharacteristics.Flow.CombiTableCurve
        (flowChar=[37.82413483,0.477445061; 41.21240825,0.46209522; 45.80996943,
            0.439577949; 50.88917518,0.409885084; 55.48229951,0.378135051;
            59.83287611,0.346382298; 62.72915232,0.316664942; 65.38189484,
            0.28489314; 67.54904892,0.252090034; 68.9890528,0.220304627;
            69.94445421,0.18953964; 70.89936264,0.157748791; 71.36917561,
            0.125952499; 71.59693384,0.095179349; 71.82419909,0.063380336;
            72.03766081,0.031581323; 72.05146434,0.002857176]),
    redeclare replaceable model EfficiencyChar =
        TRANSFORM.Fluid.Machines.BaseClasses.PumpCharacteristics.Efficiency.Constant
        (eta_constant=0.835),
    N_nominal=1785,
    m_flow_nominal=m_flow_start/nParallel,
    use_port=true,
    k_inputSignal=N_nominal/100);

//     redeclare replaceable model FlowChar =
//         TRANSFORM.Fluid.Machines.BaseClasses.PumpCharacteristics.Flow.PerformanceCurve
//         (V_flow_curve={0.477445061,0.46209522,0.439577949,0.409885084,0.378135051,
//             0.346382298,0.316664942,0.28489314,0.252090034,0.220304627,0.18953964,
//             0.157748791,0.125952499,0.095179349,0.063380336,0.031581323,0.002857176},
//           head_curve={37.82413483,41.21240825,45.80996943,50.88917518,55.48229951,
//             59.83287611,62.72915232,65.38189484,67.54904892,68.9890528,69.94445421,
//             70.89936264,71.36917561,71.59693384,71.82419909,72.03766081,72.05146434}),

end HTWP;
