### 1. Create tissue attachment points from a tissue patch model.
In Slicer, load both the combined tissue tet mesh (vtk) and the surface model directed extracted from it (see the Meshing tutorial).

Open `Markups` module. Create a closed curve to enclose a region that represents tissue attachment without compromising retraction, such as roof and upper part of medial and lateral wall. 

Under `Curve Settings`, constrain the curve to the surface model<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/b6d0b0e6-070b-4680-b6ba-0de573ef547f" />

In `Markups` module, create a `Point List` and add a few points inside the curve.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/964d3d3d-5315-49ea-bcc5-7d1bf843f139" />
 
Switch to the `Dynamic Modeler` module and create a new `Curve Cut`.<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/08779d8d-6dba-49b5-a47a-3cfc96d5300c" />

Fill the 'Input Nodes` and Uncheck `Straight cut`. In `Ouput nodes` --> `Inside model`, create a new model as 'TissueRoofPatch` or any other name you prefer. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/6e02614b-fd8f-474a-b659-e6f6a776c2ff" />

Hit Apply to create a patch.<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/5f15903c-9b6c-4d13-ab99-1471a36f2230" />


### 2. Sample tissue attachment points using the 
In the script `slicer_tissue_attachment_points_from_patch.py`, update the names in lines 32-36
```
# Export sparse attachment indices from an existing patch.
rows = export_tissue_attachment_points_from_patch(
    patch_model_name="TissueRoofPatch",
    original_model_name="orbital_tissue_remesh_1k",
    min_anchor_spacing_mm=4.0,
    original_match_tolerance_mm=0.05,
)
```
Update `patch_model_name` and `original_model_name`. Change the `min_anchor_spacing` for denser attachment points.

Use line 66 to the same ROOT_DIR as the mesh dir.
```
ROOT_DIR = "C:/Users/chi.zhang/Documents/mesh_select/sample_data_debug/new_meshes"
```
Update line 72 to save the output point indices in csv.
```
DEFAULT_OUTPUT_CSV = os.path.join(ROOT_DIR, "tissue_attachment_points.csv")
```
Ctrl+G to load the script `slicer_tissue_attachment_points_from_patch.py` in Slicer.

Copy-paste lines 30-36 in Slicer's Python console and run it. It should generate `TissueAttachment_patch_points` and `TissueAttachment_surface_points` nodes and export `tissue_attachment_points.csv`. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/2c798cc8-d5d5-48c5-a73c-32e8173020df" />

Check if `TissueAttachment_patch_points` and `TissueAttachment_surface_points` have overlapped points. 


## (Alternative approach) Create roof-tissue pairwise attachment points
### Sample tissue attachment points using the 
In the script `slicer_tissue_attachment_points_from_patch.py`, update the names in lines 31-35
```
rows = export_tissue_attachment_points_from_patch(
    patch_model_name="TissueRoofPatch",
    original_model_name="1224_tissue_remesh_1_6k_1",
    min_anchor_spacing_mm=2.0,
    original_match_tolerance_mm=0.05,
```
Update `patch_model_name` and `original_model_name`. Change the `min_anchor_spacing` for denser attachment points.

Use line 71 or 72 to save the output point indices in csv.
```
DEFAULT_OUTPUT_CSV = os.path.join(ROOT_DIR, "tissue_attachment_points.csv")
# DEFAULT_OUTPUT_CSV = os.path.join(ROOT_DIR, "orbit_collision_exclusion_points.csv")
```

Change 'patchName' at line 73 `patchName = "TissueAttachment"` accordingly.

Ctrl+G to load the script `slicer_tissue_attachment_points_from_patch.py` in Slicer.

Copy-paste lines 30-36 in Slicer's Python console and run it. It should generate `TissueAttachment_patch_points` and `TissueAttachment_surface_points` nodes and export `tissue_attachment_points.csv`. 
Check if `TissueAttachment_patch_points` and `TissueAttachment_surface_points` have overlapped points. 


### 1. Create a curve to cut the orbital roof/wall by point projection.
Load the skull surface model in Slicer. Ctrl+G to load `slicer_project_points_between_models.py`

In `slicer_project_points_between_models.py`, update lines 18-27 if necessary.
```
projected = project_markup_points_between_models(
    source_points_name="TissueRoofAttachCurve",
    source_model_name="1224_tissue_remesh_surface_from_tet_1_6k",
    target_model_name="1224_skull_remesh",
    output_points_name="TissueRoofAttachCurve_projected_to_orbit",
)

curve = create_closed_curve_from_points(
    points_node_name=projected.GetName(),
    output_curve_name="SkullPatchCurve",
)
```

Afterwards, ctrl+G to load the `slicer_project_points_between_models.py` in Slicer and copy-paste these lines in Slicer Python console. 
You should see that a curve is created and the points are located at the orbital surface. Go to the "Markups" module, select the curve, and set "Constraint to Model" to the skull model manually.
Adjust curve positions if needed. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/5f79b274-679a-4e4f-a18e-cade509d4434" />



### 2. Extract bone point indices to be excluded from the point collision model from regions roughly equivalent to the tissue patch model.
Use Dynamic Modeler - Curve Cut to cut an orbital patch model and name it as `OrbitRoofPatch`

In the script `slicer_tissue_attachment_points_from_patch.py`, update the names in lines 31-35 again for the skull models and curve:
```
rows = export_tissue_attachment_points_from_patch(
    patch_model_name="OrbitRoofPatch",
    original_model_name="1224_skull_remesh",
    min_anchor_spacing_mm=None,
    original_match_tolerance_mm=0.05,
)
```
Set the `min_anchor_spacing_mm=None` for all exclude all points in the region from Collision.

Uncomment line 72 to save the output point indices in csv.
```
# DEFAULT_OUTPUT_CSV = os.path.join(ROOT_DIR, "tissue_attachment_points.csv")
DEFAULT_OUTPUT_CSV = os.path.join(ROOT_DIR, "orbit_collision_exclusion_points.csv")
```
Change 'patchName' at line 73 `patchName = "OrbitRoof"` accordingly.

Ctrl+G to load the script `slicer_tissue_attachment_points_from_patch.py` in Slicer.

Copy-paste lines 30-36 in Slicer's Python console and run it. It should generate `TissueAttachment_patch_points` and `TissueAttachment_surface_points` nodes and export `orbit_collision_exclusion_points.csv`. 
Check if `OrbitRoof_patch_points` and `OrbitRoof_surface_points` have overlapped points. <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/5fcc174a-9a3a-446c-b764-d12c9789c0aa" />







