This revision answers the open review questions as **hard spec decisions**.
It does not trim the feature back to a pattern or a deferred sketch. It treats
the recurring critic bundle as a real Layer 1 surface: blocked review turns,
shared review-contract evaluation, exact failing-gate identity, portable
currentness when the review output is trusted downstream, carried mode /
trigger state, deterministic outcome routing, and explicit
semantic-to-output coupling. [Resolved decisions note](sandbox:/mnt/data/Pasted%20text%283%29.txt)

The design still stays Doctrine-native:

* `workflow` remains the general semantic home for producer / coordinator law
* `review` becomes the semantic home for critic / reviewer law
* `output` remains the produced-contract primitive
* review outputs remain declared `output`s
* currentness reuses the existing `current artifact ... via Output.field` rule
* reuse still follows explicit ordered patching
* no packet side channel, route payload, or shadow trust carrier is introduced

## Full `review` support spec

### 1. Status and layer

`review` is a **new top-level Doctrine declaration** and a **new reserved agent
authored slot**.

It is not a workflow alias. It is not a standard-library convention. It is a
first-class language surface for reviewer / critic turns.

This is the layer decision:

* `workflow` remains the semantic home for producer / coordinator law
* `review` is the semantic home for reviewer / critic law
* `output` remains the only produced-contract primitive
* `trust_surface` remains the typed downstream-trust surface for current truth and carried review state
* no packet, obligation token, or route payload primitive is introduced just to make review work

### 2. Governing split

The review feature family is governed by this split:

* `review` decides **what was reviewed, what failed, what passed, what remains current, and who owns next**
* `output` decides **what the next owner must be able to read and trust from that review**

That keeps the same Doctrine-native split already earned by workflow law:
typed local semantics in the authored surface, typed downstream readability on
`output`.

### 3. What review support must solve

A complete review surface must be able to express:

* one reviewed subject or one reviewed subject family
* one referenced shared review contract
* handoff-first block gates
* ordinary reject gates
* one accept gate
* preserved truth that the reviewer must confirm stayed intact
* assertion-style review checks such as `preserve`, `support_only`, and `ignore`
* exact outcome routing on accept and reject
* typed downstream carried mode / trigger state when multiple branches go to the same next owner
* portable currentness when the review output is supposed to tell the next owner what artifact is current now
* exact coupling between semantic verdict / route / currentness and declared output fields
* exact exported contract gate identity, not just contract pass / fail
* inheritance and patching with the same explicit Doctrine model already used elsewhere

---

## 4. Surface model

### 4.1 New declaration

```prompt
abstract review BaseReview: "Title"
```

```prompt
review Name: "Title"
```

Inherited forms:

```prompt
abstract review ChildBase[ParentBase]: "Title"
```

```prompt
review ChildReview[BaseReview]: "Title"
```

### 4.2 New agent slot

A concrete agent may define:

```prompt
review: SomeReview
```

An agent may **not** define both `workflow:` and `review:` in the same
concrete declaration. Other authored slots are still allowed: `role`,
`read_first`, `inputs`, `outputs`, `skills`, and other already-earned authored
slots. The review body renders where the main semantic body would otherwise
render.

An `abstract review` may not be attached directly to a concrete agent.

### 4.3 Review-contract workflows

`contract:` may reference only a top-level named `workflow` that compiles as a
**review-contract workflow**.

A review-contract workflow is a restricted workflow profile:

* it may contain ordinary preamble prose
* it may contain first-level keyed titled sections
* it may inherit and compose other workflows through ordinary Doctrine rules
* it may **not** contain operational `route`, `current`, `invalidate`, or `carry` semantics

Its exported contract gates are the **first-level keyed workflow section
identities after inheritance/composition flattening**.

So:

```prompt
workflow MetadataReviewContract: "Shared Metadata Review Contract"
    review_basis: "Review Basis"
        ...
    handoff_truth: "Handoff Truth"
        ...
    metadata_specific_checks: "Metadata-Specific Checks"
        ...
```

exposes:

* `contract.review_basis`
* `contract.handoff_truth`
* `contract.metadata_specific_checks`

Those are gate identities, not booleans and not freeform strings.

### 4.4 Supporting output surface

`review` does not replace rich output contracts. Review outputs remain ordinary
`output` declarations. The output-side rules this spec relies on are:

* `trust_surface`
* keyed conditional output sections with stable identities
* guarded sections that may read resolved review semantic fields after review semantics have already been computed

So the keyed conditional section form becomes:

```prompt
failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
    ...
```

not a title-only anonymous `section "..." when ...:` form. That keeps it
Doctrine-native, patchable, and addressable.

### 4.5 Reserved review surfaces

`review` reserves exactly these keyed surfaces:

* `fields`
* `on_accept`
* `on_reject`

Everything else is an ordinary named pre-outcome review section.

---

## 5. Grammar

### 5.1 Review declaration

```ebnf
abstract_review_decl     ::= "abstract" "review" CNAME ["[" review_ref "]"] ":" string NEWLINE
                             INDENT review_item+ DEDENT

review_decl              ::= "review" CNAME ["[" review_ref "]"] ":" string NEWLINE
                             INDENT review_item+ DEDENT

review_item              ::= review_config
                           | pre_outcome_review_section
                           | outcome_review_section
                           | review_inherit
                           | review_override_section

review_ref               ::= name_ref

review_config            ::= subject_stmt
                           | subject_map_stmt
                           | contract_stmt
                           | comment_output_stmt
                           | fields_stmt

subject_stmt             ::= "subject" ":" artifact_subject_expr

subject_map_stmt         ::= "subject_map" ":" NEWLINE
                             INDENT subject_map_entry+ DEDENT

subject_map_entry        ::= enum_member_ref ":" artifact_ref NEWLINE

contract_stmt            ::= "contract" ":" workflow_ref
comment_output_stmt      ::= "comment_output" ":" output_ref

fields_stmt              ::= "fields" ":" NEWLINE
                             INDENT semantic_field_binding+ DEDENT

semantic_field_binding   ::= semantic_field_name ":" field_path NEWLINE

semantic_field_name      ::= "verdict"
                           | "reviewed_artifact"
                           | "analysis"
                           | "readback"
                           | "failing_gates"
                           | "blocked_gate"
                           | "next_owner"
                           | "active_mode"
                           | "trigger_reason"

artifact_subject_expr    ::= artifact_ref
                           | "{" artifact_ref ("," artifact_ref)* "}"

artifact_ref             ::= name_ref
enum_member_ref          ::= name_ref
workflow_ref             ::= name_ref
output_ref               ::= name_ref
```

