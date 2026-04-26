# Skill Graph Language Spec

Status: Doctrine-side language work shipped. The `../lessons_studio`
migration is still out of scope here.

This spec defines Doctrine-side language changes for first-class skill graph
support. It is based on the
[`lessons_studio` skill graph audit](LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md), the
studio authoring flow controller in `../lessons_studio`, and an independent
fresh consult with Claude Opus 4.7 at xhigh effort.

This spec does not refactor `../lessons_studio`. It defines the language,
compiler, emit, docs, and test work Doctrine should own.

## Core Decision

Add `skill_graph` as a first-class Doctrine declaration.

The first pass treated a skill graph as only an inferred compiler closure. That
was too weak for the studio authoring use case. The studio controller is
hand-maintaining several views of one missing source object:

- a flow registry
- stage contracts
- recovery rules
- a stepwise manifest projection
- examples that prove normal, recovery, and changed-flow behavior

Those views should come from one checked graph. The graph should have a name,
roots, policies, emitted views, and a source receipt.

The right shape is still small:

- `skill` declares reusable capability and links to a package.
- `skill relations` declare direct skill-to-skill edges.
- `artifact` declares a durable target symbol that stages can write or read.
- `receipt` declares typed handoff facts.
- `stage` declares one graph node and its owner skill.
- `skill_flow` declares a DAG of stages and nested flows.
- `skill_graph` declares the graph boundary, policies, roots, and emitted
  views.

`skill_graph` must not become a nested copy of every skill, stage, and receipt.
It is the graph object and projection boundary. The smaller declarations remain
the typed source of truth.

## Goal

Skill graph truth should be compiler-owned.

An author should be able to declare:

- the reusable skills in the graph
- the direct relations between skills
- the emitted package each skill points at
- the receipts passed between stages
- the stages that use those skills
- the durable checkpoint each stage owns
- the route choices each receipt exposes
- the flow DAG, including safe branches and nested flows
- the graph policy that bans unsafe shapes
- the graph views that should be emitted
- the optional diagrams the author wants, including Mermaid on request

Doctrine should then prove:

- skill refs resolve
- skill relations resolve
- package ids resolve
- stage owners exist
- support skills exist
- receipt fields are typed
- receipt route choices point at real stages, flows, or allowed sentinels
- flow nodes point at real stages or nested flows
- flow edges form a DAG unless a cycle is explicitly allowed
- graph roots point at real flows or stages
- generated graph docs and contracts are current

The result should feel natural to authors who know Python, Go, or typed
configuration. Small named declarations compose into a larger checked graph.

## Non-Goals

Doctrine should not own runtime state, memory, scheduling, tool calls, or
adapter behavior.

The graph contract tells a harness what the authored graph says. The harness
still decides what ran, what is current, and when to call a tool.

Doctrine should also not become a product policy engine. It should prove
generic structure. It should not judge whether a product-specific lesson plan
is good.

## Studio Controller Evidence

The studio authoring flow controller shows the need for a real graph object.
Its `SKILL.prompt` emits these references:

- `references/flow-registry.md`
- `references/stage-contracts.md`
- `references/recovery-audit.md`
- `references/stepwise-manifest.md`
- `references/examples.md`
- `references/studio-operating-doctrine.md`

Those files repeat the same facts in different forms. For example:

- The flow registry owns F1-F18, stage order, safe variations, unsafe
  variations, and approval routes.
- The stage contracts own stage id, owner skill, supporting skills, durable
  target, durable evidence, advance condition, risk guarded, forbidden
  outputs, and next owner.
- The recovery audit owns statuses, invalidation rules, and the next safe route.
- The stepwise manifest must project only the selected flow and recovery state.

This is exactly what a `skill_graph` should do:

- hold the graph identity
- gather the flows and stages that belong together
- enforce graph rules once
- emit the human views from the checked graph
- emit a machine contract for harnesses and other agents

The controller should not have to keep a Markdown registry, a stage table, a
recovery guide, and a stepwise guide in sync by hand.

## Existing Primitives To Reuse

The design should reuse these shipped surfaces:

- `skill package` emits one `SKILL.md` tree.
- Top-level `skill` names a reusable capability.
- `package:` on a top-level `skill` links that skill to a package id.
- `host_contract:` declares package host facts.
- `bind:` binds host facts at a consuming skill use site.
- Receipt host slots declare what a package emits on each run.
- `enum`, `table`, `schema`, and `document` own typed shapes.
- `workflow` and `sequence` own normal runtime instructions.
- `output schema route field` already models typed route choices.
- `rule` already models compiler-owned authoring policy.
- Source receipts already prove source freshness.

The new work should extend these pieces, not fork them.

`skill_flow` is new because a graph DAG is not the same thing as a prose
workflow. A `workflow` tells an agent how to do work. A `skill_flow` tells the
compiler which graph nodes can follow which other graph nodes.

## Mental Model

Use these nouns:

| Noun | Meaning |
| --- | --- |
| `skill` | A reusable capability an agent can load or call. |
| `skill relation` | A checked edge from one skill to another. |
| `skill package` | The emitted `SKILL.md` tree for one skill. |
| `artifact` | A durable target symbol a stage writes or a later stage reads. |
| `receipt` | A typed handoff fact a stage emits or reads. |
| `stage` | One graph node. It binds an owner skill to inputs, outputs, and durable checkpoint rules. |
| `skill_flow` | A typed DAG of stages and nested flows. |
| `skill_graph` | A named graph boundary. It selects roots, enforces policy, and emits graph views. |

This split keeps each declaration narrow.

## Skill Relations

Extend top-level `skill` with an optional `relations:` block.

Stages tell the graph who owns a unit of work. Skill relations tell the graph
how skills depend on each other outside one stage. This matters for wrappers,
primitives, diagnostics, and baseline skills.

### Syntax

```prompt
skill StudioPlayableMaterializer: "Studio Playable Materializer"
    purpose: "Build the runtime manifest from approved plan and situations."
    package: "studio-playable-materializer"
    relations:
        wraps PsmobileLessonPlayableLayout:
            why: "Adds studio proof checks around generic layout validation."
        delegates_to CatalogOps:
            why: "Writes catalog-backed lesson fields."
        delegates_to LessonsOps:
            why: "Writes lesson manifest JSON."

skill PsmobileLessonPlayableLayout: "PSMobile Lesson Playable Layout"
    purpose: "Validate and build playable layouts."
    package: "psmobile-lesson-playable-layout"
```

Built-in relation kinds are closed in v1.

Capability relation kinds:

- `requires`
- `delegates_to`
- `wraps`
- `audits`
- `extends`
- `supports`
- `composes`
- `teaches`
- `repairs`
- `baseline_for`
- `blocks`
- `supersedes`
- `related`

Surface relation kinds:

