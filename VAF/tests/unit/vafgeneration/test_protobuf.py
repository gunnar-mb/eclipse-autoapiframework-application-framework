"""
protobuf generator test
"""

# pylint: disable=duplicate-code
import copy
import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.vafgeneration import vaf_protobuf_serdes
from vaf.vafpy import import_model
from vaf.vafpy.model_runtime import model_runtime


# pylint: disable=too-many-statements
# pylint: disable=missing-any-param-doc
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=too-few-public-methods
# mypy: disable-error-code="no-untyped-def"
class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for silkit generation"""
        m = vafmodel.MainModel()

        m.DataTypeDefinitions = vafmodel.DataTypeDefinition()
        m.DataTypeDefinitions.Arrays.append(
            vafmodel.Array(
                Name="MyArray",
                Namespace="test",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Size=1,
            )
        )
        m.DataTypeDefinitions.Vectors.append(
            vafmodel.Vector(
                Name="MyVector",
                Namespace="test",
                TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
            )
        )
        sub1 = vafmodel.SubElement(
            Name="MySub1",
            TypeRef=vafmodel.DataType(Name="MyStruct", Namespace="test2"),
        )
        sub2 = vafmodel.SubElement(
            Name="MySub2",
            TypeRef=vafmodel.DataType(Name="MyVector", Namespace="test"),
        )
        m.DataTypeDefinitions.Structs.append(
            vafmodel.Struct(
                Name="MyStruct",
                Namespace="test",
                SubElements=[sub1, sub2],
            )
        )
        m.DataTypeDefinitions.Strings.append(
            vafmodel.String(
                Name="MyString",
                Namespace="test",
            )
        )
        literals = [
            vafmodel.EnumLiteral(
                Label="MyLit1",
                Value=0,
            ),
            vafmodel.EnumLiteral(
                Label="MyLit2",
                Value=1,
            ),
            vafmodel.EnumLiteral(
                Label="MyLit3",
                Value=4,
            ),
        ]
        m.DataTypeDefinitions.Enums.append(
            vafmodel.VafEnum(
                Name="MyEnum",
                Namespace="test",
                Literals=literals,
            )
        )
        m.DataTypeDefinitions.Maps.append(
            vafmodel.Map(
                Name="MyMap",
                Namespace="test",
                MapKeyTypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                MapValueTypeRef=vafmodel.DataType(Name="MyString", Namespace="test"),
            )
        )
        m.DataTypeDefinitions.TypeRefs.append(
            vafmodel.TypeRef(
                Name="MyTypeRef",
                Namespace="test",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
            )
        )

        m.DataTypeDefinitions.Arrays.append(
            vafmodel.Array(
                Name="MyArray",
                Namespace="test2",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Size=1,
            )
        )
        m.DataTypeDefinitions.Vectors.append(
            vafmodel.Vector(
                Name="MyVector",
                Namespace="test2",
                TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
            )
        )
        sub1 = vafmodel.SubElement(
            Name="MySub1",
            TypeRef=vafmodel.DataType(Name="MyStruct", Namespace="test2"),
        )
        sub2 = vafmodel.SubElement(
            Name="MySub2",
            TypeRef=vafmodel.DataType(Name="MyVector", Namespace="test2"),
        )
        m.DataTypeDefinitions.Structs.append(
            vafmodel.Struct(
                Name="MyStruct",
                Namespace="test2",
                SubElements=[sub1, sub2],
            )
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

        silkit_connection_point = vafmodel.SILKITConnectionPoint(
            Name="CPoint",
            ServiceInterfaceName="MyInterface",
            RegistryUri="silkit://localhost:8500",
        )

        m.PlatformProviderModules.append(
            vafmodel.PlatformModule(
                Name="MyProviderModule",
                Namespace="test",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=silkit_connection_point,
            )
        )

        m.PlatformConsumerModules.append(copy.deepcopy(m.PlatformProviderModules[0]))
        m.PlatformConsumerModules[0].Name = "MyConsumerModule"

        m.SILKITAdditionalConfiguration = vafmodel.SILKITAdditionalConfigurationType(
            ConnectionPoints=[silkit_connection_point],
        )

        tmp_file = tmp_path / "tmp.json"
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(m.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True, by_alias=True))

        import_model(str(tmp_file))

        vaf_protobuf_serdes.generate(model_runtime, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        pm_path = tmp_path / "src-gen/libs/protobuf_serdes/proto"
        assert filecmp.cmp(
            pm_path / "protobuf_test.proto",
            script_dir / "protobuf/protobuf_test.proto",
        )
        assert filecmp.cmp(
            pm_path / "protobuf_test2.proto",
            script_dir / "protobuf/protobuf_test2.proto",
        )


# pylint: enable=too-many-statements
