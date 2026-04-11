Yes — that is now the shipped direction, and the first shared-root
implementation slice is landed.

Status note:

- the public module namespaces are `doctrine.std.*` and
  `doctrine.packs_public.*`
- the shipped physical authored-source roots are `prompts/doctrine/std/**` and
  `prompts/doctrine/packs_public/**`
- manifest-backed proof now lives in `examples/50_stdlib_coordination`,
  `examples/51_stdlib_role_home_and_portable_truth`, and
  `examples/52_public_code_review_pack`
- shared coordination outputs currently keep generic trust carriers explicit
  and unconditional because ordinary output guards may not read imported input
  conventions under the shipped compiler

The clean version is a **four-layer stack**:

1. **Doctrine core**: the language, compiler, diagnostics, and the smallest proven semantic surface.
2. **Doctrine stdlib**: public, reusable, opinionated building blocks authored *in Doctrine*.
3. **Public packs / reference domains**: concrete but public systems like code review that prove stdlib sufficiency and create extraction pressure.
4. **Private application packs**: proprietary systems like Lessons that import from the lower layers and keep domain truth private.

That fits the project’s current center of gravity: Doctrine is example-first, tries to keep the core small, keeps `workflow` as the semantic home, keeps `output` as the produced-contract primitive, avoids packet-like shadow models, and prefers explicit inheritance and patching over magic. The newer law direction also fits that shape because it treats this as a **portable-truth model**: `law` decides what is true now, and `output` decides what the next owner must be able to read and trust.     

The important refinement is this:

**Layer 4 should usually depend directly on Layer 2, not blindly on Layer 3.**
Layer 3 is where you prove a public domain pack like code review. If Lessons wants something from code review and it is truly generic, the right move is usually to **extract it downward into stdlib**, then let both code review and Lessons import that shared thing. That keeps Layer 3 from accidentally becoming “the real framework” just because it was the first concrete public pack. That discipline is exactly in the spirit of Doctrine’s example-first design: prove things in examples, but do not promote them to the language or public foundation until they are clearly earned.   

---

## The stack I would recommend

### Layer 1: Doctrine core

This layer is the language and compiler itself. It should contain only things that change parsing, typing, validation, rendering, or compiler-owned semantics. It is where `agent`, `workflow`, `skills`, `inputs`, `outputs`, inheritance, explicit patching, enums, and built-in I/O concepts live today. Assuming you land the portable-truth work, this is also where `law`, `trust_surface`, `current artifact ... via ...`, `current none`, `invalidate ... via ...`, `mode`, `match`, `own only`, `preserve`, `support_only`, `ignore`, `stop`, and explicit `route` belong.    

This layer should also own:

* parser and AST shape
* renderer behavior
* diagnostics and compiler errors
* manifest-backed example verification
* built-in declarations like `Prompt`, `File`, `EnvVar`, `TurnResponse`
* the formal inheritance and patching rules for workflows, skills, inputs, outputs, and law subsections

What should **not** live here is just as important:

* no Lessons vocabulary
* no public-domain product jargon unless it is truly language-shaped
* no free-floating obligation runtime
* no nominal `artifact` calculus
* no `current status` without a real `status` declaration family
* no targetless routing magic
* no `runtime_tools` side language
* no packet model as the foundation

Those boundaries are already very clear in the docs and in the audit/spec cycle you’ve been refining.    

A good mental model is:

* **Layer 1 defines meaning**
* it does **not** define your company’s doctrine
* it does **not** define your first public domain kit
* it only defines the smallest reusable semantic machine

A concrete repo shape could be:

```text
doctrine/
  compiler/
  parser/
  renderer/
  diagnostics/
  docs/
  examples/
    01_...
    ...
    29_...
    30_law_route_only_turns/
    ...
    38_metadata_polish_capstone/
```

That matches the current repo posture: examples are proof and pressure, not the source of truth by themselves.  

---

### Layer 2: Doctrine stdlib

This is the most important missing layer.

Layer 2 is **not** new language. It is **public Doctrine source written using the language**. It should live in the Doctrine repo because it is the official opinionated foundation you expect many users to import. It is where you make the language feel “zero-prose by default” without bloating the core.

This layer should contain reusable, domain-neutral foundations such as:

* generic role-home shells
* generic coordination outputs
* generic handoff / trust-surface patterns
* generic review verdict vocabularies
* generic route-only workflows
* generic mode-aware portable-truth workflows
* generic narrow-scope editing shells
* generic invalidation-and-rebuild patterns
* generic shared outputs blocks and inputs blocks
* generic public skills, but only when the capability is truly generic

This is also where most of your default prose should live. The current docs already make a big deal of richer output contract material staying on `output`, and the portable-truth model says `output` is the canonical downstream trust surface. So stdlib should ship a lot of pre-authored `output` declarations and `outputs` blocks with good default `standalone_read`, trust fields, and predictable section titles.    

A strong stdlib shape is now:

```text
prompts/doctrine/std/
  coordination/
    inputs.prompt
    outputs.prompt
    workflows.prompt
    enums.prompt

  role_home/
    workflows.prompt

  portable_truth/
    workflows.prompt
```

The point is that authors in Layers 3 and 4 mostly stop writing English paragraphs like:

* “A downstream owner must be able to read this output alone...”
* “Use this route when no current artifact exists...”
* “Keep the next owner and next step explicit...”

Instead, they import defaults that already render that prose, and they mostly author **semantic diffs**: current artifact, mode, ownership, preservation, invalidation, route. That is the clean path to a near-zero-prose authoring surface.  

A stdlib example might look like this:

```prompt
# prompts/doctrine/std/coordination/outputs.prompt

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
        invalidations

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now and what is no longer current."


outputs PortableTruthOutputs: "Outputs"
    coordination_handoff: "Coordination Handoff"
        CoordinationHandoff
```

And a reusable stdlib workflow shell could look like this:

```prompt
# prompts/doctrine/std/coordination/workflows.prompt

workflow RouteOnlyTurns: "Route-Only Triage"
    "Handle turns that can only stop and reroute."

    law:
        active when CurrentHandoff.missing or CurrentHandoff.unclear

        when CurrentHandoff.missing:
            current none
            stop "Current handoff is missing."
            route "Route the same issue back to RoutingOwner." -> doctrine.std.coordination.workflows.RoutingOwner
```

Notice what stdlib is doing here: it is not choosing your domain nouns. It is choosing **structure**, **defaults**, and **override points**. That is where the power comes from.

---

### Layer 3: public packs / reference domains

This is where code review belongs.

Layer 3 should contain **complete, public, domain-shaped packs** built on top of stdlib. These are not language features. They are not proprietary. They are public systems that prove the foundation is strong enough for real use.

This layer is valuable for three reasons:

1. it proves stdlib sufficiency in a second real domain
2. it creates extraction pressure for what should move down into stdlib
3. it gives outside users something concrete to copy before they have their own private pack

A code review pack is a very good choice because it exercises a lot of the same semantic families the Lessons corpus exposed:

* one current artifact per turn
* route-only turns
* review gates and verdict law
* support-only comparison evidence
* narrow write authority
* explicit handoff/readback
* invalidation when upstream structure or base diff changes
* critic independence and route-back behavior

That makes it a strong public proving ground without dragging Lessons IP into the open. The prose-bucket pass is useful here: it showed those families are not just “Lessons weirdness”; they are generic recurring jobs like currentness, output normalization, routing, review law, and preservation.   

A public pack layout could be:

```text
prompts/doctrine/packs_public/code_review/
  common/
    enums.prompt
    outputs.prompt
    skills.prompt
    role_home.prompt
  contracts/
    patch_scope.prompt
    review_readiness.prompt
    architecture_review.prompt
    security_review.prompt
  agents/
    review_lead/AGENTS.prompt
    pull_request_reviewer/AGENTS.prompt
    acceptance_critic/AGENTS.prompt
    rebuild_reviewer/AGENTS.prompt
  examples/
  ref/
```

A code review pack should define its own domain nouns:

* `PullRequestDiff`
* `PatchSummary`
* `ReviewVerdict`
* `RequestedReviewMode`
* `ReviewComment`
* `ArchitectureFindings`
* `SecurityFindings`

But it should import generic structure from stdlib:

* generic coordination handoff output
* generic route-only workflow
* generic mode-aware edit/review shell
* generic review verdict family if it is truly domain-neutral
* generic critic role-home shell if it is not code-review-specific

A code review workflow could look like this:

