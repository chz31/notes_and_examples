### Feb 10, 2026
Tested mesh roi select file on office workstation with collision model, but the new tool file is not uploaded to the Drive.\
Old plate too sparse\

Problem: still the collision model penetration issue. <r>

Plan:<r>
1. Move the tool model slower to allow collision computation
2. Create a collision-only tool object without simulating it as a rigid object. Move the collision model by interpolation using a transform.

Go back to find that tool model or find a new way to easily fabricate models.<br>
Find the "interpolation example" Paul mentioned or asked him on Discord. <br>
Looks like it is the linearMoveMentProjectiveConstraint method.


The "test_roi_select" method also needs to be updated. For example, collision models can be grouped to optionally 
activate/deactivate them between objects. <br>

Only enable collision model at the positive surface of the retractor model. Using the zero-thickness plane model as the actual collision model. 
Visual model with a thickness could be used via mapping. <br>


### Feb 12, 2026
Move the new plate with 5,000 points collision model slower with `root.addObject('LocalMinDistance', alarmDistance=0.5, contactDistance=0.1)`. Penetration still occurs.

Using     
`root.addObject('CCDTightInclusionIntersection', name="Intersection", continuousCollisionType="FreeMotion",
                        maxIterations=1000, alarmDistance = 0, contactDistance = 1) #sofa > v25.12`
The simulation stuck
What is collapsed is the tiny protrusion that protruded into a depression of the bone; it was not a sharp protrusion but looks pretty smooth.
After collision, the tetrahedron just exploded
Same issue did not happen for the old `LocalMinDistance` setup, in which the plate simply penetrated the protrusion


Create a smoother model without that protrusion using CGAL --Done

A reason that `CCDTightInclusion` is probably because the `contactDistance=1` was too large, causing collision detection detected many
points away from the actual contact area as shown in a screenshot. Collision still failed when using a much smoother orbital model.
Change to `contactDistance=0.1` at least did not cause the explosion of tetrahedra and visually chaotic collision detection.
However, the collision is still very slow. Penetration also still occured.

<img width="300" alt="Screenshot from 2026-02-12 11-07-58" src="https://github.com/user-attachments/assets/aedfd0cd-0259-4310-a651-ce14b56bf3a7" />
<img width="300" alt="Screenshot from 2026-02-12 11-36-28" src="https://github.com/user-attachments/assets/2e38e45f-3c6d-484a-8874-8d88442f8fb9" />
<img width="300" alt="Screenshot from 2026-02-12 17-26-42" src="https://github.com/user-attachments/assets/b2f94b71-0d55-4803-8146-5e2e72aa1318" />
<img width="300" alt="Screenshot from 2026-02-12 17-38-35" src="https://github.com/user-attachments/assets/1c135f0a-e4ad-475f-ad58-118fd5757a9e" />



Next time:
Create a partial collision model of the orbital tissue
Create a sparser retractor model.
Worked now: Rigid mapping between plane and plate model did not work for retractor `toolFineVisualModel.addObject('RigidMapping', globalToLocalCoords=True)`

### Feb 17, 2026
It could be the mesh compression issue causing collision model penetration
- Disable bone, try to lift the tissue, and if penetration still occur
  - Even disable the bone collision model by simply lift it, penetration still occurred
  - Disable restSpringForceField for the tissue points within the ROI, penetration disappear (of course because the model just flew away upon contact.)
  - The above shows it was the constraints causing the problem.
  - Change restSpringForceField of orbital tissue stiffness from 1e6 to 1e6, tissue started to bounce up and down and penetration still occured when it bounced back
  - Using fixedProjectiveConstraint instead, penetration still occurred

- Test a generic soft model without MeshROI select without bone
  - Using youngs = 4e2 and poisson = 0.2 appeared to improve the problem. Lift a generic tissue model showed no or minimal penetration, but computation really slow.
  - However, when youngs = 4.5e4, collision detection works, collision reaction observed but plate penetration occurred more severe; Thus, collision model failed probably due to object too stiff?


Somehow when I used a smoother orbital tissue model with the same material property, I could not demonstrate the deformation within the orbit, 
especially the different compression of fat and other tissue, 
by dragging it against the orbital wall. The collision detection was confirmed. However, collision took a huge amount of time to calculate. 
The model also appeared to penetrate the orbital wall a lot.
I think collision model still worked since I also switched restSpring with fixedProjConstraint.

If penetration still occurs but it does not prevent tissue retraction for plate insertion, then it will be fine.

However, collision computation was too slow. After a few lifting clicks, it just stuck there and took a huge amount of time for computing.

Did these steps suggested by ChatGPT as well:
What to do today (30–60 minutes): one “stability sanity pass”

Goal: stop the catastrophic stall and get “it retracts without freezing.”

Step 1 — Simplify contact to remove solver overload

Change:

CollisionResponse ... FrictionContactConstraint
to:

CollisionResponse response='PenaltyContact' (temporarily) #This did not work at all.<br>
Keep LocalMinDistance and disable CCDTightInclusionIntersection for now. #This obviously made it faster

Step 2 — Remove tool internal fighting<br>
Comment out the tool’s RestShapeSpringsForceField entirely first.<br>
Keep the bilateral constraint (one coupling is enough).

Step 3 — Reduce tool movement step<br>
In ScoopController, set delta=0.05 (or 0.02). 

Step 4 — Make tissue uniform (remove heterogeneity for now)

Temporarily set a single Young’s modulus, e.g. 2e3–5e3 Pa, Poisson 0.2–0.35.
Your 100× contrast (4.5e4 vs 4.5e2) is not a good first stability test. 

**Experiments:**<br>
dt = 0.01; delta = 0.05; orbital tissue fixed by RestShapeSpringField; heterogeneous model; tool RestShapeSpringForceField still there.<br>
Both CCD and LocalMinDistance performed moderately better, especially at the initial steps. After several lifting clicks, penetration still occured.
LocalMinDistance appeared to perform moderately better in this case.

Disable tool RestShapeSpringField.
Same setting as above: both CCD and LocalMinDistance still showed penetration.

Overall, moving the plate slower, i.e., wait for a few seconds between controller activation, helped to prolong good collision response.
Eventually, penetration still happened. I simply could not lift the soft tissue for a visually significant amount of distance.

