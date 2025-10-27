import os, json, datetime, time, logging, hashlib, re
import requests
from pathlib import Path
from typing import Tuple
from PyPDF2 import PdfReader
try:
    from docx import Document  # python-docx
    DOCX_OK = True
except Exception:
    DOCX_OK = False

from sanitize import sanitize_text

# -------- Config --------
# Make paths relative to the script's location for robustness
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FRAMEWORK_DIR = REPO_ROOT / "framework"
OUTPUT_DIR    = REPO_ROOT / "blueprints"
SCHEMA_PATH   = SCRIPT_DIR / "schema_blueprint.json" # schema is in the same `tools` dir

JULES_API_SESSIONS = "https://jules.googleapis.com/v1/sessions"
API_KEY = os.getenv("JULES_API_KEY")           # ต้องตั้งใน GitHub Secrets / .env
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
            "source_file": str(src),
            "last_updated": str(datetime.date.today()),
            "pipeline": "auto-blueprint-full"
        }
    }
    return bp

# -------- Jules Integration --------
def jules_enrich(blueprint: dict) -> dict:
    if not API_KEY:
        logging.warning("No JULES_API_KEY provided; skipping Jules enrichment.")
        return blueprint
    payload = {"input": {"text": json.dumps(blueprint, ensure_ascii=False)}}
    for attempt in range(1, RETRIES+1):
        try:
            r = requests.post(
                JULES_API_SESSIONS,
                headers={"X-Goog-Api-Key": API_KEY},
                json=payload,
                timeout=TIMEOUT,
            )
            if r.status_code == 200:
                data = r.json()
                enriched = data.get("output") or data  # fallback
                logging.info("Jules enrichment success.")
                return enriched
            else:
                logging.warning(f"Jules error {r.status_code}: {r.text}")
        except requests.RequestException as e:
            logging.warning(f"Jules network error: {e}")
        time.sleep(2 * attempt)
    logging.warning("Jules enrichment failed after retries; use base blueprint.")
    return blueprint

# -------- Runner --------
def process_one(p: Path) -> Tuple[str, bool]:
    text = load_raw(p)
    if not text:
        logging.warning(f"Empty/unreadable: {p.name}")
        return p.name, False
    bp = build_blueprint(p, text)
    bp = jules_enrich(bp)
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