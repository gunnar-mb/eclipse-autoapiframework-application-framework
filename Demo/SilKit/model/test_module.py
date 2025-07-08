from datetime import timedelta
from vaf import vafpy, BaseTypes

from .imported_models import *

test_module = vafpy.ApplicationModule(
    name="TestModule", namespace="NsApplicationUnit::NsTestModule"
)
test_module.add_consumed_interface(
    instance_name="BrakeServiceConsumer",
    interface=interfaces.Af.AdasDemoApp.Services.brake_service,
)
test_module.add_provided_interface(
    instance_name="ImageServiceProvider1",
    interface=interfaces.Af.AdasDemoApp.Services.image_service,
)
test_module.add_provided_interface(
    instance_name="ImageServiceProvider2",
    interface=interfaces.Af.AdasDemoApp.Services.image_service,
)
test_module.add_provided_interface(
    instance_name="SteeringAngleServiceProvider",
    interface=interfaces.Af.AdasDemoApp.Services.steering_angle_service,
)
test_module.add_provided_interface(
    instance_name="VelocityServiceProvider",
    interface=interfaces.Af.AdasDemoApp.Services.velocity_service,
)

test_module.add_task(
    task=vafpy.Task(name="BrakeTask", period=timedelta(milliseconds=100))
)
test_module.add_task(
    task=vafpy.Task(name="ImageTask", period=timedelta(milliseconds=100))
)
test_module.add_task(
    task=vafpy.Task(name="SteeringAngleTask", period=timedelta(milliseconds=1000))
)
test_module.add_task(
    task=vafpy.Task(name="VelocityTask", period=timedelta(milliseconds=1000))
)
