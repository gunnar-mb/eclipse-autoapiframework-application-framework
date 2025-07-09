import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import load, update_conandata, copy

from pathlib import Path


class VafcppRecipe(ConanFile):
    name = "vafcpp"

    # Optional metadata
    license = "Vector Informatik GmbH"
    author = "christian.marchl@vector.com"
    url = "https://gitlab.vi.vector.int/pes/teamprojects/pes-ft-applicationframework"
    description = "Vehicle Application Framework"
    topics = ("API", "Application Development", "Application Framework", "SDV")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def export(self):
        update_conandata(self, {"src_path": Path(__file__).resolve().parent.as_posix()})

    def source(self):
        files_to_copy = ["CMakeLists.txt", "lib/*", "include/*", "test/*", "cmake/*"]
        for file in files_to_copy:
            copy(self, file, self.conan_data["src_path"], self.source_folder)

    def set_version(self):
        self.version = self.version or load(self, "../../version.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            # del self.options.fPIC
            raise ConanException("Windows OS is currently not supported")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # self.cpp_info.libs = ["vafcpp"]

        # Integrate cmake files packaged with the software stack
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "vafcpp"))
