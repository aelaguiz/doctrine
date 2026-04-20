# Scalar Host Slot Family — Feature Request

**Date:** 2026-04-20
**Requester:** Rally (sibling repo consuming Doctrine `skill package` authoring)
**Status:** Draft feature request — WHY and WHAT only, not HOW
**Related:**
- `DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` (P3 `receipt` family shipped the precedent pattern of widening the host-slot family enum)
- Rally's `RALLY_DOCTRINE_V5_ADOPTION_AUDIT_2026-04-19.md` (forward-finding F-6, three concrete skill sites)

## How to read this document

This is a **feature request**, not a design proposal.

- **Why it bites** — the cost of not having the feature, observed in real consumer code.
- **What authors need to express** — the shape of the expressiveness at the language-user level.
- **Use cases** — concrete Rally skill packages that demonstrate the gap.
- **Non-goals** — what this request is deliberately not asking for.

I deliberately do not prescribe implementation — grammar, error codes, validator wiring, contract-sidecar shape, and family-enum layout are Doctrine-team territory. The goal here is to make the *problem* legible so Doctrine can decide how (and whether) to close it.

---

## Context: what `host_contract:` covers today

Doctrine's shipped `host_contract:` surface lets a fat `skill package` declare typed slots that its consuming agent must bind. The shipped family enum is closed: `input`, `output`, `document`, `analysis`, `schema`, `table`, `final_output`, `receipt`. Each family names a Doctrine-typed authored entity — a declared input, an emitted output shape, a produced document, a review analysis, a JSON schema, a tabular result, a final-output carrier, or (as of P3) a receipt carrier.

In every shipped family, the slot's *value* at runtime is an addressable Doctrine artifact the agent already authored somewhere else. The consuming `bind:` line wires one Doctrine symbol to another Doctrine symbol, and the compiler checks the shapes match.

That covers "share my typed Doctrine artifacts with the fat skill package." It does not cover a different and common case: "the skill package needs a plain string, path, or identifier that only the host runtime knows, and that the agent never authored as a Doctrine artifact."

## The gap — plain-English host facts have no family

Real consumer skills need to reference host-owned **scalars** that never exist as `input`, `output`, `document`, `analysis`, `schema`, `table`, `final_output`, or `receipt`. These are runtime facts the host injects at install time: env-var values, installed tool paths, stable workspace identifiers, CLI binary locations, fixed on-disk subtrees.

None of these are Doctrine artifacts. None of them fit a shipped family. Authors today have three bad options:

1. **Hard-code the literal into the skill prompt.** The literal drifts when the host changes the variable name or path. The compiler cannot catch it, because nothing typed it.
2. **Write prose that names the env var and hope the runtime sets it.** This is what Rally does today in three places. The prose restates what the host README already says. The compiler does not enforce that the host actually provides the value.
3. **Invent a synthetic "fake input" just to force a family match.** This misuses the `input` family for a value that is not a Doctrine input, bloats emitted contracts, and still drifts because the host never actually supplies a typed input for it.

Rally chose option (2) and left three `TODO(doctrine F-6)` markers in production skill sources. That debt is two days old and has nowhere upstream to land.

## Why it bites

### Prose drift between skill prompt and runtime

When a skill prompt says *"use `$RALLY_CLI_BIN` to invoke the Rally CLI"*, nothing in Doctrine checks that `RALLY_CLI_BIN` is the real variable the host sets. If Rally renames the variable, the skill prompt says one thing and the runtime says another. The compiler cannot flag the drift because the variable is a string inside a prose bullet, not a typed symbol.

### No compile-time host-binding enforcement

The whole point of `host_contract:` is that the consuming agent must bind every declared slot exactly once, and the compiler fails loud when a slot is missing. For Doctrine-authored artifacts that guarantee already exists. For plain host scalars it does not — and these are exactly the values where drift bites hardest, because they are produced entirely outside the Doctrine prompt graph.

### Downstream prompts cannot interpolate through a typed symbol

`host_contract:` slots today support `{{host:slot}}` interpolation inside the package body and inside emitted companion docs. Scalar host facts would benefit from the same interpolation shape: one declared symbol, many references, one authoritative source. Without a family for them, authors cannot use the existing interpolation path — they fall back to typing the literal variable name in every prose bullet that needs it.

### Teaching gap

The authoring guide (`SKILL_PACKAGE_AUTHORING.md`) tells authors to use `host_contract:` when a package needs "typed host facts from its consuming agent." Authors naturally reach for `host_contract:` when their skill needs a host-owned CLI path or env-var value, hit the closed family list, and have no path forward. The feature as shipped advertises more coverage than it actually provides.

## What authors need to express

At the language-user level, authors want to declare that their package depends on a **named, host-supplied scalar fact** — a path, an identifier, a CLI invocation target, an env-var value — and reference that fact by typed symbol from inside the package body and emitted companion docs. Concretely:

- The package declares each scalar host fact once, with a symbol name and a short description of what the host must supply.
- The consuming agent (or the runtime wiring at the boundary, wherever Doctrine decides scalar binding should live) supplies the concrete value for each declared scalar.
- Anywhere the package body or its emitted companions want to reference the value, they go through the typed host symbol rather than repeating the raw literal.
- The compiler fails loud when a declared scalar is not supplied, or when the package references an undeclared scalar symbol.

