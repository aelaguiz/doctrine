from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import Expr, InheritItem, NameRef, ProseLine
from doctrine._model.law import IgnoreStmt, PreserveStmt, SupportOnlyStmt


@_dataclass(slots=True, frozen=True)
class ReviewSubjectConfig:
    subjects: tuple[NameRef, ...]


@_dataclass(slots=True, frozen=True)
class ReviewSubjectMapEntry:
    enum_member_ref: NameRef
    artifact_ref: NameRef


@_dataclass(slots=True, frozen=True)
class ReviewSubjectMapConfig:
    entries: tuple[ReviewSubjectMapEntry, ...]


@_dataclass(slots=True, frozen=True)
class ReviewContractRef:
    ref: NameRef


@_dataclass(slots=True, frozen=True)
class ReviewContractConfig:
    contract: ReviewContractRef

    @property
    def contract_ref(self) -> NameRef:
        return self.contract.ref


@_dataclass(slots=True, frozen=True)
class ReviewCommentOutputConfig:
    output_ref: NameRef


@_dataclass(slots=True, frozen=True)
class ReviewFieldBinding:
    semantic_field: str
    field_path: tuple[str, ...]


@_dataclass(slots=True, frozen=True)
class ReviewFieldsConfig:
    bindings: tuple[ReviewFieldBinding, ...]


@_dataclass(slots=True, frozen=True)
class ReviewSelectorConfig:
    field_name: str
    expr: Expr
    enum_ref: NameRef


@_dataclass(slots=True, frozen=True)
class ContractGateRef:
    key: str


@_dataclass(slots=True, frozen=True)
class SectionGateRef:
    key: str


ReviewGateLabel: _TypeAlias = str | ContractGateRef | SectionGateRef


@_dataclass(slots=True, frozen=True)
class ReviewBlockStmt:
    gate: ReviewGateLabel
    expr: Expr


@_dataclass(slots=True, frozen=True)
class ReviewRejectStmt:
    gate: ReviewGateLabel
    expr: Expr


@_dataclass(slots=True, frozen=True)
class ReviewAcceptStmt:
    gate: ReviewGateLabel
    expr: Expr


@_dataclass(slots=True, frozen=True)
class ReviewOutputFieldRef:
    parts: tuple[str, ...]


@_dataclass(slots=True, frozen=True)
class ReviewCurrentArtifactStmt:
    artifact_ref: NameRef
    carrier: ReviewOutputFieldRef
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class ReviewCurrentNoneStmt:
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class ReviewCarryStmt:
    field_name: str
    expr: Expr


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeRouteStmt:
    label: str
    target: NameRef
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class ReviewMatchHead:
    options: tuple[Expr, ...]
    when_expr: Expr | None = None


@_dataclass(slots=True, frozen=True)
class ReviewPreOutcomeWhenStmt:
    expr: Expr
    items: tuple["ReviewPreOutcomeStmt", ...]


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeWhenStmt:
    expr: Expr
    items: tuple["ReviewOutcomeStmt", ...]


@_dataclass(slots=True, frozen=True)
class ReviewPreOutcomeMatchArm:
    head: ReviewMatchHead | None
    items: tuple["ReviewPreOutcomeStmt", ...]


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeMatchArm:
    head: ReviewMatchHead | None
    items: tuple["ReviewOutcomeStmt", ...]


@_dataclass(slots=True, frozen=True)
class ReviewPreOutcomeMatchStmt:
    expr: Expr
    cases: tuple[ReviewPreOutcomeMatchArm, ...]


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeMatchStmt:
    expr: Expr
    cases: tuple[ReviewOutcomeMatchArm, ...]


ReviewPreOutcomeStmt: _TypeAlias = (
    ReviewBlockStmt
    | ReviewRejectStmt
    | ReviewAcceptStmt
    | PreserveStmt
    | SupportOnlyStmt
    | IgnoreStmt
    | ReviewPreOutcomeWhenStmt
    | ReviewPreOutcomeMatchStmt
    | ProseLine
)


ReviewOutcomeStmt: _TypeAlias = (
    ReviewCurrentArtifactStmt
    | ReviewCurrentNoneStmt
    | ReviewCarryStmt
    | ReviewOutcomeRouteStmt
    | ReviewOutcomeWhenStmt
    | ReviewOutcomeMatchStmt
    | ProseLine
)


@_dataclass(slots=True, frozen=True)
class ReviewSection:
    key: str
    title: str | None
    items: tuple[ReviewPreOutcomeStmt, ...]


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeSection:
    key: str
    title: str | None
    items: tuple[ReviewOutcomeStmt, ...]


@_dataclass(slots=True, frozen=True)
class ReviewOverrideFields:
    bindings: tuple[ReviewFieldBinding, ...]


@_dataclass(slots=True, frozen=True)
class ReviewOverrideSection:
    key: str
    title: str | None
    items: tuple[ReviewPreOutcomeStmt, ...]


@_dataclass(slots=True, frozen=True)
class ReviewOverrideOutcomeSection:
    key: str
    title: str | None
    items: tuple[ReviewOutcomeStmt, ...]


@_dataclass(slots=True, frozen=True)
class ReviewCase:
    key: str
    title: str
    head: ReviewMatchHead
    subject: ReviewSubjectConfig
    contract: ReviewContractConfig
    checks: tuple[ReviewPreOutcomeStmt, ...]
    on_accept: ReviewOutcomeSection
    on_reject: ReviewOutcomeSection


@_dataclass(slots=True, frozen=True)
class ReviewCasesConfig:
    cases: tuple[ReviewCase, ...]


ReviewItem: _TypeAlias = (
    ReviewSubjectConfig
    | ReviewSubjectMapConfig
    | ReviewContractConfig
    | ReviewCommentOutputConfig
    | ReviewFieldsConfig
    | ReviewSelectorConfig
    | ReviewCasesConfig
    | ReviewSection
    | ReviewOutcomeSection
    | InheritItem
    | ReviewOverrideFields
    | ReviewOverrideSection
    | ReviewOverrideOutcomeSection
)


@_dataclass(slots=True, frozen=True)
class ReviewBody:
    title: str
    items: tuple[ReviewItem, ...]


@_dataclass(slots=True, frozen=True)
class ReviewDecl:
    name: str
    body: ReviewBody
    abstract: bool = False
    parent_ref: NameRef | None = None
    family: bool = False
