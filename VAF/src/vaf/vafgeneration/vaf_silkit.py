"""Generator library for SILKIT communication modules."""
# pylint: disable=duplicate-code

from pathlib import Path

from vaf import vafmodel
from vaf.cli_core.common.utils import to_snake_case

from .generation import (
    FileHelper,
    Generator,
    has_exactly_one_output_parameter,
    is_data_type_base_type,
    is_data_type_cstdint_type,
    is_out_parameter,
)


# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks
def get_data_type_definition_of_parameter(data_type: vafmodel.DataType, model: vafmodel.MainModel) -> str:
    """Get type definition of a DataType

    Args:
        data_type (vafmodel.DataType): The data type
        model (vafmodel.MainModel): The model

    Returns:
        str: type def as string
    """
    result = "NOT_FOUND"
    if is_data_type_base_type(data_type.Name, data_type.Namespace) or is_data_type_cstdint_type(
        data_type.Name, data_type.Namespace
    ):
        match data_type.Name:
            case "uint8_t":
                result = "uint32"
            case "uint16_t":
                result = "uint32"
            case "uint32_t":
                result = "uint32"
            case "uint64_t":
                result = "uint64"
            case "int8_t":
                result = "int32"
            case "int16_t":
                result = "int32"
            case "int32_t":
                result = "int32"
            case "int64_t":
                result = "int64"
            case _:
                result = "data_type.Name"
    else:
        if model.DataTypeDefinitions:
            for datatype in vafmodel.data_types:
                for data in getattr(model.DataTypeDefinitions, datatype):
                    if data_type.Name == data.Name and data_type.Namespace == data.Namespace:
                        result = datatype
                        break
    return result


# pylint: enable=too-many-branches
# pylint: enable=too-many-nested-blocks


def _get_in_parameter_list_comma_separated(operation: vafmodel.Operation) -> str:
    parameter_str = ""
    is_first = True
    for parameter in operation.Parameters:
        if not is_out_parameter(parameter):
            if is_first:
                parameter_str = parameter.Name
                is_first = False
            else:
                parameter_str = parameter_str + ", " + parameter.Name
    return parameter_str


def _generate_provider_modules(
    model: vafmodel.MainModel, output_path: Path, generator: Generator, verbose_mode: bool = False
) -> None:
    subdirs: list[str] = []

    for m in model.PlatformProviderModules:
        if m.OriginalEcoSystem == vafmodel.OriginalEcoSystemEnum.SILKIT:
            assert m.ConnectionPointRef
            assert isinstance(m.ConnectionPointRef, vafmodel.SILKITConnectionPoint)
            subdirs.append(to_snake_case(m.Name))
            generator.set_base_directory(output_path / "platform_provider_modules" / to_snake_case(m.Name))
            interface_file = FileHelper(m.ModuleInterfaceRef.Name + "Provider", m.ModuleInterfaceRef.Namespace)
            module_file = FileHelper(m.Name, m.Namespace)
            service_interface_name = m.ConnectionPointRef.ServiceInterfaceName
            registry_uri = m.ConnectionPointRef.RegistryUri

            generator.generate_to_file(
                module_file,
                ".h",
                "vaf_silkit/provider_module_h.jinja",
                module=m,
                interface_file=interface_file,
                service_interface_name=service_interface_name,
                verbose_mode=verbose_mode,
            )

            generator.generate_to_file(
                module_file,
                ".cpp",
                "vaf_silkit/provider_module_cpp.jinja",
                module=m,
                interface_file=interface_file,
                service_interface_name=service_interface_name,
                has_exactly_one_output_parameter=has_exactly_one_output_parameter,
                get_data_type_definition_of_parameter=get_data_type_definition_of_parameter,
                str=str,
                model=model,
                get_in_parameter_list_comma_separated=_get_in_parameter_list_comma_separated,
                verbose_mode=verbose_mode,
                registry_uri=registry_uri,
            )

            generator.generate_to_file(
                FileHelper("CMakeLists", "", True),
                ".txt",
                "vaf_silkit/module_cmake.jinja",
                target_name="vaf_" + to_snake_case(m.Name),
                files=[module_file],
                libraries=[
                    "$<IF:$<TARGET_EXISTS:vafcpp::vaf_core>,vafcpp::vaf_core,vaf_core>",
                    "vaf_module_interfaces",
                    "vaf_module_interfaces",
                    "SilKit::SilKit",
                    "vaf_protobuf",
                    "vaf_protobuf_transformer",
                ],
                verbose_mode=verbose_mode,
            )

    generator.set_base_directory(output_path / "platform_provider_modules")
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "common/cmake_subdirs.jinja",
        subdirs=subdirs,
        verbose_mode=verbose_mode,
    )