Homogeneous model with young's = 3e3 and poisson = 0.2
Other settings the same as above with tool RestSpring disabled. <br>
Both CCD and localMinDistance: penetration eventually still occurred. Still could only lift the tissue model minimally.

Perhaps the force isn't large enough is the reason that the orbital tissue could not be significantly lifted upward.

Actually, if I holding the tool lifting key and forced the tool to move upward, the orbital tissue could be lifted significantly.
However, the penetration also became more and more severe. Eventually collision model just failed probably because 
the computation became too intense.

<img width="300" alt="Screenshot from 2026-02-17 09-46-00" src="https://github.com/user-attachments/assets/0f39d93f-5947-44d9-98eb-1abd7b09d484" />
<img width="300" alt="Screenshot from 2026-02-17 11-07-56" src="https://github.com/user-attachments/assets/8a061e74-e60f-4fbb-a4c9-3f65f879ec25" />
<img width="300" alt="Screenshot from 2026-02-17 13-18-07" src="https://github.com/user-attachments/assets/742607da-d564-43f8-9cf2-7df23e7ad067" />
<img width="300" alt="Screenshot from 2026-02-17 13-40-48" src="https://github.com/user-attachments/assets/044669d5-7934-4bd9-baee-8dbad93ced6e" />


When dragging orbital tissue within the orbit, change mouse setting to attach cursor at a point using bilatConstraint

**Need to start from the position for lifting tissue to control variables.**

**Need to design a more efficient and controlled experiment. For example, using interpolation to move the tool along a certain path for n time steps, 
then visualize the final results in SOFA, instead of just clicking the controller keys by hands**

Understand how mechanical object is constructed? Passing the mesh topology to it? Which mesh? 
What if nothing is simulated but only a collision model exists? Why must have a mechanical object?<br>
Understand how collision response is mapped to the mechanical object (?) <br>

**What I learned today:**
- Increased stiffness made penetration worse
- Orbit is not required for instability; removed orbit still showed same issue
- It is not just a problem of dt, even move tools slower did not fix the penetration issue though helped initially
- Adding constraints causing the collision issue, even a simple one
- Heterogeneity is not required for instability: homogeneous soft tissue behaves moderately better, though did not ultimately solve the penetration issue
- CCDTightInclusion did not solve the problem at current setting. With large contactDistance it exploded.
- PenaltyContact caused explosion
- Large collision meshes likely overload the solver
- Manual keyboard lifting introduces uncontrolled velocity jumps
- Tool spring removal does not fix it


**ChatGPT's guess**
Based on everything:

You have a dense contact constraint system with:
- moderately stiff deformable body
- Lagrangian friction contact
- insufficient damping
- large contact candidate sets
- potentially mismatched collision geometry templates earlier

Over time:
- constraints accumulate
- solver cannot fully converge within one step
- penetration grows
-e ventually freeze or explosion

This is a scaling + constraint resolution problem. Not:
- a modeling philosophy problem
- not a Young’s modulus conceptual problem
- not a “you don’t understand FEM” problem

How do I make a bounded-size contact problem between a soft body and a kinematic surface that does not accumulate unsatisfied constraints over time?

### Feb 19 SOFA tests:
Create a reusable scene.
Using interpolate methods to define a tool moving path within a certain amount of time.
Run SOFA in the background, then display the results in the GUI.

Simplified tissue and tool models

Add damping; Crop collisions to a tight ROI (don’t let it touch the whole world)

Task 1: create a sparser retractor collision model and use an ROI to crop the orbit collision model
Setting: plate collision plane model: 30 * 20 points; tissue collision model: roi selected inferior half.
Tissue youngs modulus: 3e2; no orbital bone model included.
**Results significantly better**. Faster with occasionally minimal penetration, even when holding the lift key and retracted a longer distance.
One issue may cause previous failure could be a low convex are (though looked smooth) at the inferior tissue model.
The plane contacted it first and almost throughout the retracting process with minimal contact of other tissue inferior surface.
That region was usually worst for penetration. In a stiffer model, other regions eventually also penetrated.
This could be due to failure of solvers in that region impact the solving of the whole tissue collision model. <br>

Eventually penetration in that convex area still occurred and spreaded to bigger area when I moved the plane up and down fast.

Thus, the hypothesis is that in a stiffer tissue model, if the curvature at the contact surface isn't smooth, that is, a small
elevated area, though appears to be smooth, present like in the current case. It may cause problem of convergence (hopefully I am using it right)
because the collision will only occur at that small area. The issue is, this is probably the case for fat herniation: 
a small area of fat herniates into the maxillary sinus.

Task 2:
**Don't forget to reset the controller center of mass to the current center of mass** Could this be a reason for the penetration problem?

<img width="300" alt="Screenshot from 2026-02-19 10-31-35" src="https://github.com/user-attachments/assets/6db45926-b1df-44a6-82cb-9b6f217641c4" />
<img width="300" alt="Screenshot from 2026-02-19 10-19-49" src="https://github.com/user-attachments/assets/2f701877-7a0e-497f-84da-90559ad641cf" />



### Feb 24:
Previously penetration of soft tissue might be caused by the protruded or elevated area near the anterior edge. 
If the plane is underneath a significant part of the globe, then retraction works well even for faster movement by holding the lifting key.
A protrusion near the anterior edge still penetrated the plate. Another elevated area in the middle also penetrated the plate eventually.
However, overall the orbit could be lifted significantly even though those two protrusions are present. 
Meanwhile, the original protruded area, now near the left lateral edge of the plane, stopped penetrating the plate.

I then move the plane backward to a position similar to the position I tried last time. That original protruded area still penetrated the plate after retracting
the orbit significantly but somehow to a much lesser degree. I could also lift the orbital tissue pretty efficient even thought the plane was not
fully underneath the tissue.

It could be because I reset the center of the controller object to the center of the plane object.

Successfully added a linear projective constraint to move the plate

Controller moved with the linear movement. After pressing controller key, the plane suddenly reset to the original position and the tissue bounced back.

Why does the controller reset the plane after LinearMovement moved it to 10?<br>
This is the important one. The root cause: you now have two masters driving the same rigid state<br>
During the lift, your tool pose is being dictated by: LinearMovementProjectiveConstraint (hard projective constraint) on the tool’s MechanicalObject<Rigid3>
Your controller setup is also dictating tool pose via: controllerMO (toolCMState), BilateralLagrangianConstraint between controllerMO and toolMo. 
So after the motion, when you use the controller, it “wins” (or conflicts) and the system resolves by snapping back toward the controller’s state. 
That looks like a reset. It’s not primarily center-of-mass. It’s competing constraints. <br>

