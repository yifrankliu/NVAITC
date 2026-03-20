# ML Worklog

## Mar 19th
SINGLE COMMAND TO RUN DOCKER FMU: (base) yhkd@Macintosh-9 sustain-lc % docker run --platform linux/amd64 -it --rm -v ~/Desktop/NVAITC_files/sustain-lc:/workspace -w /workspace sustain-lc-env:latest bash
(base) root@bda759adb35d:/workspace# 

Created dockerfile_u to run lc-opt FMU using MAC. Created Linux container.

Pivoted from compiling my own OpenModelica FMU to work on ML layer first. To compile my own FMU, I will either have to wait for perost to resolve the ticket and ship v1.27.0, or I will have to try to fix the compiler myself. Instead, I've fetchewd the FMU from LC-opt to start developing the ML layer:

- To use LC-opt's FMU, set up conda environment with necessary dependencies in environment lc-opt-twin
    -To activate: conda activate lc-opt twin
- Compiled FMU and necessary environment, however FMU was originally built on Linux, currently running on linux container created on docker, sent email to Yale HPC to see if I can run it there as well.
- Many version difficulties with running on local machine. Waiting for Yale HPC access, currently running on Collab and getting started on ML layer.

## Current Solution: LC-Opt FMU Setup Guide
The LC_Frontier_5Cabinet_4_17_25.fmu contains binaries for linux64, win32, and win64 only.
Mac ARM64 cannot execute the FMU binary natively. Solution: run inside a Linux x86_64 Docker container.

---

### Prerequisites
- Docker Desktop installed and running
- sustain-lc repo cloned to your machine
- FMU file present in the sustain-lc directory

---

### One-Time Setup

#### 1. Start the Docker container
```bash
docker run --platform linux/amd64 -it --rm \
  -v ~/Desktop/NVAITC_files/sustain-lc:/workspace \
  -w /workspace \
  continuumio/miniconda3 bash
```
- `--platform linux/amd64` — forces x86_64 Linux architecture (matches FMU binary)
- `-v .../sustain-lc:/workspace` — mounts your local sustain-lc folder into the container
- `continuumio/miniconda3` — official Miniconda image with conda pre-installed
- Container is ephemeral: exits when you type `exit`

#### 2. Create and activate conda environment
```bash
conda create -n sustain-lc python=3.10 -y
conda activate sustain-lc
```

#### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install PyFMI via conda-forge
```bash
conda install -c conda-forge pyfmi -y
```
**Critical:** Use `conda install -c conda-forge` NOT `pip install pyfmi`.
- pip only has PyFMI 2.5 (2018) which fails to compile against modern FMIL
- conda-forge has PyFMI 2.13.0 with pre-built binaries — no compilation needed

#### 5. Verify FMU loads
```bash
python -c "
from pyfmi import load_fmu
fmu = load_fmu('LC_Frontier_5Cabinet_4_17_25.fmu')
print('FMU loaded successfully')
print('Model name:', fmu.get_name())
"
```
Expected output:
```
FMU loaded successfully
Model name: LC_Frontier_5Cabinet_4_17_25
```

---

#### Every Session (Steps to Repeat)
Each time you open a new terminal, the container is gone. Repeat:
```bash
# Step 1: Start container
docker run --platform linux/amd64 -it --rm \
  -v ~/Desktop/NVAITC_files/sustain-lc:/workspace \
  -w /workspace \
  continuumio/miniconda3 bash

# Step 2: Inside container
conda create -n sustain-lc python=3.10 -y  # only needed first time per container
conda activate sustain-lc
pip install -r requirements.txt            # only needed first time per container
conda install -c conda-forge pyfmi -y      # only needed first time per container
```

---

#### Making the Environment Persistent (Optional)
To avoid reinstalling every session, build a custom Docker image.

Create a file named `Dockerfile` in your sustain-lc directory:
```dockerfile
FROM --platform=linux/amd64 continuumio/miniconda3

WORKDIR /workspace

COPY requirements.txt .

RUN conda create -n sustain-lc python=3.10 -y && \
    conda run -n sustain-lc pip install -r requirements.txt && \
    conda run -n sustain-lc conda install -c conda-forge pyfmi -y

SHELL ["conda", "run", "-n", "sustain-lc", "/bin/bash", "-c"]
```

Build and run:
```bash
docker build -t sustain-lc-env .
docker run -it --rm -v ~/Desktop/NVAITC_files/sustain-lc:/workspace -w /workspace sustain-lc-env bash
```

---

## Why This Works
| Layer | Solution |
|-------|----------|
| FMU binary platform | linux/amd64 Docker container matches linux64 FMU binary |
| PyFMI installation | conda-forge pre-built binary, no compilation required |
| Dependencies | requirements.txt installs gymnasium, torch, stable-baselines3 |
| File access | Volume mount (-v) gives container access to FMU on your Mac |

---

## Known Limitations
- Container is ephemeral by default — reinstall required each session unless Dockerfile approach is used
- Yale HPC cluster (linux x86_64 native) is the preferred long-term compute environment
- Mac ARM64 cannot run the FMU binary natively regardless of Python setup