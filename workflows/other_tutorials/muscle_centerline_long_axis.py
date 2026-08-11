r"""Extract a muscle centerline in 3D Slicer using long-axis cross sections.

Run this file from Slicer's Python console (``exec(open(path).read())``), then
call :func:`extract_centerline_along_long_axis`.  The script uses only modules
that ship with Slicer.

exec(open(
    r"C:\Users\chi.zhang\Documents\chi_vs_workspace\others\muscle_centerline_long_axis.py"
).read())

result = extract_centerline_along_long_axis(
    slicer.util.getNode("Segmentation_2"),
    "inferior_rectus_left_fx",
    slicer.util.getNode("1224_iso"),
    output_name="1224_left_fx",
    number_of_points=20,
    long_axis_direction_ras=(0, -1, 0),
)

slicer.util.saveNode(
    result["curve"],
    r"C:\Users\chi.zhang\Documents\output_muscle_test\1224_right.mrk.json",
)

The output curve contains a fixed number of control points, so its saved
``.mrk.json`` file can be consumed by ``test_muscle_conform.ipynb``.
"""

import numpy as np
import vtk
import slicer


def _segment_id(segmentation_node, segment_name_or_id):
    """Return a segment ID, accepting either an ID or an exact segment name."""
    segmentation = segmentation_node.GetSegmentation()
    if segmentation.GetSegment(segment_name_or_id):
        return segment_name_or_id
    segment_id = segmentation.GetSegmentIdBySegmentName(segment_name_or_id)
    if not segment_id:
        raise ValueError("Segment not found: {!r}".format(segment_name_or_id))
    return segment_id


def _oriented_bounding_box(segmentation_node, segment_id):
    """Get OBB center, diameters, and axis directions in world RAS."""
    import SegmentStatistics

    logic = SegmentStatistics.SegmentStatisticsLogic()
    parameter_node = logic.getParameterNode()
    parameter_node.SetParameter("Segmentation", segmentation_node.GetID())
    keys = (
        "obb_origin_ras",
        "obb_diameter_mm",
        "obb_direction_ras_x",
        "obb_direction_ras_y",
        "obb_direction_ras_z",
    )
    for key in keys:
        parameter_node.SetParameter(
            "LabelmapSegmentStatisticsPlugin.{}.enabled".format(key), "True"
        )
    logic.computeStatistics()
    stats = logic.getStatistics()

    prefix = "LabelmapSegmentStatisticsPlugin."
    origin = np.asarray(stats[segment_id, prefix + "obb_origin_ras"], dtype=float)
    diameters = np.asarray(
        stats[segment_id, prefix + "obb_diameter_mm"], dtype=float
    )
    directions = np.column_stack(
        [
            np.asarray(
                stats[segment_id, prefix + "obb_direction_ras_" + axis],
                dtype=float,
            )
            for axis in "xyz"
        ]
    )
    center = origin + directions @ (0.5 * diameters)
    return center, diameters, directions


def _long_axis_geometry(
    center_ras,
    diameters_mm,
    directions_ras,
    spacing_mm,
    padding_mm,
    long_axis_direction_ras,
):
    """Create a right-handed IJK basis with K along the longest OBB axis."""
    order = np.argsort(diameters_mm)
    x_index, y_index, z_index = order
    x_axis = directions_ras[:, x_index].copy()
    z_axis = directions_ras[:, z_index].copy()

    # Eigenvector/OBB signs are arbitrary.  A hint makes point order consistent
    # across specimens (for example, (0, 1, 0) requests posterior-to-anterior
    # ordering in Slicer's RAS coordinate system).
    if long_axis_direction_ras is not None:
        hint = np.asarray(long_axis_direction_ras, dtype=float)
        if np.linalg.norm(hint) == 0:
            raise ValueError("long_axis_direction_ras must be non-zero")
        if np.dot(z_axis, hint) < 0:
            z_axis *= -1.0
    else:
        # Deterministic fallback: make the largest R/A/S component positive.
        if z_axis[np.argmax(np.abs(z_axis))] < 0:
            z_axis *= -1.0

    # Rebuild the middle axis to guarantee an orthonormal, right-handed basis.
    x_axis /= np.linalg.norm(x_axis)
    z_axis /= np.linalg.norm(z_axis)
    y_axis = np.cross(z_axis, x_axis)
    y_axis /= np.linalg.norm(y_axis)
    x_axis = np.cross(y_axis, z_axis)

    dimensions_mm = np.asarray(
        [diameters_mm[x_index], diameters_mm[y_index], diameters_mm[z_index]]
    )
    shape_ijk = np.ceil((dimensions_mm + 2.0 * padding_mm) / spacing_mm).astype(int) + 1
    shape_ijk = np.maximum(shape_ijk, 2)
    basis = np.column_stack((x_axis, y_axis, z_axis))
    origin_ras = center_ras - basis @ (0.5 * (shape_ijk - 1) * spacing_mm)
    return basis, origin_ras, shape_ijk


