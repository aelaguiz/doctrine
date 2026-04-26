from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True, slots=True)
class _EdgeKindPart:
    value: str
    line: int | None
    column: int | None


@dataclass(frozen=True, slots=True)
class _EdgeWhyPart:
    value: str
    line: int | None
    column: int | None


@dataclass(frozen=True, slots=True)
class _RepeatOverPart:
    ref: model.NameRef
    line: int | None
    column: int | None


@dataclass(frozen=True, slots=True)
class _RepeatOrderPart:
    value: str
    line: int | None
    column: int | None


@dataclass(frozen=True, slots=True)
class _RepeatWhyPart:
    value: str
    line: int | None
    column: int | None


@dataclass(frozen=True, slots=True)
class _ChangedWorkflowAllowPart:
    value: str
    line: int | None
    column: int | None


@dataclass(frozen=True, slots=True)
class _ChangedWorkflowRequirePart:
    value: str
    line: int | None
    column: int | None


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

    @v_args(meta=True, inline=True)
    def package_host_receipt_slot_ref(self, meta, key, receipt_ref):
        return _with_source_span(
            model.ReceiptHostSlotRef(key=key, receipt_ref=receipt_ref),
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

    @v_args(meta=True, inline=True)
    def receipt_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        decl_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            decl_body = body
        return _with_source_span(
            model.ReceiptDecl(
                name=name,
                title=title,
                items=tuple(decl_body),
                parent_ref=parent_ref,
            ),
            meta,
        )

    def receipt_decl_body(self, items):
        return _flatten_grouped_items(items)

    @v_args(meta=True, inline=True)
    def receipt_decl_field(self, meta, key, type_value):
        type_ref, list_element = type_value
        return _with_source_span(
            model.ReceiptDeclField(
                key=key,
                type_ref=type_ref,
                list_element=list_element,
            ),
            meta,
        )

    @v_args(inline=True)
    def receipt_decl_field_type(self, value):
        if isinstance(value, tuple):
            return value
        return (value, False)

    @v_args(inline=True)
    def receipt_decl_field_list_type(self, name_ref):
        return (name_ref, True)

    @v_args(meta=True, inline=True)
    def receipt_decl_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def receipt_decl_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    @v_args(meta=True, inline=True)
    def receipt_decl_override(self, meta, key, type_value):
        type_ref, list_element = type_value
        return _with_source_span(
            model.ReceiptDeclOverride(
                key=key,
                type_ref=type_ref,
                list_element=list_element,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def receipt_decl_route_field(self, meta, key, title, *choices):
        return _with_source_span(
            model.ReceiptDeclRouteField(
                key=key,
                title=title,
                choices=tuple(choices),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def receipt_route_choice(self, meta, key, title, target):
        return _with_source_span(
            model.ReceiptRouteChoice(key=key, title=title, target=target),
            meta,
        )

    @v_args(meta=True, inline=True)
    def receipt_route_target_stage(self, meta, ref):
        return _with_source_span(
            model.ReceiptRouteStageTarget(stage_ref=ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def receipt_route_target_flow(self, meta, ref):
        return _with_source_span(
            model.ReceiptRouteFlowTarget(flow_ref=ref),
            meta,
        )

    @v_args(meta=True)
    def receipt_route_target_human(self, meta, _children=None):
        return _with_source_span(
            model.ReceiptRouteSentinelTarget(sentinel="human"),
            meta,
        )

    @v_args(meta=True)
    def receipt_route_target_external(self, meta, _children=None):
        return _with_source_span(
            model.ReceiptRouteSentinelTarget(sentinel="external"),
            meta,
        )

    @v_args(meta=True)
    def receipt_route_target_terminal(self, meta, _children=None):
        return _with_source_span(
            model.ReceiptRouteSentinelTarget(sentinel="terminal"),
            meta,
        )

    # Stage declarations -------------------------------------------------

    @v_args(meta=True, inline=True)
    def stage_decl(self, meta, name, title, body):
        return _with_source_span(
            model.StageDecl(
                name=name,
                title=title,
                items=tuple(body),
            ),
            meta,
        )

    def stage_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def stage_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def stage_owner_stmt(self, meta, ref):
        return _with_source_span(
            model.StageOwnerItem(owner_ref=ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def stage_lane_stmt(self, meta, ref):
        return _with_source_span(
            model.StageLaneItem(lane_ref=ref),
            meta,
        )

    @v_args(meta=True)
    def stage_supports_block(self, meta, items):
        refs = tuple(items)
        return _with_source_span(
            model.StageSupportsItem(skill_refs=refs),
            meta,
        )

    @v_args(inline=True)
    def stage_supports_item(self, ref):
        return ref

    @v_args(meta=True)
    def stage_applies_to_block(self, meta, items):
        refs = tuple(items)
        return _with_source_span(
            model.StageAppliesToItem(flow_refs=refs),
            meta,
        )

    @v_args(inline=True)
    def stage_applies_to_item(self, ref):
        return ref

    @v_args(meta=True)
    def stage_inputs_block(self, meta, items):
        return _with_source_span(
            model.StageInputsItem(entries=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def stage_input_item(self, meta, key, ref):
        return _with_source_span(
            model.StageInputEntry(key=key, type_ref=ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def stage_emits_stmt(self, meta, ref):
        return _with_source_span(
            model.StageEmitsItem(receipt_ref=ref),
            meta,
        )

    @v_args(meta=True)
    def stage_forbidden_outputs_block(self, meta, items):
        return _with_source_span(
            model.StageForbiddenOutputsItem(values=tuple(items)),
            meta,
        )

    @v_args(inline=True)
    def stage_forbidden_outputs_item(self, value):
        return value

    @v_args(meta=True, inline=True)
    def stage_scalar_stmt(self, meta, key, value):
        return _with_source_span(
            model.StageScalarItem(key=key, value=value),
            meta,
        )

    def stage_scalar_key_id(self, _children):
        return "id"

    def stage_scalar_key_intent(self, _children):
        return "intent"

    def stage_scalar_key_durable_target(self, _children):
        return "durable_target"

    def stage_scalar_key_durable_evidence(self, _children):
        return "durable_evidence"

    def stage_scalar_key_advance_condition(self, _children):
        return "advance_condition"

    def stage_scalar_key_risk_guarded(self, _children):
        return "risk_guarded"

    def stage_scalar_key_checkpoint(self, _children):
        return "checkpoint"

    # Top-level skill_flow declarations ----------------------------------

    @v_args(meta=True, inline=True)
    def skill_flow_decl_bare(self, meta, name, title):
        return _with_source_span(
            model.SkillFlowDecl(name=name, title=title, items=()),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_decl_body(self, meta, name, title, body):
        return _with_source_span(
            model.SkillFlowDecl(name=name, title=title, items=tuple(body)),
            meta,
        )

    def skill_flow_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def skill_flow_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def skill_flow_intent_stmt(self, meta, value):
        return _with_source_span(
            model.SkillFlowIntentItem(value=value),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_start_stmt(self, meta, ref):
        return _with_source_span(
            model.SkillFlowStartItem(node_ref=ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_approve_stmt(self, meta, ref):
        return _with_source_span(
            model.SkillFlowApproveItem(flow_ref=ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_edge_stmt(self, meta, source_ref, target_ref, body):
        kind = "normal"
        why: str | None = None
        route: model.SkillFlowEdgeRouteRef | None = None
        when: model.SkillFlowEdgeWhenRef | None = None
        seen_kind = False
        seen_why = False
        seen_route = False
        seen_when = False
        for item in body:
            if isinstance(item, _EdgeKindPart):
                if seen_kind:
                    raise TransformParseFailure(
                        "Skill flow edges may declare `kind:` only once.",
                        hints=("Keep one `kind:` per `edge` block.",),
                        line=item.line,
                        column=item.column,
                    )
                kind = item.value
                seen_kind = True
                continue
            if isinstance(item, _EdgeWhyPart):
                if seen_why:
                    raise TransformParseFailure(
                        "Skill flow edges may declare `why:` only once.",
                        hints=("Keep one `why:` per `edge` block.",),
                        line=item.line,
                        column=item.column,
                    )
                why = item.value
                seen_why = True
                continue
            if isinstance(item, model.SkillFlowEdgeRouteRef):
                if seen_route:
                    line = item.source_span.line if item.source_span else None
                    column = item.source_span.column if item.source_span else None
                    raise TransformParseFailure(
                        "Skill flow edges may declare `route:` only once.",
                        hints=("Keep one `route:` per `edge` block.",),
                        line=line,
                        column=column,
                    )
                route = item
                seen_route = True
                continue
            if isinstance(item, model.SkillFlowEdgeWhenRef):
                if seen_when:
                    line = item.source_span.line if item.source_span else None
                    column = item.source_span.column if item.source_span else None
                    raise TransformParseFailure(
                        "Skill flow edges may declare `when:` only once.",
                        hints=("Keep one `when:` per `edge` block.",),
                        line=line,
                        column=column,
                    )
                when = item
                seen_when = True
                continue
        if why is None:
            line, column = _meta_line_column(meta)
            raise TransformParseFailure(
                "Skill flow edges require a `why:` reason.",
                hints=("Add a `why: \"...\"` line under the `edge` block.",),
                line=line,
                column=column,
            )
        return _with_source_span(
            model.SkillFlowEdgeItem(
                source_ref=source_ref,
                target_ref=target_ref,
                why=why,
                kind=kind,
                route=route,
                when=when,
            ),
            meta,
        )

    def skill_flow_edge_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def skill_flow_edge_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def skill_flow_edge_route_stmt(self, meta, ref):
        # The author writes `route: ReceiptRef.route_field.choice`. The grammar
        # parses one `name_ref`; the trailing two dotted parts are the route
        # field key and the choice key. The receipt ref keeps the leading
        # module-dotted path when present.
        if not ref.module_parts or len(ref.module_parts) < 2:
            line = ref.source_span.line if ref.source_span else None
            column = ref.source_span.column if ref.source_span else None
            raise TransformParseFailure(
                "Skill flow edge `route:` must be `ReceiptRef.route_field.choice`.",
                hints=(
                    "Use `route: <ReceiptRef>.<route_field>.<choice>` so the "
                    "binding names a receipt route choice.",
                ),
                line=line,
                column=column,
            )
        receipt_ref = model.NameRef(
            module_parts=ref.module_parts[:-2],
            declaration_name=ref.module_parts[-2],
            source_span=ref.source_span,
        )
        route_field_key = ref.module_parts[-1]
        choice_key = ref.declaration_name
        return _with_source_span(
            model.SkillFlowEdgeRouteRef(
                receipt_ref=receipt_ref,
                route_field_key=route_field_key,
                choice_key=choice_key,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_edge_kind_stmt(self, meta, value):
        line, column = _meta_line_column(meta)
        return _EdgeKindPart(value=value, line=line, column=column)

    @v_args(meta=True, inline=True)
    def skill_flow_edge_when_stmt(self, meta, ref):
        # `when:` accepts only `EnumName.member`. Lower it into a typed
        # branch ref where the last dotted segment is the enum member key
        # and the remainder names the enum declaration.
        if not ref.module_parts:
            raise TransformParseFailure(
                "Skill flow `when:` must be a dotted `EnumName.member` ref.",
                hints=(
                    "Use `when: <EnumName>.<member>` so the branch resolves to "
                    "a declared enum member.",
                ),
                line=ref.source_span.line if ref.source_span else None,
                column=ref.source_span.column if ref.source_span else None,
            )
        enum_ref = model.NameRef(
            module_parts=ref.module_parts[:-1],
            declaration_name=ref.module_parts[-1],
            source_span=ref.source_span,
        )
        return _with_source_span(
            model.SkillFlowEdgeWhenRef(
                enum_ref=enum_ref,
                member_key=ref.declaration_name,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_edge_why_stmt(self, meta, value):
        line, column = _meta_line_column(meta)
        return _EdgeWhyPart(value=value, line=line, column=column)

    @v_args(meta=True, inline=True)
    def skill_flow_repeat_stmt(self, meta, name, target_flow_ref, body):
        over_ref: model.NameRef | None = None
        order: str | None = None
        why: str | None = None
        seen_over = False
        seen_order = False
        seen_why = False
        for item in body:
            if isinstance(item, _RepeatOverPart):
                if seen_over:
                    raise TransformParseFailure(
                        "Skill flow repeats may declare `over:` only once.",
                        hints=("Keep one `over:` per `repeat` block.",),
                        line=item.line,
                        column=item.column,
                    )
                over_ref = item.ref
                seen_over = True
                continue
            if isinstance(item, _RepeatOrderPart):
                if seen_order:
                    raise TransformParseFailure(
                        "Skill flow repeats may declare `order:` only once.",
                        hints=("Keep one `order:` per `repeat` block.",),
                        line=item.line,
                        column=item.column,
                    )
                order = item.value
                seen_order = True
                continue
            if isinstance(item, _RepeatWhyPart):
                if seen_why:
                    raise TransformParseFailure(
                        "Skill flow repeats may declare `why:` only once.",
                        hints=("Keep one `why:` per `repeat` block.",),
                        line=item.line,
                        column=item.column,
                    )
                why = item.value
                seen_why = True
                continue
        line, column = _meta_line_column(meta)
        if over_ref is None:
            raise TransformParseFailure(
                f"Skill flow repeat `{name}` is missing required `over:`.",
                hints=("Add `over: <Enum|Table|Schema>` under `repeat`.",),
                line=line,
                column=column,
            )
        if order is None:
            raise TransformParseFailure(
                f"Skill flow repeat `{name}` is missing required `order:`.",
                hints=("Add `order: serial`, `order: parallel`, or `order: unspecified`.",),
                line=line,
                column=column,
            )
        if why is None:
            raise TransformParseFailure(
                f"Skill flow repeat `{name}` is missing required `why:`.",
                hints=("Add `why: \"...\"` under the `repeat` block.",),
                line=line,
                column=column,
            )
        return _with_source_span(
            model.SkillFlowRepeatItem(
                name=name,
                target_flow_ref=target_flow_ref,
                over_ref=over_ref,
                order=order,
                why=why,
            ),
            meta,
        )

    def skill_flow_repeat_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def skill_flow_repeat_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def skill_flow_repeat_over_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return _RepeatOverPart(ref=ref, line=line, column=column)

    @v_args(meta=True, inline=True)
    def skill_flow_repeat_order_stmt(self, meta, value):
        line, column = _meta_line_column(meta)
        return _RepeatOrderPart(value=value, line=line, column=column)

    @v_args(meta=True, inline=True)
    def skill_flow_repeat_why_stmt(self, meta, value):
        line, column = _meta_line_column(meta)
        return _RepeatWhyPart(value=value, line=line, column=column)

    @v_args(meta=True, inline=True)
    def skill_flow_variation_stmt(self, meta, name, title, body=None):
        safe_when: model.SkillFlowEdgeWhenRef | None = None
        if body is not None:
            for item in body:
                if isinstance(item, model.SkillFlowEdgeWhenRef):
                    if safe_when is not None:
                        line = item.source_span.line if item.source_span else None
                        column = item.source_span.column if item.source_span else None
                        raise TransformParseFailure(
                            "Skill flow variations may declare `safe_when:` only once.",
                            hints=("Keep one `safe_when:` per `variation` block.",),
                            line=line,
                            column=column,
                        )
                    safe_when = item
        return _with_source_span(
            model.SkillFlowVariationItem(
                name=name,
                title=title,
                safe_when=safe_when,
            ),
            meta,
        )

    def skill_flow_variation_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def skill_flow_variation_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def skill_flow_variation_safe_when_stmt(self, meta, ref):
        if not ref.module_parts:
            raise TransformParseFailure(
                "Skill flow `safe_when:` must be a dotted `EnumName.member` ref.",
                hints=(
                    "Use `safe_when: <EnumName>.<member>` so the branch resolves "
                    "to a declared enum member.",
                ),
                line=ref.source_span.line if ref.source_span else None,
                column=ref.source_span.column if ref.source_span else None,
            )
        enum_ref = model.NameRef(
            module_parts=ref.module_parts[:-1],
            declaration_name=ref.module_parts[-1],
            source_span=ref.source_span,
        )
        return _with_source_span(
            model.SkillFlowEdgeWhenRef(
                enum_ref=enum_ref,
                member_key=ref.declaration_name,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_unsafe_stmt(self, meta, name, title):
        return _with_source_span(
            model.SkillFlowUnsafeItem(name=name, title=title),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skill_flow_changed_workflow_stmt(self, meta, body):
        allow_provisional_flow = False
        requires: list[str] = []
        seen_requires: set[str] = set()
        line, column = _meta_line_column(meta)
        for item in body:
            if isinstance(item, _ChangedWorkflowAllowPart):
                if item.value != "provisional_flow":
                    raise TransformParseFailure(
                        f"Skill flow `changed_workflow:` only allows `provisional_flow`, got `{item.value}`.",
                        hints=("Use `allow provisional_flow` exactly.",),
                        line=item.line,
                        column=item.column,
                    )
                if allow_provisional_flow:
                    raise TransformParseFailure(
                        "Skill flow `changed_workflow:` may declare `allow provisional_flow` only once.",
                        hints=("Keep one `allow provisional_flow` line per block.",),
                        line=item.line,
                        column=item.column,
                    )
                allow_provisional_flow = True
                continue
            if isinstance(item, _ChangedWorkflowRequirePart):
                if item.value in seen_requires:
                    raise TransformParseFailure(
                        f"Skill flow `changed_workflow:` declares `require {item.value}` more than once.",
                        hints=("List each required field once per block.",),
                        line=item.line,
                        column=item.column,
                    )
                seen_requires.add(item.value)
                requires.append(item.value)
                continue
        return _with_source_span(
            model.SkillFlowChangedWorkflowItem(
                allow_provisional_flow=allow_provisional_flow,
                requires=tuple(requires),
            ),
            meta,
        )

    def skill_flow_changed_workflow_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def skill_flow_changed_workflow_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def skill_flow_changed_workflow_allow_stmt(self, meta, value):
        line, column = _meta_line_column(meta)
        return _ChangedWorkflowAllowPart(value=value, line=line, column=column)

    @v_args(meta=True, inline=True)
    def skill_flow_changed_workflow_require_stmt(self, meta, value):
        line, column = _meta_line_column(meta)
        return _ChangedWorkflowRequirePart(value=value, line=line, column=column)

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
