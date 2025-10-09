import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# --- Configuration ---
# Make paths relative to the script's location for robustness
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# The directory where your raw blueprint files (.txt, .md) are stored.
WORKFLOWS_DIR = REPO_ROOT / 'Workflows'
# The name of the output file that will be generated.
OUTPUT_FILE_NAME = 'import.json'
# The file extensions to look for.
VALID_EXTENSIONS = ('.txt', '.md')
# List of files to ignore during conversion.
IGNORED_FILES = {
    'GUIDE.md',
    'sample_blueprint.json',
    OUTPUT_FILE_NAME
}

def create_blueprint_from_file(filepath):
    """
    Reads a raw file and converts it into a structured dictionary (blueprint).

    Args:
        filepath (Path): The full path to the raw file.

    Returns:
        dict: A dictionary representing the blueprint, or None if reading fails.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [Warning] Could not read file: {filepath.name}. Error: {e}")
        return None

    # Use the filename (without extension) as the title, making it more readable.
    title = filepath.stem.replace('_', ' ').replace('-', ' ').title()

    # Create the blueprint object with default values.
    # The NaMo Hub app's "auto-classify" feature can refine these later.
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

def main():
    """
    Main function to discover raw files, process them, and write the
    consolidated data to a single JSON file for import.
    """
    all_blueprints = []
    output_path = WORKFLOWS_DIR / OUTPUT_FILE_NAME

    print("🚀 Starting Blueprint Conversion Script...")
    print(f"Looking for '{', '.join(VALID_EXTENSIONS)}' files in '{WORKFLOWS_DIR}'...")

    # Ensure the workflows directory exists
    if not WORKFLOWS_DIR.is_dir():
        print(f"❌ Error: The '{WORKFLOWS_DIR}' directory does not exist. Please create it and add your raw files.")
        return

    # Iterate over all files in the specified directory
    found_files = 0
    for file_path in sorted(WORKFLOWS_DIR.iterdir()):
        # Skip files that are in the ignored list or don't have a valid extension
        if file_path.name in IGNORED_FILES or file_path.suffix not in VALID_EXTENSIONS:
            continue

        found_files += 1
        print(f"  - Processing: {file_path.name}")

        blueprint_data = create_blueprint_from_file(file_path)
        if blueprint_data:
            all_blueprints.append(blueprint_data)

    if found_files == 0:
        print("\n🟡 No raw blueprint files found to convert.")
        return

    # Write the collected blueprints to the output JSON file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_blueprints, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Success! Converted {len(all_blueprints)} files.")
        print(f"   Output file created at: {output_path}")
        print("\n👉 Next Step: Open 'app/index.html' in your browser and use the 'Import JSON' button to load this file.")

    except Exception as e:
        print(f"\n❌ Error: Could not write to the output file '{output_path}'.")
        print(f"   Reason: {e}")

if __name__ == "__main__":
    main()