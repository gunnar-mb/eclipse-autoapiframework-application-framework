"""Runtime for building a complete model with config as code"""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from vaf import vafmodel
from vaf.cli_core.common.utils import ProjectType, concat_str_to_path, create_name_namespace_full_name

from .core import ModelError, VafpyAbstractBase
from .datatypes import Array, Enum, Map, String, Struct, TypeRef, Vector
from .elements import (
    ApplicationModule,
    ModuleInterface,
    PlatformConsumerModule,
    PlatformProviderModule,
)
from .model_runtime import ModelRuntime, model_runtime
from .validator import Validator

# List of data types for cleanups
## Special: Structs & Maps
## Generic: Arrays, Enums (VafEnums -> Enums), Strings, TypeRefs, Vectors
special_dtd_cleanup_data_types = ["Structs", "Maps"]

generic_dtd_cleanup_data_types = [
    data_type for data_type in vafmodel.data_types if data_type not in special_dtd_cleanup_data_types
]


# Dictionary that translates a string of element type to its actual class
model_element_converter: Dict[str, Any] = {
    "ApplicationModule": ApplicationModule,
    "Array": Array,
    "Enum": Enum,
    "Map": Map,
    "ModuleInterface": ModuleInterface,
    "PlatformConsumerModule": PlatformConsumerModule,
    "PlatformProviderModule": PlatformProviderModule,
    "String": String,
    "Struct": Struct,
    "TypeRef": TypeRef,
    "Vector": Vector,
}


def _add_struct_to_graph(graph: nx.DiGraph, structs: List[VafpyAbstractBase]) -> Tuple[nx.DiGraph, List[str]]:
    """Function to add a list of struct to graph and collect base types from their subelements
    Args:
        graph: Directional Graph
        structs: List of structs
        dtd_namespace: namespace of current DataTypeDef
    Returns:
        updated Directional Graph
        list of new base types
    """
    new_base_types: List[str] = []
    for struct in structs:
        assert isinstance(struct, Struct)
        # add struct to graph
        struct_identifier = create_name_namespace_full_name(struct.Name, struct.Namespace)
        graph.add_node(struct_identifier)

        # add subelements to struct
        for subelement in struct.SubElements:
            subelement_identifier = create_name_namespace_full_name(subelement.Name, struct_identifier)
            graph.add_edge(struct_identifier, subelement_identifier)
            typeref_identifier = create_name_namespace_full_name(subelement.TypeRef.Name, subelement.TypeRef.Namespace)

            # typeref non base types: connect typeref to subelements
            graph.add_edge(subelement_identifier, typeref_identifier)
            if not subelement.TypeRef.Namespace:
                # add base types
                new_base_types.append(typeref_identifier)
    return graph, new_base_types


def _add_generic_data_types_to_graph(
    graph: nx.DiGraph,
    generic_data: List[VafpyAbstractBase],
) -> Tuple[nx.DiGraph, List[str]]:
    """Function to add a list of generic data types to graph
        Generic Data Types: All Data Types that has TypeRef as direct attribute
        -> Arrays, Enums, Strings, TypeRefs, Vectors
    Args:
        graph: Directional Graph
        generic_data: List of Generic Data
        dtd_namespace: namespace of current DataTypeDef
    Returns:
        updated Directional Graph
        list of new base types
    """
    new_base_types: List[str] = []

    for data in generic_data:
        assert isinstance(data, (Array, Enum, String, TypeRef, Vector))
        # add data to graph
        data_identifier = create_name_namespace_full_name(data.Name, data.Namespace)
        graph.add_node(data_identifier)

        # if data has typeref then create the typeref node and connect it to the data
        if isinstance(data, (Array, TypeRef, Vector)):
            # typeref non base types: connect typeref to data
            graph.add_edge(
                data_identifier,
                create_name_namespace_full_name(data.TypeRef.Name, data.TypeRef.Namespace),
            )
            # Vectors, Arrays, TypeRefs: if TypeRef.Namespace is empty -> base types
            if data.TypeRef.Namespace == "":
                new_base_types.append(data_identifier)
        else:
            # Not Vectors, Arrays, TypeRefs: base types
            new_base_types.append(data_identifier)

    return graph, new_base_types


