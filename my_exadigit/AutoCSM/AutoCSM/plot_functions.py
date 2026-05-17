# -*- coding: utf-8 -*-
"""
Created on Wed May  7 09:53:21 2025

@author: fig
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shutil
import pickle
import re
from collections import defaultdict
import os
# sys.path.append(os.path.join(base_path,r'/../AutoCSM'))
import helper_functions
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SignalTemplate:
    name: str
    variable_names: List[str]
    offset: Optional[float] = 0.0
    delta: Optional[float] = 1.0
    
    def apply_scaling(self, values):
        return values * self.delta + self.offset
    
def read_scaled_data_from_templates_single(filename, signal_templates, randomize=False):
    """
    Reads a CSV file containing a column for 'time', and single columns for other signals (e.g., 'power'),
    scales signal values, and maps them to model variable names.
    
    Parameters
    ----------
    filename : str
        Path to the input CSV file. Must contain 'time' and one column per signal name.
    
    signal_templates : list of SignalTemplate
        Signal configurations defining CSV column names, variable name mappings, 
        and optional scaling factors.
    
    randomize : bool, optional
        If True, applies random variation to signals.
    
    Returns
    -------
    np.ndarray
        Structured array with time, scaled signals, and mapped variable names.
    """

    df_input = pd.read_csv(filename)

    dtype = [('time', np.double)]
    dtype.extend([(template.name, np.double) for template in signal_templates])

    signals = np.array(list(df_input.itertuples(index=False, name=None)), dtype=dtype)

    for template in signal_templates:
        signals[template.name] = template.apply_scaling(signals[template.name])

    var_matches = []
    for template in signal_templates:
        for var_name in template.variable_names:
            var_matches.append((template.name, var_name))

    signals = helper_functions.create_new_array_with_renamed_fields(signals, var_matches, keep_original=['time'])

    if randomize:
        signals = create_variations(signals, var=(0.8, 1.2), keep_original=['time'])

    return signals

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
 
def get_matching_variables(variables, pattern):
    # Regex pattern to match strings containing ".summary."
    pattern = re.compile(pattern)
    
    # Filtering the list using the regex pattern
    filtered_vars = [var for var in variables if pattern.match(var)]
    return filtered_vars

# Plot functions
def plot_source_signals(signals, var_names = None, individual=False):
    # Retrieve all input variables that are not "time"
    if var_names is None:
        var_names = [name for name in signals.dtype.names if name != 'time']
    
    if individual:
        for var in var_names:
            fig, ax = plt.subplots()
            ax.plot(signals['time'], signals[var], label=var)
            ax.set_title(var)
    else:
        fig, ax = plt.subplots()
        for i, var in enumerate(var_names):
            max_val = np.max(signals[var])
            max_val = 1 if np.isclose(max_val,0,1e-7) else max_val
            ax.plot(signals['time'], signals[var]/max_val, label=f'i_{i}/{max_val:.1e}')
        ax.legend(ncol=int(np.ceil((i+1)/20)),loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
            
def group_result_outputs(varnames, additional_groups=[]):
    groups = defaultdict(list)
    
    group_names = '|'.join(['summary','sources'] + additional_groups)
    for text in varnames:
        # Remove the [digits] parts
        cleaned_text = re.sub(r"\[\d+\]", '', text)
        
        # Now match the groups
        pattern = r'((?:\w+\.)+)({})\.(.+)'.format(group_names)
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
    
    
def plot_result_as_groups(result, output_path, varnames=None, additional_groups=[]):
    
    if varnames is None:
        varnames = result.dtype.names
        
    # Group variables
    groups = group_result_outputs(varnames, additional_groups)
    
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
        os.makedirs(output_path)
    else:
        os.makedirs(output_path)
        
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
                ax.plot(time,result[var])
                ax.set_title(var, fontsize=fontsize)
                ax.set_xlabel(xlabel)
                fig.savefig(os.path.join(output_path, str(i)))
                plt.close(fig)
        else:
            fig, ax = plt.subplots()
            for var in lst:
                if var not in result.dtype.names:
                    skipped.append(var)
                    continue
                label = remove_brackets_and_extract_numbers(var)
                ax.plot(time,result[var], label=label)
            ax.legend()
            legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8}, ncol=int(np.ceil(len(lst)/20)))
            # TODO add logic to deal with long legends
    
            ax.set_title(group, fontsize=fontsize)
            ax.set_xlabel(xlabel)
            fig.savefig(os.path.join(output_path, group.replace('.','_')),bbox_inches='tight')
            plt.close(fig)   