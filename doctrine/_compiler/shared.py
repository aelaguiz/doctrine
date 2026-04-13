from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TypeAlias

from doctrine import model
from doctrine._compiler.types import (
    CompiledAgent,
    CompiledBodyItem,
    CompiledBulletsBlock,
    CompiledCalloutBlock,
    CompiledChecklistBlock,
    CompiledCodeBlock,
    CompiledDefinitionsBlock,
    CompiledField,
    CompiledFinalOutputSpec,
    CompiledFootnotesBlock,
    CompiledGuardBlock,
    CompiledImageBlock,
    CompiledPropertiesBlock,
    CompiledRawTextBlock,
    CompiledReadableBlock,
    CompiledRuleBlock,
    CompiledSection,
    CompiledSequenceBlock,
    CompiledTableBlock,
    CompiledTableCell,
    CompiledTableColumn,
    CompiledTableData,
    CompiledTableRow,
    FlowAgentNode,
    FlowEdge,
    FlowGraph,
    FlowInputNode,
    FlowOutputNode,
    ResolvedRenderProfile,
)
from doctrine._compiler.support import (
    default_worker_count as _default_worker_count,
    dotted_decl_name as _dotted_decl_name,
    path_location as _path_location,
)
from doctrine.diagnostics import CompileError, DoctrineError
from doctrine.parser import parse_file

# Shared compiler support types and helpers; public entrypoints stay on doctrine.compiler.


@dataclass(slots=True, frozen=True)
class AgentFieldCompileSpec:
    field: model.Field
    slot_body: ResolvedWorkflowBody | None = None


FlowAgentKey = tuple[tuple[str, ...], str]
FlowArtifactKey = tuple[tuple[str, ...], str]
ReadableDecl: TypeAlias = (
    model.Agent
    | model.AnalysisDecl
    | model.SchemaDecl
    | model.DocumentDecl
    | model.InputDecl
    | model.InputSourceDecl
    | model.OutputDecl
    | model.OutputTargetDecl
    | model.OutputShapeDecl
    | model.JsonSchemaDecl
    | model.SkillDecl
    | model.EnumDecl
)
AddressableRootDecl: TypeAlias = (
    ReadableDecl
    | model.WorkflowDecl
    | model.SkillsDecl
    | model.AnalysisDecl
    | model.SchemaDecl
    | model.DocumentDecl
    | "ReviewSemanticFieldsRoot"
    | "ReviewSemanticContractRoot"
)
AddressableTarget: TypeAlias = (
    AddressableRootDecl
    | model.RecordScalar
    | model.RecordSection
    | model.GuardedOutputSection
    | model.SchemaSection
    | model.SchemaGate
    | "ResolvedSchemaArtifact"
    | "ResolvedSchemaGroup"
    | "SchemaFamilyTarget"
    | model.DocumentBlock
    | model.ReadableListItem
    | model.ReadablePropertyItem
    | model.ReadableDefinitionItem
    | model.ReadableSchemaEntry
    | model.ReadableTableColumn
    | model.ReadableTableRow
    | model.ReadableFootnoteItem
    | model.EnumMember
    | "ReadableColumnsTarget"
    | "ReadableRowsTarget"
    | "ReadableSchemaTarget"
    | "ReviewSemanticFieldTarget"
    | "ReviewSemanticContractFactTarget"
    | "ReviewSemanticContractGateTarget"
    | "ResolvedAnalysisSection"
    | "ResolvedSectionItem"
    | "ResolvedUseItem"
    | "ResolvedWorkflowSkillsItem"
    | "ResolvedSkillsSection"
    | "ResolvedSkillEntry"
    | "AddressableProjectionTarget"
)


@dataclass(slots=True, frozen=True)
class ResolvedRouteLine:
    label: str
    target_module_parts: tuple[str, ...]
    target_name: str
    target_display_name: str


@dataclass(slots=True, frozen=True)
class ResolvedSectionRef:
    label: str


