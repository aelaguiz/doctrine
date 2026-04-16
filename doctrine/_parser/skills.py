from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    EnumMemberFieldPart,
    SkillPackageBodyParts,
    SkillPackageMetadataBlockPart,
    SkillPackageMetadataFieldPart,
    SkillsBodyParts,
    _body_prose_location,
    _body_prose_value,
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
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_decl(self, meta, name, title, items):
        return _with_source_span(
            model.SkillDecl(name=name, title=title, items=tuple(items)),
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

    @v_args(inline=True)
    def skill_entry(self, key, target, body=None):
        return model.SkillEntry(
            key=key,
            target=target,
            items=tuple(body or ()),
        )

    @v_args(meta=True, inline=True)
    def skills_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(inline=True)
    def skills_override_entry(self, key, target, body=None):
        return model.OverrideSkillEntry(
            key=key,
            target=target,
            items=tuple(body or ()),
        )

    @v_args(inline=True)
    def skills_section(self, key, title, items):
        return model.SkillsSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def skills_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideSkillsSection(
            key=key,
            title=title,
            items=tuple(section_items),
        )

    def record_body(self, items):
        return tuple(items)

    def skill_package_body(self, items):
        record_items: list[model.RecordItem] = []
        metadata = model.SkillPackageMetadata()
        seen_metadata = False
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
            record_items.append(item)
        return SkillPackageBodyParts(
            items=tuple(record_items),
            metadata=metadata,
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

    @v_args(inline=True)
    def record_keyed_item(self, key, head, body=None):
        if isinstance(head, str) and body is not None:
            return model.RecordSection(key=key, title=head, items=tuple(body))
        return model.RecordScalar(key=key, value=head, body=None if body is None else tuple(body))

    @v_args(inline=True)
    def record_ref_item(self, ref, body=None):
        return model.RecordRef(ref=ref, body=None if body is None else tuple(body))

    def skills_body(self, items):
        preamble: list[model.ProseLine] = []
        skills_items: list[model.SkillsItem] = []
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

    def skill_entry_body(self, items):
        return tuple(items[0])
