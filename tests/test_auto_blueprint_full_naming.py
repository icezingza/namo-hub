import json
import tempfile
import unittest
from pathlib import Path
import sys

tools_dir = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

from auto_blueprint_full import build_output_path

class TestAutoBlueprintFullNaming(unittest.TestCase):
    def test_collision_uses_hash_suffix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            safe_stem = "example"
            existing_path = output_dir / "example.json"
            existing_path.write_text(json.dumps({
                "metadata": {"source_hash": "abc123"}
            }), encoding="utf-8")

            new_path = build_output_path(output_dir, safe_stem, "def4567890")
            self.assertIn("example_def45678", new_path.name)

    def test_same_hash_reuses_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            safe_stem = "example"
            existing_path = output_dir / "example.json"
            existing_path.write_text(json.dumps({
                "metadata": {"source_hash": "abc123"}
            }), encoding="utf-8")

            new_path = build_output_path(output_dir, safe_stem, "abc123")
            self.assertEqual(existing_path, new_path)

if __name__ == "__main__":
    unittest.main()
