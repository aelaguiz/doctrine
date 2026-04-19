# Finding Catalog

Use only these core Doctrine codes.
Choose the smallest correct code by recognition test, not by keyword match.
Use this file to calibrate what strong findings look like.

| Code | Title | Recognition test | Default recommendation |
| --- | --- | --- | --- |
| `AL100` | Oversized Always-On Context | The role home carries too much always-on text, or new local bulk does not buy clearer loading, stronger reuse, or exact truth. | Move deep reference material into a shared skill, module, or docs index. |
| `AL110` | Pasted Reference Instead Of Pointer | Long reference text is pasted where a shared pointer should exist. | Replace the pasted block with a pointer to one shared source. |
| `AL120` | Deep Procedure In The Role Home | A reusable method is taught inline instead of through a shared skill. | Move the reusable method into a skill. |
| `AL130` | Dead Inherited Section | Inherited text is present but not used. | Drop the inherit or move the pointer to the step that needs it. |
| `AL200` | Duplicate Rule Across Agents | The same rule or step list appears in several agents. A fixed vocabulary written as a pipe list (for example `A \| B \| C`) and repeated on several roles or on the critic gate is a canonical shape. | Lift the repeated rule into one shared skill or module. For a pipe-list vocabulary, declare an `enum` and type the field with it. |
| `AL210` | Repeated Method Should Become A Skill | Several agents carry the same decision method without a shared skill owner. | Extract the shared method into a skill. |
| `AL220` | Repeated Background Block Across Agents | Several agent homes carry the same background or glossary block. | Move the shared background into one importable module. |
| `AL230` | Semantic Duplicate Across Agents | Several targets say the same rule in different words. | Collapse the semantic copies behind one shared owner. |
| `AL240` | Skill Hardcodes Invocation Inputs | A skill hardcodes changing subject, dataset, or case facts. | Keep the method in the skill and move changing facts into inputs or source reads. |
| `AL300` | Runtime Boundary Leak | The prompt starts owning runtime state, safety control, memory, scheduling, or orchestration. | Remove runtime ownership from the prompt. |
| `AL310` | Shadow Control Plane | Prose creates a second source of truth that competes with a typed surface. | Delete the shadow surface and keep one canonical owner. |
| `AL320` | Host-Namespace Jargon Without Grounding | Prose uses harness-specific verbs, paths, or env vars without grounding. | Replace private jargon with neutral language or a shared grounded owner. |
| `AL400` | Exact Truth Hidden In Prose | Exact requirements are hidden in prose instead of a typed surface. | Move exact requirements into the declared contract. |
| `AL410` | Prose Drift From Declared Constraints | Prompt text conflicts with exact supplied constraints. | Align the prose with the declared constraint surface. |
| `AL420` | Prose Names Artifact Not In Declared Outputs | Prose promises an artifact the declared output contract does not carry. | Add the artifact to the contract or delete the promise. |
| `AL430` | Deterministic Work Forced Into Prose | Prose is asked to do exact counting, validation, routing, or assignment work. | Move exact work into a typed surface or deterministic helper. |
| `AL500` | Mixed Role Ownership | One role owns too many jobs. | Narrow the role to one clear job and one clear output. |
| `AL510` | Missing Handoff Artifact | The role does not say what concrete artifact or blocker it must leave behind. | Require a concrete artifact or concrete blocker note. |
| `AL520` | Source Should Be Read, Not Remembered | The prompt tells the agent to work from memory when a real source should be read. | Point to the real source and remove memory-based fallback language. |
| `AL530` | Role-Shift In Process Without Stop Line | One process silently changes responsibility mid-sequence. | Add an explicit stop line and handoff artifact before ownership shifts. |
| `AL540` | Prose Routing Without Declared Next Owner | Prose tells the agent to route work without naming a declared next owner or route. | Use the declared route surface or name the exact next owner. |
| `AL550` | Read-Many Work Leaves Raw Notes | Read-many work leaves raw notes instead of one compact synthesized handoff. | Require one compact synthesis artifact. |
| `AL600` | Weak Resolver Name | A name is too vague to help a resolver or an author know what it is for. | Rename it so the job and scope are clear. |
| `AL610` | Weak Description | A description does not explain purpose, trigger, or boundary. | Rewrite the description with purpose, trigger, and limit. |
| `AL700` | Reading Level Too High | The prose is harder to read than the active style target allows. | Split long sentences and replace abstract words with common words. |
| `AL710` | Vague Wording | The prose uses vague verbs or nouns that hide the real action. | Replace vague verbs with exact actions and name the artifact directly. |
| `AL720` | Missing Priority Or Stop Line | The prompt gives several goals but does not say which comes first or when to stop. | Order the work and add a clear stop rule. |
| `AL730` | Quality Bar Mixes Gates With Craft | A quality bar mixes must-pass gates with taste advice. | Split hard gates from craft advice. |
| `AL800` | Internal Contradiction | One surface gives incompatible instructions. | State the priority rule or split default behavior from exceptions. |
| `AL810` | Cross-Surface Contradiction | Two related surfaces disagree with each other. | Align local text with the shared source of truth. |
| `AL820` | Asymmetric When-To-Use Vs When-Not-To-Use | A skill or role defines overlapping or contradictory scope boundaries. | Rewrite the two scopes so they do not overlap. |
| `AL900` | Skill Too Broad | One skill mixes several unrelated jobs or reads like a handbook. | Split the skill by job and keep one repeatable method per skill. |
| `AL910` | Shared Law Trapped In Local Text | One local role carries a rule that should be shared by many roles. | Lift the shared law into a shared module or skill. |
| `AL920` | Compiler-Owned Semantics Restated In Prose | Prose restates verdicts, routing, or other semantics the compiler already owns. | Delete the prose copy and point at the declared surface. |
| `AL950` | Inlined Vocabulary Should Be An Enum-Typed Field | A fixed set of values is listed as prose (for example `A \| B \| C`) instead of a declared `enum` typed onto a field. | Declare `enum X: "..."` once, then write `type: X` on the field. |

