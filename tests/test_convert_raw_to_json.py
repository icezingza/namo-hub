import unittest
import os
import subprocess
import sys

class TestConvertRawToJson(unittest.TestCase):

    def setUp(self):
        # Determine the project root by going up one level from the 'tests' directory
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.workflows_dir = os.path.join(self.project_root, 'Workflows')
        self.test_file_path = os.path.join(self.workflows_dir, 'test_blueprint.txt')
        self.script_path = os.path.join(self.project_root, 'scripts', 'convert_raw_to_json.py')

        # Create a dummy Workflows directory and a test file
        if not os.path.exists(self.workflows_dir):
            os.makedirs(self.workflows_dir)
        with open(self.test_file_path, 'w') as f:
            f.write('test content')

    def tearDown(self):
        # Clean up the dummy directory and files
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        # Only remove directory if it's empty
        if os.path.exists(self.workflows_dir) and not os.listdir(self.workflows_dir):
             # Check for other files to avoid deleting user files if they exist
            other_files = [f for f in os.listdir(self.workflows_dir) if f not in ['test_blueprint.txt', 'import.json']]
            if not other_files:
                os.rmdir(self.workflows_dir)
        output_file = os.path.join(self.workflows_dir, 'import.json')
        if os.path.exists(output_file):
            os.remove(output_file)

    def test_script_succeeds_when_run_from_subdirectory(self):
        # After the fix, the script should run successfully from any directory.
        # We run it from the 'tests' directory to confirm this.
        process = subprocess.Popen(
            [sys.executable, self.script_path],
            cwd=os.path.dirname(__file__),  # Run from the 'tests' directory
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        # Check for successful execution output
        self.assertIn("Success! Converted 1 files.", stdout)
        self.assertNotIn("Error:", stdout)
        self.assertEqual(stderr, "")

        # Verify that the output file was created
        output_file_path = os.path.join(self.workflows_dir, 'import.json')
        self.assertTrue(os.path.exists(output_file_path))

if __name__ == '__main__':
    unittest.main()
