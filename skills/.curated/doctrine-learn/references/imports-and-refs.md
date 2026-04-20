# Imports And Refs

This reference teaches how Doctrine files find each other and how one declaration points at another. Reach for it when you are splitting files, reusing a declaration across modules, or wiring a ref from one place into another.

Use `import` to pull in a whole module by alias. Use `from module import Name` to pull in one symbol. Use addressable refs (and `self:`) to point inside a named declaration. Use grouped `inherit { ... }` to cherry-pick which parent fields a child keeps.

## Prefer Typed Refs Over Quoted Names

When a role, review, output, or skill needs to name another Doctrine
declaration, use a typed ref, not a quoted string literal. A typed ref
carries the exact truth the compiler can check. A quoted name is a
decayed copy that drifts the moment the target renames.

- Use `inputs:key` and `outputs:key` when pointing at the current
  agent's IO slots.
- Use `from module import Name` or a bare declaration ref when
  pointing at another declaration by name.
- Use addressable paths like `OutputSchema:field.subfield` when
  pointing at a field inside a named declaration body.
- Use `self:sibling_key` inside a declaration body when you want to
  cite a sibling without repeating the parent name.
- Use bare readable declaration refs (bare `Title` or `Title:key`)
  inside interpolations where a declaration title or key is what you
  actually want to render.

Anti-pattern: the role body carries a quoted string like
`"LessonPlanner"`, `"home:issue.md"`, or
`target_lesson_concepts_sha256` where a typed ref would carry the same
truth. The string survives rename and drifts silently.

`agent-linter` fails loud with `AL440` (declaration name quoted as string
instead of typed ref) when a role cites another declaration this way.

The sections below teach each ref form: module imports, symbol imports,
multi-root resolution, addressable refs, self refs, grouped inherit, and
IO section refs.

## Module Imports

`import module.path` brings in another flow or runtime package. Its exported declarations are available under the dotted path.

`import module.path as Alias` renames the module for this file.

```prompt-fragment
import shared.greeters
import shared.workflows
import chains.deep.levels.one.two.entry as deep_chain
```

After an import, every declaration in that module can be cited with the dotted path:

```prompt-fragment
agent HelloWorldGreeter[shared.greeters.PoliteGreeter]:
    role: "You are the hello world greeter."
```

See `examples/04_inheritance/` for an abstract agent imported from another flow and `examples/03_imports/` for the full `import ... as` and `from ... import` surface.

## Symbol Imports

`from module.path import Name` binds one symbol directly into the current file.

`from module.path import Name as Alias` renames the symbol on the way in.

```prompt-fragment
from shared.review import DraftReviewComment
from shared.review import DraftReviewComment as ImportedComment
from shared.contracts import ReviewContract
```

Imported symbols compose with normal language features. They can be used as parents, `use` entries, workflow refs, IO refs, or anywhere a named declaration is legal.

```prompt
agent ImportsDemo:
    role: "You are the imports demonstration agent."

    workflow: "Imported Steps"
        "Follow the imported instructions below."

        review_contract: ReviewContract
        comment_output: DraftReviewComment
        imported_comment: ImportedComment
```

See `examples/03_imports/prompts/AGENTS.prompt` for the full shipped surface.

## Multi-Root Resolution

Doctrine resolves imports against an ordered list of prompt roots:

1. The absolute prompts root for the current build target.
2. Any `additional_prompt_roots` declared in `pyproject.toml` under `[tool.doctrine.compile]`.
3. For `SKILL.prompt` skill packages, the local package source root when a cross-flow import targets a nested flow under that package, such as a bundled runtime home.

An `additional_prompt_roots` entry reads like this:

```toml
[tool.doctrine.compile]
additional_prompt_roots = ["shared/prompts"]
```

With that config, an author can write a standard import and Doctrine will search the main prompts root first, then the shared root:

```prompt-fragment
import local.shared_turn
import library.io.shared_inputs
```

See `examples/75_cross_root_standard_library_imports/` for the real multi-root layout, including a `shared/prompts/library/` tree that imports resolve into.

Collision detection is strict. If the same dotted path resolves in more than one root, Doctrine fails loud instead of guessing. The `invalid_ambiguous/` sub-case inside `examples/75_cross_root_standard_library_imports/` proves this.

Inside a `SKILL.prompt` package, sibling files in the same flow do not import each other. They use bare refs. Cross-flow imports from that package may still search the package source root for nested flow entrypoints, and package-local collisions with a repo-wide module at the same dotted path still fail loud.

## Addressable Refs

A ref points at a named declaration. The short form uses the declaration name. The long form walks into the declaration with a colon and a dotted path.

Short form (whole declaration):

```prompt-fragment
workflow: SharedGuide
outputs: "Outputs"
    FinalResponse
```

Long form (inside a declaration):

```prompt-fragment
role: "Keep {{ReleaseGates:columns.evidence.title}} and {{ReleaseGuide:release_gates.rows.package_smoke}} aligned."
```

The part before the colon is the named declaration. The part after is the addressable path into its body.

Path refs can reach into any named declaration that carries keyed children: documents, tables, outputs, workflows, skills blocks, IO wrappers, enums.

## Self Refs

`self:` inside a declaration body refers to a path rooted at the current declaration. Use it when you want to cite a sibling key without repeating the parent name.

