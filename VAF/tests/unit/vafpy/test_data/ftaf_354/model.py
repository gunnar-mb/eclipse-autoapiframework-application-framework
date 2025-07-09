"""Definition of the CollisionDetection application module"""

import os
from datetime import timedelta

from silkit import Af

from vaf import BaseTypes, save_main_model, vafpy

# try to define Velocity (existing Velocity is datatypes::Velocity)
velocity = vafpy.datatypes.Struct(name="Velocity", namespace="MyInterface::Schmarrn")
velocity.add_subelement(name="Identifier", datatype=BaseTypes.INT16_T)
velocity.add_subelement(name="Velocity", datatype=BaseTypes.FLOAT)

# try to define UInt8Vector (existing UInt8Vector is datatypes::UInt8Vector)
vector = vafpy.datatypes.Vector(name="UInt8Vector", namespace="ThouInterface::Tiramisu", datatype=velocity)

# try to define VelocityService (existing VelocityService is datatypes::VelocityService)
vel_service = vafpy.ModuleInterface(name="VelocityService", namespace="FakeInterface::Salat")
vel_service.add_data_element(name="VelocityObj", datatype=vector)

# try to redefine datatypes::SteeringAngle
steering_angle = vafpy.datatypes.Struct(name="SteeringAngle", namespace="datatypes")
steering_angle.add_subelement(name="Identifier", datatype=BaseTypes.INT16_T)
steering_angle.add_subelement(name="SteeringAngle", datatype=BaseTypes.FLOAT)

# try to define datatypes::UInt8Vector
vector = vafpy.datatypes.Vector(name="UInt8Vector", namespace="datatypes", datatype=steering_angle)

fake_mod = vafpy.ApplicationModule(name="FakeAppModule", namespace="FakeNamespace")
fake_mod.add_provided_interface(instance_name="BrakeServiceProvider", interface=Af.Adas_Demo_App.Services.brake_service)
fake_mod.add_consumed_interface(instance_name="VelocityServiceProvider", interface=vel_service)
fake_mod.add_task(vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200), preferred_offset=0))


if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_main_model(os.path.join(script_path, "model.json"))
