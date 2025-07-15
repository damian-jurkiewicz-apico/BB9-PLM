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

        all_components = design.allComponents
        export_data = []

        for comp in all_components:
            comp_name = comp.name

            # --- USER PARAMETERS ---
            user_params = design.userParameters
            for p in user_params:
                export_data.append({
                    "Component": comp_name,
                    "ParameterType": "User",
                    "FullName": f"{comp_name}.{p.name}",
                    "Name": p.name,
                    "Value": p.value,
                    "Unit": p.unit,
                    "Expression": p.expression,
                    "Configured": "No"
                })

            # --- MODEL PARAMETERS ---
            model_params = comp.modelParameters
            for mp in model_params:
                export_data.append({
                    "Component": comp_name,
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
        file_path = os.path.join(desktop_path, 'parameters_export.csv')

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Component', 'ParameterType', 'FullName', 'Name', 'Value', 'Unit', 'Expression', 'Configured']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in export_data:
                writer.writerow(row)

        ui.messageBox(f'Parametry wyeksportowane na pulpit:\n{file_path}')

    except Exception as e:
        if ui:
            ui.messageBox(f'Błąd skryptu:\n{traceback.format_exc()}')
