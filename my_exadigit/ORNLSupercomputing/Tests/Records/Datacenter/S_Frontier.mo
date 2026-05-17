within ORNLSupercomputing.Tests.Records.Datacenter;
model S_Frontier
  parameter S_DataCenter_Uniform computeBlock(
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
  parameter S_DataCenter_Uniform adminBlock
    annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
  annotation (defaultComponentName="system_structure");
end S_Frontier;
