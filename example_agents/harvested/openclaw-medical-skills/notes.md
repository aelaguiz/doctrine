# Notes

This source is the strongest of the four for skills and guardrails. The README explains how skills are loaded and scoped, while the selected skill modules show explicit invocation rules, required MCP connectors, allowed-tools lists, and narrow output packages.

The most useful files are the prior authorization skill and the FHIR developer skill. The prior auth skill gives a staged workflow with required connectors, waypoint outputs, and a strict vs lenient decision rubric. The FHIR skill gives typed resource validation, cardinality-based required fields, enum constraints, and exact HTTP status choices. The search strategy skill adds source-specific query decomposition, and the scientific brainstorming skill shows a structured but conversational agent mode.

Selected artifacts:
- `raw/README.md`
- `raw/skills/prior-auth-review-skill/SKILL.md`
- `raw/skills/fhir-developer-skill/SKILL.md`
- `raw/skills/search-strategy/SKILL.md`
- `raw/skills/scientific-brainstorming/SKILL.md`
