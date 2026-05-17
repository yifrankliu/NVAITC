# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

import json

def read_json(file_path):
    """
    Reads a JSON file from the specified file path and returns its contents as a dictionary.

    Parameters:
    file_path (str): The path to the JSON file.

    Returns:
    dict: The contents of the JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred: {e}")

def export_dict_to_json(data, file_path):
    import json
     # Exporting to a JSON string
    json_string = json.dumps(data, indent=4)

    # Exporting to a JSON file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
        
#%%
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
class Loader:
    def __init__(self, desc="Loading...", end="Done!", timeout=0.1, steps='cycle'):
        """
        Source: https://stackoverflow.com/questions/22029562/python-how-to-make-simple-animated-loading-while-process-is-running
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        
        Example usage:
        with Loader("Loading with context manager..."):
            for i in range(10):
                sleep(0.25)

        loader = Loader("Loading with object...", "That was fast!", 0.05).start()
        for i in range(10):
            sleep(0.25)
        loader.stop()
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        
        if steps == 'dots':
            self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        elif steps == 'cycle':
            self.steps = ['-', '/', '|', '\\']
        elif type(steps) == list:
            self.steps = steps
            
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{self.desc} {self.end}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()
       
#%%
import time

class TicToc:
    '''
    # Example usage:
    tt = TicToc()
    tt.tic()
    time.sleep(2)  # Simulate a delay
    tt.toc()
    '''
    def __init__(self):
        self.start_time = None

    def tic(self):
        self.start_time = time.time()
        print("Tic...")

    def toc(self):
        if self.start_time is None:
            print("Toc: You need to call tic() first!")
        else:
            elapsed_time = time.time() - self.start_time
            print(f"Toc: {elapsed_time:.6f} seconds")
            self.start_time = None  # Reset start_time if you want to measure multiple intervals

if __name__ == "__main__":
    with Loader("Loading with context manager..."):
        for i in range(10):
            sleep(0.25)

    loader = Loader("Loading with object...", "That was fast!", 0.1, steps='cycle').start()
    for i in range(10):
        sleep(0.25)
    loader.stop()
    
#%%
import numpy as np

def create_new_array_with_renamed_fields(original_array, field_mapping, keep_original=None):
    # Extract the original dtype names and formats
    original_dtype = original_array.dtype
    original_fields = original_dtype.names
    
    # If keep_original is None, keep all original fields
    if keep_original is None:
        keep_original = original_fields
    
    # Create a new dtype list with the new field names
    new_dtype = []
    for field in original_fields:
        if field in keep_original:
            new_dtype.append((field, original_dtype[field]))
    
    # Add the new fields to the dtype list
    for old_field, new_field in field_mapping:
        new_dtype.append((new_field, original_dtype[old_field]))
    
    # Create the new array with the new dtype
    new_array = np.empty(original_array.shape, dtype=new_dtype)
    
    # Copy the data from the original fields to the new fields
    for field in original_fields:
        if field in keep_original:
            new_array[field] = original_array[field]
    
    for old_field, new_field in field_mapping:
        new_array[new_field] = original_array[old_field]
    
    return new_array

#%%
import re

def convert_numbers_to_bracket_form(name):
    # Use regex to find numbers surrounded by underscores and replace with "[number]."
    new_name = re.sub(r'_(\d+)_', r'[\1].', name)
    return new_name
    
#%%
def overwrite_line_with_list(input_file, output_file, keyword, replacement, replaceLine=False):
    """
    Reads a text file, searches for a keyword, and either replaces the entire line or 
    just the keyword with the provided replacement. The modified content is saved to a new file.

    Parameters:
    -----------
    input_file : str
        The path to the input text file to be read.
    output_file : str
        The path to the output text file where the modified content will be written.
    keyword : str
        The keyword to search for in the lines of the text file.
    replacement : str or list of str
        The replacement content. If replacing a line, the replacement can be a string 
        or a list of strings (which will be joined with newline characters).
        If replacing the keyword within a line, this should be a string.
    replaceLine : bool, optional
        If True, replaces the entire line containing the keyword with the replacement content. 
        If False, only the keyword within the line is replaced. Defaults to False.

    Returns:
    --------
    None
    """
    # Open the input file for reading
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Replace the line containing the keyword with the replacement_list
    with open(output_file, 'w') as file:
        for line in lines:
            if keyword in line:
                if replaceLine:
                    # Write replacement in this line
                    file.write(replacement)
                else:
                   # Replace only the keyword in the line, keeping the rest of the line intact
                   new_line = line.replace(keyword, replacement)
                   file.write(new_line)
            else:
                # Write the line as-is if keyword not found
                file.write(line)
    