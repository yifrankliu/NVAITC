# -*- coding: utf-8 -*-
"""
@author: Scott Greenwood

Copyright (c) 2024 UT-Battelle
Licensed under the terms of both the MIT license and the Apache License (Version 2.0).
Users may choose either license, at their discretion.
"""

import pathlib

from ..language_method import LanguageMethod
from . import create_model_nested
from . import create_fmu_dymola
from . import create_architecture
from helper_functions import overwrite_line_with_list

class ModelicaMethods(LanguageMethod):
    """
    Implements Modelica-specific methods for creating architecture, generating models, and building FMUs.
    
    Attributes:
        METHOD_PATH (Path): The path where the Modelica method to use is located.
        TEMPLATE_FOLDER (Path): Path to the folder containing the Modelica template system.
        STRUCTURE_PATH (Path): Path to the file defining the Modelica structure component.
        SUPPORTED_ARCHITECTURES (list): Architectures supported by Modelica.
        SUPPORTED_FMU_COMPILERS (list): FMU compilers supported by Modelica.
    """

    METHOD_PATH = (pathlib.Path(LanguageMethod.BASE_PATH) / '../../methods/modelica/TemplatesCSM').resolve()
    TEMPLATE_FOLDER = (METHOD_PATH / 'Templates/TemplateSystem').resolve()
    STRUCTURE_PATH = (METHOD_PATH / 'Templates/Structure.mo').resolve()

    SUPPORTED_ARCHITECTURES = ['nested']
    SUPPORTED_FMU_COMPILERS = ['dymola']
    
    def __init__(self, parent):
        super().__init__(parent)  # Call the parent class initializer
    
    def create_architecture(self, template_folder: str = None, **kwargs):
        """
        Creates the Modelica architecture by copying the template system structure.
        
        Args:
            template_folder (str, optional): Path to the template folder. If not provided, uses the default.
            **kwargs: Additional keyword arguments for creating the architecture.
        
        Raises:
            RuntimeError: If the architecture creation fails.
        """
        # Call the parent logic
        template_folder = super().create_architecture(template_folder)
        
        try:
            create_architecture.main(self.parent.input_specification,
                                              self.parent.output_path,
                                              template_folder,
                                              self.parent.project_name,
                                              self.parent.architecture)
        except FileNotFoundError as e:
            raise RuntimeError(f"Template not found: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create architecture: {str(e)}")
        
    def create_model(self, structure_path: str = None, parent_class: str = 'TemplatesCSM.BaseClasses.Tests.PartialTest', **kwargs):
        """
        Creates the Modelica model for the specified architecture.
        
        Args:
            structure_path (str, optional): Path to the model structure file. Defaults to self.STRUCTURE_PATH.
            parent_class (str): The base example model for constructing the model.
            uniform (list, optional): A list indicating uniform settings. Defaults to [True, True].
            **kwargs: Additional keyword arguments for model creation.
        
        Raises:
            RuntimeError: If the model creation fails.
        """
        # Call the parent logic
        structure_path = super().create_model(structure_path, **kwargs)
        
        try:
            if self.parent.architecture == 'nested':
                # Extract parameters from kwargs
                uniform = kwargs.pop('uniform', None)
                uniform = [True, True] if uniform is None or not uniform else uniform
                
                force_redeclare = kwargs.pop('force_redeclare', True)
                
                create_model_nested.main(self.parent.input_specification,
                                                  self.parent.project_path,
                                                  pathlib.Path(self.parent.project_path).name,
                                                  parent_class,
                                                  self.parent.model_path,
                                                  structure_path,
                                                  uniform,
                                                  force_redeclare)
            #TODO: Add new architecture methods here
        except FileNotFoundError as e:
            raise RuntimeError(f"File not found during model creation: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create model: {str(e)}")
            
    def create_setup(self, dependencies: list = None, compiler: str = 'dymola', **kwargs):
        """
        Generates an setup file (i.e., setup.mos).
        
        Args:
            dependencies (list[str], optional): List of dependencies required for FMU generation.
            **kwargs: Additional keyword arguments for FMU creation.
        
        Raises:
            RuntimeError: If FMU creation fails.
        """      
        # Verify dependencies
        dependencies = super().create_setup(dependencies, **kwargs)
        
        # Add required project and template dependencies
        dependencies = super()._add_required_dependencies(dependencies)

        # Add simulation file
        dependencies.append(pathlib.Path(self.parent.model_path).absolute().as_posix())
        
        if compiler == 'dymola' or compiler == 'omedit':
            temp = '../template_setup_dymola.mos' if compiler=='dymola' else '../template_setup_omedit.mos'
            template_path = (self.METHOD_PATH / temp).as_posix()
            output_path = (pathlib.Path(self.parent.model_path).parent / 'setup.mos').as_posix()
            replacement = '{' + ',\n\t\t'.join(f'"{dep}"' for dep in dependencies) + '}'
            overwrite_line_with_list(template_path, output_path, 'TODO_ADD_DEPENDENCIES_HERE', replacement)
        else:
            raise ValueError('Unsupported compiler for setup')
            
    def create_fmu(self, dependencies: list = None, compiler: str = 'dymola', experimentSettings: dict = None, **kwargs):
        """
        Generates an FMU using the specified compiler.
        
        Args:
            dependencies (list[str], optional): List of dependencies required for FMU generation.
            compiler (str, optional): Compiler to use for FMU generation. Defaults to 'dymola'.
            experimentSettings (dict, optional): FMU experiment settings. Defaults to an empty dict.
            **kwargs: Additional keyword arguments for FMU creation.
        
        Raises:
            RuntimeError: If FMU creation fails.
        """
        # Verify dependencies
        dependencies, experimentSettings = super().create_fmu(dependencies, compiler, experimentSettings, **kwargs)
    
        # Add required project and template dependencies
        dependencies = super()._add_required_dependencies(dependencies)
            
        try:
            if compiler == 'dymola':
                # Extract parameters from kwargs
                showwindow = kwargs.pop('showwindow', False)
                includeVariables = kwargs.pop('includeVariables', None)
                if includeVariables == []:
                    includeVariables = None
                    
                create_fmu_dymola.main(dependencies, 
                                                self.parent.model_path, 
                                                pathlib.Path(self.parent.output_path).resolve(),
                                                experimentSettings, 
                                                showwindow,
                                                includeVariables)
            #TODO: Add new fmu compiler methods here
        except FileNotFoundError as e:
            raise RuntimeError(f"Dependency file not found: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create FMU: {str(e)}")