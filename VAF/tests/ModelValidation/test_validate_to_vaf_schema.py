import json
import sys
import unittest
from pathlib import Path

import pydantic

sys.path.append("../MetaModel")
import vaf.vafmodel as vafmodel


class TestValidateConfigToSchema(unittest.TestCase):
    REPO_ROOT = Path(__file__).parent / "../../.."

    def test_platform_first_demo_config(self) -> None:
        """
        Test: Checks all VAF Configuration files if they are according to the
              schema.
                - Search all model.json files.
                - If the model file contains a $schema key which point to the
                  VAF schema that file is selected for the check.
        """
        # glob all json files which might be a candidate for schema checking
        model_candidates = Path(self.REPO_ROOT).rglob("model.json")

        # Remove all json files in the Concepts folder
        filtered_candidates = [f for f in model_candidates if "Concepts" not in f.parts]
        for f in filtered_candidates:
            print(f)

        # Search for the "$schema": key in each found json file
        for file in filtered_candidates:
            plt_model = None
            with open(file) as fh:
                plt_model = json.load(fh)

            # file contains "$schema" key and ...
            if "$schema" in plt_model:
                # ... point to VAF schema
                if plt_model["$schema"] is not None and Path(plt_model["$schema"]).name == "vaf_schema.json":
                    print(f"Checking {str(file)}")

                    try:
                        vafmodel.load_json(file)
                    except pydantic.ValidationError:
                        self.fail("Configuration is not according to VAF schema")
                else:
                    print(f"Skipping {str(file)}, as it doesn't contain a valid value for $schema")


if __name__ == "__main__":
    unittest.main()
