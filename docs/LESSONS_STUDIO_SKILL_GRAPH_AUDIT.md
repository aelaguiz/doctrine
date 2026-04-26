# Lessons Studio Skill Graph Audit

This audit looks at `../lessons_studio` as a real skill-graph use case.
It asks two questions:

1. Which shipped Doctrine features could make the graph safer today?
2. What should Doctrine add if we want skill graphs to be a first-class
   authoring surface?

The short answer: `lessons_studio` already uses Doctrine well for skill
package emit, source receipts, shared docs, and generated skill trees. The
main gap is that the skill graph itself is still mostly prose. Skill names,
stage owners, support skills, receipt shapes, route choices, and flow order are
written in Markdown tables and strings. That means Doctrine can compile each
skill, but it cannot prove that the graph is sound.

## Scope Checked

I inspected these surfaces:

- `../lessons_studio/pyproject.toml`
- `../lessons_studio/prompts/claude_home/SKILL.prompt`
- `../lessons_studio/skills/**/prompts/SKILL.prompt`
- `../lessons_studio/skills/**/prompts/refs/*.prompt`
- `../lessons_studio/skills/**/build/SKILL.source.json`
- `../lessons_studio/skills/studio-authoring-flow-controller/prompts/refs/flow_registry.prompt`
- `../lessons_studio/skills/studio-authoring-flow-controller/prompts/refs/stage_contracts.prompt`
- `../lessons_studio/scripts/build_skills.sh`
- `../lessons_studio/tests/test_doctrine_emit.py`
- `../lessons_studio/tests/test_psmobile_skill_source_of_truth.py`
- `../lessons_studio/tests/test_psmobile_skill_contracts.py`
- Doctrine docs and examples for skill packages, host contracts, receipt
  slots, modes, typed tables, output schemas, route contracts, and source
  receipts.

The studio worktree had user changes in several prompt files while I read it.
I treated it as read-only.

## Current Shape

The current graph has these counts:

| Item | Count | Notes |
| --- | ---: | --- |
| Emit targets | 43 | 42 skill targets plus the root instruction generator |
| Skill directories | 42 | All have emitted `SKILL.source.json` files |
| Local `skills/*/prompts/SKILL.prompt` packages | 34 | Studio-owned and wrapper skills |
| External `source_root` targets | 8 | psmobile primitive skills |
| Targets with `lock_file` | 8 | psmobile primitive skills only |
| `host_contract:` uses | 0 | No skill package declares typed host slots |
| `bind:` uses | 0 | No consuming agent binds a package contract |
| `package:` uses on inline `skill` declarations | 0 | No inline skill graph exists |
| `receipt` host slots | 0 | Run receipts are prose-only |
| `mode` bindings | 0 | No producer/audit/manual mode is typed |
| Emitted `SKILL.contract.json` files | 0 | Expected from zero host contracts |

The repo already uses strong source receipts. The eight psmobile primitive
targets point at `psmobile/skills/<name>/prompts/SKILL.prompt`, set
`source_root = "psmobile"`, set stable `source_id` values, and write
`doctrine.skill.lock`. That is the right shape for copied upstream skill
freshness.

The graph layer is different. The root home, flow registry, and stage
contracts use prose and Markdown tables to name skills and stages. Those names
look structured to a human, but they are not Doctrine references.

## What Is Strong Already

### Source freshness is real

The psmobile primitive skill targets use Doctrine source receipts and a lock
file. For example, `pyproject.toml` sets `source_root`, `source_id`, and
`lock_file` for `catalog-ops`, `concepts-ops`, `lessons-ops`,
`glossary-ops`, `poker-kb`, `fastcards`, `bq-telemetry`, and `doorstop`.

`tests/test_psmobile_skill_source_of_truth.py` also checks that psmobile-owned
skills are emitted from `psmobile`, not copied into local prompt source. That
is exactly the ownership line Doctrine should protect.

### Emit and receipt checks are part of tests

