# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.

An example of running the FMU created by run_auto_csm.

This python file will:
    - read a input file
    - scale the values to relavent values for the model
    - populate variables to save
    - simulate the fmu
    - create a wide variety of plots (with grouping to help compare variables of the same name)

"""

import fmpy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys
import os
import pathlib
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_path,r'../../AutoCSM'))
import helper_functions
import plot_functions as pf

def read_data_power_multi(filename, structure):
    # TODO: Should be generalized and moved to plot_functions
    # Process input data
    # Read data
    df = pd.read_csv(filename)
    dtype = [(col, np.double) for col in df.columns]
    signals = np.array(list(df.itertuples(index=False, name=None)), dtype=dtype)
    
    signals['temperature'] += 273.15
    for i in range(structure['nComputeBlocks']):
        signals[f'power[{i+1}]'] /= structure['nCabinets']
    
    # Variable matching
    var_matches = [('temperature', f'simulator_{i+1}_centralEnergyPlant_{j+1}_coolingTowerLoop_{k+1}_sources_T_ext') for k in range(structure['nCoolingTowerLoops']) for j in range(structure['nCentralEnergyPlants']) for i in range(structure['nSimulators'])]
    var_matches.extend([(f'power[{k+1}]', f'simulator_{i+1}_datacenter_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total') for m in range(structure['nCabinets']) for k in range(structure['nComputeBlocks']) for j in range(structure['nDatacenters']) for i in range(structure['nSimulators'])])
    signals = helper_functions.create_new_array_with_renamed_fields(signals, var_matches, keep_original=['time'])
    
    return signals
             
if __name__ == "__main__":
        
    #%% Input signals
    structure = {'nComputeBlocks':10,
                    'nCabinets':3,
                    'nCentralEnergyPlants':1,
                    'nCoolingTowerLoops':1,
                    'nSimulators':1,
                    'nDatacenters':1}
    
    # Create templates for signal data from file to FMU input
    signal_templates = [
        pf.SignalTemplate(
            name='temperature',
            variable_names=[
                f'simulator_{i+1}_centralEnergyPlant_{j+1}_coolingTowerLoop_{k+1}_sources_T_ext'
                for k in range(structure['nCoolingTowerLoops'])
                for j in range(structure['nCentralEnergyPlants'])
                for i in range(structure['nSimulators'])
            ],
            offset=15+273.15,
            delta=6
        ),
        pf.SignalTemplate(
            name='power',
            variable_names=[
                f'simulator_{i+1}_datacenter_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total'
                for m in range(structure['nCabinets'])
                for k in range(structure['nComputeBlocks'])
                for j in range(structure['nDatacenters'])
                for i in range(structure['nSimulators'])
            ],
            offset=5e3,
            delta=1e4
        )
    ]
        
    # Read in the input data to input signals
    signals = pf.read_scaled_data_from_templates_single('../data/example_timeseries_scaled.csv', signal_templates, randomize=False)

    # Plot the source signals on a single plot or as separate plots
    pf.plot_source_signals(signals, individual=False)

    # Retrieve all input variables that are not "time"
    var_names = [name for name in signals.dtype.names if name != 'time']
        
    #%% Prepare the inputs for simulating the FMU
    # Location of FMU
    fmu_filename = 'temp/Simulator.fmu'
    
    # Read FMU
    fmpy.dump(fmu_filename)
    model_description = fmpy.read_model_description(fmu_filename)
    
    # Get all variables by name
    var_model = []
    for variable in model_description.modelVariables:
            var_model.append(variable.name)
        
    # Define the variables to be exported from the FMU simulation
    outputs = []
    # Reformat the strings to appropriate form for Modelica
    # outputs += [helper_functions.convert_numbers_to_bracket_form(var) for var in var_names]
    # Add additional CUSTOM variables
    outputs += [f'simulator[1].datacenter[1].computeBlock[{i+1}].cabinet[{j+1}].volume.medium.T' for j in range(structure['nCabinets']) for i in range(structure['nComputeBlocks'])]
    # Add summary variables
    outputs += pf.get_matching_variables(var_model, r'.*(\.summary\.|^summary).*')
    # Add source variables
    outputs += pf.get_matching_variables(var_model, r'.*\.sources\.(?!controlBus\.).*Q_flow_total')
    # Add performance variables
    outputs += ['CPUtime', 'EventCounter']
    
    # Verify all inputs/outputs are valid
    for var in var_names:
        if not var in var_model:
            print(f'Variable not found in model variables: {var}')

    #%% Simulate the FMU
    tt = helper_functions.TicToc()
    tt.tic()
    result = fmpy.simulate_fmu(fmu_filename,input=signals,stop_time=86400, output=outputs, output_interval=15, debug_logging=True)#,output_interval=1)
    tt.toc()
    
    # Save to file. Can load with pf.loadPickle(filename)
    pf.toPickle('temp/result', result) 
    
    #%% Plot results
    # Path to output 
    output_path = (pathlib.Path(fmu_filename).parent / 'plots').resolve().as_posix()
    
    # Simple
    var = outputs[3]
    fig, ax = plt.subplots()
    ax.plot(result['time'],result[var])
    ax.set_title(var)
    
    # Fancy
    pf.plot_result_as_groups(result, output_path, outputs, ['volume.medium'])