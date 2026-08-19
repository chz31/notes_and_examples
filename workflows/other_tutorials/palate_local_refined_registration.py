"""
Local refined rigid registration for upper palate wound measurement in 3D Slicer.

This script expects two already globally rigid-registered palate surface models:
source = initial presurgery palate, target = post-surgery palate.

It uses:
  - Dynamic Modeler "ROI cut" to crop both models with the same ROI.
  - Dynamic Modeler "Curve cut" to remove the surgical site from each local crop,
    producing annulus models. The surgical-site curve and inside points are
    manually placed on the target model, then projected onto the original source
    model surface and used to cut the ROI-cropped source model.
  - FastModelAlign rigid registration to align the source annulus to the target
    annulus.
  - The annulus transform hardened onto a clone of the ROI-cropped source model,
    preserving the surgical site in the locally refined source model.
  - Optional CPD warping, fit on the rigid-registered source annulus to target
    annulus, then applied to the full locally refined source patch. This runs
    by default; set perform_cpd_warping=0 to skip it.

Example in Slicer's Python interactor:

exec(open("/home/zhang/Documents/chi_vs_workspace/other_scripts/palate_local_refined_registration.py").read())

result = run_palate_local_refined_registration(
    source_model_name="initial_presurgery_global_registered",
    target_model_name="Final Surgery Scan",
    roi_name="SurgerySiteROI",
    target_curve_name="target_surgery_site_curve",
    target_inside_points_name="target_surgery_site_inside_points",
    perform_cpd_warping=1,
)

The returned dictionary contains the important created nodes.
"""

import os

import slicer
import vtk
import vtk.util.numpy_support as vtk_np


DEFAULT_FAST_MODEL_ALIGN_PARAMETERS = {
    "pointDensity": 1.5,
    "normalSearchRadius": 2.0,
    "FPFHNeighbors": 100,
    "FPFHSearchRadius": 5.0,
    "distanceThreshold": 3.0,
    "maxRANSAC": 1000000,
    "ICPDistanceThreshold": 1.5,
}

# Higher alpha = more rigid, less deformation. Lower alpha = more flexible warping.
# Higher beta = smoother, broader deformation that changes gradually across the patch. Lower beta = more local, sharper deformation.
DEFAULT_CPD_PARAMETERS = {
    "pointDensity": 1.5,
    "normalSearchRadius": 2.0,
    "FPFHNeighbors": 100,
    "FPFHSearchRadius": 5.0,
    "distanceThreshold": 3.0,
    "maxRANSAC": 1000000,
    "ICPDistanceThreshold": 1.5,
    "alpha": 4.0,
    "beta": 6.0,
    "CPDIterations": 100,
    "CPDTolerance": 0.001,
    "Acceleration": 0,
    "BCPDFolder": "",
}


def get_current_fast_model_align_ui_settings():
    try:
        widget = slicer.modules.fastmodelalign.widgetRepresentation().self()
        ui = widget.ui
    except Exception:
        return None, None

    parameters = {
        "pointDensity": ui.pointDensityAdvancedSlider.value,
        "normalSearchRadius": ui.normalSearchRadiusSlider.value,
        "FPFHNeighbors": int(ui.FPFHNeighborsSlider.value),
        "FPFHSearchRadius": ui.FPFHSearchRadiusSlider.value,
        "distanceThreshold": ui.maximumCPDThreshold.value,
        "maxRANSAC": int(ui.maxRANSAC.value),
        "ICPDistanceThreshold": float(ui.ICPDistanceThresholdSlider.value),
    }
    return parameters, bool(ui.poissonSubsampleCheckBox.checked)


def get_node(name_or_node):
    if hasattr(name_or_node, "GetID"):
        return name_or_node
    node = slicer.mrmlScene.GetFirstNodeByName(name_or_node)
    if node is None:
        raise RuntimeError(f"Could not find node '{name_or_node}'")
    return node


def remove_existing_node(name):
    existing = slicer.mrmlScene.GetFirstNodeByName(name)
    if existing is not None:
        slicer.mrmlScene.RemoveNode(existing)


def unique_name(base_name, overwrite_existing=True):
    if overwrite_existing:
        remove_existing_node(base_name)
        return base_name
    return slicer.mrmlScene.GenerateUniqueName(base_name)


