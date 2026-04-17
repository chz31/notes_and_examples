### Create a venv in TAMU FASTER for MONAI:

Create a venv with Pytorch 2.7
```
create_venv monai_faster -g orbit_seg -t "GCC/13.2.0 OpenMPI/4.1.6 PyTorch/2.7.0 scikit-learn/1.4.0 scikit-image/0.24.0 SimpleITK/2.5.2 graphviz-python/0.20.1 NiBabel/5.3.2 Seaborn/0.13.2 imagecodecs/2024.6.1 YACS/0.1.8 tqdm/4.66.2 einops/0.8.0 JupyterLab/4.2.0 typing-extensions/4.10.0"
```
There is no need to pip install jupyter.

Activate the venv
```
source activate_venv monai_faster
```

Install monai, nnunet, and dependencies
```
pip install numexpr==2.8.7 click==8.1.7 torch==2.7.0 monai fire nnunetv2 hiddenlayer
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
