import importlib.util
import json
import shutil
import tempfile
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from unittest import mock


class TestConvertRawToJsonGolden(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_file = self.temp_dir / "golden_input.txt"
        self.input_file.write_text("Golden content.", encoding="utf-8")
        self.script_path = Path(__file__).resolve().parent.parent / "scripts" / "convert_raw_to_json.py"
        self.expected_path = Path(__file__).resolve().parent / "golden" / "convert_raw_to_json_expected.json"

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def load_module(self):
        spec = importlib.util.spec_from_file_location("convert_raw_to_json", self.script_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load convert_raw_to_json module.")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_golden_output(self):
        module = self.load_module()
        fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        fixed_time = datetime(2025, 1, 2, 3, 4, 5)

        class FixedDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_time

        with mock.patch.object(module.uuid, "uuid4", return_value=fixed_uuid), \
            mock.patch.object(module, "datetime", FixedDatetime):
            blueprint = module.create_blueprint_from_file(str(self.input_file))

        expected = json.loads(self.expected_path.read_text(encoding="utf-8"))
        self.assertEqual(blueprint, expected)


if __name__ == "__main__":
    unittest.main()
