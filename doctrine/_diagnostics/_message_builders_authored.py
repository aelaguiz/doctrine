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


_AUTHORED_MESSAGE_BUILDERS: tuple[_PatternBuilder, ...] = (
    (
        re.compile(r"^Skill is missing string purpose: (?P<name>.+)$"),
        "E220",
        "Skill is missing string purpose",
        lambda match: f"Skill `{match.group('name')}` is missing a string `purpose` field.",
        (),
    ),
    (
        re.compile(r"^Input is missing typed source: (?P<name>.+)$"),
        "E221",
        "Input is missing typed source",
        lambda match: f"Input `{match.group('name')}` is missing a typed `source` field.",
        (),
    ),
    (
        re.compile(r"^Input is missing shape: (?P<name>.+)$"),
        "E222",
        "Input is missing shape",
        lambda match: f"Input `{match.group('name')}` is missing a `shape` field.",
        (),
    ),
    (
        re.compile(r"^Input is missing requirement: (?P<name>.+)$"),
        "E223",
        "Input is missing requirement",
        lambda match: f"Input `{match.group('name')}` is missing a `requirement` field.",
        (),
    ),
    (
        re.compile(r"^Output mixes `files` with `target` or `shape`: (?P<name>.+)$"),
        "E224",
        "Output mixes files with target or shape",
        lambda match: f"Output `{match.group('name')}` mixes `files` with `target` or `shape`.",
        (),
    ),
    (
        re.compile(r"^Output must define either `files` or both `target` and `shape`: (?P<name>.+)$"),
        "E224",
        "Output declaration is incomplete",
        lambda match: f"Output `{match.group('name')}` must define either `files` or both `target` and `shape`.",
        (),
    ),
    (
        re.compile(r"^Output target must be typed: (?P<name>.+)$"),
        "E225",
        "Output target must be typed",
        lambda match: f"Output `{match.group('name')}` must use a typed `target` reference.",
        (),
    ),
    (
        re.compile(r"^Unsupported record item: (?P<kind>.+)$"),
        "E226",
        "Unsupported record item",
        lambda match: f"Unsupported record item `{match.group('kind')}`.",
        (),
    ),
    (
        re.compile(r"^Config entries must be scalar key/value lines in (?P<owner>.+)$"),
        "E230",
        "Config entries must be scalar key/value lines",
        lambda match: f"Config entries must be scalar key/value lines in `{match.group('owner')}`.",
        (),
    ),
    (
        re.compile(r"^Duplicate config key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E231",
        "Duplicate config key",
        lambda match: f"Config owner `{match.group('owner')}` repeats key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Unknown config key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E232",
        "Unknown config key",
        lambda match: f"Config owner `{match.group('owner')}` uses unknown key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Missing required config key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E233",
        "Missing required config key",
        lambda match: f"Config owner `{match.group('owner')}` is missing required key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Config key declarations must be simple titled scalars in (?P<owner>.+)$"),
        "E234",
        "Config key declarations must be simple titled scalars",
        lambda match: f"Config key declarations must be simple titled scalars in `{match.group('owner')}`.",
        (),
    ),
    (
        re.compile(r"^Config key declarations must use string labels in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E234",
        "Config key declarations must use string labels",
        lambda match: f"Config key declaration `{match.group('key')}` in `{match.group('owner')}` must use a string label.",
        (),
    ),
    (
        re.compile(r"^Duplicate config key declaration in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E235",
        "Duplicate config key declaration",
        lambda match: f"Config owner `{match.group('owner')}` repeats config key declaration `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Cyclic workflow inheritance: (?P<detail>.+)$"),
        "E240",
        "Cyclic workflow inheritance",
        lambda match: f"Workflow inheritance cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Cyclic skills inheritance: (?P<detail>.+)$"),
        "E250",
        "Cyclic skills inheritance",
        lambda match: f"Skills inheritance cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Cyclic output inheritance: (?P<detail>.+)$"),
        "E251",
        "Cyclic output inheritance",
        lambda match: f"Output inheritance cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(
            r"^(?P<action>inherit|override) requires an inherited output in (?P<owner>[^:]+): (?P<key>.+)$"
        ),
        "E252",
        "Output patch requires an inherited output",
        lambda match: (
            f"`{match.group('action')}` for key `{match.group('key')}` requires an inherited output in "
            f"`{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot inherit undefined output entry in (?P<owner>[^:]+): (?P<key>.+)$"
        ),
        "E253",
        "Cannot inherit undefined output entry",
        lambda match: (
            f"Output `{match.group('owner')}` cannot inherit undefined key `{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot inherit output with unkeyed top-level items in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E254",
        "Inherited output needs keyed top-level entries",
        lambda match: (
            f"Output `{match.group('owner')}` contains unkeyed top-level items: {match.group('detail')}."
        ),
        (
            "Give inherited outputs stable keyed top-level items before patching them.",
        ),
    ),
    (
        re.compile(r"^Inherited output requires `override (?P<key>.+)` in (?P<owner>[^:]+)$"),
        "E255",
        "Invalid output inheritance patch",
        lambda match: (
            f"Output `{match.group('owner')}` must use `override {match.group('key')}` when it patches an inherited output item."
        ),
        (),
    ),
    (
        re.compile(r"^Override kind mismatch for output entry in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E255",
        "Invalid output inheritance patch",
        lambda match: (
            f"Output `{match.group('owner')}` overrides entry `{match.group('key')}` with the wrong kind."
        ),
        (),
    ),
    (
        re.compile(r"^Duplicate output item key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E255",
        "Invalid output inheritance patch",
        lambda match: (
            f"Output `{match.group('owner')}` repeats output item key `{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Conflicting concrete-turn binding roots resolve different artifacts: (?P<path>.+)$"
        ),
        "E260",
        "Conflicting concrete-turn binding roots",
        lambda match: (
            f"Concrete-turn binding root `{match.group('path')}` resolves to different artifacts."
        ),
        (
            "Keep each bound input or output root path attached to exactly one artifact.",
        ),
    ),
    (
        re.compile(r"^Duplicate workflow item key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E261",
        "Duplicate workflow item key",
        lambda match: f"Workflow owner `{match.group('owner')}` repeats key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Cannot inherit undefined workflow entry in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E241",
        "Cannot inherit undefined workflow entry",
        lambda match: f"Workflow owner `{match.group('owner')}` cannot inherit undefined key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Override kind mismatch for workflow entry in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E242",
        "Override kind mismatch",
        lambda match: f"Workflow owner `{match.group('owner')}` overrides `{match.group('key')}` with the wrong kind.",
        (),
    ),
    (
        re.compile(r"^(?P<kind>inherit|override) requires an inherited workflow in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E243",
        "Workflow patch requires an inherited workflow",
        lambda match: (
            f"`{match.group('kind')}` for key `{match.group('key')}` requires an inherited workflow in `{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Cyclic (?P<kind>inputs|outputs) inheritance: (?P<detail>.+)$"),
        "E244",
        "Cyclic IO block inheritance",
        lambda match: (
            f"{match.group('kind').title()} inheritance cycle: {match.group('detail')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot inherit undefined (?P<kind>inputs|outputs) entry in (?P<owner>[^:]+): (?P<key>.+)$"
        ),
        "E245",
        "Cannot inherit undefined IO block entry",
        lambda match: (
            f"{match.group('kind').title()} block `{match.group('owner')}` cannot inherit undefined key `{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?P<action>inherit|override) requires an inherited (?P<kind>inputs|outputs) block in (?P<owner>[^:]+): (?P<key>.+)$"
        ),
        "E246",
        "IO block patch requires an inherited IO block",
        lambda match: (
            f"`{match.group('action')}` for key `{match.group('key')}` requires an inherited "
            f"{match.group('kind')} block in `{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot inherit (?P<kind>inputs|outputs) block with unkeyed top-level refs in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E247",
        "Inherited IO block needs keyed top-level entries",
        lambda match: (
            f"{match.group('kind').title()} block `{match.group('owner')}` contains unkeyed top-level refs: {match.group('detail')}."
        ),
        (
            "Give inherited inputs and outputs blocks stable keyed sections before patching them.",
        ),
    ),
    (
        re.compile(
            r"^(?P<field>Inputs|Outputs) fields must resolve to (?P<expected>inputs|outputs) blocks, not (?P<actual>inputs|outputs) blocks: (?P<ref>.+)$"
        ),
        "E248",
        "IO field ref kind mismatch",
        lambda match: (
            f"`{match.group('field').lower()}` field ref `{match.group('ref')}` must resolve to "
            f"a {match.group('expected')} block, not a {match.group('actual')} block."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?P<field>Inputs|Outputs) patch fields must inherit from (?P<expected>inputs|outputs) blocks, not (?P<actual>inputs|outputs) blocks: (?P<ref>.+)$"
        ),
        "E249",
        "IO patch base kind mismatch",
        lambda match: (
            f"`{match.group('field').lower()}` patch base `{match.group('ref')}` must inherit from "
            f"a {match.group('expected')} block, not a {match.group('actual')} block."
        ),
        (),
    ),
)
