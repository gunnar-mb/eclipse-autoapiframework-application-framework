"""Module providing config as code for VAF projects."""

from vaf import vafmodel

# pylint: disable=too-few-public-methods


class ModelError(Exception):
    """Exception class for modeling errors"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BaseTypesWrapper:
    """Wrapper for std types"""

    def _get_type_ref(self) -> vafmodel.DataTypeRef:
        """Method to get typeref from current instance
        Returns:
            Respective string typeref of current instance
        """
        return vafmodel.DataType(Name=self.Name, Namespace=self.Namespace)

    def __init__(self, name: str, namespace: str = "") -> None:
        self.Name = name
        self.Namespace = namespace
        self.TypeRef = vafmodel.DataType(Name=name, Namespace=namespace)


class BaseTypes:
    """All c++ std base types"""

    INT8_T = BaseTypesWrapper("int8_t")
    INT16_T = BaseTypesWrapper("int16_t")
    INT32_T = BaseTypesWrapper("int32_t")
    INT64_T = BaseTypesWrapper("int64_t")
    UINT8_T = BaseTypesWrapper("uint8_t")
    UINT16_T = BaseTypesWrapper("uint16_t")
    UINT32_T = BaseTypesWrapper("uint32_t")
    UINT64_T = BaseTypesWrapper("uint64_t")
    FLOAT = BaseTypesWrapper("float", "")
    DOUBLE = BaseTypesWrapper("double", "")
    BOOL = BaseTypesWrapper("bool", "")
    STRING = BaseTypesWrapper("string", "vaf")


# pylint: disable=too-few-public-methods
# pylint: disable=super-init-not-called
class VafpyAbstractBase(vafmodel.DataType, BaseTypesWrapper):
    """Base Abstract class for VafpyObject"""

    def __init__(self) -> None:
        """
        Raises:
            ModelError: if initialized
        """
        raise ModelError("Dude, who told you to construct this forbidden class?")
