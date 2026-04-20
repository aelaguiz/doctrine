"""Public error types and diagnostic rendering for Doctrine.

Stage labels. Every diagnostic carries a `stage` string set by the raising
subclass:

    ParseError    -> "parse"    (fallback code E199)
    CompileError  -> "compile"  (fallback code E299)
    EmitError     -> "emit"     (fallback code E599)
    DoctrineError -> "runtime"  (fallback code E999)

Code bands. Code bands are authoritative in `docs/COMPILER_ERRORS.md` and
are wider than the fallback first-digit would suggest:

    E001-E099   reserved language-rule errors (E001/E002/E003 have pinned meanings)
    E100-E199   parse
    E200-E468   semantic compile
    E469-E500   review-specific parse + compile
    E501-E699   emit / build-target
    E900-E999   internal bugs or invariant failures

Stage and band do not always map one-to-one. Some parser-transform failures
are raised as `ParseError` (stage="parse") but carry codes in the compile
band — e.g. `E309` on malformed grouped `inherit` is raised by
`ParseError.from_transform` via `TransformParseFailure`. Treat the code
catalog as the source of truth for the band; the stage records *where* in
the pipeline the failure was raised.

Adding a new subclass. Set both `stage` and `fallback_code` at class
definition time. A missing `fallback_code` inherits `DoctrineError`'s
`E999`, which silently lands the diagnostic in the runtime bucket regardless
of what the subclass actually represents.

`DoctrineDiagnostic` (from `_diagnostics.contracts`) is the immutable wire
shape: `(code, stage, summary, detail, location, excerpt, caret_column,
related, hints, trace, cause)`. `DoctrineError` wraps one and adds the
`prepend_trace` / `ensure_location` mutators for compile-path enrichment.
"""

from __future__ import annotations

import tomllib
from dataclasses import replace
from pathlib import Path
from typing import Any

from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
    VisitError,
)
from doctrine._diagnostics.contracts import (
    DiagnosticExcerptLine,
    DiagnosticLocation,
    DiagnosticRelatedLocation,
    DiagnosticTraceFrame,
    DoctrineDiagnostic,
    TransformParseFailure,
)
from doctrine._diagnostics.formatting import (
    _build_excerpt,
    _format_block,
    _format_excerpt,
    _format_location,
    _json_safe_value,
)
from doctrine._diagnostics.message_builders import _emit_diagnostic_from_message
from doctrine._diagnostics.parse_errors import (
    _classify_unexpected_token,
    _extract_toml_decode_position,
    _extract_tree_position,
    _format_expected_tokens,
    _format_parse_detail,
    _format_unexpected_token_cause,
)


def diagnostic_to_dict(error_or_diagnostic: DoctrineError | DoctrineDiagnostic) -> dict[str, Any]:
    diagnostic = _coerce_diagnostic(error_or_diagnostic)
    return _json_safe_value(diagnostic)


def format_diagnostic(error_or_diagnostic: DoctrineError | DoctrineDiagnostic) -> str:
    diagnostic = _coerce_diagnostic(error_or_diagnostic)
    lines = [f"{diagnostic.code} {diagnostic.stage} error: {diagnostic.summary}"]

    if diagnostic.location is not None:
        lines.extend(["", "Location:", f"- {_format_location(diagnostic.location)}"])

    if diagnostic.excerpt:
        lines.extend(["", "Source:"])
        lines.extend(
            _format_excerpt(
                diagnostic.excerpt,
                highlight_line=diagnostic.location.line if diagnostic.location is not None else None,
                caret_column=diagnostic.caret_column,
            )
        )

    if diagnostic.related:
        lines.extend(["", "Related:"])
        for related in diagnostic.related:
            location_text = "<unknown>"
            if related.location is not None:
                location_text = _format_location(related.location)
            lines.append(f"- {related.label}: {location_text}")
            if related.excerpt:
                lines.extend(
                    _format_excerpt(
                        related.excerpt,
                        highlight_line=(
                            related.location.line if related.location is not None else None
                        ),
                        caret_column=related.caret_column,
                    )
                )

    if diagnostic.detail:
        lines.extend(["", "Detail:"])
        lines.extend(_format_block(diagnostic.detail))

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


