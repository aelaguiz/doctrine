from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import Literal as _Literal, TYPE_CHECKING, TypeAlias as _TypeAlias

from doctrine._model.core import AddressableRef, Expr, InheritItem, NameRef, ProseLine, SourceSpan
from doctrine._model.readable import ReadableBlock, ReadableOverrideBlock

if TYPE_CHECKING:
    from doctrine._compiler.resolve.field_types import FieldTypeRef


@_dataclass(slots=True, frozen=True)
class TrustSurfaceItem:
    path: tuple[str, ...]
    when_expr: Expr | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


RecordScalarValue: _TypeAlias = str | NameRef | AddressableRef


@_dataclass(slots=True, frozen=True)
class RecordScalar:
    key: str
    value: RecordScalarValue
    body: tuple["AnyRecordItem", ...] | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RecordSection:
    key: str
    title: str
    items: tuple["AnyRecordItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class IoSection:
    key: str
    title: str | None
    items: tuple["RecordItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class GuardedOutputSection:
    key: str
    title: str
    when_expr: Expr
    items: tuple["AnyRecordItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class GuardedOutputScalar:
    key: str
    value: RecordScalarValue
    when_expr: Expr
    body: tuple["AnyRecordItem", ...] | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RecordRef:
    ref: NameRef
    body: tuple["AnyRecordItem", ...] | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewRouteVia:
    section: _Literal["on_accept", "on_reject"]
    resolution: _Literal["route"]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputRecordCase:
    enum_member_ref: NameRef
    items: tuple["AnyRecordItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


RecordItem: _TypeAlias = ProseLine | RecordScalar | RecordSection | RecordRef | ReadableBlock
AnyRecordItem: _TypeAlias = (
    RecordItem | GuardedOutputSection | GuardedOutputScalar | ReviewRouteVia | OutputRecordCase
)
OutputRecordItem: _TypeAlias = (
    RecordItem | GuardedOutputSection | GuardedOutputScalar | ReviewRouteVia | OutputRecordCase
)


@_dataclass(slots=True, frozen=True)
class OutputOverrideRecordScalar:
    key: str
    value: RecordScalarValue
    body: tuple["AnyRecordItem", ...] | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputOverrideRecordSection:
    key: str
    title: str | None
    items: tuple["AnyRecordItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputOverrideGuardedOutputSection:
    key: str
    title: str | None
    when_expr: Expr
    items: tuple["AnyRecordItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputOverrideGuardedOutputScalar:
    key: str
    value: RecordScalarValue
    when_expr: Expr
    body: tuple["AnyRecordItem", ...] | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


OutputOverrideItem: _TypeAlias = (
    OutputOverrideRecordScalar
    | OutputOverrideRecordSection
    | OutputOverrideGuardedOutputSection
    | OutputOverrideGuardedOutputScalar
    | ReadableOverrideBlock
)
OutputAuthoredItem: _TypeAlias = OutputRecordItem | InheritItem | OutputOverrideItem


@_dataclass(slots=True, frozen=True)
class OverrideIoSection:
    key: str
    title: str | None
    items: tuple[RecordItem, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


IoItem: _TypeAlias = IoSection | RecordRef | InheritItem | OverrideIoSection


@_dataclass(slots=True, frozen=True)
class IoBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[IoItem, ...]


IoFieldValue: _TypeAlias = tuple[RecordItem, ...] | NameRef | IoBody


@_dataclass(slots=True, frozen=True)
class InputStructureConfig:
    structure_ref: NameRef


@_dataclass(slots=True, frozen=True)
class InputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    structure: InputStructureConfig | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)

    @property
    def structure_ref(self) -> NameRef | None:
        return None if self.structure is None else self.structure.structure_ref


@_dataclass(slots=True, frozen=True)
class InputsDecl:
    name: str
    body: IoBody
    parent_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class InputSourceDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


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
    items: tuple[OutputAuthoredItem, ...]
    schema: OutputSchemaConfig | None = None
    structure: OutputStructureConfig | None = None
    render_profile_ref: NameRef | None = None
    trust_surface: tuple[TrustSurfaceItem, ...] = ()
    parent_ref: NameRef | None = None
    schema_mode: str | None = None
    structure_mode: str | None = None
    render_profile_mode: str | None = None
    trust_surface_mode: str | None = None
    schema_source_span: SourceSpan | None = _field(default=None, compare=False)
    structure_source_span: SourceSpan | None = _field(default=None, compare=False)
    render_profile_source_span: SourceSpan | None = _field(default=None, compare=False)
    trust_surface_source_span: SourceSpan | None = _field(default=None, compare=False)
    source_span: SourceSpan | None = _field(default=None, compare=False)

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
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputTargetDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    delivery_skill_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


OutputShapeAuthoredItem: _TypeAlias = OutputRecordItem | InheritItem | OutputOverrideItem


@_dataclass(slots=True, frozen=True)
class OutputShapeSelectorConfig:
    field_name: str
    enum_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputShapeDecl:
    name: str
    title: str
    items: tuple[OutputShapeAuthoredItem, ...]
    parent_ref: NameRef | None = None
    selector: OutputShapeSelectorConfig | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaField:
    key: str
    title: str
    items: tuple["OutputSchemaBodyItem", ...]
    type_ref: "FieldTypeRef | None" = _field(default=None, compare=False)
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaDef:
    key: str
    title: str
    items: tuple["OutputSchemaBodyItem", ...]
    type_ref: "FieldTypeRef | None" = _field(default=None, compare=False)
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaRouteChoice:
    key: str
    title: str
    target_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaRouteField:
    key: str
    title: str
    items: tuple["OutputSchemaRouteBodyItem", ...]
    type_ref: "FieldTypeRef | None" = _field(default=None, compare=False)
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaOverrideField:
    key: str
    title: str | None
    items: tuple["OutputSchemaBodyItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaOverrideDef:
    key: str
    title: str | None
    items: tuple["OutputSchemaBodyItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaOverrideRouteField:
    key: str
    title: str | None
    items: tuple["OutputSchemaRouteBodyItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


OutputSchemaLiteralValue: _TypeAlias = str | int | float | bool | None


@_dataclass(slots=True, frozen=True)
class OutputSchemaFlag:
    key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaSetting:
    key: str
    value: str | int | float | bool | None | NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaEnum:
    values: tuple[OutputSchemaLiteralValue, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaValues:
    values: tuple[OutputSchemaLiteralValue, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaItems:
    value: NameRef | tuple["OutputSchemaBodyItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaVariant:
    key: str | None
    items: tuple["OutputSchemaBodyItem", ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaAnyOf:
    variants: tuple[OutputSchemaVariant, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaExampleEntry:
    key: str
    value: "OutputSchemaExampleValue"


@_dataclass(slots=True, frozen=True)
class OutputSchemaExampleObject:
    entries: tuple[OutputSchemaExampleEntry, ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaExampleArray:
    items: tuple["OutputSchemaExampleValue", ...]


OutputSchemaExampleValue: _TypeAlias = (
    OutputSchemaExampleObject | OutputSchemaExampleArray | OutputSchemaLiteralValue
)


@_dataclass(slots=True, frozen=True)
class OutputSchemaExample:
    key: str
    value: OutputSchemaExampleObject
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputSchemaOverrideExample:
    key: str
    value: OutputSchemaExampleObject
    source_span: SourceSpan | None = _field(default=None, compare=False)


OutputSchemaBodyItem: _TypeAlias = (
    OutputSchemaFlag
    | OutputSchemaSetting
    | OutputSchemaEnum
    | OutputSchemaValues
    | OutputSchemaItems
    | OutputSchemaAnyOf
    | OutputSchemaField
    | OutputSchemaDef
    | OutputSchemaRouteField
)
OutputSchemaRouteBodyItem: _TypeAlias = OutputSchemaBodyItem | OutputSchemaRouteChoice
OutputSchemaAuthoredItem: _TypeAlias = (
    OutputSchemaField
    | OutputSchemaRouteField
    | OutputSchemaDef
    | OutputSchemaExample
    | InheritItem
    | OutputSchemaOverrideField
    | OutputSchemaOverrideRouteField
    | OutputSchemaOverrideDef
    | OutputSchemaOverrideExample
)


@_dataclass(slots=True, frozen=True)
class OutputSchemaDecl:
    name: str
    title: str
    items: tuple[OutputSchemaAuthoredItem, ...]
    parent_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    package_link: "SkillPackageLink" | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillPackageMetadata:
    name: str | None = None
    description: str | None = None
    version: str | None = None
    license: str | None = None


@_dataclass(slots=True, frozen=True)
class SkillPackageEmitEntry:
    path: str
    ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillPackageLink:
    package_id: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillPackageHostSlot:
    key: str
    family: str
    title: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillPackageDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    metadata: SkillPackageMetadata
    emit_entries: tuple[SkillPackageEmitEntry, ...] = ()
    host_contract: tuple[SkillPackageHostSlot, ...] = ()
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class EnumMember:
    key: str
    title: str
    wire: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)

    @property
    def value(self) -> str:
        return self.wire if self.wire is not None else self.title


@_dataclass(slots=True, frozen=True)
class EnumDecl:
    name: str
    title: str
    members: tuple[EnumMember, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)
