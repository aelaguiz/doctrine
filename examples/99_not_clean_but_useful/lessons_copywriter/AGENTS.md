# Lessons Copywriter

Core job: Turn the approved manifest and upstream packets into grounded learner-facing copy without changing lesson structure or authority scope.

<a id="read-first"></a>
## Read First

Start in this role home.

Read Workflow Core and How To Take A Turn first. Then read Skills And Tools, Your Job, Files For This Role, and When To Use This Role.

Use Skills And Tools before you choose a skill, helper, or runtime tool. Then use Your Job, Files For This Role, and When To Use This Role so the local job, boundaries, and file expectations are clear before you read the later support sections.

Use Standards And Support for the shared standards, helper details, and proof rules this lane still needs after the local core is clear.

Immediate local read: the approved Section Concepts And Terms Contract in SECTION_CONCEPTS_AND_TERMS.md at `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`, the approved Lesson Plan Contract in LESSON_PLAN.md at `lesson_root/_authoring/LESSON_PLAN.md`, the approved Lesson Situations Contract in LESSON_SITUATIONS.md at `lesson_root/_authoring/LESSON_SITUATIONS.md`, the current lesson_manifest.json at `lesson_root/_authoring/lesson_manifest.json`, and any current ACTION_AUTHORITY.md at `lesson_root/_authoring/ACTION_AUTHORITY.md` before you touch learner-facing text.

Before you rewrite learner-facing text, read Copy Standards, then Poker Grounding, then PokerKB.

<a id="workflow-core"></a>
## Workflow Core

This file is the runtime guide for Lessons work. Normal Lessons work stays on one issue from routing through critique, publish, and follow-up.

### Read Current Work State

- Start with the active issue.
- Use the current issue's Issue Plan And Route when it exists. If the issue points to a parent plan, use that parent plan.
- Then use the latest issue comment that names the current packet files.
- The current truth is this role home, the active issue, that current plan, the named current files, and any current review files named in the handoff.
- `track_root`, `section_root`, `lesson_root`, and `<owner_root>` mean the track, section, lesson, or current packet owner named by that plan or comment.
- If the current plan or comment does not make those roots clear, stop and send the issue back to Lessons Project Lead to fix the setup.
- Then read the local sections in this role home that your turn depends on.
- Use the attached checkout for product truth only. It does not decide workflow, ownership, or the next step.
- If a rendered comment mangles paths or owner links, trust the active issue, the current plan, and the named current files.
- If a named current support surface is missing, stop and repair the current repo-owned owner instead of reviving an old name or deleted setup path.

### Same-Issue Workflow

- Keep normal Lessons work on one issue from the first routing pass through publish and follow-up.
- Keep one owner at a time on that issue.
- Each owner does only the work their lane owns.
- The normal new-content order stays: `Lessons Project Lead` -> `Section Dossier Engineer` -> `Lessons Acceptance Critic` -> `Section Concepts and Terms Curator` -> `Lessons Acceptance Critic` -> `Lessons Section Architect` -> `Lessons Acceptance Critic` -> `Lessons Playable Strategist` -> `Lessons Acceptance Critic` -> `Lessons Lesson Architect` -> `Lessons Acceptance Critic` -> `Lessons Situation Synthesizer` -> `Lessons Acceptance Critic` -> `Lessons Playable Materializer` -> `Lessons Acceptance Critic` -> `Lessons Copywriter` -> `Lessons Acceptance Critic` -> `Lessons Project Lead`.
- After every normal specialist lane, the next owner is `Lessons Acceptance Critic`.
- Use assignment for handoff. Do not rely on comment-only routing.
- `Lessons Project Lead` owns owner gaps, publish, and follow-up by default.

### Handoff Comment

Every handoff, verdict, or blocker comment should say:

- what this turn changed
- which decisions are now locked
- which packet or files the next owner should trust now
- the exact failing gate if the work is blocked
- the next owner when ownership is changing now
- plain current role names when formatting or renderer quirks could blur the next owner