ResolvedSectionBodyItem: TypeAlias = (
    model.ProseLine
    | ResolvedRouteLine
    | ResolvedSectionRef
    | "ResolvedSectionItem"
    | model.ReadableBlock
)


@dataclass(slots=True, frozen=True)
class ResolvedSectionItem:
    key: str
    title: str
    items: tuple[ResolvedSectionBodyItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedUseItem:
    key: str
    target_unit: IndexedUnit
    workflow_decl: model.WorkflowDecl


@dataclass(slots=True, frozen=True)
class ResolvedSkillEntry:
    key: str
    metadata_unit: IndexedUnit
    target_unit: IndexedUnit
    skill_decl: model.SkillDecl
    items: tuple[model.RecordItem, ...]


ResolvedSkillsSectionBodyItem: TypeAlias = model.ProseLine | ResolvedSkillEntry


@dataclass(slots=True, frozen=True)
class ResolvedSkillsSection:
    key: str
    title: str
    items: tuple[ResolvedSkillsSectionBodyItem, ...]


ResolvedSkillsItem = ResolvedSkillsSection | ResolvedSkillEntry


@dataclass(slots=True, frozen=True)
class ResolvedSkillsBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedSkillsItem, ...]


ResolvedAnalysisSectionItem: TypeAlias = (
    model.ProseLine
    | ResolvedSectionRef
    | model.ProveStmt
    | model.DeriveStmt
    | model.ClassifyStmt
    | model.CompareStmt
    | model.DefendStmt
)


@dataclass(slots=True, frozen=True)
class ResolvedAnalysisSection:
    unit: IndexedUnit
    key: str
    title: str
    items: tuple[ResolvedAnalysisSectionItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedAnalysisBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedAnalysisSection, ...]
    render_profile: "ResolvedRenderProfile" | None = None


@dataclass(slots=True, frozen=True)
class ResolvedSchemaArtifact:
    key: str
    title: str
    ref: model.NameRef
    artifact: "ContractArtifact"


@dataclass(slots=True, frozen=True)
class ResolvedSchemaGroup:
    key: str
    title: str
    members: tuple[str, ...]


SchemaAddressableItem: TypeAlias = (
    model.SchemaSection | model.SchemaGate | ResolvedSchemaArtifact | ResolvedSchemaGroup
)


@dataclass(slots=True, frozen=True)
class SchemaFamilyTarget:
    family_key: str
    title: str
    items: tuple[SchemaAddressableItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedSchemaBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    sections: tuple[model.SchemaSection, ...]
    gates: tuple[model.SchemaGate, ...]
    artifacts: tuple[ResolvedSchemaArtifact, ...]
    groups: tuple[ResolvedSchemaGroup, ...]
    render_profile: ResolvedRenderProfile | None = None


@dataclass(slots=True, frozen=True)
class ResolvedDocumentBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.DocumentBlock, ...]
    render_profile: ResolvedRenderProfile | None = None


@dataclass(slots=True, frozen=True)
class ResolvedIoSection:
    key: str
    section: CompiledSection
    artifacts: tuple["ContractArtifact", ...] = ()
    bindings: tuple["ContractBinding", ...] = ()


@dataclass(slots=True, frozen=True)
class ResolvedIoRef:
    section: CompiledSection
    artifact: "ContractArtifact"


ResolvedIoItem = ResolvedIoSection | ResolvedIoRef


@dataclass(slots=True, frozen=True)
class ResolvedIoBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedIoItem, ...]
    artifacts: tuple["ContractArtifact", ...] = ()
    bindings: tuple["ContractBinding", ...] = ()


@dataclass(slots=True, frozen=True)
class ResolvedWorkflowSkillsItem:
    key: str
    body: ResolvedSkillsBody


ResolvedWorkflowItem = ResolvedSectionItem | ResolvedUseItem | ResolvedWorkflowSkillsItem


