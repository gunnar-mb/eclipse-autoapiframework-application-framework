"""
example tests
"""

import sys
from pathlib import Path
from shutil import copyfile
from types import ModuleType
from typing import Any, Dict, List

import pytest
from test_project_cmd import import_by_file_name

from vaf.cli_core.bootstrap import project_init_cmd
from vaf.cli_core.common.utils import ProjectType
from vaf.cli_core.main import model_cmd as uut
from vaf.cli_core.main import project_cmd
from vaf.vafmodel import load_json

# mypy: disable-error-code="no-untyped-def"


# needed otherwise importlib error in CI
def mock_importlib_import_module(name: str) -> ModuleType:
    """importlib.import_module somehow fails in pytest and can't find the modules"""
    file_dir, file_name = name.split(".")
    module: ModuleType = import_by_file_name(f"{sys.path[-1]}/{file_dir}/{file_name}.py")

    return module


class TestModelCmd:  # pylint: disable=too-few-public-methods
    """
    Class docstrings are also parsed
    """

    def assert_two_dictionary_identical(self, dict_1: Dict[str, Any], dict_2) -> None:
        """Assert that two dictionaries are identical by checking contents and ignore orders"""

        def __sort_dictionary_by_key(dict_obj: Dict[str, Any]) -> Dict[str, Any]:
            return {key: dict_obj[key] for key in sorted(list(dict_obj.keys()))}

        # first assert the keys
        assert sorted(list(dict_1.keys())) == sorted(list(dict_2.keys()))
        # assert values by ignoring orders
        for key, values in dict_1.items():
            if isinstance(values, Dict):
                assert __sort_dictionary_by_key(dict_1) == __sort_dictionary_by_key(dict_2)
            elif isinstance(values, List):
                assert sorted(values) == sorted(dict_2[key])

    def test_import_vss(self, tmp_path) -> None:
        """Test generate_vss function"""
        model_cmd = uut.ModelCmd()
        model_dir = tmp_path / "tmp_out"
        model_dir.mkdir(exist_ok=True)
        input_json = Path(__file__).parent / "test_data/minimal_vss.json"
        model_cmd.import_vss(str(input_json), str(model_dir))
        assert (model_dir / "vss.py").is_file()

    # @mock.patch("importlib.import_module", side_effect=mock_importlib_import_module)
    def test_ftaf_467(
        self,
        # mocked_importlib: mock.MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        recwarn: pytest.WarningsRecorder,
    ) -> None:
        """FTAF-467: Handling of unconnected app-modules in integration project"""
        test_data_dir = Path(__file__).parent / "test_data/ftaf_467"

        # create project
        prj_setter = project_cmd.ProjectCmd()
        model_cmd = uut.ModelCmd()

        prj_init_setter = project_init_cmd.ProjectInitCmd()

        # init interface project
        prj_init_setter.interface_project_init("Interfaces", tmp_path.as_posix())
        # build interface project & appmodule pat
        interface_prj_path = tmp_path / "Interfaces"
        copyfile(test_data_dir / "interfaces.py", interface_prj_path / "interfaces.py")
        model_cmd.generate(ProjectType.INTERFACE, str(interface_prj_path), "ALL")

        # init project
        prj_init_setter.integration_project_init("SweetHomeAlabama", tmp_path.as_posix())
        prj_path = tmp_path / "SweetHomeAlabama"

        # initiates all app module projects
        for app_module_name in ["Fake", "Mockery", "Invisible"]:
            # add app-module
            prj_setter.create_appmodule("Snuggle", app_module_name, str(prj_path), ".", "model/vaf")

            # copy app-module model
            path_to_app_module_prj_model_dir = prj_path / "src/application_modules" / app_module_name.lower() / "model"

            model_cmd.import_model(
                str(interface_prj_path / "export/Interfaces.json"), path_to_app_module_prj_model_dir.as_posix(), "copy"
            )

            for file_name in [f"{app_module_name.lower()}.py"]:
                copyfile(test_data_dir / file_name, path_to_app_module_prj_model_dir / file_name)

        # add appmodule imported but not used
        # init app-module and then import them to integration project
        prj_init_setter.app_module_project_init("Snuggle", "BlueSparkle", str(tmp_path / "SesameStreet"))
        prj_setter.import_appmodule(str(tmp_path / "SesameStreet/BlueSparkle"), str(prj_path), ".", "model/vaf")

        # copy model.py
        copyfile(test_data_dir / "model.py", prj_path / "model/vaf/model.py")

        monkeypatch.chdir(prj_path)

        model_cmd.generate(ProjectType.INTEGRATION, "model/vaf", "ALL")

        # assert only connected app modules are used in model.json
        goal_model = load_json(str(test_data_dir / "goal-model.json"))
        generated_model = load_json(str(prj_path / "model/vaf/model.json"))
        # assert set fields
        assert goal_model.model_fields_set == generated_model.model_fields_set
        for attr in goal_model.model_fields_set:
            goal_attr_values = getattr(goal_model, attr)
            generated_attr_values = getattr(generated_model, attr)
            # Flaky DataTypeDefinitions: order doesn't matter
            if attr == "DataTypeDefinitions":
                for field in generated_attr_values.model_fields_set:
                    assert all(
                        generated_data in getattr(goal_attr_values, field)
                        for generated_data in getattr(generated_attr_values, field)
                    ), f"{field} is not identical!"
            else:
                assert len(goal_attr_values) == len(generated_attr_values), f"{attr} is not identical!"
                for value in generated_attr_values:
                    assert value in goal_attr_values, f"{value} not in {goal_attr_values}"

        assert len(recwarn) == 1
        assert sorted(str(recwarn[0].message).split("\n")) == [
            f"App Module '{unconnected}' is defined, but not connected in any Executable"
            for unconnected in ["Snuggle::BlueSparkle", "Snuggle::Invisible"]
        ]

    def test_ftaf_460(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        recwarn: pytest.WarningsRecorder,
    ) -> None:
        """FTAF-460: Provide datatypes as CaC in Interface Projects"""
        test_data_dir = Path(__file__).parent / "test_data/ftaf_460"

        # create project
        prj_init_setter = project_init_cmd.ProjectInitCmd()
        model_cmd = uut.ModelCmd()

        # init interface project
        prj_init_setter.interface_project_init("Interfaces", tmp_path.as_posix())
        # init app module project
        prj_init_setter.app_module_project_init("Soft::Drinks::Aint::Beer", "SchocaCola", str(tmp_path))

        # build interface project & appmodule pat
        interface_prj_path = tmp_path / "Interfaces"
        for filename in ["interfaces.py"]:
            copyfile(test_data_dir / filename, interface_prj_path / filename)
        model_cmd.generate(ProjectType.INTERFACE, str(interface_prj_path), "ALL")

        # build app_module project
        app_module_path = tmp_path / "SchocaCola"
        for filename in ["schoca_cola.py"]:
            copyfile(test_data_dir / filename, app_module_path / "model" / filename)
        model_cmd.import_model(
            str(interface_prj_path / "export/Interfaces.json"), str(app_module_path / "model"), "copy"
        )
        model_cmd.generate(ProjectType.APP_MODULE, str(app_module_path / "model"), "ALL")

        # DISABLED -> enable if the generated codes need to be assured
        # run project generate app module
        # dont forget to add pytest.mark.slow if enabled
        # # monkeypatch.chdir(app_module_path)
        # # prj_setter.generate_app_module("model/model.json", ".", "STD")

        # assert only connected app modules are used in model.json
        goal_model = load_json(str(test_data_dir / "goal-model.json"))
        generated_model = load_json(str(app_module_path / "model/model.json"))
        assert goal_model == generated_model
