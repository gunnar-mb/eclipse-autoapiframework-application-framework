"""
This module contains the implementation of the make commands

"""

import os
import subprocess
import sys
from pathlib import Path


class MakeCmd:
    """Class implementing the make related commands"""

    def __init__(self, verbose_mode: bool = False) -> None:
        """
        Ctor for CmdProject class
        Args:
            verbose_mode (bool): Flag to enable verbose mode
        """
        self.verbose_mode = verbose_mode

    def preset(self, build_dir: str, compiler: str, build_type: str, defines: str, cwd: str) -> None:  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """
        Preset.

        Args:
            build_dir: Build directory
            compiler: Compiler version
            build_type: Debug or release build
            defines: Additional defines
            cwd: Current working directory

        """
        opt_build_dir = "tools.cmake.cmake_layout:build_folder=" + build_dir
        opt_compiler = "-pr:a=" + cwd + "/.conan/" + compiler
        opt_type = "build_type=" + build_type
        subprocess.run(
            ["conan", "install", cwd, opt_compiler, "-s", opt_type, "-c", opt_build_dir, "--build=missing"],
            check=False,
            stderr=None if self.verbose_mode else subprocess.DEVNULL,
            stdout=None if self.verbose_mode else subprocess.DEVNULL,
        )
        current_dir = Path.cwd()
        os.chdir(cwd)  # cmake --preset must run in project root directory
        if build_type == "Release":
            subprocess.run(
                ["cmake", "--preset", "conan-release", defines],
                check=False,
                stderr=None if self.verbose_mode else subprocess.DEVNULL,
                stdout=None if self.verbose_mode else subprocess.DEVNULL,
            )
        else:
            subprocess.run(
                ["cmake", "--preset", "conan-debug", defines],
                check=False,
                stderr=None if self.verbose_mode else subprocess.DEVNULL,
                stdout=None if self.verbose_mode else subprocess.DEVNULL,
            )
        os.chdir(current_dir)

    def build(self, preset: str) -> None:
        """
        Build.

        Args:
            preset: CMake preset

        """
        cpu_count = os.cpu_count() or 1
        subprocess.run(
            ["cmake", "--build", "--preset", preset, "--parallel", str(cpu_count)],
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )

    def clean(self, preset: str) -> None:
        """
        Clean.

        Args:
            preset: CMake preset

        """
        subprocess.run(
            ["cmake", "--build", "--target", "clean", "--preset", preset],
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )

    def install(self, preset: str) -> None:
        """
        Install.

        Args:
            preset: CMake preset

        """
        cpu_count = os.cpu_count() or 1
        subprocess.run(
            ["cmake", "--build", "--target", "install", "--preset", preset, "--parallel", str(cpu_count)],
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
