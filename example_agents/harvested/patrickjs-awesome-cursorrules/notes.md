# Notes

This source is mostly a catalog of many small rule packs. The Doctrine-relevant signal is not the repo's marketing copy; it is the way the repo packages local rules, scopes them by path, and pairs general guidance with narrow rule fragments.

The strongest pressure points are:

- root-level curation versus file-level rules
- path-scoped application with explicit glob metadata
- small, direct guardrails that are easy to turn into fail-loud Doctrine examples
- a mix of style guidance, test gates, and framework-specific exclusions

The selected files are intentionally diverse:

- the root README shows the catalog and naming pattern
- the Next.js package README shows how a package-level prompt file explains the stack and its shape
- the App Router rule shows a minimal scoped rule with an explicit directory boundary
- the FastAPI testing rule shows a narrow quality gate
- the early-return rule shows a style preference that can be tested as a soft rule rather than a hard semantic constraint

Keep the Doctrine interpretation generic. Do not carry the repo's framework names into Doctrine examples unless the example is specifically about scoping or specialization.
