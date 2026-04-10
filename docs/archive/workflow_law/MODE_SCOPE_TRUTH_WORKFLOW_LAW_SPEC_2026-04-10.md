# Mode, Scope, And Truth Workflow Law Spec

> Historical note: this file is preserved as the original 2026-04-10 workflow-law
> design spec. For the live shipped reference, use
> [`../../WORKFLOW_LAW.md`](../../WORKFLOW_LAW.md).

Status: proposal

This document remains the original proposal/spec reference for the workflow-law
cutover. It is not the canonical shipped-language summary after implementation;
for shipped truth, use `doctrine/`, the active manifests, and the current docs
set under `docs/README.md`.

The v1 design is intentionally Doctrine-native:

- `workflow` remains the semantic home
- `output` remains the produced-contract primitive
- inheritance remains explicit ordered patching
- new surfaces only ship when they have compiler-owned meaning

The governing split for this feature family is:

- `law` decides what is true now
- `output` decides what the next owner must be able to read and trust

This document therefore treats Example 2 as a portable-truth model, not as a
second coordination language.

## Summary

Example 2 needs first-class language support for work that has:

- an explicit activation trigger
- one active mode per turn
- one current artifact per active branch, or explicitly no current artifact
- narrow write authority
- preserved truth outside the owned scope
- support-only comparison evidence
- rewrite-evidence deauthorization
- explicit invalidation when structural truth moves
- stop lines and explicit reroute

The smallest Doctrine-compatible v1 surface that supports that family is:

- a reserved `law:` child block inside `workflow`
- a reserved `trust_surface:` child block inside `output`
- `current artifact X via Output.field`
- `current none`
- `invalidate X via Output.field`
- `active when`
- `mode`
- `must`
- `when`
- `match`
- `own only`
- `preserve`
- `support_only`
- `ignore`
- `forbid`
- `stop`
- explicit `route "..." -> Agent`

Everything else proposed in the earlier draft is either explanatory or deferred.

## V1 Boundary

### Keep In V1

- `law` as a child of `workflow`
- `trust_surface` as a child of `output`
- `current artifact ... via ...`
- `current none`
- `active when`
- `mode`
- `must`
- `when`
- `match`
- `own only`
- `preserve exact`
- `preserve structure`
- `preserve decisions`
- `preserve mapping`
- `preserve vocabulary`
- `support_only ... for comparison`
- `ignore ... for truth`
- `ignore ... for comparison`
- `ignore ... for rewrite_evidence`
- `invalidate ... via ...`
- `forbid` over artifact or field scope
- `stop`
- explicit `route "..." -> Agent`
- named `law` subsections for reuse inside inherited workflows

### Defer From V1

- `obligation`
- `lens`
- `concern`
- `current status`
- nominal `artifact` typing as a language type
- basis roles beyond `truth`, `comparison`, and `rewrite_evidence`
- targetless `route`
- top-level reusable `law` declarations
- `let`
- any packet-like or free-floating coordination token model

## Goals

- Make exclusive mode-gated work explicit instead of smuggling it through prose.
- Make "one current artifact per active branch" a real language rule.
- Bind portable currentness to a declared downstream carrier instead of leaving
  proof ownership descriptive.
- Keep downstream trust on `output`, not in a shadow packet model.
- Make `own only` and preservation law strong enough to reject contradictory
  scope definitions.
- Make support-only comparison and rewrite-evidence exclusion explicit.
- Make invalidation a real truth transition rather than advisory prose.
- Keep emitted Markdown human-first and natural.
- Keep reuse aligned with Doctrine's existing explicit patching model.

## Non-Goals

- This spec does not define a packet primitive.
- This spec does not define a `status` declaration family.
- This spec does not define free-floating obligations or owed-now runtime
  tokens.
- This spec does not define a full expression language. `expr` remains a
  bounded host surface.
- This spec does not define a full `review` primitive.
- This spec does not widen route semantics beyond explicit labels and explicit
  targets.
- This spec does not require every semantic rule to be fully decidable at
  compile time. Some rules remain normative and example-proved until deeper
  analyzers exist.

## Portable Truth Model

### Artifact

In this document, "artifact" is explanatory vocabulary, not a new top-level
Doctrine primitive.

