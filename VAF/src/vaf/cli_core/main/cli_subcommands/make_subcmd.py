"""Source code for vaf project subcommands"""

from pathlib import Path

import click

from vaf.cli_core.common.click_extension import cli_verbose_option, preserve_params
from vaf.cli_core.common.utils import ProjectType, get_project_type
from vaf.cli_core.main.make_cmd import MakeCmd


# vaf make preset #
@preserve_params
@cli_verbose_option
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "-b",
    "--build-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=lambda: str(Path(click.get_current_context().params.get("project_dir", ".")) / "build"),
    help="Build directory",
    show_default=True,
)
@click.option(
    "-t",
    "--build-type",
    help="Type variant of build, either 'Debug' or 'Release'",
    required=True,
    type=click.Choice(["Debug", "Release"], case_sensitive=True),
    default="Release",
    show_default=True,
)
@click.option(
    "-c",
    "--compiler",
    help="Compiler version, either 'gcc11__x86_64-pc-linux-elf' or 'gcc12__x86_64-pc-linux-elf'",
    required=False,
    type=click.Choice(["gcc11__x86_64-pc-linux-elf", "gcc12__x86_64-pc-linux-elf"], case_sensitive=True),
    default="gcc12__x86_64-pc-linux-elf",
    show_default=True,
)
@click.option(
    "-d",
    "--defines",
    type=str,
    default="",
    help="Additional defines, -d -DVAF_BUILD_TESTS=OFF",
    show_default=True,
)
def make_preset(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    project_dir: str, build_dir: str, compiler: str, build_type: str, defines: str, verbose: bool = False
) -> None:
    """
    Preset build.
    :param project_dir: Project directory.
    :param build_dir: Build directory.
    :param compiler: Compiler version.
    :param build_type: Debug or release build.
    :param defines: Set defines.
    :param verbose: enable verbose mode (show full CMake output)
    """
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd(verbose)
        cmd.preset(build_dir, compiler, build_type, defines, Path(project_dir).as_posix())
    else:
        click.echo("\nInvalid VAF project type for make preset command.")


# vaf make build #
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "--preset",
    required=True,
    type=click.Choice(["conan-debug", "conan-release"], case_sensitive=True),
    default="conan-release",
    show_default=True,
)
def make_build(project_dir: str, preset: str) -> None:
    """
    Build the project artifacts.
    :param project_dir: Project directory.
    :param preset: CMake preset.

    """
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd()
        cmd.build(preset)
    else:
        click.echo("\nInvalid VAF project type for make build command.")


# vaf make clean #
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "--preset",
    required=True,
    type=click.Choice(["conan-debug", "conan-release"], case_sensitive=True),
    default="conan-release",
    show_default=True,
)
def make_clean(project_dir: str, preset: str) -> None:
    """
    Clean up the project build directory.
    :param project_dir: Project directory.
    :param preset: CMake preset.

    """
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd()
        cmd.clean(preset)
    else:
        click.echo("\nInvalid VAF project type for make clean command.")


# vaf make install #
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "--preset",
    required=True,
    type=click.Choice(["conan-debug", "conan-release"], case_sensitive=True),
    default="conan-release",
    show_default=True,
)
def make_install(project_dir: str, preset: str) -> None:
    """
    Install the built artifacts to build/<build-type>/install directory.
    :param project_dir: Project directory.
    :param preset: CMake preset.

    """
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd()
        cmd.install(preset)
    else:
        click.echo("\nInvalid VAF project type for make install command.")
