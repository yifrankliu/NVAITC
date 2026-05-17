within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses;
model CT_staging
  "CT staging with deltaT based on T - Tdelay modified accounting for 30 min delT as well"
  extends Modelica.Blocks.Icons.Block;
  import TRANSFORM.Units.Conversions.Functions.Pressure_Pa.to_psi;
  Real delT, delT2;
  Real new_T, new_T2;
//   Real T_int, T_int_2;

  Real delpUp, delpDown;
  Modelica.Units.SI.Time startTime[nCT_max]; // for exponent change
  Real xb[nCT_max](start = fill(eps, nCT_max)); // tracker variable
  parameter Real eps = 1e-5; //small valve indicating closed valve
  parameter Real delayMax=30 "Time in seconds for delay" annotation(Dialog(group="Inputs"));
  parameter Real delayMax2=1800 "Time in seconds for longer delay" annotation(Dialog(group="Inputs"));
  parameter Real delTtol=eps "delta T (abs(T-Tdelay)) tolerance " annotation(Dialog(group="Inputs"));
  parameter Real delptol=eps "delta p (p - ps_stage) tolerance" annotation(Dialog(group="Inputs"));
  parameter Integer nCT_start=12 "starting no of CTs" annotation(Dialog(group="Inputs"));
  parameter Integer nCT_min=7 "min. no of CTs" annotation(Dialog(group="Inputs"));
  parameter Integer nCT_max=16 "max. no of CTs" annotation(Dialog(group="Inputs"));
  parameter Real ps_stage_up = 23.9 "CT Staging up pressure (gauge) boundary" annotation(Dialog(group="Inputs"));
  parameter Real ps_stage_down = 22.9 "CT Staging down pressure (gauge) boundary" annotation(Dialog(group="Inputs"));
  parameter Modelica.Units.SI.Time tau = 4.0 "Time constant to open/close valves" annotation(Dialog(group="Inputs"));
  parameter Real valve_opening_min = 0.01 "Minimium opening of valves";
  Real valve_int[nCT_max];

  Modelica.Blocks.Interfaces.RealInput T "HTWS Temperature"
    annotation (Placement(transformation(
        extent={{19.8,-20},{-19.8,20}},
        rotation=180,
        origin={-120.2,30}),iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,-30})));
  Modelica.Blocks.Interfaces.RealInput p "CTWR header pressure (gauge)"
                                                                annotation (
      Placement(transformation(
        extent={{19.8,-20},{-19.8,20}},
        rotation=180,
        origin={-120.2,-30}),iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,30})));
  Modelica.Blocks.Interfaces.RealOutput valveCTs[nCT_max] "CT valve"
    annotation (Placement(transformation(
        extent={{-20,-20},{20,20}},
        rotation=0,
        origin={120,30}),
                        iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,-30})));
  Modelica.Blocks.Interfaces.RealOutput    nCT "No. of active CTs"
    annotation (Placement(transformation(
        extent={{-20,-20},{20,20}},
        rotation=0,
        origin={120,-30}),
                        iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,30})));

initial equation
  nCT = nCT_start;
  startTime[1:nCT_max] = zeros(nCT_max);
  valveCTs[1:nCT_start] = ones(nCT_start);
  valveCTs[nCT_start+1:nCT_max] = valve_opening_min*ones(nCT_max - nCT_start);

equation
  assert(tau > 0.0, "Time constant must be positive");
  assert(nCT_max >= nCT_min, "max. no of CTs should be >= min no. of CTs");
  assert(nCT_start >= nCT_min, "starting no of CTs should be >= min no. of CTs");
  assert(nCT_start <= nCT_max, "starting no of CTs should be <= max no. of CTs");
  delpUp = p - ps_stage_up;
  delpDown = p - ps_stage_down;

//   new_T = delay(T_int, delayMax);
//   delT = T - new_T;
//
//   new_T2 = delay(T_int_2, delayMax2);
//   delT2 = T - new_T2;

  new_T = delay(T, delayMax);
  delT = T - new_T;

  new_T2 = delay(T, delayMax2);
  delT2 = T - new_T2;

  when delpUp >= delptol and time > delayMax and delT >= delTtol then
    nCT = min(max(pre(nCT) + 1, nCT_min), nCT_max);
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
  elsewhen delpUp >= delptol and time > delayMax2 and delT2 >= delTtol then
    nCT = min(max(pre(nCT) + 1, nCT_min), nCT_max);
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
  elsewhen delpDown <= -delptol and time > delayMax and delT <= -delTtol then
    nCT = min(max(pre(nCT) - 1, nCT_min), nCT_max);
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
  elsewhen delpDown <= -delptol and time > delayMax2 and delT2 <= -delTtol then
    nCT = min(max(pre(nCT) - 1, nCT_min), nCT_max);
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
      valve_int[idx] = 1.0 - Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Open the valve
    elseif xb[idx] <= -0.5 then
      valve_int[idx] = Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Close the valve
    else
      valve_int[idx] = valve_int[idx];
      // Do nothing
    end if;
    valveCTs[idx] = Modelica.Media.Air.MoistAir.Utilities.smoothMax(valve_int[idx],valve_opening_min, 0.5*valve_opening_min);
  end for;

end CT_staging;
