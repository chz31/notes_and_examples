This tutorial shows how to run a monai_nnunet workflow.

Link to the [official Monai-nnU-net tutorial](https://github.com/Project-MONAI/tutorials/tree/main/nnunet).

To run this tutorial, the images and labels, including the augmented copies should be put under three folders `imagesTr`, `imagesTs`, and `labelsTr` under a root folder, which was named as `monai_nn_tr` in previous tutorials.

A json format data list for the traning dataset `msd_monai_nnunet_tr_folds.json` should also be created (see [tutorial 03](https://github.com/chz31/notes_and_examples/blob/main/workflows/MONAI_seg/03_data_prep_for_monai_nnunet.md))

### 1. Prepare an `input.yaml` to configure the data list file and input and output directories.
Here is a sample [input.yaml](https://github.com/chz31/notes_and_examples/blob/main/workflows/MONAI_seg/msd_monai_nnunet_tr_folds.json) and its content:
```
modality: CT
datalist: "./msd_monai_nnunet_tr_folds.json" #path to the data list json file. 
dataroot: "./monai_nn_tr" #path to the folder containing raw images and labels.
nnunet_preprocessed: "./data_preprocessing/nnUNet_preprocessed" # directory for storing pre-processed data (optional)
nnunet_raw: "./data_preprocessing/nnUNet_raw_data_base" # directory for storing formated raw data (optional)
nnunet_results: "./results_test1/nnUNet_trained_models" # directory for storing trained model checkpoints (optional)
```
The last three lines are optional but still recommended. Putting `nnunet_preprocessed` 

**Note that on Windows, `/` needs to be changed to `\\`:** 
```
modality: CT
datalist: ".\\msd_monai_nnunet_tr_folds.json"
dataroot: ".\\monai_nnunet_tr"
nnunet_preprocessed: ".\\p\\nnUNet_preprocessed"
nnunet_raw: ".\\p\\nnUNet_raw_data_base"
nnunet_results: ".\\o\\nnUNet_trained_models"
```

### 2. Put the data list (json) file, and `input.ymal`, and the raw images and labels folder into the same directory.
Create a `data_preprocessing` folder in the same directory. This allows reusing the preprocessed dataset for different trainings.

Create a another folder to save the results, such as `results_test1`.

If you change the folder names, you can manually edit the `input.yaml' accordingly.


### 3. Data preprocessing for monai-nnunet implementation

Go to the root folder containing the above files by typing the command below (update path) in the terminal:<br>
`cd /path/to/the/root/directory/`

**For editing the arguments or paths, you can first copy-paste them into a txt file.**

Convert the dataset to make the data readable for Monai. Copy-paste the command below in the terminal:
```
# [component] convert dataset; makes data readable
python -m monai.apps.nnunet nnUNetV2Runner convert_dataset --input_config "./input.yaml"
```
It will take some time to do the processing. You should be able to see the progress in the terminal. You should also see two subfolders created under the `data_preprocessing` called `nnUNet_preprocessed` and `nnUNet_raw_data_base` as specified at line 4 and 5 in the `input.yaml`.

Set up U-Net model configurations and make data trainable
```
# [component] experiment planning and data pre-processing; setup model configurations; makes data trainable
python -m monai.apps.nnunet nnUNetV2Runner plan_and_process --input_config "./input.yaml"
```
Wait until the process finishes. It may take a while.

After this step, if your raw data does not change and if you set `nnunet_results` directory differently from the directory of converted data in input.ymal, you can reuse these converted data and model configurations.

### 4. Train a model
[Optional]A quick smoke test that run 5 epochs to train a single `3d_fullres` model for a single folder.
```
[component] use all available GPU(s) to train a single model for 5 epochs.
python -m monai.apps.nnunet nnUNetV2Runner train_single_model --input_config "./input.yaml" \
    --config "3d_fullres" \
    --fold 0 \
    --trainer_class_name "nnUNetTrainer_5epochs"
```

**Use all available GPU(s) to train five models under the 3d_fullres configuration** <br>
'3d_fullres' configuration should be sufficient for the 3D segmentation model training. By default, monai-nnunet will train five different models with cross-validation (i.e., each time, it will randomly pick up some cases as validating dataset without being included in the training process). 
```
for f in 0 1 2 3 4; do
  python -m monai.apps.nnunet nnUNetV2Runner train_single_model \
    --input_config "./input.yaml" \
    --config "3d_fullres" \
    --fold $f \
done
```
In the monitor, you should be able to observe the loss dropping:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/849ee862-ba74-469c-b70d-60b17fa1df1a" />


Results will be stored in five different folders in `/path/to/nnunet_results/nnUNet_trained_models/Dataset001_monai_nn_tr/nnUNetTrainer_1000epochs__nnUNetPlans__3d_fullres`

By default, nnUNetTrainer will train 1000 epochs for each model. 

You can change the epoch number by adding a `trainer_class_name` argument to specify epochs numbers (for available epochs, see [tutorial](https://github.com/Project-MONAI/tutorials/tree/main/nnunet#:~:text=The%20supported%20trainer_class_name,nnUNetTrainer_8000epochs)): 
```
for f in 0 1 2 3 4; do
  python -m monai.apps.nnunet nnUNetV2Runner train_single_model \
    --input_config "./input.yaml" \
    --config "3d_fullres" \
    --fold $f \
    --trainer_class_name "nnUNetTrainer_2000epochs"
done
```

[Optional] You can also use all available GPU(s) to train all 20 models (4 configurations, five folders each). You do not have to because it contains 2d and 3d low resolution models. Slicer nnunet app will only use the 3d_full res. 

The command below will only train 20 epochs. You could change the epoch numbers in `trainer_class_name` or remove it to run the default 1000 epoch training. 
```
## [component] use all available GPU(s) to train all 20 models (4 configurations, five folders each).
python -m monai.apps.nnunet nnUNetV2Runner train --input_config "./input.yaml" \
    --trainer_class_name "nnUNetTrainer_20epochs"
```

### 5. Use the model
If you go to each folder under `/path/to/nnunet_results/nnUNet_trained_models/Dataset001_monai_nn_tr/nnUNetTrainer_nnUNetPlans__3d_fullres`, you can see the training log in a txt file such as `training_log_2025_10_1_02_21_01.txt`. It records the loss and dice score changes across the training process. At the end, you can see a summary of the train-val split and average dice score of the validation dataset.<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/041cb399-9b2f-47f1-8a4a-88114cc080e4" />

You can see more details about the validation results in the subfolder `validation`. The dice scores of validation datasets are summarized in `summary.json`. It also has nii.gz files of the predicted segmentations for the validation dataset.

To run the model, search and install the **nnUNet** extension in Slicer. Restart the computer, then switch to the nnUNet module.


