# Release Checklist (Pre-Sale)

## Security and Secrets
- Confirm `.env` is not included in any release bundles.
- Ensure `.env_example` contains placeholder values only.
- Scan for leaked keys: `rg -n "sk-" .`
- Rotate any exposed keys immediately.

## Build and Tests
- Install dependencies: `pip install -r requirements.txt`
- Install dev dependencies: `pip install -r requirements-dev.txt`
- Run tests: `pytest`

## Configuration and Defaults
- Verify `OPENAI_MODEL` defaults match README and `.env_example`.
- Confirm `config.json` reflects the intended public persona defaults.
- Ensure `custom_directives` complies with platform policies.

## Documentation
- README quick start and configuration are accurate.
- SECURITY.md includes the correct contact procedure.
- LICENSE is correct for your business model.
- SUPPORT.md matches your support promise and pricing terms.

## Release Hygiene
- Remove local caches: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- Check repository for large or irrelevant files.
