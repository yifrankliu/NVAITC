# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

import re
import os

def _remove_whitespace_between_strings(text, str1, str2):
    """
    Removes whitespace between two specified strings in a given text.

    Args:
        text: The input string.
        str1: The first string.
        str2: The second string.

    Returns:
        The modified string with whitespace removed between str1 and str2.
    """

    pattern = re.compile(rf"({re.escape(str1)})\s+({re.escape(str2)})")
    
    def replace_match(match):
        return match.group(1) + match.group(2)

    return pattern.sub(replace_match, text)

def _remove_comments(content):
    """
    Remove Modelica comments while preserving string literals.
    
    Args:
        content (str): The file content as a string.
    
    Returns:
        str: Content with comments removed.
    """
    # Remove multi-line comments (/* ... */) across lines
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Process each line to remove single-line comments (//), respecting strings
    lines = content.splitlines()
    for i in range(len(lines)):
        line = lines[i]
        in_string = False
        new_line = []
        for j, char in enumerate(line):
            if char == '"':
                in_string = not in_string
            if not in_string and line[j:j+2] == '//':
                break
            new_line.append(char)
        lines[i] = ''.join(new_line)
    return '\n'.join(lines)

def _extract_variable_name_dims_mods(expression):
    """
    Find name, dimensions [], and modifiers () of variable declaration using the '=' as the divider.
    
    Args:
        expression (str): The string to search (e.g., 'hello[3](start=0) = 1.0 "cool"').
    
    Returns:
        name (str): Name of the variable (e.g., hello)
        brackets (str): Contents, if any, of brackets (e.g., 3 or None)
        parenthesis (str): Contents, if any, of parenthesis (e.g., start=0 or None)
        right_part (str): Portion of expression on right side of '=' (e.g., 1.0 "cool")
    """
    # Step 1: Find the first '=' that is NOT inside parentheses
    depth_paren = 0  # Track parentheses depth
    depth_bracket = 0  # Track brackets depth

    for i, char in enumerate(expression):
        if char == '(':
            depth_paren += 1
        elif char == ')':
            depth_paren -= 1
        elif char == '[':
            depth_bracket += 1
        elif char == ']':
            depth_bracket -= 1
        elif char == '=' and depth_paren == 0:  # Found '=' outside parentheses
            left_part = expression[:i].strip()
            right_part = expression[i + 1:].strip()
            break
    else:
        raise ValueError("No valid '=' found outside parentheses.")

    # Step 2: Extract parts from the left side
    pattern = re.match(r'([^\[\(]+)(?:\[(.*?)\])?(?:\((.*?)\))?', left_part)

    if pattern:
        name = pattern.group(1).strip() # Main variable name
        brackets = pattern.group(2).replace(' ', '') if pattern.group(2) else None # Content inside square brackets
        parenthesis = pattern.group(3) if pattern.group(3) else None      # Content inside parentheses
    else:
        raise ValueError("Invalid left-hand side format.")
    
    return name, brackets, parenthesis, right_part


def extract_variables(file_path, type_prefixes=None, types=None, exclude_prefixes=['final'], invert_type_prefixes=False, invert_types=False):
    """
    Parse a Modelica file to extract variables declarations.

    Args:
        file_path (str): Path to the Modelica file.
        type_prefixes (str or list, optional): Type-prefixes to extract (e.g., 'parameter|input|output' or ['parameter', 'input']).
                                       Defaults to 'parameter|input|output' if None.
        types (list (str), optional): Types to extract (e.g., "Real, String, etc."). Defaults to all if None.                           
        exclude_prefixes (list (str), optional): Ignore variables with any of the specified prefixes (e.g., "final")
        invert_type_prefixes (bool, optional): Invert the type_prefixes to return all not matching type_prefixes. Only used if type_prefixes is not None.
        invert_types (bool, optional): Invert the invert_types to return all not matching invert_types. Only used if invert_types is not None.
    Returns:
        list: List of dictionaries containing variable details.
    """

    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()

    content = content.replace('\n',' ')
    
    # Remove all comments from the content
    content = _remove_comments(content)

    # Set up the type prefix pattern for the regex
    if type_prefixes is None:
        type_prefixes = 'parameter|input|output'
    elif isinstance(type_prefixes, list):
        type_prefixes = '|'.join(type_prefixes)

    # Define regex pattern to match variable declarations
    # Captures: (prefixes) (type_prefix) (type) (definition);
    pattern = r'((?:\b\w+\s+)*)\b({})\s+([A-Za-z_][\w.]*)\s+(.*?);'.format(type_prefixes)
    matches = re.finditer(pattern, content, re.DOTALL)

    variables = []
    for match in matches:
        prefixes = match.group(1).strip().split()   # Extract and split prefixes to list (e.g., final)
        type_prefix = match.group(2)                # e.g., 'parameter', 'input'
        type_ = match.group(3)                      # e.g., 'Real', 'Integer'
        definition = match.group(4).strip()         # remaining portions of variable declartion (e.g., "NAME(...)=...")

        # Extract variable name, dimensions (if any), and modifiers (if any)
        name, dimensions, modifiers, definition = _extract_variable_name_dims_mods(definition)

        # Find then remove annotation if present
        annotation = None
        definition = _remove_whitespace_between_strings(definition, 'annotation', '(') # Correct for spaces
        annotation_index = definition.find("annotation(")
        if annotation_index != -1:
            annotation = definition[annotation_index:]
            definition = definition[:annotation_index]

        # Extract comment if present. If type is String than set value.
        comment = None
        value = None
        comment_matches = re.findall(r'"(.*?)"', definition)
        if len(comment_matches) == 1 and type_ != 'String':
            comment = comment_matches[0]
        elif len(comment_matches) == 1 and type_ == 'String':
            # No comment
            value = comment_matches[0]
        elif len(comment_matches) == 2 and type_ == 'String':
            comment = comment_matches[1]
            value = comment_matches[0]   
        elif len(comment_matches) == 0 and type_ == 'String':
            raise ValueError('No value found for variable of type String: {}'.format(definition))
        elif len(comment_matches) > 2:
            raise ValueError('Unrecongized variable definition: {}'.format(definition))
        
        # Remove comment and update remaining string
        if comment is not None:
            pattern = rf'"{re.escape(comment)}"'
            definition = re.sub(pattern, '', definition)
        
        # If value not set to remaining content (i.e., not a string)
        if value is None:
            value = definition.replace(' ','')

        # Exclusion logic
        if type_prefixes:
            if invert_type_prefixes:
                if type_prefix in type_prefixes:
                    continue
            else:
                if type_prefix not in type_prefixes:
                    continue
                
        if types:
            if invert_types:
                if type_ in types:
                    continue
            else:
                if type_ not in types:
                    continue
                
        if any(prefix in prefixes for prefix in exclude_prefixes):
            continue
    
        # Construct dictionary with variable details
        variable = {
            "name": name,
            "prefixes": prefixes if prefixes else None,
            "type_prefix": type_prefix,
            "type": type_,
            "dimensions": dimensions,
            "modifiers": modifiers,
            "value": value,
            "comment": comment,
            "annotation": annotation                
        }
        variables.append(variable)

    return variables

def get_variable_by_type(file_path, dtype='parameter'):
    """
    Retrieves variables from a file based on a specified modelica type (e.g., parameter, input, output).

    Parameters:
    file_path (str): Path to the file.
    dtype (str): Type of variable to extract ('parameter' by default).

    Returns:
    list: A list of tuples representing the variables found.
    """
    # lines = get_file_lines(file_path)
    # input_string = convert_lines_to_string(lines)
    parameters = extract_variables(file_path, dtype)
    return parameters

def extract_default_class_from_model(file_path, folder='Sources', instance='sources', ignore_prefix=False):
    """
    Extracts class declarations matching specified patterns in a model file.

    Parameters:
    file_path (str): Path to the file to read.
    folder (str): Name of the folder or category to search within (e.g., 'Sources', 'Models').
    instance (str): Name of the instance to match (e.g., 'sources').
    ignore_prefix (bool): If True, allows matching classes even if 'redeclare' and 'replaceable' keywords are absent.

    Returns:
    list: A list of tuples where each tuple contains matches found for the specified classes.
    
    TODO: Could add option for enforcing redeclare or r
    """

    if ignore_prefix:
        pattern = r'(?:\b(redeclare|replaceable)\b\s+)?\b{}\b\.(\w+)\s+\b{}\b'.format(folder, instance)
    else:
        pattern = r'\b(?:redeclare|replaceable)\b\s+.*\b{}\b.(\w+)\s+\b{}\b'.format(folder, instance)

    with open(file_path, 'r') as file:
        content = file.read()

    matches = re.findall(pattern, content)
    return matches

def apply_instance_naming_conventions(name):
    """
    Applies naming conventions for instance names.

    Parameters:
    name (str): The original name.

    Returns:
    str: The name converted to follow conventions (lowercase abbreviation or lowercased first letter).
    """
    if name.isupper():
        # Abbreviations are all lowercase for the the instance (e.g., CDU -> cdu)
        name = name.lower()
    else:
        # All instances are lower case first letter
        name = name[0].lower() + name[1:]
    return name

def search_log_file_reverse(file_path, search_text):
    """
    Searches a log file for a specific text in reverse (from the end of the file).
    It reads the file in chunks and processes the lines backward.
    
    Parameters:
    file_path (str): Path to the log file to search.
    search_text (str): The text to search for in the log file.
    
    Returns:
    None: Prints the line number where the text is found.
"""

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Set file pointer to the end of the file
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        buffer = bytearray()
        buffer_size = 1024
        offset = 0
        line_number = 0
        found_line = -1
        
        while offset < file_size:
            # Calculate how much to read
            read_size = min(buffer_size, file_size - offset)
            offset += read_size
            
            # Move file pointer back
            file.seek(file_size - offset)
            
            # Read the data and prepend to the buffer
            buffer = file.read(read_size) + buffer
            
            # Split the buffer into lines
            lines = buffer.split(b'\n')
            
            # Process lines in reverse
            for i in range(len(lines)-1, -1, -1):
                line = lines[i].decode(errors='ignore')
                line_number += 1
                if search_text in line:
                    found_line = line_number
                    break
            if found_line != -1:
                break
            # Keep the last part of the buffer (incomplete line) for the next read
            buffer = lines[0]
        
        if found_line != -1:
            print(f'\n"{search_text}" found at line {line_number} in file "{file_path}"\n')

if __name__ == "__main__":
    
    file_path = '../../../methods/modelica/TemplatesCSM/Templates/Structure.mo'
    file_path = r'../../../examples/modelica/GenericDatacenter/Systems/Datacenter/Systems/CoolingBlock/Systems/Cabinet/Sources/v0.mo'
    parameters = get_variable_by_type(file_path, 'input')
    print(parameters)

    