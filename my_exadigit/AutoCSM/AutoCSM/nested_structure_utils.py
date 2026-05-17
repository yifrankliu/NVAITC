# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

def is_not_nested(lst):
    """
    Checks if a list is not nested, i.e., none of its elements are lists.
    
    Parameters:
    lst (list): The list to check.
    
    Returns:
    bool: True if the list is not nested, False otherwise.
    
    Examples:
    >>> is_not_nested([1, 2, 3, 4, 5])
    True
    >>> is_not_nested([1, 2, [3, 4], 5])
    False
    """

    return all(not isinstance(i, list) for i in lst)

def length_of_lowest_list(nested_list):
    # Base case: if the input is not a list, return None (no list found)
    if not isinstance(nested_list, list):
        return None
    
    # If it's a list of non-lists, return its length
    if all(not isinstance(i, list) for i in nested_list):
        return len(nested_list)
    
    # Otherwise, recursively find the length of the lowest list
    lengths = [length_of_lowest_list(i) for i in nested_list if isinstance(i, list)]
    
    # Filter out None values and return the maximum length found
    lengths = [length for length in lengths if length is not None]
    return max(lengths, default=None)
    
def to_lowercase_strings(nested_list):
    """
    Recursively converts all elements in a nested list to lowercase strings.
    
    Example:
    input_list = [1, ['A', 'B'], [['C', 2], 'D']]
    result = to_lowercase_strings(input_list)
    print(result)  # Output: ['1', ['a', 'b'], [['c', '2'], 'd']]
    """
    if isinstance(nested_list, list):
        return [to_lowercase_strings(element) for element in nested_list]
    else:
        return str(nested_list).lower()
    
def set_structure_parameters(data, default_values):
    """
    Sets structure parameters based on provided data and default values.
    
    Example:
    data = {'Structure': {'useParallel': True}}
    default_values = {'n':1, 'useParallel':False}

    result = set_structure_parameters(data, default_values)
    print(result)  # Output: {'n': 1, 'useParallel': 'true'}
    """
    structure_parameters = {}
    if 'Structure' in data.keys():
        for key, val in default_values.items():
            if key in data['Structure'].keys():
                # Found, use provided value
                temp_val = data['Structure'][key]
                if key == 'useParallel':
                    temp_val = str(temp_val).lower()
                structure_parameters[key] = temp_val
            else:
                # Not found, use default value
                structure_parameters[key] = val
    else:
        # Structure not in dict, use with defaults
        for key, val in default_values.items():
            structure_parameters[key] = val
            
    return structure_parameters

def get_first_value(nested_list):
    """
    Recursively finds the first non-list value in a nested list.
    
    Example:
    nested_list = [[[1, 2], 3], [4, 5]]
    result = get_first_value(nested_list)
    print(result)  # Output: 1
    """
    if isinstance(nested_list, list):
        for element in nested_list:
            value = get_first_value(element)
            if value is not None:
                return value
    else:
        return nested_list

def create_nested_list(n, p, X):
    """
    Creates a nested list structure based on given parameters accounting for parallel logic.
    
    Example:
    n = [2, [3, 2]]
    p = [True, [False, True]]
    X = 'Y'
    result = create_nested_list(n, p, X)
    print(result)  # Output: [['Y'], [['Y', 'Y', 'Y'], ['Y']]]
    """
    def process(n_item, p_item):
        if isinstance(p_item, list):
            return [process(n_sub, p_sub) for n_sub, p_sub in zip(n_item, p_item)]
        else:
            return [X] if p_item else [X] * n_item
    return process(n, p)

def generate_key_strings(struct, key_path, var):
    """
    Generates key strings based on the structure and given path.
    
    Example:
    struct = [[1, 2], [3, 4]]
    key_path = 'level1.level2'
    var = 'value'
    result = generate_key_strings(struct, key_path, var)
    print(result)  # Output: ['level1_1_level2_1_value', 'level1_1_level2_2_value', 'level1_2_level2_1_value', 'level1_2_level2_2_value']
    """
    def traverse(current_struct, current_indices):
        if not isinstance(current_struct, list):
            path_elements = key_path.split('.')
            indexed_path = [f"{elem}_{idx}" for elem, idx in zip(path_elements, current_indices)]
            return [f"{'_'.join(indexed_path)}_{var}"]
        
        result = []
        for i, item in enumerate(current_struct, 1):
            result.extend(traverse(item, current_indices + [i]))
        return result

    return traverse(struct, [])

def replace_struct_values(struct, values):
    """
    Replaces values in a nested list structure with values from a list.
    
    Example:
    struct = [[1, 2], [3, 4]]
    values = ['a', 'b', 'c', 'd']
    result = replace_struct_values(struct, values)
    print(result)  # Output: [['a', 'b'], ['c', 'd']]
    """
    def replace_recursive(current_struct, output_iter):
        if not isinstance(current_struct, list):
            return next(output_iter)
        
        return [replace_recursive(item, output_iter) for item in current_struct]

    output_iter = iter(values)
    return replace_recursive(struct, output_iter)

