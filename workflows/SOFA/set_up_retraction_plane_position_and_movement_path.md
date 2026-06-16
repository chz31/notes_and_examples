In this tutorial, we will create a plane model and set up a position

In `Create_plane_model_in_slicer.py`, change these numbers for size and point density:
width = 40.0
height = 25.0
xRes = 60   # increase for denser mesh
yRes = 40

We should aim at around 200 points or smaller. Don't make the plane too large.

Copy-paste the content in the Slicer console. You should see two plane models created, one with thickness and one without. Hide the one with thickness<br>

<img width="500" alt="image" src="https://github.com/user-attachments/assets/0f76fa02-a87f-4ea6-a0ed-0c6cfb6012a8" />

Right click the "eyeball" and check Interation transform. You should see:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/08ec72f5-45b5-49c8-97af-f87ea28100f2" />

Use the interaction transform handle to just below the tissue, not too far away. Right click the rotated transform symbol at the very right side and click "Harden Transform"

Export the plane model as obj. 

Now we need to extract the center of mass of the plane model. Change the first line into the plane model name for the hardened transformed plane with no thickness. Paste the code directly in Slicer's Python console.
```
modelNode = getNode('MyPlaneModelNode')
polyData = modelNode.GetPolyData()

# Compute Center of Mass
com = vtk.vtkCenterOfMass()
com.SetInputData(polyData)
com.Update()
center = com.GetCenter()
print(f"Center of Mass: {center}")
```
You should be able to see the center of mass coordinates are printed out.

In sofa_excercise.py, replace the first three numbers in line 55 `TOOL_INITIAL_POSE_SLICER = [-21.504049827060026, 96.1390150805589, -34.34271930512928, 0, 0, 0, 1]`


We can then define the motion of the plane. In Slicer, switch to the Markups Moduel. Click "Line" and create a line node.

<img width="300" alt="image" src="https://github.com/user-attachments/assets/86fa8ec4-7876-454c-9989-d955f7b59c1a" />

Run below script to get the start and end position in Slicer Python console:
```
# 1. Fetch your line node from the scene by its name
lineNode = slicer.util.getNode('L')  # Replace 'L' with your line node name

# 2. Extract control point coordinates as a NumPy array
coords = slicer.util.arrayFromMarkupsControlPoints(lineNode)

# 3. Access individual endpoints (Line nodes usually have exactly 2 points)
start_point = coords[0]
end_point = coords[1]

print(f"Start Point: {start_point}")
print(f"End Point: {end_point}")
```

You should see something like this:
```
Start Point: [-46.94150828 -44.58614906 -66.64108472]
End Point: [-53.98743235 -68.22664575  -3.7500321 ]
```

Make sure that start point is below the end point. You can verify it in Markups Module, select the line node you created, and expand Control Points.


Now, replace lines 64-65 with actual point in `sofa_experiments.py`
```
TOOL_START_POINT_SLICER = [0.0, 0.0, 0.0]
TOOL_END_POINT_SLICER = [0.0, 0.0, 1.0]
```


## Play with sofa_experiments.py
Assuming everything is setup. One easy way to play with it is to comment out all orbit object from lines 395 to lines 422.

Enter the sofa pixi folder and `pixi shell`.

Run the script see if the plane moves upward to lift the tissue.

Then go back, turn on the orbit. See if it works. It should be much slower.

