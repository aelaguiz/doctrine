# Lessons Prompt Prose Buckets V1 Proposal

Date: 2026-04-10

## Status

This document is an unconstrained design exercise.

It keeps the bucket taxonomy from
[`LESSONS_PROSE_BUCKETS_2026-04-10.md`](LESSONS_PROSE_BUCKETS_2026-04-10.md),
but changes the question:

What if Doctrine were free to become a beautiful, Python-shaped language for
agent law, document law, and symbolic authority selection?

For this pass:

- do not optimize for implementation cost
- do not optimize for backward compatibility
- do not anchor on the currently shipped grammar
- do keep the examples grounded in the live Lessons corpus under
  `../paperclip_agents/doctrine/prompts/lessons/**`
- keep the document self-contained: each bucket should show the live before,
  what the bucket is doing today, the unconstrained v1 syntax, and the changed
  rendered Markdown

## Goal

The original buckets document proved that the Lessons corpus is not "just
strings." It is carrying recurring semantic jobs:

- ownership
- work ordering
- current-truth selection
- output normalization
- mode activation
- evidence law
- review law
- routing
- preservation
- delegation

This proposal asks the next question:

If we lifted those recurring jobs into first-class language, what would the
best source syntax look like, and what would that let the rendered Markdown say
more cleanly?

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

Each bucket below keeps the same semantic job as the original document, but it
rewrites the example in a deliberately unconstrained v1 language that is more
Pythonic, more symbolic, and less prose-dependent.

## Design Thesis

The ideal version of Doctrine should let authors write policy and document
contracts as if they were writing clear Python, not as if they were hiding a
state machine inside prose paragraphs.

That implies a few design choices:

- indentation is semantic
- `if`, `elif`, and `else` carry branch law directly
- recurring jobs become first-class blocks instead of prose habits
- prose stays for domain meaning, examples, and nuance
- the compiler owns authority, mode, routing, preservation, proof, and review
  semantics
- the renderer turns those symbolic structures into natural Markdown instead of
  flattening everything into adjacent strings

## Proposed V1 Surface

This document uses one consistent imagined surface:

- `purpose:` opens the seam in human language
- `owns:` lists what this role or artifact actually owns
- `must:` and `must not:` express hard law
- `do in order:` expresses turn protocol
- `current truth:` expresses authority, support, and ignore-by-default rules
- `render <Artifact>:` expresses required readback shape
- `mode:` and `if mode == ...:` express mutually exclusive branches
- `prove:` and `compare:` express evidence obligations
- `review <Artifact>:` expresses critic gates and verdict rules
- `route ... -> Agent` expresses explicit owner transitions
- `preserve exactly:` expresses anti-drift law
- `delegate ... via Skill` expresses specialist routing

That is a much stronger language than the shipped one. That is deliberate.

## Quick Headline

The biggest shift is this:

The current corpus stores semantic law inside prose sentences.

The proposed v1 language would store that law as symbolic structure and let
Markdown become a readable rendering of those symbols.

That is the right direction for the Lessons use case because the same questions
keep recurring:

- What is current?
- What is merely support?
- Which mode is live?
- Who owns next?
- What proof must be present?
- What exact shape must the handoff comment have?
- What must never be silently reopened?

## Bucket Map

| Bucket | Best v1 primitive |
| --- | --- |
| Role and seam identity | Keep as prose; no language change |
| Turn protocol and work ordering | `do in order`, `step`, `require before next step` |
| Current-truth and authority selection | `current truth`, `support only`, `ignore by default`, `authority` |
| Output-shape and readback normalization | `render`, `field`, `inline`, `reject when` |
| Lane boundaries and non-goals | `in scope`, `out of scope`, `must not`, `forbid sidecar` |
| Conditional modes and branch activation | `mode`, `exactly one of`, `if mode == ...` |
| Evidence, proof, and comparison obligations | `prove`, `compare`, `receipts`, `reject summary_without_proof` |
| Review gates and verdict law | `review`, `must confirm`, `accept when`, `changes requested when` |
| Routing and owner transition | `route`, `owner`, `same issue`, `fallback owner` |
| Preservation and anti-drift constraints | `preserve exactly`, `forbid as evidence`, `do not reopen` |
| Tool delegation and specialist skill routing | `delegate`, `via`, `owns`, `does not own` |

## Worked Example: `RouteOnlyTurns`

