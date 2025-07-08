"""Validator to raise Errors in case of Configuration Error before generating JSON"""

import math
import warnings
from collections.abc import Hashable
from typing import Callable, Dict, List, Tuple

from vaf.cli_core.common.utils import ProjectType as PType
from vaf.cli_core.common.utils import create_name_namespace_full_name
from vaf.vafmodel import ApplicationModule, Executable

from .core import ModelError
from .model_runtime import ModelRuntime


def make_list_unique(list_input: List[Hashable] | List[str]) -> List[Hashable] | List[str]:
    """Method to make list unique
    Args:
        list_input: List to be made unique
    Return:
        List without any duplicates
    """
    return list(set(list_input))


def format_warning(
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    line: str | None = None,
) -> str:
    # pylint: disable=unused-argument
    """Format the warnings to be more user-friendly.
    Args:
        message (Warning | str): The warning message to format.
        category (type[Warning]): The category of the warning.
        filename (str): The name of the file where the warning occurred.
        lineno (int): The line number where the warning occurred.
        line (str, optional): The line of code where the warning occurred (default is None).
    Returns:
        str: Formatted warning message.
    """
    return "\n" + str(filename) + ":" + str(lineno) + ": " + category.__name__ + ":\n" + str(message) + "\n"


class Validator:
    # pylint: disable=too-few-public-methods
    """Handling Config Validation"""

    msg_str: Dict[str, str] = {
        "error": "Identical Duplicates for {WHAT} Name = {DTD_NAME} : {DATA}",
        "warning": "Possible {DTD_N} duplicates for {WHAT} Name = {DTD_NAME} with different namespaces {DATA}",
    }

    def __init__(self, project_type: PType) -> None:
        # List that defines which validation methods will be executed for which project-type
        self.__executor_manager: List[Tuple[List[PType], Callable[[ModelRuntime], Tuple[List[str], List[str]]]]] = [
            ([PType.INTEGRATION], self.__validate_executables),
            ([PType.INTEGRATION], self.__validate_interface_connections),
            ([PType.INTEGRATION, PType.APP_MODULE], self.__validate_application_module),
            ([PType.INTEGRATION, PType.APP_MODULE, PType.INTERFACE], self.__validate_interface_definition),
        ]
        self.project_type = project_type

    def validate_model(self, runtime_model: ModelRuntime) -> ModelRuntime:
        """Method to validate CaC model
        Args:
            runtime_model: ModelRuntime to be validated
        Returns:
            Updated ModelRuntime
        Raises:
            ModelError: hard modelling list_errors
        """
        warnings.formatwarning = format_warning

        hard_errors: List[str] = []
        light_warnings: List[str] = []

        for project_types, validate_method in self.__executor_manager:
            if self.project_type in project_types:
                err, wrn = validate_method(runtime_model)
                hard_errors += err
                light_warnings += wrn

        if light_warnings:
            warnings.warn("\n".join(light_warnings))
        if hard_errors:
            raise ModelError("\n".join(hard_errors))

        # returns runtime_model so it can be used in one-liner
        return runtime_model

    def __validate_executable_executor_period(self, executable: Executable) -> Tuple[List[str], List[str]]:
        """Method to validate an executable's executor period
        Args:
            exec: Executable to be validated
        Returns:
            List of errors & warnings for Executable modelling
        """
        list_errors: List[str] = []

        # get all periodic tasks from all app modules belonging to the executable
        periodic_tasks_data = [
            [
                create_name_namespace_full_name(
                    app_module.ApplicationModuleRef.Name, app_module.ApplicationModuleRef.Namespace
                ),
                task.Name,
                int(task.Period.rstrip("ms")),
            ]
            for app_module in executable.ApplicationModules
            for task in app_module.ApplicationModuleRef.Tasks
            if task.Period.rstrip("ms").isdigit()
        ]
        if periodic_tasks_data:
            app_module_names, tasks_names, all_tasks_period = zip(*periodic_tasks_data)

            error_msg = ""
            if executable.ExecutorPeriod == "Default":
                # calculate the common denominators of all PeriodicTasks
                executable.ExecutorPeriod = f"{math.gcd(*all_tasks_period)}ms"
            elif executable.ExecutorPeriod.rstrip("ms").isdigit():
                # ensure Executor Period <= the smallest task period
                executor_period = int(executable.ExecutorPeriod.rstrip("ms"))
                if executor_period > min(all_tasks_period):
                    # get tasks with the minimum
                    error_msg = "\n".join(
                        [
                            f"Invalid ExecutorPeriod of Executable {executable.Name}: {executable.ExecutorPeriod}!",
                            f"Executor Period {executable.ExecutorPeriod} is longer than its Task(s)' period:",
                        ]
                        + [
                            f"   AppModule: {app_module_names[idx]} - Task: {tasks_names[idx]} with period {task_period}ms"  # pylint:disable=line-too-long
                            for idx, task_period in enumerate(all_tasks_period)
                            if executor_period > task_period
                        ]
                    )

            if error_msg:
                list_errors.append(error_msg)

        return list_errors, []

    def __validate_executables(self, runtime_model: ModelRuntime) -> Tuple[List[str], List[str]]:
        """Method to validate model's executables
        Also: Clean unused application modules from model
        Args:
            runtime_model: ModelRuntime to be validated
        Returns:
            List of errors & warnings for Executable modelling
        """
        # set placeholder to collect all errors & warnings
        list_errors: List[str] = []

        # create placeholder for valid executables
        valid_executables: List[Executable] = []
        # create placeholder for all executables name
        valid_executables_name: List[str] = []
        # create placeholder for connected application modules
        connected_app_modules: List[ApplicationModule] = []

        for executable in runtime_model.main_model.Executables:
            # raise error if duplicates are discovered
            if executable.Name in valid_executables_name:
                list_errors.append(f"Executable {executable.Name} is defined multiple times!")

            # valid executables have at least 1 ApplicationModule
            if executable.ApplicationModules:
                # add to valid executables
                valid_executables.append(executable)
                valid_executables_name.append(executable.Name)
                # add connected app modules
                connected_app_modules += [
                    app_module_obj.ApplicationModuleRef for app_module_obj in executable.ApplicationModules
                ]

            # verify periodic task
            exec_periodic_task_err, _ = self.__validate_executable_executor_period(executable)
            list_errors += exec_periodic_task_err

        # replace model.Executables with valid_executables
        runtime_model.main_model.Executables = valid_executables

        # get unconnected app modules for warning message
        unconnected_app_modules: List[ApplicationModule] = [
            app_module
            for app_module in runtime_model.main_model.ApplicationModules
            if app_module not in connected_app_modules
        ]
        # overwrite model's app modules
        runtime_model.main_model.ApplicationModules = connected_app_modules

        # build warnings
        list_warnings = [
            f"App Module '{unconnected_am.Namespace}::{unconnected_am.Name}' is defined, "
            "but not connected in any Executable"
            for unconnected_am in unconnected_app_modules
        ]

        return list_errors, list_warnings

    # pylint: enable=too-many-nested-blocks

    @staticmethod
    def __validate_interface_connections(runtime_model: ModelRuntime) -> Tuple[List[str], List[str]]:
        """Method to validate model's interface connections
        Args:
            runtime_model: ModelRuntime to be validated
        Returns:
            List of list_errors & warnings for unconnected interfaces
        """
        # placeholder for all warnings
        list_warnings: List[str] = []
        unconnected_interfaces = []

        for app_module in runtime_model.main_model.ApplicationModules:
            module_str = f"{app_module.Namespace}::{app_module.Name}"
            for ci in app_module.ConsumedInterfaces:
                if not ci.IsOptional and ci.InstanceName not in runtime_model.connected_interfaces[module_str]:
                    unconnected_interfaces.append(f"{module_str} - {ci.InstanceName}")
            for pi in app_module.ProvidedInterfaces:
                if pi.InstanceName not in runtime_model.connected_interfaces[module_str]:
                    unconnected_interfaces.append(f"{module_str} - {pi.InstanceName}")

        if unconnected_interfaces:
            list_warnings.append(f"Following interfaces are defined but not connected: {unconnected_interfaces}")

        return [], list_warnings

    @staticmethod
    def __validate_interface_definition(runtime_model: ModelRuntime) -> Tuple[List[str], List[str]]:
        """Method to validate model's interface definitions
        Args:
            runtime_model: ModelRuntime to be validated
        Returns:
            List of list_errors & warnings for empty interfaces
        """
        # placeholder for all warnings
        list_warnings: List[str] = []
        empty_interfaces = []

        # use module interface from main model since validation takes place after cleanup
        for module_interaface in runtime_model.main_model.ModuleInterfaces:
            if not module_interaface.DataElements and not module_interaface.Operations:
                empty_interfaces.append(f"{module_interaface.Namespace}::{module_interaface.Name}")

        if empty_interfaces:
            list_warnings.append(
                f"Following interfaces are defined without data elements and operations: {empty_interfaces}"
            )

        return [], list_warnings

    @staticmethod
    def __validate_application_module(runtime_model: ModelRuntime) -> Tuple[List[str], List[str]]:
        """Method to validate model's application modules
        Args:
            runtime_model: ModelRuntime to be validated
        Returns:
            List of errors & warnings for application module modelling
        """
        # placeholder for all errors
        list_errors: List[str] = []
        for app_module in runtime_model.main_model.ApplicationModules:
            all_task_names: list[str] = []
            all_run_afters: set[str] = set()
            for task in app_module.Tasks:
                all_task_names.append(task.Name)
                all_run_afters.update(task.RunAfter)

            for run_after in all_run_afters:
                if run_after not in all_task_names:
                    list_errors.append(
                        f"Task {run_after} is used in as a 'run_after' dependency in ApplicationModule"
                        f" {app_module.Namespace}::{app_module.Name}, but is not part of it."
                    )

        return list_errors, []
