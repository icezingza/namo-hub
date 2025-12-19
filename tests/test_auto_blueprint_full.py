import unittest
import json
import sys
from pathlib import Path

# Add the 'tools' directory to the Python path to allow direct import of modules within it
tools_dir = Path(__file__).resolve().parent.parent / 'tools'
sys.path.insert(0, str(tools_dir))

from auto_blueprint_full import build_blueprint, build_source_info

class TestAutoBlueprintFull(unittest.TestCase):

    def test_source_file_path_format(self):
        # Create a dummy file path
        dummy_file = Path("framework/test_document.txt")

        # Dummy content for the file
        raw_text = "This is a test document."

        source_info = build_source_info(dummy_file, raw_text, False)
        blueprint = build_blueprint(dummy_file, raw_text, source_info, run_id="", pii_redacted=False)

        # Get the source file path from the blueprint
        source_file_path = blueprint.get("metadata", {}).get("source_file")

        # Check if the path is in the correct posix format
        self.assertEqual(source_file_path, "framework/test_document.txt")

if __name__ == '__main__':
    unittest.main()
