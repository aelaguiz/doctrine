# Candidate Tests

## Source Summary

Harvest from a skill-pack repo with generated AGENTS docs, rule catalogs, and
specialized markdown guidance for React, React Native, view transitions, and
composition.

## High-Signal Patterns

- Pattern: generated compiled docs from rule sources.
  Doctrine pull: an example that distinguishes source rule files from a derived
  canonical instruction artifact.

- Pattern: rule catalogs with category and prefix metadata.
  Doctrine pull: a structured example where rule families are grouped by
  priority and surface, not just listed as prose.

- Pattern: view-transition ordering and support constraints.
  Doctrine pull: a workflow that treats motion semantics as a typed contract
  with browser support limits.

- Pattern: composition patterns for explicit variants and compound components.
  Doctrine pull: a design-system example that encodes state, variants, and
  children composition as reusable instructions.

## Candidate Doctrine Examples

- Title: Generated skill pack
  Main bucket: `commands_and_quality_gates`
  Likely surface: build, validate, and extract commands with generated output.

- Title: React performance rule catalog
  Main bucket: `skills_tools_and_capabilities`
  Likely surface: a large markdown catalog with categories, prefixes, and
  optimized patterns.

- Title: View transition workflow
  Main bucket: `domain_specific_constraints`
  Likely surface: ordered motion semantics, browser support, and trigger types.

- Title: Composition pattern guide
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: compound components, state injection, and explicit variants.

## Candidate Diagnostics

- Diagnostic idea: reject a package where source rule files and compiled
  AGENTS output disagree.
- Diagnostic idea: reject a view-transition guide that collapses trigger types
  or support constraints into vague animation advice.

## Keep Out

- React package names or product-specific slogans in the eventual Doctrine text.
- Any example that depends on the full generated catalog instead of one rule
  family at a time.
