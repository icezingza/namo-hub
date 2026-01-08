# Release Process

This document defines release steps for NamoFoundry.

## Pre-release checklist
- Run tests: `python -m unittest discover -s tests`
- Run JS test: `node tests/test_normalize.js`
- Validate blueprints: `python tools/validate_blueprints.py --mode strict`
- Review manifest and audit logs if generated.

## Versioning
- Update version references in docs or metadata when needed.
- Tag release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- Push tags: `git push --tags`

## Deployment (GitHub Pages)
- Ensure workflows `deploy.yml` or `static.yml` are enabled.
- Merge to the default branch to trigger deployment.
- Verify the Pages URL after the workflow completes.

## Rollback
- Revert to a previous tag and redeploy.
- If a workflow change caused the issue, restore the prior workflow version.