```prompt
import doctrine.std.coordination.outputs
import doctrine.std.editing.workflows
import doctrine.std.review.enums

enum CodeReviewMode: "Code Review Mode"
    correctness: "correctness"
    architecture: "architecture"
    security: "security"


input CurrentReviewHandoff: "Current Review Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required

input PullRequestDiff: "Pull Request Diff"
    source: File
        path: "review_root/PR_DIFF.md"
    shape: MarkdownDocument
    requirement: Required

output PatchSummary: "Patch Summary"
    target: File
        path: "review_root/patch_summary.json"
    shape: JsonObject
    requirement: Required


outputs CodeReviewOutputs[doctrine.std.coordination.outputs.PortableTruthOutputs]: "Outputs"
    patch_summary: "Patch Summary"
        PatchSummary

    inherit coordination_handoff


workflow CodeReview[doctrine.std.editing.workflows.ModeAwarePortableTruthEdit]: "Code Review"
    law:
        inherit activation

        mode_selection:
            mode review_mode = CurrentReviewHandoff.active_mode as CodeReviewMode

        currentness:
            current artifact PatchSummary via CoordinationHandoff.current_artifact

        evidence:
            support_only PullRequestDiff for comparison

        stop_lines:
            stop "Requested review mode is unclear." when unclear(CurrentReviewHandoff.active_mode)
            route "Route the same review back to ReviewLead." -> ReviewLead when unclear(CurrentReviewHandoff.active_mode)
```

That is exactly the right kind of Layer 3 artifact: concrete enough to feel real, public enough to ship, and generic enough to create reuse pressure. It is not the language. It is not private. It is a public domain pack.

---

### Layer 4: private application packs

This is where Lessons belongs.

Layer 4 is where you put:

* proprietary domain nouns
* internal lane graph
* private file conventions
* private output contracts
* internal review gates
* organization-specific quality bars
* internal skills
* business-specific route semantics
* private examples, refs, manifests, and CI

Your current Lessons surface already looks like a real Layer 4 pack: it has shared role-home material, shared outputs, a skills surface, many contracts, and many concrete role prompts. The prose-bucket document is basically an audit of a mature private pack that is now creating pressure to formalize recurring semantics upstream.  

A private pack layout might remain very close to what you already have:

```text
company_agents/doctrine/lessons/
  common/
    agents.prompt
    role_home.prompt
    skills.prompt
  outputs/
    outputs.prompt
  contracts/
    dossier.prompt
    section_architecture.prompt
    metadata_wording.prompt
    lesson_situations.prompt
    copy_grounding.prompt
    ...
  agents/
    lessons_project_lead/AGENTS.prompt
    lessons_section_architect/AGENTS.prompt
    lessons_copywriter/AGENTS.prompt
    lessons_metadata_copywriter/AGENTS.prompt
    lessons_acceptance_critic/AGENTS.prompt
    ...
```

The key difference is that, in the future version, these files should mostly import from Layers 2 and 3 instead of re-stating every semantic family as prose.

A Lessons workflow should not be forced to fit code review nouns. But it should absolutely be able to reuse the public foundations that code review proved. A private `MetadataPolish` lane might import:

* stdlib coordination output
* stdlib route-only workflow
* stdlib mode-aware portable-truth shell
* stdlib critic role-home shell
* maybe a public `review` family extracted while building code review

A private Lessons agent could then stay focused on proprietary semantics:

```prompt
import doctrine.std.coordination.outputs
import doctrine.std.editing.workflows
import doctrine.std.role_home.workflows

enum MetadataPassMode: "Metadata Pass Mode"
    lesson_title: "lesson-title"
    section: "section"


workflow MetadataPolish[doctrine.std.editing.workflows.ModeAwarePortableTruthEdit]: "Metadata Polish"
    law:
        inherit activation

        mode_selection:
            mode pass_mode = CurrentHandoff.active_mode as MetadataPassMode

        currentness:
            match pass_mode:
                MetadataPassMode.lesson_title:
                    current artifact LessonTitleManifest via CoordinationHandoff.current_artifact
                    own only LessonTitleManifest.title
                    preserve exact LessonTitleManifest.* except title
                    preserve decisions LessonPlan

                MetadataPassMode.section:
                    current artifact SectionMetadata via CoordinationHandoff.current_artifact
                    own only {SectionMetadata.name, SectionMetadata.description}
                    preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
                    preserve decisions SectionLessonMap

        invalidation:
            invalidate SectionMetadata via CoordinationHandoff.invalidations when structure_changed

        stop_lines:
            stop "Mode, current artifact, or preserve basis is unclear." when unclear(...)
            route "Route the same issue back to LessonsProjectLead." -> LessonsProjectLead when unclear(...)
```

That is exactly where proprietary value should live: the nouns, the owned fields, the specific preserve basis, the specific invalidation threshold, the actual routing owner. The underlying semantic machine should already exist below it.

---

## The composition rule that matters most

The most important rule in this whole system is:

**Higher layers are allowed to specialize lower layers, but they should not redefine lower-layer meaning.**

That means:

* Layer 4 can override a stdlib workflow section
* Layer 4 can add a proprietary trust-surface field
* Layer 4 can create stricter route rules
* Layer 4 can add internal skills and contracts

But Layer 4 should **not** invent a different meaning for:

* `current artifact`
* `trust_surface`
* `route`
* `inherit` / `override`
* what counts as emitted output
* what invalidation means

Those meanings belong to Layers 1 and 2. If a private pack wants a different semantic model, that is a signal the lower layers are incomplete, not that the private pack should silently fork the semantics. That follows directly from the audit’s emphasis on keeping `law` Doctrine-native, keeping `output` as the trust surface, and making composition follow the same explicit patching model as the rest of the language.   

---

## The right dependency graph

I would not make the layers a strict chain.

I would make them this shape:

```text
Layer 1: doctrine.core
    ↓
Layer 2: doctrine.std
   ↙  ↘
Layer 3   Layer 4
```

That is the healthy shape.

Layer 4 can import from Layer 3 **only when the concrete pack actually matches**. But in practice, when something from code review becomes useful to Lessons, the better move is usually:

1. notice the reuse
2. extract the generic piece down into Layer 2
3. let both Layer 3 and Layer 4 import the extracted piece

This avoids a common trap where “the first public app pack” quietly becomes the real framework. Doctrine’s own notes are very clear about wanting to earn complexity rather than assume it, and not to add primitives just to paper over a bad example. The same philosophy should apply to pack layering.  

---

## What belongs where, precisely

Here is the short boundary test I would use.

### Put it in Layer 1 if:

* it changes syntax or grammar
* it changes compiler validation
* it changes renderer obligations generically
* it creates a new cross-domain semantic invariant
* it is proven by at least one or two focused language examples

Examples:

* `law`
* `trust_surface`
* `current artifact ... via ...`
* `invalidate ... via ...`
* named law subsection patching
* emitted-carrier diagnostics
* one-current-subject-per-active-branch rules

### Put it in Layer 2 if:

* it is not language, but many domains will want it
* it can be authored in Doctrine today
* it has stable override points
* it does not reveal one company’s workflow truth

Examples:

* `CoordinationHandoff`
* `RouteOnlyTurns`
* `PortableTruthOutputs`
* `ModeAwarePortableTruthEdit`
* generic `ReviewVerdict`
* generic critic or editor role-home shells
* default `standalone_read` phrasing
* reusable outputs and workflow shells

### Put it in Layer 3 if:

* it is concrete and public
* it teaches or proves stdlib sufficiency
* it has domain nouns that are not universal enough for stdlib
* it is reusable by some users, but not truly cross-domain

Examples:

* code review
* spec review
* migration planning
* QA regression triage
* design critique

### Put it in Layer 4 if:

* it reveals internal domain logic
* it encodes company-specific paths, roles, or policies
* it depends on private skills or internal quality bars
* it would be awkward, leaky, or misleading in public

Examples:

* Lessons
* internal learning-design workflows
* proprietary acceptance gates
* organization-specific issue continuity rules
* product-specific evidence and validation conventions

---

## How zero-prose actually emerges

The way to get near-zero-prose authoring is not to force every human sentence into syntax. It is to let Layers 2 and 3 carry almost all of the default authored prose.

In practice, that means the author in Layer 4 mostly writes:

* imports
* enums
* inputs and outputs specific to the domain
* law sections
* override points
* only the rare prose line that truly cannot be formalized

Everything else is inherited.

A good test is this:

If five different private packs would write the same paragraph, that paragraph probably belongs in stdlib.

For example, these should usually migrate downward:

* downstream trust/readback wording
* route-only no-current wording
* generic stop/readback phrasing
* generic “one current artifact is current now” explanations
* generic critic independence language
* generic “preserve everything except owned scope” render text

