from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import AddressableRef, Expr, InheritItem, NameRef, ProseLine
from doctrine._model.readable import ReadableBlock, ReadableOverrideBlock


@_dataclass(slots=True, frozen=True)
class TrustSurfaceItem:
    path: tuple[str, ...]
    when_expr: Expr | None = None


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
class OutputOverrideRecordScalar:
    key: str
    value: RecordScalarValue
    body: tuple["AnyRecordItem", ...] | None = None


@_dataclass(slots=True, frozen=True)
class OutputOverrideRecordSection:
    key: str
    title: str | None
    items: tuple["AnyRecordItem", ...]


@_dataclass(slots=True, frozen=True)
class OutputOverrideGuardedOutputSection:
    key: str
    title: str | None
    when_expr: Expr
    items: tuple["AnyRecordItem", ...]


@_dataclass(slots=True, frozen=True)
class OutputOverrideGuardedOutputScalar:
    key: str
    value: RecordScalarValue
    when_expr: Expr
    body: tuple["AnyRecordItem", ...] | None = None


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


IoItem: _TypeAlias = RecordSection | RecordRef | InheritItem | OverrideIoSection


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


OutputShapeAuthoredItem: _TypeAlias = OutputRecordItem | InheritItem | OutputOverrideItem


@_dataclass(slots=True, frozen=True)
class OutputShapeDecl:
    name: str
    title: str
    items: tuple[OutputShapeAuthoredItem, ...]
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class OutputSchemaField:
    key: str
    title: str
    items: tuple["OutputSchemaBodyItem", ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaDef:
    key: str
    title: str
    items: tuple["OutputSchemaBodyItem", ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaOverrideField:
    key: str
    title: str | None
    items: tuple["OutputSchemaBodyItem", ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaOverrideDef:
    key: str
    title: str | None
    items: tuple["OutputSchemaBodyItem", ...]


OutputSchemaLiteralValue: _TypeAlias = str | int | float | bool | None


@_dataclass(slots=True, frozen=True)
class OutputSchemaFlag:
    key: str


@_dataclass(slots=True, frozen=True)
class OutputSchemaSetting:
    key: str
    value: str | int | float | bool | None | NameRef


@_dataclass(slots=True, frozen=True)
class OutputSchemaEnum:
    values: tuple[OutputSchemaLiteralValue, ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaItems:
    value: NameRef | tuple["OutputSchemaBodyItem", ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaVariant:
    key: str | None
    items: tuple["OutputSchemaBodyItem", ...]


@_dataclass(slots=True, frozen=True)
class OutputSchemaAnyOf:
    variants: tuple[OutputSchemaVariant, ...]


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


@_dataclass(slots=True, frozen=True)
class OutputSchemaOverrideExample:
    key: str
    value: OutputSchemaExampleObject


OutputSchemaBodyItem: _TypeAlias = (
    OutputSchemaFlag
    | OutputSchemaSetting
    | OutputSchemaEnum
    | OutputSchemaItems
    | OutputSchemaAnyOf
    | OutputSchemaField
    | OutputSchemaDef
)
OutputSchemaAuthoredItem: _TypeAlias = (
    OutputSchemaField
    | OutputSchemaDef
    | OutputSchemaExample
    | InheritItem
    | OutputSchemaOverrideField
    | OutputSchemaOverrideDef
    | OutputSchemaOverrideExample
)


@_dataclass(slots=True, frozen=True)
class OutputSchemaDecl:
    name: str
    title: str
    items: tuple[OutputSchemaAuthoredItem, ...]
    parent_ref: NameRef | None = None


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
