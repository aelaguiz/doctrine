from __future__ import annotations

import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable

from lark.exceptions import UnexpectedCharacters, UnexpectedEOF, UnexpectedInput, UnexpectedToken


@dataclass(slots=True, frozen=True)
class DiagnosticLocation:
    path: Path | None = None
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class DiagnosticExcerptLine:
    number: int
    text: str


@dataclass(slots=True, frozen=True)
class DiagnosticTraceFrame:
    label: str
    location: DiagnosticLocation | None = None


@dataclass(slots=True, frozen=True)
class PyPromptDiagnostic:
    code: str
    stage: str
    summary: str
    detail: str | None = None
    location: DiagnosticLocation | None = None
    excerpt: tuple[DiagnosticExcerptLine, ...] = ()
    caret_column: int | None = None
    hints: tuple[str, ...] = ()
    trace: tuple[DiagnosticTraceFrame, ...] = ()
    cause: str | None = None


def diagnostic_to_dict(error_or_diagnostic: PyPromptError | PyPromptDiagnostic) -> dict[str, Any]:
    diagnostic = _coerce_diagnostic(error_or_diagnostic)
    return asdict(diagnostic)


def format_diagnostic(error_or_diagnostic: PyPromptError | PyPromptDiagnostic) -> str:
    diagnostic = _coerce_diagnostic(error_or_diagnostic)
    lines = [f"{diagnostic.code} {diagnostic.stage} error: {diagnostic.summary}"]

    if diagnostic.location is not None:
        lines.extend(["", "Location:", f"- {_format_location(diagnostic.location)}"])

    if diagnostic.detail:
        lines.extend(["", "Detail:"])
        lines.extend(_format_block(diagnostic.detail))

    if diagnostic.excerpt:
        lines.extend(["", "Source:"])
        lines.extend(
            _format_excerpt(
                diagnostic.excerpt,
                highlight_line=diagnostic.location.line if diagnostic.location is not None else None,
                caret_column=diagnostic.caret_column,
            )
        )

    if diagnostic.trace:
        lines.extend(["", "Trace:"])
        for frame in diagnostic.trace:
            location = ""
            if frame.location is not None:
                location = f" ({_format_location(frame.location)})"
            lines.append(f"- {frame.label}{location}")

    if diagnostic.hints:
        label = "Hint:" if len(diagnostic.hints) == 1 else "Hints:"
        lines.extend(["", label])
        for hint in diagnostic.hints:
            lines.extend(_format_block(hint))

    if diagnostic.cause:
        lines.extend(["", "Cause:"])
        lines.extend(_format_block(diagnostic.cause))

    return "\n".join(lines)