The Lessons prose-bucket pass already shows where the recurring families are. The law spec then identifies which of those deserve compiler-owned semantics. Stdlib should capture the rest as default authored contracts and render text.   

---

## The best way to use code review as Layer 3

Code review is valuable here, but not because Lessons should inherit a `PullRequestReviewer` role home.

It is valuable because it forces you to answer public, generic questions such as:

* what is a good review handoff?
* what does route-only look like in a second domain?
* how does one-current-artifact work when the artifact is a review summary instead of a lesson manifest?
* how do invalidation and rebuild work when the base diff changes?
* what review-specific nouns belong in stdlib, and which ones stay pack-local?

That is exactly the kind of pressure that helps you build a solid Layer 2. The public code review pack is a proving ground and extraction engine.

So the healthy sequence is:

1. ship Layer 1 semantics
2. build a small but strong Layer 2
3. build code review as Layer 3
4. whenever code review invents something that feels generic, move it down to Layer 2
5. then build Lessons as Layer 4 on the extracted foundation

That keeps the architecture honest.

---

## My recommended practical repo strategy

I would do it like this.

### In the Doctrine repo

Keep both Layer 1 and Layer 2.

```text
doctrine/
  compiler/
  docs/
  examples/
  std/
    coordination/
    review/
    editing/
    role_home/
```

Possibly also keep Layer 3 *initially* in the Doctrine repo, but only as examples or public packs while it is still stabilizing.

```text
prompts/doctrine/packs_public/
  code_review/
```

That gives you one public place to evolve the public foundation. It also keeps extraction friction low in the early phase.

### In the proprietary repo

Keep Layer 4.

```text
company_agents/
  doctrine/
    lessons/
```

Import from `doctrine.std` and from `doctrine.packs_public` only when there is genuine semantic fit.

That split also matches the docs’ current philosophy that the structured source of truth lives in the Doctrine authoring surface, while runtime `AGENTS.md` stays compiled output. 

---

## The one governance rule I would make explicit

Every time a Layer 4 pack wants to reuse something from Layer 3, ask one question:

**Is this genuinely code-review-shaped, or is it actually a generic reusable pattern that only happened to appear there first?**

If it is generic, move it to Layer 2.
If it is still code-review-shaped, leave it in Layer 3.
If it is Lessons-shaped, keep it in Layer 4.

That one rule will prevent a huge amount of architectural drift.

---

## Bottom line

I think your instinct is exactly right:

* **(1) core language/compiler** lives in Doctrine
* **(2) public stdlib/foundation** also lives in Doctrine
* **(3) public concrete packs** like code review prove the foundation and create extraction pressure
* **(4) proprietary packs** like Lessons stay private and import what they need

The most important discipline is that **Layer 2, not Layer 3, should become the reusable foundation**. Code review is there to help you discover that foundation, not to become the hidden framework. Lessons then extends the public foundation with private nouns, private skills, private contracts, and private role graphs, while still benefiting from the same portable-truth and explicit-patching model. That is the architecture I would bet on.    

The strongest next move is to sketch a tiny `doctrine.std` with just four modules — `coordination`, `editing`, `review`, and `role_home` — then build one public `code_review` pack against it before refactoring Lessons onto the extracted pieces.




----


Yes. Here is the Layer 2 pass I would actually use as a working spec.

I’m treating Layer 2 as **`doctrine.std`**: a public, authored-in-Doctrine standard library that sits above Layer 1 core semantics and below public/private domain packs. It should be built from the current Doctrine design spine — example-first growth, `workflow` as the semantic home, `output` as the one produced-contract primitive, explicit ordered patching, first-class `inputs`/`outputs`/`skills` blocks, and the new portable-truth law surfaces from examples `30`–`38`. 

The headline theorem for Layer 2 should stay exactly the same as the v1 law work:

* `law` decides what is true now.
* `output` decides what the next owner must be able to read and trust.

Layer 2 exists to make that theorem reusable **without** turning Doctrine into a second coordination language, a packet system, or a Lessons-shaped framework.

---

# Layer 2 (`doctrine.std`) Specification

## 1. Status and purpose

Layer 2 is the **public standard library** for Doctrine. It is authored in ordinary Doctrine source files. It does not add syntax. It does not change parser behavior. It does not create new core semantics. It packages the most reusable generic doctrine patterns as stable public declarations.

Its purpose is fourfold:

1. eliminate repeated authored prose and repeated coordination outputs that multiple packs would otherwise copy,
2. give public and private packs a reusable portable-truth foundation,
3. keep generic coordination/readback/role-home structure out of proprietary packs,
4. create a disciplined extraction layer so Layer 3 and Layer 4 do not accidentally become shadow frameworks.

Layer 2 should not try to “finish the language.” It should consume the language the core has already earned and package the parts that are now clearly reusable. That is consistent with Doctrine’s example-first design notes and with the audit’s push to keep only the genuinely generic parts of Example 2.

---

## 2. Boundary with the other layers

### Layer 1 owns meaning

Layer 1 owns grammar, typing, diagnostics, rendering behavior, and compiler semantics: `agent`, `workflow`, explicit inheritance, `inputs`, `outputs`, `skills`, enums, and the v1 portable-truth surfaces like `law`, `trust_surface`, `current artifact ... via ...`, `current none`, `invalidate ... via ...`, `active when`, `mode`, `match`, `own only`, `preserve`, `support_only`, `ignore`, `forbid`, `stop`, and explicit `route`.

### Layer 2 owns reusable authored doctrine

Layer 2 owns public authored declarations built from those semantics:

* generic coordination outputs,
* generic trust-surface field conventions,
* generic route-only and portable-truth output/readback patterns,
* generic role-home workflows and shared support sections,
* generic enums only when they are truly cross-domain,
* documented law-section conventions for patchable workflow reuse.

### Layer 3 owns public domain packs

Layer 3 owns concrete public packs like code review. Those packs get domain nouns, domain artifacts, and domain workflows, but should import Layer 2 for generic coordination and role-home structure.

### Layer 4 owns private packs

Layer 4 owns proprietary packs like Lessons. Those packs should import Layer 2 directly, and only import Layer 3 when the domain fit is real. Anything found to be generic should be extracted downward into Layer 2, not left trapped in a public pack.

---

## 3. Hard rules for what may live in Layer 2

A declaration belongs in Layer 2 only if all of the following are true.

It is **generic**. It must not depend on proprietary nouns like lesson plans, section dossiers, or any private role graph. The law audit is explicit that the real pressure should be expressed in generic framework terms, not copied from Lessons jargon.

It is **authored in existing Doctrine**. Layer 2 cannot invent core surfaces through convention. If the language does not support a thing yet, Layer 2 must not fake it. This matters especially for things like output inheritance, parameterized workflows, free-floating obligations, `current status`, or targetless `route`. Those are either deferred or unsupported.

It is **stable under explicit patching**. Doctrine’s reusable surfaces are explicit and ordered. Anything central to Layer 2 has to compose through named blocks, imports, and `inherit` / `override`, not by invisible convention or omission. The law reuse example makes this especially important for named `law` subsections.

It has either **compiler-owned meaning** or **stable default prose value**. Some Layer 2 items are semantic wrappers around core features; others are reusable authored prose. Both are legitimate. What is not legitimate is a pseudo-formal feature that looks semantic but is really just atmosphere. That is the core audit criticism of `obligation`, `lens`, `concern`, `current status`, and widened basis-role families in v1.

It is **proven by examples**. Layer 2 should only standardize patterns already exercised by the example ladder or clearly implied by the shipped docs. Doctrine is explicitly example-first.

---

## 4. Non-goals for Layer 2

Layer 2 must not introduce or simulate:

* packet primitives,
* floating obligation runtimes,
* nominal artifact calculus,
* `current status`,
* top-level reusable `law`,
* targetless routes,
* root-binding/path-variable systems,
* `runtime_tools`,
* private host schemas disguised as “generic” stdlib APIs.

That last point matters. Layer 2 may document host field conventions, but it should not pretend that prompt-provided coordination state is fully typed if the core does not yet validate it as such. The I/O notes are clear that turn-level I/O should stay primitive and non-magical, and that packets are not the foundation.

---

## 5. The real v1 surface for Layer 2

Based on the examples you have now, Layer 2 v1 is four public module families:

```text
prompts/doctrine/std/
  coordination/
    enums.prompt
    inputs.prompt
    outputs.prompt
    workflows.prompt
  portable_truth/
    workflows.prompt
    conventions.md
  role_home/
    workflows.prompt
  docs/
    README.md
```

