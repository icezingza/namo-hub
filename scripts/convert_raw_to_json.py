import argparse
import json
import os
import uuid
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WORKFLOWS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'Workflows'))
OUTPUT_FILE_NAME = 'import.json'
VALID_EXTENSIONS = ('.txt', '.md')

def create_blueprint_from_file(filepath):
    """
    Reads a raw file and converts it into a structured dictionary (blueprint).

    Args:
        filepath (str): The full path to the raw file.

    Returns:
        dict: A dictionary representing the blueprint, or None if reading fails.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [Warning] Could not read file: {os.path.basename(filepath)}. Error: {e}")
        return None

    # Use the filename (without extension) as the title, making it more readable.
    filename = os.path.basename(filepath)
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

    # Create the blueprint object with default values.
    # The NamoFoundry app's "auto-classify" feature can refine these later.
    blueprint = {
        "id": f"bp-auto-{uuid.uuid4()}",
        "title": title,
        "author": "Automated Script",
        "nature": "Blueprint",
        "domain": "Technical",  # Default value
        "status": "Draft",      # Default value
        "tags": ["automated-import"],
        "content": content,
        "completeness": 0,      # Will be auto-calculated in the app
        "createdAt": datetime.now().isoformat()
    }
    return blueprint

def parse_args():
    parser = argparse.ArgumentParser(description="Convert raw .txt/.md files to import.json.")
    parser.add_argument("--input-dir", default=DEFAULT_WORKFLOWS_DIR, help="Directory with raw files.")
    parser.add_argument("--output-file", default=OUTPUT_FILE_NAME, help="Output JSON filename.")
    parser.add_argument("--dry-run", action="store_true", help="Process files without writing output.")
    return parser.parse_args()

def main():
    """
    Main function to discover raw files, process them, and write the
    consolidated data to a single JSON file for import.
    """
    args = parse_args()
    all_blueprints = []
    workflows_dir = os.path.abspath(args.input_dir)
    if os.path.isabs(args.output_file) or os.path.dirname(args.output_file):
        output_path = os.path.abspath(args.output_file)
    else:
        output_path = os.path.join(workflows_dir, args.output_file)
    ignored_files = {
        'GUIDE.md',
        'sample_blueprint.json',
        os.path.basename(output_path)
    }

    print("Starting Blueprint Conversion Script...")
    print(f"Looking for '{', '.join(VALID_EXTENSIONS)}' files in '{workflows_dir}/'...")

    # Ensure the workflows directory exists
    if not os.path.isdir(workflows_dir):
        print(f"Error: The '{workflows_dir}' directory does not exist. Please create it and add your raw files.")
        return

    # Iterate over all files in the specified directory
    found_files = 0
    for filename in sorted(os.listdir(workflows_dir)):
        # Skip files that are in the ignored list or don't have a valid extension
        if filename in ignored_files or not filename.endswith(VALID_EXTENSIONS):
            continue

        found_files += 1
        filepath = os.path.join(workflows_dir, filename)
        print(f"  - Processing: {filename}")

        blueprint_data = create_blueprint_from_file(filepath)
        if blueprint_data:
            all_blueprints.append(blueprint_data)

    if found_files == 0:
        print("\nNo raw blueprint files found to convert.")
        return

    # Write the collected blueprints to the output JSON file
    if args.dry_run:
        print(f"\nDry run complete. Files processed: {len(all_blueprints)}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_blueprints, f, indent=2, ensure_ascii=False)

        print(f"\nSuccess! Converted {len(all_blueprints)} files.")
        print(f"   Output file created at: {output_path}")
        print("\nNext Step: Open 'app/index.html' in your browser and use the 'Import JSON' button to load this file.")

    except Exception as e:
        print(f"\nError: Could not write to the output file '{output_path}'.")
        print(f"   Reason: {e}")

if __name__ == "__main__":
    main()
