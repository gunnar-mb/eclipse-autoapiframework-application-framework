import os

from vaf.vafpy import Executable
from vaf.vafpy.runtime import (
    get_module_interface,
    get_platform_consumer_module,
    get_platform_provider_module,
    import_model,
)

script_path = os.path.dirname(os.path.realpath(__file__))

import_model(os.path.join(script_path, "silkit-model.json"))

# Adapted to work with SIL Kit


# Service interfaces
class Af:
    class Adas_Demo_App:
        class Services:
            # Module Interfaces
            brake_service = get_module_interface("BrakeService", "af::adas_demo_app::services")
            image_service = get_module_interface("ImageService", "af::adas_demo_app::services")
            steering_angle_service = get_module_interface("SteeringAngleService", "af::adas_demo_app::services")
            velocity_service = get_module_interface("VelocityService", "af::adas_demo_app::services")


# Executables and their ports
class AdasDemoApp:
    # Executable
    executable = Executable("adas_demo_app")

    # Required Ports
    class ConsumerModules:
        image_service1 = get_platform_consumer_module("ImageService1", "nsadas_demo_app::nsconsumermodules")
        image_service2 = get_platform_consumer_module("ImageService2", "nsadas_demo_app::nsconsumermodules")
        velocity_service = get_platform_consumer_module("VelocityService", "nsadas_demo_app::nsconsumermodules")
        steering_angle_service = get_platform_consumer_module(
            "SteeringAngleService", "nsadas_demo_app::nsconsumermodules"
        )

    # Provided Ports
    class ProviderModules:
        brake_service = get_platform_provider_module("BrakeService", "nsadas_demo_app::nsprovidermodules")


class AdasDemoTestApp:
    # Executable
    executable = Executable("adas_demo_test_app")

    # Required Ports
    class ConsumerModules:
        brake_service = get_platform_consumer_module("BrakeService", "nsadas_demo_test_app::nsconsumermodules")

    # Provided Ports
    class ProviderModules:
        steering_angle_service = get_platform_provider_module(
            "SteeringAngleService", "nsadas_demo_test_app::nsprovidermodules"
        )
        image_service1 = get_platform_provider_module("ImageService1", "nsadas_demo_test_app::nsprovidermodules")
        velocity_service = get_platform_provider_module("VelocityService", "nsadas_demo_test_app::nsprovidermodules")
        image_service2 = get_platform_provider_module("ImageService2", "nsadas_demo_test_app::nsprovidermodules")
