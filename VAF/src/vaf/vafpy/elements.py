"""Abstraction layer for vafmodel.ModuleInterfaces in Config as Code"""

from copy import deepcopy
from typing import Any, List, Optional

from typing_extensions import Self

from vaf import vafmodel
from vaf.cli_core.common.utils import create_name_namespace_full_name

from .core import ModelError
from .datatypes import VafpyAbstractDatatypeTyperef, VafpyDataTypeRef
from .factory import VafpyAbstractElement
from .model_runtime import model_runtime
from .task import Task

# pylint: disable = too-few-public-methods
# pylint: disable = unused-private-member # Used via decorators
# pylint: disable = super-init-not-called # DUE to decorators' use
# pylint: disable = unused-argument # DUE to overload in decorator
# pylint: disable = protected-access
# mypy: disable-error-code="misc"

ElementType = vafmodel.ApplicationModule | vafmodel.PlatformModule


class ModuleInterface(vafmodel.ModuleInterface, VafpyAbstractElement):
    """Represents a VAF module interface"""

    @classmethod
    def _build_instance(cls, obj: Optional[Self] = None, **kwargs: Any) -> Optional[Self]:
        """Method to build an vafpy module interface
        Args:
            obj: object to be built
            kwargs: attributes of the object
        """
        # call parent's build
        obj = super()._build_instance(obj, **kwargs)
        assert obj is not None
        # append element name to internal interfaces
        model_runtime.internal_interfaces.append(obj.Name)

        return obj

    def __init__(self, name: str, namespace: str, operation_output_namespace: Optional[str] = None) -> None:
        self._build_instance(self, Name=name, Namespace=namespace, OperationOutputNamespace=operation_output_namespace)

    def add_data_element(self, name: str, datatype: VafpyDataTypeRef) -> None:
        """Add a data element to the module interface

        Args:
            name (str): Unique name for the data element
            datatype (VafpyDataTypeRef): VAF Datatype of the element

        Raises:
            ModelError: If a data element with the same name already exists.
        """
        data_element_names = [da.Name for da in self.DataElements]
        if name in data_element_names:
            raise ModelError(f"Duplicated DataElement {name} for inter  face {self.Namespace}:{self.Name}.")

        self.DataElements.append(
            vafmodel.DataElement(
                Name=name,
                TypeRef=datatype._get_type_ref(),
            )
        )

        # borrow check typeref from VafpyAbstractDatatypeTyperef
        VafpyAbstractDatatypeTyperef._check_typeref(datatype)

        model_runtime.used_module_interfaces[create_name_namespace_full_name(self.Name, self.Namespace)].append(
            create_name_namespace_full_name(datatype.Name, datatype.Namespace)
        )

    def add_operation(
        self,
        name: str,
        in_parameter: dict[str, VafpyDataTypeRef] | None = None,
        out_parameter: dict[str, VafpyDataTypeRef] | None = None,
        inout_parameter: dict[str, VafpyDataTypeRef] | None = None,
    ) -> None:
        """
        Add an operation to the module interface.

        Args:
            name (str): Unique name for the operation.
            in_parameter (dict[str, VafpyDataTypeRef], optional): Dictionary of input parameters.
            Defaults to None.
            out_parameter (dict[str, VafpyDataTypeRef], optional): Dictionary of output parameters.
            Defaults to None.
            inout_parameter (dict[str, VafpyDataTypeRef], optional): Dictionary of input/output
            parameters. Defaults to None.

        Raises:
            ModelError: If an operation with the same name already exists.
        """
        # consolidate parameters
        params: dict[vafmodel.ParameterDirection, dict[str, VafpyDataTypeRef]] = {
            vafmodel.ParameterDirection.IN: in_parameter if in_parameter is not None else {},
            vafmodel.ParameterDirection.OUT: out_parameter if out_parameter is not None else {},
            vafmodel.ParameterDirection.INOUT: inout_parameter if inout_parameter is not None else {},
        }

        operation_names = [op.Name for op in self.Operations]
        if name in operation_names:
            raise ModelError(f"Duplicated operation {name} for interface {self.Namespace}:{self.Name}.")

        function_parameters: List[vafmodel.Parameter] = []

        for param_direction, param_dict in params.items():
            for param_name, datatype in param_dict.items():
                function_parameters.append(
                    vafmodel.Parameter(Name=param_name, TypeRef=datatype._get_type_ref(), Direction=param_direction)
                )
                # borrow check typeref from VafpyAbstractDatatypeTyperef
                VafpyAbstractDatatypeTyperef._check_typeref(datatype)

        self.Operations.append(vafmodel.Operation(Name=name, Parameters=function_parameters))


