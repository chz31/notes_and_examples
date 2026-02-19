This tutorial shows how to use torchio for data augmentation

### 1. Installtion
Following instructions here: [https://docs.torchio.org/quickstart.html](https://docs.torchio.org/quickstart.html)

In Windows, search for 'cmd' and open the terminal. 

I created a conda environment: `conda create -n torchio python=3.12 -y`<br>
Activate the environment: `conda activate torchio`

Installation: `pip install torchio`

In Ubuntu, 

In Windows, Pytorch might need to be installed first.

Run torchio using this sample script [torchio_test.py](https://github.com/chz31/notes_and_examples/blob/main/torchio_test.py)

In this script:
First, change the directories in lines 8-12: <br>
```
volRoot = '/home/zhang/Documents/orbital_seg/imageAug/images/' #Directory of raw images in nii.gz format
maskRoot = '/home/zhang/Documents/orbital_seg/imageAug/labels/' #Directory of labelmaps (segmentations) in nii.gz format

volOutRoot = '/home/zhang/Documents/orbital_seg/imageAug/images_aug/'
maskOutRoot = '/home/zhang/Documents/orbital_seg/imageAug/labels_aug/'

```
