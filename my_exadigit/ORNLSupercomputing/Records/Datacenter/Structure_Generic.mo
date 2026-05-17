within ORNLSupercomputing.Records.Datacenter;
model Structure_Generic

  parameter Real fudge_factor_CDUP=1.00;
  parameter Real fudge_factor_HTWP=1.00;
  parameter Real fudge_factor_CTWP=1.00;
  parameter Integer nHTWPs=1;
  parameter Integer nCTWPs=1;
  parameter Integer nCTs=1;
  parameter Integer nEHXs=1;

  parameter BaseClasses.Records.S_Datacenter data annotation (Placement(
        transformation(extent={{-8,-8},{12,12}})), choicesAllMatching=true);
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end Structure_Generic;
