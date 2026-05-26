Open WSL in admin mode

Directly unzip SOFA v25.12.99, for example
```
mkdir -p ~/sofa
cd ~/sofa
unzip /mnt/c/Users/chi.zhang/Downloads/SOFA_v25.12.99-full_Linux.zip
```

Create a pixi venv:
```
cd pixi_env_folder

pixi init
pixi add python=3.12 pip numpy scipy
pixi shell

```

A few checks
```
find .pixi -name "libpython3.12.so.1.0"
python -c "import sys; print(sys.executable); import numpy as np; print(np.__version__)"
python -m pip --version
```

set SOFA paths from inside the pixi shell
```
export SOFA_ROOT=~/sofa/SOFA_v25.12.99_Linux
export LD_LIBRARY_PATH=$PIXI_PROJECT_ROOT/.pixi/envs/default/lib:$SOFA_ROOT/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$SOFA_ROOT/plugins/SofaPython3/lib/python3/site-packages:$PIXI_PROJECT_ROOT/.pixi/envs/default/lib/python3.12/site-packages:$PYTHONPATH
```

Then test whether SofaPython3 can now find libpython3.12 (optional)
```
ldd $SOFA_ROOT/plugins/SofaPython3/lib/libSofaPython3.so | grep python
```

Expected output similar to:
```
libpython3.12.so.1.0 => /home/chizhang/.../.pixi/envs/default/lib/libpython3.12.so.1.0
```

Run SOFA
```
$SOFA_ROOT/bin/runSofa-25.12.99 -l SofaPython3 -g imgui \
/mnt/c/Users/chi.zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_retraction_scene_debug.py
```

Or run a full length long command:
```
SOFA_ROOT=~/sofa/SOFA_v25.12.99_Linux \
LD_LIBRARY_PATH=$PIXI_PROJECT_ROOT/.pixi/envs/default/lib:~/sofa/SOFA_v25.12.99_Linux/lib:$LD_LIBRARY_PATH \
PYTHONPATH=~/sofa/SOFA_v25.12.99_Linux/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH \
~/sofa/SOFA_v25.12.99_Linux/bin/runSofa-25.12.99 -l SofaPython3 -g imgui \
/mnt/c/Users/chi.zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_retraction_scene_debug.py
```

Alternatively, install WSL Ubuntu 24.04 that uses py3.12
```
wsl -d Ubuntu-24.04
```

If encountered libpython not found error:
```
sudo apt update
sudo apt install unzip libpython3.12 libnss3 libglu1-mesa mesa-utils libgl1-mesa-dri
```

Test ldd $SOFA_ROOT/plugins/SofaPython3/lib/libSofaPython3.so | grep python
Expect to see `libpython3.12.so.1.0 => /usr/lib/..., not not found.`

**Make a launcher bash script to set up a sofa paths:**
```
mkdir -p ~/bin
nano ~/bin/runsofa2512
```

Inside the bash, put:
```
#!/usr/bin/env bash

export SOFA_ROOT="$HOME/sofa/SOFA_v25.12.99_Linux"
export PYTHONPATH="$SOFA_ROOT/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH"

"$SOFA_ROOT/bin/runSofa-25.12.99" -l SofaPython3 -g imgui "$@"
```

**If no generic py3.12, especially in a pixi env, the bash file should add LD_LIBRARY_PATH**
```
#!/usr/bin/env bash

export SOFA_ROOT="$HOME/sofa/SOFA_v25.12.99_Linux"
export LD_LIBRARY_PATH="$PIXI_PROJECT_ROOT/.pixi/envs/default/lib:$SOFA_ROOT/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$SOFA_ROOT/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH"

"$SOFA_ROOT/bin/runSofa-25.12.99" -l SofaPython3 -g imgui "$@"
```

If `~/bin` is not on the path, it can be manually added:
```
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Make the script executable:
```
chmod +x ~/bin/runsofa2512
```

Then runsofa can be directly executed as:
```
runsofa2512 /mnt/c/Users/chi.zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_retraction_scene_debug.py
```

Alternatively, the bash could be made everywhere:
```
mkdir -p ~/envs/sofa_scripts
nano ~/envs/sofa_scripts/runsofa2512
```
Then run explicitly:
```
~/envs/sofa_scripts/runsofa2512 /path/to/scene.py

#For, example
~/envs/sofa_scripts/runsofa2512 /mnt/c/Users/chi.zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_retraction_scene_debug.py
```
In this case, no need to run `chmod -x`

If permission denied (no need to add to the path):
```
chmod +x ~/envs/sofa_scripts/runsofa2512
~/envs/sofa_scripts/runsofa2512 /path/to/scene.py

```

