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
    RenderProfilePart,
    TrustSurfacePart,
    _body_prose_location,
    _body_prose_value,
    _meta_line_column,
    _positioned_body_prose,
    _positioned_input_structure,
    _positioned_render_profile,
    _positioned_trust_surface,
)
from doctrine.diagnostics import TransformParseFailure


class IoTransformerMixin:
    """Shared inputs, outputs, and IO-body lowering for the public parser boundary."""

    @v_args(inline=True)
    def inputs_inline_field(self, title, items):
        return model.InputsField(title=title, value=tuple(items))

    @v_args(inline=True)
    def inputs_ref_field(self, ref):
        return model.InputsField(title=None, value=ref)

    @v_args(inline=True)
    def inputs_patch_field(self, parent_ref, title, body):
        return model.InputsField(
            title=title,
            value=self._io_body(title, body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def outputs_inline_field(self, title, items):
        return model.OutputsField(title=title, value=tuple(items))

    @v_args(inline=True)
    def outputs_ref_field(self, ref):
        return model.OutputsField(title=None, value=ref)

    @v_args(inline=True)
    def outputs_patch_field(self, parent_ref, title, body):
        return model.OutputsField(
            title=title,
            value=self._io_body(title, body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def inputs_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return model.InputsDecl(
            name=name,
            body=self._io_body(title, io_body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def input_decl(self, name, title, body):
        return model.InputDecl(
            name=name,
            title=title,
            items=body.items,
            structure=body.structure,
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

    @v_args(inline=True)
    def input_source_decl(self, name, title, items):
        return model.InputSourceDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def output_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        output_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            output_body = body
        return model.OutputDecl(
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
        )

    @v_args(inline=True)
    def output_body_line(self, value):
        return value

    def output_body(self, items):
        record_items: list[model.OutputAuthoredItem] = []
        schema: model.OutputSchemaConfig | None = None
        structure: model.OutputStructureConfig | None = None
        render_profile_ref: model.NameRef | None = None
        trust_surface: tuple[model.TrustSurfaceItem, ...] = ()
        schema_mode: str | None = None
        structure_mode: str | None = None
        render_profile_mode: str | None = None
        trust_surface_mode: str | None = None
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
                continue
            if isinstance(item, model.InheritItem):
                if item.key == "schema":
                    if schema_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `schema:` only once.",
                            hints=("Keep exactly one `schema:` attachment per output declaration.",),
                        )
                    schema_mode = "inherit"
                    continue
                if item.key == "structure":
                    if structure_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `structure:` only once.",
                            hints=("Keep exactly one `structure:` attachment per output declaration.",),
                        )
                    structure_mode = "inherit"
                    continue
                if item.key == "render_profile":
                    if render_profile_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `render_profile:` only once.",
                            hints=("Keep exactly one `render_profile:` attachment per output declaration.",),
                        )
                    render_profile_mode = "inherit"
                    continue
                if item.key == "trust_surface":
                    if trust_surface_mode is not None:
                        raise TransformParseFailure(
                            "Output declarations may define `trust_surface` only once.",
                            hints=("Keep exactly one `trust_surface:` block per output declaration.",),
                        )
                    trust_surface_mode = "inherit"
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

    @v_args(inline=True)
    def output_inherit(self, key):
        return model.InheritItem(key=key)

    def output_record_item_body(self, items):
        return tuple(items[0])

    @v_args(meta=True, inline=True)
    def output_record_keyed_item(self, meta, key, head, body=None):
        if isinstance(head, str) and body is not None:
            line, column = _meta_line_column(meta)
            return OutputRecordSectionPart(
                section=model.RecordSection(key=key, title=head, items=tuple(body)),
                line=line,
                column=column,
            )
        return model.RecordScalar(key=key, value=head, body=None if body is None else tuple(body))

    @v_args(meta=True, inline=True)
    def output_override_keyed_item(self, meta, key, head, body=None):
        if isinstance(head, str) and body is not None:
            line, column = _meta_line_column(meta)
            return OutputRecordSectionPart(
                section=model.OutputOverrideRecordSection(
                    key=key,
                    title=head,
                    items=tuple(body),
                ),
                line=line,
                column=column,
            )
        return model.OutputOverrideRecordScalar(
            key=key,
            value=head,
            body=None if body is None else tuple(body),
        )

    @v_args(inline=True)
    def output_record_ref_item(self, ref, body=None):
        return model.RecordRef(ref=ref, body=None if body is None else tuple(body))

    @v_args(inline=True)
    def guarded_output_section(self, key, title, when_expr, items):
        return model.GuardedOutputSection(
            key=key,
            title=title,
            when_expr=when_expr,
            items=tuple(items),
        )

    @v_args(inline=True)
    def output_override_guarded_section(self, key, title, when_expr, items):
        return model.OutputOverrideGuardedOutputSection(
            key=key,
            title=title,
            when_expr=when_expr,
            items=tuple(items),
        )

    @v_args(inline=True)
    def guarded_output_scalar_item(self, key, head, when_expr, body=None):
        return model.GuardedOutputScalar(
            key=key,
            value=head,
            when_expr=when_expr,
            body=None if body is None else tuple(body),
        )

    @v_args(inline=True)
    def output_override_guarded_scalar_item(self, key, head, when_expr, body=None):
        return model.OutputOverrideGuardedOutputScalar(
            key=key,
            value=head,
            when_expr=when_expr,
            body=None if body is None else tuple(body),
        )

    @v_args(meta=True)
    def trust_surface_block(self, meta, items):
        return _positioned_trust_surface(meta, tuple(items))

    @v_args(meta=True)
    def output_override_trust_surface_block(self, meta, items):
        return _positioned_trust_surface(meta, tuple(items), override=True)

    @v_args(inline=True)
    def trust_surface_item(self, path, when_expr=None):
        return model.TrustSurfaceItem(path=tuple(path), when_expr=when_expr)

    @v_args(inline=True)
    def trust_surface_when(self, expr):
        return expr

    @v_args(inline=True)
    def outputs_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return model.OutputsDecl(
            name=name,
            body=self._io_body(title, io_body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def output_target_decl(self, name, title, items):
        return model.OutputTargetDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def output_shape_decl(self, name, title, items):
        return model.OutputShapeDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def json_schema_decl(self, name, title, items):
        return model.JsonSchemaDecl(name=name, title=title, items=tuple(items))

    @v_args(meta=True, inline=True)
    def io_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def io_body_line(self, value):
        return value

    def io_body(self, items):
        preamble: list[model.ProseLine] = []
        io_items: list[model.IoItem] = []
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

    @v_args(inline=True)
    def io_section(self, key, title, items):
        return model.RecordSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def io_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def io_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideIoSection(
            key=key,
            title=title,
            items=tuple(section_items),
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