## Full Calibration

### `AL100` Oversized Always-On Context

What it means: The role home carries too much always-on text, or local prompt growth added bulk without buying clearer loading, stronger reuse, or stronger exact truth.
Why it matters: Context is a budget. Extra local text should earn something durable.
Default fix: Move deep reference material behind a pointer.
Good: `Read the quoting guide only when a quote is weak.`
Bad: `Keep the full quoting guide, glossary, archive, and style handbook in mind on every turn.`

### `AL110` Pasted Reference Instead Of Pointer

What it means: Long reference text is pasted where one pointer would do.
Why it matters: The same text will drift when copied, and copied reference text is a common way to add bulk without creating reuse.
Default fix: Replace the pasted block with one shared pointer.
Good: `Use the shared SummaryRubric skill before you finalize work.`
Bad: `Here are the full 18 summary rules copied into this role home again.`

### `AL120` Deep Procedure In The Role Home

What it means: A reusable method is taught inline instead of through a skill.
Why it matters: The role home gets fat and the method cannot be reused cleanly. The added bulk did not buy reusable leverage.
Default fix: Move the method into a skill.
Good: `Use the InterviewSynthesis skill after you read the transcript.`
Bad: `Step 1 read, step 2 cluster, step 3 compare, step 4 score, step 5 write...`

### `AL130` Dead Inherited Section

What it means: Inherited text is present but not used.
Why it matters: Dead inherited text hides the real active path.
Default fix: Drop the inherit or point to the step that needs it.
Good: `Inherit only the shared EvidenceCheck block that this role still calls.`
Bad: `Inherit the full ReviewerWorkflow` with no remaining reference to it.

### `AL200` Duplicate Rule Across Agents

What it means: The same rule or step list appears in several agents. A fixed vocabulary written as a pipe list (for example `A | B | C`) and repeated on several roles, or repeated once on a role and again as a critic gate check, is a canonical shape of this finding.
Why it matters: One rule should have one owner. When the repeat is a value vocabulary, the two copies drift and the critic gate can silently fall behind the producer prose.
Default fix: Lift the repeated rule into one shared skill or module. For a pipe-list vocabulary, declare an `enum` and type the field with it. The rendered schema now owns the vocabulary and the critic stops restating it. See also: `AL950`.
Shared owner: Almost always required.
Good: `Use the shared ClaimEvidenceCheck skill before you finalize work.`
Bad: `Check each claim against a source quote. Mark weak quotes. Remove unsupported claims.` in three different roles.
Bad: `step_role values are introduce | practice | test | capstone` written once on the producer role and again as a critic gate.

