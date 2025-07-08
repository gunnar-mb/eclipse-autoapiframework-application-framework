"""Generator for shared cmake files
Generates
    - CMakeLists.txt
    - executables/CMakeLists.txt
    - libs/CMakeLists.txt
    - libs/data_types/CMakeLists.txt
"""

from pathlib import Path
from typing import List

from vaf import vafmodel
from vaf.cli_core.common.utils import to_snake_case

from .generation import (
    FileHelper,
    Generator,
    is_silkit_used,
)
from .vaf_generate_common import get_ancestor_file_suffix


def _generate_data_types_cmake(generator: Generator, output_dir: Path, verbose_mode: bool = False) -> None:
    data_types_path = output_dir / "src-gen/libs/data_types"
    generator.set_base_directory(data_types_path)
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True), ".txt", "vaf_cmake_common/data_types_cmake.jinja", verbose_mode=verbose_mode
    )


def _generate_executables_cmake(
    generator: Generator, model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False
) -> None:
    if len(model.Executables) > 0:
        generator.set_base_directory(output_dir / "src-gen/executables")
        exe_subdirs: set[str] = set()
        for e in model.Executables:
            exe_subdirs.add(to_snake_case(e.Name))
        # add existing folders
        if (output_dir / "src-gen/executables").exists():
            exe_subdirs = exe_subdirs.union(
                {it.parts[-1] for it in (output_dir / "src-gen/executables").iterdir() if it.is_dir()}
            )
        exe_subdirs_list = list(exe_subdirs)
        exe_subdirs_list.sort()
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            ".txt",
            "common/cmake_subdirs.jinja",
            subdirs=exe_subdirs_list,
            verbose_mode=verbose_mode,
        )


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def _generate_src_and_src_gen_cmake(
    generator: Generator,
    model: vafmodel.MainModel,
    output_dir: Path,
    is_ancestor: bool,
    generate_for_application_module: bool,
    verbose_mode: bool = False,
) -> List[str]:
    subdirs_src_gen: list[str] = []
    subdirs_src: list[str] = []
    merge_relevant_files: List[str] = []

    subdirs_src_gen.append("libs")
    if len(model.Executables) > 0:
        subdirs_src.append("executables")
        subdirs_src_gen.append("executables")
    if len(model.ApplicationModules) > 0:
        subdirs_src.append("application_modules")

    generator.set_base_directory(output_dir / "src-gen")
    if not is_ancestor:
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            ".txt",
            "common/cmake_subdirs.jinja",
            subdirs=subdirs_src_gen,
            verbose_mode=verbose_mode,
        )

    if not generate_for_application_module:
        generator.set_base_directory(output_dir / "src")
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            f".txt{get_ancestor_file_suffix(is_ancestor)}",
            "common/cmake_subdirs.jinja",
            subdirs=subdirs_src,
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        merge_relevant_files.append("src/CMakeLists.txt")

    return merge_relevant_files


def _generate_test_cmake(
    generator: Generator, model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False
) -> None:
    subdirs_test: list[str] = []
    if len(model.ModuleInterfaces) > 0:
        subdirs_test.append("mocks")

    generator.set_base_directory(output_dir / "test-gen")
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "common/cmake_subdirs.jinja",
        subdirs=subdirs_test,
        verbose_mode=verbose_mode,
    )


def _generate_test_mocks_cmake(
    generator: Generator, model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False
) -> None:
    subdirs_test: list[str] = []
    if len(model.ModuleInterfaces) > 0:
        subdirs_test.append("interfaces")

    if len(subdirs_test) > 0:
        generator.set_base_directory(output_dir / "test-gen" / "mocks")
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            ".txt",
            "common/cmake_subdirs.jinja",
            subdirs=subdirs_test,
            verbose_mode=verbose_mode,
        )


