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


_WORKFLOW_LAW_MESSAGE_BUILDERS: tuple[_PatternBuilder, ...] = (
    (
        re.compile(
            r"^Active leaf branch must resolve exactly one current-subject form in (?P<owner>.+)$"
        ),
        "E331",
        "Missing current-subject form",
        lambda match: (
            "Each active workflow-law leaf branch must declare exactly one current subject "
            f"in {match.group('owner')}."
        ),
        ("Add either `current artifact ... via ...` or `current none` in each active branch.",),
    ),
    (
        re.compile(
            r"^Active leaf branch resolves more than one current-subject form \((?P<detail>.+)\) in (?P<owner>.+)$"
        ),
        "E332",
        "Multiple current-subject forms",
        lambda match: (
            f"One active workflow-law leaf branch declares multiple current-subject forms "
            f"({match.group('detail')}) in {match.group('owner')}."
        ),
        ("Keep exactly one `current artifact` or `current none` in each active branch.",),
    ),
    (
        re.compile(
            r"^current artifact carrier output must be emitted by the concrete turn in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E333",
        "Current carrier output not emitted",
        lambda match: (
            f"Current-artifact carrier output `{match.group('name')}` is not emitted by "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact output must be emitted by the concrete turn in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E334",
        "Current output not emitted",
        lambda match: (
            f"Current-artifact output `{match.group('name')}` is not emitted by "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact target must resolve to a (?:declared input or output|declared or bound concrete-turn input or declared or bound concrete-turn output) in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E335",
        "Current artifact target has wrong kind",
        lambda match: (
            f"Current-artifact target `{match.group('name')}` must resolve to a declared or "
            f"bound concrete-turn input or output in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact carrier field must be listed in trust_surface in (?P<owner>(?:(?!review).)+): (?P<name>.+)$"
        ),
        "E336",
        "Current carrier field missing from trust surface",
        lambda match: (
            f"Current-artifact carrier field `{match.group('name')}` is not listed in "
            f"`trust_surface` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Unknown output field on current artifact via in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E337",
        "Unknown current carrier field",
        lambda match: (
            f"Current-artifact carrier field `{match.group('path')}` does not exist in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Output guard reads disallowed source in (?P<owner>.+): (?P<source>.+)$"
        ),
        "E338",
        "Output guard reads disallowed source",
        lambda match: (
            f"Output guard in {match.group('owner')} reads disallowed source "
            f"`{match.group('source')}`."
        ),
        (
            "Read only declared inputs and enum members in output guards.",
            "Do not read workflow-local bindings or emitted output fields inside guarded output items.",
            "Route-bound outputs may also guard on compiler-owned route refs such as `route.exists` and `route.choice`.",
        ),
    ),
    (
        re.compile(
            r"^next_owner field must interpolate routed target in (?P<owner>.+): (?P<path>.+) -> (?P<target>.+)$"
        ),
        "E339",
        "Routed next_owner field is not structurally bound",
        lambda match: (
            f"`next_owner` field `{match.group('path')}` in {match.group('owner')} "
            f"does not structurally bind the routed target `{match.group('target')}`."
        ),
        (
            "Use an explicit interpolation such as `{{RoutingOwner}}` or `{{RoutingOwner:name}}` inside the `next_owner` field for routed branches.",
            "If ownership stays local, keep the field generic and do not emit a semantic route.",
        ),
    ),
    (
        re.compile(
            r"^standalone_read cannot interpolate guarded output detail in (?P<owner>.+): (?P<ref>.+)$"
        ),
        "E340",
        "Standalone read references guarded output detail",
        lambda match: (
            f"`standalone_read` in {match.group('owner')} references guarded output detail "
            f"`{match.group('ref')}`."
        ),
        (
            "Keep `standalone_read` at branch-level readback only.",
            "Do not interpolate guarded item detail inside `standalone_read`.",
        ),
    ),
    (
        re.compile(r"^Mode value is outside enum (?P<enum>.+) in (?P<owner>.+): (?P<value>.+)$"),
        "E341",
        "Mode value outside enum",
        lambda match: (
            f"Mode value `{match.group('value')}` is outside enum `{match.group('enum')}` "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^match on (?P<enum>.+) must be exhaustive or include else in (?P<owner>.+)$"),
        "E342",
        "Non-exhaustive mode match",
        lambda match: (
            f"`match` on `{match.group('enum')}` must cover every enum member or include `else` "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Multiple route-bearing control surfaces are live in agent (?P<agent>.+): (?P<sources>.+)$"
        ),
        "E343",
        "Multiple route-bearing control surfaces are live",
        lambda match: (
            f"Agent `{match.group('agent')}` has more than one live route-bearing control "
            f"surface: {match.group('sources')}."
        ),
        (
            "Keep shared `route.*` truth on exactly one surface per concrete turn.",
            "Use one of `workflow:`, `review:`, or `handoff_routing:` to supply route semantics.",
        ),
    ),
    (
        re.compile(
            r"^handoff_routing law only supports active when, mode, when, match, route_from, stop, and route in (?P<owner>.+): (?P<stmt>.+)$"
        ),
        "E344",
        "handoff_routing law uses a non-routing statement",
        lambda match: (
            f"`handoff_routing` law in {match.group('owner')} uses unsupported statement "
            f"`{match.group('stmt')}`."
        ),
        (
            "Use only `active when`, `mode`, `when`, `match`, `route_from`, `stop`, and `route` in `handoff_routing` law.",
            "Keep currentness, preservation, invalidation, and other workflow-law truth controls on `workflow:`.",
        ),
    ),
    (
        re.compile(
            r"^law may appear only on workflow or handoff_routing in (?P<owner>.+): (?P<slot>.+)$"
        ),
        "E345",
        "Law is not allowed on this authored slot",
        lambda match: (
            f"`law:` is not allowed on authored slot `{match.group('slot')}` in "
            f"{match.group('owner')}."
        ),
        (
            "Attach `law:` only to `workflow:` or `handoff_routing:`.",
            "Keep other authored slots as readable instruction surfaces.",
        ),
    ),
    (
        re.compile(
            r"^route_from selector reads invalid source in (?P<owner>.+): (?P<source>.+)$"
        ),
        "E346",
        "route_from selector reads invalid source",
        lambda match: (
            f"`route_from` selector in {match.group('owner')} reads invalid source "
            f"`{match.group('source')}`."
        ),
        (
            "Read only declared inputs, emitted outputs, or enum members in a `route_from` selector.",
            "Do not read workflow-local bindings or other compiler-local names there.",
        ),
    ),
    (
        re.compile(
            r"^Duplicate route_from arm in (?P<owner>.+): (?P<choice>.+)$"
        ),
        "E348",
        "Duplicate route_from arm",
        lambda match: (
            f"`route_from` in {match.group('owner')} names "
            f"`{match.group('choice')}` more than once."
        ),
        (
            "Name each enum member at most once in `route_from`.",
            "Use `else` at most once, and only when you need the remaining members.",
        ),
    ),
    (
        re.compile(
            r"^own only must stay rooted in the current artifact, an emitted output surface, or a declared schema family in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E351",
        "Owned scope is outside the allowed modeled surface",
        lambda match: (
            f"Owned scope `{match.group('path')}` is not rooted in the current artifact, "
            f"an emitted output surface, or a declared schema family in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^own only target must resolve to a (?:declared input or output|declared or bound concrete-turn input or declared or bound concrete-turn output|declared or bound concrete-turn input or declared or bound concrete-turn output or declared schema family) in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E352",
        "Owned scope target is unknown",
        lambda match: (
            f"Owned scope target `{match.group('path')}` must resolve to a declared or bound "
            f"concrete-turn input or output or a declared schema family in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Owned scope overlaps exact-preserved scope in (?P<owner>.+)$"),
        "E353",
        "Owned scope overlaps exact preservation",
        lambda match: (
            f"Owned scope overlaps exact-preserved scope in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Owned and forbidden scope overlap in (?P<owner>.+)$"),
        "E354",
        "Owned scope overlaps forbidden scope",
        lambda match: (
            f"Owned scope overlaps forbidden scope in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^preserve (?P<kind>structure|mapping|vocabulary|exact|decisions) target must resolve to a (?P<label>declared input or output|declared or bound concrete-turn input or declared or bound concrete-turn output|declared enum|declared or bound concrete-turn input or declared or bound concrete-turn output or declared schema family or declared grounding|declared enum or declared or bound concrete-turn input or declared or bound concrete-turn output or declared schema family|declared or bound concrete-turn input or declared or bound concrete-turn output or declared schema family) in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E355",
        "Preserve target is unknown",
        lambda match: (
            f"`preserve {match.group('kind')}` target `{match.group('path')}` must resolve to a "
            f"{match.group('label')} in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^The current artifact cannot be ignored for truth in (?P<owner>.+)$"),
        "E361",
        "Current artifact ignored for truth",
        lambda match: (
            f"The current artifact is being ignored for truth in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^support_only and ignore for comparison contradict in (?P<owner>.+)$"),
        "E362",
        "Comparison-only basis contradiction",
        lambda match: (
            f"`support_only` and `ignore ... for comparison` contradict in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^The current artifact cannot be invalidated in the same active branch in (?P<owner>.+)$"
        ),
        "E371",
        "Current artifact invalidated in same branch",
        lambda match: (
            f"The current artifact is invalidated in the same active branch in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^invalidate carrier field must be listed in trust_surface in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E372",
        "Invalidation carrier field missing from trust surface",
        lambda match: (
            f"Invalidation carrier field `{match.group('name')}` is not listed in `trust_surface` "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^invalidate target must resolve to a declared or bound concrete-turn input or declared or bound concrete-turn output or declared schema group in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E373",
        "Invalidation target is unknown",
        lambda match: (
            f"Invalidation target `{match.group('path')}` must resolve to a declared or bound "
            f"concrete-turn input, output, or schema group in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Inherited law blocks must use named sections only in (?P<owner>.+)$"),
        "E381",
        "Inherited law requires named sections",
        lambda match: (
            f"Inherited law blocks must use named sections only in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Inherited law block accounts for the same parent subsection more than once in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E382",
        "Duplicate inherited law subsection",
        lambda match: (
            f"Inherited law block accounts for subsection `{match.group('key')}` more than once "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Inherited law block omits parent subsection\(s\) in (?P<owner>.+): (?P<keys>.+)$"
        ),
        "E383",
        "Missing inherited law subsection",
        lambda match: (
            f"Inherited law block omits parent subsection(s) `{match.group('keys')}` in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot override undefined law section in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E384",
        "Cannot override undefined law subsection",
        lambda match: (
            f"Cannot override undefined law subsection `{match.group('key')}` in "
            f"{match.group('owner')}."
        ),
        (),
    ),
)