class PyPromptError(RuntimeError):
    stage = "runtime"
    fallback_code = "E999"
    fallback_summary = "Unexpected PyPrompt error"

    def __init__(
        self,
        message: str | None = None,
        *,
        diagnostic: PyPromptDiagnostic | None = None,
    ) -> None:
        if diagnostic is None:
            diagnostic = self._diagnostic_from_message(message or self.fallback_summary)
        self.diagnostic = diagnostic
        super().__init__(format_diagnostic(diagnostic))

    @property
    def code(self) -> str:
        return self.diagnostic.code

    @property
    def location(self) -> DiagnosticLocation | None:
        return self.diagnostic.location

    def __str__(self) -> str:
        return format_diagnostic(self.diagnostic)

    @classmethod
    def from_parts(
        cls,
        *,
        code: str,
        summary: str,
        detail: str | None = None,
        location: DiagnosticLocation | None = None,
        excerpt: tuple[DiagnosticExcerptLine, ...] = (),
        caret_column: int | None = None,
        hints: tuple[str, ...] = (),
        trace: tuple[DiagnosticTraceFrame, ...] = (),
        cause: str | None = None,
    ) -> PyPromptError:
        return cls(
            diagnostic=PyPromptDiagnostic(
                code=code,
                stage=cls.stage,
                summary=summary,
                detail=detail,
                location=location,
                excerpt=excerpt,
                caret_column=caret_column,
                hints=hints,
                trace=trace,
                cause=cause,
            )
        )

    def prepend_trace(
        self,
        label: str,
        *,
        location: DiagnosticLocation | None = None,
    ) -> PyPromptError:
        self.diagnostic = replace(
            self.diagnostic,
            trace=(DiagnosticTraceFrame(label=label, location=location), *self.diagnostic.trace),
        )
        self.args = (format_diagnostic(self.diagnostic),)
        return self

    def ensure_location(
        self,
        *,
        path: Path | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> PyPromptError:
        if self.diagnostic.location is not None:
            return self
        self.diagnostic = replace(
            self.diagnostic,
            location=DiagnosticLocation(path=path, line=line, column=column),
        )
        self.args = (format_diagnostic(self.diagnostic),)
        return self

    def _diagnostic_from_message(self, message: str) -> PyPromptDiagnostic:
        return PyPromptDiagnostic(
            code=self.fallback_code,
            stage=self.stage,
            summary=self.fallback_summary,
            detail=message,
        )


class ParseError(PyPromptError):
    stage = "parse"
    fallback_code = "E199"
    fallback_summary = "Parse failure"

    @classmethod
    def from_lark(
        cls,
        *,
        source: str,
        path: Path | None,
        exc: UnexpectedInput,
    ) -> ParseError:
        line = getattr(exc, "line", None)
        column = getattr(exc, "column", None)
        location = DiagnosticLocation(path=path, line=line, column=column)
        excerpt, caret_column = _build_excerpt(source, line=line, column=column)

        if isinstance(exc, UnexpectedCharacters):
            summary = "Unexpected character"
            code = "E102"
            hints = (
                f"Remove or replace the unsupported character near column {column}.",
            )
            cause = f"Unexpected character {exc.char!r}."
        elif isinstance(exc, UnexpectedEOF):
            summary = "Unexpected end of file"
            code = "E103"
            hints = ("Finish the current declaration or block before the file ends.",)
            cause = _format_expected_tokens(getattr(exc, "expected", None))
        elif isinstance(exc, UnexpectedToken):
            code, summary, hints = _classify_unexpected_token(exc)
            cause = _format_unexpected_token_cause(exc)
        else:
            summary = "Unexpected parser input"
            code = "E199"
            hints = ("Check the surrounding syntax and indentation.",)
            cause = str(exc)

        return cls.from_parts(
            code=code,
            summary=summary,
            detail=_format_parse_detail(exc),
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=hints,
            cause=cause,
        )


class CompileError(PyPromptError):
    stage = "compile"
    fallback_code = "E299"
    fallback_summary = "Compile failure"

    def _diagnostic_from_message(self, message: str) -> PyPromptDiagnostic:
        return _compile_diagnostic_from_message(message)


class EmitError(PyPromptError):
    stage = "emit"
    fallback_code = "E599"
    fallback_summary = "Emit failure"

    def _diagnostic_from_message(self, message: str) -> PyPromptDiagnostic:
        return _emit_diagnostic_from_message(message)


def _coerce_diagnostic(error_or_diagnostic: PyPromptError | PyPromptDiagnostic) -> PyPromptDiagnostic:
    if isinstance(error_or_diagnostic, PyPromptError):
        return error_or_diagnostic.diagnostic
    return error_or_diagnostic


def _format_location(location: DiagnosticLocation) -> str:
    path = location.path
    if path is None:
        return "<unknown>"
    rendered = _display_path(path)
    if location.line is None:
        return rendered
    if location.column is None:
        return f"{rendered}:{location.line}"
    return f"{rendered}:{location.line}:{location.column}"


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return str(resolved.relative_to(cwd))
    except ValueError:
        return str(resolved)


def _format_block(text: str) -> list[str]:
    return [f"- {line}" if index == 0 else f"  {line}" for index, line in enumerate(text.splitlines())]


def _format_excerpt(
    excerpt: tuple[DiagnosticExcerptLine, ...],
    *,
    highlight_line: int | None = None,
    caret_column: int | None,
) -> list[str]:
    number_width = max(len(str(line.number)) for line in excerpt)
    lines: list[str] = []
    for entry in excerpt:
        lines.append(f"  {entry.number:>{number_width}} | {entry.text}")
        if caret_column is not None and highlight_line is not None and entry.number == highlight_line:
            padding = " " * (number_width + 5 + max(caret_column - 1, 0))
            lines.append(f"{padding}^")
    return lines


def _build_excerpt(
    source: str,
    *,
    line: int | None,
    column: int | None,
) -> tuple[tuple[DiagnosticExcerptLine, ...], int | None]:
    if line is None:
        return (), None
    all_lines = source.splitlines()
    if not all_lines:
        return (), column
    start = max(line - 2, 1)
    end = min(line + 1, len(all_lines))
    excerpt = tuple(
        DiagnosticExcerptLine(number=index, text=all_lines[index - 1])
        for index in range(start, end + 1)
    )
    return excerpt, column


def _classify_unexpected_token(
    exc: UnexpectedToken,
) -> tuple[str, str, tuple[str, ...]]:
    token_type = exc.token.type
    if token_type == "_INDENT":
        return (
            "E104",
            "Unexpected indented block",
            ("Indent this block only after a declaration line that opens a nested body.",),
        )
    if token_type == "_DEDENT":
        return (
            "E104",
            "Unexpected dedent",
            ("Keep indentation aligned with the current block structure.",),
        )
    if token_type == "_NL":
        return (
            "E101",
            "Unexpected newline",
            ("Finish the current declaration before starting a new line.",),
        )
    return (
        "E101",
        "Unexpected token",
        ("Check the expected token list and the surrounding punctuation.",),
    )


def _format_unexpected_token_cause(exc: UnexpectedToken) -> str:
    token = exc.token
    token_value = token.value.replace("\n", "\\n")
    parts = [f"Unexpected token `{token.type}` with value `{token_value}`."]
    expected = _format_expected_tokens(exc.expected)
    if expected:
        parts.append(expected)
    return " ".join(parts)


def _format_expected_tokens(expected: set[str] | list[str] | None) -> str | None:
    if not expected:
        return None
    normalized = ", ".join(f"`{token}`" for token in sorted(expected))
    return f"Expected one of: {normalized}."


def _format_parse_detail(exc: UnexpectedInput) -> str:
    if isinstance(exc, UnexpectedToken):
        token_type = exc.token.type
        if token_type == "_NL":
            return "The parser hit a line break where the current grammar still expected more input."
        if token_type == "_INDENT":
            return "The parser entered an indented block that is not valid at this point in the grammar."
        if token_type == "_DEDENT":
            return "The parser left an indented block before the current declaration was complete."
    if isinstance(exc, UnexpectedCharacters):
        return "The parser hit a character that does not belong to any token on this surface."
    if isinstance(exc, UnexpectedEOF):
        return "The file ended before the current declaration or block was complete."
    return "The parser could not match the current source against the shipped grammar."


_COMPILE_PATTERN_BUILDERS: tuple[
    tuple[re.Pattern[str], str, str, Callable[[re.Match[str]], str | None], tuple[str, ...]],
    ...,
] = (
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
        re.compile(r"^Cyclic agent inheritance: (?P<detail>.+)$"),
        "E207",
        "Cyclic agent inheritance",
        lambda match: f"Agent inheritance cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Duplicate workflow item key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E261",
        "Duplicate workflow item key",
        lambda match: f"Workflow owner `{match.group('owner')}` repeats key `{match.group('key')}`.",
        (),
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
        re.compile(r"^Unknown workflow string interpolation field in (?P<owner>[^:]+): (?P<detail>.+)$"),
        "E273",
        "Unknown workflow interpolation field",
        lambda match: f"In `{match.group('owner')}`, `{match.group('detail')}` does not resolve to a known interpolation field.",
        (),
    ),
    (
        re.compile(r"^Workflow string interpolation field must resolve to a scalar in (?P<owner>[^:]+): (?P<detail>.+)$"),
        "E274",
        "Workflow interpolation field must resolve to a scalar",
        lambda match: f"In `{match.group('owner')}`, `{match.group('detail')}` resolves to a non-scalar surface.",
        (),
    ),
    (
        re.compile(r"^Missing import module: (?P<module>.+)$"),
        "E280",
        "Missing import module",
        lambda match: f"Import module `{match.group('module')}` could not be found under the current prompts root.",
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
        re.compile(r"^Internal compiler error: (?P<detail>.+)$"),
        "E901",
        "Internal compiler error",
        lambda match: match.group("detail"),
        ("This is a compiler bug, not a prompt authoring error.",),
    ),
)