`tests/test_doctrine_emit.py` compiles every emit target and then runs
`doctrine.verify_skill_receipts` for each target. This catches stale emitted
trees and hand-edited build output.

`scripts/build_skills.sh` also emits all skill targets, verifies skill
receipts, and rewires `.claude/skills` and `.agents/skills`. That keeps the
runtime install path boring and repeatable.

### Shared references are imported instead of copied

The studio uses `additional_prompt_roots` for `shared/prompts` and
`psmobile/skills/shared/prompts`. Many skills import shared docs such as
`StudioOperatingDoctrine` and `DoorstopContract`, then re-emit them through
`emit:`. This is a good use of Doctrine's package source-root model.

### Skill descriptions are doing real resolver work

Most emitted skill descriptions state the layer, entry state, output, and
delegation boundary. That matches Doctrine's resolver-first bias. It also
makes the graph useful to current runtimes that only load `SKILL.md` files.

## Findings

### 1. The graph edges are prose, not compiler-owned references

Severity: high.

The root home lists skills by job family in a Markdown table. The stage
contract table names `owner_skill`, `supporting_skills`, and
`next_on_approve` as plain strings. The flow registry names stage order as
plain text like `lesson plan -> render -> situation synthesis`.

Evidence:

- `prompts/claude_home/SKILL.prompt` has the root skill inventory table at
  lines 191-200.
- `skills/studio-authoring-flow-controller/prompts/refs/stage_contracts.prompt`
  has `Owner skill`, `Supporting skills`, and `Next on approve` columns at
  lines 108-131.
- `skills/studio-authoring-flow-controller/prompts/refs/flow_registry.prompt`
  has flow stage order as prose at lines 21-40.

Why this matters:

Doctrine can prove that each skill package emits. It cannot prove that a stage
owner exists, that a support skill exists, that a route target is a real stage,
or that a flow's stage names map to canonical stage ids.

Smallest fix with shipped Doctrine:

- Declare closed `enum` values for `StageId`, `FlowId`, `StageStatus`,
  `DurableArtifactStatus`, and `SkillFamily`.
- Convert the flow and stage registries from raw Markdown tables into
  first-class `table` declarations with typed `row_schema` entries.
- Use `type: StageId` and `type: FlowId` wherever the current table uses
  string ids.

Best fix with new Doctrine support:

- Add top-level `stage`, `receipt`, and `skill_flow` declarations, then select
  them with a first-class `skill_graph`. Let the compiler resolve every skill,
  stage, route, and flow ref.
- Emit the Markdown tables from that graph instead of authoring the tables by
  hand.
- Emit `SKILL_GRAPH.contract.json` for harnesses and tests.

### 2. FlowReceipt and stage handoffs are prose-only contracts

Severity: high.

The controller tells the agent to emit a `FlowReceipt` with many required
fields. The stage contract file also lists recovery and handoff fields. Those
field names are not a schema. A future edit can rename, drop, or add a field
without a compiler error.

Evidence:

- `skills/studio-authoring-flow-controller/prompts/SKILL.prompt` line 59 says
  to emit a `FlowReceipt`.
- The same file lists required fields at lines 61-66.
- `stage_contracts.prompt` lists completion fields at lines 8-26 and handoff
  fields at lines 28-34.

Why this matters:

The controller is the safety-critical router for the graph. Its output is the
thing later stages trust. A missing `why_next_route`, wrong `current_stage`,
or free-form `durable_artifact_status` can let a run advance from stale chat
state.

Smallest fix with shipped Doctrine:

- Add a typed receipt slot to the controller skill package:
  `host_contract: receipt flow_receipt: "Flow Receipt"`.
- Type fields through enums and tables. Examples: `flow_id: FlowId`,
  `current_stage: StageId`, `durable_artifact_status:
  DurableArtifactStatus`, `completed_stages: list[StageLedgerRow]`.
- Do the same for reusable stage handoff receipts where a stage output becomes
  input to later work.