Why did the controller move with the plane during lifting? Because the bilateral constraint couples them. When LinearMovement forces the tool, the bilateral constraint forces the controller to follow (or vice versa). So you see both moving. Then when you actuate the controller, it pulls the coupled system toward its own stored state (which may still be the old pose, depending on your controller implementation).


**With releigh damping reduced tissue bouncing by reducing kinetic/oscillation energy**, looked like the results got much better, even the protruded area near the plane anterior margin did not penetrate.
Eventually, penetration still occured. Need controlled tests using linear movement for more distances next time to see whether damping indeed helped.

<img width="300" alt="Screenshot from 2026-02-24 15-45-40" src="https://github.com/user-attachments/assets/5efb5b5e-08b5-4be0-b6f0-0d5e14818947" />
<img width="300" alt="Screenshot from 2026-02-24 10-41-03" src="https://github.com/user-attachments/assets/9d9ca5a9-3a79-41e3-a469-64d3a53bc7ee" />
<img width="300" alt="Screenshot from 2026-02-24 10-29-07" src="https://github.com/user-attachments/assets/a733e206-60ff-4af7-9e36-e3a6467fdb2e" />


SOFA notes: why small protrusions causes problem (from ChatGPT):
- When the plane is well underneath the globe → lifting works well
- When protrusions are near anterior edge → penetration occurs
- When moved slightly backward → penetration reduced
- When controller center changed → behavior improved

Protrusions create local curvature mismatch --> Local curvature + low collision resolution = unstable normal estimation --> Near edge contact → reduced constraint redundancy --> Small changes in tool pose change contact graph topology
- Fewer constraints, high local force concentration, larger penetration oscillation

Broad region: contact normal distributed and system well-conditioned.

ChatGPT: not a solver failure, but contact issue.

ChatGPT summary: Contact stability in orbital retraction is highly dependent on tool support coverage and constraint graph conditioning. Preliminary experiments demonstrate stable lift under full and partial support, with localized penetration emerging under edge-only contact due to reduced constraint redundancy rather than global solver instability.

Next time, also test a stiffer model and perhaps heterogeneous model without orbit. Compare damping vs no damping

### Feb 26
dt = 0.01<br>
movement = 0.05/dt<br>
Initial frame rate 1.4 --> after 1s: <1 --> after 3s: 0.6 --> after 4s: < 0.5

This movement is probably enough for testing:
```
toolNode.addObject(
    'LinearMovementProjectiveConstraint',
    template='Rigid3',
    keyTimes="0 1 2 3 4 5 6",
    movements="""
        0 0 0   0 0 0
        0 0 5   0 0 0
        0 0 10   0 0 0
        0 0 15   0 0 0
        0 0 15   0 0 0
        0 0 15   0 0 0
    """
)
```

**Youngs = 3e2 poisson = 0.2 rayleighMass=0.01 rayleighStiffness=0.1**
Minimal penetration at the protrusion at the anterior edge

**Youngs = 3e4 poisson = 0.2 rayleighMass=0.01 rayleighStiffness=0.1**
Minimal penetration at the protrusion at the anterior edge; It appears that the anterior protrusion protruded earlier probably due to the stiffness (I could be wrong) <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/d8f53957-a509-4491-acbf-314de848aaec" />

Task: write a helper function to convert Slicer transform to SOfA initial position for testing.

Task: test differemt rayleigh damping

Task: test different lifting distances, velocity, contact distances, dt, and repeated movement cycles

