"""Runtime for building a complete model with config as code"""

from collections import defaultdict
from typing import Dict, List, Tuple

from vaf import vafmodel
from vaf.cli_core.common.utils import create_name_namespace_full_name

from .core import ModelError, VafpyAbstractBase


class ModelRuntime:
    """Runtime to store modeling progress"""

    # Dict that stores namespace & name of used module interfaces
    # and their respectives data_elements & operations typerefs
    used_module_interfaces: Dict[str, List[str]] = {}
    # List that stores the name of internal interfaces
    internal_interfaces: List[str] = []
    # List that stores the name of connected internal interfaces
    connected_interfaces: defaultdict[str, List[str]] = defaultdict(list)
    # dictionary that stores vafpy elements by namespace (for CaC)
    # Reason: getter function in runtime.py can get the vafpy elements
    # CaC and some generations are namespace-based: One can access the model
    # by calling <vafpy_element>.vafmodel
    element_by_namespace: Dict[str, Dict[str, Dict[str, VafpyAbstractBase]]] = {}

    def __init__(self) -> None:
        self.main_model = vafmodel.MainModel()

    def reset(self) -> None:
        """Resets the model runtime"""
        self.main_model = vafmodel.MainModel()
        self.used_module_interfaces.clear()
        self.internal_interfaces.clear()
        self.connected_interfaces.clear()
        self.element_by_namespace.clear()

    @staticmethod
    def __get_element_type(vaf_model_obj: VafpyAbstractBase) -> str:
        """Method to get element type of a vafmodel object
        Args:
            vaf_model_obj: vafmodel obj
        Return:
            data type of vafmodel in plural (Enums instead of VafEnums)
        """
        return type(vaf_model_obj).__name__.removeprefix("Vaf") + "s"

    def __get_element_data(self, element: VafpyAbstractBase) -> Tuple[str, str, str]:
        """Method to get data of a vafpy/vafmodel object
        Args:
            element: vafpy/vafmodel object
        Return:
            Tuple that contains: object's name, object's namespace, element's type
        """
        return (
            element.Name,
            element.Namespace,
            self.__get_element_type(element),
        )

    def add_element(self, element: VafpyAbstractBase, imported: bool = False) -> None:
        """Adds an element to the model
        Args:
            element: element to be added to the model
            imported: boolean to define if it's addition for import/load
        Raises:
            ModelError: if element already exists
        """
        if isinstance(element, VafpyAbstractBase):
            # get element data
            name, namespace, element_type = self.__get_element_data(element)

            # add to main model if not yet recorded
            if self.element_by_namespace.get(namespace, {}).get(element_type, {}).get(name, None) is None:
                getattr(
                    self.main_model.DataTypeDefinitions if element_type in vafmodel.data_types else self.main_model,
                    element_type,
                ).append(element)

            # add vafpy objects to element_by_namespace database
            if namespace not in self.element_by_namespace:
                self.element_by_namespace[namespace] = {}
            if element_type not in self.element_by_namespace[namespace]:
                self.element_by_namespace[namespace][element_type] = {name: element}
            else:
                duplicate = name in self.element_by_namespace[namespace][element_type]
                if not duplicate:
                    self.element_by_namespace[namespace][element_type][name] = element
                elif not imported:
                    # raise ModelError for duplicates if not imported
                    # means: user wrongly modelled an object twice
                    # This must be simply silently ignored in import
                    # operations (via import_json())
                    raise ModelError(
                        "".join(
                            [
                                f"Failed to add a duplicate for MainModel Element {element_type}:"
                                f" with Identifier: {namespace}::{name}"
                            ]
                        )
                    )

            # special operations for specific elements
            # ModuleInterface, PlatformModule, Executable
            if isinstance(element, vafmodel.PlatformModule):
                self.add_used_module_interfaces(element.ModuleInterfaceRef)
            elif not imported:
                if isinstance(element, vafmodel.ModuleInterface):
                    self.add_used_module_interfaces(element)
                elif isinstance(element, vafmodel.ApplicationModule):
                    self.add_used_module_interfaces(
                        [mi.ModuleInterfaceRef for mi in element.ConsumedInterfaces + element.ProvidedInterfaces]
                    )

    def remove_element(self, element: VafpyAbstractBase) -> None:
        """Remove an element from the model
        Args:
            element: element to be removed from the model
        """
        if isinstance(element, VafpyAbstractBase):
            name, namespace, element_type = self.__get_element_data(element)

            if name in self.element_by_namespace[namespace][element_type]:
                # remove from main_model via model from internal lookup
                # reason: element is a deepcopy and might not the same object
                # like the one in the model that needs to be deleted
                getattr(
                    self.main_model.DataTypeDefinitions if element_type in vafmodel.data_types else self.main_model,
                    element_type,
                ).remove(self.element_by_namespace[namespace][element_type][name])
                # remove element from internal lookup
                del self.element_by_namespace[namespace][element_type][name]

            if not self.element_by_namespace[namespace][element_type]:
                del self.element_by_namespace[namespace][element_type]

            if not self.element_by_namespace[namespace]:
                del self.element_by_namespace[namespace]

            # special operations for specific elements
            # ModuleInterface, PlatformModule, Executable
            if isinstance(element, vafmodel.ModuleInterface):
                self.remove_used_module_interfaces(element)
            elif isinstance(element, vafmodel.PlatformModule):
                self.remove_used_module_interfaces(element.ModuleInterfaceRef)
            elif isinstance(element, vafmodel.ApplicationModule):
                self.remove_used_module_interfaces(
                    [mi.ModuleInterfaceRef for mi in element.ConsumedInterfaces + element.ProvidedInterfaces]
                )

    def replace_element(self, element: VafpyAbstractBase) -> None:
        """Replace an element with same name & namespace
        Args:
            element: element to be replaced in the model
        """
        if isinstance(element, VafpyAbstractBase):
            # replace element from model by namespace
            name, namespace, element_type = self.__get_element_data(element)
            if name in self.element_by_namespace[namespace][element_type]:
                self.element_by_namespace[namespace][element_type][name] = element
                # replace in main model
                element_list = getattr(
                    self.main_model.DataTypeDefinitions if element_type in vafmodel.data_types else self.main_model,
                    element_type,
                )
                for idx, el in enumerate(element_list):
                    if el.Name == element.Name and el.Namespace == element.Namespace:
                        element_list[idx] = element
                        break

    def add_used_module_interfaces(
        self, module_interfaces: List[vafmodel.ModuleInterface] | vafmodel.ModuleInterface
    ) -> None:
        """Adds a module interface to the used module interface
        Args:
            module_interfaces (vafmodel.ModuleInterface): list of module interface
        """
        if not isinstance(module_interfaces, List):
            module_interfaces = [module_interfaces]
        for mi in module_interfaces:
            module_interface_id = create_name_namespace_full_name(mi.Name, mi.Namespace)
            if module_interface_id not in self.used_module_interfaces:
                self.used_module_interfaces[module_interface_id] = list(
                    set(
                        [
                            create_name_namespace_full_name(data_el.TypeRef.Name, data_el.TypeRef.Namespace)
                            for data_el in mi.DataElements
                        ]
                        + [
                            create_name_namespace_full_name(
                                surgery_parameter.TypeRef.Name, surgery_parameter.TypeRef.Namespace
                            )
                            for surgery in mi.Operations
                            for surgery_parameter in surgery.Parameters
                        ]
                    )
                )

    def remove_used_module_interfaces(
        self, module_interfaces: List[vafmodel.ModuleInterface] | vafmodel.ModuleInterface
    ) -> None:
        """Adds a module interface to the used module interface
        Args:
            module_interfaces (vafmodel.ModuleInterface): list of module interface
        """
        if not isinstance(module_interfaces, List):
            module_interfaces = [module_interfaces]
        for mi in module_interfaces:
            module_interface_id = create_name_namespace_full_name(mi.Name, mi.Namespace)
            if module_interface_id in self.used_module_interfaces:
                del self.used_module_interfaces[module_interface_id]


# prevent cylic dependency
model_runtime = ModelRuntime()
