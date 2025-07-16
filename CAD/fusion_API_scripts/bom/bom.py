import adsk.core, adsk.fusion, traceback
import csv
from collections import defaultdict

EXPORT_NAME = 'custom_bom_export.csv'

DEFAULTS = {
    'Milestone': '',
    'Description': '',
    'Lifecycle': '',
    'Revision': '',
    'State': '',
    'Change Order': ''
}

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent

        # Dialog wyboru lokalizacji
        file_dialog = ui.createFileDialog()
        file_dialog.isMultiSelectEnabled = False
        file_dialog.title = 'Zapisz BOM jako...'
        file_dialog.filter = 'CSV files (*.csv)'
        file_dialog.initialFilename = EXPORT_NAME
        if file_dialog.showSave() != adsk.core.DialogResults.DialogOK:
            return
        export_path = file_dialog.filename

        # Zliczanie wystąpień komponentów po nazwie
        occurrence_counts = defaultdict(int)

        def count_occurrences(component):
            for occ in component.occurrences:
                comp = occ.component
                occurrence_counts[comp.name] += 1
                if not occ.isReferencedComponent:
                    count_occurrences(comp)

        count_occurrences(root)

        # Zbieranie danych BOM
        bom_data = []

        def extract(component, level):
            for occ in component.occurrences:
                comp = occ.component
                name = comp.name
                is_external = occ.isReferencedComponent

                bom_data.append({
                    'Level': level,
                    'Part Number': name,
                    'Part Name': name,
                    'External Component': is_external,
                    'Milestone': DEFAULTS['Milestone'],
                    'Description': DEFAULTS['Description'],
                    'Item Number': name,
                    'Lifecycle': DEFAULTS['Lifecycle'],
                    'Revision': DEFAULTS['Revision'],
                    'State': DEFAULTS['State'],
                    'Quantity': occurrence_counts[name],
                    'Material Name': comp.material.name if comp.material else '',
                    'Change Order': DEFAULTS['Change Order']
                })

                if not is_external:
                    extract(comp, level + 1)

        extract(root, 1)

        columns = [
            "Level", "Part Number", "Part Name", "External Component", "Milestone", "Description",
            "Item Number", "Lifecycle", "Revision", "State", "Quantity", "Material Name", "Change Order"
        ]

        with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for row in bom_data:
                writer.writerow(row)

        ui.messageBox(f'BOM exported successfully:\n{export_path}')

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
