# tools/blueprint_intelligence.py
from pathlib import Path
import json
import sys

def validate_blueprints():
    base = Path(__file__).resolve().parent.parent
    blueprint_dir = base / "blueprints"

    print("Validating blueprints in:", blueprint_dir)
    errors = []

    if not blueprint_dir.exists():
        print("Warning: No 'blueprints/' directory found.")
        sys.exit(1)

    for file in blueprint_dir.glob("**/*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                errors.append(f"{file.name} is not a valid JSON object.")
            elif "sections" not in data:
                errors.append(f"{file.name} missing 'sections' key.")
            else:
                print(f"OK: {file.name} passed validation.")
        except Exception as e:
            errors.append(f"{file.name} failed: {e}")

    if errors:
        print("\nValidation failed for the following blueprints:")
        for err in errors:
            print(" -", err)
        sys.exit(1)
    else:
        print("\nAll blueprints passed validation.")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_blueprints()
    else:
        print("Usage: python tools/blueprint_intelligence.py validate")
