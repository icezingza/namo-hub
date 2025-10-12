import unittest
import os
import json
import tempfile
import shutil
import subprocess
from pathlib import Path

class TestValidateBlueprints(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.blueprints_dir = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def run_script(self, blueprints_path):
        script_path = Path(__file__).resolve().parent.parent / "tools" / "validate_blueprints.py"
        # The script is designed to be run from the repo root, so we change the CWD
        # to ensure it can find its dependencies if needed.
        repo_root = Path(__file__).resolve().parent.parent

        result = subprocess.run(
            ["python", str(script_path), str(blueprints_path)],
            capture_output=True,
            text=True,
            cwd=repo_root
        )
        return result

    def test_valid_blueprint(self):
        blueprint_content = {
            "sections": {
                "executive_summary": "summary",
                "value_proposition": "value",
                "system_overview": "overview",
                "quick_start_guide": "guide",
                "template_instructions": "instructions",
                "examples": "examples",
                "license_and_notes": "license",
                "marketing_pack": "pack"
            }
        }
        with open(self.blueprints_dir / "valid.json", "w") as f:
            json.dump(blueprint_content, f)

        result = self.run_script(self.blueprints_dir)

        self.assertIn("✅ valid.json complete", result.stdout)
        self.assertIn("Summary", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_missing_sections(self):
        blueprint_content = {
            "sections": {
                "executive_summary": "summary"
            }
        }
        with open(self.blueprints_dir / "missing.json", "w") as f:
            json.dump(blueprint_content, f)

        result = self.run_script(self.blueprints_dir)

        self.assertIn("⚠️ missing.json missing sections", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_invalid_json(self):
        with open(self.blueprints_dir / "invalid.json", "w") as f:
            f.write("{ not json }")

        result = self.run_script(self.blueprints_dir)

        self.assertIn("❌ invalid.json is not valid JSON.", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_non_existent_directory(self):
        non_existent_dir = self.blueprints_dir / "non_existent"
        result = self.run_script(non_existent_dir)
        self.assertIn(f"Directory '{non_existent_dir}' not found. Skipping validation.", result.stdout)
        self.assertEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()
