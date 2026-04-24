(Slicer nninteractive)[https://github.com/coendevente/SlicerNNInteractive]

## Linux

Create a conda ene if none existed:
```
conda create -n nninteractive python=3.12
conda activate nninteractive
```

Install nninteractive server
```
pip install nninteractive-slicer-server
```

Start the server
```
nninteractive-slicer-server --host 0.0.0.0 --port 1527
```

[**Issue caused by the new nnunetv2 2.7.0**](https://github.com/coendevente/SlicerNNInteractive/issues/89)
```
TypeError: nnUNetTrainer.build_network_architecture() takes from 4 to 5 positional arguments but 6 were given
```
Solution:
```
#Uninstall nnunet 2.7.0
pip uninstall nnunetv2 -y

# Installing an older version
pip install nnunetv2==2.6
```

Verify key package versions:
```
pip list | grep -E "nnunet|nninteractive|torch"
```

Switch to Slicer nninteractive module
