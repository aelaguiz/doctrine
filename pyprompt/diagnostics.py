from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable

from lark import Token, Tree
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
    VisitError,
)


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
    return _json_safe_value(diagnostic)


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

    @classmethod
    def from_transform(
        cls,
        *,
        source: str,
        path: Path | None,
        exc: VisitError,
    ) -> ParseError:
        line, column = _extract_tree_position(exc.obj)
        location = DiagnosticLocation(path=path, line=line, column=column)
        excerpt, caret_column = _build_excerpt(source, line=line, column=column)
        detail = str(exc.orig_exc)
        return cls.from_parts(
            code="E105",
            summary="Invalid authored slot body",
            detail=detail,
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=(
                "Do not attach an inline body to a referenced authored workflow slot.",
            ),
            cause=f"{type(exc.orig_exc).__name__}: {detail}",
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

    @classmethod
    def from_toml_decode(
        cls,
        *,
        path: Path,
        exc: tomllib.TOMLDecodeError,
    ) -> EmitError:
        location = DiagnosticLocation(path=path.resolve(), line=exc.lineno, column=exc.colno)
        excerpt, caret_column = _build_excerpt(exc.doc, line=exc.lineno, column=exc.colno)
        return cls.from_parts(
            code="E506",
            summary="Invalid emit config TOML",
            detail="The emit config file is not valid TOML.",
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=("Fix the TOML syntax before running `emit_docs` again.",),
            cause=exc.msg,
        )


def _coerce_diagnostic(error_or_diagnostic: PyPromptError | PyPromptDiagnostic) -> PyPromptDiagnostic:
    if isinstance(error_or_diagnostic, PyPromptError):
        return error_or_diagnostic.diagnostic
    return error_or_diagnostic


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, DiagnosticLocation):
        return {
            "path": _json_safe_value(value.path),
            "line": value.line,
            "column": value.column,
        }
    if isinstance(value, DiagnosticExcerptLine):
        return {
            "number": value.number,
            "text": value.text,
        }
    if isinstance(value, DiagnosticTraceFrame):
        return {
            "label": value.label,
            "location": _json_safe_value(value.location),
        }
    if isinstance(value, PyPromptDiagnostic):
        return {
            "code": value.code,
            "stage": value.stage,
            "summary": value.summary,
            "detail": value.detail,
            "location": _json_safe_value(value.location),
            "excerpt": _json_safe_value(value.excerpt),
            "caret_column": value.caret_column,
            "hints": _json_safe_value(value.hints),
            "trace": _json_safe_value(value.trace),
            "cause": value.cause,
        }
    return value


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


def _extract_tree_position(obj: object) -> tuple[int | None, int | None]:
    if isinstance(obj, Token):
        return getattr(obj, "line", None), getattr(obj, "column", None)
    if isinstance(obj, Tree):
        for child in obj.children:
            line, column = _extract_tree_position(child)
            if line is not None:
                return line, column
    return None, None


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
        re.compile(r"^Cyclic agent inheritance: (?P<detail>.+)$"),
        "E207",
        "Cyclic agent inheritance",
        lambda match: f"Agent inheritance cycle: {match.group('detail')}.",
        (),
    ),
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
        re.compile(r"^Missing local declaration ref in (?P<label>.+) (?P<owner>[^:]+): (?P<name>.+)$"),
        "E276",
        "Missing local declaration reference",
        lambda match: (
            f"Missing local declaration ref `{match.group('name')}` in {match.group('label')} `{match.group('owner')}`."
        ),
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
        re.compile(r"^Input source must stay typed in interpolation: (?P<name>.+)$"),
        "E275",
        "Input source must stay typed in interpolation",
        lambda match: f"Input `{match.group('name')}` must keep a typed `source` in interpolation.",
        (),
    ),
    (
        re.compile(r"^Output target must stay typed in interpolation: (?P<name>.+)$"),
        "E275",
        "Output target must stay typed in interpolation",
        lambda match: f"Output `{match.group('name')}` must keep a typed `target` in interpolation.",
        (),
    ),
    (
        re.compile(r"^Prompt source path is required for compilation\.$"),
        "E291",
        "Prompt source path is required for compilation",
        lambda _match: "Prompt source path is required for compilation.",
        (),
    ),
    (
        re.compile(r"^Could not resolve prompts/ root for (?P<path>.+)\.$"),
        "E292",
        "Could not resolve prompts root",
        lambda match: f"Could not resolve `prompts/` root for `{match.group('path')}`.",
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
    (
        re.compile(r"^Emit config must point at pyproject\.toml: (?P<path>.+)$"),
        "E507",
        "Emit config path must point at pyproject.toml",
        lambda match: f"Emit config path must point at `pyproject.toml`, got `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Missing pyproject\.toml: (?P<path>.+)$"),
        "E504",
        "Missing pyproject.toml",
        lambda match: f"Missing `pyproject.toml`: `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Emit target #(?P<index>.+) must be a TOML table\.$"),
        "E508",
        "Emit target must be a TOML table",
        lambda match: f"Emit target #{match.group('index')} must be a TOML table.",
        (),
    ),
    (
        re.compile(r"^Duplicate emit target name: (?P<name>.+)$"),
        "E509",
        "Duplicate emit target name",
        lambda match: f"Emit target `{match.group('name')}` is defined more than once.",
        (),
    ),
    (
        re.compile(r"^Emit target (?P<name>.+) must point at an AGENTS\.prompt entrypoint, got (?P<entrypoint>.+)$"),
        "E510",
        "Emit target entrypoint must be AGENTS.prompt",
        lambda match: (
            f"Emit target `{match.group('name')}` must point at an `AGENTS.prompt` entrypoint, got `{match.group('entrypoint')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Emit target (?P<name>.+) output_dir is a file: (?P<path>.+)$"),
        "E511",
        "Emit target output_dir is a file",
        lambda match: f"Emit target `{match.group('name')}` output_dir is a file: `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^(?P<label>.+) does not exist: (?P<value>.+)$"),
        "E512",
        "Emit config path does not exist",
        lambda match: f"{match.group('label')} does not exist: {match.group('value')}",
        (),
    ),
    (
        re.compile(r"^(?P<label>.+)\.(?P<key>.+) must be a string\.$"),
        "E513",
        "Emit config value must be a string",
        lambda match: f"{match.group('label')}.{match.group('key')} must be a string.",
        (),
    ),
    (
        re.compile(r"^Could not resolve prompts/ root for (?P<path>.+)$"),
        "E514",
        "Could not resolve prompts root",
        lambda match: f"Could not resolve `prompts/` root for `{match.group('path')}`.",
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
