within ORNLSupercomputing.Components.SubComponents.DataCenter.Blade.BaseClasses;
model GPU_3D "3D model of a GPU"
  extends Icons.GPU;
  extends chip_3D;
  annotation (
      experiment(StopTime=10500, __Dymola_Algorithm="Dassl"));
end GPU_3D;
