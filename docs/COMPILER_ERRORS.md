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
| `E200`-`E499` | semantic compile errors |
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
| `E199` | Parse failure | Generic fallback parse code when the failure does not fit a narrower shipped parse code yet. |

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
| `E220`-`E225` | Typed declaration completeness errors | These codes cover missing required typed declaration fields such as skill purpose, input source, input shape, input requirement, and output target shape combinations. |
| `E226` | Unsupported record item | A record surface contains an item kind the shipped compiler does not support there. |
| `E230`-`E235` | Config declaration and config instance errors | These codes cover invalid config item shapes, duplicate or unknown keys, missing required keys, and bad config key declarations. |
| `E240`-`E243` | Workflow inheritance and patching errors | These codes cover cyclic workflow inheritance, inheriting undefined keys, kind mismatches, and `inherit` or `override` without an inherited workflow. |
| `E244`-`E249` | IO block inheritance and typed-field ref errors | These codes cover cyclic `inputs` / `outputs` block inheritance, undefined inherited keys, patching without an inherited IO block, inherited IO blocks without stable keyed sections, and wrong-kind IO refs or patch bases. |
| `E250` | Cyclic skills inheritance | Top-level `skills` block inheritance forms a cycle. |
| `E261` | Duplicate workflow item key | One workflow body repeats the same keyed entry. |
| `E270` | Ambiguous declaration reference | A readable or addressable ref matches more than one visible declaration kind. |
| `E271` | Workflow ref is not allowed here | A bare workflow ref was used on a readable surface that allows declarations but not workflow roots. |
| `E272` | Abstract agent ref is not allowed here | A readable mention points at an abstract agent instead of a concrete owner. |
| `E273` | Unknown addressable path | An interpolation or addressable ref asked for a nested path that does not exist on that surface. |
| `E274` | Addressable path must stay addressable | A path tried to keep traversing after it had already reached a scalar or other non-addressable surface. |
| `E275` | Typed declaration must stay typed | A typed declaration field such as `source`, `target`, or `shape` was treated like an untyped pathable value. |
| `E276` | Missing local declaration reference | A local readable or addressable ref points at a declaration that does not exist. |
| `E280` | Missing import module | An imported module could not be found under the current `prompts/` root. |
| `E281` | Missing imported declaration | The imported module resolved, but the requested declaration does not exist there. |
| `E282` | Route target must be a concrete agent | A route points at an abstract or otherwise invalid target. |
| `E283` | Cyclic workflow composition | `use`-based workflow composition forms a cycle. |
| `E284` | Duplicate record key | A record body repeats the same key where the current surface expects uniqueness. |
| `E288` | Duplicate declaration name | One module defines the same declaration name more than once. |
| `E289` | Cyclic import module | Import resolution forms a module cycle. |
| `E290` | Relative import walks above prompts root | A relative import escapes above the current `prompts/` root. |
| `E291` | Prompt source path is required for compilation | The compiler was asked to compile a prompt object without a source path. |
| `E292` | Could not resolve prompts root | The compiler could not find the owning `prompts/` root for the current prompt file path. |
| `E293` | Duplicate enum member key | One `enum` body repeats the same member key. |
| `E299` | Compile failure | Generic fallback compile code when the failure does not fit a narrower shipped compile code yet. |

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
| `E599` | Emit failure | Generic fallback emit code when the failure does not fit a narrower shipped emit code yet. |

### Internal codes

| Code | Summary | Notes |
| --- | --- | --- |
| `E901` | Internal compiler error | The compiler hit an invariant failure or unsupported internal state. Treat this as a compiler bug. |

## Example

The checked-in error reference under
[examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md](../examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md)
shows the canonical formatted shape for one shipped compile error.