An artifact is any declared input or output that may be read, preserved,
invalidated, or named as current. In v1, the language surface only binds
currentness to declared `input` and `output` roots.

### Active Law Branch

An active law branch is the single path through:

- the `law` block
- any enclosing `active when`
- any nested `when`
- the selected `match` arm

that is currently in force for the turn.

Currentness, ownership, authority, and invalidation rules are evaluated per
active branch.

### Portable Currentness

Portable currentness is the combination of:

- one local statement that says what artifact is authoritative now, and
- one declared output field that carries that truth forward for the next owner

The v1 form is:

```prompt
current artifact PrimaryManifest via CoordinationHandoff.current_artifact
```

That one statement means both:

- `PrimaryManifest` is locally authoritative for the active branch, and
- `CoordinationHandoff.current_artifact` is the declared carrier that must tell
  the next owner that this is true

### Trust Carrier

A trust carrier is an addressable field on a declared `output` that is listed
in that output's `trust_surface`.

Trust carriers are how portable truth leaves the current turn.

### Basis Roles

V1 keeps only three basis roles:

- `truth`: what may decide what is current now
- `comparison`: what may guide comparison without becoming current truth
- `rewrite_evidence`: what may count as admissible old evidence during a
  rewrite pass

These roles are not synonyms. They exist so the language can say, for example,
that an artifact remains useful for comparison while no longer counting as
rewrite evidence.

### Invalidation

Invalidation is a first-class truth transition.

It does not delete an artifact.

It means:

- the artifact may still physically exist
- the artifact is no longer portable as current truth
- downstream owners must see that loss of authority on the declared trust
  carrier
- portability only returns when a later turn explicitly rebuilds or reissues
  currentness for that artifact

### Route-Only Work

Some turns do not have a current durable artifact. They only block, reroute, or
keep ownership honest.

The v1 form for that is:

```prompt
current none
```

`current none` is the only currentness form that does not require a carrier.

## Surface Overview

### `law` On `workflow`

`law` is a reserved child block inside `workflow`.

It coexists with ordinary authored prose and ordinary workflow sections.

```prompt
workflow MetadataPolish: "Metadata Polish"
    "Human-facing mission and tone still live here."

    law:
        ...
```

The prose outside `law` stays authored and natural.
The `law` block holds typed truth, scope, authority, invalidation, and reroute
semantics.

### `trust_surface` On `output`

`trust_surface` is a reserved child block inside `output`.

It names the output fields that a downstream owner must be able to read in
order to trust what is current now.

```prompt
output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    invalidations: "Invalidations"
        "Name any artifacts that are no longer current."

    trust_surface:
        current_artifact
        invalidations when invalidation_count > 0
```

`trust_surface` is the typed downstream-trust surface.
`standalone_read` remains the human-facing prose companion to it.

### No New Top-Level Declarations In V1

V1 does not add top-level `lens`, `obligation`, `concern`, `artifact`, or
`status` declarations.

This feature family stays attached to the surfaces Doctrine has already earned:

- `workflow`
- `output`
- `input`
- `enum`
- explicit inheritance and patching

## Grammar

This section is normative for the v1 surface described here.

### `law` Grammar