def _add_maps_to_graph(graph: nx.DiGraph, maps: List[VafpyAbstractBase]) -> Tuple[nx.DiGraph, List[str]]:
    """Function to add a list of maps to graph
    Args:
        graph: Directional Graph
        maps: List of Maps
        dtd_namespace: namespace of current DataTypeDef
    Returns:
        updated Directional Graph
        list of new base types
    """
    new_base_types: List[str] = []
    for map_data in maps:
        assert isinstance(map_data, Map)
        map_identifier = create_name_namespace_full_name(map_data.Name, map_data.Namespace)
        for type_ref in [
            getattr(map_data, f"Map{which_type_ref.capitalize()}TypeRef") for which_type_ref in ["key", "value"]
        ]:
            # connect both typerefs to data
            graph.add_edge(map_identifier, create_name_namespace_full_name(type_ref.Name, type_ref.Namespace))
            # add to base types if typeref namespace is empty
            if type_ref.Namespace == "":
                new_base_types.append(map_identifier)
    return graph, new_base_types


# suffix for old json
old_json_suffix = "~"


def __get_all_nested_namespaces_references(model: ModelRuntime) -> Tuple[nx.DiGraph, List[str]]:
    """Get all namespaces references
       E.g.: a::b::c refers to a::b::d -> if one needs a::b::c, a::b::d is also needed

    Args:
        model: ModelRuntime whose artifacts are to be reduced

    Returns:
        Directional Graph of nested references of namespaces
        List of all strings of base types data
    """
    graph = nx.DiGraph()
    base_types: List[str] = []

    for ns_elements_data in model.element_by_namespace.values():
        # Special Data Types: Structs & Maps

        ## Structs due to the real type refs referenced in the subelements level
        ## add structs & their subelements reference to graph
        graph, new_base_types = _add_struct_to_graph(graph, list(ns_elements_data.get("Structs", {}).values()))
        base_types += new_base_types

        ## Maps due to typerefs referenced in key & value
        ## add key & value reference to graph
        graph, new_base_types = _add_maps_to_graph(graph, list(ns_elements_data.get("Maps", {}).values()))
        base_types += new_base_types

        # Generic Data Types: All Data Types that have TypeRef as direct attribute
        ## arrays, vectors, strings, typeref, enums
        for data_type in generic_dtd_cleanup_data_types:
            graph, new_base_types = _add_generic_data_types_to_graph(
                graph, list(ns_elements_data.get(data_type, {}).values())
            )
            base_types += new_base_types

    return graph, list(set(base_types))


def __get_used_namespaces(
    module_interfaces_data: Dict[str, List[str]], nested_references_graph: nx.DiGraph, base_types_list: List[str]
) -> List[str]:
    """Get lists of all used namespaces by using tree
    Args:
        module_interfaces_data: Dictionary that contains id of used module interfaces and
                                typerefs of their data elements
        nested_references_graph: graph object that represents all references between namespaces
        base_types_list: list that contains all base types
    Returns:
        Lists of all used namespaces
    """
    used_namespaces: List[str] = []

    # loop over data elements in module interfaces
    for data_element_typeref_ids in module_interfaces_data.values():
        # add all data elements' typeref to used namespaces
        used_namespaces += data_element_typeref_ids
        for data_element_typeref_id in data_element_typeref_ids:
            ### DEBUGGING nx.DiGraphs ###
            # getting list of all paths
            # list(nx.all_simple_paths(graph, node1, node2))

            # getting all direct "neighbour" nodes pointed out by a node
            # list(graph.out_edges(node))
            #############################

            # check graph only if data_element_identifier is a node in the graph
            if nested_references_graph.has_node(data_element_typeref_id):
                # get all nested references by checking all paths between data element and all base types
                used_namespaces += [
                    referenced_nodes
                    for base_type in base_types_list  # loop over all base types
                    for path in list(
                        nx.all_simple_paths(nested_references_graph, data_element_typeref_id, base_type)
                    )  # get all paths
                    for referenced_nodes in path[1:]  # ignore first element (data_element), since already added
                ]

    return list(set(used_namespaces))


