# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

import pathlib
from languages.modelica.methods import ModelicaMethods
from languages.julia.methods import JuliaMethods
from helper_functions import Loader

class AutoCSM:
    """
    AutoCSM class to automate the creation of simulation architectures and models.

    Attributes:
        language (str): Programming language for model generation ('modelica', 'julia').
        architecture (str): Architecture type for the system ('nested').
        terminal_animation (bool): Whether terminal animations are shown during processing.
        input_specification (str): Path to the input specification file.
        output_path (str): Path to store output files.
        project_path (str): Path to the project directory.
        model_path (str): Path to the output directory of model created during create_model().
    """

    # Class-level constant for language methods
    LANGUAGE_METHODS = {
        'modelica': ModelicaMethods,
        'julia': JuliaMethods
        }
 
    # ARCHITECTURES = ['nested'] # at level of the language
    def __init__(self, language: str = 'modelica', architecture: str = 'nested', terminal_animation: bool = True):
        self._language = None
        self._architecture = None
        self._terminal_animation = None
        self._input_specification = None
        self._output_path = None
        self._project_path = None
        self._project_name = None
        
        # Internal variables
        self._model_path = None
        
        # Setting via the property to validate.
        self.language = language
        self.architecture = architecture
        self.terminal_animation = terminal_animation
        
    @property
    def terminal_animation(self) -> str:
        """Returns the terminal_animation setting."""
        return self._terminal_animation

    @terminal_animation.setter
    def terminal_animation(self, value: bool) -> None:
        """Sets the terminal_animation."""
        self._terminal_animation = value
        
    @property
    def language(self) -> str:
        """Returns the current language setting."""
        return self._language

    @language.setter
    def language(self, value: str) -> None:
        """Sets the language for model generation, with validation."""
        if value not in self.LANGUAGE_METHODS:
            raise ValueError(f"Unsupported language: {value}")
        self._language = value
        self._language_method = self.LANGUAGE_METHODS[value](self)

    @property
    def architecture(self) -> str:
        """Returns the current architecture setting."""
        return self._architecture

    @architecture.setter
    def architecture(self, value: str) -> None:
        """Sets the architecture type."""
        self._architecture = value

    @property
    def input_specification(self) -> str:
        """Returns the input specification path."""
        return self._input_specification

    @input_specification.setter
    def input_specification(self, path: str) -> None:
        """Sets and validates the input specification file path."""
        if not pathlib.Path(path).is_file():
            raise FileNotFoundError(f"Input specification file not found: {path}")
        self._input_specification = path
        
    @property
    def output_path(self) -> str:
        """Returns the output directory path."""
        return self._output_path

    @output_path.setter
    def output_path(self, path: str) -> None:
        """Sets and validates the output directory path."""
        output_dir = pathlib.Path(path)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist
        self._output_path = output_dir.as_posix()
        
    @property
    def model_path(self) -> str:
        """Returns the output directory path."""
        return self._model_path
    
    @model_path.setter
    def model_path(self, path: str) -> None:
        """Sets the path to the model file."""
        self._model_path = path

    @property
    def project_path(self) -> str:
        """Returns the project path."""
        return self._project_path

    @project_path.setter
    def project_path(self, path: str) -> None:
        """Sets the project path, ensuring it's not 'package.mo'. Updates project_name if name doesn't match path"""
        temp = pathlib.Path(path).resolve()
        if temp.name == "package.mo":
            temp = temp.parent
        self._project_path = temp.as_posix()
        if self._project_name != temp.stem:
            print(f'Updating project name to match project path. Changed {self._project_name} to {temp.stem}')
            self._project_name = temp.stem
             
    @property
    def project_name(self) -> str:
        """Returns the project name."""
        return self._project_name

    @project_name.setter
    def project_name(self, name: str) -> None:
        """Sets the project name."""
        self._project_name = name
                    
    def _execute_with_animation(self, message: str, method, *args, **kwargs):
        """
        Executes a method with an optional terminal animation.
        
        Args:
            message (str): The message to display during animation.
            method (callable): The method to be executed.
        """
        if self.terminal_animation:
            with Loader(message):
                return method(*args, **kwargs)
        else:
            print(message)
            return method(*args, **kwargs)

    def create_architecture(self, *args: tuple, **kwargs: dict) -> None:
        """
        Creates the architecture based on the selected language and architecture.
        
        The output project architecture name is deterined from the project name if provided else the JSON file.

        Args:
            *args: Additional positional arguments passed to the architecture creation method.
            **kwargs: Additional keyword arguments passed to the architecture creation method.
        """
        try:
            return self._execute_with_animation("Creating the architecture...",
                                                self._language_method.create_architecture, *args, **kwargs)
        except Exception as e:
            print(f"Failed to create the architecture: {str(e)}")
            raise

    def create_model(self, model_name='Simulator.mo', *args: tuple, **kwargs: dict) -> None:
        """
        Creates the model for simulation.

        Args:
            *args: Additional positional arguments passed to the model creation method.
            **kwargs: Additional keyword arguments passed to the model creation method.
        """
        self.model_path = pathlib.Path.as_posix(pathlib.Path(self.output_path) / model_name)
        
        try:
            return self._execute_with_animation("Creating the model...",
                                                self._language_method.create_model, *args, **kwargs)
        except Exception as e:
            print(f"Failed to create the model: {str(e)}")
            raise

    def create_setup(self, *args: tuple, **kwargs: dict) -> None:
        """
        Creates the setup file for the simulation model.

        Args:
            *args: Additional positional arguments passed to the model creation method.
            **kwargs: Additional keyword arguments passed to the model creation method.
        """        
        try:
            return self._execute_with_animation("Creating the setup file...",
                                                self._language_method.create_setup, *args, **kwargs)
        except Exception as e:
            print(f"Failed to create the setup file: {str(e)}")
            raise
            
    def create_fmu(self, *args: tuple, **kwargs: dict) -> None:
        """
        Creates the Functional Mock-up Unit (FMU).

        Args:
            *args: Additional positional arguments passed to the FMU creation method.
            **kwargs: Additional keyword arguments passed to the FMU creation method.
        """
        try:
            return self._execute_with_animation("Creating the FMU...",
                                                self._language_method.create_fmu, *args, **kwargs)
        except Exception as e:
            print(f"Failed to create the FMU: {str(e)}")
            raise

if __name__ == "__main__":

    # Instantiate AutoCSM
    csm = AutoCSM(language='modelica', architecture='nested')

    # Load the JSON specification
    csm.input_specification = '../examples/json/input_specification_v0.json'

    # Set the path to output created files
    csm.output_path = '../temp'

    csm.project_name = 'GenericDatacenter'
    
    # This line creates a project with a file structure for the specified language and architecture
    csm.create_architecture() # Useful if a project is being created from scratch
    
    # Set the path to the project which uses an AutoCSM language method 
    csm.project_path = '../examples/modelica/GenericDatacenter' + csm.project_name

    # Create the model for export to FMU (i.e., Simulator.mo)
    csm.create_model(uniform=[False, False])
    # Note this does not specify a solver in the model file. That is added in create_FMU.

    # Model dependencies: List of libraries needed for FMU generation
    dependencies = [
        r'../../../Modelica/TRANSFORM-Library/TRANSFORM/package.mo'
        ]
    
    # Generate the FMU (i.e., Simulator.fmu)
    csm.create_fmu(dependencies, experimentSettings={'solver':'Sdirk34hw','tolerance':1e-5})