# Flow Namespace Worklog

Plan: [docs/PROPOSAL_FLOW_NAMESPACE.md](/Users/aelaguiz/workspace/doctrine/docs/PROPOSAL_FLOW_NAMESPACE.md:1)

## 2026-04-17

- Started `auto-implement` from the canonical flow-namespace plan.
- Preflight passed:
  - `~/.codex/hooks.json` points `Stop` at the installed `arch_controller_stop_hook.py`.
  - the installed runner exists.
  - `codex features list` shows `codex_hooks` enabled.
- Resolved the last branchy plan line in Section 6 by choosing to retarget
  `examples/03_imports/` in place.
- Created the implement-loop controller state for this session.
- Marked Phase 1 as `IN PROGRESS`.
- Landed the first Phase 1 code slice:
  - `export` now parses as a top-level declaration modifier.
  - relative-import syntax is gone from the shipped grammar.
  - `PromptFile.exported_names` records exported declarations without wrapping
    authored declaration nodes.
  - `doctrine._compiler.indexing` now has flow-boundary discovery helpers.
- Ran:
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_parser_source_spans`
- Result:
  - `OK` (`16` tests)
- Next:
  - replace unit-first ownership with a real merged `IndexedFlow`
  - re-key the session to `root_flow`
  - start wiring exported declarations into real flow-aware indexing
- Landed the second Phase 1 code slice:
  - `IndexedFlow` now owns merged declarations plus declaration-owner-unit
    bookkeeping.
  - flow loading moved from unit/module caches to flow caches and
    `CompilationSession.root_flow`.
  - `load_module` now resolves through the owning flow and keeps same-flow
    sibling imports inside one merged boundary.
  - compile entry selection for root agents, readable declarations, and skill
    packages now comes from `root_flow`.
  - runtime-package flow entrypoints keep their package-root metadata.
- Ran:
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_parser_source_spans tests.test_import_loading`
- Result:
  - `OK` (`31` tests)
- Next:
  - keep deleting the remaining root-owner reads outside `root_flow`
  - start the Phase 2 resolver and traversal cut
- Landed the next Phase 1 plus Phase 2 slice:
  - `CompilationSession` now preserves the active in-memory `PromptFile` while
    it builds `root_flow`, so mutated prompt tests exercise the real flow path
    instead of reparsing stale disk state.
  - peer `AGENTS.prompt` and `SOUL.prompt` files now compile as separate
    runtime flows, which keeps runtime-package imports from merging both
    entrypoints into one namespace.
  - the red repo invalid fixtures in `examples/45`, `46`, `47`, and `49` now
    live under nested flow roots, so compile-fail and parse-fail proof runs
    stop poisoning sibling cases under one directory-wide flow.
  - skill-package nested agent prompts now compile from their owning flow unit
    instead of pretending the package root file owns every bundled agent.
- Ran:
  - `uv run --locked python -m unittest tests.test_compile_diagnostics`
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_emit_docs tests.test_emit_skill`
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_parser_source_spans tests.test_import_loading tests.test_compile_diagnostics tests.test_review_imported_outputs tests.test_emit_flow tests.test_emit_docs tests.test_emit_skill`
- Result:
  - `OK` (`178` tests)
  - `OK` (`43` tests)
  - `OK` (`262` tests)
- Next:
  - move bare-name lookup onto flow-wide registries
  - retire same-flow imports with dedicated flow-era diagnostics
  - keep pushing graph and emit traversal off unit-owned roots
- Landed the next Phase 2 plus Phase 3 slice:
  - generic bare-name declaration lookup now resolves through the owning
    `IndexedFlow`, which lets sibling declarations resolve without same-flow
    imports
  - local skill-package scans now treat the whole flow as visible instead of
    only the current file
  - `examples/03_imports` now teaches dotted cross-flow imports without
    relative-import syntax and proves real cross-flow cycle behavior with
    nested flow roots
  - `examples/69`, `70`, and `75` now use explicit helper flows with exported
    declarations instead of file-owned helper modules
  - host-bound skill-package corpus and smoke fixtures dropped same-flow
    `from refs... import ...` patterns and now rely on flow-local bare names
  - moved fixture paths and one checked-in host-bound skill contract were
    retargeted to the new flow-root layout
