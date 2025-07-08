"""Generator for controller
Generates
    - executable_controller.h
    - executable_controller.cpp
    - user_controller.h
    - user_controller.cpp
    - CMakeLists.txt
"""
# pylint: disable=too-many-locals

from pathlib import Path
from typing import List

from vaf import vafmodel
from vaf.cli_core.common.utils import to_snake_case
from vaf.vafgeneration.vaf_generate_common import get_ancestor_file_suffix

from .generation import (
    FileHelper,
    Generator,
    is_silkit_used,
    time_str_to_nanoseconds,
)


def _is_vsf_platform_module(executable: vafmodel.Executable, module: vafmodel.PlatformModule) -> bool:
    for m in executable.InternalCommunicationModules:
        if m == module:
            return True
    return False


def get_full_type_of_application_module(
    am: vafmodel.ExecutableApplicationModuleMapping,
) -> str:
    """Get the full type of an application module from its mapping

    Args:
        am (vafmodel.ExecutableApplicationModuleMapping): The application module mapping

    Returns:
        str: The full type of the application module
    """
    return FileHelper(am.ApplicationModuleRef.Name, am.ApplicationModuleRef.Namespace).get_full_type_name()


def get_include_of_application_module(
    am: vafmodel.ExecutableApplicationModuleMapping,
) -> str:
    """Get the include of an application module from its mapping

    Args:
        am (vafmodel.ExecutableApplicationModuleMapping): The application module mapping

    Returns:
        str: The include of the application module
    """
    return FileHelper(am.ApplicationModuleRef.Name, am.ApplicationModuleRef.Namespace).get_include()


def get_full_type_of_platform_module(sm: vafmodel.PlatformModule) -> str:
    """Get the full type of a platform module

    Args:
        sm (vafmodel.PlatformModule): The platform module

    Returns:
        str: The full type of the platform module
    """
    return FileHelper(sm.Name, sm.Namespace).get_full_type_name()


def get_includes_of_platform_modules(
    platform_modules: list[vafmodel.PlatformModule],
) -> list[str]:
    """Gets the list of unique platform module includes

    Args:
        platform_modules (list[vafmodel.PlatformModule]): List of platform modules.

    Returns:
        list[str]: The unique includes for the platform modules
    """
    includes: list[str] = []
    for sm in platform_modules:
        includes.append(FileHelper(sm.Name, sm.Namespace).get_include())
    includes = list(set(includes))
    includes.sort()
    return includes


def is_internal_communication_module(exe: vafmodel.Executable, sm: vafmodel.PlatformModule) -> bool:
    """Returns True if platform module is internal communication module, otherwise False

    Args:
        exe (vafmodel.Executable): The executable
        sm (vafmodel.PlatformModule): The platform module

    Returns:
        bool: True if internal communication module
    """
    if not _is_vsf_platform_module(exe, sm):
        return False
    return True


def _get_provided_modules_of_application_module(
    eamm: vafmodel.ExecutableApplicationModuleMapping,
) -> list[vafmodel.PlatformModule]:
    modules: list[vafmodel.PlatformModule] = []
    am = eamm.ApplicationModuleRef
    for ami in am.ProvidedInterfaces:
        found_iitmm = [iitm for iitm in eamm.InterfaceInstanceToModuleMappings if iitm.InstanceName == ami.InstanceName]
        if len(found_iitmm) == 1:
            modules.append(found_iitmm[0].ModuleRef)
        else:
            raise ValueError(
                f"Error: The application module interface instance: {ami.InstanceName}"
                f" defined for application module: {am.Namespace}::{am.Name} is not mapped/connected."
                "Consider using the 'connect_interfaces()' method to connect the interfaces internally."
            )
    return modules


def _get_consumed_modules_of_application_module(
    eamm: vafmodel.ExecutableApplicationModuleMapping,
) -> list[vafmodel.PlatformModule]:
    modules: list[vafmodel.PlatformModule] = []
    am = eamm.ApplicationModuleRef
    for ami in am.ConsumedInterfaces:
        found_iitmm = [iitm for iitm in eamm.InterfaceInstanceToModuleMappings if iitm.InstanceName == ami.InstanceName]
        if len(found_iitmm) == 1:
            modules.append(found_iitmm[0].ModuleRef)
        else:
            raise ValueError(
                f"Error: The application module interface instance: {ami.InstanceName}"
                f" defined for application module: {am.Namespace}::{am.Name} is not mapped/connected."
                "Consider using the 'connect_interfaces()' method to connect the interfaces internally."
            )
    return modules