```prompt
workflow WorkflowRoot: "Workflow Root"
    use shared: ReviewRules

    skills: SharedSkills

    review_sequence: "Review Sequence"
        self:shared.title
        self:skills.title
        self:shared.gates.build.check_build_honesty
        self:skills.can_run.grounding
        "Run {{self:shared.gates.build.check_build_honesty}} with {{self:skills.can_run.grounding}}."
```

`self:` is a `PATH_REF` prefix. It works both as a bare ref line and inside interpolation expressions. See `examples/28_addressable_workflow_paths/prompts/self_and_descent/AGENTS.prompt` for the self-addressed and nested descent surfaces.

## Grouped Inherit

A child declaration can list which parent fields to keep with `inherit { ... }`. The braces carry a comma-separated list of keys.

```prompt
output LessonsLeadOutput[BaseReply]: "Lessons Lead Output"
    inherit {target, shape, requirement, summary}

    hit: "Test"
        "blah blah blah"
```

Grouped inherit also works on IO wrappers:

```prompt-fragment
inputs ReviewSectionInputs[BaseSectionInputs]: "Your Inputs"
    inherit {scoped_catalog_truth}

    override continuity_only: "Continuity Only"
        "Use continuity evidence to re-earn the section."
        "Read one section ahead when the review calls for it."
        ForwardContinuityPacket


outputs ReviewSectionOutputs[BaseSectionOutputs]: "Your Outputs"
    inherit {durable_section_truth}

    override coordination_handoff: "Coordination Handoff"
        "Point the next owner at the reviewed dossier truth."
        CoordinationHandoff
```

Grouped `inherit { ... }` ships across the same block kinds that accept single-key `inherit` today: `agent_slot`, `review`, `analysis`, `schema`, `document`, `workflow`, `skills`, `io`, `output`, and `law`. Pick the shape that matches the parent.

See `examples/24_io_block_inheritance/` for IO block inheritance and `examples/107_output_inheritance_basic/` for output inheritance.

## Bare-Identity Semantic Field Binding

A `semantic_field_binding` can carry a bare identifier with no trailing field path. Use this when the binding carries its own root identity and no descendant path.

```prompt-fragment
bind:
    section_map: SectionMap
    final_response: final_output
```

`SectionMap` here is a bare named ref. `final_output` is a bare identity. Neither walks a path. This is the shipped shape used by `host_contract:` binds in `examples/124_skill_package_host_binding/`.

## IO Section Refs (Direct Form)

An IO wrapper can point at a named ref directly, without a keyed child wrapper. This is the shipped short form.

```prompt
inputs SectionDossierInputs: "Your Inputs"
    issue_ledger: LessonsIssueLedger

outputs SectionDossierOutputs: "Your Outputs"
    section_handoff: SectionHandoff
```

Each body line is `key: RefName`. See `examples/117_io_omitted_wrapper_titles/` for both the direct form and the counter cases that fail loud.

## Runtime Agent Packages

A runtime agent package is a directory-backed import. When an `import` resolves to a directory that contains `<module>/AGENTS.prompt`, Doctrine treats that whole directory as one module.

```prompt-fragment
# prompts/AGENTS.prompt
import writer_home
```

With the source tree:

```text
prompts/
|-- AGENTS.prompt
|-- editor_home/
|   |-- AGENTS.prompt
|   |-- SOUL.prompt
|   `-- references/
`-- writer_home/
    `-- AGENTS.prompt
```

The `writer_home` module resolves into `writer_home/AGENTS.prompt`. Declarations inside it are reached through the module alias:

```prompt
agent BriefWriter:
    role: "Draft the first brief and hand it to the editor."
    workflow: "Draft"
        "Write the first brief for the editor."
        routing: "Routing"
            route "Hand the brief to BriefEditor." -> editor_home.BriefEditor
```

Rules:

- The directory name is the module name.
- The directory must contain `AGENTS.prompt` at its root.
- Peer files such as `SOUL.prompt` and `references/` belong to the same runtime home and emit beside the compiled `AGENTS.md`.
- Nested runtime packages follow the same rule recursively.

See `examples/115_runtime_agent_packages/` for the full layout plus nested references.

Runtime agent packages and `SKILL.prompt` skill packages are different surfaces. A runtime package emits `AGENTS.md`. A skill package emits `SKILL.md`. See `references/skills-and-packages.md` for the skill package surface.

## Pitfalls

- Do not mix `import module` and `from module import Name` on the same symbol in the same file. Pick one.
- Do not rely on search-order luck across multi-root setups. Collisions fail loud and should be renamed, not silenced.
- Do not use `self:` to reach outside the current declaration. It is rooted at the declaration, not the file.
- Do not write `inherit { ... }` for fields the parent does not declare. The compiler checks every key.
- Do not import a runtime agent package as a plain module. The directory form is the shipped shape; it owns the whole runtime home.
- Do not write relative imports. They are retired. Inside one flow use bare refs. Across flows use absolute imports.

## Related References

- `references/skills-and-packages.md` owns the `SKILL.prompt` package source root and its own import rules.
- `references/outputs-and-schemas.md` owns `output` inheritance, `route field`, and `final_output` refs.
- `references/reviews.md` owns review inheritance and carried-state refs.
- `references/agents-and-workflows.md` owns `workflow` refs, routes, and `handoff_routing`.
- `references/emit-targets.md` owns the `pyproject.toml` `additional_prompt_roots` setting and emit pipelines.

**Load when:** the author is splitting files across modules, wiring a ref across packages, picking fields with `inherit { ... }`, using `self:` inside a declaration, or setting up a directory-backed runtime agent package.
