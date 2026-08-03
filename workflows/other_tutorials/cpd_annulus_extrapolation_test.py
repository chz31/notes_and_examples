"""
Test script: warp a full pre-surgical local patch (annulus + surgical site)
using a CPD deformation field fit ONLY on annulus-to-annulus correspondence.

Run this in the Slicer Python console (or Python Interactor).

Assumptions going in:
  - Pre and post models are already RIGIDLY registered (global + annulus-restricted
    point-to-plane ICP) and that rigid transform has been HARDENED onto both,
    so everything below is in the same coordinate frame already.
  - You have three model nodes already loaded in the scene:
      preAnnulusNode  : pre-surgical (source), cropped to annulus ONLY (no surgical site)
      postAnnulusNode : post-surgical (target), cropped to annulus ONLY
      preFullNode     : pre-surgical, FULL local patch (annulus + surgical site),
                        same rigid transform already applied/hardened
  - Update the getNode(...) calls below to match your actual node names.
"""

import numpy as np
import vtk
import vtk.util.numpy_support as vtk_np
import slicer

import ALPACA
alpacaLogic = ALPACA.ALPACALogic()

# ---------------------------------------------------------------------------
# 0. INPUTS -- edit these node names to match your scene
# ---------------------------------------------------------------------------
preAnnulusNode  = slicer.util.getNode('initial_to_final_annulus_rigid') # annulus of the local source model after local refined rigid registration
postAnnulusNode = slicer.util.getNode('final_surgery_annulus') # annulus of the target model
preFullNode     = slicer.util.getNode('initial_local_refined_by_annulus_registration') # full local source model after local refined rigid registration (annulus + surgical site) 

# ---------------------------------------------------------------------------
# 1. Parameters
#    - alpha/beta are CPD's regularization params (see ALPACA docs):
#         alpha = rigidity (lower -> larger deformations allowed)
#         beta  = motion coherence / kernel width (higher -> smoother,
#                 farther-reaching extrapolation -- important here so the
#                 surgical-site vertices, which are far from any real
#                 annulus correspondence, still get a coherent, non-collapsing
#                 displacement rather than fading to ~0 at the defect center)
#    - Start with beta noticeably higher than ALPACA's specimen-alignment
#      default (commonly ~2) and inspect the result; tune from there.
# ---------------------------------------------------------------------------
parameterDictionary = {
    "pointDensity": 1.0,
    "normalSearchRadius": 2.0,
    "FPFHNeighbors": 100,
    "FPFHSearchRadius": 5.0,
    "distanceThreshold": 3.0,
    "maxRANSAC": 1000000,
    "ICPDistanceThreshold": 1.5,
    "alpha": 2.0,
    "beta": 6.0,          # <-- bumped up from typical default; tune per result
    "CPDIterations": 100,
    "CPDTolerance": 0.001,
    "Acceleration": 0,    # 0 = pure-python cpd; 1 = BCPD binary (set BCPDFolder below)
    "BCPDFolder": "",
}

scalingOption = False   # already rigidly registered at true physical scale
usePoisson    = False   # switch to True if you prefer poisson-disk subsampling

# ---------------------------------------------------------------------------
# 2. Subsample the ANNULUS-ONLY clouds -- this is the fitting substrate for CPD.
#    Reusing ALPACA's own subsampling keeps voxel size / normal estimation
#    consistent with the rest of your pipeline. FPFH features are computed
#    as a side effect but unused here (they're only needed for RANSAC).
# ---------------------------------------------------------------------------
(sourceSLM, targetSLM, sourceFeatures, targetFeatures,
 voxelSize, scalingFactor) = alpacaLogic.runSubsample(
    preAnnulusNode, postAnnulusNode, scalingOption, parameterDictionary, usePoisson
)
print(f":: Annulus subsample -- source: {len(sourceSLM)} pts, target: {len(targetSLM)} pts")

# ---------------------------------------------------------------------------
# 3. Extract EVERY vertex of the full pre-surgical local patch
#    (annulus + surgical site together) in native point order.
#    This becomes the "sourceLM" query set that rides along inside CPD's
#    combined source cloud and gets predicted positions back.
# ---------------------------------------------------------------------------
prePolyData   = preFullNode.GetPolyData()
prePointsVTK  = prePolyData.GetPoints()
sourceLM      = vtk_np.vtk_to_numpy(prePointsVTK.GetData()).copy()  # (N, 3)
print(f":: Full pre-surgical patch: {sourceLM.shape[0]} vertices")

# ---------------------------------------------------------------------------
# 4. Run CPD. Internally this concatenates sourceLM onto the end of the
#    annulus-only source cloud, fits CPD once on the combined set against
#    the annulus-only target cloud, and returns predicted positions for
#    just the sourceLM rows (same order in -> same order out).
# ---------------------------------------------------------------------------
warpedFull = alpacaLogic.runCPDRegistration(
    sourceLM, sourceSLM, targetSLM, parameterDictionary
)
print(f":: CPD returned {warpedFull.shape[0]} warped points "
      f"(should equal {sourceLM.shape[0]})")
assert warpedFull.shape[0] == sourceLM.shape[0], "Row count mismatch -- check inputs"

# ---------------------------------------------------------------------------
# 5. Write the warped coordinates back into a cloned model node so you can
#    inspect it directly next to the post-surgical scan.
# ---------------------------------------------------------------------------
warpedPolyData = vtk.vtkPolyData()
warpedPolyData.DeepCopy(prePolyData)
warpedPointsVTK  = warpedPolyData.GetPoints()
warpedArrayVTK   = vtk_np.numpy_to_vtk(warpedFull, deep=True)
warpedPointsVTK.SetData(warpedArrayVTK)
warpedPolyData.Modified()

warpedModelNode = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLModelNode", "Pre_FullPatch_CPDWarped"
)
warpedModelNode.CreateDefaultDisplayNodes()
warpedModelNode.SetAndObservePolyData(warpedPolyData)
warpedModelNode.GetDisplayNode().SetColor(0, 1, 0)  # green, for easy visual ID

print(":: Done. 'Pre_FullPatch_CPDWarped' added to scene.")
print(":: Sanity checks worth doing next:")
print("   1. Visually compare the warped annulus portion against the real")
print("      post-surgical annulus -- they should now overlap closely.")
print("   2. Hold out a handful of annulus points from step 2's fitting call,")
print("      re-run, and check residuals at those held-out points to gauge")
print("      how much to trust the extrapolation into the surgical site.")
print("   3. Compare this CPD-warped surgical-site prediction against a")
print("      rigid-only version as a sensitivity check.")
