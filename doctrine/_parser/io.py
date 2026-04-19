from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    InputBodyParts,
    InputStructurePart,
    IoBodyParts,
    OutputBodyParts,
    OutputRecordSectionPart,
    OutputSchemaPart,
    OutputStructurePart,
    OutputTargetDeliverySkillPart,
    RenderProfilePart,
    TrustSurfacePart,
    _body_prose_location,
    _body_prose_value,
    _expand_grouped_inherit,
    _flatten_grouped_items,
    _meta_line_column,
    _positioned_body_prose,
    _positioned_input_structure,
    _positioned_render_profile,
    _positioned_trust_surface,
    _source_span_from_line_column,
    _source_span_from_meta,
    _with_source_span,
)
from doctrine._parser.skills import _split_record_scalar_body
from doctrine.diagnostics import TransformParseFailure


class IoTransformerMixin:
    """Shared inputs, outputs, and IO-body lowering for the public parser boundary."""

    def _io_section_from_ref(
        self,
        section_type: type[model.IoSection] | type[model.OverrideIoSection],
        *,
        key: str,
        ref: model.NameRef,
        meta: object,
    ) -> model.IoSection | model.OverrideIoSection:
        record_ref = model.RecordRef(ref=ref, source_span=ref.source_span)
        return section_type(
            key=key,
            title=None,
            items=(record_ref,),
            source_span=_source_span_from_meta(meta),
        )

    @v_args(meta=True, inline=True)
    def inputs_inline_field(self, meta, title, items):
        return _with_source_span(model.InputsField(title=title, value=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def inputs_ref_field(self, meta, ref):
        return _with_source_span(model.InputsField(title=None, value=ref), meta)

    @v_args(meta=True, inline=True)
    def inputs_patch_field(self, meta, parent_ref, title, body):
        return _with_source_span(
            model.InputsField(
                title=title,
                value=self._io_body(title, body),
                parent_ref=parent_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def outputs_inline_field(self, meta, title, items):
        return _with_source_span(model.OutputsField(title=title, value=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def outputs_ref_field(self, meta, ref):
        return _with_source_span(model.OutputsField(title=None, value=ref), meta)

    @v_args(meta=True, inline=True)
    def outputs_patch_field(self, meta, parent_ref, title, body):
        return _with_source_span(
            model.OutputsField(
                title=title,
                value=self._io_body(title, body),
                parent_ref=parent_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def inputs_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return _with_source_span(
            model.InputsDecl(
                name=name,
                body=self._io_body(title, io_body),
                parent_ref=parent_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def input_decl(self, meta, name, title, body):
        return _with_source_span(
            model.InputDecl(
                name=name,
                title=title,
                items=body.items,
                structure=body.structure,
            ),
            meta,
        )

    @v_args(inline=True)
    def input_body_line(self, value):
        return value

    def input_body(self, items):
        record_items: list[model.RecordItem] = []
        structure: model.InputStructureConfig | None = None
        for item in items:
            if isinstance(item, InputStructurePart):
                if structure is not None:
                    raise TransformParseFailure(
                        "Input declarations may define `structure:` only once.",
                        hints=("Keep exactly one `structure:` attachment per input declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                structure = item.config
                continue
            record_items.append(item)
        return InputBodyParts(items=tuple(record_items), structure=structure)

    @v_args(meta=True, inline=True)
    def input_structure_stmt(self, meta, ref):
        return _positioned_input_structure(meta, ref)

    @v_args(meta=True, inline=True)
    def input_source_decl(self, meta, name, title, items):
        return _with_source_span(
            model.InputSourceDecl(name=name, title=title, items=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        output_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            output_body = body
        return _with_source_span(
            model.OutputDecl(
                name=name,
                title=title,
                items=output_body.items,
                schema=output_body.schema,
                structure=output_body.structure,
                render_profile_ref=output_body.render_profile_ref,
                trust_surface=output_body.trust_surface,
                parent_ref=parent_ref,
                schema_mode=output_body.schema_mode,
                structure_mode=output_body.structure_mode,
                render_profile_mode=output_body.render_profile_mode,
                trust_surface_mode=output_body.trust_surface_mode,
                schema_source_span=output_body.schema_source_span,
                structure_source_span=output_body.structure_source_span,
                render_profile_source_span=output_body.render_profile_source_span,
                trust_surface_source_span=output_body.trust_surface_source_span,
            ),
            meta,
        )

    @v_args(inline=True)
    def output_body_line(self, value):
        return value

    def output_body(self, items):
        record_items: list[model.OutputAuthoredItem] = []
        items = _flatten_grouped_items(items)
        schema: model.OutputSchemaConfig | None = None
        structure: model.OutputStructureConfig | None = None
        render_profile_ref: model.NameRef | None = None
        trust_surface: tuple[model.TrustSurfaceItem, ...] = ()
        schema_mode: str | None = None
        structure_mode: str | None = None
        render_profile_mode: str | None = None
        trust_surface_mode: str | None = None
        schema_source_span: model.SourceSpan | None = None
        structure_source_span: model.SourceSpan | None = None
        render_profile_source_span: model.SourceSpan | None = None
        trust_surface_source_span: model.SourceSpan | None = None
        has_must_include = False
        for item in items:
            if isinstance(item, RenderProfilePart):
                if render_profile_mode is not None:
                    raise TransformParseFailure(
                        "Output declarations may define `render_profile:` only once.",
                        hints=("Keep exactly one `render_profile:` attachment per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                render_profile_ref = item.ref
                render_profile_mode = "override" if item.override else "set"
                render_profile_source_span = _source_span_from_line_column(item.line, item.column)
                continue
            if isinstance(item, TrustSurfacePart):
                if trust_surface_mode is not None:
                    raise TransformParseFailure(
                        "Output declarations may define `trust_surface` only once.",
                        hints=("Keep exactly one `trust_surface:` block per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                trust_surface = item.items
                trust_surface_mode = "override" if item.override else "set"
                trust_surface_source_span = _source_span_from_line_column(item.line, item.column)
                continue
            if isinstance(item, OutputSchemaPart):
                if schema_mode is not None:
                    raise TransformParseFailure(
                        "Output declarations may define `schema:` only once.",
                        hints=("Keep exactly one `schema:` attachment per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                if structure is not None:
                    raise TransformParseFailure(
                        "Outputs may not define both `schema:` and `structure:`.",
                        hints=(
                            "Pick one artifact owner per markdown output declaration.",
                            "Use `schema:` for reusable inventory ownership or `structure:` for reusable markdown structure, not both.",
                        ),
                        line=item.line,
                        column=item.column,
                    )
                if has_must_include:
                    raise TransformParseFailure(
                        "Outputs may not define both `schema:` and `must_include:`.",
                        hints=(
                            "Pick one inventory owner per output declaration.",
                            "Use `schema:` for reusable inventory ownership or keep local `must_include:` prose, not both.",
                        ),
                        line=item.line,
                        column=item.column,
                    )
                schema = item.config
                schema_mode = "override" if item.override else "set"
                schema_source_span = _source_span_from_line_column(item.line, item.column)
                continue
            if isinstance(item, OutputStructurePart):
                if structure_mode is not None:
                    raise TransformParseFailure(
                        "Output declarations may define `structure:` only once.",
                        hints=("Keep exactly one `structure:` attachment per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                if schema is not None:
                    raise TransformParseFailure(
                        "Outputs may not define both `schema:` and `structure:`.",
                        hints=(
                            "Pick one artifact owner per markdown output declaration.",
                            "Use `schema:` for reusable inventory ownership or `structure:` for reusable markdown structure, not both.",
                        ),
                        line=item.line,
                        column=item.column,
                    )
                structure = item.config
                structure_mode = "override" if item.override else "set"
                structure_source_span = _source_span_from_line_column(item.line, item.column)
                continue
            if isinstance(item, model.InheritItem):
                if item.key == "schema":
                    if schema_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `schema:` only once.",
                            hints=("Keep exactly one `schema:` attachment per output declaration.",),
                        )
                    schema_mode = "inherit"
                    schema_source_span = item.source_span
                    continue
                if item.key == "structure":
                    if structure_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `structure:` only once.",
                            hints=("Keep exactly one `structure:` attachment per output declaration.",),
                        )
                    structure_mode = "inherit"
                    structure_source_span = item.source_span
                    continue
                if item.key == "render_profile":
                    if render_profile_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `render_profile:` only once.",
                            hints=("Keep exactly one `render_profile:` attachment per output declaration.",),
                        )
                    render_profile_mode = "inherit"
                    render_profile_source_span = item.source_span
                    continue
                if item.key == "trust_surface":
                    if trust_surface_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `trust_surface` only once.",
                            hints=("Keep exactly one `trust_surface:` block per output declaration.",),
                        )
                    trust_surface_mode = "inherit"
                    trust_surface_source_span = item.source_span
                    continue
            if isinstance(item, OutputRecordSectionPart):
                if item.section.key == "must_include":
                    if schema_mode is not None and schema is not None:
                        raise TransformParseFailure(
                            "Outputs may not define both `schema:` and `must_include:`.",
                            hints=(
                                "Pick one inventory owner per output declaration.",
                                "Use `schema:` for reusable inventory ownership or keep local `must_include:` prose, not both.",
                            ),
                            line=item.line,
                            column=item.column,
                        )
                    has_must_include = True
                record_items.append(item.section)
                continue
            record_items.append(item)
        return OutputBodyParts(
            items=tuple(record_items),
            schema=schema,
            structure=structure,
            render_profile_ref=render_profile_ref,
            trust_surface=trust_surface,
            schema_mode=schema_mode,
            structure_mode=structure_mode,
            render_profile_mode=render_profile_mode,
            trust_surface_mode=trust_surface_mode,
            schema_source_span=schema_source_span,
            structure_source_span=structure_source_span,
            render_profile_source_span=render_profile_source_span,
            trust_surface_source_span=trust_surface_source_span,
        )

    def output_shape_body(self, items):
        items = _flatten_grouped_items(items)
        return tuple(
            item.section if isinstance(item, OutputRecordSectionPart) else item
            for item in items
        )

    @v_args(inline=True)
    def output_shape_body_line(self, value):
        return value

    @v_args(inline=True)
    def output_shape_schema_item(self, ref):
        return model.RecordScalar(key="schema", value=ref)

    @v_args(inline=True)
    def output_shape_override_schema_item(self, ref):
        return model.OutputOverrideRecordScalar(key="schema", value=ref)

    @v_args(meta=True)
    def output_shape_selector_block(self, meta, items):
        if len(items) != 1:
            raise TransformParseFailure(
                "Output shape selector blocks must declare exactly one selector.",
                location=_meta_line_column(meta),
            )
        return items[0]

    @v_args(meta=True, inline=True)
    def output_shape_selector_stmt(self, meta, field_name, enum_ref):
        return _with_source_span(
            model.OutputShapeSelectorConfig(field_name=field_name, enum_ref=enum_ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_record_case_stmt(self, meta, enum_member_ref, body):
        return _with_source_span(
            model.OutputRecordCase(
                enum_member_ref=enum_member_ref,
                items=tuple(body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return OutputSchemaPart(
            config=model.OutputSchemaConfig(schema_ref=ref),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def output_override_schema_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return OutputSchemaPart(
            config=model.OutputSchemaConfig(schema_ref=ref),
            override=True,
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def output_structure_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return OutputStructurePart(
            config=model.OutputStructureConfig(structure_ref=ref),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def output_override_structure_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return OutputStructurePart(
            config=model.OutputStructureConfig(structure_ref=ref),
            override=True,
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def output_render_profile_stmt(self, meta, ref):
        return _positioned_render_profile(meta, ref)

    @v_args(meta=True, inline=True)
    def output_override_render_profile_stmt(self, meta, ref):
        return _positioned_render_profile(meta, ref, override=True)

    def output_record_body(self, items):
        return tuple(
            item.section if isinstance(item, OutputRecordSectionPart) else item
            for item in items
        )

    @v_args(inline=True)
    def output_record_item(self, value):
        return value

    @v_args(meta=True, inline=True)
    def output_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def output_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    def output_record_item_body(self, items):
        return tuple(items[0])

    def output_record_keyed_scalar_body(self, items):
        # Grammar: `_INDENT output_record_keyed_scalar_body_line+ _DEDENT`.
        # Each line is either an `OutputSchemaSetting(key="type")` or an
        # `output_record_item`. The item handler splits the `type:` line
        # off into `type_name` + `type_source_span` on the resulting
        # `RecordScalar`. Unwrap `OutputRecordSectionPart` the same way
        # `output_record_body` does.
        return tuple(
            item.section if isinstance(item, OutputRecordSectionPart) else item
            for item in items
        )

    @v_args(meta=True, inline=True)
    def output_record_keyed_scalar_item(self, meta, key, head, body=None):
        body_items, type_name, type_source_span = _split_record_scalar_body(
            body, key=key
        )
        if type_name is None and body_items is not None and body_items:
            line, column = _meta_line_column(meta)
            return OutputRecordSectionPart(
                section=_with_source_span(
                    model.RecordSection(key=key, title=head, items=tuple(body_items)),
                    meta,
                ),
                line=line,
                column=column,
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
    def output_record_keyed_ref_item(self, meta, key, head, body=None):
        return _with_source_span(
            model.RecordScalar(
                key=key,
                value=head,
                body=None if body is None else tuple(body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_override_keyed_item(self, meta, key, head, body=None):
        if isinstance(head, str) and body is not None:
            line, column = _meta_line_column(meta)
            return OutputRecordSectionPart(
                section=_with_source_span(
                    model.OutputOverrideRecordSection(
                        key=key,
                        title=head,
                        items=tuple(body),
                    ),
                    meta,
                ),
                line=line,
                column=column,
            )
        return _with_source_span(
            model.OutputOverrideRecordScalar(
                key=key,
                value=head,
                body=None if body is None else tuple(body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_record_ref_item(self, meta, ref, body=None):
        return _with_source_span(
            model.RecordRef(ref=ref, body=None if body is None else tuple(body)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def guarded_output_section(self, meta, key, title, when_expr, items):
        return _with_source_span(
            model.GuardedOutputSection(
                key=key,
                title=title,
                when_expr=when_expr,
                items=tuple(items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_override_guarded_section(self, meta, key, title, when_expr, items):
        return _with_source_span(
            model.OutputOverrideGuardedOutputSection(
                key=key,
                title=title,
                when_expr=when_expr,
                items=tuple(items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def guarded_output_scalar_item(self, meta, key, head, when_expr, body=None):
        return _with_source_span(
            model.GuardedOutputScalar(
                key=key,
                value=head,
                when_expr=when_expr,
                body=None if body is None else tuple(body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_override_guarded_scalar_item(self, meta, key, head, when_expr, body=None):
        return _with_source_span(
            model.OutputOverrideGuardedOutputScalar(
                key=key,
                value=head,
                when_expr=when_expr,
                body=None if body is None else tuple(body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_route_via_stmt(self, meta, section, resolution):
        return _with_source_span(
            model.ReviewRouteVia(section=section, resolution=resolution),
            meta,
        )

    def review_outcome_accept(self, _items):
        return "on_accept"

    def review_outcome_reject(self, _items):
        return "on_reject"

    def review_route_resolution_route(self, _items):
        return "route"

    @v_args(meta=True)
    def trust_surface_block(self, meta, items):
        return _positioned_trust_surface(meta, tuple(items))

    @v_args(meta=True)
    def output_override_trust_surface_block(self, meta, items):
        return _positioned_trust_surface(meta, tuple(items), override=True)

    @v_args(meta=True, inline=True)
    def trust_surface_item(self, meta, path, when_expr=None):
        return _with_source_span(
            model.TrustSurfaceItem(path=tuple(path), when_expr=when_expr),
            meta,
        )

    @v_args(inline=True)
    def trust_surface_when(self, expr):
        return expr

    @v_args(meta=True, inline=True)
    def outputs_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return _with_source_span(
            model.OutputsDecl(
                name=name,
                body=self._io_body(title, io_body),
                parent_ref=parent_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_target_decl(self, meta, name, title, body):
        return _with_source_span(
            model.OutputTargetDecl(
                name=name,
                title=title,
                items=body[0],
                delivery_skill_ref=body[1],
            ),
            meta,
        )

    @v_args(inline=True)
    def output_target_body_line(self, value):
        return value

    def output_target_body(self, items):
        record_items: list[model.RecordItem] = []
        delivery_skill_ref: model.NameRef | None = None
        for item in items:
            if isinstance(item, OutputTargetDeliverySkillPart):
                if delivery_skill_ref is not None:
                    raise TransformParseFailure(
                        "Output target declarations may define `delivery_skill:` only once.",
                        hints=("Keep exactly one delivery skill binding per output target.",),
                        line=item.line,
                        column=item.column,
                    )
                delivery_skill_ref = item.ref
                continue
            record_items.append(item)
        return tuple(record_items), delivery_skill_ref

    @v_args(meta=True, inline=True)
    def output_target_delivery_skill_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return OutputTargetDeliverySkillPart(ref=ref, line=line, column=column)

    @v_args(meta=True, inline=True)
    def output_shape_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        items = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            items = body
        selector: model.OutputShapeSelectorConfig | None = None
        non_selector_items: list[object] = []
        for item in items:
            if isinstance(item, model.OutputShapeSelectorConfig):
                if selector is not None:
                    raise TransformParseFailure(
                        f"Output shape `{name}` declares more than one `selector:` block.",
                        location=_meta_line_column(meta),
                    )
                selector = item
                continue
            non_selector_items.append(item)
        return _with_source_span(
            model.OutputShapeDecl(
                name=name,
                title=title,
                items=tuple(non_selector_items),
                parent_ref=parent_ref,
                selector=selector,
            ),
            meta,
        )

    def output_schema_body(self, items):
        return _flatten_grouped_items(items)

    def output_schema_item_body(self, items):
        return tuple(items)

    def output_schema_route_field_body(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def output_schema_type_stmt(self, meta, type_name):
        return _with_source_span(model.OutputSchemaSetting(key="type", value=type_name), meta)

    @v_args(meta=True, inline=True)
    def output_schema_note_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="note", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_format_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="format", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_pattern_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="pattern", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_const_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="const", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_ref_stmt(self, meta, ref):
        return _with_source_span(model.OutputSchemaSetting(key="ref", value=ref), meta)

    @v_args(meta=True, inline=True)
    def output_schema_items_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaItems(value=value), meta)

    @v_args(meta=True)
    def output_schema_items_block(self, meta, items):
        return _with_source_span(model.OutputSchemaItems(value=tuple(items)), meta)

    @v_args(meta=True)
    def output_schema_nullable_stmt(self, meta, _items=None):
        return _with_source_span(model.OutputSchemaFlag(key="nullable"), meta)

    @v_args(meta=True)
    def output_schema_required_stmt(self, meta, _items=None):
        return _with_source_span(model.OutputSchemaFlag(key="required"), meta)

    @v_args(meta=True)
    def output_schema_optional_stmt(self, meta, _items=None):
        return _with_source_span(model.OutputSchemaFlag(key="optional"), meta)

    @v_args(meta=True, inline=True)
    def output_schema_variant(self, meta, *children):
        key: str | None = None
        variant_items = children
        if children and isinstance(children[0], str):
            key = children[0]
            variant_items = children[1:]
        return _with_source_span(
            model.OutputSchemaVariant(
                key=key,
                items=tuple(variant_items),
            ),
            meta,
        )

    @v_args(meta=True)
    def output_schema_any_of_block(self, meta, items):
        return _with_source_span(model.OutputSchemaAnyOf(variants=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def output_schema_min_length_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="min_length", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_max_length_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="max_length", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_minimum_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="minimum", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_maximum_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="maximum", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_exclusive_minimum_stmt(self, meta, value):
        return _with_source_span(
            model.OutputSchemaSetting(key="exclusive_minimum", value=value),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_exclusive_maximum_stmt(self, meta, value):
        return _with_source_span(
            model.OutputSchemaSetting(key="exclusive_maximum", value=value),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_multiple_of_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="multiple_of", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_min_items_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="min_items", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_max_items_stmt(self, meta, value):
        return _with_source_span(model.OutputSchemaSetting(key="max_items", value=value), meta)

    @v_args(inline=True)
    def output_schema_identifier(self, value):
        return value

    def output_schema_true(self, _items=None):
        return True

    def output_schema_false(self, _items=None):
        return False

    def output_schema_null(self, _items=None):
        return None

    @v_args(meta=True, inline=True)
    def output_schema_field(self, meta, key, title, items=None):
        return _with_source_span(
            model.OutputSchemaField(
                key=key,
                title=title,
                items=tuple(items) if items is not None else (),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_route_field(self, meta, key, title, items=None):
        return _with_source_span(
            model.OutputSchemaRouteField(
                key=key,
                title=title,
                items=tuple(items) if items is not None else (),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_def(self, meta, key, title, items=None):
        return _with_source_span(
            model.OutputSchemaDef(
                key=key,
                title=title,
                items=tuple(items) if items is not None else (),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_example(self, meta, value):
        return _with_source_span(model.OutputSchemaExample(key="example", value=value), meta)

    @v_args(meta=True, inline=True)
    def output_schema_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def output_schema_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    @v_args(meta=True, inline=True)
    def output_schema_override_field(self, meta, key, title_or_items=None, items=None):
        title: str | None = None
        body_items = title_or_items
        if items is not None:
            title = title_or_items
            body_items = items
        elif isinstance(title_or_items, str):
            title = title_or_items
            body_items = ()
        if body_items is None:
            body_items = ()
        return _with_source_span(
            model.OutputSchemaOverrideField(
                key=key,
                title=title,
                items=tuple(body_items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_override_route_field(self, meta, key, title_or_items=None, items=None):
        title: str | None = None
        body_items = title_or_items
        if items is not None:
            title = title_or_items
            body_items = items
        elif isinstance(title_or_items, str):
            title = title_or_items
            body_items = ()
        if body_items is None:
            body_items = ()
        return _with_source_span(
            model.OutputSchemaOverrideRouteField(
                key=key,
                title=title,
                items=tuple(body_items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_override_def(self, meta, key, title_or_items=None, items=None):
        title: str | None = None
        body_items = title_or_items
        if items is not None:
            title = title_or_items
            body_items = items
        elif isinstance(title_or_items, str):
            title = title_or_items
            body_items = ()
        if body_items is None:
            body_items = ()
        return _with_source_span(
            model.OutputSchemaOverrideDef(
                key=key,
                title=title,
                items=tuple(body_items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_override_example(self, meta, value):
        return _with_source_span(
            model.OutputSchemaOverrideExample(key="example", value=value),
            meta,
        )

    @v_args(meta=True, inline=True)
    def output_schema_route_choice(self, meta, key, title, target_ref):
        return _with_source_span(
            model.OutputSchemaRouteChoice(
                key=key,
                title=title,
                target_ref=target_ref,
            ),
            meta,
        )

    def output_schema_example_object(self, items):
        return model.OutputSchemaExampleObject(entries=tuple(items))

    @v_args(inline=True)
    def output_schema_example_entry(self, key, value):
        return model.OutputSchemaExampleEntry(key=key, value=value)

    def output_schema_example_array(self, items):
        return model.OutputSchemaExampleArray(items=tuple(items))

    @v_args(inline=True)
    def output_schema_example_array_item(self, value):
        return value

    def output_schema_example_true(self, _items=None):
        return True

    def output_schema_example_false(self, _items=None):
        return False

    def output_schema_example_null(self, _items=None):
        return None

    @v_args(meta=True, inline=True)
    def output_schema_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        items = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            items = body
        return _with_source_span(
            model.OutputSchemaDecl(
                name=name,
                title=title,
                items=tuple(items),
                parent_ref=parent_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def io_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def io_body_line(self, value):
        return value

    def io_body(self, items):
        preamble: list[model.ProseLine] = []
        io_items: list[model.IoItem] = []
        items = _flatten_grouped_items(items)
        for item in items:
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if io_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Inputs and outputs prose lines must appear before keyed entries.",
                        hints=(
                            "Move prose lines to the top of the inputs or outputs body or put them inside a titled section.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            io_items.append(item)
        return IoBodyParts(preamble=tuple(preamble), items=tuple(io_items))

    @v_args(meta=True, inline=True)
    def io_section(self, meta, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return _with_source_span(
            model.IoSection(key=key, title=title, items=tuple(section_items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def io_section_ref(self, meta, key, ref):
        return self._io_section_from_ref(model.IoSection, key=key, ref=ref, meta=meta)

    @v_args(meta=True, inline=True)
    def io_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def io_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    @v_args(meta=True, inline=True)
    def io_override_section(self, meta, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return _with_source_span(
            model.OverrideIoSection(
                key=key,
                title=title,
                items=tuple(section_items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def io_override_section_ref(self, meta, key, ref):
        return self._io_section_from_ref(
            model.OverrideIoSection,
            key=key,
            ref=ref,
            meta=meta,
        )

    @v_args(inline=True)
    def output_readable_block(self, value):
        return value

    @v_args(inline=True)
    def output_override_readable_block(self, value):
        return value

    @v_args(inline=True)
    def output_section_block(self, key, title, *parts):
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

    @v_args(inline=True)
    def output_override_section_block(self, key, *parts):
        title, requirement, when_expr, item_schema, row_schema, payload = (
            self._split_readable_override_parts(parts)
        )
        return model.ReadableOverrideBlock(
            kind="section",
            key=key,
            title=title,
            payload=tuple(payload),
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )
