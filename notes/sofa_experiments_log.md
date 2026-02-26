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
  - contact counts per frame, penetration distances, plane contact force (stable or unstable? Suddenly increase), and kinetic energey (e.g., when move slower, is it stable or suddenly increase? Is it accumulating, dissipitating, or oscillating (inssufficient damping)

### March 02
Goal: why did frame rate drop throughout time steps?

Task: extract contact numbers per frame to monitor changes.
- Switch back to genericConstraintSolver to export it (probably don't do it since I am using the SparseLDLSolver: https://www.sofa-framework.org/community/forum/topic/counting-number-of-nodes-in-contact/
- Extracted from the contact manager.

Task: alter rayleigh damping values:
- RayleighMass = 0.005, 0.01, 0.02
- Perhaps combined with repeated movement cycle