That is the minimum shape authors actually need. Whether the family is one broad bucket or split by sub-kind (path vs identifier vs env-var name vs arbitrary string), whether binding happens at the consuming skill entry or at a runtime-level boundary, and whether the contract sidecar grows a new section are Doctrine-team calls.

## Use cases — Rally evidence

Rally has three live skills carrying `TODO(doctrine F-6)` markers today. All three sit in `rally/skills/*/prompts/SKILL.prompt`. Each one demonstrates the same gap from a slightly different angle.

### RallyKernel (`rally/skills/rally-kernel/prompts/SKILL.prompt`)

This skill teaches an agent how to invoke the Rally CLI. Its prompt bullets reference three host-supplied scalars:

- the path to the Rally CLI binary (a filesystem path the host runtime resolves at install time)
- the active Rally run id (a short string identifier stable across one run)
- the active workspace root (a filesystem path specific to the host)

None of these are Doctrine-authored artifacts. None of them are inputs, outputs, documents, analyses, schemas, tables, final outputs, or receipts. All three are plain strings the Rally runtime owns. The current prompt spells each one as a prose bullet referencing the raw env-var name, and the prompt drifts silently when Rally renames the variable.

### RallyMemory (`rally/skills/rally-memory/prompts/SKILL.prompt`)

This skill teaches an agent how to read and write persistent memory through a Rally subcommand. It needs:

- the Rally CLI binary path (same scalar as RallyKernel — a real reuse case)
- the active run id (same scalar as RallyKernel)
- a per-agent identifier so memory writes route to the right agent bucket

Two of the three scalars are shared with RallyKernel. One is unique to this skill. A typed host family would let both skills reference the shared scalars through one declared symbol rather than copying raw variable names into two prose blocks, and would let the per-agent identifier carry its own typed declaration that the runtime must bind exactly once.

### DemoGitSkill (`rally/skills/demo-git/prompts/SKILL.prompt`)

This skill operates on a fixed subtree inside the Rally run home — `home:repos/demo_repo`. The path is host-supplied (the Rally run home is only known at runtime) but is not a Doctrine artifact. Today it appears as a literal `home:` reference inside the prompt. The gap here is slightly different in flavor — the value is a stable subpath rather than an env-var — but the underlying need is the same: a typed symbol the skill can reference, backed by a compiler guarantee that the host actually supplies it.

## Why it matters beyond Rally

The pattern is general. Any fat skill package that wraps a host-owned tool, a host-owned filesystem convention, or a host-owned identifier format will hit this. Skills that wrap a database connection URL, an OAuth-provider base URL, a per-deployment feature flag, or a stable home-directory layout all describe the same shape: host-owned scalar, referenced by typed symbol, bound once at the boundary, enforced at compile time.

Doctrine already decided in P3 that the `receipt` carrier deserved first-class family membership rather than being shoehorned into the `document` family. That decision treated "widening the family enum consciously" as the right way to grow `host_contract:`. A scalar family would be the same kind of conscious widening for a different typed shape.

## Adjacent / peer patterns to consider (author-POV only)

- **P3 receipt family.** The precedent for widening the closed family enum when a new typed shape earns its own slot. The scalar family would be the same move for scalar host facts.
- **`skills:` `bind:` and existing `host_contract:` binding enforcement.** Authors already expect "declare once, bind once, fail loud on missing binds." A scalar family should feel like the same shape from the author's seat.
- **`{{host:slot}}` interpolation.** Authors already know how to reference a host slot inside a package body and inside emitted companions. A scalar family should reuse that interpolation shape so authors do not learn a new reference form.

## Non-goals

- **Not a general runtime-config mechanism.** This is not a request to expose arbitrary runtime state, arbitrary typed records, or an arbitrary configuration object through `host_contract:`. Scalars only.
- **Not a change to shipped family behavior.** The existing `input`, `output`, `document`, `analysis`, `schema`, `table`, `final_output`, and `receipt` families should keep their current semantics unchanged. A scalar family would be additive.
- **Not a prescription for a specific binding site.** Whether scalar binding lives at the consuming skill entry (like today's `host_contract:` binds) or at a different runtime boundary is a Doctrine-team call. Authors just need the symbol to be compiler-enforced wherever binding lands.
- **Not a request for type-checking scalar values themselves.** Asking Doctrine to validate that a path exists, an identifier matches a regex, or an env-var value has a specific format is out of scope. The request is for typed symbolic reference and enforced binding, not for value validation.
- **Not a syntax proposal.** I avoid proposing a keyword, a family name, a reserved token, or a block shape. Doctrine should pick the authoring shape that fits its grammar and contract-sidecar model.

## What Rally will do when this lands

Close forward-finding F-6 in `RALLY_DOCTRINE_V5_ADOPTION_AUDIT_2026-04-19.md` by:

- Declaring host scalars once on each affected `skill package` (RallyKernel, RallyMemory, DemoGitSkill).
- Replacing the three `TODO(doctrine F-6)` markers with real typed references.
- Removing the raw env-var literals and path literals from skill prose bullets.
- Letting the Doctrine compiler enforce that Rally's runtime actually supplies every scalar a shipped skill declares.

Rally is happy to be the first downstream consumer and provide feedback on the shipped shape.
