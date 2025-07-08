import os
from datetime import timedelta
from pathlib import Path

from vaf.cli_core.common.utils import ProjectType

os.environ["IMPORT_APPLICATION_MODULES"] = "import"

from .application_modules import *
from vaf import *

# TODO: Create executable instances (or configure existing ones from the platform configuration)
executable = Executable("Pulp-A-Tine", timedelta(milliseconds=10))

# TODO: Add application modules to executable instances
executable.add_application_module(Fake, [(Instances.Fake.Tasks.SweetHomeAlabama, timedelta(milliseconds=1), 0)])
executable.add_application_module(Mockery, [(Instances.Mockery.Tasks.California, timedelta(milliseconds=1), 1)])

# TODO: Wire the internal application module instances
executable.connect_interfaces(Fake, Instances.Fake.ProvidedInterfaces.KentuckyFriedChicken,
                              Mockery, Instances.Mockery.ConsumedInterfaces.McDonalds)
def export_model():
    script_path = Path(__file__).resolve().parent
    save_main_model(script_path / "model.json", project_type=ProjectType.INTEGRATION)


if __name__ == "__main__":
    export_model()