### `AL210` Repeated Method Should Become A Skill

What it means: Several agents carry the same decision method with no skill owner.
Why it matters: A repeated method should have one reusable home.
Default fix: Extract the shared method into a skill.
Shared owner: Almost always required.
Good: `Use the FounderMatchMethod skill with the supplied founder set.`
Bad: Three agents each teach the same clustering and compare method inline.

### `AL220` Repeated Background Block Across Agents

What it means: Several agent homes carry the same background or glossary block.
Why it matters: Shared background should not be copied into every role.
Default fix: Move the block into one importable module.
Shared owner: Almost always required.
Good: `Read the shared InterviewGlossary module when a term is unclear.`
Bad: The same glossary paragraph is pasted into every interview role.

### `AL230` Semantic Duplicate Across Agents

What it means: Several targets say the same rule in different words.
Why it matters: Semantic copies still drift even when the wording changes.
Default fix: Collapse the copies behind one shared owner.
Shared owner: Almost always required.
Good: `Use the shared SafetyEscalation rule.`
Bad: One role says `raise blockers early` while another says `surface risks before handoff` for the same policy.

### `AL240` Skill Hardcodes Invocation Inputs

What it means: A skill hardcodes the changing subject, dataset, or case.
Why it matters: The skill stops acting like a reusable method call.
Default fix: Keep the method in the skill and move changing facts into inputs or source reads.
Good: `Read the supplied founder application and the supplied source set.`
Bad: `Read Maria Santos's application and Contrail's billing commits.`

### `AL300` Runtime Boundary Leak

What it means: The prompt starts owning runtime state, safety control, memory, scheduling, or orchestration.
Why it matters: The prompt now competes with the harness.
Default fix: Remove runtime ownership from the prompt.
Good: `If a source is missing, leave a blocker note.`
Bad: `Keep a safety strike count, auto-block future requests after three strikes, and rerun the cron in 30 minutes.`

### `AL310` Shadow Control Plane

What it means: Prose creates a second source of truth beside a typed surface.
Why it matters: The agent gets two competing control planes.
Default fix: Delete the shadow surface and keep one canonical owner.
Good: `Follow the declared route surface.`
Bad: `Ignore the declared route and send the work to ReviewerTwo if it feels right.`

### `AL320` Host-Namespace Jargon Without Grounding

What it means: The prose uses harness-specific verbs, paths, or env vars with no grounding.
Why it matters: The role only makes sense inside one private host setup.
Default fix: Replace private jargon with neutral language or a grounded owner.
Good: `Use the available file-reading tools to inspect the source.`
Bad: `Kick this through /tmp/agent_mux and write state to $BRAIN_SIDECHANNEL.`

### `AL400` Exact Truth Hidden In Prose

What it means: Exact requirements live in prose instead of a typed surface.
Why it matters: Exact truth in prose is hard to trust and hard to keep current.
Default fix: Move exact requirements into the declared contract.
Good: `The required fields live in the declared output contract.`
Bad: `The output must have exactly seven keys and this exact nesting...` only in prose.

### `AL410` Prose Drift From Declared Constraints

What it means: Prompt text conflicts with exact supplied constraints.
Why it matters: The prose teaches behavior the exact surface does not allow.
Default fix: Align the prose with the declared constraint surface.
Good: `Use ReadFile and SearchDocs when you need source material.`
Bad: `Use any browser or shell tool that seems useful.` when only two tools are allowed.

### `AL420` Prose Names Artifact Not In Declared Outputs

What it means: Prose promises an artifact the declared outputs do not carry.
Why it matters: The handoff promise is fake.
Default fix: Add the artifact to the contract or delete the promise.
Good: `Leave one compact founder brief.` and the output contract names that brief.
Bad: `Leave a risk register and a scorecard.` when neither output exists.

### `AL430` Deterministic Work Forced Into Prose

What it means: Prose is asked to do exact counting, routing, validation, or assignment work.
Why it matters: Deterministic work does not belong in latent judgment.
Default fix: Move exact work into a typed surface or deterministic helper.
Good: `Apply the seating rules from the typed seating surface.`
Bad: `Seat 600 founders into tables of exactly 8 with no repeats and exact sector balance.`

