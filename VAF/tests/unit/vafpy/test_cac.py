"""
Test CaC with vafpy
"""

# pylint: disable=missing-param-doc
# pylint: disable=missing-any-param-doc
# pylint: disable=anomalous-backslash-in-string
# pylint: disable=missing-raises-doc
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
# pylint: disable=unused-variable
# pylint: disable=missing-class-docstring
# pylint: disable=too-many-locals
# mypy: disable-error-code="no-untyped-def,union-attr"


# Ruff: ignore unused variables
# ruff: noqa: F841

import importlib
import json
import os
import re
import sys
from pathlib import Path
from shutil import copyfile, copytree
from types import ModuleType
from unittest import mock

import pytest

from vaf import save_main_model, save_part_of_main_model, vafmodel, vafpy
from vaf.cli_core.common.utils import ProjectType, create_name_namespace_full_name
from vaf.vafpy.model_runtime import model_runtime

### IMPORT MOCKING ###
# Store original __import__
orig_import = __import__
mock_import: dict[str, ModuleType] = {}


def import_mock(name: str, *args) -> ModuleType:
    """Function to mock import calls from CaC python files"""
    return mock_import[name] if name in mock_import else orig_import(name, *args)


def import_by_file_name(path_to_file: Path | str, file_name: str) -> ModuleType:
    """importlib.import_module somehow fails in pytest and can't find the modules"""
    spec = importlib.util.spec_from_file_location(file_name, f"{path_to_file}/{file_name}.py")
    if spec:
        module = importlib.util.module_from_spec(spec)
        if module and spec.loader:
            sys.modules[file_name] = module
            spec.loader.exec_module(module)

    if not module:
        raise RuntimeError(f"Failed to import module in {path_to_file}/{file_name}.py")

    return module


def mock_vafpy(path_to_model: str | Path, imports_list: list[str]) -> None:
    """Mock vafpy call using __import__
    Args:
        path_to_model: path to the output dir that contains the CaC models
        imports_list: all modules to be imported
    """
    with mock.patch("builtins.__import__", side_effect=import_mock):
        mock_import["vafpy"] = importlib.import_module("vaf.vafpy")
        for import_name in imports_list:
            if "/" in import_name:
                import_file_data = import_name.split("/")
                mock_import[".".join(import_file_data)] = import_by_file_name(
                    f"{path_to_model}/{''.join(import_file_data[:-1])}", import_file_data[-1]
                )
            else:
                mock_import[import_name] = import_by_file_name(path_to_model, import_name)
        import_by_file_name(path_to_model, "model")


def __get_type_ref_string(typeref: vafmodel.TypeRef | vafmodel.DataType) -> str:
    return create_name_namespace_full_name(typeref.Name, typeref.Namespace)


UT_PATH = Path(__file__).parent