def _compile_diagnostic_from_message(message: str) -> PyPromptDiagnostic:
    for pattern, code, summary, detail_builder, hints in _COMPILE_PATTERN_BUILDERS:
        match = pattern.match(message)
        if match is None:
            continue
        return PyPromptDiagnostic(
            code=code,
            stage="compile",
            summary=summary,
            detail=detail_builder(match),
            hints=hints,
            cause=message if message != detail_builder(match) else None,
        )
    return PyPromptDiagnostic(
        code="E299",
        stage="compile",
        summary="Compile failure",
        detail=message,
    )


_EMIT_PATTERN_BUILDERS: tuple[
    tuple[re.Pattern[str], str, str, Callable[[re.Match[str]], str | None], tuple[str, ...]],
    ...,
] = (
    (
        re.compile(r"^Unknown emit target: (?P<target>.+)$"),
        "E501",
        "Unknown emit target",
        lambda match: f"Emit target `{match.group('target')}` is not defined in `pyproject.toml`.",
        (),
    ),
    (
        re.compile(r"^Emit target (?P<target>.+) has no concrete agents in (?P<path>.+)$"),
        "E502",
        "Emit target has no concrete agents",
        lambda match: f"Emit target `{match.group('target')}` points at `{match.group('path')}`, which has no concrete agents.",
        (),
    ),
    (
        re.compile(r"^pyproject\.toml does not define any \[tool\.pyprompt\.emit\.targets\]\.$"),
        "E503",
        "Missing emit targets",
        lambda _match: "The current `pyproject.toml` does not define any emit targets.",
        (),
    ),
    (
        re.compile(r"^Could not find pyproject\.toml in (?P<detail>.+)\.$"),
        "E504",
        "Missing pyproject.toml",
        lambda match: f"Could not find `pyproject.toml` in {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Emit target (?P<target>.+) maps both (?P<a>.+) and (?P<b>.+) to (?P<path>.+)$"),
        "E505",
        "Emit target path collision",
        lambda match: (
            f"Emit target `{match.group('target')}` maps `{match.group('a')}` and `{match.group('b')}` to the same path `{match.group('path')}`."
        ),
        (),
    ),
)


def _emit_diagnostic_from_message(message: str) -> PyPromptDiagnostic:
    for pattern, code, summary, detail_builder, hints in _EMIT_PATTERN_BUILDERS:
        match = pattern.match(message)
        if match is None:
            continue
        return PyPromptDiagnostic(
            code=code,
            stage="emit",
            summary=summary,
            detail=detail_builder(match),
            hints=hints,
            cause=message if message != detail_builder(match) else None,
        )
    return PyPromptDiagnostic(
        code="E599",
        stage="emit",
        summary="Emit failure",
        detail=message,
    )
