within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses;
model CTWP_Staging
  "Staging for CTWPs modified to account for down staging with nCT input"
  // Assume that all pumps run in the same speed, hence a common pump speed
  // can be used to stage pumps up or down. Additionally, pump staging is
  // activated through control valves.
  // The logic for CTWP also has additional criteria for satging down depending
  // on the number of CTs.
  extends Modelica.Blocks.Icons.Block;
//   Integer nPUMP; // nPUMP for tracking no of PUMPs
  Modelica.Units.SI.Time startTime[nPUMP_max]; // for exponent change
  Real xb[nPUMP_max](start = fill(eps, nPUMP_max)); // tracker variable
  parameter Real eps = 1e-5; //small valve indicating closed valve
  parameter Integer nPUMP_start=2 "Starting number of pumps" annotation(Dialog(group="Inputs"));
  // starting no of PUMPs
  parameter Integer nPUMP_min=2 "Min. number of pumps" annotation(Dialog(group="Inputs"));
  // min. no of PUMPs
  parameter Integer nPUMP_max=4 "Max. number of pumps" annotation(Dialog(group="Inputs"));
  // max. no of PUMPs
  parameter Real PUMP_Nrel_min=50.0 "Min. Rel. pump speed" annotation(Dialog(group="Inputs"));
  // min. pump speed
  parameter Real PUMP_Nrel_max=70.0 "Max. Rel. pump speed" annotation(Dialog(group="Inputs"));
  // max. pump speed
  parameter Modelica.Units.SI.Time tau = 4.0 "Time constant to open/close valves" annotation(Dialog(group="Inputs"));
  // time constant to open/close valves
  parameter Real tolerance = 0.1 "tolerance in %N to turn on/off pumps" annotation(Dialog(group="Inputs"));
  // tolerance to turn on/off pumps
  parameter Real valve_opening_min = 0.01 "Minimium opening of valves";
  Real valve_int[nPUMP_max];


  Modelica.Blocks.Interfaces.RealInput PUMP_Nrel "Pump Nrel" annotation (
      Placement(transformation(
        extent={{19.8,-20},{-19.8,20}},
        rotation=180,
        origin={-120.2,-30}),iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,-30})));
  Modelica.Blocks.Interfaces.RealOutput valvePUMP[nPUMP_max] "Pump valves"
    annotation (Placement(transformation(
        extent={{-20,-20},{20,20}},
        rotation=0,
        origin={120,30}),iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,-30})));
  Modelica.Blocks.Interfaces.IntegerOutput nPUMP "no. of pumps in operation"
    annotation (Placement(transformation(
        extent={{-20,-20},{20,20}},
        rotation=0,
        origin={120,-30}), iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,30})));
  Modelica.Blocks.Interfaces.RealInput nCT "no. of active cooling towers"
    annotation (Placement(transformation(
        extent={{19.8,-20},{-19.8,20}},
        rotation=180,
        origin={-120.2,30}), iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,30})));
initial equation
  nPUMP = nPUMP_start;
  startTime[1:nPUMP_max] = zeros(nPUMP_max);
  valvePUMP[1:nPUMP_start] = ones(nPUMP_start);
  valvePUMP[nPUMP_start+1:nPUMP_max] = valve_opening_min*ones(nPUMP_max-nPUMP_start);
equation
  assert(tau > 0.0, "Time constant must be positive");
  assert(nPUMP_max >= nPUMP_min, "max. no of pumps should be >= min no. of pumps");
  assert(nPUMP_start >= nPUMP_min, "starting no of pumps should be >= min no. of pumps");
  assert(nPUMP_start <= nPUMP_max, "starting no of pumps should be <= max no. of pumps");
  when abs(PUMP_Nrel - PUMP_Nrel_max) <= tolerance then
    nPUMP = min(max(pre(nPUMP) + 1, nPUMP_min), nPUMP_max);
    for idx in 1:nPUMP_max loop
      startTime[idx] = time;
      if idx <= nPUMP then
        if pre(valvePUMP[idx]) < 0.5 then
          xb[idx] = 1.0;
          // Open the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      else
        if pre(valvePUMP[idx]) >= 0.5 then
          xb[idx] = -1.0;
          // Close the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      end if;
    end for;
  elsewhen PUMP_Nrel <= PUMP_Nrel_min and nCT <= 14.0 and pre(
      nPUMP) == 4 then
    nPUMP = min(max(pre(nPUMP) - 1, nPUMP_min), nPUMP_max);
    for idx in 1:nPUMP_max loop
      startTime[idx] = time;
      if idx <= nPUMP then
        if pre(valvePUMP[idx]) < 0.5 then
          xb[idx] = 1.0;
          // Open the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      else
        if pre(valvePUMP[idx]) >= 0.5 then
          xb[idx] = -1.0;
          // Close the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      end if;
    end for;
  elsewhen PUMP_Nrel <= PUMP_Nrel_min and nCT <= 11.0 and pre(
      nPUMP) == 3 then
    nPUMP = min(max(pre(nPUMP) - 1, nPUMP_min), nPUMP_max);
    for idx in 1:nPUMP_max loop
      startTime[idx] = time;
      if idx <= nPUMP then
        if pre(valvePUMP[idx]) < 0.5 then
          xb[idx] = 1.0;
          // Open the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      else
        if pre(valvePUMP[idx]) >= 0.5 then
          xb[idx] = -1.0;
          // Close the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      end if;
    end for;
  elsewhen PUMP_Nrel <= PUMP_Nrel_min and nCT <= 8.0 and pre(
      nPUMP) == 3 then
    nPUMP = min(max(pre(nPUMP) - 1, nPUMP_min), nPUMP_max);
    for idx in 1:nPUMP_max loop
      startTime[idx] = time;
      if idx <= nPUMP then
        if pre(valvePUMP[idx]) < 0.5 then
          xb[idx] = 1.0;
          // Open the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      else
        if pre(valvePUMP[idx]) >= 0.5 then
          xb[idx] = -1.0;
          // Close the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      end if;
    end for;
  elsewhen abs(PUMP_Nrel - PUMP_Nrel_min) <= tolerance and nCT <= 8.0 and pre(
      nPUMP) == 2 then
    nPUMP = min(max(pre(nPUMP) - 1, nPUMP_min), nPUMP_max);
    for idx in 1:nPUMP_max loop
      startTime[idx] = time;
      if idx <= nPUMP then
        if pre(valvePUMP[idx]) < 0.5 then
          xb[idx] = 1.0;
          // Open the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      else
        if pre(valvePUMP[idx]) >= 0.5 then
          xb[idx] = -1.0;
          // Close the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      end if;
    end for;
  end when;

  for idx in 1:nPUMP_max loop
    if xb[idx] >= 0.5 then
      valve_int[idx] = 1.0 - Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Open the valve
    elseif xb[idx] <= -0.5 then
      valve_int[idx] = Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Close the valve
    else
      valve_int[idx] = valve_int[idx]; // Do nothing
    end if;
    valvePUMP[idx] = Modelica.Media.Air.MoistAir.Utilities.smoothMax(valve_int[idx],valve_opening_min, 0.5*valve_opening_min);
  end for;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end CTWP_Staging;
