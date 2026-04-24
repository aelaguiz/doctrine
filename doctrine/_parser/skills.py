from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    EnumMemberFieldPart,
    SkillDeclBodyParts,
    SkillEntryBindBlockPart,
    SkillEntryBodyParts,
    SkillPackageBodyParts,
    SkillPackageEmitBlockPart,
    SkillPackageHostContractBlockPart,
    SkillPackageMetadataBlockPart,
    SkillPackageMetadataFieldPart,
    SkillPackageSourceBlockPart,
    SkillPackageSourceIdPart,
    SkillPackageSourceTrackBlockPart,
    SkillsBodyParts,
    _body_prose_location,
    _body_prose_value,
    _expand_grouped_inherit,
    _flatten_grouped_items,
    _meta_line_column,
    _positioned_body_prose,
    _positioned_enum_member_field,
    _with_source_span,
)
from doctrine.diagnostics import TransformParseFailure


def _split_record_scalar_body(
    body, *, key: str
):
    """Split a record scalar-head body into non-type items and a `type:` name.

    The grammar permits a `type:` line only inside the scalar-head record
    body (`record_keyed_scalar_body`). Every field-shaped body in the
    language routes `type:` through `resolve_field_type_ref`.
    """
    if body is None:
        return None, None, None
    remaining: list = []
    type_name: str | None = None
    type_source_span: model.SourceSpan | None = None
    for item in body:
        if isinstance(item, model.OutputSchemaSetting) and item.key == "type":
            if type_name is not None:
                raise TransformParseFailure(
                    f"Duplicate `type:` line in record field `{key}` body.",
                    hints=("Declare `type:` at most once per field.",),
                )
            type_name = item.value
            type_source_span = item.source_span
            continue
        remaining.append(item)
    return remaining, type_name, type_source_span


