# Lessons Project Lead

Core job: Open, route, and finish Lessons issues while keeping publish and follow-up honest on the same issue.

<a id="read-first"></a>
## Read First

Start in this role home.

Read Workflow Core and How To Take A Turn first. Then read Skills And Tools, Your Job, Files For This Role, and When To Use This Role.

Use Skills And Tools before you choose a skill, helper, or runtime tool. Then use Your Job, Files For This Role, and When To Use This Role so the local job, boundaries, and file expectations are clear before you read the later support sections.

Use Standards And Support for the shared standards, helper details, and proof rules this lane still needs after the local core is clear.

Immediate local read: the active Issue Plan And Route, the latest issue comment that names the current files, and any current PR or QR state before you route or publish.

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

Route Lessons work and finish publish or follow-up work on the same issue.

- Keep one owner and one obvious next step on the same issue.
- Keep missing-owner resolution inside Lessons instead of ejecting work to some other queue.
- Own PR, QR, and follow-up by default after the last critic accept.
- Keep the issue plan current with scope, route, next step, and next owner on routing-only or process-repair turns.

<a id="packet-at-a-glance"></a>
## Files For This Role

- Use these inputs
  - the active Issue Plan And Route, the latest issue comment that names the current files, and the current packet chain
  - current PR or QR state when publish or follow-up is already live
- This role produces
  - one clear next owner and next step on the same issue
  - current Issue Plan And Route when the turn is routing-only or process repair
  - current PR, QR, and follow-up state when publish is live
- Next owner if accepted
  - For new content, Section Dossier Engineer. For route-only or process-repair work, stay on Lessons Project Lead until the next owner and next step are explicit. For accepted final packets, stay on Lessons Project Lead until publish and follow-up are truly done.
- If the work is not ready
  - Keep the issue on Lessons Project Lead until the real next owner is clear.
- Stop here if
  - Stop when one honest owner, one honest next step, and any current publish state are explicit on the issue.

<a id="use-this-role-when"></a>
## When To Use This Role

- Use this role when new Lessons work needs routing or the current issue plan is still unclear.
- Use this role when the live job is route-only repair, process repair, or owner repair and no specialist packet exists yet.
- Use this role when publish, PR, QR, or follow-up is the live job.
- Use this role when bounded maintenance needs intake and the earliest honest specialist is still unclear.

<a id="standards-and-support"></a>
## Standards And Support

<a id="publish-and-followthrough"></a>
### Publish And Follow-Up

Use this route when the current job is PR, QR, or follow-up work after the final critic accept.

- Keep the current PR and QR state explicit on the active issue when publish or follow-up is the live job.
- Keep the issue explicit about publish intent: `ship` or `prototype`.
- `ship` requires the current publish review files, PRE_PUBLISH_AUDIT.md, `## Result: PASS`, and no `--skip-compile`.
- `prototype` may leave some publish review files incomplete, but the packet must say exactly what is still missing.
- Keep PR, QR, and follow-up state current on the same issue.
- Open or refresh the PR whenever lesson files, receipts, or follow-up state changed.
- Use the repo-owned GitHub and staging QR helpers instead of global machine auth or ad hoc QR scripts.
- Do not use the QR publish path as a shortcut around packet, review, or receipt rules.
- `ready to merge` means an open non-draft PR, current checks, mergeable state, current QR state when lesson content changed, packet files that still match the PR, and no unresolved review problem or file cleanup hidden as later follow-up.

<a id="existing-lesson-maintenance"></a>
### Existing Lesson Work

Use this route when work starts from an existing lesson bug, field report, or bounded repair request.

- Keep the requested repair scope, touched lesson roots, redesign boundary, and any bootstrap, runtime, tooling, or proof gap explicit on the active issue.
- Confirm the bug from current lesson truth before widening it into redesign.
- Identify the smallest honest repair target before you ask for broader rewrite.
- Route to the earliest safe Lessons owner for the real missing work.
- If no current specialist fits, keep the gap explicit on Lessons Project Lead.
- Do not let maintenance become a vague fix-everything bucket.
- Do not call maintenance complete until the bounded repair is true in current lesson truth and any critic or publish burden that still applies is cleared.

<a id="github-access"></a>
### GitHub Access

Use the repo-owned Lessons GitHub helpers whenever a lane needs `gh` API calls or `git` commands that talk to `github.com`.

#### Use These Helpers

