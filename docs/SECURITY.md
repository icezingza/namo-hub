# Security and PII Policy

This document defines baseline security and privacy practices for this repository.

## Data classification
- Public: documentation and code.
- Internal: generated blueprints and manifests.
- Sensitive: any source content that contains PII.

## PII handling
- Redact obvious PII when the pipeline is run with redaction enabled.
- Store only the minimum metadata required for processing.
- Do not commit secrets or API keys into the repository.

## Audit logging
- Audit logs must be pseudonymized.
- Use hashed identifiers for source file paths.
- Record timestamp, file hash, and status for each processed file.

## Secrets management
- Use environment variables for API keys.
- Add secrets only via CI or local environment, never in files.

## License and watermarking
- If output requires license enforcement or watermarking, include `license_id` and `build_id` in metadata.

## Incident response
- If a leak is suspected, rotate keys immediately and remove leaked artifacts.
- Re-run the pipeline with PII redaction enabled for affected inputs.
