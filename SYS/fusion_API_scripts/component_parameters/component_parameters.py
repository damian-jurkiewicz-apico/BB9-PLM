
import adsk.core, adsk.fusion, traceback
import csv

def _safe_model_parameters(comp):
    """Zwraca listę parametrów modelu lub pustą listę, jeśli komponent nie jest parametryczny."""
    try:
        return list(comp.modelParameters)
    except RuntimeError:
        return []
    except:
        return []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            if ui:
                ui.messageBox("No active design found.")
            return

        export_data = []

        # Sprawdź typ projektu (Parametric vs Direct)
        is_parametric = design.designType == adsk.fusion.DesignTypes.ParametricDesignType

        if is_parametric:
            # --- Iterate over all components (includes root) ---
            for comp in design.allComponents:
                comp_name = comp.name
                # partNumber może być pusty na wielu komponentach
                part_number = getattr(comp, "partNumber", "")

                # --- Model Parameters ---
                for mp in _safe_model_parameters(comp):
                    # Czasem niektóre właściwości mogą rzucić wyjątek, więc zabezpieczamy odczyt
                    try:
                        name = mp.name
                    except:
                        name = ""
                    try:
                        value = mp.value
                    except:
                        value = ""
                    try:
                        unit = mp.unit
                    except:
                        unit = ""
                    try:
                        expression = mp.expression
                    except:
                        expression = ""

                    export_data.append({
                        "Component Name": comp_name,
                        "Part Number": part_number,
                        "ParameterType": "Model",
                        "FullName": f"{comp_name}.{name}",
                        "Name": name,
                        "Value": value,
                        "Unit": unit,
                        "Expression": expression,
                        "Configured": "No"
                    })

            # --- User Parameters (globalne) ---
            # W Direct Design nie istnieją – dlatego tylko gdy is_parametric == True
            root = design.rootComponent
            root_name = root.name
            root_part_number = getattr(root, "partNumber", "")

            for up in design.userParameters:
                try:
                    up_name = up.name
                except:
                    up_name = ""
                try:
                    up_value = up.value
                except:
                    up_value = ""
                try:
                    up_unit = up.unit
                except:
                    up_unit = ""
                try:
                    up_expression = up.expression
                except:
                    up_expression = ""

                export_data.append({
                    "Component Name": root_name,
                    "Part Number": root_part_number,
                    "ParameterType": "User",
                    "FullName": f"{root_name}.{up_name}",
                    "Name": up_name,
                    "Value": up_value,
                    "Unit": up_unit,
                    "Expression": up_expression,
                    "Configured": "No"
                })
        else:
            # Projekt Direct – nie ma parametrów, ale i tak pozwól zapisać pusty CSV z nagłówkiem
            if ui:
                ui.messageBox("Active design is Direct (non-parametric). No parameters to export.\nI'll still let you save an empty CSV.")

        # --- File save dialog ---
        if ui:
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

            ui.messageBox(f'Parameters successfully exported to:\\n{file_path}')

    except Exception as e:
        if ui:
            ui.messageBox(f'Script error:\\n{traceback.format_exc()}')
