# Compiler Errors

This document is the canonical error reference for the shipped Doctrine parser,
compiler, and emit pipeline.
For public compatibility rules, release duties, and upgrade policy, use
[VERSIONING.md](VERSIONING.md).

The error surface is now structured first and formatted second.

Every user-facing error should carry:
- a stable code such as `E101` or `E280`
- a stage label such as `parse`, `compile`, or `emit`
- a short summary line
- optional location, source excerpt, related sites, trace, hints, and
  normalized cause text

The formatter order is canonical:
- first line: `CODE stage error: summary`
- then location
- then source excerpt when we know a line and column
- then related sites
- then detail
- then trace
- then hints
- then the normalized low-level cause

Compile diagnostics follow one default policy:
- use the real authored line when the compiler has a truthful `SourceSpan`
- add one `Related:` block when the failure depends on another real site
- keep the location file-scoped when there is no truthful authored line to show
- prove shipped `compile_fail` cases with `error_code`, `location_line` or
  `location_path`, and optional `related` sites instead of snippet matching

Stability rules:
- keep existing error identities stable once they are shipped
- preserve `E001`, `E002`, and `E003` meanings
- prefer adding a new code over silently changing an old code's meaning
- keep wording human and direct, but allow the exact sentences to tighten over time

## Code Bands

| Band | Meaning |
| --- | --- |
| `E001`-`E099` | reserved canonical language-rule errors |
| `E100`-`E199` | parse errors |
| `E200`-`E468` | semantic compile errors |
| `E469`-`E500` | review-specific parse and compile errors |
| `E501`-`E699` | emit and build-target errors |
| `E900`-`E999` | internal compiler bugs or invariant failures |

## Current Stable Codes

### Reserved language-rule codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E001` | Cannot override undefined inherited entry | Used when `override` tries to replace an inherited authored slot, workflow, `skills`, or named IO entry that does not exist. |
| `E002` | Missing rendered section title | Reserved meaning: a rendered section needs an explicit visible title and the source does not provide one. |
| `E003` | Missing inherited entry | Used when explicit inherited patching omits one of the inherited authored-slot, workflow, `skills`, `output`, or named IO entries. |

### Parse codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E101` | Unexpected token or newline | The parser saw a token or line break that does not fit the current grammar state. |
| `E102` | Unexpected character | The parser hit a character that does not map to a valid token on this surface. |
| `E103` | Unexpected end of file | The file ended before the current declaration or block was complete. |
| `E104` | Indentation-sensitive parse failure | The parser saw an unexpected indent or dedent. |
| `E105` | Invalid authored slot body | A referenced authored workflow slot was given an inline body instead of either a named workflow ref or an inline workflow body. |
| `E106` | Invalid string literal | A quoted string token could not be decoded because its escapes or delimiters were invalid. |
| `E131` | Missing route label | A route line reached `->` without a quoted label first. |
| `E132` | Missing route target | A route line reached the end of the statement after `->` without an explicit agent target. |
| `E133` | Missing `via` carrier | A workflow-law currentness or invalidation statement omitted its required `via Output.field` carrier. |
| `E199` | Parse failure | Generic fallback parse code when the failure does not fit a narrower shipped parse code yet, including parser-level output owner conflicts such as `schema:` plus `must_include:`, `schema:` plus `structure:`, invalid named-table ownership such as `columns:` on a named table use site, or parser-owned `skill_flow` block-shape failures such as a missing required `why:` line or duplicate edge or repeat body keys. |