This is the same seam the original document used because it is the cleanest
place to see the difference between prose and symbolic law.

### Proposed V1 Syntax

```prompt
workflow RouteOnlyTurns:
    enters when no current.specialist_output and work.kind in {
        routing,
        process_repair,
        owner_repair,
    }

    must:
        issue.plan.say(next_owner, next_step)
        issue.comment.say(next_owner, next_step)

    if section.write_mode in {new, rewrite}:
        mark RewriteMode
        suspend authority of SectionMetadataFileOutput.name
        suspend authority of SectionMetadataFileOutput.description
        later LessonsMetadataCopywriter rewrites
            SectionMetadataFileOutput.name,
            SectionMetadataFileOutput.description
        after upstream.review

    if critic.same_miss.repeats:
        render RouteOnlyHandoffOutput.repeated_problem:
            failing_pattern = critic.same_miss.summary
            returned_from = critic.returned_from_role
            next_fix = route.next_fix

    elif route.next_owner is unknown:
        owner stays LessonsProjectLead
```

### Rendered Markdown

```md
## Routing-Only Turns

Use this route when no specialist output file is current and the live job is
routing, process repair, or owner repair.

The current issue plan and the current issue comment must both name the next
owner and the next step.

### Rewrite Mode

When a section is being authored fresh or completely rewritten, mark Rewrite
Mode.

The current `section` metadata `name` and `description` do not define section
truth in this mode. After upstream review,
`LessonsMetadataCopywriter` rewrites those fields.

### Repeated Problem

When the same critic miss comes back again, include a short `Repeated Problem`
section that states what keeps failing, which role returned it, and the next
concrete fix.

### Fallback Owner

If the right specialist is still unclear, `LessonsProjectLead` keeps the
issue.
```

### What Changed

- entry conditions became symbolic branch law instead of sentence prose
- metadata authority suspension became explicit instead of implied
- conditional handoff rendering became a real render block
- fallback ownership became explicit state, not a trailing sentence

## 1. Role And Seam Identity

This bucket is not a useful formalization target in this revision.

Keep it as authored prose. Do not turn it into a language feature just to
rephrase seam text.

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
- defining what good looks like for that seam
- stopping the role from turning into a generic helper

Cross-file connection:

- top-level `role:` text gives the human-readable job
- `Your Job` workflows turn that identity into recurring operating law
- skill `purpose` text refines seam ownership for subproblems inside a lane

### Proposed V1 Syntax

No language change proposed.

Keep `role:` and adjacent seam-defining prose as ordinary authored prose.

### Rendered Markdown

No renderer change proposed.

The rendered Markdown for this bucket should stay exactly as the current source
authors it.

### Why This Is Better

- it avoids turning prose wording preferences into fake language design
- it keeps bucket 1 focused on seam communication rather than symbolic law
- it saves formalization effort for the buckets that are actually carrying
  checkable behavior

## 2. Turn Protocol And Work Ordering

The best syntax here is an explicit ordered procedure.

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

### Proposed V1 Syntax

```prompt
workflow HowToTakeATurn:
    do in order:
        step "Read upstream materials":
            read issue.active
            read plan.current or plan.parent_if_issue_points_there
            read comment.latest_current
            read upstream.files.required_by_lane

        step "Analyze before writing":
            require named analysis.tables_checks_comparisons
            consult ParaMemoryFilesSkill before execution

        step "Write current outputs":
            update lane.current_artifacts

        step "Close the turn":
            render HandoffOutput
            assign same_issue to next_owner
            end turn
```

### Rendered Markdown

```md
## How To Take A Turn

1. Read the active issue, the current issue plan or current parent plan when
   the issue points there, the latest current comment, and the upstream files
   your lane depends on.
2. Do your own analysis before writing. Name the tables, checks, or
   comparisons that drove the decision. Check `ParaMemoryFilesSkill` before
   execution when relevant.
3. Update the current artifacts for your lane.
4. Close the turn by rendering the handoff comment, reassigning the same issue
   to the next owner, and ending the turn.
```

### Why This Is Better

- read-before-write and analyze-before-write become real step law
- order is no longer encoded as numbered strings
- downstream tooling could point to a specific failed step instead of a vague
  prose violation

## 3. Current-Truth And Authority Selection

This is one of the places where the current language most wants a real logic
surface.

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

- the shared role home sets the top-level currentness rules
- output contracts encode how currentness must be named in comments
- individual contracts add lane-specific support-only and not-current-by-default rules

