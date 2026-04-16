from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.readable_diagnostics import (
    duplicate_readable_key_error,
    invalid_readable_block_error,
    readable_source_span,
)
from doctrine._compiler.resolved_types import (
    IndexedUnit,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveDocumentBlocksMixin:
    """Document-block and readable-payload resolution helpers for ResolveMixin."""

    def _resolve_document_block(
        self,
        item: model.DocumentBlock,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> model.DocumentBlock:
        if item.when_expr is not None:
            self._validate_readable_guard_expr(
                item.when_expr,
                unit=unit,
                owner_label=owner_label,
            )
        item_schema = self._resolve_readable_inline_schema(
            item.item_schema,
            unit=unit,
            owner_label=owner_label,
            schema_label="item_schema",
            surface_label=f"{item.kind} item schema",
        )
        row_schema = self._resolve_readable_inline_schema(
            item.row_schema,
            unit=unit,
            owner_label=owner_label,
            schema_label="row_schema",
            surface_label=f"{item.kind} row schema",
        )
        if item.kind == "section":
            return replace(
                item,
                payload=self._resolve_document_shared_readable_body(
                    item.payload,
                    unit=unit,
                owner_label=owner_label,
                kind="section",
                owner_source_span=item.source_span,
            ),
                item_schema=item_schema,
                row_schema=row_schema,
        )
        if item.kind in {"sequence", "bullets", "checklist"}:
            resolved_items: list[model.ReadableListItem] = []
            seen_keys: dict[str, model.ReadableListItem] = {}
            for list_item in self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind=item.kind,
                unit=unit,
                source_span=item.source_span,
            ):
                if not isinstance(list_item, model.ReadableListItem):
                    raise invalid_readable_block_error(
                        detail=(
                            f"Readable {item.kind} items must stay list entries in "
                            f"{owner_label}."
                        ),
                        unit=unit,
                        source_span=readable_source_span(list_item) or item.source_span,
                    )
                if list_item.key is not None:
                    if list_item.key in seen_keys:
                        raise duplicate_readable_key_error(
                            subject_label="Readable surface",
                            owner_label=owner_label,
                            kind_label=f"{item.kind} item",
                            key=list_item.key,
                            unit=unit,
                            source_span=list_item.source_span,
                            first_source_span=seen_keys[list_item.key].source_span,
                        )
                    seen_keys[list_item.key] = list_item
                resolved_items.append(
                    replace(
                        list_item,
                        text=self._interpolate_authored_prose_line(
                            list_item.text,
                            unit=unit,
                            owner_label=owner_label,
                            surface_label=f"{item.kind} item prose",
                            ambiguous_label=f"{item.kind} item interpolation ref",
                        ),
                    )
                )
            return replace(
                item,
                payload=tuple(resolved_items),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "properties":
            return replace(
                item,
                payload=self._resolve_readable_properties_payload(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "definitions":
            resolved_items: list[model.ReadableDefinitionItem] = []
            seen_keys: dict[str, model.ReadableDefinitionItem] = {}
            for definition in self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind="definitions",
                unit=unit,
                source_span=item.source_span,
            ):
                if not isinstance(definition, model.ReadableDefinitionItem):
                    raise invalid_readable_block_error(
                        detail=(
                            f"Readable definitions entries must stay definition items in "
                            f"{owner_label}."
                        ),
                        unit=unit,
                        source_span=readable_source_span(definition) or item.source_span,
                    )
                if definition.key in seen_keys:
                    raise duplicate_readable_key_error(
                        subject_label="Readable surface",
                        owner_label=owner_label,
                        kind_label="definitions item",
                        key=definition.key,
                        unit=unit,
                        source_span=definition.source_span,
                        first_source_span=seen_keys[definition.key].source_span,
                    )
                seen_keys[definition.key] = definition
                resolved_items.append(
                    replace(
                        definition,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{owner_label}.{definition.key}",
                                surface_label="definitions prose",
                                ambiguous_label="definitions prose interpolation ref",
                            )
                            for line in definition.body
                        ),
                    )
                )
            return replace(
                item,
                payload=tuple(resolved_items),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "table":
            if isinstance(item.payload, model.ReadableTableUseData):
                table_title, resolved_table = self._resolve_named_document_table_payload(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                )
            else:
                table_title = item.title
                resolved_table = self._resolve_document_readable_table_payload(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                    owner_source_span=item.source_span,
                )
            return replace(
                item,
                title=table_title,
                payload=resolved_table,
                item_schema=item_schema,
                row_schema=resolved_table.row_schema,
            )
        if item.kind == "guard":
            return replace(
                item,
                payload=self._resolve_document_shared_readable_body(
                    item.payload,
                    unit=unit,
                owner_label=owner_label,
                kind="guard",
                owner_source_span=item.source_span,
            ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "callout":
            if not isinstance(item.payload, model.ReadableCalloutData):
                raise invalid_readable_block_error(
                    detail=f"Readable callout payload must stay callout-shaped in {owner_label}.",
                    unit=unit,
                    source_span=readable_source_span(item.payload) or item.source_span,
                )
            if item.payload.kind is not None and item.payload.kind not in {
                "required",
                "important",
                "warning",
                "note",
            }:
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable block `{owner_label}` uses unknown callout kind "
                        f"`{item.payload.kind}`."
                    ),
                    unit=unit,
                    source_span=item.payload.source_span or item.source_span,
                    hints=(
                        "Use one of the shipped callout kinds: `required`, `important`, "
                        "`warning`, or `note`.",
                    ),
                )
            return replace(
                item,
                payload=model.ReadableCalloutData(
                    kind=item.payload.kind,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=owner_label,
                            surface_label="callout prose",
                            ambiguous_label="callout interpolation ref",
                        )
                        for line in item.payload.body
                    ),
                    source_span=item.payload.source_span,
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "code":
            if not isinstance(item.payload, model.ReadableCodeData):
                raise invalid_readable_block_error(
                    detail=f"Readable code payload must stay code-shaped in {owner_label}.",
                    unit=unit,
                    source_span=readable_source_span(item.payload) or item.source_span,
                )
            if "\n" not in item.payload.text:
                raise invalid_readable_block_error(
                    detail=f"Readable code block `{owner_label}` must use a multiline string.",
                    unit=unit,
                    source_span=item.payload.source_span or item.source_span,
                    hints=("Use a multiline string for readable code block text.",),
                )
            return replace(item, item_schema=item_schema, row_schema=row_schema)
        if item.kind in {"markdown", "html"}:
            if not isinstance(item.payload, model.ReadableRawTextData):
                raise invalid_readable_block_error(
                    detail=f"Readable {item.kind} payload must stay text-shaped in {owner_label}.",
                    unit=unit,
                    source_span=readable_source_span(item.payload) or item.source_span,
                )
            text = self._interpolate_authored_prose_string(
                item.payload.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{item.kind} text",
                ambiguous_label=f"{item.kind} interpolation ref",
            )
            if "\n" not in text:
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable {item.kind} block `{owner_label}` must use a multiline string."
                    ),
                    unit=unit,
                    source_span=item.payload.source_span or item.source_span,
                    hints=("Use a multiline string for raw markdown or html readable blocks.",),
                )
            return replace(
                item,
                payload=model.ReadableRawTextData(
                    text=text,
                    source_span=item.payload.source_span,
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "footnotes":
            return replace(
                item,
                payload=self._resolve_readable_footnotes_payload(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "image":
            if not isinstance(item.payload, model.ReadableImageData):
                raise invalid_readable_block_error(
                    detail=f"Readable image payload must stay image-shaped in {owner_label}.",
                    unit=unit,
                    source_span=readable_source_span(item.payload) or item.source_span,
                )
            return replace(
                item,
                payload=model.ReadableImageData(
                    src=self._interpolate_authored_prose_string(
                        item.payload.src,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="image src",
                        ambiguous_label="image src interpolation ref",
                    ),
                    alt=self._interpolate_authored_prose_string(
                        item.payload.alt,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="image alt",
                        ambiguous_label="image alt interpolation ref",
                    ),
                    caption=(
                        self._interpolate_authored_prose_string(
                            item.payload.caption,
                            unit=unit,
                            owner_label=owner_label,
                            surface_label="image caption",
                            ambiguous_label="image caption interpolation ref",
                        )
                        if item.payload.caption is not None
                        else None
                    ),
                    source_span=item.payload.source_span,
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "rule":
            return replace(item, item_schema=item_schema, row_schema=row_schema)
        return replace(
            item,
            payload=self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind=item.kind,
                unit=unit,
                source_span=item.source_span,
            ),
            item_schema=item_schema,
            row_schema=row_schema,
        )

    def _resolve_document_shared_readable_body(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        kind: str,
        owner_source_span: model.SourceSpan | None = None,
    ) -> tuple[model.ReadableSectionBodyItem, ...]:
        resolved: list[model.ReadableSectionBodyItem] = []
        for child in self._require_tuple_payload(
            payload,
            owner_label=owner_label,
            kind=kind,
            unit=unit,
            source_span=owner_source_span,
        ):
            if isinstance(child, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        child,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="document prose",
                        ambiguous_label="document prose interpolation ref",
                    )
                )
                continue
            if not isinstance(child, model.ReadableBlock):
                raise invalid_readable_block_error(
                    detail=f"Readable {kind} payload must stay block-shaped in {owner_label}.",
                    unit=unit,
                    source_span=readable_source_span(child) or owner_source_span,
                )
            resolved.append(
                self._resolve_document_block(
                    child,
                    unit=unit,
                    owner_label=f"{owner_label}.{child.key}",
                )
            )
        return tuple(resolved)

    def _resolve_readable_inline_schema(
        self,
        schema: model.ReadableInlineSchemaData | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        schema_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ReadableInlineSchemaData | None:
        if schema is None:
            return None
        seen_keys: dict[str, model.ReadableSchemaEntry] = {}
        entries: list[model.ReadableSchemaEntry] = []
        for entry in schema.entries:
            if entry.key in seen_keys:
                raise duplicate_readable_key_error(
                    subject_label="Readable surface",
                    owner_label=owner_label,
                    kind_label=schema_label,
                    key=entry.key,
                    unit=unit,
                    source_span=entry.source_span,
                    first_source_span=seen_keys[entry.key].source_span,
                )
            seen_keys[entry.key] = entry
            entries.append(
                replace(
                    entry,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{schema_label}.{entry.key}",
                            surface_label=surface_label,
                            ambiguous_label=f"{schema_label} interpolation ref",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        )
                        for line in entry.body
                    ),
                )
            )
        return model.ReadableInlineSchemaData(
            entries=tuple(entries),
            source_span=schema.source_span,
        )

    def _resolve_readable_properties_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ReadablePropertiesData:
        if not isinstance(payload, model.ReadablePropertiesData):
            raise invalid_readable_block_error(
                detail=f"Readable properties payload must stay properties-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload),
            )
        seen_keys: dict[str, model.ReadablePropertyItem] = {}
        entries: list[model.ReadablePropertyItem] = []
        for entry in payload.entries:
            if entry.key in seen_keys:
                raise duplicate_readable_key_error(
                    subject_label="Readable surface",
                    owner_label=owner_label,
                    kind_label="properties entry",
                    key=entry.key,
                    unit=unit,
                    source_span=entry.source_span,
                    first_source_span=seen_keys[entry.key].source_span,
                )
            seen_keys[entry.key] = entry
            entries.append(
                replace(
                    entry,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{entry.key}",
                            surface_label="properties prose",
                            ambiguous_label="properties interpolation ref",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        )
                        for line in entry.body
                    ),
                )
            )
        return model.ReadablePropertiesData(
            entries=tuple(entries),
            source_span=payload.source_span,
        )

    def _resolve_readable_footnotes_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ReadableFootnotesData:
        if not isinstance(payload, model.ReadableFootnotesData):
            raise invalid_readable_block_error(
                detail=f"Readable footnotes payload must stay footnotes-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload),
            )
        seen_keys: dict[str, model.ReadableFootnoteItem] = {}
        entries: list[model.ReadableFootnoteItem] = []
        for entry in payload.entries:
            if entry.key in seen_keys:
                raise duplicate_readable_key_error(
                    subject_label="Readable surface",
                    owner_label=owner_label,
                    kind_label="footnote",
                    key=entry.key,
                    unit=unit,
                    source_span=entry.source_span,
                    first_source_span=seen_keys[entry.key].source_span,
                )
            seen_keys[entry.key] = entry
            entries.append(
                model.ReadableFootnoteItem(
                    key=entry.key,
                    text=self._interpolate_authored_prose_line(
                        entry.text,
                        unit=unit,
                        owner_label=f"{owner_label}.{entry.key}",
                        surface_label="footnotes prose",
                        ambiguous_label="footnote interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                    ),
                    source_span=entry.source_span,
                )
            )
        return model.ReadableFootnotesData(
            entries=tuple(entries),
            source_span=payload.source_span,
        )

    def _resolve_document_readable_table_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        owner_source_span: model.SourceSpan | None = None,
    ) -> model.ReadableTableData:
        if not isinstance(payload, model.ReadableTableData):
            raise invalid_readable_block_error(
                detail=f"Readable table payload must stay table-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or owner_source_span,
            )
        return self._resolve_readable_table_data(
            payload,
            unit=unit,
            owner_label=owner_label,
            owner_source_span=owner_source_span,
        )

    def _resolve_table_decl_data(
        self,
        table_decl: model.TableDecl,
        *,
        unit: IndexedUnit,
    ) -> model.ReadableTableData:
        return self._resolve_readable_table_data(
            table_decl.table,
            unit=unit,
            owner_label=f"table {_dotted_decl_name(unit.module_parts, table_decl.name)}",
            owner_source_span=table_decl.source_span,
        )

    def _resolve_named_document_table_payload(
        self,
        payload: model.ReadableTableUseData,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[str, model.ReadableTableData]:
        table_unit, table_decl = self._resolve_table_ref(payload.table_ref, unit=unit)
        declaration_table = self._resolve_table_decl_data(table_decl, unit=table_unit)
        resolved_rows = self._resolve_readable_table_rows(
            payload.rows,
            columns=declaration_table.columns,
            unit=unit,
            owner_label=owner_label,
        )
        resolved_notes = self._resolve_readable_table_notes(
            payload.notes,
            unit=unit,
            owner_label=owner_label,
        )
        return table_decl.title, model.ReadableTableData(
            columns=declaration_table.columns,
            rows=resolved_rows,
            notes=(*declaration_table.notes, *resolved_notes),
            row_schema=declaration_table.row_schema,
        )

    def _resolve_readable_table_data(
        self,
        payload: model.ReadableTableData,
        *,
        unit: IndexedUnit,
        owner_label: str,
        owner_source_span: model.SourceSpan | None = None,
    ) -> model.ReadableTableData:
        resolved_columns: list[model.ReadableTableColumn] = []
        column_keys: dict[str, model.ReadableTableColumn] = {}
        for column in payload.columns:
            if column.key in column_keys:
                raise duplicate_readable_key_error(
                    subject_label="Readable surface",
                    owner_label=owner_label,
                    kind_label="table column",
                    key=column.key,
                    unit=unit,
                    source_span=column.source_span,
                    first_source_span=column_keys[column.key].source_span,
                )
            column_keys[column.key] = column
            resolved_columns.append(
                replace(
                    column,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.columns.{column.key}",
                            surface_label="table column prose",
                            ambiguous_label="table column interpolation ref",
                        )
                        for line in column.body
                    ),
                )
            )
        if not resolved_columns:
            raise invalid_readable_block_error(
                detail=f"Readable table `{owner_label}` must declare at least one column.",
                unit=unit,
                source_span=owner_source_span or payload.source_span,
                hints=("Declare at least one table column before rows or notes.",),
            )

        row_schema = self._resolve_readable_inline_schema(
            payload.row_schema,
            unit=unit,
            owner_label=owner_label,
            schema_label="row_schema",
            surface_label="table row schema",
        )

        resolved_rows = self._resolve_readable_table_rows(
            payload.rows,
            columns=tuple(resolved_columns),
            unit=unit,
            owner_label=owner_label,
        )

        resolved_notes = self._resolve_readable_table_notes(
            payload.notes,
            unit=unit,
            owner_label=owner_label,
        )

        return model.ReadableTableData(
            columns=tuple(resolved_columns),
            rows=resolved_rows,
            notes=resolved_notes,
            row_schema=row_schema,
            source_span=payload.source_span,
        )

    def _resolve_readable_table_rows(
        self,
        rows: tuple[model.ReadableTableRow, ...],
        *,
        columns: tuple[model.ReadableTableColumn, ...],
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ReadableTableRow, ...]:
        column_keys = {column.key for column in columns}
        resolved_rows: list[model.ReadableTableRow] = []
        row_keys: dict[str, model.ReadableTableRow] = {}
        for row in rows:
            if row.key in row_keys:
                raise duplicate_readable_key_error(
                    subject_label="Readable surface",
                    owner_label=owner_label,
                    kind_label="table row",
                    key=row.key,
                    unit=unit,
                    source_span=row.source_span,
                    first_source_span=row_keys[row.key].source_span,
                )
            row_keys[row.key] = row
            cell_keys: dict[str, model.ReadableTableCell] = {}
            resolved_cells: list[model.ReadableTableCell] = []
            for cell in row.cells:
                if cell.key not in column_keys:
                    raise invalid_readable_block_error(
                        detail=(
                            f"Readable table row in `{owner_label}` references unknown column "
                            f"`{cell.key}`."
                        ),
                        unit=unit,
                        source_span=cell.source_span or row.source_span,
                        hints=("Match each table cell key to a declared table column key.",),
                    )
                if cell.key in cell_keys:
                    raise duplicate_readable_key_error(
                        subject_label="Readable surface",
                        owner_label=f"{owner_label}.{row.key}",
                        kind_label="table row cell",
                        key=cell.key,
                        unit=unit,
                        source_span=cell.source_span,
                        first_source_span=cell_keys[cell.key].source_span,
                    )
                cell_keys[cell.key] = cell
                if cell.body is not None:
                    resolved_cells.append(
                        model.ReadableTableCell(
                            key=cell.key,
                            body=self._resolve_document_shared_readable_body(
                                cell.body,
                                unit=unit,
                                owner_label=f"{owner_label}.{row.key}.{cell.key}",
                                kind="table cell body",
                            ),
                            source_span=cell.source_span,
                        )
                    )
                    continue
                cell_text = self._interpolate_authored_prose_string(
                    cell.text or "",
                    unit=unit,
                    owner_label=f"{owner_label}.{row.key}.{cell.key}",
                    surface_label="table cell prose",
                    ambiguous_label="table cell interpolation ref",
                )
                if "\n" in cell_text:
                    raise invalid_readable_block_error(
                        detail=(
                            f"Readable table inline cell `{owner_label}.{row.key}.{cell.key}` "
                            "must stay single-line unless it uses a structured cell body."
                        ),
                        unit=unit,
                        source_span=cell.source_span or row.source_span,
                        hints=(
                            "Move multi-line cell content into a structured cell body instead of "
                            "an inline table cell.",
                        ),
                    )
                resolved_cells.append(
                    model.ReadableTableCell(
                        key=cell.key,
                        text=cell_text,
                        source_span=cell.source_span,
                    )
                )
            resolved_rows.append(
                model.ReadableTableRow(
                    key=row.key,
                    cells=tuple(resolved_cells),
                    source_span=row.source_span,
                )
            )
        return tuple(resolved_rows)

    def _resolve_readable_table_notes(
        self,
        notes: tuple[model.ProseLine, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ProseLine, ...]:
        return tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="table notes",
                ambiguous_label="table note interpolation ref",
            )
            for line in notes
        )
