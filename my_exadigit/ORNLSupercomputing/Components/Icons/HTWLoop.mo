within ORNLSupercomputing.Components.Icons;
partial model HTWLoop

 annotation (defaultComponentName="HTW_Loop",
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    Icon(                                      graphics={Bitmap(extent={{-100,-100},{100,100}}, fileName
            = "modelica://TRANSFORM/Resources/Images/Icons/subSystem.jpg"),
            Bitmap(extent={{-80,-80},{80,80}}, fileName=
              "modelica://ORNLSupercomputing/Resources/Images/HTW_Loop_Frontier.png"),
              Text(
          extent={{-90,-60},{90,-85}},
          lineColor={0,0,0},
          lineThickness=1,
          fillColor={255,255,237},
          fillPattern=FillPattern.Solid,
          textString="HTW Loop")}));
end HTWLoop;
