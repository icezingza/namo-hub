import argparse
import datetime
import hashlib
import json
import logging
import os
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from google import genai
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
from pii import redact_pii

# -------- Config --------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

DEFAULT_INPUT_DIR = REPO_ROOT / "framework"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "blueprints"
DEFAULT_SCHEMA_PATH = SCRIPT_DIR / "schema_blueprint.json"

PIPELINE_NAME = "auto-blueprint-full"
PIPELINE_VERSION = "1.1"
SCHEMA_VERSION = "1.1"

BRAND = "NamoNexus"
SLOGAN = "Elevate your existence with NamoNexus."
META_DEF = (
    "This Blueprint is designed as an entity beyond AI - "
    "a self-evolving, meta-intelligent framework that grows infinitely across dimensions."
)

TIMEOUT = 20
RETRIES = 3

# -------- Gemini Setup --------
def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and GENAI_OK:
        return genai.Client(api_key=api_key)
    if api_key and not GENAI_OK:
        logging.warning(
            "GEMINI_API_KEY set but google-genai is not installed; skipping Gemini enrichment."
        )
        return None
    logging.info("GEMINI_API_KEY not found; skipping Gemini enrichment.")
    return None

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
    ext = p.suffix.lower()
    if ext in [".txt", ".md"]:
        return read_txt_md(p)
    if ext == ".pdf":
        return read_pdf(p)
    if ext == ".docx":
        return read_docx(p)
    return ""

# -------- Helpers --------
def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def hash_identifier(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]

