import adsk.core, adsk.fusion, traceback

def _curve_length_cm_from_sketchcurve(sk_curve: adsk.fusion.SketchCurve, units_mgr: adsk.core.UnitsManager) -> float:
    """Return full length of a sketch curve in centimeters using its 2D geometry evaluator."""
    try:
        geo = sk_curve.geometry  # Curve2D
        if not geo:
            return 0.0
        ev = geo.evaluator
        ok1, tmin, tmax = ev.getParameterExtents()
        if not ok1:
            return 0.0
        ok2, length = ev.getLengthAtParameter(tmin, tmax)
        if not ok2:
            return 0.0
        # Fusion internal sketch lengths are already in cm (sketch plane 2D space).
        return length
    except:
        return 0.0

def _sketch_unique_perimeter_cm(sketch: adsk.fusion.Sketch, units_mgr: adsk.core.UnitsManager) -> float:
    """
    Compute unique perimeter of a sketch by summing each underlying SketchCurve used by any profile
    exactly once. This avoids double counting the same edge across multiple Profile regions.
    """
    seen_tokens = set()
    total = 0.0
    try:
        # Traverse all profiles and collect the underlying sketch curves they use
        for prof in sketch.profiles:
            for loop in prof.profileLoops:
                for pcurve in loop.profileCurves:
                    # ProfileCurve.sketchEntity references the underlying SketchEntity (line/arc/spline)
                    sk_ent = pcurve.sketchEntity
                    sk_curve = adsk.fusion.SketchCurve.cast(sk_ent) if sk_ent else None
                    if not sk_curve:
                        continue
                    token = sk_curve.entityToken
                    if token in seen_tokens:
                        continue
                    seen_tokens.add(token)
                    total += _curve_length_cm_from_sketchcurve(sk_curve, units_mgr)
    except:
        pass
    return total

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        if not design:
            ui.messageBox("No active design found.")
            return

        units_mgr = adsk.fusion.Design.cast(design).unitsManager

        # CSV header: replace previous Perimeter with Sketch-level unique perimeter
        result = (
            "Component Name,Part Number,Sketch,ProfileIndex,"
            "Area [cm²],CentroidX [cm],CentroidY [cm],"
            "Ixx [cm⁴],Iyy [cm⁴],Izz [cm⁴],"
            "Ixy [cm⁴],Iyz [cm⁴],Ixz [cm⁴],"
            "Sketch Perimeter [cm]\n"
        )

        for comp in design.allComponents:
            part_number = comp.partNumber
            for sketch in comp.sketches:
                # Use your naming rule here; adjust as needed
                if not sketch.name.startswith("REQ"):
                    continue

                # Compute unique perimeter ONCE per sketch
                sketch_perim = _sketch_unique_perimeter_cm(sketch, units_mgr)
                wrote_perimeter_for_this_sketch = False

                for i, profile in enumerate(sketch.profiles):
                    props = profile.areaProperties()
                    moments = props.getMomentsOfInertia()

                    area = props.area
                    centroidX = props.centroid.x
                    centroidY = props.centroid.y

                    Ixx = moments[1]
                    Iyy = moments[2]
                    Izz = moments[3]
                    Ixy = moments[4]
                    Iyz = moments[5]
                    Ixz = moments[6]

                    # Put the sketch perimeter only on the first row for this sketch
                    perim_cell = f"{sketch_perim:.10e}" if not wrote_perimeter_for_this_sketch else ""
                    if not wrote_perimeter_for_this_sketch:
                        wrote_perimeter_for_this_sketch = True

                    result += (
                        f"{comp.name},{part_number},{sketch.name},{i},"
                        f"{area:.10e},{centroidX:.10e},{centroidY:.10e},"
                        f"{Ixx:.10e},{Iyy:.10e},{Izz:.10e},"
                        f"{Ixy:.10e},{Iyz:.10e},{Ixz:.10e},"
                        f"{perim_cell}\n"
                    )

        # Save dialog
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        fileDlg.title = "Save CSV file"
        fileDlg.filter = "CSV files (*.csv)"
        fileDlg.initialFilename = "component_cross_sections.csv"
        fileDlg.filterIndex = 0

        if fileDlg.showSave() != adsk.core.DialogResults.DialogOK:
            return

        filename = fileDlg.filename
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)

        ui.messageBox(f"CSV successfully saved:\n{filename}")

    except:
        if ui:
            ui.messageBox('Script failed:\n{}'.format(traceback.format_exc()))