```ebnf
law_block             ::= "law" ":" NEWLINE INDENT law_item+ DEDENT

law_item              ::= law_stmt
                        | law_section
                        | law_inherit
                        | law_override_section

law_section           ::= CNAME ":" NEWLINE INDENT law_stmt+ DEDENT
law_inherit           ::= "inherit" CNAME NEWLINE
law_override_section  ::= "override" CNAME ":" NEWLINE INDENT law_stmt+ DEDENT

law_stmt              ::= active_when_stmt
                        | mode_stmt
                        | must_stmt
                        | current_artifact_stmt
                        | current_none_stmt
                        | own_only_stmt
                        | preserve_stmt
                        | support_only_stmt
                        | ignore_stmt
                        | invalidate_stmt
                        | forbid_stmt
                        | when_stmt
                        | match_stmt
                        | stop_stmt
                        | route_stmt

active_when_stmt      ::= "active when" expr
mode_stmt             ::= "mode" CNAME "=" expr "as" enum_ref
must_stmt             ::= "must" expr
current_artifact_stmt ::= "current artifact" artifact_ref "via" carrier_ref
current_none_stmt     ::= "current none"
own_only_stmt         ::= "own only" path_set_expr ["when" expr]
preserve_stmt         ::= "preserve" preserve_kind preserve_target ["except" path_set_expr] ["when" expr]
support_only_stmt     ::= "support_only" support_target "for" "comparison" ["when" expr]
ignore_stmt           ::= "ignore" ignore_target ["for" ignore_basis_list] ["when" expr]
invalidate_stmt       ::= "invalidate" artifact_ref "via" carrier_ref ["when" expr]
forbid_stmt           ::= "forbid" path_set_expr ["when" expr]
when_stmt             ::= "when" expr ":" NEWLINE INDENT law_stmt+ DEDENT
match_stmt            ::= "match" expr ":" NEWLINE INDENT match_case+ DEDENT
stop_stmt             ::= "stop" [string] ["when" expr]
route_stmt            ::= "route" string "->" agent_ref ["when" expr]

match_case            ::= match_head ":" NEWLINE INDENT law_stmt+ DEDENT
match_head            ::= expr | "else"

preserve_kind         ::= "exact"
                        | "structure"
                        | "decisions"
                        | "mapping"
                        | "vocabulary"

preserve_target       ::= artifact_ref | enum_ref | path_set_expr
support_target        ::= artifact_ref | path_set_expr
ignore_target         ::= artifact_ref | path_set_expr

path_set_expr         ::= path_expr
                        | "{" path_expr ("," path_expr)* "}"
                        | path_set_expr "except" path_set_expr

path_expr             ::= artifact_ref
                        | artifact_ref "." field_path
                        | artifact_ref ".*"

field_path            ::= CNAME ("." CNAME)*
carrier_ref           ::= output_ref "." field_path
artifact_ref          ::= name_ref
output_ref            ::= name_ref
enum_ref              ::= name_ref
agent_ref             ::= name_ref

ignore_basis_list     ::= ignore_basis ("," ignore_basis)*
ignore_basis          ::= "truth" | "comparison" | "rewrite_evidence"
```

### `trust_surface` Grammar

```ebnf
trust_surface_block   ::= "trust_surface" ":" NEWLINE INDENT trust_surface_item+ DEDENT
trust_surface_item    ::= field_path ["when" expr]
```

`trust_surface` items are relative to the current `output` declaration.
They point at already-declared output fields.

### Expression Surface

`expr` is intentionally not fully specified here.

This spec only relies on a small host expression surface that can represent:

- booleans
- strings
- integers
- enum members such as `MetadataPolishMode.section_summary`
- equality and inequality
- set membership
- boolean conjunction and disjunction
- bounded helper predicates such as `unclear(...)`

This document does not introduce a separate packet or status expression model.
Law expressions read from ordinary inputs, ordinary outputs, and host runtime
facts made available to the turn.

In the examples below, symbols such as `current_handoff` are shorthand for
host-available values derived from ordinary input contracts. They do not imply
a new packet or status declaration family.

## Addressability And Host Data

### Current Artifact Roots

`current artifact X via ...` is valid only when `X` resolves to a declared
`input` or `output`.

V1 does not allow:

- `current status`
- currentness rooted in enums
- currentness rooted in an undeclared artifact concept

### Law Paths

Law paths use member-style field syntax such as:

- `PrimaryManifest.title`
- `SectionMetadata.description`
- `SectionMetadata.*`

This is a law-expression surface.
It is intentionally separate from the readable `Decl:path.to.child` surface
already used elsewhere in Doctrine.

The separation is deliberate:

- readable refs are for authored mentions and interpolation
- law paths are for scope algebra and authority rules

### Carrier Refs

Carrier refs are output-field refs rooted at a declared `output`.

Examples:

- `CoordinationHandoff.current_artifact`
- `CoordinationHandoff.invalidations`
- `TrackerComment.current_artifact`

Carrier refs are only valid in:

- `current artifact ... via ...`
- `invalidate ... via ...`

### Trust Surface Items

Inside `output`, `trust_surface` items are relative field paths, not standalone
declarations.

In:

```prompt
output CoordinationHandoff: "Coordination Handoff"
    current_artifact: "Current Artifact"
        "Name what is current now."

    invalidations: "Invalidations"
        "Name what is no longer current."

    trust_surface:
        current_artifact
        invalidations
```

the `trust_surface` items point to existing output fields:

- `current_artifact`
- `invalidations`

### Imported Symbols

Imported `input`, `output`, `enum`, and `agent` declarations may be referenced
through qualified names in the same way other Doctrine declarations are
referenced.

## Output Coupling And Carrier Invariants

### `trust_surface` Is The Canonical Downstream Trust Surface

`trust_surface` is the typed place where an `output` says:

- what downstream truth it carries
- under what conditions that carried truth matters

This is the v1 replacement for descriptive "proof owner" prose.

### Carrier Invariants

If a workflow uses:

```prompt
current artifact PrimaryManifest via CoordinationHandoff.current_artifact
```

then all of the following must hold:

- `CoordinationHandoff` is a declared `output`
- `current_artifact` is an addressable field on `CoordinationHandoff`
- `current_artifact` is listed in `CoordinationHandoff.trust_surface`
- the concrete agent turn emits `CoordinationHandoff`
- if `PrimaryManifest` resolves to a declared `output`, the concrete agent turn
  also emits `PrimaryManifest`

If a workflow uses:

```prompt
invalidate SectionReview via CoordinationHandoff.invalidations
```

then all of the following must hold:

- `CoordinationHandoff` is a declared `output`
- `invalidations` is an addressable field on `CoordinationHandoff`
- `invalidations` is listed in `CoordinationHandoff.trust_surface`
- the concrete agent turn emits `CoordinationHandoff`

### Currentness And Output Coupling

A workflow that uses transferable currentness must emit a carrier that can say
what is current now.

That is a hard v1 rule.

If the current artifact resolves to a declared `output`, the concrete agent turn
must also emit that output.

Mode, preserve-basis, comparison-only, and rewrite-evidence details are also
part of downstream trust when they matter, but v1 treats those as a mix of:

- typed output design requirements
- render requirements
- example-backed normative law

Only current-artifact carriage and invalidation carriage are mandatory
compile-time carrier checks in v1.

## Operational Semantics

### Activation

`active when expr` gates whether the enclosing law branch applies.

If the expression is false:

- the gated branch is inactive
- statements inside it do not contribute currentness, scope, or invalidation
- that inactive branch does not need a current subject

If no `active when` is present, the law block is active whenever the workflow is
entered.

### `must`

`must expr` states a required invariant for the active branch.

It does not choose a branch.

Use:

- `active when`
- `when`
- `match`

for branching, and use `must` for hard requirements within the chosen branch.

Compile-time behavior:

- if the compiler can prove a `must` statement is false statically, compilation
  fails
- otherwise it remains a rendered hard requirement and a runtime-enforceable
  rule

### Modes

`mode name = expr as EnumRef` binds a typed exclusive mode selector.

Rules:

- the bound value must resolve to one member of the named enum
- a `match` over a typed mode must be exhaustive or include `else`
- mode selection may drive currentness, scope, invalidation, and reroute logic

### Currentness

Every active leaf branch must resolve to exactly one current-subject form:

- `current artifact X via Carrier.field`, or
- `current none`

Rules:

- two active `current artifact` statements in the same leaf branch are an error
- `current artifact` and `current none` in the same leaf branch are an error
- an active leaf branch with neither form is an error
- `current artifact` is the only v1 currentness form that carries portable
  truth
- `current none` is the only v1 form that omits `via`

`current none` is for route-only or block-only turns.

`current artifact` may bind either:

- a currently authoritative input artifact, or
- an output artifact produced by the current turn

### Ownership

`own only` defines the active branch write set.

Rules:

- `own only` paths must be addressable
- `own only` paths must be rooted in the current artifact
- the active write set is the union of active `own only` statements in the
  branch
- a path may not be both owned and forbidden in the same active branch

Examples:

- `own only PrimaryManifest.title`
- `own only {SectionMetadata.name, SectionMetadata.description}`
- `own only SectionMetadata`

### `forbid`

`forbid` is intentionally narrow in v1.

