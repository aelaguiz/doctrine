Yes — your decomposition is the right pivot.

The key move is **not** “make the syntax prettier.” It is: **promote the recurring semantic jobs into first-class statements, and leave everything else as prose**. Your bucket map shows eleven recurring prose families, and your `RouteOnlyTurns` example shows that one English sentence is often secretly doing three jobs at once: branch activation, ownership transfer, and render-shape law. Doctrine’s own docs also keep pushing the design toward explicit typed declarations, minimal magic, and away from widening into packets, root binding, or tool-script surfaces too early.  

So my answer is:

**Keep most of Doctrine’s top-level shape.**
Do **not** spend design capital renaming `agent`, `workflow`, `input`, `output`, `skill`, `enum`, `inherit`, `override`, or imports right now. The docs are pretty clear that explicit ordered patching is intentional, top-level workflows are canonical reusable structure, richer output contract material belongs on `output`, and the system wants to stay small and non-magical.   

What *is* missing is a **formal statement vocabulary inside the existing structure**, plus one new primitive that feels truly earned: `review`.

## What should stay prose vs become logic

I would collapse your 11 buckets into this:

* **Keep as prose**

  * role and seam identity
  * tone / vibe
  * explanatory rationale
  * human-facing quality-bar language that is judgmental rather than checkable

* **Make formal**

  * work ordering → `step`
  * current truth / authority → `current`, `support_only`, `ignore`
  * output normalization → `must include`, `section ... when`
  * lane boundaries → `forbid`, `own only`
  * modes / branch activation → `when`, `match`, enums
  * evidence / proof obligations → `must emit`, `table`, `compare`
  * review gates / verdict law → `review`, `accept when`, `reject when`
  * routing / owner transition → `route -> Agent when ...`
  * anti-drift preservation → `preserve`
  * skill routing → `use Skill when ...`

That directly matches the decomposition: your own doc says the prose is hiding branch selection, authority selection, render-shape normalization, evidence obligations, routing, review gates, and preservation constraints.  

## The language I’d actually design

I would keep current Doctrine and add a **small law vocabulary** inside `workflow`, `output`, and a new `review` block.

### Existing declarations stay

```python
import ...
enum ...
input ...
output ...
skill ...
workflow ...
agent ...
abstract agent ...
```

### One new declaration

```python
review Name: "Title"
```

### New statement forms

```python
when <expr>:
match <expr>:
must <predicate>
forbid <predicate>
preserve <ref-or-path>
own only <ref-or-path[, ...]>
current <ref>
support_only <ref>
ignore <ref>
route "label" -> Agent when <expr>
accept when <predicate>
reject when <predicate>
step "Title":
section "Title" when <expr>:
use Skill when <expr>
```

That is the whole trick.

No macro system. No giant logic calculus. Just a few declarative statements with Pythonic boolean expressions and indentation.

## Why this is the right amount of formalization

Because it formalizes the semantic buckets without inventing a new feature per sentence.

Your decomposition is already telling us the right split:

* one line often mixes branch selection, downstream ownership, and render-shape law
* the prose families recur heavily
* review law is especially dense
* role-home shells are already earned; the open question is what belongs *inside* them.   

So I would **not** add ten new top-level primitives.
I would add **one** (`review`) and enrich the bodies of the primitives you already have.

---

## Example 1: `RouteOnlyTurns`

This is exactly the kind of prose that should stop being raw strings. Your own decomposition calls out that it is secretly entry-condition law, output-shape law, ownership law, and fallback routing law. 

### Before source