def _make_reference_volume(name, basis, origin_ras, shape_ijk, spacing_mm):
    reference = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLScalarVolumeNode", name
    )
    image = vtk.vtkImageData()
    image.SetDimensions(*(int(value) for value in shape_ijk))
    image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
    image.GetPointData().GetScalars().Fill(0)
    reference.SetAndObserveImageData(image)

    ijk_to_ras = np.eye(4)
    ijk_to_ras[:3, :3] = basis * spacing_mm
    ijk_to_ras[:3, 3] = origin_ras
    reference.SetIJKToRASMatrix(slicer.util.vtkMatrixFromArray(ijk_to_ras))
    return reference


def _slice_centroids_ras(mask_node):
    """Compute one area-weighted binary-mask centroid per nonempty K slice."""
    mask_kji = slicer.util.arrayFromVolume(mask_node)
    ijk_to_ras_matrix = vtk.vtkMatrix4x4()
    mask_node.GetIJKToRASMatrix(ijk_to_ras_matrix)
    ijk_to_ras = slicer.util.arrayFromVTKMatrix(ijk_to_ras_matrix)
    spacing = mask_node.GetSpacing()
    points = []
    areas = []
    slice_indices = []

    for k, section_ji in enumerate(mask_kji):
        j, i = np.nonzero(section_ji)
        if i.size == 0:
            continue
        point_ijk = np.array([i.mean(), j.mean(), float(k), 1.0])
        points.append((ijk_to_ras @ point_ijk)[:3])
        areas.append(float(i.size) * spacing[0] * spacing[1])
        slice_indices.append(k)

    if len(points) < 2:
        raise ValueError("The exported segment occupies fewer than two cross sections")

    return np.asarray(points), np.asarray(areas), np.asarray(slice_indices)


def _smooth_points(points, smoothing_window):
    """Apply an endpoint-preserving moving average to an Nx3 point array."""
    smoothing_window = int(smoothing_window)
    if smoothing_window > 1:
        if smoothing_window % 2 == 0:
            raise ValueError("smoothing_window must be odd")
        radius = smoothing_window // 2
        padded = np.pad(points, ((radius, radius), (0, 0)), mode="edge")
        kernel = np.ones(smoothing_window, dtype=float) / smoothing_window
        points = np.column_stack(
            [np.convolve(padded[:, axis], kernel, mode="valid") for axis in range(3)]
        )
    return points


def _resample_polyline(points, number_of_points):
    """Resample points at equal arc-length intervals (NumPy-only)."""
    number_of_points = int(number_of_points)
    if number_of_points < 2:
        raise ValueError("number_of_points must be at least 2")
    distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
    cumulative = np.concatenate(([0.0], np.cumsum(distances)))
    keep = np.concatenate(([True], np.diff(cumulative) > 1e-8))
    points = points[keep]
    cumulative = cumulative[keep]
    if cumulative[-1] <= 0:
        raise ValueError("Centerline has zero length")
    samples = np.linspace(0.0, cumulative[-1], number_of_points)
    return np.column_stack(
        [np.interp(samples, cumulative, points[:, axis]) for axis in range(3)]
    )


def _make_curve(name, points_ras):
    curve = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode", name)
    for point in points_ras:
        point_index = curve.AddControlPointWorld(vtk.vtkVector3d(*point))
        # SetAllControlPointsVisibility is unavailable in some Slicer versions.
        curve.SetNthControlPointVisibility(point_index, True)
    return curve


def _make_cross_section_table(name, points_ras, areas_mm2, slice_indices):
    table_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", name)
    columns = (
        ("Slice K", slice_indices, vtk.vtkIntArray),
        ("R (mm)", points_ras[:, 0], vtk.vtkDoubleArray),
        ("A (mm)", points_ras[:, 1], vtk.vtkDoubleArray),
        ("S (mm)", points_ras[:, 2], vtk.vtkDoubleArray),
        ("Area (mm2)", areas_mm2, vtk.vtkDoubleArray),
    )
    for column_name, values, array_type in columns:
        column = array_type()
        column.SetName(column_name)
        for value in values:
            column.InsertNextValue(value)
        table_node.AddColumn(column)
    return table_node