Best fix with new Doctrine support:

- Promote receipts to top-level reusable declarations, not only skill-package
  host slots.
- Let `stage` declarations name `emits: FlowReceipt` or
  `emits: StageReceipt`.
- Emit JSON Schema for each receipt and include it in the graph contract.

### 3. No skill package declares host facts or receipt facts

Severity: high.

The current graph has no `host_contract:`, no `bind:`, no inline `skill`
declarations with `package:`, no `receipt` slots, and no emitted
`SKILL.contract.json` files.

Evidence:

- A full prompt scan found zero exact uses of `host_contract:`, `bind:`,
  `package:`, `receipt` host slots, and `mode`.
- `skills/*/build/SKILL.contract.json` has no matches.

Why this matters:

Many skills name required upstream facts in prose. For example, `studio-lesson-plan`
requires the section lesson map, the section playable strategy, the analysis
packet, concepts, and burden inputs. `studio-playable-materializer` requires
the locked plan and situations. Those are real parameters. Today they are
method text, not compiler-bound slots.

Smallest fix with shipped Doctrine:

- Add a real consuming `AGENTS.prompt` or graph entrypoint that declares
  inline `skill` declarations with `package: "<skill-name>"`.
- For the highest-risk stage skills, declare `host_contract:` slots in their
  `SKILL.prompt` files.
- Bind those slots at the consuming skill entry.

Good early candidates:

- `studio-authoring-flow-controller`: `receipt flow_receipt`
- `studio-section-playable-strategy`: `document analysis_packet`,
  `document section_shape`, `receipt strategy_receipt`
- `studio-lesson-plan`: `document section_strategy`,
  `document analysis_packet`, `document concept_lock`,
  `receipt lesson_plan_receipt`
- `studio-playable-materializer`: `document lesson_plan`,
  `document situations`, `receipt materialization_receipt`
- `lesson-copy-discipline`: `receipt copy_baseline_receipt`

Best fix with new Doctrine support:

- Let a `skill package` declare package-to-package dependencies directly.
  Today `host_contract` works through a consuming agent skill entry. A skill
  graph needs package edges even when there is no concrete agent wrapping each
  skill.

### 4. The root skill inventory can drift from the real target set

Severity: medium.

The actual studio has 42 skill targets. The root inventory is a hand-authored
Markdown table. It omits at least one real skill target:
`curriculum-consistency-check`.

Evidence:

- `pyproject.toml` declares `curriculum-consistency-check` at lines 278-281.
- The root skill inventory table at `prompts/claude_home/SKILL.prompt`
  lines 191-200 does not include it.
- A scan of slash and dollar skill mentions found `curriculum-consistency-check`
  was the only skill directory never referenced by `$/` in the inspected
  sources.

Why this matters:

The root home is the discovery layer. If it omits a real skill, a runtime may
never load the right lane. This is the exact kind of drift Doctrine should
remove.

Smallest fix with shipped Doctrine:

- Generate the inventory from the emit target list or a typed table.
- Add an explicit "manual only" or "hidden from default flows" field for
  skills that should not be loaded by default.

Best fix with new Doctrine support:

- Let the graph contract record `category`, `visibility`, `manual_only`,
  `default_flow_member`, and `aliases` for each top-level skill.
- Emit the root skill inventory from the graph.
- Add a compile check: every emitted skill is either listed in one category or
  marked `hidden`.

### 5. The flow registry and stage contracts duplicate graph truth

Severity: medium.

The flow registry owns order. The stage contracts own owners, support skills,
advance conditions, and next owners. Root home also repeats canonical order in
plain prose.

Evidence:

- The controller says flow truth lives in the controller and should not be
  re-declared elsewhere at `SKILL.prompt` lines 34-41.
- The root home repeats the high-level canonical order at
  `prompts/claude_home/SKILL.prompt` lines 221-236.
