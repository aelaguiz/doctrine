# Candidate Tests

## Source Summary

Harvest from a browser automation repo with strong command sequencing,
session persistence, auth recovery, and proxy/environment controls.

## High-Signal Patterns

- Pattern: navigate -> snapshot -> interact -> re-snapshot.
  Doctrine pull: a browser example that proves state must be refreshed after
  each DOM mutation or navigation.

- Pattern: reusable auth and session state.
  Doctrine pull: a portable-truth example where state save/load or session
  names carry browser identity across turns.

- Pattern: explicit command chaining for safe multi-step automation.
  Doctrine pull: a workflow that treats a batch of browser commands as one
  ordered contract instead of free-form prose.

- Pattern: proxy and bypass configuration.
  Doctrine pull: a policy surface for environment-sensitive browser behavior
  with explicit allow and bypass paths.

## Candidate Doctrine Examples

- Title: Snapshot-driven browser loop
  Main bucket: `commands_and_quality_gates`
  Likely surface: navigation, snapshot, interaction, and refresh discipline.

- Title: Auth state reuse
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: saved state, session restore, and repeated dashboard access.

- Title: Session isolation and persistence
  Main bucket: `context_and_memory`
  Likely surface: named sessions that keep cookies and storage separate.

- Title: Proxy-aware browser execution
  Main bucket: `negative_guardrails`
  Likely surface: proxy, bypass, and environment controls with fail-loud setup.

## Candidate Diagnostics

- Diagnostic idea: reject a browser workflow that keeps using stale refs after a
  navigation or DOM mutation.
- Diagnostic idea: reject a browser instruction that hides auth/session state
  behind prose instead of an explicit carrier or command.

## Keep Out

- Browser brand names or CLI trivia in the eventual Doctrine example text.
- Vague "just click around" instructions that do not encode the refresh loop.