### 5.2 Review sections and patching

```ebnf
pre_outcome_review_section ::= CNAME ":" string NEWLINE
                               INDENT pre_outcome_review_stmt+ DEDENT

outcome_review_section     ::= "on_accept" ":" [string] NEWLINE
                               INDENT outcome_review_stmt+ DEDENT
                             | "on_reject" ":" [string] NEWLINE
                               INDENT outcome_review_stmt+ DEDENT

review_inherit             ::= "inherit" review_item_key NEWLINE
review_override_section    ::= "override" review_item_key ":" [string] NEWLINE
                               INDENT (semantic_field_binding+
                                     | pre_outcome_review_stmt+
                                     | outcome_review_stmt+) DEDENT

review_item_key            ::= CNAME
                             | "fields"
                             | "on_accept"
                             | "on_reject"
```

Ordinary pre-outcome section keys are stable compiler identities exactly like
workflow section keys. `fields`, `on_accept`, and `on_reject` are reserved
surfaces with fixed semantics.

### 5.3 Review statements

```ebnf
pre_outcome_review_stmt  ::= block_stmt
                           | reject_stmt
                           | accept_stmt
                           | preserve_stmt
                           | support_only_stmt
                           | ignore_stmt
                           | pre_outcome_when_stmt
                           | pre_outcome_match_stmt
                           | prose_line

outcome_review_stmt      ::= current_artifact_stmt
                           | current_none_stmt
                           | carry_stmt
                           | outcome_route_stmt
                           | outcome_when_stmt
                           | outcome_match_stmt
                           | prose_line

block_stmt               ::= "block" gate_label "when" expr
reject_stmt              ::= "reject" gate_label "when" expr
accept_stmt              ::= "accept" gate_label "when" expr

gate_label               ::= string
                           | contract_gate_ref
                           | section_gate_ref

contract_gate_ref        ::= "contract" "." CNAME
section_gate_ref         ::= CNAME

current_artifact_stmt    ::= "current" "artifact" artifact_ref "via" output_field_ref
current_none_stmt        ::= "current none"

carry_stmt               ::= "carry" carried_field "=" expr
carried_field            ::= "active_mode" | "trigger_reason"

output_field_ref         ::= output_ref "." field_path

pre_outcome_when_stmt    ::= "when" expr ":" NEWLINE
                             INDENT pre_outcome_review_stmt+ DEDENT

outcome_when_stmt        ::= "when" expr ":" NEWLINE
                             INDENT outcome_review_stmt+ DEDENT

pre_outcome_match_stmt   ::= "match" expr ":" NEWLINE
                             INDENT pre_outcome_match_case+ DEDENT

outcome_match_stmt       ::= "match" expr ":" NEWLINE
                             INDENT outcome_match_case+ DEDENT

pre_outcome_match_case   ::= review_match_head ":" NEWLINE
                             INDENT pre_outcome_review_stmt+ DEDENT

outcome_match_case       ::= review_match_head ":" NEWLINE
                             INDENT outcome_review_stmt+ DEDENT

review_match_head        ::= union_expr ["when" expr]
                           | "else"

union_expr               ::= expr ("|" expr)*

outcome_route_stmt       ::= "route" string "->" agent_ref ["when" expr]
```

### 5.4 Reused law statements and expression additions

`preserve`, `support_only`, and `ignore` inside `review` reuse the same
path/basis semantics as the workflow-law family:

```ebnf
preserve_stmt            ::= "preserve" preserve_kind preserve_target ["except" path_set_expr] ["when" expr]
support_only_stmt        ::= "support_only" support_target "for" "comparison" ["when" expr]
ignore_stmt              ::= "ignore" ignore_target ["for" ignore_basis_list] ["when" expr]
```

What changes is their role in verdict computation: inside `review`, they are
**check assertions**. A failed assertion causes the containing pre-outcome
review section to fail as a gate once, under that section's identity.

Review expressions add two narrow forms beyond the currently shipped baseline:

* membership negation: `expr not in expr`
* presence predicates: `present(channel_name)` and `missing(channel_name)`

These are limited to review semantics and review-output guard evaluation.

---

## 6. Exact expression namespace

This is now frozen.

### 6.1 Allowed names in review expressions

Review expressions may read only:

1. declared `input` roots attached to the current agent
2. enum members
3. declared subject members by artifact identity
4. compiler-known derived review facts
5. paths rooted in the reviewed subject(s)
6. carried field names inside the active outcome branch, after they have been set

### 6.2 Compiler-known derived review facts

The compiler owns these review-derived facts:

* `contract.passes`
* `contract.failed_gates`
* `contract.first_failed_gate`
* `failed(contract.some_check_key)`
* `passed(contract.some_check_key)`
* `current_truth.from_unnamed_support`
* `current_truth.from_unaccepted_output`
* `present(channel_name)`
* `missing(channel_name)`
* `writes(path_expr)`
* `unclear(...)`

Nothing else is implicit.

If you want values such as `copy_outcome`, `upstream_problem`,
`section_metadata_owed`, or `trigger_reason`, they must come from declared
inputs like `ReviewState`. No implicit `_present` booleans exist.

### 6.3 Output guards

Guards on conditional output sections may read:

* declared input roots
* enum members
* compiler-known derived review facts
* semantic field names resolved by the current review result

They may **not** read arbitrary sibling output fields, workflow-local names, or
review-local ad hoc variables that are not otherwise declared.

Guard timing is fixed:

1. resolve review semantics
2. bind semantic fields and carried option values
3. evaluate guarded output sections
4. validate required output content
5. render

---

## 7. Semantic model

### 7.1 Subject

`subject:` declares the artifact identity or artifact identity set that this
review may review.

A subject member may be only a declared `input` or `output` root. Review does
not compare raw path strings. It compares **normalized artifact identities**:

* declaration kind: `input` or `output`
* fully qualified declaration reference

The host/runtime must normalize any incoming "current artifact" or "reviewed
artifact" reference into one of those declared artifact identities before
review semantics use it.

If `subject` is a set, the review is multi-subject and every reachable terminal
branch must prove **exactly one live subject member**. The compiler accepts
three proof forms:

1. direct currentness proof
   the branch binds exactly one subject member with `current artifact X via Output.field`
2. mode-map proof
   the review declares a total `subject_map` from one enum mode to one subject member,
   and the branch carries exactly one `active_mode` value
3. explicit reviewed-artifact proof
   the branch binds a semantic `reviewed_artifact` value that normalizes to exactly one subject member

If the compiler cannot prove exactly one subject member per terminal branch, it
must raise `E489 REVIEW_SUBJECT_SET_REQUIRES_DISAMBIGUATION`.

### 7.2 Contract

`contract:` may reference only a review-contract workflow as defined above.

The compiler exposes these derived contract facts:

* `contract.passes`
* `contract.failed_gates`
* `contract.first_failed_gate`
* `failed(contract.some_check_key)`
* `passed(contract.some_check_key)`

`contract.passes` is defined **only from the referenced contract workflow**.
It does not include local review law. This avoids circularity with
`accept "..." when contract.passes`.

`contract.failed_gates` is an ordered list of exported contract gate
identities in contract order.

### 7.3 Comment output

`comment_output:` names the one declared `output` this review emits as its
durable verdict / handoff artifact.

Every concrete agent that uses a `review:` must emit that output.

### 7.4 Semantic fields

`fields:` is a **distinct inherited binding surface**. It is not ordinary prose
and it is not a loose config bag.

Its job is to bind compiler-known review channels to relative paths inside
`comment_output`.

These field bindings are relative to `comment_output`.

Required field bindings for concrete reviews:

* `verdict`
* `reviewed_artifact`
* `analysis`
* `readback`
* `next_owner`
* `failing_gates`

Conditionally required field bindings:

* `blocked_gate`: required if any `block` gate exists
* `active_mode`: required if any route branch carries downstream mode
* `trigger_reason`: required if any route branch carries downstream trigger reason

`fields:` does **not** carry currentness by alias. Review currentness still uses
the direct carrier rule `current artifact ... via Output.field`.

### 7.5 Hard language verdicts

`review` has exactly two language verdicts:

* `ReviewVerdict.accept`
* `ReviewVerdict.changes_requested`

These are compiler-owned verdict atoms, not freeform string labels.

A bound `verdict` output field must agree with one of those exact semantic
values and no others.

### 7.6 Gate evaluation order

Gate evaluation is fixed.

1. Evaluate local `block` gates in source order.
2. If one or more `block` gates fire:

   * verdict = `ReviewVerdict.changes_requested`
   * `failing_gates` = all true block gate identities in source order
   * `blocked_gate` = first true block gate identity
   * skip content-review evaluation for this branch

3. If no block gates fired, evaluate explicit local `reject` gates in source order.
4. If no block gates fired, evaluate assertion-style check sections. A
   pre-outcome section containing one or more `preserve`, `support_only`, or
   `ignore` statements fails once under that section's identity if any of those
   assertions fail.
5. If no block gates fired, evaluate the referenced contract workflow and compute:

   * `contract.failed_gates`
   * `contract.first_failed_gate`
   * `contract.passes`

6. If no block gates fired and there are still no local reject failures, no
   assertion-section failures, and no contract failures, evaluate the single
   `accept` gate.
7. Verdict is `ReviewVerdict.accept` iff no failing gates remain. Otherwise it
   is `ReviewVerdict.changes_requested`.

`failing_gates` ordering is fixed:

* true block gates in source order
* true local reject gates in source order
* failed assertion-section identities in authored section order
* `contract.failed_gates` in contract order
* the accept gate identity only if every earlier layer passed but the accept gate still failed

This gives exact gate identity without collapsing the contract layer to one
opaque boolean.

### 7.7 Blocked review turns

Blocked / unclear review turns live **inside** `review`.

They are expressed with `block` gates, not with a separate pre-review workflow.
That keeps the handoff-first stop line inside the same reviewer semantic unit
that ultimately produces verdict, currentness, and next-owner routing.

### 7.8 Outcome routing and placement

A review must define both:

* `on_accept`
* `on_reject`

Those are reserved outcome sections. Only the section matching the resolved
verdict is evaluated for routing, carried state, and currentness.

Statement placement is fixed.

Allowed only outside outcome sections:

* `block`
* `reject`
* `accept`
* `preserve`
* `support_only`
* `ignore`
* prose
* `when`
* `match` used to select pre-outcome check variants

Allowed only inside `on_accept` / `on_reject`:

* `current artifact ... via Output.field`
* `current none`
* `carry ...`
* `route ...`
* prose
* `when`
* `match`

Each terminal outcome branch must produce:

* exactly one route outcome
* exactly one currentness outcome (`current artifact ... via Output.field` or `current none`)
* zero or more carried semantic fields

### 7.9 Route determinism

Route resolution is fixed.

