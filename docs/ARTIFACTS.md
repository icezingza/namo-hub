# Artifacts Policy

This document defines which generated files are tracked in git and which are local-only.

## Tracked in git
- `blueprints/*.json`: generated blueprints used by the app and validation.
- `blueprints/_manifest.json`: pipeline run summary.

## Local-only
- `output/`: markdown transformations created by `scripts/transform_framework_docs.py`.
- Temporary files created during testing or conversion.

## Guidance
- Keep generated blueprints committed when they are treated as source of truth.
- If the repository grows too large, consider storing blueprints externally and keep only samples in git.