- Flow order appears in `flow_registry.prompt` lines 23-40.
- Next-stage edges appear in `stage_contracts.prompt` lines 110-131.

Why this matters:

Some duplication is useful for always-on routing. But today there is no
source that emits the short root reminder, the detailed flow rows, and the
stage table from one graph. A future change can update one surface and miss
another.

Smallest fix with shipped Doctrine:

- Keep the controller as the single prose owner.
- Move the root home to a shorter pointer. It should say that the controller
  owns F1-F18 order, then point to the controller.
- Turn stage and flow rows into first-class tables so at least the table data
  has one source.

Best fix with new Doctrine support:

- Let the graph emit several views:
  - compact root summary
  - full `flow-registry.md`
  - full `stage-contracts.md`
  - machine graph JSON
  - flow and dependency diagram

### 6. Regex tests are filling gaps that the compiler should own

Severity: medium.

The studio has useful tests for stale command names and source-of-truth drift.
Some of those tests are proving graph and contract facts with regex or string
presence checks.

Evidence:

- `tests/test_psmobile_skill_contracts.py` checks primitive contracts by
  calling psmobile scripts at lines 55-107.
- The same file bans retired aliases by regex across active skill and home
  files at lines 109-158.
- It checks that specific command strings appear in skill prompts at lines
  165-195.

Why this matters:

These tests are valuable, but they are local guardrails. They do not give
Doctrine a reusable model for skill graphs. They also do not help another repo
write the same kind of graph without copying tests.

Smallest fix with shipped Doctrine:

- Keep the tests for product-specific primitive contracts.
- Move generic graph invariants into typed Doctrine source where possible.
- Add a generated graph artifact, even if first built by a repo script, so
  tests can compare graph truth instead of scraping prose.

Best fix with new Doctrine support:

- Add `doctrine.verify_skill_graph`.
- Let product tests focus on product truth, while Doctrine verifies graph
  closure, typed refs, modes, receipt schemas, and source receipt freshness.

### 7. The root instruction generator is using a skill package as a doc emitter

Severity: low to medium.

`prompts/claude_home/SKILL.prompt` is a `skill package` whose main job is to
emit `CLAUDE.md` and `AGENTS.md`. This works because `skill package` can emit
docs, but it also means the root home is not an `AGENTS.prompt` runtime home
with agent-level `skills`, `inputs`, `outputs`, or `final_output` semantics.

Evidence:

- `prompts/claude_home/SKILL.prompt` lines 1-10 define `StudioClaudeHome` as a
  skill package that only emits the root instruction files.
- The `studio-claude-home` emit target is in `pyproject.toml` lines 300-303.

Why this matters:

The root home is the natural place to declare the installed skill set and its
typed package links. Today it cannot do that with shipped agent-level
`skills:` blocks because it is a document emitted from a skill package.

Smallest fix with shipped Doctrine:

- Keep the doc emitter if it is working, but add a separate graph or
  `AGENTS.prompt` entrypoint that owns typed skill declarations.
- Generate the prose inventory from that entrypoint.

Best fix with new Doctrine support:

- Add a general `emit documents` target that does not require wrapping docs in
  a `skill package`.
- Or add a first-class `repo home` declaration that can emit both `CLAUDE.md`
  and `AGENTS.md` and also own typed installed-skill refs.

## Existing Doctrine Features To Use Now

### Skill package source receipts

The studio already uses this well for psmobile primitives. Keep it.

Consider extending the same rigor to local wrapper skills that depend on
repo-level files outside their package source root. If a wrapper's truth
depends on a local script, schema, or shared generated contract, use target
`source_root` and `source.track` when the current model can express it.

### First-class `document` and `table`

The controller references are currently `document` declarations whose bodies
are raw Markdown tables. Move the table content into first-class `table`
declarations with typed rows.

Useful tables:

- `SkillInventory`
- `StageContracts`
- `FlowRegistry`
- `StageStatusLedger`
- `FlowReceiptFields`
- `StageReceiptFields`

