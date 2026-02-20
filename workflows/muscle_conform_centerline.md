**Activate nnInteractive**<br>
Open 3D Slicer<br>
Make sure the image is isotropic. Switch to `Crop Volume` module. Create an ROI. 

Switch to nnInteractive module

Use nnInteractive to segment the inferior rectus muscles on both sides

Download the below script to extract centerline
[muscle_centerline_extraction.py](https://github.com/chz31/notes_and_examples/blob/main/muscle_centerline_extraction.py)

Change the script first.

In Line 1 and 2, change the volume and segmentation node names in the paranthesis
```
volumeNode = slicer.util.getNode('iso_vol')
segmentationNode = slicer.util.getNode('totalSeg')
```

In Line 3 and 4, change the numbers in the '[]' to the actual order of right and left muscle segments in a segmentation node
```
rightMuscleID = segmentationNode.GetSegmentation().GetSegmentIDs()[8]
leftMuscleMirrorID = segmentationNode.GetSegmentation().GetSegmentIDs()[17]

# In the above code, the right and left muscle segments are the 8th and 17th in the segmentation node.
```

After the changes are made, click Ctrl/Command + G to run the script in Slicer.

You should be able to see that centerlines have been extracted.

Right click each centerline object in the `Data` module and click "Edit Properties". This will bring you to the Markups Module. 

Scroll down to find and expand "Resample". Create a new node with new name by adding "_resampled" as the postscript:<br>
<img width="600" alt="image" src="https://github.com/user-attachments/assets/e507a999-3d0d-465c-9e9a-15db54595856" />

Click "Resample Curve" will resample the curve control points into 20.

Creating an empty point list called "LeftCentroid" and "rightCentroids". Do not manually adding an point. You can right click to exit point placement.<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/750341ab-59ea-4f18-8504-95bed44d7374" />

Go back to the resampled curve object and select all points under "Control Points".<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/373d472c-2574-495d-97c5-d9529812fe4e" />

Copy all those points by Ctrl+A or right clicking. Paste the points under the empty "Control Points" <br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/4ad23f24-bd40-4c45-af00-5f166e0869c9" />
<img width="400" height="560" alt="image" src="https://github.com/user-attachments/assets/41dcbea4-d9b9-4a39-a80c-f5eee36b9dc8" />

Export Point Lists only (leftCentroids and  rightCentroids) as in the mrk.json and name them using the format "1633_right" and "1633_left_fx".

Save and exit.


Samples that has been segmented by nninteractive (if not marked "muscle curves created", muscle curves still need to be created:
- 1224
- 1494
- 1570
- 1617 (marked wrong as 1702 in muscle pts; muscle curves created)
- 1662 
- 1807
- 1958

Sampled that has not been segmented by nninteractive
- 1633
- 1702
- 1728
- 1756
- 1846
- 1928
- 1937
- 1944
