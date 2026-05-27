```
SOFA_ROOT=/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux \
PYTHONPATH=/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH \
/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux/bin/runSofa-25.12.99 -l SofaPython3 -g qglviewer \
/home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/test_roi_select.py
```

In Linux, create a bash to runSofa for v25.12.99 unzipped version as:

```
#!/usr/bin/env bash

export SOFA_ROOT="/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux"
export PYTHONPATH="$SOFA_ROOT/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH"

export SOFA_TIMER_ALL=20

"$SOFA_ROOT/bin/runSofa-25.12.99" -l SofaPython3 -g imgui "$@"
```

`imgui` can be switched to `qglviewer` if not available.

Optionlly, add 'export LD_LIBRARY_PATH' such as `export LD_LIBRARY_PATH="$PIXI_PROJECT_ROOT/.pixi/envs/default/lib:$SOFA_ROOT/lib:$LD_LIBRARY_PATH"` if runSofa could not find it.

`export SOFA_TIMER_ALL=10` export run time for 20 steps. It can be disabled by setting the value to `0`.

Grant permission by `chmod -x` if needed:
```
chmod +x ./bash_scripts/runsofa_bash
~/envs/sofa_scripts/runsofa2512 /path/to/scene.py
```

Run the bash explicity
```
./bash_scripts/runsofa2512 ./sofa_experiments/sofa_retraction_scene_debug.py

```
