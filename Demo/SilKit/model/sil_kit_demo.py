from datetime import timedelta

from .application_modules import TestModule, SensorFusion, Instances, CollisionDetection
from vaf import *

# Create executable instances (or configure existing ones from the platform configuration)
executable = Executable("AdasDemoExecutable", timedelta(milliseconds=20))
tester = Executable("AdasDemoTester", timedelta(milliseconds=20))

# Add application modules to executable instances
b_10ms = timedelta(milliseconds=10)
executable.add_application_module(
    SensorFusion,
    [
        (Instances.SensorFusion.Tasks.Step1, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step2, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step3, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step4, b_10ms, 0),
    ],
)
executable.add_application_module(
    CollisionDetection,
    [(Instances.CollisionDetection.Tasks.PeriodicTask, timedelta(milliseconds=1), 1)],
)

tester.add_application_module(
    TestModule,
    [
        (Instances.TestModule.Tasks.BrakeTask, b_10ms, 0),
        (Instances.TestModule.Tasks.ImageTask, b_10ms, 0),
        (Instances.TestModule.Tasks.SteeringAngleTask, b_10ms, 0),
        (Instances.TestModule.Tasks.VelocityTask, b_10ms, 0),
    ],
)

# Connect the application module instances internally
executable.connect_interfaces(
    SensorFusion,
    Instances.SensorFusion.ProvidedInterfaces.ObjectDetectionListModule,
    CollisionDetection,
    Instances.CollisionDetection.ConsumedInterfaces.ObjectDetectionListModule,
)

# Connect the application module instances with middleware
executable.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.ImageServiceConsumer1,
    "Silkit_ImageService1",
)
executable.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.ImageServiceConsumer2,
    "Silkit_ImageService2",
)
executable.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.SteeringAngleServiceConsumer,
    "Silkit_SteeringAngleService",
)
executable.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.VelocityServiceConsumer,
    "Silkit_VelocityService",
)

executable.connect_provided_interface_to_silkit(
    CollisionDetection,
    Instances.CollisionDetection.ProvidedInterfaces.BrakeServiceProvider,
    "Silkit_BrakeService",
)

tester.connect_consumed_interface_to_silkit(
    TestModule,
    Instances.TestModule.ConsumedInterfaces.BrakeServiceConsumer,
    "Silkit_BrakeService",
)
tester.connect_provided_interface_to_silkit(
    TestModule,
    Instances.TestModule.ProvidedInterfaces.ImageServiceProvider1,
    "Silkit_ImageService1",
)
tester.connect_provided_interface_to_silkit(
    TestModule,
    Instances.TestModule.ProvidedInterfaces.ImageServiceProvider2,
    "Silkit_ImageService2",
)
tester.connect_provided_interface_to_silkit(
    TestModule,
    Instances.TestModule.ProvidedInterfaces.SteeringAngleServiceProvider,
    "Silkit_SteeringAngleService",
)
tester.connect_provided_interface_to_silkit(
    TestModule,
    Instances.TestModule.ProvidedInterfaces.VelocityServiceProvider,
    "Silkit_VelocityService",
)
