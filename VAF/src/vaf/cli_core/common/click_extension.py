"""Implements custom extensions to the click library"""

import re
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Type

import click
from click_prompt.core.option import ChoiceOption, FilePathOption

from vaf.cli_core.common.utils import ProjectType, _get_default_model_path, get_project_type, get_subprojects_in_path


# pylint: disable-next=missing-param-doc
def choice_option(*args: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Typed decorator to replace the untyped one from click_prompt"""

    def decorator(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        if "cls" not in kwargs:
            kwargs["cls"] = ChoiceOption
        return click.option(*args, **kwargs)(f)

    return decorator


# pylint: disable-next=missing-param-doc
def filepath_option(*args: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Typed decorator to replace the untyped one from click_prompt"""

    def decorator(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        if "cls" not in kwargs:
            kwargs["cls"] = FilePathOption
        return click.option(*args, **kwargs)(f)

    return decorator


# pylint: disable-next=missing-param-doc
def sanatized_str_option(*args: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Click decorator that sanitizes the input string to ensure compatibility with POSIX 'Fully portable filenames'."""

    # pylint:disable-next=unused-argument
    def callback_handler(ctx: click.Context, option: click.Option, value: str) -> Any:
        """Sanatizes the input string to ensure compatibility with POSIX 'Fully portable filenames'.

        Args:
            ctx (click.Context): Click context object.
            option (click.Option): The option instance being handled.
            value (str): The value of the option.
        Returns:
            The value of the option.
        Raises:
            BadParameter: If the value contains invalid characters.
        """
        value = value.strip()
        if not re.match(r"^[a-zA-Z0-9._-]+$", value):
            raise click.BadParameter("Only A-Z, a-z, 0-9, underscores, hyphens and dots are allowed.")
        return value

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        kwargs["callback"] = callback_handler
        return click.option(*args, **kwargs)(func)

    return decorator


def cli_verbose_option(function: Callable[..., Any]) -> Callable[..., Any]:
    """Function to create verbose CLI option that can be reusable in multiple cmds
    Args:
        function: Function to be decorated
    Returns:
        function decorated with click.option
    """
    function = click.option(
        "-v",
        "--verbose",
        "verbose",
        help="Flag to enable verbose mode for debugging.",
        is_flag=True,
    )(function)
    return function


def get_project_type_for_project_dir(project_dir: Optional[str] = None) -> ProjectType:
    """Safely get project type based on project directory.
    Args:
        project_dir: project directory
    Returns:
        ProjectType: Type of the VAF project
    """

    if project_dir is not None:
        return get_project_type(Path(project_dir))  # Use explicitly passed project_dir

    ctx = click.get_current_context(silent=True)
    if ctx and ctx.params.get("project_dir"):
        return get_project_type(Path(ctx.params["project_dir"]))  # Use Click context

    return get_project_type(Path())  # Fallback if no Click context


def preserve_params(function: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to preserve the click command parameters in __vaf_click_params__
    Args:
        function: Function to be decorated
    Returns:
        function decorated with with the click params in __vaf_click_params__
    Raises:
        AttributeError: If the function does not have __click_params__
    """
    try:
        params = getattr(function, "__click_params__")
    except AttributeError as e:
        raise AttributeError(
            f"The @preserve_params decorator must be the outermost decorator of the click command {function.__name__}"
        ) from e

    setattr(function, "__vaf_click_params__", params)
    return function


def project_generate_common_click_decorators(function: Callable[..., Any]) -> Callable[..., Any]:
    """Function to create common options for vaf project generate
    Args:
        function: Function to be decorated
    Returns:
        function decorated with click.option
    """
    # verbose
    function = cli_verbose_option(function)
    # -p
    function = click.option(
        "-p",
        "--project-dir",
        type=click.Path(exists=False, file_okay=False, writable=False),
        required=False,
        help="Path to the project directory.",
        default=".",
    )(function)
    # -i
    function = click.option(
        "-i",
        "--input-file",
        type=click.Path(exists=False, dir_okay=False, writable=True),
        required=False,
        help="Path to the project model JSON file.",
        default=lambda: str(
            Path(click.get_current_context().params.get("project_dir", "."))
            / _get_default_model_path(get_project_type_for_project_dir())
            / "model.json"
        ),
    )(function)
    # -b
    function = click.option(
        "-b",
        "--build-dir",
        type=click.Path(exists=False, file_okay=False, writable=False),
        default="build",
        help="Build directory",
        show_default=True,
    )(function)
    # -m
    function = click.option(
        "--manual-merge",
        "manual_merge",
        help="Flag to disable the automatic 3-way merge mechanism on re-generation of user-editable source files.",
        is_flag=True,
    )(function)
    # --skip-model-update
    function = click.option(
        "--skip-model-update",
        "skip_model_update",
        help="Flag to not update model.json before generating the project.",
        is_flag=True,
    )(function)
    # --skip-make-preset
    function = click.option(
        "--skip-make-preset",
        "skip_make_preset",
        help="Flag to skip the make preset call after generating the project.",
        is_flag=True,
    )(function)
    # pass context
    function = click.pass_context(function)
    return function


class DisableForProjectOption(click.Option):
    """This class disables click options for certain project types."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.parse_opts: Mapping[str, Any] | None = None
        self.disable_for_type = kwargs.pop("disable_param_for_project_type", {})
        self.original_callback = kwargs.get("callback", None)
        kwargs["callback"] = self.callback_handler
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx: click.Context, opts: Mapping[str, Any], args: list[str]) -> Any:
        """
        Saves the parsed options for later use.

        Args:
            ctx (click.Context): The Click context object.
            opts (Mapping[str, Any]): A dictionary of parsed options.
            args (list[str]): A list of remaining command-line arguments.
        """
        self.parse_opts = opts
        return super().handle_parse_result(ctx, opts, args)

    def callback_handler(self, ctx: click.Context, option: click.Option, value: str) -> Any:
        """Disables specific options for certain project types.
        Calls the original callback function, if one exists.

        Args:
            ctx (click.Context): Click context object.
            option (click.Option): The option instance being handled.
            value (str): The value of the option.
        Returns:
            The value of the option.
        """
        if value and self.parse_opts is not None and not self.parse_opts.get("help"):
            project_type = get_project_type(Path(value))

            for param in ctx.command.params:
                # Click replaces dashes with underscores in parameter names, so we need to convert them back
                actual_name = getattr(param, "name", "").replace("_", "-")

                # Check if the parameter should be disabled for the current project type,
                # or disable all parameters for unsupported types
                if actual_name in self.disable_for_type.get(project_type, []) or (
                    project_type not in self.disable_for_type.keys()
                    and any(actual_name in sublist for sublist in self.disable_for_type.values())
                ):
                    setattr(param, "prompt_required", False)
                    param.required = False

        if self.original_callback:
            return self.original_callback(ctx, option, value)
        return value


def modifying_choice_fp_option(*args: str, choice_to_modify: str = "app-modules") -> Type[FilePathOption]:
    """Function to get the custom click option ModifyingChoiceFpOption.
    This class modifies the specified click choice option and adds application modules paths as choices.

    Args:
        *args (str): Names of the click option
        choice_to_modify (str): Name of the click option to modify
    Returns:
        ModifyingChoiceFpOption class
    """
    choice_to_modify = choice_to_modify.replace("-", "_")

    class ModifyingChoiceFpOption(FilePathOption):  # type: ignore
        """This class adds application module paths found in the model path as choices to a specified click choice."""

        def __init__(self, _: str, **kwargs: Any) -> None:
            assert args, "Pass option names into modifying_choice_fp_option()"

            self.parse_opts: Mapping[str, Any] | None = None
            self.original_callback = kwargs.get("callback", None)
            kwargs["callback"] = self.callback_handler
            super().__init__(args, **kwargs)

        def handle_parse_result(self, ctx: click.Context, opts: Mapping[str, Any], args: list[str]) -> Any:
            """
            Saves the parsed options for later use.

            Args:
                ctx (click.Context): The Click context object.
                opts (Mapping[str, Any]): A dictionary of parsed options.
                args (list[str]): A list of remaining command-line arguments.
            """
            self.parse_opts = opts
            return super().handle_parse_result(ctx, opts, args)

        def callback_handler(self, ctx: click.Context, option: click.Option, value: str) -> Any:
            """Searches for application modules and add their paths as click choices to the specified click option.
            Calls the original callback function, if one exists.

            Args:
                ctx (click.Context): Click context object.
                option (click.Option): The option instance being handled.
                value (str): The value of the option.
            Returns:
                The value of the option.
            """
            if value and self.parse_opts is not None and not self.parse_opts.get("help"):
                project_type = get_project_type_for_project_dir()
                if project_type == ProjectType.INTEGRATION:
                    project_dir = Path(ctx.params.get("project_dir", "."))
                    app_modules = get_subprojects_in_path(ProjectType.APP_MODULE, project_dir / value)
                    if len(app_modules) < 1:
                        click.echo(f"No application modules found in {project_dir / value}")
                        ctx.exit(1)
                    for parameter in ctx.command.params:
                        if choice_to_modify == parameter.name and isinstance(parameter.type, click.Choice):
                            parameter.type.choices = [module.as_posix() for module in app_modules]
                            if len(app_modules) == 1 and not self.parse_opts.get(choice_to_modify):
                                # This is required for the interactive prompt to work with only one choice.
                                # If the parameter is specified on the CLI `multiple` has always be True,
                                # regardless of the number of choices.
                                parameter.multiple = False

            if self.original_callback:
                return self.original_callback(ctx, option, value)
            return value

    return ModifyingChoiceFpOption
