# ADAS demo using SIL Kit

This example is inspired by an ADAS application and illustrates the workflow when using the Vehicle
Application Framework (VAF) with SIL Kit. The tutorial illustrates, how development of a distributed
application can be done, even if the middleware of the later target system is not known yet. In
other words, platform-specific design artifacts are not needed. Instead, modeling and configuration
is all done in the VAF. An appropriate platform abstraction for SIL Kit is automatically generated,
which facilitates rapid prototyping, quick development, and system-level testing. Still, the
migration path to other lower layer solutions is open as just another platform abstraction can be
attached in replacement for the SIL Kit one.

The example starts with the creation of an architecture for the ADAS application in a modular way
using application modules. The ADAS application executable of this demo consists of two application
modules: (1) collision detection, and (2) sensor fusion. The collision detection receives the object
detection list from the sensor fusion application module. The sensor fusion module consumes camera
input (ImageService) (left/right), velocity service, and a steering angle service. From this
information, it computes the object list and sends it to the collision detection application module.
The collision detection module then commands the brake accordingly.

![silkit](../figures/silkit.drawio.svg)

For the architecture, the following interfaces are completely defined in the Configuration as Code
(CaC) environment of the VAF:

| Service: ImageService     |
| ------------------------- |
| DataElement: camera_image |
| Operation: GetImageSize   |

| Service: ObjectDetectionList       |
| ---------------------------------- |
| DataElement: object_detection_list |

| Service: BrakeService     |
| ------------------------- |
| DataElement: brake_action |
| Operation: SumTwoSummands |

| Service: SteeringAngleService |
| ----------------------------- |
| DataElement: steering_angle   |

| Service: VelocityService  |
| ------------------------- |
| DataElement: car_velocity |

