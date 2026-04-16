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


_AGENT_MESSAGE_BUILDERS: tuple[_PatternBuilder, ...] = (
    (
        re.compile(r"^E001 (?P<detail>.+)$"),
        "E001",
        "Cannot override undefined inherited entry",
        lambda match: match.group("detail"),
        (
            "If this entry is new, define it directly instead of using `override`.",
        ),
    ),
    (
        re.compile(r"^E003 (?P<detail>.+)$"),
        "E003",
        "Missing inherited entry",
        lambda match: match.group("detail"),
        (
            "Account for every inherited entry explicitly with `inherit` or `override`.",
        ),
    ),
    (
        re.compile(r"^Missing target agent: (?P<agent>.+)$"),
        "E201",
        "Missing target agent",
        lambda match: f"Target agent `{match.group('agent')}` does not exist in the root prompt file.",
        (),
    ),
    (
        re.compile(r"^Abstract agent does not render: (?P<agent>.+)$"),
        "E202",
        "Abstract agent does not render",
        lambda match: f"Agent `{match.group('agent')}` is marked abstract and cannot render output directly.",
        ("Render a concrete child agent instead.",),
    ),
    (
        re.compile(r"^Duplicate role field in agent (?P<agent>.+)$"),
        "E203",
        "Duplicate role field",
        lambda match: f"Agent `{match.group('agent')}` defines `role` more than once.",
        (),
    ),
    (
        re.compile(r"^Duplicate typed field in agent (?P<agent>[^:]+): (?P<field>.+)$"),
        "E204",
        "Duplicate typed field",
        lambda match: (
            f"Agent `{match.group('agent')}` defines typed field `{match.group('field')}` more than once."
        ),
        (),
    ),
    (
        re.compile(r"^Agent (?P<agent>.+) is outside the shipped subset: (?P<detail>.+)$"),
        "E206",
        "Unsupported agent field order",
        lambda match: (
            f"Agent `{match.group('agent')}` is outside the shipped subset. {match.group('detail')}"
        ),
        (),
    ),
    (
        re.compile(r"^Concrete agent is missing role field: (?P<agent>.+)$"),
        "E205",
        "Concrete agent is missing role field",
        lambda match: f"Concrete agent `{match.group('agent')}` is missing its required `role` field.",
        ("Add a `role` field before the rest of the authored workflow surface.",),
    ),
    (
        re.compile(r"^Unsupported agent field in (?P<agent>[^:]+): (?P<field>.+)$"),
        "E208",
        "Unsupported agent field",
        lambda match: f"Agent `{match.group('agent')}` uses unsupported field type `{match.group('field')}`.",
        (),
    ),
    (
        re.compile(
            r"^E209 Concrete agent is missing abstract authored slots in agent (?P<agent>[^:]+): (?P<slots>.+)$"
        ),
        "E209",
        "Concrete agent is missing abstract authored slots",
        lambda match: (
            f"Concrete agent `{match.group('agent')}` must define abstract authored slots: "
            f"{', '.join(f'`{slot.strip()}`' for slot in match.group('slots').split(','))}."
        ),
        ("Define each missing slot directly with `slot_key: ...`.",),
    ),
    (
        re.compile(
            r"^E210 Abstract authored slot in (?P<label>[^:]+) must be defined directly in agent (?P<agent>[^:]+): (?P<slot>.+)$"
        ),
        "E210",
        "Abstract authored slot must be defined directly",
        lambda match: (
            f"Agent `{match.group('agent')}` cannot satisfy abstract authored slot "
            f"`{match.group('slot')}` from {match.group('label')} with `inherit` or `override`."
        ),
        ("Define the slot directly with `slot_key: ...`.",),
    ),
    (
        re.compile(
            r"^E211 final_output must point at an output declaration in (?P<owner>[^:]+): (?P<ref>.+) resolves to (?P<kind>.+)$"
        ),
        "E211",
        "Final output must point at output declaration",
        lambda match: (
            f"`final_output` in {match.group('owner')} points at `{match.group('ref')}`, "
            f"which resolves to {match.group('kind')} instead of an `output` declaration."
        ),
        ("Point `final_output:` at a declared `output`.",),
    ),
    (
        re.compile(
            r"^E212 final_output output is not emitted by the concrete turn in agent (?P<agent>[^:]+): (?P<output>.+)$"
        ),
        "E212",
        "Final output is not emitted by the concrete turn",
        lambda match: (
            f"Agent `{match.group('agent')}` declares `final_output` as "
            f"`{match.group('output')}`, but that output is not emitted by the concrete turn."
        ),
        ("Add the output to the agent `outputs:` contract, or point `final_output:` at one that already is.",),
    ),
    (
        re.compile(
            r"^E213 final_output must designate one TurnResponse output, not files or another target, in agent (?P<agent>[^:]+): (?P<output>.+)$"
        ),
        "E213",
        "Final output must designate one TurnResponse message",
        lambda match: (
            f"Agent `{match.group('agent')}` points `final_output` at `{match.group('output')}`, "
            "but the designated output is not one `TurnResponse` assistant message."
        ),
        ("Use a typed `output` with `target: TurnResponse` and no `files:` bundle.",),
    ),
    (
        re.compile(
            r"^E500 final_output review_fields are invalid in agent (?P<agent>[^:]+): (?P<detail>.+)$"
        ),
        "E500",
        "`final_output.review_fields` is used in an invalid place",
        lambda match: (
            f"Agent `{match.group('agent')}` uses `final_output.review_fields` in an invalid place. "
            f"{match.group('detail')}"
        ),
        (
            "Use `review_fields:` only on split final responses for review-driven agents.",
        ),
    ),
    (
        re.compile(
            r"^E215 final_output example_file is retired in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E215",
        "Final output example_file is retired",
        lambda match: (
            f"`final_output` in {match.group('owner')} still uses retired "
            f"`example_file`. {match.group('detail')}"
        ),
        (
            "Delete `example_file` from the `output shape`.",
            "Add `example:` on `output schema` only when you want a rendered example block.",
        ),
    ),
    (
        re.compile(
            r"^E216 final_output example does not match lowered schema in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E216",
        "Final output example does not match the lowered schema",
        lambda match: (
            f"`final_output` example in {match.group('owner')} does not match the "
            f"lowered schema. {match.group('detail')}"
        ),
        ("Fix the authored `example:` so it matches the lowered schema.",),
    ),
    (
        re.compile(
            r"^E217 final_output lowered schema failed Draft 2020-12 validation in "
            r"(?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E217",
        "Final output lowered schema is not valid Draft 2020-12 JSON Schema",
        lambda match: (
            f"`final_output` lowered schema in {match.group('owner')} is not valid Draft 2020-12 "
            f"JSON Schema. {match.group('detail')}"
        ),
        ("Fix the authored `output schema` so the lowered schema is valid Draft 2020-12.",),
    ),
    (
        re.compile(
            r"^E218 final_output lowered schema is outside OpenAI structured outputs subset in "
            r"(?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E218",
        "Final output lowered schema is outside the OpenAI structured outputs subset",
        lambda match: (
            f"`final_output` lowered schema in {match.group('owner')} is outside the supported "
            f"OpenAI structured outputs subset. {match.group('detail')}"
        ),
        ("Fix the authored `output schema` so it stays inside the supported OpenAI subset.",),
    ),
    (
        re.compile(r"^Cyclic agent inheritance: (?P<detail>.+)$"),
        "E207",
        "Cyclic agent inheritance",
        lambda match: f"Agent inheritance cycle: {match.group('detail')}.",
        (),
    ),
)
