import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from pii import contains_pii, redact_pii

class TestPii(unittest.TestCase):
    def test_contains_pii(self):
        self.assertTrue(contains_pii("Contact me at test@example.com"))
        self.assertTrue(contains_pii("Call +1-415-555-1212 for info"))
        self.assertTrue(contains_pii("Server at 192.168.1.10"))
        self.assertTrue(contains_pii("Card 4111 1111 1111 1111"))

    def test_redact_pii(self):
        text = "Email test@example.com and call 415-555-1212."
        redacted, counts = redact_pii(text)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertEqual(counts["email"], 1)
        self.assertEqual(counts["phone"], 1)

if __name__ == "__main__":
    unittest.main()
