# Candidate Tests

## Good Doctrine Pressures

| Source signal | Doctrine example or diagnostic idea | Why it matters |
| --- | --- | --- |
| Universal security principles | Example of an `alwaysApply` rule that governs all generated code | Tests global guardrail semantics |
| Unsafe input to sensitive operations | Diagnostic for file paths, shell calls, and database queries that consume user input | Good fit for fail-loud negative examples |
| MCP approval gate | Example that blocks autonomous tool execution until explicit user approval | Pressures tool-use surfaces and delegation limits |
| Dangerous flow tracing | Example or diagnostic that follows tainted input across multiple steps | Useful for path-sensitive reasoning examples |
| Python-specific unsafe APIs | Example of a language-scoped security rule pack with concrete banned operations | Tests scoped restrictions and language-specific surfaces |

## Proposed Doctrine Example Ideas

1. Global guardrail example.
   - Model a universal security rule that applies to every file and forbids direct use of untrusted input in sensitive operations.

2. MCP approval diagnostic.
   - Add a failure for autonomous tool execution or file modification triggered solely by MCP output.

3. Dangerous-flow chain example.
   - Trace user input through a helper function into a shell or file sink and show the exact point where the rule is violated.

4. Language-scoped security rule.
   - Use a Python-only rule file to test whether Doctrine can scope a security constraint to a single language family.

5. Secrets-in-output diagnostic.
   - Reject code or examples that leak tokens, credentials, or PII in logs, frontend output, or generated text.

## Keep Out

- Do not turn the pack into a general code-style example.
- Do not describe these rules as optional preferences; their value is in the hard stop behavior.
- Do not import the repo's own tone or emojis into Doctrine tests.
