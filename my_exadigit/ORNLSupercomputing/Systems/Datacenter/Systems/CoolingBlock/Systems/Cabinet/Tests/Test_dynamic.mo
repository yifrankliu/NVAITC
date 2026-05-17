within ORNLSupercomputing.Systems.Datacenter.Systems.CoolingBlock.Systems.Cabinet.Tests;
model Test_dynamic "dynamic test of the cabinet model with 27 cabinets"
  extends Test_steady(
  n=27,
    redeclare replaceable Models.v0 simulator(data(ccVolCabinet={(0.6 - 0.3)/(n - 1)*(i - 1)
             + 0.3 for i in 1:n}, R_Cab={(5500 - 11000)/(n - 1)*(i - 1) + 11000
            for i in 1:n}), each sources(Q_flow_total=data_external.y[1]
                /750)) constrainedby
      BaseClasses.BaseClasses_A.PartialModel_A,
    boundary_inlet(use_m_flow_in=false, use_T_in=false),
    boundary_outlet(
      use_p_in=false,
      use_T_in=false,
      p=550000,
      T=308.15));
  Modelica.Blocks.Sources.CombiTimeTable data_external(
    tableOnFile=true,
    tableName="table",
    fileName=Modelica.Utilities.Files.loadResource("modelica://ORNLSupercomputing/../python/data/input_synthetic_data_comb.txt"),
    columns={2,3},
    extrapolation=Modelica.Blocks.Types.Extrapolation.HoldLastPoint)
    annotation (Placement(transformation(extent={{-10,26},{10,46}})));

  annotation (experiment(StopTime=2000, __Dymola_Algorithm="Sdirk34hw"));
end Test_dynamic;
