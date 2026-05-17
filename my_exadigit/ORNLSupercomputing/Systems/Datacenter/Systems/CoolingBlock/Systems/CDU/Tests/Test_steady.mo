within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.CDU.Tests;
model Test_steady "steady state test of a CDU"
  extends
    TemplatesCSM.BaseClasses.Tests.PartialTest_FourPort_across_mT_pT_mT_pT(
    n=1,
      redeclare replaceable Models.v0 simulator constrainedby
      BaseClasses.BaseClasses_A.PartialModel_A,
    boundary_inlet_1(m_flow=5, T=293.65),
    boundary_outlet_1(T=308.15),
    boundary_inlet_2(m_flow=8, T=308.15),
    boundary_outlet_2(T=301.15),
    plenum_inlet_2(T_start=boundary_inlet_2.T, redeclare model Geometry =
          TRANSFORM.Fluid.ClosureRelations.Geometry.Models.LumpedVolume.GenericVolume
          (V=0.1)),
    plenum_inlet_1(T_start=boundary_inlet_1.T));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    experiment(StopTime=86400, __Dymola_Algorithm="Sdirk34hw"));
end Test_steady;
