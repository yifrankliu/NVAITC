within ORNLSupercomputing.Tests;
model Test_dynamic_2dcs "test dynamic model for an assumed 2 datacenter model"

  extends Test_steady_2dcs(simulator(
      redeclare Systems.CentralEnergyPlant.Models.v0 centralEnergyPlant(
          redeclare
          Systems.CentralEnergyPlant.Systems.CoolingTowerLoop.Models.v0
          coolingTowerLoop(sources(Towb=data_external.y[2] + 273.15)),
          redeclare Systems.CentralEnergyPlant.Systems.HotWaterLoop.Models.v0
          hotWaterLoop),
      redeclare Systems.Datacenter.Models.v0 datacenter(redeclare
          Systems.Datacenter.Systems.CoolingBlock.Models.v0 computeBlock(
          redeclare
            Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Models.v0 cdu,
          redeclare
            Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Models.v0
            cabinet(sources(Q_flow_total=data_external.y[1]/(system_structure.computeBlock.nCoolingBlocks
                  *system_structure.computeBlock.nCabinetsPerCoolingBlock))),
          structure)),
      redeclare Systems.Datacenter.Models.v0 datacenter_1(redeclare
          Systems.Datacenter.Systems.CoolingBlock.Models.v0 computeBlock(
            redeclare
            Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Models.v0 cdu,
            cabinet(sources(Q_flow_total=data_external.y[1]/(system_structure.computeBlock.nCoolingBlocks
                  *system_structure.computeBlock.nCabinetsPerCoolingBlock)))))));
  Modelica.Blocks.Sources.CombiTimeTable data_external(
    tableOnFile=true,
    tableName="table",
    fileName=Modelica.Utilities.Files.loadResource(
        "modelica://ORNLSupercomputing/../python/data/input_04-07-24_comb.txt"),
    columns={2,3},
    extrapolation=Modelica.Blocks.Types.Extrapolation.HoldLastPoint)
    annotation (Placement(transformation(extent={{-60,20},{-40,40}})));
  annotation (experiment(
      StopTime=86400,
      __Dymola_NumberOfIntervals=2000,
      __Dymola_Algorithm="Sdirk34hw"));
end Test_dynamic_2dcs;
