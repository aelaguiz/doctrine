from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    ReadableFieldPart,
    ReadablePayloadParts,
    _meta_line_column,
    _positioned_readable_field,
)
from doctrine.diagnostics import TransformParseFailure


class ReadableNodeTransformerMixin:
    """Shared readable-block and readable-payload lowering for the public parser boundary."""

    def readable_nonsection_block(self, items):
        return items[0]

    def override_readable_nonsection_block(self, items):
        return items[0]

    @v_args(inline=True)
    def readable_sequence_block(self, key, title, *parts):
        return self._readable_block("sequence", key, title, parts)

    @v_args(inline=True)
    def readable_properties_block(self, key, title, *parts):
        return self._readable_block("properties", key, title, parts)

    def readable_inline_properties_block(self, items):
        return model.ReadableBlock(
            kind="properties",
            key="properties",
            title=None,
            payload=items[0],
            anonymous=True,
        )

    @v_args(inline=True)
    def readable_guard_shell_block(self, key, guard, body):
        return model.ReadableBlock(
            kind="guard",
            key=key,
            title=None,
            payload=tuple(body),
            when_expr=guard[1],
        )

    @v_args(inline=True)
    def readable_bullets_block(self, key, title, *parts):
        return self._readable_block("bullets", key, title, parts)

    @v_args(inline=True)
    def readable_checklist_block(self, key, title, *parts):
        return self._readable_block("checklist", key, title, parts)

    @v_args(inline=True)
    def readable_definitions_block(self, key, title, *parts):
        return self._readable_block("definitions", key, title, parts)

    @v_args(inline=True)
    def readable_table_block(self, key, title, *parts):
        return self._readable_block("table", key, title, parts)

    @v_args(inline=True)
    def readable_callout_block(self, key, title, *parts):
        return self._readable_block("callout", key, title, parts)

    @v_args(inline=True)
    def readable_code_block(self, key, title, *parts):
        return self._readable_block("code", key, title, parts)

    @v_args(inline=True)
    def readable_markdown_block(self, key, title, *parts):
        return self._readable_block("markdown", key, title, parts)

    @v_args(inline=True)
    def readable_html_block(self, key, title, *parts):
        return self._readable_block("html", key, title, parts)

    @v_args(inline=True)
    def readable_footnotes_block(self, key, title, *parts):
        return self._readable_block("footnotes", key, title, parts)

    @v_args(inline=True)
    def readable_image_block(self, key, title, *parts):
        return self._readable_block("image", key, title, parts)

    @v_args(inline=True)
    def readable_rule_block(self, key, *parts):
        requirement, when_expr, item_schema, row_schema, _payload = self._split_readable_parts(parts)
        return model.ReadableBlock(
            kind="rule",
            key=key,
            title=None,
            payload=None,
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )

    @v_args(inline=True)
    def override_readable_sequence_block(self, key, *parts):
        return self._readable_override_block("sequence", key, parts)

    @v_args(inline=True)
    def override_readable_properties_block(self, key, *parts):
        return self._readable_override_block("properties", key, parts)

    @v_args(inline=True)
    def override_readable_guard_shell_block(self, key, guard, body):
        return model.DocumentOverrideBlock(
            kind="guard",
            key=key,
            title=None,
            payload=tuple(body),
            when_expr=guard[1],
        )

    @v_args(inline=True)
    def override_readable_bullets_block(self, key, *parts):
        return self._readable_override_block("bullets", key, parts)

    @v_args(inline=True)
    def override_readable_checklist_block(self, key, *parts):
        return self._readable_override_block("checklist", key, parts)

    @v_args(inline=True)
    def override_readable_definitions_block(self, key, *parts):
        return self._readable_override_block("definitions", key, parts)

    @v_args(inline=True)
    def override_readable_table_block(self, key, *parts):
        return self._readable_override_block("table", key, parts)

    @v_args(inline=True)
    def override_readable_callout_block(self, key, *parts):
        return self._readable_override_block("callout", key, parts)

    @v_args(inline=True)
    def override_readable_code_block(self, key, *parts):
        return self._readable_override_block("code", key, parts)

    @v_args(inline=True)
    def override_readable_markdown_block(self, key, *parts):
        return self._readable_override_block("markdown", key, parts)

    @v_args(inline=True)
    def override_readable_html_block(self, key, *parts):
        return self._readable_override_block("html", key, parts)

    @v_args(inline=True)
    def override_readable_footnotes_block(self, key, *parts):
        return self._readable_override_block("footnotes", key, parts)

    @v_args(inline=True)
    def override_readable_image_block(self, key, *parts):
        return self._readable_override_block("image", key, parts)

    @v_args(inline=True)
    def override_readable_rule_block(self, key, *parts):
        title, requirement, when_expr, item_schema, row_schema, _payload = self._split_readable_override_parts(parts)
        return model.DocumentOverrideBlock(
            kind="rule",
            key=key,
            title=title,
            payload=None,
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
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

    @v_args(inline=True)
    def readable_list_keyed_item(self, key, text):
        return model.ReadableListItem(key=key, text=text)

    @v_args(meta=True)
    def readable_item_schema_block(self, meta, items):
        return _positioned_readable_field(
            meta,
            "item_schema",
            model.ReadableInlineSchemaData(entries=tuple(items)),
        )

    def readable_properties_body(self, items):
        return model.ReadablePropertiesData(entries=tuple(items))

    @v_args(inline=True)
    def readable_property_item(self, key, title, body=None):
        return model.ReadablePropertyItem(key=key, title=title, body=tuple(body or ()))

    def readable_property_item_body(self, items):
        return tuple(items[0])

    def readable_definitions_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def readable_definition_item(self, key, title, body=None):
        return model.ReadableDefinitionItem(
            key=key,
            title=title,
            body=tuple(body or ()),
        )

    def readable_definition_item_body(self, items):
        return tuple(items[0])

    def readable_table_body(self, items):
        columns: tuple[model.ReadableTableColumn, ...] = ()
        rows: tuple[model.ReadableTableRow, ...] = ()
        notes: tuple[model.ProseLine, ...] = ()
        row_schema: model.ReadableInlineSchemaData | None = None
        for item in items:
            if isinstance(item, ReadableFieldPart):
                block_kind = item.key
                block_value = item.value
                line, column = item.line, item.column
            else:
                block_kind, block_value = item
                line, column = None, None
            if block_kind == "columns":
                columns = block_value
            elif block_kind == "rows":
                rows = block_value
            elif block_kind == "notes":
                notes = block_value
            elif block_kind == "row_schema":
                if row_schema is not None:
                    raise TransformParseFailure(
                        "Readable table bodies may define `row_schema:` only once.",
                        hints=("Keep exactly one `row_schema:` block per readable table.",),
                        line=line,
                        column=column,
                    )
                row_schema = block_value
        return ReadablePayloadParts(
            payload=model.ReadableTableData(
                columns=columns,
                rows=rows,
                notes=notes,
                row_schema=row_schema,
            ),
            row_schema=row_schema,
        )

    @v_args(meta=True)
    def readable_row_schema_block(self, meta, items):
        return _positioned_readable_field(
            meta,
            "row_schema",
            model.ReadableInlineSchemaData(entries=tuple(items)),
        )

    def readable_table_columns_block(self, items):
        return ("columns", tuple(items))

    @v_args(inline=True)
    def readable_table_column(self, key, title, body=None):
        return model.ReadableTableColumn(
            key=key,
            title=title,
            body=tuple(body or ()),
        )

    def readable_table_column_body(self, items):
        return tuple(items[0])

    def readable_table_rows_block(self, items):
        return ("rows", tuple(items))

    @v_args(inline=True)
    def readable_table_row(self, key, *cells):
        return model.ReadableTableRow(key=key, cells=tuple(cells))

    @v_args(inline=True)
    def readable_table_cell_text(self, key, text):
        return model.ReadableTableCell(key=key, text=text)

    @v_args(inline=True)
    def readable_table_cell_body(self, key, body):
        return model.ReadableTableCell(key=key, body=tuple(body))

    def readable_table_notes_block(self, items):
        return ("notes", tuple(items))

    @v_args(inline=True)
    def readable_table_note(self, value):
        return value

    @v_args(inline=True)
    def readable_inline_schema_item(self, key, title, body=None):
        return model.ReadableSchemaEntry(key=key, title=title, body=tuple(body or ()))

    def readable_inline_schema_item_body(self, items):
        return tuple(items[0])

    def readable_callout_body(self, items):
        kind: str | None = None
        body: list[model.ProseLine] = []
        for item in items:
            if isinstance(item, tuple) and item[0] == "kind":
                kind = item[1]
                continue
            body.append(item)
        return model.ReadableCalloutData(kind=kind, body=tuple(body))

    @v_args(inline=True)
    def readable_callout_kind(self, kind):
        return ("kind", kind)

    def readable_code_body(self, items):
        language: str | None = None
        text: str | None = None
        for item in items:
            if item[0] == "language":
                language = item[1]
            elif item[0] == "text":
                text = item[1]
        return model.ReadableCodeData(language=language, text="" if text is None else text)

    @v_args(inline=True)
    def readable_code_language(self, language):
        return ("language", language)

    @v_args(inline=True)
    def readable_code_text(self, text):
        return ("text", text)

    def readable_raw_text_body(self, items):
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
        return model.ReadableRawTextData(text="" if text is None else text)

    def readable_raw_text_line(self, items):
        return items[0]

    @v_args(meta=True, inline=True)
    def readable_raw_text_text(self, meta, text):
        return _positioned_readable_field(meta, "text", text)

    def readable_footnotes_body(self, items):
        return model.ReadableFootnotesData(entries=tuple(items))

    @v_args(inline=True)
    def readable_footnote_item(self, key, text):
        return model.ReadableFootnoteItem(key=key, text=text)

    def readable_image_body(self, items):
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
        return model.ReadableImageData(src=src, alt=alt, caption=caption)

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

    @v_args(inline=True)
    def shared_section_block(self, key, title, *parts):
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return model.ReadableBlock(
            kind="section",
            key=key,
            title=title,
            payload=tuple(payload),
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )
