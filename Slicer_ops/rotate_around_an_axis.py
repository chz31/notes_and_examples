# Example from Slicer script repository

# Set up the scene:

# Add a markup line node (rotationAxisMarkupsNode) with 2 points to specify rotation axis.

# Add a rotation transform (rotationTransformNode) that will be edited in Transforms module to specify rotation angle.

# Add a transform (finalTransformNode) and apply it (not harden) to those nodes (images, models, etc.) that you want to rotate around the line.

# Then run the script below, go to Transforms module, select rotationTransformNode, and move Edit / Rotation / IS slider.


import numpy as np

# This markups point list node specifies the center of rotation
rotationAxisMarkupsNode = getNode("A_P_axis")
# This transform can be edited in Transforms module (Edit / Rotation / IS slider)
rotationTransformNode = getNode("rotation_transform")
# This transform has to be applied to the image, model, etc.
finalTransformNode = getNode("final_transform")

def updateFinalTransform(unusedArg1=None, unusedArg2=None, unusedArg3=None):
  import numpy as np
  rotationAxisPoint1_World = np.zeros(3)
  rotationAxisMarkupsNode.GetNthControlPointPositionWorld(0, rotationAxisPoint1_World)
  rotationAxisPoint2_World = np.zeros(3)
  rotationAxisMarkupsNode.GetNthControlPointPositionWorld(1, rotationAxisPoint2_World)
  axisDirectionZ_World = rotationAxisPoint2_World-rotationAxisPoint1_World
  axisDirectionZ_World = axisDirectionZ_World/np.linalg.norm(axisDirectionZ_World)
  # Get transformation between world coordinate system and rotation axis aligned coordinate system
  worldToRotationAxisTransform = vtk.vtkMatrix4x4()
  p=vtk.vtkPlaneSource()
  p.SetNormal(axisDirectionZ_World)
  axisOrigin = np.array(p.GetOrigin())
  axisDirectionX_World = np.array(p.GetPoint1())-axisOrigin
  axisDirectionY_World = np.array(p.GetPoint2())-axisOrigin
  rotationAxisToWorldTransform = np.vstack((np.column_stack((axisDirectionX_World, axisDirectionY_World, axisDirectionZ_World, rotationAxisPoint1_World)), (0, 0, 0, 1)))
  rotationAxisToWorldTransformMatrix = slicer.util.vtkMatrixFromArray(rotationAxisToWorldTransform)
  worldToRotationAxisTransformMatrix = slicer.util.vtkMatrixFromArray(np.linalg.inv(rotationAxisToWorldTransform))
  # Compute transformation chain
  rotationMatrix = vtk.vtkMatrix4x4()
  rotationTransformNode.GetMatrixTransformToParent(rotationMatrix)
  finalTransform = vtk.vtkTransform()
  finalTransform.Concatenate(rotationAxisToWorldTransformMatrix)
  finalTransform.Concatenate(rotationMatrix)
  finalTransform.Concatenate(worldToRotationAxisTransformMatrix)
  finalTransformNode.SetAndObserveMatrixTransformToParent(finalTransform.GetMatrix())

# Manual initial update
updateFinalTransform()

# Automatic update when point is moved or transform is modified
rotationTransformNodeObserver = rotationTransformNode.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, updateFinalTransform)
rotationAxisMarkupsNodeObserver = rotationAxisMarkupsNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, updateFinalTransform)

# Execute these lines to stop automatic updates:
# rotationTransformNode.RemoveObserver(rotationTransformNodeObserver)
# rotationAxisMarkupsNode.RemoveObserver(rotationAxisMarkupsNodeObserver)
