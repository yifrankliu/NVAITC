within ORNLSupercomputing.Systems.CentralEnergyPlant.Tests;
model Test_steady
  extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across_mT_pT(
      redeclare Models.v0 simulator(redeclare Systems.HotWaterLoop.Models.v0
        hotWaterLoop, redeclare Systems.CoolingTowerLoop.Models.v0
        coolingTowerLoop));
  annotation (experiment(StopTime=86400, __Dymola_Algorithm="Sdirk34hw"));
end Test_steady;
