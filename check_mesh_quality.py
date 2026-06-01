import math
import os

import gmsh


ROOT_DIR = "/home/zhang/Documents/mesh_select/1224"
ORIGINAL_TET_CANDIDATES = (
    os.path.join(ROOT_DIR, "1224_remesh", "1224_tissue_remesh_1_6k.msh"),
    os.path.join(ROOT_DIR, "1224_tissue_remesh_1_6k.msh"),
)
STAGE3_TET_PATH = os.path.join(ROOT_DIR, "retraction_stages", "stage3_deformed_tissue_tet.vtk")
NEAR_ZERO_VOLUME = 1.0e-8
VOLUME_RATIO_THRESHOLDS = (0.05, 0.1, 0.2, 2.0, 5.0, 10.0)


def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def signed_tet_volume(p0, p1, p2, p3):
    return dot(subtract(p1, p0), cross(subtract(p2, p0), subtract(p3, p0))) / 6.0


def first_existing_path(paths):
    for path in paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("None of these paths exist:\n" + "\n".join(paths))


def summarize_values(name, values):
    if not values:
        print(f"{name}: none")
        return

    sorted_values = sorted(values)
    n = len(sorted_values)

    def percentile(percent):
        if n == 1:
            return sorted_values[0]
        index = (n - 1) * percent / 100.0
        lo = math.floor(index)
        hi = math.ceil(index)
        if lo == hi:
            return sorted_values[int(index)]
        weight = index - lo
        return sorted_values[lo] * (1.0 - weight) + sorted_values[hi] * weight

    print(f"{name} min:", sorted_values[0])
    print(f"{name} p01:", percentile(1))
    print(f"{name} p05:", percentile(5))
    print(f"{name} mean:", sum(sorted_values) / n)
    print(f"{name} p95:", percentile(95))
    print(f"{name} p99:", percentile(99))
    print(f"{name} max:", sorted_values[-1])


def load_tet_mesh(path):
    gmsh.clear()
    gmsh.merge(path)

    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    coord_by_tag = {
        int(tag): tuple(coords[3 * i:3 * i + 3])
        for i, tag in enumerate(node_tags)
    }

    dim_counts = {}
    for dim in (0, 1, 2, 3):
        _, element_tags, _ = gmsh.model.mesh.getElements(dim)
        dim_counts[dim] = sum(len(tags) for tags in element_tags)

    element_types, element_tags, element_node_tags = gmsh.model.mesh.getElements(3)
    tet_tags = []
    tets = []
    edge_lengths = []
    signed_volumes = []

    for etype, tags, conn in zip(element_types, element_tags, element_node_tags):
        if etype != 4:
            continue

        for element_index, tag in enumerate(tags):
            offset = 4 * element_index
            tet_nodes = [int(node_tag) for node_tag in conn[offset:offset + 4]]
            points = [coord_by_tag[node_tag] for node_tag in tet_nodes]
            tet_tags.append(int(tag))
            tets.append(tet_nodes)

            for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
                edge_lengths.append(distance(points[a], points[b]))
            signed_volumes.append(signed_tet_volume(*points))

    qualities = gmsh.model.mesh.getElementQualities(tet_tags) if tet_tags else []
    return {
        "path": path,
        "node_count": len(node_tags),
        "dim_counts": dim_counts,
        "tet_tags": tet_tags,
        "tets": tets,
        "edge_lengths": edge_lengths,
        "qualities": list(qualities),
        "signed_volumes": signed_volumes,
    }


def print_mesh_report(mesh):
    signed_volumes = mesh["signed_volumes"]
    abs_volumes = [abs(volume) for volume in signed_volumes]
    qualities = mesh["qualities"]

    print("\n===", mesh["path"], "===")
    print("nodes:", mesh["node_count"])
    for dim in (0, 1, 2, 3):
        print(f"{dim}D elements:", mesh["dim_counts"][dim])
    print("tetrahedra:", len(mesh["tets"]))

    summarize_values("edge length", mesh["edge_lengths"])
    summarize_values("quality", qualities)
    if qualities:
        print("quality < 0.1:", sum(q < 0.1 for q in qualities))
        print("quality < 0.2:", sum(q < 0.2 for q in qualities))

    summarize_values("signed volume", signed_volumes)
    summarize_values("absolute volume", abs_volumes)
    print("negative signed volumes:", sum(volume < 0.0 for volume in signed_volumes))
    print("near-zero abs volumes:", sum(volume < NEAR_ZERO_VOLUME for volume in abs_volumes))
    print("total signed volume:", sum(signed_volumes))
    print("total absolute volume:", sum(abs_volumes))


def print_comparison(original, deformed):
    print("\n=== Original vs deformed comparison ===")
    if len(original["tets"]) != len(deformed["tets"]):
        print("Cannot compare per-tet volume ratios: tet counts differ.")
        print("original tetrahedra:", len(original["tets"]))
        print("deformed tetrahedra:", len(deformed["tets"]))
        return

    matching_connectivity = sum(
        original_tet == deformed_tet
        for original_tet, deformed_tet in zip(original["tets"], deformed["tets"])
    )
    print("matching connectivity entries:", matching_connectivity, "/", len(original["tets"]))
    if matching_connectivity != len(original["tets"]):
        print("WARNING: connectivity order differs; per-tet ratios assume original/deformed tets are still aligned by element order.")

    original_volumes = original["signed_volumes"]
    deformed_volumes = deformed["signed_volumes"]
    abs_ratios = []
    signed_ratios = []
    sign_flips = 0
    skipped_zero_original = 0

    for original_volume, deformed_volume in zip(original_volumes, deformed_volumes):
        if abs(original_volume) < NEAR_ZERO_VOLUME:
            skipped_zero_original += 1
            continue

        abs_ratios.append(abs(deformed_volume) / abs(original_volume))
        signed_ratios.append(deformed_volume / original_volume)
        if original_volume * deformed_volume < 0.0:
            sign_flips += 1

    summarize_values("abs volume ratio deformed/original", abs_ratios)
    summarize_values("signed volume ratio deformed/original", signed_ratios)
    print("sign flips:", sign_flips)
    print("skipped near-zero original volumes:", skipped_zero_original)
    for threshold in VOLUME_RATIO_THRESHOLDS:
        if threshold < 1.0:
            print(
                f"abs volume ratio < {threshold}:",
                sum(ratio < threshold for ratio in abs_ratios),
            )
        else:
            print(
                f"abs volume ratio > {threshold}:",
                sum(ratio > threshold for ratio in abs_ratios),
            )


def main():
    gmsh.initialize()
    try:
        original = load_tet_mesh(first_existing_path(ORIGINAL_TET_CANDIDATES))
        deformed = load_tet_mesh(STAGE3_TET_PATH)
        print_mesh_report(original)
        print_mesh_report(deformed)
        print_comparison(original, deformed)
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    main()
