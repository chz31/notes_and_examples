# SOFA Force Indices vs MechanicalObject Global Indices
1. Two index spaces always exist in SOFA
(A) MechanicalObject global indices (DOFs)

Defined by the MechanicalObject

One index per node (for Vec3d, one node = 3 DOFs)

Example:

```
global node indices = [0, 1, 2, ..., N-1]
```

These indices index:

- positions (N, 3)
- velocities (N, 3)
- internal FEM forces
- mass contributions

In most FEM meshes:

mesh points ≈ mechanical nodes (1:1)

(B) ForceField local indices

Each ForceField defines its own index list:
```
indices = [i0, i1, i2, ...]  # global node indices
```

Internally, the force field stores forces only for these nodes:

```
local index 0 → global node i0
local index 1 → global node i1
local index 2 → global node i2
```

This mapping is critical.

2. Shape and meaning of forces

For a ConstantForceField:

```
ConstantForceField(indices=indices, forces=...)
```

SOFA allocates:

```
forces.shape == (len(indices), 3)


forces[k] = force vector applied to global node indices[k]
```

The 3 corresponds to (Fx, Fy, Fz)

**Important:**

forces is not indexed by global node ID
it is indexed by the force field’s local index

3. Global vs local indexing (the core rule)
What you want	Correct indexing
- Force on node indices[k]	forces[k]
- Force on global node i	find k such that indices[k] == i
- Force on all nodes	forces[:] = forceVec

🚫 Never do:
```
forces[globalNodeID]
```
unless indices == [0,1,2,...,N-1].

4. Why “all nodes” is a special case

If you do:
```
indices = np.arange(N)
```

Then:
```
len(indices) == N

local index == global index
```
So this works by coincidence:
```
forces[globalID] = ...
```

This is why prostate.py does not crash.

⚠️ The moment you switch to an ROI or subset, this breaks.


5. Recommended safe patterns
Apply same force to all selected nodes
```
forces[:] = forceVec
```

Apply per-node forces for selected nodes
```
for k in range(len(indices)):
    forces[k] = forceVec
```
ROI-based force (safe)
```
indices = roiIndices
forces = np.zeros((len(indices), 3))
forces[:] = forceVec
```

6. External vs internal forces

External forces

- ConstantForceField
- gravity
- collision response

Internal forces

- FEM (TetrahedronFEMForceField)
- springs
- constraints

External forces act only on selected nodes;
internal forces propagate deformation through topology.

7. Key mental model
```
ForceField
├── indices = [i0, i1, i2]
└── forces  = [f0, f1, f2]

SOFA assembly:
globalForce[i0] += f0
globalForce[i1] += f1
globalForce[i2] += f2
```

8. Rule to remember forever

A ForceField never sees the full mesh.
It only knows the nodes listed in its indices.

Everything else follows from this.