### UNIT TESTS ###
def test_generate_vss_model(tmp_path) -> None:
    """FTAF-260: Test Generation of VSS Artifacts based on CaC"""
    path_out = tmp_path / "ftaf_260"

    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(UT_PATH / "test_data/ftaf_260/model.py", path_out / "model.py")

    mock_vafpy(path_out, ["vss"])

    save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.INTEGRATION)

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(UT_PATH / "test_data/ftaf_260/model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_bug_ftaf_260_app_module(tmp_path) -> None:
    """FTAF-260: Bug with Application Modules"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "ftaf_260_bug"
    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(UT_PATH / "test_data/ftaf_260_bug/model.py", path_out / "model.py")
    # assert that unused Vectors, Maps, TypeRefs, Arrays, Enums are removed
    copyfile(UT_PATH / "test_data/ftaf_260_bug/silkit-model.json", path_out / "silkit-model.json")
    os.chdir(path_out)

    try:
        mock_vafpy(path_out, ["silkit"])

        save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.INTEGRATION)

        with open(path_out / "model.json", "r", encoding="utf-8") as generated:
            with open(UT_PATH / "test_data/ftaf_260_bug/model.json", "r", encoding="utf-8") as goal:
                assert json.loads(generated.read()) == json.loads(goal.read())
    finally:
        os.chdir(original_working_dir)


def test_error_duplicate_executables(tmp_path) -> None:
    """FTAF-339: Error in case of duplicate executables"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "ftaf_339"

    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(
        UT_PATH / "test_data/ftaf_339/model.py",
        path_out / "model.py",
    )
    os.chdir(path_out)
    try:
        mock_vafpy(path_out, ["silkit"])

        with pytest.raises(vafpy.core.ModelError) as error_msg:
            save_main_model(path_out / "model.json", project_type=ProjectType.INTEGRATION)
            assert error_msg.value.args[0] == "Executable adas_demo_app is defined multiple times!"
    finally:
        os.chdir(original_working_dir)


def test_validation_unconnected_interfaces(tmp_path, recwarn) -> None:
    """FTAF-258: Warn user of unconnected interfaces"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "ftaf_258"

    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(
        UT_PATH / "test_data/ftaf_258/model.py",
        path_out / "model.py",
    )
    os.chdir(path_out)

    try:
        mock_vafpy(path_out, ["silkit"])

        save_main_model(path_out / "model.json", project_type=ProjectType.INTEGRATION)

        relevant_warnings = [
            wrn.message.args[0] for wrn in recwarn if wrn.message.args[0].startswith("Following interfaces")
        ]
        assert len(relevant_warnings) == 1

        goal_unconnected_interfaces = [
            "NsApplicationUnit::NsCollisionDetection::CollisionDetection - BrakeServiceProvider",
            "NsApplicationUnit::NsCollisionDetection::CollisionDetection - ImageServiceProvider1",
            "NsApplicationUnit::NsSensorFusion::SensorFusion - ImageServiceConsumer1",
            "NsApplicationUnit::NsSensorFusion::SensorFusion - ImageServiceConsumer2",
            "NsApplicationUnit::NsSensorFusion::SensorFusion - SteeringAngleServiceConsumer",
            "NsApplicationUnit::NsSensorFusion::SensorFusion - VelocityServiceConsumer",
        ]

        result_unconnected_interfaces = re.findall(
            r"Following interfaces are defined but not connected: \[(.+?)\]", relevant_warnings[0]
        )
        assert result_unconnected_interfaces, f"Incorrect Warning returned: {relevant_warnings[0]}"
        result_unconnected_interfaces = [
            unconnected_interface.replace("'", "").replace('"', "")
            for unconnected_interface in result_unconnected_interfaces[0].split(", '")
        ]
        assert set(goal_unconnected_interfaces) == set(result_unconnected_interfaces)
    finally:
        os.chdir(original_working_dir)


def test_invalid_exec_periodic_tasks(tmp_path, recwarn) -> None:
    """FTAF-421: Error if Exec's periodic task > its tasks' Periodic tasks"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "ftaf_421"

    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(
        UT_PATH / "test_data/ftaf_421/model.py",
        path_out / "model.py",
    )
    copyfile(
        UT_PATH / "test_data/ftaf_421/silkit.py",
        path_out / "silkit.py",
    )
    os.chdir(path_out)

    try:
        mock_vafpy(path_out, ["silkit"])

        with pytest.raises(vafpy.core.ModelError) as error_msg:
            save_main_model(path_out / "model.json", project_type=ProjectType.INTEGRATION)

        # ensure validator errors
        goal_errors = [
            "Invalid ExecutorPeriod of Executable adas_demo_app: 23ms!",
            "Executor Period 23ms is longer than its Task(s)' period:",
            "   AppModule: NsApplicationUnit::NsSensorFusion::SensorFusion - Task: Step2 with period 5ms",
            "   AppModule: NsApplicationUnit::NsSensorFusion::SensorFusion - Task: Step3 with period 22ms",
        ]
        errors = error_msg.value.args[0].split("\n")
        assert len(recwarn) == 0
        assert sorted(errors) == sorted(goal_errors)
    finally:
        os.chdir(original_working_dir)


def test_validation_empty_interfaces(tmp_path, recwarn) -> None:
    """FTAF-457: Detect and warn about empty interface definition in vafpy"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "ftaf_457"
    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(
        UT_PATH / "test_data/ftaf_457/model.py",
        path_out / "model.py",
    )
    os.chdir(path_out)

    try:
        mock_vafpy(path_out, [])

        save_part_of_main_model(
            Path("model.json"), ["DataTypeDefinitions", "ModuleInterfaces"], project_type=ProjectType.INTEGRATION
        )

        relevant_warnings = [
            wrn.message.args[0] for wrn in recwarn if wrn.message.args[0].startswith("Following interfaces")
        ]
        assert len(relevant_warnings) == 1

        goal_epmty_interfaces = [
            "demo::EmptyInterface",
        ]

        result_epmty_interfaces = re.findall(
            r"Following interfaces are defined without data elements and operations: \[(.+?)\]", relevant_warnings[0]
        )
        assert result_epmty_interfaces, f"Incorrect Warning returned: {relevant_warnings[0]}"
        result_epmty_interfaces = [
            epmty_interface.replace("'", "").replace('"', "")
            for epmty_interface in result_epmty_interfaces[0].split(", '")
        ]
        assert set(goal_epmty_interfaces) == set(result_epmty_interfaces)
    finally:
        os.chdir(original_working_dir)


def test_validation_duplicate_datatype_interface(tmp_path) -> None:
    """FTAF-354: Warning for duplicates datatypes & interfaces"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "ftaf-354"
    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(
        UT_PATH / "test_data/ftaf_354/model.py",
        path_out / "model.py",
    )
    os.chdir(path_out)

    try:
        with pytest.raises(vafpy.core.ModelError) as error_msg:
            mock_vafpy(path_out, ["silkit"])

            # ensure validator errors
            goal_errors = [
                "Failed to add a duplicate for DataTypeDefinition with Type Struct: datatypes::SteeringAngle",
            ]
            errors = error_msg.value.args[0].split("\n")
            assert sorted(errors) == sorted(goal_errors)
    finally:
        os.chdir(original_working_dir)


def test_bug_remove_unused_artifacts(tmp_path) -> None:
    """FTAF-386: Bug in __remove_unused_artifacts"""
    path_out = tmp_path / "ftaf_386"

    copytree(UT_PATH / "test_data/ftaf_386", path_out)

    mock_vafpy(path_out, ["imported_models/interface_project", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.INTEGRATION)

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(UT_PATH / "test_data/ftaf_386/model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_bug2_remove_unused_artifacts(tmp_path) -> None:
    """FTAF-394: 2nd Bug in __remove_unused_artifacts"""
    path_out = tmp_path / "ftaf_394"

    copytree(UT_PATH / "test_data/ftaf_394", path_out)

    mock_vafpy(path_out, ["silkit", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.INTEGRATION)

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(UT_PATH / "test_data/ftaf_394/goal-model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_consolidation_fixed_size_array_vector() -> None:
    """FTAF-382: Consolidation of Fixed Size Arrays & Vectors
    Update FTAF-474: Feature reverted!
    """

    ma_struct = vafpy.datatypes.Struct(name="MaStruct", namespace="test")
    ma_struct.add_subelement(name="x", datatype=vafpy.BaseTypes.DOUBLE)

    vafpy.datatypes.Vector(name="MaVector", namespace="test", datatype=ma_struct)

    vafpy.datatypes.Vector(name="MyVectorFixed", namespace="test", datatype=ma_struct)
    vafpy.datatypes.Vector(name="MyVectorFixedAgain", namespace="test", datatype=ma_struct)

    vafpy.datatypes.Vector(name="MockVector1", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)
    vafpy.datatypes.Vector(name="MockVector2", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)
    vafpy.datatypes.Vector(name="MockVector3", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)
    vafpy.datatypes.Vector(name="MockVector4", namespace="test", datatype=vafpy.BaseTypes.FLOAT)
    vafpy.datatypes.Vector(name="MockVector5", namespace="test", datatype=vafpy.BaseTypes.BOOL)

    vafpy.datatypes.Array(name="MyFixedArray", namespace="test", datatype=ma_struct, size=2)
    vafpy.datatypes.Array(name="MyFixedArray2", namespace="test", datatype=ma_struct, size=2)

    vafpy.datatypes.Array(name="MockArray1", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    vafpy.datatypes.Array(name="MockArray2", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    vafpy.datatypes.Array(name="MockArray3", namespace="test", datatype=vafpy.BaseTypes.FLOAT, size=2)
    vafpy.datatypes.Array(name="MockArray4", namespace="test", datatype=vafpy.BaseTypes.BOOL, size=2)

    assert len(model_runtime.main_model.DataTypeDefinitions.Vectors) == 8
    for idx, name in enumerate(
        [
            "MaVector",
            "MyVectorFixed",
            "MyVectorFixedAgain",
            "MockVector1",
            "MockVector2",
            "MockVector3",
            "MockVector4",
            "MockVector5",
        ]
    ):
        assert model_runtime.main_model.DataTypeDefinitions.Vectors[idx].Name == name

    assert len(model_runtime.main_model.DataTypeDefinitions.Arrays) == 6
    for idx, name in enumerate(
        ["MyFixedArray", "MyFixedArray2", "MockArray1", "MockArray2", "MockArray3", "MockArray4"]
    ):
        assert model_runtime.main_model.DataTypeDefinitions.Arrays[idx].Name == name


def test_consolidation_fixed_size_array_vector_reference() -> None:
    """Assert References of Consolidated Fixed Size Arrays & Vectors"""

    ma_struct = vafpy.datatypes.Struct(name="MaStruct", namespace="test")
    ma_struct.add_subelement(name="x", datatype=vafpy.BaseTypes.DOUBLE)

    vafpy.datatypes.Vector(name="MaVector", namespace="test", datatype=ma_struct)

    my_vector_fix = vafpy.datatypes.Vector(name="MyVectorFixed", namespace="test", datatype=ma_struct)

    mock_vector2 = vafpy.datatypes.Vector(name="MockVector2", namespace="test", datatype=vafpy.BaseTypes.FLOAT)
    mock_vector3 = vafpy.datatypes.Vector(name="MockVector3", namespace="test", datatype=vafpy.BaseTypes.FLOAT)
    mock_vector4 = vafpy.datatypes.Vector(name="MockVector4", namespace="test", datatype=vafpy.BaseTypes.FLOAT)

    mock_array1 = vafpy.datatypes.Array(name="MockArray1", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    mock_array2 = vafpy.datatypes.Array(name="MockArray2", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    mock_array3 = vafpy.datatypes.Array(name="MockArray3", namespace="test", datatype=vafpy.BaseTypes.FLOAT, size=2)

    mock_struct = vafpy.datatypes.Struct(name="MockStruct", namespace="test")
    mock_struct.add_subelement(name="W", datatype=mock_vector3)
    mock_struct.add_subelement(name="H", datatype=mock_vector2)
    mock_struct.add_subelement(name="Y", datatype=mock_array3)
    mock_struct.add_subelement(name="M", datatype=mock_array1)
    mock_struct.add_subelement(name="C", datatype=mock_array2)
    mock_struct.add_subelement(name="A", datatype=mock_vector4)

    vafpy.datatypes.TypeRef(name="MockTypeRef", namespace="test", datatype=mock_array3)

    vafpy.datatypes.Map(name="MockMap", namespace="test", key_type=mock_array2, value_type=mock_array3)
    vafpy.datatypes.Map(name="MockMap1", namespace="test", key_type=mock_struct, value_type=my_vector_fix)

    vafpy.datatypes.Vector(name="RefVector", namespace="test", datatype=mock_array2)

    vafpy.datatypes.Array(name="RefArray", namespace="test", datatype=mock_vector4, size=2)

    mock_interface = vafpy.ModuleInterface(name="MockInterface", namespace="test")
    mock_interface.add_data_element(name="struct", datatype=mock_struct)
    mock_interface.add_data_element(name="array", datatype=mock_array2)
    mock_interface.add_data_element(name="vector", datatype=mock_vector4)

    mock_interface_func = vafpy.ModuleInterface(name="MockInterfaceFWraps", namespace="interfaces1")
    mock_interface_func.add_operation(
        name="func1",
        in_parameter={"in1": mock_array2, "in2": mock_vector4},
        out_parameter={"out1": mock_array3, "out2": mock_vector4},
        inout_parameter={"inout1": mock_array1, "inout2": mock_array2},
    )

    mock_mod = vafpy.ApplicationModule(name="temp", namespace="test")
    mock_mod.add_provided_interface(instance_name="MockIf1", interface=mock_interface)
    mock_mod.add_provided_interface(instance_name="MockIf2", interface=mock_interface_func)

    # assert reference in struct
    mock_struct_goal = {
        "W": "test::MockVector3",
        "H": "test::MockVector2",
        "Y": "test::MockArray3",
        "M": "test::MockArray1",
        "C": "test::MockArray2",
        "A": "test::MockVector4",
    }
    for subelement in model_runtime.main_model.DataTypeDefinitions.Structs[-1].SubElements:
        assert __get_type_ref_string(subelement.TypeRef) == mock_struct_goal[subelement.Name]
    # assert corresponding typerefs
    mock_typeref_goal = {
        "MockTypeRef": "test::MockArray3",
    }
    assert len(model_runtime.main_model.DataTypeDefinitions.TypeRefs) == len(mock_typeref_goal)
    for typeref in model_runtime.main_model.DataTypeDefinitions.TypeRefs:
        assert __get_type_ref_string(typeref.TypeRef) == mock_typeref_goal[typeref.Name]

    # assert reference in maps
    assert (
        __get_type_ref_string(model_runtime.main_model.DataTypeDefinitions.Maps[-2].MapKeyTypeRef) == "test::MockArray2"
    )
    assert (
        __get_type_ref_string(model_runtime.main_model.DataTypeDefinitions.Maps[-2].MapValueTypeRef)
        == "test::MockArray3"
    )
    assert (
        __get_type_ref_string(model_runtime.main_model.DataTypeDefinitions.Maps[-1].MapKeyTypeRef) == "test::MockStruct"
    )
    assert (
        __get_type_ref_string(model_runtime.main_model.DataTypeDefinitions.Maps[-1].MapValueTypeRef)
        == "test::MyVectorFixed"
    )

    # assert reference in vectors
    assert __get_type_ref_string(model_runtime.main_model.DataTypeDefinitions.Vectors[-1].TypeRef) == "test::MockArray2"
    # assert reference in arrays
    assert __get_type_ref_string(model_runtime.main_model.DataTypeDefinitions.Arrays[-1].TypeRef) == "test::MockVector4"

    # assert reference in module interface
    mock_interface_goal = {
        "struct": "test::MockStruct",
        "array": "test::MockArray2",
        "vector": "test::MockVector4",
    }
    for data_element in model_runtime.main_model.ModuleInterfaces[0].DataElements:
        assert __get_type_ref_string(data_element.TypeRef) == mock_interface_goal[data_element.Name]

    mock_interface_fwrap_goal = {
        "in1": "test::MockArray2",
        "in2": "test::MockVector4",
        "out1": "test::MockArray3",
        "out2": "test::MockVector4",
        "inout1": "test::MockArray1",
        "inout2": "test::MockArray2",
    }
    for param in model_runtime.main_model.ModuleInterfaces[1].Operations[0].Parameters:
        assert __get_type_ref_string(param.TypeRef) == mock_interface_fwrap_goal[param.Name]


def test_bug_cleanup_vss_model(tmp_path) -> None:
    """FTAF-399: Test Bug on Cleanup of VSS Model"""
    path_out = tmp_path / "ftaf_399"

    copytree(UT_PATH / "test_data/ftaf_399", path_out)

    mock_vafpy(path_out, ["vss", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.APP_MODULE)

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(UT_PATH / "test_data/ftaf_399/model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_bug_cleanup_ftaf_422(tmp_path) -> None:
    """FTAF-422: Test vafpy cleanup fails with source node ::uint32_t not in graph"""
    path_out = tmp_path / "ftaf_422"

    copytree(UT_PATH / "test_data/ftaf_422", path_out)

    mock_vafpy(path_out, ["imported_models/interface", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.APP_MODULE)

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(UT_PATH / "test_data/ftaf_422/model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_bug_ftaf_553(tmp_path) -> None:
    """FTAF-553: Custom datatype as operation parameter is removed from model"""
    path_out = tmp_path / "ftaf_553"

    copytree(UT_PATH / "test_data/ftaf_553", path_out)

    mock_vafpy(path_out, ["imported_models/interfaces", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.APP_MODULE)

    vafmodel.load_json(path_out / "model.json")


def test_ftaf_576_string_base_type(tmp_path) -> None:
    """FTAF-576: Add string to basetypes"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "ftaf_576_string_base_type"
    path_out.mkdir(parents=True, exist_ok=True)
    copyfile(UT_PATH / "test_data/ftaf_576/model.py", path_out / "model.py")

    mock_vafpy(path_out, [])

    save_main_model(path_out / "model.json", cleanup=True, project_type=ProjectType.INTEGRATION)

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(UT_PATH / "test_data/ftaf_576/model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())