def relative_source_path(src: Path, repo_root: Path) -> str:
    try:
        rel = src.relative_to(repo_root)
        return rel.as_posix()
    except Exception:
        return src.as_posix()

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename by forcing it to ASCII, removing special characters,
    and handling potential empty results.
    """
    stem = Path(filename).stem
    ascii_stem = stem.encode("ascii", "ignore").decode("ascii")
    safe_stem = re.sub(r"[^\w.-]+", "_", ascii_stem)
    safe_stem = re.sub(r"_+", "_", safe_stem).strip("_")
    if not safe_stem:
        return f"blueprint_{hashlib.md5(stem.encode()).hexdigest()[:8]}"
    return safe_stem

def build_output_path(output_dir: Path, safe_stem: str, source_hash: str) -> Path:
    primary = output_dir / f"{safe_stem}.json"
    if not primary.exists():
        return primary
    existing_hash = extract_source_hash(primary)
    if existing_hash == source_hash:
        return primary
    suffix = source_hash[:8]
    candidate = output_dir / f"{safe_stem}_{suffix}.json"
    if not candidate.exists():
        return candidate
    counter = 2
    while True:
        candidate = output_dir / f"{safe_stem}_{suffix}_{counter}.json"
        if not candidate.exists():
            return candidate
        counter += 1

def extract_source_hash(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    return data.get("metadata", {}).get("source_hash", "")

def format_mtime(src: Path) -> str:
    try:
        return datetime.datetime.fromtimestamp(src.stat().st_mtime).isoformat()
    except Exception:
        return ""

# -------- Blueprint Maker --------
def make_id(seed: str) -> str:
    h = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:6]
    return f"BP-{datetime.date.today().strftime('%Y%m%d')}-{h}"

def scaffold_sections(content: str) -> dict:
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

def build_source_info(src: Path, raw_text: str, anonymize_source: bool) -> Dict[str, object]:
    source_file = relative_source_path(src, REPO_ROOT)
    source_name = src.name
    source_hash = hash_text(raw_text)
    source_bytes = len(raw_text.encode("utf-8", errors="ignore"))
    source_mtime = format_mtime(src)
    if anonymize_source:
        source_id = hash_identifier(source_file)
        source_file = f"hash:{source_id}"
        source_name = f"hash:{source_id}"
    return {
        "source_file": source_file,
        "source_name": source_name,
        "source_hash": source_hash,
        "source_bytes": source_bytes,
        "source_mtime": source_mtime,
        "anonymized_source": anonymize_source
    }

def build_blueprint(
    src: Path,
    content: str,
    source_info: Dict[str, object],
    run_id: str,
    pii_redacted: bool
) -> dict:
    title = src.stem.replace("_", " ").strip()
    metadata = {
        "author": "NamoVerse Engine",
        "language": "en",
        "source_file": source_info["source_file"],
        "source_name": source_info["source_name"],
        "source_hash": source_info["source_hash"],
        "source_bytes": source_info["source_bytes"],
        "source_mtime": source_info["source_mtime"],
        "last_updated": str(datetime.date.today()),
        "pipeline": PIPELINE_NAME,
        "pipeline_version": PIPELINE_VERSION,
        "pii_redacted": pii_redacted,
        "anonymized_source": source_info["anonymized_source"]
    }
    if run_id:
        metadata["run_id"] = run_id

    return {
        "schema_version": SCHEMA_VERSION,
        "id": make_id(src.name),
        "brand": BRAND,
        "title": title,
        "slogan": SLOGAN,
        "meta_definition": META_DEF,
        "tags": [],
        "sections": scaffold_sections(content),
        "visual_identity": {},
        "status": "draft",
        "version": "0.2",
        "metadata": metadata
    }

# -------- Gemini Integration --------
def gemini_enrich(blueprint: dict, client) -> dict:
    if client is None or not GENAI_OK:
        if client is None:
            logging.info("Gemini client not configured; skipping enrichment.")
        return blueprint

    raw_content = blueprint["sections"]["executive_summary"]
    title = blueprint["title"]

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

If the raw content is empty or meaningless, return reasonable placeholders related to "{title}".
"""

    for attempt in range(1, RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            text = (response.text or "").strip()
            if text.startswith("```json"):
                text = text[7:-3]
            if text.startswith("```"):
                text = text[3:-3]

            data = json.loads(text)
            blueprint["sections"].update(data.get("sections", {}))
            blueprint["tags"] = data.get("tags", []) or []
            logging.info("Gemini enrichment success.")
            return blueprint
        except Exception as e:
            logging.warning(f"Gemini error attempt {attempt}: {e}")
            time.sleep(2 * attempt)

    logging.warning("Gemini enrichment failed after retries; using base blueprint.")
    return blueprint

# -------- Runner --------
def process_one(
    p: Path,
    output_dir: Path,
    client,
    run_id: str,
    redact: bool,
    anonymize_source: bool,
    dry_run: bool,
    skip_unchanged: bool,
    max_bytes: int,
    output_lock
) -> Tuple[Dict[str, object], bool]:
    started = time.time()
    result: Dict[str, object] = {
        "source_file": "",
        "source_name": "",
        "source_hash": "",
        "status": "error",
        "output_file": "",
        "warnings": [],
        "errors": [],
        "duration_ms": 0
    }

    if max_bytes and p.stat().st_size > max_bytes:
        result["status"] = "skipped"
        result["warnings"].append("max-bytes-exceeded")
        result["duration_ms"] = int((time.time() - started) * 1000)
        return result, True

    raw_text = load_raw(p)
    if not raw_text:
        result["status"] = "skipped"
        result["warnings"].append("empty-or-unreadable")
        result["duration_ms"] = int((time.time() - started) * 1000)
        return result, True

    sanitized = sanitize_text(raw_text)
    pii_redacted = False
    if redact:
        sanitized, pii_stats = redact_pii(sanitized)
        pii_redacted = any(pii_stats.values())

    source_info = build_source_info(p, raw_text, anonymize_source)
    result["source_file"] = source_info["source_file"]
    result["source_name"] = source_info["source_name"]
    result["source_hash"] = source_info["source_hash"]

    safe_stem = sanitize_filename(p.name)

    out_path = build_output_path(output_dir, safe_stem, source_info["source_hash"])
    if skip_unchanged and out_path.exists():
        existing_hash = extract_source_hash(out_path)
        if existing_hash == source_info["source_hash"]:
            result["status"] = "skipped"
            result["warnings"].append("unchanged")
            result["output_file"] = out_path.as_posix()
            result["duration_ms"] = int((time.time() - started) * 1000)
            return result, True

    bp = build_blueprint(
        p,
        sanitized,
        source_info,
        run_id,
        pii_redacted
    )
    bp = gemini_enrich(bp, client)
    bp["status"] = "complete"

    if dry_run:
        result["status"] = "dry_run"
        result["output_file"] = out_path.as_posix()
        result["duration_ms"] = int((time.time() - started) * 1000)
        return result, True

    try:
        if output_lock:
            output_lock.acquire()
        out_path = build_output_path(output_dir, safe_stem, source_info["source_hash"])
        out_path.write_text(json.dumps(bp, ensure_ascii=False, indent=2), encoding="utf-8")
        result["status"] = "ok"
        result["output_file"] = out_path.as_posix()
        result["duration_ms"] = int((time.time() - started) * 1000)
        logging.info(f"Saved blueprint: {out_path}")
        return result, True
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"write-error:{e}")
        result["duration_ms"] = int((time.time() - started) * 1000)
        return result, False
    finally:
        if output_lock:
            output_lock.release()

