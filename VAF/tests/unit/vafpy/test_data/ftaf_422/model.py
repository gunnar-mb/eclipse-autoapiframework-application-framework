#!/usr/bin/env python3
import os

from vaf import (save_part_of_main_model)

# Import the application module model
import app_module1


def export_model():
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_part_of_main_model(
        os.path.join(script_path, "model.json"),
        ["DataTypeDefinitions", "ModuleInterfaces", "ApplicationModules"],
        cleanup=True,
    )


if __name__ == "__main__":
    export_model()
