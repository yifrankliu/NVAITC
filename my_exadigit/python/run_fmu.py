# -*- coding: utf-8 -*-
"""
Created on Tue May 28 10:38:37 2024

@author: Scott Greenwood
"""

import fmpy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shutil
import pickle
import re
from collections import defaultdict
import sys
import os
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_path,r'../../AutoCSM/AutoCSM'))
import helper_functions

def toPickle(filePath, data):
    with open('{}.pickle'.format(filePath), 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def loadPickle(filePath):   
    with open('{}.pickle'.format(filePath), 'rb') as handle:
        return pickle.load(handle)
   
def create_variations(array, var=(0.8,1.2), keep_original=[]):
    # Create an array to store the n variations
    array_new = np.empty(array.shape, dtype=array.dtype)
    
    for name in array.dtype.names:
        if name in keep_original:
            array_new[name] = array[name]
        else:
            variation = np.random.uniform(0.8, 1.2, size=array[name].shape)

            # Apply the random variations
            array_new[name] = array[name] * variation
           
    return array_new

# Structure inputs
nComputeBlocks = 25
nCabinets = 3
nCentralEnergyPlants = 1
nCoolingTowerLoops = 1
nSimulators = 1
nDatacenters = 1

def read_data_power_single(filename, randomize=False):
    # Process input data
    # Read data
    df_input = pd.read_csv(filename)
    
    # Convert data to input signals
    dtype = [('time', np.double), ('power', np.double), ('temperature', np.double)]
    signals = np.array(list(df_input.itertuples(index=False, name=None)), dtype=dtype)
    
    # Apply scaling/unit corrections as needed
    signals['temperature'] += 273.15 # Convert from C to K
    signals['power'] /= (nComputeBlocks * nCabinets) # Scale from total power to individual
    
    # Variable matching
    var_matches = [('temperature', f'simulator_{i+1}_centralEnergyPlant_{j+1}_coolingTowerLoop_{k+1}_sources_Towb') for k in range(nCoolingTowerLoops) for j in range(nCentralEnergyPlants) for i in range(nSimulators)]
    var_matches.extend([('power', f'simulator_{i+1}_datacenter_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total') for m in range(nCabinets) for k in range(nComputeBlocks) for j in range(nDatacenters) for i in range(nSimulators)])
    
    signals = helper_functions.create_new_array_with_renamed_fields(signals, var_matches, keep_original=['time'])
    
    if randomize:
        signals = create_variations(signals, var=(0.8,1.2), keep_original=['time'])
    return signals

def read_data_power_multi(filename):
    # Process input data
    # Read data
    df = pd.read_csv(filename)
    dtype = [(col, np.double) for col in df.columns]
    signals = np.array(list(df.itertuples(index=False, name=None)), dtype=dtype)
    
    signals['OA Wetbulb Temp'] += 273.15
    for i in range(nComputeBlocks):
        signals[f'power[{i+1}]'] /= nCabinets
    
    # Variable matching
    var_matches = [('OA Wetbulb Temp', f'simulator_{i+1}_centralEnergyPlant_{j+1}_coolingTowerLoop_{k+1}_sources_Towb') for k in range(nCoolingTowerLoops) for j in range(nCentralEnergyPlants) for i in range(nSimulators)]
    var_matches.extend([(f'power[{k+1}]', f'simulator_{i+1}_datacenter_{j+1}_computeBlock_{k+1}_cabinet_{m+1}_sources_Q_flow_total') for m in range(nCabinets) for k in range(nComputeBlocks) for j in range(nDatacenters) for i in range(nSimulators)])
    signals = helper_functions.create_new_array_with_renamed_fields(signals, var_matches, keep_original=['time'])
    
    return signals
    
signals = read_data_power_multi('data/input_04-07-24.csv')

#%%
var_names = [name for name in signals.dtype.names if name != 'time']

# User Input
fmu_filename = os.path.join(base_path, r'temp\Simulator.fmu')

output_path = os.path.dirname(os.path.abspath(fmu_filename))

outputs = []
# outputs += var_names
outputs += [helper_functions.convert_numbers_to_bracket_form(var) for var in var_names]
outputs += [f'simulator[1].datacenter[1].computeBlock[{i+1}].cabinet[{j+1}].coolingChannels.medium.T' for j in range(nCabinets) for i in range(nComputeBlocks)]

# FMU Prep

# Read FMU
fmpy.dump(fmu_filename)

model_description = fmpy.read_model_description(fmu_filename)

var_model = []
for variable in model_description.modelVariables:
        var_model.append(variable.name)
    
def get_matching_variables(variables, pattern):
    # Regex pattern to match strings containing ".summary."
    pattern = re.compile(pattern)
    
    # Filtering the list using the regex pattern
    filtered_vars = [var for var in variables if pattern.match(var)]
    return filtered_vars

# Add summary variables to model
outputs += get_matching_variables(var_model, r'.*(\.summary\.|^summary).*')
outputs += get_matching_variables(var_model, r'.*\.sources\.(?!controlBus\.).*')
outputs += ['CPUtime', 'EventCounter']

# Verify all inputs/outputs are valid
for var in var_names:
    if not var in var_model:
        print(f'Variable not found in model variables: {var}')
  
#%%
if True:
    individual = False
    if individual:
        for var in signals.dtype.names:
            fig, ax = plt.subplots()
            ax.plot(signals['time'], signals[var], label=var)
            ax.set_title(var)
    else:
        fig, ax = plt.subplots()
        for var in signals.dtype.names:
            ax.plot(signals['time'], signals[var], label=var)
        ax.set_title(var)
       

#%%
# Simulate
tt = helper_functions.TicToc()
tt.tic()

result = fmpy.simulate_fmu(fmu_filename,input=signals,stop_time=86400, output=outputs, output_interval=15, debug_logging=True)#,output_interval=1)
tt.toc()

# Save pickle
toPickle(os.path.join(output_path,'result'), result)

# Load pickle
result = loadPickle(os.path.join(output_path,'result'))

# Group variables
#TODO should also add for same name variables not in summary or sources
def group_result_outputs(varnames):
    groups = defaultdict(list)
    for text in varnames:
        # Remove the [digits] parts
        cleaned_text = re.sub(r"\[\d+\]", '', text)
        
        # Now match the groups
        pattern = r'((?:\w+\.)+)(summary|sources)\.(.+)'
        # pattern = r'((?:\w+\.)+)\.(.+)'
        match = re.match(pattern, cleaned_text)
        
        if match:
            key = match[0]
            groups[key].append(text)
        else:
            groups['sep'].append(text)
    return groups

def remove_brackets_and_extract_numbers(text):
    # Extract numbers from the text
    numbers = re.findall(r"\[(\d+)\]", text)
    # Join the numbers with underscores
    numbers_str = "_".join(numbers)
    return numbers_str

groups = group_result_outputs(outputs)


# Plotting

plot_dir = os.path.join(output_path, 'plots')
if os.path.exists(plot_dir):
    shutil.rmtree(plot_dir)
    os.makedirs(plot_dir)
else:
    os.makedirs(plot_dir)
    
def plot_time_based_on_max(result):
    # Extract the time array
    time = result['time']
    
    # Determine the maximum value
    max_time = max(time)
    
    # Set the unit and scale based on the max value
    if max_time > 86400*3:  # More than 72 hours
        time = time / 86400
        xlabel = 'Time (days)'
    elif max_time > 3600:  # More than 60 minutes (1 hour)
        time = time / 3600
        xlabel = 'Time (hours)'
    elif max_time > 60:  # More than 60 seconds (1 minute)
        time = time / 60
        xlabel = 'Time (minutes)'
    else:  # 60 seconds or less
        xlabel = 'Time (seconds)'
    return time, xlabel

time, xlabel = plot_time_based_on_max(result)

fontsize = 8
skipped = []
for group, lst in groups.items():
    if group == 'sep':
        for i, var in enumerate(lst):
            if var not in result.dtype.names:
                skipped.append(var)
                continue
            fig, ax = plt.subplots()
            ax.plot(time[1::],result[var][1::])
            ax.set_title(var, fontsize=fontsize)
            ax.set_xlabel(xlabel)
            fig.savefig(os.path.join(plot_dir, str(i)))
            plt.close(fig)
    else:
        fig, ax = plt.subplots()
        for var in lst:
            if var not in result.dtype.names:
                skipped.append(var)
                continue
            label = remove_brackets_and_extract_numbers(var)
            ax.plot(time[1::],result[var][1::], label=label)
        ax.legend()
        legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8}, ncol=np.ceil(len(lst)/20))
        # TODO add logic to deal with long legends

        ax.set_title(group, fontsize=fontsize)
        ax.set_xlabel(xlabel)
        fig.savefig(os.path.join(plot_dir, group.replace('.','_')),bbox_inches='tight')
        plt.close(fig)