from datetime import timedelta

from .application_modules import *
from vaf import *

# Create executable instances
executable = Executable("DemoExecutable", timedelta(milliseconds=10))

# Add application modules to executable instances
executable.add_application_module(
    VssProvider,
    [(Instances.VssProvider.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)],
)
executable.add_application_module(
    VssConsumer,
    [(Instances.VssConsumer.Tasks.PeriodicTask, timedelta(milliseconds=1), 1)],
)

# Connect the internal application module instances
executable.connect_interfaces(
    VssProvider,
    Instances.VssProvider.ProvidedInterfaces.AccelerationProvider,
    VssConsumer,
    Instances.VssConsumer.ConsumedInterfaces.AccelerationConsumer,
)
executable.connect_interfaces(
    VssProvider,
    Instances.VssProvider.ProvidedInterfaces.DriverProvider,
    VssConsumer,
    Instances.VssConsumer.ConsumedInterfaces.DriverConsumer,
)
