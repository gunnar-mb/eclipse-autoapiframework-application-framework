"""Source code for vaf project subcommands"""

from pathlib import Path
from typing import Any

import click
from click.core import ParameterSource

from vaf.cli_core.common.click_extension import (
    DisableForProjectOption,
    choice_option,
    filepath_option,
    get_project_type_for_project_dir,
    modifying_choice_fp_option,
    project_generate_common_click_decorators,
    sanatized_str_option,
)
from vaf.cli_core.common.utils import (
    ProjectType,
    _get_default_model_path,
    get_project_type,
    get_projects_in_path,
)

from ..cli_subcommands.make_subcmd import make_preset
from ..cli_subcommands.model_subcmd import model_generate
from ..model_cmd import ModelCmd
from ..project_cmd import ProjectCmd


# vaf project create group #
@click.group()
def project_create() -> None:
    """Create the specified project artifacts inside the given project."""


# vaf project create app-module #
@project_create.command(name="app-module")
@sanatized_str_option(
    "-n", "--name", type=str, required=True, help="App-module name.", prompt="Enter the name of the app-module"
)
@click.option(
    "--namespace",
    type=str,
    required=True,
    help="App-module namespace.",
    prompt="Enter the namespace of the app-module",
    callback=lambda ctx, param, value: value.strip() if value else "",
)
@filepath_option(
    "-p",
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
    help="Path to the project root directory.",
    default=".",
    prompt="Enter the path to the project root directory",
)
@click.option(
    "--pre-path",
    type=click.Path(exists=False, file_okay=False, writable=True),
    help="Relative pre-path to the app module directory: <project_root_dir>/src/application_modules/<pre_path>/<app_module_dir>",  # pylint: disable=line-too-long
    default=".",
    required=False,
)
@click.option(
    "-m",
    "--model-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=False,
    help="Relative path to VAF model directory from project dir.",
    default=_get_default_model_path(get_project_type_for_project_dir()),
)
def project_create_app_module(namespace: str, name: str, project_dir: str, pre_path: str, model_dir: str) -> None:  # pylint: disable=missing-param-doc
    """Create an application module project and add it to the given integration project."""
    click.echo(f"Creating app-module {namespace}::{name} to {project_dir}/src/application_modules/{pre_path}/{name}.")
    cmd = ProjectCmd()
    cmd.create_appmodule(namespace, name, project_dir, pre_path, model_dir)


# pylint:disable=unused-argument # mode used via kwargs
def __update_vaf_model(
    ctx: click.Context, project_type: ProjectType, project_dir: str, input_file: str, mode: str
) -> None:
    """Function to also update vaf model by calling vaf model generate
    Args:
        input_file: Path to the model.json as string
        mode: type of generation mode used
    """
    model_dir = str(Path(input_file).parent)
    click.echo(f"\nTriggering vaf model generate in {model_dir}...")
    ctx.invoke(model_generate, project_type=project_type, project_dir=project_dir, model_dir=model_dir, mode=mode)
    click.echo(f"\nSUCCESS: VAF model generated and stored in {model_dir}")


# vaf project generate #
@project_generate_common_click_decorators
@click.option(
    "--mode",
    help="Generation mode for integration project, either 'PRJ' or 'ALL'",
    required=False,
    envvar="TYPE_VARIANT",
    type=click.Choice(["PRJ", "ALL"], case_sensitive=False),
    default="PRJ",
    show_default=True,
)
# pylint: disable=missing-param-doc, missing-raises-doc, line-too-long, too-many-arguments, too-many-positional-arguments, too-many-locals
def project_generate(
    ctx: click.Context,
    project_dir: str,
    input_file: str,
    build_dir: str,
    mode: str,
    manual_merge: bool = False,
    verbose: bool = False,
    skip_model_update: bool = False,
    skip_make_preset: bool = False,
) -> None:
    """Generate the source code of the VAF project based on the configuration and generation mode."""

    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    else:
        # Check if the user provided `--input-file` or if it's using the default value
        ctx = click.get_current_context()
        input_file_source = ctx.get_parameter_source("input_file")
        if input_file_source != ParameterSource.DEFAULT and not skip_model_update:
            click.echo("Disabling the model update for a user provided model JSON file.")
            skip_model_update = True

        # Check if required parameters for cmake execution are available
        make_preset_params = getattr(make_preset, "__vaf_click_params__", None)
        assert make_preset_params is not None, (
            "Make sure you have added the @preserve_params decorator to the click command make_preset."
        )
        make_preset_cmd = click.Command(name="", callback=make_preset, params=make_preset_params)

        def __run_make_preset(project_dir: str = project_dir, **kwargs: Any) -> None:
            ctx.invoke(make_preset_cmd, project_dir=project_dir, verbose=verbose, **kwargs)

        def __run_make_preset_debug(**kwargs: Any) -> None:
            __run_make_preset(build_type="Debug", **kwargs)

        def __run_make_preset_release(**kwargs: Any) -> None:
            __run_make_preset(build_type="Release", **kwargs)

        cmd = ProjectCmd(verbose)
        if project_type == ProjectType.INTEGRATION:
            if not skip_model_update:
                click.echo("Updating integration project model before generation.")
                __update_vaf_model(ctx, project_type, project_dir, input_file, mode)
            click.echo(f"Generating integration project for {mode} based on model in {input_file}")
            cmd.generate_integration(
                input_file,
                project_dir,
                mode,
                manual_merge,
            )
            if not skip_make_preset:
                if mode == "ALL":
                    # Execute cmake preset for all included app-module projects
                    for pr_path, _ in get_projects_in_path(Path(project_dir)):
                        __run_make_preset_debug(project_dir=pr_path)
                        __run_make_preset_release(project_dir=pr_path)
                __run_make_preset_debug()
                __run_make_preset_release()

        elif project_type == ProjectType.APP_MODULE:
            click.echo("\nSkipping generation mode selection as the project is not an integration project.")

            if not skip_model_update:
                click.echo("Updating integration project model before generation.")
                __update_vaf_model(ctx, project_type, project_dir, input_file, "PRJ")
            click.echo(f"\nGenerating application module based on model in {input_file}")
            cmd.generate_app_module(
                input_file,
                project_dir,
                manual_merge,
            )
            if not skip_make_preset:
                __run_make_preset_debug()
                __run_make_preset_release()
        else:
            click.echo("\nInvalid VAF project for project generate command.")