def clone_node(node, output_name, harden_transform=True, overwrite_existing=True):
    output_name = unique_name(output_name, overwrite_existing)
    sh_node = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    item_id = sh_node.GetItemByDataNode(node)
    if item_id:
        cloned_item_id = slicer.modules.subjecthierarchy.logic().CloneSubjectHierarchyItem(
            sh_node, item_id
        )
        clone = sh_node.GetItemDataNode(cloned_item_id)
        clone.SetName(output_name)
    else:
        clone = slicer.mrmlScene.AddNewNodeByClass(node.GetClassName(), output_name)
        clone.Copy(node)
        clone.SetName(output_name)

    clone.CreateDefaultDisplayNodes()
    if harden_transform and clone.GetParentTransformNode() is not None:
        slicer.vtkSlicerTransformLogic().hardenTransform(clone)
    return clone


def model_polydata_in_world(model_node):
    polydata = model_node.GetPolyData()
    if polydata is None or polydata.GetNumberOfPoints() == 0:
        raise RuntimeError(f"Model '{model_node.GetName()}' has no polydata points")

    transform_node = model_node.GetParentTransformNode()
    if transform_node is None:
        output = vtk.vtkPolyData()
        output.DeepCopy(polydata)
        return output

    transform = vtk.vtkGeneralTransform()
    slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(transform_node, None, transform)

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(polydata)
    transform_filter.SetTransform(transform)
    transform_filter.Update()

    output = vtk.vtkPolyData()
    output.DeepCopy(transform_filter.GetOutput())
    return output


def create_model_node(name, color=None, opacity=1.0, overwrite_existing=True):
    name = unique_name(name, overwrite_existing)
    model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", name)
    model_node.CreateDefaultDisplayNodes()
    display_node = model_node.GetDisplayNode()
    if display_node is not None:
        display_node.SetOpacity(float(opacity))
        if color is not None:
            display_node.SetColor(*color)
    return model_node


def run_dynamic_modeler_roi_cut(input_model_node, roi_node, output_name, overwrite_existing=True):
    output_node = create_model_node(output_name, overwrite_existing=overwrite_existing)

    dynamic_modeler_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
    dynamic_modeler_node.SetToolName("ROI cut")
    dynamic_modeler_node.SetNodeReferenceID("ROICut.InputModel", input_model_node.GetID())
    dynamic_modeler_node.SetNodeReferenceID("ROICut.InputROI", roi_node.GetID())
    dynamic_modeler_node.SetNodeReferenceID("ROICut.OutputPositiveModel", output_node.GetID())

    slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamic_modeler_node)
    slicer.mrmlScene.RemoveNode(dynamic_modeler_node)

    validate_model_has_cells(output_node, "ROI cut")
    return output_node


def run_dynamic_modeler_curve_cut(
    input_model_node,
    curve_node,
    inside_points_node,
    output_name,
    keep_inside=False,
    use_straight_cut=False,
    overwrite_existing=True,
):
    if not curve_node.IsA("vtkMRMLMarkupsClosedCurveNode"):
        raise RuntimeError(
            f"Curve cut requires a closed curve node. "
            f"'{curve_node.GetName()}' is {curve_node.GetClassName()}."
        )
    if inside_points_node is None or inside_points_node.GetNumberOfControlPoints() == 0:
        raise RuntimeError("Curve cut requires a fiducial point list with at least one inside point.")

    output_node = create_model_node(output_name, overwrite_existing=overwrite_existing)

    dynamic_modeler_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
    dynamic_modeler_node.SetToolName("Curve cut")
    dynamic_modeler_node.SetNodeReferenceID("CurveCut.InputModel", input_model_node.GetID())
    dynamic_modeler_node.SetNodeReferenceID("CurveCut.InputCurve", curve_node.GetID())
    dynamic_modeler_node.SetNodeReferenceID("CurveCut.InsidePoint", inside_points_node.GetID())

    if keep_inside:
        dynamic_modeler_node.SetNodeReferenceID("CurveCut.OutputInside", output_node.GetID())
    else:
        dynamic_modeler_node.SetNodeReferenceID("CurveCut.OutputOutside", output_node.GetID())

    # Compatibility roles for older/nightly builds. Current Slicer uses
    # InputCurve, InsidePoint, OutputInside/OutputOutside, and StraightCut.
    dynamic_modeler_node.SetNodeReferenceID("CurveCut.CuttingCurve", curve_node.GetID())
    dynamic_modeler_node.SetNodeReferenceID("CurveCut.SelectionPoint", inside_points_node.GetID())
    dynamic_modeler_node.SetNodeReferenceID("CurveCut.InputFiducial", inside_points_node.GetID())
    dynamic_modeler_node.SetNodeReferenceID("CurveCut.OutputModel", output_node.GetID())

    straight_cut_value = "true" if use_straight_cut else "false"
    dynamic_modeler_node.SetAttribute("CurveCut.StraightCut", straight_cut_value)
    dynamic_modeler_node.SetAttribute("CurveCut.UseStraightCut", straight_cut_value)
    dynamic_modeler_node.SetAttribute("CurveCut.KeepCellsInside", str(bool(keep_inside)).lower())
    dynamic_modeler_node.SetAttribute("CurveCut.KeepCellsOutside", str(not bool(keep_inside)).lower())

    slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamic_modeler_node)
    slicer.mrmlScene.RemoveNode(dynamic_modeler_node)

    validate_model_has_cells(output_node, "Curve cut")
    return output_node


