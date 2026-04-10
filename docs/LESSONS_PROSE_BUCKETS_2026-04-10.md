# Lessons Prompt Prose Buckets

## Goal

This document buckets the prose in `../paperclip_agents/doctrine/prompts/lessons/**` by the job that prose is doing.

This is not a verb taxonomy and it is not a syntax proposal.

The point is simpler: a lot of the Lessons corpus looks like "just strings," but the strings are carrying recurring semantic jobs. If we want to reduce drift later, we first need a clean map of those jobs.

Each bucket below now includes inlined doctrine snippets so the document stays reviewable on its own.

## Corpus And Method

Representative files read for this pass:

- `../paperclip_agents/doctrine/prompts/lessons/common/role_home.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/common/skills.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/outputs/outputs.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_section_architect/AGENTS.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/dossier.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/section_architecture.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/metadata_wording.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/lesson_situations.prompt`
- `../paperclip_agents/doctrine/prompts/lessons/contracts/copy_grounding.prompt`

I bucketed each prose fragment by its primary job, even though many lines do more than one thing at once.

## Quick Headline

The Lessons corpus is not one big mass of "instructions." It is a mixture of recurring prose families:

1. Role and seam identity
2. Turn protocol and work ordering
3. Current-truth and authority selection
4. Output-shape and readback normalization
5. Lane boundaries and non-goals
6. Conditional modes and branch activation
7. Evidence, proof, and comparison obligations
8. Review gates and verdict law
9. Routing and owner transition
10. Preservation and anti-drift constraints
11. Tool delegation and specialist skill routing

High-signal markers across the corpus:

- `At minimum confirm`: 108 matches
- `route the same issue`: 17 matches
- `Do not create`: 14 matches
- `Put the actual`: 12 matches

Those counts are not the taxonomy. They are just useful markers that these prose jobs recur a lot.

## Worked Example: `RouteOnlyTurns`

Source:

- `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt:51`

Original section:

```prompt
workflow RouteOnlyTurns: "Routing-Only Turns"
    "Use this route when no specialist output file is current yet and the live job is routing, process repair, or owner repair."
    "Keep the current issue plan and the current issue comment explicit about the next owner and the next step."
    "When a section is being authored fresh or completely rewritten, indicate Rewrite Mode. That means {{lessons.common.agents.LessonsMetadataCopywriter:name}} will later rewrite final `{{lessons.contracts.metadata_wording.SectionMetadataFileOutput:target.path}}` `name` and `description` after upstream review instead of inheriting old section metadata."
    "When the same critic miss comes back again, put one short `{{ProjectLeadCommentLabels:repeated_problem}}` section in the routing comment."
    "Say what keeps failing, which role it came back from, and the next concrete fix."
    "If it is still unclear which specialist should go next, keep the issue on {{lessons.common.agents.LessonsProjectLead:name}} instead of pretending the next step is settled."
```

What those six lines are actually doing:

| Line | Primary prose bucket | What the line is really doing |
| --- | --- | --- |
| `Use this route when ...` | Conditional modes and branch activation | Declares the entry condition for this workflow branch. |
| `Keep the current issue plan ...` | Output-shape and readback normalization | Declares the minimum normalized routing comment content. |
| `When a section is being authored ...` | Conditional modes and branch activation | Opens a rewrite-mode branch. |
| Same rewrite-mode line | Routing and owner transition | Declares that a later metadata lane owns final section wording. |
| `When the same critic miss ...` | Output-shape and readback normalization | Declares a conditional rendered subsection in the routing comment. |
| `Say what keeps failing ...` | Evidence, proof, and comparison obligations | Declares the contents that conditional subsection must actually carry. |
| `If it is still unclear ...` | Routing and owner transition | Declares the fallback owner when no specialist owner is yet justified. |

This is the key pattern behind a lot of Lessons prose:

