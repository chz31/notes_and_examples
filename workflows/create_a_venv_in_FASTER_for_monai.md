### Create a venv in TAMU FASTER for MONAI:

Create a venv with Pytorch 2.7
```
create_venv mytorchvenv -t "GCC/13.2.0 OpenMPI/4.1.6 PyTorch/2.7.0 JupyterLab/4.2.0"

# Change mytorchvenv to your own venv name
```

Activate the environment
```
source activate_venv mytorchvenv
```

Install JupyterLab before using it:
```
pip install jupyterlab
```

Go to Interactive Apps at the FASTER portal, and open Jupyter Lab.

Select 'TAMU Modulair' for the "Type of Environment"

Select the create venv under the "TAMU Modulair environment"

Open JupyterLab

Remove venv
```
delete_venv monai_group
```

### Create a group venv (beta):

Create a group venv:
```
create_venv monai_group -t "GCC/13.2.0 OpenMPI/4.1.6 PyTorch/2.7.0" -g orbit_seg
```

Show versions of installed libaries, for example:
```
module spider matplotlib
```
Purge modules
```
ml purge
```

Check how to load a version of a library
```
module spider matplotlib/3.8.2

# showed:
# You will need to load all module(s) on any one of the lines below before the "matplotlib/3.8.2" module is available to load.
# GCC/13.2.0
```
Load the module as instructed:
```
module load GCC/13.2.0 matplotlib/3.8.2
```

Show file counts per directory (may take a while):
```
du - h --max-depth=1 $SCRATCH
```

Remove a folder using recursive `-r` (remove the folder and all its content) and `-f` option (force removing; no confirmation asked).
```
rm -rf $SCRATCH/.conda/*
```
