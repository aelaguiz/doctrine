# Lessons Prompt Prose Buckets V2 Proposal

Date: 2026-04-10

## Status

This document is a second unconstrained design pass.

It keeps the same self-contained format as
[`LESSONS_PROSE_BUCKETS_V1_PROPOSAL_2026-04-10.md`](LESSONS_PROSE_BUCKETS_V1_PROPOSAL_2026-04-10.md),
but it follows a different design doctrine:

- keep Doctrine's current top-level skeleton
- do not spend design capital renaming declarations that are already earned
- promote recurring law into first-class statements inside the existing
  structure
- add one genuinely earned new primitive: `review`
- keep seam identity, tone, rationale, and other judgment-heavy prose as prose

Each bucket below shows:

- the live current Lessons examples
- what the bucket is doing today
- the v2 source proposal
- the changed rendered Markdown

## Goal

The original prose-buckets document identified eleven recurring prose families.

The key question is not "how do we make the syntax prettier?"

The key question is:

Which recurring prose jobs should become formal statements, and which should
stay human prose?

This v2 answer is narrower than v1.

It says Doctrine should mostly keep its current declaration skeleton and gain a
small law vocabulary inside `workflow`, `output`, and a new `review`
declaration.

## Corpus And Grounding

Representative live files read for this proposal:

- `../paperclip_agents/doctrine/prompts/lessons/common/role_home.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/common/skills.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/outputs/outputs.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/dossier.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/metadata_wording.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/lesson_situations.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/copy_grounding.prompt`

This proposal also uses the current Doctrine docs as constraints on design
taste:

- explicit typed declarations are good
- explicit ordered patching is good
- top-level workflows remain canonical reusable structure
- richer output contract material belongs on `output`
- avoid widening into packets, root binding, or runtime-tooling surfaces too
  early

## Design Thesis

Doctrine does not need ten new top-level primitives.

It needs a small statement vocabulary for law.

The recurring drift is not coming from imports, inheritance syntax, or top-level
declaration names. It is coming from the fact that activation conditions,
authority rules, scope limits, preservation rules, proof obligations, and
review gates are still being authored as prose paragraphs.

So the design move is:

- keep the current top-level declaration skeleton
- formalize the recurring semantic jobs inside those declarations
- leave everything else as prose

## What Stays Prose Vs Becomes Logic

Keep as prose:

- role and seam identity
- tone / vibe
- explanatory rationale
- quality-bar language that is judgment-heavy rather than mechanically checkable

Make formal:

- work ordering
- current-truth and authority selection
- output normalization
- lane boundaries
- mode activation
- evidence and proof obligations
- review gates and verdict law
- routing and owner transition
- preservation and anti-drift law
- skill routing

## Proposed V2 Surface

### Existing Declarations Stay

```prompt
import ...
enum ...
input ...
output ...
skill ...
workflow ...
agent ...
abstract agent ...
```

### One New Declaration

```prompt
review Name: "Title"
```

### New Statement Forms

```prompt
when <expr>:
match <expr>:
step "Title":
must <predicate>
forbid <predicate>
preserve <ref-or-path>
own only <ref-or-path[, ...]>
current <ref>
support_only <ref>
ignore <ref>
must include <field-or-path[, ...]>
section "Title" when <expr>:
must emit <artifact-or-proof-shape>
compare <left> with <right> for <reason>
route "Label" -> Agent when <expr>
accept when <predicate>
reject when <predicate>
use Skill when <expr>
```

This is the whole move.

No packet system.
No new macro language.
No general theorem prover.
Just a small law vocabulary that fits the prose jobs the corpus already keeps
repeating.

## Quick Headline

V1 tried to imagine Doctrine as maximally symbolic.

V2 is stricter about where symbolism belongs:

- declarations stay recognizable
- seam identity mostly stays prose
- law becomes explicit only where the corpus has clearly earned it

That makes v2 feel more compatible with current Doctrine design notes while
still solving the actual source of drift.

## Bucket Map

| Bucket | V2 treatment |
| --- | --- |
| Role and seam identity | Keep as prose; no language change |
| Turn protocol and work ordering | `step` |
| Current-truth and authority selection | `current`, `support_only`, `ignore` |
| Output-shape and readback normalization | `must include`, `section ... when`, `forbid` |
| Lane boundaries and non-goals | `own only`, `forbid` |
| Conditional modes and branch activation | `when`, `match`, enums |
| Evidence, proof, and comparison obligations | `must emit`, `table`, `compare` |
| Review gates and verdict law | `review`, `accept when`, `reject when` |
| Routing and owner transition | `route ... -> Agent when ...` |
| Preservation and anti-drift constraints | `preserve` |
| Tool delegation and specialist skill routing | `use Skill when ...` |

