from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import Expr, InheritItem, NameRef, ProseLine


ReadableRequirement: _TypeAlias = str


@_dataclass(slots=True, frozen=True)
class ReadableListItem:
    key: str | None
    text: ProseLine


@_dataclass(slots=True, frozen=True)
class ReadableDefinitionItem:
    key: str
    title: str
    body: tuple[ProseLine, ...]


@_dataclass(slots=True, frozen=True)
class ReadablePropertyItem:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@_dataclass(slots=True, frozen=True)
class ReadablePropertiesData:
    entries: tuple[ReadablePropertyItem, ...]


@_dataclass(slots=True, frozen=True)
class ReadableSchemaEntry:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@_dataclass(slots=True, frozen=True)
class ReadableInlineSchemaData:
    entries: tuple[ReadableSchemaEntry, ...]


@_dataclass(slots=True, frozen=True)
class ReadableTableCell:
    key: str
    text: str | None = None
    body: tuple["ReadableSectionBodyItem", ...] | None = None


@_dataclass(slots=True, frozen=True)
class ReadableTableColumn:
    key: str
    title: str
    body: tuple[ProseLine, ...]


@_dataclass(slots=True, frozen=True)
class ReadableTableRow:
    key: str
    cells: tuple[ReadableTableCell, ...]


@_dataclass(slots=True, frozen=True)
class ReadableTableData:
    columns: tuple[ReadableTableColumn, ...]
    rows: tuple[ReadableTableRow, ...] = ()
    notes: tuple[ProseLine, ...] = ()
    row_schema: ReadableInlineSchemaData | None = None


@_dataclass(slots=True, frozen=True)
class ReadableCalloutData:
    kind: str | None
    body: tuple[ProseLine, ...]


@_dataclass(slots=True, frozen=True)
class ReadableCodeData:
    language: str | None
    text: str


@_dataclass(slots=True, frozen=True)
class ReadableRawTextData:
    text: str


@_dataclass(slots=True, frozen=True)
class ReadableFootnoteItem:
    key: str
    text: ProseLine


@_dataclass(slots=True, frozen=True)
class ReadableFootnotesData:
    entries: tuple[ReadableFootnoteItem, ...]


@_dataclass(slots=True, frozen=True)
class ReadableImageData:
    src: str
    alt: str
    caption: str | None = None


ReadableSectionBodyItem: _TypeAlias = ProseLine | "ReadableBlock"
ReadablePayload: _TypeAlias = (
    tuple[ReadableSectionBodyItem, ...]
    | tuple[ReadableListItem, ...]
    | tuple[ReadableDefinitionItem, ...]
    | ReadablePropertiesData
    | ReadableTableData
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

    @property
    def title(self) -> str:
        return self.body.title