- Ran:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/69_case_selected_review_family/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/70_route_only_declaration/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/75_cross_root_standard_library_imports/cases.toml`
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/124_skill_package_host_binding/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/48_review_inheritance_and_explicit_patching/cases.toml`
  - `make verify-examples`
  - `make verify-diagnostics`
- Result:
  - all targeted manifest runs passed
  - `OK` (`23` tests)
  - `make verify-examples` passed
  - `make verify-diagnostics` passed
- Next:
  - keep the implement loop armed for a fresh audit against the wider Phase 2
    through Phase 5 frontier
  - let the audit decide whether the next slice stays in Phase 2 semantic cut
    work or moves deeper into the remaining planned corpus/docs/release work
- Landed the next Phase 1 plus Phase 2 owner-cleanup slice:
  - cached `root_flow` inside `CompilationSession`, so same-flow resolution
    now stays on the active in-memory prompt graph instead of silently
    reparsing stale disk state
  - removed the shipped `ModuleLoadKey` / `root_unit` owner aliases and
    retargeted the remaining session, flow, output-validation, docs, flow
    emit, and corpus helpers to `root_flow` / `root_entrypoint_unit`
  - reworked runtime emit-root discovery into a depth-first same-flow walk, so
    nested runtime packages keep first-seen import-graph order
- Ran:
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_emit_docs`
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading tests.test_compile_diagnostics tests.test_emit_docs tests.test_emit_flow tests.test_output_schema_lowering tests.test_output_schema_validation`
  - `make verify-examples`
  - `make verify-diagnostics`
- Result:
  - `OK` (`202` tests)
  - `OK` (`256` tests)
  - `make verify-examples` passed
  - `make verify-diagnostics` passed
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether the next frontier stays in the remaining
    Phase 2 import/diagnostic cut or moves into the planned Phase 3 corpus
    additions and the untouched Phase 4 and 5 docs/release work
- Landed the next Phase 2 flow-owned contract-resolution slice:
  - `ResolveRefsMixin._resolve_decl_ref` now resolves imported declarations
    through the owning flow registry instead of only through the imported
    entrypoint file, so exported sibling declarations stay visible across
    boundaries.
  - review subjects, route_only facts, schema artifacts, review subject-key
    validation, and final_output declaration resolution now all use flow-owned
    input and output lookup helpers instead of current-file registries.
  - focused tests now prove two missing cases:
    - same-flow review contracts can bind sibling-file inputs and outputs with
      no same-flow import syntax
    - an imported review flow can export its shared comment output from a
      sibling file under the flow root instead of only from `AGENTS.prompt`
- Ran:
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_review_imported_outputs tests.test_import_loading tests.test_compile_diagnostics`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - `OK` (`206` tests)
  - `make verify-diagnostics` passed
  - `make verify-examples` passed
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether the next honest frontier is the remaining
    Phase 1 thin-carrier cleanup, deeper Phase 2 owner cleanup, or the still
    incomplete Phase 3 through Phase 5 plan work
- Landed the next Phase 1 thin-carrier slice:
  - `IndexedUnit` no longer stores `UnitDeclarations` or `LoadedImports`
    directly.
  - `IndexedFlow` now owns per-member declaration and import bundles through
    `unit_declarations_by_path` and `loaded_imports_by_path`.
  - the old `unit.declarations`, `unit.loaded_imports`, and flattened
    `unit.*_by_name` reads still work, but they now proxy through flow-owned
    state instead of making the carrier object the storage owner.
  - flow construction no longer clones units just to swap in rebound import
    state; the flow now re-homes that state while keeping one unit object per
    member file.
- Ran:
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading tests.test_compile_diagnostics`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - `OK` (`204` tests)
  - `make verify-diagnostics` passed
  - `make verify-examples` passed
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether the next honest frontier is the remaining
    Phase 2 flow-keyed graph and emit identity cut, the planned Phase 3 proof
    expansion, or the still untouched Phase 4 and Phase 5 work
