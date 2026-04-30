Go to [FASTER portal](https://portal-faster.hprc.tamu.edu/pun/sys/dashboard)

Go to `Interactive Apps` then `JupyterLab`. 

Choose `Type of Environment` as `Tamu ModuLair (Python virtual venv)`

Choose 'monai_FASTER` or your own venve under `TAMU ModuLair env`

Check `Select if you want to work in group venve directory` if using group venve

Clikc 'Lauch` and wait until it is launched.

Go to JupyterLab. In the terminal, activate the venv and go the data directory:
```
source activate_venv monai_faster

cd /scratch/group/orbit_seg/data/orbit_data
```

Run Monai commands

Currently working set up: >= 12 CPU cores and >= 200 GB RAM


## Submit a batch job
Open FASTER Shell
```
cd /path/to/slurm/batch/file
```
[Sumbit a batch job tutorial]()

Here is a slurm file recently sent for testing 'train_monai_nnunet_5epochs.slurm'
```
#!/bin/bash
#SBATCH --job-name=orbit_nnunet_5ep
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=200G
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --output=orbit_nnunet_5ep.%j.out
#SBATCH --error=orbit_nnunet_5ep.%j.err
#SBATCH --mail-type=ALL

source activate_venv monai_faster

cd /scratch/group/orbit_seg/data/orbit_data || exit 1

python -m monai.apps.nnunet nnUNetV2Runner train_single_model \
    --input_config "./input.yaml" \
    --config "3d_fullres" \
    --fold 0 \
    --trainer_class_name "nnUNetTrainer_5epochs"

```

In FASTER shell, submit the job:
```
sbatch train_monai_nnunet_5epochs.slurm
```