@dataclass(slots=True, frozen=True)
class ResolvedWorkflowBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedWorkflowItem, ...]
    law: model.LawBody | None = None


@dataclass(slots=True, frozen=True)
class ContractArtifact:
    kind: str
    unit: IndexedUnit
    decl: model.InputDecl | model.OutputDecl


@dataclass(slots=True, frozen=True)
class ContractBinding:
    binding_path: tuple[str, ...]
    artifact: ContractArtifact


@dataclass(slots=True, frozen=True)
class ResolvedContractBucket:
    body: tuple[CompiledBodyItem, ...]
    artifacts: tuple[ContractArtifact, ...]
    bindings: tuple[ContractBinding, ...]
    direct_artifacts: tuple[ContractArtifact, ...] = ()
    has_keyed_children: bool = False


@dataclass(slots=True, frozen=True)
class ContractSectionSummary:
    key: str
    artifacts: tuple[ContractArtifact, ...]
    bindings: tuple[ContractBinding, ...]


@dataclass(slots=True, frozen=True)
class ContractBodySummary:
    keyed_items: tuple[ContractSectionSummary, ...]
    unkeyed_artifacts: tuple[ContractArtifact, ...]
    artifacts: tuple[ContractArtifact, ...]
    bindings: tuple[ContractBinding, ...]


@dataclass(slots=True, frozen=True)
class AgentContract:
    inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]]
    input_bindings_by_path: dict[tuple[str, ...], ContractBinding]
    outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]]
    output_bindings_by_path: dict[tuple[str, ...], ContractBinding]


@dataclass(slots=True, frozen=True)
class FinalOutputJsonShapeSummary:
    shape_unit: IndexedUnit
    shape_decl: model.OutputShapeDecl
    schema_unit: IndexedUnit
    schema_decl: model.JsonSchemaDecl
    schema_profile: str | None
    schema_file: str | None
    example_file: str | None
    resolved_schema_file: Path | None
    resolved_example_file: Path | None
    payload_rows: tuple[tuple[str, str, str], ...]
    example_text: str | None
    extra_items: tuple[model.AnyRecordItem, ...]


@dataclass(slots=True, frozen=True)
class LawBranch:
    activation_exprs: tuple[model.Expr, ...] = ()
    mode_bindings: tuple[model.ModeStmt, ...] = ()
    current_subjects: tuple[model.CurrentArtifactStmt | model.CurrentNoneStmt, ...] = ()
    musts: tuple[model.MustStmt, ...] = ()
    owns: tuple[model.OwnOnlyStmt, ...] = ()
    preserves: tuple[model.PreserveStmt, ...] = ()
    supports: tuple[model.SupportOnlyStmt, ...] = ()
    ignores: tuple[model.IgnoreStmt, ...] = ()
    forbids: tuple[model.ForbidStmt, ...] = ()
    invalidations: tuple[model.InvalidateStmt, ...] = ()
    stops: tuple[model.StopStmt, ...] = ()
    routes: tuple[model.LawRouteStmt, ...] = ()


@dataclass(slots=True, frozen=True)
class ReviewContractGate:
    key: str
    title: str


@dataclass(slots=True, frozen=True)
class ReviewContractSpec:
    kind: str
    title: str
    gates: tuple[ReviewContractGate, ...]


@dataclass(slots=True, frozen=True)
class ReviewSemanticContext:
    review_module_parts: tuple[str, ...]
    output_module_parts: tuple[str, ...]
    output_name: str
    field_bindings: tuple[tuple[str, tuple[str, ...]], ...] = ()
    contract_gates: tuple[ReviewContractGate, ...] = ()


@dataclass(slots=True, frozen=True)
class ReviewSemanticFieldsRoot:
    context: ReviewSemanticContext


@dataclass(slots=True, frozen=True)
class ReviewSemanticContractRoot:
    context: ReviewSemanticContext


