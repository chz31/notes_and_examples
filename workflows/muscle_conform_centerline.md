Activate nnInteractive

Open 3D Slicer

Make sure the image is isotropic. Switch to each 

Switch to nnInteractive module

Use nnInteractive to segment the inferior rectus muscles on both sides

Use the below script to extract centerline
[muscle_centerline_extraction.py](https://github.com/chz31/notes_and_examples/blob/main/muscle_centerline_extraction.py)

Download the script first.

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


Save the entire file


