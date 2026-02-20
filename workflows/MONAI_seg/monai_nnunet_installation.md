This doc summarizes the MONAI and nnUnet installation steps that have worked.

[Link to MONAI installation](https://github.com/Project-MONAI/tutorials/tree/main)

[Link to Monai-nnunet installation](https://github.com/Project-MONAI/tutorials/blob/main/nnunet/docs/install.md)

Create a conda environment with Python 3.12
```
conda create environment_name python=3.12 -y #change environment_name to a specific name

```

Activate conda environment
```
conda activate environment_name
```

Install dependencies
```
pip install -U pip
pip install -U matplotlib
pip install -U pandas
pip install -U notebook
```

Install Pytorch. Install [pytorch 2.6.0](https://pytorch.org/get-started/previous-versions/). Pytorch 2.7.0 also works.
```
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
```

Install MONAI<br>
```
# install latest monai (pip install monai)
pip install git+https://github.com/Project-MONAI/MONAI#egg=monai
```

Install more dependencies
```
# install dependencies
pip install fire nibabel
pip install "scikit-image>=0.19.0"
```

Install nnU-Net and dependencies
```
# install dependencies
pip install --upgrade git+https://github.com/MIC-DKFZ/acvl_utils.git
pip install --upgrade git+https://github.com/MIC-DKFZ/dynamic-network-architectures.git

# install nnunet
pip install nnunetv2

# install hiddenlayer (optional)
pip install --upgrade git+https://github.com/julien-blanchon/hiddenlayer.git
```
