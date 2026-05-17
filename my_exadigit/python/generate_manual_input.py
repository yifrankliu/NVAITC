# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 18:57:03 2024

@author: Scott Greenwood
"""
outputfile = 'temp/manual_input.txt'
# Manual
with open(outputfile, 'w') as fil:
    for i in range(1):
        for j in range(1):
            for k in range(25):
                for m in range(3):
                    text = 'Modelica.Blocks.Interfaces.RealInput '
                    text += f'simulator_{i+1}_datacenter_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total'
                    text += f'(start=0.0) = data_external.y[{k+1}]/3;\n\n'
                    fil.writelines(text)
                    
with open(outputfile, 'a') as fil:
    for i in range(1):
        for j in range(1):
            for k in range(5):
                for m in range(1):
                    text = 'Modelica.Blocks.Interfaces.RealInput '
                    text += f'simulator_{i+1}_datacenter_1_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total'
                    text += f'(start=0.0) = data_external.y[{k+1}]/3;\n\n'
                    fil.writelines(text)
                    
                    
#%% Using input_signals file

with open(outputfile, 'w') as fil:
    for i in range(1):
        for j in range(1):
            for k in range(1):
                    text = 'Modelica.Blocks.Interfaces.RealInput '
                    text += f'simulator_{i+1}_centralEnergyPlant_{j+1}_coolingTowerLoop_{k+1}_sources_Towb'
                    text += f'(start=298.15) = data_external.y[{k+1}];\n\n'
                    # Number is 2:25+1
                    fil.writelines(text)
                    
with open(outputfile, 'a') as fil:
    for i in range(1):
        for j in range(1):
            for k in range(25):
                for m in range(3):
                    text = 'Modelica.Blocks.Interfaces.RealInput '
                    text += f'simulator_{i+1}_datacenter_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total'
                    text += f'(start=0.0) = data_external.y[{k+1+1}];\n\n'
                    # Number is 2:25+1
                    fil.writelines(text)
                    
with open(outputfile, 'a') as fil:
    for i in range(1):
        for j in range(1):
            for k in range(155):
                for m in range(1):
                    text = 'Modelica.Blocks.Interfaces.RealInput '
                    text += f'simulator_{i+1}_datacenter_1_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total'
                    text += f'(start=0.0) = data_external.y[{k+1+25}];\n\n'
                    # Numbering is 25+1:155+1
                    fil.writelines(text)
                    
with open(outputfile, 'a') as fil:
    nCols = 1+25+155
    text = 'Modelica.Blocks.Sources.CombiTimeTable data_external(\
              tableOnFile=true,\
              tableName="table",\
              fileName=Modelica.Utilities.Files.loadResource("modelica://ORNLSupercomputing/../python/temp/input_signals.txt"),\
              columns={i + 1 for i in 1:(1+25+155)},\
              extrapolation=Modelica.Blocks.Types.Extrapolation.HoldLastPoint)\
              annotation (Placement(transformation(extent={{-74,28},{-54,48}})));'
    fil.writelines(text)    