```prompt
workflow RouteOnlyTurns: "Routing-Only Turns"
    "Use this route when no specialist output file is current yet and the live job is routing, process repair, or owner repair."
    "Keep the current issue plan and the current issue comment explicit about the next owner and the next step."
    "When a section is being authored fresh or completely rewritten, indicate Rewrite Mode. That means {{lessons.common.agents.LessonsMetadataCopywriter:name}} will later rewrite final `{{lessons.contracts.metadata_wording.SectionMetadataFileOutput:target.path}}` `name` and `description` after upstream review instead of inheriting old section metadata."
    "When the same critic miss comes back again, put one short `{{ProjectLeadCommentLabels:repeated_problem}}` section in the routing comment."
    "Say what keeps failing, which role it came back from, and the next concrete fix."
    "If it is still unclear which specialist should go next, keep the issue on {{lessons.common.agents.LessonsProjectLead:name}} instead of pretending the next step is settled."
```

### After source

```python
output RouteOnlyHandoffOutput: "Routing Or Publish Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    must include next_owner, next_step

    section "Repeated Problem" when critic_miss.repeated:
        must include failing_pattern, returned_from, next_fix


workflow RouteOnlyTurns: "Routing-Only Turns"
    when current.specialist_output is None and live_job in {routing, process_repair, owner_repair}:
        when section.status in {new, full_rewrite}:
            must RouteOnlyHandoffOutput.include(rewrite_mode)
            owe lessons.common.agents.LessonsMetadataCopywriter.section_metadata

        when next_owner is unknown:
            route "Keep the issue on Project Lead" -> lessons.common.agents.LessonsProjectLead
```

### Compiled render

```md
## Routing-Only Turns

Active when no specialist output file is current and the live job is routing, process repair, or owner repair.

The routing comment must name the next owner and the next step.

If the section is new or full rewrite, the routing comment must mark Rewrite Mode, and later section metadata wording belongs to Lessons Metadata Copywriter.

If the same critic miss repeats, include a **Repeated Problem** section naming what keeps failing, which role returned it, and the next concrete fix.

If the next owner is still unclear, keep the issue on Lessons Project Lead.
```

What changed here is not cosmetic. The English got decomposed into:

* activation condition
* output contract
* conditional section emission
* downstream ownership
* fallback route

That is exactly the semantic split your bucket doc identified. 

---

## Example 2: metadata mode / scope / preservation

This is another area where the prose is doing real law: mode selection, current-file law, lane boundaries, and preservation of upstream truth. Your decomposition calls those out as separate recurring families, and the existing docs already treat enums, currentness, and typed contracts as earned surfaces.  

### Before source

```prompt
workflow MetadataCopywriterJob: "Your Job"
    "Handle the last learner-facing metadata wording pass after structure is locked."
    "Work in exactly one mode per turn: `{{...MetadataPassMode:lesson_title}}` or `{{...MetadataPassMode:section}}`."
    "In `lesson_title`, own only `...LessonTitleManifestFileOutput:target.path` `title`."
    "In `section`, own only `...SectionMetadataFileOutput:target.path` `name` and `description`."
    "Run only when the current handoff already says this metadata pass is owed now."
    "Do not take over general lesson copy, section structure, or routing."
    "If this pass is not clearly owed now, do not invent another owner, backup mode, or alternate route."
    "If the active mode, the current file, or the required upstream truth is unclear, stop and route the same issue to Project Lead."
```

### After source

```python
workflow MetadataCopywriterJob: "Your Job"
    must handoff.mode in MetadataPassMode
    must handoff.current_file in {
        lessons.contracts.metadata_wording.LessonTitleManifestFileOutput,
        lessons.contracts.metadata_wording.SectionMetadataFileOutput,
    }
    must handoff.owed_now

    when handoff.mode == MetadataPassMode.lesson_title:
        own only lessons.contracts.metadata_wording.LessonTitleManifestFileOutput.title
        preserve lessons.contracts.lesson_plan.LessonPlanContract

    when handoff.mode == MetadataPassMode.section:
        own only (
            lessons.contracts.metadata_wording.SectionMetadataFileOutput.name,
            lessons.contracts.metadata_wording.SectionMetadataFileOutput.description,
        )
        preserve lessons.contracts.metadata_wording.SectionLessonMapContract
        preserve lessons.common.role_home.SectionCatalogMeta

    forbid general_lesson_copy
    forbid section_structure_changes
    forbid routing_takeover
    forbid backup_mode_invention

    when unclear(handoff.mode, handoff.current_file, upstream.truth):
        route "Route upstream when mode or truth is unclear" -> lessons.common.agents.LessonsProjectLead
```