## Worked Example: `RouteOnlyTurns`

This is still the best compact example because the current English is secretly
doing several jobs at once:

- branch activation
- output contract law
- downstream ownership
- fallback routing

### Before: Current Lessons Example

```prompt
workflow RouteOnlyTurns: "Routing-Only Turns"
    "Use this route when no specialist output file is current yet and the live job is routing, process repair, or owner repair."
    "Keep the current issue plan and the current issue comment explicit about the next owner and the next step."
    "When a section is being authored fresh or completely rewritten, indicate Rewrite Mode. That means {{lessons.common.agents.LessonsMetadataCopywriter:name}} will later rewrite final `{{lessons.contracts.metadata_wording.SectionMetadataFileOutput:target.path}}` `name` and `description` after upstream review instead of inheriting old section metadata."
    "When the same critic miss comes back again, put one short `{{ProjectLeadCommentLabels:repeated_problem}}` section in the routing comment."
    "Say what keeps failing, which role it came back from, and the next concrete fix."
    "If it is still unclear which specialist should go next, keep the issue on {{lessons.common.agents.LessonsProjectLead:name}} instead of pretending the next step is settled."
```

### What This Is Doing Today

- activating a branch
- imposing output-shape law on the routing comment
- declaring deferred ownership for metadata wording
- giving a fallback owner when routing is still unclear

### Proposed V2 Syntax

```prompt
output RouteOnlyHandoffOutput: "Routing Or Publish Comment"
    target: IssueComment
        issue: "What you're routing or following up in plain language"
    shape: RouteOnlyCommentText
    requirement: Required

    must include current_route, next_owner, next_step

    section "Repeated Problem" when critic_miss.repeated:
        must include failing_pattern, returned_from, next_fix


workflow RouteOnlyTurns: "Routing-Only Turns"
    when current.specialist_output is None and live_job in {routing, process_repair, owner_repair}:
        must RouteOnlyHandoffOutput.include(next_owner)
        must RouteOnlyHandoffOutput.include(next_step)

        when section.status in {new, full_rewrite}:
            must RouteOnlyHandoffOutput.include(rewrite_mode)
            route "Metadata wording is owed later" -> lessons.common.agents.LessonsMetadataCopywriter when upstream.review.accepted

        route "Keep the issue on Project Lead" -> lessons.common.agents.LessonsProjectLead when next_owner is unknown
```

### Rendered Markdown

```md
## Routing-Only Turns

Active when no specialist output file is current and the live job is routing,
process repair, or owner repair.

The routing comment must name the next owner and the next step.

If the section is new or full rewrite, the routing comment must mark Rewrite
Mode, and later section metadata wording belongs to Lessons Metadata
Copywriter.

If the same critic miss repeats, include a **Repeated Problem** section naming
what keeps failing, which role returned it, and the next concrete fix.

If the next owner is still unclear, keep the issue on Lessons Project Lead.
```

### What Changed

- branch activation became `when`
- comment law moved onto the output contract
- repeated-problem rendering became a conditional output section
- downstream ownership became an explicit route

## 1. Role And Seam Identity

V2 makes no language change here.

The corpus needs human-readable seam identity here more than symbolic law, and
rewriting that prose is not a useful language proposal.

### Before: Current Lessons Examples

```prompt
agent LessonsProjectLead[lessons.common.role_home.LessonsAgent]:
    role: "You are Lessons Project Lead. You hand work to the right specialist, keep one clear owner on the same issue, and pull it back to yourself only when routing, process repair, or publish follow-up is the real job."

workflow ProjectLeadJob: "Your Job"
    "Keep work moving with one clear owner and one real next step at a time."
    "Keep each role doing its own job. Do not absorb specialist authoring work just because the request is urgent."
```

```prompt
agent LessonsAcceptanceCritic[lessons.common.role_home.LessonsAgent]:
    role: "You are Lessons Acceptance Critic. You review the work other agents hand you and decide whether it is ready for the next step. You do not produce lesson content yourself."

skill AnswerOptionCopySkill: "psmobile-lesson-answer-option-copy"
    purpose: "Keep learner-visible answer options mutually exclusive, canonical, and screen-fit."
```

What this bucket is doing today:

- establishing seam ownership
- defining the improved world state for that seam
- preventing the role from collapsing into a generic helper

Cross-file connection:

- top-level `role:` text carries human seam identity
- `Your Job` workflows reinforce that identity operationally
- skill `purpose` text refines sub-seams inside a lane

### Proposed V2 Syntax

No language change proposed.

Keep `role:` and adjacent seam prose exactly in the ordinary prose layer.

### Rendered Markdown

No renderer change proposed.