### `AL500` Mixed Role Ownership

What it means: One role owns too many jobs.
Why it matters: Mixed ownership makes stop lines and outputs fuzzy.
Default fix: Narrow the role to one clear job and one clear output.
Good: `Write the first summary draft.`
Bad: `Read, score, rewrite, approve, publish, and notify the team.`

### `AL510` Missing Handoff Artifact

What it means: The role does not say what concrete artifact or blocker it leaves behind.
Why it matters: The next owner cannot tell when the job is done.
Default fix: Require a concrete artifact or blocker note.
Good: `Leave one draft summary or one blocker note.`
Bad: `Finish the work and hand it off.`

### `AL520` Source Should Be Read, Not Remembered

What it means: The prompt tells the agent to work from memory when a real source should be read.
Why it matters: Memory is weaker than the source of truth.
Default fix: Point to the real source and remove the memory fallback.
Good: `Read the current pricing page before you summarize it.`
Bad: `Use what you remember about our pricing model.`

### `AL530` Role-Shift In Process Without Stop Line

What it means: One process silently changes responsibility mid-sequence.
Why it matters: Ownership shifts with no clean handoff.
Default fix: Add an explicit stop line and handoff artifact.
Good: `Stop after the draft. The reviewer owns final approval.`
Bad: `Draft the summary, then approve it, then publish it if it looks good.`

### `AL540` Prose Routing Without Declared Next Owner

What it means: Prose tells the agent to route work without naming a declared next owner or route.
Why it matters: The prompt invents routing outside the declared surface.
Default fix: Use the declared route surface or name the exact next owner.
Good: `Route to the declared Reviewer agent.`
Bad: `Send this to whoever should handle it next.`

### `AL550` Read-Many Work Leaves Raw Notes

What it means: Read-many work leaves raw notes instead of one compact handoff.
Why it matters: Raw notes slow the next reader and repeat work.
Default fix: Require one compact synthesis artifact.
Good: `Leave one founder brief with claim-vs-build gaps and timeline notes.`
Bad: `Leave a folder of copied quotes and browser notes.`

### `AL600` Weak Resolver Name

What it means: A name is too vague to help a resolver or author.
Why it matters: Weak names make the surface harder to load at the right time.
Default fix: Rename it so the job and scope are clear.
Good: `InterviewSummaryReviewer`
Bad: `Helper`

### `AL610` Weak Description

What it means: A description does not explain purpose, trigger, or boundary.
Why it matters: Resolvers and humans both get weak routing help.
Default fix: Rewrite the description with purpose, trigger, and limit.
Good: `Review one interview summary for evidence support and contradiction.`
Bad: `Does review stuff.`

### `AL700` Reading Level Too High

What it means: The prose is harder to read than the style target allows.
Why it matters: Dense wording slows tired readers and weakens execution.
Default fix: Split long sentences and use common words.
Good: `Read the transcript. Write one short summary.`
Bad: `Synthesize the interview's multidimensional thematic landscape into a concise artifact.`

### `AL710` Vague Wording

What it means: The prose uses vague verbs or nouns that hide the real action.
Why it matters: The agent does not know what concrete move to make.
Default fix: Replace vague words with exact actions and artifacts.
Good: `Leave one blocker note that names the missing quote.`
Bad: `Handle any issues as needed.`

### `AL720` Missing Priority Or Stop Line

What it means: The prompt gives several goals but does not say which comes first or when to stop.
Why it matters: The role can chase the wrong goal first.
Default fix: Order the work and add a clear stop rule.
Good: `Check evidence first. Then draft the summary. Stop after the draft.`
Bad: `Check evidence, improve tone, fix structure, and keep going until it feels done.`

### `AL730` Quality Bar Mixes Gates With Craft

What it means: A quality bar mixes must-pass gates with taste advice.
Why it matters: The reader cannot tell what is required versus preferred.
Default fix: Split hard gates from craft advice.
Good: `Must: every claim has support. Craft: keep the tone calm.`
Bad: `The summary must be accurate, elegant, warm, and compelling.`

