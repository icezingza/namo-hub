import argparse
import datetime
import json
from pathlib import Path

try:
    import jsonschema
    JSONSCHEMA_OK = True
except Exception:
    jsonschema = None
    JSONSCHEMA_OK = False

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_SCHEMA = SCRIPT_DIR / "schema_blueprint.json"

REQUIRED_SECTIONS = [
    "executive_summary",
    "value_proposition",
    "system_overview",
    "quick_start_guide",
    "template_instructions",
    "examples",
    "license_and_notes",
    "marketing_pack"
]

TOP_LEVEL_REQUIRED = [
    "schema_version",
    "id",
    "brand",
    "title",
    "meta_definition",
    "sections",
    "status",
    "version",
    "metadata"
]

METADATA_REQUIRED = [
    "author",
    "language",
    "source_file",
    "source_name",
    "source_hash",
    "source_bytes",
    "last_updated",
    "pipeline",
    "pipeline_version"
]

def load_schema(schema_path: Path) -> dict:
    return json.loads(schema_path.read_text(encoding="utf-8"))

def validate_file(path: Path, schema: dict, strict: bool) -> dict:
    result = {
        "file": path.name,
        "status": "ok",
        "missing_sections": [],
        "missing_fields": [],
        "errors": []
    }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        result["status"] = "error"
        result["errors"].append("invalid-json")
        return result
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"read-error:{e}")
        return result

    if strict:
        if not JSONSCHEMA_OK:
            result["status"] = "error"
            result["errors"].append("jsonschema-not-installed")
            return result
        try:
            jsonschema.validate(instance=data, schema=schema)
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"schema-error:{e}")
            return result

    for key in TOP_LEVEL_REQUIRED:
        if key not in data:
            result["missing_fields"].append(key)

    sections = data.get("sections") or {}
    missing_sections = [k for k in REQUIRED_SECTIONS if not sections.get(k)]
    if missing_sections:
        result["missing_sections"] = missing_sections
        result["status"] = "error"

    metadata = data.get("metadata") or {}
    missing_metadata = [k for k in METADATA_REQUIRED if not metadata.get(k)]
    if missing_metadata:
        result["missing_fields"].extend([f"metadata.{k}" for k in missing_metadata])
        if result["status"] != "error":
            result["status"] = "warn" if not strict else "error"

    return result

def summarize(results: list) -> dict:
    counts = {"ok": 0, "warn": 0, "error": 0}
    for r in results:
        counts[r["status"]] += 1
    return {
        "date": str(datetime.date.today()),
        "counts": counts,
        "total": len(results)
    }

def main(blueprints_dir_path: str, schema_path: str, strict: bool, summary_json: str, fail_fast: bool) -> int:
    blueprints_dir = Path(blueprints_dir_path) if blueprints_dir_path else REPO_ROOT / "blueprints"

    if not blueprints_dir.exists():
        print(f"Directory '{blueprints_dir}' not found. Skipping validation.")
        return 0

    schema = load_schema(Path(schema_path))
    results = []

    for f in blueprints_dir.iterdir():
        if not f.name.endswith(".json"):
            continue
        result = validate_file(f, schema, strict)
        results.append(result)
        if result["status"] == "ok":
            print(f"OK: {f.name} complete")
        elif result["status"] == "warn":
            print(f"Warning: {f.name} missing fields or sections")
        else:
            print(f"Error: {f.name} failed validation")
        if fail_fast and result["status"] == "error":
            break

    summary = summarize(results)
    print(f"Summary {summary['date']}: OK={summary['counts']['ok']}, Warning={summary['counts']['warn']}, Error={summary['counts']['error']}")

    if summary_json:
        Path(summary_json).write_text(json.dumps(summary, ensure_ascii=True, indent=2), encoding="utf-8")

    return 1 if summary["counts"]["error"] > 0 else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate blueprint JSON files.")
    parser.add_argument("blueprints_dir", nargs="?", default=None, help="Path to the blueprints directory (optional).")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Path to schema JSON.")
    parser.add_argument("--strict", action="store_true", help="Enable JSON schema validation.")
    parser.add_argument("--summary-json", default="", help="Write a summary JSON file.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first error.")
    args = parser.parse_args()

    exit_code = main(args.blueprints_dir, args.schema, args.strict, args.summary_json, args.fail_fast)
    raise SystemExit(exit_code)
