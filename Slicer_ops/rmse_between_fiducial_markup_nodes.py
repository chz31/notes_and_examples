import numpy as np
import slicer

def fiducialRMSE(node1, node2, world=True, checkLabels=False):
    """
    Compute RMSE between two markups fiducial nodes in Slicer.

    Assumptions:
    - The two nodes contain corresponding points in the same order.
    - Same number of control points in both nodes.

    Parameters
    ----------
    node1, node2 : vtkMRMLMarkupsNode or str
        Either the node objects or their names in the scene.
    world : bool
        If True, use world coordinates (applies parent transforms).
        If False, use local node coordinates.
    checkLabels : bool
        If True, require matching point labels in the same order.

    Returns
    -------
    rmse : float
        Root mean square error across all point-coordinate differences.
    perPointDistances : numpy.ndarray
        Euclidean distance for each corresponding point pair.
    """

    if isinstance(node1, str):
        node1 = slicer.util.getNode(node1)
    if isinstance(node2, str):
        node2 = slicer.util.getNode(node2)

    n1 = node1.GetNumberOfControlPoints()
    n2 = node2.GetNumberOfControlPoints()

    if n1 != n2:
        raise ValueError(f"Point count mismatch: {n1} vs {n2}")

    if checkLabels:
        for i in range(n1):
            l1 = node1.GetNthControlPointLabel(i)
            l2 = node2.GetNthControlPointLabel(i)
            if l1 != l2:
                raise ValueError(f"Label mismatch at point {i}: '{l1}' vs '{l2}'")

    p1 = slicer.util.arrayFromMarkupsControlPoints(node1, world=world)
    p2 = slicer.util.arrayFromMarkupsControlPoints(node2, world=world)

    # Euclidean distance for each corresponding fiducial pair
    perPointDistances = np.linalg.norm(p1 - p2, axis=1)

    # RMSE over x,y,z coordinate errors
    rmse = np.sqrt(np.mean((p1 - p2) ** 2))

    return rmse, perPointDistances


# Example usage:
nodeA = slicer.util.getNode("stryker_small_right")
nodeB = slicer.util.getNode("stryker_small_right Copy")

rmse, distances = fiducialRMSE(nodeA, nodeB, world=True, checkLabels=False)

print(f"RMSE = {rmse:.4f} mm")
print("Per-point distances (mm):", distances)
print(f"Mean distance = {np.mean(distances):.4f} mm")
print(f"Max distance = {np.max(distances):.4f} mm")