### Proposed V1 Syntax

```prompt
workflow CurrentWorkState:
    current truth:
        work_state = issue.plan.current + comment.latest_current
        attached_checkout = product_truth only

    support only:
        section.hand_usage_ledger
        nearby.accepted_supporting_files

    ignore by default:
        legacy.authoring_files
        same_folder.old_attempts
        under_construction.outputs_from_other_lanes

    revive ignored only when explicitly named as support

    if current.roots or current.files or current.review_files are unclear:
        stop specialist_work
        route "Current work state is unclear" -> LessonsProjectLead
```

### Rendered Markdown

```md
## Current Work State

### Current Truth

- Use the current issue plan together with the latest current comment as the
  work state.
- Use the attached checkout for product truth only.

### Support Only

- Section hand-usage ledgers
- Nearby accepted supporting files when explicitly needed

### Ignore By Default

- Legacy authoring files
- Older same-folder attempts
- Under-construction outputs from other lanes

Only an explicit local rule may revive an ignored file, and even then it stays
support evidence rather than current truth.

If current roots, current files, or current review files are unclear, stop
specialist work and route the same issue to `LessonsProjectLead`.
```

### Why This Is Better

- current truth, support evidence, and ignored material stop competing in one
  prose layer
- authority selection becomes explicit instead of interpretive
- unclear-currentness becomes a direct route condition

## 4. Output-Shape And Readback Normalization

The best syntax should let the author declare readback law directly.

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
- requiring the real analysis and real readback, not a pointer like `see file`
- making conditional sections and exact labels reusable across turns
- keeping routing turns from inventing fake specialist artifacts

Cross-file connection:

- `outputs.prompt` defines the shared handoff schema
- agents and contracts add exact section labels or local render obligations

### Proposed V1 Syntax

```prompt
output HandoffOutput:
    render:
        what_changed: required
        analysis_performed: required inline actual_analysis
        output_contents_that_matter: required inline actual_readback
        use_now: required
        next_owner: required

    reject when:
        analysis_performed.is_label_only
        output_contents_that_matter.is_heading_only
        use_now.is_guess

output RouteOnlyHandoffOutput:
    render:
        current_route: required
        analysis_performed: required inline actual_route_analysis
        output_contents_that_matter: required inline actual_route_readback
        next_step: required
        next_owner: required fallback LessonsProjectLead
```

### Rendered Markdown

```md
## Producer Handoff Comment

### Required Fields

- `What Changed`
- `Analysis Performed`: put the actual analysis in the comment, not just a
  label
- `Output Contents That Matter`: put the actual readback in the comment, not
  just section names or headings
- `What To Use Now`
- `Next Owner`

Reject the handoff if analysis is label-only, if output readback is heading-
only, or if `What To Use Now` is guessed.

## Routing Handoff Comment

The routing version must also name the current status, the next concrete step,
and the next owner, with `LessonsProjectLead` as the fallback owner when the
earliest clear owner is still unclear.
```

### Why This Is Better

- required comment shape becomes a typed render contract
- vague handoff failures become precise rejection rules
- inline-versus-pointer behavior becomes symbolic

## 5. Lane Boundaries And Non-Goals

The ideal language should say what a lane is for and what it refuses to become.

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
- reducing silent overlap between neighboring lanes

Cross-file connection:

- role jobs set high-level boundaries
- workflow intros restate them where a seam is easy to widen
- contract notes often enforce the same boundary as file-law

### Proposed V1 Syntax

```prompt
workflow MetadataWordingWorkflow:
    seam:
        late wording pass for one current metadata file

    in scope:
        lesson_title only when mode == lesson_title
        section.name when mode == section
        section.description when mode == section

    out of scope:
        general.lesson_copy
        section.structure
        top_level.lesson_title during section mode

    must not:
        create sidecar("SECTION_CONTINUITY.md")
        widen into redesign
```

### Rendered Markdown

```md
## Metadata Wording Workflow

This seam is a late wording pass for one current metadata file.

### In Scope

- Lesson title only in lesson-title mode
- Section `name` in section mode
- Section `description` in section mode

### Out Of Scope

- General lesson copy
- Section structure
- Top-level lesson title during section mode

### Must Not

- Create `SECTION_CONTINUITY.md` or another side file
- Widen into redesign work
```

### Why This Is Better

