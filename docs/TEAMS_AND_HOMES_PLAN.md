# Teams And Homes: Implementation Plan For Issues #90 To #103

Status: reviewed. This file is the binding spec for every implementer.

**Language design is closed.** Every keyword, grammar rule, semantic rule, diagnostic
code, CLI verb, JSON key, and render line below was set by the language designer. An
implementer does not choose syntax, names, defaults, error wording, or output shape.
If this spec is wrong, silent, or contradicts the code, stop and report it. Do not
work around it and do not fill the gap. The one thing left to implementers is internal
code structure that no author, harness, or test can see.

## 1. What The Requests Really Ask For

Long-running agent teams hit five failures with hand-written Markdown: length nobody
can see, near-copies that drift, lessons that reach the wrong agents, boilerplate about
how runtimes load files, and compiled files that go stale.

The issues read as 13 requests. They come down to six ideas.

| Idea | Issues | One line |
| --- | --- | --- |
| Finish the prose surface | #103, part of #96 | No text is lost. Every string is a paragraph. Every inherited item is accounted for. |
| One patch language | #96, #103 item 1 | `inherit`, `override`, `drop`, and `inherit *` work the same on every inheritable body. |
| Late-bound values | #91 | Shared text reads the words of the agent it lands in. |
| Teams are folders | #94, #97, #95 | What an agent is comes from its role. Where it lives comes from its team's folder. |
| Hot and cold text | #92, #93 | Mark what is read on demand. Count what is always on. |
| The home map | #98, #99, #101, #93, #96 | One record of which declaration produced which text in which home drives every report. |

