import adsk.core, adsk.fusion, traceback
import csv

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox("No active design found.")
            return

        export_data = []

        root = design.rootComponent
        root_name = root.name
        root_part_number = root.partNumber

        # --- GLOBAL USER PARAMETERS ---
        for p in design.userParameters:
            export_data.append({
                "Component Name": root_name,
                "Part Number": root_part_number,
                "ParameterType": "User",
                "FullName": f"{root_name}.{p.name}",
                "Name": p.name,
                "Value": p.value,
                "Unit": p.unit,
                "Expression": p.expression,
                "Configured": "No"
            })

        # --- COMPONENT MODEL PARAMETERS ---
        all_components = design.allComponents
        for comp in all_components:
            comp_name = comp.name
            part_number = comp.partNumber

            model_params = comp.modelParameters
            for mp in model_params:
                export_data.append({
                    "Component Name": comp_name,
                    "Part Number": part_number,
                    "ParameterType": "Model",
                    "FullName": f"{comp_name}.{mp.name}",
                    "Name": mp.name,
                    "Value": mp.value,
                    "Unit": mp.unit,
                    "Expression": mp.expression,
                    "Configured": "No"
                })

        # --- FILE SAVE DIALOG ---
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        fileDlg.title = "Save parameter CSV"
        fileDlg.filter = "CSV files (*.csv)"
        fileDlg.initialFilename = "component_parameters.csv"
        fileDlg.filterIndex = 0

        dlgResult = fileDlg.showSave()
        if dlgResult != adsk.core.DialogResults.DialogOK:
            return  # User cancelled

        file_path = fileDlg.filename

        # --- WRITE TO CSV FILE ---
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Component Name', 'Part Number', 'ParameterType', 'FullName', 'Name', 'Value', 'Unit', 'Expression', 'Configured']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in export_data:
                writer.writerow(row)

        ui.messageBox(f'Parameters successfully exported to:\n{file_path}')

    except Exception as e:
        if ui:
            ui.messageBox(f'Script error:\n{traceback.format_exc()}')

