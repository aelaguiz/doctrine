from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import TYPE_CHECKING, TypeAlias as _TypeAlias

from doctrine._model.core import Expr, InheritItem, NameRef, ProseLine, SourceSpan

if TYPE_CHECKING:
    from doctrine._compiler.resolve.field_types import FieldTypeRef


ReadableRequirement: _TypeAlias = str


@_dataclass(slots=True, frozen=True)
class ReadableListItem:
    key: str | None
    text: ProseLine
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableDefinitionItem:
    key: str
    title: str
    body: tuple[ProseLine, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadablePropertyItem:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadablePropertiesData:
    entries: tuple[ReadablePropertyItem, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableSchemaEntry:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()
    type_ref: "FieldTypeRef | None" = None
    type_name: str | None = None
    type_source_span: SourceSpan | None = _field(default=None, compare=False)
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableInlineSchemaData:
    entries: tuple[ReadableSchemaEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableTableCell:
    key: str
    text: str | None = None
    body: tuple["ReadableSectionBodyItem", ...] | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableTableColumn:
    key: str
    title: str
    body: tuple[ProseLine, ...]
    type_ref: "FieldTypeRef | None" = None
    type_name: str | None = None
    type_source_span: SourceSpan | None = _field(default=None, compare=False)
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableTableRow:
    key: str
    cells: tuple[ReadableTableCell, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableTableData:
    columns: tuple[ReadableTableColumn, ...]
    rows: tuple[ReadableTableRow, ...] = ()
    notes: tuple[ProseLine, ...] = ()
    row_schema: ReadableInlineSchemaData | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableTableUseData:
    table_ref: NameRef
    rows: tuple[ReadableTableRow, ...] = ()
    notes: tuple[ProseLine, ...] = ()
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableCalloutData:
    kind: str | None
    body: tuple[ProseLine, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableCodeData:
    language: str | None
    text: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableRawTextData:
    text: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableFootnoteItem:
    key: str
    text: ProseLine
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableFootnotesData:
    entries: tuple[ReadableFootnoteItem, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableImageData:
    src: str
    alt: str
    caption: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


ReadableSectionBodyItem: _TypeAlias = ProseLine | "ReadableBlock"
ReadablePayload: _TypeAlias = (
    tuple[ReadableSectionBodyItem, ...]
    | tuple[ReadableListItem, ...]
    | tuple[ReadableDefinitionItem, ...]
    | ReadablePropertiesData
    | ReadableTableData
    | ReadableTableUseData
    | ReadableCalloutData
    | ReadableCodeData
    | ReadableRawTextData
    | ReadableFootnotesData
    | ReadableImageData
    | None
)


@_dataclass(slots=True, frozen=True)
class ReadableBlock:
    kind: str
    key: str
    title: str | None
    payload: ReadablePayload
    requirement: ReadableRequirement | None = None
    when_expr: Expr | None = None
    item_schema: ReadableInlineSchemaData | None = None
    row_schema: ReadableInlineSchemaData | None = None
    anonymous: bool = False
    legacy_section: bool = False
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReadableOverrideBlock:
    kind: str
    key: str
    title: str | None
    payload: ReadablePayload
    requirement: ReadableRequirement | None = None
    when_expr: Expr | None = None
    item_schema: ReadableInlineSchemaData | None = None
    row_schema: ReadableInlineSchemaData | None = None
    anonymous: bool = False
    source_span: SourceSpan | None = _field(default=None, compare=False)


DocumentBlock = ReadableBlock
DocumentOverrideBlock = ReadableOverrideBlock
DocumentItem: _TypeAlias = ProseLine | ReadableBlock | InheritItem | ReadableOverrideBlock


@_dataclass(slots=True, frozen=True)
class DocumentBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[DocumentItem, ...]


@_dataclass(slots=True, frozen=True)
class DocumentDecl:
    name: str
    body: DocumentBody
    parent_ref: NameRef | None = None
    render_profile_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)

    @property
    def title(self) -> str:
        return self.body.title


@_dataclass(slots=True, frozen=True)
class TableDecl:
    name: str
    title: str
    table: ReadableTableData
    source_span: SourceSpan | None = _field(default=None, compare=False)
