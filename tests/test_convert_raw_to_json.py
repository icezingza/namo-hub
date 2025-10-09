import os
import sys
import json
import unittest
import subprocess
from pathlib import Path

# Add the scripts directory to the Python path to allow importing the script
# This is a common pattern for testing standalone scripts
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

# Now we can import the script we want to test
import convert_raw_to_json

class TestConvertRawToJson(unittest.TestCase):

    def setUp(self):
        """Set up a controlled environment for each test."""
        self.workflows_dir = REPO_ROOT / 'Workflows'
        self.output_file = self.workflows_dir / 'import.json'
        self.test_file1 = self.workflows_dir / 'test_blueprint_1.txt'
        self.test_file2 = self.workflows_dir / 'test_blueprint_2.md'
        self.ignored_file = self.workflows_dir / 'GUIDE.md'

        # Ensure the directory exists
        self.workflows_dir.mkdir(exist_ok=True)

        # Create dummy raw files for the test
        self.test_file1.write_text("This is test file 1.", encoding='utf-8')
        self.test_file2.write_text("This is test file 2.", encoding='utf-8')
        self.ignored_file.write_text("This is an ignored file.", encoding='utf-8')

        # Make sure the output file doesn't exist before the test
        if self.output_file.exists():
            self.output_file.unlink()

    def tearDown(self):
        """Clean up the environment after each test."""
        # Remove the dummy files and the generated output file
        if self.test_file1.exists():
            self.test_file1.unlink()
        if self.test_file2.exists():
            self.test_file2.unlink()
        if self.ignored_file.exists():
            self.ignored_file.unlink()
        if self.output_file.exists():
            self.output_file.unlink()

    def test_script_runs_from_different_directory(self):
        """
        Verify that the script runs correctly even when the current working
        directory is not the repository root. This is the core of the bug fix.
        """
        # Create a temporary directory to simulate a different CWD
        temp_dir = REPO_ROOT / 'temp_test_dir'
        temp_dir.mkdir(exist_ok=True)

        # Define the full path to the script to be executed
        script_path = SCRIPTS_DIR / 'convert_raw_to_json.py'

        # Execute the script with the temporary directory as the CWD
        try:
            # We run it as a subprocess to ensure it's a clean execution environment
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                check=True  # This will raise an exception if the script returns a non-zero exit code
            )
            print(result.stdout)
            print(result.stderr)
        finally:
            # Clean up the temporary directory
            temp_dir.rmdir()

        # --- Assertions ---
        # 1. Check that the output file was created in the correct location
        self.assertTrue(self.output_file.exists(),
                        f"The output file '{self.output_file}' was not created.")

        # 2. Check the contents of the generated JSON file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # It should have processed the two valid test files
        self.assertEqual(len(data), 2, "The JSON should contain two blueprint entries.")

        # Check titles (derived from filenames)
        titles = sorted([item['title'] for item in data])
        expected_titles = sorted(['Test Blueprint 1', 'Test Blueprint 2'])
        self.assertEqual(titles, expected_titles, "The blueprint titles are incorrect.")

        # Check that the content was correctly read
        content = {item['title']: item['content'] for item in data}
        self.assertEqual(content['Test Blueprint 1'], "This is test file 1.")
        self.assertEqual(content['Test Blueprint 2'], "This is test file 2.")

        # 3. Check that the ignored file was not processed
        for item in data:
            self.assertNotEqual(item['title'], 'GUIDE', "The ignored file 'GUIDE.md' should not be processed.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)