### Compile codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E201` | Missing target agent | The requested concrete agent does not exist in the root prompt file. |
| `E202` | Abstract agent does not render | The target agent exists, but it is marked `abstract`. |
| `E203` | Duplicate role field | One agent defines `role` more than once. |
| `E204` | Duplicate typed field | One agent defines the same typed field more than once. |
| `E205` | Concrete agent is missing role field | A concrete agent is missing its required `role` field. |
| `E206` | Unsupported agent field order | The authoring shape is outside the shipped subset, such as violating the bootstrap role/workflow order rule. |
| `E207` | Cyclic agent inheritance | Agent inheritance forms a cycle. |
| `E208` | Unsupported agent field | A field reached the compiler on a surface the shipped subset does not support. |
| `E209` | Concrete agent is missing abstract authored slots | A concrete agent still has unresolved `abstract <slot_key>` requirements after inheritance resolution. |
| `E210` | Abstract authored slot must be defined directly | An inherited abstract authored slot was handled with `inherit` or `override` instead of a direct `slot_key: ...` definition. |
| `E211` | Final output must point at output declaration | `final_output:` resolved to some declaration kind other than `output`. Related routed-final-output checks still fail loud with direct messages when `final_output.route:` points at a non-structured final output or a field that is not a `route field`. |
| `E212` | Final output is not emitted by the concrete turn | `final_output:` points at an `output`, but the concrete agent does not emit it through `outputs:`. |
| `E213` | Final output must designate one TurnResponse message | `final_output:` points at a file bundle or some non-`TurnResponse` target instead of one final assistant message. |
| `E214` | Retired | Reserved error code. Review-driven `final_output:` may now differ from `comment_output:`. |
| `E215` | Final output `example_file` is retired | A structured `final_output:` still uses `example_file` on `output shape`, which is retired. |
| `E216` | Final output example does not match the lowered schema | A structured `final_output:` declares an `example:`, but that JSON object does not validate against the lowered schema. |
| `E217` | Final output lowered schema failed Draft 2020-12 validation | Doctrine lowered an `output schema`, but the resulting JSON Schema is not valid Draft 2020-12. |
| `E218` | Final output lowered schema is outside the OpenAI structured-outputs subset | Doctrine lowered an `output schema`, but the result uses a shape or rule the OpenAI structured-outputs subset does not allow. |
| `E220`-`E225` | Typed declaration completeness errors | These codes cover missing required typed declaration fields such as skill purpose, input source, input shape, input requirement, and output target shape combinations. |
| `E226` | Reserved | Reserved for a future user-facing "unsupported record item" check. The shipped grammar already restricts what can appear on each record surface, so any unexpected record-item kind that reaches the compiler today is an internal invariant failure and fails loud as `E901`. |
| `E227`-`E229` | Retired in language 5.0 | Covered the deleted inline `type: enum` plus `values:` form and the legacy `type: string` plus `enum:` form for `output schema` fields. Both forms are removed in 5.0; the canonical form is `enum X: "..."` plus `type: X`. Unknown `type:` names now fail loud under `E320`. Codes stay reserved to avoid accidental reuse. |
| `E230`-`E235` | Config declaration and config instance errors | These codes cover invalid config item shapes, duplicate or unknown keys, missing required keys, and bad config key declarations. |
| `E236` | Output schema `required` is retired | `required` is still parseable inside `output schema` so Doctrine can fail loudly and tell authors to delete it. Output-schema object properties still stay present on the wire today. |
| `E237` | Output schema `optional` is retired | `optional` is still parseable inside `output schema` so Doctrine can fail loudly and tell authors to use `nullable` when the value may be `null`. |
| `E240`-`E243` | Workflow inheritance and patching errors | These codes cover cyclic workflow inheritance, inheriting undefined keys, kind mismatches, and `inherit` or `override` without an inherited workflow. |
| `E244`-`E249` | IO block inheritance and typed-field ref errors | These codes cover cyclic `inputs` / `outputs` block inheritance, undefined inherited keys, patching without an inherited IO block, inherited IO blocks without stable keyed sections, and wrong-kind IO refs or patch bases. |
| `E250` | Cyclic skills inheritance | Top-level `skills` block inheritance forms a cycle. |
| `E251` | Cyclic output inheritance | Top-level `output` declaration inheritance forms a cycle. |
| `E252` | Output patch requires an inherited output | `inherit` or `override` was used in an `output` body that does not inherit a parent output. |
| `E253` | Cannot inherit undefined output entry | An inherited `output` asked for a top-level key the parent output does not define. |
| `E254` | Inherited output needs keyed top-level entries | A parent `output` used for inheritance contains bare top-level prose or another unkeyed top-level item. |
| `E255` | Invalid output inheritance patch | An inherited `output` repeats a key, overrides it with the wrong kind, or patches an inherited entry without `override`. |
| `E260` | Conflicting concrete-turn binding roots | One concrete-turn bound root path resolves to different artifacts inside the same concrete turn. |
| `E261` | Duplicate workflow item key | One workflow body repeats the same keyed entry. |
| `E270` | Ambiguous declaration reference | A readable or addressable ref matches more than one visible declaration kind. |
| `E271` | Workflow ref is not allowed here | A bare workflow ref was used on a readable surface that allows declarations but not workflow roots. |
| `E272` | Abstract agent ref is not allowed here | A readable mention points at an abstract agent instead of a concrete owner. |
| `E273` | Unknown addressable path | An interpolation or addressable ref asked for a nested path that does not exist on that surface. |
| `E274` | Addressable path must stay addressable | A path tried to keep traversing after it had already reached a scalar or other non-addressable surface. |
| `E275` | Typed declaration must stay typed | A typed declaration field such as `source`, `target`, or `shape` was treated like an untyped pathable value. |
| `E276` | Missing local declaration reference | A local readable, analysis, named-table, output `shape:` ref, or addressable ref points at a declaration that does not exist. |
| `E280` | Missing import module | An imported module could not be found in the active import-root registry. When Doctrine runs through a wrapper harness that owns the import-root registry, use the wrapper's build entrypoint — invoking `python -m doctrine.emit_docs` directly bypasses the wrapper's active roots and surfaces this code. |
| `E281` | Missing imported declaration | The imported module resolved, but the requested declaration does not exist there. |
| `E282` | Route target must be a concrete agent | A route points at an abstract or otherwise invalid target. |
| `E283` | Cyclic workflow composition | `use`-based workflow composition forms a cycle. |
| `E284` | Duplicate record key | A record body repeats the same key where the current surface expects uniqueness. |
| `E285` | Invalid compile config | The nearest Doctrine compile config is structurally invalid, such as a non-table `[tool.doctrine.compile]`, a bad `additional_prompt_roots` entry, or a bad provider prompt root. |
| `E286` | Duplicate active prompts root | A configured or provider `prompts/` root resolves to the same directory more than once, including duplication of the entrypoint-local root. |
| `E287` | Ambiguous import module | An absolute import matches the same dotted module path in more than one active `prompts/` root, or in both a skill-package source root and an active `prompts/` root. |
| `E288` | Duplicate declaration name | One prompt file defines the same declaration name more than once. Use `E316` when the collision crosses sibling files inside one flow. |
| `E289` | Cyclic import module | Import resolution forms a true cross-flow cycle after Doctrine resolves real flow boundaries. |
| `E290` | Relative import walks above prompts root | Legacy relative-import guard. Relative import syntax is retired from the shipped grammar. |
| `E291` | Prompt source path is required for compilation | The compiler was asked to compile a prompt object without a source path. |
| `E292` | Could not resolve prompts root | The compiler could not find the owning `prompts/` root for the current prompt file path. |
| `E293` | Duplicate enum member key | One `enum` body repeats the same member key. |
| `E294` | Duplicate enum member wire | One `enum` body repeats the same host-facing `wire` value. |
| `E295` | Duplicate readable key | A readable surface repeats a keyed child such as a document block, properties entry, inline schema entry, footnote, or table child. |
| `E296` | Readable guard reads disallowed source | A readable `when` guard reads emitted output fields or other disallowed sources instead of only declared inputs and enum members. |
| `E297` | Invalid readable block structure | A readable block uses an invalid structural shape, such as an unknown callout kind, single-line raw/code text, an empty inline or named table, or a multiline inline table cell. |
| `E298` | Invalid render_profile declaration | A `render_profile` declares an unknown target, unsupported mode, or duplicate target rule. |
| `E299` | Compile failure | Generic fallback compile code when the failure does not fit a narrower shipped compile code yet. No shipped manifest-backed compile-fail case currently depends on `E299`. |
| `E301` | Invalid IO bucket item | An `inputs:` or `outputs:` bucket contains an invalid item shape, inline declaration body, or wrong-kind declaration ref. |
| `E302` | Invalid output attachment declaration | An output attaches an invalid `schema:` or `structure:` surface, such as a sectionless schema or a non-markdown structure target. |
| `E303` | Invalid schema declaration | A schema artifact or schema group uses an invalid declaration shape, such as a wrong-kind artifact ref, an unknown group member, or an empty group. |
| `E304` | Invalid skill package bundle | A `skill package` bundle uses an invalid `emit:` path, points an `emit:` entry at the wrong declaration kind, collides with another emitted path, points at an unreadable bundled file, or lowers a nested agent prompt with the wrong concrete-agent shape. |
| `E305` | Invalid document inheritance patch | A document inheritance patch uses the wrong override shape, such as a kind mismatch or a patch without an inherited document parent. |
| `E307` | Duplicate imported name | One prompt file binds the same visible imported name more than once, whether that name came from a module import, alias, or imported symbol. |
| `E308` | Ambiguous flow-local vs imported symbol | A bare visible name is both a flow-local declaration and an imported symbol, so Doctrine refuses to guess which owner the ref should use. |
| `E309` | Malformed grouped `inherit` | A grouped `inherit { ... }` is empty, repeats the same key, or uses a key that is not legal on that grouped surface. |
| `E312` | `self:` needs a declaration-root addressable context | `self:` was used on a surface that does not carry a live declaration-root addressable context. Use an explicit `Root:path` ref there. |
| `E314` | Imported declaration is not exported | A cross-flow import reached the target flow, but the requested declaration stays internal because it is not marked `export`. |
| `E315` | Same-flow import retired | One sibling `.prompt` file tried to import another sibling from the same flow, even though the flow already shares one flat namespace. Sibling `.prompt` files inside one flow reach each other by bare ref — see the "Flow Boundaries And Exports" section of `doctrine-learn/references/imports-and-refs.md`. |
| `E316` | Sibling declaration collision | Two sibling prompt files in the same flow declared the same name, so Doctrine refused to guess which sibling owns it. |
| `E317` | `via review` clause is misplaced or does not match the resolved outcome | A `via review.<section>.route` clause appears outside a `next_owner:` field body on an output declaration, or appears inside an output shape body, or names the wrong `on_*` section for the branch that resolves the route, or appears more than once in the same body. |
| `E318` | Output shape selector + case dispatch is malformed | An output shape uses `case ...:` without a `selector:` block, a `case` block appears outside an output shape body, the selector does not resolve to a closed enum, a case selects the wrong enum (including a same-named enum from a different imported flow), the cases overlap, or the cases do not cover every enum member. |
| `E319` | Agent selector binding is missing or wrong for an output shape | An agent's `final_output` points at an output shape with a `selector:` block, but the agent does not bind that selector under `selectors:`, binds the same selector twice, binds a selector key the shape does not declare, or binds the selector to a member of a same-named enum from a different imported flow. |
| `E320` | Field `type:` references unknown name | A field's `type: <CNAME>` on any field-shaped surface (output schema field/route field/def, readable `row_schema` entry, readable `item_schema` entry, readable `table` column, record scalar) names something that is neither a builtin primitive (`string`, `integer`, `number`, `boolean`, `object`, `array`, `null`) nor a visible `enum` decl. Declare the enum or use a builtin. |
| `E331` | Missing current-subject form | An active workflow-law leaf branch did not resolve either `current artifact ... via ...` or `current none`. |
| `E332` | Multiple current-subject forms | One active workflow-law leaf branch declared more than one current subject. |
| `E333` | Current carrier output not emitted | The output carrying current truth is not emitted by the concrete turn. |
| `E334` | Current output not emitted | A workflow-law current artifact points at an output the concrete turn does not emit. |
| `E335` | Current artifact target has wrong kind | A `current artifact` target does not resolve to a declared or bound concrete-turn input or output. |
| `E336` | Current carrier field missing from trust surface | A currentness carrier field is not listed in the target output's `trust_surface`. |
| `E337` | Retired | Reserved error code. Unknown `current artifact ... via ...` carrier fields fall through to the normal unknown-field check and fail loud as `E299`, which is the shared unknown-field code called out in the `E500` note. |
| `E338` | Output guard reads disallowed source | A guarded output item reads a workflow-local binding, emitted output field, undeclared runtime name, or other disallowed expression source instead of only declared inputs, enum members, or live compiler-owned route semantics such as `route.exists` and `route.choice`, including `route.choice == OutputSchema.route_field.choice_key` on routed final outputs. |
| `E339` | Routed next_owner field is not structurally bound | A route-only output includes a `next_owner` field, but that field does not structurally bind the routed target. |
| `E340` | Standalone read references guarded output detail | A `standalone_read` section structurally references guarded output detail that may be absent when the guard is false. |
| `E341` | Mode value outside enum | A workflow-law `mode` binding resolved to a value outside the referenced enum. |
| `E342` | Non-exhaustive mode match | A workflow-law `match` on an enum omitted one or more members without `else`. |
| `E343` | Multiple route-bearing control surfaces are live | More than one live route-bearing surface, such as `workflow` law, `handoff_routing` law, or `final_output.route:`, would supply shared `route.*` truth for the same concrete turn. |
| `E344` | `handoff_routing` law uses a non-routing statement | `handoff_routing` law used something outside its route-only subset, such as `current artifact`, `current none`, `own only`, `preserve`, or `invalidate`. |
| `E345` | Law is not allowed on this authored slot | `law:` was attached to an authored slot other than `workflow:` or `handoff_routing:`. |
| `E346` | `route_from` selector reads invalid source | A `route_from` selector was not one direct ref to a declared input field, an emitted output field on the concrete turn, or an enum member. |
| `E347` | Route detail needs one selected branch | `route.label` or `route.summary` was read while more than one route branch still stayed live. |
| `E348` | Duplicate `route_from` arm | A `route_from` block named the same enum member twice or used `else` more than once. |
| `E351` | Owned scope is outside the allowed modeled surface | `own only` points at a path that is not rooted in the current artifact, an emitted output surface the concrete turn owns, or a declared schema family. |
| `E352` | Owned scope target is unknown | `own only` points at something that does not resolve to a declared or bound concrete-turn input or output or a declared schema family. |
| `E353` | Owned scope overlaps exact preservation | `own only` overlaps `preserve exact` without an explicit `except`. |
| `E354` | Owned scope overlaps forbidden scope | `own only` overlaps `forbid`. |
| `E355` | Preserve target is unknown | `preserve exact`, `preserve structure`, `preserve decisions`, `preserve mapping`, or `preserve vocabulary` points at a target outside its allowed modeled surface, including schema-family and grounding roots where those kinds are supported. |
| `E361` | Current artifact ignored for truth | The current artifact is also ignored for truth in the same active branch. |
| `E362` | Comparison-only basis contradiction | `support_only ... for comparison` and `ignore ... for comparison` contradict each other. |
| `E371` | Current artifact invalidated in same branch | The current artifact is invalidated in the same active branch that declares it current. |
| `E372` | Invalidation carrier field missing from trust surface | An `invalidate ... via ...` carrier field is not listed in the output's `trust_surface`. |
| `E373` | Invalidation target is unknown | `invalidate` points at something that is not a declared or bound concrete-turn input, output, or schema group. |
| `E381` | Inherited law requires named sections | An inherited workflow-law block mixed bare statements with section patching. |
| `E382` | Duplicate inherited law subsection | An inherited workflow-law block accounted for the same parent subsection more than once. |
| `E383` | Missing inherited law subsection | An inherited workflow-law block omitted one or more required parent subsections. |
| `E384` | Cannot override undefined law subsection | `override <section_key>:` targeted a law subsection the parent workflow does not define. |