def extract_centerline_along_long_axis(
    segmentation_node,
    segment_name_or_id,
    reference_volume_node,
    output_name=None,
    number_of_points=20,
    spacing_mm=None,
    padding_mm=2.0,
    smoothing_window=5,
    long_axis_direction_ras=None,
):
    """Extract a fixed-length centerline and an aligned cross-section mask.

    Parameters
    ----------
    segmentation_node : vtkMRMLSegmentationNode
        Segmentation containing the muscle.
    segment_name_or_id : str
        Exact segment name or segment ID (avoids fragile numeric indices).
    reference_volume_node : vtkMRMLScalarVolumeNode
        Source image that defines a sensible sampling resolution.
    output_name : str, optional
        Prefix for created nodes.  Defaults to the segment name.
    number_of_points : int
        Number of curve control points; 20 matches the existing notebook.
    spacing_mm : float, optional
        Isotropic output spacing. Defaults to the smallest source voxel spacing.
    padding_mm : float
        Padding around the oriented bounding box.
    smoothing_window : int
        Odd moving-average window over raw slice centroids; use 1 to disable.
    long_axis_direction_ras : sequence of 3 floats, optional
        Desired direction from first to last point. In RAS, +Y is anterior.

    Returns
    -------
    dict
        ``curve`` (fixed point count), ``rawCurve``, ``alignedMask``, ``table``,
        and the long-axis ``basis`` (columns are cross-section X, Y, long axis).
    """
    if not segmentation_node or not reference_volume_node:
        raise ValueError("A segmentation node and reference volume node are required")
    segment_id = _segment_id(segmentation_node, segment_name_or_id)
    segment = segmentation_node.GetSegmentation().GetSegment(segment_id)
    output_name = output_name or segment.GetName()
    if spacing_mm is None:
        spacing_mm = min(reference_volume_node.GetSpacing())
    spacing_mm = float(spacing_mm)
    if spacing_mm <= 0:
        raise ValueError("spacing_mm must be positive")

    center, diameters, directions = _oriented_bounding_box(
        segmentation_node, segment_id
    )
    basis, origin, shape = _long_axis_geometry(
        center,
        diameters,
        directions,
        spacing_mm,
        float(padding_mm),
        long_axis_direction_ras,
    )
    reference = _make_reference_volume(
        output_name + " Centerline Reference", basis, origin, shape, spacing_mm
    )
    aligned_mask = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLLabelMapVolumeNode", output_name + " Aligned Mask"
    )
    segment_ids = vtk.vtkStringArray()
    segment_ids.InsertNextValue(segment_id)
    try:
        success = slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsToLabelmapNode(
            segmentation_node, segment_ids, aligned_mask, reference
        )
    finally:
        slicer.mrmlScene.RemoveNode(reference)
    if not success:
        slicer.mrmlScene.RemoveNode(aligned_mask)
        raise RuntimeError("Could not export the segment to the long-axis geometry")

    raw_points, areas, slice_indices = _slice_centroids_ras(aligned_mask)
    smoothed_points = _smooth_points(raw_points, smoothing_window)
    sampled_points = _resample_polyline(smoothed_points, number_of_points)
    raw_curve = _make_curve(output_name + " Raw Centerline", raw_points)
    curve = _make_curve(output_name + " Centerline", sampled_points)
    table = _make_cross_section_table(
        output_name + " Cross Sections", raw_points, areas, slice_indices
    )
    aligned_mask.CreateDefaultDisplayNodes()

    return {
        "curve": curve,
        "rawCurve": raw_curve,
        "alignedMask": aligned_mask,
        "table": table,
        "basis": basis,
        "obbDiametersMm": diameters,
    }


# Example (run after loading this file in Slicer's Python console):
# result = extract_centerline_along_long_axis(
#     slicer.util.getNode("totalSeg"),
#     "Exact muscle segment name",
#     slicer.util.getNode("iso_vol"),
#     output_name="specimen_right",
#     number_of_points=20,
#     long_axis_direction_ras=(0, 1, 0),  # first point posterior, last anterior
# )
# slicer.util.saveNode(result["curve"], r"C:\path\specimen_right.mrk.json")
