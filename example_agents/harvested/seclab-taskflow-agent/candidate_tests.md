# Candidate Tests

## Source Summary

The Taskflow Agent repo is best used for Doctrine pressure where we need staged workflow execution, explicit reuse, and hard guardrails. It also gives us a clean place to study how input variables, environment variables, and toolboxes are surfaced without making the prompt itself do all the work.

## High-Signal Patterns

- Pattern: `must_complete`, `headless`, `blocked_tools`, `repeat_prompt`, `uses`, and `inputs` all live in the same grammar.
  Doctrine pull: examples that need strongly typed workflow surfaces and explicit turn-by-turn state.

- Pattern: security prompts ask for evidence, not speculation.
  Doctrine pull: fail-loud examples where the agent must stay within declared proof and stop conditions.

- Pattern: reusable taskflows can be overridden without rewriting the entire workflow.
  Doctrine pull: inheritance and patching examples with explicit local changes.

## Candidate Doctrine Examples

- Title: Security triage with memory-backed notes
  Main bucket: `orchestration_roles_and_delegation`
  Likely surface: a multi-turn workflow with a route-only or stop-and-reroute branch plus a carry-forward note artifact.
  Why this stays generic: keep the security context abstract and focus on staged analysis and memory reuse.

- Title: Comprehensive taskflow grammar
  Main bucket: `commands_and_quality_gates`
  Likely surface: a feature-complete grammar example showing inputs, env, repeat_prompt, blocked tools, and reusable prompts.
  Why this stays generic: it should become a Doctrine grammar-pressure example, not a GitHub-specific security workflow.

- Title: Reusable taskflow override
  Main bucket: `scope_hierarchy`
  Likely surface: a parent workflow with a child override that only changes one field.
  Why this stays generic: the value is the override behavior, not the upstream repository naming.

- Title: Evidence-only code review
  Main bucket: `negative_guardrails`
  Likely surface: a compile or review example that rejects speculation and forces code-backed claims.
  Why this stays generic: keep the security specifics as a concrete domain example but extract the no-speculation rule itself.

## Candidate Diagnostics

- Diagnostic idea: a task references `inputs.foo` without declaring `foo`.
  Failure to prove: workflow variables must be declared before they can be interpolated.

- Diagnostic idea: a reusable taskflow override drops a required field from the parent workflow.
  Failure to prove: inheritance should not silently weaken required task behavior.

- Diagnostic idea: a security review prompt asks for analysis but does not provide a proof artifact or stop condition.
  Failure to prove: security review examples should fail loud when they overpromise output without a contract.

## Keep Out

- Security-lab naming and repository-specific MCP labels unless the candidate test is explicitly about them.
- Free-floating prose about vulnerability classes that cannot be tied back to an explicit taskflow artifact.