# vaf project import #
# This option has to come before all options mentioned in the disable_param_for_project_type dictionary.
@click.option(
    "-p",
    "--project-dir",
    cls=DisableForProjectOption,
    disable_param_for_project_type={
        ProjectType.INTEGRATION: ["input-file"],
        ProjectType.APP_MODULE: ["input-dir"],
    },
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=False,
    help="Path to the project root directory.",
    default=".",
)
@filepath_option(
    "--input-dir",
    type=click.Path(exists=True, file_okay=False, writable=False),
    required=True,
    help="Path to the application module project to be imported. "
    "Applicable only for the app-module import into an integration project.",
    prompt="Enter the path to the application module project to be imported:",
)
@click.option(
    "--pre-path",
    type=click.Path(exists=False, file_okay=False, writable=False),
    help="Relative pre-path to the app-module directory: <project_root_dir>/src/application_modules/<pre_path>/<app_module_dir>",  # pylint: disable=line-too-long
    default=".",
    required=False,
)
@click.option(
    "-m",
    "--model-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=False,
    help="Path to the VAF model directory.",
    default=lambda: str(
        Path(click.get_current_context().params.get("project_dir", "."))
        / _get_default_model_path(get_project_type_for_project_dir())
        / ""
    ),
)
@filepath_option(
    "--input-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the exported VAF model JSON file(from the interface project). "
    "Applicable only for the interface import into an application module project.",
    required=True,
    prompt="Please provide the path to the exported VAF model JSON file",
)
@click.option("--force-import", is_flag=True, help="Carry out import in any case. Will overwrite existing files.")
@click.option("--skip-import", is_flag=True, help="Cancel operation directly in case of a re-import.")
@click.argument("import-mode", default="copy", type=click.Choice(["copy", "reference"], case_sensitive=False))
def project_import(  # pylint: disable=missing-param-doc, too-many-positional-arguments, too-many-arguments
    project_dir: str,
    input_dir: str,
    pre_path: str,
    model_dir: str,
    input_file: str,
    force_import: bool,
    skip_import: bool,
    import_mode: str,
) -> None:
    """Import an interface/app-module project to the given project based on the project type."""

    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type == ProjectType.INTEGRATION:
        click.echo(f"Importing an app-module from {input_dir} to the integration project {model_dir}.")
        project_cmd = ProjectCmd()
        project_cmd.import_appmodule(input_dir, project_dir, pre_path, model_dir)
    elif project_type == ProjectType.APP_MODULE:
        click.echo(f"Importing an interface from {input_file} to the app-module project {model_dir}.")
        model_cmd = ModelCmd()
        model_cmd.import_model(input_file, model_dir, import_mode, force_import, skip_import)
    else:
        click.echo("\nInvalid VAF project type for project import command.")


# vaf project remove group #
@click.group()
def project_remove() -> None:
    """Remove the specified project artifacts from the given project."""


def __validate_integration_project_dir(ctx: click.Context, option: click.Option, value: str) -> str:
    """Validates that the given project directory is an integration project."""
    if get_project_type(Path(value)) != ProjectType.INTEGRATION:
        raise click.BadParameter("This command is only supported for integration projects.")
    return value


# vaf project remove app_module #
@project_remove.command(name="app-module")
@sanatized_str_option(
    "-n", "--name", type=str, required=True, help="App-module name.", prompt="Enter the name of the app-module"
)
@filepath_option(
    "-p",
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
    help="Path to the project root directory.",
    default=".",
    prompt="Enter the path to the project root directory",
    callback=__validate_integration_project_dir,
)
# This option has to come before the --app-modules option, because the app-modules are populated by it's callback
@filepath_option(
    cls=modifying_choice_fp_option("-m", "--model-dir", choice_to_modify="app-modules"),
    type=click.Path(exists=True, file_okay=False, writable=True),
    help="Path to the model directory.",
    default=_get_default_model_path(get_project_type_for_project_dir()),
    prompt="Enter the path to the model directory",
)
@choice_option(
    "--app-modules",
    prompt="Choose one ore more application modules",
    type=click.Choice([]),
    help="Absolute path to the application module project to remove. Specify multiple times for multiple modules.",
    multiple=True,
)
# pylint: disable=missing-param-doc
def project_remove_app_module(project_dir: Path, model_dir: Path, app_modules: list[str]) -> None:
    """Remove an app-module from an integration project."""
    # This workaround is necessary, because of the hacky solution to support only one choice in
    # ModifyingChoiceFpOption.callback_handler()
    if isinstance(app_modules, str):
        app_modules = [app_modules]

    cmd = ProjectCmd()
    cmd.remove_appmodule(project_dir, model_dir, app_modules)
