"""Generator library for generating the complete VAF project"""

import shutil
from pathlib import Path
from typing import List

from vaf import vafmodel
from vaf.cli_core.common.exceptions import VafProjectGenerationError
from vaf.vafpy import import_model
from vaf.vafpy.model_runtime import model_runtime

from .generation import is_silkit_used

# Utils
from .vaf_application_module import generate_app_module_project_files

# Build system files generators
from .vaf_cmake_common import generate as generate_cmake_common
from .vaf_conan import generate as generate_conan_deps
from .vaf_generate_common import get_ancestor_model, merge_after_regeneration

# VAF generators
from .vaf_interface import generate_module_interfaces as generate_interface
from .vaf_protobuf_serdes import generate as generate_protobuf_serdes
from .vaf_std_data_types import generate as generate_vaf_std_data_types


def validate_application_module(app_module: vafmodel.ApplicationModule) -> None:
    """Function to validate a single application model
    Args:
        app_module: Application Module to be validated
    Raises:
        VafProjectGenerationError: If InstallationPath is not defined
    """
    if app_module.ImplementationProperties is None:
        raise VafProjectGenerationError(f"ImplementationProperties for application module {app_module.Name}  missing!")
    if app_module.ImplementationProperties.InstallationPath is None:
        raise VafProjectGenerationError(f"InstallationPath for application module {app_module.Name}  missing!")


def _print_info(header: str, content: str = "") -> None:
    columns = shutil.get_terminal_size().columns
    remaining_columns = columns - len(header) - 2  # Two spaces around the header
    if remaining_columns <= 0:
        prefix_cnt = postfix_cnt = 0
    else:
        prefix_cnt = remaining_columns // 2
        postfix_cnt = remaining_columns // 2 + (remaining_columns % 2 > 0)

    print(f"\n{prefix_cnt * '-'} {header} {postfix_cnt * '-'}")
    if content:
        print("\n".join([content, f"{columns * '-'}\n"]))


def generate_application_module(  # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-branches
    model_file: str,
    project_dir: str,
    execute_merge: bool = True,
    verbose_mode: bool = False,
) -> None:
    """Generates all app modules files & operations
    Args:
        model_file (str): Path to the VAF model JSON
        project_dir (str): Path to the output directory
        execute_merge (bool): Flag to enable/disable automatic merge changes after regeneration
        verbose_mode (bool): Flag to enable verbose mode
    Raises:
        SystemError: If there is a system-related error during cleanup.
        ValueError: If the given model contains more or less application modules than one.
    """
    list_merge_relevant_files: List[str] = []

    # clean model runtime before every run
    model_runtime.reset()
    # import json as model_runtime
    import_model(model_file)
    main_model = model_runtime.main_model
    path_output_dir = Path(project_dir)
    if len(main_model.ApplicationModules) != 1:
        raise ValueError(
            "".join(
                [
                    "An application module model needs exactly one application module, ",
                    f"but found {len(main_model.ApplicationModules)}",
                ]
            )
        )
    print(f"Generate app-module in {path_output_dir}\n\n")

    # define flag for merge: execute merge == True and not first time
    # (first time: if src-gen folder only contains one file - conan_deps.list)
    execute_merge &= len(list((path_output_dir / "src-gen").glob("*"))) != 1

    for subdir_name in ["src-gen", "test"]:
        if (path_output_dir / subdir_name).is_dir():
            try:
                shutil.rmtree(path_output_dir / subdir_name)
            except OSError as e:
                raise SystemError(
                    f'Folder "{(path_output_dir / subdir_name).absolute().as_posix()}" could not be removed due to {e}!'
                ) from e

    # This generator needs to run before calling get_paths()
    generate_conan_deps(main_model, path_output_dir, verbose_mode)

    _print_info("VAF GENERATE APP-MODULE: STEP 1", "Generating module interfaces files")
    generate_interface(main_model, path_output_dir, verbose_mode)

    _print_info("VAF GENERATE APP-MODULE: STEP 2", f"Generating source files based on: {model_file}")
    list_merge_relevant_files = generate_app_module_project_files(
        main_model.ApplicationModules[0], path_output_dir, is_ancestor=False, verbose_mode=verbose_mode
    )
    print("SUCCESS: Source files generated!")
    # check for "ancestor" model.json (model.json~)
    ancestor_model = get_ancestor_model(model_file) if execute_merge else None
    # generate ancestor files if this exists and merge will be performed
    if ancestor_model is not None:
        if verbose_mode:
            print("VERBOSE: Generating ancestor files for auto-merge")
        generate_app_module_project_files(
            ancestor_model.ApplicationModules[0],
            path_output_dir,
            is_ancestor=True,
            verbose_mode=verbose_mode,
        )

    _print_info("VAF GENERATE APP-MODULE: STEP 3", "Generating datatypes using std generator")
    generate_vaf_std_data_types(model_runtime, path_output_dir, verbose_mode)

    if is_silkit_used(main_model):
        generate_protobuf_serdes(model_runtime, path_output_dir, verbose_mode)

    # must run as last generator
    # No files to merge when generating for app-modules
    _ = generate_cmake_common(
        main_model, path_output_dir, generate_for_application_module=True, verbose_mode=verbose_mode
    )
    print("SUCCESS: Datatypes generated!")

    # execute merge if list of user files are not empty
    if execute_merge and list_merge_relevant_files:
        _print_info("VAF GENERATE APP-MODULE: STEP 4", "Merging existing source files with results from step 1")
        # solve conflicts for user files
        merge_after_regeneration(path_output_dir, list_merge_relevant_files, verbose_mode)
        _print_info("SUCCESS: MERGE EXECUTED!")