I would **not** ship a first Layer 2 `review/` module yet. Review is clearly coming, and the prose buckets show it as a major recurring family, but the current example ladder fully proves portable truth and coordination more strongly than it proves a stdlib-grade generic review kit. Review can become Layer 2 once Example 3 is similarly narrowed and proved.

---

# 6. Detailed spec for each Layer 2 module

## 6.1 `doctrine.std.coordination.enums`

This module should be tiny.

The current example ladder clearly proves that first-class enums are useful and that a generic rewrite regime is reusable across packs, but mode enums themselves remain pack-local because their members are domain nouns. `EditMode`, `MetadataPolishMode`, and similar enums should stay in Layers 3 and 4.

### Required export

```prompt
enum RewriteRegime: "Rewrite Regime"
    carry_forward: "carry-forward"
    rewrite: "rewrite"
```

This is justified by the rewrite-evidence example and by the capstone example, both of which use rewrite regime as a generic pass-state concept rather than a pack-specific noun.

### Requirements

* Layer 2 enums must represent closed vocabularies that are visibly cross-domain.
* Layer 2 must not define mode enums for one public or private pack.
* Every Layer 2 enum must have stable literal members and stable titles.
* If a mode vocabulary depends on a pack’s domain nouns, it stays outside Layer 2.

---

## 6.2 `doctrine.std.coordination.inputs`

This module should be conservative.

The examples repeatedly use `CurrentHandoff` as a prompt-provided `JsonObject`, but the core language still treats input shape lightly and does not yet have a schema-level input contract parallel to `output`+`json schema`. So Layer 2 may provide a **recommended input contract**, but it should present it as a host-coordination convention, not as a magically validated runtime model.

### Required export

```prompt
input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided coordination facts for currentness, active mode, preserve basis, rewrite regime, invalidations, and stop-or-route conditions."
```

### Requirements

* `CurrentHandoff` is a recommended base input, not a hidden runtime packet.
* Layer 2 may document expected field names such as `active_mode`, `preserve_basis`, `rewrite_regime`, and invalidation-related booleans, but those remain conventions until core input typing widens.
* Pack-specific owed-now flags should stay in Layer 3/4, because example names like `owes_edit` and `owes_metadata_polish` are still domain-shaped.

### What Layer 2 must not do here

It must not create a fake generic handoff schema that claims more type safety than the core actually supports. The audit repeatedly rejected floating coordination-token models for exactly this reason.

---

## 6.3 `doctrine.std.coordination.outputs`

This is the heart of Layer 2.

The examples prove two things very strongly:

1. `output` remains the only produced-contract primitive, and rich authored support should live there, not on a second artifact primitive.
2. the canonical downstream trust surface is `trust_surface`, carried by declared output fields, with `standalone_read` as its human-facing prose companion.

Because individual `output` declarations are not yet a shipped inheritance surface, Layer 2 should prefer **explicit named output families**, even if some duplication remains. That is more Doctrine-native than pretending output inheritance exists.

### Required exports

Layer 2 v1 should export these explicit outputs.

#### A. `CoordinationComment`

For route-only or block-only turns where no current artifact is carried.

```prompt
output CoordinationComment: "Coordination Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    standalone_read: "Standalone Read"
        "A downstream owner should be able to read this comment alone and understand the coordination state for this turn."
```

This is justified directly by example `30`, where route-only work uses `current none` and a coordination comment with no trust-surface carrier.

#### B. `PortableTruthHandoff`

For one-current-artifact carriage.

```prompt
output PortableTruthHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    trust_surface:
        current_artifact

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know which artifact is current now."
```

This is proved by example `31`.

#### C. `ModeAwarePortableTruthHandoff`

For branches that also need one active mode.

```prompt
output ModeAwarePortableTruthHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    active_mode: "Active Mode"
        "Name the one active mode for this pass."

    trust_surface:
        current_artifact
        active_mode

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know which artifact is current now and which mode is active."
```

This is proved by example `32`. 

#### D. `ComparisonPortableTruthHandoff`

For branches that need currentness plus comparison-only basis.

```prompt
output ComparisonPortableTruthHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    comparison_basis: "Comparison Basis"
        "Name any comparison-only artifacts used in this pass."

    trust_surface:
        current_artifact
        comparison_basis

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now and what was comparison-only."
```

This follows the rewrite-aware and law-reuse examples.

#### E. `InvalidationPortableTruthHandoff`

For branches that need currentness plus invalidations.

```prompt
output InvalidationPortableTruthHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    invalidations: "Invalidations"
        "Name any artifacts that are no longer current."

    trust_surface:
        current_artifact
        invalidations

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now and what is no longer current."
```

This is proved by example `36`.

#### F. `PortableTruthHandoffFull`

For the fully integrated portable-truth model.

```prompt
output PortableTruthHandoffFull: "Coordination Handoff"
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
        comparison_basis when CurrentHandoff.peer_comparison_used
        rewrite_exclusions when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
        invalidations when CurrentHandoff.structure_changed

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now, why it is current, and what no longer counts as current."
```

This is justified by the capstone.

### Output-family requirements

Every Layer 2 coordination output must obey these requirements:

* `target` must remain `TurnResponse`.
* `shape` must remain `Comment`.
* every trust carrier must be a real declared output field,
* every trust carrier used by law must appear in `trust_surface`,
* `standalone_read` must never promise more than the declared trust surface actually carries,
* field titles must remain stable and generic,
* if a field is conditional in `trust_surface`, the prose must read conditionally too,
* shared output modules should keep those conditions rooted in shipped output
  semantics rather than in imported input-guard conventions that the current
  compiler does not allow on ordinary outputs.

That last rule is important because your example audit caught places where rendered prose outran the actual trust surface. Layer 2 should make that impossible by design.

---

## 6.4 `doctrine.std.coordination.workflows`

This module should be small in v1.

The current core does not have workflow parameters or abstract law subsections as a formally shipped feature. So Layer 2 should not pretend it can offer a giant generic workflow framework. Instead, it should export only workflows that are truly reusable **as written**, plus a documented naming convention for law subsections used by downstream inherited workflows.

### Required exported workflow

#### `RouteOnlyTurns`

```prompt
workflow RouteOnlyTurns: "Route-Only Triage"
    "Handle turns that can only stop and reroute."

    law:
        when CurrentHandoff.missing:
            current none
            stop "Current handoff is missing."
            route "Route the same issue back to RoutingOwner." -> RoutingOwner

        when CurrentHandoff.unclear:
            current none
            stop "Current handoff is unclear."
            route "Route the same issue back to RoutingOwner." -> RoutingOwner
```

This is fully justified by example `30`.

### Required exported agent

#### `RoutingOwner`

```prompt
agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue."
    workflow: "Instructions"
        "Take back the same issue when route-only work cannot continue safely."
```

This is deliberately generic and appears across the portable-truth examples as the neutral reroute owner.

### Workflow law section convention

Even where Layer 2 does not export a fully generic workflow, it should export a **convention** for named `law` subsections. This is crucial for pack composition because example `37` proves that law reuse is explicit and subsection-based.

Layer 2 should standardize these section keys:

* `activation`
* `mode_selection`
* `currentness`
* `scope`
* `evidence`
* `invalidation`
* `stop_lines`

These are not new language features. They are stdlib naming conventions. A Layer 2 or higher-layer reusable workflow that uses `law` should prefer these keys and document which are required override points. The capstone and audit both converge on this structure.

### Requirements

* Any Layer 2 workflow with `law` must use named subsections if it is meant to be inherited.
* Every inherited child must account for every inherited `law` subsection exactly once, because that is Doctrine’s existing explicit patching model.
* Layer 2 must not require top-level reusable `law` declarations, since those are explicitly deferred from v1.

---

## 6.5 `doctrine.std.portable_truth.workflows`

This module is not a bag of generic magic workflows. It is a small set of **reference workflow patterns** and **documented law conventions** that downstream packs can adopt.

### Required content

#### A. `README`-style conventions

It should define the portable-truth section contract:

* `activation` chooses whether the branch is live,
* `mode_selection` binds one typed mode if relevant,
* `currentness` binds one current artifact or `current none`,
* `scope` defines ownership and preservation,
* `evidence` defines support-only and rewrite-evidence law,
* `invalidation` revokes portability where needed,
* `stop_lines` holds stop + explicit route behavior.

#### B. Reference workflow skeleton

Layer 2 may ship a **documented pattern** like this, even if it is not directly imported as a complete turnkey workflow:

```prompt
workflow PortableTruthWork: "Portable Truth Work"
    "Keep portable truth explicit and narrow."

    law:
        activation:
            ...

        mode_selection:
            ...

        currentness:
            ...

        scope:
            ...

        evidence:
            ...

        invalidation:
            ...

        stop_lines:
            ...
```

