within GenericDatacenter.Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Tests;
model Test_steady

  extends TemplatesCSM.BaseClasses.Tests.PartialTest_TwoPort_across_mT_pT
                                                                       (
    n=27,
    redeclare Models.v0 simulator(
                            each sources(Q_flow_total=if time < 1000 then 1e3
             else 1e4)),
    boundary_inlet(use_m_flow_in=false));

  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
end Test_steady;
