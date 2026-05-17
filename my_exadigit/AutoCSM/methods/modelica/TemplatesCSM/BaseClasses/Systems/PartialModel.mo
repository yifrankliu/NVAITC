within TemplatesCSM.BaseClasses.Systems;
partial model PartialModel
  extends Icons.Model;

  replaceable PartialSummary summary annotation (Placement(transformation(
          extent={{-70,120},{-50,140}})), Dialog(group="External", enable=false));
  replaceable parameter PartialData data annotation (
    Placement(transformation(extent={{50,120},{70,140}})),
    choicesAllMatching=true,
    Dialog(group="Internal"));
  replaceable PartialControlBus controlBus annotation (
    Placement(transformation(extent={{-10,90},{10,110}}), iconTransformation(
          extent={{-10,90},{10,110}})),
    choicesAllMatching=true,
    Dialog(group="Internal"));
  replaceable parameter PartialStructure structure
    annotation (Placement(transformation(extent={{-110,120},{-90,140}})));
  replaceable PartialControls controls constrainedby PartialControls annotation (
    Placement(transformation(extent={{10,120},{30,140}})),
    choicesAllMatching=true,
    Dialog(group="Internal"));
  replaceable PartialSources sources constrainedby PartialSources annotation (
    Placement(transformation(extent={{-30,120},{-10,140}})),
    choicesAllMatching=true,
    Dialog(group="External", enable=false));

equation
  connect(controls.controlBus, controlBus) annotation (Line(
      points={{20,120},{20,110},{0,110},{0,100}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  connect(sources.controlBus, controlBus) annotation (Line(
      points={{-20,120},{-20,110},{0,110},{0,100}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));
  annotation (Icon(graphics={Text(
          extent={{-100,20},{100,-20}},
          textColor={0,0,0},
          textString="%name")}), Diagram(coordinateSystem(preserveAspectRatio=false,
          extent={{-180,-100},{180,140}})));
end PartialModel;
