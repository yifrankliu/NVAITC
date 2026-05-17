# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:31:03 2024

@author: Scott Greenwood
"""

import os
import sys
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_path,r'../../AutoCSM/AutoCSM'))
from auto_csm import AutoCSM

if __name__ == "__main__":
    # JSON file path
    json_file_path = 'data/input_specification_frontier_test.json'
    
    # Output Modelica file
    output_path = 'temp'

    # Path to project
    project_path = os.path.join(base_path,r"../ORNLSupercomputing/package.mo")
    
    # Model dependecies
    dependencies = [os.path.join(base_path,r"../../../../Modelica/TRANSFORM-Library/TRANSFORM/package.mo"),
          		    os.path.join(base_path,r"../../../../Modelica/modelica-buildings/Buildings/package.mo")]
    
    #%%
    # Instantiate AutoCSM
    csm = AutoCSM(language='modelica', architecture='nested')
    
    # You can turn off terminal animation if desired
    csm.terminal_animation = False
    
    # Load the JSON specification
    csm.input_specification = json_file_path

    # Set the path to output created files
    csm.output_path = output_path

    # Create architecture (if creating project from scratch)
    csm.create_architecture()
    
    # Project path
    csm.project_path = project_path

    # Create the model for export to FMU (i.e., Simulator.mo)
    csm.create_model(uniform=[False, False], force_redeclare=True)

    # Create the setup.mos file (optional)
    csm.create_setup(dependencies, compiler='dymola')
            
    # Generate the FMU (i.e., Simulator.fmu)
    # csm.create_fmu(dependencies, experimentSettings={'solver':'Sdirk34hw','tolerance':1e-5})