The rendered Markdown for this bucket should stay whatever the authored prose
already says.

### Why This Is Better

- it makes clear that bucket 1 is out of scope for formalization
- it avoids nitpicking author word choice under the banner of language design
- it keeps v2 focused on the buckets that actually want new statement forms

## 2. Turn Protocol And Work Ordering

This bucket wants formal sequencing.

### Before: Current Lessons Examples

```prompt
workflow HowToTakeATurn: "How To Take A Turn"
    turn_sequence: "Turn Sequence"
        "1. Read all upstream materials in order..."
        "2. Do your own analysis work first. Name the specific tables, checks, comparisons, or grounding work that drive the decision before you write outputs."
        "3. Craft or update the output files that now matter."
        "4. Close the turn cleanly..."
        required "5. Leave one clear comment according to the handoff rules below."
        required "6. Reassign the same issue to the next owner."
        "7. Then end your turn."
```

```prompt
workflow LessonSituationsAnalysis: "Lesson Situations Analysis Steps"
    intro: "Introduction"
        "This analysis is the real rep-selection work in this role. Run it in order, then map it directly into the lesson situations file."
```

What this bucket is doing today:

- forcing read-before-write
- forcing analysis-before-output
- forcing closeout and handoff discipline
- making the workflow sequence inspectable instead of implied

Cross-file connection:

- `common/role_home.prompt` defines the universal turn frame
- contract workflows define lane-specific ordered analysis inside that frame

### Proposed V2 Syntax

```prompt
workflow HowToTakeATurn: "How To Take A Turn"
    step "Read upstream materials":
        must read issue.active
        must read plan.current or plan.parent_if_issue_points_there
        must read comment.latest_current
        must read upstream.files.required_by_lane

    step "Do analysis first":
        must name analysis.tables_checks_comparisons
        use lessons.common.skills.ParaMemoryFilesSkill when relevant_memory_exists

    step "Update the current outputs":
        must write lane.current_outputs

    step "Close the turn":
        must render lessons.outputs.outputs.HandoffOutput
        must reassign same_issue to next_owner
```

### Rendered Markdown

```md
## How To Take A Turn

1. Read the active issue, the current issue plan or current parent plan when
   the issue points there, the latest current comment, and the upstream files
   your lane depends on.
2. Do the analysis first and name the tables, checks, or comparisons that
   drove the decision. Use `ParaMemoryFilesSkill` when relevant memory exists.
3. Update the current outputs for your lane.
4. Render the handoff comment and reassign the same issue to the next owner.
```

### Why This Is Better

- sequencing becomes real statement structure
- the author stops encoding order inside numbered prose
- downstream diagnostics can fail on a specific step

## 3. Current-Truth And Authority Selection

This bucket wants explicit authority statements.

### Before: Current Lessons Examples

```prompt
workflow HowToTakeATurn: "How To Take A Turn"
    read_current_work_state: "Read Current Work State"
        "- Use the current issue plan and the latest issue comment that names the current files as the work state."
        "- If current roots, current files, or current review files are still too unclear to keep working without guessing, stop specialist work and route the same issue to {{lessons.common.agents.LessonsProjectLead:name}}."

workflow LegacyAndOldAuthoringFiles: "Legacy And Old Authoring Files"
    legacy_by_default: "Legacy By Default"
        "Old same-folder authoring files are not current truth by default."
        "Only a later section that names one of those files as conditional support may revive it, and even then it stays support evidence rather than current truth."
```

```prompt
output HandoffOutput: "Producer Handoff Comment"
    must_include: "Must Include"
        use_now: "What To Use Now"
            "Name the main file the next person should use now."
            "If the next person would not find proof just by opening that file, name the exact proof location."

output LessonSituationsFileOutput: "Lesson Situations File"
    notes: "Notes"
        "If a section hand-usage ledger exists, treat it as support evidence only. Do not make it a second current contract beside this file."
```

What this bucket is doing today:

- picking the live source of truth
- demoting support evidence so it cannot compete with the primary artifact
- preventing nearby old-file confusion
- making the handoff comment explain what is current right now

Cross-file connection:

- the shared role home sets top-level currentness rules
- outputs encode how currentness must be named in comments
- lane contracts add support-only and ignore-by-default rules

### Proposed V2 Syntax

```prompt
workflow CurrentWorkState: "Read Current Work State"
    current issue.plan.current
    current comment.latest_current
    support_only section.hand_usage_ledger
    ignore legacy.same_folder_authoring_files
    ignore under_construction.outputs_from_other_lanes

    route "Current work state is unclear" -> lessons.common.agents.LessonsProjectLead when unclear(current.roots, current.files, current.review_files)
```

### Rendered Markdown