- scope becomes a first-class contract instead of scattered reminders
- negative space becomes explicit and reviewable
- "do not widen this pass" stops being a stylistic suggestion

## 6. Conditional Modes And Branch Activation

This is the bucket where a Python-shaped language helps the most.

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
- making conditional downstream obligations explicit
- preventing the reader from guessing which mode is live

Cross-file connection:

- rewrite status starts in the dossier
- that status propagates into section architecture and later metadata work
- exact-move in-scope versus out-of-scope plays the same branch role elsewhere

### Proposed V1 Syntax

```prompt
workflow MetadataWordingWorkflow:
    mode MetadataPassMode:
        exactly one of {lesson_title, section}

    if mode == lesson_title:
        current file = LessonTitleManifestFileOutput
        in scope = {title}

    elif mode == section:
        current file = SectionMetadataFileOutput
        in scope = {name, description}

    else:
        error "Metadata wording must run in exactly one mode"

    forbid:
        both LessonTitleManifestFileOutput and SectionMetadataFileOutput
        being current in one turn
```

### Rendered Markdown

```md
## Metadata Wording Workflow

Work in exactly one mode per turn.

### Lesson Title Mode

- Current file: `LESSON_MANIFEST.md`
- In scope: `title`

### Section Mode

- Current file: `SECTION_METADATA.md`
- In scope: `name` and `description`

Do not treat both files as current in one turn.
```

### Why This Is Better

- mutually exclusive branch law becomes native instead of narrated
- current file selection attaches directly to mode
- invalid mixed-mode turns become compiler-detectable

## 7. Evidence, Proof, And Comparison Obligations

The strongest version of Doctrine should own proof law directly.

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
- requiring actual tables, actual rows, actual receipts, actual comparisons
- making downstream review possible without reconstruction
- preventing a handoff comment from collapsing into a title plus a pointer

Cross-file connection:

- shared outputs require the readback
- contracts define which tables, receipts, and comparison rows count as proof

### Proposed V1 Syntax

```prompt
workflow DossierEngineerAnalysis:
    prove:
        learner_history_by_section as table
        next_capabilities as keep_reject_table
        grounding_and_open_questions with returned_receipts

    compare:
        nearby.accepted_lessons for adjacency_overlap
        nearby.accepted_lesson_situations for repeated_showcase_hand_overlap

    require:
        kept wording follows returned_receipts
        kept section truth follows returned_receipts

    reject:
        summary_without_receipts
        comparison_claim_without_named_neighbors
```

### Rendered Markdown

```md
## Dossier Engineer Analysis

### Proof Required

- Build `Learner History By Section` as a table.
- Build `Next Capabilities` as a keep-versus-reject table.
- Keep the actual returned receipts in `Grounding And Open Questions`.

### Comparison Required

- Compare against nearby accepted lessons for adjacency overlap.
- Compare against nearby accepted lesson situations for repeated showcase-hand
  overlap.

Reject summaries without receipts and comparison claims that do not name the
neighboring examples they rely on.
```

### Why This Is Better

- proof becomes a distinct semantic class rather than a prose habit
- comparison obligations stop hiding inside individual sentences
- receipt-bearing evidence becomes a hard rule, not a tone preference

## 8. Review Gates And Verdict Law

This bucket wants a native review language.

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

### Proposed V1 Syntax

```prompt
review SectionDossierFileOutput:
    must confirm:
        nonempty learner_history_by_section
        nonempty learner_baseline
        nonempty next_capabilities
        nonempty grounding_and_open_questions
        on rewrite or new_section:
            SectionMetadataFileOutput.name not used as evidence
            SectionMetadataFileOutput.description not used as evidence
        stop_line keeps section as small as learner needs now

    accept when all gates pass

    changes requested when any gate fails:
        next_owner = earliest role that owns the missing work
```

### Rendered Markdown

```md
## Shared Dossier Review Contract

At minimum confirm:

- `Learner History By Section` is present and non-empty.
- `Learner Baseline` is present and non-empty.
- `Next Capabilities` is present and non-empty.
- `Grounding And Open Questions` is present and non-empty.
- On a rewrite or new section, current section metadata `name` and
  `description` were not used as evidence.
- The stop line keeps the section as small as the learner needs now.

Return `accept` only when every gate passes. Otherwise return
`changes requested` and route the same issue to the earliest role that owns the
missing work.
```

### Why This Is Better

