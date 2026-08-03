"""
Project a Slicer markups curve from one model surface to another.

This script is based on slicer_project_points_between_models.py, but it skips
the intermediate fiducial markup node. It reads control points from an existing
curve, projects those points along source-model normals onto a target model,
creates a new curve node, and constrains that curve onto the target model.

Example from the Slicer Python interactor:

exec(open("/home/zhang/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/preprocessing/slicer_project_curve_between_models.py").read())

source_points_name = "final_annulus_cut"
source_model_name = "final_surgery_local"
target_model_name = "initial_local"
output_curve_name = source_points_name + "projected"

projected_curve = project_curve_between_models(
    source_curve_name=source_points_name,
    source_model_name=source_model_name,
    target_model_name=target_model_name,
    output_curve_name=output_curve_name,
)
"""

import slicer
import vtk


def get_node(name):
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node is None:
        raise RuntimeError(f"Could not find node '{name}'")
    return node


def remove_existing_node(name):
    existing = slicer.mrmlScene.GetFirstNodeByName(name)
    if existing is not None:
        slicer.mrmlScene.RemoveNode(existing)


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


def get_curve_control_points_world(curve_node):
    points = vtk.vtkPoints()
    labels = []

    for point_index in range(curve_node.GetNumberOfControlPoints()):
        if hasattr(curve_node, "GetNthControlPointPositionStatus"):
            status = curve_node.GetNthControlPointPositionStatus(point_index)
            if status == curve_node.PositionUndefined:
                continue

        point = [0.0, 0.0, 0.0]
        curve_node.GetNthControlPointPositionWorld(point_index, point)
        points.InsertNextPoint(point)
        labels.append(curve_node.GetNthControlPointLabel(point_index) or str(point_index))

    if points.GetNumberOfPoints() == 0:
        raise RuntimeError(f"Curve node '{curve_node.GetName()}' has no defined control points")
    return points, labels


def ensure_point_normals(polydata):
    normal_array = polydata.GetPointData().GetArray("Normals")
    if normal_array is not None:
        return polydata, normal_array

    normal_filter = vtk.vtkPolyDataNormals()
    normal_filter.SetInputData(polydata)
    normal_filter.ComputePointNormalsOn()
    normal_filter.ComputeCellNormalsOff()
    normal_filter.SplittingOff()
    normal_filter.ConsistencyOn()
    normal_filter.AutoOrientNormalsOff()
    normal_filter.Update()

    normal_polydata = normal_filter.GetOutput()
    normal_array = normal_polydata.GetPointData().GetArray("Normals")
    if normal_array is None:
        raise RuntimeError("Could not compute point normals on source model")
    return normal_polydata, normal_array


def project_points_polydata(
    source_polydata,
    target_polydata,
    original_points,
    ray_length,
    use_closest_point_fallback=True,
):
    print(f"[ProjectCurve] original control points: {original_points.GetNumberOfPoints()}", flush=True)

    source_polydata, normal_array = ensure_point_normals(source_polydata)

    obb_tree = vtk.vtkOBBTree()
    obb_tree.SetDataSet(target_polydata)
    obb_tree.BuildLocator()

    source_locator = vtk.vtkPointLocator()
    source_locator.SetDataSet(source_polydata)
    source_locator.BuildLocator()

    target_locator = vtk.vtkPointLocator()
    target_locator.SetDataSet(target_polydata)
    target_locator.BuildLocator()

    projected_points = vtk.vtkPoints()
    projection_status = []

    for point_index in range(original_points.GetNumberOfPoints()):
        original_point = original_points.GetPoint(point_index)
        closest_source_id = source_locator.FindClosestPoint(original_point)
        ray_direction = normal_array.GetTuple(closest_source_id)

        forward_end = [
            original_point[dim] + ray_direction[dim] * ray_length
            for dim in range(3)
        ]
        intersection_ids = vtk.vtkIdList()
        intersection_points = vtk.vtkPoints()
        obb_tree.IntersectWithLine(
            original_point,
            forward_end,
            intersection_points,
            intersection_ids,
        )

        if intersection_points.GetNumberOfPoints() > 0:
            projected_points.InsertNextPoint(
                intersection_points.GetPoint(intersection_points.GetNumberOfPoints() - 1)
            )
            projection_status.append("forward")
            continue

        reverse_end = [
            original_point[dim] - ray_direction[dim] * ray_length
            for dim in range(3)
        ]
        intersection_points.Reset()
        intersection_ids.Reset()
        obb_tree.IntersectWithLine(
            original_point,
            reverse_end,
            intersection_points,
            intersection_ids,
        )

        if intersection_points.GetNumberOfPoints() > 0:
            projected_points.InsertNextPoint(intersection_points.GetPoint(0))
            projection_status.append("reverse")
            continue

        if use_closest_point_fallback:
            closest_target_id = target_locator.FindClosestPoint(original_point)
            projected_points.InsertNextPoint(target_polydata.GetPoint(closest_target_id))
            projection_status.append("closest")
        else:
            projected_points.InsertNextPoint(original_point)
            projection_status.append("failed")

    print(
        "[ProjectCurve] projected "
        f"{projected_points.GetNumberOfPoints()} control points "
        f"(forward={projection_status.count('forward')}, "
        f"reverse={projection_status.count('reverse')}, "
        f"closest={projection_status.count('closest')}, "
        f"failed={projection_status.count('failed')})",
        flush=True,
    )
    return projected_points, projection_status