### Compiled render

```md
## Your Job

The handoff must name one active metadata mode and one current metadata file.
This pass must already be owed now.

If mode is `lesson_title`, this role owns only the lesson title and must preserve the current lesson plan truth.

If mode is `section`, this role owns only section `name` and `description` and must preserve the current section lesson map and section catalog truth.

This role may not take over general lesson copy, section structure, or routing.

If the active mode, the current file, or the required upstream truth is unclear, route the same issue to Lessons Project Lead.
```

This is much cleaner because it turns “what this lane owns,” “what it preserves,” and “when it must stop” into first-class law instead of relying on a reviewer to infer it from prose paragraphs.

---

## Example 3: a truly earned new primitive — `review`

I think `review` is the one new top-level thing that is genuinely justified.

Why? Because your corpus shows review law is dense and recurring, with 108 instances of “At minimum confirm,” and because critic behavior repeatedly combines:

* subject file selection
* verdict conditions
* exact failing-gate naming
* route-on-accept / route-on-reject
* verdict-comment schema. 

That is not “just another workflow.” It is a reusable semantic kind.

### Before source

Today this is spread across:

* critic posture prose
* imported review contract workflows
* verdict rules
* who-it-goes-back-to prose
* routing tables

### After source

```python
review CopyReview: "Copy Review"
    subject = lessons.contracts.copy_grounding.CopyManifestFileOutput
    contract = lessons.contracts.copy_grounding.CopyGroundingReviewContract

    must handoff.current_file == subject
    reject when handoff.invalid
    reject when current_truth.from_unnamed_support
    reject when current_truth.from_unaccepted_output
    reject when writes(lessons.contracts.metadata_wording.LessonTitleManifestFileOutput.title)

    preserve lessons.contracts.lesson_situations.LessonSituationsFileOutput.exact_move_boundary

    accept when contract.passes

    on accept:
        match copy_outcome:
            new_lesson | redesigned_lesson ->
                lessons.common.agents.LessonsMetadataCopywriter(
                    mode=lessons.contracts.metadata_wording.MetadataPassMode.lesson_title
                )

            bounded_tweak if owes.section_metadata ->
                lessons.common.agents.LessonsMetadataCopywriter(
                    mode=lessons.contracts.metadata_wording.MetadataPassMode.section
                )

            bounded_tweak ->
                lessons.common.agents.LessonsProjectLead

            unclear ->
                lessons.common.agents.LessonsProjectLead

    on reject:
        route -> lessons.common.agents.LessonsCopywriter unless upstream_problem
        else -> lessons.common.agents.LessonsProjectLead

    comment:
        must include verdict, failed_gates, owner_of_fix, exact_file, exact_check
```

### Compiled render

```md
## Copy Review

Current file must be the copy manifest.

Reject if the handoff is invalid.
Reject if unnamed support files or unaccepted outputs were treated as current truth.
Reject if this pass rewrites the top-level lesson title.

Preserve the exact-move boundary from the current lesson situations truth.

Accept only if the shared copy review contract passes.

If accepted:
- new lesson or redesigned lesson → Lessons Metadata Copywriter (`lesson_title`)
- bounded tweak with section metadata owed → Lessons Metadata Copywriter (`section`)
- bounded tweak with no metadata owed → Lessons Project Lead
- unclear boundary → Lessons Project Lead

If rejected:
- route to Lessons Copywriter
- route to Lessons Project Lead when the problem is upstream

The verdict comment must name the verdict, the failing gates, the owner of the fix, the exact file, and the exact failed check.
```

That is a huge improvement because verdict law becomes inspectable as law.

---

## What I would *not* change right now

I would leave these alone:

* `inherit` / `override`
* imports
* dotted refs
* `{{...}}` interpolation
* current path-string convention
* the “rich output contracts stay on `output`” direction
* the no-packets / no-`runtime_tools` / no-root-binding-for-now stance

