### 1. Create surface model from tet mesh.
First, create a surface model using `extract_surface_from_tet_vtk.py`

Set up the directories. Set up `DEFAULT_STAGTE_DIR` manually to the root dir that contains the model files manually if needed.
```
DEFAULT_STAGE_DIR = mesh_select_subdir("1224", "1224_remesh")
DEFAULT_TET_VTK = os.path.join(DEFAULT_STAGE_DIR, "1224_tissue_remesh_1_6k.vtk")
DEFAULT_SURFACE_VTK = os.path.join(DEFAULT_STAGE_DIR, "1224_tissue_remesh_surface_from_tet_1_6k.vtk")
DEFAULT_SURFACE_OBJ = os.path.join(DEFAULT_STAGE_DIR, "1224_tissue_remesh_surface_from_tet_1_6k.obj")
```

### 2. Create tissue attachment points from a tissue patch model.
In Slicer, load both the tissue tet mesh (vtk) and created surface models.

Create a closed curve and fit the curve onto the surface model, and add a few points inside the curve. Use Curve Cut in Dynamic Modeler to create a tissue patch called 'TissueRoofPatch' in the example. Uncheck `Straight cut`.
<img width="300" alt="image" src="https://github.com/user-attachments/assets/964d3d3d-5315-49ea-bcc5-7d1bf843f139" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/6e02614b-fd8f-474a-b659-e6f6a776c2ff" />

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

### 3. Create a curve to cut the orbital roof/wall by point projection.
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

### 4. Extract bone point indices to be excluded from the point collision model from regions roughly equivalent to the tissue patch model.
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