- `owns_surface`
- `reads_surface`
- `writes_surface`

Rules:

- relation targets must resolve to top-level `skill` declarations
- relation kinds are closed in v1
- `why:` is required under `require relation_reason`
- graph closure includes relation targets for reached skills
- generated graph JSON indexes relations by source skill and target skill

This gives the graph useful package-to-package and skill-to-skill structure
without making stage flows carry every support edge.

The surface relation kinds are useful for current studio checks, but they may
move to a future typed `surface` declaration if Doctrine adds one.

## New Declaration: `artifact`

Add top-level `artifact` declarations for durable graph targets.

Artifacts are symbols, not live file checks. They tell the graph which stage
writes a durable target and let later stages require that target by name.

### Syntax

```prompt
document SectionDoorstop: "Section Doorstop"
    "Section doorstop paths."

artifact SectionPlayableAnalysisPacket: "Section Playable Analysis Packet"
    owner: SectionPlayableAnalysis
    path_family: SectionDoorstop
    section: "Template"
    anchor: "Section Playable Analysis Packet"
    intent: "Carry checked section analysis facts."

stage SectionPlayableAnalysis: "Section Playable Analysis"
    owner: StudioSectionPlayableAnalysis
    artifacts:
        SectionPlayableAnalysisPacket
    intent: "Write the analysis packet."
    durable_target: "Section playable analysis packet."
    durable_evidence: "Catalog write receipt."
    advance_condition: "Packet is written."
```

Rules:

- `owner:` must resolve to a top-level `stage`.
- `path_family:` is optional. When present, it must resolve to a supported
  top-level type such as `document`, `schema`, `table`, `enum`, `receipt`,
  `input`, `output`, or `output target`.
- The artifact must declare at least one location hint: `path:`, `section:`,
  or `anchor:`.
- Only the owner stage may list the artifact under `artifacts:`.
- Later stages may read the artifact by listing it under `inputs:`.
- Reached artifact anchors must be unique inside one graph.

## New Declaration: `receipt`

Add top-level `receipt` declarations.

Today a receipt can live inside a `skill package` host contract. That works
for one package, but skill graphs need receipts that many stages and packages
can share.

### Syntax

```prompt
enum FlowId: "Flow Id"
    f1: "F1"
    f3: "F3"

enum StageStatus: "Stage Status"
    not_started: "Not Started"
    partial: "Partial"
    complete_unapproved: "Complete, Not Approved"
    approved: "Approved"
    stale: "Stale"
    invalidated: "Invalidated"
    blocked: "Blocked"

enum DurableArtifactStatus: "Durable Artifact Status"
    missing: "Missing"
    preview_only: "Preview Only"
    written: "Written"
    waived: "Waived"
    not_applicable: "Not Applicable"

table StageLedgerRow: "Stage Ledger Row"
    columns:
        stage: "Stage"
            type: string
        status: "Status"
            type: StageStatus
        durable_artifact_status: "Durable Artifact Status"
            type: DurableArtifactStatus
        evidence: "Evidence"
            type: string

receipt FlowReceipt: "Flow Receipt"
    flow_id: FlowId
    current_stage: string
    why_this_flow: string
    why_current_stage: string
    evidence_checked: list[string]
    durable_artifact_status: DurableArtifactStatus
    durable_evidence: string
    completed_stages: list[StageLedgerRow]
    blocked_or_partial_stages: list[StageLedgerRow]
    author_decision_needed: string
```

The body is compact on purpose. It should read like a typed struct.

Allowed field types:

- builtin scalar types: `string`, `integer`, `number`, `boolean`
- `enum`
- `table`
- `schema`
- another `receipt`, if there is no receipt cycle
- `list[TypeRef]`

All fields are required. If a value can be absent, model that as an enum value
such as `none`, or as a nullable schema. Do not add field-level `optional` in
the first version.

Receipts lower to JSON Schema. Keep prose-heavy `document` content behind a
path, id, or summary field instead of embedding it as a receipt field.

### Receipt Inheritance

Receipts should support the normal explicit inheritance model:

```prompt
receipt StageReceipt: "Stage Receipt"
    stage: string
    status: StageStatus

receipt LessonPlanReceipt[StageReceipt]: "Lesson Plan Receipt"
    inherit {stage, status}
    fit_grid_written: boolean
    choice_lock_written: boolean
```

Rules:

- inherited receipt fields must be accounted for with `inherit` or `override`
- duplicate fields fail
- wrong-kind overrides fail
- receipt inheritance cycles fail

This mirrors `workflow`, `document`, `output`, and other explicit patching
surfaces.

## Package Receipt By Reference

Extend `host_contract:` receipt slots so they can point at a top-level
receipt.

```prompt
skill package ControllerPackage: "Controller Package"
    metadata:
        name: "studio-authoring-flow-controller"
    host_contract:
        receipt flow_receipt: FlowReceipt
```

The current inline form stays valid:

```prompt
host_contract:
    receipt process_receipt: "Process Receipt"
        confidence: ConfidenceLevel
        evidence: list[EvidenceRow]
```

Rules:

- `receipt key: ReceiptRef` uses a top-level receipt.
- `receipt key: "Title"` with fields keeps the current inline form.
- `receipt key: "Title"` without fields remains `E535`.
- A package may not declare the same receipt slot key twice.
- `SKILL.contract.json` records the slot key, the receipt ref when present,
  the lowered field map, and a conservative receipt `json_schema`.

This keeps package contracts local while letting graph handoffs use shared
receipt types.

## New Declaration: `stage`

Add top-level `stage` declarations.

A stage is the graph role binding. It says which skill owns a graph step, what
the step reads, what it emits, and what durable checkpoint proves it served its
purpose.

### Syntax

```prompt
skill StudioLessonPlan: "Studio Lesson Plan"
    purpose: "Plan one lesson from the current section strategy."
    package: "studio-lesson-plan"

skill CatalogOps: "Catalog Ops"
    purpose: "Write exact catalog facts."
    package: "catalog-ops"

enum StageLane: "Stage Lane"
    router: "Router"
    pipeline: "Pipeline Stage"
    primitive: "Primitive"
    renderer: "Renderer"
    diagnostic: "Diagnostic"

stage LessonPlan: "Lesson Plan"
    id: "lesson_plan"
    owner: StudioLessonPlan
    lane: StageLane.pipeline
    supports:
        CatalogOps
    applies_to:
        F1AuthorLesson
        F2AuthorEmptySection
        F3BuildSection
    inputs:
        flow_receipt: FlowReceipt
        analysis_packet: SectionPlayableAnalysisPacket
    emits: LessonPlanReceipt
    intent: "Turn locked slot truth into the lesson plan and playable choice lock."
    durable_target: "Lesson doorstop `## Brief`."
    durable_evidence: "`catalog-ops spine write <lesson> --section Brief` receipt."
    advance_condition: "Author approval plus write receipt."
    risk_guarded: "Reps chosen before the pool exists."
    forbidden_outputs:
        "rep selection"
        "correct action columns"
