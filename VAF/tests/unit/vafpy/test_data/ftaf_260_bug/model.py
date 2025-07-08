"""Definition of the CollisionDetection application module"""

import os
from datetime import timedelta

from silkit import Af

from vaf import BaseTypes, save_main_model, vafpy

# define the provided interface
object_detection = vafpy.datatypes.Struct(name="ObjectDetection", namespace="adas::interfaces")
object_detection.add_subelement(name="x", datatype=BaseTypes.UINT64_T)
object_detection.add_subelement(name="y", datatype=BaseTypes.UINT64_T)
object_detection.add_subelement(name="z", datatype=BaseTypes.UINT64_T)

od_list = vafpy.datatypes.Vector(name="ObjectDetectionList", namespace="adas::interfaces", datatype=object_detection)

od_list_if = vafpy.ModuleInterface(
    name="ObjectDetectionListInterface", namespace="nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist"
)
od_list_if.add_data_element(name="object_detection_list", datatype=od_list)

collision_detection = vafpy.ApplicationModule(
    name="CollisionDetection", namespace="NsApplicationUnit::NsCollisionDetection"
)
collision_detection.add_provided_interface(
    instance_name="BrakeServiceProvider", interface=Af.Adas_Demo_App.Services.brake_service
)
collision_detection.add_consumed_interface(instance_name="ObjectDetectionListModule", interface=od_list_if)
collision_detection.add_task(vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200), preferred_offset=0))

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_main_model(os.path.join(script_path, "model.json"))
