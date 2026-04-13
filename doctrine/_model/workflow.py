from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import (
    AddressableRef,
    Expr,
    InheritItem,
    LawBody,
    LawPathSet,
    NameRef,
    ProseLine,
    RoleBlock,
    RoleScalar,
    RouteLine,
    SectionBodyRef,
    TrustSurfaceItem,
)
from doctrine._model.readable import ReadableBlock


SectionBodyItem: _TypeAlias = ProseLine | RouteLine | SectionBodyRef | "LocalSection" | ReadableBlock


@_dataclass(slots=True, frozen=True)
class LocalSection:
    key: str
    title: str
    items: tuple[SectionBodyItem, ...]


@_dataclass(slots=True, frozen=True)
class WorkflowUse:
    key: str
    target: NameRef


@_dataclass(slots=True, frozen=True)
class OverrideSection:
    key: str
    title: str | None
    items: tuple[SectionBodyItem, ...]


@_dataclass(slots=True, frozen=True)
class OverrideUse:
    key: str
    target: NameRef


RecordScalarValue: _TypeAlias = str | NameRef | AddressableRef


@_dataclass(slots=True, frozen=True)
class RecordScalar:
    key: str
    value: RecordScalarValue
    body: tuple["AnyRecordItem", ...] | None = None


@_dataclass(slots=True, frozen=True)
class RecordSection:
    key: str
    title: str
    items: tuple["AnyRecordItem", ...]


@_dataclass(slots=True, frozen=True)
class GuardedOutputSection:
    key: str
    title: str
    when_expr: Expr
    items: tuple["AnyRecordItem", ...]


@_dataclass(slots=True, frozen=True)
class GuardedOutputScalar:
    key: str
    value: RecordScalarValue
    when_expr: Expr
    body: tuple["AnyRecordItem", ...] | None = None


@_dataclass(slots=True, frozen=True)
class RecordRef:
    ref: NameRef
    body: tuple["AnyRecordItem", ...] | None = None


RecordItem: _TypeAlias = ProseLine | RecordScalar | RecordSection | RecordRef | ReadableBlock
AnyRecordItem: _TypeAlias = RecordItem | GuardedOutputSection | GuardedOutputScalar
OutputRecordItem: _TypeAlias = RecordItem | GuardedOutputSection | GuardedOutputScalar


@_dataclass(slots=True, frozen=True)
class SkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


SkillsSectionItem: _TypeAlias = ProseLine | SkillEntry


@_dataclass(slots=True, frozen=True)
class SkillsSection:
    key: str
    title: str
    items: tuple[SkillsSectionItem, ...]


@_dataclass(slots=True, frozen=True)
class OverrideSkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


@_dataclass(slots=True, frozen=True)
class OverrideSkillsSection:
    key: str
    title: str | None
    items: tuple[SkillsSectionItem, ...]


SkillsItem: _TypeAlias = (
    SkillsSection | SkillEntry | InheritItem | OverrideSkillsSection | OverrideSkillEntry
)


@_dataclass(slots=True, frozen=True)
class SkillsBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[SkillsItem, ...]


SkillsValue: _TypeAlias = SkillsBody | NameRef


@_dataclass(slots=True, frozen=True)
class OverrideIoSection:
    key: str
    title: str | None
    items: tuple[RecordItem, ...]


IoItem: _TypeAlias = RecordSection | RecordRef | InheritItem | OverrideIoSection


@_dataclass(slots=True, frozen=True)
class IoBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[IoItem, ...]


IoFieldValue: _TypeAlias = tuple[RecordItem, ...] | NameRef | IoBody


@_dataclass(slots=True, frozen=True)
class WorkflowSkillsItem:
    key: str
    value: SkillsValue


@_dataclass(slots=True, frozen=True)
class OverrideWorkflowSkillsItem:
    key: str
    value: SkillsValue


WorkflowItem: _TypeAlias = (
    LocalSection
    | WorkflowUse
    | InheritItem
    | OverrideSection
    | OverrideUse
    | WorkflowSkillsItem
    | OverrideWorkflowSkillsItem
)


@_dataclass(slots=True, frozen=True)
class WorkflowBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[WorkflowItem, ...]
    law: LawBody | None = None


@_dataclass(slots=True, frozen=True)
class WorkflowDecl:
    name: str
    body: WorkflowBody
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class RouteOnlyGuard:
    key: str
    expr: Expr


@_dataclass(slots=True, frozen=True)
class RouteOnlyRoute:
    key: str | None
    target: NameRef


@_dataclass(slots=True, frozen=True)
class RouteOnlyBody:
    title: str
    facts_ref: NameRef | None = None
    when_exprs: tuple[Expr, ...] = ()
    current_none: bool = False
    handoff_output_ref: NameRef | None = None
    guarded: tuple[RouteOnlyGuard, ...] = ()
    routes: tuple[RouteOnlyRoute, ...] = ()