def _get_consumed_interface(
    am: vafmodel.ExecutableApplicationModuleMapping, m: vafmodel.PlatformModule
) -> vafmodel.ApplicationModuleConsumedInterface:
    for iitmm in am.InterfaceInstanceToModuleMappings:
        if iitmm.ModuleRef == m:
            for ci in am.ApplicationModuleRef.ConsumedInterfaces:
                if ci.InstanceName == iitmm.InstanceName:
                    return ci
    raise ValueError(f"Error: could not find consumed interface of platform module {m.Namespace}::{m.Name}")


# pylint: disable=too-many-branches
def get_dependencies_of_application_module(
    exe: vafmodel.Executable,
    am: vafmodel.ExecutableApplicationModuleMapping,
) -> tuple[list[str], list[str]]:
    """Gets the execution and module dependencies of a application module by its mapping

    Args:
        exe (vafmodel.Executable): The executable the application module is mapped to
        am (vafmodel.ExecutableApplicationModuleMapping): The application module mapping

    Returns:
        tuple[list[str], list[str]]: The execution and module dependencies
    """
    execution_dependencies: list[str] = []
    module_dependencies_c: list[str] = []
    module_dependencies_p: list[str] = []

    provided_modules = _get_provided_modules_of_application_module(am)
    for m in provided_modules:
        module_dependencies_p.append(m.Name)
        if not _is_vsf_platform_module(exe, m):
            execution_dependencies.append(m.Name)

    consumed_modules = _get_consumed_modules_of_application_module(am)
    for m in consumed_modules:
        module_dependencies_c.append(m.Name)

        if not _get_consumed_interface(am, m).IsOptional:
            execution_dependencies.append(m.Name)

    return (execution_dependencies, module_dependencies_c + module_dependencies_p)


# pylint: enable=too-many-branches


def get_task_mapping(
    mapping: vafmodel.ExecutableTaskMapping,
    am: vafmodel.ExecutableApplicationModuleMapping,
) -> tuple[int, int]:
    """Gets the offset and budget of a task by its mapping

    Args:
        mapping (vafmodel.ExecutableTaskMapping): The task mapping
        am (vafmodel.ExecutableApplicationModuleMapping): The application module the task is mapped to

    Raises:
        ValueError: If the mapped task is not found in the application module

    Returns:
        tuple[int, int]: The offset and budget of the task
    """
    offset = mapping.Offset if mapping.Offset is not None else 0
    budget = time_str_to_nanoseconds(mapping.Budget) if mapping.Budget is not None else 0

    task = [r for r in am.ApplicationModuleRef.Tasks if r.Name == mapping.TaskName]
    if len(task) == 0:
        raise ValueError(
            f"Error: could not find mapped task {mapping.TaskName} in application module"
            f"{am.ApplicationModuleRef.Namespace}::{am.ApplicationModuleRef.Name}"
        )

    preferred_offset = task[0].PreferredOffset
    if preferred_offset is not None:
        if mapping.Offset is None:
            offset = preferred_offset
        elif mapping.Offset != preferred_offset:
            print(f"Warning: offset for task {mapping.TaskName} is different then its preferred offset")

    return (offset, budget)


# Locals use seems reasonable. Generator could become an argument but not really a benefit there


