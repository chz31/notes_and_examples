Get ROI bounds

```
import numpy as np
roi = slicer.util.getNode('R')
bounds = np.zeros(6)
roi.GetBounds(bounds)
```
It will print out xmin, xmax, ymin, ymax, zmin, zmax. In SOFA,reverse the sign of xmin, xmax, ymin, ymax for the ROI
