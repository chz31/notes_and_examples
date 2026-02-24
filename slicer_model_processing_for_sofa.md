Get ROI bounds

```
import numpy as np
roi = slicer.util.getNode('R')
bounds = np.zeros(6)
roi.GetBounds(bounds)
```
It will print out xmin, xmax, ymin, ymax, zmin, zmax. In SOFA,reverse the sign of xmin, xmax, ymin, ymax for the ROI. If run SlicerSOFA, then no need to reverse the signs.


Get center of mass from a surface model using `vtkCenterOfMass`:
```
modelNode = getNode('MyModelNode')
polyData = modelNode.GetPolyData()

# Compute Center of Mass
com = vtk.vtkCenterOfMass()
com.SetInputData(polyData)
com.Update()
center = com.GetCenter()
print(f"Center of Mass: {center}")
```


