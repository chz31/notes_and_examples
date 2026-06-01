## 1. Segmentation processing

### 1. Load the image and segmentation.

Switch to the Segment Editor module, select the segmentation and reference volume.

### 2. Create an empty orbital tissue segment for one side.
Use logical operator to add all orbital tissue on that side to the empty segment.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/6991cac5-6386-4dde-acd8-e44733051803" />

Browse through the slices. Make sure there is no internal holes. Switch to 'Smoothing' tool. In "Smoothing method", select "Closing (fill holes)". Alter kernal size to 5x5x5 pixels, and hit Apply.
This should close most small holes. You may also need to manually closing holes by using Paint tool.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/b389c534-511c-49a3-96b2-d509b94748cf" />

### 3. Clean the skull semgnet, and create an empty new segment and copy the skull into it using Logical Operator. 
Use scissor tool to crop the skull to leave only orbital region. Clean the fracture site to remove isolated bones. Fill holes at the unfractured regions. You may first use the "Closing (fill holes") effect in 
the smoothing method again and then manually paint the remaining holes.

Expand a cloned skull segment by 1mm using Margin<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/c0bbb713-3457-4276-8d58-2f24f5d67e2e" />

Subtract the full orbital tissue segment from the expanded skull segment. This should create an at least 1mm distance between fat tissue and the skull surfaces.<br>

### 4. Smoothing the orbital tissue segment
Switch to the "Smoothing" tool and select the segment you want to smooth. Adjust kernal size for 3x3x3 pxiel. Run the smoothing.
<img width="300" alt="image" src="https://github.com/user-attachments/assets/8ab6e23d-9479-405f-9bc4-b7c128e847d0" />

A global smoothing may not be enough for fractured cases due to local protrusions. Local smoothing might be needed. Expand "Smoothing brush options", check "Edit in 3D views", increase the kernal size to 5x5x5 pixels or even bigger and
smooth the segment in 3D manually, especially local protrusions. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/c4e0938f-2f48-4d31-bb7a-7e8be3553fa0" />

### 5. Convert orbital tissue and skull into a surface model
Go back to data module. Hide all other segments but only the combined orbital tissue segment. Right click to export it as a model. The model tends to have high density. 

Switch to the "Surface Toolbox" module. 

Remesh the skull

Remsh the tissue

## 3. Run gmsh script to do the meshing
