within TemplatesCSM.Templates.TemplateSystem.Sources;
model v0
  extends BaseClasses.PartialSources(redeclare replaceable Data.v0 data);

  input Real u=0.0 "Example input variable"
    annotation (Dialog(group="Input"));
  Modelica.Blocks.Sources.RealExpression u_int(y=
        u) annotation (Placement(transformation(
          extent={{-40,-70},{-20,-50}})));
equation

  connect(controlBus.u, u_int.y) annotation (Line(
      points={{0,-100},{0,-60},{-19,-60}},
      color={255,215,136},
      pattern=LinePattern.Dash,
      thickness=0.5));

end v0;
