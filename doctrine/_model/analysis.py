from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import Expr, InheritItem, NameRef, ProseLine, SectionBodyRef
from doctrine._model.law import LawPathSet


@_dataclass(slots=True, frozen=True)
class ProveStmt:
    target_title: str
    basis: LawPathSet


@_dataclass(slots=True, frozen=True)
class DeriveStmt:
    target_title: str
    basis: LawPathSet


@_dataclass(slots=True, frozen=True)
class ClassifyStmt:
    target_title: str
    enum_ref: NameRef


@_dataclass(slots=True, frozen=True)
class CompareStmt:
    target_title: str
    basis: LawPathSet
    using_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class DefendStmt:
    target_title: str
    basis: LawPathSet


AnalysisSectionItem: _TypeAlias = (
    ProseLine
    | SectionBodyRef
    | ProveStmt
    | DeriveStmt
    | ClassifyStmt
    | CompareStmt
    | DefendStmt
)


@_dataclass(slots=True, frozen=True)
class AnalysisSection:
    key: str
    title: str
    items: tuple[AnalysisSectionItem, ...]


@_dataclass(slots=True, frozen=True)
class AnalysisOverrideSection:
    key: str
    title: str | None
    items: tuple[AnalysisSectionItem, ...]


AnalysisItem: _TypeAlias = AnalysisSection | InheritItem | AnalysisOverrideSection


@_dataclass(slots=True, frozen=True)
class AnalysisBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[AnalysisItem, ...]


@_dataclass(slots=True, frozen=True)
class AnalysisDecl:
    name: str
    body: AnalysisBody
    parent_ref: NameRef | None = None
    render_profile_ref: NameRef | None = None

    @property
    def title(self) -> str:
        return self.body.title


@_dataclass(slots=True, frozen=True)
class DecisionMinimumCandidates:
    count: int


@_dataclass(slots=True, frozen=True)
class DecisionRequiredItem:
    key: str


@_dataclass(slots=True, frozen=True)
class DecisionChooseWinner:
    pass


@_dataclass(slots=True, frozen=True)
class DecisionRankBy:
    dimensions: tuple[str, ...]


DecisionItem: _TypeAlias = (
    DecisionMinimumCandidates | DecisionRequiredItem | DecisionChooseWinner | DecisionRankBy
)


@_dataclass(slots=True, frozen=True)
class DecisionBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[DecisionItem, ...]


@_dataclass(slots=True, frozen=True)
class DecisionDecl:
    name: str
    body: DecisionBody
    render_profile_ref: NameRef | None = None

    @property
    def title(self) -> str:
        return self.body.title