- review law becomes executable structure rather than repeated sentence stems
- verdict rules stop being smeared across multiple prose paragraphs
- critic outputs can point to named failed gates

## 9. Routing And Owner Transition

The language should say ownership and rerouting directly.

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

### Proposed V1 Syntax

```prompt
workflow RoutingLaw:
    owner:
        exactly one current owner per issue
        reroutes stay on same issue

    if current.work_state is unclear:
        route "Current work state is unclear" -> LessonsProjectLead

    if copy_problem.kind in {option_count, nRequired_mismatch, structural}:
        route "Problem is structural, not textual" ->
            LessonsPlayableMaterializer

    if next_owner is unknown:
        owner stays LessonsProjectLead
```

### Rendered Markdown

```md
## Routing Law

- Keep exactly one current owner per issue.
- Keep reroutes on the same issue.

Route the same issue to `LessonsProjectLead` when the current work state is
unclear.

Route the same issue to `LessonsPlayableMaterializer` when the problem is
structural rather than textual, including bad option count or an
`nRequired` mismatch.

If the next owner is still unclear, `LessonsProjectLead` keeps the issue.
```

### Why This Is Better

- owner transition stops looking like ordinary prose
- same-issue routing becomes a first-class rule
- fallback ownership becomes explicit state instead of implication

## 10. Preservation And Anti-Drift Constraints

This is another area that deserves a native primitive.

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
- metadata can rewrite wording later, but only after structure is locked
- copy can rewrite text without widening concept or answer truth

### Proposed V1 Syntax

```prompt
workflow PreservationLaw:
    preserve exactly:
        approved.section_burden
        locked.concept_order
        every out_of_scope field

    forbid as evidence when section.write_mode in {new, rewrite}:
        SectionMetadataFileOutput.name
        SectionMetadataFileOutput.description

    copy pass must not:
        rename locked.concepts
        widen answer.claims
        sharpen exact_move.claims
```

### Rendered Markdown

```md
## Preservation Law

### Preserve Exactly

- Approved section burden
- Locked concept order
- Every out-of-scope field

### Do Not Use As Evidence On New Or Rewrite Passes

- Current section metadata `name`
- Current section metadata `description`

### Copy Pass Must Not

- Rename locked concepts
- Widen answer claims
- Sharpen exact-move claims
```

### Why This Is Better

- preservation stops being scattered across different prose surfaces
- stale identity fields become an explicit forbidden evidence class
- downstream passes get a hard boundary against "helpful" reopening

## 11. Tool Delegation And Specialist Skill Routing

The best syntax should make delegation look like field routing, not like polite
English advice.

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

### Proposed V1 Syntax

```prompt
skill HeadlineCopySkill:
    owns:
        learner_facing.headline_copy

    use when:
        learner_facing.headline changes

    does not own:
        cue_text
        option_labels
        feedback
        step_structure

workflow CopyGroundingContract:
    delegate headline -> HeadlineCopySkill
    delegate coach_text -> CoachTextSkill
    delegate answer_options -> AnswerOptionCopySkill
    delegate feedback -> FeedbackSkill
```

### Rendered Markdown

```md
## Headline Copy Skill

### Owns

- Learner-facing headline copy

### Use When

- Learner-facing headline copy changes

### Does Not Own

- Cue text
- Option labels
- Feedback
- Step structure

## Shared Copy Contract

- Route headline work through `HeadlineCopySkill`.
- Route coach text through `CoachTextSkill`.
- Route answer options through `AnswerOptionCopySkill`.
- Route feedback through `FeedbackSkill`.
```

### Why This Is Better

- delegation becomes an explicit routing relation between fields and skills
- skill seams stop living only in freehand purpose prose
- the language can now distinguish field ownership from role ownership

## What This Proposal Suggests

The original buckets document was right that the taxonomy is the durable part.

The next step is to accept that several of those buckets are not really "prose
styles." They are missing language primitives.

The most important candidates are:

- `current truth`
- `render`
- `mode`
- `review`
- `preserve exactly`
- `delegate`
- `owner`

If Doctrine ever becomes maximally expressive for the Lessons use case, I would
push it toward a language where:

- currentness is symbolic
- support evidence is symbolic
- proof obligations are symbolic
- review gates are symbolic
- routing is symbolic
- preservation is symbolic
- the final Markdown is mostly a readable rendering of those symbolic choices

That would be a real change in kind, not just a nicer string syntax.