* plain `route` statements with guards are evaluated in source order
* `match` blocks use first-match-wins
* union heads such as `new_lesson | redesigned_lesson` are legal and mean logical disjunction
* guarded match heads such as `bounded_tweak when ReviewState.section_metadata_owed` are legal
* `else` is required unless the compiler can prove the match is exhaustive over the referenced enum or literal set
* after all nested `when` and `match` selection resolves, exactly one route must remain live

### 7.10 Current truth in reviews

`review` reuses the exact shipped portable-currentness rule:

* `current artifact X via Output.field`
* `current none`

No `via current` alias exists.

Every terminal outcome branch must resolve exactly one currentness outcome.

`current artifact X via Output.field` means:

* `X` is authoritative after this review outcome
* `Output.field` is the carrier that tells the next owner this is true

The carrier rules are the same as workflow law:

* the carrier root must be a declared emitted `output`
* the carrier field must exist
* the carrier field must appear in that output's `trust_surface`

`current none` means no durable artifact is carried forward as current after
that outcome and requires no carrier.

### 7.11 Carried downstream mode / trigger reason

Typed downstream mode does **not** travel in route syntax.

It travels on the declared `comment_output` through carried semantic fields:

* `carry active_mode = Enum.member`
* `carry trigger_reason = Enum.member`

Each optional carried channel follows an explicit option model:

* `Some(value)` when the branch carries it
* `None` when the branch does not

No implicit `_present` booleans exist.

Guards and trust-surface clauses use built-ins:

* `present(active_mode)`
* `missing(trigger_reason)`

Those fields must be bound in `fields:` and must appear in the output's
`trust_surface` under the same presence conditions that make them live.

### 7.12 Output agreement rules

Semantic-to-output agreement happens in three layers.

Compile-time agreement checks:

* the bound field exists and is addressable
* required semantic channels are bound
* currentness carriers point at declared output fields in `trust_surface`
* the concrete agent emits `comment_output`
* outcome branches are total

Emit/runtime agreement checks:

* `verdict` must equal the resolved semantic verdict
* `next_owner` must equal the resolved route target
* `current` must equal the resolved artifact identity or explicit none on the declared carrier
* `active_mode` and `trigger_reason` must equal any carried enum values
* `failing_gates` must equal the ordered failing gate list
* `blocked_gate` must equal the first blocking gate identity when one exists
* `reviewed_artifact` must normalize to the reviewed artifact identity

Presence-only authored fields:

* `analysis`
* `readback`

Those two are required for presence and placement, not semantic string
equality. This avoids pretending compile-time rules can prove human review
analysis prose while still keeping the coordination fields compiler-owned.

---

## 8. Inheritance and patching

`review` uses the same explicit ordered patching model as Doctrine workflows.

### 8.1 Abstract reviews and config inheritance

`abstract review` is the inheritance-only form:

```prompt
abstract review BaseReview: "Base Review"
```

Rules:

* `abstract review` may omit `subject`, `subject_map`, `contract`, `comment_output`, `accept`, `on_accept`, and `on_reject`
* `abstract review` may not be attached directly to a concrete agent
* a concrete `review` must satisfy all required surfaces before compilation succeeds

Config inheritance rules:

* `subject`, `subject_map`, `contract`, and `comment_output` inherit by value unless explicitly overridden

### 8.2 Binding surface and section inheritance

`fields` is a reserved inherited binding surface.

Children must account for it explicitly via:

* `inherit fields`
* `override fields:`

Within `override fields:`, bindings are keyed by semantic channel name and
follow the same explicit inherit/override rules as other Doctrine patchable
surfaces.

If a base review declares ordinary named pre-outcome sections or outcome
sections, the child review must account for every inherited section exactly
once via:

* `inherit section_key`
* `override section_key: "Title"`

New sections may be inserted explicitly by key.

No implicit merge exists. No silent section dropping exists.

### 8.3 Why this is required

This is not stylistic. The whole Doctrine direction has been explicit ordered
patching for reusable authored surfaces, and review support should not
introduce a second, fuzzier composition model.

---

## 9. Render semantics

The rendered review section should read naturally, not like a debug dump.

Render order is:

1. title
2. subject summary
3. referenced contract summary
4. named pre-outcome review sections in authored order
5. accept gate
6. routes and carried state on accept
7. routes and carried state on reject
8. outputs section, where the `comment_output` contract renders in ordinary output form

Render significance is fixed:

* ordinary named review section keys are patch identities
* ordinary named review section titles are authored render data
* `fields` does not render
* `on_accept` and `on_reject` may use authored titles or default to "If Accepted" / "If Rejected" when omitted

The renderer may normalize semantic order for readability, but it may not
silently discard authored titles for ordinary named review sections.

If a conditional output section exists, compiled static docs may show the
section shell plus "Rendered only when ...", while runtime required-content
semantics treat the section as present only when its guard is true.

---

## 10. Diagnostics

Review reuses the existing generic route parse diagnostics:

* `E131` missing route label
* `E132` missing route target

Review then reserves `E470`–`E499` for review-specific failures.

Parse-stage:

* `E470` invalid `review` declaration shape
* `E471` illegal statement placement in review body
* `E472` invalid guarded match head
* `E473` invalid or incomplete `fields:` binding surface

Compile-stage:

* `E474` missing `subject`
* `E475` invalid `subject` kind
* `E476` missing `contract`
* `E477` invalid `contract` target or unknown contract gate ref
* `E478` missing `comment_output`
* `E479` concrete agent does not emit `comment_output`
* `E480` concrete agent defines both `workflow:` and `review:`
* `E481` missing `accept`
* `E482` multiple `accept` gates
* `E483` missing reserved outcome section
* `E484` outcome not total
* `E485` multiple routes in one terminal branch
* `E486` multiple currentness outcomes in one terminal branch
* `E487` currentness declared without a valid carrier
* `E488` bound current carrier missing from `trust_surface`
* `E489` subject-set disambiguation failure
* `E490` missing inherited review section
* `E491` duplicate inherited review section accounting
* `E492` unknown overridden review section
* `E493` carried semantic channel is missing a required binding
* `E494` illegal concrete use of `abstract review`

