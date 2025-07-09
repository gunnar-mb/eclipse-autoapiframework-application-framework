"""Generator library for generating the complete VAF project"""

import shutil
import subprocess
from pathlib import Path
from typing import List

from vaf import vafmodel

# Utils
from vaf.cli_core.common.utils import (
    concat_str_to_path,
)

# suffix for ancestor of model.json
from vaf.vafpy.runtime import old_json_suffix

# suffix for old source file
suffix_old_source = "~"
ancestor_file_suffix = "~ancestor"
new_file_suffix = ".new~"


def __file_has_conflict(file_path: Path) -> bool:
    """Function to check if file contains conflicts
    Args:
        file_path: Path to the file
    Return:
        boolean if file contains conflicts
    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    return all(conflict_sign in file_content for conflict_sign in ["<<<<<<<", "=======", ">>>>>>>"])


def __get_ancestor_file_rel_path(real_file_rel_path: str | Path) -> str | Path:
    """Function to get rel path of the ancestor of a user file as str
    Args:
        real_file_rel_path: rel path of the real file
    Returns:
        respective rel path of the ancestor
    """
    return (
        concat_str_to_path(real_file_rel_path, ancestor_file_suffix)
        if isinstance(real_file_rel_path, Path)
        else real_file_rel_path + ancestor_file_suffix
    )


def __get_newly_generated_file_path(real_file_rel_path: str | Path) -> str | Path:
    """Function to get rel path of the newly generated file (.new~)
    Args:
        real_file_rel_path: rel path of the real file
    Returns:
        respective rel path of the newly generated file
    """
    return (
        concat_str_to_path(real_file_rel_path, new_file_suffix)
        if isinstance(real_file_rel_path, Path)
        else real_file_rel_path + new_file_suffix
    )


def __get_backup_file_path(real_file_rel_path: str | Path) -> str | Path:
    """Function to get rel path of the backup file (~)
    Args:
        real_file_rel_path: rel path of the real file
    Returns:
        respective rel path of the backup file
    """
    return (
        concat_str_to_path(real_file_rel_path, suffix_old_source)
        if isinstance(real_file_rel_path, Path)
        else real_file_rel_path + suffix_old_source
    )


def __merge_files(
    newly_generated_file: Path,
    patched_file_path: Path,
    common_ancestor_file_path: Path,
    verbose_mode: bool = False,
) -> None:
    """Function to perform three-way files merge through subprocess
    Documentation for git merge-file: https://git-scm.com/docs/git-merge-file
    Args:
        newly_generated_file: path to the newly generated file (ends w/ .new~)
        patched_file_path: path to the patched file (older generated file + patch)
        common_ancestor_file_path: path to the common ancestor of current & patched (older generated file)
        verbose_mode (bool): Flag to enable verbose mode
    """
    # build cmd to perform git merge-file:
    # merge newly generated file to current file (patched_file)
    args = [
        "git",
        "merge-file",
        "-p",  # -p to send results to stdout
        str(patched_file_path),
        str(common_ancestor_file_path),
        str(newly_generated_file),
    ]
    # run the cmd
    merge = subprocess.run(args, capture_output=True, text=True, check=False)

    old_file_path = concat_str_to_path(patched_file_path, suffix_old_source)

    # check if merge results has conflicts
    msg_list = []
    if merge.returncode == 0:
        msg_list += (
            [
                "\nMERGE INFO",
                f"    Merge of {newly_generated_file} with {patched_file_path} successfully without conflicts!",
                f"    Merge result is saved in {patched_file_path}.",
            ]
            if verbose_mode
            else []
        )
    elif merge.returncode == 1:
        msg_list += [
            "\nMERGE WARNING:",
            f"    Merge of {newly_generated_file} with {patched_file_path} has conflicts!",
            f"    Merge result is saved in {patched_file_path}. Please resolve the conflicts before moving on.",
        ]

    msg_list += (
        [
            f"    Original state of {patched_file_path} before merge is saved as backup in {old_file_path}\n",
        ]
        if msg_list
        else []
    )

    if merge.returncode in (0, 1):
        print("\n".join(msg_list))
        # save merge results
        with open(patched_file_path, "w", encoding="utf-8") as out_file:
            out_file.write(merge.stdout)
    else:
        # Inform user if merge fails: Don't abort the whole workflow!
        print(f"Auto file mechanism for file {patched_file_path} failed! Reason: {merge.stderr}")


def merge_after_regeneration(out_dir: Path, list_of_user_files_rel_path: List[str], verbose_mode: bool = False) -> None:
    """Function to perform three-way files merge after regeneration of app_module
    Args:
        out_dir: Path to the output directory
        list_of_user_files_rel_path: List of relative path from out_dir to user files (files that users can edit)
        verbose_mode (bool): Flag to enable verbose mode
    """
    for rel_path_to_file in list_of_user_files_rel_path:
        newly_generated_file_path = out_dir / __get_newly_generated_file_path(rel_path_to_file)
        ancestor_file_path = out_dir / __get_ancestor_file_rel_path(rel_path_to_file)
        # merge needed if there is a copy of .new~ file is created
        # merge can only be performed if ancestor exists
        if newly_generated_file_path.is_file():
            if ancestor_file_path.is_file():
                # backup current file
                current_file = out_dir / rel_path_to_file
                backup_file = __get_backup_file_path(current_file)
                # if current file has conflict, then check if backup is valid to be used
                if __file_has_conflict(current_file):
                    print(
                        "\n".join(
                            [
                                "WARNING:",
                                f"  The file {current_file} contains unresolved merge conflicts and will be ignored!",
                                f"  Using the backup file {backup_file} for the merge instead.",
                            ]
                        )
                    )
                    assert isinstance(backup_file, Path)  # Are you satisfied now, mypy?
                    if backup_file.is_file() and not __file_has_conflict(backup_file):
                        shutil.copyfile(backup_file, current_file)
                else:
                    # current file has no conflict, overwrite backup
                    shutil.copyfile(out_dir / rel_path_to_file, __get_backup_file_path(out_dir / rel_path_to_file))

                # perform three way merge
                __merge_files(
                    newly_generated_file=newly_generated_file_path,
                    patched_file_path=out_dir / rel_path_to_file,
                    common_ancestor_file_path=ancestor_file_path,
                    verbose_mode=verbose_mode,
                )
            else:
                # warning only if newly generated file exists,
                msg_list = [
                    "WARNING:",
                    f"  Cannot merge {newly_generated_file_path} to {out_dir / rel_path_to_file} automatically!",
                    "  Can't find old model.json~",
                    (
                        "  Please merge both files manually. The auto merge will be available "
                        + "the next time the model is updated."
                    ),
                ]
                print("\n".join(msg_list))

            # remove newly generated file only if merge took place
            # else no old model.json~ -> new file is identical with current, remove it
            newly_generated_file_path.unlink()

        # remove ancestor file regardless of the merge
        if ancestor_file_path.is_file():
            ancestor_file_path.unlink()


def get_ancestor_file_suffix(is_ancestor: bool) -> str:
    """Method to get file's suffix for ancestor
    Args:
        is_ancestor: boolean for ancestor
    Returns:
        file suffix if it's ancestor
    """
    return ancestor_file_suffix if is_ancestor else ""


def get_ancestor_model(input_file: str) -> vafmodel.MainModel | None:
    """Function to get old model
    Args:
        input_file: Path to current model file
    Returns:
        Old vafmodel, if old model.json file exists
    """
    # check for "ancestor" model.json (model.json~)
    ancestor_json = concat_str_to_path(Path(input_file), old_json_suffix)
    return vafmodel.load_json(ancestor_json) if ancestor_json.is_file() else None