It forbids artifact or field scope, not free-floating semantic concerns.

Examples:

- `forbid SectionMetadata.taxonomy`
- `forbid {SectionMetadata.flags, SectionMetadata.taxonomy}`

Broader semantic-boundary labels are deferred with `concern`.

### Preservation

V1 keeps five preservation kinds.

#### `preserve exact`

The addressed target must remain value-identical.

Examples:

- `preserve exact PrimaryManifest.* except PrimaryManifest.title`
- `preserve exact {SectionMetadata.id, SectionMetadata.order}`

Rules:

- exact-preserved paths must be addressable
- overlap with owned scope is only valid if explicitly excluded through
  `except`

#### `preserve structure`

The addressed target's structural organization must remain stable.

Typical uses:

- heading families
- ordered sections
- route skeletons
- durable document shape

#### `preserve decisions`

The addressed upstream declaration remains authoritative for decisions the
current branch may not silently reopen.

Typical uses:

- approved plan
- approved structure
- locked route choice
- accepted burden or scope

#### `preserve mapping`

The addressed source-to-target mapping must remain aligned.

Typical uses:

- concept-to-slot maps
- route-to-output maps
- field-to-job maps

#### `preserve vocabulary`

The addressed vocabulary set must remain stable.

Typical uses:

- enum literals
- stable labels
- closed status words

#### Preservation Rules

- preserve targets must be addressable
- the compiler validates target existence and obvious kind mismatches where it
  can
- deeper semantic fit may remain normative in v1 and is therefore proved
  through examples

### Basis Roles

V1 keeps only three basis roles.

#### `truth`

`truth` is what may decide what is current now.

Currentness implicitly binds truth.

#### `comparison`

`comparison` is what may guide comparison without becoming current truth.

`support_only X for comparison` means:

- `X` may inform comparison
- `X` may not become truth merely by being present as comparison help

#### `rewrite_evidence`

`rewrite_evidence` is what may count as admissible old evidence during a
rewrite pass.

`ignore X for rewrite_evidence` means:

- `X` may still exist
- `X` may still be preserved
- `X` does not justify carry-forward wording during rewrite

#### Broad Ignore

`ignore X` with no `for` clause means:

- ignore `X` for `truth`
- ignore `X` for `comparison`
- ignore `X` for `rewrite_evidence`

#### Basis-Role Contradictions

The compiler must reject at least these contradictions:

- the same target is both `support_only ... for comparison` and `ignore ... for comparison` in the same active branch
- the current artifact target is ignored for `truth` in the same active branch

#### Downstream Readback

When comparison-only or rewrite-evidence distinctions matter downstream, the
carrier output should expose corresponding trust-surface fields.

That readback is normative in v1 and must be shown in the example corpus.

Only these readbacks are mandatory compile-time carrier checks in v1:

- current artifact
- invalidations

### Invalidation

`invalidate X via Carrier.field` is a truth transition.

It means:

- `X` is no longer eligible to bind as current after the invalidation takes
  effect
- `X` may still physically exist
- the invalidation must be expressed on the declared carrier
- portability only returns when a later turn explicitly rebuilds or reissues
  currentness for `X`

Rules:

- invalidation targets are declared `input` or `output` roots
- the carrier field must satisfy the same carrier invariants as currentness
- the current artifact may not also be invalidated in the same active branch

### Stop And Route

`stop` ends local specialist progress in the active branch.

By default, `stop` means:

- make no new in-scope durable edits after the stop line
- leave the handoff or output explicit
- transfer ownership only through an explicit `route`

`route` stays deliberately narrow in v1:

```prompt
route "Route the same issue back to Project Lead." -> ProjectLead
```

Rules:

- the label is required
- the target is required
- targetless route is out of scope for v1

### Law Reuse And Patching

`law` exists only as a child block of `workflow`.

Reuse happens only through named law subsections inside inherited workflows.

Example:

```prompt
workflow BaseMetadataPolish: "Metadata Polish"
    law:
        mode_selection:
            ...
        currentness:
            ...
        scope:
            ...
```

```prompt
workflow MetadataPolish[BaseMetadataPolish]: "Metadata Polish"
    law:
        inherit mode_selection
        override currentness:
            ...
        inherit scope
```