def source_curve_is_closed(source_curve_node):
    return source_curve_node.IsA("vtkMRMLMarkupsClosedCurveNode")


def copy_curve_display(source_curve_node, output_curve_node):
    source_display = source_curve_node.GetDisplayNode()
    output_display = output_curve_node.GetDisplayNode()
    if source_display is None or output_display is None:
        return

    output_display.SetColor(*source_display.GetColor())
    output_display.SetSelectedColor(*source_display.GetSelectedColor())
    output_display.SetGlyphScale(source_display.GetGlyphScale())
    output_display.SetLineThickness(source_display.GetLineThickness())
    output_display.SetTextScale(source_display.GetTextScale())


def constrain_curve_to_model(
    curve_node,
    target_model,
    use_shortest_distance_on_surface=True,
    maximum_search_radius_tolerance=0.25,
):
    if hasattr(curve_node, "SetAndObserveSurfaceConstraintNode"):
        curve_node.SetAndObserveSurfaceConstraintNode(target_model)
    else:
        curve_node.SetAndObserveShortestDistanceSurfaceNode(target_model)

    if hasattr(curve_node, "SetSurfaceConstraintMaximumSearchRadiusTolerance"):
        curve_node.SetSurfaceConstraintMaximumSearchRadiusTolerance(
            float(maximum_search_radius_tolerance)
        )

    if use_shortest_distance_on_surface:
        curve_node.SetCurveTypeToShortestDistanceOnSurface(target_model)


def create_projected_curve_node(
    source_curve_node,
    target_model,
    projected_points,
    point_labels,
    output_curve_name,
    closed=None,
    use_shortest_distance_on_surface=True,
    surface_constraint_maximum_search_radius=0.25,
    locked=False,
    copy_display=True,
):
    if closed is None:
        closed = source_curve_is_closed(source_curve_node)

    curve_class = "vtkMRMLMarkupsClosedCurveNode" if closed else "vtkMRMLMarkupsCurveNode"
    remove_existing_node(output_curve_name)
    output_curve_node = slicer.mrmlScene.AddNewNodeByClass(curve_class, output_curve_name)

    for point_index in range(projected_points.GetNumberOfPoints()):
        point = projected_points.GetPoint(point_index)
        label = point_labels[point_index] if point_index < len(point_labels) else str(point_index)
        output_curve_node.AddControlPointWorld(vtk.vtkVector3d(*point), label)

    constrain_curve_to_model(
        curve_node=output_curve_node,
        target_model=target_model,
        use_shortest_distance_on_surface=use_shortest_distance_on_surface,
        maximum_search_radius_tolerance=surface_constraint_maximum_search_radius,
    )

    if copy_display:
        copy_curve_display(source_curve_node, output_curve_node)

    output_curve_node.SetLocked(bool(locked))
    output_curve_node.Modified()
    return output_curve_node


def project_curve_between_models(
    source_curve_name,
    source_model_name,
    target_model_name,
    output_curve_name=None,
    max_projection_factor=0.005,
    ray_length_mm=None,
    use_closest_point_fallback=True,
    closed=None,
    use_shortest_distance_on_surface=True,
    surface_constraint_maximum_search_radius=0.25,
    locked=False,
):
    source_curve_node = get_node(source_curve_name)
    source_model = get_node(source_model_name)
    target_model = get_node(target_model_name)

    if not source_curve_node.IsA("vtkMRMLMarkupsCurveNode"):
        raise RuntimeError(
            f"Node '{source_curve_node.GetName()}' is not a markups curve node"
        )

    source_polydata = model_polydata_in_world(source_model)
    target_polydata = model_polydata_in_world(target_model)
    original_points, point_labels = get_curve_control_points_world(source_curve_node)

    if ray_length_mm is None:
        ray_length_mm = target_polydata.GetLength() * float(max_projection_factor)
    print(f"[ProjectCurve] ray length: {ray_length_mm}", flush=True)

    projected_points, _ = project_points_polydata(
        source_polydata,
        target_polydata,
        original_points,
        ray_length=float(ray_length_mm),
        use_closest_point_fallback=use_closest_point_fallback,
    )

    if output_curve_name is None:
        output_curve_name = f"{source_curve_node.GetName()}_projected_to_{target_model.GetName()}"

    output_curve_node = create_projected_curve_node(
        source_curve_node=source_curve_node,
        target_model=target_model,
        projected_points=projected_points,
        point_labels=point_labels,
        output_curve_name=output_curve_name,
        closed=closed,
        use_shortest_distance_on_surface=use_shortest_distance_on_surface,
        surface_constraint_maximum_search_radius=surface_constraint_maximum_search_radius,
        locked=locked,
    )

    print(
        f"[ProjectCurve] Created '{output_curve_node.GetName()}' constrained to "
        f"'{target_model.GetName()}'.",
        flush=True,
    )
    return output_curve_node


# Convenience default for interactive use. Edit these names, then uncomment:
# projected_curve = project_curve_between_models(
#     source_curve_name="RoofAttachCurve",
#     source_model_name="1224_tissue_surface_from_tet",
#     target_model_name="1224_skull_remesh",
#     output_curve_name="RoofAttachCurve_projected_to_orbit",
# )
