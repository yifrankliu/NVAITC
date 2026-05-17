within ORNLSupercomputing.Systems.Datacenter.Controls;
model CS_NULL
  extends
    ORNLSupercomputing.Systems.Datacenter.BaseClasses.PartialControls(
     redeclare Data.NULL data);
  extends TemplatesCSM.Icons.NULL;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end CS_NULL;