def __remove_unused_artifacts(model: ModelRuntime) -> ModelRuntime:
    """Remove unused artifacts of a model
    Args:
        model: ModelRuntime whose artifacts are to be reduced

    Returns:
        ModelRuntime with reduced artifacts
    """
    # get all nested references of namespaces
    namespace_references, all_base_types = __get_all_nested_namespaces_references(model)
    # get all needed custom namespaces
    used_namespaces: List[str] = __get_used_namespaces(
        model.used_module_interfaces, namespace_references, all_base_types
    )

    # deepcopy since the real dictionary might change dynamically during the loop
    for ns_elements_data in deepcopy(model.element_by_namespace).values():
        # Structs: Special Case due to possible reference by their SubElements
        # structs need to be looped also in the Subelements
        for struct in ns_elements_data.get("Structs", {}).values():
            assert isinstance(struct, Struct)
            struct_identifier = create_name_namespace_full_name(struct.Name, struct.Namespace)
            # check if whole struct is needed
            if struct_identifier not in used_namespaces:
                used_subelements = [
                    subelement
                    for subelement in struct.SubElements
                    if create_name_namespace_full_name(subelement.Name, subelement.TypeRef.Namespace) in used_namespaces
                ]
                # remove struct if it's not needed
                if used_subelements:
                    struct.SubElements = used_subelements
                    model.replace_element(struct)
                else:
                    model.remove_element(struct)

        # get used arrays, enums, vectors, strings, typerefs, maps
        ## Maps is not special here: since they can't be referenced by their children attribute
        for dtd_type_str in [*generic_dtd_cleanup_data_types, "Maps"]:
            for data in ns_elements_data.get(dtd_type_str, {}).values():
                assert isinstance(data, (Array, Enum, Map, String, TypeRef, Vector))
                if create_name_namespace_full_name(data.Name, data.Namespace) not in used_namespaces:
                    model.remove_element(data)

        # loop module interfaces
        for module_interface in ns_elements_data.get("ModuleInterfaces", {}).values():
            assert isinstance(module_interface, ModuleInterface)
            module_interface_identifier = create_name_namespace_full_name(
                module_interface.Name, module_interface.Namespace
            )
            # ignore if already listed as used module interfaces
            # only check if not listed as used module interfaces and identifier not in used_namespaces
            if (
                module_interface_identifier not in model.used_module_interfaces
                and module_interface_identifier not in used_namespaces
            ):
                # check if module interface is not used (possibility as needed parents or grandparents)
                # get used module interface data elements
                # first data element also needed as it's for itself
                used_data_elements = module_interface.DataElements[0:1] + [
                    data_element
                    for data_element in module_interface.DataElements
                    if (data_element.Name == data_element.TypeRef.Name)
                    and (
                        create_name_namespace_full_name(data_element.TypeRef.Name, data_element.TypeRef.Namespace)
                        in used_namespaces
                    )
                ]

                # if found used data element == itself/empty then it's unused
                if len(used_data_elements) <= 1:
                    # remove module interface
                    model.remove_element(module_interface)
                # if data elements differ then replace
                elif len(used_data_elements) != len(module_interface.DataElements):
                    module_interface.DataElements = used_data_elements
                    model.replace_element(module_interface)

    return model


def get_main_model() -> Any:
    """Get the main model as JSON

    Returns:
        Any: The model
    """
    return json.loads(model_runtime.main_model.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True))


