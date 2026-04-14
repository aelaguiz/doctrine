from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from doctrine._model.core import ProseLine, RenderProfileRule, RoleScalar
from doctrine._model.readable import (
    ReadableDefinitionItem,
    ReadableFootnoteItem,
    ReadableInlineSchemaData,
    ReadablePropertyItem,
)

# Renderer and flow-renderer import this module directly because it is the
# canonical owner for shared compiled data contracts.


@dataclass(slots=True, frozen=True)
class CompiledSection:
    title: str
    body: tuple[CompiledBodyItem, ...]
    requirement: str | None = None
    when_text: str | None = None
    emit_metadata: bool = False
    render_profile: "ResolvedRenderProfile" | None = None
    semantic_target: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledSequenceBlock:
    title: str
    items: tuple[ProseLine, ...]
    requirement: str | None = None
    when_text: str | None = None
    item_schema: ReadableInlineSchemaData | None = None
    semantic_target: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledBulletsBlock:
    title: str
    items: tuple[ProseLine, ...]
    requirement: str | None = None
    when_text: str | None = None
    item_schema: ReadableInlineSchemaData | None = None
    semantic_target: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledChecklistBlock:
    title: str
    items: tuple[ProseLine, ...]
    requirement: str | None = None
    when_text: str | None = None
    item_schema: ReadableInlineSchemaData | None = None
    semantic_target: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledDefinitionsBlock:
    title: str
    items: tuple[ReadableDefinitionItem, ...]
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledPropertiesBlock:
    title: str | None
    entries: tuple[ReadablePropertyItem, ...]
    requirement: str | None = None
    when_text: str | None = None
    anonymous: bool = False


@dataclass(slots=True, frozen=True)
class CompiledTableCell:
    key: str
    text: str | None = None
    body: tuple[CompiledBodyItem, ...] | None = None


@dataclass(slots=True, frozen=True)
class CompiledTableColumn:
    key: str
    title: str
    body: tuple[ProseLine, ...]


@dataclass(slots=True, frozen=True)
class CompiledTableRow:
    key: str
    cells: tuple[CompiledTableCell, ...]


@dataclass(slots=True, frozen=True)
class CompiledTableData:
    columns: tuple[CompiledTableColumn, ...]
    rows: tuple[CompiledTableRow, ...] = ()
    notes: tuple[ProseLine, ...] = ()
    row_schema: ReadableInlineSchemaData | None = None


@dataclass(slots=True, frozen=True)
class CompiledTableBlock:
    title: str
    table: CompiledTableData
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledCalloutBlock:
    title: str
    body: tuple[ProseLine, ...]
    kind: str | None = None
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledCodeBlock:
    title: str
    text: str
    language: str | None = None
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledRawTextBlock:
    title: str
    text: str
    kind: str
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledFootnotesBlock:
    title: str
    entries: tuple[ReadableFootnoteItem, ...]
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledImageBlock:
    title: str
    src: str
    alt: str
    caption: str | None = None
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledGuardBlock:
    title: str | None
    body: tuple[CompiledBodyItem, ...]
    when_text: str


@dataclass(slots=True, frozen=True)
class CompiledRuleBlock:
    requirement: str | None = None
    when_text: str | None = None


@dataclass(slots=True, frozen=True)
class CompiledFinalOutputSpec:
    output_key: "OutputDeclKey"
    output_name: str
    output_title: str
    target_title: str
    shape_name: str | None
    shape_title: str | None
    requirement: str | None
    format_mode: str
    schema_name: str | None = None
    schema_title: str | None = None
    schema_profile: str | None = None
    schema_file: str | None = None
    example_file: str | None = None
    resolved_schema_file: Path | None = None
    resolved_example_file: Path | None = None
    section: CompiledSection | None = None


@dataclass(slots=True, frozen=True)
class CompiledReviewOutputSpec:
    output_key: "OutputDeclKey"
    output_name: str


@dataclass(slots=True, frozen=True)
class CompiledReviewFinalResponseSpec:
    mode: str
    output_key: "OutputDeclKey" | None = None
    output_name: str | None = None
    review_fields: tuple[tuple[str, tuple[str, ...]], ...] = ()
    control_ready: bool = False


@dataclass(slots=True, frozen=True)
class CompiledReviewOutcomeSpec:
    exists: bool
    verdict: str
    route_behavior: str


@dataclass(slots=True, frozen=True)
class CompiledReviewSpec:
    comment_output: CompiledReviewOutputSpec
    carrier_fields: tuple[tuple[str, tuple[str, ...]], ...]
    final_response: CompiledReviewFinalResponseSpec
    outcomes: tuple[tuple[str, CompiledReviewOutcomeSpec], ...]


@dataclass(slots=True, frozen=True)
class CompiledAgent:
    name: str
    fields: tuple[CompiledField, ...]
    final_output: CompiledFinalOutputSpec | None = None
    review: CompiledReviewSpec | None = None


@dataclass(slots=True, frozen=True)
class CompiledSkillPackage:
    name: str
    title: str
    frontmatter: tuple[tuple[str, str], ...]
    root: CompiledSection
    files: tuple["CompiledSkillPackageFile", ...] = ()


@dataclass(slots=True, frozen=True)
class CompiledSkillPackageFile:
    path: str
    content: bytes


@dataclass(slots=True, frozen=True)
class FlowAgentNode:
    module_parts: tuple[str, ...]
    name: str
    title: str
    detail_lines: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class FlowInputNode:
    module_parts: tuple[str, ...]
    name: str
    title: str
    source_title: str | None = None
    shape_title: str | None = None
    requirement_title: str | None = None
    detail_lines: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class FlowOutputNode:
    module_parts: tuple[str, ...]
    name: str
    title: str
    target_title: str | None = None
    primary_path: str | None = None
    shape_title: str | None = None
    requirement_title: str | None = None
    detail_lines: tuple[str, ...] = ()
    trust_surface: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class FlowEdge:
    kind: str
    source_kind: str
    source_module_parts: tuple[str, ...]
    source_name: str
    target_kind: str
    target_module_parts: tuple[str, ...]
    target_name: str
    label: str


@dataclass(slots=True, frozen=True)
class FlowGraph:
    agents: tuple[FlowAgentNode, ...]
    inputs: tuple[FlowInputNode, ...]
    outputs: tuple[FlowOutputNode, ...]
    edges: tuple[FlowEdge, ...]


CompiledReadableBlock: TypeAlias = (
    CompiledSection
    | CompiledSequenceBlock
    | CompiledBulletsBlock
    | CompiledChecklistBlock
    | CompiledDefinitionsBlock
    | CompiledPropertiesBlock
    | CompiledTableBlock
    | CompiledCalloutBlock
    | CompiledCodeBlock
    | CompiledRawTextBlock
    | CompiledFootnotesBlock
    | CompiledImageBlock
    | CompiledGuardBlock
    | CompiledRuleBlock
)
CompiledBodyItem: TypeAlias = ProseLine | CompiledReadableBlock
CompiledField: TypeAlias = RoleScalar | CompiledReadableBlock


@dataclass(slots=True, frozen=True)
class ResolvedRenderProfile:
    name: str
    rules: tuple[RenderProfileRule, ...] = ()
