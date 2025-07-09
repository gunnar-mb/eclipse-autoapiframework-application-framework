from datetime import timedelta
from vaf import vafpy, BaseTypes, vafmodel

# Import the CaC support from platform derive or interface import
from .imported_models import interfaces

schoca_cola = vafpy.ApplicationModule(
    name="SchocaCola", namespace="Soft::Drinks::Aint::Beer"
)

original = vafpy.ModuleInterface(
    name="OriginalCola", namespace="Soft::Drinks::Aint::Beer",
)
interfaces.Adas.Interfaces.object_detection.add_subelement("status", interfaces.Adas.Interfaces.object_detection_status)
interfaces.Adas.Interfaces.object_detection.add_subelement("YellowWorld", BaseTypes.FLOAT)
interfaces.Adas.Interfaces.object_detection.SubElements.append(vafmodel.SubElement(Name="Camelot", TypeRef=vafmodel.DataType(Name="ObjectDetectionMode", Namespace="adas::interfaces")))

original.add_data_element("BadGuysDetector", interfaces.Adas.Interfaces.object_detection)
schoca_cola.add_consumed_interface("OriginalCola", original)

# Add consumed and provided interfaces using the ApplicationModule API
schoca_cola.add_provided_interface("ColaZeerow", interfaces.Adas.Interfaces.object_detection_list_interface)


periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
schoca_cola.add_task(task=periodic_task)
