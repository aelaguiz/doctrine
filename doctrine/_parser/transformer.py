from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    DocumentBodyParts,
    IoBodyParts,
    ReadablePayloadParts,
    RenderProfilePart,
    SchemaBodyParts,
    SkillPackageMetadataFieldPart,
    SkillsBodyParts,
    WorkflowBodyParts,
    _body_prose_location,
    _body_prose_value,
    _expand_grouped_inherit,
    _flatten_grouped_items,
    _positioned_body_prose,
    _positioned_render_profile,
    _positioned_schema_item,
    _schema_block_key,
    _schema_item_location,
    _schema_item_value,
    _with_source_span,
)
from doctrine.diagnostics import TransformParseFailure


class ReadableTransformerMixin:
    """Shared readable-block transform helpers for the public parser boundary."""

    def _readable_block(
        self,
        kind: str,
        key: str,
        title: str | None,
        parts: tuple[object, ...],
        *,
        anonymous: bool = False,
    ) -> model.ReadableBlock:
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return model.ReadableBlock(
            kind=kind,
            key=key,
            title=title,
            payload=payload,
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
            anonymous=anonymous,
        )

    def _readable_override_block(
        self,
        kind: str,
        key: str,
        parts: tuple[object, ...],
    ) -> model.DocumentOverrideBlock:
        title, requirement, when_expr, item_schema, row_schema, payload = self._split_readable_override_parts(parts)
        return model.DocumentOverrideBlock(
            kind=kind,
            key=key,
            title=title,
            payload=payload,
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )

    def _split_readable_parts(
        self,
        parts: tuple[object, ...],
    ) -> tuple[
        str | None,
        model.Expr | None,
        model.ReadableInlineSchemaData | None,
        model.ReadableInlineSchemaData | None,
        object,
    ]:
        requirement: str | None = None
        when_expr: model.Expr | None = None
        item_schema: model.ReadableInlineSchemaData | None = None
        row_schema: model.ReadableInlineSchemaData | None = None
        payload: object = ()
        for part in parts:
            if isinstance(part, tuple) and part and part[0] == "requirement":
                requirement = part[1]
                continue
            if isinstance(part, tuple) and part and part[0] == "guard":
                when_expr = part[1]
                continue
            if isinstance(part, ReadablePayloadParts):
                payload = part.payload
                item_schema = part.item_schema
                row_schema = part.row_schema
                continue
            payload = part
        return requirement, when_expr, item_schema, row_schema, payload

    def _split_readable_override_parts(
        self,
        parts: tuple[object, ...],
    ) -> tuple[
        str | None,
        str | None,
        model.Expr | None,
        model.ReadableInlineSchemaData | None,
        model.ReadableInlineSchemaData | None,
        object,
    ]:
        title: str | None = None
        remainder = parts
        if remainder and isinstance(remainder[0], str):
            title = remainder[0]
            remainder = remainder[1:]
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(remainder)
        return title, requirement, when_expr, item_schema, row_schema, payload


