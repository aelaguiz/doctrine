from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import Expr, InheritItem, NameRef, ProseLine, SourceSpan
from doctrine._model.law import IgnoreStmt, PreserveStmt, SupportOnlyStmt


@_dataclass(slots=True, frozen=True)
class ReviewSubjectConfig:
    subjects: tuple[NameRef, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewSubjectMapEntry:
    enum_member_ref: NameRef
    artifact_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewSubjectMapConfig:
    entries: tuple[ReviewSubjectMapEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewContractRef:
    ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewContractConfig:
    contract: ReviewContractRef
    source_span: SourceSpan | None = _field(default=None, compare=False)

    @property
    def contract_ref(self) -> NameRef:
        return self.contract.ref


@_dataclass(slots=True, frozen=True)
class ReviewCommentOutputConfig:
    output_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewFieldBinding:
    semantic_field: str
    field_path: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewFieldsConfig:
    bindings: tuple[ReviewFieldBinding, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewSelectorConfig:
    field_name: str
    expr: Expr
    enum_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ContractGateRef:
    key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SectionGateRef:
    key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


ReviewGateLabel: _TypeAlias = str | ContractGateRef | SectionGateRef


@_dataclass(slots=True, frozen=True)
class ReviewBlockStmt:
    gate: ReviewGateLabel
    expr: Expr
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewRejectStmt:
    gate: ReviewGateLabel
    expr: Expr
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewAcceptStmt:
    gate: ReviewGateLabel
    expr: Expr
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOutputFieldRef:
    parts: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewCurrentArtifactStmt:
    artifact_ref: NameRef
    carrier: ReviewOutputFieldRef
    when_expr: Expr | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewCurrentNoneStmt:
    when_expr: Expr | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewCarryStmt:
    field_name: str
    expr: Expr
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeRouteStmt:
    label: str
    target: NameRef
    when_expr: Expr | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewMatchHead:
    options: tuple[Expr, ...]
    when_expr: Expr | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewPreOutcomeWhenStmt:
    expr: Expr
    items: tuple["ReviewPreOutcomeStmt", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeWhenStmt:
    expr: Expr
    items: tuple["ReviewOutcomeStmt", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewPreOutcomeMatchArm:
    head: ReviewMatchHead | None
    items: tuple["ReviewPreOutcomeStmt", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeMatchArm:
    head: ReviewMatchHead | None
    items: tuple["ReviewOutcomeStmt", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewPreOutcomeMatchStmt:
    expr: Expr
    cases: tuple[ReviewPreOutcomeMatchArm, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeMatchStmt:
    expr: Expr
    cases: tuple[ReviewOutcomeMatchArm, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


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
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOutcomeSection:
    key: str
    title: str | None
    items: tuple[ReviewOutcomeStmt, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOverrideFields:
    bindings: tuple[ReviewFieldBinding, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOverrideSection:
    key: str
    title: str | None
    items: tuple[ReviewPreOutcomeStmt, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewOverrideOutcomeSection:
    key: str
    title: str | None
    items: tuple[ReviewOutcomeStmt, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


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
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewCasesConfig:
    cases: tuple[ReviewCase, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


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
    source_span: SourceSpan | None = _field(default=None, compare=False)
