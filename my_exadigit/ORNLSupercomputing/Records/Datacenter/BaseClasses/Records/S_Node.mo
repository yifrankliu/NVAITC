within ORNLSupercomputing.Records.Datacenter.BaseClasses.Records;
record S_Node
  parameter Integer nCPUs=1;
  parameter Integer nGPUs=1;
  //parameter Integer nMemorySlots;
  //parameter Integer nSICOV;
  //parameter Integer nNIC;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end S_Node;
