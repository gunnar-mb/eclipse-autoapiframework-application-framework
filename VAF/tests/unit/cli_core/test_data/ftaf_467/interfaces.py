from vaf import BaseTypes, vafpy

# Define the required datatypes
od_struct = vafpy.datatypes.Struct(name="ObjectDetection", namespace="adas::interfaces")
od_struct.add_subelement(name="x", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="y", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="z", datatype=BaseTypes.UINT64_T)

od_list = vafpy.datatypes.Vector(
    name="ObjectDetectionList",
    namespace="adas::interfaces",
    datatype=od_struct,
)

# Define the interface
od_interface = vafpy.ModuleInterface(
    name="ObjectDetectionListInterface",
    namespace="adas::interfaces",
)
od_interface.add_data_element(name="object_detection_list", datatype=od_list)

# Define datatype as interface (importables)
od_mode = vafpy.datatypes.String(name="ObjectDetectionMode", namespace="adas::interfaces")

od_status = vafpy.datatypes.Struct(name="ObjectDetectionStatus", namespace="adas::interfaces")
od_status.add_subelement(name="Active", datatype=BaseTypes.BOOL)
od_status.add_subelement(name="Mode", datatype=od_mode)
