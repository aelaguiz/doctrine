# Notes

This source is a concentrated guardrail pack. It is less about workflow coordination and more about fail-loud security constraints that should apply to generated code and agent actions.

The main Doctrine pressure points are:

- explicit negative rules that say what must not happen
- universal guardrails versus file-scoped rules
- specialized safety constraints for MCP, Python, and dangerous data flows
- guidance that requires an explanation when a rule is violated

The selected files cover:

- a general README that frames the pack as a security baseline
- universal principles that apply to all generated code
- MCP-specific restrictions on tool use and sensitive data
- a dangerous-flow guide that traces untrusted input to a sink
- a Python-specific file with concrete unsafe APIs and secret-handling rules

Keep the Doctrine reading generic. The exact language stack is less important than the shape of the constraints: untrusted input, unsafe sinks, and explicit approval gates.