def validate_model_has_cells(model_node, operation_name):
    mesh = model_node.GetMesh()
    number_of_points = mesh.GetNumberOfPoints() if mesh is not None else 0
    number_of_cells = mesh.GetNumberOfCells() if mesh is not None else 0
    if number_of_points == 0 or number_of_cells == 0:
        raise RuntimeError(
            f"{operation_name} produced empty model '{model_node.GetName()}'. "
            "Check the ROI, curve, inside points, and model transforms."
        )
    print(
        f"[PalateLocalRegistration] {operation_name}: '{model_node.GetName()}' "
        f"has {number_of_points} points and {number_of_cells} cells",
        flush=True,
    )


def get_markup_control_points_world(markups_node):
    points = vtk.vtkPoints()
    labels = []

    for point_index in range(markups_node.GetNumberOfControlPoints()):
        if hasattr(markups_node, "GetNthControlPointPositionStatus"):
            status = markups_node.GetNthControlPointPositionStatus(point_index)
            if status == markups_node.PositionUndefined:
                continue
        point = [0.0, 0.0, 0.0]
        markups_node.GetNthControlPointPositionWorld(point_index, point)
        points.InsertNextPoint(point)
        labels.append(markups_node.GetNthControlPointLabel(point_index) or str(point_index))

    if points.GetNumberOfPoints() == 0:
        raise RuntimeError(f"Markup node '{markups_node.GetName()}' has no defined control points")
    return points, labels


def ensure_point_normals(polydata):
    normals = polydata.GetPointData().GetArray("Normals")
    if normals is not None:
        return polydata, normals

    normal_filter = vtk.vtkPolyDataNormals()
    normal_filter.SetInputData(polydata)
    normal_filter.ComputePointNormalsOn()
    normal_filter.ComputeCellNormalsOff()
    normal_filter.SplittingOff()
    normal_filter.ConsistencyOn()
    normal_filter.AutoOrientNormalsOff()
    normal_filter.Update()

    normal_polydata = normal_filter.GetOutput()
    normals = normal_polydata.GetPointData().GetArray("Normals")
    if normals is None:
        raise RuntimeError("Could not compute source model point normals")
    return normal_polydata, normals


