import gmsh
import math
import os
import sys

gmsh.initialize()

gmsh.clear()
path = "/home/zhang/Documents/mesh_select/1224/1224_remesh"
gmsh.merge(os.path.join(path, '1224_tissue_remesh_1_6k.stl'))


angle = 40
forceParametrizablePatches = 1
includeBoundary = True
curveAngle = 180
gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary,
                                    forceParametrizablePatches,
                                    curveAngle * math.pi / 180.)



# gmsh.model.mesh.createGeometry()

s = gmsh.model.getEntities(2)

l = gmsh.model.geo.addSurfaceLoop([e[1] for e in s])

gmsh.model.geo.addVolume([l])

gmsh.model.geo.synchronize()


f = gmsh.model.mesh.field.add("MathEval")
gmsh.model.mesh.field.setString(f, "F", "2")
gmsh.model.mesh.field.setAsBackgroundMesh(f)


# lc = 6.0
# gmsh.option.setNumber("Mesh.MeshSizeMin", lc)
# gmsh.option.setNumber("Mesh.MeshSizeMax", lc)

# gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
# gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
# gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)



print("surfaces:", gmsh.model.getEntities(2))
print("volumes:", gmsh.model.getEntities(3))


gmsh.model.mesh.generate(3)

gmsh.model.mesh.optimize("Netgen")


def print_mesh_info():
    nodes, coords, _ = gmsh.model.mesh.getNodes()
    print("nodes:", len(nodes))

    for dim in [0, 1, 2, 3]:
        element_types, element_tags, _ = gmsh.model.mesh.getElements(dim)
        count = sum(len(tags) for tags in element_tags)
        print(f"{dim}D elements:", count)

    element_types, element_tags, element_node_tags = gmsh.model.mesh.getElements(3)

    tet_count = sum(len(tags) for tags in element_tags)
    print("tetrahedra:", tet_count)

    coord_by_tag = {}
    for i, tag in enumerate(nodes):
        coord_by_tag[tag] = coords[3 * i:3 * i + 3]

    edge_lengths = []
    for etype, conn in zip(element_types, element_node_tags):
        # 4-node tetrahedron element type is 4
        if etype != 4:
            continue

        for i in range(0, len(conn), 4):
            tet_nodes = conn[i:i + 4]
            pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

            for a, b in pairs:
                pa = coord_by_tag[tet_nodes[a]]
                pb = coord_by_tag[tet_nodes[b]]
                dx = pa[0] - pb[0]
                dy = pa[1] - pb[1]
                dz = pa[2] - pb[2]
                edge_lengths.append(math.sqrt(dx * dx + dy * dy + dz * dz))

    if edge_lengths:
        print("edge length min:", min(edge_lengths))
        print("edge length mean:", sum(edge_lengths) / len(edge_lengths))
        print("edge length max:", max(edge_lengths))

    if tet_count:
        all_tet_tags = []
        for tags in element_tags:
            all_tet_tags.extend(tags)

        qualities = gmsh.model.mesh.getElementQualities(all_tet_tags)
        print("quality min:", min(qualities))
        print("quality mean:", sum(qualities) / len(qualities))
        print("quality < 0.1:", sum(q < 0.1 for q in qualities))


print_mesh_info()


gmsh.write(os.path.join(path, '1224_tissue_remesh_1_6k.msh'))
gmsh.write(os.path.join(path, '1224_tissue_remesh_1_6k.vtk'))

# gmsh.fltk.run()

gmsh.finalize()
