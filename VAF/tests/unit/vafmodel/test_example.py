"""
Test
"""

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-variable

# from unittest import mock

import json
import os
from pathlib import Path

from vaf import vafmodel


class TestMain:
    """
    TestMain class
    """

    def test_schema_export(self) -> None:
        """test schema export"""
        vafmodel.generate_json_schema("./schema.json")
        Path.unlink(Path("./schema.json"))

    def test_import(self) -> None:
        """Test importing a model"""
        script_dir = Path(os.path.realpath(__file__)).parent
        model_file = script_dir / "test_model.json"
        m = vafmodel.load_json(model_file)
        with open("./export_model.json", "w", encoding="utf-8") as f:
            f.write(m.model_dump_json(indent=2))
            Path.unlink(Path("./export_model.json"))

    def test_import2(self) -> None:
        """Test importing a model"""
        script_dir = Path(os.path.realpath(__file__)).parent
        model_file = script_dir / "test_model2.json"
        m = vafmodel.load_json(model_file)
        with open("./export_model.json", "w", encoding="utf-8") as f:
            f.write(m.model_dump_json(indent=2))
            Path.unlink(Path("./export_model.json"))

    def test_manual_usage(self) -> None:
        """Test for direct usage of the classes"""
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
        j = json.loads(m.model_dump_json())
        assert j["DataTypeDefinitions"]["Arrays"][0]["Name"] == "MyArray"
        assert j["DataTypeDefinitions"]["Arrays"][0]["TypeRef"] == "uint64_t"
        assert j["DataTypeDefinitions"]["Arrays"][0]["Size"] == 1
