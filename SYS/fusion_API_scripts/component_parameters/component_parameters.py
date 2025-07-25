
import adsk.core, adsk.fusion, traceback
import csv
import os

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox("Brak aktywnego modelu typu 'Design'.")
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

        # --- EXPORT TO DESKTOP ---
        desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')
        file_path = os.path.join(desktop_path, 'component_parameters.csv')

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Component Name', 'Part Number', 'ParameterType', 'FullName', 'Name', 'Value', 'Unit', 'Expression', 'Configured']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in export_data:
                writer.writerow(row)

        ui.messageBox(f'Parametry wyeksportowane na pulpit:\n{file_path}')

    except Exception as e:
        if ui:
            ui.messageBox(f'Błąd skryptu:\n{traceback.format_exc()}')