def project_points_polydata(
    source_polydata,
    target_polydata,
    original_points,
    ray_length_mm,
    use_closest_point_fallback=True,
):
    source_polydata, normals = ensure_point_normals(source_polydata)

    source_locator = vtk.vtkPointLocator()
    source_locator.SetDataSet(source_polydata)
    source_locator.BuildLocator()

    target_locator = vtk.vtkPointLocator()
    target_locator.SetDataSet(target_polydata)
    target_locator.BuildLocator()

    obb_tree = vtk.vtkOBBTree()
    obb_tree.SetDataSet(target_polydata)
    obb_tree.BuildLocator()

    projected_points = vtk.vtkPoints()
    statuses = []
    for point_index in range(original_points.GetNumberOfPoints()):
        original_point = original_points.GetPoint(point_index)
        source_point_id = source_locator.FindClosestPoint(original_point)
        normal = normals.GetTuple(source_point_id)

        forward_end = [original_point[dim] + normal[dim] * ray_length_mm for dim in range(3)]
        intersection_ids = vtk.vtkIdList()
        intersection_points = vtk.vtkPoints()
        obb_tree.IntersectWithLine(original_point, forward_end, intersection_points, intersection_ids)
        if intersection_points.GetNumberOfPoints() > 0:
            projected_points.InsertNextPoint(
                intersection_points.GetPoint(intersection_points.GetNumberOfPoints() - 1)
            )
            statuses.append("forward")
            continue

        reverse_end = [original_point[dim] - normal[dim] * ray_length_mm for dim in range(3)]
        intersection_ids.Reset()
        intersection_points.Reset()
        obb_tree.IntersectWithLine(original_point, reverse_end, intersection_points, intersection_ids)
        if intersection_points.GetNumberOfPoints() > 0:
            projected_points.InsertNextPoint(intersection_points.GetPoint(0))
            statuses.append("reverse")
            continue

        if use_closest_point_fallback:
            target_point_id = target_locator.FindClosestPoint(original_point)
            projected_points.InsertNextPoint(target_polydata.GetPoint(target_point_id))
            statuses.append("closest")
            continue

        projected_points.InsertNextPoint(original_point)
        statuses.append("failed")

    print(
        "[PalateLocalRegistration] Projection status: "
        f"forward={statuses.count('forward')}, reverse={statuses.count('reverse')}, "
        f"closest={statuses.count('closest')}, failed={statuses.count('failed')}",
        flush=True,
    )
    return projected_points, statuses


def create_projected_curve_node(source_curve_node, target_model_node, projected_points, labels, output_name):
    output_name = unique_name(output_name, overwrite_existing=True)
    curve_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode", output_name)
    for point_index in range(projected_points.GetNumberOfPoints()):
        point = projected_points.GetPoint(point_index)
        label = labels[point_index] if point_index < len(labels) else str(point_index)
        curve_node.AddControlPointWorld(vtk.vtkVector3d(*point), label)

    if hasattr(curve_node, "SetAndObserveSurfaceConstraintNode"):
        curve_node.SetAndObserveSurfaceConstraintNode(target_model_node)
    else:
        curve_node.SetAndObserveShortestDistanceSurfaceNode(target_model_node)
    curve_node.SetCurveTypeToShortestDistanceOnSurface(target_model_node)

    source_display = source_curve_node.GetDisplayNode()
    curve_node.CreateDefaultDisplayNodes()
    output_display = curve_node.GetDisplayNode()
    if source_display is not None and output_display is not None:
        output_display.SetColor(*source_display.GetColor())
        output_display.SetSelectedColor(*source_display.GetSelectedColor())
        output_display.SetLineThickness(source_display.GetLineThickness())
        output_display.SetTextScale(source_display.GetTextScale())

    return curve_node


def create_projected_fiducial_node(projected_points, labels, output_name):
    output_name = unique_name(output_name, overwrite_existing=True)
    fiducials = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", output_name)
    for point_index in range(projected_points.GetNumberOfPoints()):
        point = projected_points.GetPoint(point_index)
        label = labels[point_index] if point_index < len(labels) else str(point_index)
        fiducials.AddControlPointWorld(vtk.vtkVector3d(*point), label)
    fiducials.SetLocked(True)
    display_node = fiducials.GetDisplayNode()
    if display_node is not None:
        display_node.SetTextScale(0.0)
    return fiducials


def project_markups_from_source_to_target(
    markups_node,
    source_model_node,
    target_model_node,
    output_name,
    ray_length_mm=None,
    max_projection_factor=0.02,
):
    source_polydata = model_polydata_in_world(source_model_node)
    target_polydata = model_polydata_in_world(target_model_node)
    points, labels = get_markup_control_points_world(markups_node)
    if ray_length_mm is None:
        ray_length_mm = max(source_polydata.GetLength(), target_polydata.GetLength()) * max_projection_factor

    projected_points, statuses = project_points_polydata(
        source_polydata,
        target_polydata,
        points,
        float(ray_length_mm),
        use_closest_point_fallback=True,
    )

    if markups_node.IsA("vtkMRMLMarkupsCurveNode"):
        output_node = create_projected_curve_node(
            markups_node,
            target_model_node,
            projected_points,
            labels,
            output_name,
        )
    else:
        output_node = create_projected_fiducial_node(projected_points, labels, output_name)
    return output_node, statuses


