# Compiler Errors

This document is the canonical error reference for the shipped Doctrine parser,
compiler, and emit pipeline.

The error surface is now structured first and formatted second.

Every user-facing error should carry:
- a stable code such as `E101` or `E280`
- a stage label such as `parse`, `compile`, or `emit`
- a short summary line
- optional location, source excerpt, trace, hints, and normalized cause text

The formatter order is canonical:
- first line: `CODE stage error: summary`
- then location
- then detail
- then source excerpt when we know a line and column
- then trace
- then hints
- then the normalized low-level cause

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
| `E469`-`E499` | review-specific parse and compile errors |
| `E500`-`E699` | emit and build-target errors |
| `E900`-`E999` | internal compiler bugs or invariant failures |

## Current Stable Codes

### Reserved language-rule codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E001` | Cannot override undefined inherited entry | Used when `override` tries to replace an inherited authored slot, workflow, `skills`, or named IO entry that does not exist. |
| `E002` | Missing rendered section title | Reserved meaning: a rendered section needs an explicit visible title and the source does not provide one. |
| `E003` | Missing inherited entry | Used when explicit inherited patching omits one of the inherited authored-slot, workflow, `skills`, or named IO entries. |

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
| `E199` | Parse failure | Generic fallback parse code when the failure does not fit a narrower shipped parse code yet, including parser-level output owner conflicts such as `schema:` plus `must_include:` or `schema:` plus `structure:`. |

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
| `E211` | Final output must point at output declaration | `final_output:` resolved to some declaration kind other than `output`. |
| `E212` | Final output is not emitted by the concrete turn | `final_output:` points at an `output`, but the concrete agent does not emit it through `outputs:`. |
| `E213` | Final output must designate one TurnResponse message | `final_output:` points at a file bundle or some non-`TurnResponse` target instead of one final assistant message. |
| `E214` | Retired | Reserved error code. Review-driven `final_output:` may now differ from `comment_output:`. |
| `E215` | Final output support file is missing or unreadable | A schema-backed `final_output:` declares a schema or example support file that the compiler cannot read. |
| `E216` | Final output schema file must contain a JSON object | A schema-backed `final_output:` points at a schema file that is not valid JSON object text. |
| `E220`-`E225` | Typed declaration completeness errors | These codes cover missing required typed declaration fields such as skill purpose, input source, input shape, input requirement, and output target shape combinations. |
| `E226` | Unsupported record item | A record surface contains an item kind the shipped compiler does not support there. |
| `E230`-`E235` | Config declaration and config instance errors | These codes cover invalid config item shapes, duplicate or unknown keys, missing required keys, and bad config key declarations. |
| `E240`-`E243` | Workflow inheritance and patching errors | These codes cover cyclic workflow inheritance, inheriting undefined keys, kind mismatches, and `inherit` or `override` without an inherited workflow. |
| `E244`-`E249` | IO block inheritance and typed-field ref errors | These codes cover cyclic `inputs` / `outputs` block inheritance, undefined inherited keys, patching without an inherited IO block, inherited IO blocks without stable keyed sections, and wrong-kind IO refs or patch bases. |
| `E250` | Cyclic skills inheritance | Top-level `skills` block inheritance forms a cycle. |
| `E260` | Conflicting concrete-turn binding roots | One concrete-turn bound root path resolves to different artifacts inside the same concrete turn. |
| `E261` | Duplicate workflow item key | One workflow body repeats the same keyed entry. |
| `E270` | Ambiguous declaration reference | A readable or addressable ref matches more than one visible declaration kind. |
| `E271` | Workflow ref is not allowed here | A bare workflow ref was used on a readable surface that allows declarations but not workflow roots. |
| `E272` | Abstract agent ref is not allowed here | A readable mention points at an abstract agent instead of a concrete owner. |
| `E273` | Unknown addressable path | An interpolation or addressable ref asked for a nested path that does not exist on that surface. |
| `E274` | Addressable path must stay addressable | A path tried to keep traversing after it had already reached a scalar or other non-addressable surface. |
| `E275` | Typed declaration must stay typed | A typed declaration field such as `source`, `target`, or `shape` was treated like an untyped pathable value. |
| `E276` | Missing local declaration reference | A local readable, analysis, or addressable ref points at a declaration that does not exist. |
| `E280` | Missing import module | An imported module could not be found in the active import-root registry. |
| `E281` | Missing imported declaration | The imported module resolved, but the requested declaration does not exist there. |
| `E282` | Route target must be a concrete agent | A route points at an abstract or otherwise invalid target. |
| `E283` | Cyclic workflow composition | `use`-based workflow composition forms a cycle. |
| `E284` | Duplicate record key | A record body repeats the same key where the current surface expects uniqueness. |
| `E285` | Invalid compile config | The nearest Doctrine compile config is structurally invalid, such as a non-table `[tool.doctrine.compile]` or a bad `additional_prompt_roots` entry. |
| `E286` | Duplicate configured prompts root | A configured additional `prompts/` root resolves to the same directory more than once, including duplication of the entrypoint-local root. |
| `E287` | Ambiguous import module | An absolute import matches the same dotted module path in more than one configured `prompts/` root. |
| `E288` | Duplicate declaration name | One module defines the same declaration name more than once. |
| `E289` | Cyclic import module | Import resolution forms a module cycle. |
| `E290` | Relative import walks above prompts root | A relative import escapes above the current `prompts/` root. |
| `E291` | Prompt source path is required for compilation | The compiler was asked to compile a prompt object without a source path. |
| `E292` | Could not resolve prompts root | The compiler could not find the owning `prompts/` root for the current prompt file path. |
| `E293` | Duplicate enum member key | One `enum` body repeats the same member key. |
| `E294` | Duplicate enum member wire | One `enum` body repeats the same host-facing `wire` value. |
| `E295` | Duplicate readable key | A readable surface repeats a keyed child such as a document block, properties entry, inline schema entry, footnote, or table child. |
| `E296` | Readable guard reads disallowed source | A readable `when` guard reads emitted output fields or other disallowed sources instead of only declared inputs and enum members. |
| `E297` | Invalid readable block structure | A readable block uses an invalid structural shape, such as an unknown callout kind, single-line raw/code text, an empty table, or a multiline inline table cell. |
| `E298` | Invalid render_profile declaration | A `render_profile` declares an unknown target, unsupported mode, or duplicate target rule. |
| `E299` | Compile failure | Generic fallback compile code when the failure does not fit a narrower shipped compile code yet. No shipped manifest-backed compile-fail case currently depends on `E299`. |
| `E301` | Invalid IO bucket item | An `inputs:` or `outputs:` bucket contains an invalid item shape, inline declaration body, or wrong-kind declaration ref. |
| `E302` | Invalid output attachment declaration | An output attaches an invalid `schema:` or `structure:` surface, such as a sectionless schema or a non-markdown structure target. |
| `E303` | Invalid schema declaration | A schema artifact or schema group uses an invalid declaration shape, such as a wrong-kind artifact ref, an unknown group member, or an empty group. |
| `E305` | Invalid document inheritance patch | A document inheritance patch uses the wrong override shape, such as a kind mismatch or a patch without an inherited document parent. |
| `E331` | Missing current-subject form | An active workflow-law leaf branch did not resolve either `current artifact ... via ...` or `current none`. |
| `E332` | Multiple current-subject forms | One active workflow-law leaf branch declared more than one current subject. |
| `E333` | Current carrier output not emitted | The output carrying current truth is not emitted by the concrete turn. |
| `E334` | Current output not emitted | A workflow-law current artifact points at an output the concrete turn does not emit. |
| `E335` | Current artifact target has wrong kind | A `current artifact` target does not resolve to a declared or bound concrete-turn input or output. |
| `E336` | Current carrier field missing from trust surface | A currentness carrier field is not listed in the target output's `trust_surface`. |
| `E337` | Unknown current carrier field | A `current artifact ... via ...` carrier points at an unknown output field. |
| `E338` | Output guard reads disallowed source | A guarded output item reads a workflow-local binding, emitted output field, undeclared runtime name, or other disallowed expression source instead of only declared inputs, enum members, or live compiler-owned route semantics such as `route.exists` and `route.choice`. |
| `E339` | Routed next_owner field is not structurally bound | A route-only output includes a `next_owner` field, but that field does not structurally bind the routed target. |
| `E340` | Standalone read references guarded output detail | A `standalone_read` section structurally references guarded output detail that may be absent when the guard is false. |
| `E341` | Mode value outside enum | A workflow-law `mode` binding resolved to a value outside the referenced enum. |
| `E342` | Non-exhaustive mode match | A workflow-law `match` on an enum omitted one or more members without `else`. |
| `E343` | Multiple route-bearing control surfaces are live | More than one live route-bearing surface, such as `workflow` law and `handoff_routing` law, would supply shared `route.*` truth for the same concrete turn. |
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
| `E470` | compile | Invalid review declaration shape | Review inheritance, `review_family` authoring, case-selected review-family selection, `subject_map` authoring, or explicit review patching used an invalid structural shape, such as a review cycle, a missing inherited review family, overlapping or non-exhaustive cases, a duplicate `subject_map` entry, or a kind-mismatched override. |
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
| `E510` | Emit target entrypoint must be `AGENTS.prompt` or `SOUL.prompt` | An emit target points at an unsupported prompt filename. |
| `E511` | Emit target output_dir is a file | The configured output directory path is already a file. |
| `E512` | Emit config path does not exist | A configured emit entrypoint or referenced path does not exist. |
| `E513` | Emit config value must be a string | A required emit config field has the wrong TOML type. |
| `E514` | Could not resolve prompts root | The emit pipeline could not resolve the owning `prompts/` root for an entrypoint. |
| `E515` | Pinned D2 dependency is unavailable | `emit_flow` could not find the pinned repo-local D2 dependency needed for same-command SVG rendering. |
| `E516` | Pinned D2 renderer failed | `emit_flow` produced `.flow.d2`, but the pinned D2 renderer failed while producing `.flow.svg`. |
| `E517` | Emit flow CLI requires exactly one resolution mode | `emit_flow` was invoked with both configured-target mode and direct mode, or with neither mode. |
| `E518` | Direct emit flow mode requires entrypoint and output_dir | Direct `emit_flow` mode omitted either `--entrypoint` or `--output-dir`. |
| `E519` | Emit contract support file must stay within project root | A machine-readable emitted contract resolved its entrypoint or final-output support file outside the target project's root. |
| `E520` | Emit target output_dir must stay within project root | A configured or direct emit output directory resolved outside the owning project's root. |
| `E599` | Emit failure | Generic fallback emit code when the failure does not fit a narrower shipped emit code yet. |

### Internal codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E901` | Internal compiler error | The compiler hit an invariant failure or unsupported internal state. Treat this as a compiler bug. |

## Example

The checked-in error reference under
[examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md](../examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md)
shows the canonical formatted shape for one shipped compile error.
