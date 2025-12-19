import os
import json
import datetime
import time
import logging
import hashlib
import re
from pathlib import Path
from typing import Tuple

try:
    import google.generativeai as genai
    GENAI_OK = True
except Exception:
    genai = None
    GENAI_OK = False

try:
    from PyPDF2 import PdfReader
    PDF_OK = True
except Exception:
    PdfReader = None
    PDF_OK = False

try:
    from docx import Document  # python-docx
    DOCX_OK = True
except Exception:
    Document = None
    DOCX_OK = False

from sanitize import sanitize_text

# -------- Config --------
# Make paths relative to the script's location for robustness
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FRAMEWORK_DIR = REPO_ROOT / "framework"
OUTPUT_DIR    = REPO_ROOT / "blueprints"
SCHEMA_PATH   = SCRIPT_DIR / "schema_blueprint.json" # schema is in the same `tools` dir

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GENAI_OK:
    genai.configure(api_key=GEMINI_API_KEY)
elif GEMINI_API_KEY and not GENAI_OK:
    logging.warning(
        "GEMINI_API_KEY set but google-generativeai is not installed; skipping Gemini enrichment."
    )
else:
    logging.info("GEMINI_API_KEY not found; skipping Gemini enrichment.")
BRAND   = "NamoNexus"
SLOGAN  = "Elevate your existence with NamoNexus."
META_DEF = ("This Blueprint is designed as an entity beyond AI — "
            "a self-evolving, meta-intelligent framework that grows infinitely across dimensions.")