Emit/runtime-agreement stage:

* `E495` semantic verdict does not match bound output field
* `E496` semantic next owner does not match bound output field
* `E497` semantic currentness does not match declared carrier field
* `E498` required carried field omitted when a semantic value exists
* `E499` required conditional output section missing after its guard resolved true

---

## 11. Canonical declarations used by the examples

### 11.1 Verdict, mode, and outcome enums

```prompt
enum ReviewVerdict: "Review Verdict"
    accept: "accept"
    changes_requested: "changes_requested"

enum MetadataPassMode: "Metadata Pass Mode"
    lesson_title: "lesson_title"
    section: "section"

enum MetadataTriggerReason: "Metadata Trigger Reason"
    new_lesson: "new_lesson"
    redesigned_lesson: "redesigned_lesson"

enum CopyOutcome: "Copy Outcome"
    new_lesson: "new_lesson"
    redesigned_lesson: "redesigned_lesson"
    bounded_tweak: "bounded_tweak"
```

### 11.2 Shared inputs and contract workflows

```prompt
input ProducerHandoff: "Producer Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the current producer handoff facts, including whether the handoff is invalid and what artifact identity it names as current."

input ReviewState: "Review State"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use current review-state facts such as copy outcome, whether the problem is upstream, whether section metadata is still owed, whether scope leaked, and whether a metadata trigger reason is present."

input ApprovedBoundary: "Approved Boundary"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the approved boundary facts whose exact scope must remain stable during review."

workflow CopyReviewContract: "Copy Review Contract"
    handoff_truth: "Handoff Truth"
        "Confirm the producer handoff is complete enough to identify the reviewed artifact honestly."

    copy_specific_checks: "Copy-Specific Checks"
        "Confirm the copy pass stayed inside the allowed title and boundary rules."

workflow MetadataReviewContract: "Metadata Review Contract"
    handoff_truth: "Handoff Truth"
        "Confirm the producer handoff names the exact metadata artifact now under review."

    metadata_specific_checks: "Metadata-Specific Checks"
        "Confirm the metadata pass stayed inside the intended scope and wording rules."

output CopyManifest: "Copy Manifest"
    target: File
        path: "unit_root/_authoring/COPY_MANIFEST.md"
    shape: MarkdownDocument
    requirement: Required

output LessonTitleMetadata: "Lesson Title Metadata"
    target: File
        path: "unit_root/_authoring/LESSON_TITLE_METADATA.json"
    shape: JsonObject
    requirement: Required

output SectionMetadata: "Section Metadata"
    target: File
        path: "unit_root/_authoring/SECTION_METADATA.json"
    shape: JsonObject
    requirement: Required
```

### 11.3 Shared review output and concrete owners

```prompt
output CriticVerdictAndHandoffOutput: "Critic Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "Say `accept` or `changes_requested`. No other verdict values."

    reviewed_artifact: "What You Reviewed"
        "Name the exact artifact identity you reviewed."
        "If review stopped before content review, name the producer handoff comment and say content review did not start."

    analysis_performed: "Analysis Performed"
        "Put the actual review analysis here."

    output_contents_that_matter: "Output Contents That Matter"
        "Put the actual reviewed contents, preserved constraints, or concrete failing details that still matter now."

    current_artifact: "Current Artifact"
        "Name the current artifact when one remains current after this review outcome."

    next_owner: "Next Owner"
        "Name the next owner for the same issue."

    active_mode: "Active Mode"
        "Name the active downstream mode when the next owner needs one."

    trigger_reason: "Trigger Reason"
        "Name the trigger reason when the next owner needs it."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        failing_gates: "Failing Gates"
            "Name the exact failing gates in order."

        failing_gate_if_blocked: "Failing Gate If Blocked"
            "If the review was blocked before content review, name that first blocking gate. Otherwise say plainly that no blocking gate applies."

    trust_surface:
        current_artifact when present(current_artifact)
        active_mode when present(active_mode)
        trigger_reason when present(trigger_reason)

    standalone_read: "Readable On Its Own"
        "A downstream owner should be able to read this comment alone and know the verdict, see the real review analysis and output readback, know what artifact is current now when one is current, know any carried mode or trigger reason, know what failed if it did not pass, and know who owns next."

agent ReviewLead:
    role: "Own explicit reroutes when specialist review work cannot continue cleanly."
    workflow: "Instructions"
        "Take back the same issue when review cannot hand off to a more specific owner honestly."

agent CopyAuthor:
    role: "Own copy revisions when review sends copy work back."
    workflow: "Instructions"
        "Revise the current copy artifact when review requests copy-local changes."

agent MetadataAuthor:
    role: "Own metadata revisions when review sends metadata work back."
    workflow: "Instructions"
        "Revise the current metadata artifact when review requests metadata changes."
```

---

## 12. Canonical positive example: `CopyReview`

```prompt
review CopyReview: "Copy Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.failing_gate_if_blocked
        next_owner: next_owner
        active_mode: active_mode
        trigger_reason: trigger_reason

    start_review: "Start Review"
        block contract.handoff_truth when ProducerHandoff.invalid
        reject "Current artifact does not match the copy manifest." when ProducerHandoff.current_artifact != CopyManifest
        reject "Unnamed support was treated as current truth." when current_truth.from_unnamed_support
        reject "Unaccepted output was treated as current truth." when current_truth.from_unaccepted_output

    contract_checks: "Contract Checks"
        preserve exact ApprovedBoundary.exact_scope_boundary
        reject contract.copy_specific_checks when writes(LessonTitleMetadata.title)
        accept "Shared copy review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact

        match ReviewState.copy_outcome:
            CopyOutcome.new_lesson:
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = MetadataTriggerReason.new_lesson
                route "Accepted copy needs a lesson-title metadata pass." -> MetadataAuthor

            CopyOutcome.redesigned_lesson:
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = MetadataTriggerReason.redesigned_lesson
                route "Accepted copy needs a lesson-title metadata pass." -> MetadataAuthor

            CopyOutcome.bounded_tweak when ReviewState.section_metadata_owed:
                carry active_mode = MetadataPassMode.section
                route "Accepted copy needs a section metadata pass." -> MetadataAuthor

            CopyOutcome.bounded_tweak:
                route "Accepted bounded tweak returns to ReviewLead." -> ReviewLead

            else:
                route "Accepted copy still leaves the boundary unclear, so keep the issue on ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact

        route "Return copy-local defects to CopyAuthor." -> CopyAuthor when ReviewState.upstream_problem == false
        route "Return upstream defects to ReviewLead." -> ReviewLead when ReviewState.upstream_problem
```