class DoctrineError(RuntimeError):
    """Base for every Doctrine diagnostic. Owns the runtime (E9xx) bucket.

    Subclasses override `stage` and `fallback_code` to claim their bucket.
    Raising `DoctrineError` directly means "no stage fits" and lands in E9xx.
    """

    stage = "runtime"
    fallback_code = "E999"
    fallback_summary = "Unexpected Doctrine error"

    def __init__(
        self,
        message: str | None = None,
        *,
        diagnostic: DoctrineDiagnostic | None = None,
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
        related: tuple[DiagnosticRelatedLocation, ...] = (),
        hints: tuple[str, ...] = (),
        trace: tuple[DiagnosticTraceFrame, ...] = (),
        cause: str | None = None,
    ) -> DoctrineError:
        return cls(
            diagnostic=DoctrineDiagnostic(
                code=code,
                stage=cls.stage,
                summary=summary,
                detail=detail,
                location=location,
                excerpt=excerpt,
                caret_column=caret_column,
                related=related,
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
    ) -> DoctrineError:
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
    ) -> DoctrineError:
        current_location = self.diagnostic.location
        resolved_path = (
            current_location.path
            if current_location is not None and current_location.path is not None
            else path
        )
        resolved_line = line if line is not None else (
            current_location.line if current_location is not None else None
        )
        resolved_column = column if column is not None else (
            current_location.column if current_location is not None else None
        )
        if (
            current_location is not None
            and current_location.path == resolved_path
            and current_location.line == resolved_line
            and current_location.column == resolved_column
            and self.diagnostic.excerpt
        ):
            return self
        excerpt = self.diagnostic.excerpt
        caret_column = self.diagnostic.caret_column
        if (
            not excerpt
            and resolved_path is not None
            and resolved_line is not None
            and resolved_column is not None
        ):
            try:
                source = Path(resolved_path).read_text(encoding="utf-8")
            except OSError:
                pass
            else:
                excerpt, caret_column = _build_excerpt(
                    source,
                    line=resolved_line,
                    column=resolved_column,
                )
        self.diagnostic = replace(
            self.diagnostic,
            location=DiagnosticLocation(
                path=resolved_path,
                line=resolved_line,
                column=resolved_column,
            ),
            excerpt=excerpt,
            caret_column=caret_column,
        )
        self.args = (format_diagnostic(self.diagnostic),)
        return self

    def _diagnostic_from_message(self, message: str) -> DoctrineDiagnostic:
        return DoctrineDiagnostic(
            code=self.fallback_code,
            stage=self.stage,
            summary=self.fallback_summary,
            detail=message,
        )


class ParseError(DoctrineError):
    """Parse-stage diagnostic (E1xx). Raised only from `doctrine.parser`.

    Two construction paths:
      - `from_lark`: lexer / parser failure (UnexpectedCharacters -> E102,
        UnexpectedEOF -> E103, UnexpectedToken -> classified by
        `_classify_unexpected_token`, anything else -> E199).
      - `from_transform`: post-parse transform failure. `TransformParseFailure`
        carries its own (code, summary, hints); invalid string literals map to
        E106; everything else defaults to E105.
    """

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
        line = getattr(exc.orig_exc, "line", None)
        column = getattr(exc.orig_exc, "column", None)
        if line is None:
            line, column = _extract_tree_position(exc.obj)
        location = DiagnosticLocation(path=path, line=line, column=column)
        excerpt, caret_column = _build_excerpt(source, line=line, column=column)
        detail = str(exc.orig_exc)
        code = "E105"
        summary = "Invalid authored slot body"
        hints = (
            "Do not attach an inline body to a referenced authored workflow slot.",
        )
        if isinstance(exc.orig_exc, TransformParseFailure):
            code = exc.orig_exc.code
            summary = exc.orig_exc.summary
            hints = exc.orig_exc.hints
        elif getattr(exc, "rule", None) in {"ESCAPED_STRING", "MULTILINE_STRING"} and isinstance(
            exc.orig_exc, (SyntaxError, ValueError)
        ):
            code = "E106"
            summary = "Invalid string literal"
            hints = (
                "Fix the quoted string so its escapes and delimiters are valid.",
            )
        return cls.from_parts(
            code=code,
            summary=summary,
            detail=detail,
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=hints,
            cause=f"{type(exc.orig_exc).__name__}: {detail}",
        )


class CompileError(DoctrineError):
    """Compile-stage diagnostic. Raised from `doctrine/_compiler/**`.

    Every compile-path raise should supply an explicit code via `from_parts`;
    E299 is only the "author forgot a code" fallback, not a design intent.
    Codes span the E200-E468 compile band (plus E469-E500 for review-specific
    checks and E900-E999 for invariant failures); see `docs/COMPILER_ERRORS.md`.
    """

    stage = "compile"
    fallback_code = "E299"
    fallback_summary = "Compile failure"


class EmitError(DoctrineError):
    """Emit-stage diagnostic. Raised from the three emit pipelines.

    Codes sit in the E501-E699 emit / build-target band.
    `from_toml_decode` is the dedicated constructor for `tomllib` failures on
    emit-config (`pyproject.toml [tool.doctrine.emit]`); it always emits E506
    with a caret anchored at the TOML decode position. Other emit errors use
    the generic `from_parts` path with an explicit code.
    """

    stage = "emit"
    fallback_code = "E599"
    fallback_summary = "Emit failure"

    def _diagnostic_from_message(self, message: str) -> DoctrineDiagnostic:
        return _emit_diagnostic_from_message(message)

    @classmethod
    def from_toml_decode(
        cls,
        *,
        path: Path,
        exc: tomllib.TOMLDecodeError,
    ) -> EmitError:
        line = getattr(exc, "lineno", None)
        column = getattr(exc, "colno", None)
        if line is None or column is None:
            line, column = _extract_toml_decode_position(
                getattr(exc, "doc", ""),
                getattr(exc, "pos", None),
            )
        location = DiagnosticLocation(path=path.resolve(), line=line, column=column)
        excerpt, caret_column = _build_excerpt(getattr(exc, "doc", ""), line=line, column=column)
        return cls.from_parts(
            code="E506",
            summary="Invalid emit config TOML",
            detail="The emit config file is not valid TOML.",
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=("Fix the TOML syntax before running `emit_docs` again.",),
            cause=getattr(exc, "msg", str(exc)),
        )


def _coerce_diagnostic(error_or_diagnostic: DoctrineError | DoctrineDiagnostic) -> DoctrineDiagnostic:
    if isinstance(error_or_diagnostic, DoctrineError):
        return error_or_diagnostic.diagnostic
    return error_or_diagnostic
