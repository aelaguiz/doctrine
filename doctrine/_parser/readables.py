from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    ReadableFieldPart,
    ReadablePayloadParts,
    _meta_line_column,
    _positioned_readable_field,
    _with_source_span,
)
from doctrine.diagnostics import TransformParseFailure


class ReadableNodeTransformerMixin:
    """Shared readable-block and readable-payload lowering for the public parser boundary."""

    def readable_nonsection_block(self, items):
        return items[0]

    def override_readable_nonsection_block(self, items):
        return items[0]

    @v_args(meta=True, inline=True)
    def readable_sequence_block(self, meta, key, *parts):
        title: str | None = None
        readable_parts = parts
        if readable_parts and isinstance(readable_parts[0], str):
            title = readable_parts[0]
            readable_parts = readable_parts[1:]
        return _with_source_span(
            self._readable_block("sequence", key, title, readable_parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_properties_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("properties", key, title, parts),
            meta,
        )

    @v_args(meta=True)
    def readable_inline_properties_block(self, meta, items):
        return _with_source_span(
            model.ReadableBlock(
                kind="properties",
                key="properties",
                title=None,
                payload=items[0],
                anonymous=True,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_guard_shell_block(self, meta, key, guard, body):
        return _with_source_span(
            model.ReadableBlock(
                kind="guard",
                key=key,
                title=None,
                payload=tuple(body),
                when_expr=guard[1],
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_bullets_block(self, meta, key, *parts):
        title: str | None = None
        readable_parts = parts
        if readable_parts and isinstance(readable_parts[0], str):
            title = readable_parts[0]
            readable_parts = readable_parts[1:]
        return _with_source_span(
            self._readable_block("bullets", key, title, readable_parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_checklist_block(self, meta, key, *parts):
        title: str | None = None
        readable_parts = parts
        if readable_parts and isinstance(readable_parts[0], str):
            title = readable_parts[0]
            readable_parts = readable_parts[1:]
        return _with_source_span(
            self._readable_block("checklist", key, title, readable_parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_definitions_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("definitions", key, title, parts),
            meta,
        )

    @v_args(inline=True)
    def readable_table_block(self, value):
        return value

    @v_args(meta=True, inline=True)
    def readable_inline_table_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("table", key, title, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_named_table_block(self, meta, key, table_ref, *parts):
        return self._named_table_block(model.ReadableBlock, key, table_ref, parts, meta=meta)

    @v_args(meta=True, inline=True)
    def readable_callout_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("callout", key, title, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_code_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("code", key, title, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_markdown_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("markdown", key, title, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_html_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("html", key, title, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_footnotes_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("footnotes", key, title, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_image_block(self, meta, key, title, *parts):
        return _with_source_span(
            self._readable_block("image", key, title, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_rule_block(self, meta, key, *parts):
        requirement, when_expr, item_schema, row_schema, _payload = self._split_readable_parts(parts)
        return _with_source_span(
            model.ReadableBlock(
                kind="rule",
                key=key,
                title=None,
                payload=None,
                requirement=requirement,
                when_expr=when_expr,
                item_schema=item_schema,
                row_schema=row_schema,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_sequence_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("sequence", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_properties_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("properties", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_guard_shell_block(self, meta, key, guard, body):
        return _with_source_span(
            model.DocumentOverrideBlock(
                kind="guard",
                key=key,
                title=None,
                payload=tuple(body),
                when_expr=guard[1],
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_bullets_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("bullets", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_checklist_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("checklist", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_definitions_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("definitions", key, parts),
            meta,
        )

    @v_args(inline=True)
    def override_readable_table_block(self, value):
        return value

    @v_args(meta=True, inline=True)
    def override_readable_inline_table_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("table", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_named_table_block(self, meta, key, table_ref, *parts):
        return self._named_table_block(
            model.DocumentOverrideBlock,
            key,
            table_ref,
            parts,
            meta=meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_callout_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("callout", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_code_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("code", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_markdown_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("markdown", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_html_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("html", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_footnotes_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("footnotes", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_image_block(self, meta, key, *parts):
        return _with_source_span(
            self._readable_override_block("image", key, parts),
            meta,
        )

    @v_args(meta=True, inline=True)
    def override_readable_rule_block(self, meta, key, *parts):
        title, requirement, when_expr, item_schema, row_schema, _payload = self._split_readable_override_parts(parts)
        return _with_source_span(
            model.DocumentOverrideBlock(
                kind="rule",
                key=key,
                title=title,
                payload=None,
                requirement=requirement,
                when_expr=when_expr,
                item_schema=item_schema,
                row_schema=row_schema,
            ),
            meta,
        )

    def readable_list_body(self, items):
        rendered_items: list[model.ReadableListItem] = []
        item_schema: model.ReadableInlineSchemaData | None = None
        for item in items:
            if isinstance(item, ReadableFieldPart) and item.key == "item_schema":
                if item_schema is not None:
                    raise TransformParseFailure(
                        "Readable list bodies may define `item_schema:` only once.",
                        hints=("Keep exactly one `item_schema:` block per readable list.",),
                        line=item.line,
                        column=item.column,
                    )
                item_schema = item.value
                continue
            if isinstance(item, model.ReadableListItem):
                rendered_items.append(item)
                continue
            rendered_items.append(model.ReadableListItem(key=None, text=item))
        return ReadablePayloadParts(payload=tuple(rendered_items), item_schema=item_schema)

    @v_args(meta=True, inline=True)
    def readable_list_keyed_item(self, meta, key, text):
        return _with_source_span(model.ReadableListItem(key=key, text=text), meta)

    @v_args(meta=True)
    def readable_item_schema_block(self, meta, items):
        return _positioned_readable_field(
            meta,
            "item_schema",
            _with_source_span(model.ReadableInlineSchemaData(entries=tuple(items)), meta),
        )

    @v_args(meta=True)
    def readable_properties_body(self, meta, items):
        return _with_source_span(model.ReadablePropertiesData(entries=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def readable_property_item(self, meta, key, title, body=None):
        return _with_source_span(
            model.ReadablePropertyItem(key=key, title=title, body=tuple(body or ())),
            meta,
        )

    def readable_property_item_body(self, items):
        return tuple(items[0])

    def readable_definitions_body(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def readable_definition_item(self, meta, key, title, body=None):
        return _with_source_span(
            model.ReadableDefinitionItem(
                key=key,
                title=title,
                body=tuple(body or ()),
            ),
            meta,
        )

    def readable_definition_item_body(self, items):
        return tuple(items[0])

    @v_args(meta=True, inline=True)
    def table_decl(self, meta, name, title, body):
        return _with_source_span(model.TableDecl(name=name, title=title, table=body), meta)

    @v_args(meta=True)
    def table_decl_body(self, meta, items):
        return self._readable_table_data(
            items,
            owner_label="Table declarations",
            allow_columns=True,
            allow_rows=False,
            allow_row_schema=True,
            invalid_hint=(
                "Put shared table structure on the declaration and put concrete rows "
                "on each document use site."
            ),
            meta=meta,
        )

    @v_args(meta=True)
    def readable_table_body(self, meta, items):
        return ReadablePayloadParts(
            payload=self._readable_table_data(
                items,
                owner_label="Readable table bodies",
                allow_columns=True,
                allow_rows=True,
                allow_row_schema=True,
                invalid_hint="Use `columns:`, `rows:`, `row_schema:`, or `notes:` in readable table bodies.",
                meta=meta,
            ),
            row_schema=self._readable_table_row_schema(items),
        )

    def readable_table_use_body(self, items):
        rows: tuple[model.ReadableTableRow, ...] = ()
        notes: tuple[model.ProseLine, ...] = ()
        for item in items:
            block_kind, block_value, line, column = self._readable_table_field(item)
            if block_kind == "rows":
                rows = block_value
                continue
            if block_kind == "notes":
                notes = block_value
                continue
            raise TransformParseFailure(
                "Named table uses may define only `rows:` and `notes:`.",
                hints=("Move `columns:` and `row_schema:` to the top-level `table` declaration.",),
                line=line,
                column=column,
            )
        return ("table_use", rows, notes)

    def readable_named_table_suffix(self, items):
        return items[0] if items else ("table_use", (), ())

    def _readable_table_data(
        self,
        items,
        *,
        owner_label: str,
        allow_columns: bool,
        allow_rows: bool,
        allow_row_schema: bool,
        invalid_hint: str,
        meta: object | None = None,
    ) -> model.ReadableTableData:
        columns: tuple[model.ReadableTableColumn, ...] = ()
        rows: tuple[model.ReadableTableRow, ...] = ()
        notes: tuple[model.ProseLine, ...] = ()
        row_schema: model.ReadableInlineSchemaData | None = None
        for item in items:
            block_kind, block_value, line, column = self._readable_table_field(item)
            if block_kind == "columns":
                if not allow_columns:
                    raise TransformParseFailure(
                        f"{owner_label} may not define `columns:`.",
                        hints=(invalid_hint,),
                        line=line,
                        column=column,
                    )
                columns = block_value
            elif block_kind == "rows":
                if not allow_rows:
                    raise TransformParseFailure(
                        f"{owner_label} may not define `rows:`.",
                        hints=(invalid_hint,),
                        line=line,
                        column=column,
                    )
                rows = block_value
            elif block_kind == "notes":
                notes = block_value
            elif block_kind == "row_schema":
                if not allow_row_schema:
                    raise TransformParseFailure(
                        f"{owner_label} may not define `row_schema:`.",
                        hints=(invalid_hint,),
                        line=line,
                        column=column,
                    )
                if row_schema is not None:
                    raise TransformParseFailure(
                        f"{owner_label} may define `row_schema:` only once.",
                        hints=("Keep exactly one `row_schema:` block per readable table.",),
                        line=line,
                        column=column,
                    )
                row_schema = block_value
        table_data = model.ReadableTableData(
            columns=columns,
            rows=rows,
            notes=notes,
            row_schema=row_schema,
        )
        if meta is not None:
            return _with_source_span(table_data, meta)
        return table_data

    def _readable_table_row_schema(self, items) -> model.ReadableInlineSchemaData | None:
        for item in items:
            block_kind, block_value, _line, _column = self._readable_table_field(item)
            if block_kind == "row_schema":
                return block_value
        return None

    def _readable_table_field(self, item):
        if isinstance(item, ReadableFieldPart):
            return item.key, item.value, item.line, item.column
        block_kind, block_value = item
        return block_kind, block_value, None, None

    def _named_table_block(self, block_cls, key, table_ref, parts, *, meta: object | None = None):
        requirement: str | None = None
        when_expr: model.Expr | None = None
        rows: tuple[model.ReadableTableRow, ...] = ()
        notes: tuple[model.ProseLine, ...] = ()
        for part in parts:
            if isinstance(part, tuple) and part and part[0] == "requirement":
                requirement = part[1]
                continue
            if isinstance(part, tuple) and part and part[0] == "guard":
                when_expr = part[1]
                continue
            if isinstance(part, tuple) and part and part[0] == "table_use":
                rows = part[1]
                notes = part[2]
        table_use = model.ReadableTableUseData(
            table_ref=table_ref,
            rows=rows,
            notes=notes,
        )
        if meta is not None:
            table_use = _with_source_span(table_use, meta)
        block = block_cls(
            kind="table",
            key=key,
            title=None,
            payload=table_use,
            requirement=requirement,
            when_expr=when_expr,
        )
        if meta is not None:
            return _with_source_span(block, meta)
        return block

    @v_args(meta=True)
    def readable_row_schema_block(self, meta, items):
        return _positioned_readable_field(
            meta,
            "row_schema",
            _with_source_span(model.ReadableInlineSchemaData(entries=tuple(items)), meta),
        )

    @v_args(meta=True)
    def readable_table_columns_block(self, meta, items):
        return _positioned_readable_field(meta, "columns", tuple(items))

    @v_args(meta=True, inline=True)
    def readable_table_column(self, meta, key, title, body=None):
        return _with_source_span(
            model.ReadableTableColumn(
                key=key,
                title=title,
                body=tuple(body or ()),
            ),
            meta,
        )

    def readable_table_column_body(self, items):
        return tuple(items[0])

    @v_args(meta=True)
    def readable_table_rows_block(self, meta, items):
        return _positioned_readable_field(meta, "rows", tuple(items))

    @v_args(meta=True, inline=True)
    def readable_table_row(self, meta, key, *cells):
        return _with_source_span(model.ReadableTableRow(key=key, cells=tuple(cells)), meta)

    @v_args(meta=True, inline=True)
    def readable_table_cell_text(self, meta, key, text):
        return _with_source_span(model.ReadableTableCell(key=key, text=text), meta)

    @v_args(meta=True, inline=True)
    def readable_table_cell_body(self, meta, key, body):
        return _with_source_span(model.ReadableTableCell(key=key, body=tuple(body)), meta)

    @v_args(meta=True)
    def readable_table_notes_block(self, meta, items):
        return _positioned_readable_field(meta, "notes", tuple(items))

    @v_args(inline=True)
    def readable_table_note(self, value):
        return value

    @v_args(meta=True, inline=True)
    def readable_inline_schema_item(self, meta, key, title, body=None):
        return _with_source_span(
            model.ReadableSchemaEntry(key=key, title=title, body=tuple(body or ())),
            meta,
        )

    def readable_inline_schema_item_body(self, items):
        return tuple(items[0])

    @v_args(meta=True)
    def readable_callout_body(self, meta, items):
        kind: str | None = None
        body: list[model.ProseLine] = []
        for item in items:
            if isinstance(item, tuple) and item[0] == "kind":
                kind = item[1]
                continue
            body.append(item)
        return _with_source_span(model.ReadableCalloutData(kind=kind, body=tuple(body)), meta)

    @v_args(inline=True)
    def readable_callout_kind(self, kind):
        return ("kind", kind)

    @v_args(meta=True)
    def readable_code_body(self, meta, items):
        language: str | None = None
        text: str | None = None
        for item in items:
            if item[0] == "language":
                language = item[1]
            elif item[0] == "text":
                text = item[1]
        return _with_source_span(
            model.ReadableCodeData(language=language, text="" if text is None else text),
            meta,
        )

    @v_args(inline=True)
    def readable_code_language(self, language):
        return ("language", language)

    @v_args(inline=True)
    def readable_code_text(self, text):
        return ("text", text)

    @v_args(meta=True)
    def readable_raw_text_body(self, meta, items):
        text: str | None = None
        for item in items:
            if isinstance(item, ReadableFieldPart):
                item_key = item.key
                item_value = item.value
                line, column = item.line, item.column
            else:
                item_key, item_value = item
                line, column = None, None
            if item_key != "text":
                continue
            if text is not None:
                raise TransformParseFailure(
                    "Raw text readable blocks may define `text:` only once.",
                    hints=("Keep exactly one `text:` field in the block body.",),
                    line=line,
                    column=column,
                )
            text = item_value
        return _with_source_span(
            model.ReadableRawTextData(text="" if text is None else text),
            meta,
        )

    def readable_raw_text_line(self, items):
        return items[0]

    @v_args(meta=True, inline=True)
    def readable_raw_text_text(self, meta, text):
        return _positioned_readable_field(meta, "text", text)

    @v_args(meta=True)
    def readable_footnotes_body(self, meta, items):
        return _with_source_span(model.ReadableFootnotesData(entries=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def readable_footnote_item(self, meta, key, text):
        return _with_source_span(model.ReadableFootnoteItem(key=key, text=text), meta)

    @v_args(meta=True)
    def readable_image_body(self, meta, items):
        src: str | None = None
        alt: str | None = None
        caption: str | None = None
        for item in items:
            if isinstance(item, ReadableFieldPart):
                item_key = item.key
                item_value = item.value
                line, column = item.line, item.column
            else:
                item_key, item_value = item
                line, column = None, None
            if item_key == "src":
                if src is not None:
                    raise TransformParseFailure(
                        "Image readable blocks may define `src:` only once.",
                        hints=("Keep exactly one `src:` field in the image block body.",),
                        line=line,
                        column=column,
                    )
                src = item_value
            elif item_key == "alt":
                if alt is not None:
                    raise TransformParseFailure(
                        "Image readable blocks may define `alt:` only once.",
                        hints=("Keep exactly one `alt:` field in the image block body.",),
                        line=line,
                        column=column,
                    )
                alt = item_value
            elif item_key == "caption":
                if caption is not None:
                    raise TransformParseFailure(
                        "Image readable blocks may define `caption:` only once.",
                        hints=("Keep exactly one `caption:` field in the image block body.",),
                        line=line,
                        column=column,
                    )
                caption = item_value
        if src is None or alt is None:
            raise TransformParseFailure(
                "Image readable blocks require both `src:` and `alt:`.",
                hints=("Define both `src:` and `alt:` in the image block body.",),
            )
        return _with_source_span(
            model.ReadableImageData(src=src, alt=alt, caption=caption),
            meta,
        )

    @v_args(meta=True, inline=True)
    def readable_image_src(self, meta, text):
        return _positioned_readable_field(meta, "src", text)

    @v_args(meta=True, inline=True)
    def readable_image_alt(self, meta, text):
        return _positioned_readable_field(meta, "alt", text)

    @v_args(meta=True, inline=True)
    def readable_image_caption(self, meta, text):
        return _positioned_readable_field(meta, "caption", text)

    def readable_requirement_required(self, _items):
        return ("requirement", "required")

    def readable_requirement_advisory(self, _items):
        return ("requirement", "advisory")

    def readable_requirement_optional(self, _items):
        return ("requirement", "optional")

    @v_args(inline=True)
    def readable_guard(self, expr):
        return ("guard", expr)

    def shared_readable_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def shared_readable_block(self, value):
        return value

    @v_args(meta=True, inline=True)
    def shared_section_block(self, meta, key, title, *parts):
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return _with_source_span(
            model.ReadableBlock(
                kind="section",
                key=key,
                title=title,
                payload=tuple(payload),
                requirement=requirement,
                when_expr=when_expr,
                item_schema=item_schema,
                row_schema=row_schema,
            ),
            meta,
        )
