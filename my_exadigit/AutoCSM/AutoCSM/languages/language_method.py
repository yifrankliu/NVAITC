# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

import pathlib
from abc import abstractmethod 

class LanguageMethod:
    """
    A base class for methods that extend from different language methods, such as Modelica.

    This class provides basic structure and validation for methods that are extended 
    by specific language methods (e.g., Modelica). 
    
    Child classes must implement the following abstract methods:
        - create_architecture()
        - create_model()
        - create_fmu()
    
    Attributes:
        parent (AutoCSM): The parent AutoCSM object.
        BASE_PATH (Path): Base path where python methods are located (for relative path reconstruction).
        METHOD_PATH (Path): Path to the ExaDigiT language method implmentation.
        TEMPLATE_PATH (Path): Path to folder containing the template folder structure.
        STRUCTURE_PATH (Path): Path to the file defining the structure component.
        SUPPORTED_ARCHITECTURES (list): Supported architectures for the method.
        SUPPORTED_FMU_COMPILERS (list): Supported FMU compilers for the method.
    """
    
    BASE_PATH = pathlib.Path(__file__).parent
    METHOD_PATH = None # To be overridden by child classes
    TEMPLATE_PATH = None # To be overridden by child classes
    STRUCTURE_PATH = None # To be overridden by child classes
    
    SUPPORTED_ARCHITECTURES = []  # To be overridden by child classes
    SUPPORTED_FMU_COMPILERS = []  # To be overridden by child classes
    
    def __init__(self, parent):
        self.parent = parent

    def validate_architecture(self):
        """
        Validates if the current architecture is supported.
    
        Raises:
            ValueError: If the architecture is not supported.
        """
        if self.parent.architecture not in self.SUPPORTED_ARCHITECTURES:
            raise ValueError(f"Unsupported architecture: {self.parent.architecture}. "
                              f"Supported architectures are: {self.SUPPORTED_ARCHITECTURES}")
    
    def validate_fmu_compiler(self, compiler):
        """
        Validates if the FMU compiler is supported.
    
        Raises:
            ValueError: If the FMU compiler is not supported.
        """
        if compiler not in self.SUPPORTED_FMU_COMPILERS:
            raise ValueError(f"Unsupported FMU compiler: {compiler}. "
                             f"Supported compilers are: {self.SUPPORTED_FMU_COMPILERS}")

    def validate_and_convert_paths(self, paths: list) -> list:
        """
        Validates and converts a list of file paths to absolute paths.
        
        Args:
            paths (list): List of file paths (relative or absolute).
        
        Returns:
            list: List of validated absolute paths.
        
        Raises:
            FileNotFoundError: If any file path does not exist.
        """
        absolute_paths = []
        
        for path in paths:
            abs_path = pathlib.Path(path).resolve()
            if not abs_path.exists():
                raise FileNotFoundError(f"The file '{abs_path}' does not exist.")
            absolute_paths.append(abs_path.as_posix())
        
        return absolute_paths
    
    def _add_required_dependencies(self, dependencies: list = None):
        # Adds project package if not already in dependency list
        project_package = (pathlib.Path(self.parent.project_path) / 'package.mo').resolve()
        if project_package.as_posix() not in dependencies:
            dependencies.append(project_package.as_posix())
                
        # This avoids redefining the ExaDigiT method template if it already was included in the dependency in a different location (e.g., a customized version)
        exadigit_package  = self.METHOD_PATH if self.METHOD_PATH.parts[-1] == 'package.mo' else self.METHOD_PATH / 'package.mo'
        if '/'.join(list(exadigit_package.parts[-2:])) not in dependencies:
            dependencies.append(exadigit_package.as_posix())
        return dependencies
    
    @abstractmethod
    def create_architecture(self, template_folder: str = None, **kwargs):
        """
        Abstract method to create a language-supported architecture by copying 
        the template system structure.
        
        Args:
            template_folder (str, optional): Path to the template folder. If not 
            provided, uses the default TEMPLATE_FOLDER.
        
        Note:
            This method must be implemented by child classes to handle architecture
            creation specific to the language (e.g., Modelica, etc.).
        """

        # Validate the architecture
        self.validate_architecture()
        
        # Update input parameters
        template_folder = template_folder or self.TEMPLATE_FOLDER.as_posix()
        
        return template_folder
    
    @abstractmethod
    def create_model(self, structure_path: str = None, **kwargs):
        """
        Creates the model using the selected architecture.
        
        Args:
            structure_path (str, optional): Path to the model structure file. If not provided, uses teh default STRUCTURE_PATH.
            parent_class (str): The base example model for constructing the model.
            **kwargs: Additional keyword arguments passed to the method.
            
        Note:
            This method must be implemented by child classes to handle architecture
            creation specific to the language (e.g., Modelica, etc.).
        """
        
        # Validate the architecture
        self.validate_architecture()
        
        # Update input parameters
        structure_path = structure_path or self.STRUCTURE_PATH.as_posix()
        
        return structure_path
    
    @abstractmethod
    def create_setup(self, dependencies: list = None, **kwargs):
        """
        Generates an setup file (e.g., setup.mos) to simplify use of the generated model (e.g., Simulator.mo) in non-fmu form.
        
        Args:
            dependencies Optional[List[str]] List of dependencies required for FMU generation. If not provided, uses defaults.
            **kwargs: Additional keyword arguments passed to the method.
            
        Note:
            This method must be implemented by child classes to handle architecture
            creation specific to the language (e.g., Modelica, etc.).
        """            

        # Verify dependencies are valid
        if dependencies is not None:
            dependencies = self.validate_and_convert_paths(dependencies)
        
        # Update input parameters
        dependencies = dependencies or []
        
        return dependencies
    
    @abstractmethod
    def create_fmu(self, dependencies: list = None, compiler: str = '', experimentSettings: dict = None, **kwargs):
        """
        Generates an FMU (Functional Mock-up Unit) using the specified compiler.
        
        Args:
            dependencies Optional[List[str]] List of dependencies required for FMU generation. If not provided, uses defaults.
            compiler (str): Compiler to use for FMU generation.
            experimentSettings (dict, optional): FMU experiment settings. Defaults to an empty dict.
            **kwargs: Additional keyword arguments passed to the method.
            
        Note:
            This method must be implemented by child classes to handle architecture
            creation specific to the language (e.g., Modelica, etc.).
        """
        # Validate the fmu compiler
        self.validate_fmu_compiler(compiler)
            
        # Verify dependencies are valid
        if dependencies is not None:
            dependencies = self.validate_and_convert_paths(dependencies)
        
        # Update input parameters
        dependencies = dependencies or []
        experimentSettings = experimentSettings or {}
                        
        return dependencies, experimentSettings