```

Fields:

- `id:` is optional. It gives the public stage id used in rendered docs.
- `owner:` is required.
- `lane:` is optional. It must be an enum member when present.
- `supports:` is optional.
- `applies_to:` is optional. It may list `skill_flow` refs as an explicit
  flow-membership declaration.
- `inputs:` is optional.
- `artifacts:` is optional. It lists durable artifact symbols this stage owns.
- `emits:` is optional.
- `intent:` is required for stages used by a `skill_graph`.
- `durable_target:` is required unless the stage is marked
  `checkpoint: none`.
- `durable_evidence:` is required unless the stage is marked
  `checkpoint: none`.
- `advance_condition:` is required.
- `risk_guarded:` is optional.
- `forbidden_outputs:` is optional.
- `checkpoint:` is optional. Allowed values are `durable`, `review_only`,
  `diagnostic`, and `none`. Default is `durable`.

Rules:

- `owner:` must resolve to a top-level `skill`.
- `lane:` must resolve to an enum member.
- Each `supports:` item must resolve to a top-level `skill`.
- `supports:` may not repeat `owner:`.
- `applies_to:` values must resolve to `skill_flow` declarations.
- In the shipped sub-plan 2 slice, `applies_to:` only validates those refs and
  rejects duplicate resolved flows through the stage diagnostic family.
- Reachability cross-checks between `applies_to:` and expanded flow membership
  are deferred until real `skill_flow` expansion ships.
- `inputs:` values must resolve to a `receipt`, `artifact`, `document`,
  `schema`, or `table`.
- `artifacts:` values must resolve to top-level `artifact` declarations owned
  by this stage.
- `emits:` must resolve to a top-level `receipt`.
- Stages in a `skill_graph` must have `intent:` and `advance_condition:`.
- Durable stages must have `durable_target:` and `durable_evidence:`.
- A `review_only`, `diagnostic`, or `none` checkpoint may omit durable
  curriculum evidence, but it must say why in `advance_condition:`.

### Why `stage` Points At `skill`

The graph should not have a second way to declare skills. A top-level `skill`
already carries `purpose:` and optional `package:`. The stage should point at
that.

Do this:

```prompt
skill StudioLessonPlan: "Studio Lesson Plan"
    purpose: "Plan one lesson."
    package: "studio-lesson-plan"

stage LessonPlan: "Lesson Plan"
    owner: StudioLessonPlan
```

Do not do this:

```prompt
skill_graph StudioGraph: "Studio Graph"
    skills:
        skill lesson_plan: package "studio-lesson-plan"
```

That would create two skill declaration sites and invite drift.

## Stage Handoffs Live On Receipts

Stage handoffs should live on typed receipts.

This follows Doctrine's existing route model. Agent routing already lives on
output schema route fields. Stage routing should follow the same rule.

### Syntax

```prompt
enum PlanStatus: "Plan Status"
    approve: "Approve"
    revise: "Revise"
    human: "Human Review"

receipt LessonPlanReceipt: "Lesson Plan Receipt"
    plan_status: PlanStatus
    route next_route: "Next Route"
        approve: "Show the plan for author review." -> stage AuthorRender
        revise: "Return to lesson plan." -> stage LessonPlan
        human: "Hand to a human author." -> human
```

Route target forms:

- `-> stage StageRef`
- `-> flow SkillFlowRef`
- `-> human`
- `-> external`
- `-> terminal`

Rules:

- route choice keys are local to the route field
- route labels render for humans
- `stage StageRef` must resolve to a declared `stage`
- `flow SkillFlowRef` must resolve to a declared `skill_flow`
- sentinels are closed: `human`, `external`, `terminal`
- route fields lower into receipt JSON Schema
- route choices are recorded in the graph contract

This gives `next_on_approve` style handoffs compiler truth without adding a
second handoff language on stages.

## New Declaration: `skill_flow`

Add top-level `skill_flow` declarations.

A `skill_flow` is a graph DAG. It is not a prose workflow. It owns nodes,
edges, branch reasons, nested flows, and safe or unsafe variations.

### Linear Flow Syntax

```prompt
skill_flow F1AuthorLesson: "F1 - Author One Lesson"
    intent: "Turn one stable lesson slot into a complete review-ready lesson."
    start: LessonPlan
    edge LessonPlan -> AuthorRender:
        route: LessonPlanReceipt.next_route.approve
        kind: review
        why: "The author reviews the plan before downstream work depends on it."
    edge AuthorRender -> SituationSynthesis:
        why: "Concrete situations must be built from approved plan truth."
    edge SituationSynthesis -> ExactMoveProof:
        when: ExactMoveProofNeeded.yes
        why: "Exact action claims need solver proof before build."
    edge SituationSynthesis -> PlayableMaterialization:
        when: ExactMoveProofNeeded.no
        why: "No exact-action proof is needed for this lesson contract."
    edge ExactMoveProof -> PlayableMaterialization:
        why: "The proof must land before the manifest relies on it."
    edge PlayableMaterialization -> CopyLaneBaseline:
        why: "Copy work must see the built manifest and proof receipts."
    edge CopyLaneBaseline -> CopyCoherence:
        why: "The final copy pass checks one throughline."
    edge CopyCoherence -> OverviewRender:
        why: "The author reviews the finished lesson surface."
    approve: F18PublishHandoff
```

The left and right side of `edge` can be:

- a `stage` ref
- a nested `skill_flow` ref
- a named `repeat` node

The compiler records `start:` and every edge. It derives terminal nodes.

Edge fields:

- `why:` is required under `require edge_reason`.
- `route:` binds the edge to a receipt route choice.
- `route:` is required when the source stage emits a receipt with a route
  choice that targets the edge target.
- `kind:` is optional. Allowed values are `normal`, `review`, `repair`,
  `recovery`, `approval`, and `handoff`. Default is `normal`.
- `when:` is optional. It names a typed branch condition.

### Edge And Route Binding

Flow edges and receipt routes must not become two sources of truth.

Use `route:` to bind a graph edge to the typed receipt route that authorizes
that handoff:

```prompt
edge LessonPlan -> AuthorRender:
    route: LessonPlanReceipt.next_route.approve
    kind: review
    why: "The author reviews the plan before downstream work depends on it."
