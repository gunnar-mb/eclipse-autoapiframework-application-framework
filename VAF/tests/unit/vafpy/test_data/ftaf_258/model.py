"""Definition of the CollisionDetection application module"""

import os
from datetime import timedelta

from silkit import AdasDemoApp, Af

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

fake_if = vafpy.ModuleInterface(
    name="FakeObjectInterface", namespace="nsapplicationunit::nsmoduleinterface::nsfakeobject"
)
fake_if.add_data_element(name="v", datatype=od_list)
fake_if.add_data_element(name="r", datatype=BaseTypes.FLOAT)

metoo_if = vafpy.ModuleInterface(name="MeTooInterface", namespace="nsapplicationunit::nsmoduleinterface::nsmetoo")
metoo_if.add_data_element(name="a", datatype=BaseTypes.UINT16_T)
metoo_if.add_data_element(name="z", datatype=BaseTypes.FLOAT)

p_200ms = timedelta(milliseconds=200)

cd_mod = vafpy.ApplicationModule(name="CollisionDetection", namespace="NsApplicationUnit::NsCollisionDetection")
cd_mod.add_provided_interface(instance_name="BrakeServiceProvider", interface=Af.Adas_Demo_App.Services.brake_service)
cd_mod.add_provided_interface(instance_name="ImageServiceProvider1", interface=Af.Adas_Demo_App.Services.image_service)
cd_mod.add_consumed_interface(instance_name="ObjectDetectionListModule", interface=od_list_if)
cd_mod.add_task(vafpy.Task(name="PeriodicTask", period=p_200ms, preferred_offset=0))

sf_mod = vafpy.ApplicationModule(name="SensorFusion", namespace="NsApplicationUnit::NsSensorFusion")
sf_mod.add_provided_interface(instance_name="ObjectDetectionListModule", interface=od_list_if)
sf_mod.add_consumed_interface(instance_name="ImageServiceConsumer1", interface=Af.Adas_Demo_App.Services.image_service)
sf_mod.add_consumed_interface(instance_name="ImageServiceConsumer2", interface=Af.Adas_Demo_App.Services.image_service)
sf_mod.add_consumed_interface(
    instance_name="SteeringAngleServiceConsumer", interface=Af.Adas_Demo_App.Services.steering_angle_service
)
sf_mod.add_consumed_interface(
    instance_name="VelocityServiceConsumer", interface=Af.Adas_Demo_App.Services.velocity_service
)

task1 = vafpy.Task(name="Step1", period=p_200ms, preferred_offset=0)
task2 = vafpy.Task(name="Step2", period=p_200ms, preferred_offset=0)
task3 = vafpy.Task(name="Step3", period=p_200ms, preferred_offset=0)
task4 = vafpy.Task(name="Step4", period=p_200ms, preferred_offset=0, run_after=[task3])

sf_mod.add_task(task=task1)
sf_mod.add_task_chain(tasks=[task2, task3], run_after=[task1])
sf_mod.add_task(task=task4)


# add application modules
p_10ms = timedelta(milliseconds=10)
AdasDemoApp.executable.add_application_module(
    sf_mod,
    [
        ("Step1", p_10ms, 0),
        ("Step2", p_10ms, 0),
        ("Step3", p_10ms, 0),
        ("Step4", p_10ms, 0),
    ],
)
AdasDemoApp.executable.add_application_module(cd_mod, [("PeriodicTask", timedelta(milliseconds=1), 1)])

# connect intra process interfaces
AdasDemoApp.executable.connect_interfaces(sf_mod, "ObjectDetectionListModule", cd_mod, "ObjectDetectionListModule")


if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_main_model(os.path.join(script_path, "model.json"))