@_dataclass(slots=True, frozen=True)
class RouteOnlyDecl:
    name: str
    body: RouteOnlyBody


@_dataclass(slots=True, frozen=True)
class GroundingPolicyStartFrom:
    source: str
    unless: str | None = None


@_dataclass(slots=True, frozen=True)
class GroundingPolicyForbid:
    value: str


@_dataclass(slots=True, frozen=True)
class GroundingPolicyAllow:
    value: str


@_dataclass(slots=True, frozen=True)
class GroundingPolicyRoute:
    condition: str
    target: NameRef


GroundingPolicyItem: _TypeAlias = (
    GroundingPolicyStartFrom
    | GroundingPolicyForbid
    | GroundingPolicyAllow
    | GroundingPolicyRoute
)


@_dataclass(slots=True, frozen=True)
class GroundingBody:
    title: str
    source_ref: NameRef | None = None
    target: str | None = None
    policy_items: tuple[GroundingPolicyItem, ...] = ()


@_dataclass(slots=True, frozen=True)
class GroundingDecl:
    name: str
    body: GroundingBody


@_dataclass(slots=True, frozen=True)
class SkillsDecl:
    name: str
    body: SkillsBody
    parent_ref: NameRef | None = None


WorkflowSlotValue: _TypeAlias = WorkflowBody | NameRef


@_dataclass(slots=True, frozen=True)
class AuthoredSlotField:
    key: str
    value: WorkflowSlotValue


@_dataclass(slots=True, frozen=True)
class AuthoredSlotAbstract:
    key: str


@_dataclass(slots=True, frozen=True)
class AuthoredSlotInherit:
    key: str


@_dataclass(slots=True, frozen=True)
class AuthoredSlotOverride:
    key: str
    value: WorkflowSlotValue


@_dataclass(slots=True, frozen=True)
class InputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class OutputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class AnalysisField:
    value: NameRef


@_dataclass(slots=True, frozen=True)
class DecisionField:
    value: NameRef


@_dataclass(slots=True, frozen=True)
class SkillsField:
    value: SkillsValue


@_dataclass(slots=True, frozen=True)
class ReviewField:
    value: NameRef


@_dataclass(slots=True, frozen=True)
class FinalOutputField:
    value: NameRef


Field: _TypeAlias = (
    RoleScalar
    | RoleBlock
    | AuthoredSlotField
    | AuthoredSlotAbstract
    | AuthoredSlotInherit
    | AuthoredSlotOverride
    | InputsField
    | OutputsField
    | AnalysisField
    | DecisionField
    | SkillsField
    | ReviewField
    | FinalOutputField
)


@_dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]
    title: str | None = None
    abstract: bool = False
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class InputStructureConfig:
    structure_ref: NameRef


@_dataclass(slots=True, frozen=True)
class InputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    structure: InputStructureConfig | None = None

    @property
    def structure_ref(self) -> NameRef | None:
        return None if self.structure is None else self.structure.structure_ref


@_dataclass(slots=True, frozen=True)
class InputsDecl:
    name: str
    body: IoBody
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class InputSourceDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaConfig:
    schema_ref: NameRef


@_dataclass(slots=True, frozen=True)
class OutputStructureConfig:
    structure_ref: NameRef


@_dataclass(slots=True, frozen=True)
class OutputDecl:
    name: str
    title: str
    items: tuple[OutputRecordItem, ...]
    schema: OutputSchemaConfig | None = None
    structure: OutputStructureConfig | None = None
    render_profile_ref: NameRef | None = None
    trust_surface: tuple[TrustSurfaceItem, ...] = ()

    @property
    def schema_ref(self) -> NameRef | None:
        return None if self.schema is None else self.schema.schema_ref

    @property
    def structure_ref(self) -> NameRef | None:
        return None if self.structure is None else self.structure.structure_ref


@_dataclass(slots=True, frozen=True)
class OutputsDecl:
    name: str
    body: IoBody
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class OutputTargetDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@_dataclass(slots=True, frozen=True)
class OutputShapeDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@_dataclass(slots=True, frozen=True)
class JsonSchemaDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@_dataclass(slots=True, frozen=True)
class SkillDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@_dataclass(slots=True, frozen=True)
class SkillPackageMetadata:
    name: str | None = None
    description: str | None = None
    version: str | None = None
    license: str | None = None


@_dataclass(slots=True, frozen=True)
class SkillPackageDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    metadata: SkillPackageMetadata


@_dataclass(slots=True, frozen=True)
class EnumMember:
    key: str
    title: str
    wire: str | None = None

    @property
    def value(self) -> str:
        return self.wire if self.wire is not None else self.title


@_dataclass(slots=True, frozen=True)
class EnumDecl:
    name: str
    title: str
    members: tuple[EnumMember, ...]