def __save_model_artifacts(
    path: Path, project_type: ProjectType, keys: Optional[List[str]] = None, cleanup: bool = False
) -> None:
    """Saves the main model to file

    Args:
        path (Path): Path to the file
        project_type (ProjectType): Type of the current project
        cleanup: (bool): Boolean flag to remove unused data elements & module interfaces in model
        keys: (list[str]): Key to be saved in the export for partial save
    """
    if path.exists():
        print(f"File {path.name} already exists. Backup existing file to {path.name}{old_json_suffix}")
        backup_output_path = concat_str_to_path(path, old_json_suffix)
        backup_output_path.write_bytes(path.read_bytes())

    if cleanup:
        __remove_unused_artifacts(model_runtime)
    Validator(project_type).validate_model(model_runtime)

    if keys is not None:
        target_model: vafmodel.MainModel = vafmodel.MainModel()
        for key in keys:
            if hasattr(target_model, key):
                getattr(target_model, key).extend(getattr(model_runtime.main_model, key))

    with open(path, "w", encoding="utf-8") as f:
        f.write(
            (model_runtime.main_model if keys is None else target_model).model_dump_json(
                indent=2, exclude_none=True, exclude_defaults=True, by_alias=True
            )
        )


def save_main_model(path: Path, project_type: ProjectType, cleanup: bool = False) -> None:
    """Saves the main model to file

    Args:
        path (Path): Path to the file
        project_type (ProjectType): Type of the current project
        cleanup: (bool): Boolean flag to remove unused data elements & module interfaces in model
    """
    __save_model_artifacts(path, project_type, keys=None, cleanup=cleanup)


def save_part_of_main_model(path: Path, keys: list[str], project_type: ProjectType, cleanup: bool = False) -> None:
    """Saves the main model to file

    Args:
        path (Path): Path to the file
        keys: (list[str]): Key to be saved in the export
        project_type (ProjectType): Type of the current project
        cleanup: (bool): Boolean flag to remove unused data elements & module interfaces in model
    """
    __save_model_artifacts(path, project_type, keys=keys, cleanup=cleanup)


def __create_vafpy_from_imported_vafmodel(data: vafmodel.ModelElement, element_type: str) -> None:
    # construct vafpy object from vafmodel
    # vafpy.<Element>.(vafmodel.ModelElement)
    assert element_type in model_element_converter, f"ERROR: invalid Element {element_type}"
    model_element_converter[element_type]._from_vaf_model(vaf_model=data, imported=True)  # pylint:disable=protected-access


def __read_model(path: str, import_type: str, am_path: Optional[str] = None) -> None:
    """Function to read model_runtime from a model file
    Args:
        path: path to model file
        import_type: type of import: "model" or "app-module"
    """
    imported_model = vafmodel.load_json(path)

    assert import_type in ("app-module", "model")
    if import_type == "app-module":
        assert am_path is not None

    for key, value in vars(imported_model).items():
        if key == "DataTypeDefinitions":
            for dtd_type_str in vafmodel.data_types:
                for new_data in getattr(value, dtd_type_str):
                    # create vafpy object in model_runtime based on vafmodel object
                    __create_vafpy_from_imported_vafmodel(new_data, dtd_type_str.removesuffix("s"))
        elif key in ["ModuleInterfaces", "PlatformConsumerModules", "PlatformProviderModules", "ApplicationModules"]:
            for val in value:
                # if import_app_module -> add installation paths to app modules
                if import_type == "app-module" and isinstance(val, vafmodel.ApplicationModule):
                    if val.ImplementationProperties is None:
                        val.ImplementationProperties = vafmodel.ImplementationProperty()
                    val.ImplementationProperties.InstallationPath = am_path
                # create vafpy object in model_runtime based on vafmodel object
                __create_vafpy_from_imported_vafmodel(val, key.removesuffix("s"))
        else:  # other keys
            if import_type == "model":
                if isinstance(value, List) and len(value) > 0:
                    setattr(
                        model_runtime.main_model,
                        key,
                        getattr(model_runtime.main_model, key) + value,
                    )


def import_model(path: str) -> None:
    """Imports a module from json.
    Merges existing lists, does not overwrite other members.

    Args:
        path (str): Path to the json file
    """
    __read_model(path, import_type="model")


