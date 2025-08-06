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

        # --- Iterate over all components (includes root) ---
        for comp in design.allComponents:
            comp_name = comp.name
            part_number = comp.partNumber

            # --- Model Parameters ---
            for mp in comp.modelParameters:
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

        # --- User Parameters (only exist globally, assign to root) ---
        root = design.rootComponent
        root_name = root.name
        root_part_number = root.partNumber

        for up in design.userParameters:
            export_data.append({
                "Component Name": root_name,
                "Part Number": root_part_number,
                "ParameterType": "User",
                "FullName": f"{root_name}.{up.name}",
                "Name": up.name,
                "Value": up.value,
                "Unit": up.unit,
                "Expression": up.expression,
                "Configured": "No"
            })

        # --- File save dialog ---
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

        # --- Write to CSV ---
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