# pylint:disable=too-many-arguments
# pylint:disable=too-many-positional-arguments
def _generate_src_gen_libs_cmake(  # pylint: disable=too-many-branches
    generator: Generator,
    model: vafmodel.MainModel,
    output_dir: Path,
    does_data_type_definition_exist: bool,
    generate_for_application_module: bool,
    verbose_mode: bool = False,
) -> None:  # pylint: disable=line-too-long
    libs_subdirs: list[str] = []

    if does_data_type_definition_exist:
        libs_subdirs.append("data_types")
    libs_subdirs.append("interfaces")
    if is_silkit_used(model):
        libs_subdirs.append("protobuf_serdes")
    if len(model.ApplicationModules) > 0:
        libs_subdirs.append("application_modules_base")
    if not generate_for_application_module:
        for e in model.Executables:
            if len(e.InternalCommunicationModules) > 0:
                libs_subdirs.append("platform_vaf")
                break

        if is_silkit_used(model):
            libs_subdirs.append("platform_silkit")

    if len(libs_subdirs) > 0:
        generator.set_base_directory(output_dir / "src-gen/libs")
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            ".txt",
            "common/cmake_subdirs.jinja",
            subdirs=libs_subdirs,
            verbose_mode=verbose_mode,
        )


def _generate_src_executables_cmake(
    generator: Generator, model: vafmodel.MainModel, output_dir: Path, is_ancestor: bool, verbose_mode: bool = False
) -> List[str]:
    libs_subdirs: list[str] = []
    merge_relevant_files: List[str] = []

    for e in model.Executables:
        libs_subdirs.append(to_snake_case(e.Name))

    if len(model.Executables) > 0:
        generator.set_base_directory(output_dir / "src/executables")
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            f".txt{get_ancestor_file_suffix(is_ancestor)}",
            "common/cmake_subdirs.jinja",
            subdirs=libs_subdirs,
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        merge_relevant_files.append("src/executables/CMakeLists.txt")
    return merge_relevant_files


def generate(
    model: vafmodel.MainModel,
    output_dir: Path,
    is_ancestor: bool = False,
    generate_for_application_module: bool = False,
    verbose_mode: bool = False,
) -> List[str]:
    """Generate shared cmake files

    Args:
        model (vafmodel.MainModel): The model
        output_dir (Path): Base output directory
        is_ancestor (bool): Flag to trigger generation for ancestor
        generate_for_application_module (bool, optional): Generate for application module
        verbose_mode (bool, optional): Flag to enable verbose_mode mode
    Returns:
        List of paths for user-editable files
    """
    # collect list of merge relevant files
    list_merge_relevant_files: List[str] = []

    generator = Generator()

    does_data_type_definition_exist: bool = bool(
        model.DataTypeDefinitions.Arrays
        or model.DataTypeDefinitions.Enums
        or model.DataTypeDefinitions.Maps
        or model.DataTypeDefinitions.Strings
        or model.DataTypeDefinitions.Structs
        or model.DataTypeDefinitions.TypeRefs
    )

    list_merge_relevant_files += _generate_src_and_src_gen_cmake(
        generator,
        model,
        output_dir,
        is_ancestor,
        generate_for_application_module,
        verbose_mode=verbose_mode,
    )
    if not is_ancestor:
        _generate_src_gen_libs_cmake(
            generator,
            model,
            output_dir,
            does_data_type_definition_exist,
            generate_for_application_module,
            verbose_mode=verbose_mode,
        )
    list_merge_relevant_files += _generate_src_executables_cmake(
        generator, model, output_dir, is_ancestor, verbose_mode=verbose_mode
    )
    if not is_ancestor:
        _generate_executables_cmake(generator, model, output_dir, verbose_mode=verbose_mode)
        _generate_test_cmake(generator, model, output_dir, verbose_mode=verbose_mode)
        _generate_test_mocks_cmake(generator, model, output_dir, verbose_mode=verbose_mode)

    if does_data_type_definition_exist and not is_ancestor:
        _generate_data_types_cmake(generator, output_dir, verbose_mode=verbose_mode)

    return list_merge_relevant_files
