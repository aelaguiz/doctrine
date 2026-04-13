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


_REVIEW_MESSAGE_BUILDERS: tuple[_PatternBuilder, ...] = (
    (
        re.compile(r"^Cyclic review inheritance: (?P<detail>.+)$"),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            "Review declaration shape is invalid because inheritance is cyclic: "
            f"{match.group('detail')}."
        ),
        (),
    ),
    (
        re.compile(r"^Override kind mismatch for review entry in (?P<owner>.+): (?P<key>.+)$"),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            f"Review `{match.group('owner')}` uses the wrong inherited entry shape for "
            f"`{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review subject_map entry must resolve to an enum member in "
            r"(?P<owner>.+): (?P<entry>.+)$"
        ),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            f"Review `{match.group('owner')}` uses a `subject_map` entry that does not "
            f"resolve to an enum member: `{match.group('entry')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Duplicate review subject_map entry in (?P<owner>.+): (?P<entry>.+)$"),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            f"Review `{match.group('owner')}` repeats `subject_map` entry "
            f"`{match.group('entry')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Missing local review declaration: (?P<name>.+)$"),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            f"Review declaration shape is invalid because inherited review "
            f"`{match.group('name')}` does not exist locally."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review subject_map target must be one of the declared review subjects in "
            r"(?P<owner>.+): (?P<target>.+)$"
        ),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            f"Review `{match.group('owner')}` maps `subject_map` to undeclared review subject "
            f"`{match.group('target')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Review cases overlap in (?P<owner>.+): (?P<detail>.+)$"),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            f"Review `{match.group('owner')}` has overlapping case-selected review cases: "
            f"`{match.group('detail')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Review cases must be exhaustive in (?P<owner>.+)$"),
        "E470",
        "Invalid review declaration shape",
        lambda match: (
            f"Review `{match.group('owner')}` has a case-selected review family that is not exhaustive."
        ),
        (),
    ),
    (
        re.compile(r"^Review is missing fields: (?P<name>.+)$"),
        "E473",
        "Review is missing fields",
        lambda match: f"Review `{match.group('name')}` is missing the required `fields:` binding surface.",
        (),
    ),
    (
        re.compile(r"^Review fields are incomplete in (?P<owner>.+): (?P<detail>.+)$"),
        "E473",
        "Review fields are incomplete",
        lambda match: (
            f"Review fields are incomplete in {match.group('owner')}: "
            f"{match.group('detail')}."
        ),
        (),
    ),
    (
        re.compile(r"^Review is missing subject: (?P<name>.+)$"),
        "E474",
        "Review is missing subject",
        lambda match: f"Review `{match.group('name')}` is missing `subject:`.",
        (),
    ),
    (
        re.compile(
            r"^Review subject must resolve to an input or output declaration in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E475",
        "Review subject has the wrong kind",
        lambda match: (
            f"Review subject `{match.group('name')}` must resolve to an input or output "
            f"declaration in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Review is missing contract: (?P<name>.+)$"),
        "E476",
        "Review is missing contract",
        lambda match: f"Review `{match.group('name')}` is missing `contract:`.",
        (),
    ),
    (
        re.compile(r"^Unknown review contract gate in (?P<owner>.+): (?P<name>.+)$"),
        "E477",
        "Unknown review contract gate",
        lambda match: (
            f"Unknown review contract gate `{match.group('name')}` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Review contract may not define (?:workflow law|skills) in (?P<owner>.+)$"),
        "E477",
        "Invalid review contract target",
        lambda match: f"Review contract uses unsupported workflow features in {match.group('owner')}.",
        (),
    ),
    (
        re.compile(r"^Review contract must export at least one gate in (?P<owner>.+): (?P<name>.+)$"),
        "E477",
        "Invalid review contract target",
        lambda match: (
            f"Review contract `{match.group('name')}` in {match.group('owner')} must export at "
            "least one gate."
        ),
        (),
    ),
    (
        re.compile(r"^Review is missing comment_output: (?P<name>.+)$"),
        "E478",
        "Review is missing comment_output",
        lambda match: f"Review `{match.group('name')}` is missing `comment_output:`.",
        (),
    ),
    (
        re.compile(
            r"^Review comment_output must be emitted by the concrete turn in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E479",
        "Review comment_output is not emitted",
        lambda match: (
            f"Review comment output `{match.group('name')}` is not emitted by "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Concrete agent may not define both `workflow` and `review`: (?P<agent>.+)$"),
        "E480",
        "Concrete agent defines both workflow and review",
        lambda match: (
            f"Concrete agent `{match.group('agent')}` may not define both `workflow:` and `review:`."
        ),
        (),
    ),
    (
        re.compile(r"^Review must define exactly one accept gate in (?P<owner>.+): found 0$"),
        "E481",
        "Review is missing accept",
        lambda match: f"Review in {match.group('owner')} is missing an `accept` gate.",
        (),
    ),
    (
        re.compile(r"^Review must define exactly one accept gate in (?P<owner>.+): found (?P<count>[1-9][0-9]*)$"),
        "E482",
        "Review has multiple accept gates",
        lambda match: (
            f"Review in {match.group('owner')} defines multiple `accept` gates "
            f"({match.group('count')})."
        ),
        (),
    ),
    (
        re.compile(r"^Review is missing on_(?P<section>accept|reject): (?P<name>.+)$"),
        "E483",
        "Review is missing a reserved outcome section",
        lambda match: (
            f"Review `{match.group('name')}` is missing reserved outcome section "
            f"`on_{match.group('section')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Review match must be exhaustive or include else in (?P<owner>.+)$"),
        "E484",
        "Review outcome is not total",
        lambda match: f"Review match must be exhaustive or include `else` in {match.group('owner')}.",
        (),
    ),
    (
        re.compile(r"^Review outcome is not total in (?P<owner>.+): (?P<section>.+)$"),
        "E484",
        "Review outcome is not total",
        lambda match: (
            f"Review outcome branch `{match.group('section')}` is not total in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review outcome resolves more than one route in (?P<owner>.+): (?P<section>.+)$"
        ),
        "E485",
        "Review outcome resolves more than one route",
        lambda match: (
            f"Review outcome branch `{match.group('section')}` resolves more than one route in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review outcome resolves more than one currentness result in (?P<owner>.+): (?P<section>.+)$"
        ),
        "E486",
        "Review outcome resolves more than one currentness result",
        lambda match: (
            "Review outcome branch "
            f"`{match.group('section')}` resolves more than one currentness result in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact carrier target must resolve to a (?:declared output|declared or bound concrete-turn output) in (?P<owner>.+review.+): (?P<name>.+)$"
        ),
        "E487",
        "Review currentness requires a valid carrier",
        lambda match: (
            f"Review currentness carrier `{match.group('name')}` must resolve to a declared or "
            f"bound concrete-turn output in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact carrier field must be listed in trust_surface in (?P<owner>.+review.+): (?P<name>.+)$"
        ),
        "E488",
        "Review current carrier is missing from trust surface",
        lambda match: (
            f"Review currentness carrier field `{match.group('name')}` is not listed in "
            f"`trust_surface` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review current artifact must stay rooted in a review subject or emitted output in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E469",
        "Review current artifact is outside the review subject set",
        lambda match: (
            f"Review current artifact `{match.group('name')}` must stay rooted in a declared "
            f"review subject or emitted output in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Review subject set requires disambiguation in (?P<owner>.+): (?P<section>.+)$"),
        "E489",
        "Review subject set requires disambiguation",
        lambda match: (
            f"Review subject set requires disambiguation in {match.group('owner')} "
            f"branch `{match.group('section')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Missing inherited review entry in (?P<owner>.+): (?P<key>.+)$"),
        "E490",
        "Missing inherited review entry",
        lambda match: (
            f"Review `{match.group('owner')}` does not account for inherited review entry "
            f"`{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Duplicate review item key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E491",
        "Duplicate review item key",
        lambda match: (
            f"Review `{match.group('owner')}` repeats review item key `{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(r"^`override` requires an inherited review in (?P<owner>.+): (?P<key>.+)$"),
        "E492",
        "Review override requires an inherited review",
        lambda match: (
            f"Review override for `{match.group('key')}` requires an inherited review in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Carried review field is missing a binding in (?P<owner>.+): (?P<field>.+)$"),
        "E493",
        "Carried review field is missing a binding",
        lambda match: (
            f"Carried review field `{match.group('field')}` is missing a required binding in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Concrete agents may not attach abstract reviews directly: (?P<name>.+)$"),
        "E494",
        "Concrete agent may not attach abstract review directly",
        lambda match: (
            f"Concrete agent may not attach abstract review `{match.group('name')}` directly."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review verdict field is not live for semantic verdict in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E495",
        "Review verdict does not match the bound output field",
        lambda match: (
            f"Resolved review verdict is not guaranteed to reach bound output field "
            f"`{match.group('path')}` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review next_owner field is not live for routed target in (?P<owner>.+): (?P<path>.+) -> (?P<agent>.+)$"
        ),
        "E496",
        "Review next owner does not match the bound output field",
        lambda match: (
            f"Resolved next owner `{match.group('agent')}` is not guaranteed to reach bound output "
            f"field `{match.group('path')}` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review next_owner field must structurally bind the routed target in (?P<owner>.+): (?P<path>.+) -> (?P<agent>.+)$"
        ),
        "E496",
        "Review next owner does not match the bound output field",
        lambda match: (
            f"Bound next-owner field `{match.group('path')}` does not structurally bind routed "
            f"target `{match.group('agent')}` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review current artifact carrier field is not live for semantic currentness in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E497",
        "Review currentness does not match the declared carrier field",
        lambda match: (
            f"Resolved review currentness is not guaranteed to reach carrier field "
            f"`{match.group('path')}` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review current artifact carrier field stays live without semantic currentness in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E497",
        "Review currentness does not match the declared carrier field",
        lambda match: (
            f"Carrier field `{match.group('path')}` stays live even though the review resolves "
            f"`current none` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review carried field is not live when semantic value exists in (?P<owner>.+): (?P<field>.+) -> (?P<path>.+)$"
        ),
        "E498",
        "Required carried review field is omitted when semantic value exists",
        lambda match: (
            f"Carried review field `{match.group('field')}` is not guaranteed to reach bound output "
            f"field `{match.group('path')}` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Review conditional output field is not aligned with resolved review semantics in (?P<owner>.+): (?P<field>.+) -> (?P<path>.+)$"
        ),
        "E499",
        "Required conditional review output section is missing after its guard resolves true",
        lambda match: (
            f"Conditional review output field `{match.group('path')}` for semantic channel "
            f"`{match.group('field')}` is not aligned with resolved review semantics in "
            f"{match.group('owner')}."
        ),
        (),
    ),
)
