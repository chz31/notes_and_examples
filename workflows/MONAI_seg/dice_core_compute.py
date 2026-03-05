Compute dice scores:

Load a volume and its labelmap from monai_nnunet_tr

Run the below script in Slicer's Python console:
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

Run the below script to change segment names. **Remember to update the segmenation node's name `segmentationNode = slicer.util.getNode("1048")`**
```
#Change names to be consistent with the color table
segment_names_to_labels = [(name.replace("_", " "), label) for name, label in segment_names_to_labels] #remove '_'

segmentationNode = slicer.util.getNode("1048") #Change it to your segment name
segmentation = segmentationNode.GetSegmentation()

for i, item in enumerate(segment_names_to_labels):
    segment = segmentation.GetNthSegment(i)
    segment.SetName(item[0])
    print(item)
```
You should see the segment names are updated.

Switch to **nnUNET** module.
