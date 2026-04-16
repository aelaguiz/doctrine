from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

import doctrine._model as model
from doctrine._compiler.indexing import IndexedUnit, ModuleLoadKey
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
    CompiledReviewFinalResponseSpec,
    CompiledReviewOutcomeSpec,
    CompiledReviewOutputSpec,
    CompiledReviewSpec,
    CompiledFootnotesBlock,
    CompiledGuardBlock,
    CompiledImageBlock,
    CompiledPropertiesBlock,
    CompiledRawTextBlock,
    CompiledReadableBlock,
    CompiledRouteBranchSpec,
    CompiledRouteChoiceMemberSpec,
    CompiledRouteContractSpec,
    CompiledRouteSelectorSpec,
    CompiledRouteTargetSpec,
    CompiledRuleBlock,
    CompiledSection,
    CompiledSequenceBlock,
    CompiledSkillPackage,
    CompiledSkillPackageFile,
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
from doctrine.diagnostics import CompileError, DoctrineError

# Canonical resolved-contract owner for compiler internals and doctrine.compiler.


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
    | model.TableDecl
    | model.DocumentDecl
    | model.InputDecl
    | model.InputSourceDecl
    | model.OutputDecl
    | model.OutputTargetDecl
    | model.OutputShapeDecl
    | model.OutputSchemaDecl
    | model.SkillDecl
    | model.EnumDecl
)
AddressableRootDecl: TypeAlias = (
    ReadableDecl
    | model.WorkflowDecl
    | model.SkillsDecl
    | model.AnalysisDecl
    | model.SchemaDecl
    | model.TableDecl
    | model.DocumentDecl
    | "ReviewSemanticFieldsRoot"
    | "ReviewSemanticContractRoot"
)
AddressableTarget: TypeAlias = (
    AddressableRootDecl
    | model.RecordScalar
    | model.RecordSection
    | model.GuardedOutputSection
    | model.GuardedOutputScalar
    | model.OutputSchemaField
    | model.OutputSchemaDef
    | model.OutputSchemaOverrideField
    | model.OutputSchemaOverrideDef
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
    render_profile: ResolvedRenderProfile | None = None


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


ResolvedWorkflowItem = (
    ResolvedSectionItem | model.ReadableBlock | ResolvedUseItem | ResolvedWorkflowSkillsItem
)


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
    direct_sections: tuple[tuple[int, CompiledSection], ...] = ()
    has_keyed_children: bool = False


@dataclass(slots=True, frozen=True)
class ContractSectionSummary:
    key: str
    title: str
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
    schema_decl: model.OutputSchemaDecl
    schema_profile: str | None
    lowered_schema: dict[str, object]
    payload_rows: tuple[tuple[str, ...], ...]
    example_text: str | None
    extra_items: tuple[model.AnyRecordItem, ...]


@dataclass(slots=True, frozen=True)
class FinalOutputRouteBinding:
    output_key: "OutputDeclKey"
    output_unit: IndexedUnit
    output_decl: model.OutputDecl
    schema_unit: IndexedUnit
    schema_decl: model.OutputSchemaDecl
    field_path: tuple[str, ...]
    route_field: model.OutputSchemaRouteField
    null_behavior: str
    choices: tuple[model.OutputSchemaRouteChoice, ...]


@dataclass(slots=True, frozen=True)
class LawBranch:
    activation_exprs: tuple[model.Expr, ...] = ()
    mode_bindings: tuple[model.ModeStmt, ...] = ()
    match_bindings: tuple[tuple[tuple[str, ...], str], ...] = ()
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
    choice_members: tuple["RouteChoiceMember", ...] = ()


@dataclass(slots=True, frozen=True)
class RouteSelector:
    surface: str
    field_path: tuple[str, ...] | None = None
    null_behavior: str | None = None


@dataclass(slots=True, frozen=True)
class RouteSemanticContext:
    branches: tuple[RouteSemanticBranch, ...] = ()
    has_unrouted_branch: bool = False
    route_required: bool = False
    unrouted_review_verdicts: frozenset[str] = frozenset()
    selector: RouteSelector | None = None


@dataclass(slots=True, frozen=True)
class RouteChoiceMember:
    member_key: str
    member_title: str
    member_wire: str
    enum_module_parts: tuple[str, ...] = ()
    enum_name: str | None = None


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
    route: model.ReviewOutcomeRouteStmt | None
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
class ResolvedOutputTargetDeliverySkill:
    title: str


@dataclass(slots=True, frozen=True)
class ResolvedOutputTargetSpec:
    # Output targets carry delivery metadata, so they stay separate from input-source config specs.
    title: str
    required_keys: dict[str, str]
    optional_keys: dict[str, str]
    delivery_skill: ResolvedOutputTargetDeliverySkill | None = None


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