def write_manifest(path: Path, payload: Dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

def write_audit_log(path: Path, entries: List[Dict[str, object]]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-generate blueprint JSON files from documents.")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Input directory with raw files.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for blueprints.")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="Schema path (informational).")
    parser.add_argument("--manifest", default="", help="Path to manifest JSON output.")
    parser.add_argument("--audit-log", default="", help="Path to audit log JSONL.")
    parser.add_argument("--dry-run", action="store_true", help="Process files without writing outputs.")
    parser.add_argument("--max-files", type=int, default=0, help="Limit number of files processed.")
    parser.add_argument("--max-bytes", type=int, default=0, help="Skip files larger than this size.")
    parser.add_argument("--skip-unchanged", action="store_true", help="Skip files if output hash matches.")
    parser.add_argument("--redact-pii", action="store_true", help="Redact obvious PII before output.")
    parser.add_argument("--anonymize-source", action="store_true", help="Hash source paths in metadata.")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker threads.")
    parser.add_argument("--log-level", default="INFO", help="Logging level.")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    client = configure_gemini()
    run_id = str(uuid.uuid4())
    workers = max(1, int(args.workers))

    if not input_dir.exists():
        logging.error(f"Input directory not found: {input_dir}")
        return 1

    files = sorted([p for p in input_dir.iterdir() if p.suffix.lower() in (".txt", ".md", ".pdf", ".docx")])
    if args.max_files and args.max_files > 0:
        files = files[:args.max_files]

    if not files:
        logging.info("No raw files found.")
        return 0

    success, fail = 0, 0
    results: List[Dict[str, object]] = []
    audit_entries: List[Dict[str, object]] = []
    output_lock = None
    if workers > 1:
        import threading
        output_lock = threading.Lock()

    run_started = datetime.datetime.utcnow()

    def handle_result(result: Dict[str, object], ok: bool, file_name: str) -> None:
        nonlocal success, fail
        results.append(result)
        status = result.get("status", "")
        if status not in ("ok", "dry_run"):
            logging.warning(f"Skipped {file_name}: {status}")
        success += 1 if ok else 0
        fail += 0 if ok else 1
        audit_entries.append({
            "run_id": run_id,
            "source_id": hash_identifier(str(result.get("source_file", ""))),
            "source_hash": result.get("source_hash", ""),
            "status": status,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })

    if workers > 1:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    process_one,
                    p,
                    output_dir,
                    client,
                    run_id,
                    args.redact_pii,
                    args.anonymize_source,
                    args.dry_run,
                    args.skip_unchanged,
                    args.max_bytes,
                    output_lock
                ): p
                for p in files
            }
            for future in as_completed(future_map):
                p = future_map[future]
                try:
                    result, ok = future.result()
                except Exception as e:
                    result = {
                        "source_file": "",
                        "source_name": p.name,
                        "source_hash": "",
                        "status": "error",
                        "output_file": "",
                        "warnings": [],
                        "errors": [f"exception:{e}"],
                        "duration_ms": 0
                    }
                    ok = False
                handle_result(result, ok, p.name)
    else:
        for p in files:
            result, ok = process_one(
                p,
                output_dir,
                client,
                run_id,
                args.redact_pii,
                args.anonymize_source,
                args.dry_run,
                args.skip_unchanged,
                args.max_bytes,
                output_lock
            )
            handle_result(result, ok, p.name)

    results.sort(key=lambda r: r.get("source_name", ""))
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    dry_runs = sum(1 for r in results if r.get("status") == "dry_run")
    warning_count = sum(len(r.get("warnings", [])) for r in results)
    error_count = sum(len(r.get("errors", [])) for r in results)

    run_finished = datetime.datetime.utcnow()
    summary = {
        "run_id": run_id,
        "pipeline": PIPELINE_NAME,
        "pipeline_version": PIPELINE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "schema_path": Path(args.schema).as_posix(),
        "input_dir": input_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "started_at": run_started.isoformat() + "Z",
        "finished_at": run_finished.isoformat() + "Z",
        "total_files": len(files),
        "success": success,
        "failed": fail,
        "skipped": skipped,
        "dry_run": dry_runs,
        "warnings": warning_count,
        "errors": error_count,
        "results": results
    }

    manifest_path = Path(args.manifest) if args.manifest else output_dir / "_manifest.json"
    if not args.dry_run:
        write_manifest(manifest_path, summary)
        logging.info(f"Manifest written: {manifest_path}")

    if args.audit_log:
        write_audit_log(Path(args.audit_log), audit_entries)

    logging.info(f"Done. Success: {success} | Failed: {fail}")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
