"""
example tests
"""

# mypy: disable-error-code="no-untyped-def"

import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from vaf.cli_core.bootstrap import project_init_cmd as project_init
from vaf.cli_core.main import make_cmd as makecmd
from vaf.cli_core.main import project_cmd as project


@contextmanager
def change_dir(dir: Path):
    current_dir = Path.cwd().as_posix()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(current_dir)


@pytest.fixture(scope="session")
def shared_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("test")


class TestMakeCmd:  # pylint: disable=too-few-public-methods
    """
    Class docstrings are also parsed
    """

    proj_name = "TestProject"
    proj_parent_dir = Path(__file__).parent / "tmp"
    build_dir = "build"

    @pytest.mark.dependency()
    def test_make_preset_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the Preset command.
        """
        pj_init = project_init.ProjectInitCmd()
        pj_init.integration_project_init(str(self.proj_name), str(shared_tmp_path))
        proj_dir = shared_tmp_path / self.proj_name
        assert Path(proj_dir).is_dir()  # make sure we have a generated project
        current_dir = Path.cwd().as_posix()
        make = makecmd.MakeCmd()
        make.preset(self.build_dir, "gcc12__x86_64-pc-linux-elf", "Release", "", str(current_dir / proj_dir))
        assert (proj_dir / self.build_dir).is_dir()  # make sure we have a generated build folder

    # @pytest.mark.slow
    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_preset_default"])
    def test_make_application_modules_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the create_appmodule command. Depends on preset successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        pj = project.ProjectCmd()
        pj.create_appmodule(
            name="AppModule1",
            namespace="demo",
            project_dir=proj_dir.as_posix(),
            rel_pre_path=".",
            model_dir="model/vaf",
        )
        pj.create_appmodule(
            name="AppModule2",
            namespace="demo",
            project_dir=proj_dir.as_posix(),
            rel_pre_path="demo",
            model_dir="model/vaf",
        )
        pj = project.ProjectCmd()
        test_dir = Path(__file__).parent
        pj.generate_app_module(
            input_file=str(test_dir / "test_data/ftaf_305/model/vaf/model_module1.json"),
            project_dir=proj_dir.as_posix() + "/src/application_modules/app_module1",
        )
        pj.generate_app_module(
            input_file=str(test_dir / "test_data/ftaf_305/model/vaf/model_module2.json"),
            project_dir=proj_dir.as_posix() + "/src/application_modules/demo/app_module2",
        )

    # @pytest.mark.slow
    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_application_modules_default"])
    def test_make_build_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the build command. Depends on create_appmodule successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        pj = project.ProjectCmd()
        test_dir = Path(__file__).parent

        pj.generate_integration(
            input_file=str(test_dir / "test_data/ftaf_305/model/vaf/model.json"),
            project_dir=proj_dir,
            mode="PRJ",
        )

        make = makecmd.MakeCmd()
        with change_dir(proj_dir):
            make.build("conan-release")
        assert (
            proj_dir / self.build_dir / "Release/bin/DemoExecutable/bin/DemoExecutable"
        ).is_file()  # make sure we have a built executable

    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_build_default"])
    def test_make_install_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the install command. Depends on build successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        make = makecmd.MakeCmd()
        with change_dir(proj_dir):
            make.install("conan-release")
        assert (proj_dir / self.build_dir / "Release/install/opt/DemoExecutable/bin/DemoExecutable").is_file()

    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_install_default"])
    def test_make_clean_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the build command. Depends on preset successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        make = makecmd.MakeCmd()
        with change_dir(proj_dir):
            make.clean("conan-release")
        assert not (proj_dir / self.build_dir / "Release/bin/DemoExecutable/bin/DemoExecutable").is_file()