def replace_struct_values_expand(struct, values):
    '''
    Recursively traverses the structure and replacing the elements with the values from the list truncating the value list.
    
    Example:
    struct = [[['Y'], ['Y', 'Y', 'Y']], [['Y'], ['Y', 'Y', 'Y']]]
    values = [1, 2, 4]
    expanded_list = expand_values(values, struct)
    print(expanded_list)  # Output: [[[1], [1, 2, 4]], [[1], [1, 2, 4]]]
    '''
    def fill(substructure):
        nonlocal index
        if isinstance(substructure, list):
            if all(not isinstance(item, list) for item in substructure):
                # Reset index when starting a new lowest-level list
                index = 0
            return [fill(item) for item in substructure]
        else:
            result = values[index]
            index = (index + 1) % len(values)
            return result

    index = 0
    return fill(struct)

def get_nested_list_length(struct):
    """
    Get the total size (leaf nodes) of a nested list.
    
    Example:
    struct = [[1, 2], [3, [4, 5]]]
    result = get_nested_list_length(struct)
    print(result)  # Output: 5
    """
    def count_recursive(current_struct):
        if not isinstance(current_struct, list):
            return 1
        return sum(count_recursive(item) for item in current_struct)
    
    return count_recursive(struct)

def same_dimensions(lst1, lst2):
    """
    Checks if two nested lists have the same dimensions.
    
    Example:
    lst1 = [[1, 2], [3, 4]]
    lst2 = [[5, 6], [7, 8]]
    result = same_dimensions(lst1, lst2)
    print(result)  # Output: True
    """
    if isinstance(lst1, list) and isinstance(lst2, list):
        if len(lst1) != len(lst2):
            return False
        return all(same_dimensions(sub1, sub2) for sub1, sub2 in zip(lst1, lst2))
    return not isinstance(lst1, list) and not isinstance(lst2, list)

def expand_data(data, default_structure_values, temp_struct=None, is_top_level=True):
    """
    Expands and validates the structure of input data based on default parameters.
    
    This function recursively processes the input data, expanding and validating
    the structure according to the provided default values.
    
    Example:
    data = {
    "Name": "Generic",
	"InstanceName":"simulator",
	"Structure":{"n":2},
	"ClassName":"v1",
	"SourceName":"NULL",
    "Systems": [{"Name": "Level_1",
			"InstanceName":"next",
			"Structure":{"n":1},
			"ClassName":"v0_a",
			"SourceName":"NULL",
            "Systems":[{}]
            }]
    }
    default_structure_values = {'n':1, 'useParallel':False}
    
    expand_data(data, default_values)
    print(data)
    {'Name': 'Generic',
     'InstanceName': 'simulator',
     'Structure': {'n': 2, 'useParallel': True},
     'ClassName': 'v1',
     'SourceName': 'NULL',
     'Systems': [{'Name': 'Level_1',
                  'InstanceName': 'next',
                  'Structure': {'n': [1], 'useParallel': [True]},
                  'ClassName': 'v0_a',
                  'SourceName': 'NULL',
                  'Systems': [{}]
                  }]
     }
    """
    
    default_structure = set_structure_parameters(data, default_structure_values)
    
    # Get top level
    n = data['Structure'].get('n', default_structure['n'])
    useParallel = data['Structure'].get('useParallel', False if default_structure['useParallel']=='false' else True)
        
    if is_top_level:
        if not isinstance(n, int): 
            raise ValueError(f'Input data "n" at InstanceName = {data["InstanceName"]} must be an integer but found: {n} -> {type(n)}')
        
        if not isinstance(useParallel, bool):
            raise ValueError(f'Input data "useParallel" at InstanceName = {data["InstanceName"]} must be a boolean but found: {useParallel} -> {type(useParallel)}')
            
        data['Structure']['n'] = n
        data['Structure']['useParallel'] = useParallel
        
    else:
        n_last = length_of_lowest_list(temp_struct)
        
        if isinstance(n, int): 
            # Simplified input with a single value (uniform across all)
            data['Structure']['n'] = replace_struct_values(temp_struct, [n]*get_nested_list_length(temp_struct))
        elif same_dimensions(n, temp_struct):
            # Complete structure provided as input
            data['Structure']['n'] = n
        elif is_not_nested(n) and (n_last == len(n) or n_last == 1):
            data['Structure']['n'] = replace_struct_values_expand(temp_struct, n)#*n_last)
        else:
            # Simplified input based on useParallel - input must match number above?
            raise ValueError(f'Structure at InstanceName = {data["InstanceName"]} is not supported: "n":{n}')
            
            
        if isinstance(useParallel, bool):
            # Simplified input with a single value (uniform across all)
            data['Structure']['useParallel'] = replace_struct_values(temp_struct, [useParallel]*get_nested_list_length(temp_struct))
        elif same_dimensions(useParallel, temp_struct):
            # Complete structure provided as input
            data['Structure']['useParallel'] = useParallel
        elif is_not_nested(useParallel) and (n_last == len(useParallel) or n_last == 1):
            data['Structure']['useParallel'] = replace_struct_values_expand(temp_struct, useParallel)#*n_last)
        else:
            raise ValueError(f'Structure at InstanceName = {data["InstanceName"]} is not supported: "useParallel":{useParallel}')
            
    # With updated entries, get struct for next level
    temp_struct = create_nested_list(data['Structure']['n'], data['Structure']['useParallel'], 'Y')
        
    systems = data.get('Systems', [])
    if systems and systems != [{}]:
        for i in range(len(systems)):
            # Go to next level
            sub_dict = data['Systems'][i]
            expand_data(sub_dict, default_structure_values, temp_struct, is_top_level=False)
    