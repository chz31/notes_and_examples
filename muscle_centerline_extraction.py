volumeNode = slicer.util.getNode('iso_vol')
segmentationNode = slicer.util.getNode('totalSeg')
rightMuscleID = segmentationNode.GetSegmentation().GetSegmentIDs()[8]
leftMuscleMirrorID = segmentationNode.GetSegmentation().GetSegmentIDs()[17]

rightMuscleLabelMapArray = arrayFromSegmentBinaryLabelmap(segmentationNode, rightMuscleID, volumeNode)
leftMuscleMirrorLabelMapArray = arrayFromSegmentBinaryLabelmap(segmentationNode, leftMuscleMirrorID, volumeNode)


import numpy as np

# Get non-empty slices along axis 0 (first axis)
rightMuslceSliceIndices = np.where(np.any(rightMuscleLabelMapArray != 0, axis=(0, 2)))[0]
leftMuslceMirrorSliceIndices = np.where(np.any(leftMuscleMirrorLabelMapArray != 0, axis=(0, 2)))[0]


# Crop array to keep only those slices
rightMuscleArray= rightMuscleLabelMapArray[:, rightMuslceSliceIndices[0] : rightMuslceSliceIndices[-1] + 1, :]
leftMuscleMirrorArray= leftMuscleMirrorLabelMapArray[:, leftMuslceMirrorSliceIndices[0] : leftMuslceMirrorSliceIndices[-1] + 1, :]



#Compute centroid
rightCentroids = []

for i in range(rightMuscleArray.shape[1]):
    slice2D = rightMuscleArray[:, i, :]

    segRegion = np.argwhere(slice2D != 0)

    y_mean, x_mean = segRegion.mean(axis=0)
    rightCentroids.append((np.round(x_mean), rightMuslceSliceIndices[i], np.round(y_mean)))  # (x, y, z)


# for i in range(rightMuscleArray.shape[0]):
#     slice2D = rightMuscleArray[i, :, :]  # slice in (J, K) plane
#     segRegion = np.argwhere(slice2D != 0)
#
#     if segRegion.size == 0:
#         continue
#
#     j_mean, k_mean = segRegion.mean(axis=0)
#     ijk_point = (i, j_mean, k_mean)  # (I, J, K)
#
#     rightCentroids.append(ijk_point)


rightCentroids.reverse()



# Get voxel position in IJK coordinate system
rightCentroidsListNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'rightCentroids')
rightCentroidsCurveNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsCurveNode', 'rightCentroidsCurve')

for i in range(len(rightCentroids)):
    point_Ijk = rightCentroids[i]

    # Get physical coordinates from voxel coordinates
    volumeIjkToRas = vtk.vtkMatrix4x4()
    volumeNode.GetIJKToRASMatrix(volumeIjkToRas)
    point_VolumeRas = [0, 0, 0, 1]
    volumeIjkToRas.MultiplyPoint(np.append(point_Ijk,1.0), point_VolumeRas)

    # Add a markup at the computed position and print its coordinates
    rightCentroidsListNode.AddControlPoint((point_VolumeRas[0], point_VolumeRas[1], point_VolumeRas[2]))
    # print(point_VolumeRas)

    pos = [point_VolumeRas[0], point_VolumeRas[1], point_VolumeRas[2]]
    rightCentroidsCurveNode.AddControlPoint(pos)

# rightCentroidsCurveNode.ResampleCurveWorld(50.0)


#Left muscle centroids
leftCentroids = []

for i in range(leftMuscleMirrorArray.shape[1]):
    slice2D = leftMuscleMirrorArray[:, i, :]

    segRegion = np.argwhere(slice2D != 0)

    y_mean, x_mean = segRegion.mean(axis=0)
    leftCentroids.append((np.round(x_mean), leftMuslceMirrorSliceIndices[i], np.round(y_mean)))  # (x, y, z)


leftCentroids.reverse()


# Get voxel position in IJK coordinate system
leftCentroidsListNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'leftCentroids')
leftCentroidsCurveNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsCurveNode', 'leftCentroidsCurve')

for i in range(len(leftCentroids)):
    point_Ijk = leftCentroids[i]

    # Get physical coordinates from voxel coordinates
    volumeIjkToRas = vtk.vtkMatrix4x4()
    volumeNode.GetIJKToRASMatrix(volumeIjkToRas)
    point_VolumeRas = [0, 0, 0, 1]
    volumeIjkToRas.MultiplyPoint(np.append(point_Ijk,1.0), point_VolumeRas)

    # Add a markup at the computed position and print its coordinates
    leftCentroidsListNode.AddControlPoint((point_VolumeRas[0], point_VolumeRas[1], point_VolumeRas[2]))
    # print(point_VolumeRas)

    pos = [point_VolumeRas[0], point_VolumeRas[1], point_VolumeRas[2]]
    leftCentroidsCurveNode.AddControlPoint(pos)

# leftCentroidsCurveNode.ResampleCurveWorld(10.0)
#flip firt axis to -1 created a rough mirror