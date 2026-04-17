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
        return _with_source_span(
            model.SkillEntry(
                key=key,
                target=target,
                items=items,
                binds=binds,
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
        return _with_source_span(
            model.OverrideSkillEntry(
                key=key,
                target=target,
                items=items,
                binds=binds,
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
            record_items.append(item)
        return SkillEntryBodyParts(items=tuple(record_items), binds=binds)

    @v_args(inline=True)
    def skill_entry_body_line(self, value):
        return value

    def skill_package_body(self, items):
        record_items: list[model.RecordItem] = []
        metadata = model.SkillPackageMetadata()
        emit_entries: tuple[model.SkillPackageEmitEntry, ...] = ()
        host_contract: tuple[model.SkillPackageHostSlot, ...] = ()
        seen_metadata = False
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
            emit_entries=emit_entries,
            host_contract=host_contract,
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

    @v_args(meta=True, inline=True)
    def record_keyed_item(self, meta, key, head, body=None):
        if isinstance(head, str) and body is not None:
            return _with_source_span(
                model.RecordSection(key=key, title=head, items=tuple(body)),
                meta,
            )
        return _with_source_span(
            model.RecordScalar(key=key, value=head, body=None if body is None else tuple(body)),
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
