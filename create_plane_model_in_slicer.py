#Create a plane model first

import vtk, slicer

# --- parameters (mm) ---
width = 40.0
height = 25.0
xRes = 60   # increase for denser mesh
yRes = 40

plane = vtk.vtkPlaneSource()
plane.SetOrigin(-width/2, -height/2, 0)
plane.SetPoint1( width/2, -height/2, 0)
plane.SetPoint2(-width/2,  height/2, 0)
plane.SetXResolution(xRes)
plane.SetYResolution(yRes)
plane.Update()

# Triangulate (good for many downstream filters / exporters)
tri = vtk.vtkTriangleFilter()
tri.SetInputConnection(plane.GetOutputPort())
tri.Update()

modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "RetractorPlane")
modelNode.SetAndObservePolyData(tri.GetOutput())
modelNode.CreateDefaultDisplayNodes()


#Add thickness
modelNode = slicer.util.getNode("RetractorPlane")
poly = modelNode.GetPolyData()

thickness_mm = 0.5

# Ensure normals exist (extrusion needs a direction; normals help if the surface isn't perfectly axis-aligned)
normals = vtk.vtkPolyDataNormals()
normals.SetInputData(poly)
normals.ConsistencyOn()
normals.AutoOrientNormalsOn()
normals.SplittingOff()
normals.Update()

extrude = vtk.vtkLinearExtrusionFilter()
extrude.SetInputConnection(normals.GetOutputPort())
extrude.SetExtrusionTypeToNormalExtrusion()
extrude.SetScaleFactor(thickness_mm)     # thickness in mm
extrude.CappingOn()                      # adds the "back face"
extrude.Update()

# Triangulate output (often helpful)
tri = vtk.vtkTriangleFilter()
tri.SetInputConnection(extrude.GetOutputPort())
tri.Update()

thickNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "RetractorPlane_1mm")
thickNode.SetAndObservePolyData(tri.GetOutput())
thickNode.CreateDefaultDisplayNodes()



