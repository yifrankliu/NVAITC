within ORNLSupercomputing.Tests;
model Test_steady_2dcs
  "test steady state model for an assumed 2 datacenter model"
  //   extends TemplatesCSM.BaseClasses.Tests.PartialTest(n=1,
  //       redeclare Models.v0 simulator(
  //         structure(datacenter(n={2})),
  //         datacenter(
  //           structure(computeBlock(n={{2,3}})),
  //           computeBlock(
  //             structure(cabinet(n={{{2,3},{2,2,3}}})),
  //             cabinet(sources(each Q_flow_total=if time < 1000 then 1e3 else 1e4))))));

//   extends TemplatesCSM.BaseClasses.Tests.PartialTest(n=1, redeclare
//       Models.v0 simulator(structure(datacenter(n={2})), datacenter(structure(
//             computeBlock(n={{2,3}})), computeBlock(structure(cabinet(n={{{2,3},{
//                   2,2,3}}})), cabinet(sources(Q_flow_total={{{{if time < 1000
//                    then 1e3 else 1e3,if time < 1000 then 1e3 else 1e4},{if time <
//                   1000 then 1e3 else 1e4,if time < 1000 then 1e3 else 1e4,if
//                   time < 1000 then 1e3 else 1e4}},{{if time < 1000 then 1e3
//                    else 1e3,if time < 1000 then 1e2 else 1e4},{if time < 1000
//                    then 1e3 else 1e4,if time < 1000 then 1e3 else 1e4},{if time <
//                   1000 then 1e3 else 1e4,if time < 1000 then 1e3 else 1e4,if
//                   time < 1000 then 1e3 else 1e4}}}}))))));

  extends TemplatesCSM.BaseClasses.Tests.PartialTest(n=1, redeclare
      Models.v1 simulator(
      structure(datacenter(each n=1)),
      redeclare Systems.Datacenter.Models.v0 datacenter_1(structure(
            computeBlock(each n=25)), redeclare
          Systems.Datacenter.Systems.CoolingBlock.Models.v0 computeBlock(
          structure(cabinet(each n=3)),
          redeclare
            Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Models.v0 cdu,
          redeclare
            Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Models.v0
            cabinet(sources(each Q_flow_total=if time < 1000 then 1e5 else 1e4)))),
      datacenter(structure(computeBlock(each n=25)), redeclare
          Systems.Datacenter.Systems.CoolingBlock.Models.v0 computeBlock(
          structure(cabinet(each n=3)),
          redeclare
            Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Models.v0 cdu,
          redeclare
            Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Models.v0
            cabinet(sources(each Q_flow_total=if time < 1000 then 1e4 else 1e5)))),
      redeclare Systems.CentralEnergyPlant.Models.v0 centralEnergyPlant));

protected
  BaseClasses.ControlBus controlBus
    annotation (Placement(transformation(extent={{-20,20},{20,60}})));
equation
  connect(simulator[1].controlBus, controlBus) annotation (Line(
      points={{0,10},{0,40}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (experiment(StopTime=36000, __Dymola_Algorithm="Sdirk34hw"));
end Test_steady_2dcs;
