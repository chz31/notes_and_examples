import numpy as np

fiducialList1 = slicer.util.getNode("F_1")  # moving fiducial list
fiducialList2 = slicer.util.getNode("F_2")  # target fiducial list

line1Name = "L_1"
line2Name = "L_2"
transformName = "Rotate_F1_onto_F2"

def get_point_world(markupsNode, index):
    p = np.zeros(3)
    markupsNode.GetNthControlPointPositionWorld(index, p)
    return p


def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-8:
        raise ValueError("Zero-length vector.")
    return v / n


def create_or_update_line(lineName, p0, p1):
    lineNode = slicer.mrmlScene.GetFirstNodeByName(lineName)

    if lineNode is None:
        lineNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLMarkupsLineNode",
            lineName
        )
    else:
        lineNode.RemoveAllControlPoints()

    lineNode.AddControlPointWorld(p0)
    lineNode.AddControlPointWorld(p1)

    return lineNode

# Read first two points from each fiducial list
f1_p0 = get_point_world(fiducialList1, 0)
f1_p1 = get_point_world(fiducialList1, 1)

f2_p0 = get_point_world(fiducialList2, 0)
f2_p1 = get_point_world(fiducialList2, 1)

# Create line nodes
line1Node = create_or_update_line(line1Name, f1_p0, f1_p1)
line2Node = create_or_update_line(line2Name, f2_p0, f2_p1)

# Define pivot and direction vectors
# The second point is the already-aligned shared point
pivot = f1_p1

# Optional check
pivot_distance = np.linalg.norm(f1_p1 - f2_p1)
print(f"Distance between point 1 of the two lists: {pivot_distance:.6f} mm")

# Direction vectors from point 1 to point 0
v1 = normalize(f1_p0 - f1_p1)
v2 = normalize(f2_p0 - f2_p1)


# Compute rotation from first line to second line
axis = np.cross(v1, v2)
axis_norm = np.linalg.norm(axis)

dot = np.clip(np.dot(v1, v2), -1.0, 1.0)
angle_rad = np.arccos(dot)
angle_deg = np.degrees(angle_rad)

if axis_norm < 1e-8:
    if dot > 0:
        print("The two lines already point in the same direction. No rotation needed.")
        axis = np.array([0.0, 0.0, 1.0])
        angle_deg = 0.0
    else:
        raise ValueError(
            "The two lines point in opposite directions. "
            "The rotation axis is ambiguous and needs to be defined manually."
        )
else:
    axis = axis / axis_norm

# --------------------------------------------------
# Build a rotation transform around the pivot point
# --------------------------------------------------
rotationOnlyTransform = vtk.vtkTransform()
rotationOnlyTransform.Identity()
rotationOnlyTransform.RotateWXYZ(angle_deg, axis[0], axis[1], axis[2])

R_vtk = rotationOnlyTransform.GetMatrix()

R = np.eye(4)
for i in range(4):
    for j in range(4):
        R[i, j] = R_vtk.GetElement(i, j)

# Rotation around pivot:
# x' = R x + pivot - R pivot
M = np.eye(4)
M[:3, :3] = R[:3, :3]
M[:3, 3] = pivot - R[:3, :3] @ pivot

vtkMatrix = vtk.vtkMatrix4x4()
for i in range(4):
    for j in range(4):
        vtkMatrix.SetElement(i, j, M[i, j])


# --------------------------------------------------
# Create or update transform node
# --------------------------------------------------
transformNode = slicer.mrmlScene.GetFirstNodeByName(transformName)

if transformNode is None:
    transformNode = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLLinearTransformNode",
        transformName
    )

transformNode.SetMatrixTransformToParent(vtkMatrix)


# --------------------------------------------------
# Apply transform to the entire first fiducial list
# --------------------------------------------------
fiducialList1.SetAndObserveTransformNodeID(transformNode.GetID())

