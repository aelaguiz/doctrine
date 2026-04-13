from __future__ import annotations

import re
from typing import Callable

_PatternBuilder = tuple[
    re.Pattern[str],
    str,
    str,
    Callable[[re.Match[str]], str | None],
    tuple[str, ...],
]


_READABLE_MESSAGE_BUILDERS: tuple[_PatternBuilder, ...] = (
    (
        re.compile(r"^Duplicate enum member key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E293",
        "Duplicate enum member key",
        lambda match: f"Enum `{match.group('owner')}` repeats member key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Duplicate enum member wire in (?P<owner>[^:]+): (?P<wire>.+)$"),
        "E294",
        "Duplicate enum member wire",
        lambda match: f"Enum `{match.group('owner')}` repeats wire value `{match.group('wire')}`.",
        (),
    ),
    (
        re.compile(
            r"^Duplicate (?P<kind>document block|properties entry|item_schema|row_schema|definitions item|footnote|table column|table row|table row cell) key in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E295",
        "Duplicate readable key",
        lambda match: (
            f"Readable surface `{match.group('owner')}` repeats "
            f"{match.group('kind')} key `{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Readable guard reads disallowed source in (?P<owner>.+): (?P<source>.+)$"
        ),
        "E296",
        "Readable guard reads disallowed source",
        lambda match: (
            f"Readable guard in {match.group('owner')} reads disallowed source "
            f"`{match.group('source')}`."
        ),
        (
            "Read only declared inputs and enum members in readable guards.",
            "Do not read emitted output fields or workflow-local bindings inside readable `when` expressions.",
        ),
    ),
    (
        re.compile(r"^Unknown callout kind in (?P<owner>.+): (?P<kind>.+)$"),
        "E297",
        "Invalid readable block structure",
        lambda match: (
            f"Readable block `{match.group('owner')}` uses unknown callout kind "
            f"`{match.group('kind')}`."
        ),
        ("Use one of the shipped callout kinds: `required`, `important`, `warning`, or `note`.",),
    ),
    (
        re.compile(r"^Code block text must use a multiline string in (?P<owner>.+)$"),
        "E297",
        "Invalid readable block structure",
        lambda match: f"Readable code block `{match.group('owner')}` must use a multiline string.",
        ("Use a multiline string for readable code block text.",),
    ),
    (
        re.compile(r"^Raw (?P<kind>markdown|html) blocks must use a multiline string in (?P<owner>.+)$"),
        "E297",
        "Invalid readable block structure",
        lambda match: (
            f"Readable {match.group('kind')} block `{match.group('owner')}` must use a multiline string."
        ),
        ("Use a multiline string for raw markdown or html readable blocks.",),
    ),
    (
        re.compile(r"^Readable table must declare at least one column in (?P<owner>.+)$"),
        "E297",
        "Invalid readable block structure",
        lambda match: f"Readable table `{match.group('owner')}` must declare at least one column.",
        ("Declare at least one table column before rows or notes.",),
    ),
    (
        re.compile(
            r"^Readable table inline cells must stay single-line in (?P<owner>.+); nested tables require structured cell bodies\.$"
        ),
        "E297",
        "Invalid readable block structure",
        lambda match: (
            f"Readable table inline cell `{match.group('owner')}` must stay single-line unless "
            "it uses a structured cell body."
        ),
        (
            "Move multi-line cell content into a structured cell body instead of an inline table cell.",
        ),
    ),
    (
        re.compile(r"^Unknown render_profile target in (?P<owner>.+): (?P<target>.+)$"),
        "E298",
        "Invalid render_profile declaration",
        lambda match: (
            f"Render profile `{match.group('owner')}` targets unsupported surface "
            f"`{match.group('target')}`."
        ),
        ("Use only shipped render_profile targets.",),
    ),
    (
        re.compile(r"^Unknown render_profile mode in (?P<owner>.+): (?P<mode>.+)$"),
        "E298",
        "Invalid render_profile declaration",
        lambda match: (
            f"Render profile `{match.group('owner')}` uses unknown mode "
            f"`{match.group('mode')}`."
        ),
        ("Use only shipped render_profile modes.",),
    ),
    (
        re.compile(
            r"^Invalid render_profile mode for (?P<target>.+) in (?P<owner>.+): (?P<mode>.+)$"
        ),
        "E298",
        "Invalid render_profile declaration",
        lambda match: (
            f"Render profile `{match.group('owner')}` cannot use mode "
            f"`{match.group('mode')}` for target `{match.group('target')}`."
        ),
        ("Keep each render_profile target on one of its shipped supported modes.",),
    ),
    (
        re.compile(
            r"^Duplicate render_profile rule target in (?P<owner>.+): (?P<target>.+)$"
        ),
        "E298",
        "Invalid render_profile declaration",
        lambda match: (
            f"Render profile `{match.group('owner')}` repeats target "
            f"`{match.group('target')}`."
        ),
        ("Declare each render_profile target at most once.",),
    ),
    (
        re.compile(r"^Scalar keyed items are not allowed in (?P<owner>.+): (?P<key>.+)$"),
        "E301",
        "Invalid IO bucket item",
        lambda match: (
            f"IO bucket `{match.group('owner')}` cannot contain scalar keyed item "
            f"`{match.group('key')}`."
        ),
        ("Keep inputs and outputs buckets limited to declaration refs or titled groups.",),
    ),
    (
        re.compile(
            r"^Declaration refs cannot define inline bodies in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E301",
        "Invalid IO bucket item",
        lambda match: (
            f"Declaration ref `{match.group('name')}` in IO bucket `{match.group('owner')}` "
            "cannot define an inline body."
        ),
        (
            "Keep declaration refs bare inside inputs and outputs buckets.",
            "Use a titled group when you need nested prose around multiple declarations.",
        ),
    ),
    (
        re.compile(
            r"^Inputs refs must resolve to input declarations, not output declarations: (?P<name>.+)$"
        ),
        "E301",
        "Invalid IO bucket item",
        lambda match: (
            f"Input bucket ref `{match.group('name')}` must resolve to an input declaration."
        ),
        (),
    ),
    (
        re.compile(
            r"^Outputs refs must resolve to output declarations, not input declarations: (?P<name>.+)$"
        ),
        "E301",
        "Invalid IO bucket item",
        lambda match: (
            f"Output bucket ref `{match.group('name')}` must resolve to an output declaration."
        ),
        (),
    ),
    (
        re.compile(
            r"^Output-attached schema must export at least one section in output (?P<output>.+): (?P<schema>.+)$"
        ),
        "E302",
        "Invalid output attachment declaration",
        lambda match: (
            f"Output `{match.group('output')}` attaches schema `{match.group('schema')}`, "
            "but that schema does not export any sections."
        ),
        (),
    ),
    (
        re.compile(
            r"^Output structure requires one markdown-bearing output artifact in (?P<output>.+)$"
        ),
        "E302",
        "Invalid output attachment declaration",
        lambda match: (
            f"Output `{match.group('output')}` must expose exactly one markdown-bearing artifact "
            "before it can attach `structure:`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Output structure requires a markdown-bearing shape in output (?P<output>.+)$"
        ),
        "E302",
        "Invalid output attachment declaration",
        lambda match: (
            f"Output `{match.group('output')}` must use a markdown-bearing shape before it can "
            "attach `structure:`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Schema artifact refs must resolve to input or output declarations in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E303",
        "Invalid schema declaration",
        lambda match: (
            f"Schema `{match.group('owner')}` artifact ref `{match.group('name')}` must resolve "
            "to an input or output declaration."
        ),
        (),
    ),
    (
        re.compile(r"^Unknown schema group member in (?P<owner>.+): (?P<path>.+)$"),
        "E303",
        "Invalid schema declaration",
        lambda match: (
            f"Schema `{match.group('owner')}` group member `{match.group('path')}` does not "
            "match any declared local schema artifact."
        ),
        (),
    ),
    (
        re.compile(r"^Schema groups may not be empty in (?P<owner>.+): (?P<key>.+)$"),
        "E303",
        "Invalid schema declaration",
        lambda match: (
            f"Schema `{match.group('owner')}` group `{match.group('key')}` must contain at least "
            "one artifact."
        ),
        (),
    ),
    (
        re.compile(
            r"^Override kind mismatch for document entry in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E305",
        "Invalid document inheritance patch",
        lambda match: (
            f"Document `{match.group('owner')}` overrides entry `{match.group('key')}` with the "
            "wrong block kind."
        ),
        (),
    ),
    (
        re.compile(
            r"^Inherited document requires `override (?P<key>.+)` in (?P<owner>.+)$"
        ),
        "E305",
        "Invalid document inheritance patch",
        lambda match: (
            f"Document `{match.group('owner')}` must use `override {match.group('key')}` when it "
            "patches an inherited document block."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?P<action>inherit|override) requires an inherited document declaration in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E305",
        "Invalid document inheritance patch",
        lambda match: (
            f"`{match.group('action')}` for document entry `{match.group('key')}` requires an "
            f"inherited document declaration in `{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot inherit undefined document entry in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E305",
        "Invalid document inheritance patch",
        lambda match: (
            f"Document `{match.group('owner')}` cannot inherit undefined entry "
            f"`{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Cyclic import module: (?P<detail>.+)$"),
        "E289",
        "Cyclic import module",
        lambda match: f"Import cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Relative import walks above prompts root: (?P<detail>.+)$"),
        "E290",
        "Relative import walks above prompts root",
        lambda match: f"Import `{match.group('detail')}` walks above the prompts root.",
        (),
    ),
    (
        re.compile(r"^Input source must stay typed(?:(?: in interpolation))?: (?P<name>.+)$"),
        "E275",
        "Input source must stay typed",
        lambda match: f"Input `{match.group('name')}` must keep a typed `source`.",
        (),
    ),
    (
        re.compile(r"^Output target must stay typed(?:(?: in interpolation))?: (?P<name>.+)$"),
        "E275",
        "Output target must stay typed",
        lambda match: f"Output `{match.group('name')}` must keep a typed `target`.",
        (),
    ),
    (
        re.compile(r"^Output shape must stay typed: (?P<name>.+)$"),
        "E275",
        "Output shape must stay typed",
        lambda match: f"Output `{match.group('name')}` must keep a typed `shape`.",
        (),
    ),
    (
        re.compile(r"^Prompt source path is required for compilation\.$"),
        "E291",
        "Prompt source path is required for compilation",
        lambda _match: "Prompt source path is required for compilation.",
        (),
    ),
)