- Landed the next Phase 2 plus Phase 3 graph-and-proof slice:
  - flow-graph extraction now keys agents, artifacts, note maps, and edges by
    `(prompt_root, flow_root, name)` identity instead of only by module parts,
    so sibling-named nodes from imported flows stop colliding in the live
    graph
  - docs emit now builds previous-turn context maps with flow-owned agent keys,
    and resolves predecessor outputs through the owning flow instead of
    reparsing module-only owners
  - D2 layout and render grouping now salt node and path identity with flow
    roots, while helper-only imported runtime packages no longer fail loud
    when they add no concrete runtime agent
  - the remaining same-flow import-era emit and output-rendering tests now use
    bare same-flow refs or real helper flow roots, and the checked-in flow
    build refs in `examples/36`, `73`, and `115` were regenerated for the new
    graph identity
- Ran:
  - `uv run --locked python -m unittest tests.test_emit_flow tests.test_emit_docs tests.test_output_rendering`
  - `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading tests.test_compile_diagnostics tests.test_review_imported_outputs tests.test_emit_flow tests.test_emit_docs tests.test_output_rendering`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - `OK` (`59` tests)
  - `OK` (`265` tests)
  - `make verify-diagnostics` passed
  - `make verify-examples` passed
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether the remaining honest frontier is the late
    Phase 1 carrier cleanup, the last Phase 2 diagnostics and identity work,
    the planned Phase 3 `129` through `134` additions, or the still untouched
    Phase 4 and Phase 5 docs and release work
- Landed the next Phase 3 proof-expansion slice:
  - added `examples/129_flow_sibling_namespace` through
    `examples/134_flow_export_boundary`
  - the new set proves the flat sibling namespace, sibling producer and critic
    routing, honest cross-flow imports, sibling-collision failures, retired
    same-flow imports, and export-gated cross-flow visibility
  - updated `examples/README.md` so the shipped corpus index now names the new
    examples and their flow-era purpose
