import os
import docx
import PyPDF2
import re

# Define constants for directories
FRAMEWORK_DIR = "framework"
OUTPUT_DIR = "output"

def sanitize_filename(filename):
    """Sanitizes a string to be used as a valid filename."""
    # Replace spaces with underscores first
    filename = filename.replace(" ", "_")
    # Keep only alphanumeric characters, underscores, hyphens, and periods
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
    # Ensure it's not empty
    if not sanitized:
        return "unnamed_file"
    return sanitized

def read_docx(file_path):
    """Reads and returns the text content from a .docx file."""
    try:
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error reading DOCX file {file_path}: {e}")
        return ""

def read_pdf(file_path):
    """Reads and returns the text content from a .pdf file."""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            full_text = [page.extract_text() for page in reader.pages]
            return "\n".join(full_text)
    except Exception as e:
        print(f"Error reading PDF file {file_path}: {e}")
        return ""

def transform_and_structure_content(raw_text, original_filename):
    """
    Transforms raw text into the structured Master Template format.
    This version incorporates the actual content from the source file.
    """
    print(f"Transforming content from: {original_filename}")

    # 1. Sanitize names (as per instructions)
    sanitized_text = re.sub(r'(พี่ไอซ์|Namo)', '[Subject Matter Expert]', raw_text, flags=re.IGNORECASE)

    # 2. Extract the first 3 paragraphs for the Executive Summary
    paragraphs = [p.strip() for p in sanitized_text.split('\n') if p.strip()]
    executive_summary_paragraphs = paragraphs[:3]
    executive_summary = "\n\n".join(executive_summary_paragraphs)

    # The rest of the content becomes the core content
    core_content_paragraphs = paragraphs[3:]
    core_content = "\n\n".join(core_content_paragraphs)

    if not executive_summary:
        executive_summary = "*(No content was available in the source document to generate a summary.)*"

    if not core_content:
        core_content = "*(The rest of the document content appears here.)*"

    # 3. Clean the title from the filename for a professional look
    title = original_filename.replace("_", " ").replace("-", " ").strip()

    # 4. AI-Generated Marketing Content (Simulated based on title)
    value_proposition = f"Based on the 's '{title}' blueprint, the primary value is its ability to [AI-Generated Core Value], enabling users to build next-generation applications by following the principles and architecture detailed within."
    target_audience = "- Advanced AI Developers\n- Enterprise Architects\n- Technology Futurists & Innovators"
    suggested_pricing = "- **Developer Tier**: $99/month (Access to core framework)\n- **Business Tier**: $499/month (Advanced features & standard support)\n- **Enterprise Tier**: Custom Pricing (Dedicated support, custom integrations)"
    usp = f"Unlike traditional AI models, the '{title}' is a 'living' framework designed for infinite evolution, learning, and adaptation, as detailed in the core content."
    go_to_market = "Primary channels will include technical blogs, partnerships with AI research labs, and a strong presence on GitHub."
    bundling = f"This blueprint can be bundled with the 'NamoNexus Fusion Protocol' for a complete end-to-end intelligent system."
    brand_voice = "Authoritative, visionary, professional, and deeply technical yet accessible."
    license_notes = "This blueprint is released under the MIT License. For commercial use and support, please contact the NamoNexus team."

    # --- Construct the Master Template ---

    transformed_content = f"""
# NamoNexus Master Blueprint: {title}

> **Slogan:** Elevate your existence with NamoNexus.

---

## Meta Definition
> This Blueprint is designed as an entity beyond AI — a self-evolving, meta-intelligent framework that grows infinitely across dimensions.

---

## 1. Executive Summary
{executive_summary}

## 2. Value Proposition (Suggested)
{value_proposition}

## 3. Core Blueprint Content
---
{core_content}
---

## 4. Marketing Pack (Suggested)
### Target Audience
{target_audience}

### Suggested Pricing Models
{suggested_pricing}

### Unique Selling Points (USP)
{usp}

### Go-to-Market Strategy
{go_to_market}

### Potential Bundling
{bundling}

### Brand Voice Guidelines
{brand_voice}

## 5. License & Notes
{license_notes}

---
*This document was automatically generated and transformed by the Blueprint & Template Transformation AI.*
"""
    return transformed_content

def save_as_markdown(content, filename):
    """Saves the given content as a Markdown file in the output directory."""
    output_path = os.path.join(OUTPUT_DIR, f"{filename}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved Master Template to: {output_path}")

def main():
    """
    Main function to orchestrate the transformation process.
    """
    print("Starting the Blueprint & Template Transformation process...")

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    # Loop through all files in the framework directory
    print("Scanning for files in the framework directory...")
    for filename in os.listdir(FRAMEWORK_DIR):
        file_path = os.path.join(FRAMEWORK_DIR, filename)
        base_filename, extension = os.path.splitext(filename)

        print(f"\nAttempting to process: {filename}")
        raw_content = ""
        if extension.lower() == ".docx":
            raw_content = read_docx(file_path)
        elif extension.lower() == ".pdf":
            raw_content = read_pdf(file_path)
        else:
            print(f"Skipping unsupported file type: {filename}")
            continue

        if not raw_content:
            print(f"Content from {filename} is empty or could not be read. Skipping.")
            continue

        # Sanitize the base filename for saving
        safe_filename = sanitize_filename(base_filename)

        # Pass the original filename to the transformation function for use in the title
        master_template_content = transform_and_structure_content(raw_content, base_filename)

        # Use the sanitized filename for saving the file
        save_as_markdown(master_template_content, safe_filename)

        # If this is the target file for verification, print its content to the console.
        if filename == "Code Engine.docx":
            print("\n\n--- VERIFICATION: TRANSFORMED CONTENT FOR 'Code Engine.docx' ---")
            print(master_template_content)
            print("--- END OF VERIFICATION ---\n\n")

    print("\nInitial processing complete.")
    print("Transformation process finished.")

if __name__ == "__main__":
    main()