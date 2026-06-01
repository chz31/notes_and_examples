## 1. Load a segmentation and update segment names
Load the image and existing segmentation.

Run below script to create segment names and order:
```
segment_names_to_labels = [("right_eyeball", 1), 
                           ("lateral_rectus_muscle_right", 2), 
                           ("superior_oblique_muscle_right", 3), 
                           ("levator_palpebrae_superioris_right", 4), 
                           ("superior_rectus_muscle_right", 5), 
                           ("medial_rectus_muscle_left", 6), 
                           ("inferior_oblique_muscle_right", 7), 
                           ("inferior_rectus_muscle_right", 8),
                           ("optic_nerve_left", 9), 
                           ("left_eyeball", 10), 
                           ("lateral_rectus_muscle_left", 11), 
                           ("superior_oblique_muscle_left", 12), 
                           ("levator_palpebrae_superioris_left", 13), 
                           ("superior_rectus_muscle_left", 14), 
                           ("medial_rectus_muscle_right", 15), 
                           ("inferior_oblique_muscle_left", 16),
                           ("inferior_rectus_muscle_left", 17), 
                           ("optic_nerve_right", 18), 
                           ("orbital_fat_right", 19), 
                           ("orbital_fat_left", 20), 
                           ("maxillary_sinus_right", 21), 
                           ("maxillary_sinus_left", 22), 
                           ("skull", 23)]
```

Update names. Make sure to update segmentationNode name.
```
segmentationNode = slicer.util.getNode("1048.nii.gz") #Change it to your segment name
segmentation = segmentationNode.GetSegmentation()

for i, item in enumerate(segment_names_to_labels):
    segment = segmentation.GetNthSegment(i)
    segment.SetName(item[0])
    print(item)
```

## 2. Starting from Total Segmentator created segmentation

**Convert a volume into isotropic if it is not** <br>
Go to "Crop Volume" module. Create a new ROI in the "input ROI". Select "output volume" of the raw image itself, and check **isotropic space.** Hit Apply to convert it to isotropic.

Add four new segments inside the Segment Editor module following the order:
```
"orbital_fat_right"
"orbital_fat_left"
"maxillary_sinus_right"
"maxillary_sinus_left" 
```

Afterwards, in the Segment Editor module, move the skull segment to the last row.

## 3. Adding and/or correcting segments
First, right click the volume, then "Editor Properties" or directly go to the Volumes module and select the volume. **Uncheck Interpolate" to show pixel boundaries.**

If orbital fat and maxillary sinus were not added, add them using `nnInteractive`. 

Fat tissue can overlap with other tissue. After done, go to Logical Operator tool  in the Segment Editor and subtract fat tissue from others<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/fe5e68e7-5264-4f9a-94be-471c5e8fbceb" />

You may change the Window level to adjust contrast to better show tissue boundary. This can be especially helpful for segmenting herniated fat in the fracture side.

You can adjust the Window/level by enbale it in the top menu or right click a slice view and select Adjust Window/level, and hold and drag the left mouse button in a slice view
<img width="200" alt="image" src="https://github.com/user-attachments/assets/76f3b1a3-038b-48c7-a227-a9f5b3daeebe" />

**For more accurate adjustment**, right click a volume to select "Edit properties". In the Volumes module, you can adjust the Window/Level bar for contrast, such as reducing the width of the blue bar and move it:

For example, before adjustment, the herniated fat and blood were not very differentiable <br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/43a279d1-b731-4ae2-9437-bc938346b115" />


After adjusting Window/Level, the boundary between herniated fat and blood/sinus is clearer.<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/f15102fd-008f-4d85-b5e2-ef28c949d77c" />

nnInteractive tends to exaggerate the muscle size, especially inferior oblique.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/100c670a-838f-46f1-a131-7c160fed86ef" />


Focus on fixing medial rectus, inferior rectus, and inferior oblique

You may still need to use manual tools to fix the skull segmentation, such as using Thresholding to mask the image and apply manual fixing, such as paiting.


## 4. Save the output.
After donw, go to Data Module, right click the segmentation and select "Export to file", select Export Format as `.seg.nrrd`, and its name the same as the volume.<br>
<img width="200" alt="image" src="https://github.com/user-attachments/assets/5ec04856-e43a-4f2a-a5f0-cf0be075527c" />

Select a directory or create a new folder to save the output, preferably a folder only for labels/segmentations.