### Intended render

```md
## Copy Review

Review the current copy manifest and the producer handoff.

Block first if the producer handoff is too vague to tell what was really reviewed.

Reject if the current artifact does not match the copy manifest.
Reject if unnamed support was treated as current truth.
Reject if unaccepted output was treated as current truth.

Preserve the exact approved scope boundary.

Reject if the copy pass rewrote the lesson-title metadata outside the allowed contract.
Accept only if the shared copy review contract passes.

If accepted:
- the current artifact remains the copy manifest
- new lesson -> Metadata Author, carry `lesson_title` and `new_lesson`
- redesigned lesson -> Metadata Author, carry `lesson_title` and `redesigned_lesson`
- bounded tweak with section metadata still owed -> Metadata Author, carry `section`
- bounded tweak with no metadata owed -> Review Lead
- unclear accepted boundary -> Review Lead

If rejected:
- the current artifact remains the copy manifest
- copy-local defects go to Copy Author
- upstream defects go to Review Lead
```

This is the recurring semantic family the corpus keeps spelling out in prose
today: handoff-first stop line, exact current artifact, preserved upstream
truth, exact failing gates, current artifact readback, and next-owner routing.

---

## 13. Canonical positive example: `MetadataReview`

This example proves the fully-defined support for a multi-subject review family
and typed downstream mode.

```prompt
review MetadataReview: "Metadata Review"
    subject: {
        LessonTitleMetadata,
        SectionMetadata
    }
    subject_map:
        MetadataPassMode.lesson_title: LessonTitleMetadata
        MetadataPassMode.section: SectionMetadata
    contract: MetadataReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.failing_gate_if_blocked
        next_owner: next_owner
        active_mode: active_mode
        trigger_reason: trigger_reason

    start_review: "Start Review"
        block "Current mode is implicit." when unclear(ReviewState.active_mode)
        block "Current artifact is implicit." when unclear(ProducerHandoff.current_artifact)
        block "Lesson-title trigger reason is implicit." when ReviewState.active_mode == MetadataPassMode.lesson_title and unclear(ReviewState.trigger_reason)
        reject "Producer handoff named an artifact outside the metadata review family." when ProducerHandoff.current_artifact not in subject

    metadata_checks: "Metadata Checks"
        reject contract.metadata_specific_checks when ReviewState.scope_leak
        accept "Shared metadata review contract passes." when contract.passes

    on_accept: "If Accepted"
        match ReviewState.active_mode:
            MetadataPassMode.lesson_title:
                current artifact LessonTitleMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = ReviewState.trigger_reason
                route "Accepted lesson-title metadata returns to ReviewLead." -> ReviewLead

            MetadataPassMode.section:
                current artifact SectionMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.section
                route "Accepted section metadata returns to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        match ReviewState.active_mode:
            MetadataPassMode.lesson_title:
                current artifact LessonTitleMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = ReviewState.trigger_reason
                route "Return lesson-title metadata defects to MetadataAuthor." -> MetadataAuthor

            MetadataPassMode.section:
                current artifact SectionMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.section
                route "Return section metadata defects to MetadataAuthor." -> MetadataAuthor
```

This closes the multi-subject and typed-downstream-mode gap cleanly:

* `subject` is a real artifact set
* `subject_map` proves how mode selects the live subject
* route syntax stays narrow
* mode travels on the output, not on the route
* the next owner does not have to guess which metadata branch is live

---

## 14. Inheritance example

```prompt
abstract review BaseArtifactReview: "Artifact Review"
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.failing_gate_if_blocked
        next_owner: next_owner

    common_gates: "Common Gates"
        block "Producer handoff is incomplete." when ProducerHandoff.invalid
        reject "Unnamed support was treated as current truth." when current_truth.from_unnamed_support
        reject "Unaccepted output was treated as current truth." when current_truth.from_unaccepted_output


review CopyReview[BaseArtifactReview]: "Copy Review"
    subject: CopyManifest
    contract: CopyReviewContract

    inherit fields
    inherit common_gates

    copy_specific: "Copy-Specific Checks"
        preserve exact ApprovedBoundary.exact_scope_boundary
        reject contract.copy_specific_checks when writes(LessonTitleMetadata.title)
        accept "Shared copy review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact
        route "Accepted copy returns to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact
        route "Return copy defects to CopyAuthor." -> CopyAuthor
```

This is the Doctrine-native reuse story: explicit inheritance, explicit ordered
patching, no hidden merge.

---

## 15. Invalid examples

### 15.1 Incomplete `fields:` binding surface

```prompt
review InvalidReview: "Invalid Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        reviewed_artifact: reviewed_artifact
        next_owner: next_owner

    start_review: "Start Review"
        accept "Shared copy review contract passes." when contract.passes

    on_accept: "If Accepted"
        route "Route accepted copy." -> ReviewLead

    on_reject: "If Rejected"
        route "Route rejected copy." -> CopyAuthor
```

**Error:** `E473 invalid or incomplete fields binding surface`

### 15.2 Agent defines both workflow and review

```prompt
agent InvalidCritic:
    role: "Invalid."
    workflow: SomeWorkflow
    review: CopyReview
```

**Error:** `E480 concrete agent defines both workflow and review`

