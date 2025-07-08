# Software libraries

## VAF core library

The VAF core library (C++) covers static code artifacts on executable-level.
It includes implementations for: 
- Data pointer handling
- Asynchronous operation support via future/promise
- Executor
- Logging
- Error handling
- and more...

More details are provided in the following subsection of the project documentation: [SW library](../Documentation/contents/28_sw_library.md)

### Conan Package

First check if an update of the version number is required. If so, update the version number of the
package within the `conanfile.py`

To create a Conan package from the library, execute the following command:

    conan create . --profile:host=test_package/gcc12__x86_64-pc-linux-elf --profile:build=test_package/gcc12__x86_64-pc-linux-elf -s build_type=Debug
    conan create . --profile:host=test_package/gcc12__x86_64-pc-linux-elf --profile:build=test_package/gcc12__x86_64-pc-linux-elf -s build_type=Release

It something incompatible changes regarding the build, i.e., some errors occur while creating the
package, execute the following commands in the given order to narrow down where the package
creation fails:

    conan install . --profile:host=test_package/gcc12__x86_64-pc-linux-elf --profile:build=test_package/gcc12__x86_64-pc-linux-elf -s build_type=Debug

    conan build . --profile:host=test_package/gcc12__x86_64-pc-linux-elf --profile:build=test_package/gcc12__x86_64-pc-linux-elf -s build_type=Debug

    conan export-pkg . --profile:host=test_package/gcc12__x86_64-pc-linux-elf --profile:build=test_package/gcc12__x86_64-pc-linux-elf -s build_type=Debug

Choose the right package version for the next command, here version 0.1.0 is used:

    conan  test test_package vafcpp/0.1.0  --profile:host=gcc12__x86_64-pc-linux-elf --profile:build=gcc12__x86_64-pc-linux-elf -s build_type=Debug