- one line often mixes branch selection, downstream ownership, and render-shape law
- a "plain English" paragraph is often secretly a structured contract
- many of the drift-prone strings are not arbitrary text at all; they are carrying recurring semantic types

## Bucket Map

| Bucket | What this prose is doing | Typical places it lives |
| --- | --- | --- |
| Role and seam identity | Defines who owns a seam and why it exists | `role:` fields, `Your Job`, skill `purpose` |
| Turn protocol and work ordering | Defines the order of work inside a turn | common role home workflows |
| Current-truth and authority selection | Decides what counts as current and what does not | common role home, inputs, outputs, contract notes |
| Output-shape and readback normalization | Normalizes what must be said back in handoffs and comments | shared outputs, handoff labels, route-only comments |
| Lane boundaries and non-goals | Prevents one lane from silently becoming another | role jobs, workflow intros, contract notes |
| Conditional modes and branch activation | Switches behavior based on rewrite state, route state, or lesson mode | project lead, dossier, metadata, lesson situations |
| Evidence, proof, and comparison obligations | Forces real analysis, tables, receipts, and comparisons onto the record | contracts, outputs, copy and metadata workflows |
| Review gates and verdict law | Defines what a critic must check and what rejection means | review contracts, critic rules |
| Routing and owner transition | Decides who owns next and when to route upstream | project lead, shared role home, copy and metadata workflows |
| Preservation and anti-drift constraints | Keeps locked truth intact and prevents old state from sneaking back in | dossier, section architecture, metadata, copy |
| Tool delegation and specialist skill routing | Pushes specialized quality calls to explicit skills | `common/skills.prompt`, copy contract, shared role home |

## 1. Role And Seam Identity

This prose tells the model what seam it owns and what improved world state it is supposed to create.

Inline doctrine examples:

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

What this bucket is doing:

- establishing seam ownership
- defining what "good" looks like for that seam
- stopping the role from turning into a generic helper

Cross-file connection:

- top-level agent `role:` text gives the human-readable job
- `Your Job` workflows turn that identity into recurring operating law
- skill `purpose` text further refines seam ownership for subproblems inside a lane

## 2. Turn Protocol And Work Ordering

This prose defines the order in which a turn is supposed to happen.

Inline doctrine examples:

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

What this bucket is doing:

- forcing read-before-write
- forcing analysis-before-output
- forcing closeout and handoff discipline
- making the workflow sequence inspectable instead of implied

Cross-file connection:

- `common/role_home.prompt` defines the universal turn frame
- contract workflows then define lane-specific ordered analysis inside that universal frame

## 3. Current-Truth And Authority Selection

This prose decides what is authoritative, what is merely support, and what must be ignored.

Inline doctrine examples:

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

What this bucket is doing:

- picking the live source of truth
- demoting support evidence so it cannot compete with the primary artifact
- preventing "nearby old file" confusion
- making the handoff comment explain what is current right now

Cross-file connection:

- the shared role home sets the top-level currentness rules
- output contracts encode how currentness must be named in comments
- individual contracts add lane-specific "support only" or "not current by default" rules

## 4. Output-Shape And Readback Normalization

This prose is not about the work itself. It is about how the work must be rendered back to the next reader.

Inline doctrine examples:

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

What this bucket is doing:

- normalizing handoff structure
- requiring the real analysis and real readback, not a pointer like "see file"
- making conditional sections and exact labels reusable across turns
- keeping routing turns from inventing fake specialist artifacts

Cross-file connection:

- `outputs.prompt` defines the general shared handoff schema
- agents and contracts then add exact section labels or local render obligations that sit inside that shared handoff shape

## 5. Lane Boundaries And Non-Goals

This prose tells a role what it must not silently become.

Inline doctrine examples:

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

What this bucket is doing:

- stopping scope creep
- preventing "helpful" lane collapse
- keeping each artifact small and purpose-built
- reducing silent overlap between neighboring lanes

Cross-file connection:

- role jobs set high-level boundaries
- workflow intros restate them when a seam is especially easy to widen
- contract notes often enforce the same boundary as "no second file" or "do not widen this pass"

