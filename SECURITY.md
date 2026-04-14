# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.x stable line | Yes |
| Older tags and unreleased snapshots | No |

Security fixes, if issued, should be expected on the latest supported 1.x line.
Older snapshots, generated artifacts, and local forks are not maintained as
supported release lines.

## Reporting a vulnerability

For non-security questions or bug reports, use [SUPPORT.md](SUPPORT.md).

Do not open a public issue with exploit details.

Use GitHub private vulnerability reporting for this repo.
Open the Security tab, then use the private report flow.

If that GitHub path is unavailable, open a minimal public issue that asks for a
private contact path and keep the report details out of the issue body.

Please include enough detail for a fast triage. We will confirm receipt,
reproduce the issue, and keep the report private until we have a fix plan.

Include:

- affected file, surface, or command
- impact and expected severity
- clear reproduction steps
- any known workaround or mitigation

## Scope

This policy covers the shipped Python package in `doctrine/`, the verified
example corpus, and the VS Code extension under `editors/vscode/`.
