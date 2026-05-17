within ORNLSupercomputing.Components.SubComponents.DataCenter.Blade.BaseClasses;
model PartialBlademodel
  extends Icons.Blade;
  extends Record_SubSystem;
  replaceable package Medium =
                   ORNLSupercomputing.Components.SubComponents.Media.Medium;
  Modelica.Blocks.Interfaces.RealInput Q_flow_ext(unit="W") annotation (
      Placement(transformation(
        rotation=270,
        extent={{-10,-10},{10,10}},
        origin={0,100})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_a(redeclare package Medium =
        Medium, m_flow(min=if allowFlowReversal then -Modelica.Constants.inf else 0)) annotation (Placement(transformation(rotation=0, extent={{-110,
            -10},{-90,10}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_State port_b(redeclare package Medium =
        Medium, m_flow(max=if allowFlowReversal then +Modelica.Constants.inf else 0)) annotation (Placement(transformation(rotation=0, extent={{90,-10},
            {110,10}})));
end PartialBlademodel;