This is not a new syntax proposal; it is a library convention for how reusable workflows should be organized. Example `37` makes that organization valuable, because reuse works only if the override points are stable and explicit.

### Requirements

* Layer 2 portable-truth workflows must never smuggle currentness in prose when `law` can express it.
* They must never shift downstream trust back into vague handoff narrative once `trust_surface` exists.
* They must keep rewrite-evidence, comparison-only basis, and invalidation consequences explicit when those matter.
* They must not use deferred abstractions like `obligation`, `lens`, `concern`, or `current status`.

---

## 6.6 `doctrine.std.role_home.workflows`

This is where a large amount of the “zero-prose by default” value actually lives.

The prose-bucket pass showed that many recurring lines are not domain-specific at all. They are generic role-home jobs: seam identity, turn ordering, current-truth discipline, output readback normalization, lane boundaries, and skill routing. Those do not all belong in Layer 1 semantics, but they absolutely do belong in a reusable stdlib.

### Required exports

I would start with these reusable workflows.

#### `HowToTakeATurn`

```prompt
workflow HowToTakeATurn: "How To Take A Turn"
    "Read the current artifact and the declared carrier first."
    "Do the required analysis before you emit durable output."
    "Close the turn by making currentness, stop lines, and routes explicit."
```

This is justified by the design notes’ emphasis on role-home composition and by the prose-bucket emphasis on turn protocol and work ordering.

#### `CurrentTruthDiscipline`

```prompt
workflow CurrentTruthDiscipline: "Current Truth"
    "Treat the declared current artifact as authoritative for this turn."
    "Treat comparison-only artifacts as support, not as current truth."
    "Do not treat nearby files, stale siblings, or unaccepted artifacts as current merely because they exist."
```

This is exactly the kind of prose the buckets identified as recurring and generic, and it complements the formal `law` layer rather than competing with it.

#### `CoordinationReadbackDiscipline`

```prompt
workflow CoordinationReadbackDiscipline: "Coordination Readback"
    "Make the trust surface explicit for the next owner."
    "Do not compress currentness, comparison-only basis, rewrite exclusions, or invalidations into vague summary language."
```

This follows from the output/readback normalization bucket and from the trust-surface output family.

#### `SkillFirstSupport`

```prompt
workflow SkillFirstSupport: "Skills And Support"
    "Prefer explicit reusable skills for specialist judgment."
    "Do not smuggle deep quality bars into one-off workflow prose when a named skill can carry them."
```

Doctrine’s design notes are explicit that the language is skill-first and does not want a parallel `runtime_tools` surface.

### Requirements

* Role-home workflows in Layer 2 must stay generic and domain-neutral.
* They may mention currentness, outputs, and trust surfaces in generic terms.
* They must not hardcode private artifacts, paths, or role graphs.
* They are allowed to remain prose-heavy, because their job is to carry shared authored defaults, not to simulate missing semantics.

---

# 7. Canonical Layer 2 field vocabulary

Layer 2 should make a small set of trust/readback field names stable.

Based on the example ladder, the canonically earned field names are:

* `current_artifact`
* `active_mode`
* `preserve_basis`
* `comparison_basis`
* `rewrite_exclusions`
* `invalidations`

Layer 2 should **not** yet standardize:

* `trigger_reason`
* `next_owner`
* `next_step`
* typed obligation payloads
* status-carried currentness

Those appeared in earlier design pressure or in prose buckets, but the current example ladder has not yet proven them as a stable generic Layer 2 output vocabulary.

---

# 8. What Layer 2 should deliberately leave out

The examples and audit are clear enough that this should be written as a hard exclusion list.

Layer 2 v1 should not contain:

* `obligation`
* `lens`
* `concern`
* `current status`
* nominal `artifact` types
* top-level reusable `law`
* generic review verdict kits
* conditional output emission semantics
* host-input schemas masquerading as compiler-enforced types.

The strongest reason is architectural: these are exactly the abstractions the audit called out as either too early, too project-shaped, or not yet fully integrated with Doctrine’s current model. Layer 2 should not sneak them back in under a “library” label.

---

# 9. Composition model: how Layer 2 should be used

## 9.1 Layer 2 + Layer 3 public pack

A public `code_review` pack should import Layer 2 for coordination and role-home defaults, while defining its own domain nouns.

Example:

```prompt
import doctrine.std.coordination.inputs
import doctrine.std.coordination.outputs
import doctrine.std.coordination.enums
import doctrine.std.role_home.workflows

enum ReviewMode: "Review Mode"
    correctness: "correctness"
    architecture: "architecture"
    security: "security"

input PullRequestDiff: "Pull Request Diff"
    source: File
        path: "review_root/PR_DIFF.md"
    shape: MarkdownDocument
    requirement: Required

output ReviewSummary: "Review Summary"
    target: File
        path: "review_root/review_summary.json"
    shape: JsonObject
    requirement: Required

agent PullRequestReviewer:
    role: "Review one pull request in exactly one mode."
    read_first: doctrine.std.role_home.workflows.CurrentTruthDiscipline
    how_to_take_a_turn: doctrine.std.role_home.workflows.HowToTakeATurn

    workflow: "Review Work"
        "Apply the requested review mode and keep one current review artifact explicit."

    law:
        activation:
            active when CurrentHandoff.review_requested

        mode_selection:
            mode review_mode = CurrentHandoff.active_mode as ReviewMode

        currentness:
            current artifact ReviewSummary via doctrine.std.coordination.outputs.PortableTruthHandoff.current_artifact
```

What lives where here is very clean:

* `ReviewMode`, `PullRequestDiff`, and `ReviewSummary` are Layer 3,
* `CurrentHandoff`, `PortableTruthHandoff`, and role-home defaults are Layer 2,
* `law`, `current artifact ... via ...`, and `trust_surface` semantics are Layer 1.

## 9.2 Layer 2 + Layer 4 private pack

A private Lessons-like pack should do the same thing, but with proprietary nouns:

```prompt
import doctrine.std.coordination.inputs
import doctrine.std.coordination.outputs
import doctrine.std.coordination.enums
import doctrine.std.role_home.workflows

enum MetadataPolishMode: "Metadata Polish Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"

input ApprovedPlan: "Approved Plan" ...
input ApprovedStructure: "Approved Structure" ...
input AcceptedPeerSet: "Accepted Peer Set" ...

output PrimaryManifest: "Primary Manifest" ...
output SectionMetadata: "Section Metadata" ...
output SectionReview: "Section Review" ...

agent MetadataPolisher:
    role: "Handle the last narrow wording pass after structure is already locked."

    read_first: doctrine.std.role_home.workflows.CurrentTruthDiscipline
    how_to_take_a_turn: doctrine.std.role_home.workflows.HowToTakeATurn
    coordination_readback: doctrine.std.role_home.workflows.CoordinationReadbackDiscipline

    outputs: "Outputs"
        PrimaryManifest
        SectionMetadata
        doctrine.std.coordination.outputs.PortableTruthHandoffFull

    workflow: "Metadata Polish"
        "Work in exactly one metadata mode."

    law:
        activation:
            active when CurrentHandoff.owes_metadata_polish

        mode_selection:
            mode pass_mode = CurrentHandoff.active_mode as MetadataPolishMode

        currentness:
            match pass_mode:
                MetadataPolishMode.manifest_title:
                    current artifact PrimaryManifest via PortableTruthHandoffFull.current_artifact
                    must CurrentHandoff.preserve_basis == ApprovedPlan

                MetadataPolishMode.section_summary:
                    current artifact SectionMetadata via PortableTruthHandoffFull.current_artifact
                    must CurrentHandoff.preserve_basis == ApprovedStructure
```

Again, Layer 2 is providing the portable-truth carrier and the reusable role-home prose, while the private pack owns the domain nouns and actual branch law. That is exactly the composition you want.

---

# 10. Extraction rules: when something moves into Layer 2

A feature or declaration should be promoted into Layer 2 only when all of the following are true:

It appears in at least two places: either two different example families, or one public pack plus one private pack.

It can be named without domain nouns.

It either has direct compiler-owned meaning or clearly valuable default prose.

It has a documented override surface.

It does not rely on unsupported core features.

It improves drift materially rather than just making source look prettier.

This rule matters because your earlier iterations repeatedly ran into the same trap: some abstractions were beautiful but not yet earned. Layer 2 should be strict about earnedness, not a back door for speculative primitives.

---

# 11. Testing and conformance requirements for Layer 2

Layer 2 should have its own conformance bar.

Every exported Layer 2 declaration should have:

* at least one positive import/use example,
* a rendered reference output if it affects runtime Markdown,
* a patch/override example if it is meant to be inherited,
* no dependency on private packs,
* a README entry explaining its intended override points and what remains pack-local.

For coordination outputs specifically:

* `trust_surface` fields must all exist,
* rendered `standalone_read` must not overpromise beyond the trust surface,
* a carrier field used by `current artifact ... via ...` or `invalidate ... via ...` must appear in `trust_surface`,
* the carrier output must be emitted,
* if the current artifact is itself an output artifact, the concrete pack must also emit that artifact. That last one was the real semantic hole you already identified in the example pack and should stay enforced at the Layer 1/Layer 2 boundary.

For law-section conventions:

* reusable Layer 2 workflows with law must use named subsections,
* child workflows must account for all inherited sections exactly once,
* Layer 2 docs must state the intended subsection keys.

---

# 12. The actual v1 implementation plan I would recommend

If you want the smallest credible Layer 2 that still feels real, I would implement it in this order:

## Phase A: coordination outputs + one route-only workflow

Ship:

* `RewriteRegime`
* `CurrentHandoff`
* `CoordinationComment`
* `PortableTruthHandoff`
* `ModeAwarePortableTruthHandoff`
* `ComparisonPortableTruthHandoff`
* `InvalidationPortableTruthHandoff`
* `PortableTruthHandoffFull`
* `RoutingOwner`
* `RouteOnlyTurns`

This gives immediate value and is fully grounded by examples `30`, `31`, `32`, `35`, `36`, and `38`.

## Phase B: role-home prose defaults

Ship:

* `HowToTakeATurn`
* `CurrentTruthDiscipline`
* `CoordinationReadbackDiscipline`
* `SkillFirstSupport`

This is where the zero-prose payoff starts becoming visible, because these are exactly the recurring prose buckets that do not need to stay pack-local.

## Phase C: portable-truth conventions doc

Ship:

* the law subsection naming convention,
* the field vocabulary contract,
* examples of public-pack and private-pack composition,
* the promotion rule for future Layer 2 extraction.

This keeps Layer 2 disciplined instead of letting it sprawl.

---

# 13. Bottom line

If I reduce all of this to the strongest single definition:

**Layer 2 is the public Doctrine-authored standard library for portable-truth coordination and reusable role-home defaults.**
It is not new syntax.
It is not a packet layer.
It is not a public domain pack.
It is the place where the generic output/readback surfaces, coordination carriers, route-only patterns, and recurring role-home prose live so that Layers 3 and 4 can stop copying them.

And the most important concrete rule is:

**Layer 2 should be output-heavy before it is workflow-heavy.**

That is the cleanest consequence of everything your examples and audits have converged on:

* core `law` gives you local truth,
* Layer 2 `output` declarations give you portable downstream trust,
* Layer 2 role-home workflows carry the remaining generic prose,
* public/private packs keep their own nouns and branch law.

That draft is now materially shipped under `prompts/doctrine/std/**`, with the
direction doc still serving as the higher-level explanation of why the layer
split exists.

-----


I’m taking **Phase 3** to mean **Phase C from the Layer 2 plan**: the **portable-truth conventions/documentation phase** for `doctrine.std`, not a new parser phase. This phase should **codify how to use the already-earned v1 portable-truth surface** from examples `30`–`38`, rather than inventing more language. The examples, the tightened law spec, and the audit all converge on the same core split: `workflow` stays the semantic home, `output` stays the produced-contract primitive, `law` decides what is true now, and `output` says what the next owner must be able to read and trust. Doctrine also stays example-first, explicit, patchable, non-packetized, and hostile to speculative abstractions that outrun compiler-owned meaning. 

Below is the version I would actually freeze.

---

# Phase 3 Spec: `doctrine.std.portable_truth`

## 1. What Phase 3 is

Phase 3 is a **normative standard-library conventions layer**. It does **not** add syntax. It does **not** change grammar. It does **not** widen Doctrine beyond the frozen v1 portable-truth surface. Its job is to document and standardize how public and private packs should compose:

* `law` inside `workflow`
* `trust_surface` inside `output`
* one current artifact per active branch, or `current none`
* explicit scope / preserve / evidence / invalidation / stop / route structure
* explicit law subsection naming for reuse
* stable trust-carrier field vocabulary
* stable render expectations
* stable composition patterns with the Layer 2 coordination and role-home modules.

So this phase is **not** “new features.” It is the point where the already-earned surface becomes a **public doctrine pattern** instead of just a set of examples. That matches Doctrine’s example-first design and the rule that new examples should stay narrow and that you should not add a primitive just to paper over a bad example.

---

## 2. Deliverables

I would make Phase 3 ship these exact deliverables:

```text
prompts/doctrine/std/
  portable_truth/
    README.md
    EXAMPLES.md
    CONFORMANCE.md
```

`README.md` is the normative spec.
`EXAMPLES.md` is the small curated example appendix.
`CONFORMANCE.md` is the pack-author checklist and extraction policy.

You could collapse `EXAMPLES.md` and `CONFORMANCE.md` into the README if you want one document, but I would still structure it as three conceptual parts.

Phase 3 should **not** ship new `.prompt` declarations purely for its own sake. The usable declarations already live in earlier Layer 2 modules and in the core example ladder. Phase 3 explains **how to use them together**. That is consistent with the current Doctrine split where the language stays small, `output` remains the one produced-contract primitive, and richer rules live on authored contracts and examples rather than on speculative new primitives.

---

## 3. Status line and theorem

The README should begin with something very close to this:

> `doctrine.std.portable_truth` is the Layer 2 conventions package for work that must keep one portable current artifact explicit across turns. It standardizes how `law` and `output` cooperate without opening a packet model or a second coordination language.

Then the document should state the theorem explicitly:

* `law` decides what is true now.
* `current artifact ... via ...` binds that truth to a declared carrier.
* `output` declares the downstream trust surface.
* `invalidate ... via ...` revokes portability when structural truth moves.
* deferred features return only if they strengthen that same model instead of opening a second coordination plane.

That theorem is the whole point of Phase 3. If the README does not make it explicit, the module will sprawl.

---

## 4. Scope and non-goals

The README should say plainly that Phase 3 standardizes use of these v1 surfaces:

* `law`
* `trust_surface`
* `current artifact ... via ...`
* `current none`
* `active when`
* `mode`
* `must`
* `when`
* `match`
* `own only`
* `preserve exact`
* `preserve structure`
* `preserve decisions`
* `preserve mapping`
* `preserve vocabulary`
* `support_only ... for comparison`
* `ignore ... for truth`
* `ignore ... for comparison`
* `ignore ... for rewrite_evidence`
* `invalidate ... via ...`
* `forbid`
* `stop`
* explicit `route "..." -> Agent`
* named `law` subsections inside inherited workflows.

And it should explicitly exclude:

* `obligation`
* `lens`
* `concern`
* `current status`
* nominal `artifact` typing
* targetless `route`
* top-level reusable `law`
* packet-like or free-floating coordination token models
* a full `review` primitive
* root binding and `runtime_tools`.

That exclusion list matters because Phase 3 is where a standard library can accidentally sneak speculative design back in. It should not.

---

## 5. Dependencies

Phase 3 should declare itself dependent on four things that are already earned:

1. **Core Doctrine semantics**
   The parser, renderer, explicit inheritance model, and first-class `inputs` / `outputs` / `skills` blocks remain Layer 1 concerns. `workflow` is the semantic home; `output` is the produced-contract primitive.

2. **Layer 2 coordination modules**
   Phase 3 assumes the existence of standard coordination outputs and the `CurrentHandoff` input convention from earlier Layer 2 phases. The examples repeatedly use handoff-carried facts and `TurnResponse` comment outputs as the trust carrier.

3. **Layer 2 role-home defaults**
   Phase 3 assumes generic prose defaults still belong in shared role-home workflows rather than being recoded as fake semantics. The prose-bucket pass showed recurring non-semantic families like turn protocol, current-truth discipline, and readback normalization that belong in reusable authored defaults.

4. **The example ladder `30`–`38`**
   These examples are the proof surface for the portable-truth family: route-only work, currentness, typed modes, scope/preservation, evidence roles, invalidation, law patching, and the capstone.

---

## 6. Normative law-section convention

This is the most important concrete thing Phase 3 should standardize.

The README should declare that **reusable portable-truth workflows SHOULD organize `law` into these named subsections**:

* `activation`
* `mode_selection`
* `currentness`
* `scope`
* `evidence`
* `invalidation`
* `stop_lines`