def fast_model_align_rigid_registration(
    source_model_node,
    target_model_node,
    output_transform_name,
    parameters=None,
    use_poisson=None,
    require_fast_model_align=True,
    prefer_ui_settings=True,
):
    try:
        import FastModelAlign
    except Exception as exc:
        if require_fast_model_align:
            raise RuntimeError(
                "FastModelAlign could not be imported. Install/enable SlicerMorph "
                "and open FastModelAlign once if its dependencies need setup."
            ) from exc
        return vtk_icp_rigid_registration(source_model_node, target_model_node, output_transform_name)

    ui_parameters, ui_use_poisson = (
        get_current_fast_model_align_ui_settings() if prefer_ui_settings else (None, None)
    )
    parameter_dictionary = dict(ui_parameters or DEFAULT_FAST_MODEL_ALIGN_PARAMETERS)
    if parameters:
        parameter_dictionary.update(parameters)
    if use_poisson is None:
        use_poisson = ui_use_poisson if ui_use_poisson is not None else False

    print(
        "[PalateLocalRegistration] FastModelAlign parameters: "
        f"{parameter_dictionary}, scaling=False, poisson={bool(use_poisson)}",
        flush=True,
    )

    registration_source = clone_node(
        source_model_node,
        source_model_node.GetName() + "_fast_model_align_working",
        harden_transform=True,
        overwrite_existing=True,
    )

    logic = FastModelAlign.FastModelAlignLogic()
    _, _, scaling_transform_node, transform_node = logic.ITKRegistration(
        registration_source,
        target_model_node,
        False,
        parameter_dictionary,
        bool(use_poisson),
    )
    transform_node.SetName(unique_name(output_transform_name, overwrite_existing=True))

    if scaling_transform_node is not None:
        slicer.mrmlScene.RemoveNode(scaling_transform_node)

    registered_source_name = unique_name(
        source_model_node.GetName() + "_registered_to_target_annulus",
        overwrite_existing=True,
    )
    registration_source.SetName(registered_source_name)
    registration_source.CreateDefaultDisplayNodes()
    if registration_source.GetDisplayNode() is not None:
        registration_source.GetDisplayNode().SetColor(1.0, 0.0, 0.0)
        registration_source.GetDisplayNode().SetOpacity(0.7)

    return transform_node, registration_source


def vtk_icp_rigid_registration(source_model_node, target_model_node, output_transform_name):
    source_polydata = model_polydata_in_world(source_model_node)
    target_polydata = model_polydata_in_world(target_model_node)

    icp = vtk.vtkIterativeClosestPointTransform()
    icp.SetSource(source_polydata)
    icp.SetTarget(target_polydata)
    icp.GetLandmarkTransform().SetModeToRigidBody()
    icp.SetMaximumNumberOfIterations(200)
    icp.StartByMatchingCentroidsOn()
    icp.Modified()
    icp.Update()

    transform_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLTransformNode",
        unique_name(output_transform_name, overwrite_existing=True),
    )
    transform_node.SetMatrixTransformToParent(icp.GetMatrix())
    registered_source = clone_node(
        source_model_node,
        source_model_node.GetName() + "_vtk_icp_registered_to_target_annulus",
        harden_transform=True,
        overwrite_existing=True,
    )
    registered_source.SetAndObserveTransformNodeID(transform_node.GetID())
    slicer.vtkSlicerTransformLogic().hardenTransform(registered_source)
    return transform_node, registered_source


def harden_transform_on_model_clone(input_model_node, transform_node, output_name):
    output_node = clone_node(input_model_node, output_name, harden_transform=True, overwrite_existing=True)
    output_node.SetAndObserveTransformNodeID(transform_node.GetID())
    slicer.vtkSlicerTransformLogic().hardenTransform(output_node)
    output_node.CreateDefaultDisplayNodes()
    if output_node.GetDisplayNode() is not None:
        output_node.GetDisplayNode().SetColor(0.0, 0.6, 1.0)
        output_node.GetDisplayNode().SetOpacity(0.85)
    return output_node


