import json
import unittest
from pathlib import Path

import vaf.vafmodel as vafmodel


class TestSchemReleaseVersion(unittest.TestCase):
    SCHEMA_INFO = ".schema-infos.json"

    def test_schema_version_consistency(self) -> None:
        """
        Test: Verify that the version referenced in `.schema-infos.json`
        matches with the version in the model
        """
        mmodel = vafmodel.vafmodel.MainModel()
        version = mmodel.model_config.get("json_schema_extra")["version"]  # type: ignore
        # remove the trailing 'v'
        version = str(version).replace("v", "")

        schema_info_file = Path(__file__).parent / self.SCHEMA_INFO
        assert schema_info_file.is_file()

        with open(str(schema_info_file)) as fh:
            schema_info = json.load(fh)

        assert version == schema_info["schemaInfos"][0]["currentVersion"]


if __name__ == "__main__":
    unittest.main()
