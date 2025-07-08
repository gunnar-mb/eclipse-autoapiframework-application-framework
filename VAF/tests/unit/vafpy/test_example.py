"""
Test
"""

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-variable
# pylint: disable=missing-function-docstring
# pylint: disable=dangerous-default-value
# pylint: disable=unused-argument
# pylint: disable=too-many-function-args
# pylint: disable=no-value-for-parameter
# pylint: disable=unexpected-keyword-arg

# mypy: disable-error-code="union-attr, call-arg, arg-type"

# Ruff: ignore unused variables
# ruff: noqa: F841
import unittest
from datetime import timedelta

import pytest

from vaf import vafmodel, vafpy
from vaf.cli_core.common.utils import create_name_namespace_full_name
from vaf.vafpy.model_runtime import model_runtime


class TestMain(unittest.TestCase):
    """
    TestMain class
    """

    def __get_type_ref_string(self, typeref: vafmodel.DataTypeRef | vafmodel.ModelElement) -> str:
        return create_name_namespace_full_name(typeref.Name, typeref.Namespace)

    def setUp(self) -> None:
        """Reset model runtime for each test"""
        model_runtime.reset()

    def test_string(self) -> None:
        """test string creation"""
        vafpy.datatypes.String("FirstString", "test")
        r = vafpy.datatypes.String(name="MyString", namespace="test")
        assert isinstance(r, vafpy.datatypes.String)

        vafpy.datatypes.String._from_vaf_model(vafmodel.String(Name="Mulligan", Namespace="test"))  # pylint:disable=protected-access

        assert len(model_runtime.element_by_namespace["test"]["Strings"]) == 3
        assert model_runtime.element_by_namespace["test"]["Strings"]["FirstString"].Name == "FirstString"
        assert model_runtime.element_by_namespace["test"]["Strings"]["MyString"].Name == "MyString"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "FirstString"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[1].Name == "MyString"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[2].Name == "Mulligan"

    def test_invalid_data_types(self) -> None:
        """Test unnamed vector creation"""
        # invalid init arguments
        with pytest.raises(TypeError):
            vafpy.datatypes.String("test", "TestString", vafpy.BaseTypes.UINT16_T, 223, 815)

        # invalid namespace
        with pytest.raises(vafpy.core.ModelError):
            vafpy.datatypes.String("123test", "TestString")

        # invalid name
        with pytest.raises(vafpy.core.ModelError):
            vafpy.datatypes.String("aber::comb", "TestString")
            vafpy.datatypes.String("aber", "comb::TestString")

        # duplicates
        with pytest.raises(vafpy.core.ModelError):
            vafpy.datatypes.String("valid", "TestString")
            vafpy.datatypes.String("valid", "TestString")

    def test_invalid_vector_array(self) -> None:
        """Test unnamed vector creation"""

        # vector doesn't accept sizes
        with pytest.raises(TypeError):
            vafpy.datatypes.Vector("test", vafpy.BaseTypes.UINT16_T, 223, "TestVector", 815)

        # invalid arguments
        with pytest.raises(TypeError):
            vafpy.datatypes.Vector(
                namespace="test", name="TestVector", datatype=vafpy.BaseTypes.UINT16_T, abrakadabra=815
            )

        # array with no size
        with pytest.raises(TypeError):
            vafpy.datatypes.Array(namespace="test", name="TestArray", datatype=vafpy.BaseTypes.UINT16_T)

        # vector and array without name
        with pytest.raises(TypeError):
            vafpy.datatypes.Array(namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
        with pytest.raises(TypeError):
            vafpy.datatypes.Vector(namespace="test", datatype=vafpy.BaseTypes.UINT16_T)

    def test_named_vector(self) -> None:
        """Test named vector creation"""

        vafpy.datatypes.Vector(name="MyVector", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)

        assert "TypeRefs" not in model_runtime.element_by_namespace["test"]
        self.assertEqual(model_runtime.element_by_namespace["test"]["Vectors"]["MyVector"].Name, "MyVector")
        self.assertEqual(
            self.__get_type_ref_string(model_runtime.element_by_namespace["test"]["Vectors"]["MyVector"].TypeRef),
            "::uint16_t",
        )
        assert len(model_runtime.main_model.DataTypeDefinitions.Vectors) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Vectors[0].Name == "MyVector"
        assert model_runtime.main_model.DataTypeDefinitions.Vectors[0].TypeRef == vafmodel.DataType(
            Name="uint16_t", Namespace=""
        )

    def test_named_vector_in_struct(self) -> None:
        """Test named vectors as struct subelement"""

        my_struct = vafpy.datatypes.Struct(name="MyStruct", namespace="test")
        my_struct.add_subelement(name="x", datatype=vafpy.BaseTypes.DOUBLE)

        my_vector = vafpy.datatypes.Vector(name="MyVector", namespace="test", datatype=my_struct)

        my_outer_struct = vafpy.datatypes.Struct(name="MyStruct2", namespace="test")
        my_outer_struct.add_subelement(name="y", datatype=my_vector)

        self.assertEqual(len(model_runtime.main_model.DataTypeDefinitions.Structs), 2)
        self.assertEqual(
            self.__get_type_ref_string(model_runtime.main_model.DataTypeDefinitions.Structs[1].SubElements[0].TypeRef),
            "test::MyVector",
        )
        self.assertEqual(len(model_runtime.main_model.DataTypeDefinitions.Vectors), 1)
        self.assertEqual(model_runtime.main_model.DataTypeDefinitions.Vectors[0].Name, "MyVector")

    def test_exe(self) -> None:
        """Test creating a simple but complete model"""

        my_interface = vafpy.ModuleInterface(name="MyInterface", namespace="interfaces")
        my_interface.add_data_element(name="data_element1", datatype=vafpy.BaseTypes.UINT16_T)

        app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="app_modules")
        app_module1.add_provided_interface(instance_name="Instance1", interface=my_interface)

        app_module2 = vafpy.ApplicationModule(name="AppModule2", namespace="app_modules")
        app_module2.add_consumed_interface(instance_name="Instance1", interface=my_interface)

        exe = vafpy.Executable("exe", timedelta(milliseconds=10))
        exe.add_application_module(app_module1, [])
        exe.add_application_module(app_module2, [])
        exe.connect_interfaces(app_module1, "Instance1", app_module2, "Instance1")

        vafpy.runtime.get_main_model()

    def test_complex(self) -> None:
        """Test creating a complex and complete model"""

        my_string = vafpy.datatypes.String(name="MyString", namespace="complex")

        my_struct = vafpy.datatypes.Struct(name="MyStruct", namespace="complex")
        my_struct.add_subelement(name="a", datatype=my_string)
        my_struct.add_subelement(name="b", datatype=vafpy.BaseTypes.BOOL)

        my_vector = vafpy.datatypes.Vector(name="MyVector", namespace="complex1", datatype=my_struct)
        my_map = vafpy.datatypes.Map(
            name="MyMap",
            namespace="complex3",
            key_type=vafpy.BaseTypes.UINT16_T,
            value_type=vafpy.BaseTypes.DOUBLE,
        )

        my_array = vafpy.datatypes.Array(name="MyArray", namespace="complex2", datatype=my_map, size=100)

        my_type_ref = vafpy.datatypes.TypeRef(name="MyTypeRef", namespace="other", datatype=my_vector)

        my_enum = vafpy.datatypes.Enum(name="MyEnum", namespace="complex")
        my_enum.add_entry(label="ABC", value=1)
        my_enum.add_entry(label="DEF", value=2)

        my_interface = vafpy.ModuleInterface(name="MyInterface", namespace="inter")
        my_interface.add_data_element(name="a", datatype=my_string)
        my_interface.add_data_element(name="b", datatype=my_struct)
        my_interface.add_data_element(name="c", datatype=my_vector)
        my_interface.add_data_element(name="d", datatype=my_map)
        my_interface.add_data_element(name="e", datatype=my_array)
        my_interface.add_data_element(name="f", datatype=my_type_ref)
        my_interface.add_data_element(name="g", datatype=my_enum)

        app1 = vafpy.ApplicationModule(name="App1", namespace="app1")
        app1.add_provided_interface(instance_name="Instance1", interface=my_interface)

        app2 = vafpy.ApplicationModule(name="App2", namespace="app2")
        app2.add_consumed_interface(instance_name="Instance2", interface=my_interface)

        exe = vafpy.Executable("exe", timedelta(milliseconds=10))
        exe.add_application_module(app1, [])
        exe.add_application_module(app2, [])
        exe.connect_interfaces(app1, "Instance1", app2, "Instance2")

    def test_operations(self) -> None:
        """Test creating operations"""

        my_array = vafpy.datatypes.Array(
            name="MyArray", namespace="operations_types", datatype=vafpy.BaseTypes.DOUBLE, size=100
        )

        my_interface = vafpy.ModuleInterface(name="MyInterface", namespace="interfaces1")
        my_interface.add_operation(
            name="func1",
            in_parameter={"in1": vafpy.BaseTypes.BOOL, "in2": my_array},
            out_parameter={"out1": vafpy.BaseTypes.BOOL, "out2": my_array},
            inout_parameter={"inout1": vafpy.BaseTypes.BOOL, "inout2": my_array},
        )
        my_interface.add_operation(name="func2", out_parameter={"out": vafpy.BaseTypes.BOOL})
        my_interface.add_operation(
            name="func3", out_parameter={"out": vafpy.BaseTypes.BOOL}, inout_parameter={"inout": vafpy.BaseTypes.BOOL}
        )

    def test_tasks(self) -> None:
        """Test creating tasks and task chains"""

        app = vafpy.ApplicationModule(name="App", namespace="app")

        p_10ms = timedelta(milliseconds=10)
        step1 = vafpy.Task(name="Step1", period=p_10ms, preferred_offset=0)
        step2 = vafpy.Task(name="Step2", period=p_10ms, preferred_offset=0, run_after=[step1])
        step3 = vafpy.Task(name="Step3", period=p_10ms, preferred_offset=0, run_after=[step1])
        step4 = vafpy.Task(name="Step4", period=p_10ms, preferred_offset=0, run_after=[step1, step2, step3])

        app.add_task_chain(tasks=[step1])
        app.add_task_chain(tasks=[step2], run_after=[step3])
        app.add_task_chain(tasks=[step4, step3], run_after=[step1], increment_preferred_offset=True)

    def test_vaf_string_base_datatype(self) -> None:
        """FTAF-597: Add vaf::string in model is used"""
        # datatypes: vector/array/typeref
        vafpy.Vector("test", "MacVector", vafpy.BaseTypes.STRING)

        assert isinstance(
            model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).get("string", None), vafpy.String
        )
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

        model_runtime.reset()
        vafpy.Array("test", "MaXRay", vafpy.BaseTypes.STRING, 2)

        assert isinstance(
            model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).get("string", None), vafpy.String
        )
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

        model_runtime.reset()
        vafpy.TypeRef("test", "T-Rex", vafpy.BaseTypes.STRING)

        assert isinstance(
            model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).get("string", None), vafpy.String
        )
        vafpy.Array("test", "MaXRay", vafpy.BaseTypes.STRING, 2)
        assert len(model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

        model_runtime.reset()
        vafpy.Vector("test", "MacVector", vafpy.BaseTypes.BOOL)
        assert model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).get("string", None) is None
        assert len(model_runtime.main_model.DataTypeDefinitions.Strings) == 0

        # struct
        model_runtime.reset()
        struct = vafpy.Struct(name="MyStruct", namespace="demo")
        struct.add_subelement(name="MaStr", datatype=vafpy.BaseTypes.STRING)
        assert len(model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

    def test_vaf_string_base_module_interface(self) -> None:
        """FTAF-597: Add vaf::string in model is used"""

        # module interface
        model_runtime.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")
        assert model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).get("string", None) is None
        assert len(model_runtime.main_model.DataTypeDefinitions.Strings) == 0

        # via add data elements
        interface.add_data_element("Stringulation", vafpy.BaseTypes.STRING)
        assert len(model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

        model_runtime.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")

        # via add operations in
        interface.add_operation("inopt", in_parameter={"in_string": vafpy.BaseTypes.STRING})
        assert len(model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

        model_runtime.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")

        # via add operations out
        interface.add_operation("outopt", out_parameter={"out_string": vafpy.BaseTypes.STRING})
        assert len(model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

        model_runtime.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")

        # via add operations inout
        interface.add_operation("twoway", inout_parameter={"bidirect_string": vafpy.BaseTypes.STRING})
        assert len(model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"

        # full add
        model_runtime.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")
        interface.add_operation(
            "inopt",
            in_parameter={"in_string": vafpy.BaseTypes.STRING},
            out_parameter={"out_string": vafpy.BaseTypes.STRING},
            inout_parameter={"bidirect_string": vafpy.BaseTypes.STRING},
        )
        interface.add_data_element("Stringulation", vafpy.BaseTypes.STRING)
        assert len(model_runtime.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert model_runtime.main_model.DataTypeDefinitions.Strings[0].Name == "string"