def generate(  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    model: vafmodel.MainModel, output_dir: Path, is_ancestor: bool = False, verbose_mode: bool = False
) -> List[str]:
    """Generate the VAF controller

    Args:
        model (vafmodel.MainModel): The main model
        output_dir (Path): The output directory
        is_ancestor (bool): Flag to trigger generation for ancestor
        verbose_mode: flag to enable verbose_mode mode

    Raises:
        ValueError: If there is a interface mapping problem
    """
    generator = Generator()

    # collect list of merge relevant files
    list_merge_relevant_files: List[str] = []

    for e in model.Executables:  # pylint: disable=too-many-branches, too-many-nested-blocks
        output_path = output_dir / "src-gen/executables"
        provided_modules: list[vafmodel.PlatformModule] = []
        consumed_modules: list[vafmodel.PlatformModule] = []

        for am in e.ApplicationModules:
            for mapping in am.InterfaceInstanceToModuleMappings:
                if (
                    len(
                        [
                            ci
                            for ci in am.ApplicationModuleRef.ConsumedInterfaces
                            if ci.InstanceName == mapping.InstanceName
                        ]
                    )
                    > 0
                ):
                    if not _is_vsf_platform_module(e, mapping.ModuleRef):
                        consumed_modules.append(mapping.ModuleRef)
                elif (
                    len(
                        [
                            ci
                            for ci in am.ApplicationModuleRef.ProvidedInterfaces
                            if ci.InstanceName == mapping.InstanceName
                        ]
                    )
                    > 0
                ):
                    provided_modules.append(mapping.ModuleRef)

                else:
                    raise ValueError(
                        f"Mapped interface instance {mapping.InstanceName} not found in application module: "
                    )

        folder_name = to_snake_case(e.Name)
        generator.set_base_directory(output_path / folder_name)

        exe_controller_file = FileHelper("ExecutableController", "executable_controller")
        if not is_ancestor:
            generator.generate_to_file(exe_controller_file, ".h", "vaf_controller/executable_controller_h.jinja")
            generator.generate_to_file(
                exe_controller_file,
                ".cpp",
                "vaf_controller/executable_controller_cpp.jinja",
                get_full_type_of_application_module=get_full_type_of_application_module,
                get_dependencies_of_application_module=get_dependencies_of_application_module,
                get_includes_of_platform_modules=get_includes_of_platform_modules,
                get_full_type_of_platform_module=get_full_type_of_platform_module,
                is_internal_communication_module=is_internal_communication_module,
                get_include_of_application_module=get_include_of_application_module,
                get_task_mapping=get_task_mapping,
                executable=e,
                communication_modules=consumed_modules + provided_modules,
                vafmodel=vafmodel,
                isinstance=isinstance,
                verbose_mode=verbose_mode,
            )

        output_path = output_dir / "src/executables"
        generator.set_base_directory(output_path / folder_name)

        user_controller_file = FileHelper("UserController", "")
        generator.generate_to_file(
            user_controller_file,
            f".h{get_ancestor_file_suffix(is_ancestor)}",
            "vaf_controller/user_controller_h.jinja",
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        list_merge_relevant_files.append(f"src/executables/{folder_name}/UserController.h")
        generator.generate_to_file(
            user_controller_file,
            f".cpp{get_ancestor_file_suffix(is_ancestor)}",
            "vaf_controller/user_controller_cpp.jinja",
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        list_merge_relevant_files.append(f"src/executables/{folder_name}/UserController.cpp")

        output_path = output_dir / "src-gen/executables"
        generator.set_base_directory(output_path / folder_name)

        main_file = FileHelper("Main", "")
        if not is_ancestor:
            generator.generate_to_file(
                main_file,
                ".cpp",
                "vaf_controller/main_cpp.jinja",
                controller_file=exe_controller_file,
                verbose_mode=verbose_mode,
            )

        def __generate_platform_modules_library_list(modules: List[vafmodel.PlatformModule]) -> List[str]:
            result = []
            for module in modules:
                target_name_list = [
                    "vaf",
                    to_snake_case(module.Name),
                ]
                result.append("_".join(target_name_list))
            return result

        libraries = __generate_platform_modules_library_list(
            consumed_modules
        ) + __generate_platform_modules_library_list(provided_modules)

        for a in e.ApplicationModules:
            libraries.append(to_snake_case(a.ApplicationModuleRef.Name))

        if not is_ancestor:
            generator.generate_to_file(
                FileHelper("CMakeLists", "", True),
                ".txt",
                "vaf_controller/CMakeLists_txt.jinja",
                target_name=e.Name,
                files=[exe_controller_file],
                libraries=libraries,
                uses_silkit=is_silkit_used(model),
                verbose_mode=verbose_mode,
            )
        output_path = output_dir / "src/executables"
        generator.set_base_directory(output_path / folder_name)
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            f".txt{get_ancestor_file_suffix(is_ancestor)}",
            "vaf_controller/user_controller_CMakeLists_txt.jinja",
            target_name=e.Name,
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        list_merge_relevant_files.append(f"src/executables/{folder_name}/CMakeLists.txt")

    return list_merge_relevant_files


# pylint: enable=too-many-locals