Rules:

- workflows with no parent may use either bare law statements or named law
  subsections
- inherited workflows that patch `law` must use named law subsections only
- each inherited named law subsection must be accounted for exactly once
- `inherit key` keeps the inherited subsection and places it exactly here
- `override key:` replaces the inherited subsection and places the replacement
  exactly here
- new named law subsections may be added directly
- bare law statements are not allowed in inherited law blocks because they have
  no patch identity
- law subsection keys are compiler identities and do not automatically render as
  human-facing headings

## Static Diagnostics

The compiler must reject at least these conditions.

- `law` appears outside `workflow`
- `trust_surface` appears outside `output`
- a `trust_surface` item does not resolve to a declared output field
- `current artifact` is missing `via`
- `current artifact` targets something other than a declared `input` or
  `output`
- a carrier ref root is not a declared `output`
- a carrier ref field does not exist
- a carrier ref field is not listed in the output's `trust_surface`
- the concrete agent turn does not emit the carrier output
- `current artifact` targets a declared `output` that the concrete agent turn
  does not emit
- an active leaf branch has more than one current-subject form
- an active leaf branch has no current-subject form
- `current none` appears with `current artifact` in the same active branch
- `current none` appears with `own only` paths in the same active branch
- a typed `match` is non-exhaustive and has no `else`
- a `mode` statement binds a value outside the referenced enum
- an `own only` path is not addressable
- an `own only` path is not rooted in the current artifact
- an owned path overlaps an exact-preserved path without explicit exclusion
- a path is both owned and forbidden in the same active branch
- the same target is both `support_only ... for comparison` and `ignore ... for comparison` in the same active branch
- the current artifact target is ignored for `truth`
- `invalidate` is missing `via`
- an invalidation carrier field does not satisfy the carrier invariants
- the current artifact is invalidated in the same active branch
- `route` omits its label
- `route` omits its target
- an inherited law block overrides an unknown subsection
- an inherited law block accounts for the same parent subsection more than once
- an inherited law block omits a parent subsection
- an inherited law block mixes patching with bare law statements

## Render Semantics

The renderer must stay human-first.

It must not dump the AST directly.

### Workflow Law Rendering

Resolved law should render in a stable semantic order:

1. Activation
2. Current Mode
3. Current Artifact Or Explicit No-Current State
4. Owned Scope
5. Preserved Truth
6. Comparison-Only Evidence
7. Ignored Or Deauthorized Evidence
8. Forbidden Scope
9. Invalidations
10. Stop Line And Route

The renderer may reorganize internal law subsection ordering to achieve that
readability, but it must not silently drop active meaning.

### Law Section Keys

Named law subsection keys are compiler identities.

They do not automatically render as headings.

They exist so inherited workflows can patch law explicitly and fail loudly.

### `trust_surface` Rendering

`trust_surface` should render as part of the output contract, using authored
field titles rather than raw keys whenever titles exist.

It should read like a downstream pickup contract, not like a debugging dump.

### Basis-Role Rendering

The renderer must make basis-role distinctions explicit in plain English.

Examples:

- support-only comparison artifacts should read as subordinate comparison help,
  not as current truth
- rewrite-evidence exclusions should read as "the old value does not count as
  rewrite evidence"
- invalidations should read as "this is no longer current"

## Canonical V1 Example

This example is intentionally generic.
It shows the frozen v1 split:

- `law` decides local truth
- `output` declares the downstream trust carrier

### Shared Declarations