### `AL800` Internal Contradiction

What it means: One surface gives incompatible instructions.
Why it matters: The agent cannot satisfy both.
Default fix: State the priority rule or split default behavior from exceptions.
Good: `Be concise by default. Go longer only when the user asks for depth.`
Bad: `Always keep the answer under five lines.` plus `Provide a full, exhaustive analysis.`

### `AL810` Cross-Surface Contradiction

What it means: Two related surfaces disagree.
Why it matters: The author and shipped surface now teach different behavior.
Default fix: Align local text with the shared source of truth.
Good: Authored and emitted tool guidance both say `Use ReadFile and SearchDocs.`
Bad: Authored text says `Use any browser or shell tool.` while the emitted skill says otherwise.

### `AL820` Asymmetric When-To-Use Vs When-Not-To-Use

What it means: A skill or role defines overlapping or contradictory scope boundaries.
Why it matters: The resolver cannot tell when the skill should load.
Default fix: Rewrite the two scopes so they do not overlap.
Good: `Use for auditing prompts. Not for rewriting prompts.`
Bad: `Use for any prompt work.` and `Do not use for prompt edits or prompt reviews.`

### `AL900` Skill Too Broad

What it means: One skill mixes several unrelated jobs or reads like a handbook.
Why it matters: Broad skills undertrigger, overtrigger, and teach too much at once.
Default fix: Split the skill by job.
Good: One skill audits prompt quality.
Bad: One skill audits prompts, rewrites prompts, ships packages, and runs releases.

### `AL910` Shared Law Trapped In Local Text

What it means: One local role carries a rule that should be shared by many roles.
Why it matters: Shared law in one local file will drift everywhere else, and one rule change will need several edits.
Default fix: Lift the shared law into a shared module or skill.
Shared owner: Almost always required.
Good: `Use the shared EvidenceSupportLaw module.`
Bad: One local role is the only place that says `Every claim needs a quote.`

### `AL920` Compiler-Owned Semantics Restated In Prose

What it means: Prose restates verdicts, routing, or other compiler-owned semantics.
Why it matters: The prose copy can drift from the real compiler owner.
Default fix: Delete the prose copy and point at the declared surface.
Good: `Follow the declared route surface.`
Bad: `If branch A happens, route to Reviewer; if branch B happens, stop with no owner.` copied into prose beside the real route surface.

### `AL950` Inlined Vocabulary Should Be An Enum-Typed Field

What it means: A fixed set of values is listed as prose instead of a declared `enum` typed onto a field. Common shapes are a pipe list (`A | B | C`) inside a role step, or a vocabulary repeated once on the producer role and again as a critic gate check.
Why it matters: The prose copy and the gate copy will drift. The rendered schema should own the vocabulary, not the role body.
Default fix: Declare `enum X: "..."` once with one member per value. Set the field's `type: X` on the schema, row_schema, item_schema, table column, or record scalar. Delete the prose and the duplicate gate line.
Good: `type: StepRole` on the `step_role` field, backed by `enum StepRole: "Step Role"` with members `introduce`, `practice`, `test`, `capstone`.
Bad: `step_role values are introduce | practice | test | capstone` written in the role body, plus `step_role_in_vocabulary` as a separate critic gate.
See also: `AL200` for the duplicate-rule framing, and `examples/139_enum_typed_field_bodies/` for the canonical form.

## Severity

- `high`: likely to mislead the agent or create conflicting truth
- `medium`: likely to create drift, bloat, or poor reuse
- `low`: likely to reduce clarity, but lower risk

## Confidence

- `high`: exact evidence and low ambiguity
- `medium`: strong evidence, but local intent might justify it
- `low`: weak signal and should stay hidden by default

## Hybrid Checks

These checks benefit most from exact side signals plus model judgment:

- `AL100`
- `AL130`
- `AL200`
- `AL220`
- `AL230`
- `AL240`
- `AL320`
- `AL400`
- `AL410`
- `AL420`
- `AL430`
- `AL540`
- `AL700`
- `AL920`
- `AL950`

Useful exact side signals:

- size stats
- duplicate hints
- inheritance graphs
- declared constraint sets
- declared route edges and next-owner names
- declared output fields
- host-namespace vocab lists that need grounding
- reading metrics