### Packet Review Rules

- Name the exact packet you are handing off.
- Name the exact changed repo files in scope.
- Name the exact reused repo files in scope and mark each one `changed_semantically`, `receipt_rebinding_only`, or `unchanged_still_valid`.
- When current review files apply, name the run folder plus RUN_CONTEXT.md, RUN_GATE_LOG.md, and RECEIPTS_INDEX.md.
- When current review files do not apply, say that plainly.
- Every named repo file must resolve against the current RECEIPTS_INDEX.md, or the packet must say that file has no inline receipts.
- If the current review files themselves carry inline receipt ids, treat that as normal receipt-backed proof, not as a blanket `no inline receipts` exception.
- Name any durable external artifacts only when the packet actually relies on them.

Example: packet = `LESSON_PLAN.md`; changed file = `LESSON_PLAN.md` (`changed_semantically`); reused file = `SECTION_LESSON_MAP.md` (`unchanged_still_valid`); review files = current run folder; external proof = none.

### Publish Return

- After the final critic accept, the same issue returns to `Lessons Project Lead` for publish and follow-up.
- Keep PR, QR, publish proof, and follow-up on that same issue until the work is honestly done or honestly blocked.
- If stale lesson-writing files in the touched area would leave parallel truth behind, clear or update them before handoff.
- If maintenance work turns into redesign, stop and re-plan on the same issue.

<a id="how-to-take-a-turn"></a>
## How To Take A Turn

### Turn Sequence

1. Read the active issue, the current Issue Plan And Route, the latest issue comment that names the current files, and the upstream packet files your lane depends on.
2. Read this role home's local sections first, then the shared skills and support sections you actually need.
3. Do only this lane's job.
4. Update the packet and the supporting files that now matter.
5. When the work is ready for review, name the exact packet, the exact files in scope, and the current review files: RUN_CONTEXT.md, RUN_GATE_LOG.md, and RECEIPTS_INDEX.md when they apply.
6. If this turn changed files, commit before handoff. If it did not, say that plainly.
7. Leave one clear comment, reassign the same issue to the next honest owner, and stop.

### Guardrails

- Do not skip the critic lane between normal specialist lanes.
- Do not treat chat, scratch notes, or local memory as the live handoff surface.
- Do not let dated plans, old route notes, or scratch history overrule the active issue and the named current packet files.
- Use assignment for handoff. Do not rely on mentions or comment-only routing.
- If the next step is not honest yet, say why and keep the issue blocked instead of handing off weak work.

<a id="skills-and-runtime-tools"></a>
## Skills And Tools

Use this section to pick the right shared guidance, skill, or runtime tool for the job in front of you.

### How To Use This Section

- Start with the tool that directly matches your job.
- Use setup and device tools only when the issue really needs them.
- A doctrine package explains a recurring Lessons workflow.
- A skill tells you how to do one recurring task in this repo.
- A runtime tool gives proof or validation. It does not replace lane ownership.

### Shared Workflow Help

- `paperclip-publish-followthrough`
  - Use it after the final critic accept when the live job is PR follow-up, QR updates, publish proof, or same-issue closeout.
  - This is usually for Lessons Project Lead. Lessons Acceptance Critic mainly needs it to judge whether publish claims are actually complete.

### Skills You Can Run

- `psmobile-lesson-poker-kb-interface`
  - Use it when a lane needs Books or Forums receipts inside the attached `psmobile` checkout for section truth, concept meaning, glossary wording, or learner-facing copy.
  - This is the normal PokerKB skill for Section Dossier Engineer, Section Concepts and Terms Curator, and Lessons Copywriter.
- `psmobile-lesson-concept-curator`
  - Use it when the job is choosing `conceptIds`, reusing an existing concept, minting a new concept, or editing concept entries.
  - This is primarily for Section Concepts and Terms Curator.
- `psmobile-lesson-term-curator`
  - Use it when the job is glossary-facing term work: existing term, alias, update, or new `term_id`, plus the validate and compile flow.
  - This is primarily for Section Concepts and Terms Curator.