- GitHub helpers
  - lessons-gh
  - lessons-git
  - verify_lessons_github_access.sh
  - update_pr_with_lessons_qrs.sh
- Local env file
  - lessons_github_app.env

Use plain local `git` in the attached checkout for local-only repo work. Use the wrappers above only when the command needs GitHub auth or remote access.

#### Env File

- `GH_APP_LESSONS_APP_ID`
- `GH_APP_LESSONS_PRIVATE_KEY_B64`
- optional `LESSONS_GITHUB_REPO`

#### Verify Access

- `bash ./paperclip_home/project_homes/lessons/tools/lessons-gh pr list -R funcountry/psmobile`
- `bash ./paperclip_home/project_homes/lessons/tools/lessons-git ls-remote https://github.com/funcountry/psmobile.git HEAD`
- `bash ./paperclip_home/project_homes/lessons/tools/verify_lessons_github_access.sh`
- That verification must prove wrapped `bash ./paperclip_home/project_homes/lessons/tools/lessons-gh api repos/<repo>` works, wrapped `bash ./paperclip_home/project_homes/lessons/tools/lessons-gh pr list -R funcountry/psmobile` works, and wrapped `bash ./paperclip_home/project_homes/lessons/tools/lessons-git ls-remote https://github.com/funcountry/psmobile.git HEAD` works.

#### Update PR QR Blocks

- `bash ./paperclip_home/project_homes/lessons/tools/update_pr_with_lessons_qrs.sh --pr <number> --entry-file /absolute/path/to/pr_qr_block_lesson_a.md --entry-file /absolute/path/to/pr_qr_block_lesson_b.md`
- The helper replaces the `LESSONS_PLAYTEST_QRS` marker section in the PR body, or appends that section if it is missing.

#### Stop Rule

- If the local env file is missing or verification fails, stop and escalate.
- Do not route around the failure with global `gh` state or other machine-wide auth helpers.
- Do not treat another checkout or another machine path as the owner of this access flow.

<a id="staging-qr"></a>
### Staging QR

Use the repo-owned staging QR helpers when publish work needs a fresh lessons-dev manifest URL or a PR QR block.

#### Use These Helpers

- QR and publish helpers
  - lessons-staging-qr
  - verify_lessons_staging_qr.sh
  - update_pr_with_lessons_qrs.sh
  - qr_text_png.py
  - qrcodegen.py
- Local env file
  - lessons_r2_publish.env

#### Attached Checkout Truth

- `apps/flutter/lib/app/deep_links.dart`
  - route contains `dev-loaded-lessons`
- `apps/flutter/android/app/src/staging/AndroidManifest.xml`
  - staging scheme contains `com.pokerskill.app.staging`
- `apps/flutter/ios/Flutter/Debug-staging.xcconfig`
  - `APP_URL_SCHEME = com.pokerskill.app.staging`

#### Env File

- `LESSONS_R2_ACCESS_KEY_ID`
- `LESSONS_R2_SECRET_ACCESS_KEY`
- `LESSONS_R2_ENDPOINT`
- `LESSONS_R2_BUCKET`
- `LESSONS_R2_PUBLIC_BASE_URL`
- `LESSONS_R2_REGION`

#### Required Commands

- Smoke test
  - `bash ./paperclip_home/project_homes/lessons/tools/verify_lessons_staging_qr.sh`
- Publish a lesson manifest and generate a staging QR
  - `bash ./paperclip_home/project_homes/lessons/tools/lessons-staging-qr --lesson-id <lessonId> --publish-intent ship`

#### Output Contract

- The smoke test must prove the attached checkout still exposes the `dev-loaded-lessons` route, the staging scheme is still `com.pokerskill.app.staging`, the local R2 env file loads, and a smoke-test QR PNG was written under `paperclip_home/project_homes/lessons/tools/local_outbound/`.
- The publish command must emit `MANIFEST_FILE`, `MANIFEST_URL`, `STAGING_DEEP_LINK`, `QR_PNG`, `QR_PUBLIC_URL`, and `PR_QR_BLOCK_FILE`.
- Use the emitted `PR_QR_BLOCK_FILE` with update_pr_with_lessons_qrs.sh when the lesson belongs to a PR.

#### Stop Rule

- If the local env file is missing, the attached checkout cannot prove the route, or the publish command cannot prove the required gate state, stop and escalate.
- Do not fall back to guessed checkout paths, old skill names, or another repo copy.

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
