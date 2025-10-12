import unittest
from pathlib import Path
import sys

# Add the tools directory to the Python path to allow importing sanitize
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from sanitize import sanitize_text, GENERIC_PERSON, GENERIC_ORG

class TestSanitize(unittest.TestCase):
    def test_name_replacement(self):
        self.assertEqual(sanitize_text("Hello Namo"), f"Hello {GENERIC_PERSON}")
        self.assertEqual(sanitize_text("พี่ไอซ์ is here"), f"{GENERIC_PERSON} is here")
        self.assertEqual(sanitize_text("Thanks, Ice!"), f"Thanks, {GENERIC_PERSON}!")

    def test_org_replacement(self):
        self.assertEqual(sanitize_text("Welcome to NaMo-Hub"), f"Welcome to {GENERIC_ORG}")
        self.assertEqual(sanitize_text("This is NamoVerse"), f"This is {GENERIC_ORG}")

    def test_case_insensitivity(self):
        self.assertEqual(sanitize_text("hello namo"), f"hello {GENERIC_PERSON}")
        self.assertEqual(sanitize_text("WELCOME TO NAMOHUB"), f"WELCOME TO {GENERIC_ORG}")

    def test_no_matches(self):
        self.assertEqual(sanitize_text("This is a standard sentence."), "This is a standard sentence.")

    def test_empty_string(self):
        self.assertEqual(sanitize_text(""), "")

    def test_multiple_matches(self):
        self.assertEqual(
            sanitize_text("Namo and พี่ไอซ์ work at NaMo-Hub"),
            f"{GENERIC_PERSON} and {GENERIC_PERSON} work at {GENERIC_ORG}"
        )

    def test_trimming_spaces(self):
        self.assertEqual(sanitize_text("  hello   world  "), "hello world")

    def test_thai_name_replacement(self):
        self.assertEqual(sanitize_text("คุณนะโม"), f"คุณ{GENERIC_PERSON}")

if __name__ == '__main__':
    unittest.main()
