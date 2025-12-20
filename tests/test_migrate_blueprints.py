import unittest
from pathlib import Path
import sys

tools_dir = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

from migrate_blueprints import migrate_blueprint

class TestMigrateBlueprints(unittest.TestCase):
    def test_migration_adds_required_fields(self):
        data = {
            "id": "BP-20250101-abc123",
            "brand": "NamoNexus",
            "title": "Sample",
            "meta_definition": "Definition",
            "sections": {
                "executive_summary": "summary"
            },
            "status": "draft",
            "version": "0.1",
            "metadata": {
                "author": "Test",
                "language": "en",
                "source_file": "framework/sample.txt",
                "last_updated": "2025-01-01",
                "pipeline": "auto-blueprint-full"
            }
        }
        migrated, report = migrate_blueprint(
            data,
            Path("sample.json"),
            schema_version="1.1",
            pipeline_version="legacy",
            placeholder="Placeholder",
            use_source=False
        )
        self.assertEqual(migrated["schema_version"], "1.1")
        self.assertIn("metadata", migrated)
        self.assertEqual(migrated["metadata"]["pipeline_version"], "legacy")
        self.assertEqual(migrated["sections"]["value_proposition"], "Placeholder")
        self.assertGreaterEqual(report["placeholders_added"], 1)

if __name__ == "__main__":
    unittest.main()
