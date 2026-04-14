from __future__ import annotations

from dataclasses import dataclass

from doctrine import model


@dataclass(slots=True, frozen=True)
class WorkflowBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.WorkflowItem, ...]
    law: model.LawBody | None = None


@dataclass(slots=True, frozen=True)
class SkillsBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.SkillsItem, ...]


@dataclass(slots=True, frozen=True)
class IoBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.IoItem, ...]


@dataclass(slots=True, frozen=True)
class InputBodyParts:
    items: tuple[model.RecordItem, ...]
    structure: model.InputStructureConfig | None


@dataclass(slots=True, frozen=True)
class InputStructurePart:
    config: model.InputStructureConfig
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class OutputBodyParts:
    items: tuple[model.OutputRecordItem, ...]
    schema: model.OutputSchemaConfig | None
    structure: model.OutputStructureConfig | None
    render_profile_ref: model.NameRef | None
    trust_surface: tuple[model.TrustSurfaceItem, ...]


@dataclass(slots=True, frozen=True)
class OutputSchemaPart:
    config: model.OutputSchemaConfig
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class OutputStructurePart:
    config: model.OutputStructureConfig
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class OutputRecordSectionPart:
    section: model.RecordSection
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class BodyProsePart:
    value: model.ProseLine
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class RenderProfilePart:
    ref: model.NameRef
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class SchemaItemPart:
    item: model.SchemaItem
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class TrustSurfacePart:
    items: tuple[model.TrustSurfaceItem, ...]
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class ReviewBodyParts:
    items: tuple[model.ReviewItem, ...]


@dataclass(slots=True, frozen=True)
class FinalOutputOutputPart:
    ref: model.NameRef
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class FinalOutputReviewFieldsPart:
    config: model.ReviewFieldsConfig
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class FinalOutputBodyParts:
    output_ref: model.NameRef
    review_fields: model.ReviewFieldsConfig | None = None


@dataclass(slots=True, frozen=True)
class RouteOnlyBodyParts:
    facts_ref: model.NameRef | None = None
    when_exprs: tuple[model.Expr, ...] = ()
    current_none: bool = False
    handoff_output_ref: model.NameRef | None = None
    guarded: tuple[model.RouteOnlyGuard, ...] = ()
    routes: tuple[model.RouteOnlyRoute, ...] = ()


@dataclass(slots=True, frozen=True)
class GroundingBodyParts:
    source_ref: model.NameRef | None = None
    target: str | None = None
    policy_items: tuple[model.GroundingPolicyItem, ...] = ()


@dataclass(slots=True, frozen=True)
class AnalysisBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.AnalysisItem, ...]
    render_profile_ref: model.NameRef | None = None


@dataclass(slots=True, frozen=True)
class DecisionBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.DecisionItem, ...]
    render_profile_ref: model.NameRef | None = None


@dataclass(slots=True, frozen=True)
class DecisionItemPart:
    item: model.DecisionItem
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class SkillPackageMetadataFieldPart:
    key: str
    value: str
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class SkillPackageMetadataBlockPart:
    fields: tuple[SkillPackageMetadataFieldPart, ...]
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class SkillPackageBodyParts:
    items: tuple[model.RecordItem, ...]
    metadata: model.SkillPackageMetadata


@dataclass(slots=True, frozen=True)
class SchemaBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.SchemaItem, ...]
    render_profile_ref: model.NameRef | None = None


@dataclass(slots=True, frozen=True)
class DocumentBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.DocumentItem, ...]
    render_profile_ref: model.NameRef | None = None


@dataclass(slots=True, frozen=True)
class ReadablePayloadParts:
    payload: object
    item_schema: model.ReadableInlineSchemaData | None = None
    row_schema: model.ReadableInlineSchemaData | None = None


@dataclass(slots=True, frozen=True)
class WorkflowLawPart:
    body: model.LawBody
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class ReadableFieldPart:
    key: str
    value: object
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class EnumMemberFieldPart:
    key: str
    value: str
    line: int | None = None
    column: int | None = None


def _meta_line_column(meta: object) -> tuple[int | None, int | None]:
    return getattr(meta, "line", None), getattr(meta, "column", None)


def _item_line_column(item: object) -> tuple[int | None, int | None]:
    return getattr(item, "line", None), getattr(item, "column", None)


def _positioned_body_prose(meta: object, value: model.ProseLine) -> BodyProsePart:
    line, column = _meta_line_column(meta)
    return BodyProsePart(value=value, line=line, column=column)


