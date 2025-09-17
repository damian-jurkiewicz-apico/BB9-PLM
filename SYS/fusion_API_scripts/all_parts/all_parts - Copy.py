import adsk.core, adsk.fusion, traceback
import csv

def compute_component_dims_cm(comp: adsk.fusion.Component, units_mgr: adsk.core.UnitsManager):
    """
    Compute axis-aligned bounding box dimensions from the component's definition
    (comp.bRepBodies), so orientation in the assembly doesn't affect the size.
    Returns (dim_x_cm, dim_y_cm, dim_z_cm).
    """
    try:
        bodies = comp.bRepBodies
        if bodies.count == 0:
            return 0.0, 0.0, 0.0

        # Union all body bounding boxes (in internal units)
        min_x = min_y = min_z =  1e99
        max_x = max_y = max_z = -1e99

        for body in bodies:
            bb = body.boundingBox
            if bb is None:
                continue
            min_x = min(min_x, bb.minPoint.x); max_x = max(max_x, bb.maxPoint.x)
            min_y = min(min_y, bb.minPoint.y); max_y = max(max_y, bb.maxPoint.y)
            min_z = min(min_z, bb.minPoint.z); max_z = max(max_z, bb.maxPoint.z)

        # Convert to centimeters using the units manager
        iu = units_mgr.internalUnits
        dim_x_cm = units_mgr.convert(max_x - min_x, iu, "cm")
        dim_y_cm = units_mgr.convert(max_y - min_y, iu, "cm")
        dim_z_cm = units_mgr.convert(max_z - min_z, iu, "cm")
        return dim_x_cm, dim_y_cm, dim_z_cm
    except:
        return 0.0, 0.0, 0.0

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('A Fusion 360 design must be active.')
            return

        root = design.rootComponent
        units_mgr = design.unitsManager

        # File save dialog
        fileDlg = ui.createFileDialog()
        fileDlg.title = "Save detailed BOM CSV (occurrences, dims from component definition)"
        fileDlg.filter = "CSV files (*.csv)"
        fileDlg.initialFilename = "all_parts.csv"
        fileDlg.isMultiSelectEnabled = False

        if fileDlg.showSave() != adsk.core.DialogResults.DialogOK:
            return

        file_path = fileDlg.filename

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Part Number', 'Description',
                'Mass [kg]', 'Dim X [cm]', 'Dim Y [cm]', 'Dim Z [cm]',
                'Occurrence Name', 'Full Path'
            ])

            for occ in root.allOccurrences:
                comp = occ.component
                part_number = comp.partNumber or "(no number)"
                description = comp.description or ""

                # Mass & properties from the occurrence (correct for that instance)
                props = occ.physicalProperties

                # Dimensions from the component definition (orientation-independent)
                dim_x_cm, dim_y_cm, dim_z_cm = compute_component_dims_cm(comp, units_mgr)

                writer.writerow([
                    part_number,
                    description,
                    round(props.mass, 4),
                    round(dim_x_cm, 2),
                    round(dim_y_cm, 2),
                    round(dim_z_cm, 2),
                    occ.name,
                    occ.fullPathName
                ])

        ui.messageBox(f'Detailed BOM export completed:\n{file_path}')

    except:
        if ui:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))