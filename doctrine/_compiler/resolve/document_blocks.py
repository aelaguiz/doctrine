from __future__ import annotations

from dataclasses import replace

from doctrine._compiler.resolved_types import *  # noqa: F401,F403


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
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind in {"sequence", "bullets", "checklist"}:
            resolved_items: list[model.ReadableListItem] = []
            seen_keys: set[str] = set()
            for list_item in self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind=item.kind,
            ):
                if not isinstance(list_item, model.ReadableListItem):
                    raise CompileError(
                        f"Readable {item.kind} items must stay list entries in {owner_label}"
                    )
                if list_item.key is not None:
                    if list_item.key in seen_keys:
                        raise CompileError(
                            f"Duplicate {item.kind} item key in {owner_label}: {list_item.key}"
                        )
                    seen_keys.add(list_item.key)
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
            seen_keys: set[str] = set()
            for definition in self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind="definitions",
            ):
                if not isinstance(definition, model.ReadableDefinitionItem):
                    raise CompileError(
                        f"Readable definitions entries must stay definition items in {owner_label}"
                    )
                if definition.key in seen_keys:
                    raise CompileError(
                        f"Duplicate definitions item key in {owner_label}: {definition.key}"
                    )
                seen_keys.add(definition.key)
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
            resolved_table = self._resolve_document_readable_table_payload(
                item.payload,
                unit=unit,
                owner_label=owner_label,
            )
            return replace(
                item,
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
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "callout":
            if not isinstance(item.payload, model.ReadableCalloutData):
                raise CompileError(f"Readable callout payload must stay callout-shaped in {owner_label}")
            if item.payload.kind is not None and item.payload.kind not in {
                "required",
                "important",
                "warning",
                "note",
            }:
                raise CompileError(f"Unknown callout kind in {owner_label}: {item.payload.kind}")
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
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "code":
            if not isinstance(item.payload, model.ReadableCodeData):
                raise CompileError(f"Readable code payload must stay code-shaped in {owner_label}")
            if "\n" not in item.payload.text:
                raise CompileError(f"Code block text must use a multiline string in {owner_label}")
            return replace(item, item_schema=item_schema, row_schema=row_schema)
        if item.kind in {"markdown", "html"}:
            if not isinstance(item.payload, model.ReadableRawTextData):
                raise CompileError(f"Readable {item.kind} payload must stay text-shaped in {owner_label}")
            text = self._interpolate_authored_prose_string(
                item.payload.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{item.kind} text",
                ambiguous_label=f"{item.kind} interpolation ref",
            )
            if "\n" not in text:
                raise CompileError(f"Raw {item.kind} blocks must use a multiline string in {owner_label}")
            return replace(
                item,
                payload=model.ReadableRawTextData(text=text),
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
                raise CompileError(f"Readable image payload must stay image-shaped in {owner_label}")
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
    ) -> tuple[model.ReadableSectionBodyItem, ...]:
        resolved: list[model.ReadableSectionBodyItem] = []
        for child in self._require_tuple_payload(payload, owner_label=owner_label, kind=kind):
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
                raise CompileError(
                    f"Readable {kind} payload must stay block-shaped in {owner_label}"
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
        seen_keys: set[str] = set()
        entries: list[model.ReadableSchemaEntry] = []
        for entry in schema.entries:
            if entry.key in seen_keys:
                raise CompileError(f"Duplicate {schema_label} key in {owner_label}: {entry.key}")
            seen_keys.add(entry.key)
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
        return model.ReadableInlineSchemaData(entries=tuple(entries))

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
            raise CompileError(f"Readable properties payload must stay properties-shaped in {owner_label}")
        seen_keys: set[str] = set()
        entries: list[model.ReadablePropertyItem] = []
        for entry in payload.entries:
            if entry.key in seen_keys:
                raise CompileError(f"Duplicate properties entry key in {owner_label}: {entry.key}")
            seen_keys.add(entry.key)
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
        return model.ReadablePropertiesData(entries=tuple(entries))

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
            raise CompileError(f"Readable footnotes payload must stay footnotes-shaped in {owner_label}")
        seen_keys: set[str] = set()
        entries: list[model.ReadableFootnoteItem] = []
        for entry in payload.entries:
            if entry.key in seen_keys:
                raise CompileError(f"Duplicate footnote key in {owner_label}: {entry.key}")
            seen_keys.add(entry.key)
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
                )
            )
        return model.ReadableFootnotesData(entries=tuple(entries))

    def _resolve_document_readable_table_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> model.ReadableTableData:
        if not isinstance(payload, model.ReadableTableData):
            raise CompileError(f"Readable table payload must stay table-shaped in {owner_label}")
        resolved_columns: list[model.ReadableTableColumn] = []
        column_keys: set[str] = set()
        for column in payload.columns:
            if column.key in column_keys:
                raise CompileError(f"Duplicate table column key in {owner_label}: {column.key}")
            column_keys.add(column.key)
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
            raise CompileError(f"Readable table must declare at least one column in {owner_label}")

        row_schema = self._resolve_readable_inline_schema(
            payload.row_schema,
            unit=unit,
            owner_label=owner_label,
            schema_label="row_schema",
            surface_label="table row schema",
        )

        resolved_rows: list[model.ReadableTableRow] = []
        row_keys: set[str] = set()
        for row in payload.rows:
            if row.key in row_keys:
                raise CompileError(f"Duplicate table row key in {owner_label}: {row.key}")
            row_keys.add(row.key)
            cell_keys: set[str] = set()
            resolved_cells: list[model.ReadableTableCell] = []
            for cell in row.cells:
                if cell.key not in column_keys:
                    raise CompileError(
                        f"Table row references an unknown column in {owner_label}: {cell.key}"
                    )
                if cell.key in cell_keys:
                    raise CompileError(
                        f"Duplicate table row cell in {owner_label}.{row.key}: {cell.key}"
                    )
                cell_keys.add(cell.key)
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
                    raise CompileError(
                        "Readable table inline cells must stay single-line in "
                        f"{owner_label}.{row.key}.{cell.key}; nested tables require structured cell bodies."
                    )
                resolved_cells.append(model.ReadableTableCell(key=cell.key, text=cell_text))
            resolved_rows.append(model.ReadableTableRow(key=row.key, cells=tuple(resolved_cells)))

        resolved_notes = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="table notes",
                ambiguous_label="table note interpolation ref",
            )
            for line in payload.notes
        )

        return model.ReadableTableData(
            columns=tuple(resolved_columns),
            rows=tuple(resolved_rows),
            notes=resolved_notes,
            row_schema=row_schema,
        )