### 15.3 Current truth without a valid carrier

```prompt
review InvalidReview: "Invalid Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    start_review: "Start Review"
        accept "Contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact CopyManifest via current
        route "Route accepted copy." -> ReviewLead

    on_reject: "If Rejected"
        route "Route rejected copy." -> CopyAuthor
```

**Error:** `E487 currentness declared without a valid carrier`

### 15.4 Non-total accept routing

```prompt
review InvalidReview: "Invalid Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    start_review: "Start Review"
        accept "Contract passes." when contract.passes

    on_accept: "If Accepted"
        match ReviewState.copy_outcome:
            CopyOutcome.new_lesson:
                route "Route accepted copy." -> MetadataAuthor

    on_reject: "If Rejected"
        route "Route rejected copy." -> CopyAuthor
```

**Error:** `E484 outcome not total`

### 15.5 Multi-subject review without disambiguation

```prompt
review InvalidMetadataReview: "Invalid Metadata Review"
    subject: {
        LessonTitleMetadata,
        SectionMetadata
    }
    contract: MetadataReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    start_review: "Start Review"
        accept "Contract passes." when contract.passes

    on_accept: "If Accepted"
        route "Route accepted metadata." -> ReviewLead

    on_reject: "If Rejected"
        route "Route rejected metadata." -> MetadataAuthor
```

**Error:** `E489 subject-set disambiguation failure`

---

## 16. Corpus build plan

This is the ladder to actually check in.

It is deliberately shaped like the existing `30` through `42` workflow-law and
guarded-output corpus: each example proves **one new review idea at a time**,
keeps public examples generic rather than product-specific, keeps `output` as
the produced-contract primitive, and makes the new `review` surface carry real
compiler-owned semantics instead of merely renaming prose.

One planning correction matters here: the repo already ships `39` through `42`,
so the review ladder should use the next free range. This plan therefore maps
the new review corpus to `43` through `49`.

### 16.1 Fixed conventions for the whole ladder

These examples assume the following decisions are frozen:

* `review` is a top-level declaration and a reserved agent slot.
* `contract:` points to a review-contract workflow: a top-level `workflow` whose first-level keyed sections export gate identities.
* `fields:` binds compiler-owned review channels to concrete paths on `comment_output`.
* `ReviewVerdict.accept` and `ReviewVerdict.changes_requested` are hard language verdicts.
* `current artifact ... via Output.field` is reused exactly as the portable-currentness carrier form.
* guarded output sections may read bound semantic fields such as `verdict` or `active_mode`, but only after review resolution.
* `on_accept` and `on_reject` are mandatory outcome sections.
* outcome routing is first-match-wins and must be total.
* `output` still owns the readable downstream contract: exact fields, trust surface, standalone-read promise, and conditional failure sections.
* each rung should ship with targeted `INVALID_*` negatives that prove the new validation surface added by that rung.

### 16.2 Example `43_review_basic_verdict_and_route_coupling`

What this proves:

* the smallest first-class `review`
* one reviewed subject
* one shared review contract
* one accept gate
* one reject gate
* one `comment_output`
* verdict, failing-gates, and next-owner coupling

Minimum prompt shape:

* one generic contract workflow with two exported gates such as `completeness` and `clarity`
* one file input such as `DraftSpec`
* one comment output that binds `verdict`, `reviewed_artifact`, `analysis_performed`, `output_contents_that_matter`, `next_owner`, and guarded `failure_detail.failing_gates`
* one producer owner and one accepted-work owner
* one `review` that rejects an obviously bad local condition and accepts on `contract.passes`

Minimum render commitments:

* the rendered review must read like a real reviewer instruction surface, not a compiler dump
* the rendered output contract must show `Failure Detail` only conditionally on `ReviewVerdict.changes_requested`
* the rendered prose must make the accept and reject next-owner consequences visible

Required negatives:

* missing required `fields:` binding
* missing `on_accept`
* missing `on_reject`

### 16.3 Example `44_review_handoff_first_block_gates`

What this proves:

* `block`
* blocked review turns live inside `review`
* `blocked_gate`
* handoff-first stop line before content review

Minimum prompt shape:

* add `ProducerHandoff`
* add a guarded `failing_gate_if_blocked` field under `failure_detail`
* block on incomplete producer handoff
* reject if the handoff names the wrong current artifact
* still use one durable review comment output

Minimum render commitments:

* the review prose must say clearly that handoff quality is checked first
* the output contract must explain that blocked review still produces `changes_requested`
* the output contract must explain that `reviewed_artifact` names the handoff comment when content review never started

Required negatives:

* missing `blocked_gate` binding when a `block` gate exists
* illegal `block` placement inside `on_accept` / `on_reject`

### 16.4 Example `45_review_contract_gate_export_and_exact_failures`

What this proves:

* `contract.some_check_key`
* exported contract gate identities
* exact failing-gate naming from the shared contract family

Minimum prompt shape:

* one contract workflow with at least three exported keyed sections
* one review that explicitly rejects on `contract.<gate>`
* one output whose `failing_gates` field promises exact exported contract-gate identities

Minimum render commitments:

* the review prose should surface the named contract gates as actual checks, not opaque contract plumbing
* the output prose must make it clear that shared-contract failures use exported gate identities

Required negatives:

* unknown `contract.some_check_key`
* contract target that is not a review-contract workflow

### 16.5 Example `46_review_current_truth_and_trust_surface`

What this proves:

* `current artifact ... via Output.field`
* `trust_surface`
* semantically coupled current artifact readback on the review output

Minimum prompt shape:

* one review comment output with a dedicated carrier field such as `use_now` or `current_artifact`
* that carrier field listed in `trust_surface`
* both `on_accept` and `on_reject` bind the current artifact through the review output

Minimum render commitments:

* the review prose must say what remains current after accept and reject
* the output render must show the trusted carrier field under `trust_surface`
* the standalone-read promise must name current truth explicitly

