import adsk.core, adsk.fusion, traceback
import csv
import os

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

        # Przygotuj ścieżkę do zapisu CSV
        folder_path = os.path.expanduser("~/Desktop")
        os.makedirs(folder_path, exist_ok=True)
        output_file = os.path.join(folder_path, 'export_full_physical_mechanical_properties.csv')

        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Component Name', 'Occurrence Name', 'Full Path',
                'Description', 'Part Number', 'Material',
                'Mass [kg]', 'Volume [cm³]', 'Density [kg/m³]', 'Surface Area [cm²]',
                'CoM X [cm]', 'CoM Y [cm]', 'CoM Z [cm]',
                'I1 [kg·cm²]', 'I2 [kg·cm²]', 'I3 [kg·cm²]',
                'Size X [cm]', 'Size Y [cm]', 'Size Z [cm]',
                'Young\'s Modulus [Pa]', 'Poisson\'s Ratio', 'Shear Modulus [Pa]',
                'Thermal Conductivity [W/m·K]', 'Thermal Expansion [1/K]'
            ])

            for occ in root.allOccurrences:
                props = occ.physicalProperties
                com = props.centerOfMass.asArray()
                inertia = props.getPrincipalMomentsOfInertia()

                # Informacje komponentu
                comp = occ.component
                material = comp.material.name if comp.material else "N/A"
                mat = comp.material

                # Bounding box rozmiary
                bbox = occ.boundingBox
                size_x = (bbox.maxPoint.x - bbox.minPoint.x)
                size_y = (bbox.maxPoint.y - bbox.minPoint.y)
                size_z = (bbox.maxPoint.z - bbox.minPoint.z)

                # Domyślne wartości
                young_modulus = poisson_ratio = shear_modulus = thermal_cond = thermal_exp = "N/A"

                try:
                    if mat and mat.physicalProperties:
                        mp = mat.physicalProperties
                        if mp.youngsModulus:  # Pa
                            young_modulus = round(mp.youngsModulus.value, 2)  
                        if mp.poissonsRatio:
                            poisson_ratio = round(mp.poissonsRatio, 3)
                        if mp.shearModulus:
                            shear_modulus = round(mp.shearModulus.value, 2)  
                        if mp.thermalConductivity:
                            thermal_cond = round(mp.thermalConductivity.value, 2)
                        if mp.thermalExpansionCoefficient:
                            thermal_exp = round(mp.thermalExpansionCoefficient.value, 8)
                except:
                    pass  # zachowaj "N/A" w razie błędu

                writer.writerow([
                    comp.name,
                    occ.name,
                    occ.fullPathName,
                    comp.description,
                    comp.partNumber,
                    material,
                    round(props.mass, 4),
                    round(props.volume, 2),
                    round(props.density, 2),
                    round(props.area, 2),
                    round(com[0], 2),
                    round(com[1], 2),
                    round(com[2], 2),
                    round(inertia[0], 2),
                    round(inertia[1], 2),
                    round(inertia[2], 2),
                    round(size_x, 2),
                    round(size_y, 2),
                    round(size_z, 2),
                    young_modulus,
                    poisson_ratio,
                    shear_modulus,
                    thermal_cond,
                    thermal_exp
                ])

        ui.messageBox(f'Export zakończony: {output_file}')

    except:
        if ui:
            ui.messageBox('Błąd:\n{}'.format(traceback.format_exc()))