def run_cpd_annulus_extrapolation(
    source_annulus_registered_node,
    target_annulus_node,
    source_full_refined_node,
    output_name,
    parameters=None,
    use_poisson=False,
    overwrite_existing=True,
):
    try:
        import ALPACA
    except Exception as exc:
        raise RuntimeError(
            "ALPACA could not be imported. Install/enable SlicerMorph before CPD warping."
        ) from exc

    parameter_dictionary = dict(DEFAULT_CPD_PARAMETERS)
    if parameters:
        parameter_dictionary.update(parameters)

    print(
        "[PalateLocalRegistration] CPD parameters: "
        f"{parameter_dictionary}, scaling=False, poisson={bool(use_poisson)}",
        flush=True,
    )

    alpaca_logic = ALPACA.ALPACALogic()
    source_slm, target_slm, _, _, _, _ = alpaca_logic.runSubsample(
        source_annulus_registered_node,
        target_annulus_node,
        False,
        parameter_dictionary,
        bool(use_poisson),
    )
    print(
        "[PalateLocalRegistration] CPD annulus subsample: "
        f"source={len(source_slm)} points, target={len(target_slm)} points",
        flush=True,
    )

    source_full_polydata = model_polydata_in_world(source_full_refined_node)
    source_full_points = source_full_polydata.GetPoints()
    if source_full_points is None or source_full_points.GetNumberOfPoints() == 0:
        raise RuntimeError(
            f"Full source model '{source_full_refined_node.GetName()}' has no points for CPD warping."
        )

    source_full_points_array = vtk_np.vtk_to_numpy(source_full_points.GetData()).copy()
    warped_full_points = alpaca_logic.runCPDRegistration(
        source_full_points_array,
        source_slm,
        target_slm,
        parameter_dictionary,
    )
    if warped_full_points.shape[0] != source_full_points_array.shape[0]:
        raise RuntimeError(
            "CPD returned a different number of warped points than the full source model has."
        )

    warped_polydata = vtk.vtkPolyData()
    warped_polydata.DeepCopy(source_full_polydata)
    warped_polydata.GetPoints().SetData(vtk_np.numpy_to_vtk(warped_full_points, deep=True))
    warped_polydata.Modified()

    output_name = unique_name(output_name, overwrite_existing=overwrite_existing)
    warped_model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", output_name)
    warped_model_node.CreateDefaultDisplayNodes()
    warped_model_node.SetAndObservePolyData(warped_polydata)
    if warped_model_node.GetDisplayNode() is not None:
        warped_model_node.GetDisplayNode().SetColor(0.0, 1.0, 0.0)
        warped_model_node.GetDisplayNode().SetOpacity(0.85)

    print(
        "[PalateLocalRegistration] CPD warped full source model: "
        f"{warped_model_node.GetName()}",
        flush=True,
    )
    return warped_model_node


def save_outputs(output_dir, nodes_to_save):
    if not output_dir:
        return
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    for node in nodes_to_save:
        if node is None:
            continue
        file_name = node.GetName().replace(" ", "_")
        if node.IsA("vtkMRMLTransformNode"):
            path = os.path.join(output_dir, file_name + ".h5")
        elif node.IsA("vtkMRMLModelNode"):
            path = os.path.join(output_dir, file_name + ".ply")
        elif node.IsA("vtkMRMLMarkupsNode"):
            path = os.path.join(output_dir, file_name + ".mrk.json")
        else:
            continue
        slicer.util.saveNode(node, path)
        print(f"[PalateLocalRegistration] Saved {node.GetName()} -> {path}", flush=True)


