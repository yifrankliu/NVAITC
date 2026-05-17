within ORNLSupercomputing.Components.SubComponents.DataCenter.Blade.BaseClasses;
model CPU_3D
  extends Icons.CPU;
  extends chip_3D;
   annotation (
      experiment(StopTime=10500, __Dymola_Algorithm="Dassl"));
end CPU_3D;
