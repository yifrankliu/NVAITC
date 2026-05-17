# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

import os
import sys
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_path,r'../../AutoCSM'))
from auto_csm import AutoCSM

if __name__ == "__main__":

    # Instantiate AutoCSM
    csm = AutoCSM(language='modelica', architecture='nested')
    
    # You can turn off terminal animation if desired
    csm.terminal_animation = False
    
    # Load the JSON specification
    csm.input_specification = '../json/input_specification_default.json'
    # csm.input_specification = '../data/input_specification_default_simple.json'# This uses the default ModelClass from the parent model if not specified in the JSON.

    # Set the path to output created files
    csm.output_path = 'temp'

    # Create architecture (if creating project from scratch)
    csm.create_architecture()
    
    # Project path
    csm.project_path = 'GenericDatacenter'

    # Create the model for export to FMU (i.e., Simulator.mo)
    csm.create_model(uniform=[False, False])
    # Note this does not specify a solver in the model file. That is added in create_FMU.

    # Model dependencies: List of libraries needed for FMU generation or model setup scripts
    dependencies = [
        r'../../../../../Modelica/TRANSFORM-Library/TRANSFORM/package.mo'
        ]
    
    # Create the setup.mos file (optional)
    csm.create_setup(dependencies, compiler='dymola')
            
    # Generate the FMU (i.e., Simulator.fmu)
    # includeVariables is optional. Use this to specify the exact variables that are desired in FMU. All others will be concealed.
    csm.create_fmu(dependencies, experimentSettings={'solver':'Sdirk34hw','tolerance':1e-5}, includeVariables=None)