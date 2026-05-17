within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Tests;
model Test_steady
  "test steady state for a cooling block with 3 cabinets"
  extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across_mT_pT(
    n=1,
    redeclare Models.v0 simulator(cabinet(sources(Q_flow_total=if time < 1000
               then 1e3 else 1e4)), structure(cabinet(n=3))),
    boundary_outlet(p(displayUnit="Pa")));


  // Alternative valid approaches
  // Using arrays
  //   extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across(n=3,
  //       redeclare Models.v0 simulator(cabinet(sources(Q_flow_total=if time < 1000
  //                then 1e3 else 1e4)), structure(cabinet(n={2,2,3},
  //             useParallel={true,false,true}))));

  //Using structures
  //   extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across(n=27,
  //       redeclare Models.v0 simulator(cabinet(sources(Q_flow_total=if time < 1000
  //                then 1e3 else 1e4)), structure(cabinet={
  //             TemplatesCSM.BaseClasses.Structure(n=2) for i in 1:n})));

  annotation (experiment(
      StopTime=86400,
      __Dymola_NumberOfIntervals=1000,
      __Dymola_Algorithm="Sdirk34hw"), __Dymola_experimentSetupOutput);
end Test_steady;
