# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

import pathlib

import sys
import os
import copy
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import helper_functions
import nested_structure_utils

sys.path.append(os.path.join(os.path.dirname(__file__)))
import parse_files

# A global list of variables that need to be added at the top due to issues with FMUs being generated with correct causality
global_create_interface_variables = True
global_variables_interface = []
   
def structure_line(data, uniform):
    temp = []
    systems = data.get('Systems', [])
    if systems and systems != [{}]:
        for system in systems:
            parameters = sorted(list(system['Structure'].keys()))
            temp_s = []

            for var in parameters:
                temp_val = system["Structure"][var]
                temp_val = nested_structure_utils.to_lowercase_strings(temp_val) if var == 'useParallel' else temp_val
                
                if uniform:    
                    temp_s.append(f'each {var}={nested_structure_utils.get_first_value(temp_val)}'.replace("'",""))
                else:   
                    temp_s.append(f'{var}={temp_val}'.replace('[', '{').replace(']', '}').replace("'",""))
                    
            temp_structures = ','.join(temp_s)

            temp.append(f'{system["InstanceName"]}({temp_structures})')
    line =f'structure({",".join(temp)})\n'
    return line
            
def sources_line(data, project_path, base_path, model_class_path, key_path, uniform):
    temp = []
    temp_path = pathlib.Path(project_path).parts[:-1]
    
    model_path_list = list(temp_path) + model_class_path.split('.')[0:-2] + ['Models'] + [data['ModelClass'] + '.mo']
    model_path = pathlib.Path(*model_path_list)
    
    # Find the default by searching for "redeclare replaceable Sources.* sources"
    default_source_class = parse_files.extract_default_class_from_model(model_path.as_posix(), 'Sources', 'sources')
    default_source_class = default_source_class if default_source_class == [] else default_source_class[0]
    
    # If 'SourceClass' is not in in the input file and is not the default, redeclare
    if 'SourceClass' in data.keys() and default_source_class != data['SourceClass']:
        # Adds redeclaration if a non-default source class is specified
        model_class_path = '.'.join([base_path, 'Sources', data['SourceClass']])
        line = f'redeclare {model_class_path} '
    else:
        line = ''
    
    if 'SourceClass' in data.keys():
       default_source_class = data['SourceClass'] 
       
    source_path_list = list(temp_path) + model_class_path.split('.')[0:-2] + ['Sources'] + [default_source_class + '.mo']
    source_path = os.path.join(*source_path_list)
        
    inputs = parse_files.get_variable_by_type(source_path, 'input')
    if inputs:
        temp_struct = nested_structure_utils.create_nested_list(data['Structure']['n'], data['Structure']['useParallel'], 'Y')
            
    temp_s = []
    if global_create_interface_variables:
        for var in inputs:
            # used here to force the the IDE to create an FMU with causality=Input (i.e., time variant). 
            # preference would be to have just a start or default value
            
            temp_names = nested_structure_utils.generate_key_strings(temp_struct, key_path, f'sources_{var["name"]}')
            temp_struct_filled = nested_structure_utils.replace_struct_values(temp_struct, temp_names)
            
            array_modifier = '' if var['dimensions'] is None else f'[{var["dimensions"]}]'
            if uniform:
                temp_name = nested_structure_utils.get_first_value(temp_struct_filled)
                temp_s.append(f'each {var["name"]}={temp_name}'.replace("'",""))
                
                global_variables_interface.append('Modelica.Blocks.Interfaces.RealInput ' + temp_name + array_modifier + f'(start={var["value"]});')
            else:
                temp_s.append(f'{var["name"]}={temp_struct_filled}'.replace('[', '{').replace(']', '}').replace("'",""))

                for temp_name in temp_names:
                    global_variables_interface.append('Modelica.Blocks.Interfaces.RealInput ' + temp_name + array_modifier + f'(start={var["value"]});')
                    
            temp = ','.join(temp_s)
    else:

        if uniform:
            temp = ','.join([f'each {var[2]}={var[3]}' for var in inputs])
        else:
            for var in inputs:
                temp_struct_filled = nested_structure_utils.replace_struct_values(temp_struct, [var["value"]]*nested_structure_utils.count_leaf_nodes(temp_struct))
                temp_s.append(f'{var["name"]}={temp_struct_filled}'.replace('[', '{').replace(']', '}').replace("'",""))
            temp = ','.join(temp_s)
    line += f'sources({temp if temp else ""})\n'
    return line