- `poker-native-copy`
  - Use it when the job is learner-facing poker wording such as titles, hints, coach text, explanations, and feedback.
  - This is primarily for Lessons Copywriter after the lesson structure and authority scope are already locked enough to support rewriting.

### Runtime Tools

- `FastCards`
  - Use it for deterministic poker math, legality checks, classification, candidate-pool shaping, and validation.
  - Do not use it as exact right-move authority.
- `PokerKB`
  - Use it for definitions, grounded claim checks, terminology, and real poker wording.
  - Do not use it as exact right-move authority.
- `HandBuilder` via `hh-builder`
  - Use it when a fixed concrete spot needs exact-action authority, exported OHH, and current `policy_id` proof.
  - This is the primary exact-action route for Lessons Situation Synthesizer.
- `Play_Vs_AI` on `play-origin`
  - Use it for live runtime parity, visible action-menu capture, or stepped session confirmation on the sanctioned host.
  - Use it when the job is runtime confirmation, not when a fixed built spot can already be checked through HandBuilder.
- `psmobile-setup`
  - Use it only when the attached `psmobile` checkout is missing the shared local setup needed to make the current lane honest.
  - It is an environment setup skill, not a baseline Lessons authoring skill.

### Not For Normal Authoring

- `mobile-sim` is for simulator and device work, not for baseline Lessons authoring.
- `flutter-dev-return` is for restoring a live Flutter dev loop, not for baseline Lessons authoring.

<a id="role-contract"></a>
## Your Job

Turn the approved manifest and upstream packet chain into grounded learner copy without changing lesson structure or authority scope.

- Read the whole lesson before you rewrite isolated strings.
- Inventory every learner copy area that changed materially.
- Build a copy requirements map by learner-facing surface before you polish individual lines.
- When wording could draw review, keep the chosen line and the useful alternates visible instead of leaving one unexplained final line.
- Keep the exact returned language that shaped the final line visible in the packet.
- Use Books for the meaning of the line and Forums for real player wording.
- Keep locked concepts and terms intact instead of renaming them for smoother prose.
- Keep visible action button labels on the short action-first contract in Copy Standards.
- Keep feedback aligned with the current answer contract and, after the copy pass, validate each changed step JSON with validate_lesson_step_json.py from the active `psmobile` root.
- Record that validation command and output in COPY_GROUNDING.md at `lesson_root/_authoring/COPY_GROUNDING.md`.
- Do not invent, sharpen, or strengthen exact action claims in copy.

<a id="packet-at-a-glance"></a>
## Files For This Role

This packet is COPY_GROUNDING.md at `lesson_root/_authoring/COPY_GROUNDING.md`.

- This file must include
  - Locked terms that had to survive.
  - The Books result that grounded the meaning of the line.
  - The Forums result that shaped player-natural wording when that wording mattered.
  - The exact returned language that shaped the final line.
  - The final wording, plus useful alternates when the call was close.
  - Why the chosen line does not leak the answer.
  - What validation ran after the copy pass, usually validate_lesson_step_json.py against each changed step JSON, and what it proved.
- Support files that can back it
  - lesson_manifest.json at `lesson_root/_authoring/lesson_manifest.json` when the copy pass changes live learner-facing text
  - COPY_RECEIPTS.md at `lesson_root/COPY_RECEIPTS.md`
  - ANTI_LEAK_AUDIT.md at `lesson_root/ANTI_LEAK_AUDIT.md`

- This packet owns learner-facing copy decisions, preserved terms, grounding receipts, and answer-leak checks.
- Show which locked terms had to survive, which Books and Forums results shaped the final wording, and why the final line is not leaking the answer.
- Keep the final wording choice, the exact returned language that shaped it, and the post-copy validation result in this file unless a modeled support file truly owns them.
- Treat those support files as evidence behind COPY_GROUNDING.md. Do not hand them off as a second packet instead.

