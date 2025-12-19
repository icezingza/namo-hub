# Coding Guide

This guide describes how to write and organize code in this repository. Use English for
identifiers, comments, and user-facing text. Avoid emoji and non-ASCII characters in new
source text and logs.

## Environment

- Python 3.10 or newer (3.11 recommended)
- Install dependencies: `pip install -r requirements.txt`

## Project layout

- `app/`: static web UI
- `scripts/`: simple conversion utilities
- `tools/`: pipeline tools and validators
- `framework/`: source documents
- `blueprints/`: generated JSON outputs
- `tests/`: unit tests

## General rules

- Keep functions small and single-purpose.
- Prefer `pathlib.Path` for filesystem work in new Python code.
- Validate files and directories before reading or writing.
- Use `encoding="utf-8"` for text I/O.
- Use `logging` for non-interactive output; use `print` for CLI-only scripts.
- For architecture and module design deliverables, follow `docs/MASTER_ROLE_PROMPT_TH.md`.

## Commands

- Create venv: `python -m venv venv`
- Activate venv (Windows): `venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`
- Run tests: `python -m unittest discover -s tests`
- Run manual conversion: `python scripts/convert_raw_to_json.py`
- Run full pipeline: `python tools/auto_blueprint_full.py`
- Run transform: `python scripts/transform_framework_docs.py`
- Validate blueprints: `python tools/validate_blueprints.py`

## Adding a new script

- Place it in `scripts/` or `tools/`.
- Add a `main()` entry point with a `if __name__ == "__main__":` guard.
- Document expected inputs and outputs near the top of the file.