**Task: Quantify testing as stability metrics across time steps instead of just visual examination**
  - contact counts per frame, penetration distances, plane contact force (stable or unstable? Suddenly increase), and kinetic energey (e.g., when move slower, is it stable or suddenly increase? Is it accumulating, dissipitating, or oscillating (insufficient damping)

### March 01
Added the orbit back. The tool can create a small gap at the floor of the orbit using homogeneous model with youngs = 3e2. Using personal laptop <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/32962e5a-66df-4c78-a744-62437fc34bdb" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/94163384-ab1c-47ba-824f-44de29e150c5" />
<br>
However, computation becomes really slow. After 98 time steps (dt = 0.01), the FPS dropped to 0.2. Contact at the orbital roof and wall likely led to slow down.<br>
Perhaps it is caused by material property too difficult to be compressed.<br>
Will adding higher dampiing values lead to more compressible model?

Though getting really slow, it did not look like the collision model exploded.

**Error: "DefaultContactManager" did not exist** as shown by below:
```
for obj in root.objects:
    print("root object:", obj.name, obj.__class__.__name__)
```

**Find where contacts are stored.** 
- Export contacts got a bit complicated; perhaps started from exporting forces instead to see if force is stable.
- Perhaps need to ask the **SOFA forum** how to do it, particularly referring to the CCDTightInclusion collision explosion case.

**Export constraint count** can be helpful to catch the collision explosion or increasing number of collisions over time.

**Export forces** and other mechanical states.

A thread for write and read mechanical state (position, velocity, force, etc.): https://www.sofa-framework.org/community/forum/topic/exporting-states/


### March 02
Goal: why did frame rate drop throughout time steps?

Task: extract contact numbers per frame to monitor changes.
- Switch back to genericConstraintSolver to export it (probably don't do it since I am using the SparseLDLSolver: https://www.sofa-framework.org/community/forum/topic/counting-number-of-nodes-in-contact/
- Extracted from the contact manager (did not work)

Task: alter rayleigh damping values:
- RayleighMass = 0.005, 0.01, 0.02
- Perhaps combined with repeated movement cycle

Tasks:
- Export forces
- Export constraint count

**Tested export plate force**<br>
Using `toolMO.force.array()[0]` for the rigid3 force vector
Plate force returns zero due to added LinearMovementProjectiveConstraint.

Reason: when collision happens, the solver solves for adding new constraints, including contact non peneration, bilateral constraint, and friction, to the mechanical states of the object, i.e., to correct the behavior of the objects.
Typically, both the rigid and soft objects will receive opposite impulses from the constraints.
In this case, only the soft tissue will receive the constraints because its DOF, the mechanical state, if free.
The movement of the planeis fixed by a defined trajectory by the LinearMovementProjectiveConstraint. It moved according to the trajectory defined by the Projective Constraint.

Thus, the plane DOF is fixed by the projective constraint and behaved like a moving boundary condition as an infinite mass kinematic boundary. The reaction impluses from collision added to the plane cannot override/modify the DOF fixed by the Projective Constraint. Thus, the export force will always be zero. The plane will move exactly as the LinearMovementProjectiveConstraint defined regardless of the collision constraints and reaction impuls.

The reaction from the collision still and only exists in the constraints lambda from the collision solver but cannot modify the DOF of the plane. Thus, monitoring constraint counts and magnitude can be useful signals for detect issues such as oscillation and contact explosion (suddenly more contact pairs, thus much more constrants).

One way to let the reaction impulse change the plane DOF is to use a stiff Spring model to use a spring force to drive the plane (via the controller?): `F_contact + F_drive = Ma.`

BilateralLagrangianConstraint can also may also enable it.

Also exported soft tissue force to monitor contact explosion indirectly. **Note that soft tissue mstate force include contact force, damping, internal force, etc., depending on the timing.**

Tissue force produced huge oscillations:
```
[tissueF] step= 80 t= 0.810 Fmax=8.86e+04 Frms=1.48e+03 [force] step=85 t=0.860 |F|=0.0000 [tissueF] step= 85 t= 0.860 Fmax=1.6e+05 Frms=3.02e+03 [force] step=90 t=0.910 |F|=0.0000 [tissueF] step= 90 t= 0.910 Fmax=8.38e+04 Frms=1.4e+03 [force] step=95 t=0.960 |F|=0.0000 [tissueF] step= 95 t= 0.960 Fmax=1.62e+05 Frms=3.09e+03 [force] step=100 t=1.010 |F|=0.0000 [tissueF] step= 100 t= 1.010 Fmax=3.99e+05 Frms=7.38e+03 [force] step=105 t=1.060 |F|=0.0000 [tissueF] step= 105 t= 1.060 Fmax=4.07e+05 Frms=7.34e+03 [force] step=110 t=1.110 |F|=0.0000 [tissueF] step= 110 t= 1.110 Fmax=9.02e+04 Frms=1.51e+03 [force] step=115 t=1.160 |F|=0.0000 [tissueF] step= 115 t= 1.160 Fmax=330 Frms=10.7 [force] step=120 t=1.210 |F|=0.0000 [tissueF] step= 120 t= 1.210 Fmax=1.63e+05 Frms=3.12e+03 [force] step=125 t=1.260 |F|=0.0000 [tissueF] step= 125 t= 1.260 Fmax=364 Frms=12.7 [force] step=130 t=1.310 |F|=0.0000 [tissueF] step= 130 t= 1.310 Fmax=1.68e+05 Frms=3.28e+03 [force] step=135 t=1.360 |F|=0.0000 [tissueF] step= 135 t= 1.360 Fmax=1.55e+05 Frms=3.03e+03 [force] step=140 t=1.410 |F|=0.0000 [tissueF] step= 140 t= 1.410 Fmax=7.37e+05 Frms=1.47e+04 [force] step=145 t=1.460 |F|=0.0000 [tissueF] step= 145 t= 1.460 Fmax=413 Frms=17 [force] step=150 t=1.510 |F|=0.0000 [tissueF] step= 150 t= 1.510 Fmax=434 Frms=18.3 [force] step=155 t=1.560 |F|=0.0000 [tissueF] step= 155 t= 1.560 Fmax=7.42e+05 Frms=1.45e+04 [force] step=160 t=1.610 |F|=0.0000 [tissueF] step= 160 t= 1.610 Fmax=3.71e+05 Frms=8.7e+03
```
It could be the force was exported wrong.


### March 11
<img width="600" alt="image" src="https://github.com/user-attachments/assets/dc099d42-6da4-4af0-a815-7fd7153f7ff5" /><br>
Kinentic energy in continnum object is based on an intergral of the mass density field multipled by v(x)^2 and then by 1/2 at the point of that field.<br>

In FEM, for simple uniform and diagnol mass, it is the sum of 1*2 * m_i * vi, i = node_i, i.e., the lump of all kinetic nodal energy. Each node behaves like a single particle.

Overall, if Vmax or Vrms goes up, kinetic energy goes up. Thus, v is used as a proxy to monitor kinetic energy spikes.

ChatGPT's idea:
If kinetic energy spikes, that indicates contact correction --> velocity injection --> oscillation<br>
If kinetic energy does not spike, huge force oscillation may indicate constraint impulses but velocities corrected quickly.


For meshmatrix mass, SOFA computes kinetic energy as:<br>
<img width="600" alt="image" src="https://github.com/user-attachments/assets/d9809d7f-9e7e-4b95-9dbe-ed3f3b7470c4" /><br>
Rather than just lumping nodal energy.

`MeshMatrxiMass` builds a mass matrix for each mass, so the true total kinetic energy is:
- v = nodal velocity vector
- M = mass matrix assembled by MeshMatrixMass
- Ek = 0.5 * v^T M v
For a Vec3 mechanical object with N nodes in standard FEM, v is column vector of DOFs [v_1x, v_1y, v_1z, v_2x, V_2y, ... ] with 3N_node DOFs,
In SOFA, it will be represented as a (N_node, 3) matrix but flatten during FEM computation<br>
M is a 3N x 3N matrix

In current script, `vm2 = np.sum(v**2, axis=1)` is essentially getting `||v_i||^2 = v_ix² + v_iy² + v_iz²` fpr each node, which is proportional to the global kinetic energy

Overall, each node contributes a small kinentic energy. 

Overall, by adding v to the export, the force still oscillated huge but velocity only shows moderate oscillation (depends on the scale, could still be large, but certainly to a lesser degree than the force) and decayed smoothly after plane motion stopped.

ChatGPT's opinion:
Overall, the global system and damping response is stable. The spikes of force is likely due to localized contact correction/conditioning for edge protrusions/penetrations/local basd contact geometry.

Export constraints number `lambda` next time. Do the big force spkies concicide with contact/constraint bursts?

Planning experiments using the **Design of Experiment** approaches.


### March 18
Tested documenting constraints from "BlockGaussSeidelConstraintSolver". The reason is the behavior to monitor is happening in the Lagrangian constraint solve, not in the tool’s MechanicalObject.force due to offsetting by projective constraint.

Documented:
- currentNumConstraints → most useful first
- constraintForces → likely the best proxy for lambda magnitude
- currentNumConstraintGroups → secondary, less important
- graphConstraints → probably internal structure, not first choice
- computeConstraintForces → likely a flag/method, not the data you want

`currentNumConstraints` slowly increased with small oscillations, rather than having big spikes like the tissue force array. This strongly suggests constraint accumulation / expanding active contact set, not a single catastrophic contact explosion. This appears to be consistent with gradual increasing of frame rate.

Currently, the constraintForces are empty. To export it, set up its parameter to True:
```
root.addObject(
    'BlockGaussSeidelConstraintSolver',
    computeConstraintForces=True,
    # your other parameters...
)
```
The steady increasing of constraint number could be due to more contact points.

Next time, add:
- `currentNumConstraints`: best first metric for contact/constraint accumulation
- `currentIterations`: useful to see whether the solve is becoming harder even if constraint count stays similar
- `currentError`: useful to see whether constraint satisfaction quality worsens
- `constraintForces`: useful, but only after enabling computeConstraintForces=True


### March 22 and 25

Converted the test_roi_select.py into a SlicerSofa scene test_slicersofa_roi_select.py and can run properly.

Use cgal to created a downsampled homegeneous mesh with 6,000 tetrahedras. Created a moderate gap in the orbit at the floor. Need to verify if the the gap is enough.

However, the tool might need to be moved to fully retract the tissue. In SlicerSOFA, the retracted region could be fixed by an ROI, so the tool can be moved to retract another region. The plate can be preinstalled. The retraction can keep moving until no collision between the installed plate and the tissue, which means a gap large enough is created.

Shouldn't inferior oblique stands in the way of plate insertation? Should that region be fixed by an ROI or simply let it to be retracted?

When multi-material model is involved, simulation becomes much slower.

For a simple case, demonstrate some robustness and stability metrics for comparison under different input perturbation. Try use DOE to test something, such as uncertainties of material properties.

How to export them as stress-strain or visualize as heatmap in SOFA or Slicer.


### April 13
Tentative workflow:
- Place a plate first and disable plate collision for the retraction process
- Retract tissue to expose a placed plate
- tissue restoration

Problem encountered:
- plate need to be adjusted, such as moving more posterior to lift local protruded areas.
<img width="300" alt="image" src="https://github.com/user-attachments/assets/0b66d815-1c24-4037-a109-b4665506bfec" />
<img width="300" alt="Screenshot from 2026-04-14 08-42-16" src="https://github.com/user-attachments/assets/44a13140-9e3b-46d8-8b9d-8d25678887fb" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/a9d61622-1431-43e6-966a-b9b251aefae6" />

### April 14
Probably need to save the deformed mesh, and adjust plane position within the Slicer scene.
- From the last position, adjust plane position manually under the intersection area and export new plane centroids
- Prepare a new SOFA scene using the adjusted plane position and deformed mesh.
- Restart the new SOFA scene in the same Slicer scene or a new scene.

I was able to create sufficient gap with one adjustment.
<img width="300" alt="Screenshot from 2026-04-14 09-58-53" src="https://github.com/user-attachments/assets/61f6ae55-4d19-4c80-89b8-6e4637f726d6" />
<img width="300" alt="Screenshot from 2026-04-14 09-54-44" src="https://github.com/user-attachments/assets/47ec0020-aba6-47d3-b74d-7f3603e12c1e" />

However, restoration either using constant force field or gravity became extremely slow. 

I thought it was collison's issue. However, even remove the orbital model, it was still much slower than I thought.

The reason is likely yhe initial state of the restoration scene was the retracted and deformed tissue rather than the true initial state before retraction. This initial state caused weird deformation 
when the posterior tissue is fixed either by RestSpringForceField or FixedProjectiveConstraint.

First, reduce the posterior fixed ROI to a small region.

Second, manually set up the true initial state.

### April 16-17
Eventually the tissue bounced back by setting its mechanical model's rest_position as the original tedrahedral points:
```
    tissue.addObject(
        "MechanicalObject",
        template="Vec3d",
        name="MechanicalModel",
        position=deformed_tetra_positions,
        rest_position = tetra_points,
        showObject=True,
    )
```
However, the process is extremely slow.<br>
<img width="250" alt="image" src="https://github.com/user-attachments/assets/54c2bfc1-e5b0-49c7-8ac0-d122eaba31cf" />
<img width="250" alt="image" src="https://github.com/user-attachments/assets/f29d1a0b-3190-4983-bff3-119652d99beb" />

Simplified the plate 2D model.

Did another test without the skull. It was faster, though not smooth. However, looks like as the first touch of the tissue model and plate was made, simulation was stopped. Adding gravity showed similar effect.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/6eb74bce-a8c3-4743-b524-a67c0aff0922" />

Removing the plate so no collision existed. Re-do the tissue restoration.<br>
The tissue can return to the original condition (blue).
<img width="300" alt="image" src="https://github.com/user-attachments/assets/f126fe92-71c2-4fa7-b84e-aa08e40337fa" /> <br>

Below is the deformed tissue restoration when collision is present vs the original:<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/e1b1e9c9-40cc-4cdd-a07c-62538a975ba6" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/3b1e5ca4-ab11-4505-82b8-c0f82091569a" />

How to restore the tissue back to original when collision is present?

Also, the tissue does not behave like fat tissue. The deformation is too coherent. Fat tissue should be more relaxed when local deformation is applied. 

Next steps:
- Using heterogeneous tissue
- Reduce ROI size
- Reduce or even eliminate damping
- Increase poisson ratio for incompressibility
- See if there are other SOFA components suppert hyperelastic or large deformation model rather than just tuning a linear elastic model for simulating fat tissue beavior (perhaps reading literatures about how fat tissue is simulated).

## April 19
Tried all below but problems were not solved:
- Heterogeneous tissue
- Smaller fixation ROI
- Reduced damping
- Increased Poisson ratio
- Penalty contact
- Weaker fixation
- Added gravity

Perhaps it is because running retraction and restoration in different scenes so the memory of the process was all lost in the restoration scene other than the initial positions.

## April 20
Changed collision models. If set to all triangle collision models, collision detection failed. If enable all collision models, local penetration became worse, suggesting redundant collision models did not make collision better but worse.

Insufficiant restoration could be due to too many constraints and irregular restoration forces.

Next: create an ROI to specify tissue collision region to reduce constraints. 

Setting up the whole original positions as the rest state might be too aggressive. Instead, only setting up the original positions of the retracted area as the local rest position and adding restoration forces to the retraction area.

First experiment: using an ROI to fix the superior part of the tissue, and add a constant force to the retracted part.
- Disable tissue MO rest position = original point positions
- Using an ROI to select retraction area and add a constant force
- Increase force to -100000
- Tissue deformed and fully dropped unto the plate without visible signifcan penetration. Some local penetration still occured.
- However, deformation looks unrealistic<br>

<img width="250" halt="image" src="https://github.com/user-attachments/assets/034e76ae-b496-4569-b850-d1293074aea7" />


## April 21
Task 1: add a restoration ROI at the anterior tissue, then add a constant force field to pull the tissue down; with or without gravity
- Add or not add original tissue as rest state
- Additionally, add a plate to slowly move downward to reduce sudden dropping of tissue (Looked like the tissue was able to move closer to the plate when added this, though simulation slower)
- Try the simple heterogeneous model for the same workflow

Looked like to make the anterior tissue continue deform toward the plate after posterior region fully contacted the plate, a large constant force had to be added. To make it work, the only way is to fix the upper part of the tissue using FixedProjectiveConstraint. Otherwise, dx per dt will easily exceed the contact distance. 

Compute safe distance for dx < contact distance when applying a constant force with a given dt.
```
a = F / m; F = force on one node, and m = mass of one node
dx ≈ 1/2 * a * dt^2
   = 1/2 * (F/m) * dt^2
1/2 * (F/m) * dt^2 < d_safe
Which gives:
F < 2 * m * d_safe / dt^2

If ConstantForceField uses totalForce, the force is distributed over N selected nodes, then:
F_node ≈ F_total / N
F_total / N < 2 * m_node * d_safe / dt^2
or:
F_total < N * 2 * m_node * d_safe / dt^2
where m_node ≈ TOTAL_MASS / total_number_of_tetra_nodes
```

Script for extracting "safe force" given dt and contact distance
```
mo = sim.tissue.getObject("MechanicalModel")
roi = sim.tissue.getObject("ConstForcePoints")

n_total = len(mo.position.array())
n_roi = len(roi.indices.array())

print("total nodes:", n_total)
print("ROI nodes:", n_roi)
print("avg node mass:", 0.1 / n_total)

m_node = 0.1 / n_total
dt = 0.01
contact_distance = 0.05
d_safe = 0.25 * contact_distance

f_node_safe = 2 * m_node * d_safe / (dt ** 2)
f_total_safe = f_node_safe * n_roi

print("safe per-node force ~", f_node_safe)
print("safe total force ~", f_total_safe)
```

On the other hand, a smaller dt could be used to make dx much smaller to accomodate for large force.

In that case, if F increases 100 times, dt should drop to 10 times smaller to maintain dx.

Plane motion should also increase 10 times to accomodate for small dt.

**results**
- Adding initial positions as rest positions and using homogeneous model: with or without fixed the upper tissue, anterior tissue region can both be pulled closer to the plate with a large constant force. However, without fixed the upper tissue, a smaller dt has to be added to compensate for the large force to avoid `dx > contact distance`. Also, when the upper tissue is not fixed vs deformation, there will be somewaht different deformation (of course). It looks like the fixed one (red) showed less changes because, when tissue is unfixed (blue transparent), it has more freedom to move around within the orbit.<br>
<img width="250" alt="image" src="https://github.com/user-attachments/assets/ba4cb601-8a61-4f08-b74c-3f78d22a4968" />
<img width="250" alt="image" src="https://github.com/user-attachments/assets/794fdc33-5ffa-4783-8c9c-2c813276f093" />

- Heterogeneous model will require a higher force to restore it. This is a problem. Furthermore, it is better to start with a retracted heterogeneous rather than homogeneous mesh for the retraction scene.
- Inferior rectus needs to be corrected to reduce its size or it may occupy the entire space inferior to the orbit.

Task 2: create a multi-material model with multiple tissue types to try the workflow

Task 3: inquire Paul about tissue restoration problem


## April 22
Task: Prepare a demo SOFA scene for Paul to debug

## April 23
Sent the demo scenes to Paul to debug.

Install SOFA on Mach.

Mesh preparation for specimen 1224
- Skull editing:remove bones at fracture site
- Combine all tissue segments at fx side into one
- Use nnInteractive or other tools to re-segment inferior rectus
- Or simply do not include inferior rectus in MeshROI select

## April 24
Mesh preparation
1. Use nninteractive to make a complete orbit other than the fractured side
2. Subtract the orbit from the tissue model. Clean the fx bones.
3. Clone and expand skull by 0.8 mm.
4. Subtract the tissue model from
5. Run a 3x3 kernel smoothing

## April 25
Tet number: about 9,000
Skull: about 5,000 points

Simulation very slow. After 1.5 sec, frame rate dropped to 0.1 sec This could be caused by collision at the protruded herniated region.
<img width="250" halt="image" src="https://github.com/user-attachments/assets/5c93f384-5fa3-46d0-9148-ce4cb28985be" />

At 1.58 sec, simulation basically stopped at the screenshot below. No more retraction could be effectively created even when time step slowly proceeds.

<img width="250" alt="Screenshot from 2026-04-27 13-39-54" src="https://github.com/user-attachments/assets/add34848-4573-4041-bb3b-43b51aa7df5a" />
<img width="250" alt="Screenshot from 2026-04-27 13-40-07" src="https://github.com/user-attachments/assets/31daeab7-e497-4591-8508-3fb569fda529" />

At about 1.74 sec, there is a bit collision defect appeared at the protruded region:<br>
<img width="200" alt="image" src="https://github.com/user-attachments/assets/2d657cd8-41e2-4a85-acdc-1cd1cc42d84a" />

Need to experiment a much smaller posterior fixed roi.

Need to experiment by using more aggressive local smoothing or even removing that herniated region.

## April 27-28

The distinct protruded herniated region may be the reason that cause simulation to stuck without creating sufficient gap for homogeneous model.

Next time:
- Create separate retraction, one for push the protrusion into the tissue using a smaller, smoother plane, and another for pushing the entire tissue
- Or simply remove any distinct protruded area see how things work. As the fracture occur, the fat tissue's overall volume enlarged, so removing a local protruded area may not hurt that much for outcome prediction.

Built a stacked MeshROI heterogeneous mesh. I suspect that the simulation would be super slow.

## April 29
The heterogeneous mesh from CT_brain with multiple MeshROI and Young's modulus values can be simulated in the retractio scene, though much slower.

Next, try use IndexValueWrapper to wrap poission ratio values and see if they can be correctly passed to the tetrahedron force field

Try to design >=2 rounds of retraction to fully retract the tissue in seperate scenes

The internal tetrahedra size appeared to be too large:<br>
<img width="250" alt="image" src="https://github.com/user-attachments/assets/36b93f11-bcba-4cc4-a4de-a5be21c98fc9" />

Redo the meshing by adding `cell_size` parameter to the cgal command to re-do the meshing.This parameter did not work.

Default gmsh way actually produced much finer internal tetrahedra, though reported 65 ill-shaped out of 150k tetrahedra as a warning information but no error.However, this mesh is simply too dense to run any simulation <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/57715a18-3c57-42e7-83fa-0d03e1cd29f0" />

## April 30
gmsh gui settings:<br>
- Element size factor 4
- Min/Max element size 2/5
- Unchek Compute element sizes using points values
- Extend element sizes from boundary

Overall produced around 58k elements, but the internal elements still very coarse. External ones not very uniform because it seems to use the original triangles to do the meshing.

Uniform remesh the surface model into about 2,000 points. Subdivision set up as 1, so each triangle is divided into 4 first. This improves uniformity of triangles.

In gmsh, Element size factor 1 or 1.5 both yielded around 2,000 tetrahedra. The internal tetrahedra appeared to be more uniform.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/ccae59ac-78b9-46fa-8756-e41a236790a8" />

Need a helper function to show the element size range and set up a threshold to ensure relevant size consistency.

It is better to assign regional densities of elements. For example, the globe can have lower density as it is stiffer.

Run gmsh using its Python API.


## May 1
Next week's goal: learn to use gmsh to control mesh density and quality through API, check mesh quality; aiming at creating meshes with 10k points for >=2 specimens.

## May 1-25
Used gmsh python script to create meshes for CT Brain & a fx case with around 10k tets.

Enable extending the boundary interiorly in gmsh setting important to ensure more uniform mesh size rather than extremely coarse sizes interior to the mesh.

Ultimately, mesh size is relevant to the point density at least for now. Aim at 1.2-1.5k points for the surface model.

## May 25
Retracting fx case was really slow likely due to more irregular inferior surface and localized fat herniation.

Experiments to try to decrease:<br>
1. Staged retraction scenes: use a much smaller plane to retract the isolated herniation first, then do a global retraction. (Done)
2. Simplify the collision model of the skull (Done)
3. Try to decrease the threshold and iteration number of BlockGaussSeidelConstraintSolver: `tolerance="1e-3", maxIterations="100"` or even `1e-2/50`. (Done: faster; no apparent severe penetration).
5. Try triangular TriangularFEMForceFieldOptim and FastTetrahedra (DlCorotationalForceField (Done and failed; mesh exploded)
6. Try smaller DT, alarm distance, and contact distance. (Done wiht lower BlockGaussSeidelConstraintSolver values & mu = 0.0/0.1; penetration well observed).
7. Set mu = 0.0 for FrictionContactConstraint. (Done: much faster after setting lower values for the BlockGaussSeidelConstraintSolver. **Collision visually worse at the local herniated region, but still worth trying for a staged local retraction or used at the global retraction stage after local retraction**).
```
DT = 0.002
ALARM_DISTANCE = 0.2
CONTACT_DISTANCE = 0.02
```

Tried `FastTetrahedralCorotationalForceField`. Mesh exploded when animation started. Could be due to RestSpringForceField.

`TetrahedronHyperelasticityFEMForceField` showed similar effect.

Switched to `FixedProjectiveConstrant` did not solve the problem.

The likely culprit is contact-driven inversion: the tool lifts/compresses tissue against the rigid orbit, some local tets flatten or invert, and the corotational/hyperelastic models eventually produce huge forces or invalid stiffness. Hyperelastic delaying the failure fits that story.

Did a 3 stage retraction of 1224 followed by a restoration. The problem is still likely a collision issue. The local herniated fat restored first and touched the plate. After that, further restoration became significantly slower, or basically stopped.<br>
<img width="300" alt="Screenshot from 2026-05-25 22-00-20" src="https://github.com/user-attachments/assets/f95b2721-59bd-4626-8897-4109dce32037" />

**Next steps:**
- Restoration improvement: look for methods that enable fat tissue to behave more like fat tissue. 
- Need a tracker for performance/time per component to identify bottle necks.
- Need a tracker to track collision performance/penentration
- Need a tracker for globe restoration.

**Testing To-Do**<br>
1. Baseline restoration
   - Use `TetrahedronFEMForceField`
   - Set `mu=0.0`
   - Disable gravity and extra force
   - Use plate `PointCollisionModel` only
   - Record whether tissue contacts the plate, whether restoration stalls, and timing after contact

2. Contact distance sweep
   - Test:
     ```python
     CONTACT_DISTANCE = 0.02, 0.01, 0.005
     ALARM_DISTANCE = 0.3, 0.2, 0.15
     ```
   - Record whether contact happens too early, penetrates, or stalls

3. Collision model sweep
   - Test plate collision as:
     ```python
     Point only
     Triangle only
     Point + Triangle
     Point + Line + Triangle
     ```
   - Keep point-only as the baseline if triangle-triangle remains unreliable

4. Solver tolerance sweep
   - Test:
     ```python
     tolerance="1e-4", maxIterations="200"
     tolerance="1e-5", maxIterations="500"
     tolerance="1e-6", maxIterations="2000"
     ```
   - Record whether stalling is true equilibrium or solver slowdown

5. Gravity/bias sweep
   - Try weak gravity in the desired settling direction:
     ```python
     GRAVITY = [0, 0, -50]
     GRAVITY = [0, 0, -100]
     GRAVITY = [0, 0, -500]
     ```
   - Flip sign if needed
   - Avoid physical gravity initially, e.g. `-9800 mm/s^2`

6. Broad force instead of local force
   - If gravity is not anatomically correct, apply a weak `ConstantForceField` over a broad ROI
   - Avoid concentrated local force unless needed
   - Record deformation severity

7. Two-stage restoration
   - Stage A: weak gravity or broad force to settle tissue onto the plate
   - Stage B: export settled state, remove force, reload with:
     ```python
     position = settled
     rest_position = original
     ```
   - Let FEM restore against the plate without artificial force

8. Mesh quality check
   - Check original mesh and stage-3 deformed mesh
   - Record:
     - minimum tet quality
     - number of low-quality tets
     - number of near-zero-volume tets
     - number of inverted tets
   - Treat hyperelastic failure as likely if stage-3 has near-zero or inverted tets

9. Hyperelastic isolation test
   - Disable plate/orbit collision
   - Disable `RestShapeSpringsForceField`
   - Use:
     ```python
     DT = 0.002
     YOUNG_MODULUS = 30
     ```
   - If it still explodes, suspect initial strain or mesh quality rather than contact

10. Material complexity later
    - Do not add MeshROI multi-material until homogeneous restoration/contact behavior is understood
    - Add stiffness contrast gradually
    - Start with modest contrast, e.g. 5-20x, before trying very stiff regions


Paragraph For SOFA Developer<br>
I am simulating staged orbital fat retraction/restoration with a tetrahedral soft-tissue mesh in SOFA. The workflow uses several retraction stages, then a restoration scene where the current mechanical position is the stage-3 deformed tetra mesh and rest_position is the original tetra mesh. The goal is for soft orbital fat to restore/collapse onto a rigid patient-specific plate under elastic restoration and possibly weak gravity. With TetrahedronFEMForceField, restoration starts but often stalls or becomes extremely slow once the first protruding tissue region contacts the plate, even with friction set to mu=0.0. TetrahedronHyperelasticityFEMForceField tends to explode, likely due to large deformation or near-inverted elements in the staged output. Triangle-triangle collision has been unreliable, so I am mainly testing point/triangle collision combinations, contact distances, and solver tolerances. I would appreciate advice on the recommended collision model/contact response setup for a deformable tetrahedral tissue surface settling onto a rigid plate, and on whether there are diagnostics for contact constraint count, inverted tets, or hyperelastic instability in this scenario.


## May 27
Tasks:
- Track performance; plot a curve for each component (Done; did not draw a curve)
- Mesh quality check in gmsh (Done: 1224 stage 3 deformed mesh quality was overall good). No apparent poor quality, fat, or inverted tets found. Most tets changed vol modestly after retraction.
- Hyperelastic isolation test (Done)
behavior tetra mesh responds more smoothly through BarycentricMapping
- Two stage restoration with constant force

Hyperelasitic test: if only disable the orbit, I could see that the distinct local protrusion first recovered, touched the plate, collision model became a bit like a spike, but behavior model just showed a protrusion, I could also see that the tissue mesh bounced back slightly, then quickly exploded. Collision surface mesh gets locally pulled/corrected strongly by contact constraints.
- plate contact alone is enough to trigger instability
- Hyperelastic model too fragile
- Local spikes in collision model without contact still matter. That suggests the protruded region has high local strain or local mesh/collision-surface mismatch, even if not inverted.
- Stable restoration dynamics are possible.
- Contact constraints are expensive.
- Hyperelastic contact makes the local protrusion/contact region numerically unstable.

The collision model might be slightly different from the mesh created from gmsh. They are obviously very close but not identical. I wonder is this matters since the next time step depends on a deformed collision model through mapping

A good diagnostic test is to use the boundary surface extracted directly from the deformed tetra mesh as collision/visual surface, instead of a separately generated OBJ/VTK surface. If that behaves better, the mismatch was part of the problem.
```
same regular FEM settings
same plate/orbit collision
only replace collision surface with tetra-derived boundary surface
compare:
  currentNumConstraints
  wall_step_ms
  globe displacement
  visible local spikes
```

Or make the tissue as point collision model but plate and orbit as triangle collision model.

**Overall, contact constraint increased after contact and a lot of time spent on constraint solver is the main disovery for the restoration scene.**

Next tasks: Can we reduce contact constraints or compliance cost while preserving plausible restoration?
1. Save the current baseline in stdout.txt using current settings
2. ALARM_DISTANCE = 0.15; CONTACT_DISTANCE = 0.005
3. Solver looseness: tolerance="1e-4"; maxIterations="200"; tolerance="1e-5"; maxIterations="500"
4. SparseLDLSolver test: change to
```
tissue.addObject(
    "SparseLDLSolver",
    name="solver",
    template="CompressedRowSparseMatrixMat3x3d",
)
```
5. Plate-only collision test
6. Orbit-only collision
7. Recording each round:
```
settings changed
max currentNumConstraints
max wall_step_ms
final globe_displacement_norm
AdvancedTimer dominant block
visual behavior: stable / spike / explosion / stalled
```
8. Two stage restoration with constant force


## May 28
Task:
1. Create a retraction scene in SlicerSOFA using CT Brain and compare the stable centroids of actual eyeball and MeshROI selected indices. After that, track positions in retraction and restoration and visualize changes in Slicer (Done; there is a minor difference between actual centroid and MeshROI initial centroid: `-26.46756663544368, 89.05504265557123, -11.56861729696182` vs `-26.3434393564642	89.8967865013127	-13.3696739142428` for the CT Brain dataset).
2. Update SparseLDLSolver to "CompressedRowSparseMatrixMat3x3d" (Dones; nothing changed. So the bottleneck is probably not just scalar-vs-Mat3 sparse matrix storage.)
3. Two stage restoration with constant force (partially Done; not a viable solution for now because the local protrusion's hard contact still stalled simulation even with constant force added to pull a region downward).

Current interpretation: the local fat herniation is probably real anatomy, not a mesh artifact. The problem is that the current homogeneous tissue model gives the protrusion the same stiffness/contact behavior as the rest of the orbital tissue. When it reaches the plate first, it creates many contact constraints and the ConstraintSolver becomes the dominant bottleneck. Increasing external force alone did not overcome this.






