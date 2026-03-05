segA = slicer.util.getNode("1048_1")
segB = slicer.util.getNode("1048_nnunet")
outCsvPath = "/home/zhang/Downloads/1048_dice_results.csv"   # change as you like

# -------------------------
# Helpers
# -------------------------
def segmentNameToIdMap(segNode):
    seg = segNode.GetSegmentation()
    d = {}
    for i in range(seg.GetNumberOfSegments()):
        sid = seg.GetNthSegmentID(i)
        d[seg.GetSegment(sid).GetName()] = sid
    return d

# -------------------------
# Check SegmentComparison module/logic
# -------------------------
if not hasattr(slicer.modules, "segmentcomparison"):
    raise RuntimeError(
        "SegmentComparison module not found. In Slicer 5.10 this is typically provided by the SlicerRT extension."
    )
logic = slicer.modules.segmentcomparison.logic()

# Parameter node (reused)
paramNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentComparisonNode")
paramNode.SetAndObserveReferenceSegmentationNode(segA)
paramNode.SetAndObserveCompareSegmentationNode(segB)

# Match by name
mapA = segmentNameToIdMap(segA)
mapB = segmentNameToIdMap(segB)
commonNames = sorted(set(mapA) & set(mapB))
onlyA = sorted(set(mapA) - set(mapB))
onlyB = sorted(set(mapB) - set(mapA))

print(f"Matched segments: {len(commonNames)}")
if onlyA: print("Only in A:", onlyA)
if onlyB: print("Only in B:", onlyB)

# -------------------------
# Create output table
# -------------------------
tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "DiceResults")
table = tableNode.GetTable()
table.Initialize()  # clear any prior content

# In Slicer 5.10: create vtkStringArray, then AddColumn(array)
colName = vtk.vtkStringArray()
colName.SetName("Segment")
table.AddColumn(colName)

colDice = vtk.vtkDoubleArray()
colDice.SetName("Dice")
table.AddColumn(colDice)

# -------------------------
# Compute Dice for each matched segment
# -------------------------
for name in commonNames:
    paramNode.SetReferenceSegmentID(mapA[name])
    paramNode.SetCompareSegmentID(mapB[name])

    logic.ComputeDiceStatistics(paramNode)
    d = float(paramNode.GetDiceCoefficient())

    row = table.InsertNextBlankRow()
    table.SetValue(row, 0, name)
    table.SetValue(row, 1, d)

    print(f"{name:35s} Dice={d:.6f}")

# -------------------------
# Export to CSV
# -------------------------
slicer.util.saveNode(tableNode, outCsvPath)
print("Saved CSV to:", outCsvPath)
print("Done. Results table:", tableNode.GetName())