```

Rules:

- `route:` has the form `ReceiptRef.route_field.choice`.
- The receipt must resolve to a `receipt`.
- The route field must exist on that receipt.
- The choice must exist on that route field.
- The choice target must match the edge target.
- If the source stage emits a receipt with a route choice to the edge target,
  the edge must bind that route by default.
- If more than one route choice reaches the same target, the author must name
  the intended choice.
- `allow unbound_edges` in graph policy may relax this rule for legacy graphs.
- If there is exactly one route choice from the source receipt to the edge
  target, the compiler may suggest the missing `route:`.
- A route-bound edge renders with the route choice label.

### Branches

Use `when:` on an edge when the branch is typed.

```prompt
enum ExactMoveProofNeeded: "Exact Move Proof Needed"
    yes: "Yes"
    no: "No"

skill_flow F1AuthorLesson: "F1 - Author One Lesson"
    start: SituationSynthesis
    edge SituationSynthesis -> ExactMoveProof:
        when: ExactMoveProofNeeded.yes
        why: "Exact action claims need proof."
    edge SituationSynthesis -> PlayableMaterialization:
        when: ExactMoveProofNeeded.no
        why: "Family recognition lessons do not need exact action proof."
```

Rules:

- `when:` must be a typed enum member or a boolean expression over declared
  input fields.
- Branch edges from the same source should cover all enum members or name an
  `otherwise:` edge.
- Overlapping branch conditions fail when the compiler can prove overlap.
- Missing coverage stays a fail-loud `skill_flow` error by default. A graph can
  opt into `warn branch_coverage_incomplete` for legacy graph closure, and
  `require branch_coverage` keeps the graph path strict.

### Nested Flows

Studio flows often nest other flows: `F1 per slot`, `F3 per section`, and
`F1/F5 affected lessons`.

Model that explicitly:

```prompt
skill_flow F2AuthorEmptySection: "F2 - Author All Lessons In An Empty Section"
    intent: "Fill every slot in a locked empty section."
    start: ControllerRecoveryAudit
    repeat LessonSlotRun: F1AuthorLesson
        over: LessonSlots
        order: serial
        why: "Each lesson changes the evidence for later slots."
    edge ControllerRecoveryAudit -> LessonSlotRun:
        why: "Readiness must be checked before slot authoring starts."
    edge LessonSlotRun -> SectionOverviewRender:
        why: "The section overview should see all completed slot receipts."
    approve: F18PublishHandoff
```

`repeat` is a graph template, not a scheduler. It tells the compiler and the
harness that the child flow repeats over a typed set. The harness still decides
how to run each instance.

Repeat rules:

- the repeat name is local to the `skill_flow`
- the repeated target must be a `skill_flow`
- `over:` must resolve to an input, schema field, table, enum, or named
  runtime set declared in the graph contract
- `order:` is `serial`, `parallel`, or `unspecified`
- edge target resolution checks local repeat names before top-level stage refs
- a repeat name may not shadow a top-level stage, top-level `skill_flow`, or
  another repeat in the same flow
- repeat name shadowing fails with the `E551` skill flow diagnostic family
- `serial` repeats may be used when later instances depend on earlier receipts
- `parallel` repeats may not consume each other's receipts unless a merge stage
  is declared

### Variations

Model safe and unsafe variations inside the flow:

```prompt
skill_flow F1AuthorLesson: "F1 - Author One Lesson"
    variation skip_exact_move_proof: "Skip exact-move proof for family recognition lessons."
        safe_when: ExactMoveProofNeeded.no
    unsafe concrete_hands_in_plan: "Pick concrete hands during planning."
    unsafe copy_before_reps: "Write final copy before reps and correct answers exist."
```

Rules:

- `variation` names a safe variation.
- `unsafe` names an unsafe variation.
- `safe_when:` must be typed when present.
- unsafe variations render in docs and graph contracts.
- policies may fail a flow when an unsafe variation appears in a route.

### Changed Workflow Response Shape

A `skill_flow` can declare the response shape required when the user asks for a
workflow that does not fit the graph.

```prompt
skill_flow F1AuthorLesson: "F1 - Author One Lesson"
    changed_workflow:
        allow provisional_flow
        require nearest_flow
        require difference
        require safety_rationale
```

This lowers to a typed controller response contract:

- `provisional_intent`
- `nearest_flow`
- `difference`
- `safe_to_continue`
- `registry_update_needed`
- `next_route`

The compiler does not decide if the new workflow is good. Doctrine declares
the contract. The controller or harness still produces the response and chooses
the route.

When possible, this should reuse the existing typed output or `final_output`
surface instead of inventing a separate runtime response system.

## New Declaration: `skill_graph`

Add top-level `skill_graph` declarations.

A `skill_graph` is the named graph boundary. It selects roots, sets policies,
and declares the views Doctrine should emit.

### Syntax

```prompt
skill_graph StudioAuthoringGraph: "Studio Authoring Graph"
    purpose: "Route, recover, and project studio authoring flows."
    roots:
        flow F1AuthorLesson
        flow F2AuthorEmptySection
        flow F3BuildSection
        flow F18PublishHandoff
    sets:
        LessonSlots: "The lesson slots selected by the authoring target."
        Sections: "The sections selected by the authoring target."
    recovery:
        flow_receipt: FlowReceipt
        stage_status: StageStatus
        durable_artifact_status: DurableArtifactStatus
    policy:
        dag acyclic
        require edge_reason
        require relation_reason
        require durable_checkpoint
        require route_targets_resolve
        require checked_skill_mentions
        warn orphan_stage
        warn orphan_skill
    views:
        flow_registry: "references/flow-registry.md"
        stage_contracts: "references/stage-contracts.md"
        recovery_audit: "references/recovery-audit.md"
        stepwise_manifest: "references/stepwise-manifest.md"
        skill_inventory: "references/skill-inventory.md"
        artifact_inventory: "references/artifact-inventory.md"
        graph_markdown: "references/skill-graph.md"
        graph_json: "references/skill-graph.json"
        graph_contract: "SKILL_GRAPH.contract.json"
        graph_source: "SKILL_GRAPH.source.json"
        diagram_d2: "references/skill-graph.d2"
        diagram_svg: "references/skill-graph.svg"
        diagram_mermaid: "references/skill-graph.mmd"