```md
## Read Current Work State

Current truth comes from the current issue plan and the latest current comment.

Treat the section hand-usage ledger as support evidence only.

Ignore old same-folder authoring files and under-construction outputs from
other lanes unless a later rule explicitly revives them as support.

If current roots, current files, or current review files are unclear, route
the same issue to Lessons Project Lead.
```

### Why This Is Better

- `current`, `support_only`, and `ignore` separate authority classes cleanly
- currentness law stops competing with handoff advice in the same prose block
- unclear authority becomes a direct routing statement

## 4. Output-Shape And Readback Normalization

This bucket belongs on `output`.

### Before: Current Lessons Examples

```prompt
output HandoffOutput: "Producer Handoff Comment"
    must_include: "Must Include"
        analysis_performed: "Analysis Performed"
            "Put the actual analysis in this field..."
            "A label like `learner-history table` or `compared nearby lessons` is not enough by itself."

        output_contents_that_matter: "Output Contents That Matter"
            "Put the actual output contents that matter for pickup in this field..."
            "Do not reduce this to section names or headings."
```

```prompt
output RouteOnlyHandoffOutput: "Routing Handoff Comment"
    must_include: "Must Include"
        current_route: "Current Status"
            "Say the current routing status, publish state, or process state now in force."
        next_step: "Next Step"
            "Say the next concrete step now."
        next_owner: "Next Owner"
            "Name the next owner when ownership is changing now. If the earliest clear owner is still unclear, say plainly that {{lessons.common.agents.LessonsProjectLead:name}} keeps the issue."

workflow CopyGroundingHandoffLabels: "Copy Handoff Labels"
    repeated_shape_handling: "How Repeated Lesson Shapes Were Handled"
        "Use this exact handoff table label when the pass explains how it handled repeated lesson shapes or repeated field patterns."
```

What this bucket is doing today:

- normalizing handoff structure
- requiring actual analysis and actual readback
- making conditional sections and exact labels reusable
- keeping routing turns from inventing fake specialist artifacts

Cross-file connection:

- `outputs.prompt` defines the shared schema
- agents and contracts add local render obligations and labels

### Proposed V2 Syntax

```prompt
output HandoffOutput: "Producer Handoff Comment"
    target: IssueComment
        issue: "What you're working on in plain language"
    shape: HandoffCommentText
    requirement: Required

    must include what_changed, analysis_performed, output_contents_that_matter, use_now, next_owner

    forbid analysis_performed.label_only
    forbid output_contents_that_matter.heading_only


output RouteOnlyHandoffOutput: "Routing Handoff Comment"
    target: IssueComment
        issue: "What you're routing or following up in plain language"
    shape: RouteOnlyCommentText
    requirement: Required

    must include current_route, analysis_performed, output_contents_that_matter, next_step, next_owner

    section "Repeated Problem" when critic_miss.repeated:
        must include failing_pattern, returned_from, next_fix
```

### Rendered Markdown

```md
## Producer Handoff Comment

The handoff must include `What Changed`, `Analysis Performed`,
`Output Contents That Matter`, `What To Use Now`, and `Next Owner`.

Do not reduce `Analysis Performed` to a label alone.
Do not reduce `Output Contents That Matter` to headings alone.

## Routing Handoff Comment

The routing handoff must include the current status, the routing analysis, the
route-level readback, the next step, and the next owner.

When the same critic miss repeats, include a **Repeated Problem** section
stating what keeps failing, which role returned it, and the next concrete fix.
```

### Why This Is Better

- output normalization remains an output concern
- conditional section emission becomes explicit
- "real readback, not a pointer" becomes law instead of advisory prose

## 5. Lane Boundaries And Non-Goals

This bucket wants `own only` and `forbid`.

### Before: Current Lessons Examples

```prompt
workflow ProjectLeadJob: "Your Job"
    "Keep each role doing its own job. Do not absorb specialist authoring work just because the request is urgent."
    "Do not invent a fake specialist file or comment when the live job is routing, process repair, or publish follow-up."
```

```prompt
workflow MetadataWordingWorkflow[...]: "Metadata Wording Workflow"
    override intro: "Introduction"
        "This workflow is the late metadata wording pass for one current file. It is not general lesson copy and it is not section structure."

output CopyManifestFileOutput: "Updated Lesson Manifest File"
    must_include: "Must Include"
        lesson_title_stays_out_of_scope: "Lesson Title Stays Out Of Scope"
            "Do not use this pass to rewrite top-level `title`."
```

```prompt
output SectionDossierFileOutput: "Section Dossier File"
    notes: "Notes"
        "Do not create `SECTION_CONTINUITY.md` or another side file for the continuity call."
```

What this bucket is doing today:

- stopping scope creep
- preventing helpful lane collapse
- keeping each artifact small and purpose-built
- reducing overlap between neighboring lanes

Cross-file connection:

- role jobs set high-level boundaries
- workflow intros restate them where a seam is easy to widen
- contract notes often restate the same boundary as file-law

### Proposed V2 Syntax

```prompt
workflow MetadataCopywriterJob: "Your Job"
    own only (
        lessons.contracts.metadata_wording.SectionMetadataFileOutput.name,
        lessons.contracts.metadata_wording.SectionMetadataFileOutput.description,
    ) when handoff.mode == lessons.contracts.metadata_wording.MetadataPassMode.section

    own only lessons.contracts.metadata_wording.LessonTitleManifestFileOutput.title when handoff.mode == lessons.contracts.metadata_wording.MetadataPassMode.lesson_title

    forbid general_lesson_copy
    forbid section_structure_changes
    forbid routing_takeover
    forbid create("SECTION_CONTINUITY.md")
```

### Rendered Markdown

```md
## Your Job

If the active mode is `section`, this pass owns only section `name` and
`description`.

If the active mode is `lesson_title`, this pass owns only the lesson title.

This pass may not take over general lesson copy, section structure, routing, or
create `SECTION_CONTINUITY.md`.
```

### Why This Is Better

- scope becomes explicit and narrow
- non-goals become formal and reviewable
- "this seam must not silently widen" becomes real law

## 6. Conditional Modes And Branch Activation

This bucket wants `when`, `match`, and enums.

### Before: Current Lessons Examples

```prompt
workflow RouteOnlyTurns: "Routing-Only Turns"
    "Use this route when no specialist output file is current yet and the live job is routing, process repair, or owner repair."
    "When a section is being authored fresh or completely rewritten, indicate Rewrite Mode."
```

```prompt
workflow MetadataWordingWorkflow[...]: "Metadata Wording Workflow"
    override intro: "Introduction"
        "Work in exactly one mode per turn: `{{MetadataPassMode:lesson_title}}` or `{{MetadataPassMode:section}}`."

    mode_scope: "Mode Scope"
        "In `{{MetadataPassMode:lesson_title}}`, the current file is `{{LessonTitleManifestFileOutput:target.path}}` and only `title` is in scope."
        "In `{{MetadataPassMode:section}}`, the current file is `{{SectionMetadataFileOutput:target.path}}` and only `name` and `description` are in scope."
        "Do not treat both files as current in one turn."
```

```prompt
output LessonSituationsFileOutput: "Lesson Situations File"
    must_include: "Must Include"
        exact_move_boundary: "Exact-Move Boundary"
            "Say whether exact-move proof is in scope and why."
            "If it is in scope, name the one concrete kept rep or built spot that really teaches or grades one exact action."
            "If it is out of scope, say plainly what the lesson is teaching instead..."
```

What this bucket is doing today:

- selecting the active branch
- narrowing what is in scope in that branch
- making downstream obligations conditional
- preventing the reader from guessing which mode is live

Cross-file connection:

- rewrite status starts in the dossier
- metadata wording uses a strict mode split
- lesson situations uses exact-move scope as another branch surface

### Proposed V2 Syntax

```prompt
workflow MetadataCopywriterJob: "Your Job"
    must handoff.mode in lessons.contracts.metadata_wording.MetadataPassMode
    must handoff.current_file in {
        lessons.contracts.metadata_wording.LessonTitleManifestFileOutput,
        lessons.contracts.metadata_wording.SectionMetadataFileOutput,
    }

    match handoff.mode:
        lessons.contracts.metadata_wording.MetadataPassMode.lesson_title:
            own only lessons.contracts.metadata_wording.LessonTitleManifestFileOutput.title

        lessons.contracts.metadata_wording.MetadataPassMode.section:
            own only (
                lessons.contracts.metadata_wording.SectionMetadataFileOutput.name,
                lessons.contracts.metadata_wording.SectionMetadataFileOutput.description,
            )

    forbid both_metadata_files_current
```

### Rendered Markdown

```md
## Your Job

The handoff must name one active metadata mode and one current metadata file.

If mode is `lesson_title`, this pass owns only the lesson title.

If mode is `section`, this pass owns only section `name` and `description`.

Do not treat both metadata files as current in one turn.
```

### Why This Is Better

- mode selection becomes first-class law
- scope attaches directly to branch selection
- the author stops hiding mutually exclusive modes inside prose paragraphs

## 7. Evidence, Proof, And Comparison Obligations

This bucket wants `must emit` and `compare`.

### Before: Current Lessons Examples