### Review codes

| Code | Stage | Summary | Notes |
| --- | --- | --- | --- |
| `E469` | compile | Review current artifact is outside the review subject set | `current artifact ... via ...` pointed at something other than a declared review subject or an emitted output. |
| `E470` | compile | Invalid review declaration shape | Review inheritance, `review_family` authoring, case-selected review-family selection, `subject_map` authoring, or explicit review patching used an invalid structural shape, such as a review cycle, a missing inherited review family, overlapping or non-exhaustive cases, a duplicate `subject_map` entry, or a kind-mismatched override. Grow the selector enum and the case list together — see the "Growing A Case Family" section of `doctrine-learn/references/reviews.md`. |
| `E471` | parse | Illegal statement placement in review body | A review statement appeared in the wrong section family, such as `block` inside `on_accept` or `route` inside a pre-outcome review section. |
| `E472` | parse | Invalid guarded match head | A review `match` head used an invalid guarded fallback shape, such as `else when ...`. |
| `E473` | compile | Review fields surface is invalid or incomplete | The required `fields:` binding surface is missing or does not bind every required semantic channel. |
| `E474` | compile | Review is missing subject | A concrete review omitted `subject:`. |
| `E475` | compile | Review subject has the wrong kind | `subject:` must resolve only to declared `input` or `output` roots. |
| `E476` | compile | Review is missing contract | A concrete review omitted `contract:`. |
| `E477` | compile | Review contract target or gate ref is invalid | The referenced contract workflow or schema is invalid for review semantics, such as exporting no gates, or the review names an unknown `contract.<gate>` identity. |
| `E478` | compile | Review is missing comment_output | A concrete review omitted `comment_output:`. |
| `E479` | compile | Review comment_output is not emitted | The concrete agent does not emit the review's declared `comment_output`. |
| `E480` | compile | Concrete agent defines both workflow and review | A concrete agent may not attach both `workflow:` and `review:`. |
| `E481` | compile | Review is missing accept | A concrete review must define exactly one `accept` gate, and none were found. |
| `E482` | compile | Review has multiple accept gates | A concrete review defined more than one `accept` gate. |
| `E483` | compile | Review is missing a reserved outcome section | A concrete review is missing `on_accept` or `on_reject`. |
| `E484` | compile | Review outcome is not total | A review outcome branch or review `match` does not cover every reachable path. |
| `E485` | compile | Review outcome resolves more than one route | One terminal review outcome branch leaves more than one route live. |
| `E486` | compile | Review outcome resolves more than one currentness result | One terminal review outcome branch leaves more than one currentness result live. |
| `E487` | compile | Review currentness requires a valid carrier | `current artifact ... via ...` must carry through a declared or bound concrete-turn output field. |
| `E488` | compile | Review current carrier is missing from trust surface | The review currentness carrier field is not listed in `trust_surface`. |
| `E489` | compile | Review subject set requires disambiguation | A multi-subject review branch does not prove exactly one live reviewed subject. |
| `E490` | compile | Missing inherited review entry | A child review failed to account for an inherited review surface such as `fields` or a named pre-outcome section. |
| `E491` | compile | Duplicate review item key | A review body repeats the same reserved or named review item key. |
| `E492` | compile | Review override requires an inherited review | `override` was used on a review body that does not inherit a parent review. |
| `E493` | compile | Carried review field is missing a binding | A carried semantic channel such as `active_mode` or `trigger_reason` has no `fields:` binding. |
| `E494` | compile | Concrete agent may not attach abstract review directly | A concrete agent pointed `review:` at an `abstract review`. |
| `E495` | compile | Review verdict does not match the bound output field | The bound verdict field is not guaranteed to receive the resolved semantic verdict. |
| `E496` | compile | Review next owner does not match the bound output field | The bound `next_owner` field does not stay aligned with the resolved routed owner. |
| `E497` | compile | Review currentness does not match the declared carrier field | The declared currentness carrier field is not guaranteed to reflect the resolved review currentness, including branches that resolve `current none`. |
| `E498` | compile | Required carried review field is omitted when semantic value exists | A carried semantic field can be live on a branch without the bound output field also being live. |
| `E499` | compile | Required conditional review output section is missing after its guard resolves true | A review-bound conditional output field or section does not stay aligned with the resolved review semantics. |
| `E500` | compile | `final_output.review_fields` is used in an invalid place | Review-field bindings were used on a non-review agent. Carrier-mode review-driven agents may opt into `review_fields:` as explicit structural validation; bindings that reference a field missing from the carrier fail loud through the normal unknown-field check (`E299`). |

