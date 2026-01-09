# Security Policy

## Supported Versions
This project is maintained on a best-effort basis. Use the latest commit when possible.

## Reporting a Vulnerability
If you discover a security issue, do not open a public issue. Contact the maintainer
privately and include steps to reproduce the problem.

## Key Management
- Never commit real API keys to source control.
- Use `.env` for local secrets and keep `.env` in `.gitignore`.
- Rotate keys immediately if they are exposed.