```prompt
output HandoffOutput: "Producer Handoff Comment"
    must_include: "Must Include"
        analysis_performed: "Analysis Performed"
            "Put the actual analysis in this field..."

        output_contents_that_matter: "Output Contents That Matter"
            "Put the actual output contents that matter for pickup in this field..."
```

```prompt
output LessonSituationsFileOutput: "Lesson Situations File"
    must_include: "Must Include"
        candidate_pools: "Candidate Pools"
            "Keep the candidate pool for each step, not just the winners."
        variety_and_pattern_proof: "Variety And Pattern Proof"
            "Name the nearby accepted lesson situations or nearby accepted lessons you checked for adjacent showcase-hand overlap..."
            "If a repeated hand family stays, say plainly what contrast ... still makes both lessons earn their place..."
```

```prompt
workflow DossierReviewContract: "Shared Dossier Review Contract"
    "At minimum confirm `{{SectionDossierFileOutput:must_include.grounding_and_open_questions}}` shows the actual returned receipts for kept section truth, kept next-capability rows, or kept advancement claims instead of plausible summaries..."
```

What this bucket is doing today:

- requiring visible evidence, not vibes
- requiring actual tables, rows, receipts, and comparisons
- making downstream review possible without reconstruction
- preventing a handoff comment from collapsing into a title plus a pointer

Cross-file connection:

- shared outputs require the readback
- contracts define which proof shapes count in each lane

### Proposed V2 Syntax

```prompt
workflow DossierEngineerAnalysis: "Dossier Engineer Analysis Steps"
    step "Build learner history":
        must emit table lessons.contracts.dossier.SectionDossierFileOutput.learner_history_by_section

    step "Ground next capabilities":
        must emit table lessons.contracts.dossier.SectionDossierFileOutput.next_capabilities
        must emit receipts lessons.contracts.dossier.SectionDossierFileOutput.grounding_and_open_questions

    step "Check overlap and contrast":
        compare candidate_section with nearby.accepted_lessons for adjacency_overlap
        compare candidate_section with nearby.accepted_lesson_situations for repeated_showcase_hand_overlap
```

### Rendered Markdown

```md
## Dossier Engineer Analysis Steps

Build `Learner History By Section` as a table.

Build `Next Capabilities` as a keep-versus-reject table and keep the returned
receipts in `Grounding And Open Questions`.

Compare the proposed section against nearby accepted lessons and nearby
accepted lesson situations for overlap and contrast.
```

### Why This Is Better

- proof-bearing outputs become explicit artifacts
- comparison becomes a first-class obligation
- review no longer has to reconstruct whether evidence was actually emitted

## 8. Review Gates And Verdict Law

This bucket has earned a new top-level primitive: `review`.

### Before: Current Lessons Examples

```prompt
workflow DossierReviewContract: "Shared Dossier Review Contract"
    "At minimum confirm the file has non-empty `{{SectionDossierFileOutput:must_include.learner_history_by_section}}` ..."
    "At minimum confirm that on a full rewrite or a new section the dossier did not use the current `{{lessons.contracts.metadata_wording.SectionMetadataFileOutput:target.path}}` `name` or `description` as evidence..."
    "At minimum confirm the stop line keeps the section as small as the learner needs now instead of quietly absorbing deferred work."
```

```prompt
workflow SectionArchitectureReviewContract: "Shared Section Architecture Review Contract"
    "At minimum confirm the lesson count rationale comes from learner jobs, not symmetry, aesthetics, or repeated-pattern inertia."
    "At minimum confirm downstream invalidation is explicit when the section spine changed."
    "At minimum confirm the file preserves the approved section burden and locked concept order instead of quietly reopening them."
```

```prompt
workflow MetadataWordingReviewContract[...]: "Shared Metadata Review Contract"
    metadata_specific_checks: "Metadata-Specific Checks"
        "At minimum confirm the producer worked in exactly one mode and one current file for the turn."
        "At minimum confirm the pass did not widen into general lesson copy, section structure, or open-ended naming invention."
```

What this bucket is doing today:

- turning quality expectations into checkable law
- making critic rejection concrete rather than taste-based
- preserving shared gate language across producer and critic

Cross-file connection:

- critic prompts import contract review workflows and add local posture
- the heavy review law already lives in the contracts
- this is the densest recurring prose family in the corpus

### Proposed V2 Syntax

```prompt
review DossierReview: "Shared Dossier Review Contract"
    subject = lessons.contracts.dossier.SectionDossierFileOutput

    must subject.learner_history_by_section.nonempty
    must subject.learner_baseline.nonempty
    must subject.next_capabilities.nonempty
    must subject.grounding_and_open_questions.nonempty
    must stop_line.keeps_section_small

    reject when section.status in {new, full_rewrite} and evidence_uses_current_section_metadata
    accept when all_checks_pass

    comment:
        must include verdict, failed_gates, owner_of_fix, exact_file, exact_check
```

