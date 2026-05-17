# Datacenter Cooling model

A thermo-fluid modeling framework developed using open-source Modelica libraries using the 
commercial Dymola IDE to model the cooling system for the Frontier supercomputer at Oak 
Ridge National Laboratory. This framework can be extended to other liquid-cooled systems 
and is part of ExaDigit—an open-source framework for developing comprehensive digital twins 
of liquid-cooled supercomputers. The model is dependent on the AutoCSM workflow wherein the 
Dymola Python interface is used to create a Functional MockUp Interface (FMU) of templated 
models from the cooling library using a JSON-based input specification file. The exported 
FMU can be run with either default values of required inputs or time-series values. 24 hour 
timeseries data of the central energy plant for 04/07/24 has been provided to validate the 
model. Please note that the system load data is calculated using the heat load from the 
central energy plant data. A more accurate representation of the system load is not 
publicly available.

## Requirements
- Dymola IDE
- Modelica Libraries
  - ORNL [TRANSFORM Library](https://github.com/ORNL-Modelica/TRANSFORM-Library)
  - ORNL [AutoCSM Library](https://code.ornl.gov/exadigit/AutoCSM)
  - LBNL [Buildings Library](https://github.com/lbl-srg/modelica-buildings)

# To Run
- Clone the repository
- Open `setup.mos` in a text editor and update the library locations (if needed).
- Open Dymola
  - On the `Simulation` tab, run the script `setup.mos` or load the libraries manually
- Export the FMU: python run_auto_csm.py
- Run the FMU: python run_fmu.py

## Recommended Dymola Flags
 _Note these are automatically set via AutoCSM._
- Copy paste to Dymola command line for performance improvement in editor
```
Advanced.Define.GlobalOptimizations = 2;
Advanced.Translation.SparseActivate = true;
Advanced.Translation.SparseActivateIntegrator = true;
Advanced.Translation.SparseActivateSystems = true;
Advanced.Translation.ODEJacobianForDiscrete = true;
```

## Authors:
Vineet Kumar (kumarv@ornl.gov), Oak Ridge National Laboratory.\
Michael Scott Greenwood (greenwoodms@ornl.gov), Oak Ridge National Laboratory.

## Acknowledgements:
Wesley Brewer (brewerwh@ornl.gov), Oak Ridge National Laboratory.\
Wesley Williams (williamswc@ornl.gov), Oak Ridge National Laboratory. \
Nathan Parkison (parkisonjn@ornl.gov), Oak Ridge National Laboratory. \
David Grant (grantdr@ornl.gov), Oak Ridge National Laboratory.

# Citation:
If you use ExaDigiT and/or datacenterCoolingModel in your research, please cite our work:

**ExaDigit**:

    @inproceedings{inproceedings,
    title={A Digital Twin Framework for Liquid-cooled Supercomputers as Demonstrated at Exascale}, 
    author={Brewer, Wesley and Maiterth, Matthias and Kumar, Vineet and Wojda, Rafal and Bouknight, Sedrick and Hines, Jesse and Shin, Woong and Greenwood, Scott and Grant, David and Williams, Wesley and Wang, Feiyi},
    booktitle={SC24: International Conference for High Performance Computing, Networking, Storage and Analysis},
    pages={1--18},
    year={2024},
    organization={IEEE}
    }

**datacenterCoolingModel**:

    @inproceedings{datacenterCoolingModel,
    title={Thermo-fluid Modeling Framework for Supercomputer Digital Twins: Part 1, Fluid Modeling Framework for Supercomputer Digital Twins: Part 1, Demonstration at Exascale},
    author={Kumar, V. and Greenwood, S. and Brewer, W. and Williams, W. and Grant, D. and Parkison, N.},
    booktitle={America Modelica Conference},
    pages={199--207},
    year={2024},
    organization={Modelica Association}
    doi={10.3384/ECP207 199};
    url={https://ecp.ep.liu.se/index.php/modelica/article/view/1145/1052}
    }

**Software**: 

    @misc{doecode_133738,
    title = {datacenterCoolingModel},
    author = {Kumar, Vineet and Greenwood, Michael S.},
    abstractNote = {ExaDigiT is a framework for developing comprehensive digital twins of liquid-cooled supercomputers, which has three main modules: (1) a python-based Resource Allocator and Power Simulator (RAPS), (2) a Modelica-based Thermo-Fluidic cooling model, and (3) a C++-based augmented reality model built on Unreal Engine 5. The Modelica-based cooling model is primarily built-on the open-source Transient Simulation Framework of Reconfigurable Models (TRANSFORM) library and the soon to be open-source autocsm library. The library follows the templating architecture developed in the TRANSFORM and the autocsm libraries. This tool can be easily extended to model other Frontier-like liquid cooled supercomputers.},
    }

## License:

ExaDigiT/datacenterCoolingModel is distributed under the terms of both the MIT license and the Apache License (Version 2.0).  
Users may choose either license, at their discretion.  

All new contributions must be made under both the MIT and Apache-2.0 licenses.  
See LICENSE-MIT, LICENSE-APACHE, and COPYRIGHT.txt for details.  

SPDX-License-Identifier: (Apache-2.0 OR MIT)  