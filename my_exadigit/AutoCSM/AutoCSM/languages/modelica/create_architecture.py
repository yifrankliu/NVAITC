# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.

TODO: Could add additional layer details to recreate the nested model structure of the generic approach
    - This would add to the Structure and ControlBus the appropirate information
TODO: Could autopopulate model instance in structure with parallel logic (if instanceNames provided)
"""

import os
import shutil
import json
import re
import pathlib

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import helper_functions

def check_and_modify_path(file_path):
    """
    Checks if a specified file path exists. If it does, appends `_*` to the filename, 
    where `*` is a number starting from 0. If the `_0` file exists, increments to the next 
    higher integer (e.g., `_1`) until a non-existing filename is found.

    Args:
        file_path (str): The original file path to check and potentially modify.

    Returns:
        str: The modified file path with the next available `_` number if the original 
             file path exists; otherwise, returns the original file path.
    
    Raises:
        ValueError: If the provided file path is not a string.
    """
    if not os.path.exists(file_path):
        return file_path

    directory, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)
    
    counter = 0
    new_file_path = os.path.join(directory, f"{name}_{counter}{ext}")
    
    while os.path.exists(new_file_path):
        counter += 1
        new_file_path = os.path.join(directory, f"{name}_{counter}{ext}")
    
    return new_file_path

def create_nested_structure(data, output_path, template_folder, isTopSystem=True):
    """
    Creates a nested folder structure based on the provided JSON data and a template folder.

    Parameters:
    data (dict): The dictionary containing the project structure information.
    output_path (str): The base path where the folder structure will be created.
    template_folder (str): The path to the template folder to be copied.
    isTopSystem (bool): Indicates if the current level is the top-level system.

    Returns:
    str: The path to the created project.
    """
    # Handle the special case of the top level system being the name of the project.
    if isTopSystem:
        new_folder_path = os.path.join(output_path, data['Name'])
            
        if os.path.exists(new_folder_path):
            shutil.rmtree(new_folder_path)
    else:
        new_folder_path = os.path.join(output_path, 'Systems', data['Name'])
        
    # If path exists increment name
    new_folder_path = check_and_modify_path(new_folder_path)
        
    # Copy and rename folder
    shutil.copytree(template_folder, new_folder_path)
        
    for sub_dict in data['Systems']:   
        if sub_dict: # Terminate if dictionary is empty
            create_nested_structure(sub_dict, new_folder_path, template_folder, isTopSystem=False)
        
    project_path = new_folder_path
    return project_path

def create_flat_structure(data, output_path, template_folder, isTopSystem=True):
    """
    Creates a flat folder structure based on the provided JSON data and a template folder.

    Parameters:
    data (dict): The dictionary containing the project structure information.
    output_path (str): The base path where the folder structure will be created.
    template_folder (str): The path to the template folder to be copied.
    isTopSystem (bool): Indicates if the current level is the top-level system.

    Returns:
    str: The path to the created project.
    """
    # Handle the special case of the top level.
    project_path = ''
    if isTopSystem:
        project_name = data['Name']
        output_path = os.path.join(output_path, project_name)
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.mkdir(output_path)
        
        project_path = output_path
            
        output_path = os.path.join(output_path, 'Systems')
        os.mkdir(output_path)
        
    new_folder_path = os.path.join(output_path, data['Name']) 
    
    # If path exists increment name
    new_folder_path = check_and_modify_path(new_folder_path)
    
    # Copy and rename folder
    shutil.copytree(template_folder, new_folder_path)
    
    for sub_dict in data['Systems']:   
        if sub_dict: # Terminate if dictionary is empty
            create_flat_structure(sub_dict, output_path, template_folder, isTopSystem=False)
    
    return project_path

def replace_string_between_identifiers(input_string, replacement_text, left_identifier, right_identifier):   
    """
    Replaces the text between specified identifiers in an input string with the provided replacement text.

    Parameters:
    input_string (str): The original string.
    replacement_text (str): The text to replace the original content between the identifiers.
    left_identifier (str): The left boundary identifier.
    right_identifier (str): The right boundary identifier.

    Returns:
    str: The modified string with the replaced content.
    """
    # Create a regex pattern to match everything between the identifiers
    pattern_string = left_identifier + r'(.*?)' + right_identifier
    output = re.sub(pattern_string, left_identifier + replacement_text + right_identifier, input_string)
    return output

def handle_package_mo(folder):
    """
    Ensures the package.mo file exists in the folder.
    
    Parameters:
    folder (pathlib.Path): The folder where package.mo should be created.
    """
    if len([f for f in folder.glob('package.mo')]) == 0:
        with open(os.path.join(folder, 'package.mo'), 'w') as pkgfile:
            pkgfile.write('within TO_BE_REPLACED;\n')
            pkgfile.write(f'package {folder.stem}\n')
            pkgfile.write(f'end {folder.stem};\n')
        
def handle_package_order(folder):
    """
    Ensures the package.order file exists and is up-to-date.
    
    Parameters:
    folder (pathlib.Path): The folder where package.order should be created.
    """
    if len([f for f in folder.glob('package.order')]) == 0:
        with open(os.path.join(folder, 'package.order'), 'w') as pkgfile:
            pkgfile.write('')
            
def correct_package_files(project_path, template_folder):
    """
    Corrects and ensures the existence of package.mo, *.mo "within ...;", and package.order files within the project directory.

    Parameters:
    project_path (str): The path to the created project.
    template_folder (str): The path to the template folder.

    Returns:
    None
    """
    path = pathlib.Path(project_path)
    project_name = path.parts[-1]
    
    # Check that a folder has the package.mo and package.order files. Create them if they don't exist
    folders = [f for f in path.glob("**/*") if not f.is_file()]
    folders.append(path)
    for folder in folders:
        handle_package_mo(folder)  # Create default package.mo file if it does not exist                  
        handle_package_order(folder) # Create default package.order file if it does not exist
        
    # package.mo and *.mo "within ...;" specific corrections
    files = [f for f in path.glob("**/*.mo") if f.is_file()]
    for file in files:
        with open(file, 'r') as pkgfile:
            lines = pkgfile.read()
            
            # Replaces "within ...;" with the appropriate local path e.g.: within ProjectName.System.File;
            temp = file.parts
            
            iCutoff = -2 if 'package.mo' in str(file) else -1
            temp_path_dot = str(pathlib.Path(*temp[temp.index(project_name):iCutoff]))
            temp_path_dot = temp_path_dot.replace('\\','.') #TODO: Should replace this with something more robust
            
            if file.parts[-2] == project_name:
                # Special case for top level
                lines = replace_string_between_identifiers(lines, '', 'within ', ';')    
            else:
                lines = replace_string_between_identifiers(lines, temp_path_dot, 'within ', ';')
            
            # Replace the package with the correct name: e.g., package CORRECTNAME
            lines = lines.replace(os.path.split(template_folder)[-1], file.parts[-2])    
            
        with open(file, 'w') as pkgfile:
            pkgfile.write(lines)
            
    # package.order specific corrections. This only touches empty files.
    files = [f for f in path.glob("**/*.order") if f.is_file()]
    for file in files:
        # Find all folders and files that need to be included in the package.order file
        temp_file_path = pathlib.Path(*file.parts[0:-1])
        folder_content = [f for f in temp_file_path.glob("*") if not 'package.' in str(f)]

        # Determine the name and order of the contents
        order_names = sort_folder_content(folder_content, method=1)
        
        # Write the contents to file if the package.order file is empty.
        #TODO: could have a check here that adds in any missing
        with open(file, 'r') as pkgfile:
            lines = pkgfile.read()
            
            # Skip to next loop if package.order is not empty (i.e., don't overwrite existing)
            #TODO: Could revisit to ensure everything is captured. Would want to retain existing structure potentially.
            if lines != '':
                continue
            
        with open(file, 'w') as pkgfile:
            for val in order_names:
                pkgfile.write(val + '\n')
            
def sort_folder_content(folder_content, method='default'):
    """
    Sorts the contents of a folder based on the specified method.

    Parameters:
    folder_content (list): A list of pathlib.Path objects representing the folder contents.
    method (str): The sorting method to use. Default is alphabetical order of directories and then files.

    Returns:
    list: A list of sorted folder and file names.
    """
    #TODO: can add it alternative ordering scheme. default is folders then files in alphabetical order
    if method == 'ABC_DIR_FILES' or method == 1: # Puts files in alphabetical order of directories and then files       
        # Categorize
        folders = []
        files = []
        for f in folder_content:
            if f.is_file():
                files.append(f)
            else:
                folders.append(f)
                
        # Extract order naming (unsorted)
        files = [f.stem for f in files]
        folders = [f.stem for f in folders]
        
        # Alphabetize
        files = sorted(files)
        folders = sorted(folders)
        
        # Create order
        order_names = folders + files
        
    else:  
        order_names = [f.stem for f in files]
        
    return order_names
  
def get_unique_systems(systems_list):
    """
    Returns a list of unique systems from the provided systems list.
    
    Parameters:
    systems_list (list): List of systems to filter for uniqueness.
    
    Returns:
    tuple: A tuple of the unique systems list and a list of duplicate reports.
    """
    seen_names = set()
    unique_systems = []
    report = []
    
    for system in systems_list:
        if system:
            if system['Name'] in seen_names:
                report.append(f"Removed duplicate system with name: {system['Name']}")
            else:
                seen_names.add(system['Name'])
                unique_systems.append(system)
    
    return unique_systems, report

def remove_duplicate_systems(input_dict, current_level=0):
    """
    Checks at every level in the nested dictionary if the 'systems' field's values contain 
    dictionaries in its list that have the same name. If duplicates are found, removes one of the 
    dictionaries in the list and reports what it did.
    
    This is appropirate because For the architecture (i.e., folder structure) fields at the same
    level with the same name are assumed to be of the same type. If this is not desired consider
    renaming one of the fields.
    
    :param input_dict: The input nested dictionary.
    :param current_level: The current level in the nested dictionary.
    :return: A tuple containing the new dictionary without duplicates and a report of what was removed.
    """
    report = []

    # Retain only 'Name' and 'Systems' fields
    cleaned_dict = {key: value for key, value in input_dict.items() if key in ['Name', 'Systems']}

    # Check for duplicates in the systems field at the current level
    if 'Systems' in cleaned_dict:
        unique_systems, system_report = get_unique_systems(cleaned_dict['Systems'])
        cleaned_dict['Systems'] = unique_systems
        report.extend(system_report)

        # Recursively check the nested dictionaries
        for idx, system in enumerate(cleaned_dict['Systems']):
            updated_system, system_report = remove_duplicate_systems(system, current_level + 1)
            cleaned_dict['Systems'][idx] = updated_system
            report.extend(system_report)
        
    return cleaned_dict, report
    
def main(json_file_path, output_path, template_folder, project_name=None, architecture='nested', ):
    """
    Main function to create the folder structure and correct package files.

    Parameters:
    json_file_path (str): The path to the JSON file containing the project structure.
    output_path (str): The base path where the folder structure will be created.
    template_folder (str): The path to the template folder to be copied.
    project_name (str): Name of top level project (e.g., modeling library). Input specification may contain this but if this is not None it will override it.
    architecture (str): The type of project structure to create ('nested' or 'flat').

    Returns:
    None
    """
    data = helper_functions.read_json(json_file_path)
    
    # Logic to not require project name in input specification
    if project_name is not None:
        data['Name'] = project_name
        
    if 'Name' not in data.keys():
        data['Name'] = 'PROJECTNAME'
        
    # Process the data to remove duplicates at every level
    data, report = remove_duplicate_systems(data)

    # Output the updated dictionary and the report
    if report:
        print('Duplicate systems removed for architecture creation:')
        print("Report:\n", report)
    print("Architecture created:\n", json.dumps(data, indent=2))
    
    if architecture == 'nested':
        project_path = create_nested_structure(data, output_path, template_folder)
    elif architecture == 'flat':
        project_path = create_flat_structure(data, output_path, template_folder)
    correct_package_files(project_path, template_folder)
        
if __name__ == "__main__":
    # Change to your JSON file path
    # Change to your template folder path
    # Change to your desired output directory
    json_file_path = '../../../examples/json/input_specification_v0.json'
    template_folder = '../../../methods/modelica/TemplatesCSM/Templates/TemplateSystem'
    output_path = '../../../temp'   
    main(json_file_path, output_path, template_folder, architecture='nested')