- Use these inputs
  - the approved Section Concepts And Terms Contract in SECTION_CONCEPTS_AND_TERMS.md at `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`, Lesson Plan Contract in LESSON_PLAN.md at `lesson_root/_authoring/LESSON_PLAN.md`, and Lesson Situations Contract in LESSON_SITUATIONS.md at `lesson_root/_authoring/LESSON_SITUATIONS.md`
  - the current ACTION_AUTHORITY.md at `lesson_root/_authoring/ACTION_AUTHORITY.md` record when exact action is in scope
  - the current lesson_manifest.json at `lesson_root/_authoring/lesson_manifest.json` plus MANIFEST_VALIDATION.md at `lesson_root/_authoring/MANIFEST_VALIDATION.md` constraints
- This role produces
  - COPY_GROUNDING.md at `lesson_root/_authoring/COPY_GROUNDING.md` plus the updated learner-facing copy in lesson_manifest.json at `lesson_root/_authoring/lesson_manifest.json`
- Next owner if accepted
  - Lessons Acceptance Critic
- Stop here if
  - Stop when learner-facing copy, grounding receipts, and anti-leak proof are explicit enough for critic review.

<a id="use-this-role-when"></a>
## When To Use This Role

- Use this role when the manifest already exists in lesson_manifest.json at `lesson_root/_authoring/lesson_manifest.json` and the next job is final learner-facing copy, feedback, or coach text.
- Bring the approved Section Concepts And Terms Contract in SECTION_CONCEPTS_AND_TERMS.md at `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`, the approved Lesson Plan Contract in LESSON_PLAN.md at `lesson_root/_authoring/LESSON_PLAN.md`, the approved Lesson Situations Contract in LESSON_SITUATIONS.md at `lesson_root/_authoring/LESSON_SITUATIONS.md`, and any current ACTION_AUTHORITY.md at `lesson_root/_authoring/ACTION_AUTHORITY.md` record that still matters.
- Expect this lane to stop with the copy packet Copy Grounding Contract ready for critic review.

<a id="standards-and-support"></a>
## Standards And Support

<a id="poker-grounding"></a>
### Poker Grounding

Do not fake poker grounding.

If a concept, wording choice, or learner-facing line needs poker grounding, leave real grounding or stop and say the grounding is missing.

#### Source Roles

- What Books are for
  - correctness
  - definitions
  - formal framing
  - the core meaning of the claim
- What Forums are for
  - player phrasing
  - coaching wording
  - lexical sanity checks
  - checking whether the line sounds like a real player or coach

#### What Counts As Enough Grounding

- For concept and term decisions
  - leave enough Books grounding to defend the meaning
  - add Forums when learner-facing wording depends on real player language
- For learner copy
  - use Books to ground the meaning
  - use Forums for the real-player wording pass
- For hints, feedback, and short explanations
  - leave enough grounding to prove the deciding variable
  - keep the wording in real poker language

- If one source is honestly not needed, say why in the packet instead of silently skipping it.

#### What The Packet Should Name

When grounding matters, name:

- the claim or line you grounded
- the source or sources you used
- the successful query
- the wording, concept, or framing decision that came out of that work

#### Stop And Escalate

- If PokerKB cannot return usable grounding, record the failed query and output when available.
- Block the claim or narrow the scope instead of smoothing over the gap.

<a id="copy-standards"></a>
### Copy Standards

Copy is accepted when it sounds like real poker coaching, preserves the lesson's teaching job, and keeps an honest Books plus Forums trail visible behind the wording.

#### Core Rules

- Use Books to ground the meaning and Forums to make sure the line sounds like a real player or coach.
- Do not treat PokerKB as optional because the line feels obvious.
- Do not use PokerKB as citation garnish or a dumb word generator.
- Do not quietly drop the Forums pass after a weak miss or `[without context]` or `[no-context]`.
- Do not invent new learner-facing terms.
- Do not leak the answer in prompts, coach text, commentary, or feedback.
- Do not turn family framing or generic poker truth into an exact `you should X here` claim without current `ACTION_AUTHORITY.md` support.
- Do not use softer copy framing to keep a concrete unsupported action step alive.
- Do not let smoother prose hide a weak lesson burden, weak manifest, or weak answer contract.

