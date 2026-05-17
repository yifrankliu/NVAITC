# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.

For Dymola Python API information see: PATHTO/Dymola VERSION/Modelica/Library/python_interface/doc

"""

import pathlib
import os
from dymola.dymola_interface import DymolaInterface
import parse_files
import copy

def insert_selected_solver(model_path, experimentSettings):
    '''
    solver options: 
        Sdirk34hw
        Esdirk45a
        Dassl
        etc... see Dymola
    '''
    
    experimentSettings_default = {'__Dymola_Algorithm':'Dassl',
                          'Tolerance':1e-4}
    
    experimentSettings_current = copy.deepcopy(experimentSettings_default)
    for key, val in experimentSettings.items():
        if key.lower() == 'solver':
            experimentSettings_current['__Dymola_Algorithm'] = val
        elif key.lower() == 'tolerance': 
            experimentSettings_current['Tolerance'] = val
        else:
            experimentSettings_current[key] = val
        
    filename = os.path.splitext(os.path.basename(model_path))[0]
    end_pattern = f"end {filename};"
    experiment_string = ','.join([f'{key}="{val}"' if isinstance(val, str) else f'{key}={val}' for key, val in experimentSettings_current.items()])
    annotation_line = f'annotation(experiment({experiment_string}));'
    
    # Read the file
    with open(model_path, 'r') as file:
        lines = file.readlines()
        
    # Check if the end_pattern is in the last line
    if lines and lines[-1].strip() == end_pattern:
        # Check if the annotation is already present
        if lines[-2].strip() == annotation_line:
            # Remove the annotation line
            lines.pop(-2)
        else:
            # Insert the annotation line before the end_pattern
            lines.insert(-1, annotation_line + '\n')
        
        # Write the modified lines back to the file
        with open(model_path, 'w') as file:
            file.writelines(lines)
    else:
        print(f'The pattern "{end_pattern}" not found at the end of {model_path}. Solver not added.')
        
def main(package_list, model_path, output_path, experimentSettings={}, showwindow=False, includeVariables=None):
        
    # Add solver to model file
    insert_selected_solver(model_path, experimentSettings)
       
    # Start Dymola
    dymola = DymolaInterface(showwindow=showwindow)

    # Load dependencies
    for pkg in package_list:
        dymola.openModel(pkg, changeDirectory=False)

    # Load model
    dymola.openModel(model_path, changeDirectory=False)

    # Translate to FMU
    dymola.cd(str(output_path))
    
    commands = ['Advanced.EnableCodeExport = true;',
                'Advanced.GenerateAnalyticJacobian = false;'
                'Advanced.Translation.SparseActivate = true;',
                'Advanced.Translation.SparseActivateIntegrator = true;',
                'Advanced.Translation.SparseActivateSystems = true;',
                'Advanced.Define.GlobalOptimizations = 2;',
                'Advanced.Translation.ODEJacobianForDiscrete = true;',
                'Advanced.FMI.CrossExport = true;']
                # 'Advanced.Translation.SparseMaximumDensity = 25;',
                # 'Advanced.Translation.SparseMinimumStates = 50;',
                # 'Advanced.NumberOfCores = 12;'
    for command in commands:
        dymola.ExecuteCommand(command)
    
    dymola.translateModelFMU(modelToOpen=pathlib.Path(model_path).stem,
                             fmiVersion = '2',
                             fmiType='csSolver',
                             includeVariables=includeVariables)
    
    log_file_path = os.path.join(output_path,'fmu_log.txt')
    dymola.savelog(log_file_path)
    # Verify no error in log file
    parse_files.search_log_file_reverse(log_file_path, 'Error:')

    if not dymola==None:
        dymola.close()
        dymola = None

if __name__ == "__main__":
    # Dependencies
    package_list = [r'../../../methods/modelica/TemplatesCSM/package.mo',
         		    r'../../../../../Modelica/modelica-buildings/Buildings/package.mo',
         		    r'../../../../../Modelica/TRANSFORM-Library/TRANSFORM/package.mo',
                    r'../../../examples/modelica/GenericDatacenter/package.mo']
    
    # Path to the pregenerated Simulator.mo file. This must exist.
    model_path = os.path.abspath('../../../temp/Simulator.mo')
    
    if not os.path.exists(model_path):
        raise ValueError(f'The Simulator.mo file must exist before this is run. For example, run modelica_create_model_nested.py and then this file.\n File path searched was: {model_path}')
    
    output_path = pathlib.Path(model_path).parent
    
    main(package_list, model_path, output_path, showwindow=True)



