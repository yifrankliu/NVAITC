within ORNLSupercomputing.Components.Icons;
partial model CDU

 annotation (defaultComponentName="CDU_Loop",
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Icon(                                      graphics={Bitmap(extent={{-100,-100},{100,100}}, fileName
            = "modelica://TRANSFORM/Resources/Images/Icons/subSystem.jpg"),
            Bitmap(extent={{-60,-60},{60,80}}, fileName=
              "modelica://ORNLSupercomputing/Resources/Images/CDU_Frontier.png"),
              Text(
          extent={{-90,-80},{90,-90}},
          lineColor={0,0,0},
          lineThickness=1,
          fillColor={255,255,237},
          fillPattern=FillPattern.Solid,
          textString="CDU")}));
end CDU;
