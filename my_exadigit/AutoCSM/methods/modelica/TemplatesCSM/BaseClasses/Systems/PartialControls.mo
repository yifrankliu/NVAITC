within TemplatesCSM.BaseClasses.Systems;
partial model PartialControls
  extends Icons.Control;
  replaceable parameter PartialData data annotation (Placement(
        transformation(extent={{50,-100},{70,-80}})), choicesAllMatching=true);
  replaceable PartialControlBus controlBus annotation (Placement(transformation(
          extent={{-20,-120},{20,-80}})), choicesAllMatching=true);
  replaceable parameter PartialStructure structure
    annotation (Placement(transformation(extent={{-70,-100},{-50,-80}})));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-180,-100},{180,
            100}})));
end PartialControls;
