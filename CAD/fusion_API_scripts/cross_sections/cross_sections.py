import adsk.core, adsk.fusion, traceback
import os

def run(context):

    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct

        result = (
    "Component Name,Sketch,ProfileIndex,"
    "Area [cm²],CentroidX [cm],CentroidY [cm],"
    "Ixx [cm⁴],Iyy [cm⁴],Izz [cm⁴],"
    "Ixy [cm⁴],Iyz [cm⁴],Ixz [cm⁴]\n"
)


        for comp in design.allComponents:
            for sketch in comp.sketches:
                if not sketch.name.startswith("req"):
                    continue

                for i, profile in enumerate(sketch.profiles):
                    props = profile.areaProperties()
                    moments = props.getMomentsOfInertia()

                    area = props.area
                    centroidX = props.centroid.x
                    centroidY = props.centroid.y

                    Ixx = moments[1]
                    Iyy = moments[2]
                    Izz = moments[3]
                    Ixy = moments[4]
                    Iyz = moments[5]
                    Ixz = moments[6]

                    result += (
                        f"{comp.name},{sketch.name},{i},"
                        f"{area:.10e},{centroidX:.10e},{centroidY:.10e},"
                        f"{Ixx:.10e},{Iyy:.10e},{Izz:.10e},{Ixy:.10e},{Iyz:.10e},{Ixz:.10e}\n"
                    )

        desktop_path = os.path.expanduser("~/Desktop")
        filename = os.path.join(desktop_path, "cross_sections.csv")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)

        ui.messageBox(f"CSV Saved:\n{filename}")


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
