import os, json, datetime, argparse
from pathlib import Path

def main(blueprints_dir_path):
    # Make paths relative to the script's location for robustness
    SCRIPT_DIR = Path(__file__).resolve().parent
    REPO_ROOT = SCRIPT_DIR.parent

    # Use the provided path, or default to the one in the repo
    BLUEPRINTS_DIR = Path(blueprints_dir_path) if blueprints_dir_path else REPO_ROOT / "blueprints"

    required_sections = ["executive_summary","value_proposition","system_overview","quick_start_guide","template_instructions","examples","license_and_notes","marketing_pack"]

    ok, bad = 0, 0
    # Check if blueprint directory exists
    if not BLUEPRINTS_DIR.exists():
        print(f"Directory '{BLUEPRINTS_DIR}' not found. Skipping validation.")
        return 0 # Exit with success if the directory doesn't exist

    for f in BLUEPRINTS_DIR.iterdir():
        if not f.name.endswith(".json"): continue
        try:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)

            # Gracefully handle if "sections" is null or missing by treating it as an empty dict
            sections_data = data.get("sections") or {}
            missing = [k for k in required_sections if not sections_data.get(k)]

            if missing:
                print(f"Warning: {f.name} missing sections: {missing}")
                bad += 1
            else:
                print(f"OK: {f.name} complete")
                ok += 1
        except json.JSONDecodeError:
            print(f"Error: {f.name} is not valid JSON.")
            bad += 1
        except Exception as e:
            print(f"Error processing {f.name}: {e}")
            bad += 1

    print(f"\nSummary {datetime.date.today()}: OK={ok}, Missing={bad}")
    return 1 if bad > 0 else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate blueprint JSON files.")
    parser.add_argument("blueprints_dir", nargs="?", default=None,
                        help="Path to the blueprints directory (optional).")
    args = parser.parse_args()

    exit_code = main(args.blueprints_dir)
    exit(exit_code)
