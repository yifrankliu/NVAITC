within ORNLSupercomputing.Components.SubComponents.Controls.Testing.EHX_Loop.BaseClasses;
model EHX_Staging
  // EHX staging is based on the no. of active cooling tower cells.
  // EHX staging is performed
  // activated through control valves.
  extends Modelica.Blocks.Icons.Block;
  Integer nEHX; // nEHX for tracking no of EHXs
  Modelica.Units.SI.Time startTime[nEHX_max]; // for exponent change
  Real xb[nEHX_max](start = fill(eps, nEHX_max)); // tracker variable
  parameter Real eps = 1e-5; //small valve indicating closed valve
  parameter Integer nEHX_start=2 "Starting number of EHXs" annotation(Dialog(group="Inputs"));
  // starting no of EHXs
  parameter Integer nEHX_min=1 "Min. number of EHXs" annotation(Dialog(group="Inputs"));
  // min. no of EHXs
  parameter Modelica.Units.SI.Time tau = 4.0 "Time constant to open/close valves" annotation(Dialog(group="Inputs"));
  // time constant to open/close valves
  parameter Integer nEHX_max=4 "Max number of EHXs" annotation(Dialog(group="Inputs"));
  // max. no of EHXs
  parameter Real nCT_crit[nEHX_max] = {1, 4, 8, 12} "no of cooling towers for staging EHXs" annotation(Dialog(group="Inputs"));
  // Criteria for staging EHXs
  Modelica.Blocks.Interfaces.RealInput    nCT
    "No. of cooling towers in operation" annotation (Placement(transformation(
        extent={{-19.8,-20},{19.8,20}},
        rotation=180,
        origin={-100.2,0}),  iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,0})));
  Modelica.Blocks.Interfaces.RealOutput valveEHXs[nEHX_max] "EHX valves"
    annotation (Placement(transformation(
        extent={{-16,-16},{16,16}},
        rotation=0,
        origin={116,0}), iconTransformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={110,0})));
initial equation
  nEHX = nEHX_start;
  startTime[1:nEHX_max] = zeros(nEHX_max);
  valveEHXs[1:nEHX_start] = ones(nEHX_start);
  valveEHXs[nEHX_start+1:nEHX_max] = zeros(nEHX_max-nEHX_start);
equation
  assert(tau > 0.0, "Time constant must be positive");
  assert(nEHX_max >= nEHX_min, "max. no of EHXs should be >= min no. of EHXs");
  assert(nEHX_start >= nEHX_min, "starting no of EHXs should be >= min no. of EHXs");
  assert(nEHX_start <= nEHX_max, "starting no of EHXs should be <= max no. of EHXs");
  assert(size(nCT_crit,1) == nEHX_max, "Criteria size should match max no. of EHXs");
  when {nCT >= nCT_crit[min(pre(nEHX) + 1, nEHX_max)], nCT < nCT_crit[pre(nEHX)]} then
    if nCT >= nCT_crit[min(pre(nEHX) + 1, nEHX_max)] then
      nEHX = min(max(pre(nEHX) + 1, nEHX_min), nEHX_max);
    elseif nCT < nCT_crit[pre(nEHX)] then
      nEHX = min(max(pre(nEHX) - 1, nEHX_min), nEHX_max);
    else
      nEHX = min(max(pre(nEHX), nEHX_min), nEHX_max);
    end if;
    for idx in 1:nEHX_max loop
      startTime[idx] = time;
      if nCT >= nCT_crit[idx] then
        if pre(valveEHXs[idx]) < 0.5 then
          xb[idx] = 1.0;
          // Open the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      else
        if pre(valveEHXs[idx]) >= 0.5 then
          xb[idx] = -1.0;
          // Close the valve
        else
          xb[idx] = eps;
          // Do nothing
        end if;
      end if;
    end for;
  end when;
  for idx in 1:nEHX_max loop
    if xb[idx] >= 0.5 then
      valveEHXs[idx] = 1.0 - Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Open the valve
    elseif xb[idx] <= -0.5 then
      valveEHXs[idx] = Modelica.Math.exp(-(time - startTime[idx])/tau);
      // Close the valve
    else
      valveEHXs[idx] = valveEHXs[idx];
      // Do nothing
    end if;
  end for;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end EHX_Staging;