These names are **conventions**, not new grammar. But they should be treated as the canonical Layer 2 layout because example `37` proves that `law` reuse only stays clean when subsection identities are explicit and patchable. The capstone structure already naturally falls into these buckets.

The README should define each subsection precisely.

### `activation`

Purpose: decide whether the workflow branch is live.

Allowed statements:

* `active when`
* `must` only when it tightens activation preconditions

Disallowed as a convention:

* ownership, invalidation, or routes unless they are truly part of an activation stop line

### `mode_selection`

Purpose: bind exactly one typed mode for the turn when the workflow is mode-aware.

Allowed statements:

* `mode`
* `must`
* `match` only when it is selecting downstream mode-dependent facts

### `currentness`

Purpose: bind exactly one current artifact per active leaf branch, or `current none`.

Allowed statements:

* `current artifact ... via ...`
* `current none`
* `match`
* `must`

### `scope`

Purpose: define the writable boundary and the preserved outside world.

Allowed statements:

* `own only`
* `preserve exact`
* `preserve structure`
* `preserve decisions`
* `preserve mapping`
* `preserve vocabulary`
* `forbid`
* `match`
* `must`

### `evidence`

Purpose: define comparison-only evidence and rewrite-evidence exclusions.

Allowed statements:

* `support_only ... for comparison`
* `ignore ... for truth`
* `ignore ... for comparison`
* `ignore ... for rewrite_evidence`
* `must`

### `invalidation`

Purpose: explicitly retire downstream portable truth when structural truth moves.

Allowed statements:

* `invalidate ... via ...`
* `when`
* `match`
* `must`

### `stop_lines`

Purpose: define the branch-local failure boundary and explicit reroute.

Allowed statements:

* `when`
* `stop`
* explicit `route "..." -> Agent`

This subsection naming standard gives Layer 2 and higher packs a predictable override surface while staying faithful to Doctrine’s explicit ordered patching model.

---

## 7. Canonical trust-surface vocabulary

Phase 3 should define a **small stable public vocabulary** for portable-truth carriers on outputs. Based on the capstone and intermediate examples, the canonically earned field names are:

* `current_artifact`
* `active_mode`
* `preserve_basis`
* `comparison_basis`
* `rewrite_exclusions`
* `invalidations`

The README should specify their meanings.

### `current_artifact`

The one artifact that is current now.
Required whenever any active branch uses `current artifact ... via ...`.

### `active_mode`

The one active mode for the pass.
Required whenever the workflow binds a mode and downstream pickup depends on it.

### `preserve_basis`

The upstream declaration whose decisions remain authoritative.
Required whenever mode-specific preserve truth is important for downstream trust.

### `comparison_basis`

Artifacts that were comparison-only and did not become current truth.
Required whenever `support_only ... for comparison` materially shapes downstream review or continuity.

### `rewrite_exclusions`

Fields or artifacts whose old values do not count as rewrite evidence.
Required whenever `ignore ... for rewrite_evidence` matters to downstream understanding.

### `invalidations`

Artifacts that are no longer portable as current truth.
Required whenever any active branch uses `invalidate ... via ...`.

The README should also state that `standalone_read` is the human-facing companion to `trust_surface`, and must never promise more than the trust surface actually carries. Your example review already exposed why that rule matters.

---

## 8. Currentness conventions

Phase 3 should make the following rules normative for all Layer 2 portable-truth examples and recommended for packs.

### 8.1 Exactly one current subject per active leaf branch

Each active leaf branch must resolve to exactly one of:

* one `current artifact ... via ...`
* or `current none` for route-only turns.

### 8.2 Transferable currentness always names its carrier

If currentness is portable, it must be written in the combined form:

```prompt
current artifact PrimaryManifest via CoordinationHandoff.current_artifact
```

Phase 3 should explicitly prefer this combined form because it keeps local truth and downstream truth in one statement.

### 8.3 Carrier invariants

If a workflow uses `current artifact X via Output.field`, then:

* `Output` must be a declared `output`
* `field` must exist on that output
* `field` must be listed in that output’s `trust_surface`
* the carrier output must be emitted by the concrete agent.

### 8.4 Phase 3 strengthening: emitted current output

I would add one extra Layer 2 rule here:

If the current artifact is itself an `output` root, the concrete agent should also emit that output in the active workflow family.

That closes the remaining semantic hole you already identified in the examples, where the carrier could be emitted without the named current output being emitted.

### 8.5 `current none`

`current none` is reserved for route-only or block-only turns. It requires no carrier and should pair with a coordination comment that explains that no durable artifact was carried forward.

---

## 9. Scope and preservation conventions

Phase 3 should say that the **minimum complete narrow-edit shape** for a portable-truth lane is:

* one current artifact
* one owned path set
* exact preserve of the remainder
* one preserved decision basis
* optional forbids for explicitly out-of-bounds fields.

A canonical pattern:

```prompt
scope:
    own only {SectionMetadata.name, SectionMetadata.description}
    preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
    preserve decisions ApprovedStructure
    forbid {SectionMetadata.taxonomy, SectionMetadata.flags}
```

Phase 3 should also document the contradiction rules that the examples prove:

* owned scope must not overlap exact-preserved scope
* owned scope must not overlap forbidden scope
* owned paths must be addressable
* owned paths must be rooted in the current artifact.

And it should define a clear reading order for the preserve kinds:

* `preserve exact` means preserve unowned fields literally
* `preserve structure` means preserve structural arrangement
* `preserve decisions` means preserve upstream decision authority
* `preserve mapping` means preserve established mapping surfaces
* `preserve vocabulary` means preserve established controlled vocabulary. 

---

## 10. Evidence and rewrite conventions

Phase 3 should define `evidence` as the home for two jobs:

1. comparison-only evidence
2. rewrite-evidence exclusions

That section should recommend this pattern:

```prompt
evidence:
    support_only AcceptedPeerSet for comparison
    ignore {SectionMetadata.name, SectionMetadata.description}
        for rewrite_evidence
        when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
```

This is exactly the split the frozen spec keeps in v1: only `truth`, `comparison`, and `rewrite_evidence` remain first-class basis roles. Everything wider was intentionally cut.

The README should explicitly say:

* comparison-only artifacts may inform but must not become current truth
* rewrite-evidence exclusions may coexist with exact preservation
* the fact that something is preserved does not mean it remains admissible rewrite evidence.

---

## 11. Invalidation conventions

Phase 3 should state invalidation in the strongest clean v1 form:

```prompt
invalidate SectionReview via CoordinationHandoff.invalidations
```

Meaning:

* the target may still exist physically
* it is no longer portable as current truth
* downstream owners must be able to read that loss of authority on the declared trust carrier
* portability returns only when a later turn explicitly rebuilds or reissues currentness.

The README should also say:

* invalidations belong in the `invalidation` subsection
* the carrier field must be in `trust_surface`
* invalidation should usually pair with an explicit stop and route to a rebuild-capable owner
* cross-turn rebuild proof may remain partly example-proved rather than wholly compile-time-decidable in v1.

---

## 12. Stop and route conventions

Phase 3 should preserve Doctrine’s narrow route bias.

Portable-truth docs should standardize:

```prompt
stop "Mode or preserve basis is unclear."
route "Route the same issue back to RoutingOwner." -> RoutingOwner
```

and should explicitly reject loose or targetless routing patterns. That stays aligned with the frozen spec and with older Doctrine’s narrow `route "..." -> AgentName` direction.

The README should say that `stop_lines` is where:

* ambiguity is surfaced
* authority failure is made explicit
* ownership transitions are named honestly

and that route-only work should prefer `current none` plus a coordination comment rather than inventing a fake specialist artifact.

---

## 13. Render contract

Phase 3 should define a **render contract**, not only a syntax convention, because Doctrine’s runtime remains human-first Markdown. The examples already imply a stable pattern.

At minimum, the README should standardize these render expectations:

* `active when` renders as “This pass runs only when …”
* `mode` + `match` renders as “Work in exactly one mode:” followed by the allowed values
* `current artifact ... via ...` renders as “Current artifact: X.”
* `current none` renders as “There is no current artifact for this turn.”
* `own only` renders as “Own only …”
* `preserve exact` renders as “Preserve every other … exactly.”
* `preserve decisions` renders as “Preserve the decisions already owned by …”
* `support_only ... for comparison` renders as “X is comparison-only support evidence.”
* `ignore ... for rewrite_evidence` renders as “On rewrite passes, X does not count as rewrite evidence.”
* `invalidate ... via ...` renders as “X is no longer current.”
* `stop` + `route` render together as a clear stop-or-reroute instruction.

The README should be explicit that these are **render conventions**, not new keywords.

