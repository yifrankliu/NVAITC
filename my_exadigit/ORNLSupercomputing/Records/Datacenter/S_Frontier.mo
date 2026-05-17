within ORNLSupercomputing.Records.Datacenter;
model S_Frontier
  parameter
  BaseClasses.Records.S_DataCenter_Uniform computeBlocks(
    nCoolingBlocks=25,
    nCDUsPerCoolingBlock=1,
    nCabinetsPerCoolingBlock=3,
    nShelvesPerCabinet=4,
    nChassisPerShelf=2,
    nRectifiersPerChassis=1,
    nBladesPerChassis=8,
    nNodesPerBlade=2,
    nCPUsPerNode=1,
    nGPUsPerNode=4)
    annotation (Placement(transformation(extent={{20,-10},{40,10}})));
  parameter
  BaseClasses.Records.S_DataCenter_Uniform adminBlocks
    annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
  annotation (defaultComponentName="structure");
end S_Frontier;
