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

Go to Interactive Apps at the FASTER portal, and open Jupyter Lab.

Select 'TAMU Modulair' for the "Type of Environment"

Select the create venv under the "TAMU Modulair environment"

Open JupyterLab


### Create a group venv (beta):

Create a group venv:
```
create_venv monai_group -t "GCC/13.2.0 OpenMPI/4.1.6 PyTorch/2.7.0" -g orbit_seg
```
