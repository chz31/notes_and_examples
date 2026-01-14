
################# Create points at 4, 7, 10mm
import numpy as np

# Given points
P0 = np.array([-95.807, 86.787, -0.063])
P1 = np.array([-96.027, 87.707, -4.015])

# Direction vector
v = P1 - P0

# Normalize
v_hat = v / np.linalg.norm(v)

# Distances you want (mm)
distances = [4, 7, 10]

print("Unit direction vector:", v_hat, "\n")

for d in distances:
    P = P0 + d * v_hat
    print(f"Point at {d} mm:", P)
    

#####Create horizontal planes at 4, 7, 10mm
def createPlanes(f, plane2Center=None, angle=None, useBinormal=True,
                 plane1Name="Plane1", plane2Name="Plane_7mm"):
    """
    f: vtkMRMLMarkupsFiducialNode (or any markups node with >=3 control points)
    plane2Center: [x,y,z] world coords where plane2 passes through (default: p1)
    angle: rotation (degrees) to spin perpendicular choice around plane1 normal (default: 0)
    useBinormal: True -> use binormal as plane2 normal, False -> use tangent
    """

    # --- Read 3 points from markups node f ---
    p1 = [0.0, 0.0, 0.0]
    p2 = [0.0, 0.0, 0.0]
    p3 = [0.0, 0.0, 0.0]
    f.GetNthControlPointPositionWorld(0, p1)
    f.GetNthControlPointPositionWorld(1, p2)
    f.GetNthControlPointPositionWorld(2, p3)

    rotationOfPerpendiculars = float(angle) if angle is not None else 0.0

    plane2Coordinates = plane2Center if plane2Center is not None else p1

    # --- Create Plane1 (3-point plane) ---
    plane1 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", plane1Name)
    plane1.CreateDefaultDisplayNodes()
    plane1.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)
    plane1.AddControlPointWorld(p1)
    plane1.AddControlPointWorld(p2)
    plane1.AddControlPointWorld(p3)

    # --- Get Plane1 normal (world) ---
    plane1Normal = [0.0, 0.0, 0.0]
    plane1.GetNormalWorld(plane1Normal)
    vtk.vtkMath.Normalize(plane1Normal)

    # --- Compute perpendicular directions to plane1Normal ---
    plane1Binormal = [0.0, 0.0, 0.0]
    plane1Tangent  = [0.0, 0.0, 0.0]
    vtk.vtkMath.Perpendiculars(plane1Normal, plane1Binormal, plane1Tangent, rotationOfPerpendiculars)

    n2 = plane1Binormal if useBinormal else plane1Tangent
    vtk.vtkMath.Normalize(n2)

    # --- Create Plane2 (point + normal) ---
    plane2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", plane2Name)
    plane2.CreateDefaultDisplayNodes()
    plane2.AddControlPointWorld(plane2Coordinates)
    plane2.SetNormalWorld(n2)

    print("Plane1 points:", p1, p2, p3)
    print("Plane1 normal:", plane1Normal)
    print("Plane2 origin:", plane2Coordinates)
    print("Plane2 normal:", n2)

    return plane1, plane2


f = slicer.util.getNode("F_1")  # replace "F" with your fiducials node name
plane1, plane2 = createPlanes(
    f,
    plane2Center=[-96.348, 89.051, -9.788],
    angle=0.0,
    useBinormal=False
)
#useBinormal = True create another perpendicular plane




