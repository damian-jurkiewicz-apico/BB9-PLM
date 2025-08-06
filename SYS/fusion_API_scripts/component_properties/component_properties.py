import adsk.core, adsk.fusion, traceback
import csv

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('A Fusion 360 design must be active.')
            return

        # --- File save dialog ---
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        fileDlg.title = "Save component properties CSV"
        fileDlg.filter = "CSV files (*.csv)"
        fileDlg.initialFilename = "component_properties.csv"
        fileDlg.filterIndex = 0

        dlgResult = fileDlg.showSave()
        if dlgResult != adsk.core.DialogResults.DialogOK:
            return  # User cancelled

        output_file = fileDlg.filename

        # --- Write CSV header ---
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Part Number', 'Component Name', 'Occurrence Name', 'Full Path', 'Parent Component',
                'Description', 'Material',
                'Mass [kg]', 'Volume [cm³]', 'Density [kg/cm³]', 'Surface Area [cm²]',
                'CoM X [cm]', 'CoM Y [cm]', 'CoM Z [cm]',
                'I1 [kg·cm²]', 'I2 [kg·cm²]', 'I3 [kg·cm²]',
                'Size X [cm]', 'Size Y [cm]', 'Size Z [cm]',
                'Young\'s Modulus [Pa]', 'Poisson\'s Ratio', 'Shear Modulus [Pa]',
                'Thermal Conductivity [W/m·K]', 'Thermal Expansion [1/K]'
            ])

            # --- Iterate through all components (includes root) ---
            for comp in design.allComponents:
                part_number = comp.partNumber
                comp_name = comp.name
                description = comp.description
                material = comp.material.name if comp.material else "N/A"
                mat = comp.material

                # Try to find a physical instance (occurrence) of this component
                occ = None
                for o in comp.occurrences:
                    occ = o
                    break

                if occ:
                    props = occ.physicalProperties
                    com = props.centerOfMass.asArray()
                    inertia = props.getPrincipalMomentsOfInertia()
                    bbox = occ.boundingBox
                    parent_name = occ.assemblyContext.component.name if occ.assemblyContext else "(none)"
                    occ_name = occ.name
                    full_path = occ.fullPathName
                else:
                    props = comp.physicalProperties
                    com = props.centerOfMass.asArray()
                    inertia = props.getPrincipalMomentsOfInertia()
                    bbox = comp.boundingBox
                    parent_name = "(none)"
                    occ_name = "(root)" if comp == design.rootComponent else "(standalone)"
                    full_path = comp.name

                size_x = bbox.maxPoint.x - bbox.minPoint.x
                size_y = bbox.maxPoint.y - bbox.minPoint.y
                size_z = bbox.maxPoint.z - bbox.minPoint.z

                # Material properties
                young_modulus = poisson_ratio = shear_modulus = thermal_cond = thermal_exp = "N/A"
                try:
                    if mat and mat.physicalProperties:
                        mp = mat.physicalProperties
                        if mp.youngsModulus:
                            young_modulus = mp.youngsModulus.value
                        if mp.poissonsRatio:
                            poisson_ratio = mp.poissonsRatio
                        if mp.shearModulus:
                            shear_modulus = mp.shearModulus.value
                        if mp.thermalConductivity:
                            thermal_cond = mp.thermalConductivity.value
                        if mp.thermalExpansionCoefficient:
                            thermal_exp = mp.thermalExpansionCoefficient.value
                except:
                    pass

                writer.writerow([
                    part_number,
                    comp_name,
                    occ_name,
                    full_path,
                    parent_name,
                    description,
                    material,
                    round(props.mass, 6),
                    round(props.volume, 6),
                    round(props.density, 6),
                    round(props.area, 6),
                    round(com[0], 6),
                    round(com[1], 6),
                    round(com[2], 6),
                    round(inertia[0], 6),
                    round(inertia[1], 6),
                    round(inertia[2], 6),
                    round(size_x, 6),
                    round(size_y, 6),
                    round(size_z, 6),
                    young_modulus,
                    poisson_ratio,
                    shear_modulus,
                    thermal_cond,
                    thermal_exp
                ])

        ui.messageBox(f'Export completed:\n{output_file}')

    except:
        if ui:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))
