within ORNLSupercomputing.Records.Datacenter.BaseClasses.Records;
record S_Shelf
  final parameter Integer nChassis=size(chassis, 1);
  parameter ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Chassis[
    :] chassis;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));

end S_Shelf;
