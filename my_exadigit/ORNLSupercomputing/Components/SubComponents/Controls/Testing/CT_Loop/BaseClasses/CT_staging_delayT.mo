within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CT_Loop.BaseClasses;
model CT_staging_delayT "CT staging with deltaT based on T - Tdelay"
  extends Modelica.Blocks.Icons.Block;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.from_psi;
  Real delT;
  Real new_T;
  Modelica.Units.SI.Time startTime[nCT_max]; // for exponent change
  Real xb[nCT_max](start = fill(eps, nCT_max)); // tracker variable
  parameter Real eps = 1e-5; //small valve indicating closed valve
  parameter Real delayMax=30 "Time in seconds - 10 min Rolling average" annotation(Dialog(group="Inputs"));
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
        extent={{19.8,-20},{-19.8,20}},
        rotation=180,
        origin={-120.2,20}),iconTransformation(
        extent={{10.2,-10},{-10.2,10}},
        rotation=180,
        origin={-110.2,-40})));
  Modelica.Blocks.Interfaces.RealInput p "CTWR header pressure (gauge)"
                                                                annotation (
      Placement(transformation(
        extent={{19.8,-20},{-19.8,20}},
        rotation=180,
        origin={-120.2,-20}),iconTransformation(
        extent={{10.2,-10},{-10.2,10}},
        rotation=180,
        origin={-110.2,50})));
  Modelica.Blocks.Interfaces.RealOutput valveCTs[nCT_max] "CT valve"
    annotation (Placement(transformation(
        extent={{-16,-16},{16,16}},
        rotation=0,
        origin={116,20}),
                        iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,-40})));
  Modelica.Blocks.Interfaces.RealOutput    nCT "No. of active CTs"
    annotation (Placement(transformation(
        extent={{-16,-16},{16,16}},
        rotation=0,
        origin={116,-20}),
                        iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,40})));
initial equation
  nCT = nCT_start;
  startTime[1:nCT_max] = zeros(nCT_max);
  valveCTs[1:nCT_start] = ones(nCT_start);
  valveCTs[nCT_start+1:nCT_max] = zeros(nCT_max - nCT_start);
equation
  assert(tau > 0.0, "Time constant must be positive");
  assert(nCT_max >= nCT_min, "max. no of CTs should be >= min no. of CTs");
  assert(nCT_start >= nCT_min, "starting no of CTs should be >= min no. of CTs");
  assert(nCT_start <= nCT_max, "starting no of CTs should be <= max no. of CTs");
  new_T = delay(T, delayMax);
  delT = T - new_T;
  when (time > delayMax) and abs(delT) >= delTtol then
    if delT >= delTtol and p - ps_stage_up >= delptol then
      nCT = min(max(pre(nCT) + 1, nCT_min), nCT_max);
    elseif delT <= -delTtol and p - ps_stage_down <= -delptol then
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
end CT_staging_delayT;
