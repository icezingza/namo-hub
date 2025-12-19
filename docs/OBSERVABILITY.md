# Observability

This document defines minimum operational visibility for the pipeline.

## Required outputs
- Manifest summary JSON for each run.
- Per-file status, hash, and duration.
- Warning and error counts.
- Optional audit log in JSONL format.

## Suggested metrics
- Total files processed
- Success count, failure count, skipped count
- Processing time per file (avg, p95)
- Total run time

## Runbook (basic)
- If processing fails early, verify input directory and dependencies.
- If many files are skipped, check file extensions and size limits.
- If validation fails, inspect schema version and missing sections.
