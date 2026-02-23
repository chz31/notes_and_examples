This tutorial shows how to run a monai_nnunet workflow.

Link to the [official Monai-nnU-net tutorial](https://github.com/Project-MONAI/tutorials/tree/main/nnunet).

To run this tutorial, the images and labels, including the augmented copies should be put under three folders `imagesTr`, `imagesTs`, and `labelsTr` under a root folder, which was named as `monai_nn_tr` in previous tutorials.

A json format data list for the traning dataset `msd_monai_nnunet_tr_folds.json` should also be created (see [tutorial 03](https://github.com/chz31/notes_and_examples/blob/main/workflows/MONAI_seg/03_data_prep_for_monai_nnunet.md))

### First, prepare an `input.yaml` to configure the data list file and input and output directories.
Here is a sample input.yaml and its content:
```
modality: CT
datalist: "./msd_monai_nnunet_tr_folds.json" #path to the data list json file. 
dataroot: "./monai_nn_tr" #path to 
nnunet_preprocessed: "./data_preprocessing/nnUNet_preprocessed" # directory for storing pre-processed data (optional)
nnunet_raw: "./data_preprocessing/nnUNet_raw_data_base" # directory for storing formated raw data (optional)
nnunet_results: "./results_test1/nnUNet_trained_models" # directory for storing trained model checkpoints (optional)
```
The last three lines are optional but recommended.


