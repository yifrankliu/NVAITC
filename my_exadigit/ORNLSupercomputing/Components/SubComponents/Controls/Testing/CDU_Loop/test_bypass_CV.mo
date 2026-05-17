within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CDU_Loop;
model test_bypass_CV "test CDU loop (primary side) bypass valve"
  extends Modelica.Icons.Example;
  BaseClasses.bypass_CV bypass_CV_Model(
    Ti=10,
    gain=1,
    db=2,
    dbr=0.5) annotation (Placement(transformation(extent={{-24,-26},{22,20}})));
  Modelica.Blocks.Noise.UniformNoise     CDULoop_mdot(
    samplePeriod=100,
    y_min=100,
    y_max=250)
             annotation (Placement(transformation(
        extent={{-11,-10},{11,10}},
        rotation=0,
        origin={-61,-8})));
  Modelica.Blocks.Interaction.Show.RealValue
                                       CDU_CV1
    annotation (Placement(transformation(extent={{-50,6},{-78,32}})));
equation
  connect(CDULoop_mdot.y, bypass_CV_Model.mdot) annotation (Line(points={{-48.9,
          -8},{-28,-8},{-28,2.98},{-10.292,2.98}},        color={0,0,127}));
  connect(CDU_CV1.numberPort, bypass_CV_Model.bypass_CV) annotation (Line(
        points={{-47.9,19},{-28,19},{-28,2.98},{-10.292,2.98}},
        color={0,0,127}));
  annotation (experiment(StopTime=86400, __Dymola_Algorithm="Dassl"));
end test_bypass_CV;
