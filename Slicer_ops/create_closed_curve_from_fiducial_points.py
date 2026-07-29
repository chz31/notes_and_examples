"""
Create a closed curve markup from an ordered fiducial markup point list.

Run inside 3D Slicer after creating/loading a vtkMRMLMarkupsFiducialNode.

Example from the Slicer Python interactor:

exec(open("/home/chi/Documents/chi_vs_workspace/slicersofa_sofa_scratches/sofa_experiments/preprocessing/slicer_closed_curve_from_fiducials.py").read())

curve = create_closed_curve_from_fiducials(
    fiducials_name="F",
    output_curve_name="CC",
)
"""

import slicer
import vtk


def get_node(name):
    node = slicer.util.getNode(name)
    if node is None:
        raise RuntimeError(f"Could not find node '{name}'")
    return node


def get_markup_control_points_world(markups_node):
    points = []
    for point_index in range(markups_node.GetNumberOfControlPoints()):
        if hasattr(markups_node, "GetNthControlPointPositionStatus"):
            status = markups_node.GetNthControlPointPositionStatus(point_index)
            if status == markups_node.PositionUndefined:
                continue

        point = [0.0, 0.0, 0.0]
        markups_node.GetNthControlPointPositionWorld(point_index, point)
        points.append(point)

    if len(points) < 3:
        raise RuntimeError(
            f"Markup node '{markups_node.GetName()}' has {len(points)} defined "
            "control points; a closed curve needs at least 3."
        )
    return points


def remove_existing_node(name):
    existing = slicer.mrmlScene.GetFirstNodeByName(name)
    if existing is not None:
        slicer.mrmlScene.RemoveNode(existing)


def create_closed_curve_from_fiducials(
    fiducials_name,
    output_curve_name=None,
    remove_existing=True,
    copy_labels=True,
    curve_color=(0.1, 0.6, 1.0),
    selected_color=(1.0, 0.8, 0.1),
    point_size=5.0,
    line_thickness=0.4,
):
    fiducials_node = get_node(fiducials_name)
    if output_curve_name is None:
        output_curve_name = fiducials_node.GetName() + "_closed_curve"

    if remove_existing:
        remove_existing_node(output_curve_name)

    points = get_markup_control_points_world(fiducials_node)
    curve_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLMarkupsClosedCurveNode",
        output_curve_name,
    )

    for point_index, point in enumerate(points):
        label = str(point_index)
        if copy_labels and point_index < fiducials_node.GetNumberOfControlPoints():
            label = fiducials_node.GetNthControlPointLabel(point_index) or label
        curve_node.AddControlPointWorld(vtk.vtkVector3d(*point), label)

    display_node = curve_node.GetDisplayNode()
    if display_node is not None:
        display_node.SetColor(*curve_color)
        display_node.SetSelectedColor(*selected_color)
        display_node.SetGlyphScale(point_size)
        display_node.SetLineThickness(line_thickness)

    print(
        f"[ClosedCurve] Created '{curve_node.GetName()}' from "
        f"{len(points)} points in '{fiducials_node.GetName()}'."
    )
    return curve_node


# Convenience default for interactive use. Edit these names, then uncomment:
# curve = create_closed_curve_from_fiducials(
#     fiducials_name="F",
#     output_curve_name="CC",
# )
