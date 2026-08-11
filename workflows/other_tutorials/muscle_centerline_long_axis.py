r"""Extract a muscle centerline in 3D Slicer using long-axis cross sections.

Run this file from Slicer's Python console (``exec(open(path).read())``), then
call :func:`extract_centerline_along_long_axis`.  The script uses only modules
that ship with Slicer.

exec(open(
    r"C:\Users\chi.zhang\Documents\chi_vs_workspace\others\muscle_centerline_long_axis.py"
).read())

result = extract_centerline_along_long_axis(
    slicer.util.getNode("nn_inferior_rectus"),
    "inferior_rectus_right_fx",
    slicer.util.getNode("1570_iso"),
    output_name="1570_right_fx",
    number_of_points=20,
    long_axis_direction_ras=(0, -1, 0),
)

slicer.util.saveNode(
    result["curve"],
    r"C:\Users\chi.zhang\Documents\output_muscle_test\1224_right.mrk.json",
)

The output curve contains a fixed number of control points, so its saved
``.mrk.json`` file can be consumed by ``test_muscle_conform.ipynb``.

Method provenance
-----------------
The principal-axis alignment, oriented resampling, and slice-by-slice
cross-sectional analysis were adapted from the SlicerBiomech SegmentGeometry
workflow. Cross-sectional area, centroid, percent length, and the circularity
definition (4*pi*area/perimeter^2) correspond to metrics provided by that
module. This script independently implements perimeter using VTK marching
squares and implements per-section equivalent-ellipse axes/aspect ratio from
the 2D covariance eigenvalues; these algorithms are not copied from
SegmentGeometry's perimeter or Feret-diameter implementations.

If this workflow is used in a publication, cite:
Huie JM, Summers AP, Kawano SM. (2022). SegmentGeometry: a tool for measuring
second moment of area in 3D Slicer. Integrative Organismal Biology 4(1).
https://doi.org/10.1093/iob/obac009
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


def _section_perimeter_mm(section_ji, spacing_i, spacing_j):
    """Measure all 2D contour lengths with marching squares in millimeters."""
    from vtk.util.numpy_support import numpy_to_vtk

    # Padding closes contours that touch an image boundary.
    padded = np.pad((section_ji > 0).astype(np.uint8), 1)
    image = vtk.vtkImageData()
    image.SetDimensions(padded.shape[1], padded.shape[0], 1)
    image.SetSpacing(float(spacing_i), float(spacing_j), 1.0)
    scalars = numpy_to_vtk(
        padded.ravel(order="C"), deep=True, array_type=vtk.VTK_UNSIGNED_CHAR
    )
    image.GetPointData().SetScalars(scalars)

    contours = vtk.vtkMarchingSquares()
    contours.SetInputData(image)
    contours.SetValue(0, 0.5)
    contours.Update()
    contour_polydata = contours.GetOutput()

    perimeter_mm = 0.0
    point_ids = vtk.vtkIdList()
    lines = contour_polydata.GetLines()
    lines.InitTraversal()
    while lines.GetNextCell(point_ids):
        for point_index in range(1, point_ids.GetNumberOfIds()):
            p0 = np.asarray(
                contour_polydata.GetPoint(point_ids.GetId(point_index - 1))
            )
            p1 = np.asarray(contour_polydata.GetPoint(point_ids.GetId(point_index)))
            perimeter_mm += np.linalg.norm(p1 - p0)
    return perimeter_mm


def _section_principal_axes_mm(i, j, spacing_i, spacing_j):
    """Return equivalent-ellipse major/minor diameters from 2D moments."""
    coordinates_mm = np.column_stack((i * spacing_i, j * spacing_j))
    centered = coordinates_mm - coordinates_mm.mean(axis=0)
    covariance = centered.T @ centered / len(coordinates_mm)

    # Each voxel represents a rectangular area, not a dimensionless point.
    covariance += np.diag([spacing_i**2 / 12.0, spacing_j**2 / 12.0])
    eigenvalues = np.maximum(np.linalg.eigvalsh(covariance), 0.0)
    minor_axis_mm, major_axis_mm = 4.0 * np.sqrt(eigenvalues)
    aspect_ratio = (
        major_axis_mm / minor_axis_mm if minor_axis_mm > 1e-12 else np.nan
    )
    return major_axis_mm, minor_axis_mm, aspect_ratio


def _cross_section_metrics(mask_node):
    """Compute centroid and shape metrics for every nonempty K slice."""
    mask_kji = slicer.util.arrayFromVolume(mask_node)
    ijk_to_ras_matrix = vtk.vtkMatrix4x4()
    mask_node.GetIJKToRASMatrix(ijk_to_ras_matrix)
    ijk_to_ras = slicer.util.arrayFromVTKMatrix(ijk_to_ras_matrix)
    spacing = mask_node.GetSpacing()
    metrics = {
        "pointsRas": [],
        "areaMm2": [],
        "perimeterMm": [],
        "circularity": [],
        "majorAxisMm": [],
        "minorAxisMm": [],
        "aspectRatio": [],
        "sliceIndex": [],
    }

    for k, section_ji in enumerate(mask_kji):
        j, i = np.nonzero(section_ji)
        if i.size == 0:
            continue
        point_ijk = np.array([i.mean(), j.mean(), float(k), 1.0])
        area_mm2 = float(i.size) * spacing[0] * spacing[1]
        perimeter_mm = _section_perimeter_mm(section_ji, spacing[0], spacing[1])
        circularity = (
            4.0 * np.pi * area_mm2 / perimeter_mm**2
            if perimeter_mm > 0
            else np.nan
        )
        # Small digital sections can produce values slightly above the
        # continuous-shape limit because area and contour are discretized.
        circularity = min(circularity, 1.0)
        major_axis_mm, minor_axis_mm, aspect_ratio = _section_principal_axes_mm(
            i, j, spacing[0], spacing[1]
        )

        metrics["pointsRas"].append((ijk_to_ras @ point_ijk)[:3])
        metrics["areaMm2"].append(area_mm2)
        metrics["perimeterMm"].append(perimeter_mm)
        metrics["circularity"].append(circularity)
        metrics["majorAxisMm"].append(major_axis_mm)
        metrics["minorAxisMm"].append(minor_axis_mm)
        metrics["aspectRatio"].append(aspect_ratio)
        metrics["sliceIndex"].append(k)

    if len(metrics["pointsRas"]) < 2:
        raise ValueError("The exported segment occupies fewer than two cross sections")

    for key, values in metrics.items():
        metrics[key] = np.asarray(values)
    first_slice = metrics["sliceIndex"][0]
    slice_range = metrics["sliceIndex"][-1] - first_slice
    metrics["percentLength"] = (
        100.0 * (metrics["sliceIndex"] - first_slice) / slice_range
    )
    return metrics


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


def _make_cross_section_table(name, metrics):
    table_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", name)
    columns = (
        ("Slice K", metrics["sliceIndex"], vtk.vtkIntArray),
        ("Percent length", metrics["percentLength"], vtk.vtkDoubleArray),
        ("R (mm)", metrics["pointsRas"][:, 0], vtk.vtkDoubleArray),
        ("A (mm)", metrics["pointsRas"][:, 1], vtk.vtkDoubleArray),
        ("S (mm)", metrics["pointsRas"][:, 2], vtk.vtkDoubleArray),
        ("Area (mm2)", metrics["areaMm2"], vtk.vtkDoubleArray),
        ("Perimeter (mm)", metrics["perimeterMm"], vtk.vtkDoubleArray),
        ("Circularity", metrics["circularity"], vtk.vtkDoubleArray),
        ("Major axis (mm)", metrics["majorAxisMm"], vtk.vtkDoubleArray),
        ("Minor axis (mm)", metrics["minorAxisMm"], vtk.vtkDoubleArray),
        ("Aspect ratio", metrics["aspectRatio"], vtk.vtkDoubleArray),
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
        NumPy-array ``crossSectionMetrics``, and the long-axis ``basis``
        (columns are cross-section X, Y, long axis). Aspect ratio is the major
        divided by minor equivalent-ellipse axis; circularity is 4*pi*A/P^2.
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

    cross_section_metrics = _cross_section_metrics(aligned_mask)
    raw_points = cross_section_metrics["pointsRas"]
    smoothed_points = _smooth_points(raw_points, smoothing_window)
    sampled_points = _resample_polyline(smoothed_points, number_of_points)
    raw_curve = _make_curve(output_name + " Raw Centerline", raw_points)
    curve = _make_curve(output_name + " Centerline", sampled_points)
    table = _make_cross_section_table(
        output_name + " Cross Sections", cross_section_metrics
    )
    aligned_mask.CreateDefaultDisplayNodes()

    return {
        "curve": curve,
        "rawCurve": raw_curve,
        "alignedMask": aligned_mask,
        "table": table,
        "crossSectionMetrics": cross_section_metrics,
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
