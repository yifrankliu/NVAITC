within ORNLSupercomputing.Records.Datacenter.BaseClasses.Records;
record S_Blade
  final parameter Integer nNodes=size(node, 1);
  parameter ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Node[:]
    node;

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end S_Blade;