TIMEOUT = 20
RETRIES = 3
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# -------- Readers --------
def read_txt_md(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore").strip()

def read_pdf(p: Path) -> str:
    if not PDF_OK:
        logging.warning("PyPDF2 not installed; skip .pdf")
        return ""
    try:
        reader = PdfReader(str(p))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text.strip()
    except Exception as e:
        logging.warning(f"PDF read error {p}: {e}")
        return ""

def read_docx(p: Path) -> str:
    if not DOCX_OK:
        logging.warning("python-docx not installed; skip .docx")
        return ""
    try:
        d = Document(str(p))
        return "\n".join([para.text for para in d.paragraphs]).strip()
    except Exception as e:
        logging.warning(f"DOCX read error {p}: {e}")
        return ""

def load_raw(p: Path) -> str:
    if p.suffix.lower() in [".txt", ".md"]:
        return read_txt_md(p)
    if p.suffix.lower() == ".pdf":
        return read_pdf(p)
    if p.suffix.lower() == ".docx":
        return read_docx(p)
    return ""

# -------- Blueprint Maker --------
def make_id(seed: str) -> str:
    h = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:6]
    return f"BP-{datetime.date.today().strftime('%Y%m%d')}-{h}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename by forcing it to ASCII, removing special characters,
    and handling potential empty results.
    """
    stem = Path(filename).stem

    # Force transliteration to ASCII, ignoring characters that cannot be converted
    ascii_stem = stem.encode('ascii', 'ignore').decode('ascii')

    # Replace any remaining non-alphanumeric characters (except safe ones) with an underscore
    safe_stem = re.sub(r'[^\w.-]+', '_', ascii_stem)

    # Collapse multiple underscores and remove leading/trailing ones
    safe_stem = re.sub(r'_+', '_', safe_stem).strip('_')

    # If the filename becomes empty (e.g., it was purely non-ASCII), create a fallback name
    if not safe_stem:
        return f"blueprint_{hashlib.md5(stem.encode()).hexdigest()[:8]}"

    return safe_stem

def scaffold_sections(content: str) -> dict:
    # สร้าง scaffold อังกฤษเชิงโปร + ฟิวเจอร์ริสติก
    # executive_summary ตัดสั้นเข้าใจไว, ช่องอื่นปล่อย empty ให้ทีมเติม/หรือให้ Jules enrich
    return {
        "executive_summary": content[:600],
        "value_proposition": "Universal adaptability, modular architecture, AI-agnostic integration, and self-evolving design.",
        "system_overview": "A layered framework transforming raw data into commercial blueprints with metadata and validation.",
        "quick_start_guide": "1) Place raw files into /framework  2) Run the pipeline  3) Review JSON in /blueprints  4) Deploy to your ecosystem.",
        "template_instructions": "Follow the schema. Keep sections concise. Use neutral, professional English. Avoid personal names.",
        "examples": "Education curricula, healthcare protocols, financial decision flows, brand guidelines.",
        "license_and_notes": "Licensed under NamoVerse Creative Framework License (NCFL-1.0). Provide attribution for redistribution.",
        "marketing_pack": "Target: builders, strategists, educators. Pain: unstructured data. USP: chaos-to-commerce via meta-intelligence. Pricing: Base/Pro tiers. GTM: ProductHunt + LinkedIn."
    }

def build_blueprint(src: Path, raw_text: str) -> dict:
    sanitized = sanitize_text(raw_text)
    title = src.stem.replace("_", " ")
    bp = {
        "id": make_id(src.name),
        "brand": BRAND,
        "title": title,
        "slogan": SLOGAN,
        "meta_definition": META_DEF,
        "sections": scaffold_sections(sanitized),
        "visual_identity": {},
        "status": "draft",
        "version": "0.1",
        "metadata": {
            "author": "NamoVerse Engine",
            "language": "en",
            "source_file": src.as_posix(),
            "last_updated": str(datetime.date.today()),
            "pipeline": "auto-blueprint-full"
        }
    }
    return bp

# -------- Jules Integration --------
# -------- Gemini Integration --------
def gemini_enrich(blueprint: dict) -> dict:
    if not GEMINI_API_KEY or not GENAI_OK:
        if GEMINI_API_KEY and not GENAI_OK:
            logging.warning("google-generativeai not installed; skipping Gemini enrichment.")
        else:
            logging.info("No GEMINI_API_KEY provided; skipping Gemini enrichment.")
        return blueprint

    # Prepare specific data to guide the LLM
    raw_content = blueprint['sections']['executive_summary'] # Currently holds raw text
    title = blueprint['title']
    
    prompt = f"""
    You are an expert Knowledge Architect. Your task is to transform raw unstructured text into a structured "Blueprint" JSON format.
    
    Here is the raw content from a document titled "{title}":
    ---
    {raw_content[:4000]} 
    ---
    (Note: Content truncated to first 4000 characters if too long)

    Please analyze the content and generate a JSON object that strictly follows this structure (do not include markdown fencing, just the JSON):
    {{
        "sections": {{
            "executive_summary": "A concise summary of the core idea (max 3 sentences).",
            "value_proposition": "What is the unique value or benefit? (max 2 sentences).",
            "system_overview": "Technical or logical architecture description.",
            "quick_start_guide": "Step-by-step guide to get started.",
            "examples": "Practical use cases.",
            "marketing_pack": "Target audience, pain points, and selling points."
        }},
        "tags": ["tag1", "tag2", "tag3"]
    }}

    If the raw content is empty or meaningless, just return reasonable generic placeholders related to "{title}".
    """

    model = genai.GenerativeModel('gemini-1.5-flash')

    for attempt in range(1, RETRIES+1):
        try:
            response = model.generate_content(prompt)
            # Simple cleanup to ensure valid JSON
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            if text.startswith("```"):
                text = text[3:-3]
                
            data = json.loads(text)
            
            # Merge enriched data back into blueprint
            blueprint['sections'].update(data.get('sections', {}))
            blueprint['tags'] = data.get('tags', [])
            
            logging.info("Gemini enrichment success.")
            return blueprint

        except Exception as e:
            logging.warning(f"Gemini error attempt {attempt}: {e}")
            time.sleep(2 * attempt)

    logging.warning("Gemini enrichment failed after retries; using base blueprint.")
    return blueprint

# -------- Runner --------
def process_one(p: Path) -> Tuple[str, bool]:
    text = load_raw(p)
    if not text:
        logging.warning(f"Empty/unreadable: {p.name}")
        return p.name, False
    bp = build_blueprint(p, text)
    bp = gemini_enrich(bp)
    bp["status"] = "complete"

    safe_stem = sanitize_filename(p.name)
    out_filename = f"{safe_stem}.json"
    out = OUTPUT_DIR / out_filename

    out.write_text(json.dumps(bp, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info(f"Saved blueprint: {out}")
    return p.name, True

def main():
    files = sorted([p for p in FRAMEWORK_DIR.iterdir() if p.suffix.lower() in (".txt",".md",".pdf",".docx")])
    if not files:
        logging.info("No raw files found.")
        return
    success, fail = 0, 0
    for p in files:
        _, ok = process_one(p)
        success += 1 if ok else 0
        fail    += 0 if ok else 1
    logging.info(f"Done. Success: {success} | Failed: {fail}")

if __name__ == "__main__":
    main()
