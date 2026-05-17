within ORNLSupercomputing.Records.Datacenter.BaseClasses.Records;
record S_Chassis
  parameter Integer nRectifiers=1;
  final parameter Integer nBlades=size(blade, 1);
  parameter ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Blade[:]
    blade;

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end S_Chassis;