### Enums for closed vocabularies

The studio has many closed sets:

- `F1` through `F18`
- stage ids
- recovery statuses
- durable artifact statuses
- lane vocabulary
- visibility values such as default, explicit-only, manual-only, hidden
- modes such as producer, audit, router, renderer, diagnostic

Each should be an `enum` when a field depends on the value.

### Host contracts and `bind:`

Use `host_contract:` when a package needs facts from its caller. The current
stage skills are written like parameterized methods, so this feature fits.

The missing piece is a consuming graph. That can be a real `AGENTS.prompt`
entrypoint with inline `skill` declarations that link to the skill packages
through `package:`.

### Receipt slots

Use `receipt` host slots for the controller and high-risk stages. This is the
shipped feature that best matches `FlowReceipt`, proof receipts, baseline
receipts, and stage handoff receipts.

### Skill binding mode

Use `mode` for skills that are valid in more than one posture. Examples:

- producer versus audit
- route selection versus recovery audit
- read-only diagnostic versus mutating stage
- baseline load versus copy execution

This would help distinguish audit-only flows such as F15-F17 from producer
flows without forking the whole skill surface.

### Output schemas and final output contracts

If the controller becomes an agent-like runtime entrypoint, model its
turn-ending `FlowReceipt` as structured `final_output:`. Doctrine can then
emit `final_output.contract.json` and a JSON Schema.

This may be too heavy for every skill. It is a good fit for the controller
because its output controls the next route.

### `emit_flow`

The studio wants a graph view. Today `emit_flow` is agent-flow oriented, not
skill-graph oriented. Still, if the root graph moves into an `AGENTS.prompt`
surface, existing flow diagrams may become useful for the controller path.

Long term, Doctrine should have a dedicated `emit_skill_graph`.

## New Doctrine Support Worth Adding

This section puts cost aside. It describes the best possible design if
Doctrine made skill graphs first-class.

### 1. First-class graph declarations

Add top-level declarations that compose into a graph:

```prompt
skill CatalogOps: "Catalog Ops"
    purpose: "Write exact catalog facts."
    package: "catalog-ops"

receipt SectionPlayableAnalysisReceipt: "Section Playable Analysis Receipt"
    status: StageStatus
    route next_route: "Next Route"
        approve: "Continue to strategy." -> stage SectionPlayableStrategy

stage SectionPlayableAnalysis: "Section Playable Analysis"
    owner: StudioSectionPlayableAnalysis
    supports:
        CatalogOps
        LessonsOps
        BqTelemetry
        StudioUserRender
    emits: SectionPlayableAnalysisReceipt
    intent: "Build a no-conclusions evidence packet before strategy."
    durable_target: "Section doorstop `## Template`."
    durable_evidence: "`catalog-ops spine write` receipt."
    advance_condition: "Packet exists, is current, and has no recommendation."

skill_flow F3BuildSection: "F3 - Build A Section"
    start: SectionShape
    edge SectionPlayableAnalysis -> SectionPlayableStrategy:
        route: SectionPlayableAnalysisReceipt.next_route.approve
        why: "Strategy must consume the approved evidence packet."

skill_graph StudioAuthoringGraph: "Studio Authoring Graph"
    roots:
        flow F3BuildSection
    policy:
        dag acyclic
        require edge_reason
    views:
        flow_registry: "references/flow-registry.md"
        stage_contracts: "references/stage-contracts.md"
        graph_json: "references/skill-graph.json"
