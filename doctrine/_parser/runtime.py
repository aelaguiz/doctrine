from __future__ import annotations

import threading
from dataclasses import replace as _replace
from pathlib import Path as _Path
from typing import Callable as _Callable

from lark import Lark
from lark.exceptions import UnexpectedInput, VisitError

from doctrine import model
from doctrine.diagnostics import ParseError
from doctrine.indenter import DoctrineIndenter


_THREAD_LOCAL_STATE = threading.local()
_GRAMMAR_PATH = _Path(__file__).resolve().parents[1] / "grammars" / "doctrine.lark"


def build_lark_parser() -> Lark:
    parser = getattr(_THREAD_LOCAL_STATE, "lark_parser", None)
    if parser is None:
        parser = Lark.open(
            str(_GRAMMAR_PATH),
            parser="lalr",
            lexer="contextual",
            postlex=DoctrineIndenter(),
            strict=True,
            maybe_placeholders=False,
            propagate_positions=True,
        )
        _THREAD_LOCAL_STATE.lark_parser = parser
    return parser


def parse_text(
    source: str,
    *,
    source_path: str | _Path | None = None,
    transform: _Callable[[object], model.PromptFile],
) -> model.PromptFile:
    resolved_path = _Path(source_path).resolve() if source_path is not None else None
    try:
        tree = build_lark_parser().parse(source)
    except UnexpectedInput as exc:
        raise ParseError.from_lark(source=source, path=resolved_path, exc=exc) from exc
    try:
        prompt_file = transform(tree)
        return _replace(prompt_file, source_path=resolved_path)
    except VisitError as exc:
        if isinstance(exc.orig_exc, (SyntaxError, ValueError)):
            raise ParseError.from_transform(source=source, path=resolved_path, exc=exc) from exc
        raise


def parse_file(
    path: str | _Path,
    *,
    transform: _Callable[[object], model.PromptFile],
) -> model.PromptFile:
    resolved_path = _Path(path).resolve()
    return parse_text(resolved_path.read_text(), source_path=resolved_path, transform=transform)
