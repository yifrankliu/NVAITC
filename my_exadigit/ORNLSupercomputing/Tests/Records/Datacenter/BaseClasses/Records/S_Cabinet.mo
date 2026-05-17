within ORNLSupercomputing.Tests.Records.Datacenter.BaseClasses.Records;
record S_Cabinet
  final parameter Integer nShelves=size(shelf, 1);
  parameter
    ORNLSupercomputing.Tests.Records.Datacenter.BaseClasses.Records.S_Shelf[:] shelf;

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end S_Cabinet;