def import_application_module(model_path: str, am_path: str) -> None:  # pylint: disable=too-many-locals, too-many-branches
    """Imports a module from json.
    Merges existing lists, does not overwrite other members.

    Args:
        model_path (str): Path to the json file
        am_path (str): Relative path to the application module
    """
    __read_model(model_path, import_type="app-module", am_path=am_path)


def __get_model_runtime_element(
    name: str, namespace: str, element_type: str, assert_result: bool = True
) -> Optional[VafpyAbstractBase]:
    """Generic function to get element type from model_runtime
    Args:
        name: name of the element
        namespace: namespace of the element
        element_type: type of the element
        assert_result: flag to activate result assertion

    Raises:
        ModelError: if no element found

    Returns:
        Vafpy type belongs to the element
    """
    found = model_runtime.element_by_namespace.get(namespace, {}).get(element_type, {}).get(name, None)
    if assert_result:
        if found is None:
            raise ModelError(f"Could not find {element_type}: {namespace}::{name}!")
    return found


def get_datatype(name: str, namespace: str, datatype: Optional[str] = None) -> VafpyAbstractBase:
    """Gets a datatype

    Args:
        name (str): The name of the datatype
        namespace (str): The namespace of the datatype
        datatype (str): Type of the searched datatype, e.g.: Structs or Vectors
    Raises:
        ModelError: no corresponding datatype is found
    Returns:
        VafpyAbstractDataType: The vafpy datatype object which has vafmodel obj and its reference
    """
    plural_datatype = datatype + "s" if isinstance(datatype, str) else ""
    # if datatypes defined, then look specifically for this data type:
    if datatype is not None and plural_datatype in vafmodel.data_types:
        result = __get_model_runtime_element(name, namespace, plural_datatype)
        assert result.__class__.__name__ == datatype
    else:  # not defined, look over all data types
        for dt_type in vafmodel.data_types:
            # don't raise errors if nothing found!
            result = __get_model_runtime_element(name, namespace, dt_type.removesuffix("s"), assert_result=False)
            if result is not None:
                break
    if not isinstance(result, VafpyAbstractBase):
        raise ModelError(f"Gotten datatype {namespace}::{name} has invalid type: {type(result)}")
    return result


def get_module_interface(name: str, namespace: str) -> ModuleInterface:
    """Gets a module interface by full name

    Args:
        name (str): The name of the module interface
        namespace (str): The namespace of the module interface

    Returns:
        vafmodel.ModuleInterface: The interface
    """
    result = __get_model_runtime_element(name, namespace, "ModuleInterfaces")
    assert isinstance(result, ModuleInterface)
    return result


def get_platform_consumer_module(name: str, namespace: str) -> PlatformConsumerModule:
    """Gets a platform consumer module by full name

    Args:
        name (str): The name of the module
        namespace (str): The namespace of the module

    Raises:
        ModelError: If the module was not found

    Returns:
        vafmodel.PlatformModule: The found module
    """
    result = __get_model_runtime_element(name, namespace, "PlatformConsumerModules")
    assert isinstance(result, PlatformConsumerModule)
    return result


def get_platform_provider_module(name: str, namespace: str) -> PlatformProviderModule:
    """Gets a platform provider module by full name

    Args:
        name (str): The name of the module
        namespace (str): The namespace of the module

    Raises:
        ModelError: If the module was not found

    Returns:
        vafmodel.PlatformModule: The found module
    """
    result = __get_model_runtime_element(name, namespace, "PlatformProviderModules")
    assert isinstance(result, PlatformProviderModule)
    return result


def get_application_module(name: str, namespace: str) -> ApplicationModule:
    """Gets an application module by full name

    Args:
        name (str): The name of the application module
        namespace (str): The namespace of the application module

    Raises:
        ModelError: If the module is not found

    Returns:
        vafmodel.ApplicationModule: The application module
    """
    result = __get_model_runtime_element(name, namespace, "ApplicationModules")
    assert isinstance(result, ApplicationModule)
    return result
