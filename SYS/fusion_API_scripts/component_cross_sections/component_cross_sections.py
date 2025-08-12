import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct

        # Initialize CSV header
        result = (
            "Component Name,Part Number,Sketch,ProfileIndex,"
            "Area [cm²],CentroidX [cm],CentroidY [cm],"
            "Ixx [cm⁴],Iyy [cm⁴],Izz [cm⁴],"
            "Ixy [cm⁴],Iyz [cm⁴],Ixz [cm⁴]\n"
        )

        # Loop through all components and their sketches
        for comp in design.allComponents:
            part_number = comp.partNumber
            for sketch in comp.sketches:
                # Process only sketches starting with "BB9REQ"
                if not sketch.name.startswith("REQ"):
                    continue

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

                    result += (
                        f"{comp.name},{part_number},{sketch.name},{i},"
                        f"{area:.10e},{centroidX:.10e},{centroidY:.10e},"
                        f"{Ixx:.10e},{Iyy:.10e},{Izz:.10e},"
                        f"{Ixy:.10e},{Iyz:.10e},{Ixz:.10e}\n"
                    )

        # Show file save dialog
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        fileDlg.title = "Save CSV file"
        fileDlg.filter = "CSV files (*.csv)"
        fileDlg.initialFilename = "component_cross_sections.csv"
        fileDlg.filterIndex = 0

        dlgResult = fileDlg.showSave()
        if dlgResult != adsk.core.DialogResults.DialogOK:
            return  # User cancelled the dialog

        filename = fileDlg.filename

        # Write result to selected file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)

        ui.messageBox(f"CSV successfully saved:\n{filename}")

    except:
        if ui:
            ui.messageBox('Script failed:\n{}'.format(traceback.format_exc()))
