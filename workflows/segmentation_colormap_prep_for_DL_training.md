This is a workflow for generating a uniform labelmap for all segmentations using colormap for deep learning model training.

### 1. Generate a new color table in txt
Run the example code here: [colorcode.py](https://github.com/chz31/notes_and_examples/blob/main/colorcode.py)

Edit color code table in line 7 if necessary
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

Change the file path & file name at line 34:<br>
`slicer.util.saveNode(colorTableNode, '/home/zhang/Documents/color.txt')`

Copy line 1-54 into Slicer Python console to run it.

You should see a txt file with content similar to the below one in your preferred directory. Each line marks a segment with a particular RGB color code:
```
# Color table file /home/zhang/Documents/color_test.txt
# 23 values
0 right_eyeball 42 62 77 255
1 lateral_rectus_muscle_right 151 96 17 255
2 superior_oblique_muscle_right 165 66 66 255
3 levator_palpebrae_superioris_right 175 178 232 255
4 superior_rectus_muscle_right 54 154 87 255
5 medial_rectus_muscle_left 187 134 64 255
6 inferior_oblique_muscle_right 177 217 95 255
7 inferior_rectus_muscle_right 58 82 163 255
8 optic_nerve_left 32 0 93 255
9 left_eyeball 230 51 99 255
10 lateral_rectus_muscle_left 217 74 99 255
11 superior_oblique_muscle_left 189 48 18 255
12 levator_palpebrae_superioris_left 220 156 196 255
13 superior_rectus_muscle_left 149 252 37 255
14 medial_rectus_muscle_right 172 130 237 255
15 inferior_oblique_muscle_left 54 97 131 255
16 inferior_rectus_muscle_left 170 175 82 255
17 optic_nerve_right 157 184 137 255
18 orbital_fat_right 128 77 94 255
19 orbital_fat_left 120 172 136 255
20 maxillary_sinus_right 70 135 158 255
21 maxillary_sinus_left 54 219 67 255
22 skull 159 12 37 255
```

### 2. Load the color.txt as color node to Slicer.
Assuming we ware using the segmentation updated from TotalSegmentator results.<br>
Drag and drop the color.txt to Slicer, and imported as color node by accept the default.<br>
<img height="200" alt="image" src="https://github.com/user-attachments/assets/48cd20b0-d291-4548-afe4-287ee6029e13" />

In the `Data` module, `All nodes` tab, you should see a newly imported color node:<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/a2f16f67-b93d-4e80-8fb8-6c0451d763aa" />

Right click the color node, then `Edit properties`, you should see the content of the color table node<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/689b05a3-3b39-49c8-9b5d-f97013f7ebdb" />


### 4. Change segment names to remove "_"
The original segment names using `_` to connect words in a name, such as "lateral_rectus_muscle_right" in `segment_names_to_labels` in the color table node.
When loaded in Slicer, the "_" will be automatically removed for some reason as picture above shows.
However, if using space to separate words in the color node, everything behind the first word will disappear after importing the color table into Slicer.

The label in the color table need to be matched with each segment's name. Thus, the `_` symbol in segment names need to be removed.

**First, make sure that the segment order and names are identical with the labels in the color table.**<br>

Go to `Segment Editor` module in Slicer. Make sure that the order is the same. If not, select a segment and right click it, select "Move selected segment up" or "Move segment down". Change the name if needed <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/d4b8c629-56aa-412c-805a-24573f74400c" />

Now run line 7 in [colorcode.py](https://github.com/chz31/notes_and_examples/blob/main/colorcode.py) again to make sure that the segment label names are loaded in Python.<br>

Run the script below to remove the '_' symbol from each name. **Remeber to change the segmentation name 
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

### 5. Now you can export the label map
Change the object names in paratheses following the comment in each line
```
#export segmentation into labelmap with color codes
segmentationNode = getNode('1048')  # Change source segmentation node that will be exported to a labelmap node
labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
referenceVolumeNode = slicer.util.getNode('2: DummySeriesDesc! - acquisitionNumber 1 isotropic') # it could be set to the master volume
segmentIds = segmentationNode.GetSegmentation().GetSegmentIDs()  # export all segments
colorTableNode = slicer.util.getNode('color_2')  # created from scratch or loaded from file

slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segmentationNode, segmentIds, labelmapVolumeNode, referenceVolumeNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY, colorTableNode)
```

### 6. Save the results
Right click 

