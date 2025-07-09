"""Execute to generate the complete model."""

import os

from vaf import save_part_of_main_model

# import the application module model to build up its model
import app_module1

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_part_of_main_model(os.path.join(script_path, "model.json"),["DataTypeDefinitions", "ModuleInterfaces", "ApplicationModules"], cleanup = True)