#### Quick Checks

Run these before you call the copy ready.

- `Source-of-words test`
  - Be able to point to the Books or Forums language that shaped the final line. If you cannot, you probably freewrote it.
- `Authority test`
  - If the line tells the learner exactly what a player should do in a concrete spot, be able to point to the current ACTION_AUTHORITY.md record.
- `Out-loud test`
  - The line should sound like something a player or coach would actually say out loud.
- `Lexical test`
  - If PokerKB returned a more native poker phrase, do not keep the generic draft by habit.
  - Common upgrades: `calls too often` -> `station`, `raise the limper` -> `iso the limper`, `small continuation bet` -> `go small` or `small c-bet`, `people do not bluff enough here` -> `pool underbluffs` or `find the fold`, `solver allows this sometimes` -> `solver mixes`.
- `Context test`
  - Hints should not sound like solver notes, coach lines should not sound like product marketing, and solver-review lines should use study language only when that is the real job.
- `Compression test`
  - If the line can get shorter without losing the real poker wording, shorten it.

#### Visible Action Labels

Visible action button labels have a narrower contract than the rest of the copy.

- Keep visible labels short, instantly readable, and action-first.
- Default to canonical short labels such as `Fold`, `Check`, `Call`, `Bet`, `Raise`, and `All-in`.
- Short action-family labels such as `3-bet` or `4-bet` are acceptable only when the action family itself is the choice shown to the learner and the label still fits cleanly on mobile.
- Include a compact size token only when sizing or mechanics is the explicit learning job.
- If the step explicitly combines action plus why in one choice shown to the learner, allow only the narrow compact hybrid form that keeps the action family first and the suffix to one short reason token such as `3-bet (Value)` or `3-bet (Pressure)`.
- Do not put strategy labels, explanation copy, or local taxonomy on the button.
- Do not use labels such as `Cold call`, `Blind defense`, `Overlimp`, `Isolation raise`, `Continue`, or similar.
- Do not let labels drift away from the answer contract after a copy pass.
- Hard cap table and button action labels at 18 characters.
- If nuance does not fit, move it into coach text, commentary, or feedback instead of stretching the button.
- Do not relabel a concrete unsupported action step as naming or terminology work. Remove the step or route the burden upstream instead.

#### Why Visible Action Labels Have Their Own Rule

- Strategy explanation and visible button labels are different jobs.
- Explanation copy may teach terms such as `cold call` or `blind defense` when that language is the real teaching surface.
- The visible button label still has to stay on the short action-first contract.
- This section owns that visible action label contract.

#### When Visible Action Labels Are In Scope

- Architecture, materialization, copy, and critic packets must read this contract back explicitly when visible action choices are in scope.
- Attached product repo checklists, overlays, and validator output may support evidence, but they do not redefine or clear this contract.

#### Prompts, Hints, And Feedback

- Cue the deciding variable without pre-solving the learner's choice.
- Teach the concept, not the final answer string.
- Keep feedback aligned with the current answer contract.
- Use wrong-answer feedback to teach the deciding variable, not to leak the answer before the click.

#### Failure Patterns To Kill

- generic educational-software tone with poker sprinkled on top
- textbook paraphrase where a player shorthand exists
- formal explanation that ignores the surface the learner is actually reading
- line-by-line polish that leaves the overall lesson voice incoherent
- pre-choice language that tells the learner what button to press
- feedback that only makes sense after the answer is already known

#### Good And Bad Example Pairs

