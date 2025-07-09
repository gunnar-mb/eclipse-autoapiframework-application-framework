"""
CaC support tests
"""

import copy
import filecmp
import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import List

from vaf import vafmodel, vafpy
from vaf.vafgeneration import vaf_cac_support


# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=missing-function-docstring
# pylint: disable=duplicate-code
# mypy: disable-error-code="no-untyped-def"
class Brahma:  # pylint: disable=dangerous-default-value
    """
    Here comes the God of Creation
    """

    @staticmethod
    def create_dummy_data_element(
        name: str = "dummy_element", namespace: str = "", data_type: str = "uint64_t"
    ) -> vafmodel.DataElement:
        return vafmodel.DataElement(
            Name=name,
            TypeRef=vafmodel.DataType(Name=data_type, Namespace=namespace),
        )

    @staticmethod
    def create_dummy_parameter(
        name: str = "dummy_parameter",
        namespace: str = "",
        data_type: str = "uint64_t",
        direction: vafmodel.ParameterDirection = vafmodel.ParameterDirection.OUT,
    ) -> vafmodel.Parameter:
        return vafmodel.Parameter(
            Name=name,
            TypeRef=vafmodel.DataType(Name=data_type, Namespace=namespace),
            Direction=direction,
        )

    @staticmethod
    def create_dummy_operation(
        name: str = "DummyOp",
        parameters: List[vafmodel.Parameter] = [create_dummy_parameter()],
    ) -> vafmodel.Operation:
        return vafmodel.Operation(Name=name, Parameters=parameters)

    @staticmethod
    def create_dummy_module_interface(
        name: str = "DummyInterface",
        namespace: str = "nada",
        data_elements: List[vafmodel.DataElement] = [create_dummy_data_element()],
        operations: List[vafmodel.Operation] = [create_dummy_operation()],
    ) -> vafmodel.ModuleInterface:
        return vafmodel.ModuleInterface(
            Name=name, Namespace=namespace, DataElements=data_elements, Operations=operations
        )


class TestIntegration:  # pylint: disable=too-few-public-methods
    """
    Class docstrings are also parsed
    """

    @staticmethod
    def __process_cac(
        model: vafmodel.MainModel, path: Path, file_name: str = "model.json", generate_type: str = "silkit"
    ) -> None:
        with open(path / file_name, "w", encoding="utf-8") as json_file:
            json_file.write(model.model_dump_json(indent=2, by_alias=True))
        ## generate silkit.py
        vaf_cac_support.generate(path, file_name, generate_type, path)

    def test_basic_generation(self, tmp_path) -> None:
        """
        .. test:: First unit test greet()
            :id: TCASE-INTEG_001
            :links: CREQ-001

            First unit test for greet()
        """

        m = vafmodel.MainModel(
            SILKITAdditionalConfiguration=vafmodel.SILKITAdditionalConfigurationType(ConnectionPoints=[])
        )

        data_elements: list[vafmodel.DataElement] = []
        operations: list[vafmodel.Operation] = []

        data_elements.append(
            vafmodel.DataElement(
                Name="my_data_element1",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
            )
        )

        data_elements.append(
            vafmodel.DataElement(
                Name="my_data_element2",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                InitialValue="{64}",
            )
        )

        parameters: list[vafmodel.Parameter] = []
        parameters.append(
            vafmodel.Parameter(
                Name="in",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.IN,
            )
        )
        operations.append(vafmodel.Operation(Name="MyVoidOperation", Parameters=parameters))

        parameters.append(
            vafmodel.Parameter(
                Name="out",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.OUT,
            )
        )
        parameters.append(
            vafmodel.Parameter(
                Name="inout",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.INOUT,
            )
        )
        operations.append(vafmodel.Operation(Name="MyOperation", Parameters=parameters))

        operations.append(
            vafmodel.Operation(
                Name="MyGetter",
                Parameters=[
                    vafmodel.Parameter(
                        Name="a",
                        TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                        Direction=vafmodel.ParameterDirection.OUT,
                    )
                ],
            )
        )

        operations.append(
            vafmodel.Operation(
                Name="MySetter",
                Parameters=[
                    vafmodel.Parameter(
                        Name="a",
                        TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                        Direction=vafmodel.ParameterDirection.IN,
                    )
                ],
            )
        )

        m.ModuleInterfaces.append(
            vafmodel.ModuleInterface(
                Name="MyInterface",
                Namespace="test",
                DataElements=data_elements,
                Operations=operations,
            )
        )

        m.PlatformProviderModules.append(
            vafmodel.PlatformModule(
                Name="MyProviderModule",
                Namespace="nsexec::nstest",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=vafmodel.SILKITConnectionPoint(
                    Name="CPoint", ServiceInterfaceName="ServiceName", RegistryUri="silkit://localhost:8500"
                ),
            )
        )

        connection_point = m.PlatformProviderModules[0].ConnectionPointRef
        assert isinstance(connection_point, vafmodel.SILKITConnectionPoint)
        m.SILKITAdditionalConfiguration = vafmodel.SILKITAdditionalConfigurationType(
            ConnectionPoints=[connection_point]
        )

        m.PlatformConsumerModules.append(copy.deepcopy(m.PlatformProviderModules[0]))
        m.PlatformConsumerModules[0].Name = "MyConsumerModule"

        with open(tmp_path / "derived-model.json", "w+", encoding="utf-8") as json_file:
            json_str = m.model_dump_json(indent=2, by_alias=True)
            json_file.write(json_str)

        vaf_cac_support.generate(tmp_path, "derived-model.json", "silkit", tmp_path)

        test_dir = Path(__file__).parent

        assert filecmp.cmp(
            tmp_path / "silkit.py",
            test_dir / "cac_support/silkit.py.example",
        )

    def test_create_unique_module_interface(self, tmp_path: Path) -> None:
        """Resolve FTAF-376: Make module interface in CaC unique
        Args:
            tmp_path: pytest tmp_path fixture
        """

        def __import_by_file_name(file_path: str) -> ModuleType:
            file_name = file_path.rsplit("/")[1].rstrip(".py")
            spec = importlib.util.spec_from_file_location(file_name, file_path)
            if spec:
                module = importlib.util.module_from_spec(spec)
                if module and spec.loader:
                    sys.modules[file_name] = module
                    spec.loader.exec_module(module)

            if not module:
                raise RuntimeError(f"Failed to import module in {file_path}")

            return module

        def __assert_cac_result(list_interfaces: List[vafpy.ModuleInterface], goal: List[str]) -> None:
            for idx, interface in enumerate(list_interfaces):
                assert "::".join([interface.Namespace, interface.Name]) == goal[idx]

        ## CASE 1: Easiest -> Unique Name
        mock_model = vafmodel.MainModel(
            ModuleInterfaces=[
                Brahma.create_dummy_module_interface(name="Yeah", namespace="uno::dos::tres::cuatro"),
                Brahma.create_dummy_module_interface(name="Yuhu", namespace="uno::dos::tres::cuatro"),
                Brahma.create_dummy_module_interface(name="Entre", namespace="uno::dos::tres::cuatro"),
            ]
        )
        self.__process_cac(mock_model, tmp_path, "case1.json")
        result_module = __import_by_file_name(str(tmp_path / "silkit.py"))
        __assert_cac_result(
            [
                result_module.Uno.Dos.Tres.Cuatro.yeah,
                result_module.Uno.Dos.Tres.Cuatro.yuhu,
                result_module.Uno.Dos.Tres.Cuatro.entre,
            ],
            [
                "uno::dos::tres::cuatro::Yeah",
                "uno::dos::tres::cuatro::Yuhu",
                "uno::dos::tres::cuatro::Entre",
            ],
        )

        ## CASE 2: Medium -> Identical Name, but last namespace unique
        mock_model = vafmodel.MainModel(
            ModuleInterfaces=[
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::dos::tres::dos"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::dos::tres::tres"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="uno::dos::tres::uno"),
            ]
        )
        self.__process_cac(mock_model, tmp_path, "case2.json")
        result_module = __import_by_file_name(str(tmp_path / "silkit.py"))
        __assert_cac_result(
            [
                result_module.Uno.Dos.Tres.Dos.triplet,
                result_module.Uno.Dos.Tres.Tres.triplet,
                result_module.Uno.Dos.Tres.Uno.triplet,
                result_module.Uno.Dos.Tres.Uno.weird,
            ],
            [
                "uno::dos::tres::dos::Triplet",
                "uno::dos::tres::tres::Triplet",
                "uno::dos::tres::uno::Triplet",
                "uno::dos::tres::uno::Weird",
            ],
        )

        ## CASE 3: Hard -> Identical Name and first & last namespace, but
        mock_model = vafmodel.MainModel(
            ModuleInterfaces=[
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::tres::tres::uno"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::dos::tres::tres"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="uno::dos::tres::uno"),
            ]
        )
        self.__process_cac(mock_model, tmp_path, "case3.json")
        result_module = __import_by_file_name(str(tmp_path / "silkit.py"))
        __assert_cac_result(
            [
                result_module.Uno.Dos.Tres.Tres.triplet,
                result_module.Uno.Dos.Tres.Uno.triplet,
                result_module.Uno.Dos.Tres.Uno.weird,
                result_module.Uno.Tres.Tres.Uno.triplet,
            ],
            [
                "uno::dos::tres::tres::Triplet",
                "uno::dos::tres::uno::Triplet",
                "uno::dos::tres::uno::Weird",
                "uno::tres::tres::uno::Triplet",
            ],
        )

        ## CASE 4: Extra Hard -> Longer Namespaces -> Extra Long
        mock_model = vafmodel.MainModel(
            ModuleInterfaces=[
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::mono::teamo::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="tambien::mono::teamo::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="trabajo::mono::teamo::dos::tres::uno"),
            ]
        )
        self.__process_cac(mock_model, tmp_path, "case4.json")
        result_module = __import_by_file_name(str(tmp_path / "silkit.py"))
        interfaces = [
            result_module.Uno.Mono.Teamo.Dos.Tres.Uno.triplet,
            result_module.Tambien.Mono.Teamo.Dos.Tres.Uno.triplet,
            result_module.Trabajo.Mono.Teamo.Dos.Tres.Uno.triplet,
        ]
        unique_ns = ["uno", "tambien", "trabajo"]
        for idx, interface in enumerate(interfaces):
            assert isinstance(interface, vafpy.ModuleInterface)
            assert (
                "::".join([interface.Namespace, interface.Name])
                == f"{unique_ns[idx]}::mono::teamo::dos::tres::uno::Triplet"
            )

        ## CASE 5: Extreme Hard -> Different Namespace lengths
        mock_model = vafmodel.MainModel(
            ModuleInterfaces=[
                Brahma.create_dummy_module_interface(name="Weird", namespace="uno::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="tres::uno"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="uno"),
            ]
        )
        self.__process_cac(mock_model, tmp_path, "case5.json")
        result_module = __import_by_file_name(str(tmp_path / "silkit.py"))
        interfaces = [
            result_module.Uno.weird,
            result_module.Tres.Uno.weird,
            result_module.Dos.Tres.Uno.weird,
            result_module.Uno.Dos.Tres.Uno.weird,
        ]
        unique_ns = ["", "tres::", "dos::tres::", "uno::dos::tres::"]
        for idx, interface in enumerate(interfaces):
            assert isinstance(interface, vafpy.ModuleInterface)
            assert "::".join([interface.Namespace, interface.Name]) == f"{unique_ns[idx]}uno::Weird"

        ## CASE 6: Supreme Hard -> Long Namespaces + Different Namespaces
        mock_model = vafmodel.MainModel(
            ModuleInterfaces=[
                Brahma.create_dummy_module_interface(name="Triplet", namespace="uno::mono::teamo::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="tambien::mono::teamo::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Triplet", namespace="trabajo::mono::teamo::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="uno::dos::tres::uno"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="tres::uno"),
                Brahma.create_dummy_module_interface(name="Weird", namespace="uno"),
            ]
        )
        self.__process_cac(mock_model, tmp_path, "case6.json")
        result_module = __import_by_file_name(str(tmp_path / "silkit.py"))
        interfaces = [
            result_module.Uno.Mono.Teamo.Dos.Tres.Uno.triplet,
            result_module.Tambien.Mono.Teamo.Dos.Tres.Uno.triplet,
            result_module.Trabajo.Mono.Teamo.Dos.Tres.Uno.triplet,
            result_module.Uno.Dos.Tres.Uno.weird,
            result_module.Tres.Uno.weird,
            result_module.Uno.weird,
        ]
        unique_ns = [
            "uno::mono::teamo::dos::tres::",
            "tambien::mono::teamo::dos::tres::",
            "trabajo::mono::teamo::dos::tres::",
            "uno::dos::tres::",
            "tres::",
            "",
        ]
        for idx, interface in enumerate(interfaces):
            assert isinstance(interface, vafpy.ModuleInterface)
            assert "::".join([interface.Namespace, interface.Name]) == f"{unique_ns[idx]}uno::{interface.Name}"