Two more are small and stand alone: `quote` and `person` (#100, #101), and message
outputs read as inputs (#102).

### Merged Issues

| Workstream | Issues | Why they ship together |
| --- | --- | --- |
| WS1 Prose and patches | #103, #96 | Same files, same rule: nothing inherited vanishes silently. |
| WS2 Values and teams | #91, #94 | A team is the place values live. |
| WS3 Homes and load | #92, #93, #95, #97 | All four need the home tree and the runtime model. |
| WS4 Reach | #98, #99, the report half of #101 | All read the home map. |
| WS5 Provenance | #100, the declaration half of #101 | `person` serves both. |
| WS6 Messages | #102 | Small, self-contained. |
| WS7 Tools and closure | all | `doctrine import`, docs, corpus, and downstream checks. |
| WS8 Doctrine Learn teaches results | new ask | The skill teaches how to get good results, not only the syntax. |

## 2. What We Copy, And From Whom

We invent as little as possible. Each row is a shipped design from another language.

| Doctrine feature | Copied from | What we take | What we refuse |
| --- | --- | --- | --- |
| `{{agent:x}}` late binding | Jsonnet `self`, Pkl late-bound properties, Nickel merge | Text reads the final object, so a value set low reaches text written high | Their expression languages. Values are text. No `if`, no loops (Kustomize: "free from templates and DSLs") |
| Value precedence | Nix `callPackage` | Fill from an environment, explicit args win | Priority numbers |
| Missing value error | Nix `callPackageWith`, Pkl `undefinedPropertyValue` | Names the argument and the call site | Lazy failure at read time. We fail at build, for every blank at once |
| Value cycle error | HOCON "unbreakable cycles", CUE reference cycles | Cycles are errors with a named path | Stack overflows |
| `drop` on a missing key is an error | Haskell `hiding` ("It is an error to hide an entity that is not, in fact, exported"), RFC 6902 `remove` | A stale drop fails loud | Nix `removeAttrs`, where a stale removal is silent |
| `drop` needs a reason | Rust `#[deprecated(note = ...)]` | The reason lives in source and tools read it | |
| `inherit *` | Rust `..base`, Haskell `hiding`, Dart `hide` | Everything not named, placed once | The fragile-base trap of Rust RFC 1105: new names arrive silently. Our answer is that `doctrine diff` names them |
| Explicit lists stay legal | Dart `show`, Haskell import lists | A new base member forces a decision | |
| `member` overlay | Kustomize base and overlay | State only what differs | Strategic-merge directives |
| Tree from paths | Filesystem walk both runtimes already do | No parent declaration | C3 linearization and mixins. Python's docs warn such hierarchies "should be avoided" |
| `details` | HTML `<details>`, GCC `cold` | Author marks intent, compiler chooses placement | Author-chosen chunk names |
| Shared companion | webpack SplitChunks | A module shared by many chunks lands once | Size heuristics |
| Budgets | Angular `budgets`, Lighthouse `budget.json`, webpack `performance.hints`, `cargo bloat` | Warn and error levels, nearest match, name the biggest parts, "And N smaller" | Percent baselines |
| `doctrine diff` | Terraform plan, Nx `--base`, compressed-size-action | Compile both revisions, compare, name the cause | Saved state files |
| Rule scopes | Nx tags, import-linter wildcards, Bazel `somepath` | Scope by tag or folder, print the path that reached | |
| `doctrine build --check` | prettier and black | 0 clean, 1 findings, 2 tool failure | gofmt's exit 0 on findings |
| `person.owns` | CODEOWNERS, REUSE.toml | A central list, not an attribute on the owned thing | Last-match precedence. Owners add up |
| `quote` | Pandoc `[@key]`, CSL | Declare once, cite by key, one rendering | Styles and locators |
| Near-copy check | PMD CPD, jscpd, clone Types 1 to 3, `difflib` | Token windows avoid N-squared; `autojunk=False` on short text | Semantic Type 4. That stays with the agent linter |
| Message input | Protobuf one-file contract, AsyncAPI send and receive | One declaration, both sides render it | A new message channel. Doctrine's emitted contract surface stays `output` |

### Runtime Facts The Design Rests On

Measured November 6, 2026 on Claude Code 2.1.317 and Codex source `54201ea65a`.

- Claude Code joins `CLAUDE.md` and `.claude/CLAUDE.md` from the top folder down to the
  start folder. Lower folders load when a file there is touched. Siblings never load.
- Claude Code reads `AGENTS.md` only when no CLAUDE file sits in that chain.
- `@` imports stop at four hops. In headless runs, imports from outside the start folder
  drop silently unless the project was already approved.
- On a 1M window, 150,000 characters is a warning for the combined load and a hard cut
  only for files loaded on demand. On a 200K window the numbers are 120,000 and 40,000.
  The unit is JavaScript string length (UTF-16 code units).
- Codex reads one file per folder from the nearest `.git` down to the start folder, root
  first. It follows no imports and does no lazy loading.
- Codex's `project_doc_max_bytes` is 32,768 bytes total. The file that crosses the limit
  is cut mid-file with no notice to the model, and later files are dropped. So a member's
  own file, read last, is what Codex loses.
- Both runtimes follow symlinks, and Claude Code reads a linked `CLAUDE.md` once. Its
  Edit and Write refuse the link, which suits a compiled file. So Doctrine writes one
  real `AGENTS.md` and links `CLAUDE.md` to it.
- Claude Code strips block-level HTML comments before it injects a file.

## 3. Language Version

This plan is language version **6.0**. It breaks four things on purpose. The first three
each turn a silent loss into a loud error or a corrected render:

1. Children must account for inherited head prose, `role`, and typed agent fields.
2. Every authored prose string renders as its own paragraph, and a code fence must sit whole
   inside one string.
3. A readable block no longer prints a bare kind line such as `_section_`.
4. New keywords can't be keys where their form can start: `drop` and `paragraph` in every
   patchable body, `member` and `home` as agent slots, and `values`, `budget`, `roster`, and
   `details`. A key that used one gets a parse error and a new name. Its rendered title
   doesn't change.

`docs/VERSIONING.md` and `CHANGELOG.md` record this as a major language move with
upgrade steps. The release version in the changelog is 6.0.0. No tag or publish is part
of this work.

## 4. WS1: Prose And Patches (#103, #96)

### 4.1 Every String Is One Paragraph

An authored string is one paragraph. Two adjacent prose strings in any body render with
one blank line between them. This holds for workflow roots, sections, documents, record
bodies, and role blocks. List items, table cells, and definitions are not body prose and
keep their own layout. A triple-quoted string keeps its inner newlines as written.

Today's single-newline join is removed for authored strings. There is no opt-out.

This rule is about strings an author wrote. A line the compiler generates, such as a row of a
contract table, an item of a generated list, or a line of a JSON example, keeps the layout it
ships with today. So the compile step marks authored strings at the one place they all pass,
`_interpolate_authored_prose_line`, with a `str` subclass, and `_render_body_lines` puts a
blank line around a marked string and around an `EmphasizedLine`. Everything else takes the
shipped path, so a generator needs no change.

There is no exception for what a string holds. Separate strings that each hold a list item
become a loose list, which still reads as a list. An author who wants it tight writes
`bullets`, or one `"""` string.

A code fence can't go that way, because a blank line between fenced lines changes the code. A
string that opens a fence it doesn't close is `E605`: an odd number of its lines start with
three backticks once trimmed. So a fence sits whole in one `"""` string, or in a `code` block.

### 4.2 Block Metadata

A readable block prints its metadata line only when it carries `required`, `advisory`,
`optional`, or `when`. The line then names the kind, as in `_Required · section_`. A block
with none of those prints no metadata line, so `_section_`, `_table_`, and the like never
appear alone. `compile/readable_blocks.py` must use the rule `compile/readables.py` already
uses for sections, and `_render_metadata_line` callers follow it for every kind.

### 4.3 Parse Diagnostics

- `E132` fires only when the token before the failure is `->`.
- New `E134` "Missing block title" fires when a named readable block has no title at the
  end of its head line, such as `table calls_table:` with nothing after the colon. Its
  kinds are the ones whose grammar requires that title: `table`, `definitions`, `callout`,
  `properties`, `section`, `code`, `markdown`, `html`, `footnotes`, and `image`. Its hints
  read ``Write `table calls_table: "Title"`.``, then for `table` only
  ``Write `table calls_table: TableRef` to use a declared table.``, then for a kind with a
  bare form ``Write `table:` for a block with no heading.`` The block kind and key in the
  hint come from the source. It lives beside the other parse classifications.

### 4.4 Lone Module Files

`resolve_flow_entrypoint` gains one rule. A `.prompt` file with no flow entrypoint at or
above it, inside its prompt root, is a one-file flow. This makes the shipped sentence in
`docs/LANGUAGE_REFERENCE.md` true: "A file-backed `<module>.prompt` import is a
compile-time boundary with one prompt file as its full flow surface." `E292` stays for
paths outside any prompt root. `E315` is unchanged.

### 4.5 `E206` Is Retired

`role` already renders in authored order. `_enforce_legacy_role_workflow_order` and
`E206` are deleted. `E206` moves to the retired list in `docs/COMPILER_ERRORS.md`. Example 01's
case that expected it is gone from this branch, and example 168 proves the new behavior.

### 4.6 `paragraph`

A new readable block. It gives a paragraph an address, and optionally a run-in head.

```lark
readable_paragraph_block: "paragraph" CNAME ":" string? readable_requirement? readable_guard? _NL _INDENT paragraph_body _DEDENT
override_readable_paragraph_block: "override" "paragraph" CNAME ":" string? readable_requirement? readable_guard? _NL _INDENT paragraph_body _DEDENT
paragraph_body: prose_or_details+
?prose_or_details: prose_line _NL?
                 | readable_details_block
                 | readable_bare_details_block
```

Add both to `readable_nonsection_block` and `override_readable_nonsection_block`.
`readable_details_block` arrives in WS3. Until WS3 lands, `paragraph_body` is `(prose_line _NL?)+`.

Rendering:

- With a title: `**<title>** <first string>`. Later strings follow as their own
  paragraphs. The title is rendered as written, so authors write its final punctuation.
- Without a title: the strings render as plain paragraphs with no heading and no metadata.
- A paragraph with `required`, `advisory`, or `when` renders that metadata in the same
  form as other blocks, as a line before the paragraph.

Addressing: `Decl:section.key` works like any keyed block. `{{Decl:section.key.title}}`
reads the title.

```prompt
workflow HowYouThink: "How you think"
    paragraph test_plan: "A test plan that grows with the design."
        "You test a change best having followed it from the start."
        "Write the plan while the design settles."
```

renders:

```markdown
**A test plan that grows with the design.** You test a change best having followed it from the start.

Write the plan while the design settles.
```

### 4.7 Every Inherited Item Is Accounted For

Doctrine's rule stands: "Children must account for every inherited keyed item exactly
once." This plan closes its three holes.

**Head prose.** Prose outside any keyed item is a keyed item with the reserved key
`preamble`, on `workflow`, `document`, `analysis`, `schema`, and every other body whose
model has a `preamble` field. A parent with a preamble requires the child to write
`inherit preamble`, or `drop preamble: "why"`. The child's own loose prose stays at the top
of its body, as the parser already requires, and renders after the parent's. A missing
account is `E003`, listing `preamble` like any other key.

**`role`.** On an agent, `role` is an inherited item. A child writes `role: ...` to
replace it, as today, or `inherit role` to keep it. `drop role` is `E612`. A concrete
agent that ends with no role still gets `E205`. An inherited role keeps the meaning it had
where it was written: its `{{Ref}}`s resolve in the parent's module, as a slot's do.

**Typed fields.** `inputs`, `outputs`, `analysis`, `decision`, `skills`, `review`,
`final_output`, and `selectors` on a parent are inherited items. A child writes the field
to replace it, as today, or `inherit inputs`, or `drop inputs: "why"`. Omitting one is
`E003`. Today they vanish with no error. `inputs[Parent]:` and `outputs[Parent]:` patch
fields count as an account of `inputs` and `outputs`.

An agent may have several `decision:` fields. Together they are one item, `decision`.
`inherit decision` keeps them all, in order, at that spot. `drop decision` removes them all.
Writing `decision:` in the child replaces them all.

An inherited typed field's declaration refs resolve in the parent's module, whatever the
parent imported and under whatever alias, and whether or not the declaration is exported. So
each `NameRef` in the field is pinned to the module that wrote it. Prose inside an
inline `inputs:`, `outputs:`, or `skills:` body resolves where it lands, which is what shipped
`output` inheritance does.

`_RESERVED_AGENT_FIELD_KEYS` stops rejecting `inherit role` and `inherit <typed field>`.

### 4.8 The Patch Language

Every body with an `inherit` form gains the same two forms. That is `agent`, `workflow`,
`document`, `analysis`, `schema`, `review`, `review_family`, `abstract review`, `skills`,
`inputs`, `outputs`, `output`, `output shape`, `output schema`, and `receipt`. WS2 adds
`team`. `schema` body keys are `sections`, `gates`, `artifacts`, `groups`, and `preamble`. A
`receipt`'s keys are its fields and its `route` fields, so a child accounts for a parent's
route like any field. A route has no `override` form: a child inherits or drops a parent's
route, and adds a new key for anything else. A child `route` on a parent's key is the shipped
`E544`.

```lark
inherit_all: "inherit" "*" _NL?
drop_item: "drop" patch_path ":" string _NL?
patch_path: CNAME ("." CNAME)*
```

`override` gains a dotted form on `agent` and `workflow` bodies. One rule serves both:

```lark
override_path: "override" CNAME "." patch_path ":" string? _NL _INDENT workflow_section_body _DEDENT
```

A dotted `override` names one keyed section, slot, or `paragraph` at any depth and replaces
it in place. It keeps the target's kind: the string is the new title, and the body is the
new body. A `paragraph` body takes only prose and `details`. A block with its own body form,
such as `table` or `callout`, can't be the target, because this one grammar can't parse its
body. Override the section that holds it. `drop` works on any keyed item. A path steps
through agent slot keys, workflow section keys, and keyed readable blocks. It never steps
through anonymous items.

A dotted patch on `a.b` keeps `a` and is the account for `a`, so writing `inherit a` beside
it is `E612`. Patches on different items under one parent are fine: `override a.b` and
`drop a.c` live together. `a` renders where the first patch naming it stands, or in its
parent position under `inherit *`.

**`drop key: "reason"`** accounts for an inherited item and removes it. The grammar requires
the reason. It renders nowhere in a home. The home map keeps it (section 7).

**`inherit *`** accounts for every inherited item the child does not otherwise name.

- It may appear once in a body. A second one is `E613`.
- The body is ordered in three parts. First, items written before `inherit *`. Then the
  parent's items in the parent's order, with each overridden item in its parent position
  and each dropped item gone. Last, items written after `inherit *`. A plain `role:` or
  typed field isn't an `override`, so it stays where it is written.
- An item named by `inherit key` elsewhere in the body moves to that spot, which is the
  one way to reorder.
- Grouped `inherit {a, b}` is unchanged.

Errors:

| Code | When |
| --- | --- |
| `E610` | `drop` or a dotted `override` names a key the parent does not have, or `inherit *` has nothing to inherit |
| `E611` | A dotted path steps through an item with no keyed children, or a dotted `override` targets anything but a section, slot, or `paragraph`, or gives a `paragraph` a body it can't hold |
| `E612` | A `drop` or dotted `override` names an item the body already names, `inherit a` sits beside a patch under `a`, a path sits under a dropped or overridden item, or `drop role`. The error sits on the later item |
| `E613` | `inherit *` appears twice in one body |

An abstract slot is a requirement, not an item, so it is not among the parent's keys.
Dropping one is plain `E610`, and `inherit *` doesn't account for it.

**Shipped errors stay.** `E610` to `E613` are about the new forms. Each kind keeps the errors
it already ships for its own forms. Two old-form items on one key keep their shipped
duplicate error, such as `E255`, or `E491` on a review. A missing account stays `E003`, or
`E490` on a review body, or `E544` on a receipt.

**Implementation shape (binding).** One helper expands patch forms before each resolver
runs, so all 15 kinds share one behavior:

```python
def expand_patch_items(items, *, parent_keys, kind, owner_label, unit) -> PatchExpansion
```

It returns the child's items with `inherit *` replaced by explicit inherits, plus the
set of dropped keys, plus a map from dotted paths to replacement items. Each resolver's
existing loop treats a dropped key as accounted and skips it. Dotted overrides are
applied to the parent's resolved item before that loop runs.

### 4.9 Docs Steer Prose Authors

`docs/AUTHORING_PATTERNS.md` gains "Writing A Mostly Prose Home": triple-quoted strings
take ordinary quotes and line breaks, `paragraph` addresses a lead-in, and one-line
strings fit short rules only.

## 5. WS2: Values And Teams (#91, #94)

### 5.1 Values

```lark
values_block: "values" ":" _NL _INDENT value_item+ _DEDENT
value_item: CNAME ":" string _NL?
```

`values_block` joins `agent_field`. `values` joins `_RESERVED_AGENT_FIELD_KEYS`. It does
not render. A value is plain text.

Two interpolation roots read values and facts:

- `{{agent:key}}` reads the concrete agent whose home the text lands in.
- `{{team:key}}` reads that agent's team, or, in a team's own file, that team.

They resolve late: after inheritance, once per concrete home. The resolver checks their
syntax and leaves them in place, so resolved declarations stay shared and cached. One
final pass over the compiled home substitutes them in every string, titles included.

**Where they work.** Every authored prose string and every title that lands in a home,
including `markdown` and `html` block text and `details` (section 6.3 limits shared
details). They do not work in `code` blocks, which stay literal, or in `output schema`
text, which is `E602`. A skill package body, its emitted documents, or any compile with
no home is `E602`.

**Lookup for `{{agent:key}}`, first match wins:**

1. A fact from the table below.
2. The agent's own `values:`.
3. Its team's `values:`, then each team above it by folder, innermost first.
4. Its parent agents' `values:`, nearest first. These are the defaults.

**Lookup for `{{team:key}}`:** a fact, then the team's `values:`, then each team above by
folder, then the team's parent teams, nearest first.

A child that sets a value already set by an ancestor replaces it. No `override` keyword,
because values are words, not doctrine. A value may read other values and may use
ordinary `{{Ref}}` refs. Refs resolve where the value is written. Late roots resolve in
the home that reads it.

**Facts.** The compiler supplies these. Setting one in `values:` is `E604`.

| Key | `{{agent:...}}` | `{{team:...}}` |
| --- | --- | --- |
| `key` | Agent name; for a member, the member key | Team name |
| `title` | Head title | Team title |
| `home` | Member's folder from the output root | Team's folder |
| `folder` | Last segment of `home` | Last segment of `home` |
| `members` | none | Member titles in order, joined by `, ` and a final ` and ` |
| `others` | none | The same list without this member. In a team's own file, `E602` |

An agent outside any team has no `home` or `folder`, and reading one is `E602`.

**Errors.**

| Code | When | Must say |
| --- | --- | --- |
| `E601` | A home reads a blank nothing fills, including an empty `members` or `others` | The home, every missing key, and each source line that reads that key, as file and line |
| `E602` | A late root has no owner here | The root, the surface, and why |
| `E603` | Values read each other in a cycle | The full cycle: `a -> b -> a` |
| `E604` | `values:` sets a fact key | The key |
| `E608` | One body sets a value twice, in one `values:` block or across two | The key |

`E601` reports every blank in one error, so one build lists all a new member needs.

**No logic, ever.** There is no conditional, loop, filter, or case change. A sentence for
one team belongs in that team's override.

### 5.2 Teams

A team is a folder of agents with shared doctrine, shared values, and members. Every
level of a repository can be one.

```lark
team_decl: "team" CNAME inheritance? ":" string _NL _INDENT team_body _DEDENT
abstract_team_decl: "abstract" "team" CNAME inheritance? ":" string? _NL _INDENT team_body _DEDENT
team_body: team_item+
?team_item: team_home_stmt
          | role_field
          | values_block
          | budget_block
          | member_decl
          | member_override_decl
          | agent_slot_abstract
          | agent_slot_inherit
          | agent_slot_override
          | override_path
          | agent_slot_field
          | inherit_all
          | drop_item
team_home_stmt: "home" ":" string _NL?
member_decl: "member" CNAME inheritance? ":" string _NL member_body?
member_override_decl: "override" "member" CNAME inheritance? ":" string _NL member_body?
member_body: _INDENT agent_field+ _DEDENT
```

`team_decl` and `abstract_team_decl` join `exportable_declaration`.

Rules:

- A concrete team needs `home:`. An abstract team may not have one. Breaking either is `E606`.
- `home:` is a plain relative POSIX path from the emit output root. `.` means the root. It
  must equal its own normal form, so `./pods`, `pods//growth`, `pods/growth/`, and an empty
  string are out, and it may not be absolute or hold `..`. Breaking this is `E606`.
- The tree comes from the paths. Team A is above team B when A's home is a path prefix
  of B's. No declaration names its parent level.
- A target's tree is the concrete teams in its entrypoint's flow, which is every `.prompt`
  file under the prompt root that no nearer entrypoint claims. A team in another flow can be
  a parent, but not a level of this tree.
- Typed agent fields are not legal on a team. Only `role`, `values`, `budget`, slots, and
  members are. Anything else is `E606`.
- A team and its slots use the same key space as its members. A duplicate is `E606`, and so
  is a second `home:`.
- A team and an agent can't share a name in a flow. That is the shipped duplicate error.

**Team inheritance.** `team B[A]` inherits A's `role`, slots, values, budget, and members.
Members declared on an abstract team are templates, stamped out once per concrete team.

**Overlays.** A `team` body and a `member` body are overlays. They end with an implied
`inherit *`, so everything not named is kept. The render order is `role` first, then the
items written in the body, then the inherited items in the parent's order. So a member's
own sections come before its craft. Writing `inherit *` in the body places it there
instead. `override`, `drop`, and new keys work as in section 4.8. An `agent` body stays
explicit.

```prompt
abstract team CrossFunctionalPod:
    member lead[PodLead]: "lead"
    member qa[PodQa]: "QA"
    member analyst[PodAnalyst]: "analyst"

team FeaturePod[CrossFunctionalPod]: "the feature pod"
    home: "pods/feature"
    values:
        unit: "feature"

team GrowthPod[CrossFunctionalPod]: "the growth pod"
    home: "pods/growth"
    values:
        unit: "bet"
    member marketer[PodMarketer]: "marketer"
```

**Members.** `member key[Role]: "title"` declares one concrete agent.

- Its name is `Team.key`, as in `GrowthPod.qa`. Diagnostics, corpus `agent =` fields, and
  CLI selectors use that name.
- Its folder is the key with `_` changed to `-`, under the team's home.
- `[Role]` may name an abstract agent, a concrete agent, or another member.
- With no `[Role]`, the member needs its own `role` like any concrete agent.
- `override member key[Role]: "title"` in a child team replaces the inherited member whole.
  `drop key: "why"` removes it. Key collisions are `E606`.

**Refs.** `Team.key` resolves wherever a concrete agent ref is legal: route targets, rule
targets, `{{Team.key}}`, and `{{Team.key:title}}`. A visible module with the team's name
is `E270`. A member of an abstract team cannot be referenced, and doing so is `E276`.

**Team file.** A team compiles like a concrete agent with its `role` and slots. `role` is
optional on a team. If nothing renders, the team emits no home file.

A team compiles only its own text. Team doctrine does not flow into member homes. Members
get it by the folder walk. This is the rule that removes double loading.

### 5.3 Who Is Who

`{{team:members}}` and `{{team:others}}` cover sentences. `roster` covers tables.

```lark
readable_roster_block: "roster" CNAME ":" string _NL _INDENT roster_body _DEDENT
roster_body: roster_column+ readable_table_rows_block?
roster_column: CNAME ":" string "=" string _NL?
```

`roster` joins `readable_nonsection_block`.

```prompt
roster calls: "Who makes each call"
    call: "The call" = "{{agent:calls}}"
    who: "Who makes it" = "{{agent:title}}"
    rows:
        owner:
            call: "The goal and the money"
            who: "the owner"
```

Each column is `key: "Header" = "cell template"`. There is one row per direct member of
the team, in declared order. Inside a cell, `{{agent:...}}` means that row's member. A row
is skipped when any of its cells reads an `{{agent:...}}` value that member lacks. A blank
under `{{team:...}}` is `E601` as usual, and so is a roster that skips every member, since
that is a typo. Static `rows:` follow, keyed by column key, and every column must be filled.
A `roster` needs a team. In a member's home it uses the member's team. Elsewhere it is
`E609`. A cell with no `{{agent:...}}`, or an unknown column in `rows:`, is also `E609`.

It renders as the same Markdown table as a `table` block with the same title and columns.

### 5.4 The Team Contract

Every team with at least one member writes `TEAM.contract.json` beside its home file.

```json
{
  "format_version": 1,
  "language_version": "6.0",
  "team": {"key": "GrowthPod", "title": "the growth pod", "home": "pods/growth"},
  "members": [
    {
      "key": "qa",
      "agent": "GrowthPod.qa",
      "title": "QA",
      "home": "pods/growth/qa",
      "parent": "PodQa",
      "sections": ["Your job", "Whom you work with", "How you think"]
    }
  ]
}
```

Member order is declared order, with a team's inherited members first. `sections` lists
the member's top-level headings, so a harness can warn when a launch message names a
section that is gone. This is a machine contract under the same public-surface rule as
`SKILL.contract.json`. Models, accounts, launch messages, and copies stay in the harness.

A team declares no copies. A copy that does the same job runs the same home, and the
launcher tells it which copy it is. Copies that need different text are two members.

### 5.5 Markdown-Backed Declarations

A team can move to Doctrine one file at a time. A hand-written Markdown file may stand in
for a declaration.

```lark
abstract_agent_markdown: "abstract" "agent" CNAME "from" string _NL
workflow_markdown: "workflow" CNAME "from" string _NL
```

```prompt
abstract agent QaCraft from "specialists/qa/AGENTS.md"
workflow EveryAgent from "shared/every-agent.md"

team Root: "the repository"
    home: "."
    every_agent: EveryAgent

abstract agent PodQa[QaCraft]:
    drop working_the_queue: "A pod's QA works the pod's changes, not the labeled queue."
    inherit *
```

The path is relative to the pyproject folder, or with no project config, to the parent of
the prompt root. A missing file is `E652`.

The file reads as keyed structure:

- A first-line `# Heading` is the declaration's title. For an abstract agent it is dropped.
- Text before the first `##` is the `role` of an abstract agent, or the `preamble` of a
  workflow.
- Each `##` is a keyed section, and each `###` a keyed section inside it. Deeper headings
  stay text. Headings inside code fences do not count.
- A section's key is its heading in lower case, with each run of other characters changed
  to `_` and the ends trimmed. Two siblings with one key is `E653`, naming both lines. On an
  abstract agent, a key that is a reserved agent field gets a final `_`, so `## Skills` is
  `skills_` and renders as `## Skills`. A hand-written file keeps its ordinary headings.
- Section text is verbatim, and `{{` stays literal. Links are the one exception below.
- A line starting with `@` that would be a runtime import is `E654`, because its path
  would break once inlined. Declare that file too and compose it.

**Links follow the text.** The text moves into homes in other folders, so a relative link
must keep pointing at the same file. Each destination in `[text](dest)`, `![alt](dest)`, and
a reference definition `[id]: dest` is rewritten as the path from the emitted file's folder
to the file `dest` names from the Markdown file's folder. A `#anchor` stays on the end. A
destination with a URL scheme, or starting with `/`, `#`, or `~`, is left alone, and so is
anything in a code span or code fence. Nothing checks that the linked file exists, because
`--rev` doesn't extract it. The path is worked out against the target's `output_dir`, so
`--out` gives the same bytes. The rewrite runs in the final pass of section 5.1, because one
file can land in homes in different folders. A compile with no emit target leaves links as
written.

`drop`, `override`, and dotted paths work on these keys, and `{{Decl:key.title}}` works on a
workflow's, as it does on any workflow. A `drop` naming a heading that is gone is `E610`. The file's content feeds the declaration's source
hash, and `--rev` extracts it too. The text lands in homes, so it counts in their load at
its real size.

This also keeps a shared file standing alone for readers outside the repository: the
Markdown stays the source and is inlined, so the two can't drift.

## 6. WS3: Homes And Load (#92, #93, #95, #97)

### 6.1 Runtimes

An emit target may name its runtimes.

```toml
[[tool.doctrine.emit.targets]]
name = "homes"
entrypoint = "prompts/AGENTS.prompt"
output_dir = "."
runtimes = ["claude", "codex"]
```

| Runtime | File | Size unit | Default limit |
| --- | --- | --- | --- |
| `claude` | `CLAUDE.md` | UTF-16 code units (JavaScript `.length`) | 150,000 |
| `codex` | `AGENTS.md` | UTF-8 bytes | 32,768 |

Without `runtimes`, a target emits `AGENTS.md` only, as today. An unknown runtime is `E632`.

Project settings are optional:

```toml
[tool.doctrine.runtimes.claude]
limit = 150000
warn_at = 0.95
over = "error"
external = [
  { path = "~/.claude/CLAUDE.md", reserve = 14000 },
  { path = "shared/hand-written.md" },
]
```

- `limit`: positive integer. For `codex`, with no `limit` set, Doctrine reads
  `project_doc_max_bytes` from `.codex/config.toml` in the pyproject folder, then falls
  back to 32,768.
- `warn_at`: greater than 0 and at most 1. Default `0.95`.
- `over`: `error` or `warn`. Default `error`.
- `external`: files Doctrine doesn't emit that this runtime loads for every home in the
  target. `path` is `~`-relative or relative to the pyproject folder. A present file counts
  at its real size. An absent file counts at `reserve`. An absent file with no `reserve`
  is `E633`.

Bad settings are `E632`. The Codex global file is not charged against
`project_doc_max_bytes`, so it should not be listed for `codex`. The docs say so.

### 6.2 The Home Tree

For a target with teams, each home lands at `<output_dir>/<home>/`:

- `AGENTS.md`, with `CLAUDE.md` as a relative symlink to it when both runtimes are named,
  or the one file when only one is;
- `DETAILS.md`, when that home owns details;
- `TEAM.contract.json`, for a team with members.

Two homes with one path is `E607`, naming both owners. This covers a member folder that
collides with a team home. Two targets with teams that share an `output_dir` is also `E607`,
naming both targets. Concrete agents outside a team emit as they do today.

No `@` line or import is ever written. Shared text reaches a home by inheritance or
composition, so it is inlined.

**Generated header.** Each team-tree home file starts with this line, then a blank line:

```markdown
<!-- doctrine sha256=9f2c41d07ab3 source=prompts/pods/growth.prompt. Do not edit. Run: doctrine where "<words>" -->
```

`sha256` is the first 12 hex digits of the hash of the file's bytes after the header.
`source` is the file of the team or member, relative to the pyproject folder. Claude Code
strips the comment before injecting the file. Companions (`DETAILS.md`, `_details/*.md`)
carry the same header, with their owner's source. `doctrine build` puts this header on every
Markdown file it writes, a plain agent's included, so the guard covers them all. The
`python -m doctrine.emit_*` commands write what they always did.

The header makes each file its own receipt, so the guard below works the same whether
compiled files are committed or built at launch.

**Hand-edit guard.** Before it writes anything, the build reads the header of every
Markdown file it would overwrite or remove. So `E634` leaves the tree as it was.

| The file on disk | What happens |
| --- | --- |
| Absent | Write |
| Hash matches its bytes | Write. It is a clean earlier build |
| Hash doesn't match its bytes | `E634`: it was edited by hand |
| No Doctrine header | `E634`: it was written by hand |

`E634` names the file. For an edited home file the build would overwrite, it also names each
top-level section that differs from the fresh build, matched by title and then by order among
repeats, with that section's origin and site. A section the fresh build no longer has prints
`no longer in source`. A companion names only the file and its `source`. It says to move the
edit there. `--force` overwrites or removes it. Nothing else does. A hand edit is never
silently lost.

`TEAM.contract.json` and `HOMES.contract.json` are machine files. They carry no header and
no guard, because no lesson lives in them, and `--check` shows them as `stale`.

`CLAUDE.md` follows the same table. A link to `AGENTS.md` is left as it is. A real file
goes through the guard and then becomes the link. Any other link is `E634`.

**The tree record.** A whole-tree build also writes `HOMES.contract.json` in the output root:

```json
{
  "format_version": 1,
  "files": ["AGENTS.md", "CLAUDE.md", "pods/growth/AGENTS.md", "pods/growth/TEAM.contract.json"]
}
```

`files` is every path the build emitted, sorted, without the record itself. A whole-tree
build is `doctrine build .` or `doctrine build` with no selector. No other build reads or
writes the record. A missing record means nothing is obsolete, and so does one that won't
parse, because two commits can leave it in a merge conflict and the build is what repairs it.

A path in the record that this build doesn't emit is **obsolete**: a removed member, a
moved team, or a team that no longer renders any text. Its text would otherwise keep
loading, because the runtimes read whatever is in the folder. A whole-tree build removes
obsolete files after the guard passes, and leaves their folders alone. Scanning the tree
instead would be too slow for a commit tool to run in a large repository.

**Atomic writes.** Write a temp file in the same folder, created the ordinary way so the
user's umask sets its mode, then `os.replace`, so nobody reads half a file. Skip the write when the bytes already match. Builds of one source write
identical bytes, so 16 launches at once are safe. Builds from different sources, such as a
launch from `HEAD` beside an author's working tree, can leave one home with files from both
until the next build, and `--check` shows it. There is no lock, because a launch must never
wait on one.

### 6.3 `details`

```lark
readable_details_block: "details" CNAME ":" string _NL _INDENT shared_readable_body _DEDENT
readable_bare_details_block: "details" ":" _NL _INDENT shared_readable_body _DEDENT
override_readable_details_block: "override" "details" CNAME ":" string? _NL _INDENT shared_readable_body _DEDENT
```

`details` joins the readable block family, and `paragraph_body` per section 4.6. Text in
it is left out of the always-on file and sent to a companion, under the same headings.
It imposes no form. It is a route for text, not a shape for teaching.

**Where the text lands.** The owner is the declaration that lexically holds the block.

| Owner | Companion |
| --- | --- |
| A team or member | `DETAILS.md` in that home |
| A concrete top-level agent | `DETAILS.md` beside its emitted file |
| Anything else: abstract agent, abstract team, `workflow`, `document` | `_details/<owner-slug>.md` under the output root, written once |

`<owner-slug>` is the declaration name in kebab case, with the module path joined by `-`
when the declaration is imported.

**Pointer.** A home gets one pointer line at its end, not one per section, to save
always-on text. It lists each companion that home's text points into, in first-use order:

```markdown
Fuller cases, under the same headings: [DETAILS.md](DETAILS.md), [_details/waiter.md](../../_details/waiter.md).
```

Links are relative to the home file. A home with no details gets no line.

**Companion layout.** A `DETAILS.md` repeats its home's headings at the same depth for each
section that has details, in home order, and nothing else. A `_details/` file follows its
owner instead, because homes that share it can reorder or retitle those sections. Its bytes
depend on the owner alone: an agent's slots are `##`, a workflow's or document's title is
`##` with its sections under it, in the owner's written order, each only if it holds
details.

In both, a named block gets a heading one level deeper, and text at the top of a slot sits
under the slot's heading. Anchors are GitHub slugs of heading text, with `-1`, `-2` added to
repeats in file order. The file has no preamble of its own.

**Shared details are shared words.** Text in a `_details/` file serves every home that
points at it, so it may not read `{{agent:...}}` or `{{team:...}}`. That includes its
section title. Doing so is `E621`, with the hint: "Move this into the team or member, or
write it in words that fit every reader."

**Elsewhere.** `details` is legal in an agent, team, member, workflow, or document that a
home reads. In a skill package, an emitted document, a `skill`, an `input` or `output` body,
or a document used as an output's `structure:` it is `E620`, and so is any `details` that
reaches `python -m doctrine.emit_docs`, which writes no companions. Use `doctrine build`.

```prompt
abstract agent Waiter:
    when_to_wait: "When to wait"
        "Wait only when what you wait for could change what you'd do."
        details older_cases: "Older cases"
            "On October 13 a watcher moved a member mid test pass."
```

gives a member this in its home:

```markdown
## When to wait

Wait only when what you wait for could change what you'd do.

Fuller cases, under the same headings: [_details/waiter.md](../../_details/waiter.md).
```

and `_details/waiter.md`:

```markdown
## When to wait

### Older cases

On October 13 a watcher moved a member mid test pass.
```

### 6.4 Load And Budgets

**The load of a home on a runtime** is, in order: the runtime's externals, then that
runtime's file at each level from the top of the tree down to the home. `details` never
count. Sizes use the runtime's unit on the emitted file.

**Budgets** in source:

```lark
budget_block: "budget" ":" _NL _INDENT budget_item+ _DEDENT
budget_item: CNAME ":" SIGNED_NUMBER _NL?
```

`budget_block` joins `agent_field` and `team_item`. `budget` joins the reserved keys. A key
is a runtime name.

The limit for a home follows the same order as values: its own `budget:`, its team's, teams
above by folder, its parents' as defaults, nearest first, then the runtime's `limit`. A budget
that is not a positive integer, exceeds the runtime's `limit`, or names an unknown runtime is
`E631`.

`doctrine check` judges budgets. At or past `warn_at` of the limit is `W306`. Past the
limit is `E630`, or `W306` when the runtime sets `over = "warn"`. `doctrine build` never
fails on a budget. It prints the same finding as `W306` for the homes it selected and writes
the file, because a team that can't start is worse than one over budget. A bad budget, a bad
runtime setting, or a missing external is the same: `build` prints the error to stderr, skips
the budget report, and keeps going. The failure belongs on the author's change.

`E630` reads:

```text
E630 compile error: Over load budget

Detail:
- pods/growth/qa loads 151,200 of 150,000 characters on claude.
- Biggest parts:
  - PodQa: 31,300
  - GrowthPod: 14,100
  - And 7 smaller parts: 12,000
```

Parts are home-map origins, biggest first, top five, then the `cargo bloat` style last row.

### 6.5 The `doctrine` Command

`[project.scripts]` gains `doctrine = "doctrine.cli:main"`. The `python -m doctrine.emit_*`
commands stay. `doctrine/cli.py` holds argument parsing only.

Every command takes `--pyproject PATH` and `--target NAME`. With one target that has
teams, `--target` may be left out. Otherwise leaving it out is exit 2.

| Exit | Meaning |
| --- | --- |
| 0 | Done. No findings |
| 1 | Findings: a compile error, over budget, stale files, or `--strict` warnings |
| 2 | The tool failed or the usage was wrong |

Diagnostics go to stderr in the shipped format, so a launcher can show them as they are.

A **selector** is a home path, an agent name, or a team name. A home path also selects every
home under it, and a team name means that team's home path. No selector means all. A selector
that matches nothing is `E640`.

**`build` makes files. `check` judges them.** That split is the rule that keeps a launch
from failing on someone else's rule or budget.

**Source flags.** `build`, `check`, `diff`, and `load` compile from the working tree unless
told otherwise:

- `--rev REV` compiles from that git revision. It extracts only what the result depends on,
  with `git archive`, into a temp folder, because a repository can be far larger than its
  prompts: the pyproject, `.codex/config.toml` beside it, the target's prompt roots, every
  `from` file, and every `external` path relative to the pyproject folder. An extra path the
  revision doesn't hold is left out, so it counts as absent. A `~` path reads this machine.
  A bad revision is `E641`.
- `--with PATH` (repeatable, needs `--rev`) overlays that working-tree file on the
  revision. So one author's change compiles without another session's unfinished edits.

**`doctrine build [SELECTOR...] [--out DIR] [--check] [--force] [--rev REV] [--with PATH]`**

Compiles the selected homes and the levels they load, and writes only the selected homes'
folders, plus any `_details/` file they point to when the build selects the whole tree. It
evaluates no `rule` declarations and fails on no budget. An error in a home, team, or plan
that wasn't selected can't stop it, and neither can bad settings or a file someone else wrote.
A level that won't compile prints its error to stderr and is left alone. Shared companions
are written only by a whole-tree build and aren't compared on a selected one. `--target` looks only at targets sharing that target's `output_dir`.

- The levels above the selected homes are compared, never written. A level that differs, or a
  Doctrine file this build no longer emits, prints
  `W307 stale level` with its path. A selected home is never a stale level, and a hand-written
  file with no Doctrine header isn't one either. Those files are shared by every session in a
  checkout, so one launch must not rewrite them.
- `doctrine build .` selects everything, so it writes everything and removes obsolete files
  (section 6.2).
- `--out DIR` writes under `DIR` instead of the target's `output_dir`, with its own record.
- `--check` writes nothing. It prints each path as `stale`, `edited`, `missing`, or `obsolete`,
  and exits 1 if any is. Output is deterministic, so a clean exit means the files match the
  source. `obsolete` needs the whole tree, so only a whole-tree `--check` prints it.
- With `--json` it prints `{"format_version": 1, "written": [...], "unchanged": [...],
  "removed": [...], "stale_levels": [...]}`. With `--check --json` it prints only
  `{"format_version": 1, "paths": [{"path": "...", "state": "stale"}]}`.

Prints `built <N> homes, <M> files changed` on success, with `home` and `file` singular at
1. A symlink, a contract, and a removed file each count as a file.

**`doctrine check [--strict] [--json] [--rev REV] [--with PATH]`** compiles every home,
writes nothing, and checks all rules, budgets, and warnings. Warnings print to stderr and
don't fail unless `--strict`. It prints `ok: <N> homes checked` when it exits 0. A commit
tool runs this, so the failure lands on the author. With `--json` it prints this instead,
where `text` is what the plain form prints for that finding:

```json
{"format_version": 1, "ok": false, "homes": 3,
 "errors": [{"code": "E630", "text": "..."}],
 "warnings": [{"code": "W306", "text": "..."}]}
```

**`doctrine where "<words>" [--home PATH] [--json]`** finds the source of a sentence an
agent read. It matches against each home's compiled always-on and details text, ignoring
case and whitespace, and prints each distinct origin once:

```text
PodQa.whom_you_work_with  prompts/roles/qa.prompt:12
  reaches 3 homes: pods/growth/qa, pods/feature/qa, pods/product/qa
```

A home is reached when the matching text is in its load, so a sentence at a level counts
every home under it. A text set by a value also prints the value's site. No match exits 1.

**`doctrine load [SELECTOR...] [--runtime NAME] [--json]`** prints load by headroom:

```text
Home              Runtime  Load     Limit    Headroom
pods/growth/qa    claude   145,400  150,000  4,600
pods/feature/qa   claude   142,200  150,000  7,800
```

Each column is padded to its widest cell plus two spaces, numbers use thousands commas,
rows sort by headroom, then home, then runtime, and headroom may be negative. Every home is a
row, a team's included, because a session can start in any of them.

With exactly one home selected it prints one block per runtime in the target's order, then
the drops once:

```text
pods/growth/qa on claude: 145,400 of 150,000 characters, 4,600 left

Files:
  ~/.claude/CLAUDE.md       13,600  external
  AGENTS.md                 92,100
  pods/growth/qa/AGENTS.md  39,700

Biggest parts:
  PodQa: 31,300
  GrowthPod: 14,100
  And 7 smaller parts: 12,000

Dropped:
  working_the_queue from PodQa: A pod's QA works the pod's changes, not the labeled queue.
```

The unit is `characters` for `claude` and `bytes` for `codex`. Past the limit the line ends
`1,200 over`. File columns follow the table's padding, and a file with no reserve-or-external
kind has no third cell. An absent external prints `reserved`. `Biggest parts:` follows the
`E630` rule. Blocks are separated by one blank line, and an empty block is omitted.

`--full` instead prints everything that home loads, in order, each file under a
`===== <path> (<size>) =====` line.

JSON shape:

```json
{
  "format_version": 1,
  "homes": [{
    "home": "pods/growth/qa",
    "agent": "GrowthPod.qa",
    "runtimes": {
      "claude": {
        "unit": "utf16",
        "total": 145400,
        "limit": 150000,
        "headroom": 4600,
        "files": [{"path": "~/.claude/CLAUDE.md", "size": 13600, "kind": "external"}],
        "parts": [{"origin": "PodQa", "size": 31300}],
        "details_size": 11000
      }
    },
    "drops": [{"path": ["working_the_queue"], "origin": "PodQa", "reason": "..."}]
  }]
}
```

**`doctrine diff`** and **`doctrine sources`** are in sections 8 and 9.
**`doctrine import`** is in section 11.

`[project.scripts]` carries both `doctrine` and `doctrine-agents`, pointing at the same
`main`, so `uvx doctrine-agents==X.Y.Z build .` runs on any machine with no sibling checkout.

## 7. Shared Internal Record: The Home Map

The home map is an in-memory record built for every compiled home. It is never written to
disk as its own file. Every report reads it, so there is one source of truth for "what
landed where, and from whom". A linker map file is the model.

```python
@dataclass(frozen=True, slots=True)
class MapEntry:
    path: tuple[str, ...]   # slot key, then nested keys down to depth 2
    title: str | None
    origin: str             # declaration that authored this text, as "Decl" or "Team.key"
    origin_path: tuple[str, ...]  # the same text's path inside `origin`, () at its top
    site: str               # "prompts/roles/qa.prompt:12"
    always_on: bool         # False for details
    text_hash: str          # sha256 of the entry's rendered text
    size_utf16: int
    size_bytes: int

@dataclass(frozen=True, slots=True)
class DropRecord:
    path: tuple[str, ...]
    origin: str             # declaration that wrote the drop
    reason: str

@dataclass(frozen=True, slots=True)
class HomeMap:
    home: str
    agent: str
    entries: tuple[MapEntry, ...]
    drops: tuple[DropRecord, ...]
    wildcard_keys: frozenset[tuple[str, ...]]   # paths that arrived through `inherit *`
    deps: frozenset[str]    # every declaration this home's source reaches
```

`entries` partition a home's always-on text and its details. `role` is an entry with the path
`("role",)`. An entry holds its own rendered text and leaves out its keyed children down to
depth 2, each of which is an entry of its own, and anything deeper rolls up into its depth-2
ancestor. Its sizes and `text_hash` cover that text, with no surrounding blank lines. So
origin totals never count a line twice, and the generated header, pointer line, and joining
blank lines belong to no entry.

`origin` is the declaration whose source wrote the text, not the one that inherited it.
`deps` comes from a dataclass-reflection walk over the model that collects every name ref,
addressable ref, and `{{Ref}}` in strings, closed over parents, slots, `use`, and values.
It does not need per-kind code.

A declaration's **source hash** is sha256 over its model, with all `source_span` values
removed, via one dataclass-reflection walk. Moving a declaration within a file does not
change its hash.

## 8. WS4: Reach (#98, #99, #101 Report)

### 8.1 Rule Scopes And Assertions

New scope predicates:

```lark
team_predicate: "team" ":" (name_ref | "*") _NL
member_predicate: "member" ":" CNAME _NL
home_predicate: "home" ":" string _NL
```

- `team: GrowthPod` matches that team's members. `team: *` matches every member of any team.
- `member: qa` matches any team's member with that key.
- `home: "pods/**"` matches a home path. `*` stays in one segment, and `**` crosses segments.
- Predicates still combine with OR, as shipped.
- An unknown team is `RULE001`.

New assertions:

```lark
requires_load_assertion: "requires" "load" name_ref _NL
forbids_load_assertion: "forbids" "load" name_ref _NL
```

They judge what lands, by any path. `requires load X` holds when X is an `origin` of an
always-on entry in the home or in any level above it, on any runtime. `forbids load X` is
the reverse. An unknown target is `RULE002`. A failed `requires load` is `RULE006`. A failed
`forbids load` is `RULE007`.

`RULE007` prints the path it arrived by, one shortest `deps` chain:

```text
RULE007 Forbids load

Detail:
- GrowthPod.qa must not load SpecialistsOnlyLesson.
- It arrives by: GrowthPod.qa -> PodQa -> QaCraft -> SpecialistsOnlyLesson
```

Load rules need compiled homes, so `doctrine check` evaluates them. `emit_docs` does too,
for the homes it compiles. The shipped assertions keep running at compile, except that
`doctrine build` evaluates no rule at all (section 6.5).

### 8.2 `doctrine diff`

`doctrine diff [SELECTOR...] [--base REV | --base-tree DIR] [--with PATH] [--json]`

Default base is `HEAD`. It compiles the base with the same extraction as `build --rev`, or
reads `--base-tree`, compiles the new side, and compares home maps and source hashes. The
new side is the working tree, or with `--with`, the base plus only those files. So a commit
tool in a shared checkout asks exactly what one author's files change.
Compile errors in the working tree are exit 1. A base that fails to compile prints a
warning line and compares nothing from that base, with exit 2.

Text output, in this order, each block omitted when empty:

```text
2 declarations changed. 3 homes changed.

PodQa (prompts/roles/qa.prompt) reaches 3 homes, +120 characters each:
  pods/growth/qa, pods/feature/qa, pods/product/qa

GrowthPod (prompts/pods/growth.prompt) reaches 1 home, +40 characters:
  pods/growth/qa

Owned declarations changed:
  EveryAgentRules, owned by Owner

New sections that arrive through inherit *:
  QaCraft.regression_watch reaches pods/growth/qa, pods/feature/qa

Over budget:
  pods/growth/qa on claude: 150,120 of 150,000
```

Rules:

- A home "changed" when any file in its load differs from the base, or its own details do.
  So a change at a level changes every home under it. The size is the change in the home's
  whole load.
- A declaration "reaches" a home when its source hash changed and it is in the `deps` of a
  level in that home's load whose file differs from the base, or in the home's own `deps`
  when only its details differ.
- When homes differ in size, print the range: `+120 to +612 characters`.
- Characters are UTF-16 units of always-on text. `details` changes print separately as
  `(details +300)`.
- Lines sort by declaration name, then home path.
- New sections: an entry present now and absent in the base, whose path is in
  `wildcard_keys`.

JSON shape:

```json
{
  "format_version": 1,
  "base": "HEAD",
  "changed_declarations": [{
    "name": "PodQa",
    "kind": "abstract agent",
    "site": "prompts/roles/qa.prompt:3",
    "owners": [],
    "homes": ["pods/growth/qa"],
    "delta": {"always_on": 120, "details": 0}
  }],
  "homes": [{
    "home": "pods/growth/qa",
    "delta": {"always_on": 120, "details": 0},
    "entries": [{"path": ["whom_you_work_with"], "status": "changed", "origin": "PodQa", "delta": 120}]
  }],
  "owned": [{"name": "EveryAgentRules", "owners": ["Owner"]}],
  "new_sections": [{"origin": "QaCraft", "path": ["regression_watch"], "homes": ["pods/growth/qa"]}],
  "over_budget": [{"home": "pods/growth/qa", "runtime": "claude", "total": 150120, "limit": 150000}],
  "outputs": ["pods/growth/qa/AGENTS.md", "pods/growth/qa/DETAILS.md"]
}
```

`status` is `added`, `removed`, or `changed`. `outputs` lists every emitted path added,
changed, or removed, so a commit that names exact paths can stage them. It holds only files
whose bytes differ, so a home changed by a level above it adds no path, and it holds
`HOMES.contract.json` when the list of files changed. `doctrine diff` exits 0 even when things
changed. A commit tool reads the JSON and decides. The compiler enforces nothing about
ownership.

### 8.3 Warnings

`doctrine check` runs these. They live in `docs/WARNINGS.md` as a new "Project Warnings"
section. A project turns one off with:

```toml
[tool.doctrine.check]
disable = ["W301"]
```

| Code | Key | Meaning |
| --- | --- | --- |
| `W301` | near_copy | Two source paragraphs are copies or differ by a few words |
| `W302` | double_load | One declaration's text reaches a home from two files in its load |
| `W303` | message_without_reader | A `Message` output no `inputs:` reads (section 10) |
| `W304` | unused_value | A `values:` key no text in any home reads |
| `W305` | unused_quote | A `quote` nothing cites |
| `W306` | near_budget | A home is at or past `warn_at`, or over budget during `build` |
| `W307` | stale_level | A level a selected home loads differs from this build |

**`W301` method.** Fixed values, no config.

- Paragraphs come from source, not output, so one shared section compiled into 56 homes is
  not a copy. A paragraph is one authored string, split on blank lines.
- Tokens are `\w+` runs after casefolding, with Markdown emphasis removed. Paragraphs under
  12 tokens are skipped.
- Candidates share at least three 4-token shingles, found through an inverted index.
- A candidate pair is compared with `difflib.SequenceMatcher(None, a, b, autojunk=False)`
  on token lists. A ratio of 0.85 or more is a finding: `copy` at 1.0, `near` below it.
- Only pairs in different declarations count. A parent and child do count, because an
  override that changes two words is a value in disguise.
- Findings group by declaration pair, with the first three examples shown and the total
  count. Each `near` example shows the differing words. In `check --json`, a `W301` warning
  also carries `examples`, a list of `{"sites": [...], "words": [...]}` with every pair.

```text
W301 near copy: GrowthQa and FeatureQa share 12 paragraphs that differ by a few words.
- prompts/growth/qa.prompt:14 and prompts/feature/qa.prompt:14: bet / feature
Hint: Share the paragraph and put the different words in `values:`.
```

**`W302` method.** For each home and runtime, group always-on entries in the whole load by
`origin` and `origin_path`. Those don't depend on the slot that placed the text, so one
workflow bound under two keys still groups. Two files holding one group is a finding,
naming both files.

### 8.4 The Agent Linter's Change Mode

`agent-linter` gains a change mode in its skill source.

- Input: `doctrine diff --json`, plus each changed declaration's source and the compiled
  home of one reached agent.
- Scope: only the changed declarations, read against the rest of that home.
- It asks whether the change restates something the home already says, adds a rule where
  a judgment already lives, or contradicts a parent.
- It stays judgment-first. It is not a compiler check and adds no compiler code.

New findings in `finding_catalog.prompt`:

| Code | Name | Fix |
| --- | --- | --- |
| `AL231` | Lesson Restated Beside Old Text | Change the text that already makes the call |
| `AL232` | Rule Added Where A Judgment Lives | Fold it into the judgment, or show why it needs a rule |
| `AL233` | Change Contradicts A Parent | Change the parent, or say the departure plainly |

## 9. WS5: Provenance (#100, #101)

```lark
person_decl: "person" CNAME ":" string _NL (_INDENT person_body _DEDENT)?
person_body: "owns" ":" _NL _INDENT person_owned_item+ _DEDENT
person_owned_item: (name_ref | string) _NL?
quote_decl: "quote" CNAME ":" string _NL _INDENT quote_field+ _DEDENT
?quote_field: quote_by | quote_on | quote_to | quote_about | quote_source
quote_by: "by" ":" name_ref _NL?
quote_on: "on" ":" string _NL?
quote_to: "to" ":" string _NL?
quote_about: "about" ":" string _NL?
quote_source: "source" ":" string _NL?
```

Both join `exportable_declaration`.

**`person`** names someone. `owns:` lists top-level declarations by ref, or source files
by quoted glob relative to the pyproject folder. Owning a team covers its members. Owners
add up, so one thing can have two owners. There is no precedence. Ownership does not
pass to children, because a child is a different declaration. `doctrine diff` reports a
change to an owned declaration, and any change to a `person` declaration, since that
changes who owns what. A ref that doesn't resolve is `E651`, as is a glob matching no file.

The list is central on purpose. An agent editing a declaration can't quietly delete an
attribute on it, because the attribute isn't there.

**`quote`** records someone's words. The header string is the words.

- `by:` is required and must resolve to a `person`.
- `on:` is required and must be an ISO date, `YYYY-MM-DD`.
- `to:` and `about:` are optional, and both may be set.
- `source:` is optional. A harness link such as a session id. Doctrine only stores it.
- A missing or bad field is `E650`.

`{{Name}}` in prose renders one form:

```text
(Amir, November 5, 2026, to the growth pod's lead: "There needs to be a shared contract")
```

The form is `(<person title>, <Month D, YYYY>[, to <to>][, about <about>]: "<words>")`. A
bare `Name` line in a section body renders the same text. `quote` joins the readable
declaration kinds. Its words keep their own punctuation. Quotes may use late roots, and
they resolve in the home that cites them.

**Inline form.** A named quote is for words cited in several places. Most quotes sit in one
sentence, and asking for a declaration elsewhere would push authors to drop the attribution.
So a quote can be written where it stands, in nearly the words it renders as:

```prompt
"Every pod's code goes out through one contract {{Amir, 2026-11-05, to the growth pod's lead, source 53dcb019: "There needs to be a shared contract"}}."
```

The form is `{{<PersonRef>, <YYYY-MM-DD>[, to <text>][, about <text>][, source <text>]: "<words>"}}`.
`to`, `about`, and `source` may come in any order. A comma after the first name marks an
inline quote, since no other interpolation holds a comma. It renders exactly as a named
quote does. `{`, `}`, or a bad field inside one is `E650`. Inline quotes appear in
`doctrine sources` with their site as their key. Inside a one-line string the inner quotes
need escaping, so authors use `"""` strings, which take them as written.

**`doctrine sources [--person NAME] [--json]`** lists every quote by person, then date.

```text
Amir: 12 quotes, 1 with no source

2026-11-05  ContractAllPods  prompts/shared/contract.prompt:4
  to the growth pod's lead
  source: session:abc123
  cited in 3 declarations, reaches 56 homes

No source:
  OneAdRemark  prompts/shared/ads.prompt:9
```

JSON keys: `format_version`, `people[]` with `key`, `title`, `quotes[]` holding `key`,
`on`, `to`, `about`, `source`, `site`, `cited_in`, `homes`. A harness checks `source` itself.
Doctrine ships no hook, because the JSON is the hook. Exit is 0 unless compile fails.

## 10. WS6: Messages (#102)

Doctrine's rule stays: the emitted contract surface is `output`, and there is no packet
primitive. Doctrine does not carry a message. It keeps what two homes say about one in
step.

Two additions:

1. A new built-in output target, `Message`. It takes one required key, `to:`, an agent ref,
   a team ref, or a string. A `Message` output has no `shape` or `requirement`, because a
   message is prose written to be acted on cold, not a form. Writing one is `E660`.

```prompt
output CodeReady: "Code is ready"
    target: Message
        to: CoreDev.lead
    "One message to the core dev pod's lead when a team's code is ready."
    bullets carries: "It carries"
        "The pull requests that go out together"
        "What users get from them"
        "What they need to go live"
        "Anything that can't wait"
```

2. An `inputs:` entry may name an `output` whose target is `Message`. Today that is `E301`.
   Any other target stays `E301`.

Both homes render the same body under the declaration's title. Only one line differs.

The sender, in its outputs section:

```markdown
### Code is ready

Send this to the core dev pod's lead.

One message to the core dev pod's lead when a team's code is ready.

#### It carries

- The pull requests that go out together
- What users get from them
- What they need to go live
- Anything that can't wait
```

The receiver, in its inputs section, has the line `You receive this message.` in place of
the `Send this to ...` line. Adding a line to `carries` changes both homes.

`to:` renders as: a member's `<team title>'s <member title>`, an agent's or team's title, or
the string as written.

`W303` fires when a `Message` output's `to:` is an agent or team ref and no agent in that
scope lists it in `inputs:`. A string `to:` has no check, which covers a note to one's next
session. One agent may list one `Message` in both `outputs:` and `inputs:`.

`AGENT_IO_DESIGN_NOTES.md` keeps "a packet primitive" as a non-goal and gains this line:
"`Message` is an ordinary `output`. Doctrine renders it on both sides and carries nothing
at run time."


## 11. WS7: `doctrine import`

`doctrine import PATH --name DECL --kind workflow|agent [--check]`

It reads a Markdown file with the reader from section 5.5 and prints `.prompt` source to
stdout. This is the lossless first step of a port: file by file, before any refactor.

- A `##` heading becomes `key: "Title"`, and a `###` inside it becomes `key: "Title"` one
  level deeper.
- A paragraph opening with a bold run and followed by text, `**Lead-in.** text`, becomes
  `paragraph key: "Lead-in."` with the key slugged from the lead-in.
- Every other run of text becomes one string, with blank lines kept. Before the first keyed
  item in its section it is a bare string, because the parser requires prose first. After
  one it is an untitled `paragraph text_<N>:`, with `N` counting those in the section from 1.
- A string is `"..."` when it fits on one line and holds no `"` or `\`. Otherwise it is
  `"""..."""`, with later lines at column 0, because a triple-quoted string keeps them as written.
- A repeated key in one section gets `_2`, `_3`, in order. A key that is a keyword in that
  position gets a final `_`, as Python does, so `## Details` prints `details_: "Details"`.
- Text before the first `##` becomes `role:` for `--kind agent`, or loose prose for
  `--kind workflow`.
- Link destinations stay as written. Text in `.prompt` source doesn't follow its file, so
  the port docs say to turn relative links into paths from the repository root first.

`--check` compiles the printed source in memory and compares its render with the input,
ignoring the first-line `# Heading` and trailing whitespace. A difference prints its first
line and exits 1. Lossless means this check passes.

## 12. WS8: Doctrine Learn Teaches Results

Today `doctrine-learn` teaches the language. It must teach how to get the best results
with the language, and the language as the means. This workstream can stand as its own
issue.

**R1. Mission.** The `SKILL.prompt` description and opening say so: teach an author how to
get agents that stay small, aligned, and free of drift, and then the language that does it.

**R2. First move.** It asks what result the author wants or what went wrong, before it asks
which surface they're writing. `references/getting-good-results.md` loads first. The
language references follow.

**R3. New reference `references/getting-good-results.md`**, from a new `document
GettingGoodResults`. It is written as intuitions, not a rule list, and is under about 250
lines. It must teach all of this, each point with one real corpus example:

| Topic | What it teaches |
| --- | --- |
| What Doctrine is for | Agents do well in cases nobody wrote down because they understand what matters. Doctrine doesn't write that judgment. It keeps it in one place and gets it to the right agents |
| Which failure, which tool | A table: copied role → shared role plus values. Lesson reached the wrong agents → the narrowest level, plus `requires load` and `forbids load`. Home too long → `details` and budgets. Two sides disagree → `Message`. Claim with no source → `quote`. Base drifts from a member → `drop`, or a split into craft and job |
| One fix lands once | Share by role and values. Know when not to: a sentence for one team belongs in that team's override, and a role with many blanks is two roles |
| Where a lesson lands | Run `doctrine where`, find the text that already makes the call, and change it. A new paragraph beside the old one is how drift starts. `doctrine diff` then shows the reach |
| Thin always-on text | Keep the idea and the one case that shows where it turns. Send the rest to `details`. Leave out what an agent sees by looking |
| Prose or types | Judgment stays prose. Types carry exact truth. Don't turn teaching into a fill-in form |
| Patterns that go bad | Values used as templating, deep inheritance, piles of `drop`, restating what the harness owns |
| Porting order | `from` a Markdown file, then `doctrine import`, then roles, values, rules, and budgets. One file at a time. Links follow a `from` file on their own, but not imported text, so write them from the repository root before `import` |
| The loop | Edit, `doctrine diff`, `doctrine check`, the linter's change mode, then a fresh agent on a case the file never mentions, including one where the obvious move is wrong |

**R4. Look outward.** A section titled "Read Current Practice" tells the author this field
moves fast, this file will age, and to read current guidance before authoring:

- the host's own authoring skills when it has them, such as `agents-md-authoring`,
  `prompt-authoring`, `skill-authoring`, and `intuition-building`;
- the runtime makers' current docs: Claude Code's memory docs, the Agent Skills spec at
  agentskills.io, and the AGENTS.md guidance at agents.md and in OpenAI's Codex docs.

It says to prefer those over this file when they disagree on how to write for a runtime,
and to prefer this file and the shipped corpus on what Doctrine does.

**R5. Every new construct is taught.** The language references gain every WS1 to WS6
surface with a corpus citation: `agents_and_workflows`, `documents_and_tables`, `rules`,
`emit_targets`, `verify_and_ship`, `imports_and_refs`, `outputs_and_schemas`,
`language_overview`, `examples_ladder`, plus a new `teams_and_homes` reference.

**R6. Capstone.** Example 193 is a small generic team that uses the whole method. The
results reference cites it.

**R7. Proof.** `make skills` and `make verify-skill-examples` pass. Then one back-test: a
Sonnet helper gets only the emitted skill and three cases (two near-copied roles, a lesson
to add, a home over budget). It should reach for the right tools. The designer reads the
answers.

## 13. Examples

These are written up front, as real files on this branch, and they are the executable
spec. `prompts/`, `cases.toml`, and every expected line come from the designer. An
implementer makes them pass and may not edit them. A case that seems wrong is a stop and
report, not an edit. Numbers continue the corpus.

| # | Example | Teaches | WS |
| --- | --- | --- | --- |
| 165 | `every_string_a_paragraph` | One string, one paragraph; no `_section_`; `E134`, `E605` | 1 |
| 166 | `paragraph_blocks` | `paragraph`, titled and untitled | 1 |
| 167 | `inherited_head_prose` | `inherit preamble`, `drop preamble`, `E003` | 1 |
| 168 | `role_and_typed_field_accounting` | `inherit role`, `inherit inputs`, `E003` | 1 |
| 169 | `drop_with_reason` | `drop`, `E610`, `E612` | 1 |
| 170 | `inherit_wildcard` | `inherit *` order, `E613` | 1 |
| 171 | `patch_paths` | Dotted `override` and `drop`, `E611` | 1 |
| 172 | `lone_module_import` | One-file module | 1 |
| 173 | `late_bound_values` | `{{agent:x}}`, defaults, `E601`, `E602`, `E603`, `E604` | 2 |
| 174 | `team_members` | `team`, `member`, facts, overlay order, `E606` | 2 |
| 175 | `team_value_precedence` | Member over team over outer team over role | 2 |
| 176 | `team_assembly` | Abstract team, `drop` of a member | 2 |
| 177 | `roster` | `roster`, `E609` | 2 |
| 178 | `team_contract` | `TEAM.contract.json` | 3 |
| 179 | `markdown_backed_declarations` | `from`, `E652`, `E653`, `E654` | 2 |
| 180 | `home_tree` | Level files, link, header, tree record, `E607`, Markdown links that follow the text | 3 |
| 181 | `details` | `DETAILS.md`, pointer | 3 |
| 182 | `shared_details` | `_details/`, `E620`, `E621` | 3 |
| 183 | `load_budgets` | `doctrine load`, `E630`, `E631`, `W306` | 3 |
| 184 | `doctrine_build_modes` | `build`, `--check`, `E634`, `W307`, obsolete files | 3 |
| 185 | `rule_team_scopes` | `team:`, `member:`, `home:` | 4 |
| 186 | `rule_load_assertions` | `requires load`, `forbids load` | 4 |
| 187 | `doctrine_diff` | `diff`, `where` | 4 |
| 188 | `project_warnings` | `W301`, `W302`, `W304` | 4 |
| 189 | `person_and_ownership` | `person`, `owns`, `E651` | 5 |
| 190 | `quotes` | Named and inline quotes, `sources`, `E650`, `W305` | 5 |
| 191 | `message_outputs` | `Message`, `E660`, `W303` | 6 |
| 192 | `doctrine_import` | `import --check` | 7 |
| 193 | `small_team_end_to_end` | Capstone | 8 |

### New Corpus Proof Kind

CLI behavior needs proof in the corpus too. `doctrine/_verify_corpus` gains
`kind = "cli_contract"`, in WS3 with the `doctrine` command. WS1 and WS2 use none. So
`TEAM.contract.json` and the link rewrite land in WS3 too, even though section 5 defines them.

```toml
[[cases]]
name = "load lists homes by headroom"
status = "active"
kind = "cli_contract"
project = "project"
args = ["load"]
expected_exit = 0
expected_stdout_lines = ["..."]
```

Keys:

- `project`: a folder holding `pyproject.toml` and `prompts/`.
- `args`: the command line after `doctrine`.
- `setup`: optional list of argument lists, run first with the same runner, each required to
  exit 0.
- `edit`: optional table of path to new content, written after `setup` and before `args`.
- `expected_exit`.
- `expected_stdout_lines` (exact) or `stdout_contains`, at most one.
- `stderr_contains`: optional list.
- `expected_file_lines`: optional table of emitted path to its exact lines. A Doctrine header
  on the file is checked for a correct hash and left out of the comparison.
- `expected_links`: optional table of path to symlink target.
- `expected_files`: optional table of emitted path to a file in the example, compared as JSON
  when the path ends in `.json`.
- `absent_files`: optional list of paths that must not exist.

The runner copies `project` to a temp folder, runs `doctrine.cli.main(args)` in process with
that folder as the current directory, and checks the result. `schema_version` in manifests
stays 1, since the kind is additive.

`CompilationSession.compile_agent` accepts a team name and `Team.key`, so `render_contract`
cases prove team files and members.

## 14. Test Plan

Corpus cases prove behavior. Unit tests prove what a corpus case can't reach. Each test
file below is new. Every named test is required.

**`tests/test_patch_language.py`**: one test for each of the 15 kinds, each compiling a real
parent and child of that kind through the compiler, because a test that only calls the helper
passes for a kind no resolver connects: `drop` removes an item; `inherit *` keeps parent order;
a dropped key counts as accounted; `E610`, `E612`, `E613` raise from every kind. Also: `test_wildcard_keeps_override_in_parent_position`,
`test_explicit_inherit_moves_item_past_wildcard`, `test_drop_requires_reason_parse_error`,
`test_disjoint_dotted_patches_are_legal`, `test_inherit_beside_dotted_patch_is_e612`,
`test_dotted_override_on_table_is_e611`, `test_paragraph_override_rejects_section_body`,
`test_several_decisions_are_one_item` (keep, drop, replace, order),
`test_inherited_role_refs_resolve_in_parent_module` (a same-named local declaration must not
win), `test_inherit_preamble_needs_a_parent_preamble`, `test_schema_unknown_inherit_fails`,
`test_drop_abstract_slot_is_e610`, `test_old_forms_keep_shipped_duplicate_errors`,
`test_second_override_under_wildcard_keeps_shipped_error`, `test_inherit_star_with_nothing_is_e610`,
`test_dropped_slot_fails_requires_declare`, `test_inherited_field_keeps_parent_imports` (an
alias the child reuses for another module, a `from` import, a private declaration),
`test_inherited_final_output_reaches_previous_turn`, `test_flow_keeps_inherited_role`,
`test_receipt_routes_are_inherited_items`, `test_dotted_override_needs_a_body`,
`test_paragraph_title_ref_inside_a_section` (read from a role and from its own workflow),
`test_route_cannot_replace_a_parent_key`, `test_inherited_selectors_cross_modules`.

**`tests/test_prose_render.py`**: `test_adjacent_strings_get_blank_line_in_each_surface`
over workflow root, section, document, record body, role block, callout;
`test_paragraph_renders_in_document`; `test_generated_lines_keep_their_layout` (a JSON example
fence, a final-answer quote, and a generated list); `test_e605_fence_split_across_strings`;
`test_fence_whole_in_one_string_compiles`; `test_list_strings_become_a_loose_list`;
`test_multiline_string_keeps_inner_newlines`; `test_section_metadata_only_with_requirement`;
`test_paragraph_title_runs_in`; `test_untitled_paragraph_has_no_heading`.

**`tests/test_parse_diagnostics.py`** (extend): `test_e132_only_after_arrow`,
`test_e134_named_block_without_title` for `table`, `definitions`, `callout`, with the
hints each kind gets.

**`tests/test_late_binding.py`**: `test_value_reaches_parent_workflow_text`,
`test_value_in_title`, `test_value_in_markdown_block`, `test_code_block_stays_literal`,
`test_resolved_declaration_cache_shared_across_agents` (two agents, one resolve),
`test_e601_lists_all_blanks_and_sites`, `test_e601_empty_others`, `test_e603_prints_cycle`
(from the cycle's first key, not the read that led there), `test_e608_value_set_twice`,
`test_e602_in_skill_package`, `test_e602_in_output_schema`, `test_value_reads_value`.

**`tests/test_teams.py`**: `test_member_name_and_folder`, `test_member_ref_resolves_in_route`,
`test_abstract_team_stamps_members_per_team`, `test_overlay_render_order`,
`test_team_doctrine_stays_out_of_member_home`, `test_tree_from_paths_only`,
`test_team_contract_order_and_sections`, `test_roster_skips_row_without_value`,
`test_roster_static_rows_follow`, `test_e607_member_folder_collides_with_team`,
`test_roster_team_typo_is_e601`, `test_roster_skipping_every_member_is_e601`,
`test_flow_graph_routes_to_a_member` (route field and workflow route, rendered to D2),
`test_team_and_agent_cannot_share_a_name`, `test_second_home_is_e606`.

**`tests/test_markdown_reader.py`**: `test_slug_rules`, `test_headings_in_fences_ignored`,
`test_deeper_headings_stay_text`, `test_e653_duplicate_key`, `test_e654_import_line`,
`test_role_from_text_before_first_heading`, `test_drop_gone_heading_is_e610`,
`test_relative_link_rebased_per_home`, `test_anchor_kept_on_rebased_link`,
`test_scheme_root_and_anchor_links_left_alone`, `test_links_in_code_left_alone`,
`test_reference_definition_rebased`, `test_out_dir_keeps_rebased_bytes`,
`test_no_emit_target_keeps_links_as_written`, `test_footnotes_and_prose_keep_their_text`,
`test_stray_backticks_stop_at_a_blank_line`, `test_fence_rules_follow_commonmark` (a longer
fence holding a shorter one, a fence with an info string inside a fence, inline backticks),
`test_reserved_heading_gets_final_underscore`.

**`tests/test_home_tree.py`**: `test_claude_md_is_relative_symlink`,
`test_header_hash_matches_body`, `test_emit_is_deterministic` (two builds, identical bytes),
`test_no_import_lines_emitted`, `test_concurrent_builds_are_safe` (8 processes),
`test_write_skipped_when_bytes_match` (mtime kept), `test_emit_docs_output_unchanged`,
`test_plain_agent_gets_header_and_guard`, `test_written_files_follow_umask`,
`test_contract_files_have_no_guard`, `test_claude_md_link_left_alone`,
`test_real_claude_md_goes_through_guard`, `test_other_claude_md_link_is_e634`,
`test_record_lists_every_emitted_path_sorted`, `test_missing_record_means_nothing_obsolete`,
`test_conflicted_record_counts_as_missing`.

**`tests/test_details.py`**: `test_owner_table` (one test per row of the table in section
6.3), `test_e620_in_skill_package`, `test_one_pointer_line_per_home`, `test_companion_keeps_headings_and_depth`,
`test_repeat_headings_get_suffix_anchors`, `test_details_not_in_load`,
`test_details_in_document_section`, `test_e620_in_input_and_output`, `test_e620_in_emit_docs`,
`test_e620_in_output_structure`, `test_e620_in_skill`,
`test_shared_companion_bytes_ignore_consumers` (two members reorder and retitle one inherited
section, and one `_details/` file results).

**`tests/test_load.py`**: `test_claude_counts_utf16_units` (with an astral character),
`test_codex_counts_bytes`, `test_codex_limit_read_from_project_config`,
`test_external_present_counts_real_size`, `test_external_absent_counts_reserve`,
`test_e633_absent_no_reserve`, `test_nearest_budget_wins`, `test_role_budget_is_a_default`,
`test_unknown_runtime_setting_is_e632`, `test_bad_reserve_is_e632`, `test_e631_over_runtime_limit`,
`test_biggest_parts_order_and_smaller_row`, `test_full_prints_every_file_in_order`.

**`tests/test_cli.py`**: exit codes 0, 1, 2 for each verb;
`test_every_compiling_corpus_agent_builds` (each agent the corpus compiles goes through
`build_home_map`), `test_error_in_unselected_home_cannot_stop_build`,
`test_bad_budget_or_external_cannot_stop_build`, `test_build_warns_only_for_selected_homes`,
`test_broken_unrelated_target_cannot_stop_build`, `test_rule_in_soul_cannot_stop_build`,
`test_w307_skips_selected_and_hand_written_files`, `test_check_json_is_only_json`,
`test_broken_team_elsewhere_cannot_stop_build`, `test_malformed_settings_are_e632`,
`test_binary_level_file_cannot_stop_build`, `test_target_with_no_emit_table_exits_2`,
`test_unknown_target_with_rev_exits_2`, `test_with_outside_repo_exits_2`,
`test_e634_heading_from_prose`, `test_e634_names_the_markdown_source`,
`test_build_writes_only_selected_folders`, `test_build_prints_w307_for_stale_level`,
`test_build_never_fails_on_budget_or_rule`, `test_check_fails_on_budget_and_rule`,
`test_check_mode_reports_stale_edited_missing`, `test_e634_names_section_and_origin`,
`test_e634_writes_nothing`, `test_force_overwrites_edit`, `test_force_removes_edited_obsolete_file`,
`test_rev_extracts_only_what_the_result_depends_on`, `test_rev_reads_codex_limit_from_revision`,
`test_w307_for_level_no_longer_emitted`, `test_with_overlays_one_file`, `test_e640_selector`, `test_e641_revision`,
`test_where_finds_value_text`, `test_where_reports_reach`, `test_console_scripts_declared`.

**`tests/test_diff.py`**: `test_moving_a_declaration_changes_no_hash`,
`test_reach_lists_only_changed_homes`, `test_change_at_a_level_reaches_homes_below`,
`test_size_range_printed_when_homes_differ`,
`test_details_delta_separate`, `test_owned_change_reported`, `test_person_change_reported`,
`test_new_section_through_wildcard`, `test_explicit_member_fails_instead_of_new_section`,
`test_outputs_list_exact_paths`, `test_outputs_hold_only_changed_files`,
`test_outputs_list_removed_paths`, `test_with_ignores_other_uncommitted_edits`,
`test_json_format_version`.

**`tests/test_project_warnings.py`**: `test_w301_type_1_and_near`,
`test_w301_short_paragraph_skipped`, `test_w301_shared_section_not_a_copy`,
`test_w301_groups_by_declaration_pair`, `test_w302_double_load`,
`test_w302_groups_across_slot_keys`, `test_w304_unused_value`,
`test_check_disable_list`, `test_strict_fails_on_warning`.

**`tests/test_provenance.py`**: `test_quote_render_forms` (bare, `to`, `about`, both),
`test_inline_quote_matches_named_render`, `test_inline_quote_field_order_free`,
`test_e650_bad_date`, `test_e650_unknown_person`, `test_sources_flags_missing_source`,
`test_sources_lists_inline_by_site`, `test_owners_add_up`, `test_e651_glob_matches_nothing`.

**`tests/test_messages.py`**: `test_both_homes_share_body`, `test_field_change_reaches_both`,
`test_e660_shape_on_message`, `test_e301_for_other_targets_stays`, `test_w303_no_reader`,
`test_string_to_has_no_reader_check`, `test_same_agent_sends_and_reads`.

**`tests/test_import.py`**: `test_lead_in_becomes_paragraph`, `test_check_passes_on_lossless`,
`test_check_reports_first_difference`, `test_text_after_keyed_item_gets_untitled_paragraph`,
`test_one_line_text_uses_plain_string`, `test_bold_only_paragraph_stays_text`,
`test_repeated_key_gets_suffix`, `test_printed_source_parses`.

**`doctrine/_diagnostic_smoke`** gains a fixture for every new `E6xx`, `RULE006`, `RULE007`,
and `W3xx`.

**Whole-corpus duty.** Every existing example stays and stays green. A rendered change from
section 3 is applied by regenerating `expected_lines` and `ref/` and `build_ref/`, and the
implementer's report lists how many cases changed for each of the three reasons. The
reviewer samples them. An example changes for no other reason. New required accounting
lines (`inherit preamble`, `inherit inputs`) go into existing example source only where the
compiler now demands them, and the report lists each one.

## 15. Docs And Skills Duty By Workstream

Docs land with the code that makes them true, in the same workstream. Plain language at
about a 7th grade reading level applies to all of it.

| WS | Live docs | Skills |
| --- | --- | --- |
| 1 | `LANGUAGE_REFERENCE` (workflows, inheritance, readable blocks), `LANGUAGE_DESIGN_NOTES` (patch language, paragraph), `COMPILER_ERRORS`, `AUTHORING_PATTERNS`, `FAIL_LOUD_GAPS` | `agents_and_workflows`, `documents_and_tables`, `imports_and_refs`; linter `finding_catalog` drop guidance for `AL130` |
| 2 | `LANGUAGE_REFERENCE` (values, teams, roster, `from`, interpolation), `LANGUAGE_DESIGN_NOTES` (late binding, teams are folders), `COMPILER_ERRORS`, `AUTHORING_PATTERNS` | `agents_and_workflows`, new `teams_and_homes` |
| 3 | `EMIT_GUIDE` (home tree, runtimes, `DETAILS.md`, CLI), `LANGUAGE_REFERENCE` (`details`, `budget`), `WARNINGS`, `COMPILER_ERRORS`, `WHY_DOCTRINE`, `README` quick start | `emit_targets`, `verify_and_ship`, `teams_and_homes` |
| 4 | `LANGUAGE_REFERENCE` (Project Rules), `WARNINGS` (Project Warnings; remove the candidates now shipped), `AGENT_LINTER`, `COMPILER_ERRORS` | `rules`; linter `audit_method`, `finding_catalog`, `report_contract` |
| 5 | `LANGUAGE_REFERENCE`, `COMPILER_ERRORS`, `AUTHORING_PATTERNS` | `language_overview` |
| 6 | `LANGUAGE_REFERENCE` (Outputs), `AGENT_IO_DESIGN_NOTES`, `COMPILER_ERRORS` | `outputs_and_schemas` |
| 7 | `README`, `CHANGELOG`, `VERSIONING`, `docs/README`, `examples/README`, root `AGENTS.md` (corpus range), `CONTRIBUTING` | All skills rebuilt with `make skills` |
| 8 | `DOCTRINE_LEARN`, `AUTHORING_PATTERNS` | Section 12 |

`docs/VERSIONING.md` moves to language 6.0 with an upgrade section listing the three breaks
and their mechanical fixes. `CHANGELOG.md` gets one entry per workstream under `Unreleased`.

This plan file is deleted before merge, after a restore-point commit, per `AGENTS.md`.

## 16. Build Order, Models, And Review

Each workstream lands on `feat/teams-and-homes` in order. A later one starts only after the
earlier one passes its gate.

| WS | Builder | Trip wire | Why this setting |
| --- | --- | --- | --- |
| 1 | Sol 6.1 at xhigh | 900 | Touches 15 resolvers and every render; several parts |
| 2 | Sol 6.1 at xhigh | 1,400 | New pass across compile; several parts |
| 3 | Sol 6.1 at xhigh | 1,900 | Emit, config, CLI; several parts |
| 4 | Sol 6.1 at xhigh | 1,100 | New algorithms: map, diff, near-copy |
| 5 | Terra 6.1 at xhigh | 400 | One piece from a full spec, with a check that proves it |
| 6 | Terra 6.1 at xhigh | 200 | One piece from a full spec, with a check that proves it |
| 7 | Terra 6.1 at xhigh | 250 | One tool plus bringing text in line with facts |
| 8 | The designer writes `getting-good-results`; Terra 6.1 at xhigh aligns the rest | none | Teaching is judgment; alignment is checkable |

The trip wire is net new lines under `doctrine/`, leaving out tests, docs, examples, and
skills. It is a stop, not a target. A worker that reaches it stops and reports what is
taking the room.

Every brief says: if the spec is wrong, silent, or contradicts the code, stop and report;
language design is closed; and it carries the overbuild rules below.

### Overbuild Is The Main Risk

Workers from this maker add what nobody asked for: guards, options, fallbacks, helpers, and
layers, each reasonable alone. Passing tests prove the code does what it should. They don't
prove the code is only that. So overbuild fails a gate exactly as a failing test does.

**The rule.** Every line of non-test code traces to a section of this spec, a named example,
or a named test. What doesn't trace goes. What traces but is heavier than the job is cut to
its plain version.

**One author.** A worker writes all the code itself, with no helper agents, so the code has
one voice and every line had the whole spec behind it.

**Nothing extra, by name.** Each brief bans, unless this spec names it: a guard or error path
for a case the spec doesn't name; a check for a state the compiler can't reach; a fallback,
default, or retry; an option, flag, parameter, or config key; a class, base class, registry,
or layer; a helper with one caller or a wrapper around one call; a `try` the spec gives no
outcome for; a shim or second path beside what it replaced.

**The audit belongs to the designer.** A builder never audits itself. Its report is a lead
to check, not a finding. After proof passes and before any other review, the designer does
all of this personally:

1. Counts net lines by file against the trip wire.
2. Checks the worker's list of new functions, classes, constants, and modules against the
   diff. Anything missing from the list, or with no section behind it, is a cut.
3. Runs the new code under the corpus and named tests with coverage. A line nothing runs is
   presumed unneeded until shown otherwise.
4. Reads every changed line against the rule, using the `overbuild-audit` families.
5. Compares every changed existing example file with its base, line by line, including blank
   lines. A blank line may change only beside an authored string, and generated lines stay
   byte for byte. Anything else is a regression, however the worker filed it. A comparison
   that ignores blank lines missed a real break here.

**Send back.** Every cut goes back to the worker that wrote it, in the same thread, as a list
of removals with file and line. A send-back only removes. It never asks for a new guard, test,
or option. The designer decides, and the worker can't keep a piece by arguing for it. The
designer then audits the cut diff. The gate stays shut until that audit is clean. What a
worker got wrong goes into the next workstream's brief by name.

**Review findings get the same test.** The worst bloat on record came after review, when
findings became fix briefs as written. Before a finding becomes work, ask whether a user here
meets that case, how often, and what the plain version costs them when they do.

**Gate for each workstream:**

1. The workstream's example manifests and new unit tests pass.
2. `make verify-diagnostics`, `make tests`, and `make skills` pass, the corpus passes for
   every example up to this workstream's last, and `python -m doctrine.verify_skill_examples
   --root skills/.curated/doctrine-learn --root skills/.curated/agent-linter` passes, because
   `make verify-skill-examples` reads no prompt fences from its default roots.
   `make verify-examples` runs whole once WS8 is in. Each runs once, when the workstream is
   ready.
3. The designer's overbuild audit is clean, with every cut sent back and verified.
4. The designer reads the whole diff against this spec, line by line.
5. Opus 5.5 at high, which built none of it, reviews the diff against this spec and for what
   it doesn't need. Its findings are proposals. The designer decides each one, and the cuts
   go back the same way.

**At the end:** one Opus 5.5 high read of the whole branch for what it doesn't need, one more
designer audit of the whole branch by the same rule, `make check`, and a compile of Lesson
Studio, Puzzle DB, and PS Mobile prompts against the new compiler in scratch copies. The report
lists what each needs for 6.0. Nothing in those repositories changes here.

Merging and releasing stay with the owner.

## 17. Diagnostic Wording

This is the binding wording for every new code. `<x>` is filled from the source. A code has
the summary and detail given here, in the shipped diagnostic shape, and no hint or related
site beyond what this table names. Where a row lists several details, each is one case.
`E003`, `E301`, `RULE001`, and `RULE002` keep their shipped wording.

| Code | Summary | Detail |
| --- | --- | --- |
| `E134` | `Missing block title` | The shipped parse detail. Hints: section 4.3 |
| `E601` | `Unfilled value` | `` Home `<home>` reads values nothing fills: `` then one line per blank, `` - `<root>:<key>` at <file>:<line> `` |
| `E602` | `Value has no owner here` | `` `{{<root>:<key>}}` can't be read here: <why>. `` `<why>` is one of: `a skill package has no home`; `an emitted document has no home`; `output schema text is machine text`; `this agent is outside any team`; `a team's own file has no others` |
| `E603` | `Value cycle` | `` Values read each other: `a -> b -> a` `` |
| `E604` | `Value sets a fact` | `` `values:` can't set `<key>`. The compiler supplies it. `` |
| `E605` | `Code fence split across strings` | `` A string in <owner> opens a code fence it doesn't close. `` Hint: ``Put the whole fence in one `"""` string, or use a `code` block.`` |
| `E608` | `Value set twice` | `` `values:` sets `<key>` twice. `` |
| `E606` | `Invalid team` | `` Team `<name>` needs `home:`. ``; `` Abstract team `<name>` can't have `home:`. ``; `` `home: "<value>"` must be a plain relative path, such as `pods/growth`. ``; `` Team `<name>` can't hold `<field>`. A team takes `role`, `values`, `budget`, slots, and members. ``; `` Team `<name>` uses key `<key>` twice. `` |
| `E607` | `Two homes, one path` | `` `<owner a>` and `<owner b>` both land at `<path>`. ``; `` Targets `<a>` and `<b>` share output folder `<dir>`. `` |
| `E609` | `Invalid roster` | `` `roster <key>` needs a team, and this home has none. ``; `` Column `<column>` has no `{{agent:...}}` in its cell. ``; `` `rows:` names unknown column `<column>`. ``; `` Row `<row>` leaves column `<column>` empty. `` |
| `E610` | `Missing patch target` | `` `<owner>` patches `<path>`, but its parent has no such key. ``; `` `<owner>` writes `inherit *`, but it has nothing to inherit. `` |
| `E611` | `Invalid patch path` | `` `<owner>`: `<path>` steps through `<step>`, which has no keyed items. ``; `` `<owner>`: `override <path>` targets a `<kind>`. Override the section that holds it. ``; `` `<owner>`: `override <path>` gives a paragraph a body it can't hold. A paragraph takes prose and `details`. `` |
| `E612` | `Conflicting patches` | `` `<owner>` patches `<path>` twice. ``; `` `<owner>` writes `inherit <key>` beside a patch under `<key>`. The patch already accounts for it. ``; `` `<owner>` patches `<path>` under `<parent>`, which it already dropped or overrode. ``; `` `<owner>` can't drop `role`. Write `role:` to replace it, or `inherit role` to keep it. `` |
| `E613` | `Duplicate inherit *` | `` `<owner>` writes `inherit *` more than once. `` |
| `E620` | `Details not allowed here` | `` `details` can't be used in <surface>. `` |
| `E621` | `Shared details read one agent's words` | `` `_details/<slug>.md` serves every home that points at it, so it can't read `{{<root>:<key>}}`. `` Hint: section 6.3 |
| `E630` | `Over load budget` | Section 6.4 |
| `E631` | `Invalid budget` | `` `budget` for `<key>` must be a positive integer. ``; `` `budget` for `<key>` is over the runtime's limit of <limit>. ``; `` `budget` names unknown runtime `<key>`. `` |
| `E632` | `Invalid runtime settings` | `` Unknown runtime `<name>`. ``; `` `<setting>` for `<runtime>`: <what's wrong>. `` |
| `E633` | `External file missing` | `` `<path>` is listed for <runtime>, but it is absent and has no `reserve`. `` |
| `E634` | `Hand edit in a compiled file` | `` `<path>` was edited by hand. `` then, for a file the build would overwrite, one line per differing section, `` - <title>: <origin> at <site> ``; `` `<path>` was written by hand. ``; `` `<path>` is a link Doctrine didn't write. `` Hint: ``Move the edit to its source, then build. `--force` overwrites it.`` |
| `E640` | `No home matches` | `` `<selector>` matches no home. `` |
| `E641` | `Bad revision` | `` `<rev>` is not a revision in this repository. `` |
| `E650` | `Invalid quote` | `` Quote `<name>` needs `by:`. ``; `` `by:` in `<name>` is not a `person`. ``; `` `on:` in `<name>` must be a date, `YYYY-MM-DD`. ``; `` Inline quote: <what's wrong>. `` |
| `E651` | `Invalid owner` | `` `<ref>` in `owns:` resolves to nothing. ``; `` Glob `<glob>` in `owns:` matches no file. `` |
| `E652` | `Missing Markdown source` | `` `<decl>` reads `<path>`, which does not exist. `` |
| `E653` | `Duplicate heading key` | `` `<path>` has two sibling headings with key `<key>`, at lines <a> and <b>. `` |
| `E654` | `Import line in Markdown source` | `` `<path>` line <n> is a runtime import, and its path would break once inlined. Declare that file too and compose it. `` |
| `E660` | `Message has no shape` | `` `Message` output `<name>` can't have `<field>`. A message is prose. `` |
| `RULE006` | `Requires load` | `` - <agent> must load <target>. `` |
| `RULE007` | `Forbids load` | Section 8.1 |

Warnings print one line, then any detail lines:

| Code | Line |
| --- | --- |
| `W301` | Section 8.3 |
| `W302` | `` W302 double load: <origin> reaches <home> from <file a> and <file b>. `` |
| `W303` | `` W303 message without reader: <output> goes to <to>, and nothing there reads it. `` |
| `W304` | `` W304 unused value: <key> at <site> is read by no home. `` |
| `W305` | `` W305 unused quote: <name> at <site> is cited nowhere. `` |
| `W306` | `` W306 near budget: <home> loads <n> of <limit> on <runtime>. `` |
| `W307` | `` W307 stale level: <path> differs from this build. `` |
