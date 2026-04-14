from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import AddressableRef, Expr, InheritItem, NameRef, ProseLine
from doctrine._model.readable import ReadableBlock


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
