# Demo based on input from the COVESA VSS catalogue

The following tutorial guides you through an example with the Vehicle Application Framework (VAF),
where derived interfaces from the [COVESA Vehicle Signal Specification (VSS)]
(https://covesa.global/project/vehicle-signal-specification/) are used as input to the workflow.

Plan in this demo is to develop one executable with two application modules that directly
communicate with each other. That means, they share an internal communication channel, which is
based on definitions from VSS. A high-level illustration of the setup is given below:

![vss](../figures/vss.drawio.svg)

Before starting, ensure that you have completed all [preparation
steps](../HelloVaf/README.md#prerequisites) as described in the `Hello, VAF!` demo.

## Project setup

First, enter the VAF workspace of your choice and create a new integration project and two
stand-alone application module projects using the VAF command line tool:

``` bash
vaf project init integration
Enter your project name: DemoExecutable
? Enter the directory to store your project in .

vaf project init app-module
Enter the name of the app-module: VssProvider
Enter the namespace of the app-module: demo
? Enter the path to the output root directory .

vaf project init app-module
Enter the name of the app-module: VssConsumer
Enter the namespace of the app-module: demo
? Enter the path to the output root directory .
```

## Configuration and implementation of app-modules

The following step applies for both application module projects alike. Switch folders and import the
VSS data catalogue to the project. The sample VSS catalogue is shipped as JSON file and already part
of the container. It is located in: `/opt/vaf/Demo/Vss/model/vss`
``` bash
cd VssProvider
vaf model import vss
Enter the path to the VSS catalogue file in JSON format /opt/vaf/Demo/Vss/model/vss/vss.json

cd ../VssConsumer
vaf model import vss
Enter the path to the VSS catalogue file in JSON format /opt/vaf/Demo/Vss/model/vss/vss.json
```

The command adds two new files the `model` sub-folder of the project. `vss-derived-model.json` is
the VAF model file in JSON format. It contains all relevant information as imported from the VSS
catalogue. `vss.py` is the Configuration as Code (CaC) support file, which is needed to access the
model artifacts from the configuration in Python.

Next step is the configuration of the app-modules in `VssProvider/model/vss_provider.py` and
`VssConsumer/model/vss_consumer.py` respectively.

To import the VSS interfaces from the previous step, write:
``` python
from .vss import *
```

The app-module configuration template already contains the app-module object and a default periodic
task. On top, the following interface configuration needs to be added for the example.

For the VssProvider use:
``` python
vss_provider.add_provided_interface("AccelerationProvider", interface=Vss.Vehicle.acceleration_if)
vss_provider.add_provided_interface("DriverProvider", interface=Vss.Vehicle.driver_if)
```

For the VssConsumer use:
``` python
vss_consumer.add_consumed_interface("AccelerationConsumer", interface=Vss.Vehicle.acceleration_if)
vss_consumer.add_consumed_interface("DriverConsumer", interface=Vss.Vehicle.driver_if)
```

Continue from here with model and code generation for each app-module project separately using the
following command:
``` bash
vaf project generate
```

Some sample code for VssProvider and VssConsumer app-modules is provided for reference in:
`/opt/vaf/Demo/Vss/src/vss_<consumer/provider>`. Feel free to use it as reference or simply copy the
snippets to the generated implementation stubs in `VssProvider/implementation/src/vss_provider.cpp`
and `VssConsumer/implementation/src/vss_consumer.cpp`.

Finally, check if the app-module libraries compile using:
``` bash
vaf make build
```

With this part completed for both, the VssProvider and the VssConsumer, the final integration on
executable-level can be started.

## Executable integration

Back in the integration project, next step is to create one executable with one instance of the
above-created app-modules each.

First of all, the stand-alone application module projects need to be imported to the scope of the
integration project. To do so, use the following commands:
``` bash
cd DemoExecutable
vaf project import
? Enter the path to the application module project to be imported: ../VssProvider

vaf project import
? Enter the path to the application module project to be imported: ../VssConsumer
```

The configuration of the executable in `DemoExecutable/model/vaf/demo_executable.py`, can now be
started as follows:
``` python
# Create executable instances
executable = Executable("DemoExecutable", timedelta(milliseconds=10))
```

Then, instantiating and mapping of app-modules follows:
``` python
# Add application modules to executable instances
executable.add_application_module(
    VssProvider,
    [(Instances.VssProvider.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)],
)
executable.add_application_module(
    VssConsumer,
    [(Instances.VssConsumer.Tasks.PeriodicTask, timedelta(milliseconds=1), 1)],
)
```

The second parameter, allows the definition of an integration-specific task mapping with execution
budget and order. In this example, the provider is configured to be executed before the consumer.

The two app-modules instances now can be connected as follows:
``` python
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
```

With this, the configuration part in the integration project is complete. Model and integration code
can be generated in one step using:
``` bash
vaf project generate
```

To complete the demo, finish with compile, link, and install step as follows:
``` bash
vaf make install
```

## Running the application
To start the just created binary, switch folders to
`DemoExecutable/build/Release/install/opt/DemoExecutable` and execute:
``` bash
./bin/DemoExecutable
```

Some output similar to the following should be printed to the terminal window.
``` bash
...
Longitudinal acceleration: 4.6 m/s^2
'Driver1' does not have the eyes on the road.
Longitudinal acceleration: 4.8 m/s^2
'Driver1' does not have the eyes on the road.
Longitudinal acceleration: 5 m/s^2
'Driver1' has the eyes on the road.
Longitudinal acceleration: 5.2 m/s^2
```