def _positioned_input_structure(meta: object, ref: model.NameRef) -> InputStructurePart:
    line, column = _meta_line_column(meta)
    return InputStructurePart(
        config=model.InputStructureConfig(structure_ref=ref),
        line=line,
        column=column,
    )


def _positioned_render_profile(meta: object, ref: model.NameRef) -> RenderProfilePart:
    line, column = _meta_line_column(meta)
    return RenderProfilePart(ref=ref, line=line, column=column)


def _positioned_schema_item(meta: object, item: model.SchemaItem) -> SchemaItemPart:
    line, column = _meta_line_column(meta)
    return SchemaItemPart(item=item, line=line, column=column)


def _positioned_trust_surface(
    meta: object,
    items: tuple[model.TrustSurfaceItem, ...],
) -> TrustSurfacePart:
    line, column = _meta_line_column(meta)
    return TrustSurfacePart(items=items, line=line, column=column)


def _positioned_decision_item(meta: object, item: model.DecisionItem) -> DecisionItemPart:
    line, column = _meta_line_column(meta)
    return DecisionItemPart(item=item, line=line, column=column)


def _positioned_workflow_law(meta: object, body: model.LawBody) -> WorkflowLawPart:
    line, column = _meta_line_column(meta)
    return WorkflowLawPart(body=body, line=line, column=column)


def _positioned_readable_field(meta: object, key: str, value: object) -> ReadableFieldPart:
    line, column = _meta_line_column(meta)
    return ReadableFieldPart(key=key, value=value, line=line, column=column)


def _positioned_enum_member_field(meta: object, key: str, value: str) -> EnumMemberFieldPart:
    line, column = _meta_line_column(meta)
    return EnumMemberFieldPart(key=key, value=value, line=line, column=column)


def _body_prose_value(item: object) -> model.ProseLine | None:
    if isinstance(item, BodyProsePart):
        return item.value
    if isinstance(item, (str, model.EmphasizedLine)):
        return item
    return None


def _body_prose_location(item: object) -> tuple[int | None, int | None]:
    if isinstance(item, BodyProsePart):
        return _item_line_column(item)
    return None, None


def _schema_item_value(item: object) -> model.SchemaItem:
    if isinstance(item, SchemaItemPart):
        return item.item
    return item


def _schema_item_location(item: object) -> tuple[int | None, int | None]:
    if isinstance(item, SchemaItemPart):
        return item.line, item.column
    return None, None


def _schema_block_key(item: model.SchemaItem) -> str | None:
    if isinstance(item, (model.SchemaSectionsBlock, model.SchemaOverrideSectionsBlock)):
        return "sections"
    if isinstance(item, (model.SchemaGatesBlock, model.SchemaOverrideGatesBlock)):
        return "gates"
    if isinstance(item, (model.SchemaArtifactsBlock, model.SchemaOverrideArtifactsBlock)):
        return "artifacts"
    if isinstance(item, (model.SchemaGroupsBlock, model.SchemaOverrideGroupsBlock)):
        return "groups"
    return None


def _name_ref_from_dotted_name(dotted_name: str) -> model.NameRef:
    parts = tuple(dotted_name.split("."))
    return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])


__all__ = [
    "WorkflowBodyParts",
    "SkillsBodyParts",
    "IoBodyParts",
    "InputBodyParts",
    "InputStructurePart",
    "OutputBodyParts",
    "OutputSchemaPart",
    "OutputStructurePart",
    "OutputRecordSectionPart",
    "BodyProsePart",
    "RenderProfilePart",
    "SchemaItemPart",
    "TrustSurfacePart",
    "ReviewBodyParts",
    "RouteOnlyBodyParts",
    "GroundingBodyParts",
    "AnalysisBodyParts",
    "DecisionBodyParts",
    "DecisionItemPart",
    "SkillPackageMetadataFieldPart",
    "SkillPackageMetadataBlockPart",
    "SkillPackageBodyParts",
    "SchemaBodyParts",
    "DocumentBodyParts",
    "ReadablePayloadParts",
    "WorkflowLawPart",
    "ReadableFieldPart",
    "EnumMemberFieldPart",
    "_meta_line_column",
    "_item_line_column",
    "_positioned_body_prose",
    "_positioned_input_structure",
    "_positioned_render_profile",
    "_positioned_schema_item",
    "_positioned_trust_surface",
    "_positioned_decision_item",
    "_positioned_workflow_law",
    "_positioned_readable_field",
    "_positioned_enum_member_field",
    "_body_prose_value",
    "_body_prose_location",
    "_schema_item_value",
    "_schema_item_location",
    "_schema_block_key",
    "_name_ref_from_dotted_name",
]