### Rendered Markdown

```md
## Shared Dossier Review Contract

The review subject is the section dossier file.

Require non-empty learner history, learner baseline, next capabilities, and
grounding-and-open-questions sections.

Require the stop line to keep the section as small as the learner needs now.

Reject when a new or rewrite pass uses current section metadata as evidence.

Accept only when all checks pass.

The verdict comment must include the verdict, the failing gates, the owner of
the fix, the exact file, and the exact failed check.
```

### Why This Is Better

- verdict law becomes inspectable as law
- review stops pretending to be just another workflow
- critic outputs can point to exact failed checks

## 9. Routing And Owner Transition

This bucket wants explicit route statements.

### Before: Current Lessons Examples

```prompt
workflow HowToTakeATurn: "How To Take A Turn"
    read_current_work_state: "Read Current Work State"
        "- If current roots, current files, or current review files are still too unclear to keep working without guessing, stop specialist work and route the same issue to {{lessons.common.agents.LessonsProjectLead:name}}."
```

```prompt
workflow MetadataWordingWorkflow[...]: "Metadata Wording Workflow"
    override intro: "Introduction"
        "If any of that is unclear, stop and route the same issue to {{lessons.common.agents.LessonsProjectLead:name}}."
        "This seam has one owner. Do not invent a fallback owner, backup mode, or alternate live route."
```

```prompt
workflow CopyGroundingContract: "Shared Copy Contract"
    field_specialization: "Field Specialization"
        "If the option problem is structural rather than textual, including bad option count or an `nRequired` mismatch, stop and route the same issue to {{lessons.common.agents.LessonsPlayableMaterializer:name}}."
```

What this bucket is doing today:

- preserving one active owner
- pushing mis-scoped work back to the earliest real owner
- preventing local repair from mutating into upstream redesign
- making reroutes same-issue and visible

Cross-file connection:

- Project Lead owns the global routing seam
- each specialist lane still carries local stop-lines for when to route back

### Proposed V2 Syntax

```prompt
workflow RoutingLaw: "Routing Rules"
    route "Route upstream when current work state is unclear" -> lessons.common.agents.LessonsProjectLead when unclear(current.roots, current.files, current.review_files)

    route "Route metadata work upstream when mode or file is unclear" -> lessons.common.agents.LessonsProjectLead when unclear(handoff.mode, handoff.current_file, upstream.truth)

    route "Route structural option problems to materializer" -> lessons.common.agents.LessonsPlayableMaterializer when option_problem.kind in {bad_option_count, nRequired_mismatch, structural}
```

### Rendered Markdown

```md
## Routing Rules

Route the same issue to Lessons Project Lead when the current work state is
unclear.

Route the same issue to Lessons Project Lead when metadata mode, current file,
or upstream truth is unclear.

Route the same issue to Lessons Playable Materializer when the option problem
is structural rather than textual, including bad option count or an
`nRequired` mismatch.
```

### Why This Is Better

- owner transition becomes explicit rather than implied
- route law stops hiding inside stop-line prose
- the same-issue pattern can be enforced consistently

## 10. Preservation And Anti-Drift Constraints

This bucket wants `preserve`.

### Before: Current Lessons Examples

```prompt
workflow DossierReviewContract: "Shared Dossier Review Contract"
    "At minimum confirm that on a full rewrite or a new section the dossier did not use the current `{{lessons.contracts.metadata_wording.SectionMetadataFileOutput:target.path}}` `name` or `description` as evidence..."
    "At minimum confirm `sectionId`, section ordering, and publication state stayed live even while those old learner-facing identity fields were ignored."
```

```prompt
workflow SectionArchitectureReviewContract: "Shared Section Architecture Review Contract"
    "At minimum confirm the file preserves the approved section burden and locked concept order instead of quietly reopening them."
    "At minimum confirm `{{SectionLessonMapFileOutput:must_include.late_metadata_handoff}}` stays short and structural instead of turning into metadata proof."
```

```prompt
workflow MetadataWordingWorkflow[...]: "Metadata Wording Workflow"
    override step_4_map_to_outputs: "Step 4 - Map To Outputs"
        "Update only the in-scope metadata fields in the current file."
        "Preserve every out-of-scope field exactly as it already is."

output CopyManifestFileOutput: "Updated Lesson Manifest File"
    must_include: "Must Include"
        locked_truth_stays_intact: "Locked Truth Stays Intact"
            "Do not use the copy pass to rename locked concepts, widen answer claims, or sharpen exact-move claims."
```

What this bucket is doing today:

- preserving locked upstream truth
- preventing stale labels from being used as evidence
- preventing downstream patches from silently rewriting upstream decisions
- reducing drift between what a lane owns and what it merely inherits

Cross-file connection:

- rewrite mode in the dossier disables stale metadata as evidence
- section architecture carries that forward without reopening burden
- metadata wording can update wording later, but not structure truth
- copy can rewrite text without widening concept or answer truth

### Proposed V2 Syntax

```prompt
workflow MetadataCopywriterJob: "Your Job"
    when handoff.mode == lessons.contracts.metadata_wording.MetadataPassMode.lesson_title:
        preserve lessons.contracts.lesson_plan.LessonPlanContract

    when handoff.mode == lessons.contracts.metadata_wording.MetadataPassMode.section:
        preserve lessons.contracts.metadata_wording.SectionLessonMapContract
        preserve lessons.common.role_home.SectionCatalogMeta
        preserve out_of_scope_fields


output CopyManifestFileOutput: "Updated Lesson Manifest File"
    forbid rename(locked.concepts)
    forbid widen(answer.claims)
    forbid sharpen(exact_move.claims)
```

### Rendered Markdown

```md
## Your Job

If mode is `lesson_title`, preserve the current lesson plan truth.

If mode is `section`, preserve the current section lesson map, the current
section catalog truth, and every out-of-scope field.

## Updated Lesson Manifest File

Do not rename locked concepts, widen answer claims, or sharpen exact-move
claims.
```

### Why This Is Better

- preservation becomes a first-class semantic action
- anti-drift rules stop being scattered across many prose surfaces
- reviewers can point to a concrete preserve-law violation

## 11. Tool Delegation And Specialist Skill Routing

This bucket wants `use Skill when ...`.

### Before: Current Lessons Examples

```prompt
workflow ReadFirst: "Read First"
    start_here: "Start Here"
        required "Read these instructions all the way through before you act."
        "This system is skill-first. You will prefer to use skills where one is defined."
```

```prompt
skill HeadlineCopySkill: "psmobile-lesson-headline"
    purpose: "Keep step headlines short, immediate, and clear."
    use_when: "Use When"
        "If this skill is available in the current run, use it when learner-facing headline copy changes."
    does_not: "Does Not"
        "Does not own cue text, option labels, feedback, or step structure."
```

```prompt
workflow CopyGroundingContract: "Shared Copy Contract"
    field_specialization: "Field Specialization"
        "Route headline work through the headline skill."
        "Route `coachText`, `coachCommentary`, and learner-facing guided-walkthrough beat text in scope through the coach-text skill."
        "Route learner-visible text answer options through the answer-option skill."
        "Route feedback through the feedback skill."
```

What this bucket is doing today:

- formalizing specialist sub-judgments without hardcoding them into every lane
- keeping shared capabilities reusable
- reducing prose duplication by pushing deep quality bars into skills

Cross-file connection:

- the role-home layer says to prefer skills
- the skills layer declares the seam and non-goals for each tool
- concrete contracts invoke those skills where the subproblem appears

### Proposed V2 Syntax

```prompt
skill HeadlineCopySkill: "psmobile-lesson-headline"
    purpose: "Keep step headlines short, immediate, and clear."
    does_not: "Does Not"
        "Does not own cue text, option labels, feedback, or step structure."


workflow CopyGroundingContract: "Shared Copy Contract"
    use HeadlineCopySkill when field == headline
    use CoachTextSkill when field in {coachText, coachCommentary, guided_walkthrough_beat}
    use AnswerOptionCopySkill when field == answer_options
    use FeedbackSkill when field == feedback
```

### Rendered Markdown

```md
## Shared Copy Contract

Use `HeadlineCopySkill` when the changed field is the headline.
Use `CoachTextSkill` when the changed field is coach text, coach commentary, or
guided walkthrough beat text.
Use `AnswerOptionCopySkill` when the changed field is learner-visible answer
options.
Use `FeedbackSkill` when the changed field is feedback.
```

### Why This Is Better

- delegation becomes an explicit statement form
- skills keep their human purpose prose, but routing to them becomes law
- shared capability routing stops being duplicated as freehand English

## What This Proposal Suggests

The durable insight from the buckets document still holds:

plain English in the Lessons corpus is hiding recurring semantic jobs.

V2 changes the design answer from "maximize symbolic power everywhere" to:

formalize only the law that keeps drifting.

That means keeping Doctrine's current skeleton and teaching its bodies how to
express:

- activation
- truth
- scope
- preservation
- proof
- verdicts
- routes

with a small Python-shaped statement vocabulary.

If Doctrine grows in that direction, it will feel more like code exactly where
the corpus has already earned code, and it will stay prose where prose is still
the better tool.