@dataclass(slots=True, frozen=True)
class ReviewSemanticFieldTarget:
    field_name: str
    field_path: tuple[str, ...]
    context: ReviewSemanticContext


@dataclass(slots=True, frozen=True)
class ReviewSemanticContractFactTarget:
    key: str


@dataclass(slots=True, frozen=True)
class ReviewSemanticContractGateTarget:
    gate: ReviewContractGate


@dataclass(slots=True, frozen=True)
class RouteSemanticBranch:
    target_module_parts: tuple[str, ...]
    target_name: str
    target_title: str | None
    label: str
    review_verdict: str | None = None


@dataclass(slots=True, frozen=True)
class RouteSemanticContext:
    branches: tuple[RouteSemanticBranch, ...] = ()
    has_unrouted_branch: bool = False
    route_required: bool = False


@dataclass(slots=True, frozen=True)
class ReadableColumnsTarget:
    columns: tuple[model.ReadableTableColumn, ...]


@dataclass(slots=True, frozen=True)
class ReadableRowsTarget:
    rows: tuple[model.ReadableTableRow, ...]


@dataclass(slots=True, frozen=True)
class ReadableSchemaTarget:
    title: str
    entries: tuple[model.ReadableSchemaEntry, ...]


@dataclass(slots=True, frozen=True)
class ResolvedReviewBody:
    title: str
    subject: model.ReviewSubjectConfig | None = None
    subject_map: model.ReviewSubjectMapConfig | None = None
    contract: model.ReviewContractConfig | None = None
    comment_output: model.ReviewCommentOutputConfig | None = None
    fields: model.ReviewFieldsConfig | None = None
    selector: model.ReviewSelectorConfig | None = None
    cases: tuple[model.ReviewCase, ...] = ()
    items: tuple[model.ReviewSection | model.ReviewOutcomeSection, ...] = ()


@dataclass(slots=True, frozen=True)
class ReviewOutcomeBranch:
    currents: tuple[model.ReviewCurrentArtifactStmt | model.ReviewCurrentNoneStmt, ...] = ()
    carries: tuple[model.ReviewCarryStmt, ...] = ()
    routes: tuple[model.ReviewOutcomeRouteStmt, ...] = ()
    route_selected: bool = False
    blocked_gate_present: bool | None = None


@dataclass(slots=True, frozen=True)
class ReviewGateCheck:
    identity: str
    expr: model.Expr


@dataclass(slots=True, frozen=True)
class ReviewPreSectionBranch:
    block_checks: tuple[ReviewGateCheck, ...] = ()
    reject_checks: tuple[ReviewGateCheck, ...] = ()
    accept_checks: tuple[ReviewGateCheck, ...] = ()
    has_assertions: bool = False


@dataclass(slots=True, frozen=True)
class ReviewPreOutcomeBranch:
    block_checks: tuple[ReviewGateCheck, ...] = ()
    reject_checks: tuple[ReviewGateCheck, ...] = ()
    accept_checks: tuple[ReviewGateCheck, ...] = ()
    assertion_gate_ids: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class ResolvedReviewGateBranch:
    verdict: str
    failing_gate_ids: tuple[str, ...] = ()
    blocked_gate_id: str | None = None


@dataclass(slots=True, frozen=True)
class ResolvedReviewAgreementBranch:
    section_key: str
    verdict: str
    route: model.ReviewOutcomeRouteStmt
    current: model.ReviewCurrentArtifactStmt | model.ReviewCurrentNoneStmt
    current_carrier_path: tuple[str, ...] | None = None
    current_subject_key: tuple[tuple[str, ...], str] | None = None
    reviewed_subject_key: tuple[tuple[str, ...], str] | None = None
    carries: tuple[model.ReviewCarryStmt, ...] = ()
    requires_failure_detail: bool = False
    blocked_gate_required: bool = False
    failing_gate_ids: tuple[str, ...] = ()
    blocked_gate_id: str | None = None


