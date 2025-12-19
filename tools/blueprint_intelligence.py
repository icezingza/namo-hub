import argparse
from pathlib import Path

from validate_blueprints import main as validate_blueprints_main

def parse_args():
    parser = argparse.ArgumentParser(description="Blueprint intelligence helper.")
    parser.add_argument("command", choices=["validate"], help="Command to run.")
    parser.add_argument("--mode", choices=["lenient", "strict"], default="lenient", help="Validation mode.")
    parser.add_argument("--blueprints-dir", default="", help="Blueprints directory (optional).")
    parser.add_argument("--schema", default="", help="Schema path (optional).")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    if args.command == "validate":
        schema_path = args.schema or str(Path(__file__).resolve().parent / "schema_blueprint.json")
        strict = args.mode == "strict"
        return validate_blueprints_main(args.blueprints_dir, schema_path, strict, "", False)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