def run_palate_local_refined_registration(
    source_model_name,
    target_model_name,
    roi_name,
    target_curve_name,
    target_inside_points_name,
    output_prefix="palate",
    curve_cut_keep_inside=False,
    curve_cut_use_straight_cut=False,
    projection_ray_length_mm=None,
    projection_max_factor=0.02,
    fast_model_align_parameters=None,
    fast_model_align_use_poisson=None,
    prefer_fast_model_align_ui_settings=True,
    perform_cpd_warping=1,
    cpd_parameters=None,
    cpd_use_poisson=False,
    require_fast_model_align=True,
    output_dir=None,
):
    source_model = get_node(source_model_name)
    target_model = get_node(target_model_name)
    roi_node = get_node(roi_name)
    target_curve = get_node(target_curve_name)
    target_inside_points = get_node(target_inside_points_name)

    source_for_roi = clone_node(source_model, output_prefix + "_source_world", harden_transform=True)
    target_for_roi = clone_node(target_model, output_prefix + "_target_world", harden_transform=True)
    roi_for_cut = clone_node(roi_node, output_prefix + "_roi_world", harden_transform=True)
    target_curve_world = clone_node(
        target_curve,
        output_prefix + "_target_surgery_curve_world",
        harden_transform=True,
    )
    target_inside_points_world = clone_node(
        target_inside_points,
        output_prefix + "_target_inside_points_world",
        harden_transform=True,
    )

    source_roi = run_dynamic_modeler_roi_cut(
        source_for_roi,
        roi_for_cut,
        output_prefix + "_source_roi_cut",
    )
    target_roi = run_dynamic_modeler_roi_cut(
        target_for_roi,
        roi_for_cut,
        output_prefix + "_target_roi_cut",
    )

    target_annulus = run_dynamic_modeler_curve_cut(
        target_roi,
        target_curve_world,
        target_inside_points_world,
        output_prefix + "_target_annulus",
        keep_inside=curve_cut_keep_inside,
        use_straight_cut=curve_cut_use_straight_cut,
    )

    source_curve, curve_projection_status = project_markups_from_source_to_target(
        target_curve_world,
        target_for_roi,
        source_for_roi,
        output_prefix + "_source_projected_surgery_curve",
        ray_length_mm=projection_ray_length_mm,
        max_projection_factor=projection_max_factor,
    )
    source_inside_points, point_projection_status = project_markups_from_source_to_target(
        target_inside_points_world,
        target_for_roi,
        source_for_roi,
        output_prefix + "_source_projected_inside_points",
        ray_length_mm=projection_ray_length_mm,
        max_projection_factor=projection_max_factor,
    )

    source_annulus = run_dynamic_modeler_curve_cut(
        source_roi,
        source_curve,
        source_inside_points,
        output_prefix + "_source_annulus",
        keep_inside=curve_cut_keep_inside,
        use_straight_cut=curve_cut_use_straight_cut,
    )

    annulus_transform, registered_source_annulus = fast_model_align_rigid_registration(
        source_annulus,
        target_annulus,
        output_prefix + "_source_annulus_to_target_annulus_transform",
        parameters=fast_model_align_parameters,
        use_poisson=fast_model_align_use_poisson,
        require_fast_model_align=require_fast_model_align,
        prefer_ui_settings=prefer_fast_model_align_ui_settings,
    )

    refined_source = harden_transform_on_model_clone(
        source_roi,
        annulus_transform,
        output_prefix + "_source_roi_cut_local_refined",
    )

    cpd_warped_source = None
    if bool(perform_cpd_warping):
        cpd_warped_source = run_cpd_annulus_extrapolation(
            registered_source_annulus,
            target_annulus,
            refined_source,
            output_prefix + "_source_roi_cut_local_refined_cpd_warped",
            parameters=cpd_parameters,
            use_poisson=cpd_use_poisson,
        )

    result = {
        "source_roi": source_roi,
        "target_roi": target_roi,
        "target_curve_world": target_curve_world,
        "target_inside_points_world": target_inside_points_world,
        "source_projected_curve": source_curve,
        "source_projected_inside_points": source_inside_points,
        "source_annulus": source_annulus,
        "target_annulus": target_annulus,
        "annulus_transform": annulus_transform,
        "registered_source_annulus": registered_source_annulus,
        "refined_source": refined_source,
        "cpd_warped_source": cpd_warped_source,
        "curve_projection_status": curve_projection_status,
        "point_projection_status": point_projection_status,
    }

    save_outputs(
        output_dir,
        [
            source_roi,
            target_roi,
            target_curve_world,
            target_inside_points_world,
            source_curve,
            source_inside_points,
            source_annulus,
            target_annulus,
            annulus_transform,
            registered_source_annulus,
            refined_source,
            cpd_warped_source,
        ],
    )

    print("[PalateLocalRegistration] Completed local refined registration.", flush=True)
    print(
        "[PalateLocalRegistration] Refined source model: "
        f"{refined_source.GetName()}",
        flush=True,
    )
    print(
        "[PalateLocalRegistration] Annulus transform: "
        f"{annulus_transform.GetName()}",
        flush=True,
    )
    return result
