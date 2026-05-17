within ORNLSupercomputing.Systems.Datacenter.Tests;
model Test_steady
  "steady state test for a datacenter with 2 compute blocks and {2,3} cabinets"
  //   extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across(
  //       redeclare Models.v0 simulator(
  //         structure(computeBlock(each n=structure.computeBlock.nCoolingBlocks)),
  //         computeBlock(
  //           structure(cabinet(each n=structure.computeBlock.nCabinetsPerCoolingBlock)),
  //           cabinet(sources(each Q_flow_total=if time < 1000 then 1e4 else 5e4)))));

  //   extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across_mT_pT(n=2,
  //       redeclare Models.v0 simulator(
  //         structure(computeBlock(n={2,3})),
  //         computeBlock(
  //           structure(cabinet(n={{2,3},{2,2,3}})),
  //           cabinet(sources(each Q_flow_total=if time < 1000 then 1e4 else 5e4)))));

  extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across_mT_pT(n
      =2, redeclare Models.v0 simulator(structure(computeBlock(n={2,3})),
        redeclare Systems.CoolingBlock.Models.v0 computeBlock(
        structure(cabinet(n={{2,3},{2,2,3}})),
        cabinet(sources(Q_flow_total={{{if time < 1000 then 1e4 else 5e4,if
                time < 1000 then 1e4 else 5e4},{if time < 1000 then 1e4 else
                1e4,if time < 1000 then 1e4 else 5e4,if time < 1000 then 1e4
                 else 5e4}},{{if time < 1000 then 1e4 else 5e4,if time < 1000
                 then 1e4 else 1e4},{if time < 1000 then 1e4 else 1e4,if time
                 < 1000 then 1e4 else 5e4},{if time < 1000 then 1e4 else 1e2,
                if time < 1000 then 1e4 else 5e4,if time < 1000 then 1e4 else
                1e2}}})),
        redeclare Systems.CoolingBlock.Systems.CDU.Models.v0 cdu)));

  //   extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across(
  //       redeclare Models.v0 simulator(structure={
  //           ORNLSupercomputing.Systems.Datacenter.BaseClasses.Structure(
  //           computeBlock=TemplatesCSM.BaseClasses.Structure(n=structure.computeBlock.nCoolingBlocks))
  //           for i in 1:n}, computeBlock(structure={{
  //             ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.BaseClasses.Structure(
  //             cdu=TemplatesCSM.BaseClasses.Structure(),
  //             cabinet=TemplatesCSM.BaseClasses.Structure(n=structure.computeBlock.nCabinetsPerCoolingBlock))
  //             for i in 1:structure.computeBlocks.nCoolingBlocks} for j in 1:n},
  //           cabinet(sources(Q_flow_total=if time < 1000 then 1e4 else 5e4)))));

  ORNLSupercomputing.Tests.Records.Datacenter.S_Frontier structure
    annotation (Placement(transformation(extent={{-140,80},{-120,100}})));
  annotation (experiment(
      StopTime=86400,
      __Dymola_NumberOfIntervals=1000,
      __Dymola_Algorithm="Sdirk34hw"));
end Test_steady;
