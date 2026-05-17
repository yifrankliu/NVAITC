within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Tests;
model Test_steady "steady state test of the cabinet model with 27 cabinets"

  extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across_mT_pT(
    n=27,
    redeclare replaceable Models.v0 simulator(data(ccVolCabinet={(0.6 - 0.3)/(n - 1)*(i - 1)
             + 0.3 for i in 1:n}, R_Cab={(5500 - 11000)/(n - 1)*(i - 1) + 11000
            for i in 1:n}), each sources(Q_flow_total=if time < 1000 then 1e3
            else 1e4)) constrainedby
      BaseClasses.BaseClasses_A.PartialModel_A,
    boundary_inlet(use_m_flow_in=false));

  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    experiment(StopTime=86400, __Dymola_Algorithm="Sdirk34hw"));
end Test_steady;
