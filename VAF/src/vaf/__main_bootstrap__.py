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

# Define pip package name
PACKAGE_NAME = "vaf-bootstrap"


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


# Command 'workspace'
@cli.group()
def workspace() -> None:
    """Workspace-related commands."""


# vaf workspace init #
workspace.command(name="init")(workspace_init)


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=no-value-for-parameter
