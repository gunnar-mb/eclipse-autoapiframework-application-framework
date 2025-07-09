"""Abstraction layer for the datatypes in Config as Code"""

from typing import Any, List, Optional

from typing_extensions import Self

from vaf import vafmodel

from .core import BaseTypes, BaseTypesWrapper, ModelError, VafpyAbstractBase
from .factory import VafpyAbstractElement

# pylint: disable = too-few-public-methods
# pylint: disable = unused-private-member # Used via decorators
# pylint: disable = super-init-not-called # DUE to decorators' use
# pylint: disable = unused-argument # DUE to overload in decorator
# pylint: disable = protected-access
# mypy: disable-error-code="misc"

VafpyDataTypeRef = VafpyAbstractBase | BaseTypesWrapper


class Enum(vafmodel.VafEnum, VafpyAbstractElement):
    """The VAF::Enum datatype"""

    def __init__(self, name: str, namespace: str, literals: Optional[List[vafmodel.EnumLiteral]] = None) -> None:
        literals = literals or []
        self._validate_literals(literals)  # ← Validate before anything else
        self._build_instance(self, Name=name, Namespace=namespace, Literals=literals)

    def add_entry(self, label: str, value: int) -> None:
        """Add an entry to the enum definition.

        Args:
            label (str): The label of the enum entry
            value (int): The value of the enum entry

        Raises:
            ModelError: If entry labels are invalid or duplicated
        """
        self._validate_entry(label, value)

        self.Literals.append(vafmodel.EnumLiteral(Label=label, Value=value))

    def _validate_label(self, label: str) -> None:
        """Validate label for no spaces.

        Args:
            label (str): The label of the enum entry

        Raises:
            ModelError: If entry label is invalid
        """
        if " " in label:
            raise ModelError(f"Enum - Label cannot contain spaces: '{label}'")

    def _validate_entry(self, label: str, value: int) -> None:
        """Validate the enum entries.

        Args:
            label (str): The label of the enum entry
            value (int): The value of the enum entry

        Raises:
            ModelError: If entry labels or values are invalid or duplicated
        """
        self._validate_label(label)

        if any(literal.Label == label for literal in self.Literals):
            raise ModelError(f"Enum - Duplicate label not allowed: '{label}'")
        if any(literal.Value == value for literal in self.Literals):
            raise ModelError(f"Enum - Duplicate value not allowed: {value}")

    def _validate_literals(self, literals: List[vafmodel.EnumLiteral]) -> None:
        """Validate the list of the enum literals.

        Args:
            literrals (List[vafmodel.EnumLiteral]): The list of the EnumLiterals.

        Raises:
            ModelError: If entry labels or values are invalid or duplicated
        """
        seen_labels = set()
        seen_values = set()

        for literal in literals:
            self._validate_label(literal.Label)

            if literal.Label in seen_labels:
                raise ModelError(f"Enum - Duplicate label in constructor: '{literal.Label}'")
            if literal.Value in seen_values:
                raise ModelError(f"Enum - Duplicate value in constructor: '{literal.Value}'")

            seen_labels.add(literal.Label)
            seen_values.add(literal.Value)


class Map(vafmodel.Map, VafpyAbstractElement):
    """The VAF::Map datatype"""

    def __init__(
        self,
        name: str,
        namespace: str,
        key_type: VafpyDataTypeRef,
        value_type: VafpyDataTypeRef,
    ) -> None:
        self._build_instance(
            self,
            Name=name,
            Namespace=namespace,
            MapKeyTypeRef=key_type._get_type_ref(),
            MapValueTypeRef=value_type._get_type_ref(),
        )


class String(vafmodel.String, VafpyAbstractElement):
    """The VAF::String datatype"""

    def __init__(self, name: str, namespace: str) -> None:
        self._build_instance(self, Name=name, Namespace=namespace)


class Struct(vafmodel.Struct, VafpyAbstractElement):
    """The VAF::Struct datatype"""

    def __init__(self, name: str, namespace: str, sub_elements: Optional[List[vafmodel.SubElement]] = None) -> None:
        self._build_instance(
            self, Name=name, Namespace=namespace, SubElements=sub_elements if sub_elements is not None else []
        )

    def add_subelement(self, name: str, datatype: VafpyDataTypeRef) -> None:
        """Add a subelement to the struct definition

        Args:
            name (str): The name of the subelement
            datatype (VafpyDataTypeRef): The type of the subelement

        Raises:
            ModelError: If subelement names are duplicated
        """
        if any(element.Name == name for element in self.SubElements):
            raise ModelError(f"Struct - Duplicated subelement: {name}")
        # borrow check typeref from VafpyAbstractDatatypeTyperef
        VafpyAbstractDatatypeTyperef._check_typeref(datatype)
        self.SubElements.append(vafmodel.SubElement(Name=name, TypeRef=datatype._get_type_ref()))


class VafpyAbstractDatatypeTyperef(VafpyAbstractElement):
    """Generic Abstract type for Vafpy datatypes that have typeref"""

    @classmethod
    def _check_typeref(cls, typeref: VafpyDataTypeRef) -> None:
        """Method to checkf if typeref needs construction
        Args:
            typeref: typeref as cac object
        """
        # construct typeref
        if typeref == BaseTypes.STRING:
            cls._construct_typeref_object(typeref, String)

    @classmethod
    def _build_instance(cls, obj: Optional[Self] = None, **kwargs: Any) -> None:
        # only for CaC: process given typeref
        if not kwargs.get("imported", False):
            assert isinstance(kwargs["TypeRef"], VafpyDataTypeRef)
            # store CaC typeref
            cac_typeref = kwargs["TypeRef"]
            # convert typeref in kwargs to vafmodel typeref
            kwargs["TypeRef"] = kwargs["TypeRef"]._get_type_ref()
            # construct typeref if needed
            cls._check_typeref(cac_typeref)

        # call parent build instance m
        super()._build_instance(obj, **kwargs)


# pylint: disable = too-many-ancestors
class TypeRef(vafmodel.TypeRef, VafpyAbstractDatatypeTyperef):
    """The VAF::TypeRef datatype"""

    def __init__(self, name: str, namespace: str, datatype: VafpyDataTypeRef) -> None:
        self._build_instance(self, Name=name, Namespace=namespace, TypeRef=datatype)


class Vector(vafmodel.Vector, VafpyAbstractDatatypeTyperef):
    """The VAF::Vector datatype"""

    def __init__(
        self,
        name: str,
        namespace: str,
        datatype: VafpyDataTypeRef,
    ) -> None:
        self._build_instance(self, Name=name, Namespace=namespace, TypeRef=datatype)


class Array(vafmodel.Array, VafpyAbstractDatatypeTyperef):
    """The VAF::Array datatype"""

    # Array must have size compared to Vector
    def __init__(self, name: str, namespace: str, datatype: VafpyDataTypeRef, size: int):
        self._build_instance(self, Name=name, Namespace=namespace, TypeRef=datatype, Size=size)
