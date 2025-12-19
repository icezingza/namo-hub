# Scorecard

This scorecard defines full-score acceptance criteria for each category. Use it as the Definition of Done (DoD) for quality gates.

## Master prompt completeness
- Has clear role, mission, objectives, and constraints.
- Includes IO contract, self-evolution loop, and KPI list.
- Provides few-shot examples and a short version.
- References enforcement steps and validation actions.

## Architecture separation
- System-level diagram exists.
- Responsibilities per component are documented.
- Data flow and IO contracts are explicit.
- Entry points and dependencies are mapped.

## Pipeline robustness
- Deterministic output naming or collision strategy.
- Idempotent processing or skip-unchanged option.
- Manifest/run summary is produced.
- Clear error handling with actionable messages.
- CLI options for input/output and dry-run.

## Code quality and maintainability
- Small, single-purpose functions.
- Clear module boundaries and minimal duplication.
- Consistent logging and error handling.
- Stable configuration and constants.

## Testing and QA
- Unit tests for core tools and edge cases.
- Golden outputs for representative inputs.
- Schema validation tests.
- CI gate runs tests on push/PR.

## Documentation and onboarding
- README covers workflows and commands.
- ARCHITECTURE.md describes data flow and components.
- SECURITY.md defines PII and audit policies.
- Scorecard and runbook are present.

## Security and compliance
- PII handling policy is explicit.
- Redaction capability is available.
- Audit logs are pseudonymized.
- Secrets are kept out of code and repo.

## Observability and ops
- Structured logs or summary manifest exists.
- Error counts and timing metrics are captured.
- Runbook for failure modes exists.

## Scalability and performance
- Limits and batching options exist.
- Skip-unchanged and caching paths exist.
- Large-file safeguards are documented.

## UX and validation
- Import validation with clear error feedback.
- Export format is stable and documented.
- UI shows state transitions and errors.

## Release and automation
- CI runs tests and checks on PRs.
- Automation workflows use pinned versions.
- Release steps are documented.