### Emit codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E501` | Unknown emit target | The requested emit target is not defined in `pyproject.toml`. |
| `E502` | Emit target has no concrete agents | The emit entrypoint parses, but it does not contain any concrete agents to render. |
| `E503` | Missing emit targets | `pyproject.toml` does not define any `[tool.doctrine.emit.targets]`. |
| `E504` | Missing `pyproject.toml` | The emit command could not find a config file to load. |
| `E505` | Emit target path collision | Two rendered agents map to the same output path. |
| `E506` | Invalid emit config TOML | The emit config file exists, but it is not valid TOML. |
| `E507` | Emit config path must point at `pyproject.toml` | The CLI was given a config path that does not end in `pyproject.toml`. |
| `E508` | Emit target must be a TOML table | One `targets` entry has the wrong TOML type. |
| `E509` | Duplicate emit target name | Two emit targets use the same configured name. |
| `E510` | Emit target entrypoint must match the emitter surface | `emit_docs` accepts `AGENTS.prompt` or `SOUL.prompt`, `emit_skill` accepts `SKILL.prompt`, and each emitter rejects unsupported prompt filenames. |
| `E511` | Emit target output_dir is a file | The configured output directory path is already a file. |
| `E512` | Emit config path does not exist | A configured emit entrypoint or referenced path does not exist. |
| `E513` | Emit config value must be a string | A required emit config field has the wrong TOML type. |
| `E514` | Could not resolve prompts root | The emit pipeline could not resolve the owning `prompts/` root for an entrypoint. |
| `E515` | Pinned D2 dependency is unavailable | `emit_flow` could not find the pinned repo-local D2 dependency needed for same-command SVG rendering. |
| `E516` | Pinned D2 renderer failed | `emit_flow` produced `.flow.d2`, but the pinned D2 renderer failed while producing `.flow.svg`. |
| `E517` | Emit flow CLI requires exactly one resolution mode | `emit_flow` was invoked with both configured-target mode and direct mode, or with neither mode. |
| `E518` | Direct emit flow mode requires entrypoint and output_dir | Direct `emit_flow` mode omitted either `--entrypoint` or `--output-dir`. |
| `E520` | Emit target output_dir must stay within project root | A configured or direct emit output directory resolved outside the owning project's root. |
| `E521` | Emit target entrypoint must stay within project root | A configured emit target resolved its entrypoint outside the owning project's root. |
| `E522` | Invalid release version | A Doctrine release tag or channel input does not match the shipped release-tag rules. |
| `E523` | Missing current language version | `docs/VERSIONING.md` does not expose one parseable current Doctrine language version. |
| `E524` | Invalid language version move | The requested Doctrine language version move does not match the chosen release class. |
| `E525` | Invalid release version move | The requested Doctrine release version bump does not match the chosen release class. |
| `E526` | Release changelog entry is missing or incomplete | `CHANGELOG.md` is missing the required release section or fixed release header fields. |
| `E527` | Release tag preflight failed | Release tagging could not continue because git state or tag operations failed. |
| `E528` | Release tag signing is not configured | Doctrine could not find the git signing key needed for signed public tags. |
| `E529` | GitHub release command failed | GitHub draft or publish release commands failed. |
| `E530` | Release package metadata version is missing or does not match | `pyproject.toml` is missing a usable `[project].version`, or that version does not match the requested public release's package version. |
| `E531` | Review case override removes or modifies a gate that the contract does not declare | A review case's `override gates:` block tries to `remove` or `modify` a gate name that the case's contract does not declare (or that a prior `remove` already deleted). |
| `E532` | Review case override adds or modifies a gate that collides with an existing name | A review case's `override gates:` block tries to `add` a gate name that is already declared by the contract (after `remove` entries apply), or declares the same `modify` target twice. |
| `E533` | Typed output target references a non-document/schema/table entity | An `output target`'s `typed_as:` ref resolved to an entity kind other than `document`, `schema`, or `table`. |
| `E534` | Downstream structure family does not match typed output target family | An `output` declaration's `structure:` or `schema:` points at an entity whose family does not match the target's `typed_as:` family. |
| `E535` | Receipt host slot must declare at least one typed field | A `receipt` host slot in a skill package's `host_contract:` was declared without fields, declared two fields that share the same key, or declared the same slot key twice. |
| `E536` | Receipt field reference does not resolve | A dotted addressable reference through a skill binding's receipt slot names a field the receipt host slot does not declare. |
| `E537` | Receipt field type is not a declared entity | A `receipt` host slot field was typed with a name that is not a declared `schema`, `table`, `enum`, or `document` in scope. |
| `E538` | Concrete agent binds typed abstract slot to a wrong-family entity | A concrete agent binds a typed abstract slot to a `name_ref` whose entity family does not match the abstract declaration, or binds the slot with an inline workflow block instead of a `name_ref`. |
| `E539` | Typed abstract slot annotation references an unknown entity | An `abstract` slot declaration's `: <TypedEntityRef>` annotation does not resolve to a declared `document`, `schema`, `table`, `enum`, `agent`, or `workflow`. |
| `E540` | Skill-binding mode reference does not resolve | A skill entry's `mode CNAME = expr as <Enum>` targets an enum name that does not resolve in scope. |
| `E541` | Audit-mode skill binding emits to an output target | A skill entry tagged with `mode audit = ...` bound its skill to a host slot in the `output` or `final_output` family. Audit-mode bindings must stay read-only. |
| `E542` | Skill package has no contract for the declared mode | A skill entry's `mode CNAME = ...` names a mode whose `CNAME` is not a member of the declared enum. |
| `E543` | Deprecated enum-only output-shape mode form | An output shape's `selector:` still uses the enum-only `mode CNAME as <Enum>` form. Use the expr-based `mode CNAME = expr as <Enum>` form; the enum-only form will be removed at the next minor bump. |
| `E544` | Invalid receipt declaration | A top-level `receipt` declaration is invalid. Triggers include: an empty receipt body, duplicate field keys, an `inherit` or `override` line with no parent receipt, an `inherit`/`override` line that names a field the parent does not declare, a child that redeclares an inherited field without `inherit` or `override`, missing accounting for an inherited field, a receipt inheritance cycle, a receipt-of-receipt field cycle, a field type that is not a builtin scalar (`string`, `integer`, `number`, `boolean`) and not a declared `receipt`, `enum`, `table`, or `schema`, or a duplicate route field or duplicate route choice on a receipt route field. |
| `E545` | Receipt-by-reference slot does not resolve | A skill package `host_contract:` declares `receipt key: <ReceiptRef>` but the ref does not point at a top-level `receipt` declaration in scope. |
| `E546` | Stage owner is not a declared skill | A top-level `stage` declaration's `owner:` ref does not resolve to a declared `skill`. |
| `E547` | Stage support is not a declared skill | A top-level `stage` declaration's `supports:` entry does not resolve to a declared `skill`. |
| `E548` | Stage input type is invalid | A top-level `stage` declaration's `inputs:` value does not resolve to a top-level `receipt`, `document`, `schema`, or `table`. |
| `E549` | Stage emit type is invalid | A top-level `stage` declaration's `emits:` value does not resolve to a top-level `receipt`. |
| `E550` | Emit target `source_root` must be a directory | A configured skill emit target declares `source_root`, but the path is not an existing directory. |
| `E551` | Emit target source id/root pair is incomplete | A configured skill emit target declares `source_root` without `source_id`, or `source_id` without `source_root`. |
| `E552` | Emit target entrypoint must stay within `source_root` | A configured skill emit target uses external source mode, but its entrypoint is outside the configured source root. |
| `E553` | Emit target `lock_file` path is invalid | A configured skill emit target points `lock_file` at a directory or places it inside the emitted skill tree. |
| `E554` | Missing skill source receipt or tracked source path | Receipt verification could not find `SKILL.source.json`, or `emit_skill` could not find a tracked source path. |
| `E555` | Invalid skill source receipt | `SKILL.source.json` exists, but it is not a JSON object. |
| `E556` | Invalid tracked source path | A `source.track:` path is absolute, uses `..`, uses backslashes, or leaves the receipt source root. |
| `E557` | Invalid skill lock file | A configured `lock_file` exists, but it is not valid TOML or does not use the expected target table shape. |
| `E558` | Emit target must resolve one skill package | `emit_skill` reached an internal mismatch after compilation and could not identify exactly one package declaration for the receipt. |
| `E559` | Invalid stage declaration | A top-level `stage` declaration is structurally invalid. Triggers include: missing `owner:`, missing `intent:`, missing `advance_condition:`, a duplicate stage scalar field, a duplicate `supports:` entry, a `supports:` entry that repeats the stage owner, a duplicate `applies_to:` block, an `applies_to:` ref that does not resolve to a top-level `skill_flow`, a duplicate resolved flow under `applies_to:`, a duplicate `inputs:` key, a `lane:` value that is not a declared enum member, a `checkpoint:` value outside the closed set (`durable`, `review_only`, `diagnostic`, `none`), or a durable-checkpoint stage missing `durable_target:` or `durable_evidence:`. |
| `E560` | Receipt route target is invalid | A receipt `route <field>:` choice points at `stage <Name>` or `flow <Name>` and the named declaration is not in scope. The closed sentinel set (`human`, `external`, `terminal`) is enforced by the parser. |
| `E561` | Invalid skill flow | A top-level `skill_flow` passed parse, but compile-time flow validation failed. Triggers include: a duplicate `intent:`, `start:`, `approve:`, or `changed_workflow:` block; a `start:`, edge source, edge target, or `repeat` target ref that does not resolve to a top-level `stage`, top-level `skill_flow`, or a local repeat name; an edge whose source and target are the same node; edges that form a local cycle; an edge `kind:` outside the closed `normal`/`review`/`repair`/`recovery`/`approval`/`handoff` set; an edge `route:` whose receipt, route field, or choice does not resolve, or whose choice target does not match the edge target; a routed source stage whose outgoing edge to a route-named target lacks the required `route:` binding (sub-plan 3 has no `allow unbound_edges` policy); a `when:` or `safe_when:` ref that does not resolve to a declared enum member; a source whose branch edges mix enum families, duplicate a member, or fail to cover every member; an `approve:` ref that does not resolve to a top-level `skill_flow`; a `repeat` name that shadows a top-level `stage`, top-level `skill_flow`, or another repeat in the same flow; a duplicate `repeat`, `variation`, or `unsafe` name; a repeat `over:` that does not resolve to a top-level `enum`, `table`, or `schema`; a repeat `order:` outside the closed `serial`/`parallel`/`unspecified` set; or a `changed_workflow:` `require` outside the closed `nearest_flow`/`difference`/`safety_rationale` set. Parser-owned `skill_flow` shape errors still use parse `E199`. Receipt route target resolution still uses `E560`; emit-target source-id/root pairing keeps `E551` and `E552`. |
| `E562` | Invalid skill graph | A top-level `skill_graph` passed parse, but graph closure failed. Triggers include: duplicate `purpose:` / `roots:` / `sets:` / `recovery:` / `policy:` / `views:` blocks; a missing required `purpose:` or `roots:` block; a root that does not resolve to a top-level `stage` or `skill_flow`; a duplicate root or graph-set name; a recovery ref that is missing or wrong-kind; an unsupported strict or warning policy key; a repeat `over:` that only resolves as a graph-set candidate but names no declared graph set; a reached stage whose `applies_to:` list does not include every reaching flow; `require stage_lane` on a reached stage with no `lane:`; or an expanded cross-flow stage cycle. |
| `E563` | Invalid skill graph target | `emit_skill_graph`, `verify_skill_graph`, or the public graph compile path could not pick one visible graph. Triggers include: a missing requested graph name, an unknown requested graph name, or an entrypoint that exposes more than one graph when the caller did not choose one explicitly. |
| `E564` | Invalid skill graph view path | A graph emit target declared an unsupported graph view key, mapped two graph views to the same output path, or resolved a graph view outside the target output directory. |
| `E565` | Skill graph emit failed | `emit_skill_graph` could not finish graph output. Triggers include: a graph target that reaches no stages or flows, a missing or invalid graph source receipt, or a pinned D2 render failure while writing the graph SVG. |
| `E599` | Emit failure | Generic fallback emit code when the failure does not fit a narrower shipped emit code yet. |

