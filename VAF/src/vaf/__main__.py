"""Initialize the module.
Could be used to define the public interface of the module.
CLI Function with the click module: e.g. "vaf version --help"
"""

# Python Standard Library imports
import warnings
from importlib import metadata

# External imports
import click

# Internal imports
from vaf.cli_core.bootstrap.cli_subcommands.project_subcmd import project_init
from vaf.cli_core.bootstrap.cli_subcommands.workspace_subcmd import workspace_init
from vaf.cli_core.common.click_help import CLICK_CONTEXT_SETTINGS, CustomHelpGroup, simple_user_warning
from vaf.cli_core.main.cli_subcommands.make_subcmd import make_build, make_clean, make_install, make_preset
from vaf.cli_core.main.cli_subcommands.model_subcmd import model_generate, model_import, model_update
from vaf.cli_core.main.cli_subcommands.project_subcmd import (
    project_create,
    project_generate,
    project_import,
    project_remove,
)

# Define pip package name
PACKAGE_NAME = "vaf"


# Static function to identify the pip package version.
def get_version() -> str:
    """Get the installed version of this pip package.

    Returns:
        str: Version of this pip package.
    """
    return metadata.version(PACKAGE_NAME)


# Switch to simple user warning message without stack trace or file info.
warnings.formatwarning = simple_user_warning


@click.group(
    context_settings=CLICK_CONTEXT_SETTINGS,
    help=f"This is the Vehicle Application Framework command-line interface (vaf-cli) version {get_version()}.",
    cls=CustomHelpGroup,
)
@click.version_option(get_version(), "-v", "--version", message="%(prog)s version %(version)s")
def cli() -> None:
    """This function is the entrypoint for the click arguments cli."""


# Command 'project'
@cli.group()
def project() -> None:
    """Project-related commands."""


# vaf project init #
project.add_command(name="init", cmd=project_init)
# vaf project create #
project.add_command(name="create", cmd=project_create)
# vaf project generate #
project.command(name="generate")(project_generate)
# vaf project import #
project.command(name="import")(project_import)
# vaf project remove #
project.add_command(name="remove", cmd=project_remove)


# Command 'model'
@cli.group()
def model() -> None:
    """Model-related commands."""


# vaf model import #
model.add_command(name="import", cmd=model_import)
# vaf model update #
model.command(name="update")(model_update)
# vaf model generate #
model.command(name="generate")(model_generate)


# Command 'make'
@cli.group()
def make() -> None:
    """Make-related commands."""


# vaf make preset #
make.command(name="preset")(make_preset)
# vaf make build #
make.command(name="build")(make_build)
# vaf make install #
make.command(name="install")(make_install)
# vaf make clean #
make.command(name="clean")(make_clean)


# Command 'workspace'
@cli.group()
def workspace() -> None:
    """Workspace-related commands."""


# vaf project init #
workspace.command(name="init")(workspace_init)


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=no-value-for-parameter
