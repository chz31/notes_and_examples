1. Two worlds that must stay in sync
(A) MRML world (Slicer)

Scene graph: MRML nodes

User interaction:

- Markups (points, lines)
- Transforms
- GUI widgets

Data is event-driven

Examples:
- vtkMRMLModelNode
- vtkMRMLMarkupsLineNode
- vtkMRMLTransformNode

(B) SOFA world

Physics scene graph

Mechanical state evolves via time integration

Data is time-step–driven

Core objects:

- MechanicalObject
- ForceField
- Solver
- Mapping

SlicerSOFA is about bridging these two clocks.

2. Unidirectional vs bidirectional coupling
```
Prostate.py (mostly unidirectional)
MRML → SOFA   (once, at init)
SOFA → MRML   (every timestep)
```

MRML:
- Provides geometry
- Provides control inputs (needle line)

SOFA:
- Owns the mechanical state
- Drives deformation

MRML models are visualizations of SOFA state

MRML interaction does not move SOFA nodes directly

SoftTissueSimulation (bidirectional)
```
MRML → SOFA   (on interaction events)
SOFA → MRML   (every timestep)
```

Examples:

Moving a markup → changes force direction

Changing a transform → moves constraint / attachment

SOFA state → updates MRML mesh

This requires event observers.

3. What an MRML Observer is

An observer is a callback registered on a MRML node:
```
node.AddObserver(vtk.vtkCommand.ModifiedEvent, callback)
```

Meaning:

“Whenever this node changes, call this function.”

Typical triggers:

User moves a markup point

User drags a transform

GUI parameter changes

Observers are push-based, not polling-based.

4. Why observers feel invisible (but powerful)

In many Slicer templates, you see:

self.addObserver(node, vtk.vtkCommand.ModifiedEvent, self.onNodeModified)


And things “just work” — but the logic is hidden.

That’s why:

you’ve used observers before

without explicitly thinking about them

SoftTissueSimulation relies heavily on them.

5. MRML → SOFA interaction patterns (most common)
Pattern 1: Markup controls force direction (your current case)
```
vtkMRMLMarkupsLineNode
        ↓ (observer)
compute direction vector
        ↓
update SOFA ConstantForceField.forces every time step after a 10ms qt timer
```

You already implemented this ✔

Pattern 2: Transform controls constraint / attachment
```
vtkMRMLTransformNode
        ↓
observer fires
        ↓
update SOFA FixedConstraint / RestShapeSprings
```

Used for:
- tool manipulation
- bone anchoring
- surgical guidance

Pattern 3: Fiducial controls target position
```
vtkMRMLMarkupsFiducialNode
        ↓
observer
        ↓
update goal position in SOFA controller
```

Used in:
- needle steering
- inverse problems
- constraint targets

6. Why SoftTissueSimulation feels hard
- ParameterNode abstraction
- Observers everywhere
- GUI state + MRML state + SOFA state

Designed for:
- reusability
- robustness
- end users

This adds indirection, not new physics.

7. ParameterNode: what it really is

A ParameterNode is just:
- a structured MRML node
- storing references + scalar values
- emitting ModifiedEvents

It enables:
- state persistence
- GUI auto-sync
- scene save/load

It is not required for:
- learning SlicerSOFA
- prototyping
- translating existing SOFA scenes

8. Recommended learning order (you chose correctly)
Phase 1 (now)
- prostate.py-style linear flow script
- Explicit SOFA scene
- Manual MRML ↔ SOFA mapping
- No ParameterNode
- Minimal observers

Phase 2
- Add 1–2 observers explicitly
- Markup → force / constraint
- Still script-based

Phase 3 (later)
- Introduce ParameterNode
- Move logic into module structure
- Use SlicerSOFA patterns

Skipping Phase 1 makes everything feel opaque.

9. One key mental model
- SOFA owns physics.
- MRML owns interaction.
- Observers translate intent into physics.

That’s it.

10. A simple rule to remember

If data changes because time passed → SOFA

If data changes because user touched something → MRML observer

If both must stay in sync → mapping + observers
