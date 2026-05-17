within TemplatesCSM.Icons;
expandable connector ControlBus
  annotation (
    defaultComponentName="signalSubBus",
    Icon(coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,100}},
        initialScale=0.2), graphics={
        Rectangle(
          lineColor={255,215,136},
          lineThickness=0.5,
          pattern=LinePattern.Dash,
          extent={{-20.0,-2.0},{20.0,2.0}}),
        Ellipse(
          extent={{80,80},{-80,-80}},
          lineColor={0,0,0},
          fillColor={255,215,136},
          fillPattern=FillPattern.Solid),
        Ellipse(fillPattern=FillPattern.Solid, extent={{-5,-39},{5,-29}}),
        Ellipse(fillPattern=FillPattern.Solid, extent={{23,27},{33,37}}),
        Ellipse(fillPattern=FillPattern.Solid, extent={{-33,27},{-23,37}})}),
    Diagram(coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,100}},
        initialScale=0.2), graphics={
        Ellipse(
          extent={{40,40},{-40,-40}},
          lineColor={0,0,0},
          fillColor={255,215,136},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{11.5,16.5},{16.5,11.5}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{-2.5,-11.5},{2.5,-16.5}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid),
        Ellipse(
          extent={{-16.5,16.5},{-12,12}},
          lineColor={0,0,0},
          fillColor={0,0,0},
          fillPattern=FillPattern.Solid)}),
    Documentation(info="<html>
This icon is designed for a <b>signal bus</b> connector.
</html>"));
end ControlBus;