class SkillsTransformerMixin:
    """Shared skills, records, skill package, and enum lowering."""

    @v_args(meta=True, inline=True)
    def skills_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        skills_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            skills_body = body
        return _with_source_span(
            model.SkillsDecl(
                name=name,
                body=model.SkillsBody(
                    title=title,
                    preamble=skills_body.preamble,
                    items=skills_body.items,
                ),
                parent_ref=parent_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_package_decl(self, meta, name, title, body):
        return _with_source_span(
            model.SkillPackageDecl(
                name=name,
                title=title,
                items=body.items,
                metadata=body.metadata,
                source=body.source,
                emit_entries=body.emit_entries,
                host_contract=body.host_contract,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_decl(self, meta, name, title, body):
        return _with_source_span(
            model.SkillDecl(
                name=name,
                title=title,
                items=body.items,
                package_link=body.package_link,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def enum_decl(self, meta, name, title, members):
        return _with_source_span(
            model.EnumDecl(name=name, title=title, members=tuple(members)),
            meta,
        )

    def enum_body(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def enum_member(self, meta, key, title, body=None):
        wire: str | None = None
        for item in body or ():
            if isinstance(item, EnumMemberFieldPart):
                field_key = item.key
                field_value = item.value
                line, column = item.line, item.column
            else:
                field_key, field_value = item
                line, column = None, None
            if field_key != "wire":
                raise TransformParseFailure(
                    f"Unknown enum member field: {field_key}",
                    hints=("Only `wire:` is legal inside an enum-member body.",),
                    line=line,
                    column=column,
                )
            if wire is not None:
                raise TransformParseFailure(
                    "Enum member may declare `wire` at most once.",
                    hints=("Keep one `wire:` field per enum member.",),
                    line=line,
                    column=column,
                )
            wire = field_value
        return _with_source_span(model.EnumMember(key=key, title=title, wire=wire), meta)

    def enum_member_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def enum_member_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def enum_member_wire_stmt(self, meta, value):
        return _positioned_enum_member_field(meta, "wire", value)

    @v_args(meta=True, inline=True)
    def skills_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def skills_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def skill_entry(self, meta, key, target, body=None):
        items = tuple() if body is None else body.items
        binds = tuple() if body is None else body.binds
        mode = None if body is None else body.mode
        return _with_source_span(
            model.SkillEntry(
                key=key,
                target=target,
                items=items,
                binds=binds,
                mode=mode,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skills_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def skills_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    @v_args(meta=True, inline=True)
    def skills_override_entry(self, meta, key, target, body=None):
        items = tuple() if body is None else body.items
        binds = tuple() if body is None else body.binds
        mode = None if body is None else body.mode
        return _with_source_span(
            model.OverrideSkillEntry(
                key=key,
                target=target,
                items=items,
                binds=binds,
                mode=mode,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skills_section(self, meta, key, title, items):
        return _with_source_span(
            model.SkillsSection(key=key, title=title, items=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skills_override_section(self, meta, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return _with_source_span(
            model.OverrideSkillsSection(
                key=key,
                title=title,
                items=tuple(section_items),
            ),
            meta,
        )

    def record_body(self, items):
        return tuple(items)

    def skill_decl_body(self, items):
        record_items: list[model.RecordItem] = []
        package_link: model.SkillPackageLink | None = None
        for item in items:
            if isinstance(item, model.SkillPackageLink):
                if package_link is not None:
                    raise TransformParseFailure(
                        "Skills may define `package:` only once.",
                        hints=("Keep exactly one `package:` field per skill.",),
                        line=item.source_span.line if item.source_span is not None else None,
                        column=item.source_span.column if item.source_span is not None else None,
                    )
                package_link = item
                continue
            record_items.append(item)
        return SkillDeclBodyParts(items=tuple(record_items), package_link=package_link)

    def skill_entry_body(self, items):
        record_items: list[model.RecordItem] = []
        binds: tuple[model.SkillEntryBind, ...] = ()
        mode: model.ModeStmt | None = None
        seen_bind = False
        for item in items:
            if isinstance(item, SkillEntryBindBlockPart):
                if seen_bind:
                    raise TransformParseFailure(
                        "Skill entries may define `bind:` only once.",
                        hints=("Keep exactly one `bind:` block per skill entry.",),
                        line=item.line,
                        column=item.column,
                    )
                binds = self._skill_entry_binds(item.binds)
                seen_bind = True
                continue
            if isinstance(item, model.ModeStmt):
                if mode is not None:
                    line = item.source_span.line if item.source_span is not None else None
                    column = item.source_span.column if item.source_span is not None else None
                    raise TransformParseFailure(
                        "Skill entries may declare `mode` only once.",
                        hints=("Keep exactly one `mode <CNAME> = <expr> as <Enum>` line per skill entry.",),
                        line=line,
                        column=column,
                    )
                mode = item
                continue
            record_items.append(item)
        return SkillEntryBodyParts(items=tuple(record_items), binds=binds, mode=mode)

    @v_args(inline=True)
    def skill_entry_body_line(self, value):
        return value

    def skill_package_body(self, items):
        record_items: list[model.RecordItem] = []
        metadata = model.SkillPackageMetadata()
        source = model.SkillPackageSource()
        emit_entries: tuple[model.SkillPackageEmitEntry, ...] = ()
        host_contract: tuple[model.SkillPackageHostSlotItem, ...] = ()
        seen_metadata = False
        seen_source = False
        seen_emit = False
        seen_host_contract = False
        for item in items:
            if isinstance(item, SkillPackageMetadataBlockPart):
                if seen_metadata:
                    raise TransformParseFailure(
                        "Skill packages may define `metadata:` only once.",
                        hints=("Keep exactly one `metadata:` block per skill package.",),
                        line=item.line,
                        column=item.column,
                    )
                metadata = self._skill_package_metadata(item.fields)
                seen_metadata = True
                continue
            if isinstance(item, SkillPackageSourceBlockPart):
                if seen_source:
                    raise TransformParseFailure(
                        "Skill packages may define `source:` only once.",
                        hints=("Keep exactly one `source:` block per skill package.",),
                        line=item.line,
                        column=item.column,
                    )
                source = self._skill_package_source(item.items)
                seen_source = True
                continue
            if isinstance(item, SkillPackageEmitBlockPart):
                if seen_emit:
                    raise TransformParseFailure(
                        "Skill packages may define `emit:` only once.",
                        hints=("Keep exactly one `emit:` block per skill package.",),
                        line=item.line,
                        column=item.column,
                    )
                emit_entries = item.entries
                seen_emit = True
                continue
            if isinstance(item, SkillPackageHostContractBlockPart):
                if seen_host_contract:
                    raise TransformParseFailure(
                        "Skill packages may define `host_contract:` only once.",
                        hints=("Keep exactly one `host_contract:` block per skill package.",),
                        line=item.line,
                        column=item.column,
                    )
                host_contract = self._skill_package_host_contract(item.slots)
                seen_host_contract = True
                continue
            record_items.append(item)
        return SkillPackageBodyParts(
            items=tuple(record_items),
            metadata=metadata,
            source=source,
            emit_entries=emit_entries,
            host_contract=host_contract,
        )

    def _skill_package_source(
        self,
        items: tuple[SkillPackageSourceIdPart | SkillPackageSourceTrackBlockPart, ...],
    ) -> model.SkillPackageSource:
        source_id: str | None = None
        tracked_paths: tuple[model.SkillPackageTrackedSource, ...] = ()
        seen_track = False
        for item in items:
            if isinstance(item, SkillPackageSourceIdPart):
                if source_id is not None:
                    raise TransformParseFailure(
                        "Skill package `source:` may define `id:` only once.",
                        hints=("Keep one stable source id per skill package.",),
                        line=item.line,
                        column=item.column,
                    )
                source_id = item.value
                continue
            if isinstance(item, SkillPackageSourceTrackBlockPart):
                if seen_track:
                    raise TransformParseFailure(
                        "Skill package `source:` may define `track:` only once.",
                        hints=("Keep one `track:` list per skill package.",),
                        line=item.line,
                        column=item.column,
                    )
                tracked_paths = item.tracked_paths
                seen_track = True
                continue
        return model.SkillPackageSource(
            source_id=source_id,
            tracked_paths=tracked_paths,
        )

    @v_args(inline=True)
    def record_text(self, value):
        return value

    @v_args(meta=True)
    def package_metadata_block(self, meta, items):
        line, column = _meta_line_column(meta)
        return SkillPackageMetadataBlockPart(
            fields=tuple(items),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def package_metadata_item(self, meta, key, value):
        line, column = _meta_line_column(meta)
        return SkillPackageMetadataFieldPart(
            key=key,
            value=value,
            line=line,
            column=column,
        )

    @v_args(meta=True)
    def package_emit_block(self, meta, items):
        line, column = _meta_line_column(meta)
        return SkillPackageEmitBlockPart(
            entries=tuple(items),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def package_emit_item(self, meta, path, ref):
        return _with_source_span(
            model.SkillPackageEmitEntry(path=path, ref=ref),
            meta,
        )

    @v_args(meta=True)
    def package_source_block(self, meta, items):
        line, column = _meta_line_column(meta)
        return SkillPackageSourceBlockPart(
            items=tuple(items),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def package_source_id_item(self, meta, value):
        line, column = _meta_line_column(meta)
        return SkillPackageSourceIdPart(value=value, line=line, column=column)

    @v_args(meta=True)
    def package_source_track_block(self, meta, items):
        line, column = _meta_line_column(meta)
        return SkillPackageSourceTrackBlockPart(
            tracked_paths=tuple(items),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def package_source_track_item(self, meta, path):
        return _with_source_span(
            model.SkillPackageTrackedSource(path=path),
            meta,
        )

    @v_args(meta=True)
    def package_host_contract_block(self, meta, items):
        line, column = _meta_line_column(meta)
        return SkillPackageHostContractBlockPart(
            slots=tuple(items),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def package_host_slot(self, meta, family, key, title):
        return _with_source_span(
            model.SkillPackageHostSlot(key=key, family=family, title=title),
            meta,
        )

    @v_args(meta=True, inline=True)
    def package_host_receipt_slot(self, meta, key, title, fields=None):
        field_tuple: tuple[model.ReceiptField, ...] = (
            tuple(fields) if fields is not None else ()
        )
        return _with_source_span(
            model.ReceiptHostSlot(key=key, title=title, fields=field_tuple),
            meta,
        )

    def receipt_slot_body(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def receipt_field(self, meta, key, type_value):
        type_ref, list_element = type_value
        return _with_source_span(
            model.ReceiptField(
                key=key,
                type_ref=type_ref,
                list_element=list_element,
            ),
            meta,
        )

    @v_args(inline=True)
    def receipt_field_type(self, value):
        if isinstance(value, tuple):
            return value
        return (value, False)

    @v_args(inline=True)
    def receipt_field_list_type(self, name_ref):
        return (name_ref, True)

    def package_host_slot_family_input(self, _children):
        return "input"

    def package_host_slot_family_output(self, _children):
        return "output"

    def package_host_slot_family_document(self, _children):
        return "document"

    def package_host_slot_family_analysis(self, _children):
        return "analysis"

    def package_host_slot_family_schema(self, _children):
        return "schema"

    def package_host_slot_family_table(self, _children):
        return "table"

    def package_host_slot_family_final_output(self, _children):
        return "final_output"

    @v_args(meta=True, inline=True)
    def skill_package_link_stmt(self, meta, package_id):
        return _with_source_span(
            model.SkillPackageLink(package_id=package_id),
            meta,
        )

    @v_args(meta=True)
    def skill_entry_bind_block(self, meta, items):
        line, column = _meta_line_column(meta)
        return SkillEntryBindBlockPart(
            binds=tuple(items),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def skill_entry_bind_item(self, meta, key, target):
        return _with_source_span(
            model.SkillEntryBind(key=key, target=target),
            meta,
        )

    @v_args(inline=True)
    def record_readable_block(self, value):
        return value

    @v_args(inline=True)
    def record_section_block(self, key, title, *parts):
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

    def record_item_body(self, items):
        return tuple(items[0])

    def record_keyed_scalar_body(self, items):
        # Grammar: `_INDENT record_keyed_scalar_body_line+ _DEDENT`
        # Each line is either an `OutputSchemaSetting(key="type")` or a
        # record_item. We pass the whole list through; the item handler
        # splits the `type:` line off into `type_name` + `type_source_span`.
        return tuple(items)

    @v_args(meta=True, inline=True)
    def record_keyed_scalar_item(self, meta, key, head, body=None):
        body_items, type_name, type_source_span = _split_record_scalar_body(
            body, key=key
        )
        if type_name is None and body_items is not None and body_items:
            return _with_source_span(
                model.RecordSection(key=key, title=head, items=tuple(body_items)),
                meta,
            )
        scalar_body: tuple | None
        if body_items:
            scalar_body = tuple(body_items)
        else:
            scalar_body = None
        return _with_source_span(
            model.RecordScalar(
                key=key,
                value=head,
                body=scalar_body,
                type_name=type_name,
                type_source_span=type_source_span,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def record_keyed_ref_item(self, meta, key, head, body=None):
        return _with_source_span(
            model.RecordScalar(
                key=key,
                value=head,
                body=None if body is None else tuple(body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def record_ref_item(self, meta, ref, body=None):
        return _with_source_span(
            model.RecordRef(ref=ref, body=None if body is None else tuple(body)),
            meta,
        )

    def skills_body(self, items):
        preamble: list[model.ProseLine] = []
        skills_items: list[model.SkillsItem] = []
        items = _flatten_grouped_items(items)
        for item in items:
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if skills_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Skills prose lines must appear before keyed skills entries.",
                        hints=(
                            "Move prose lines to the top of the skills body or put them inside a titled skills section.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            skills_items.append(item)
        return SkillsBodyParts(preamble=tuple(preamble), items=tuple(skills_items))

    def skills_section_body(self, items):
        return tuple(items)
