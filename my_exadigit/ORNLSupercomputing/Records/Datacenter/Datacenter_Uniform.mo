within ORNLSupercomputing.Records.Datacenter;
model Datacenter_Uniform

  parameter
    ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_DataCenter_Uniform
    computeBlocks;
  parameter
    ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_DataCenter_Uniform
    adminBlocks;

  //   parameter Integer nCoolingBlocks=1 annotation (Dialog(tab="Geometry"));
  //   parameter Integer nCDUsPerCoolingBlock=1
  //     annotation (Dialog(tab="Geometry", enable=false));
  //   parameter Integer nCabinetsPerCoolingBlock=1
  //     annotation (Dialog(tab="Geometry"));
  //   parameter Integer nShelvesPerCabinet=1 annotation (Dialog(tab="Geometry"));
  //   parameter Integer nChassisPerShelf=1 annotation (Dialog(tab="Geometry"));
  //   parameter Integer nRectifiersPerChassis=1
  //     annotation (Dialog(tab="Geometry", enable=false));
  //   parameter Integer nBladesPerChassis=1 annotation (Dialog(tab="Geometry"));
  //   parameter Integer nNodesPerBlade=1 annotation (Dialog(tab="Geometry"));
  //   parameter Integer nCPUsPerNode=1 annotation (Dialog(tab="Geometry"));
  //   parameter Integer nGPUsPerNode=1 annotation (Dialog(tab="Geometry"));

  extends ORNLSupercomputing.Records.Datacenter.Structure_Generic
                                                               (data(
        computeBlock={
          ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_CoolingBlock(
          nCDUs=computeBlocks.nCDUsPerCoolingBlock,
          cabinet={
            ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Cabinet(
            shelf={
              ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Shelf(
              chassis={
                ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Chassis(
                nRectifiers=computeBlocks.nRectifiersPerChassis,
                blade={
                  ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Blade(
                  node={
                    ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Node(
                    nCPUs=computeBlocks.nCPUsPerNode,
                    nGPUs=computeBlocks.nGPUsPerNode) for nn in 1:computeBlocks.nNodesPerBlade})
                  for mm in 1:computeBlocks.nBladesPerChassis}) for ll in 1:
                computeBlocks.nChassisPerShelf}) for kk in 1:computeBlocks.nShelvesPerCabinet})
            for jj in 1:nCabinetsPerCoolingBlock}) for ii in 1:computeBlocks.nCoolingBlocks},
        adminBlock={
          ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_CoolingBlock(
          nCDUs=adminBlocks.nCDUsPerCoolingBlock,
          cabinet={
            ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Cabinet(
            shelf={
              ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Shelf(
              chassis={
                ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Chassis(
                nRectifiers=adminBlocks.nRectifiersPerChassis,
                blade={
                  ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Blade(
                  node={
                    ORNLSupercomputing.Records.Datacenter.BaseClasses.Records.S_Node(
                    nCPUs=adminBlocks.nCPUsPerNode,
                    nGPUs=adminBlocks.nGPUsPerNode) for nn in 1:adminBlocks.nNodesPerBlade})
                  for mm in 1:adminBlocks.nBladesPerChassis}) for ll in 1:
                adminBlocks.nChassisPerShelf}) for kk in 1:adminBlocks.nShelvesPerCabinet})
            for jj in 1:nCabinetsPerCoolingBlock}) for ii in 1:adminBlocks.nCoolingBlocks}));

  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end Datacenter_Uniform;