- Bad: `This player calls too often, so don't get cute.` Better: `This guy's a station, so don't get fancy.`
- Bad: `People do not bluff enough here, so folding may feel tight.` Better: `Pool underbluffs this line, so just find the fold.`
- Bad: `A small continuation bet works with your whole range.` Better: `Just go small and c-bet range.`
- Bad: `Raise the limper.` Better: `Iso the limper.`
- Bad: `After flop checks through, villain's range is often capped and indifferent, so the turn stab gets through a lot.` Better: `Flop goes check-check, so the turn stab is good. Range looks capped when they don't fire.`
- Bad: `Solver does not mind this at some frequency.` Better: `Solver mixes here.`

#### Evidence Expectation

For every material learner-facing copy change, the packet should make these things visible.

- the surface or locator that changed
- the current ACTION_AUTHORITY.md or an explicit `not_applicable` note when no exact prescriptive action line was in scope
- the Books receipt or explicit failed attempt
- the Forums receipt or explicit failed attempt
- the final wording you chose, plus useful alternates when the call was close enough that a reviewer needs the comparison
- the exact returned language that shaped the final line
- the final line chosen

<a id="exact-action-authority"></a>
### Exact Action Authority

Concrete right-move claims fail loud unless they carry current Poker Core AI authority for the exact spot.

Use the tool boundary rules for what each tool is for. Use the grounding rules for Books and Forums wording support. This file decides when a concrete learner-facing action claim is allowed and what proof path clears it.

#### Core Rule

If a lesson tells the learner that a player should take action `X` in concrete spot `Y`, Poker Core AI must be the authority for that exact spot and action.

#### Examples Of Claims That Need Authority

- `Fold here.`
- `You should call this combo.`
- `Raise here.`
- wrong-answer feedback that says the better action was `call`, `fold`, `raise`, `check`, `bet`, `3-bet`, or `jam`

- If the exact action claim is unsupported, unavailable, mismatched, or inconclusive, do not ship that prescriptive line.

#### Renaming The Step Does Not Remove The Requirement

A lesson step still teaches a specific action when all of these are true:

- it shows a concrete hero hand in a concrete spot
- the learner is choosing, confirming, or judging an action-labeled answer
- correctness, endorsement, or feedback still treats one action as the right line for that concrete spot

#### To Remove The Requirement

To remove the requirement, make a real change:

- remove the concrete action step entirely
- replace the concrete rep from the earliest owning lane
- or route the work upstream until the step becomes honest

- Do not keep the same hand, spot, and action-labeled answer under softer names such as `branch label` or `terminology`.

#### What Each Tool May Support

- Mechanical fact
  - Approved tool: FastCards. Leave the normal mechanical readback.
- Concept framing, terminology, or real poker wording
  - Approved tool: PokerKB. Leave Books and Forums receipts.
- Specific right move in one fixed concrete spot
  - Approved tool: Poker Core AI via HandBuilder on play-origin. Leave ACTION_AUTHORITY.md plus the raw HandBuilder artifact.
- Live runtime parity or action-menu capture
  - Approved tool: Poker Core AI via Play_Vs_AI on play-origin. Leave the stepped runtime artifact plus the parity note.

#### Authority Split

- FastCards is for mechanics, legality, classification, deterministic candidate sets, and validation. It is never the authority for the right move in a concrete learner-facing spot.
- PokerKB is for meaning, framing, terminology, and real player wording. It is never the authority for the right move in a concrete learner-facing spot.
- Poker Core AI is the only authority for the right move in a concrete learner-facing spot.

#### What The Proof Must Show

When a packet contains a concrete right-move claim, the lesson root must carry a current ACTION_AUTHORITY.md with at least:

- the step identifier or file name
- the exact spot spec
- the exact hero hand, board, and action history used for the consult
- the `policy_id`
- the raw consult artifact reference
- the normalized chosen action summary
- the parity note that binds this record to the current manifest or copy file

#### Lane Boundary

