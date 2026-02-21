This workflow is about how to prepare for data preparation for monai_nnunet traning

### 1. Arrange the files into a specific format
```
monai_nnunet_tr
      ------------imagesTr
      ------------imagesTs
      ------------labelsTr
```
**Note that the images and labelmaps in the `imagesTr` and `labelsTr` should have the same name.**<br>
I am not sure if test images are necessary. I just copied three images and put them into `imagesTs`. 

### 2. Generate a json file 
A json file for the data list needs to be generated for nnU-net to convert the data.

First, activate the conda environment for monai nnunet and open jupyter notebook
```
conda activate your_environment_name

jupyter notebook
```

Download the notebook [nnunet_json_generator.ipynb](https://github.com/chz31/notes_and_examples/blob/main/nnunet_json_generator.ipynb)

In Jupyter notebook, locate this notebook and open it.

In block 3, specify the root directory for the `monai_nnunet_tr` raw data folder:<br>
`directory = '/home/zhang/Documents/orbital_seg/color_labels_new'`

In block 4, you should see a print out message `Datalist is saved to msd_monai_nnunet_tr_folds.json` stored in the root directory.

Go to root directory to open `msd_monai_nnunet_tr_folds.json`. You should see:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/69e2259b-829c-47f7-849f-ccf1020cc0d0" />

Now we can officially start the monai-unet pipeline!