```

The syntax above is only a sketch. The key point is that `skill_graph` selects
top-level graph members. It does not redeclare them inline.

Compiler checks:

- every stage owner exists
- every support skill exists
- every receipt route target exists or is marked `human`, `author_decision`, or
  `external`
- no stage id is duplicated
- every `skill_flow` id is unique
- every stage named by a `skill_flow` exists
- every nested flow expands without cycles unless explicitly marked
  iterative
- every required receipt type exists
- every route-bound edge matches the target named by its receipt route choice
- every skill is in a category or marked hidden
- every manual-only skill is absent from default flows unless explicitly
  allowed

### 2. Package-to-package dependencies

Today a package can declare host slots, and an agent skill entry can bind
them. A skill graph also needs direct package edges:

- `requires`
- `delegates_to`
- `wraps`
- `audits`
- `baseline_for`
- `blocks`
- `owns_surface`
- `reads_surface`
- `writes_surface`

These edges should compile to docs and graph JSON. They should also feed
warnings such as "this skill says it delegates to X in prose, but the graph
does not list X."

### 3. First-class stage declarations

A `stage` should be more than a row in a Markdown table.

Fields worth supporting:

- `owner`
- `support`
- `applies_to`
- `intent`
- `entry`
- `durable_target`
- `durable_evidence`
- `advance_condition`
- `risk_guarded`
- `forbidden_outputs`
- `emits`
- receipt route fields for next-stage choices
- `repair_routes`
- `waiver_policy`

Some of these fields are prose. Some are typed refs. The compiler does not
need to understand every sentence. It should own the ids, refs, receipts, and
closed vocabularies.

### 4. First-class `skill_flow` declarations

The flow registry should be generated from typed `skill_flow` declarations.

Needed features:

- ordered stages
- nested flow calls such as "F1 per slot"
- optional stages
- conditional stages
- audit-only flows
- repair loops
- author gates
- safe variations
- unsafe variations
- final route

The graph should emit a human registry and a machine graph.

### 5. Artifact and durable target contracts

Skill graphs depend on durable artifacts. Today these are strings such as
`Section doorstop ## Template` or `Lesson doorstop ## Situations`.

Doctrine should add an `artifact` or `durable_target` declaration:

```prompt
artifact SectionPlayableAnalysisPacket: "Section Playable Analysis Packet"
    path_family: SectionDoorstop
    section: "Template"
    anchor: "Section Playable Analysis Packet"
    owner: section_playable_analysis
```

Compiler checks:

- target ids resolve
- anchor names are unique within the graph
- only the owning stage writes the artifact
- downstream stages can require the artifact by symbol
- root docs can show the path shape without copying it

This stays on the authoring side. It does not read the live file system or
own runtime state.

### 6. Reusable receipt declarations

Receipt slots are useful today, but skill graphs need reusable receipt types.

Add a top-level `receipt` declaration or make `schema` easier to use as a
receipt envelope:

```prompt
receipt FlowReceipt: "Flow Receipt"
    flow_id: FlowId
    current_stage: StageId
    durable_artifact_status: DurableArtifactStatus
    next_route: RouteTarget
    why_next_route: MarkdownLine
```

Then stages and packages can say `emits: FlowReceipt`.

Compiler output:

- Markdown contract
- JSON Schema
- receipt refs in `SKILL.contract.json`
- graph contract refs

### 7. Skill mention refs in prose

The studio writes `$catalog-ops` and `/catalog-ops` in many places. Today
those are just text.

Doctrine should support explicit skill refs in prose, such as:

```prompt
"Use {{skill:catalog_ops}} for exact catalog writes."
```

or a readable form:

```prompt
skill_ref catalog_ops
```

Compiler checks:

- the skill exists
- the emitted display name is correct
- renames update safely
- unknown skill ids fail loud

This is a small feature with high value. It would catch stale skill names
without needing a full `skill_graph` declaration first.

### 8. Skill graph warnings

Some problems should be warnings before hard errors:

- skill exists but is not in any inventory
- skill is in inventory but no emitted target exists
- support skill is listed but never mentioned in the owner skill
- prose mentions a skill that is not in the graph
- manual-only skill appears in a default flow
- two skills both claim to own the same artifact
- a route-bound edge skips a required upstream stage
- a flow has stage names that only match by fuzzy prose

These fit Doctrine's planned warning layer because they are structural and
generic.

### 9. Transitive source receipts