- Ran:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/129_flow_sibling_namespace/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/130_cyclic_producer_critic/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/131_cross_flow_import/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/132_flow_sibling_collision/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/133_intra_flow_import_retired/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/134_flow_export_boundary/cases.toml`
- Result:
  - all six targeted manifest runs passed
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether the remaining honest frontier is the late
    Phase 1 carrier cleanup, the last Phase 2 diagnostics and identity work,
    the remaining Phase 3 example audit, or the untouched Phase 4 and Phase 5
    docs and release work
- Landed the first Phase 4 docs and release slice:
  - rewrote the public import story in `docs/LANGUAGE_REFERENCE.md` around
    flow roots, bare same-flow refs, `export`-gated cross-flow visibility, and
    retired same-flow imports
  - updated `docs/COMPILER_ERRORS.md` for `E314`, `E315`, and `E316`, retired
    `E306` from the public catalog, and refreshed the `E307` and `E308`
    wording
  - updated `docs/README.md`, `AGENTS.md`, and `examples/README.md` so repo
    truth and corpus scope match the new examples and namespace model
  - added the planned `4.0` breaking payload draft to `CHANGELOG.md` and
    updated `docs/VERSIONING.md` to classify the flow-root cut as a breaking
    language move from `3.0` to `4.0`
- Ran:
  - focused readback over the changed public doc surfaces
- Result:
  - the changed docs now tell one flow-root namespace story
  - no code-linked verification rerun was needed for this doc-only slice
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether the remaining honest frontier is the late
    Phase 1 carrier cleanup, the last Phase 2 diagnostics and identity work,
    the remaining Phase 3 example audit, or the rest of the unfinished Phase 4
    and Phase 5 docs and release work
- Landed the next late Phase 1 plus Phase 2 plus Phase 4 cleanup slice:
  - deleted the remaining `IndexedUnit` compatibility bridge for
    `unit.declarations`, `unit.loaded_imports`, and flattened `unit.*_by_name`
    lookups
  - retargeted the last shared resolver, validator, and skill-package lookup
    paths onto `unit_declarations(...)`, `unit_loaded_imports(...)`, and
    flow-owned package registries
  - removed same-flow `from refs... import ...` lines from the first-party
    `agent-linter` and `doctrine-learn` skill-package flows and from the
    matching `emit_skill` proof fixtures, which brought the public-install
    package proof back to green
  - finished the late Phase 4 doc sweep by updating the live `4.0` version
    line, retiring the last relative-import guidance, adding a flow-boundary
    note, and fixing the remaining import-era wording in the scanned docs
- Ran:
  - `uv run --locked python -m unittest tests.test_emit_skill tests.test_import_loading tests.test_compile_diagnostics tests.test_emit_flow tests.test_emit_docs tests.test_output_rendering`
  - `make verify-package`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `uv run --locked python -m unittest tests.test_release_flow`
- Result:
  - `OK` (`263` tests)
  - `make verify-package` passed
  - `make verify-examples` passed
  - `make verify-diagnostics` passed
  - `OK` (`24` tests)
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether any real frontier remains in Phase 2 through
    Phase 5 after the owner-path cleanup, package proof, and doc sweep landed
- Landed the last late Phase 4 public-teaching slice:
  - rewrote the stale same-flow and relative-import teaching in
    `docs/LANGUAGE_REFERENCE.md` and `docs/SKILL_PACKAGE_AUTHORING.md`
  - rewrote the bundled `doctrine-learn` references to the flow-root import
    story and updated the examples ladder to the `01` through `134` corpus
  - regenerated `skills/.curated/doctrine-learn/` so the checked public
    install tree matches the updated teaching bundle
- Ran:
  - `make verify-package`
- Result:
  - `make verify-package` passed
- Next:
  - move straight into the Phase 5 release-candidate pass from the cleaned
    tree
- Landed the local Phase 5 release-candidate slice:
  - updated `pyproject.toml` package metadata to `4.0.0`
  - promoted the breaking flow-namespace release entry to
    `## v4.0.0 - 2026-04-18` in `CHANGELOG.md`
  - reran the full local release proof set from that finalized tree
  - checked git release readiness and confirmed the actual signed tag cut is
    still blocked on a clean committed worktree
- Ran:
  - `uv sync`
  - `npm ci`
  - `uv run --locked python -m unittest tests.test_package_release`
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `make verify-package`
  - `git tag --list 'v4.0.0'`
  - `git status --short`
- Result:
  - `uv sync` passed
  - `npm ci` passed
  - `OK` (`5` tests)
  - `OK` (`24` tests)
  - `make verify-examples` passed
  - `make verify-diagnostics` passed
  - `make verify-package` passed
  - no `v4.0.0` tag exists yet
  - the worktree is still dirty, so the real signed tag cut is not reachable
    from this state
- Next:
  - keep the implement loop armed for the next fresh audit
  - let the audit decide whether to stop on the real release-cut blocker or
    continue if a clean committed tree becomes available
- Landed the real Phase 5 release-cut slice:
  - found that `make release-tag` still rejected the `v4.0.0` changelog entry
    because the helper only accepts single-line required header fields
  - rewrote the `v4.0.0` changelog header into the exact helper shape
  - reran the release-only proof set and got back to green
  - committed the changelog repair as `08330e6`
  - cut and pushed the signed annotated `v4.0.0` tag from that clean commit
- Ran:
  - `uv run --locked python -m unittest tests.test_package_release`
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `make verify-package`
  - `git commit -m "Fix v4.0.0 changelog release header"`
  - `make release-tag RELEASE=v4.0.0 CHANNEL=stable`
  - `git tag --list 'v4.0.0'`
  - `git rev-list -n 1 v4.0.0`
- Result:
  - `OK` (`5` tests)
  - `OK` (`24` tests)
  - `make verify-package` passed
  - commit `08330e6` created cleanly
  - signed annotated tag `v4.0.0` was created and pushed
  - `v4.0.0` points at `08330e684703a23e70fe9cec48e0ec89ffab6bcd`
- Next:
  - keep the implement loop armed for one fresh audit closeout pass
  - let that audit decide whether the plan can finally move to complete