---

## 14. Temporary convention for mode-exclusive outputs

Phase 3 should document one awkward but practical convention from the current example ladder.

In examples like `32`, `33`, `37`, and `38`, the agent `outputs` blocks list multiple artifacts even though only one branch is current at a time. The README should explicitly say:

> Until Doctrine gains branch-conditional output emission, portable-truth workflows may declare an **output universe** containing all artifacts the role may emit across mutually exclusive branches. `current artifact` determines which artifact is portable current in the active branch. The carrier output is always emitted.

That makes the current example style honest instead of leaving it implicit. It is a conventions-layer rule, not a change to Layer 1 semantics. It also keeps the examples usable while acknowledging the limitation.

---

## 15. Required example appendix

`EXAMPLES.md` should include at least these four examples.

### Example A: route-only no-current

A thin wrapper around the `30` shape.

Purpose:
show `current none`, `stop`, explicit route, and the absence of a trust carrier.

### Example B: minimal portable currentness

A thin wrapper around `31`.

Purpose:
show `current artifact ... via ...`, carrier invariants, and a handoff output with only `current_artifact`. 

### Example C: mode-aware narrow edit

A wrapper around `32` + `33`.

Purpose:
show mode binding, one current artifact per branch, owned scope, exact preservation, preserved decisions, and forbids.

### Example D: rewrite-aware child

A wrapper around `37` + `38`.

Purpose:
show inherited law subsections, evidence override, invalidation override, and full trust-surface carriage.

---

## 16. Composition examples

These should be in the README, because Phase 3 is supposed to teach how the pieces compose.

### 16.1 Public pack example: code review

```prompt
import doctrine.std.coordination.inputs
import doctrine.std.coordination.outputs
import doctrine.std.coordination.enums
import doctrine.std.role_home.workflows

enum ReviewMode: "Review Mode"
    correctness: "correctness"
    architecture: "architecture"

input PullRequestDiff: "Pull Request Diff"
    source: File
        path: "review_root/PR_DIFF.md"
    shape: MarkdownDocument
    requirement: Required

input AcceptedBaseline: "Accepted Baseline"
    source: File
        path: "review_root/ACCEPTED_BASELINE.md"
    shape: MarkdownDocument
    requirement: Advisory

output ReviewSummary: "Review Summary"
    target: File
        path: "review_root/review_summary.json"
    shape: JsonObject
    requirement: Required

agent RoutingOwner:
    role: "Own explicit reroutes when review work cannot continue."
    workflow: "Instructions"
        "Take back the same review when local specialist work cannot continue safely."

agent PullRequestReviewer:
    role: "Review one pull request in exactly one requested mode."
    read_first: doctrine.std.role_home.workflows.CurrentTruthDiscipline
    how_to_take_a_turn: doctrine.std.role_home.workflows.HowToTakeATurn
    coordination_readback: doctrine.std.role_home.workflows.CoordinationReadbackDiscipline

    inputs: "Inputs"
        doctrine.std.coordination.inputs.CurrentHandoff
        PullRequestDiff
        AcceptedBaseline

    outputs: "Outputs"
        ReviewSummary
        doctrine.std.coordination.outputs.PortableTruthHandoffFull

    workflow: "Code Review"
        "Keep one current review artifact explicit and preserve the approved baseline."

        law:
            activation:
                active when CurrentHandoff.review_requested

            mode_selection:
                mode review_mode = CurrentHandoff.active_mode as ReviewMode

            currentness:
                current artifact ReviewSummary via PortableTruthHandoffFull.current_artifact

            scope:
                own only ReviewSummary.*
                preserve decisions PullRequestDiff

            evidence:
                support_only AcceptedBaseline for comparison
                ignore AcceptedBaseline for rewrite_evidence when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite

            stop_lines:
                when unclear(review_mode, CurrentHandoff.preserve_basis):
                    stop "Review mode or preserve basis is unclear."
                    route "Route the same issue back to RoutingOwner." -> RoutingOwner
```

What lives where:

* `ReviewMode`, `PullRequestDiff`, and `ReviewSummary` are pack-local
* `CurrentHandoff`, `PortableTruthHandoffFull`, and role-home discipline come from Layer 2
* `law`, `trust_surface`, `current artifact ... via ...`, and invalidation semantics come from Layer 1.

### 16.2 Private pack example: metadata polish

```prompt
import doctrine.std.coordination.inputs
import doctrine.std.coordination.outputs
import doctrine.std.coordination.enums
import doctrine.std.role_home.workflows

enum MetadataPolishMode: "Metadata Polish Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"

input ApprovedPlan: "Approved Plan" ...
input ApprovedStructure: "Approved Structure" ...
input AcceptedPeerSet: "Accepted Peer Set" ...

output PrimaryManifest: "Primary Manifest" ...
output SectionMetadata: "Section Metadata" ...
output SectionReview: "Section Review" ...

agent MetadataPolisher:
    role: "Handle the last narrow wording pass after structure is already locked."
    read_first: doctrine.std.role_home.workflows.CurrentTruthDiscipline
    how_to_take_a_turn: doctrine.std.role_home.workflows.HowToTakeATurn
    coordination_readback: doctrine.std.role_home.workflows.CoordinationReadbackDiscipline

    outputs: "Outputs"
        PrimaryManifest
        SectionMetadata
        SectionReview
        doctrine.std.coordination.outputs.PortableTruthHandoffFull

    workflow: "Metadata Polish"
        "Work in exactly one metadata mode."

        law:
            activation:
                active when CurrentHandoff.owes_metadata_polish

            mode_selection:
                mode pass_mode = CurrentHandoff.active_mode as MetadataPolishMode

            currentness:
                match pass_mode:
                    MetadataPolishMode.manifest_title:
                        current artifact PrimaryManifest via PortableTruthHandoffFull.current_artifact
                        must CurrentHandoff.preserve_basis == ApprovedPlan

                    MetadataPolishMode.section_summary:
                        current artifact SectionMetadata via PortableTruthHandoffFull.current_artifact
                        must CurrentHandoff.preserve_basis == ApprovedStructure

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

            evidence:
                support_only AcceptedPeerSet for comparison
                ignore {SectionMetadata.name, SectionMetadata.description}
                    for rewrite_evidence
                    when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite

            invalidation:
                invalidate SectionReview via PortableTruthHandoffFull.invalidations
                    when CurrentHandoff.structure_changed

            stop_lines:
                when unclear(pass_mode, CurrentHandoff.preserve_basis):
                    stop "Mode or preserve basis is unclear."
                    route "Route the same issue back to RoutingOwner." -> RoutingOwner
```

This shows exactly how Phase 3 should let a private pack stay private: the nouns, files, and lane logic remain pack-local, while the portable-truth discipline is imported.

---

## 17. Conformance checklist

`CONFORMANCE.md` should include this checklist.

A portable-truth workflow is conformant only if:

* it uses only frozen v1 surfaces
* it organizes reusable `law` with named subsections
* each active leaf branch resolves to exactly one current subject or `current none`
* every transferable currentness claim names a declared carrier
* every carrier field is declared on an emitted output and listed in `trust_surface`
* `standalone_read` does not overpromise beyond `trust_surface`
* invalidations, when used, are emitted on a trusted carrier
* any inherited workflow accounts for inherited law subsections exactly once
* examples remain narrow and prove one new idea at a time
* checked-in refs are treated as output artifacts, but the manifest remains the real proof surface.

And I would add two Phase 3-specific quality checks:

* if the current artifact is an output root, the concrete agent should emit it
* if a portable-truth example uses a superset output universe for mode-exclusive branches, the README must say so explicitly

---

## 18. Promotion rules

Finally, Phase 3 should include the rule for what gets extracted upward into Layer 2 next.

A new portable-truth convention should move into Layer 2 only when:

* it appears in at least two independent places
* it can be named generically
* it has either compiler-owned consequences or obvious stable prose value
* it does not rely on deferred features
* it reduces real drift rather than just making the syntax look prettier.

That is the right way to keep `doctrine.std` from turning into a disguised private framework.

---

## Bottom line

If I reduce this to the core:

**Phase 3 should be a normative README/conformance layer for `doctrine.std.portable_truth`.**
It should not add syntax.
It should not reopen deferred features.
It should standardize:

* the portable-truth theorem
* the named `law` subsection layout
* the trust-surface field vocabulary
* the render contract
* the output-carrier invariants
* the route-only convention
* the temporary mode-exclusive output-universe convention
* public/private pack composition patterns
* the conformance and promotion rules.

That is the version I would actually implement and write down before moving on to a public Layer 3 pack like code review.
