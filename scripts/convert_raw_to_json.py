import os
import json
import uuid
from datetime import datetime

# --- Configuration ---
# The absolute path to the directory where raw blueprint files are stored.
# This is calculated relative to the script's location to ensure it works from anywhere.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOWS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'Workflows'))
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
    output_path = os.path.join(WORKFLOWS_DIR, OUTPUT_FILE_NAME)

    print("🚀 Starting Blueprint Conversion Script...")
    print(f"Looking for '{', '.join(VALID_EXTENSIONS)}' files in '{WORKFLOWS_DIR}/'...")

    # Ensure the workflows directory exists
    if not os.path.isdir(WORKFLOWS_DIR):
        print(f"❌ Error: The '{WORKFLOWS_DIR}' directory does not exist. Please create it and add your raw files.")
        return

    # Iterate over all files in the specified directory
    found_files = 0
    for filename in sorted(os.listdir(WORKFLOWS_DIR)):
        # Skip files that are in the ignored list or don't have a valid extension
        if filename in IGNORED_FILES or not filename.endswith(VALID_EXTENSIONS):
            continue

        found_files += 1
        filepath = os.path.join(WORKFLOWS_DIR, filename)
        print(f"  - Processing: {filename}")

        blueprint_data = create_blueprint_from_file(filepath)
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