```

Fields:

- `purpose:` is required.
- `roots:` is required and lists `flow` or `stage` refs.
- `sets:` is optional. It names graph-level sets used by repeat nodes.
- `recovery:` is optional. It names the receipt and enums used by recovery
  views.
- `policy:` is optional but recommended.
- `views:` is optional. If omitted, Doctrine emits default graph artifacts.

Root forms:

- `flow SkillFlowRef`
- `stage StageRef`

View keys:

- `flow_registry`
- `stage_contracts`
- `recovery_audit`
- `stepwise_manifest`
- `skill_inventory`
- `graph_markdown`
- `graph_json`
- `graph_contract`
- `graph_source`
- `diagram_d2`
- `diagram_svg`
- `diagram_mermaid`
- `receipt_schema_dir`

The `views:` keys are a closed v1 set. Custom views should be generated from
`SKILL_GRAPH.contract.json` or `skill-graph.json` outside Doctrine until the
language has a typed extension point.

Rules:

- root refs must resolve
- repeat `over:` refs must resolve to a graph set, input, schema field, table,
  or enum
- recovery refs must resolve to a `receipt` and `enum` declarations
- roots close over nested flows, repeated flows, stages, skills, receipts, and
  package links
- view paths must be inside the target output directory
- duplicate view keys fail
- a `skill_graph` may not redeclare skills or stages inline
- the compiler emits one graph contract per graph declaration

## DAG Policy

The default graph policy should be strict.

Built-in policies:

| Policy | Meaning |
| --- | --- |
| `dag acyclic` | Flow edges must form a DAG after nested flow expansion. |
| `dag allow_cycle "Reason"` | Permit a named cycle only with a reason. |
| `require edge_reason` | Every edge must have `why:`. |
| `allow unbound_edges` | Relax default route binding for legacy graphs. |
| `require relation_reason` | Every skill relation must have `why:`. |
| `require durable_checkpoint` | Durable stages need target and evidence. |
| `require route_targets_resolve` | Receipt route targets must resolve. |
| `require checked_skill_mentions` | `$skill` style prose must use checked refs when it names graph skills. |
| `require branch_coverage` | Branches over enum members must cover all members. |
| `require stage_lane` | Every reached stage must declare a lane enum member. |
| `warn orphan_stage` | Warn when a stage is visible but not reached by the graph roots. |
| `warn orphan_skill` | Warn when a package-linked skill is visible but not used by any reached stage. |
| `warn receipt_without_consumer` | Warn when a stage emits a receipt no later reached stage reads. |
| `warn manual_only_default_flow_conflict` | Warn when a reached skill is both manual-only and a default flow member. |

`dag acyclic` checks the expanded graph. Repeat nodes are templates, so they do
not create a cycle by themselves. A serial repeat can still fail if a child flow
routes back to a parent stage without an allowed cycle.

## Checked Skill Mentions

Add checked skill refs for prose.

```prompt
"Use {{skill:CatalogOps}} for exact catalog writes."
"The owner package is {{skill:StudioLessonPlan.package}}."
```

Rules:

- `{{skill:Name}}` must resolve to a top-level `skill`.
- The default projection renders the skill title.
- `{{skill:Name.package}}` renders the package id when one exists.
- `{{skill:Name.purpose}}` renders the purpose text.
- Unknown skills fail under `require checked_skill_mentions`.
- Unknown skills warn when that policy is not enabled.

This catches stale `$skill-name` prose.

If Doctrine does not already have a general `{{...}}` interpolation pass for
strings, treat this as a small parallel feature. It should resolve only inside
string and Markdown text surfaces that opt into checked interpolation. It
should ship with its own example before graph docs rely on it broadly.

## Generated Graph Contract

Every `skill_graph` emits a graph contract.

Default output:

```text
SKILL_GRAPH.contract.json
SKILL_GRAPH.source.json
references/skill-graph.json
references/skill-graph.md
references/skill-graph.d2
references/skill-graph.svg
references/skill-graph.mmd
references/skill-inventory.md
references/artifact-inventory.md
references/flow-registry.md
references/stage-contracts.md
references/recovery-audit.md
references/stepwise-manifest.md
receipts/<receipt-name>.schema.json
```

### Contract Shape

Top level:

```json
{
  "contract_version": 1,
  "graph": {
    "name": "StudioAuthoringGraph",
    "title": "Studio Authoring Graph",
    "purpose": "Route, recover, and project studio authoring flows."
  },
  "roots": [],
  "skills": {},
  "skill_relations": [],
  "artifacts": {},
  "stages": {},
  "flows": {},
  "receipts": {},
  "packages": {},
  "sets": {},
  "recovery": {},
  "policies": [],
  "views": {}
}
```

Skill entry:

```json
{
  "name": "StudioLessonPlan",
  "title": "Studio Lesson Plan",
  "package_id": "studio-lesson-plan",
  "purpose": "Plan one lesson from the current section strategy.",
  "relations": []
}
```

Skill relation entry:

```json
{
  "from": "StudioPlayableMaterializer",
  "kind": "wraps",
  "to": "PsmobileLessonPlayableLayout",
  "why": "Adds studio proof checks around generic layout validation."
}
```

Stage entry:

```json
{
  "name": "LessonPlan",
  "id": "lesson_plan",
  "title": "Lesson Plan",
  "owner": "StudioLessonPlan",
  "lane": "StageLane.pipeline",
  "supports": ["CatalogOps"],
  "applies_to": ["F1AuthorLesson", "F2AuthorEmptySection", "F3BuildSection"],
  "inputs": {
    "flow_receipt": {"kind": "receipt", "type": "FlowReceipt"},
    "analysis_packet": {"kind": "artifact", "type": "SectionPlayableAnalysisPacket"}
  },
  "emits": "LessonPlanReceipt",
  "artifacts": [],
  "checkpoint": "durable",
  "intent": "Turn locked slot truth into the lesson plan and playable choice lock.",
  "durable_target": "Lesson doorstop `## Brief`.",
  "durable_evidence": "`catalog-ops spine write <lesson> --section Brief` receipt.",
  "advance_condition": "Author approval plus write receipt.",
  "risk_guarded": "Reps chosen before the pool exists.",
  "forbidden_outputs": ["rep selection", "correct action columns"]
}
```

Artifact entry:

```json
{
  "name": "SectionPlayableAnalysisPacket",
  "title": "Section Playable Analysis Packet",
  "owner_stage": "SectionPlayableAnalysis",
  "path_family": {"kind": "document", "name": "SectionDoorstop"},
  "path": null,
  "section": "Template",
  "anchor": "Section Playable Analysis Packet",
  "intent": "Carry checked section analysis facts."
}
```

Flow entry:

```json
{
  "name": "F1AuthorLesson",
  "title": "F1 - Author One Lesson",
  "intent": "Turn one stable lesson slot into a complete review-ready lesson.",
  "start": "LessonPlan",
  "edges": [
    {
      "from": "LessonPlan",
      "to": "AuthorRender",
      "route": "LessonPlanReceipt.next_route.approve",
      "kind": "review",
      "why": "The author reviews the plan before downstream work depends on it."
    }
  ],
  "repeat_nodes": {},
  "variations": {},
  "unsafe_variations": {},
  "approve": "F18PublishHandoff"
}
```

Receipt entry:

```json
{
  "name": "LessonPlanReceipt",
  "title": "Lesson Plan Receipt",
  "fields": {
    "plan_status": {"type": "PlanStatus"}
  },
  "routes": {
    "next_route": {
      "title": "Next Route",
      "choices": {
        "approve": {
          "title": "Show the plan for author review.",
          "target_kind": "stage",
          "target": "AuthorRender"
        },
        "human": {
          "title": "Hand to a human author.",
          "target_kind": "sentinel",
          "target": "human"
        }
      }
    }
  }
}
```

## Query-Friendly Graph JSON

Emit `skill-graph.json` as the easy consumption surface.

It should include indexes a harness can use without parsing Markdown:

```json
{
  "graph": "StudioAuthoringGraph",
  "by_stage": {},
  "by_skill": {},
  "by_flow": {},
  "relations_by_skill": {},
  "owners": {},
  "supports": {},
  "next_by_stage": {},
  "routes_by_receipt": {},
  "sets": {},
  "repeats": {},
  "recovery": {},
  "recovery_statuses": ["not_started", "partial", "complete_unapproved"],
  "durable_artifact_statuses": ["missing", "preview_only", "written"]
}
```

This is the surface that makes graph consumption simple. A controller, harness,
or stepwise planner should be able to answer common questions from this file:

- What stages can follow this stage?
- Which skill owns this stage?
- Which stages use this support skill?
- Which receipt carries the next route?
- Which stages are in the selected flow?
- Which nested flow should run per lesson slot?

Markdown is for people. `skill-graph.json` is for tools and agents.

## Mermaid Diagram Output

Doctrine should be able to generate a Mermaid graph on request.

Mermaid is useful because many docs sites and chats render it directly. D2 and
SVG can remain the stable visual artifacts. Mermaid should be the portable
Markdown-native view.

View key:

```prompt
views:
    diagram_mermaid: "references/skill-graph.mmd"
