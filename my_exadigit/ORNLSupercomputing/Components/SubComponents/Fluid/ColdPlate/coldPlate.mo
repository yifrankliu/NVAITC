within ORNLSupercomputing.Components.SubComponents.Fluid.ColdPlate;
model coldPlate "Simple cold plate model - Work in progress"
  extends Icons.ColdPlate;
  import Modelica.Fluid.Types.Dynamics;
  import TRANSFORM.Math.linspace_2Dedge;
  import TRANSFORM.Math.linspaceRepeat_2Dedge;
  outer TRANSFORM.Fluid.SystemTF systemTF;
  //extends TRANSFORM.Fluid.Pipes.ClosureModels.Geometry.PipeWithWallIcons;
  // Geometry Model
  replaceable model Geometry =
      TRANSFORM.Fluid.ClosureRelations.Geometry.Models.DistributedVolume_1D.Pipe_Wall.StraightPipe
    constrainedby
    TRANSFORM.Fluid.ClosureRelations.Geometry.Models.DistributedVolume_1D.Pipe_Wall.PartialPipeWithWall
                                                                                      "Geometry"
    annotation (Dialog(group="Geometry"),choicesAllMatching=true);
  Geometry geometry
    annotation (Placement(transformation(extent={{-78,82},{-62,98}})));
  extends TRANSFORM.Fluid.Pipes.BaseClasses.GenericPipe_Record_multiSurface(
      final nV=pipe.geometry.nV, use_HeatTransfer=true);
  input Modelica.Units.SI.Acceleration g_n=Modelica.Constants.g_n
    "Gravitational acceleration"
    annotation (Dialog(tab="Advanced", group="Inputs"));
  replaceable package Material =
      TRANSFORM.Media.Solids.SS316                     constrainedby
    TRANSFORM.Media.Interfaces.Solids.PartialAlloy
    "Wall material properties" annotation (choicesAllMatching=true);
  parameter Boolean counterCurrent=false "Swap wall vector order";
  parameter Boolean use_HeatTransferOuter=false "= true to use outer wall heat port" annotation (Dialog(group="Heat Transfer"));
  final parameter Integer nVs[2](min=1) = {geometry.nR,geometry.nZ}
    "Number of discrete volumes";
  // Initialization: Wall
  parameter Dynamics energyDynamics_wall=Dynamics.DynamicFreeInitial
    "Formulation of energy balances"
    annotation (Dialog(tab="Initialization: Wall", group="Dynamics"));
  parameter Modelica.Units.SI.Temperature Ts_start_wall[nVs[1],nVs[2]]=
      linspace_2Dedge(
      T_a1_start,
      T_b1_start,
      T_a2_start,
      T_b2_start,
      nVs[1],
      nVs[2],
      {exposeState_outerWall,exposeState_a,true,exposeState_b}) "Temperature"
    annotation (Dialog(tab="Initialization: Wall", group="Start Value: Temperature"));
  parameter Modelica.Units.SI.Temperature T_a1_start=Material.T_reference
    "Temperature at port a1" annotation (Dialog(tab="Initialization: Wall",
        group="Start Value: Temperature"));
  parameter Modelica.Units.SI.Temperature T_b1_start=T_a1_start
    "Temperature at port b1" annotation (Dialog(tab="Initialization: Wall",
        group="Start Value: Temperature"));
  parameter Modelica.Units.SI.Temperature T_a2_start=Material.T_reference
    "Temperature at port a2" annotation (Dialog(tab="Initialization: Wall",
        group="Start Value: Temperature"));
  parameter Modelica.Units.SI.Temperature T_b2_start=T_a2_start
    "Temperature at port b2" annotation (Dialog(tab="Initialization: Wall",
        group="Start Value: Temperature"));
  // Advanced
  parameter Boolean exposeState_outerWall=false
    "=true, T is calculated at outer wall else Q_flow" annotation (Dialog(group=
         "Model Structure", tab="Advanced"));
  replaceable model InternalHeatModel_wall =
      TRANSFORM.HeatAndMassTransfer.DiscritizedModels.BaseClasses.Dimensions_2.GenericHeatGeneration
    constrainedby
    TRANSFORM.HeatAndMassTransfer.DiscritizedModels.BaseClasses.Dimensions_2.PartialInternalHeatGeneration
    "Internal heat generation" annotation (Dialog(group="Heat Transfer"),
      choicesAllMatching=true);
  TRANSFORM.Fluid.Pipes.GenericPipe_MultiTransferSurface pipe(
    nParallel=nParallel,
    redeclare package Medium = Medium,
    redeclare model FlowModel = FlowModel,
    use_HeatTransfer=true,
    redeclare model HeatTransfer = HeatTransfer,
    redeclare model InternalHeatGen = InternalHeatGen,
    energyDynamics=energyDynamics,
    massDynamics=massDynamics,
    traceDynamics=traceDynamics,
    ps_start=ps_start,
    use_Ts_start=use_Ts_start,
    Ts_start=Ts_start,
    hs_start=hs_start,
    Xs_start=Xs_start,
    Cs_start=Cs_start,
    p_a_start=p_a_start,
    p_b_start=p_b_start,
    T_a_start=T_a_start,
    T_b_start=T_b_start,
    h_a_start=h_a_start,
    h_b_start=h_b_start,
    X_a_start=X_a_start,
    X_b_start=X_b_start,
    C_a_start=C_a_start,
    C_b_start=C_b_start,
    m_flow_a_start=m_flow_a_start,
    m_flow_b_start=m_flow_b_start,
    m_flows_start=m_flows_start,
    momentumDynamics=momentumDynamics,
    exposeState_a=exposeState_a,
    exposeState_b=exposeState_b,
    g_n=g_n,
    useInnerPortProperties=useInnerPortProperties,
    useLumpedPressure=useLumpedPressure,
    lumpPressureAt=lumpPressureAt,
    redeclare model Geometry = Geometry,
    calc_Wb=calc_Wb)
    annotation (Placement(transformation(extent={{-10,-90},{10,-70}})));
  TRANSFORM.HeatAndMassTransfer.DiscritizedModels.Conduction_2D wall(
    redeclare package Material = Material,
    nParallel=nParallel,
    redeclare model InternalHeatModel = InternalHeatModel_wall,
    energyDynamics=energyDynamics_wall,
    Ts_start=Ts_start_wall,
    T_a1_start=T_a1_start,
    T_b1_start=T_b1_start,
    T_a2_start=T_a2_start,
    T_b2_start=T_b2_start,
    redeclare model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.DistributedVolume_1D.ShellSide_STHX
        (r_outer=wall.geometry.r_inner + sum(geometry.ths_wall)/geometry.nV,
          length_z=sum(geometry.dlengths)),
    exposeState_b1=exposeState_outerWall,
    exposeState_a2=exposeState_a,
    exposeState_b2=exposeState_b,
    exposeState_a1=if pipe.heatTransfer.flagIdeal == 1 then false else true)
    annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=90,
        origin={0,-20})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_a(redeclare package Medium =
        Medium) annotation (Placement(transformation(extent={{-110,-10},{-90,10}}),
        iconTransformation(extent={{-110,-10},{-90,10}})));
  TRANSFORM.Fluid.Interfaces.FluidPort_Flow port_b(redeclare package Medium =
        Medium) annotation (Placement(transformation(extent={{90,-10},{110,10}}),
        iconTransformation(extent={{90,-10},{110,10}})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Adiabatic adiabatic_a[geometry.nR]
    annotation (Placement(transformation(extent={{-60,-44},{-40,-24}})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Adiabatic adiabatic_b[geometry.nR]
    annotation (Placement(transformation(extent={{60,-44},{40,-24}})));
  TRANSFORM.HeatAndMassTransfer.Interfaces.HeatPort_Flow heatPorts[geometry.nZ]
   annotation (Placement(transformation(extent={{-10,34},
            {10,54}}), iconTransformation(extent={{-10,40},{10,60}})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Adiabatic adiabatic_inner[geometry.nZ]
    if not use_HeatTransfer
    annotation (Placement(transformation(extent={{60,-62},{40,-42}})));
  // Visualization
  parameter Boolean showName = true annotation(Dialog(tab="Visualization"));
  parameter Boolean showDesignFlowDirection = true annotation(Dialog(tab="Visualization"));
  extends TRANSFORM.Utilities.Visualizers.IconColorMap(showColors=systemTF.showColors, val_min=systemTF.val_min,val_max=systemTF.val_max, val=pipe.summary.T_effective);
  TRANSFORM.HeatAndMassTransfer.Interfaces.HeatPort_Flow heatPorts_add[geometry.nZ,
    geometry.nSurfaces - 1] if geometry.nSurfaces > 1 annotation (Placement(
        transformation(extent={{20,-80},{40,-60}}), iconTransformation(extent={{
            20,-10},{40,10}})));
equation
  connect(port_a, pipe.port_a) annotation (Line(
      points={{-100,0},{-60,0},{-60,-80},{-10,-80}},
      color={0,127,255},
      thickness));
  connect(port_b, pipe.port_b) annotation (Line(
      points={{100,0},{60,0},{60,-80},{10,-80}},
      color={0,127,255},
      thickness));
  connect(wall.port_a1, pipe.heatPorts[:,1]) annotation (Line(
      points={{0,-30},{0,-75}},
      color={191,0,0},
      thickness));
  connect(wall.port_a2, adiabatic_a.port) annotation (Line(
      points={{-10,-20},{-20,-20},{-20,-34},{-40,-34}},
      color={191,0,0},
      thickness));
  connect(adiabatic_b.port, wall.port_b2) annotation (Line(
      points={{40,-34},{20,-34},{20,-20},{10,-20}},
      color={191,0,0},
      thickness));
  connect(adiabatic_inner.port, wall.port_a1) annotation (Line(
      points={{40,-52},{0,-52},{0,-30}},
      color={191,0,0},
      thickness));
  connect(heatPorts_add, pipe.heatPorts[:,2:geometry.nSurfaces])
    annotation (Line(points={{30,-70},{0,-70},{0,-75}}, color={191,0,0}));
  connect(wall.port_b1, heatPorts) annotation (Line(points={{6.10623e-16,-10},{6.10623e-16,
          17},{0,17},{0,44}}, color={191,0,0}));
  annotation (defaultComponentName="coldPlate",
  Icon(coordinateSystem(preserveAspectRatio=false),Diagram(
        coordinateSystem(preserveAspectRatio=false))));
end coldPlate;