class DeclarationTransformerMixin:
    """Shared declaration builders for the public parser boundary."""

    def _skill_package_metadata(
        self,
        fields: tuple[SkillPackageMetadataFieldPart, ...],
    ) -> model.SkillPackageMetadata:
        supported_keys = {"name", "description", "version", "license"}
        values: dict[str, str] = {}
        for field in fields:
            if field.key not in supported_keys:
                supported = ", ".join(sorted(supported_keys))
                raise TransformParseFailure(
                    f"Unknown skill package metadata field: {field.key}",
                    hints=(
                        f"Supported `metadata:` fields are {supported}.",
                    ),
                    line=field.line,
                    column=field.column,
                )
            if field.key in values:
                raise TransformParseFailure(
                    f"Duplicate skill package metadata field: {field.key}",
                    hints=("Keep exactly one value per `metadata:` field.",),
                    line=field.line,
                    column=field.column,
                )
            values[field.key] = field.value
        return model.SkillPackageMetadata(
            name=values.get("name"),
            description=values.get("description"),
            version=values.get("version"),
            license=values.get("license"),
        )

    def _skill_package_host_contract(
        self,
        slots: tuple[model.SkillPackageHostSlotItem, ...],
    ) -> tuple[model.SkillPackageHostSlotItem, ...]:
        seen_keys: dict[str, model.SkillPackageHostSlotItem] = {}
        for slot in slots:
            existing = seen_keys.get(slot.key)
            if existing is not None:
                raise TransformParseFailure(
                    f"Duplicate skill package host slot: {slot.key}",
                    hints=("Keep each `host_contract:` slot key only once.",),
                    line=slot.source_span.line if slot.source_span is not None else None,
                    column=slot.source_span.column if slot.source_span is not None else None,
                )
            seen_keys[slot.key] = slot
        return slots

    def _skill_entry_binds(
        self,
        binds: tuple[model.SkillEntryBind, ...],
    ) -> tuple[model.SkillEntryBind, ...]:
        seen_keys: dict[str, model.SkillEntryBind] = {}
        for bind in binds:
            existing = seen_keys.get(bind.key)
            if existing is not None:
                raise TransformParseFailure(
                    f"Duplicate skill entry bind: {bind.key}",
                    hints=("Keep each `bind:` key only once per skill entry.",),
                    line=bind.source_span.line if bind.source_span is not None else None,
                    column=bind.source_span.column if bind.source_span is not None else None,
                )
            seen_keys[bind.key] = bind
        return binds

    def _agent(self, items, *, abstract: bool, source_span: model.SourceSpan | None = None):
        name = items[0]
        parent_ref: model.NameRef | None = None
        title: str | None = None
        fields_start = 1
        if len(items) > 1 and isinstance(items[1], model.NameRef):
            parent_ref = items[1]
            fields_start = 2
        if not abstract and len(items) > fields_start and isinstance(items[fields_start], str):
            title = items[fields_start]
            fields_start += 1
        fields = _flatten_grouped_items(items[fields_start:])
        return model.Agent(
            name=name,
            title=title,
            fields=fields,
            abstract=abstract,
            parent_ref=parent_ref,
            source_span=source_span,
        )

    def _workflow_slot_value(
        self,
        value: str | model.NameRef,
        body: WorkflowBodyParts | None,
    ) -> model.WorkflowSlotValue:
        if body is None:
            return value
        if isinstance(value, model.NameRef):
            raise ValueError("Authored workflow slot references cannot also define an inline body.")
        return model.WorkflowBody(
            title=value,
            preamble=body.preamble,
            items=body.items,
            law=body.law,
        )

    def _skills_value(
        self,
        value: str | model.NameRef,
        body: SkillsBodyParts | None,
    ) -> model.SkillsValue:
        if body is None:
            if isinstance(value, str):
                raise ValueError("Inline skills blocks must define an indented body.")
            return value
        if isinstance(value, model.NameRef):
            raise ValueError("Skills references cannot also define an inline body.")
        return model.SkillsBody(title=value, preamble=body.preamble, items=body.items)

    def _io_body(self, title: str, body: IoBodyParts) -> model.IoBody:
        return model.IoBody(title=title, preamble=body.preamble, items=body.items)

    def _review_decl(
        self,
        items,
        *,
        abstract: bool,
        family: bool,
        source_span: model.SourceSpan | None = None,
    ):
        name = items[0]
        parent_ref: model.NameRef | None = None
        title = items[1]
        review_body = items[2]
        if len(items) == 4:
            parent_ref = items[1]
            title = items[2]
            review_body = items[3]
        return model.ReviewDecl(
            name=name,
            body=model.ReviewBody(title=title, items=review_body.items),
            abstract=abstract,
            parent_ref=parent_ref,
            family=family,
            source_span=source_span,
        )


class SchemaDocumentTransformerMixin:
    """Shared schema and document lowering for the public parser boundary."""

    @v_args(meta=True, inline=True)
    def schema_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        schema_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            schema_body = body
        return _with_source_span(
            model.SchemaDecl(
                name=name,
                body=model.SchemaBody(
                    title=title,
                    preamble=schema_body.preamble,
                    items=schema_body.items,
                ),
                parent_ref=parent_ref,
                render_profile_ref=schema_body.render_profile_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def schema_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def schema_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def schema_render_profile_stmt(self, meta, ref):
        return _positioned_render_profile(meta, ref)

    def schema_body(self, items):
        preamble: list[model.ProseLine] = []
        schema_items: list[model.SchemaItem] = []
        render_profile_ref: model.NameRef | None = None
        items = _flatten_grouped_items(items)
        block_hints = {
            "sections": "Use exactly one of `sections:`, `inherit sections`, or `override sections:`.",
            "gates": "Use exactly one of `gates:`, `inherit gates`, or `override gates:`.",
            "artifacts": "Use exactly one of `artifacts:`, `inherit artifacts`, or `override artifacts:`.",
            "groups": "Use exactly one of `groups:`, `inherit groups`, or `override groups:`.",
        }
        block_claims: dict[str, str] = {}
        for item in items:
            if isinstance(item, RenderProfilePart):
                if render_profile_ref is not None:
                    raise TransformParseFailure(
                        "Schema declarations may define `render_profile:` only once.",
                        hints=("Keep exactly one `render_profile:` attachment per schema declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                render_profile_ref = item.ref
                continue
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if schema_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Schema prose lines must appear before typed schema blocks.",
                        hints=(
                            "Move prose lines to the top of the schema body or put them inside a schema section or gate body.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            schema_item = _schema_item_value(item)
            line, column = _schema_item_location(item)
            if isinstance(schema_item, model.InheritItem):
                if schema_item.key in block_hints and block_claims.get(schema_item.key) == "block":
                    raise TransformParseFailure(
                        f"Schema declarations may account for `{schema_item.key}` only once.",
                        hints=(block_hints[schema_item.key],),
                        line=line,
                        column=column,
                    )
                if schema_item.key in block_hints:
                    block_claims.setdefault(schema_item.key, "inherit")
                schema_items.append(schema_item)
                continue
            block_key = _schema_block_key(schema_item)
            if block_key is not None:
                if block_key in block_claims:
                    raise TransformParseFailure(
                        f"Schema declarations may account for `{block_key}` only once.",
                        hints=(block_hints[block_key],),
                        line=line,
                        column=column,
                    )
                block_claims[block_key] = "block"
            schema_items.append(schema_item)
        return SchemaBodyParts(
            preamble=tuple(preamble),
            items=tuple(schema_items),
            render_profile_ref=render_profile_ref,
        )

    @v_args(meta=True)
    def schema_sections_block(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaSectionsBlock(items=tuple(items)), meta),
        )

    @v_args(meta=True)
    def schema_gates_block(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaGatesBlock(items=tuple(items)), meta),
        )

    @v_args(meta=True)
    def schema_artifacts_block(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaArtifactsBlock(items=tuple(items)), meta),
        )

    @v_args(meta=True)
    def schema_groups_block(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaGroupsBlock(items=tuple(items)), meta),
        )

    @v_args(meta=True, inline=True)
    def schema_section_item(self, meta, key, title, body=None):
        return _with_source_span(
            model.SchemaSection(key=key, title=title, body=tuple(body or ())),
            meta,
        )

    def schema_section_body(self, items):
        return tuple(items[0])

    @v_args(meta=True, inline=True)
    def schema_gate_item(self, meta, key, title, body=None):
        return _with_source_span(
            model.SchemaGate(key=key, title=title, body=tuple(body or ())),
            meta,
        )

    def schema_gate_body(self, items):
        return tuple(items[0])

    @v_args(meta=True, inline=True)
    def schema_artifact_item(self, meta, key, title, body=None):
        refs = tuple(body or ())
        if len(refs) != 1:
            raise TransformParseFailure(
                f"Schema artifact `{key}` must define exactly one `ref:` entry.",
                hints=("Define one `ref:` line inside each schema artifact entry.",),
            )
        return _with_source_span(
            model.SchemaArtifact(key=key, title=title, ref=refs[0]),
            meta,
        )

    def schema_artifact_body(self, items):
        return tuple(items)

    def schema_artifact_ref(self, items):
        return items[0]

    @v_args(meta=True, inline=True)
    def schema_group_item(self, meta, key, title, body=None):
        return _with_source_span(
            model.SchemaGroup(key=key, title=title, members=tuple(body or ())),
            meta,
        )

    def schema_group_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def schema_group_member(self, key):
        return key

    @v_args(meta=True, inline=True)
    def schema_inherit(self, meta, key):
        return _positioned_schema_item(meta, _with_source_span(model.InheritItem(key=key), meta))

    @v_args(meta=True, inline=True)
    def schema_inherit_group(self, meta, keys=()):
        return [
            _positioned_schema_item(meta, item)
            for item in _expand_grouped_inherit(
                meta,
                keys,
                model.InheritItem,
                allowed_keys=("sections", "gates", "artifacts", "groups"),
            )
        ]

    @v_args(meta=True)
    def schema_override_sections(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaOverrideSectionsBlock(items=tuple(items)), meta),
        )

    @v_args(meta=True)
    def schema_override_gates(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaOverrideGatesBlock(items=tuple(items)), meta),
        )

    @v_args(meta=True)
    def schema_override_artifacts(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaOverrideArtifactsBlock(items=tuple(items)), meta),
        )

    @v_args(meta=True)
    def schema_override_groups(self, meta, items):
        return _positioned_schema_item(
            meta,
            _with_source_span(model.SchemaOverrideGroupsBlock(items=tuple(items)), meta),
        )

    def schema_block_key_sections(self, _items):
        return "sections"

    def schema_block_key_gates(self, _items):
        return "gates"

    def schema_block_key_artifacts(self, _items):
        return "artifacts"

    def schema_block_key_groups(self, _items):
        return "groups"

    @v_args(meta=True, inline=True)
    def document_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        document_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            document_body = body
        return _with_source_span(
            model.DocumentDecl(
                name=name,
                body=model.DocumentBody(
                    title=title,
                    preamble=document_body.preamble,
                    items=document_body.items,
                ),
                parent_ref=parent_ref,
                render_profile_ref=document_body.render_profile_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def document_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def document_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def document_render_profile_stmt(self, meta, ref):
        return _positioned_render_profile(meta, ref)

    def document_body(self, items):
        preamble: list[model.ProseLine] = []
        document_items: list[model.DocumentItem] = []
        render_profile_ref: model.NameRef | None = None
        items = _flatten_grouped_items(items)
        for item in items:
            if isinstance(item, RenderProfilePart):
                if render_profile_ref is not None:
                    raise TransformParseFailure(
                        "Document declarations may define `render_profile:` only once.",
                        hints=("Keep exactly one `render_profile:` attachment per document declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                render_profile_ref = item.ref
                continue
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if document_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Document prose lines must appear before keyed document blocks.",
                        hints=(
                            "Move prose lines to the top of the document body or put them inside a document block.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            document_items.append(item)
        return DocumentBodyParts(
            preamble=tuple(preamble),
            items=tuple(document_items),
            render_profile_ref=render_profile_ref,
        )

    @v_args(inline=True)
    def document_readable_block(self, value):
        return value

    @v_args(inline=True)
    def document_override_block(self, value):
        return value

    @v_args(meta=True, inline=True)
    def document_section_sugar(self, meta, key, title, items):
        return _with_source_span(
            model.ReadableBlock(
                kind="section",
                key=key,
                title=title,
                payload=tuple(items),
                legacy_section=True,
            ),
            meta,
        )

    def document_section_body(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def document_section_block(self, meta, key, title, *parts):
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

    @v_args(meta=True, inline=True)
    def document_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def document_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    @v_args(meta=True, inline=True)
    def document_override_section_block(self, meta, key, *parts):
        title, requirement, when_expr, item_schema, row_schema, payload = self._split_readable_override_parts(parts)
        return _with_source_span(
            model.DocumentOverrideBlock(
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
