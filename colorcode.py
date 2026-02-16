# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#color table
segment_names_to_labels = [("right_eyeball", 0), ("lateral_rectus_muscle_right", 1), ("superior_oblique_muscle_right", 2), ("levator_palpebrae_superioris_right", 3), ("superior_rectus_muscle_right", 4), ("medial_rectus_muscle_left", 5), ("inferior_oblique_muscle_right", 6), ("inferior_rectus_muscle_right", 7),
                           ("optic_nerve_left", 8), ("left_eyeball", 9), ("lateral_rectus_muscle_left", 10), ("superior_oblique_muscle_left", 11), ("levator_palpebrae_superioris_left", 12), ("superior_rectus_muscle_left", 13), ("medial_rectus_muscle_right", 14), ("inferior_oblique_muscle_left", 15),
                           ("inferior_rectus_muscle_left", 16), ("optic_nerve_right", 17), ("orbital_fat_right", 18), ("orbital_fat_left", 19), ("maxillary_sinus_right", 20), ("maxillary_sinus_left", 21), ("skull", 22)]

#Start from 1 next time



colorTableNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLColorTableNode")
colorTableNode.SetTypeToUser()
colorTableNode.HideFromEditorsOff()  # make the color table selectable in the GUI outside Colors module
slicer.mrmlScene.AddNode(colorTableNode); colorTableNode.UnRegister(None)

largestLabelValue = max([name_value[1] for name_value in segment_names_to_labels])
colorTableNode.SetNumberOfColors(largestLabelValue + 1)

# colorTableNode.SetColor(0, "background", 0.0, 0.0, 0.0, 1.0)

import random
for segmentName, labelValue in segment_names_to_labels:
    print(segmentName)
    r = random.uniform(0.0, 1.0)
    g = random.uniform(0.0, 1.0)
    b = random.uniform(0.0, 1.0)
    a = 1.0
    success = colorTableNode.SetColor(labelValue, segmentName, r, g, b, a)

slicer.util.saveNode(colorTableNode, '/home/zhang/Documents/orbital_seg/color_labels_new/color.txt')



#Change names to be consistent with the color table
segment_names_to_labels = [(name.replace("_", " "), label) for name, label in segment_names_to_labels]

print(segment_names_to_labels)

segmentationNode = slicer.util.getNode("1728 Isotropic Cropped Volume totalsegmentator oculomotor muscles Copy")
segmentation = segmentationNode.GetSegmentation()
segment = segmentation.GetNthSegment(0)
segment.SetName("right eyeball")

for i, item in enumerate(segment_names_to_labels):
    segment = segmentation.GetNthSegment(i)
    segment.SetName(item[0])
    print(item)

# segment = segmentation.GetNthSegment(1)
# segment.SetName("lateral_rectus_muscle_right")
#
# segment = segmentation.GetNthSegment(2)
# segment.SetName("superior_oblique_muscle_right")
#
# segment = segmentation.GetNthSegment(3)
# segment.SetName("levator_palpebrae_superioris_right")
#
# segment = segmentation.GetNthSegment(4)
# segment.SetName("superior_rectus_muscle_right")
#
# segment = segmentation.GetNthSegment(5)
# segment.SetName("medial_rectus_muscle_left")
#
# segment = segmentation.GetNthSegment(6)
# segment.SetName("inferior_oblique_muscle_right")
#
#
# segment = segmentation.GetNthSegment(7)
# segment.SetName("inferior_oblique_muscle_right")
#



#export segmentation into labelmap with color codes
segmentationNode = getNode('1048')  # source segmentation node
labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")  # export to new labelmap volume
referenceVolumeNode = slicer.util.getNode('2: DummySeriesDesc! - acquisitionNumber 1 isotropic') # it could be set to the master volume
segmentIds = segmentationNode.GetSegmentation().GetSegmentIDs()  # export all segments
colorTableNode = slicer.util.getNode('color_2')  # created from scratch or loaded from file

slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segmentationNode, segmentIds, labelmapVolumeNode, referenceVolumeNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY, colorTableNode)