class ApplicationModule(vafmodel.ApplicationModule, VafpyAbstractElement):
    """Represents a VAF application module"""

    # pylint: disable-next=too-many-positional-arguments,too-many-arguments
    def __init__(
        self,
        name: str,
        namespace: str,
        consumed_interfaces: Optional[List[vafmodel.ApplicationModuleConsumedInterface]] = None,
        provided_interfaces: Optional[List[vafmodel.ApplicationModuleProvidedInterface]] = None,
        tasks: Optional[List[vafmodel.ApplicationModuleTasks]] = None,
    ) -> None:
        self._build_instance(
            self,
            Name=name,
            Namespace=namespace,
            ConsumedInterfaces=consumed_interfaces if consumed_interfaces is not None else [],
            ProvidedInterfaces=provided_interfaces if provided_interfaces is not None else [],
            ImplementationProperties=vafmodel.ImplementationProperty(GenerateUnitTestStubs=True),
            Tasks=tasks if tasks is not None else [],
        )

    def __add_interface(
        self, instance_name: str, interface: ModuleInterface, interface_type: str, is_optional: bool = False
    ) -> None:
        """Add a consumed interface to the AppModule

        Args:
            instance_name (str): Unique name for the interface instance
            interface (vafpy.ModuleInterface): The module interface to add
            interface_type (str): consumed/provided
            is_optional (bool): Wheter the interface is mandatory for the AppModule to start

        Raises:
            ModelError: If a consumed interface with the same name already exists.
        """
        vafmodel_interfaces = getattr(self, f"{interface_type.capitalize()}Interfaces")
        assert isinstance(vafmodel_interfaces, List)
        mi_names = [mi.InstanceName for mi in vafmodel_interfaces]
        if instance_name in mi_names:
            raise ModelError(
                f"Duplicated {interface_type} interface {instance_name}for AppModule {self.Namespace}::{self.Name}."
            )

        vafmodel_interfaces.append(
            # vafmodel.ApplicationModuleConsumedInterface or vafmodel.ApplicationModuleProvidedInterface
            getattr(vafmodel, f"ApplicationModule{interface_type.capitalize()}Interface")(
                InstanceName=instance_name,
                ModuleInterfaceRef=interface,
                # IsOptional is only available for Consumed
                **({"IsOptional": is_optional} if interface_type == "consumed" else {}),
            )
        )
        model_runtime.add_used_module_interfaces(interface)

    def add_consumed_interface(self, instance_name: str, interface: ModuleInterface, is_optional: bool = False) -> None:
        """Add a consumed interface to the AppModule

        Args:
            instance_name (str): Unique name for the interface instance
            interface (vafpy.ModuleInterface): The module interface to add
            is_optional (bool): Wheter the interface is mandatory for the AppModule to start

        Raises:
            ModelError: If a consumed interface with the same name already exists.
        """
        self.__add_interface(instance_name, interface, interface_type="consumed", is_optional=is_optional)

    def add_provided_interface(self, instance_name: str, interface: ModuleInterface) -> None:
        """Add a provided interface to the app module

        Args:
            instance_name (str): Unique name for the interface instance
            interface (vafpy.ModuleInterface): The module interface to add

        Raises:
            ModelError: If a provided interface with the same name already exists.
        """
        self.__add_interface(instance_name, interface, interface_type="provided")

    def _get_task_ref(self, task: vafmodel.ApplicationModuleTasks | Task) -> vafmodel.ApplicationModuleTasks:
        if isinstance(task, vafmodel.ApplicationModuleTasks):
            return task
        return task.model

    def add_task(self, task: vafmodel.ApplicationModuleTasks | Task) -> None:
        """Add a task to the app module

        Args:
            task (vafmodel.ApplicationModuleTasks | vafpy.Task): Task to add

        Raises:
            ModelError: If a task with the same name already exists.
        """
        task_names = [task.Name for task in self.Tasks]
        task_ref = self._get_task_ref(task)
        if task_ref.Name in task_names:
            raise ModelError(f"Duplicated task {task_ref.Name} for AppModule {self.Namespace}::{self.Name}.")

        self.Tasks.append(task_ref)

    def add_task_chain(
        self,
        tasks: List[vafmodel.ApplicationModuleTasks | Task],
        run_after: List[vafmodel.ApplicationModuleTasks | Task] | None = None,
        increment_preferred_offset: bool = False,
    ) -> None:
        """
        Add multiple tasks with a strict execution order to the app module

        Args:
            tasks (List[vafmodel.ApplicationModuleTasks | vafpy.Task]): Tasks to add
            run_after (List[vafmodel.ApplicationModuleTasks | vafpy.Task]): Tasks that should run before this one
            increment_preferred_offset (bool): Uses the preferred offset of the first task as base value and increments
            it for every following task

        Raises:
            ModelError: If a task with the same name already exists.
        """
        task_names = [task.Name for task in self.Tasks]
        last_name = None
        current_offset = self._get_task_ref(tasks[0]).PreferredOffset or 0
        for task in tasks:
            task_ref = self._get_task_ref(task)
            if task_ref.Name in task_names:
                raise ModelError(f"Duplicated task {task_ref.Name} for AppModule {self.Namespace}::{self.Name}.")

            run_after_ = task_ref.RunAfter + [self._get_task_ref(task_).Name for task_ in run_after or []]
            if last_name:
                run_after_.append(last_name)

            local_task = deepcopy(task_ref)
            local_task.RunAfter = run_after_
            if increment_preferred_offset:
                local_task.PreferredOffset = current_offset
            self.Tasks.append(local_task)

            if increment_preferred_offset:
                current_offset += 1
            last_name = task_ref.Name
            task_names.append(task_ref.Name)


# pylint: disable = too-many-ancestors
class PlatformConsumerModule(vafmodel.PlatformModule, VafpyAbstractElement):
    """Represents a VAF platform consumer module"""

    def __init__(self, name: str, namespace: str, module_interface: ModuleInterface) -> None:
        self._build_instance(self, Name=name, Namespace=namespace, ModuleInterfaceRef=module_interface)


class PlatformProviderModule(PlatformConsumerModule):
    """Represents a VAF platform provider module"""
