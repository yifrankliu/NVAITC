within TemplatesCSM.Icons;
expandable connector SignalBus
  annotation (
    defaultComponentName="signalBus",
    Icon(coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,100}},
        initialScale=0.2), graphics={
        Rectangle(
          lineColor={255,204,51},
          lineThickness=0.5,
          pattern=LinePattern.Dash,
          extent={{-20.0,-2.0},{20.0,2.0}}),
        Ellipse(
          extent={{80,80},{-80,-80}},
          lineColor={0,0,0},
          fillColor={255,204,51},
          fillPattern=FillPattern.Solid),
        Ellipse(fillPattern=FillPattern.Solid, extent={{-5,-5},{5,5}}),
        Ellipse(fillPattern=FillPattern.Solid, extent={{-41,-45},{-31,-35}}),
        Ellipse(fillPattern=FillPattern.Solid, extent={{31,-45},{41,-35}}),
        Ellipse(fillPattern=FillPattern.Solid, extent={{-41,35},{-31,45}}),
        Ellipse(fillPattern=FillPattern.Solid, extent={{31,35},{41,45}})}),
    Diagram(coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,100}},
        initialScale=0.2), graphics={
        Ellipse(
          extent={{40,40},{-40,-40}},
          lineColor={0,0,0},
          fillColor={255,204,51},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{15.5,-17.5},{20.5,-22.5}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{-2.5,2.5},{2.5,-2.5}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{-20.5,-17.5},{-15.5,-22.5}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{-20.5,22.5},{-15.5,17.5}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{15.5,22.5},{20.5,17.5}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid)}),
    Documentation(info="<html>
This icon is designed for a <b>signal bus</b> connector.
</html>"));
end SignalBus;
