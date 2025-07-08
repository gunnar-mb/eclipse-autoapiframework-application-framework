"""
Tests for controller generator
"""

import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.vafgeneration import vaf_controller

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=line-too-long
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"


class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for controller generation"""

        m = vafmodel.MainModel()
        m.ModuleInterfaces.append(vafmodel.ModuleInterface(Name="MyInterface", Namespace="test"))
        m.ApplicationModules.append(
            vafmodel.ApplicationModule(
                Name="MyApp",
                Namespace="test",
                ConsumedInterfaces=[
                    vafmodel.ApplicationModuleConsumedInterface(
                        InstanceName="instance3", ModuleInterfaceRef=m.ModuleInterfaces[0]
                    ),
                    vafmodel.ApplicationModuleConsumedInterface(
                        InstanceName="instance4", ModuleInterfaceRef=m.ModuleInterfaces[0], IsOptional=True
                    ),
                ],
                ProvidedInterfaces=[
                    vafmodel.ApplicationModuleProvidedInterface(
                        InstanceName="instance1", ModuleInterfaceRef=m.ModuleInterfaces[0]
                    ),
                    vafmodel.ApplicationModuleProvidedInterface(
                        InstanceName="instance2", ModuleInterfaceRef=m.ModuleInterfaces[0]
                    ),
                ],
                Tasks=[
                    vafmodel.ApplicationModuleTasks(Name="R1", Period="10ms"),
                    vafmodel.ApplicationModuleTasks(Name="R2", Period="20ms", PreferredOffset=1),
                ],
            )
        )

        vaf_module = vafmodel.PlatformModule(
            Name="MyModule1",
            Namespace="test",
            ModuleInterfaceRef=m.ModuleInterfaces[0],
        )

        vaf_module2 = vafmodel.PlatformModule(
            Name="MyModule4",
            Namespace="test",
            ModuleInterfaceRef=m.ModuleInterfaces[0],
        )

        m.PlatformProviderModules.append(
            vafmodel.PlatformModule(
                Name="MyModule2",
                Namespace="test",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=vafmodel.SILKITConnectionPoint(
                    Name="MyConnectionPoint1", ServiceInterfaceName="MyInterface", RegistryUri="silkit://localhost:8500"
                ),
            )
        )
        m.PlatformConsumerModules.append(
            vafmodel.PlatformModule(
                Name="MyModule3",
                Namespace="test",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=vafmodel.SILKITConnectionPoint(
                    Name="MyConnectionPoint1", ServiceInterfaceName="MyInterface", RegistryUri="silkit://localhost:8500"
                ),
            )
        )

        mapping = vafmodel.ExecutableApplicationModuleMapping(
            ApplicationModuleRef=m.ApplicationModules[0],
            InterfaceInstanceToModuleMappings=[
                vafmodel.InterfaceInstanceToModuleMapping(InstanceName="instance1", ModuleRef=vaf_module),
                vafmodel.InterfaceInstanceToModuleMapping(
                    InstanceName="instance2", ModuleRef=m.PlatformProviderModules[0]
                ),
                vafmodel.InterfaceInstanceToModuleMapping(
                    InstanceName="instance3", ModuleRef=m.PlatformConsumerModules[0]
                ),
                vafmodel.InterfaceInstanceToModuleMapping(InstanceName="instance4", ModuleRef=vaf_module2),
            ],
            TaskMapping=[
                vafmodel.ExecutableTaskMapping(TaskName="R1", Offset=0, Budget="10ms"),
                vafmodel.ExecutableTaskMapping(TaskName="R2"),
            ],
        )

        m.Executables.append(
            vafmodel.Executable(
                Name="MyExecutable",
                ExecutorPeriod="10ms",
                ApplicationModules=[mapping],
                InternalCommunicationModules=[vaf_module],
            )
        )

        vaf_controller.generate(m, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        assert filecmp.cmp(
            tmp_path / "src-gen/executables/my_executable/include/executable_controller/executable_controller.h",
            script_dir / "controller/controller.h",
        )

        assert filecmp.cmp(
            tmp_path / "src-gen/executables/my_executable/src/executable_controller/executable_controller.cpp",
            script_dir / "controller/controller.cpp",
        )

        assert filecmp.cmp(
            tmp_path / "src/executables/my_executable/include/user_controller.h",
            script_dir / "controller/user_controller.h",
        )

        assert filecmp.cmp(
            tmp_path / "src/executables/my_executable/src/user_controller.cpp",
            script_dir / "controller/user_controller.cpp",
        )

        assert filecmp.cmp(
            tmp_path / "src-gen/executables/my_executable/src/main.cpp",
            script_dir / "controller/main.cpp",
        )

        assert filecmp.cmp(
            tmp_path / "src-gen/executables/my_executable/CMakeLists.txt",
            script_dir / "controller/CMakeLists.txt",
        )