Those are not where the drift is coming from. The docs explicitly defend explicit patching, small typed declarations, reusable outputs, and avoiding premature widening into packets or runtime tooling surfaces.   

So I would not burn elegance points turning `{{Ref:path}}` into some prettier sigil unless it later proves it reduces real authoring errors. Right now the real error source is that **law is still being authored as prose**.

## The design in one sentence

Keep Doctrine’s current skeleton, and make `workflow` / `output` / `review` bodies capable of expressing:

**activation, truth, scope, preservation, proof, verdicts, and routes**
with a tiny Pythonic statement vocabulary.

That gives you a language that feels much more like code, but only where the prose has already earned code.

If you want, I can take your prose-bucket doc and turn it into a concrete mini-spec with grammar, statement semantics, and 5–8 canonical examples.



Notes:


Yes — this is basically it. The center of gravity is right: keep Doctrine’s current declaration skeleton, stop renaming already-earned things, formalize recurring law inside existing structures, add one genuinely earned new primitive (`review`), and leave seam identity, tone, and rationale as prose. That is the right move, and it is much closer to “real language design” than “syntax churn.” 

It also fits Doctrine’s stated bias unusually well. The docs keep pushing toward small explicit typed declarations, explicit ordered patching, `workflow` as the main instruction surface, richer contract material living on `output`, and avoiding packets, root binding, or runtime-tool surfaces too early. Your V2 is aligned with that doctrine rather than fighting it.   

The best parts of your proposal are the ones that convert genuinely recurring semantic jobs into first-class statements: `current` / `support_only` / `ignore` for authority, `own only` / `forbid` for lane boundaries, `when` / `match` for mode activation, `preserve` for anti-drift, and `review` plus `accept when` / `reject when` for critic law. Those are not decorative. They directly target the buckets you identified as drift-heavy. 

The places I would still tighten are these.

* `use Skill when ...` should probably **not** be `use`, because Doctrine already uses `use local_key: WorkflowName` for composition. Reusing `use` for execution/routing muddies the grammar. I would switch that one to `apply Skill when ...` or `run Skill when ...`.  
* In `RouteOnlyTurns`, you are still duplicating law a bit. You define `must include ...` on the output, then also say `must RouteOnlyHandoffOutput.include(next_owner)` and `must ...include(next_step)` in the workflow. That second layer feels redundant. The output contract should own output shape; the workflow should only own branch logic and routing. 
* `review` is earned, but it should stay **narrow**. If it becomes a second general-purpose workflow language, it loses the beauty. It should mostly own: subject, contract, accept/reject rules, routing on verdict, and verdict-comment contract. 
* I would keep the statement vocabulary even smaller than the current draft. `table` and `receipts` probably should not be separate statement forms; they can be values inside a more general `emit` surface. Beauty here comes from compression. 

So the version I would bless is very close to your V2, but slightly more compressed:

```prompt
import ...
enum ...
input ...
output ...
skill ...
workflow ...
review ...
agent ...
abstract agent ...

when <expr>:
match <expr>:
step "Title":
must <predicate>
forbid <predicate>
current <ref>
support_only <ref>
ignore <ref>
own only <ref-or-path[, ...]>
preserve <ref-or-path[, ...]>
emit <artifact-or-proof-shape>
section "Title" when <expr>:
route -> Agent when <expr>
accept when <predicate>
reject when <predicate>
apply Skill when <expr>
```

That is the smallest surface I can see that still captures the real prose buckets without inventing features for their own sake. It stays Pythonic because the control shape is indentation + expressions + a few strong verbs. It stays beautiful because each keyword corresponds to a recurring semantic job, not to a stylistic preference. 

So: **yes, this is what I’m saying**, with two main edits — make the law vocabulary a little smaller, and avoid places where the same rule is expressed both on `output` and inside `workflow`. The design is strong. The next task is pruning, not rethinking.
