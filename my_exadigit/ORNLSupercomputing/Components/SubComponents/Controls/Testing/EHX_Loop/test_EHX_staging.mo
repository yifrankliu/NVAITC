within ORNLSupercomputing.Components.SubComponents.Controls.Testing.EHX_Loop;
model test_EHX_staging
  extends Modelica.Icons.Example;
  BaseClasses.EHX_Staging EHX_Staging_model(nEHX_start=4, nCT_crit={1,4,8,12})
    annotation (Placement(transformation(extent={{-20,-26},{20,14}})));
  Modelica.Blocks.Sources.TimeTable EHX_no_data(table=[0,4; 29353,4; 29444,3;
        29529,4; 29644,3; 30184,4; 30915,4; 30935,4; 30991,4; 31056,4; 31818,3;
        86400,3])
    annotation (Placement(transformation(extent={{6,42},{24,60}})));
  Modelica.Blocks.Sources.RealExpression nCT_data(y=nCT_no_data.y)
    annotation (Placement(transformation(extent={{-56,-14},{-30,12}})));
  Modelica.Blocks.Sources.TimeTable nCT_no_data(table=[0,12; 30167,12; 30192,11;
        30202,12; 30237,13; 30253,12; 30262,13; 30273,12; 30283,13; 30308,14;
        30323,13; 30333,15; 30893,16; 30903,16; 30908,15; 30974,16; 31029,15;
        31545,14; 31610,13; 31636,12; 31791,11; 31887,10; 31922,9; 31937,8;
        65547,8; 65548,9; 66439,8; 86400,8])
    annotation (Placement(transformation(extent={{-26,42},{-8,60}})));
equation
  connect(nCT_data.y, EHX_Staging_model.nCT) annotation (Line(points={{-28.7,-1},
          {-18.39,-1},{-18.39,-0.8},{-8.08,-0.8}}, color={0,0,127}));
  annotation (experiment(StopTime=86400, __Dymola_Algorithm="Dassl"));
end test_EHX_staging;
