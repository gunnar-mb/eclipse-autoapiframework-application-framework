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
class Vcandrive:
    # Module Interfaces
    service_12v = get_module_interface("Service_12V", "vcandrive")
    service_bms = get_module_interface("Service_BMS", "vcandrive")
    service_com_led = get_module_interface("Service_COM_LED", "vcandrive")
    service_com_led_command = get_module_interface("Service_COM_LED_command", "vcandrive")
    service_coordinates = get_module_interface("Service_Coordinates", "vcandrive")
    service_led_frame = get_module_interface("Service_LED_Frame", "vcandrive")
    service_microbus = get_module_interface("Service_Microbus", "vcandrive")
    service_motor_temp = get_module_interface("Service_Motor_Temp", "vcandrive")
    service_remote_data = get_module_interface("Service_Remote_Data", "vcandrive")
    service_target_m = get_module_interface("Service_Target_M", "vcandrive")
    service_us_sensors = get_module_interface("Service_US_Sensors", "vcandrive")
    service_brake_force = get_module_interface("Service_brake_force", "vcandrive")
    service_depth_camera_map = get_module_interface("Service_depth_camera_map", "vcandrive")
    service_direction = get_module_interface("Service_direction", "vcandrive")
    service_image = get_module_interface("Service_image", "vcandrive")
    service_lightcontrol_led_command = get_module_interface("Service_lightcontrol_LED_command", "vcandrive")
    service_occlusion_map = get_module_interface("Service_occlusion_map", "vcandrive")
    service_piezos = get_module_interface("Service_piezos", "vcandrive")
    service_signaling_led = get_module_interface("Service_signaling_LED", "vcandrive")
    service_steer = get_module_interface("Service_steer", "vcandrive")
    service_target = get_module_interface("Service_target", "vcandrive")
    service_ultrasonic_fusion_map = get_module_interface("Service_ultrasonic_fusion_map", "vcandrive")
    service_vehicle_position = get_module_interface("Service_vehicle_position", "vcandrive")
    servie_buttons = get_module_interface("Servie_Buttons", "vcandrive")
