"""Factory to build"""

from typing import Any, Optional

from pydantic._internal._model_construction import ModelMetaclass
from typing_extensions import Self

from vaf import vafmodel

from .core import BaseTypesWrapper, ModelError, VafpyAbstractBase
from .model_runtime import model_runtime

# pylint: disable=too-few-public-methods


class VafpyAbstractElement(VafpyAbstractBase):
    """Generic Abstract type for Vafpy Element"""

    @classmethod
    def __ensure_name_ns(cls, name: str | None, namespace: str | None) -> None:
        """Method to ensure name & namespaces of the object
        Args:
            kwargs: attributes to be checked
        Raises:
            ModelError: if name and namespace is not valid
        """
        if name is None and namespace is None:
            type_str = cls.__name__
            error_msg = "".join(
                [f"Dude, why do you want to initialize {type_str}", "with name = None & namespace = None?"]
            )
            raise ModelError(error_msg)

        assert isinstance(name, str) and isinstance(namespace, str)

        invalid_name_bs: bool = "::" in name

        if "::" in name:
            reason = "Name must not contain character '::'!"
        else:
            reason = "The first character of name and namespace must not be a number!"
            if namespace == "":
                invalid_name_bs |= name[0].isdigit()
            else:
                invalid_name_bs |= name[0].isdigit() or namespace[0].isdigit()

        if invalid_name_bs:
            raise ModelError(reason)

    @classmethod
    def __get_vafmodel_parent(cls) -> ModelMetaclass:
        """Method to get first vafmodel parent from class
        Returns:
            vafmodel class
        Raises:
            ModelError: if class is not a children of a vafmodel class
        """
        tmp_cls: Any = cls

        looping_louie: bool = True
        while looping_louie:
            tmp_cls = getattr(tmp_cls, "__base__", None)
            looping_louie = tmp_cls is not None and not tmp_cls.__module__.endswith("vafmodel")

        if type(tmp_cls) is not ModelMetaclass or not tmp_cls.__module__.endswith("vafmodel"):  # pylint: disable=unidiomatic-typecheck
            raise ModelError("Dude, your class has the wrong parent!")

        return tmp_cls

    @classmethod
    def _construct_typeref_object(cls, typeref: VafpyAbstractBase | BaseTypesWrapper, object_class: type) -> None:
        """Method to construct typeref object
        Args:
            typeref: typeref as cac object
            object_class: class of the typeref
        """
        # assert typeref hasn't constructed yet
        if (
            model_runtime.element_by_namespace.get(typeref.Namespace, {})
            .get(object_class.__name__ + "s", {})
            .get(typeref.Name, None)
            is None
        ):
            # construct the typeref as vafpy object
            object_class(typeref.Name, typeref.Namespace)

    @classmethod
    def _build_instance(cls, obj: Optional[Self] = None, **kwargs: Any) -> Optional[Self]:
        """Method to build an instance of a vafpy element
        Args:
            obj: object if it's already built
            kwargs: attributes of the object
        Returns:
            constructed object that can be fetched by caller
        """
        # construct empty instance if obj is none
        if obj is None:
            obj = cls.__new__(cls)
        # ensure validity of attributes
        cls.__ensure_name_ns(name=kwargs.get("Name", None), namespace=kwargs.get("Namespace", None))
        # construct via vafmodel constructor
        vafmodel_parent = cls.__get_vafmodel_parent()
        vafmodel_parent.__init__(  # type:ignore[misc]
            obj,
            **{
                init_args: kwargs[init_args] for init_args in vafmodel_parent.model_fields.keys() if init_args in kwargs
            },
        )
        # add to model runtime
        model_runtime.add_element(obj, imported=kwargs.get("imported", False))

        return obj

    @classmethod
    def _from_vaf_model(cls, vaf_model: vafmodel.ModelElement, **kwargs: Any) -> None:
        """Method to init vafpy object from a vaf_model
        Args:
            vaf_model: vafmodel object as input
            kwargs: Other variables
        """
        # append vaf_model attributes to kwargs
        kwargs |= {init_args: getattr(vaf_model, init_args) for init_args in vaf_model.model_fields_set}
        # construct object from kwargs
        cls._build_instance(**kwargs)
