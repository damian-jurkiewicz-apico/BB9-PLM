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

        folder_path = os.path.expanduser("~/Desktop")
        os.makedirs(folder_path, exist_ok=True)
        output_file = os.path.join(folder_path, 'component_properties.csv')

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

            # Root component
            props = root.physicalProperties
            com = props.centerOfMass.asArray()
            inertia = props.getPrincipalMomentsOfInertia()
            material = root.material.name if root.material else "N/A"
            mat = root.material

            bbox = root.boundingBox
            size_x = bbox.maxPoint.x - bbox.minPoint.x
            size_y = bbox.maxPoint.y - bbox.minPoint.y
            size_z = bbox.maxPoint.z - bbox.minPoint.z

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
                root.name,
                "(root)",
                root.name,
                "(none)",
                root.description,
                root.partNumber,
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

            for occ in root.allOccurrences:
                props = occ.physicalProperties
                com = props.centerOfMass.asArray()
                inertia = props.getPrincipalMomentsOfInertia()
                comp = occ.component
                material = comp.material.name if comp.material else "N/A"
                mat = comp.material

                bbox = occ.boundingBox
                size_x = bbox.maxPoint.x - bbox.minPoint.x
                size_y = bbox.maxPoint.y - bbox.minPoint.y
                size_z = bbox.maxPoint.z - bbox.minPoint.z

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

                parent_name = root.name if occ.assemblyContext is None else occ.assemblyContext.component.name


                writer.writerow([
                    comp.partNumber,
                    comp.name,
                    occ.name,
                    occ.fullPathName,
                    parent_name,
                    comp.description,
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

        ui.messageBox(f'Export completed: {output_file}')
    except:
        if ui:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))
