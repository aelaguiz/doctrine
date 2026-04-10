# Candidate Tests

## Why this source matters

This archive shows how to compose reusable agent roles without collapsing them into one generic prompt.
It also shows that safety and verification improve when the prompt is structured as an explicit contract instead of soft guidance.

## Candidate Doctrine examples

- **Plan-only branch**: a branch that can explore and draft but cannot edit any file except a dedicated plan artifact.
- **Explore subagent**: a search-focused role that only reads files and searches code, with no mutation tools.
- **Verification specialist**: a verification branch that must run commands and return a verdict based on observed results.
- **Security monitor**: a split prompt that combines context, threat model, and hard block/allow rules.

## Candidate diagnostics

- `INVALID_PLAN_MODE_WRITES_OUTSIDE_PLAN_FILE` for planning roles that can edit arbitrary files.
- `INVALID_EXPLORATION_MUTATION` for search-only roles that still expose write tools.
- `INVALID_VERIFICATION_WITHOUT_COMMANDS` for verification prompts that claim to test but do not require execution.
- `INVALID_SECURITY_POLICY_CONFLICT` for block/allow tables that overlap without a clear precedence rule.
