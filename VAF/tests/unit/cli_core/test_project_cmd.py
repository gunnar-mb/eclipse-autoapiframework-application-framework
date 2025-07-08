"""
example tests
"""

import importlib
import inspect
import os
import sys
from pathlib import Path
from types import ModuleType
from unittest import mock

import pytest

from vaf.cli_core.bootstrap import project_init_cmd
from vaf.cli_core.main import project_cmd
from vaf.vafpy.elements import ApplicationModule


def import_by_file_name(file_path: str) -> ModuleType:
    """importlib.import_module somehow fails in pytest and can't find the modules"""
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


def mock_importlib_import_module(name: str) -> ModuleType:
    """importlib.import_module somehow fails in CI pytest and can't find the modules"""
    module = None
    if name in [
        f"application_modules.import_{mocked_module}"
        for mocked_module in ["gerberit", "instances", "wakanda", "saufleisch"]
    ]:
        file_dir, file_name = name.split(".")
        module = import_by_file_name(f"{sys.path[-1]}/{file_dir}/{file_name}.py")
    if module is None:
        module = importlib.import_module(name)
    return module


class TestProjectCmd:  # pylint: disable=too-few-public-methods
    """
    Class docstrings are also parsed
    """

    def test_project_init_default(self, tmp_path: Path) -> None:
        """
        .. test:: First unit test greet()
            :id: TCASE-INTEG_001
            :links: CREQ-001

            First unit test for greet()
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_init_cmd.ProjectInitCmd()
        pj.integration_project_init("UutestProject", str(tmp_path))
        assert (tmp_path / "UutestProject").is_dir()

    def test_project_init_non_existing(self, tmp_path: Path) -> None:
        """
        .. test:: Test the reporting of an error if the passed template is not
                  existing.
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_init_cmd.ProjectInitCmd()
        with pytest.raises(Exception):
            pj.integration_project_init("UutestProject", str(tmp_path), "not-existing")

    def test_missing_vafconfig(self, tmp_path: Path) -> None:
        """
        Test verifying the existence of VAF_CFG_FILE
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_init_cmd.ProjectInitCmd()

        pwd = Path(__file__).resolve().parent
        broken_template = pwd / "data" / "broken_templates" / "missing_vafconfig"
        with pytest.raises(Exception):
            pj.integration_project_init("UutestProject2", str(tmp_path), str(broken_template))

    @pytest.mark.slow
    def test_generate_integration(self, tmp_path: Path) -> None:
        """FTAF-263: Identical Name of Application Modules are not allowed
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_cmd.ProjectCmd()
        pj.generate_integration(
            str(Path(__file__).parent / "test_data/mock_prj/model/vaf/model.json"),
            str(tmp_path),
            "PRJ",
        )

    @pytest.mark.slow
    def test_generate_app_module(self, tmp_path: Path) -> None:
        """FTAF-263: Identical Name of Application Modules are not allowed"""
        pj = project_cmd.ProjectCmd()
        pj.generate_app_module(
            str(Path(__file__).parent / "test_data/mock_prj/model/app/model.json"),
            str(tmp_path),
        )

    def test_generate_app_modules_identical_name(self, tmp_path: Path) -> None:
        """FTAF-263: Identical Name of Application Modules are not allowed
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_cmd.ProjectCmd()
        with pytest.raises(RuntimeError) as err:
            pj.generate_integration(
                str(Path(__file__).parent / "test_data/ftaf_263/model/vaf/model.json"),
                str(tmp_path),
                "PRJ",
            )

        assert (
            " ".join(
                [
                    "ERROR: There are 2 application modules",
                    "with name AppModuleTwin and install path ''.",
                    "Application Module must have a unique pair of name and install path!",
                ]
            )
            in err.value.args[0]
        )

    def test_add_import_appmodule(self, tmp_path: Path) -> None:
        """
        Test to verify create_appmodule & import_appmodule
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_cmd.ProjectCmd()
        pj_init = project_init_cmd.ProjectInitCmd()

        # init project
        pj_init.integration_project_init("ExecuteOrder66", str(tmp_path))
        prj_path = tmp_path / "ExecuteOrder66"

        with mock.patch("importlib.import_module", side_effect=mock_importlib_import_module):
            # add app-module
            pj.create_appmodule("Kackhaus", "Gerberit", str(prj_path), ".", "model/vaf")
            pj.create_appmodule("Forever", "Wakanda", str(prj_path), ".", "model/vaf")

            # init app-module and then import them to integration project
            pj_init.app_module_project_init("Speck", "Saufleisch", str(tmp_path / "SesameStreet"))
            pj.import_appmodule(str(tmp_path / "SesameStreet/Saufleisch"), str(prj_path), ".", "model/vaf")

        os.environ["IMPORT_APPLICATION_MODULES"] = "import"
        # import __init__.py
        init_module = import_by_file_name(str(prj_path / "model/vaf/application_modules/__init__.py"))

        # assert imported app modules
        goal_app_modules = ["Gerberit", "Wakanda", "Saufleisch"]
        imported_app_modules = [
            app_module_name
            for app_module_name, _ in inspect.getmembers(init_module, lambda x: (isinstance(x, ApplicationModule)))
        ]
        assert sorted(imported_app_modules) == sorted(goal_app_modules)

        # assert imported python files
        goal_py_modules = [f"import_{module_name.lower()}" for module_name in goal_app_modules + ["instances"]]
        imported_py_modules = [
            app_module_name for app_module_name, _ in inspect.getmembers(init_module, inspect.ismodule)
        ]
        assert sorted(imported_py_modules) == sorted(goal_py_modules)

    def test_remove_appmodule(self, tmp_path: Path) -> None:
        """
        Test to verify create_appmodule, import_appmodule & remove_appmodule
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_cmd.ProjectCmd()
        pj_init = project_init_cmd.ProjectInitCmd()

        # init project
        pj_init.integration_project_init("ExecuteOrder66", str(tmp_path))
        prj_path = tmp_path / "ExecuteOrder66"

        with mock.patch("importlib.import_module", side_effect=mock_importlib_import_module):
            # add app-module
            pj.create_appmodule("Kackhaus", "Gerberit", str(prj_path), ".", "model/vaf")
            pj.create_appmodule("Forever", "Wakanda", str(prj_path), ".", "model/vaf")

            # init app-module and then import them to integration project
            pj_init.app_module_project_init("Speck", "Saufleisch", str(tmp_path / "SesameStreet"))
            pj.import_appmodule(str(tmp_path / "SesameStreet/Saufleisch"), str(prj_path), ".", "model/vaf")

        for removed in ["Gerberit", "Saufleisch"]:
            # remove Gerberit and Saufleisch
            pj.remove_appmodule(
                prj_path, Path("model/vaf"), [str(prj_path / "src/application_modules" / removed.lower())]
            )
            # assert app modules project and import_<app_module>.py removed
            assert not Path(prj_path / "src/application_modules" / removed.lower()).is_dir()
            assert not Path(prj_path / "model/vaf" / f"import_{removed.lower()}").is_file()

        os.environ["IMPORT_APPLICATION_MODULES"] = "import"
        # import __init__.py
        init_path = prj_path / "model/vaf/application_modules/__init__.py"
        init_module = import_by_file_name(str(init_path))
        # assert imported app modules
        goal_app_modules = ["Wakanda"]
        imported_app_modules = [
            app_module_name
            for app_module_name, _ in inspect.getmembers(init_module, lambda x: (isinstance(x, ApplicationModule)))
        ]
        assert sorted(imported_app_modules) == sorted(goal_app_modules)

        # assert imported python files
        # use text assertion since using mechanism like in test_add_import_addmodule
        # causes interference of the init_module value
        goal_py_modules = [f"import_{module_name.lower()}" for module_name in goal_app_modules]
        not_exist_py_modules = [f"import_{module_name.lower()}" for module_name in ["Gerberit", "Kackhaus"]]
        init_path_content = init_path.read_text()
        assert all(goal in init_path_content for goal in goal_py_modules)
        assert not any(bad_apple in init_path_content for bad_apple in not_exist_py_modules)
