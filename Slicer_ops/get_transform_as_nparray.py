#Get a linear transform
import numpy as np
transformNode = slicer.util.getNode("Transform")

matrix = vtk.vtkMatrix4x4()
transformNode.GetMatrixTransformToWorld(matrix)

# Convert to numpy
mat_np = np.array([[matrix.GetElement(i, j) for j in range(4)] for i in range(4)])

print(mat_np)