@dataclass(slots=True, frozen=True)
class ReviewGateObservation:
    needs_blocked_gate_presence: bool = False
    needs_blocked_gate_value: bool = False
    needs_failing_gates_presence: bool = False
    needs_failing_gates_value: bool = False
    needs_contract_failed_gates_value: bool = False
    needs_contract_first_failed_gate: bool = False
    needs_contract_passes: bool = False
    referenced_contract_gate_ids: tuple[str, ...] = ()


OutputDeclKey = tuple[tuple[str, ...], str]


@dataclass(slots=True, frozen=True)
class ResolvedLawPath:
    unit: IndexedUnit
    decl: (
        model.InputDecl
        | model.OutputDecl
        | model.EnumDecl
        | model.GroundingDecl
        | SchemaFamilyTarget
        | ResolvedSchemaGroup
    )
    remainder: tuple[str, ...]
    wildcard: bool = False
    binding_path: tuple[str, ...] | None = None


@dataclass(slots=True, frozen=True)
class CanonicalLawPath:
    unit: IndexedUnit
    decl: (
        model.InputDecl
        | model.OutputDecl
        | model.EnumDecl
        | model.GroundingDecl
        | SchemaFamilyTarget
        | ResolvedSchemaGroup
    )
    remainder: tuple[str, ...]
    wildcard: bool = False


@dataclass(slots=True, frozen=True)
class ResolvedAgentSlot:
    key: str
    body: ResolvedWorkflowBody


@dataclass(slots=True, frozen=True)
class ResolvedAbstractAgentSlot:
    key: str


ResolvedAgentSlotState = ResolvedAgentSlot | ResolvedAbstractAgentSlot


@dataclass(slots=True, frozen=True)
class ConfigSpec:
    title: str
    required_keys: dict[str, str]
    optional_keys: dict[str, str]


@dataclass(slots=True, frozen=True)
class DisplayValue:
    text: str
    kind: str


@dataclass(slots=True, frozen=True)
class AddressableProjectionTarget:
    text: str
    kind: str


@dataclass(slots=True, frozen=True)
class AddressableNode:
    unit: IndexedUnit
    root_decl: AddressableRootDecl
    target: AddressableTarget


_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
_INTERPOLATION_EXPR_RE = re.compile(
    r"\s*"
    r"([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
    r"(?:\s*:\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*))?"
    r"\s*"
)
_INTERPOLATION_RE = re.compile(r"\{\{([^{}]+)\}\}")
# Reserved typed fields get their own compiler paths. Every other key is an
# authored workflow slot, with one legacy carve-out: the old `workflow` field
# still preserves 01-06 body inheritance semantics instead of switching to a
# second slot-patching dialect.
_RESERVED_AGENT_FIELD_KEYS = {
    "role",
    "inputs",
    "outputs",
    "analysis",
    "skills",
    "review",
    "final_output",
}