## 6. Conditional Modes And Branch Activation

This prose activates different behavior when the work is in a specific mode.

Inline doctrine examples:

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

What this bucket is doing:

- selecting the active branch
- narrowing what is in scope in that branch
- making conditional downstream obligations explicit
- preventing the reader from guessing which mode is live

Cross-file connection:

- rewrite status starts in the dossier
- that rewrite status propagates into section architecture and then into later metadata obligations
- exact-move in-scope versus out-of-scope plays the same role in lesson situations that rewrite mode plays in section authoring

## 7. Evidence, Proof, And Comparison Obligations

This prose forces real decision support into the artifacts and comments.

Inline doctrine examples:

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

What this bucket is doing:

- requiring visible evidence, not vibes
- requiring actual tables, actual rows, actual receipts, actual comparisons
- making downstream review possible without reconstruction
- preventing a handoff comment from collapsing into a title plus a pointer

Cross-file connection:

- shared outputs require the readback
- contracts define which tables, receipts, and comparison rows count as the real proof in that lane

## 8. Review Gates And Verdict Law

This prose defines what review must check and what counts as rejection.

Inline doctrine examples:

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

What this bucket is doing:

- turning quality expectations into checkable law
- making critic rejection concrete rather than taste-based
- preserving shared gate language across producer and critic

Cross-file connection:

- the critic prompt imports contract review workflows and adds only local posture and routing
- the heavy review law already lives in the contracts
- this is the densest recurring prose family in the corpus, with 108 `At minimum confirm` lines

## 9. Routing And Owner Transition

This prose decides who owns next and when to escalate back upstream.

Inline doctrine examples:

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

What this bucket is doing:

- preserving one active owner
- pushing mis-scoped work back to the earliest real owner
- preventing local repair from mutating into upstream redesign
- making reroutes same-issue and visible

Cross-file connection:

- Project Lead owns the global routing seam
- every specialist lane still carries local stop-lines that say when work must route back rather than continue

## 10. Preservation And Anti-Drift Constraints

This prose keeps accepted truth intact and blocks stale or smoother language from silently becoming law.

Inline doctrine examples:

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

What this bucket is doing:

- preserving locked upstream truth
- preventing stale labels from being used as evidence
- preventing downstream patches from silently rewriting upstream decisions
- reducing drift between what a lane owns and what it merely inherits

Cross-file connection:

- rewrite mode in the dossier disables stale metadata as evidence
- section architecture must carry that forward without reopening burden
- metadata can later rewrite wording, but only after structure is locked
- copy can rewrite learner-facing text without widening concept or answer truth

## 11. Tool Delegation And Specialist Skill Routing

This prose routes subproblems to explicit reusable capabilities instead of leaving them as freehand English.

Inline doctrine examples:

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

What this bucket is doing:

- formalizing specialist sub-judgments without hardcoding them into every lane
- keeping shared capabilities reusable
- reducing prose duplication by pushing deep quality bars into skills

Cross-file connection:

- the role-home layer says to prefer skills
- the skills layer declares the seam and non-goals for each tool
- concrete contracts then invoke those skills at the exact point where the subproblem appears

## What This Taxonomy Suggests

The biggest takeaway from the corpus is that "plain English" is hiding several different semantic layers:

- branch selection
- ownership transfer
- authority selection
- render-shape normalization
- evidence obligations
- preservation constraints
- review gates

That matters because different buckets drift in different ways:

- role and lane-boundary prose drifts when seams blur
- current-truth prose drifts when support evidence starts competing with primary truth
- output-shape prose drifts when readback gets compressed into vague summaries
- review-gate prose drifts when checklists fork between producer and critic
- preservation prose drifts when stale wording or downstream convenience quietly reopens locked truth

If we later want to formalize the language more aggressively, this bucket map is the part to keep fixed. The syntax question comes after this map, not before it.