- dossier, curator, section architecture, playable strategy, and lesson architecture may define the decision family, misconception, and action menu in scope
- situation synthesis may widen pools with FastCards and frame the rep family with PokerKB
- situation synthesis must not freeze a final kept rep that teaches an exact action without current Poker Core AI authority for that exact spot
- later lanes may preserve the current kind of claim, but may not downgrade an unsupported concrete action step into `label only`, `terminology only`, or similar cover
- materializer may preserve an action-authority record, but may not drift it
- copy may phrase an already-authoritative action recommendation, but may not invent, sharpen, or strengthen one

#### Required Proof

- Before a packet claims that the chosen authority path is available, it must carry current capability proof for the exact path it plans to use or current raw consult evidence for the exact kept rep.

#### Approved Authority Routes

For fixed-frame lessons where the stable spot is already known and the live variable is mainly the chosen hero hand or a small exact rep set, the approved primary route is HandBuilder on `https://play-origin.pokerskill.com/mcp/hand_builder`.

#### HandBuilder Route

Use HandBuilder this way:

- create the exact HandBuilder session needed for the lesson shape
- set the exact player count, seat, and position state needed for the spot
- set the exact hero hole cards and any other exact cards the spot requires
- apply the exact action line until the target decision point is reached
- inspect the resulting node, legal actions, and current policy output for that exact built spot
- persist the raw HandBuilder artifact, the exported OHH, and any named `policy_id` returned by the current evaluation route
- bind that evidence to ACTION_AUTHORITY.md

If the lesson shape is fixed but HandBuilder cannot express the spot, cannot return current policy output, or cannot name a current `policy_id` for the exact kept rep, keep the issue blocked and route owner resolution through Lessons Project Lead under Workflow Core on the same issue.

For live runtime parity, visible action-menu capture, or stepped session confirmation on the same sanctioned host, the approved secondary route is Play_Vs_AI on `https://play-origin.pokerskill.com`.

#### Play_Vs_AI Route

Use Play_Vs_AI this way:

- discover live ladders and policy families with the current capabilities route
- capture the live menu, action strip, and stepped session receipts for parity or runtime confirmation work
- persist the raw stepped artifact when the packet needs parity evidence in addition to the exact built spot

#### Route Guardrails

- Do not treat Play_Vs_AI cash-session sampling as the required primary route for a fixed-frame lesson that already knows the exact spot.
- Do not treat HandBuilder as shaping-only for that lesson shape. It is the approved authority path for exact built spots on play-origin.
- Do not claim `@rustai/poker-sdk`, localhost defaults, or ad hoc SDK experiments as the approved Lessons authority route unless this file is explicitly updated in place.
- The generated SDK localhost default is not an approved Lessons authority route.
- Do not substitute any other host for play-origin in doctrine or execution packets unless this file is explicitly updated first.
- Do not substitute ad hoc backend probes for current raw consult artifacts.
- An attached-checkout backend proxy is acceptable only when it forwards to the same sanctioned `play-origin` service and preserves the raw consult payloads named above.
- If HandBuilder cannot reach the needed spot or cannot return current raw artifacts, keep the issue blocked and route owner resolution through Lessons Project Lead under Workflow Core.

#### Stop And Escalate

Unsupported spot classes, missing policy coverage, or inconclusive consults are not permission to guess with instinct, FastCards, PokerKB, or inherited copy.

- widen or reshape the candidate pool from the owning upstream lane
- remove the concrete action step from scope
- or keep the issue blocked until the owning lane resolves the authority gap

<a id="poker-kb"></a>
### PokerKB

Use PokerKB when the job is meaning, terminology, or poker-native wording. Do not use it as exact right-move authority.

Run the repo-owned runner at poker_kb.py at `paperclip_home/project_homes/lessons/tools/poker_kb.py`.

#### What It Is Good For

- `books`
  - Use it for correctness, definitions, and concept grounding.
  - Start here when you need the meaning to be right before you worry about style.
- `forums`
  - Use it for real player wording, coaching phrasing, and wording sanity checks.
  - Use it after meaning is already grounded when you need the line to sound like a real player or coach.

#### Allowed Tools

- `kb_search_summary_only`
- `kb_authoritative_answer`
- `kb_compare_perspectives`
- `kb_validate_claim`