`SKILL.source.json` proves one emitted package tree. A skill graph also needs
a graph-level receipt.

Add `SKILL_GRAPH.source.json` or include graph hashes in a normal source
receipt. It should record:

- skill graph source files
- emitted skill package receipt hashes
- graph JSON hash
- graph Mermaid hash, when a Mermaid view is emitted
- generated registry docs
- generated root inventory docs

That would let downstream repos ask one question: is the installed skill
graph current?

### 10. Graph-aware install and verification

Add commands:

```bash
uv run --locked python -m doctrine.emit_skill_graph --target studio_graph
uv run --locked python -m doctrine.verify_skill_graph --target studio_graph
```

Verifier checks:

- every skill package receipt is current
- every declared graph edge resolves
- every emitted graph doc matches source
- every installed skill has a current emitted tree
- every root inventory entry is generated from the graph

## Best Possible Outcome

The ideal end state is this:

`lessons_studio` authors one typed skill graph. That graph owns the list of
skills, skill categories, stage owners, support skills, flow order, allowed
variations, durable artifacts, receipt shapes, and manual-only lanes.

Doctrine emits from that graph:

- `.claude/skills/<name>/SKILL.md`
- `.agents/skills` wiring
- root skill inventory for `AGENTS.md` and `CLAUDE.md`
- `flow-registry.md`
- `stage-contracts.md`
- `skill-graph.md`
- `skill-graph.svg`
- `skill-graph.mmd` on request for Mermaid-native docs
- `SKILL_GRAPH.contract.json`
- receipt schemas
- source and graph receipts

Doctrine verifies:

- no missing skill refs
- no orphan emitted skills unless marked hidden
- no unknown stage owners
- no broken receipt route targets or route-bound edges
- no untyped required receipts
- no stale source receipts
- no generated doc drift
- no duplicate artifact owners
- no default flow that invokes a manual-only skill

The runtime still stays thin. It reads `SKILL.md` files and root instructions.
The harness still owns scheduling, state, tool execution, and memory. Doctrine
owns the authoring graph and emits the portable facts a runtime can consume.

That outcome would make skill graphs feel like normal Doctrine:

- small source
- explicit refs
- typed contracts
- generated runtime docs
- fail-loud drift checks
- one owner for shared truth

## Suggested Path

### Phase 1: Use shipped features

1. Add enums for flow ids, stage ids, recovery statuses, and durable artifact
   statuses.
2. Convert `FlowRegistry` and `StageContracts` from raw Markdown tables to
   first-class tables.
3. Add typed receipt slots to the controller and highest-risk stage packages.
4. Add top-level `skill` declarations with `package:` links in the graph
   entrypoint or a shared imported file.
5. Generate or test the root inventory against the real emit target list.
6. Add `curriculum-consistency-check` to the root inventory or mark it hidden.

### Phase 2: Add small Doctrine features

1. Add explicit `{{skill:...}}` refs in prose.
2. Add a graph verifier that checks stage owner and support skill refs from a
   first-class table.
3. Add graph warnings for orphan skills and manual-only/default-flow conflicts.
4. Add reusable receipt declarations or make receipt schemas importable outside
   `host_contract`.

### Phase 3: Make skill graphs first-class

1. Add `skill_graph`, `stage`, and `skill_flow` declarations.
2. Emit graph Markdown, JSON, and SVG.
3. Emit graph source receipts and verify them.
4. Move root inventory, flow registry, and stage contracts to generated views.
5. Keep product-specific primitive contract tests in `lessons_studio`, but let
   Doctrine own graph closure and typed drift checks.

## Final Verdict

`lessons_studio` is a strong proof that Doctrine needs first-class skill graph
support. It already shows the right product shape: many small skills, clear
owners, generated packages, source receipts, and a real controller. The weak
part is not the skill content. The weak part is the graph substrate.

Today the graph is a human-readable convention. The best next step is to make
the graph a compiler-readable contract.
