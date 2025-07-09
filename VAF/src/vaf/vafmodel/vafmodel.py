"""Base data model library of Vehicle Application Framework"""  # pylint: disable=too-many-lines

import json
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ValidationInfo, WithJsonSchema, field_validator, model_validator
from pydantic.config import ConfigDict
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated, Self

# pylint: disable=missing-class-docstring


class VafBaseModel(BaseModel):
    """Base model calls to propagate common model config"""

    model_config = ConfigDict(extra="forbid")


class ModelReferenceError(Exception):
    """Error for invalid references"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class DataType(VafBaseModel):
    Name: str
    Namespace: str


def serialize_data_type_ref(m: DataType) -> str:
    """Serializes a DataType reference

    Args:
        m (DataType): The DataType

    Returns:
        str: The DataType reference
    """
    return m.Namespace + "::" + m.Name if len(m.Namespace) != 0 else m.Name


DataTypeRef = Annotated[
    DataType,
    WithJsonSchema({"type": "string"}),
    PlainSerializer(serialize_data_type_ref, return_type=str),
]


base_types = [
    "int8_t",
    "int16_t",
    "int32_t",
    "int64_t",
    "uint8_t",
    "uint16_t",
    "uint32_t",
    "uint64_t",
    "float",
    "double",
    "bool",
]


data_types = [
    "Strings",
    "Enums",
    "Arrays",
    "Vectors",
    "Maps",
    "Structs",
    "TypeRefs",
]


def validate_type_ref(raw: str | DataType, info: ValidationInfo) -> DataType:
    """Validates a data type reference.

    Args:
        raw (str): The data type reference.
        info (ValidationInfo): The validation info.

    Raises:
        ModelReferenceError: If the reference was not found.

    Returns:
        str: The reference unmodified.
    """
    if not isinstance(raw, str):
        return raw
    splitted = raw.split("::")
    name = splitted[-1]
    namespace = ""
    if len(splitted) > 1:
        namespace = "::".join(splitted[0 : len(splitted) - 1])

    if (len(namespace) == 0 or namespace == "std") and name in base_types:
        return DataType(Name=name, Namespace=namespace)

    assert isinstance(info.context, dict)
    data_type_definition = info.context["DataTypeDefinitions"]
    for data_type in data_types:
        if data_type in data_type_definition and data_type_definition[data_type] is not None:
            for element in data_type_definition[data_type]:
                if element["Name"] == name:
                    return DataType(Name=name, Namespace=namespace)

    raise ModelReferenceError("Reference not found: " + raw)


###################### model ######################
class BaseType(str, Enum):
    """Enum of all C++ base types"""

    INT8_T = "int8_t"
    INT16_T = "int16_t"
    INT32_T = "int32_t"
    INT64_T = "int64_t"
    UINT8_T = "uint8_t"
    UINT16_T = "uint16_t"
    UINT32_T = "uint32_t"
    UINT64_T = "uint64_t"
    FLOAT = "float"
    DOUBLE = "double"
    BOOL = "bool"


class OriginalEcoSystemEnum(str, Enum):
    SILKIT = "SILKIT"


class String(DataType):
    pass


class EnumLiteral(VafBaseModel):
    Label: str
    Value: int


class VafEnum(DataType):
    BaseType: Optional[DataTypeRef] = None
    Literals: list[EnumLiteral]
    _validate_BaseType = field_validator("BaseType", mode="before")(validate_type_ref)


class Array(DataType):
    TypeRef: DataTypeRef
    Size: int
    _validate_TypeRef = field_validator("TypeRef", mode="before")(validate_type_ref)


class Map(DataType):
    MapKeyTypeRef: DataTypeRef
    MapValueTypeRef: DataTypeRef
    _validate_MapKeyTypeRef = field_validator("MapKeyTypeRef", mode="before")(validate_type_ref)
    _validate_MapValueTypeRef = field_validator("MapValueTypeRef", mode="before")(validate_type_ref)


class TypeRef(DataType):
    TypeRef: DataTypeRef
    _validate_TypeRef = field_validator("TypeRef", mode="before")(validate_type_ref)


class SubElement(VafBaseModel):
    Name: str
    TypeRef: DataTypeRef
    Min: Optional[float] = None
    Max: Optional[float] = None
    _validate_TypeRef = field_validator("TypeRef", mode="before")(validate_type_ref)


class Struct(DataType):
    Name: str
    SubElements: list[SubElement]


class Vector(DataType):
    Name: str
    TypeRef: DataTypeRef
    _validate_TypeRef = field_validator("TypeRef", mode="before")(validate_type_ref)


ModelDataType = Array | VafEnum | Map | String | Struct | TypeRef | Vector


class DataTypeDefinition(VafBaseModel):
    Strings: list[String] = []
    Enums: list[VafEnum] = []
    Arrays: list[Array] = []
    Maps: list[Map] = []
    TypeRefs: list[TypeRef] = []
    Structs: list[Struct] = []
    Vectors: list[Vector] = []

    def extend(self, new_data_type_def: Self) -> None:
        """Function to extend DataTypeDefinition by further DataTypeDefinition
        Args:
            new_data_type_def: to be appended DataTypeDefinition
        """

        for data_type in data_types:
            current_data = getattr(self, data_type)
            new_data = getattr(new_data_type_def, data_type)
            if getattr(new_data_type_def, data_type):
                setattr(self, data_type, current_data + new_data)


class DataElement(VafBaseModel):
    Name: str
    TypeRef: DataTypeRef
    InitialValue: Optional[str] = None
    Min: Optional[float] = None
    Max: Optional[float] = None
    _validate_TypeRef = field_validator("TypeRef", mode="before")(validate_type_ref)


class ParameterDirection(str, Enum):
    IN = "IN"
    OUT = "OUT"
    INOUT = "INOUT"


class Parameter(VafBaseModel):
    Name: str
    TypeRef: DataTypeRef
    Direction: ParameterDirection
    _validate_TypeRef = field_validator("TypeRef", mode="before")(validate_type_ref)


class Operation(VafBaseModel):
    Name: str
    Parameters: list[Parameter] = []


class ModuleInterface(VafBaseModel):
    Name: str
    Namespace: str = Field(
        description="The value of this Tag is applicable when the interface is used for \
                     generation of code. For C++, this will be the namespace while for \
                     Java this will be the package hierarchy. When generating the code \
                     representing the interface, it should be placed in the namespace \
                     given by this parameter. Format: xxx::yyy::zzz."
    )
    OperationOutputNamespace: Optional[str] = None
    DataElements: Annotated[
        list[DataElement],
        Field(
            description="This array contains the definition of the data elements that \
                         are available for the users of the interface. The data element \
                         could either represent a pure data area (attribute/property/field \
                         as in OO terminology) or it can correspond to an event occurring \
                         because of some specific activity inside the module providing the interface."
        ),
    ] = []
    Operations: Annotated[
        list[Operation],
        Field(
            description="This array contains the definition of the operations that \
                         are available for the users of the interface."
        ),
    ] = []

    def __hash__(self) -> int:
        return hash(repr(self))


def serialize_module_interface_ref(m: ModuleInterface) -> str:
    """Serializes a ModuleInterface reference

    Args:
        m (ModuleInterface): The ModuleInterface

    Returns:
        str: The ModuleInterface reference
    """
    return m.Namespace + "::" + m.Name


ModuleInterfaceRefType = Annotated[
    ModuleInterface,
    WithJsonSchema({"type": "string"}),
    PlainSerializer(serialize_module_interface_ref, return_type=str),
]


def resolve_module_interface_ref(raw: str | ModuleInterface, info: ValidationInfo) -> ModuleInterface:
    """Resolves a module interface reference and returns it.

    Args:
        raw (str | ModuleInterface): A module interface reference or a module interface
        info (ValidationInfo): The validation info.

    Raises:
        ModelReferenceError: If the reference was not found.

    Returns:
        ModuleInterface: The module interface.
    """
    if isinstance(raw, str):
        assert isinstance(info.context, dict)
        for m in info.context["ModuleInterfaces"]:
            if m["Namespace"] + "::" + m["Name"] == raw:
                return ModuleInterface.model_validate(m, context=info.context)
        raise ModelReferenceError("Reference not found: " + raw)
    return raw


class DataElementRef(VafBaseModel):
    DataElement: DataElement
    ModuleInterface: ModuleInterface


def serialize_data_element_ref(d: DataElementRef) -> str:
    """Serializes a DataElement reference

    Args:
        d (DataElement): The DataElement

    Returns:
        str: The DataElement reference
    """
    return d.ModuleInterface.Namespace + "::" + d.ModuleInterface.Name + "::" + d.DataElement.Name


DataElementRefType = Annotated[
    DataElementRef,
    WithJsonSchema({"type": "string"}),
    PlainSerializer(serialize_data_element_ref, return_type=str),
]


def resolve_data_element_ref(raw: str | DataElementRef, info: ValidationInfo) -> DataElementRef:
    """Resolves a data element reference and returns it.

    Args:
        raw (str | DataElementRef): A data element reference or a data element
        info (ValidationInfo): The validation info.

    Raises:
        ModelReferenceError: If the reference was not found.

    Returns:
        DataElementRef: The data element reference.
    """
    if isinstance(raw, str):
        assert isinstance(info.context, dict)
        for m in info.context["ModuleInterfaces"]:
            if m["Namespace"] + "::" + m["Name"] == "::".join(raw.split("::")[:-1]):
                for d in m["DataElements"]:
                    if d["Name"] == raw.split("::")[-1]:
                        de = DataElement.model_validate(d, context=info.context)
                        mi = ModuleInterface.model_validate(m, context=info.context)
                        return DataElementRef(DataElement=de, ModuleInterface=mi)
        raise ModelReferenceError("Reference not found: " + raw)
    return raw


class OperationRef(VafBaseModel):
    Operation: Operation
    ModuleInterface: ModuleInterface


def serialize_operation_ref(o: OperationRef) -> str:
    """Serializes a Operation reference

    Args:
        o (Operation): The Operation

    Returns:
        str: The Operation reference
    """
    return o.ModuleInterface.Namespace + "::" + o.ModuleInterface.Name + "::" + o.Operation.Name


OperationRefType = Annotated[
    OperationRef,
    WithJsonSchema({"type": "string"}),
    PlainSerializer(serialize_operation_ref, return_type=str),
]


def resolve_operation_ref(raw: str | OperationRef, info: ValidationInfo) -> OperationRef:
    """Resolves a operation reference and returns it.

    Args:
        raw (str | OperationRef): A operation reference or a operation
        info (ValidationInfo): The validation info.

    Raises:
        ModelReferenceError: If the reference was not found.

    Returns:
        OperationRef: The OperationRef.
    """
    if isinstance(raw, str):
        assert isinstance(info.context, dict)
        for m in info.context["ModuleInterfaces"]:
            if m["Namespace"] + "::" + m["Name"] == "::".join(raw.split("::")[:-1]):
                for o in m["Operations"]:
                    if o["Name"] == raw.split("::")[-1]:
                        o = Operation.model_validate(o, context=info.context)
                        mi = ModuleInterface.model_validate(m, context=info.context)
                        return OperationRef(Operation=o, ModuleInterface=mi)
        raise ModelReferenceError("Reference not found: " + raw)
    return raw


class ApplicationModuleProvidedInterface(VafBaseModel):
    InstanceName: str
    ModuleInterfaceRef: ModuleInterfaceRefType
    _resolve_ModuleInterfaceRef = field_validator("ModuleInterfaceRef", mode="before")(resolve_module_interface_ref)


class ApplicationModuleConsumedInterface(VafBaseModel):
    InstanceName: str
    ModuleInterfaceRef: ModuleInterfaceRefType
    IsOptional: bool = False
    _resolve_ModuleInterfaceRef = field_validator("ModuleInterfaceRef", mode="before")(resolve_module_interface_ref)


class SILKITConnectionPoint(VafBaseModel):
    Name: str
    ServiceInterfaceName: str = Field(
        description="The concept of a service is not defined in SILKIT. This means that we need \
                     to create a service based on the artifacts that are available in SILIT. \
                     This tag defines the name of the service interface that is used by the service."
    )
    RegistryUri: str = Field(
        description="The registry's URI specifies where the registry can be reached. It defaults to \
        silkit://localhost:8500, that is, the registry is reachable via TCP/IP on the 'localhost' on port 8500."
    )


class SILKITAdditionalConfigurationType(VafBaseModel):
    ConnectionPoints: list[SILKITConnectionPoint] = Field(
        description="A connection point in SILKIT is a unique name mapping."
    )


def serialize_connection_point_ref(m: SILKITConnectionPoint) -> str:
    """Serializes a ConnectionPoint reference

    Args:
        m (SILKITConnectionPoint): The ConnectionPoint

    Returns:
        str: The ConnectionPoint reference
    """
    return m.Name


ConnectionPointRefType = Annotated[
    Optional[SILKITConnectionPoint],
    WithJsonSchema({"type": "string"}),
    PlainSerializer(serialize_connection_point_ref, return_type=str),
]


def resolve_connection_point_ref(
    raw: str | None | SILKITConnectionPoint, info: ValidationInfo
) -> SILKITConnectionPoint | None:
    """Resolves a ConnectionPoint reference

    Args:
        raw (str | None | SILKITConnectionPoint): A ConnectionPoint
          reference or a ConnectionPoint
        info (ValidationInfo): The validation info.

    Raises:
        ModelReferenceError: If the reference was not found.

    Returns:
        SILKITConnectionPoint | None: The ConnectionPoint or None if the
          input was None
    """
    if raw is None:
        return raw
    if isinstance(raw, str):
        assert isinstance(info.context, dict)
        if "SILKITAdditionalConfiguration" in info.context and info.context["SILKITAdditionalConfiguration"]:
            for m in info.context["SILKITAdditionalConfiguration"]["ConnectionPoints"]:
                if m["Name"] == raw:
                    return SILKITConnectionPoint.model_validate(m, context=info.context)
        raise ModelReferenceError("Reference not found: " + raw)

    return raw


class PlatformModule(VafBaseModel):
    Name: str
    Namespace: str
    ModuleInterfaceRef: ModuleInterfaceRefType
    OriginalEcoSystem: Optional[OriginalEcoSystemEnum] = None
    ConnectionPointRef: Optional[ConnectionPointRefType] = None
    _resolve_ModuleInterfaceRef = field_validator("ModuleInterfaceRef", mode="before")(resolve_module_interface_ref)
    _resolve_ConnectionPointRef = field_validator("ConnectionPointRef", mode="before")(resolve_connection_point_ref)

    @model_validator(mode="after")
    def check_platform_module(self) -> Self:
        """Checks the platform module for validity

        Raises:
            ValueError: Raised if the connection point reference is of unexpected type

        Returns:
            The Platform Module
        """
        expected = "Undefined"
        if self.OriginalEcoSystem == OriginalEcoSystemEnum.SILKIT:
            expected = "SILKITConnectionPoint"
            if isinstance(self.ConnectionPointRef, SILKITConnectionPoint):
                return self
        if self.OriginalEcoSystem is None:
            expected = "None"
            if self.ConnectionPointRef is None:
                return self
        raise ValueError(
            "Invalid connection point reference set: " + str(self.ConnectionPointRef) + " expected: " + str(expected)
        )


class ImplementationProperty(VafBaseModel):
    GenerateUnitTestStubs: Optional[bool] = None
    InstallationPath: Optional[str] = None


class ApplicationModuleTasks(VafBaseModel):
    Name: str
    Period: str
    PreferredOffset: Optional[int] = None
    RunAfter: list[str] = []


class ApplicationModule(VafBaseModel):
    Name: str
    Namespace: str
    ConsumedInterfaces: list[ApplicationModuleConsumedInterface] = Field(
        description="This array contains the definition of the interfaces \
                    that is used by the module and the modules providing the implementation of the interface."
    )
    ProvidedInterfaces: list[ApplicationModuleProvidedInterface] = Field(
        description="This array defines the interfaces which are provided \
                     by the Application Module. An application can provide 0..N interfaces."
    )
    ImplementationProperties: Annotated[
        Optional[ImplementationProperty],
        Field(description="Includes implementation properties for the Application Module."),
    ] = None
    Tasks: list[ApplicationModuleTasks] = []


def serialize_application_module_ref(m: ApplicationModule) -> str:
    """Serializes a ApplicationModule reference

    Args:
        m (ApplicationModule): The ApplicationModule

    Returns:
        str: The ApplicationModule reference
    """
    return m.Namespace + "::" + m.Name


ApplicationModuleRefType = Annotated[
    ApplicationModule,
    WithJsonSchema(
        {"type": "string"},
    ),
    PlainSerializer(serialize_application_module_ref, return_type=str),
]


def resolve_application_module_ref(raw: str | ApplicationModule, info: ValidationInfo) -> ApplicationModule:
    """Resolves a ApplicationModule reference

    Args:
        raw (str): The ApplicationModule reference
        info (ValidationInfo): The validation info.

    Raises:
        ModelReferenceError: If the reference was not found.

    Returns:
        ApplicationModule: The ApplicationModule
    """
    if isinstance(raw, str):
        assert isinstance(info.context, dict)
        for m in info.context["ApplicationModules"]:
            if m["Namespace"] + "::" + m["Name"] == raw:
                return ApplicationModule.model_validate(m, context=info.context)
        raise ModelReferenceError("Reference not found: " + raw)
    return raw


def serialize_platform_module_ref(m: PlatformModule) -> str:
    """Serializes a PlatformModule reference

    Args:
        m (PlatformModule): The PlatformModule

    Returns:
        str: The PlatformModule reference
    """
    return m.Namespace + "::" + m.Name


PlatformModuleRefType = Annotated[
    PlatformModule,
    WithJsonSchema({"type": "string"}),
    PlainSerializer(serialize_platform_module_ref, return_type=str),
]


def resolve_platform_module_ref(raw: str | PlatformModule, info: ValidationInfo) -> PlatformModule:
    """Resolves a PlatformModule reference

    Args:
        raw (str): The PlatformModule reference
        info (ValidationInfo): The validation info.

    Raises:
        ModelReferenceError: If the reference was not found.

    Returns:
        PlatformModule: The PlatformModule
    """
    if isinstance(raw, str):
        assert isinstance(info.context, dict)
        for m in info.context.get("PlatformConsumerModules", []) + info.context.get("PlatformProviderModules", []):
            if m["Namespace"] + "::" + m["Name"] == raw:
                return PlatformModule.model_validate(m, context=info.context)
        # TODO(virmlj) how is checking if the the reference is in the same executable?
        # eventually consolidate together with PlatformModule
        for e in info.context["Executables"]:
            if "InternalCommunicationModules" in e:
                for m in e["InternalCommunicationModules"]:
                    if m["Namespace"] + "::" + m["Name"] == raw:
                        return PlatformModule.model_validate(m, context=info.context)
        raise ModelReferenceError("Reference not found: " + raw)
    return raw


class InterfaceInstanceToModuleMapping(VafBaseModel):
    InstanceName: str
    ModuleRef: PlatformModuleRefType
    _resolve_ModuleRef = field_validator("ModuleRef", mode="before")(resolve_platform_module_ref)


class ExecutableTaskMapping(VafBaseModel):
    TaskName: str
    Offset: Optional[int] = None
    Budget: Optional[str] = None


class ExecutableApplicationModuleMapping(VafBaseModel):
    ApplicationModuleRef: ApplicationModuleRefType
    InterfaceInstanceToModuleMappings: list[InterfaceInstanceToModuleMapping]
    TaskMapping: list[ExecutableTaskMapping] = []
    _resolve_ApplicationModuleRef = field_validator("ApplicationModuleRef", mode="before")(
        resolve_application_module_ref
    )


class Executable(VafBaseModel):
    Name: str
    ExecutorPeriod: str
    InternalCommunicationModules: list[PlatformModule] = []
    ApplicationModules: list[ExecutableApplicationModuleMapping]


# all model element that have namespace & name
ModelElement = ModelDataType | ModuleInterface | PlatformModule | ApplicationModule


class MainModel(VafBaseModel):
    model_config = ConfigDict(
        title="VAF schema",
        arbitrary_types_allowed=True,
        extra="forbid",
        json_schema_extra={"version": "v0.6.0"},
    )

    schema_reference: Annotated[Optional[str], Field(alias="$schema")] = None
    BaseTypes: list[BaseType] = []
    DataTypeDefinitions: DataTypeDefinition = DataTypeDefinition()
    ModuleInterfaces: list[ModuleInterface] = []
    ApplicationModules: list[ApplicationModule] = []
    PlatformConsumerModules: list[PlatformModule] = []
    PlatformProviderModules: list[PlatformModule] = []
    Executables: list[Executable] = []
    SILKITAdditionalConfiguration: Annotated[
        Optional[SILKITAdditionalConfigurationType],
        Field(
            description="This information is used stage 2 of the Application Framework \
                        generation. For SIL Kit, we will use the artifacts defined \
                        to generate unique interface names"
        ),
    ] = None


###################### functions ######################
def generate_json_schema(path: str) -> None:
    """Generates the JSON schema from the data model.

    Args:
        path (str): Path where the schema will be stored.
    """
    main_model_schema = MainModel.model_json_schema()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(main_model_schema, f, indent=2)


def load_json(path: str | Path) -> MainModel:
    """Loads a model from JSON.

    Args:
        path (str | Path): Path to the JSON file.

    Returns:
        MainModel: The imported model.
    """
    with open(path, encoding="utf-8") as fh:
        raw_model = json.load(fh)

        return MainModel.model_validate(raw_model, context=raw_model)


if __name__ == "__main__":
    generate_json_schema("./vaf_schema.json")
