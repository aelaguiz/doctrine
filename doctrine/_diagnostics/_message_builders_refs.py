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


_REFERENCE_MESSAGE_BUILDERS: tuple[_PatternBuilder, ...] = (
    (
        re.compile(
            r"^Ambiguous route\.(?P<detail>label|summary) in (?P<owner>[^:]+): (?P<ref>.+)$"
        ),
        "E347",
        "Route detail needs one selected branch",
        lambda match: (
            f"`route.{match.group('detail')}` in {match.group('owner')} needs one selected route "
            f"branch, but `{match.group('ref')}` still sees more than one."
        ),
        (
            "Guard the read with `route.choice` so one route branch stays live.",
            "Use `route.next_owner.*` when you need selected-owner truth across several route choices.",
        ),
    ),
    (
        re.compile(r"^Ambiguous (?P<surface>.+) in (?P<owner>[^:]+): (?P<detail>.+)$"),
        "E270",
        "Ambiguous declaration reference",
        lambda match: f"In `{match.group('owner')}`, `{match.group('detail')}` is ambiguous on the {match.group('surface')} surface.",
        (),
    ),
    (
        re.compile(r"^Workflow refs are not allowed in (?P<surface>.+); (?P<detail>.+)$"),
        "E271",
        "Workflow ref is not allowed here",
        lambda match: f"Workflow refs are not allowed in {match.group('surface')}; {match.group('detail')}",
        (),
    ),
    (
        re.compile(r"^Abstract agent refs are not allowed in (?P<surface>.+); (?P<detail>.+)$"),
        "E272",
        "Abstract agent ref is not allowed here",
        lambda match: f"Abstract agent refs are not allowed in {match.group('surface')}; {match.group('detail')}",
        ("Mention a concrete agent instead of an abstract base agent.",),
    ),
    (
        re.compile(
            r"^Unknown (?:interpolation field|addressable path) on (?P<surface>.+) in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E273",
        "Unknown addressable path",
        lambda match: (
            f"In `{match.group('owner')}`, `{match.group('detail')}` does not resolve "
            f"to a known addressable item on the {match.group('surface')} surface."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?:Interpolation field must resolve to a scalar|Addressable path must stay addressable) on (?P<surface>.+) in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E274",
        "Addressable path must stay addressable",
        lambda match: (
            f"In `{match.group('owner')}`, `{match.group('detail')}` resolves "
            f"through a non-addressable surface on the {match.group('surface')} surface."
        ),
        (),
    ),
    (
        re.compile(r"^Missing local declaration ref in (?P<label>.+) (?P<owner>[^:]+): (?P<name>.+)$"),
        "E276",
        "Missing local declaration reference",
        lambda match: (
            f"Missing local declaration ref `{match.group('name')}` in {match.group('label')} `{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Missing local analysis declaration: (?P<name>.+)$"),
        "E276",
        "Missing local declaration reference",
        lambda match: (
            f"Analysis declaration `{match.group('name')}` does not exist in the current module."
        ),
        (),
    ),
    (
        re.compile(r"^Missing local output shape declaration: (?P<name>.+)$"),
        "E276",
        "Missing local declaration reference",
        lambda match: (
            f"Output shape declaration `{match.group('name')}` does not exist in the current module."
        ),
        (),
    ),
    (
        re.compile(r"^Doctrine compile config must be a TOML table\.$"),
        "E285",
        "Invalid compile config",
        lambda _match: "Doctrine compile config must be a TOML table.",
        (),
    ),
    (
        re.compile(r"^Doctrine compile config additional_prompt_roots must be an array of strings\.$"),
        "E285",
        "Invalid compile config",
        lambda _match: (
            "Doctrine compile config `additional_prompt_roots` must be an array of strings."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?P<label>Configured additional prompts root|"
            r"Provided prompt root `[^`]+`) must be an existing prompts directory: (?P<path>.+)$"
        ),
        "E285",
        "Invalid compile config",
        lambda match: (
            f"{match.group('label')} must be an existing `prompts/` directory: `{match.group('path')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Provided prompt roots must be ProvidedPromptRoot values\.$"),
        "E285",
        "Invalid compile config",
        lambda _match: "Provided prompt roots must be `ProvidedPromptRoot` values.",
        (),
    ),
    (
        re.compile(
            r"^Provided prompt root #(?P<index>\d+) name must be a non-empty string\.$"
        ),
        "E285",
        "Invalid compile config",
        lambda match: (
            f"Provided prompt root #{match.group('index')} name must be a non-empty string."
        ),
        (),
    ),
    (
        re.compile(
            r"^Provided prompt root `(?P<name>[^`]+)` name must not contain `:`\.$"
        ),
        "E285",
        "Invalid compile config",
        lambda match: (
            f"Provided prompt root `{match.group('name')}` name must not contain `:`."
        ),
        (),
    ),
    (
        re.compile(r"^Duplicate provided prompt root name: (?P<name>.+)$"),
        "E285",
        "Invalid compile config",
        lambda match: f"Provided prompt root name `{match.group('name')}` is duplicated.",
        (),
    ),
    (
        re.compile(
            r"^Provided prompt root `(?P<name>[^`]+)` path must be a string or path-like value\.$"
        ),
        "E285",
        "Invalid compile config",
        lambda match: (
            f"Provided prompt root `{match.group('name')}` path must be a string or path-like value."
        ),
        (),
    ),
    (
        re.compile(r"^Duplicate configured prompts root: (?P<path>.+)$"),
        "E286",
        "Duplicate configured prompts root",
        lambda match: f"Configured prompts root `{match.group('path')}` is duplicated.",
        (),
    ),
    (
        re.compile(
            r"^Duplicate provided prompts root `(?P<name>[^`]+)` matches "
            r"`(?P<prior>[^`]+)`: (?P<path>.+)$"
        ),
        "E286",
        "Duplicate active prompts root",
        lambda match: (
            f"Provided prompt root `{match.group('name')}` duplicates "
            f"`{match.group('prior')}` at `{match.group('path')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Duplicate active prompts root: (?P<detail>.+)$"),
        "E286",
        "Duplicate active prompts root",
        lambda match: f"Active prompts root is duplicated: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(
            r"^Ambiguous import module: (?P<module>.+) \(matching prompts roots: (?P<roots>.+)\)$"
        ),
        "E287",
        "Ambiguous import module",
        lambda match: (
            f"Import module `{match.group('module')}` matches more than one active prompts root: {match.group('roots')}."
        ),
        (),
    ),
    (
        re.compile(r"^Missing import module: (?P<module>.+)$"),
        "E280",
        "Missing import module",
        lambda match: (
            f"Import module `{match.group('module')}` could not be found in the active prompts roots."
        ),
        (),
    ),
    (
        re.compile(r"^Missing imported declaration: (?P<decl>.+)$"),
        "E281",
        "Missing imported declaration",
        lambda match: f"Imported declaration `{match.group('decl')}` does not exist in the resolved module.",
        (),
    ),
    (
        re.compile(r"^Route target must be a concrete agent: (?P<agent>.+)$"),
        "E282",
        "Route target must be a concrete agent",
        lambda match: f"Route target `{match.group('agent')}` is not a concrete agent.",
        (),
    ),
    (
        re.compile(r"^Cyclic workflow composition: (?P<detail>.+)$"),
        "E283",
        "Cyclic workflow composition",
        lambda match: f"Workflow composition cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Duplicate record key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E284",
        "Duplicate record key",
        lambda match: f"Record owner `{match.group('owner')}` repeats key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Duplicate declaration name: (?P<decl>.+)$"),
        "E288",
        "Duplicate declaration name",
        lambda match: f"Declaration `{match.group('decl')}` is defined more than once in the same module.",
        (),
    ),
)
