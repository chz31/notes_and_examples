#/home/zhang/Documents/orbital_seg/imageAug/torchio_test.py

import torch
import torchio as tio
import os


volRoot = '/home/zhang/Documents/orbital_seg/imageAug/images/'
maskRoot = '/home/zhang/Documents/orbital_seg/imageAug/labels/'

volOutRoot = '/home/zhang/Documents/orbital_seg/imageAug/images_aug/'
maskOutRoot = '/home/zhang/Documents/orbital_seg/imageAug/labels_aug/'


imageFiles = sorted(os.listdir(volRoot))
print(imageFiles)
labelFiles = sorted(os.listdir(maskRoot))
print(labelFiles)


iter = 5

for j in range(iter):
    for i in range(len(imageFiles)):
        imageFilePath = os.path.join(volRoot, imageFiles[i])
        print(imageFilePath)
        labelFilePath = os.path.join(maskRoot, labelFiles[i])
        print(labelFilePath)
        subject_i = tio.Subject(
            t1=tio.ScalarImage(imageFilePath),
            label=tio.LabelMap(labelFilePath),
        )

        compose_transform = tio.Compose([
            tio.RescaleIntensity(out_min_max=(0, 1)),
            tio.RandomFlip(axes=['inferior-superior'], flip_probability=0.5),
            tio.OneOf({
                tio.RandomAffine(): 0.5,
                tio.RandomElasticDeformation(): 0.5,
            },p=0.8),
            tio.RandomAnisotropy(p =0.25),
        ])
        #Add random Affine Zoom later?

        subject_tr = compose_transform(subject_i)

        fileName = imageFiles[i].split('.')[0] + 'aug_' + str(j) + '.nii.gz'
        imageOutPath = os.path.join(volOutRoot, fileName)
        subject_tr.t1.save(imageOutPath)
        labelOutPath = os.path.join(maskOutRoot, fileName)
        subject_tr.label.save(labelOutPath)


# import torch
# import torchio as tio
#
# volPath = '/home/zhang/Documents/orbital_seg/imageAug/images/1048.nii.gz'
# maskPath = '/home/zhang/Documents/orbital_seg/imageAug/images/1048_mask.nii.gz'
#
# subject_a = tio.Subject(
#     t1=tio.ScalarImage(volPath),
#     label=tio.LabelMap(maskPath),
#     diagnosis='positive',
# )
#
#
# spatial = tio.OneOf({
#         tio.RandomAffine(): 0.5,
#         tio.RandomElasticDeformation(): 0.5,
#     },
#     p=0.8,
# )
#
# subject_a_affine = spatial(subject_a)
#
# subject_a_affine.t1.save('/home/zhang/Documents/orbital_seg/imageAug/images/1048_t1_affine.nii.gz')
# subject_a_affine.label.save('/home/zhang/Documents/orbital_seg/imageAug/images/1048_t1_label_affine.nii.gz')
