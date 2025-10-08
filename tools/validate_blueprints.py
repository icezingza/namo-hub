import os, json, datetime
from pathlib import Path

# Make paths relative to the script's location for robustness
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BLUEPRINTS_DIR = REPO_ROOT / "blueprints"

required_sections = ["executive_summary","value_proposition","system_overview","quick_start_guide","template_instructions","examples","license_and_notes","marketing_pack"]

ok, bad = 0, 0
# Check if blueprint directory exists
if not BLUEPRINTS_DIR.exists():
    print(f"Directory '{BLUEPRINTS_DIR}' not found. Skipping validation.")
    exit(0)

for f in BLUEPRINTS_DIR.iterdir():
    if not f.name.endswith(".json"): continue
    try:
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
        missing = [k for k in required_sections if not data.get("sections", {}).get(k)]
        if missing:
            print(f"⚠️ {f.name} missing sections: {missing}")
            bad += 1
        else:
            print(f"✅ {f.name} complete")
            ok += 1
    except json.JSONDecodeError:
        print(f"❌ {f.name} is not valid JSON.")
        bad += 1
    except Exception as e:
        print(f"❌ Error processing {f.name}: {e}")
        bad += 1


print(f"\nSummary {datetime.date.today()}: OK={ok}, Missing={bad}")
exit(0 if bad==0 else 1)