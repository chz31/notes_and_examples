This tutorial shows how to use torchio for data augmentation

### 1. Installtion
Following instructions here: [https://docs.torchio.org/quickstart.html](https://docs.torchio.org/quickstart.html)

In Windows, search for 'cmd' and open the terminal. 

I created a conda environment: `conda create -n torchio python=3.12 -y`<br>
Activate the environment: `conda activate torchio`

Installation: `pip install torchio`

In Ubuntu, it reproted error below but torchio appeared to run well. Pytorch might also need to be installed before pip install torchio.
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
timm 1.0.19 requires torchvision, which is not installed.
batchgenerators 0.25.1 requires pandas, which is not installed.
```

In Windows, Pytorch might need to be installed first.

Run torchio using this sample script [torchio_test.py](https://github.com/chz31/notes_and_examples/blob/main/torchio_test.py)

First, download the script.

In this script:
First, change the directories in lines 8-12: <br>
```
volRoot = '/home/zhang/Documents/orbital_seg/imageAug/images/' #Directory of raw images in nii.gz format
maskRoot = '/home/zhang/Documents/orbital_seg/imageAug/labels/' #Directory of labelmaps (segmentations) in nii.gz format

volOutRoot = '/home/zhang/Documents/orbital_seg/imageAug/images_aug/' # Directory for saving augmented images
maskOutRoot = '/home/zhang/Documents/orbital_seg/imageAug/labels_aug/' # Directory for saving augmented segmentation labelmaps

```

At line 21, `iter=5` means it will iterate through the same augmentation pipeline for each image and its correspondant labelmap five times, thus generating five different copies of them.

Afterwards, activate the torchio environment in the terminal and run:<br>
`python /your/path/to/torchio_test.py`

You should be able to see the augmented images and labelmaps with postscript "aug_0, aug_1, aug_2, etc...."
