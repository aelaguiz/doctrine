from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import TypeAlias as _TypeAlias


@_dataclass(slots=True, frozen=True)
class EmphasizedLine:
    kind: str
    text: str


ProseLine: _TypeAlias = str | EmphasizedLine


# Compile diagnostics need spans on authored model values so later compiler
# stages can still point at exact lines without keeping a parallel side map.
@_dataclass(slots=True, frozen=True)
class SourceSpan:
    line: int
    column: int


@_dataclass(slots=True, frozen=True)
class RoleScalar:
    text: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RoleBlock:
    title: str
    lines: tuple[ProseLine, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ImportPath:
    level: int
    module_parts: tuple[str, ...]


@_dataclass(slots=True, frozen=True)
class ImportDecl:
    path: ImportPath
    imported_name: str | None = None
    alias: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class NameRef:
    module_parts: tuple[str, ...]
    declaration_name: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ExprRef:
    parts: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ExprCall:
    name: str
    args: tuple["Expr", ...]


@_dataclass(slots=True, frozen=True)
class ExprSet:
    items: tuple["Expr", ...]


@_dataclass(slots=True, frozen=True)
class ExprBinary:
    op: str
    left: "Expr"
    right: "Expr"


Expr: _TypeAlias = ExprRef | ExprCall | ExprSet | ExprBinary | str | int | bool


@_dataclass(slots=True, frozen=True)
class RenderProfileRule:
    target_parts: tuple[str, ...]
    mode: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RenderProfileDecl:
    name: str
    rules: tuple[RenderProfileRule, ...] = ()
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class AddressableRef:
    root: NameRef
    path: tuple[str, ...] = ()
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RouteLine:
    label: str
    target: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SectionBodyRef:
    ref: AddressableRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class InheritItem:
    key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)