def _generate_consumer_modules(
    model: vafmodel.MainModel, output_path: Path, generator: Generator, verbose_mode: bool = False
) -> None:
    subdirs: list[str] = []

    for m in model.PlatformConsumerModules:
        if m.OriginalEcoSystem == vafmodel.OriginalEcoSystemEnum.SILKIT:
            assert m.ConnectionPointRef
            assert isinstance(m.ConnectionPointRef, vafmodel.SILKITConnectionPoint)
            subdirs.append(to_snake_case(m.Name))

            generator.set_base_directory(output_path / "platform_consumer_modules" / to_snake_case(m.Name))

            interface_file = FileHelper(m.ModuleInterfaceRef.Name + "Consumer", m.ModuleInterfaceRef.Namespace)
            module_file = FileHelper(m.Name, m.Namespace)
            service_interface_name = m.ConnectionPointRef.ServiceInterfaceName
            registry_uri = m.ConnectionPointRef.RegistryUri

            generator.generate_to_file(
                module_file,
                ".h",
                "vaf_silkit/consumer_module_h.jinja",
                module=m,
                interface_file=interface_file,
                service_interface_name=service_interface_name,
                verbose_mode=verbose_mode,
            )

            generator.generate_to_file(
                module_file,
                ".cpp",
                "vaf_silkit/consumer_module_cpp.jinja",
                module=m,
                service_interface_name=service_interface_name,
                has_exactly_one_output_parameter=has_exactly_one_output_parameter,
                get_data_type_definition_of_parameter=get_data_type_definition_of_parameter,
                str=str,
                model=model,
                get_in_parameter_list_comma_separated=_get_in_parameter_list_comma_separated,
                verbose_mode=verbose_mode,
                registry_uri=registry_uri,
            )

            generator.generate_to_file(
                FileHelper("CMakeLists", "", True),
                ".txt",
                "vaf_silkit/module_cmake.jinja",
                target_name="vaf_" + to_snake_case(m.Name),
                files=[module_file],
                libraries=[
                    "$<IF:$<TARGET_EXISTS:vafcpp::vaf_core>,vafcpp::vaf_core,vaf_core>",
                    "vaf_module_interfaces",
                    "SilKit::SilKit",
                    "vaf_protobuf",
                    "vaf_protobuf_transformer",
                ],
                verbose_mode=verbose_mode,
            )

    generator.set_base_directory(output_path / "platform_consumer_modules")
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "common/cmake_subdirs.jinja",
        subdirs=subdirs,
        verbose_mode=verbose_mode,
    )


def generate(model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False) -> None:
    """Generates the middleware wrappers for silkit

    Args:
        model (vafmodel.MainModel): The main model
        output_dir (Path): The output path
        verbose_mode: flag to enable verbose_mode mode
    """
    output_path = output_dir / "src-gen/libs/platform_silkit"
    generator = Generator()
    _generate_consumer_modules(model, output_path, generator, verbose_mode)
    _generate_provider_modules(model, output_path, generator, verbose_mode)

    subdirs: list[str] = []
    if len(model.PlatformConsumerModules) > 0:
        subdirs.append("platform_consumer_modules")
    if len(model.PlatformProviderModules) > 0:
        subdirs.append("platform_provider_modules")
    generator.set_base_directory(output_path)
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "common/cmake_subdirs.jinja",
        subdirs=subdirs,
        verbose_mode=verbose_mode,
    )
