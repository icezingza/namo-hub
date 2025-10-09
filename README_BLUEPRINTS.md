# NamoVerse™ Auto Blueprint Pipeline
**Goal:** Convert raw files in `/framework` (txt/md/pdf/docx) into commercial-ready blueprints in `/blueprints` automatically.
**Brand:** NamoNexus · Slogan: "Elevate your existence with NamoNexus."

## How it works
1. Put raw files into `/framework`.
2. Pipeline sanitizes names → scaffolds professional EN sections → (optional) enrich via Jules.
3. Outputs complete JSON to `/blueprints`, validated by schema.

## Run locally
```bash
pip install PyPDF2 python-docx requests
export JULES_API_KEY=XXXX   # หรือใช้ .env
python tools/auto_blueprint_full.py
python tools/validate_blueprints.py
```

## GitHub Actions

* Triggers on push to `framework/**` and on schedule every 6 hours.
* Set `JULES_API_KEY` in **Settings → Secrets → Actions**.

## JSON Schema

See `tools/schema_blueprint.json`. Output includes:

* `meta_definition`: *entity beyond AI — self-evolving meta-intelligence*
* `sections`: executive_summary … marketing_pack