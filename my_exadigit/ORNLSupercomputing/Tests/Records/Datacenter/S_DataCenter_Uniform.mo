within ORNLSupercomputing.Tests.Records.Datacenter;
record S_DataCenter_Uniform

  parameter Integer nCoolingBlocks=1;
  parameter Integer nCDUsPerCoolingBlock=1;
  parameter Integer nCabinetsPerCoolingBlock=1;
  parameter Integer nShelvesPerCabinet=1;
  parameter Integer nChassisPerShelf=1;
  parameter Integer nRectifiersPerChassis=1;
  parameter Integer nBladesPerChassis=1;
  parameter Integer nNodesPerBlade=1;
  parameter Integer nCPUsPerNode=1;
  parameter Integer nGPUsPerNode=1;

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end S_DataCenter_Uniform;