_BUILTIN_INPUT_SOURCES = {
    "Prompt": ConfigSpec(title="Prompt", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
    "EnvVar": ConfigSpec(title="EnvVar", required_keys={"env": "Env"}, optional_keys={}),
}

_BUILTIN_OUTPUT_TARGETS = {
    "TurnResponse": ConfigSpec(title="Turn Response", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
}

_BUILTIN_RENDER_PROFILE_NAMES = ("ContractMarkdown", "ArtifactMarkdown", "CommentMarkdown")


def _semantic_render_target_for_block(kind: str, key: str) -> str | None:
    if kind == "section" and key == "contract_checks":
        return "review.contract_checks"
    if kind in {"sequence", "bullets", "checklist"} and key == "invalidations":
        return "control.invalidations"
    return None


def _resolve_render_profile_mode(
    profile: "ResolvedRenderProfile",
    *targets: str,
) -> str | None:
    authored = {".".join(rule.target_parts): rule.mode for rule in profile.rules}
    for target in targets:
        mode = authored.get(target)
        if mode is not None:
            return mode
    return None

_READABLE_DECL_REGISTRIES = (
    ("agent declaration", "agents_by_name"),
    ("analysis declaration", "analyses_by_name"),
    ("decision declaration", "decisions_by_name"),
    ("schema declaration", "schemas_by_name"),
    ("document declaration", "documents_by_name"),
    ("input declaration", "inputs_by_name"),
    ("input source declaration", "input_sources_by_name"),
    ("output declaration", "outputs_by_name"),
    ("output target declaration", "output_targets_by_name"),
    ("output shape declaration", "output_shapes_by_name"),
    ("json schema declaration", "json_schemas_by_name"),
    ("skill declaration", "skills_by_name"),
    ("enum declaration", "enums_by_name"),
)

_ADDRESSABLE_ROOT_REGISTRIES = (
    *_READABLE_DECL_REGISTRIES,
    ("workflow declaration", "workflows_by_name"),
    ("skills block", "skills_blocks_by_name"),
)
_SCHEMA_FAMILY_TITLES = {
    "sections": "Required Sections",
    "gates": "Contract Gates",
    "artifacts": "Artifact Inventory",
    "groups": "Surface Groups",
}

_REVIEW_REQUIRED_FIELD_NAMES = frozenset(
    {
        "verdict",
        "reviewed_artifact",
        "analysis",
        "readback",
        "failing_gates",
        "next_owner",
    }
)
_REVIEW_OPTIONAL_FIELD_NAMES = frozenset({"blocked_gate", "active_mode", "trigger_reason"})
_REVIEW_CONTEXT_FIELD_NAMES = frozenset({"current_artifact"})
_REVIEW_FIELD_NAMES = (
    _REVIEW_REQUIRED_FIELD_NAMES | _REVIEW_OPTIONAL_FIELD_NAMES | _REVIEW_CONTEXT_FIELD_NAMES
)
_REVIEW_GUARD_FIELD_NAMES = _REVIEW_FIELD_NAMES | frozenset({"current_artifact"})
_REVIEW_VERDICT_TEXT = {
    "accept": "accepted",
    "changes_requested": "changes requested",
}
_REVIEW_CONTRACT_FACT_KEYS = ("passes", "failed_gates", "first_failed_gate")


def _dotted_ref_name(ref: model.NameRef) -> str:
    return ".".join((*ref.module_parts, ref.declaration_name))


def _agent_typed_field_key(field: model.Field) -> str:
    if isinstance(field, model.InputsField):
        return "inputs"
    if isinstance(field, model.OutputsField):
        return "outputs"
    if isinstance(field, model.AnalysisField):
        return "analysis"
    if isinstance(field, model.DecisionField):
        return f"decision:{_dotted_ref_name(field.value)}"
    if isinstance(field, model.SkillsField):
        return "skills"
    if isinstance(field, model.ReviewField):
        return "review"
    if isinstance(field, model.FinalOutputField):
        return "final_output"
    return type(field).__name__


def _name_ref_from_dotted_name(dotted_name: str) -> model.NameRef:
    parts = tuple(dotted_name.split("."))
    return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])


def _law_path_from_name_ref(ref: model.NameRef) -> model.LawPath:
    return model.LawPath(parts=(*ref.module_parts, ref.declaration_name))


from doctrine._compiler.indexing import IndexedUnit, ModuleLoadKey
def _humanize_key(value: str) -> str:
    value = value.replace("_", " ")
    value = _CAMEL_BOUNDARY_RE.sub(" ", value)
    words = value.split()
    return " ".join(word if word.isupper() else word.capitalize() for word in words)


def _lowercase_initial(value: str) -> str:
    if not value:
        return value
    return value[0].lower() + value[1:]


def _display_addressable_ref(ref: model.AddressableRef) -> str:
    root = _dotted_ref_name(ref.root)
    if not ref.path:
        return root
    return f"{root}:{'.'.join(ref.path)}"