Before starting, ensure that you have completed all [preparation
steps](../HelloVaf/README.md#prerequisites) as described in the `Hello, VAF!` demo.

## Definition of datatypes and interfaces

The first step is to define the interfaces as described above for further use in the application
module projects for collision detection and sensor fusion. For that purpose, an interface project is
used.  To get started, create a project using the VAF command line tool and switch folders to the
just created project directory:

``` bash
vaf project init interface
Enter the name of the project: Interfaces
? Enter the directory to store your project in .

cd Interfaces
```
Next step is the interface definition part. For that, open the template file `interfaces.py` within
the newly created interface project and add the following datatype and interface definitions:

``` python
# Brake Service
brake_pressure = vafpy.datatypes.Struct(name="BrakePressure", namespace="datatypes")
brake_pressure.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
brake_pressure.add_subelement(name="value", datatype=BaseTypes.UINT8_T)

brake_service = vafpy.ModuleInterface(
    name="BrakeService", namespace="af::adas_demo_app::services"
)
brake_service.add_data_element(name="brake_action", datatype=brake_pressure)
brake_service.add_operation(
    name="SumTwoSummands",
    in_parameter={"summand_one": BaseTypes.UINT16_T, "summand_two": BaseTypes.UINT16_T},
    out_parameter={"sum": BaseTypes.UINT16_T},
)

# Object Detection List
od_struct = vafpy.datatypes.Struct(name="ObjectDetection", namespace="adas::interfaces")
od_struct.add_subelement(name="x", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="y", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="z", datatype=BaseTypes.UINT64_T)

od_list = vafpy.datatypes.Vector(
    name="ObjectDetectionList",
    namespace="adas::interfaces",
    datatype=od_struct,
)

od_interface = vafpy.ModuleInterface(
    name="ObjectDetectionListInterface",
    namespace="nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist",
)
od_interface.add_data_element(name="object_detection_list", datatype=od_list)

# ImageService
uint8_vector = vafpy.datatypes.Vector(
    name="UInt8Vector", namespace="datatypes", datatype=BaseTypes.UINT8_T
)

image = vafpy.datatypes.Struct(name="Image", namespace="datatypes")
image.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
image.add_subelement(name="height", datatype=BaseTypes.UINT16_T)
image.add_subelement(name="width", datatype=BaseTypes.UINT16_T)
image.add_subelement(name="R", datatype=uint8_vector)
image.add_subelement(name="G", datatype=uint8_vector)
image.add_subelement(name="B", datatype=uint8_vector)

image_service = vafpy.ModuleInterface(
    name="ImageService", namespace="af::adas_demo_app::services"
)
image_service.add_data_element(name="camera_image", datatype=image)
image_service.add_operation(
    name="GetImageSize",
    out_parameter={"width": BaseTypes.UINT16_T, "height": BaseTypes.UINT16_T},
)

# VelocityService
velocity = vafpy.datatypes.Struct(name="Velocity", namespace="datatypes")
velocity.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
velocity.add_subelement(name="value", datatype=BaseTypes.UINT16_T)

velocity_service = vafpy.ModuleInterface(
    name="VelocityService", namespace="af::adas_demo_app::services"
)
velocity_service.add_data_element(name="car_velocity", datatype=velocity)

# Steering Angle
steering_angle = vafpy.datatypes.Struct(name="SteeringAngle", namespace="datatypes")
steering_angle.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
steering_angle.add_subelement(name="value", datatype=BaseTypes.UINT16_T)

steering_angle_service = vafpy.ModuleInterface(
    name="SteeringAngleService", namespace="af::adas_demo_app::services"
)
steering_angle_service.add_data_element(name="steering_angle", datatype=steering_angle)
```

Once complete, the configuration needs to be exported to JSON by using the following command:

``` bash
vaf model generate
```

The exported JSON file gets stored to the subdirectory `./export` by default, along with its CaC
support file for later use in an application module project.

## Configuration and implementation of app-modules

Application modules are self-contained. That means, the corresponding VAF app-module project allows
to configure, implement, test, and maintain each module stand-alone and thus separate from the later
integration step. This brings flexibility in terms of project organization and further allows to use
app-modules in different integration projects.

For the ADAS executable in this example, two application modules are needed. One for sensor fusion
and one for the collision detection part.

### Sensor fusion application module

Switch folders to the workspace directory and create a new app-module project for sensor fusion as
follows:

``` bash
vaf project init app-module
Enter the name of the app-module: SensorFusion
Enter the namespace of the app-module: NsApplicationUnit::NsSensorFusion
? Enter the path to the output root directory .

cd SensorFusion
```

In first place, the above-created data exchange file from the interface project needs to be imported
to make the model elements from there accessible in the app-module project. Use the following
command for that:

```bash
vaf project import
? Please provide the path to the exported VAF model JSON file ../Interfaces/export/Interfaces.json
```

Next step is the configuration of the application module. For that, open the file
`SensorFusion/model/sensor_fusion.py`. To complete the import from the interface project, uncomment
the following line:

``` python
from .imported_models import *
```

The configuration of the application module is done completely in this Configuration as Code file.
According to the illustration above, SensorFusion is supposed to consume the left/right camera
ImageService and therefore needs a corresponding consumer interface. Likewise, consumer interfaces
for the SteeringAngleService and VelocityService are required. For communication with
collision_detection it acts as provider of the earlier defined ObjectDetectionListInterface.

``` python
sensor_fusion = vafpy.ApplicationModule(
    name="SensorFusion", namespace="NsApplicationUnit::NsSensorFusion"
)
sensor_fusion.add_provided_interface(
    "ObjectDetectionListModule",
    interfaces.Nsapplicationunit.Nsmoduleinterface.Nsobjectdetectionlist.object_detection_list_interface,
)
sensor_fusion.add_consumed_interface(
    "ImageServiceConsumer1", interfaces.Af.AdasDemoApp.Services.image_service
)
sensor_fusion.add_consumed_interface(
    "ImageServiceConsumer2", interfaces.Af.AdasDemoApp.Services.image_service
)
sensor_fusion.add_consumed_interface(
    "SteeringAngleServiceConsumer",
    interfaces.Af.AdasDemoApp.Services.steering_angle_service,
)
sensor_fusion.add_consumed_interface(
    "VelocityServiceConsumer", interfaces.Af.AdasDemoApp.Services.velocity_service
)

p_200ms = timedelta(milliseconds=200)
step1 = vafpy.Task(name="Step1", period=p_200ms, preferred_offset=0)
step2 = vafpy.Task(name="Step2", period=p_200ms, preferred_offset=0)
step3 = vafpy.Task(name="Step3", period=p_200ms, preferred_offset=0)

sensor_fusion.add_task(task=step1)
sensor_fusion.add_task_chain(tasks=[step2, step3], run_after=[step1])
sensor_fusion.add_task(
    vafpy.Task(name="Step4", period=p_200ms, preferred_offset=0, run_after=[step1])
)
```

### Collision detection application module

The same workflow can now be applied to prepare the collision detection application module. Start
again from the level of the workspace directory.

``` bash
vaf project init app-module
Enter the name of the app-module: CollisionDetection
Enter the namespace of the app-module: NsApplicationUnit::NsCollisionDetection
? Enter the path to the output root directory .

cd CollisionDetection
```

Import from the interface project as previously done for the SensorFusion application module:

```bash
vaf project import
Enter the path to the exported VAF model JSON file: ../Interfaces/export/Interfaces.json
```

Open the file `CollisionDetection/model/collision_detection.py`. To
complete the import from the interface project, uncomment the following line:

``` python
from .imported_models import *
```

The collision_detection app-module acts as consumer counterpart for the ObjectDetectionListInterface
and towards the platform-side, needs a provider interface for BrakeService. Configure that by adding
the following lines to the CaC file:

``` python
collision_detection = vafpy.ApplicationModule(
    name="CollisionDetection", namespace="NsApplicationUnit::NsCollisionDetection"
)
collision_detection.add_provided_interface(
    "BrakeServiceProvider", interfaces.Af.AdasDemoApp.Services.brake_service
)
collision_detection.add_consumed_interface(
    "ObjectDetectionListModule",
    interfaces.Nsapplicationunit.Nsmoduleinterface.Nsobjectdetectionlist.object_detection_list_interface,
)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
collision_detection.add_task(task=periodic_task)
```

### Steps that apply for both application module projects

Once complete, the configuration needs to be exported to the JSON data exchange format
(`model.json`), which is then used as input for the code generation step. Both steps can be executed
in a row with the following command that needs to be executed from each app-module project directory.

``` bash
vaf project generate
```

The generated code can be divided into read-write and read-only parts. Former gets generated to the
`implementation` folder. This is user space, where the framework only provides implementation and
test stubs for the developer to start. In case of re-generation, a 3-way merge strategy based on
git-merge is applied to the files in this location. The read-only parts get generated to `src-gen`
and `test-gen`. Those folders are under control of the framework. Any user modification will be
overwritten in case of re-generation.

The entry file for the user to add own code is located in
`SensorFusion/implementation/src/sensor_fusion.cpp` and
`CollisionDetection/implementation/src/collision_detection.cpp` respectively. Corresponding headers
are located in the corresponding `implementation/include` subdirectories. Some sample code for
reference is shipped as part of the container and located in: `/opt/vaf/Demo/SilKit/src`. Feel free
to copy this code to the app-module projects:

```bash
cp -r /opt/vaf/Demo/SilKit/src/sensor_fusion/* SensorFusion/implementation/
cp -r /opt/vaf/Demo/SilKit/src/collision_detection/* CollisionDetection/implementation/
```

The application module project can now be built as library, which allows to see if added code passes
the compiler checks. To do so, execute the following step:

``` bash
vaf make build
```

### Unit testing of app-modules

The Vehicle Application Framework provides means for unit testing of application modules. Test mocks
for Googletest are generated to the `test-gen` folder in the app-module projects accordingly and
allow independent first-level testing. Custom test code can be added in the corresponding
`tests.cpp` file in the `implementation/test/unittest` folder.

The resulting test binaries get stored in `build/Release/bin` for execution.

## Executable integration

Final integration of all application modules is done using a VAF integration project. This is
where the whole application, which potentially consists of multiple executables, gets integrated. In
practice, app-modules and platform modules (as provided by the framework) get instantiated and
connected. To start a new integration project, execute the following steps:

``` bash
vaf project init integration
Enter your project name: SilKitDemo
? Enter the directory to store your project in .

cd SilKitDemo
```

Continue by importing the above-created application module projects:

```bash
vaf project import
? Enter the path to the application module project to be imported: ../SensorFusion

vaf project import
? Enter the path to the application module project to be imported: ../CollisionDetection
```

The import command adds new files to `SilKitDemo/model/vaf/application_modules`. Those include
relevant path information but, most and foremost, the importer and CaC-support artifacts, which make
the model elements from the app-module accessible for the configuration in the integration project.

The next step is the configuration of the integration project in `SilKitDemo/model/vaf/sil_kit_demo.py`.

First step is to create a new executable for the ADAS demo:

```python
# Create executable instances (or configure existing ones from the platform configuration)
executable = Executable("AdasDemoExecutable", timedelta(milliseconds=20))
```

Next, add the application modules for Sensor Fusion and Collision Detection and specify the budget
and offset details for the execution of the application module tasks.

```python
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
```

The two app-module instances can now be connected internal to the executable, on the one hand, and
with SIL Kit, on the other hand. The below configuration code snippet details the part for
executable-internal communication in this example project:

``` python
# Connect the application module instances internally
executable.connect_interfaces(
    SensorFusion,
    Instances.SensorFusion.ProvidedInterfaces.ObjectDetectionListModule,
    CollisionDetection,
    Instances.CollisionDetection.ConsumedInterfaces.ObjectDetectionListModule,
)
```

The communication with a lower-layer platform is abstracted by platform modules. They deal with the
platform API towards the lower layer, i.e. the middleware stack, and with the VAF API towards the
upper, the application layer. The connection between application and platform modules is configured
as follows:

``` python
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
```

With this step done, the integration project configuration part is complete. The next step is model
and code generation using:

``` bash
vaf project generate
```

>**ℹ️ Hint** 
> Using `--mode PRJ` or `--mode ALL` allows to set the scope of this command to either,
> the current integration project only (PRJ), or to this and all related sub-projects (ALL).

To complete the integration project, build and finally installation are missing:

``` bash
vaf make install
```

The resulting binary is now available in `SilKitDemo/build/Release/install/opt`.

## Test counterpart

In order to run the ADAS demo application in a meaningful way, a counterpart is required that mimics
a counterpart that consumes/provides the necessary services from platform-side. This counterpart can
for example be realized as extra app-module that is created as part of the above integration project.

``` bash
vaf project create app-module
Enter the name of the app-module: TestModule
Enter the namespace of the app-module: NsApplicationUnit::NsTestModule
? Enter the path to the project root directory .

cd src/application_modules/test_module
```

To import the interface definitions to this app-module project use:
``` bash
vaf project import
? Please provide the path to the exported VAF model JSON file ../../../../Interfaces/export/Interfaces.json
```

Next, open the CaC file in `model/test_module.py` and complete it with the following configuration:
``` python
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
```

Trigger code generation using:
``` bash
vaf project generate
```

Afterwards, sample code as provided with the container can be integrated to the project using: 
``` bash
cp -r /opt/vaf/Demo/SilKit/src/test_module/* ./implementation/
```

Check for compilation issues and complete the TestModule with:
``` bash
vaf make build
```

Switch folders back to the level of the `SilKitDemo` integration project and trigger an update for
the newly added application module:
``` bash
vaf model update
? Choose one ore more application modules (Use arrow keys to move, <space> to select, <a> to toggle, <i> to invert)
   ○ /workspaces/EclipseWorkspace/SilKitDemo/src/application_modules/sensor_fusion
   ○ /workspaces/EclipseWorkspace/SilKitDemo/src/application_modules/collision_detection
 » ● /workspaces/EclipseWorkspace/SilKitDemo/src/application_modules/test_module
```

Next step is to extend the existing CaC project configuration with a new executable to execute an
instance of the TestModule from above. Open `SilKitDemo/model/vaf/sil_kit_demo.py` and complete it
with the following content:
``` python
tester = Executable("AdasDemoTester", timedelta(milliseconds=20))

tester.add_application_module(
    TestModule,
    [
        (Instances.TestModule.Tasks.BrakeTask, b_10ms, 0),
        (Instances.TestModule.Tasks.ImageTask, b_10ms, 0),
        (Instances.TestModule.Tasks.SteeringAngleTask, b_10ms, 0),
        (Instances.TestModule.Tasks.VelocityTask, b_10ms, 0),
    ],
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
```

Finally, complete the integration of the new module with:
``` bash
vaf project generate
vaf make install
```

## Execution of ADAS application with test counterpart

Three executables need to be started for the distributed application to work:
1. The `sil-kit-registry` communication daemon from `SilKitDemo/build/Release/install/opt/silkit/bin`
2. The TestModule from `SilKitDemo/build/Release/install/opt/AdasDemoTester`
3. The ADAS demo from `SilKitDemo/build/Release/install/opt/AdasDemoExecutable`

Use the following sequence to start them all from the `SilKitDemo` project directory:
``` bash
./build/Release/install/opt/silkit/bin/sil-kit-registry &
./build/Release/install/opt/AdasDemoTester/bin/AdasDemoTester &
./build/Release/install/opt/AdasDemoExecutable/bin/AdasDemoExecutable
```

The output should repeatedly look as follows:
``` bash
Received Velocity: 7
SensorFusion::step
Received new images
SensorFusion sending detection list
Collision onObjectList
Received brake_action call with timestamp: 11 and value: 22
...
```

To stop all running processes use `CTRL + c` and `fg` to bring the background processes to the
foreground again.
