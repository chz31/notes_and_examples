import glob
import os
import numpy as np
from monai.transforms import LoadImage

source_labels = "/home/zhang/Documents/orbital_seg/color_labels_new/labels"

all_files = glob.glob(os.path.join(source_labels, "*.nii.gz"))

print(all_files)

for idx, img_path in enumerate(all_files):
    d = LoadImage(image_only=True)(img_path)
    dirname, file = os.path.split(img_path)
    # print(f"Spacing: {np.diag(d.meta.get('affine'))} and name: {file}")
    print(f"Image: {file} => max intensity {d.array.max()} - min intensity {d.array.min()}")
    print("Unique values: ", np.unique(d.array))
    print(f"Labelmap size: {d.array.shape}")