from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import Expr, NameRef


@_dataclass(slots=True, frozen=True)
class LawPath:
    parts: tuple[str, ...]
    wildcard: bool = False


@_dataclass(slots=True, frozen=True)
class LawPathSet:
    paths: tuple[LawPath, ...]
    except_paths: tuple[LawPath, ...] = ()


@_dataclass(slots=True, frozen=True)
class ActiveWhenStmt:
    expr: Expr


@_dataclass(slots=True, frozen=True)
class ModeStmt:
    name: str
    expr: Expr
    enum_ref: NameRef


@_dataclass(slots=True, frozen=True)
class MustStmt:
    expr: Expr


@_dataclass(slots=True, frozen=True)
class CurrentArtifactStmt:
    target: LawPath
    carrier: LawPath


@_dataclass(slots=True, frozen=True)
class CurrentNoneStmt:
    pass


@_dataclass(slots=True, frozen=True)
class OwnOnlyStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class PreserveStmt:
    kind: str
    target: LawPathSet
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class SupportOnlyStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class IgnoreStmt:
    target: LawPathSet
    bases: tuple[str, ...]
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class InvalidateStmt:
    target: LawPath
    carrier: LawPath
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class ForbidStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class WhenStmt:
    expr: Expr
    items: tuple["LawStmt", ...]


@_dataclass(slots=True, frozen=True)
class MatchArm:
    head: Expr | None
    items: tuple["LawStmt", ...]
    display_label: str | None = None


@_dataclass(slots=True, frozen=True)
class MatchStmt:
    expr: Expr
    cases: tuple[MatchArm, ...]


@_dataclass(slots=True, frozen=True)
class RouteFromArm:
    head: Expr | None
    route: "LawRouteStmt"
    display_label: str | None = None


@_dataclass(slots=True, frozen=True)
class RouteFromStmt:
    expr: Expr
    enum_ref: NameRef
    cases: tuple[RouteFromArm, ...]


@_dataclass(slots=True, frozen=True)
class StopStmt:
    message: str | None = None
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class LawRouteStmt:
    label: str
    target: NameRef
    when_expr: Expr | None = None
    choice_enum_ref: NameRef | None = None
    choice_case_heads: tuple[Expr, ...] = ()
    choice_else: bool = False


LawStmt: _TypeAlias = (
    ActiveWhenStmt
    | ModeStmt
    | MustStmt
    | CurrentArtifactStmt
    | CurrentNoneStmt
    | OwnOnlyStmt
    | PreserveStmt
    | SupportOnlyStmt
    | IgnoreStmt
    | InvalidateStmt
    | ForbidStmt
    | WhenStmt
    | MatchStmt
    | RouteFromStmt
    | StopStmt
    | LawRouteStmt
)


@_dataclass(slots=True, frozen=True)
class LawSection:
    key: str
    items: tuple[LawStmt, ...]


@_dataclass(slots=True, frozen=True)
class LawInherit:
    key: str


@_dataclass(slots=True, frozen=True)
class LawOverrideSection:
    key: str
    items: tuple[LawStmt, ...]


LawTopLevelItem: _TypeAlias = LawStmt | LawSection | LawInherit | LawOverrideSection


@_dataclass(slots=True, frozen=True)
class LawBody:
    items: tuple[LawTopLevelItem, ...]
