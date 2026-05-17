within ORNLSupercomputing.Records.Datacenter.BaseClasses.Records;
record S_CoolingBlock
  parameter Integer nCDUs=1;
  final parameter Integer nCabinets=size(cabinet, 1);
  parameter ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Cabinet[
    :] cabinet;

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end S_CoolingBlock;
