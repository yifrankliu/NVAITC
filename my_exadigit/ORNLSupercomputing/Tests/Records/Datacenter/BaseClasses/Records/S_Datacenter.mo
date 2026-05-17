within ORNLSupercomputing.Tests.Records.Datacenter.BaseClasses.Records;
record S_Datacenter
  extends PartialStructure;

  final parameter Integer nComputeBlocks=3;
  //size(computeBlock, 1);
  parameter S_CoolingBlock computeBlock[3];

  //   final parameter Integer nAdminBlocks=2;//size(adminBlock,1);
  //   parameter RecordCoolingBlock[2] adminBlock;

  annotation (defaultComponentName="structure");
end S_Datacenter;
