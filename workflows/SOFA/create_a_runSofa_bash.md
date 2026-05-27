```
SOFA_ROOT=/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux \
PYTHONPATH=/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH \
/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux/bin/runSofa-25.12.99 -l SofaPython3 -g qglviewer \
/home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/test_roi_select.py
```

In Linux, create a bash to runSofa for v25.12.99 unzipped version as:

```
#!/usr/bin/env bash
set -e

export SOFA_ROOT="/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux"
export PYTHONPATH="$SOFA_ROOT/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH"

export SOFA_TIMER_ALL=10

GUI="${SOFA_GUI:-imgui}"

"$SOFA_ROOT/bin/runSofa-25.12.99" -l SofaPython3 -g "$GUI" "$@"
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


## Enable AdvancedTimer performance tracker

First way is to directly add AdvancedTimer wrappers in the runSofa command as a generic way:
```
SOFA_GUI=batch ./run_sofa.sh \
  -a \
  --computationTimeSampling 5 \
  --computationTimeAtBegin \
  --computationTimeOutputType ljson \
  /home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_restoration_scene_debug.py \
  > /home/zhang/Documents/mesh_select/updated_sample_data_debug/logs/restoration_timer.ljson
```
or
```
"$SOFA_ROOT/bin/runSofa-25.12.99" \
  -l SofaPython3 \
  -g batch \
  -a \
  --computationTimeSampling 5 \
  --computationTimeAtBegin \
  --computationTimeOutputType ljson \
  /home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_restoration_scene_debug.py \
  > /home/zhang/Documents/mesh_select/updated_sample_data_debug/logs/restoration_timer.ljson
```

or use GUI
```
"$SOFA_ROOT/bin/runSofa-25.12.99" \
  -l SofaPython3 \
  --computationTimeSampling 5 \
  --computationTimeAtBegin \
  --computationTimeOutputType ljson \
  /home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_restoration_scene_debug.py \
  > /home/zhang/Documents/mesh_select/updated_sample_data_debug/logs/restoration_timer.ljson
```

In the command:
```
-g batch: no GUI, better for timing #can be removed with `-a` for manually starting animation in the gui
-a: start animation automatically
--computationTimeSampling 5: print timing every 5 animation steps
--computationTimeAtBegin: include init timing
--computationTimeOutputType ljson: easier to parse later than plain stdout
```

Second way is to create a bash dedicated to the tracker:
```
#!/usr/bin/env bash
set -e

export SOFA_ROOT="/home/zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux"
export PYTHONPATH="$SOFA_ROOT/plugins/SofaPython3/lib/python3/site-packages:$PYTHONPATH"

"$SOFA_ROOT/bin/runSofa-25.12.99" \
  -l SofaPython3 \
  -g batch \
  -a \
  --computationTimeSampling "${SOFA_TIMER_SAMPLING:-5}" \
  --computationTimeAtBegin \
  --computationTimeOutputType "${SOFA_TIMER_OUTPUT:-ljson}" \
  "$@"
```

And run:
```
./runSofa_tracker.sh \
  /home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/sofa_restoration_scene_debug.py \
  > /home/zhang/Documents/mesh_select/updated_sample_data_debug/logs/restoration_timer.ljson
```