```prompt
enum MetadataPolishMode: "Metadata Polish Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"


enum RewriteRegime: "Rewrite Regime"
    carry_forward: "carry-forward"
    rewrite: "rewrite"


input ApprovedPlan: "Approved Plan"
    source: File
        path: "unit_root/_authoring/APPROVED_PLAN.md"
    shape: MarkdownDocument
    requirement: Required


input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
    shape: MarkdownDocument
    requirement: Required


input AcceptedPeerSet: "Accepted Peer Set"
    source: File
        path: "catalog/accepted_peers.json"
    shape: JsonObject
    requirement: Advisory


output PrimaryManifest: "Primary Manifest"
    target: File
        path: "unit_root/_authoring/primary_manifest.json"
    shape: JsonObject
    requirement: Required


output SectionMetadata: "Section Metadata"
    target: File
        path: "unit_root/_authoring/section_metadata.json"
    shape: JsonObject
    requirement: Required


output SectionReview: "Section Review"
    target: File
        path: "unit_root/_authoring/SECTION_REVIEW.md"
    shape: MarkdownDocument
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    active_mode: "Active Mode"
        "Name the one active mode for this pass."

    preserve_basis: "Preserve Basis"
        "Name the upstream declaration whose decisions remain authoritative."

    comparison_basis: "Comparison Basis"
        "Name any comparison-only artifacts used in this pass."

    rewrite_exclusions: "Rewrite Evidence Exclusions"
        "Name any fields whose old values do not count as rewrite evidence."

    invalidations: "Invalidations"
        "Name any artifacts that are no longer current."

    trust_surface:
        current_artifact
        active_mode
        preserve_basis
        comparison_basis when peer_comparison_used
        rewrite_exclusions when current_handoff.rewrite_regime == RewriteRegime.rewrite
        invalidations when current_handoff.structure_changed

    standalone_read:
        "A downstream owner must be able to read this output alone and know what is current now, why it is current, and what no longer counts as current."


agent RoutingOwner:
    role: "Own explicit reroutes when the current specialist cannot continue."
```

### Base Workflow

For brevity, this example assumes a host binding named `current_handoff`
populated from an ordinary input contract. That binding is illustrative only.

```prompt
workflow BaseMetadataPolish: "Metadata Polish"
    "Handle the last narrow wording pass after structure is already locked."

    law:
        activation:
            active when current_handoff.owes_metadata_polish

        mode_selection:
            mode pass_mode = current_handoff.active_mode as MetadataPolishMode

        currentness:
            match pass_mode:
                MetadataPolishMode.manifest_title:
                    current artifact PrimaryManifest via CoordinationHandoff.current_artifact
                    must current_handoff.preserve_basis == ApprovedPlan

                MetadataPolishMode.section_summary:
                    current artifact SectionMetadata via CoordinationHandoff.current_artifact
                    must current_handoff.preserve_basis == ApprovedStructure

        scope:
            match pass_mode:
                MetadataPolishMode.manifest_title:
                    own only PrimaryManifest.title
                    preserve exact PrimaryManifest.* except PrimaryManifest.title
                    preserve decisions ApprovedPlan

                MetadataPolishMode.section_summary:
                    own only {SectionMetadata.name, SectionMetadata.description}
                    preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
                    preserve decisions ApprovedStructure
                    forbid {SectionMetadata.taxonomy, SectionMetadata.flags}

        evidence:
            support_only AcceptedPeerSet for comparison

        stop_lines:
            when unclear(pass_mode, current_handoff.preserve_basis):
                stop "Mode or preserve basis is unclear."
                route "Route the same issue back to Routing Owner." -> RoutingOwner
```

### Rewrite-Aware Child Workflow

```prompt
workflow RewriteAwareMetadataPolish[BaseMetadataPolish]: "Metadata Polish"
    law:
        inherit activation
        inherit mode_selection
        inherit currentness
        inherit scope

        override evidence:
            support_only AcceptedPeerSet for comparison

            ignore PrimaryManifest.title for rewrite_evidence when pass_mode == MetadataPolishMode.manifest_title and current_handoff.rewrite_regime == RewriteRegime.rewrite

            ignore {SectionMetadata.name, SectionMetadata.description} for rewrite_evidence when pass_mode == MetadataPolishMode.section_summary and current_handoff.rewrite_regime == RewriteRegime.rewrite

        override stop_lines:
            when current_handoff.structure_changed:
                invalidate SectionReview via CoordinationHandoff.invalidations
                stop "Structure moved; downstream review is no longer current."
                route "Route the same issue back to Routing Owner for rebuild." -> RoutingOwner

            when unclear(pass_mode, current_handoff.preserve_basis):
                stop "Mode or preserve basis is unclear."
                route "Route the same issue back to Routing Owner." -> RoutingOwner
```

### Intended Render