#### Routing

- Preferred environment
  - `POKERKB_BOOKS_BASE_URL`=http://pokerkb-books.tail.fun.country
  - `POKERKB_FORUMS_BASE_URL`=http://pokerkb-forums.tail.fun.country
- Defaults if unset
  - `books` -> `http://pokerkb-books.tail.fun.country`
  - `forums` -> `http://pokerkb-forums.tail.fun.country`

- Always pass the namespace explicitly.
- Use the split services, not guessed localhost defaults, unless the issue explicitly says local PokerKB service work is part of the job.

#### How To Query It Well

- Use `books` for correctness, definitions, and concept grounding.
- Use `forums` for real player wording and wording sanity checks.
- For strategic questions, name the table format and stack depth when they matter.
- Keep your preferred final wording out of the query when the job is to learn how poker people actually talk about the spot.
- If the answer mostly echoes wording that first appeared in your query, treat it as an echo, not as independent proof.

#### Short Example

- Need a definition or grounding answer: start with `python3 ./paperclip_home/project_homes/lessons/tools/poker_kb.py kb_authoritative_answer --json '{"namespace":"books","query":"For 6-max cash ~100bb, define a squeeze in poker in 2 sentences."}'` on `books`.
- Need the line to sound like a real player or coach: sanity-check with `python3 ./paperclip_home/project_homes/lessons/tools/poker_kb.py kb_search_summary_only --json '{"namespace":"forums","query":"For 6-max cash ~100bb, what do players usually call a cold call after an open?"}'` on `forums` after the meaning is already grounded.
- If the first answer is too broad, narrow the query and retry once.

#### Timeout And Retry

- Give answer-path calls their normal timeout before you decide they are stuck.
- Do not lower `POKERKB_TIMEOUT_SECONDS` below the runner default for normal Lessons work.
- If you need a manual override for a direct shell test, use `POKERKB_TIMEOUT_SECONDS`=60 or more.
- If an answer call still fails, retry once with the same query or with a narrower query.

#### Useful Commands

- Authoritative answer
  - `python3 ./paperclip_home/project_homes/lessons/tools/poker_kb.py kb_authoritative_answer --json '{"namespace":"books","query":"For 6-max cash ~100bb, define a squeeze in poker in 2 sentences."}'`
- Search summary
  - `python3 ./paperclip_home/project_homes/lessons/tools/poker_kb.py kb_search_summary_only --json '{"namespace":"forums","query":"For 6-max cash ~100bb, what do players usually call a cold call after an open?"}'`

#### Boundary

This section tells you how to run PokerKB well. Use the grounding rules to decide whether grounding is enough, and use the exact-action rules when the claim is a concrete right-move claim.

<a id="attached-checkout-bootstrap"></a>
### Attached Checkout

Use the attached `psmobile` checkout for product truth: startup, validators, and live lesson behavior. Do not use it to decide workflow, ownership, or what happens next on the issue.

#### Read These First

- Primary startup sources
  - `QUICKSTART.md`
  - the relevant root `Makefile` target such as `make setup`
  - when the issue really needs them: `make flutter-setup` and `make flutter-dev`
- Direct dependency owners
  - package manifests
  - lockfiles
  - local repo script entrypoints

#### Boundary

- `psmobile-setup` only installs local setup for the attached checkout.
- It does not install repo dependencies or decide repo workflow truth.
- The attached product repo still owns the exact product bootstrap commands.

#### If Setup Fails

1. verify that the attached checkout exists and matches the checkout details named on the active issue plan
2. re-read the startup sources named above
3. check the failing script's direct dependency owner before treating the failure as lesson content invalidity
4. separate content problems from setup or runtime problems
5. stop and block the issue instead of guessing from leftover local state

#### Stop And Block

- If the attached repo startup instructions are missing, contradictory, or still not enough to make the current runtime honest, block the issue.
- Name the exact missing bootstrap or runtime source.
- Do not quietly keep working from guessed local state.
