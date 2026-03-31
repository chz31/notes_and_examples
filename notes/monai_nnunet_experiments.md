### March 19

Set up a TAMU hpc venv and workflow for the segmentation projects for students

Tasks to do:
- - [x] Use Globus to transport preprocessed data to FASTER group venv for training 
- Try using MONAI to predict and postprocessing without using Slicer
- Establish globus personal endpoint at Mac and Windows
- Test restricting training CPU usage to run SOFA and DL train at the same time
- Hyperparameter tuning in MONAI nnunet
- Test nnU-Net alone
- Training evaluation metrics establishment


### March 20
monai nnunetv2 can finish training on FASTER but ran into runtime error during validation after training.

Could be memory issue or using >1 CPU cores.

Testing using one core than switch to two cores.

nnUNet also recommended using the new architecture as the default: [https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/resenc_presets.md](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/resenc_presets.md)

This needs to be tried next time.

Also need to try restricting training CPU usage to run other programs and DL train at the same time.