```md
## Metadata Polish

Handle the last narrow wording pass after structure is already locked.

This pass runs only when metadata polish is owed now.

Work in exactly one mode:
- manifest-title
- section-summary

If mode is manifest-title:
- Current artifact: Primary Manifest.
- The coordination handoff must name that current artifact.
- Own only `title`.
- Preserve every other manifest field exactly.
- Preserve the decisions already owned by Approved Plan.

If mode is section-summary:
- Current artifact: Section Metadata.
- The coordination handoff must name that current artifact.
- Own only `name` and `description`.
- Preserve every other metadata field exactly.
- Preserve the decisions already owned by Approved Structure.
- Do not widen into `taxonomy` or `flags`.

Accepted Peer Set is comparison-only support.

On rewrite passes, the old title or summary wording does not count as rewrite evidence.

If structure changed, Section Review is no longer current. The coordination handoff must say so.

If mode or preserve basis is unclear, stop and route the same issue back to Routing Owner.
```

## Live Review Corpus

At proposal time, the shipped corpus still stopped at `examples/29_enums`.

The workflow-law review corpus for this proposal lived under `examples/30_*`
through
`examples/38_*`.

Those live example directories are now the source of truth for:

- prompt authoring
- manifest-backed proof shape
- expected renders under `ref/` and `build_ref/`
- negative case naming and staging

This spec no longer duplicates per-example requirements here. When the review
corpus changes, update the live examples and `examples/README.md` instead of
adding another planning layer to this document.

Use the live corpus for navigation:

| Example | Review Focus |
| --- | --- |
| `30_law_route_only_turns` | `law`, `current none`, `stop`, explicit `route`, nested `when` |
| `31_currentness_and_trust_surface` | `trust_surface`, `current artifact ... via ...`, carrier invariants |
| `32_modes_and_match` | `active when`, `mode`, typed `match`, `must` |
| `33_scope_and_exact_preservation` | `own only`, `preserve exact`, `preserve decisions`, `forbid` |
| `34_structure_mapping_and_vocabulary_preservation` | `preserve structure`, `preserve mapping`, `preserve vocabulary` |
| `35_basis_roles_and_rewrite_evidence` | `support_only ... for comparison`, `ignore ... for rewrite_evidence`, `ignore ... for truth` |
| `36_invalidation_and_rebuild` | `invalidate ... via ...`, invalidation as a truth transition |
| `37_law_reuse_and_patching` | named law subsections, `inherit`, `override` for `law` |
| `38_metadata_polish_capstone` | integrated portable-truth model across all v1 surfaces |

## Future Re-Entry Criteria For Deferred Features

The deferred features may return later, but only if they strengthen the same
portable-truth model.

### `obligation`

Future home:
typed coordination state carried by declared `output` or future `status`
surfaces.

Re-entry bar:
it must not be a free-floating runtime token.

### `lens`

Future home:
patchable reusable scope-policy blocks under the same explicit inheritance model
as other Doctrine surfaces.

Re-entry bar:
it must beat inline `own only` plus `preserve` in at least two generic examples
or gain a clear Doctrine-style patching story.

### `concern`

Future home:
analyzable semantic grouping metadata with real membership rules.

Re-entry bar:
it must have something like `covers` so the compiler can reason about overlap.

### `current status`

Future home:
a real `status` declaration family with addressing, typing, rendering, and
patching semantics.

Re-entry bar:
status must become a true Doctrine declaration family, not descriptive prose.

### Widened Basis Roles

Future home:
only after each added role has distinct diagnostics, render obligations, and
trust-surface consequences.

### Targetless `route`

Future home:
only if a future route model proves that the gain is generic and worth the added
context magic.

## Remaining Specification Work

After the freeze decisions in the audit and the revisions in this document, the
remaining work is packaging rather than semantic discovery:

- wire the parser and compiler to this frozen v1 surface
- add the exact compiler diagnostic catalog entries and wording
- author the example corpus from `30_*` upward
- keep the examples, docs, and implementation aligned as the surface lands

The open design stance is now stable:

- `law` determines truth locally
- `current artifact ... via ...` binds that truth to a declared carrier
- `output.trust_surface` declares what downstream trust requires
- `invalidate ... via ...` can revoke that portability
- deferred features only return if they strengthen that same model
