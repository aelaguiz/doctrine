from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias


@_dataclass(slots=True, frozen=True)
class EmphasizedLine:
    kind: str
    text: str


ProseLine: _TypeAlias = str | EmphasizedLine


@_dataclass(slots=True, frozen=True)
class RoleScalar:
    text: str


@_dataclass(slots=True, frozen=True)
class RoleBlock:
    title: str
    lines: tuple[ProseLine, ...]


@_dataclass(slots=True, frozen=True)
class ImportPath:
    level: int
    module_parts: tuple[str, ...]


@_dataclass(slots=True, frozen=True)
class ImportDecl:
    path: ImportPath


@_dataclass(slots=True, frozen=True)
class NameRef:
    module_parts: tuple[str, ...]
    declaration_name: str


@_dataclass(slots=True, frozen=True)
class ExprRef:
    parts: tuple[str, ...]


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


@_dataclass(slots=True, frozen=True)
class RenderProfileDecl:
    name: str
    rules: tuple[RenderProfileRule, ...] = ()


@_dataclass(slots=True, frozen=True)
class AddressableRef:
    root: NameRef
    path: tuple[str, ...] = ()


@_dataclass(slots=True, frozen=True)
class RouteLine:
    label: str
    target: NameRef


@_dataclass(slots=True, frozen=True)
class SectionBodyRef:
    ref: AddressableRef


@_dataclass(slots=True, frozen=True)
class InheritItem:
    key: str
