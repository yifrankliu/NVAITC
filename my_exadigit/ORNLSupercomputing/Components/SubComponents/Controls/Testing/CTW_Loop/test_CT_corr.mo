within ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop;
model test_CT_corr "test cooling tower vendor correlation"
  extends Modelica.Icons.Example;
  parameter Real TAirInWB=60.2 "Inlet air wet bulb temperature";
  parameter Real adj=0.92
    "User adjustable parameter (in deg. F) in the approach temperature calculation";
  Real TApp_Wat "Approach temperature";

equation
  TApp_Wat =
    ORNLSupercomputing.Components.SubComponents.Controls.Testing.CTW_Loop.BaseClasses.CT_corr(
    TWetBul=TAirInWB, adj=adj);

end test_CT_corr;