def create_nested_lines(data, project_path, base_path, uniform=[True,True], lines=None, is_top_system=True, key_path=None, level=0, last_modelClass=None, force_redeclare=True):

    """
    Creates a list of lines representing the structure of the Modelica model.

    Args:
        data (dict): The input data dictionary.
        project_path (str): Path to the Modelica project folder.
        unifrom (list[2] bool): controls if structure [0] and sources [1] should be assumed uniform or individually
        lines (list, optional): An existing list of lines to append to. Defaults to None.
        is_top_system (bool, optional): Whether the current system is the top-level system. Defaults to True.
        structure_path (str, optional): The path to the structure template file.
        key_path (str): the dotted path to the current point in hierarchy
        level (int): the level into the hierarchy
        last_modelClass (string): the parent model class
        force_redeclare (bool): adds redeclare statement to file even when child class remains unchanged from the default value
    Returns:
        list: A list of lines representing the structure of the Modelica model.
    """
    lines = lines or []
    
    if key_path is not None:
        key_path = '.'.join([key_path, data['InstanceName']])
    else:
        key_path = data['InstanceName']
        
    if is_top_system:
        lines.append(f'n={data["Structure"]["n"]}')
    else:
        base_path = '.'.join([base_path, 'Systems', data['Name']])

    model_instance_name = data['InstanceName']
    if is_top_system or'ModelClass' in data.keys():
        model_class_path = '.'.join([base_path, 'Models', data['ModelClass']])
        lines.append(f'redeclare {model_class_path} {model_instance_name}(')
    else:
        # If not specified in JSON, find default class from parent model (doesn't require redeclare b)
        temp_path = pathlib.Path(project_path).parts[:-1]
        model_path_list = list(temp_path) + base_path.split('.')[0:-2] + ['Models'] + [last_modelClass + '.mo']
        model_path = pathlib.Path(*model_path_list)
        default_class = parse_files.extract_default_class_from_model(model_path.as_posix(), 'Models', model_instance_name)
        data['ModelClass'] = default_class if default_class == [] else default_class[0]
        model_class_path = '.'.join([base_path, 'Models', data['ModelClass']])
        
        if force_redeclare:
            lines.append(f'redeclare {model_class_path} {model_instance_name}(')
        else:
            lines.append(f'{model_instance_name}(')


    
    # Current system changes
    ## Structure
    lines.append(structure_line(data, uniform[0]))

    ## Sources
    lines.append(sources_line(data, project_path, base_path, model_class_path, key_path, uniform[1]))
    
    # Next system changes
    for sub_dict in data['Systems']:
        if sub_dict:  # Terminate if dictionary is empty
            lines = create_nested_lines(sub_dict, project_path, base_path, uniform, lines, False, key_path, level+1, data['ModelClass'], force_redeclare)
    lines.append(')')

    return lines

def create_model_file(content, parent_class, output_path):
    """
    Creates a Modelica model file with the given content, extending the specified parent class.

    Args:
        content (str): The content of the Modelica model.
        parent_class (str): The parent class to extend.
        output_path (str or pathlib.Path): The path to the output Modelica file.
    """
    temp_path = pathlib.Path(output_path)
    if temp_path.suffix != '.mo':
        temp_path = temp_path.parent / (temp_path.name + '.mo')
        print('Modified output file extension to ".mo"')

    if not os.path.exists(temp_path.parent):
        os.mkdir(temp_path.parent)

    with open(temp_path, 'w') as mo_file:
        mo_file.write('within ;\n')
        mo_file.write(f'model {temp_path.stem}\n')
        mo_file.write(f'extends {parent_class}(\n')
        mo_file.write(f'{content});\n')
        for var in global_variables_interface:
            mo_file.write(f'{var}\n')
        mo_file.write(f'end {temp_path.stem};')
        
def main(json_file_path, project_path, base_path, parent_class, output_path, structure_path, uniform=[False, False], force_redeclare=True):
    """
    Main function to create a Modelica model file based on the given input parameters.

    Args:
        json_file_path (str): The path to the input JSON file.
        base_path (str): Dotted-styel path to top-level system model package corresponding to the first entry in the JSON file.
        parent_class (str): The parent class to extend.
        output_path (str or pathlib.Path): The path to the output Modelica file.
        structure_path (str, optional): The path to the structure template file (contains the common structural parameters).
        unifrom (list[2] bool): controls if structure [0] and sources [1] should be assumed uniform or individually
        force_redeclare (bool): adds redeclare statement to file even when child class remains unchanged from the default value
    """
    global_variables_interface.clear()
    
    data_orig = helper_functions.read_json(json_file_path)
    
    #TODO: Data check section
    # Verify required fields are present: Name, InstanceName (must be unique at that level), ModelClass (default v0), SourceClass (default NULL), Systems= [{}]
    default_structure_parameters = parse_files.get_variable_by_type(structure_path, 'parameter')
    data = copy.deepcopy(data_orig)
    nested_structure_utils.expand_data(data, {item["name"]: item["value"] for item in default_structure_parameters})

    # Export expanded json for debug purposes
    helper_functions.export_dict_to_json(data, pathlib.Path(output_path).parent / 'input_specification_expanded.json')

    lines = create_nested_lines(data, project_path, base_path, uniform, force_redeclare=force_redeclare)
    content = ','.join(lines).replace(',)', ')').replace('(,', '(')
    create_model_file(content, parent_class, output_path)
    
    
    return data

if __name__ == "__main__":
    # JSON file path
    json_file_path = '../../../examples/json/input_specification_v0.json'

    # Output Modelica file
    output_path = '../../../temp/Simulator.mo'

    # Path to ExaDigiT AutoCSM based project
    project_path = '../../../examples/modelica/GenericDatacenter'
    
    # Path to top-level system model folder (dotted path) perhaps not a good one
    base_path = pathlib.Path(project_path).name #'GenericDatacenter'

    # Model to be extended and modified
    parent_class = 'ExaDigiT_AutoCSM.BaseClasses.Tests.PartialTest'

    # Structure path
    structure_path ='../../../methods/Modelica/TemplatesCSM/Templates/Structure.mo'
    
    # Create Modelica model file
    main(json_file_path, project_path, base_path, parent_class, output_path, structure_path, uniform=[False,False])