```

Command forms:

```bash
uv run --locked python -m doctrine.emit_skill_graph --entrypoint prompts/GRAPH.prompt --output-dir build/skill_graph --graph StudioAuthoringGraph --diagram mermaid
uv run --locked python -m doctrine.emit_skill_graph --entrypoint prompts/GRAPH.prompt --output-dir build/skill_graph --graph StudioAuthoringGraph --view diagram_mermaid
```

Mermaid output should use `flowchart LR` by default.

Rules:

- generate Mermaid from the same graph contract as D2/SVG
- do not parse rendered Markdown back into Mermaid
- escape labels so stage titles, flow ids, and route labels cannot break syntax
- include stage nodes, nested flow nodes, repeat nodes, and route-bound edges
- label route-bound edges with the receipt route key when useful
- render repeat nodes as subgraphs or clearly labeled flow nodes
- keep the output deterministic and diff-friendly

Example:

```mermaid
flowchart LR
    LessonPlan["Lesson Plan"]
    AuthorRender["Author Render"]
    SituationSynthesis["Situation Synthesis"]
    LessonPlan -->|"LessonPlanReceipt.next_route.approve"| AuthorRender
    AuthorRender -->|"approved plan"| SituationSynthesis
```

## Markdown Rendering

The rendered docs should be clean views of the graph, not dumps of every
compiler field.

### Skill Inventory

```markdown
# Skill Inventory

| Skill | Package | Purpose |
| --- | --- | --- |
| Studio Lesson Plan | studio-lesson-plan | Plan one lesson from the current section strategy. |
| Catalog Ops | catalog-ops | Write exact catalog facts. |
```

### Stage Contracts

```markdown
# Stage Contracts

## Lesson Plan

Owner: Studio Lesson Plan

| Surface | Value |
| --- | --- |
| Stage id | lesson_plan |
| Lane | Pipeline Stage |
| Supports | Catalog Ops |
| Inputs | flow_receipt: FlowReceipt |
| Emits | LessonPlanReceipt |
| Durable target | Lesson doorstop `## Brief`. |
| Durable evidence | `catalog-ops spine write <lesson> --section Brief` receipt. |
| Advance condition | Author approval plus write receipt. |

Turn locked slot truth into the lesson plan and playable choice lock.
```

### Flow Registry

```markdown
# Flow Registry

## F1 - Author One Lesson

Turn one stable lesson slot into a complete review-ready lesson.

| From | To | When | Why |
| --- | --- | --- | --- |
| Lesson Plan | Author Render | always | The author reviews the plan before downstream work depends on it. |
| Situation Synthesis | Exact Move Proof | ExactMoveProofNeeded.yes | Exact action claims need solver proof before build. |
```

Route-bound edges should show the route key when useful:

```markdown
LessonPlanReceipt.next_route.approve -> Author Render
```

### Recovery Audit

```markdown
# Recovery Audit

Use the stage contract and current receipts to assign one status per reached
stage.

| Status | Meaning |
| --- | --- |
| not_started | No usable evidence exists. |
| partial | Evidence exists but misses required proof. |
| approved | The advance condition is satisfied. |
```

### Stepwise Manifest

```markdown
# Stepwise Manifest

Project only the selected flow and recovery state. Do not dump every graph
flow into a local step plan.

| Step | Owner | Entry Evidence | Exit Evidence | Stop Conditions |
| --- | --- | --- | --- | --- |
| Lesson Plan | Studio Lesson Plan | FlowReceipt | LessonPlanReceipt | Missing durable target |
```

Rendering rules:

- use titles for human labels
- keep package ids in package columns
- render enum member titles where possible
- render sentinels as lowercase words
- keep generated docs stable and diff-friendly
- avoid repeating full graph facts in every rendered view

## Source Receipt

Emit `SKILL_GRAPH.source.json`.

It records:

- graph source files
- emitted graph files
- receipt schema files
- package ids linked by graph skills
- source receipt hash for each package when available
- graph contract hash
- graph JSON hash
- graph diagram hash

`verify_skill_graph` should report:

- `current`
- `missing_graph_receipt`
- `stale_graph_source`
- `edited_graph_artifact`
- `missing_package_receipt`
- `stale_package_receipt`
- `graph_contract_mismatch`
- `unsupported_graph_receipt_version`

## Commands

Add:

```bash
uv run --locked python -m doctrine.emit_skill_graph --graph <graph-name>
uv run --locked python -m doctrine.verify_skill_graph --graph <graph-name>
```

Rules:

- `emit_skill_graph` accepts a file or configured target that contains a
  `skill_graph` declaration.
- `SKILL.prompt` remains package-first, but it may import a graph declaration.
- `GRAPH.prompt` is the preferred standalone graph entrypoint.
- The graph must compile at least one root flow or root stage.
- If no graph closure exists, `emit_skill_graph` fails loud.
- The command may reuse the D2 dependency used by `emit_flow`.

Example target:

```toml
[[tool.doctrine.emit.targets]]
name = "studio_skill_graph"
entrypoint = "prompts/GRAPH.prompt"
graph = "StudioAuthoringGraph"
output_dir = "build/skill_graph"
```

## Compiler Errors

Reserve new compile and emit errors for the graph surface. The exact numbers
can move before implementation, but the families should stay stable.

| Code | Summary | When |
| --- | --- | --- |
| `E544` | Invalid receipt declaration | Duplicate fields, empty receipt, unknown type, or receipt cycle |
| `E545` | Invalid stage declaration | Missing owner, duplicate input key, duplicate support skill, or invalid body item |
| `E546` | Stage owner is not a declared skill | `owner:` points at a missing or wrong-kind declaration |
| `E547` | Stage support is not a declared skill | `supports:` points at a missing or wrong-kind declaration |
| `E548` | Stage input type is invalid | `inputs:` points at a missing or wrong-kind declaration |
| `E549` | Stage emit type is invalid | `emits:` points at a missing or wrong-kind declaration |
| `E550` | Receipt route target is invalid | A receipt route points at a missing stage, flow, or unknown sentinel |
| `E551` | Invalid skill flow | A flow node, edge, branch, route binding, repeat, or approve route is invalid |
| `E552` | Invalid skill graph | A graph root, graph set, recovery ref, policy, view path, or closure is invalid |
| `E553` | Skill package id is unresolved | `package:` matches no visible package id or registered target |
| `E554` | Skill graph emit failed | Graph emit found no graph closure or hit an invalid graph output path |
| `E566` | Invalid skill relation | A skill relation target, relation kind, or required relation reason is invalid |

Example diagnostic:

```text
E551 compile error: Invalid skill flow

