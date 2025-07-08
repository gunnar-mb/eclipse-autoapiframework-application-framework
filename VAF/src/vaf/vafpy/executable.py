"""Executable integration calls and helper functions"""  # pylint: disable=too-many-lines

# pylint bug, see https://github.com/pylint-dev/pylint/issues/4899 and https://github.com/pylint-dev/pylint/issues/10087
# marked with # pylint-bug (29.01.25, lwiesner)

from datetime import timedelta

from vaf import vafmodel

from .core import ModelError
from .elements import ApplicationModule
from .model_runtime import model_runtime


class Executable(vafmodel.Executable):
    """Represents a VAF executable"""

    def __init__(self, name: str, executor_period: timedelta | None = None) -> None:
        """Initialize an Executable with an optional executor_period

        Args:
            name (str): Executable name
            executor_period (datetime.timedelta, optional): Executor period. Defaults to an ideal value calculated using
            the tasks of all AppModules.
        """
        period_str = f"{int(executor_period.total_seconds() * 1000)}ms" if executor_period else "Default"

        super().__init__(Name=name, ExecutorPeriod=period_str, ApplicationModules=[])

        model_runtime.main_model.Executables.append(self)

    def set_executor_period(self, executor_period: timedelta) -> None:
        """Method to set ExecutorPeriod
        Args:
            executor_period (datetime.timedelta): Executor period as timedelta
        """
        self.ExecutorPeriod = f"{int(executor_period.total_seconds() * 1000)}ms"

    def add_application_module(
        self,
        module: ApplicationModule,
        task_mapping_info: list[tuple[str, timedelta, int]],
    ) -> None:
        """Add an application module to the executable

        Args:
            module (vafpy.ApplicationModule): Application module instance to add
            task_mapping_info (list[tuple[str, timedelta, int]]): Mapping info for tasks a list of tuples with
            (task_name, budget, offset)
        """
        task_mappings: list[vafmodel.ExecutableTaskMapping] = []
        for r in task_mapping_info:
            budget_str = f"{int(r[1].total_seconds() * 1000)}ms"
            task_mappings.append(vafmodel.ExecutableTaskMapping(TaskName=r[0], Offset=r[2], Budget=budget_str))
        self.ApplicationModules.append(
            vafmodel.ExecutableApplicationModuleMapping(
                ApplicationModuleRef=module,
                InterfaceInstanceToModuleMappings=[],
                TaskMapping=task_mappings,
            )
        )

    # FIXME(virmlj) refactor
    # pylint: disable-next=too-many-locals, too-many-branches
    def connect_interfaces(
        self,
        module_a: ApplicationModule,
        instance_name_a: str,
        module_b: ApplicationModule,
        instance_name_b: str,
    ) -> None:
        """Connects two interfaces of two application modules in this executable

        Args:
            module_a (vafpy.ApplicationModule): The provider application module
            instance_name_a (str): The instance name of the provided interface
            module_b (vafpy.ApplicationModule): The consumer application module
            instance_name_b (str): The instance name of the consumed interface

        Raises:
            ModelError: If any of the modules are not mapped to the executable,
                        if any of the instances names is not found
                        or if the interfaces are not compatible
        """
        found_pi = [pi for pi in module_a.ProvidedInterfaces if pi.InstanceName == instance_name_a]
        found_ci = [ci for ci in module_b.ConsumedInterfaces if ci.InstanceName == instance_name_b]

        if len(found_pi) != 1:
            raise ModelError(
                "Could not find interface instance "
                + instance_name_a
                + " on a provided interface of module "
                + module_a.Name
            )

        if len(found_ci) != 1:
            raise ModelError(
                "Could not find interface instance "
                + instance_name_b
                + " on a consumed interface of module "
                + module_b.Name
            )

        if found_pi[0].ModuleInterfaceRef != found_ci[0].ModuleInterfaceRef:
            raise ModelError(
                "Interfaces do not match: "
                + found_pi[0].ModuleInterfaceRef.Namespace
                + "::"
                + found_pi[0].ModuleInterfaceRef.Name
                + " and "
                + found_ci[0].ModuleInterfaceRef.Namespace
                + "::"
                + found_ci[0].ModuleInterfaceRef.Name
            )

        found_am_a = [
            a
            for a in self.ApplicationModules
            if a.ApplicationModuleRef.Name == module_a.Name and a.ApplicationModuleRef.Namespace == module_a.Namespace
        ]
        found_am_b = [
            a
            for a in self.ApplicationModules
            if a.ApplicationModuleRef.Name == module_b.Name and a.ApplicationModuleRef.Namespace == module_b.Namespace
        ]

        if len(found_am_a) != 1:
            raise ModelError("Could not find application module " + module_a.Name + " mapped on executable")

        if len(found_am_b) != 1:
            raise ModelError("Could not find application module " + module_b.Name + " mapped on executable")

        already_mapped_on_provider = False
        for instance in found_am_a[0].InterfaceInstanceToModuleMappings:
            if instance.InstanceName == instance_name_a:
                already_mapped_on_provider = True
                sm = instance.ModuleRef

        if not already_mapped_on_provider:
            sm = vafmodel.PlatformModule(
                Name=found_pi[0].ModuleInterfaceRef.Name + "Module",
                Namespace="application_communication",
                ModuleInterfaceRef=found_pi[0].ModuleInterfaceRef,
            )
            self.InternalCommunicationModules.append(sm)

        mapping_a = vafmodel.InterfaceInstanceToModuleMapping(InstanceName=instance_name_a, ModuleRef=sm)
        mapping_b = vafmodel.InterfaceInstanceToModuleMapping(InstanceName=instance_name_b, ModuleRef=sm)

        if not already_mapped_on_provider:
            found_am_a[0].InterfaceInstanceToModuleMappings.append(mapping_a)
        found_am_b[0].InterfaceInstanceToModuleMappings.append(mapping_b)

        model_runtime.connected_interfaces[f"{module_a.Namespace}::{module_a.Name}"].append(found_pi[0].InstanceName)
        model_runtime.connected_interfaces[f"{module_b.Namespace}::{module_b.Name}"].append(found_ci[0].InstanceName)

    def __connect_interface_to_silkit(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        app_module: ApplicationModule,
        instance_name: str,
        silkit_address_instance_name: str,
        registry_uri: str,
        interface_type: str,
    ) -> None:
        """Connects a consumer interface of an application module with the user-provided platform consumer module
           Use this CaC support for platform-centric projects where the platform is already known

        Args:
            app_module (vafpy.ApplicationModule): Application module instance to
            connect
            instance_name (str): The interface instance name
            silkit_address_instance_name (str): The silkit instance address
            registry_uri (str): The silkit registry uri to use
            interface_type (str): type of interface "consumed" or "provided"

        Raises:
            ModelError: If the application module was not found,
                        if the instance was not found
                        or if the interfaces do not match
        """
        # found the corresponding app module
        found_am = [
            a
            for a in self.ApplicationModules
            if a.ApplicationModuleRef.Name == app_module.Name
            and a.ApplicationModuleRef.Namespace == app_module.Namespace
        ]

        if len(found_am) != 1:
            raise ModelError("Could not find application module " + app_module.Name + " mapped on executable")

        # get interface type: "Consumed"/"Provided" from Platform<type>rModule
        assert interface_type in ("Consumed", "Provided")
        #  check if interfaces are the same
        found_interface = [
            pi for pi in getattr(app_module, f"{interface_type}Interfaces") if pi.InstanceName == instance_name
        ]
        if len(found_interface) != 1:
            raise ModelError(f"No {interface_type}Interface with instance {instance_name} in Module {app_module.Name}")

        if silkit_address_instance_name == "":
            silkit_address_instance_name = f"Silkit_{found_interface[0].ModuleInterfaceRef.Name}"

        # Consumed -> Consumer, Provided -> Provider
        interface_type = interface_type.removesuffix("d") + "r"

        # check the found consumer/provider modules
        found_module = [
            interface_module
            for interface_module in getattr(model_runtime.main_model, f"Platform{interface_type}Modules")
            if interface_module.ModuleInterfaceRef == found_interface[0].ModuleInterfaceRef
            and isinstance(interface_module.ConnectionPointRef, vafmodel.SILKITConnectionPoint)
            and interface_module.ConnectionPointRef.ServiceInterfaceName == silkit_address_instance_name
        ]

        if len(found_module) > 1:
            raise ModelError(
                (
                    f"Found missconfiguration of Silkit {interface_type} modules for module interface"
                    f" {found_interface[0].ModuleInterfaceRef.Namespace}"
                    f"::{found_interface[0].ModuleInterfaceRef.Name} with  silkit instance address"
                    f" {silkit_address_instance_name}"
                )
            )
        if len(found_module) == 1:
            # use the found module
            module = found_module[0]
        else:
            # no module found
            scp = vafmodel.SILKITConnectionPoint(
                Name=f"ConnectionPoint_{interface_type.lower()}_{instance_name}",
                ServiceInterfaceName=silkit_address_instance_name,
                RegistryUri=registry_uri,
            )
            if model_runtime.main_model.SILKITAdditionalConfiguration is None:
                model_runtime.main_model.SILKITAdditionalConfiguration = vafmodel.SILKITAdditionalConfigurationType(
                    ConnectionPoints=[]
                )
            # pylint-bug
            # pylint: disable-next=no-member
            model_runtime.main_model.SILKITAdditionalConfiguration.ConnectionPoints.append(scp)
            module = vafmodel.PlatformModule(
                Name=f"{interface_type}Module_{found_interface[0].ModuleInterfaceRef.Name}_{instance_name}",
                Namespace=found_interface[0].ModuleInterfaceRef.Namespace,
                ModuleInterfaceRef=found_interface[0].ModuleInterfaceRef,
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=scp,
            )
            getattr(model_runtime.main_model, f"Platform{interface_type}Modules").append(module)

        # add the mapping
        mapping = vafmodel.InterfaceInstanceToModuleMapping(InstanceName=instance_name, ModuleRef=module)
        found_am[0].InterfaceInstanceToModuleMappings.append(mapping)
        model_runtime.connected_interfaces[f"{app_module.Namespace}::{app_module.Name}"].append(instance_name)

    def connect_consumed_interface_to_silkit(
        self,
        app_module: ApplicationModule,
        instance_name: str,
        silkit_address_instance_name: str = "",
        registry_uri: str = "silkit://localhost:8500",
    ) -> None:
        """Connects a module interface of an application module as a silkit consumer

        Args:
            app_module (vafpy.ApplicationModule): Application module instance to
            connect
            instance_name (str): The interface instance name
            silkit_address_instance_name (str): The silkit instance address
            registry_uri (str): The silkit registry uri to use

        Raises:
            ModelError: If the application module was not found,
                        if the instance was not found,
                        or if there is a missconfiguration of silkit consumer modules
        """
        self.__connect_interface_to_silkit(
            app_module, instance_name, silkit_address_instance_name, registry_uri, interface_type="Consumed"
        )

    def connect_provided_interface_to_silkit(
        self,
        app_module: ApplicationModule,
        instance_name: str,
        silkit_address_instance_name: str = "",
        registry_uri: str = "silkit://localhost:8500",
    ) -> None:
        """Connects a module interface of an application module as a silkit provider

        Args:
            app_module (vafpy.ApplicationModule): Application module instance to
            connect
            instance_name (str): The interface instance name
            silkit_address_instance_name (str): The silkit instance address
            registry_uri (str): The silkit registry uri to use

        Raises:
            ModelError: If the application module was not found,
                        if the instance was not found,
                        or if there is a missconfiguration of silkit provider modules
        """

        self.__connect_interface_to_silkit(
            app_module, instance_name, silkit_address_instance_name, registry_uri, interface_type="Provided"
        )
