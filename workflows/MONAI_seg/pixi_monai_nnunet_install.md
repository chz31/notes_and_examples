Install Pixi
```
curl -fsSL https://pixi.sh/install.sh | sh
source ~/.bashrc

pixi --version
```

Create a clean pixi project
```
mkdir -p ~/monai_nnunet_pixi
cd ~/monai_nnunet_pixi

pixi init
pixi add python=3.12 pip
```

Enter pixi environment
```
pixi shell
```

Verify Python & Pip are coming from pixi
```
which python
python --version
which pip
```
Expect to see path like `~/monai_nnunet_pixi/.pixi/envs/default/bin/`

Check gpu
```
nvidia-smi
```

Install pytorch with specific torchvision and torchaudio versions to avoid conflict [pytorch installation](https://pytorch.org/get-started/previous-versions/)

Verify torch & cuda
```
python - <<'EOF'
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("torch cuda:", torch.version.cuda)
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
EOF
```

Install monai & nnunet
```
python -m pip install monai
python -m pip install nnunetv2
```

Install dependencies
```
python -m pip install nibabel SimpleITK scikit-image pandas matplotlib tensorboard tqdm
```

Check if nnunetv2 change torch version
```
python - <<'EOF'
import torch, torchvision, torchaudio
print("torch:", torch.__version__)
print("torchvision:", torchvision.__version__)
print("torchaudio:", torchaudio.__version__)
print("cuda available:", torch.cuda.is_available())
print("torch cuda:", torch.version.cuda)
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
EOF
```
Expected output
```
torch: 2.7.1+cu126
torchvision: 0.22.1+cu126
torchaudio: 2.7.1+cu126
cuda available: True
torch cuda: 12.6
```

Also check:
```
python -m pip check
```
Expect to see `No broken requirements found.`

Leave pixi environment
```
exit
```

Reenter the environment
```
cd ~/monai_nnunet_pixi
pixi shell
```

If not entering the shell, direct using 'pixi run python' to run python apps. For example:
```
pixi run python -m monai.apps.nnunet nnUNetV2Runner --help
```