Detail:
Flow `F1AuthorLesson` has edge `LessonPlan -> MissingStage`, but
`MissingStage` does not resolve to a stage, nested flow, or repeat node.

Hint:
Declare `stage MissingStage: "Missing Stage"`, fix the edge target, or remove
the edge.
```

## Compiler Warnings

Doctrine now ships a graph-scoped warning layer. Warnings run only when the
graph opts in with a matching `warn <key>` policy line. Skill graphs need this
because some graph shapes are valid but suspicious.

Candidate warnings:

| Code | Summary | When |
| --- | --- | --- |
| `W201` | Stage has no graph | A visible stage is not reached by this `skill_graph` root |
| `W202` | Skill has no stage | A visible skill is not reached from a stage, relation, or checked skill mention |
| `W203` | Stage owner is shared | Two stages use the same owner skill |
| `W204` | Checked skill mention is unknown | `{{skill:Name}}` does not resolve and strict policy is off |
| `W205` | Branch coverage is incomplete | `warn branch_coverage_incomplete` let enum branch edges compile without covering all enum members |
| `W206` | Receipt has no consumer | A receipt is emitted by a stage but no later reached stage reads it |
| `W207` | Flow has no approve route | A flow has terminal stages but no `approve:` route |
| `W208` | Stage has no risk guard | A reached durable stage has no `risk_guarded:` text |
| `W209` | Edge route binding is missing | A stage emits a routed receipt but an outgoing edge has no `route:` under relaxed policy |
| `W210` | Skill relation has no reason | A skill relation has no `why:` and strict policy is off |
| `W211` | Manual-only default-flow conflict | A reached skill is marked both manual-only and a default flow member |

If Doctrine can prove the shape is wrong, make it an error. Use warnings only
for valid shapes that often signal drift.

## Implementation Plan

### Parser And Model

Add model types:

- `ReceiptDecl`
- `ReceiptField`
- `ReceiptRouteField`
- `ReceiptRouteChoice`
- `SkillRelation`
- `StageDecl`
- `StageInput`
- `StageLaneRef`
- `SkillFlowDecl`
- `SkillFlowEdge`
- `SkillFlowEdgeRouteRef`
- `SkillFlowRepeat`
- `SkillFlowVariation`
- `SkillGraphDecl`
- `SkillGraphRoot`
- `SkillGraphSet`
- `SkillGraphRecovery`
- `SkillGraphPolicy`
- `SkillGraphView`

Add grammar rules:

- `receipt_decl`
- `receipt_body`
- `receipt_field`
- `receipt_route_field`
- `receipt_route_choice`
- `skill_relations_block`
- `skill_relation_stmt`
- `stage_decl`
- `stage_body`
- `stage_owner_stmt`
- `stage_supports_block`
- `stage_inputs_block`
- `stage_emits_stmt`
- `stage_checkpoint_stmt`
- `stage_lane_stmt`
- `skill_flow_decl`
- `skill_flow_body`
- `skill_flow_edge`
- `skill_flow_edge_route`
- `skill_flow_repeat`
- `skill_flow_variation`
- `skill_flow_changed_workflow`
- `skill_graph_decl`
- `skill_graph_body`
- `skill_graph_roots_block`
- `skill_graph_sets_block`
- `skill_graph_recovery_block`
- `skill_graph_policy_block`
- `skill_graph_views_block`

Extend grammar rules:

- `package_host_receipt_slot` accepts `receipt key: ReceiptRef`
- top-level `skill` accepts `relations:`
- top-level `receipt` route targets accept `stage`, `flow`, and sentinels
- interpolation accepts `skill:` roots

Do not change existing `output schema route field` target syntax in v1.
Typed targets such as `-> stage StageRef` and `-> flow SkillFlowRef` are valid
only on top-level `receipt` route fields. That avoids changing the shipped
agent-output route surface while skill graph receipts are still new.

Keep grammar style close to existing surfaces:

- declaration head: `kind CNAME: "Title"`
- block ownership by indentation
- refs by `name_ref`
- route choices reuse route field shape
- no free-form YAML maps

### Resolve And Validate

Add resolver support that:

1. indexes top-level receipts, stages, skill flows, and skill graphs
2. resolves package-linked skills through existing package id lookup
3. resolves direct skill relations
4. resolves stage owners and support skills
5. resolves stage input and emit types
6. resolves receipt fields and route targets
7. resolves flow nodes, edges, branches, repeats, and approve routes
8. checks edge route bindings against receipt route choices
9. resolves graph sets and recovery metadata
10. expands nested flows into a graph closure
11. checks DAG policy and allowed cycle policy
12. applies graph-related rules
13. lowers the graph closure to contract and query JSON objects

The resolver should not require a concrete agent context. A graph can resolve
package links and package receipt contracts without binding host slots.

### Emit

Add `doctrine.emit_skill_graph`.

It should emit:

- skill inventory Markdown
- stage contract Markdown
- flow registry Markdown
- recovery audit Markdown
- stepwise manifest Markdown
- graph Markdown
- graph contract JSON
- query-friendly graph JSON
- graph source receipt JSON
- D2, SVG, and Mermaid graph output
- JSON Schema files for receipts

### Verify

Add `doctrine.verify_skill_graph`.

It should:

- compile the named graph
- compare emitted graph files to source truth
- compare graph source receipt hashes
- verify package receipts named by graph skills when those receipts exist
- report one status per graph target

Do not make `verify_skill_graph` run every package target by itself. It checks
the graph and receipts already present.

## Docs Update Plan

Update:

- `docs/LANGUAGE_REFERENCE.md`
- `docs/SKILL_PACKAGE_AUTHORING.md`
- `docs/EMIT_GUIDE.md`
- `docs/WARNINGS.md`
- `docs/COMPILER_ERRORS.md`
- `docs/AUTHORING_PATTERNS.md`
- `docs/DOCTRINE_LEARN.md`
- `examples/README.md`
- `skills/doctrine-learn/prompts/SKILL.prompt`
- `skills/doctrine-learn/prompts/refs/skill_graphs.prompt`

Add:

- `docs/SKILL_GRAPH_AUTHORING.md`

That guide should teach:

- when to use `receipt`
- when to use `stage`
- when to use `skill_flow`
- when to use `skill_graph`
- how to link a skill to a package
- how to model stage handoffs on receipt route fields
- how to model nested flow repeats
- how to emit and verify graph docs
- how to generate a Mermaid diagram on request
- how to migrate a prose inventory without changing runtime behavior

## Test Plan

Add examples after the current corpus:

- `150_receipt_top_level_decl`: reusable receipt and package receipt by ref
- `151_stage_basics`: one stage with owner, support, inputs, and emits
- `152_receipt_stage_route`: receipt route field targeting stages, flows, and sentinels
- `153_skill_flow_linear`: linear DAG with edge reasons
- `154_skill_flow_route_binding`: flow edge bound to a receipt route choice
- `155_skill_flow_branch`: branch edges with enum coverage
- `156_skill_flow_repeat`: nested flow repeat over a typed graph set
- `157_skill_graph_closure`: graph closure over roots, sets, and recovery refs
- `158_skill_graph_emit`: graph Markdown, contract, query JSON, D2, SVG, Mermaid, and source receipt
- `159_skill_graph_policy`: DAG, edge reason, route binding, durable checkpoint, and graph policy failures
- `160_skill_graph_relations_mentions`: `GRAPH.prompt`, skill relations, checked `{{skill:Name}}` refs, warnings, and receipt schemas
- `161_skill_graph_policy_allowances`: `dag allow_cycle "Reason"` for documented graph loops
- `162_skill_graph_negative_cases`: checked mention and skill relation failures
- `163_skill_graph_authoring_metadata`: skill inventory metadata, aliases, richer stage entry, repair and waiver text, and graph-path repeat targets
- `164_skill_graph_artifacts`: top-level durable artifact symbols, stage ownership, and artifact-typed stage inputs

Add unit tests for:

- parser model shape
- receipt inheritance and cycles
- package receipt by ref
- stage owner resolution
- stage support resolution
- stage input and emit type checks
- receipt route target checks
- skill relation target checks
- skill flow node and edge checks
- skill flow route binding checks
- skill flow DAG detection
- nested flow expansion
- repeat node lowering
- graph set resolution
- graph recovery metadata lowering
- checked skill mention interpolation
- graph policy behavior
- rendered Markdown tables
- emitted graph contract JSON
- emitted query graph JSON
- emitted Mermaid graph output
- emitted receipt schemas
- graph source receipt freshness
- verify statuses

Add diagnostic smoke fixtures for every new error code.

## Migration Path For `lessons_studio`

This spec does not change `../lessons_studio`, but it defines a later path:

1. Add top-level receipts for `FlowReceipt` and the main stage receipts.
2. Add top-level `skill` declarations that link to each emitted package.
3. Add top-level `stage` declarations for each stage contract row.
4. Move stage handoff choices into receipt route fields.
5. Model F1-F18 as `skill_flow` declarations.
6. Model `F1 per slot`, `F3 per section`, and affected-lesson flows as
   `repeat` nodes.
7. Add one `skill_graph StudioAuthoringGraph` with roots for the public flows.
8. Replace hand-maintained registry docs with generated graph views.
9. Replace `$skill-name` prose mentions with checked `{{skill:Name}}` refs
   where the text must be compiler-owned.
10. Run `verify_skill_graph` in CI beside `verify_skill_receipts`.

Steps 1-6 are additive and should not replace shipped runtime docs. Step 7
adds the graph boundary. Steps 8-10 replace hand-maintained views and should
wait until generated graph docs pass `verify_skill_graph` in CI.

The controller can then load a compact generated graph view instead of
maintaining F1-F18 order and stage contracts by hand.

## Rejected Alternatives

### Rejected: `skill_graph` Mega-Declaration

Do not make `skill_graph` a nested mini-language:

```prompt
skill_graph StudioSkillGraph: "Studio Skill Graph"
    skills:
        skill lesson_plan: package "studio-lesson-plan"
    stages:
        stage lesson_plan: "Lesson Plan"
    flows:
        flow authoring: "Authoring"