### Internal codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E901` | Internal compiler error | The compiler hit an invariant failure or unsupported internal state. Treat this as a compiler bug. |
| `E999` | Unclassified Doctrine error | Fallback code when a `DoctrineError` is raised without a more specific stage. Reached only when no narrower parse, compile, or emit code applies. Treat this as a compiler bug. |

### Rule-check codes

The `RULE###` band covers diagnostics raised by the declarative `rule` primitive
described in [`LANGUAGE_REFERENCE.md`](./LANGUAGE_REFERENCE.md). Rule checks run
during compile and share the same error envelope as the `E###` codes.

| Code | Summary | Notes |
| --- | --- | --- |
| `RULE001` | Rule declaration references an unknown scope predicate target | A rule's `scope:` predicate names a `flow: <agent>` whose target agent is not declared in the prompt graph. |
| `RULE002` | Rule assertion target does not resolve | A rule's `assertions:` block references an agent (for `requires inherit` or `forbids bind`) that is not declared in the prompt graph. |
| `RULE003` | Scoped agent fails `requires inherit` assertion | A concrete agent that matches the rule's `scope:` predicates does not inherit the required ancestor named in `requires inherit`. |
| `RULE004` | Scoped agent violates `forbids bind` assertion | A concrete agent that matches the rule's `scope:` predicates inherits from an ancestor that the rule forbids via `forbids bind`. |
| `RULE005` | Scoped agent fails `requires declare` assertion | A concrete agent that matches the rule's `scope:` predicates does not declare (or inherit) the slot named in `requires declare`. |

The rule primitive ships a closed predicate set: scope predicates are limited to
`agent_tag: <CNAME>`, `flow: <NameRef>`, `role_class: <CNAME>`, and
`file_tree: <STRING>`; assertions are limited to `requires inherit <NameRef>`,
`forbids bind <NameRef>`, and `requires declare <CNAME>`. Codes `RULE006` through
`RULE099` are reserved for future extensions of this closed-predicate surface.
Codes `RULE100` and above are reserved for any future open-expression-language
evolution of the rule primitive.

## Example

The checked-in error reference under
[examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md](../examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md)
shows the canonical formatted shape for one shipped compile error.
