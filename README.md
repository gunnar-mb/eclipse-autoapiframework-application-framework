# Welcome to the Git repository of the [Eclipse Automotive API Framework](https://projects.eclipse.org/projects/automotive.autoapiframework)

This space is where the implementation of our Vehicle Application Framework (VAF) is versioned and
maintained.

## Repository contents

- 📂 [.devcontainer](./.devcontainer)  
  VS Code development container configuration file for contributors of this project.
- 📂 [.vscode](./.vscode)  
  Tasks, scripts, and settings for easier development in VS Code.
- 📂 [Container](./Container)  
  Dockerfile recipe for the container image that is supposed to be provided to users of the
  framework.
- 📂 [Demo](./Demo)  
  Several demo projects with sample files that demonstrate the usage of the VAF.
- 📂 [Documentation](./Documentation)  
  The VAF technical documentation.
- 📂 [SwLibraries](./SwLibraries)  
  Libraries in C++ (the current main target programming language of this project).
- 📂 [Tools](./Tools)  
  Project-related tools.
- 📂 [VAF](./VAF)  
  The actual implementation of the framework. Includes model, Configuration as Code, importers, CLI
  tooling, and code generators.

## Getting started

Please check, which role applies to you and follow the provided instructions to get started...

### Application Framework user

1. Make sure Docker is installed on your machine. Otherwise, please follow the instructions in:
   [Install Docker using the apt
   repository.](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
2. Optional step if you are working in a corporate environment with a SSL proxy server. Modify 
   the [eclipse.Dockerfile](./Container/eclipse.Dockerfile) in lines 35 ff. and insert your SSL 
   proxy settings.
3. Start the `build.sh` script in the [Container](./Container) folder to create the image.
4. Check out the different example projects that are provided in [Demo](./Demo). Each demo comes
   with a detailed step-by-step tutorial.
5. Start own projects based on the VAF.

In case of feedback do not hesitate to get back to us. Or, even better, become a contributor
yourself and join us on the development of the Vehicle Application Framework!

### Project contributor

To make development easier, a devcontainer is also provided for project contributors. It contains
all the necessary dependencies and development tools to contribute to this project. It includes also
all runtime dependencies to use VAF itself in this container. The dockerfile and the corresponding
devcontainer configuration are located in the [.devcontainer](./.devcontainer) directory.

At the bottom of the configuration file are some commented templates to mount your ssh config and
root CA certificates from your host into the container. The latter might be necessary if you are
working in a corporate environment with a SSL proxy server. The
[Dockerfile](./.devcontainer/Dockerfile) itself must also be adapted if an SSL proxy server is
available. To do this, adapt lines 42 ff. according to your requirements.

The project uses `Conan` to manage C++ dependencies. Since there are no prebuilt packages available
in the public Conan center for the used compiler settings, the packages are built as the last step
of the dockerfile. This avoids a long wait when (re-)creating a new container.

>**ℹ️ Note**  
>On first start of the devcontainer it will take a few minutes, depending on your machine, to
>build all the Conan dependencies.

#### Building vaf-cli

The VAF CLI program uses `pdm` as build tool. To install VAF in your container, go to the `./VAF`
directory and run:

``` bash
pdm install
```

This will install the Python packages as symlinks to the repository so you don't have to re-install
them every time you make a change. This step creates a virtual environment that should be selected
as the Python environment in VS Code to enable IntelliSense. When working in a terminal window, the
virtual environment must be activated. To do this, execute the following command in the `./VAF`
directory:

``` bash
source .venv/bin/activate
```

The VAF supports bash completion. To enable it, activate the virtual environment as described
above. Then execute the following commands:

``` bash
mkdir -p ~/.local/share/bash-completion/completions
_VAF_COMPLETE=bash_source vaf > ~/.local/share/bash-completion/completions/vaf.sh
source ~/.local/share/bash-completion/completions/vaf.sh
```

#### Building vafcpp

The C++ library `vafcpp` uses `Conan` as its build tool. To build an updated package, you can use
the included Rakefile. Run `rake prod:install:vafcpp` in the project root directory. By default, the
version number stored in the [version.txt](version.txt) file is used for the Conan package. This can
be overridden with the following syntax: `rake prod:install:vafcpp[0.6.0]`.

Note that each VAF project lists its dependencies in the `conanfile.py`, which also includes a
reference to a specific version of this package. If you want to test changes with a different
version number, you need to update it accordingly. To update the version number in the template for
new projects, use the rake task `rake prod:patch:project_vafcpp_version[version]` in the project
root directory.

>**ℹ️ Hint**  
>To list all available rake tasks, run `rake --tasks` in the project root directory.

## Related projects

This project makes use of the following open-source projects:

- [expected by TartanLlama](https://github.com/TartanLlama/expected) available under [CC0 1.0
  Universal License](https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt)
- [Vector SIL Kit](https://github.com/vectorgrp/sil-kit) available under [MIT
  License](https://mit-license.org/)

Other dependencies via Conan include:

- [protobuf v5.27.0](https://github.com/protocolbuffers/protobuf/tree/v5.27.0)
- [gtest v1.13.0](https://github.com/google/googletest/tree/v1.13.0)
