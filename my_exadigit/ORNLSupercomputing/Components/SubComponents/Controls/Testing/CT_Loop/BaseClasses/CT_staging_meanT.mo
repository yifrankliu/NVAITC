within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CT_Loop.BaseClasses;
model CT_staging_meanT "CT Staging based on a delta T of T - mean T"
  extends Modelica.Blocks.Icons.Block;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  Modelica.Units.SI.Time startTime[nCT_max]; // for exponent change
  Real xb[nCT_max](start = fill(eps, nCT_max)); // tracker variable
  parameter Real eps = 1e-5; //small valve indicating closed valve
  parameter Real invFreq=30 "Time in seconds - 10 min Rolling average" annotation(Dialog(group="Inputs"));
  parameter Real delTtol=0.1 "delta T (abs(T-Tdelay)) tolerance " annotation(Dialog(group="Inputs"));
  parameter Real delptol=from_psi(0.1) "delta p (p - ps_stage) tolerance" annotation(Dialog(group="Inputs"));
  parameter Integer nCT_start=12 "starting no of CTs" annotation(Dialog(group="Inputs"));
  parameter Integer nCT_min=8 "min. no of CTs" annotation(Dialog(group="Inputs"));
  parameter Integer nCT_max=16 "max. no of CTs" annotation(Dialog(group="Inputs"));
  parameter Modelica.Units.SI.Pressure ps_stage_up = from_psi(23.9) "CT Staging up pressure boundary" annotation(Dialog(group="Inputs"));
  parameter Modelica.Units.SI.Pressure ps_stage_down = from_psi(22.9) "CT Staging down pressure boundary" annotation(Dialog(group="Inputs"));
  parameter Modelica.Units.SI.Time tau = 4.0 "Time constant to open/close valves" annotation(Dialog(group="Inputs"));

  Modelica.Blocks.Interfaces.RealInput T "HTWS Temperature"
    annotation (Placement(transformation(
        extent={{-19.8,-20},{19.8,20}},
        rotation=180,
        origin={-100.2,-2}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Math.Mean mean(f=1/invFreq) "Mean HTWS Temperature"
    annotation (Placement(transformation(extent={{-32,-10},{-14,8}})));
  Modelica.Blocks.Math.RealToBoolean convBoolean(threshold=delTtol)
                                                                annotation (
      Placement(transformation(
        extent={{7,7},{-7,-7}},
        rotation=180,
        origin={43,41})));
  Modelica.Blocks.Logical.Timer timer_CT annotation (Placement(transformation(
        extent={{7,6.875},{-7,-6.875}},
        rotation=180,
        origin={67,40.875})));
  Modelica.Blocks.Logical.GreaterEqualThreshold ThresholdCT(threshold=30)
    "Threshold for HTWS temp. increase"
    annotation (Placement(transformation(extent={{84,34},{98,47.75}})));
  Modelica.Blocks.Math.Feedback feedback
    annotation (Placement(transformation(extent={{-12,30},{8,50}})));
  Modelica.Blocks.Interfaces.RealInput p "CTWR header pressure" annotation (
      Placement(transformation(
        extent={{-19.8,-20},{19.8,20}},
        rotation=180,
        origin={-100.2,-40}),iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Math.Abs absValue annotation (Placement(transformation(
        extent={{7,7},{-7,-7}},
        rotation=180,
        origin={21,41})));
  Modelica.Blocks.Interfaces.RealOutput valveCTs[nCT_max] "CT valve"
    annotation (Placement(transformation(
        extent={{-13,-13},{13,13}},
        rotation=0,
        origin={113,-1}),
                        iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
  Modelica.Blocks.Interfaces.RealOutput    nCT "No. of active CTs"
    annotation (Placement(transformation(
        extent={{-15,-15},{15,15}},
        rotation=0,
        origin={115,-41}),
                        iconTransformation(
        extent={{-6,-6},{6,6}},
        rotation=180,
        origin={-40.4,26})));
initial equation
  nCT = nCT_start;
  startTime[1:nCT_max] = zeros(nCT_max);
  valveCTs[1:nCT_start] = ones(nCT_start);
  valveCTs[nCT_start+1:nCT_max] = zeros(nCT_max - nCT_start);
equation
  connect(T, mean.u) annotation (Line(points={{-100.2,-2},{-100.2,-1},{-33.8,-1}},
        color={0,0,127}));
  connect(convBoolean.y, timer_CT.u) annotation (Line(points={{50.7,41},{50.7,40.875},
          {58.6,40.875}}, color={255,0,255}));
  connect(timer_CT.y, ThresholdCT.u)
    annotation (Line(points={{74.7,40.875},{82.6,40.875}}, color={0,0,127}));
  connect(mean.y, feedback.u2) annotation (Line(points={{-13.1,-1},{-2,-1},{-2,32}},
                            color={0,0,127}));
  connect(T, feedback.u1) annotation (Line(points={{-100.2,-2},{-100.2,40},{-10,
          40}},
        color={0,0,127}));
  assert(tau > 0.0, "Time constant must be positive");
  assert(nCT_max >= nCT_min, "max. no of CTs should be >= min no. of CTs");
  assert(nCT_start >= nCT_min, "starting no of CTs should be >= min no. of CTs");
  assert(nCT_start <= nCT_max, "starting no of CTs should be <= max no. of CTs");
  when (time > invFreq*3.0) and (ThresholdCT.y == true) then
    if feedback.y >= delTtol and p - ps_stage_up >= delptol then
      nCT = min(max(pre(nCT) + 1, nCT_min), nCT_max);
    elseif feedback.y <= -delTtol and p - ps_stage_down <= -delptol then
      nCT = min(max(pre(nCT) - 1, nCT_min), nCT_max);
    else
      nCT = min(max(pre(nCT), nCT_min), nCT_max);
    end if;
    for idx in 1:nCT_max loop
      startTime[idx] = time;
      if idx <= nCT then
        if pre(valveCTs[idx]) < 0.5 then
          xb[idx] = 1.0;
          // Open the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      else
        if pre(valveCTs[idx]) >= 0.5 then
          xb[idx] = -1.0;
          // Close the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      end if;
    end for;
  end when;
  for idx in 1:nCT_max loop
    if xb[idx] >= 0.5 then
      valveCTs[idx] = 1.0 - Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Open the valve
    elseif xb[idx] <= -0.5 then
      valveCTs[idx] = Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Close the valve
    else
      valveCTs[idx] = valveCTs[idx];
      // Do nothing
    end if;
  end for;
  connect(absValue.y, convBoolean.u)
    annotation (Line(points={{28.7,41},{34.6,41}}, color={0,0,127}));
  connect(feedback.y, absValue.u)
    annotation (Line(points={{7,40},{7,41},{12.6,41}}, color={0,0,127}));
end CT_staging_meanT;