Required negatives:

* currentness with an invalid carrier path
* carrier field not listed in `trust_surface`
* current artifact rooted outside declared review subjects / emitted outputs

### 16.6 Example `47_review_multi_subject_mode_and_trigger_carry`

What this proves:

* subject sets
* branch disambiguation through `subject_map` and `match`
* carried `active_mode`
* carried `trigger_reason`
* same next owner, different live mode

Minimum prompt shape:

* one mode enum
* one trigger-reason enum
* two reviewed subject artifacts
* `subject_map` tying the mode enum to the subject set
* one review output with optional `active_mode` and `trigger_reason` fields in `trust_surface` using `present(...)`
* accept and reject branches that carry different combinations of mode and trigger

Minimum render commitments:

* the prose must show how each mode selects a different current artifact
* the output render must show that `active_mode` and `trigger_reason` are trusted only when present

Required negatives:

* subject set without disambiguation proof
* carried `active_mode` without a bound `fields:` entry
* carried `trigger_reason` without a bound `fields:` entry

### 16.7 Example `48_review_inheritance_and_explicit_patching`

What this proves:

* `abstract review`
* explicit `inherit`
* explicit child sections
* no hidden merge model

Minimum prompt shape:

* one `abstract review` base with `comment_output`, `fields`, and shared gates
* one concrete child review with `subject`, `contract`, `inherit fields`, and inherited common gates
* one local child-only section plus concrete `on_accept` / `on_reject`

Minimum render commitments:

* the final render must read like one coherent review surface
* inherited shared review gates must appear exactly once in the final render
* local child law must appear in authored order, not hidden-parent order

Required negatives:

* missing inherited review section
* duplicate inherited review section accounting
* illegal concrete use of `abstract review`

### 16.8 Example `49_review_capstone`

What this proves:

* blocked review turns live inside `review`
* exact contract gates
* `support_only`
* `ignore ... for rewrite_evidence`
* `preserve`
* multi-subject review
* carried `active_mode`
* carried `trigger_reason`
* `current artifact ... via Output.field`
* `current none` for blocked handoff-first outcomes
* one durable review comment output that stays readable and trusted downstream

Minimum prompt shape:

* a multi-subject metadata-like family with one review-contract workflow
* `ProducerHandoff`, `ReviewState`, current subject artifacts, one preserved upstream structure input, and one comparison-only advisory input
* one review output with verdict, reviewed artifact, analysis, readback, current artifact, next owner, active mode, trigger reason, and guarded failure detail
* block on invalid handoff or unclear mode
* reject on contract gates and local scope violations
* `support_only` comparison help and `ignore ... for rewrite_evidence` branches
* `on_accept` branches that carry current artifact plus typed downstream state
* `on_reject` branches that either route blocked work with `current none` or route concrete defects with current artifact still explicit

Minimum render commitments:

* the render must read like one coherent reviewer surface, not like pasted sections from unrelated features
* blocked branches must clearly state that no durable artifact is current
* accepted and rejected branches must clearly state what remains current, what mode is active, and who owns next
* the output contract must remain readable on its own and faithful to the trust surface

Required negatives:

* illegal mixture of `current none` and `current artifact` in one terminal branch
* illegal use of pre-outcome statements inside outcome sections
* guarded review-output section that reads a disallowed name

### 16.9 Why this ladder is the right progression

This is the right order to implement and prove:

* `43` proves that `review` is real and not just workflow prose with a new name.
* `44` proves blocked turns live inside `review`.
* `45` proves contract gate exposure and exact `failing_gates`.
* `46` proves review reuses the shipped portable-currentness carrier rule.
* `47` proves mode-carry and multi-subject disambiguation.
* `48` proves reuse and explicit patching.
* `49` proves the full bundle together.

That mirrors the example-first design discipline already explicit in Doctrine:
prove one idea at a time, keep the runtime Markdown natural, and only widen the
language where the compiler actually owns the meaning.

## 17. The one-sentence version

**`review` is a first-class critic surface whose job is to bind reviewed subject, review contract, exact gates, portable current truth, next-owner routing, and typed verdict/handoff readback into one compiler-owned semantic unit, with `output` still serving as the canonical downstream contract.**

## 18. Resolved audit decisions

The current audit pressure is now answered directly in the spec:

* `review` is treated as a full Layer 1 primitive, not a narrow alias
* blocked / unclear review turns live inside `review`
* portable currentness is part of `review`, but it reuses the exact existing `via Output.field` carrier rule
* contract workflows export first-level keyed gate identities after flattening
* contract evaluation exposes `contract.passes`, `contract.failed_gates`, `contract.first_failed_gate`, `failed(...)`, and `passed(...)`
* `fields:` is a distinct inherited binding surface, not a prose section and not a hidden carrier alias
* guarded review-output sections may read resolved semantic fields such as `verdict`
* multi-subject reviews must prove exactly one live subject member per terminal branch through direct currentness, `subject_map`, or explicit reviewed-artifact proof
* `abstract review` is the inheritance-only form for reusable review bases
* optional carried state uses `present(...)` / `missing(...)` instead of implicit `_present` booleans
* semantic-to-output agreement is explicit and staged

## 19. Shipped reference status

This document is now the live shipped review reference, not a proposal draft.
The language shape above is the implementation contract for first-class
`review` in Doctrine.

Maintenance notes for future changes:

* keep exported review-contract gate flattening aligned with ordinary workflow
  inheritance and composition rather than introducing a review-only contract
  path
* keep artifact-identity normalization explicit at the host/runtime boundary
  before review evaluation starts instead of hiding it inside ad hoc parser or
  renderer behavior
* keep parser, compiler, verifier, error catalog, examples, and editor support
  aligned whenever the review surface changes
* keep public examples generic and avoid drifting back to product-specific
  names in the shipped review ladder

These are ordinary shipped-surface maintenance constraints, not unresolved
language-design holes.
