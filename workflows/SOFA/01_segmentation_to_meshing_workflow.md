## 1. Segmentation processing

### 1. Load the image and segmentation.

Switch to the `Segment Editor` module, select the segmentation and reference volume.

### 2. Create an empty orbital tissue segment for one side.
Create an empty segment to combine tissue segments into one and name it as something like "orbital_tissue_combined".

Use the Logical Operator tool in Segment Editor to add all orbital tissue on that side to the empty segment. **Don't forget to enable `Allow Overlapping` first.<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/6991cac5-6386-4dde-acd8-e44733051803" />

Browse through the slices. Make sure there is no internal holes. Switch to 'Smoothing' tool. In "Smoothing method", select "Closing (fill holes)". Alter kernal size to 5x5x5 pixels, and hit Apply.
This should close most small holes. You may also need to manually closing holes by using Paint tool.<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/b389c534-511c-49a3-96b2-d509b94748cf" />

### 3. Clean the skull segment, and create an empty new segment and copy the skull into it using Logical Operator. 
Use scissor tool to crop the skull to leave only orbital region. Clean the fracture site to remove isolated bones. Fill holes at the unfractured internal orbital surface, such as using the Paint Tool in Segment Editor. You may first use the "Closing (fill holes") effect in 
the smoothing method again and then manually paint the remaining holes.

Expand a cloned skull segment by 0.5mm (or at least one-voxel size) using `Margin` tool in `Segment Editor`<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/c0bbb713-3457-4276-8d58-2f24f5d67e2e" />

Subtract the full orbital tissue segment from the expanded skull segment. This should create an at least 1mm distance between fat tissue and the skull surfaces.<br>

### 4. Smoothing the combined orbital tissue segment
Switch to the "Smoothing" tool and select the segment you want to smooth. Adjust kernal size for 5x5x5 pxiel. Run the smoothing.
<img width="500" alt="image" src="https://github.com/user-attachments/assets/8ab6e23d-9479-405f-9bc4-b7c128e847d0" />

You can start with a global smoothing only. If a global smoothing is enough for fractured cases for fat herniation and meshing reported errors or very low quality (see below steps), more aggressive local smoothing might be needed. Expand "Smoothing brush options", check "Edit in 3D views", increase kernel size to 7x7 or even 9x9, then smooth the protruded regions in 3D manually, especially fat herniated regions. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/c4e0938f-2f48-4d31-bb7a-7e8be3553fa0" />

### 5. Convert orbital tissue and skull into a surface model, downsample and remesh it.
Go back to data module. Hide all other segments but only the combined orbital tissue segment. Right click the main segmentation node to export it as a model. The model tends to have high density of points.

Switch to the "Surface Toolbox" module. Before downsampling it, save your results first since downsampling may have some glitch. You can downsample the tissue model using the default.<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/29db9ed5-e1f2-40c2-9d00-94571ce9440f" />

You can then remesh it using `Uniform remesh` in the `Surface Toolbox` module. Try "Number of points" = 1 to 1.5k points. Set "Subdivide" = 1 or even 2. Visually check the resultant model. Pay attention to the herniated region. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/bb734214-d96a-4dab-86c4-c5ab45495f30" />

Go to "Models" module selected the remeshed surface. In "3D Display", select "Representation" as "Surface with Edges". You want to see uniformly distributed triangles, including herniated region like below:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/3382ab59-38e9-408d-8331-01573dd7ca8b" />

Save the segmentation in .seg.nrrd and model in both stl and obj.

### 6. Downsample and remesh the skull
Go back to the Segmentation Editor module and visualize the skull segment. Fix holes at the non-fractured region. You can use a paint brush with threshold to mask it. Use scissor to only keep the orbital region.

Convert the skull segment into a surface model.

Follow the instructions above to downsample or remesh the skull in Surface Toolbox. I would target about 1.5-2k points depending on how large the area you kept. The triangles should not be much finer than the picture below. <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/db903da1-66d8-409f-8cf2-60e616af350e" />

Save the segmentation in .seg.nrrd and model in both stl and obj.

## 2. Run gmsh script to do the meshing for the combined soft tissue model
In the gmsh script, change lines 11 and 12 for the correct path
```
path = '/full/path/to/the/root/foler/containing/the/soft/tissue/stl'
gmsh.merge(os.path.join(path, 'your_stl_file_name.stl'))
```
Go to the gmsh pixi env folder and activate the env:
```
pixi shell
```

Run the script.
```
python /full/path/to/the/script/root/folder/gmsh_mesh_creation_test.py
```

Hopefully, you can see something like below with internal tetrahedra:<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/aa0863d9-6537-4735-962e-ea1272c40ddf" />

Monitor if the terminal produced error messages.

If things go well, uncomment lines 115 and 116 and change the output model names to your choice
```
gmsh.write(os.path.join(path, 'your_choice_of_name.msh'))
gmsh.write(os.path.join(path, 'your_choice_of_name.vtk'))
```
The meshes in both msh and vtk formats should be saved in the folder specificed by `path`. You can load vtk into Slicer directly.

## 3. Run quality check
Look at the terminal. It should print out some basic information. <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/9af63575-b4d0-43c3-b418-cb161f5a3f69" />
Make assure the tetrahedra number is around 150k or smaller. If it exceeds 200k, then the surface model may be too dense or the element size might be too large (default = 2.0mm): `gmsh.model.mesh.field.setString(f, "F", "2")`

Optionaly, you can run a full quality check
```
python /home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/check_mesh_quality.py
```
Paste the output into the AI chat window to read it.

## 4.Create individual tissue surface models
Create below 3 segments:
- Eyeball
- Optic nerve
- A segment combined all muscles

Convert these segments to surface models.

Downsample or uniform remesh these surface models in Surface Toolbox to a few hundreds of points, for example
- Globe: 500 pts
- Optic nerve: 400 pts
- Muscle_combined: 900 pts