```

This creates one large root with duplicate declaration sites. It also makes
review hard because one block owns too many jobs.

The accepted design keeps graph members top-level and lets `skill_graph`
select them.

### Rejected: Stage-Local `next`

Do not put handoffs on stages:

```prompt
stage LessonPlan: "Lesson Plan"
    next:
        approve: "Approve" -> SituationSynthesis
```

Routing belongs on typed output. For stages, that typed output is the receipt.

### Rejected: Workflow-Only Graphs

Do not rely only on `workflow sequence` to model graph flows.

That was the first revision of this spec. It was too weak for the studio case.
It could model a straight list, but not a real graph with branch reasons,
repeat nodes, nested flows, safe variations, unsafe variations, and graph-level
emitted views.

`workflow` should still exist for agent instructions. `skill_flow` should own
the graph DAG.

## Final Shape

The core feature should look like this:

```prompt
skill Controller: "Controller"
    purpose: "Route graph work."
    package: "studio-authoring-flow-controller"

receipt FlowReceipt: "Flow Receipt"
    current_stage: string
    why_next_route: string
    route next_route: "Next Route"
        done: "Stop." -> terminal

stage RouteWork: "Route Work"
    owner: Controller
    emits: FlowReceipt
    intent: "Name the next safe graph route."
    checkpoint: diagnostic
    advance_condition: "Receipt names the current stage and next route."

skill_flow AuthoringFlow: "Authoring Flow"
    intent: "Route one authoring job."
    start: RouteWork

skill_graph AuthoringGraph: "Authoring Graph"
    purpose: "Expose the authoring flow as a checked graph."
    roots:
        flow AuthoringFlow
    policy:
        dag acyclic
        require edge_reason
        require relation_reason
        require route_targets_resolve
    views:
        graph_json: "references/skill-graph.json"
        flow_registry: "references/flow-registry.md"
```

That is the heart of the design.

It gives Doctrine a first-class skill graph with compiler-enforced structure,
clean generated views, and a simple machine surface for agents and harnesses.
