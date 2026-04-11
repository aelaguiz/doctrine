from __future__ import annotations

import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TypeAlias

from doctrine import model
from doctrine.diagnostics import CompileError, DiagnosticLocation, DoctrineError
from doctrine.parser import parse_file


@dataclass(slots=True, frozen=True)
class CompiledSection:
    title: str
    body: tuple[CompiledBodyItem, ...]


@dataclass(slots=True, frozen=True)
class CompiledAgent:
    name: str
    fields: tuple[CompiledField, ...]


@dataclass(slots=True, frozen=True)
class AgentFieldCompileSpec:
    field: model.Field
    slot_body: ResolvedWorkflowBody | None = None


FlowAgentKey = tuple[tuple[str, ...], str]
FlowArtifactKey = tuple[tuple[str, ...], str]


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
    detail_lines: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class FlowOutputNode:
    module_parts: tuple[str, ...]
    name: str
    title: str
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


CompiledBodyItem: TypeAlias = model.ProseLine | CompiledSection
CompiledField: TypeAlias = model.RoleScalar | CompiledSection
ReadableDecl: TypeAlias = (
    model.Agent
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
    | "ReviewSemanticFieldsRoot"
    | "ReviewSemanticContractRoot"
)
AddressableTarget: TypeAlias = (
    AddressableRootDecl
    | model.RecordScalar
    | model.RecordSection
    | model.GuardedOutputSection
    | model.EnumMember
    | "ReviewSemanticFieldTarget"
    | "ReviewSemanticContractFactTarget"
    | "ReviewSemanticContractGateTarget"
    | "ResolvedSectionItem"
    | "ResolvedUseItem"
    | "ResolvedWorkflowSkillsItem"
    | "ResolvedSkillsSection"
    | "ResolvedSkillEntry"
)


@dataclass(slots=True, frozen=True)
class IndexedUnit:
    module_parts: tuple[str, ...]
    prompt_file: model.PromptFile
    imports: tuple[model.ImportDecl, ...]
    workflows_by_name: dict[str, model.WorkflowDecl]
    reviews_by_name: dict[str, model.ReviewDecl]
    inputs_blocks_by_name: dict[str, model.InputsDecl]
    inputs_by_name: dict[str, model.InputDecl]
    input_sources_by_name: dict[str, model.InputSourceDecl]
    outputs_blocks_by_name: dict[str, model.OutputsDecl]
    outputs_by_name: dict[str, model.OutputDecl]
    output_targets_by_name: dict[str, model.OutputTargetDecl]
    output_shapes_by_name: dict[str, model.OutputShapeDecl]
    json_schemas_by_name: dict[str, model.JsonSchemaDecl]
    skills_by_name: dict[str, model.SkillDecl]
    skills_blocks_by_name: dict[str, model.SkillsDecl]
    enums_by_name: dict[str, model.EnumDecl]
    agents_by_name: dict[str, model.Agent]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]


@dataclass(slots=True, frozen=True)
class ResolvedRouteLine:
    label: str
    target_module_parts: tuple[str, ...]
    target_name: str


@dataclass(slots=True, frozen=True)
class ResolvedSectionRef:
    label: str


ResolvedSectionBodyItem: TypeAlias = (
    model.ProseLine | ResolvedRouteLine | ResolvedSectionRef | "ResolvedSectionItem"
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
    workflow_unit: IndexedUnit
    workflow_decl: model.WorkflowDecl
    workflow_body: ResolvedWorkflowBody
    gates: tuple[ReviewContractGate, ...]


@dataclass(slots=True, frozen=True)
class ReviewSemanticContext:
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
class ResolvedReviewBody:
    title: str
    subject: model.ReviewSubjectConfig | None = None
    subject_map: model.ReviewSubjectMapConfig | None = None
    contract: model.ReviewContractConfig | None = None
    comment_output: model.ReviewCommentOutputConfig | None = None
    fields: model.ReviewFieldsConfig | None = None
    items: tuple[model.ReviewSection | model.ReviewOutcomeSection, ...] = ()


@dataclass(slots=True, frozen=True)
class ReviewOutcomeBranch:
    currents: tuple[model.ReviewCurrentArtifactStmt | model.ReviewCurrentNoneStmt, ...] = ()
    carries: tuple[model.ReviewCarryStmt, ...] = ()
    routes: tuple[model.ReviewOutcomeRouteStmt, ...] = ()
    route_selected: bool = False


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
    decl: model.InputDecl | model.OutputDecl | model.EnumDecl
    remainder: tuple[str, ...]
    wildcard: bool = False
    binding_path: tuple[str, ...] | None = None


@dataclass(slots=True, frozen=True)
class CanonicalLawPath:
    unit: IndexedUnit
    decl: model.InputDecl | model.OutputDecl | model.EnumDecl
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
_RESERVED_AGENT_FIELD_KEYS = {"role", "inputs", "outputs", "skills", "review"}

_BUILTIN_INPUT_SOURCES = {
    "Prompt": ConfigSpec(title="Prompt", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
    "EnvVar": ConfigSpec(title="EnvVar", required_keys={"env": "Env"}, optional_keys={}),
}

_BUILTIN_OUTPUT_TARGETS = {
    "TurnResponse": ConfigSpec(title="Turn Response", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
}

_READABLE_DECL_REGISTRIES = (
    ("agent declaration", "agents_by_name"),
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
_REVIEW_FIELD_NAMES = _REVIEW_REQUIRED_FIELD_NAMES | _REVIEW_OPTIONAL_FIELD_NAMES
_REVIEW_GUARD_FIELD_NAMES = _REVIEW_FIELD_NAMES | frozenset({"current_artifact"})
_REVIEW_VERDICT_TEXT = {
    "accept": "accepted",
    "changes_requested": "changes requested",
}
_REVIEW_CONTRACT_FACT_KEYS = ("passes", "failed_gates", "first_failed_gate")


def _default_worker_count(task_count: int) -> int:
    if task_count <= 1:
        return 1
    cpu_count = os.cpu_count() or 1
    return min(task_count, max(2, cpu_count))


def _clone_doctrine_error(error: DoctrineError) -> DoctrineError:
    return type(error)(diagnostic=error.diagnostic)


def _register_decl(
    registry: dict[str, object],
    name: str,
    module_parts: tuple[str, ...],
) -> None:
    if name in registry:
        dotted_name = ".".join((*module_parts, name)) or name
        raise CompileError(f"Duplicate declaration name: {dotted_name}")


def _validate_enum_decl(decl: model.EnumDecl, *, owner_label: str) -> None:
    seen_keys: set[str] = set()
    for member in decl.members:
        if member.key in seen_keys:
            raise CompileError(f"Duplicate enum member key in {owner_label}: {member.key}")
        seen_keys.add(member.key)


class CompilationSession:
    def __init__(self, prompt_file: model.PromptFile):
        self.prompt_root = _resolve_prompt_root(prompt_file.source_path)
        self._module_cache: dict[tuple[str, ...], IndexedUnit] = {}
        self._module_load_errors: dict[tuple[str, ...], Exception] = {}
        self._module_loading: dict[tuple[str, ...], threading.Event] = {}
        self._module_lock = threading.Lock()
        # Shared prompt graph data lives on the session; compile contexts stay task-local.
        self.root_unit = self._index_unit(
            prompt_file,
            module_parts=(),
            ancestry=(),
            allow_parallel_imports=True,
        )

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        try:
            return CompilationContext(self).compile_agent(agent_name)
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"compile agent `{agent_name}`",
                location=_path_location(self.root_unit.prompt_file.source_path),
            ).ensure_location(path=self.root_unit.prompt_file.source_path)

    def compile_agents(self, agent_names: tuple[str, ...]) -> tuple[CompiledAgent, ...]:
        if len(agent_names) <= 1:
            return tuple(self.compile_agent(agent_name) for agent_name in agent_names)

        with ThreadPoolExecutor(max_workers=_default_worker_count(len(agent_names))) as executor:
            futures = {
                agent_name: executor.submit(self.compile_agent, agent_name)
                for agent_name in agent_names
            }
            return tuple(futures[agent_name].result() for agent_name in agent_names)

    def _compile_agent_field_task(
        self,
        spec: AgentFieldCompileSpec,
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
    ) -> CompiledField:
        return CompilationContext(self)._compile_agent_field(
            spec,
            agent_name=agent_name,
            unit=unit,
            agent_contract=agent_contract,
            review_output_contexts=review_output_contexts,
        )

    def extract_target_flow_graph(self, agent_names: tuple[str, ...]) -> FlowGraph:
        try:
            return CompilationContext(self).extract_target_flow_graph(agent_names)
        except DoctrineError as exc:
            raise exc.prepend_trace(
                "extract flow graph",
                location=_path_location(self.root_unit.prompt_file.source_path),
            ).ensure_location(path=self.root_unit.prompt_file.source_path)

    def load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        if not module_parts:
            return self.root_unit
        return self._load_module(module_parts, ancestry=())

    def _index_unit(
        self,
        prompt_file: model.PromptFile,
        *,
        module_parts: tuple[str, ...],
        ancestry: tuple[tuple[str, ...], ...],
        allow_parallel_imports: bool,
    ) -> IndexedUnit:
        imports: list[model.ImportDecl] = []
        workflows_by_name: dict[str, model.WorkflowDecl] = {}
        reviews_by_name: dict[str, model.ReviewDecl] = {}
        skills_blocks_by_name: dict[str, model.SkillsDecl] = {}
        inputs_blocks_by_name: dict[str, model.InputsDecl] = {}
        inputs_by_name: dict[str, model.InputDecl] = {}
        input_sources_by_name: dict[str, model.InputSourceDecl] = {}
        outputs_blocks_by_name: dict[str, model.OutputsDecl] = {}
        outputs_by_name: dict[str, model.OutputDecl] = {}
        output_targets_by_name: dict[str, model.OutputTargetDecl] = {}
        output_shapes_by_name: dict[str, model.OutputShapeDecl] = {}
        json_schemas_by_name: dict[str, model.JsonSchemaDecl] = {}
        skills_by_name: dict[str, model.SkillDecl] = {}
        agents_by_name: dict[str, model.Agent] = {}
        enums_by_name: dict[str, model.EnumDecl] = {}

        for declaration in prompt_file.declarations:
            if isinstance(declaration, model.ImportDecl):
                imports.append(declaration)
                continue
            if isinstance(declaration, model.WorkflowDecl):
                _register_decl(workflows_by_name, declaration.name, module_parts)
                workflows_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.ReviewDecl):
                _register_decl(reviews_by_name, declaration.name, module_parts)
                reviews_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.SkillsDecl):
                _register_decl(skills_blocks_by_name, declaration.name, module_parts)
                skills_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputsDecl):
                _register_decl(inputs_blocks_by_name, declaration.name, module_parts)
                inputs_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputDecl):
                _register_decl(inputs_by_name, declaration.name, module_parts)
                inputs_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputSourceDecl):
                _register_decl(input_sources_by_name, declaration.name, module_parts)
                input_sources_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputsDecl):
                _register_decl(outputs_blocks_by_name, declaration.name, module_parts)
                outputs_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputDecl):
                _register_decl(outputs_by_name, declaration.name, module_parts)
                outputs_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputTargetDecl):
                _register_decl(output_targets_by_name, declaration.name, module_parts)
                output_targets_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputShapeDecl):
                _register_decl(output_shapes_by_name, declaration.name, module_parts)
                output_shapes_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.JsonSchemaDecl):
                _register_decl(json_schemas_by_name, declaration.name, module_parts)
                json_schemas_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.SkillDecl):
                _register_decl(skills_by_name, declaration.name, module_parts)
                skills_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.EnumDecl):
                _register_decl(enums_by_name, declaration.name, module_parts)
                _validate_enum_decl(
                    declaration,
                    owner_label=f"enum {_dotted_decl_name(module_parts, declaration.name)}",
                )
                enums_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.Agent):
                _register_decl(agents_by_name, declaration.name, module_parts)
                agents_by_name[declaration.name] = declaration
                continue
            raise CompileError(f"Unsupported declaration type: {type(declaration).__name__}")

        imported_units = self._load_imports(
            imports,
            module_parts=module_parts,
            importer_path=prompt_file.source_path,
            ancestry=ancestry,
            allow_parallel_imports=allow_parallel_imports,
        )

        return IndexedUnit(
            module_parts=module_parts,
            prompt_file=prompt_file,
            imports=tuple(imports),
            workflows_by_name=workflows_by_name,
            reviews_by_name=reviews_by_name,
            inputs_blocks_by_name=inputs_blocks_by_name,
            inputs_by_name=inputs_by_name,
            input_sources_by_name=input_sources_by_name,
            outputs_blocks_by_name=outputs_blocks_by_name,
            outputs_by_name=outputs_by_name,
            output_targets_by_name=output_targets_by_name,
            output_shapes_by_name=output_shapes_by_name,
            json_schemas_by_name=json_schemas_by_name,
            skills_by_name=skills_by_name,
            skills_blocks_by_name=skills_blocks_by_name,
            enums_by_name=enums_by_name,
            agents_by_name=agents_by_name,
            imported_units=imported_units,
        )

    def _load_imports(
        self,
        imports: list[model.ImportDecl],
        *,
        module_parts: tuple[str, ...],
        importer_path: Path | None,
        ancestry: tuple[tuple[str, ...], ...],
        allow_parallel_imports: bool,
    ) -> dict[tuple[str, ...], IndexedUnit]:
        imported_units: dict[tuple[str, ...], IndexedUnit] = {}
        if not imports:
            return imported_units

        resolved_imports = [
            (_resolve_import_path(import_decl.path, module_parts=module_parts), import_decl)
            for import_decl in imports
        ]

        if allow_parallel_imports and len(resolved_imports) > 1:
            futures: dict[tuple[str, ...], object] = {}
            with ThreadPoolExecutor(max_workers=_default_worker_count(len(resolved_imports))) as executor:
                for resolved_module_parts, _import_decl in resolved_imports:
                    if resolved_module_parts in futures:
                        continue
                    futures[resolved_module_parts] = executor.submit(
                        self._load_module,
                        resolved_module_parts,
                        ancestry=ancestry,
                    )

                for resolved_module_parts, _import_decl in resolved_imports:
                    try:
                        imported_units[resolved_module_parts] = futures[
                            resolved_module_parts
                        ].result()
                    except DoctrineError as exc:
                        raise exc.prepend_trace(
                            f"resolve import `{'.'.join(resolved_module_parts)}`",
                            location=_path_location(importer_path),
                        )
            return imported_units

        for resolved_module_parts, _import_decl in resolved_imports:
            try:
                imported_units[resolved_module_parts] = self._load_module(
                    resolved_module_parts,
                    ancestry=ancestry,
                )
            except DoctrineError as exc:
                raise exc.prepend_trace(
                    f"resolve import `{'.'.join(resolved_module_parts)}`",
                    location=_path_location(importer_path),
                )
        return imported_units

    def _load_module(
        self,
        module_parts: tuple[str, ...],
        *,
        ancestry: tuple[tuple[str, ...], ...],
    ) -> IndexedUnit:
        cached = self._module_cache.get(module_parts)
        if cached is not None:
            return cached
        if module_parts in ancestry:
            raise CompileError(f"Cyclic import module: {'.'.join(module_parts)}")

        with self._module_lock:
            cached = self._module_cache.get(module_parts)
            if cached is not None:
                return cached

            cached_error = self._module_load_errors.get(module_parts)
            if cached_error is not None:
                if isinstance(cached_error, DoctrineError):
                    raise _clone_doctrine_error(cached_error)
                raise cached_error

            ready = self._module_loading.get(module_parts)
            if ready is None:
                ready = threading.Event()
                self._module_loading[module_parts] = ready
                is_loader = True
            else:
                is_loader = False

        if not is_loader:
            ready.wait()
            with self._module_lock:
                cached = self._module_cache.get(module_parts)
                if cached is not None:
                    return cached
                cached_error = self._module_load_errors.get(module_parts)
            if cached_error is None:
                raise CompileError(
                    f"Internal compiler error: module load finished without a result: {'.'.join(module_parts)}"
                )
            if isinstance(cached_error, DoctrineError):
                raise _clone_doctrine_error(cached_error)
            raise cached_error

        module_path = self.prompt_root.joinpath(*module_parts).with_suffix(".prompt")
        try:
            if not module_path.is_file():
                raise CompileError(f"Missing import module: {'.'.join(module_parts)}")
            try:
                prompt_file = parse_file(module_path)
                indexed = self._index_unit(
                    prompt_file,
                    module_parts=module_parts,
                    ancestry=(*ancestry, module_parts),
                    allow_parallel_imports=False,
                )
            except DoctrineError as exc:
                raise exc.prepend_trace(
                    f"load import module `{'.'.join(module_parts)}`",
                    location=_path_location(module_path),
                ).ensure_location(path=module_path)
        except Exception as exc:
            with self._module_lock:
                if isinstance(exc, DoctrineError):
                    self._module_load_errors[module_parts] = _clone_doctrine_error(exc)
                else:
                    self._module_load_errors[module_parts] = exc
            raise
        else:
            with self._module_lock:
                self._module_cache[module_parts] = indexed
            return indexed
        finally:
            with self._module_lock:
                ready = self._module_loading.pop(module_parts, None)
            if ready is not None:
                ready.set()


class CompilationContext:
    def __init__(self, session: CompilationSession):
        self.session = session
        self.prompt_root = session.prompt_root
        self._workflow_compile_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._review_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._inputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._outputs_resolution_stack: list[
            tuple[
                tuple[str, ...],
                str,
                frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
            ]
        ] = []
        self._agent_slot_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._resolved_workflow_cache: dict[tuple[tuple[str, ...], str], ResolvedWorkflowBody] = {}
        self._resolved_review_cache: dict[tuple[tuple[str, ...], str], ResolvedReviewBody] = {}
        self._addressable_workflow_cache: dict[
            tuple[tuple[str, ...], str], ResolvedWorkflowBody
        ] = {}
        self._resolved_skills_cache: dict[tuple[tuple[str, ...], str], ResolvedSkillsBody] = {}
        self._addressable_skills_cache: dict[
            tuple[tuple[str, ...], str], ResolvedSkillsBody
        ] = {}
        self._resolved_inputs_cache: dict[tuple[tuple[str, ...], str], ResolvedIoBody] = {}
        self._resolved_outputs_cache: dict[
            tuple[
                tuple[str, ...],
                str,
                frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
            ],
            ResolvedIoBody,
        ] = {}
        self._resolved_agent_slot_cache: dict[
            tuple[tuple[str, ...], str],
            tuple[ResolvedAgentSlotState, ...],
        ] = {}
        # Mutable resolution stacks and caches remain local to one compile task.
        self.root_unit = session.root_unit

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        agent = self.root_unit.agents_by_name.get(agent_name)
        if agent is None:
            raise CompileError(f"Missing target agent: {agent_name}")
        if agent.abstract:
            raise CompileError(f"Abstract agent does not render: {agent_name}")
        return self._compile_agent_decl(agent, unit=self.root_unit)

    def extract_target_flow_graph(self, agent_names: tuple[str, ...]) -> FlowGraph:
        root_agents: list[tuple[IndexedUnit, model.Agent]] = []
        for agent_name in agent_names:
            agent = self.root_unit.agents_by_name.get(agent_name)
            if agent is None:
                raise CompileError(f"Missing target agent: {agent_name}")
            if agent.abstract:
                raise CompileError(f"Abstract agent does not render: {agent_name}")
            root_agents.append((self.root_unit, agent))

        agent_nodes: dict[FlowAgentKey, FlowAgentNode] = {}
        input_nodes: dict[FlowArtifactKey, FlowInputNode] = {}
        output_nodes: dict[FlowArtifactKey, FlowOutputNode] = {}
        agent_notes: dict[FlowAgentKey, list[str]] = {}
        input_notes: dict[FlowArtifactKey, list[str]] = {}
        output_notes: dict[FlowArtifactKey, list[str]] = {}
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ] = {}

        for unit, agent in root_agents:
            agent_key = (unit.module_parts, agent.name)
            self._flow_upsert_agent_node(agent_nodes, agent, unit=unit)

            agent_contract = self._resolve_agent_contract(agent, unit=unit)
            for input_key, (input_unit, input_decl) in sorted(agent_contract.inputs.items()):
                self._flow_upsert_input_node(input_nodes, input_decl, unit=input_unit)
                self._flow_add_edge(
                    edges,
                    FlowEdge(
                        kind="consume",
                        source_kind="input",
                        source_module_parts=input_key[0],
                        source_name=input_key[1],
                        target_kind="agent",
                        target_module_parts=agent_key[0],
                        target_name=agent_key[1],
                        label="consumes",
                    ),
                )

            for output_key, (output_unit, output_decl) in sorted(agent_contract.outputs.items()):
                self._flow_upsert_output_node(output_nodes, output_decl, unit=output_unit)
                self._flow_add_edge(
                    edges,
                    FlowEdge(
                        kind="produce",
                        source_kind="agent",
                        source_module_parts=agent_key[0],
                        source_name=agent_key[1],
                        target_kind="output",
                        target_module_parts=output_key[0],
                        target_name=output_key[1],
                        label="produces",
                    ),
                )

            for slot_state in self._resolve_agent_slots(agent, unit=unit):
                if not isinstance(slot_state, ResolvedAgentSlot):
                    continue
                self._collect_flow_from_workflow_body(
                    slot_state.body,
                    workflow_unit=unit,
                    agent_unit=unit,
                    agent=agent,
                    agent_contract=agent_contract,
                    agent_nodes=agent_nodes,
                    agent_notes=agent_notes,
                    input_notes=input_notes,
                    output_nodes=output_nodes,
                    output_notes=output_notes,
                    edges=edges,
                    owner_label=f"agent {agent.name} slot {slot_state.key}",
                    workflow_stack=(),
                )

        return FlowGraph(
            agents=tuple(
                FlowAgentNode(
                    module_parts=node.module_parts,
                    name=node.name,
                    title=node.title,
                    detail_lines=node.detail_lines,
                    notes=tuple(agent_notes.get((node.module_parts, node.name), ())),
                )
                for node in sorted(
                    agent_nodes.values(),
                    key=lambda node: (node.module_parts, node.name),
                )
            ),
            inputs=tuple(
                FlowInputNode(
                    module_parts=node.module_parts,
                    name=node.name,
                    title=node.title,
                    detail_lines=node.detail_lines,
                    notes=tuple(input_notes.get((node.module_parts, node.name), ())),
                )
                for node in sorted(
                    input_nodes.values(),
                    key=lambda node: (node.module_parts, node.name),
                )
            ),
            outputs=tuple(
                FlowOutputNode(
                    module_parts=node.module_parts,
                    name=node.name,
                    title=node.title,
                    detail_lines=node.detail_lines,
                    trust_surface=node.trust_surface,
                    notes=tuple(output_notes.get((node.module_parts, node.name), ())),
                )
                for node in sorted(
                    output_nodes.values(),
                    key=lambda node: (node.module_parts, node.name),
                )
            ),
            edges=tuple(
                sorted(
                    edges.values(),
                    key=lambda edge: (
                        edge.kind,
                        edge.source_kind,
                        edge.source_module_parts,
                        edge.source_name,
                        edge.target_kind,
                        edge.target_module_parts,
                        edge.target_name,
                        edge.label,
                    ),
                )
            ),
        )

    def _collect_flow_from_workflow_body(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        workflow_unit: IndexedUnit,
        agent_unit: IndexedUnit,
        agent: model.Agent,
        agent_contract: AgentContract,
        agent_nodes: dict[FlowAgentKey, FlowAgentNode],
        agent_notes: dict[FlowAgentKey, list[str]],
        input_notes: dict[FlowArtifactKey, list[str]],
        output_nodes: dict[FlowArtifactKey, FlowOutputNode],
        output_notes: dict[FlowArtifactKey, list[str]],
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ],
        owner_label: str,
        workflow_stack: tuple[tuple[tuple[str, ...], str], ...],
    ) -> None:
        agent_key = (agent_unit.module_parts, agent.name)

        for item in workflow_body.items:
            if isinstance(item, ResolvedSectionItem):
                self._collect_flow_from_section_items(
                    item.items,
                    agent_key=agent_key,
                    agent_nodes=agent_nodes,
                    edges=edges,
                )
                continue
            if isinstance(item, ResolvedWorkflowSkillsItem):
                continue

            workflow_key = (item.target_unit.module_parts, item.workflow_decl.name)
            if workflow_key in workflow_stack:
                cycle = " -> ".join(
                    ".".join(parts + (name,)) or name
                    for parts, name in [*workflow_stack, workflow_key]
                )
                raise CompileError(f"Cyclic workflow composition: {cycle}")

            self._collect_flow_from_workflow_body(
                self._resolve_workflow_decl(item.workflow_decl, unit=item.target_unit),
                workflow_unit=item.target_unit,
                agent_unit=agent_unit,
                agent=agent,
                agent_contract=agent_contract,
                agent_nodes=agent_nodes,
                agent_notes=agent_notes,
                input_notes=input_notes,
                output_nodes=output_nodes,
                output_notes=output_notes,
                edges=edges,
                owner_label=f"workflow {_dotted_decl_name(item.target_unit.module_parts, item.workflow_decl.name)}",
                workflow_stack=(*workflow_stack, workflow_key),
            )

        if workflow_body.law is None:
            return

        flat_items = self._flatten_law_items(workflow_body.law, owner_label=owner_label)
        self._validate_workflow_law(
            flat_items,
            unit=workflow_unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )
        branches = self._collect_law_leaf_branches(flat_items, unit=workflow_unit)
        if not branches:
            branches = (LawBranch(),)

        for branch in branches:
            current = branch.current_subjects[0] if branch.current_subjects else None
            if isinstance(current, model.CurrentNoneStmt):
                self._flow_append_note(
                    agent_notes,
                    agent_key,
                    "May end with no current artifact",
                )
            elif isinstance(current, model.CurrentArtifactStmt):
                target = self._validate_law_path_root(
                    current.target,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="current artifact",
                    allowed_kinds=("input", "output"),
                )
                if target.remainder or target.wildcard:
                    raise CompileError(
                        "current artifact must stay rooted at one input or output artifact in "
                        f"{owner_label}: {'.'.join(current.target.parts)}"
                    )
                carrier = self._validate_carrier_path(
                    current.carrier,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="current artifact",
                )
                target_label = self._display_readable_decl(target.decl)
                carrier_label = self._flow_carrier_label(
                    carrier,
                    owner_label=owner_label,
                )
                self._flow_append_artifact_note(
                    input_notes=input_notes,
                    output_notes=output_notes,
                    resolved=target,
                    note=f"Current via {carrier_label}",
                )
                self._flow_append_note(
                    output_notes,
                    (carrier.unit.module_parts, carrier.decl.name),
                    f"Carries current for {target_label}",
                )

            for invalidate in branch.invalidations:
                target = self._validate_law_path_root(
                    invalidate.target,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="invalidate",
                    allowed_kinds=("input", "output"),
                )
                if target.remainder or target.wildcard:
                    raise CompileError(
                        f"invalidate must name one full input or output artifact in {owner_label}: "
                        f"{'.'.join(invalidate.target.parts)}"
                    )
                carrier = self._validate_carrier_path(
                    invalidate.carrier,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="invalidate",
                )
                target_label = self._display_readable_decl(target.decl)
                carrier_label = self._flow_carrier_label(
                    carrier,
                    owner_label=owner_label,
                )
                self._flow_append_artifact_note(
                    input_notes=input_notes,
                    output_notes=output_notes,
                    resolved=target,
                    note=f"Invalidated via {carrier_label}",
                )
                self._flow_append_note(
                    output_notes,
                    (carrier.unit.module_parts, carrier.decl.name),
                    f"Carries invalidation for {target_label}",
                )

            for route in branch.routes:
                route_label = self._interpolate_authored_prose_string(
                    route.label,
                    unit=workflow_unit,
                    owner_label=owner_label,
                    surface_label="route labels",
                )
                target_unit, target_agent = self._resolve_agent_ref(route.target, unit=workflow_unit)
                self._flow_upsert_agent_node(agent_nodes, target_agent, unit=target_unit)
                self._flow_add_edge(
                    edges,
                    FlowEdge(
                        kind="law_route",
                        source_kind="agent",
                        source_module_parts=agent_key[0],
                        source_name=agent_key[1],
                        target_kind="agent",
                        target_module_parts=target_unit.module_parts,
                        target_name=target_agent.name,
                        label=route_label,
                    ),
                )

        for output_key, (output_unit, output_decl) in sorted(agent_contract.outputs.items()):
            if output_key not in output_nodes:
                self._flow_upsert_output_node(output_nodes, output_decl, unit=output_unit)

    def _collect_flow_from_section_items(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        agent_key: FlowAgentKey,
        agent_nodes: dict[FlowAgentKey, FlowAgentNode],
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ],
    ) -> None:
        for item in items:
            if isinstance(item, ResolvedSectionItem):
                self._collect_flow_from_section_items(
                    item.items,
                    agent_key=agent_key,
                    agent_nodes=agent_nodes,
                    edges=edges,
                )
                continue
            if not isinstance(item, ResolvedRouteLine):
                continue
            target_unit = (
                self._load_module(item.target_module_parts)
                if item.target_module_parts
                else self.root_unit
            )
            target_agent = target_unit.agents_by_name.get(item.target_name)
            if target_agent is not None:
                self._flow_upsert_agent_node(agent_nodes, target_agent, unit=target_unit)
            self._flow_add_edge(
                edges,
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=agent_key[0],
                    source_name=agent_key[1],
                    target_kind="agent",
                    target_module_parts=item.target_module_parts,
                    target_name=item.target_name,
                    label=item.label,
                ),
            )

    def _flow_upsert_agent_node(
        self,
        nodes: dict[FlowAgentKey, FlowAgentNode],
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> None:
        key = (unit.module_parts, agent.name)
        if key in nodes:
            return
        nodes[key] = FlowAgentNode(
            module_parts=unit.module_parts,
            name=agent.name,
            title=agent.name,
            detail_lines=self._flow_agent_detail_lines(agent, unit=unit),
        )

    def _flow_upsert_input_node(
        self,
        nodes: dict[FlowArtifactKey, FlowInputNode],
        decl: model.InputDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        key = (unit.module_parts, decl.name)
        if key in nodes:
            return
        nodes[key] = FlowInputNode(
            module_parts=unit.module_parts,
            name=decl.name,
            title=decl.title,
            detail_lines=self._flow_input_detail_lines(decl, unit=unit),
        )

    def _flow_upsert_output_node(
        self,
        nodes: dict[FlowArtifactKey, FlowOutputNode],
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        key = (unit.module_parts, decl.name)
        if key in nodes:
            return
        nodes[key] = FlowOutputNode(
            module_parts=unit.module_parts,
            name=decl.name,
            title=decl.title,
            detail_lines=self._flow_output_detail_lines(decl, unit=unit),
            trust_surface=self._flow_trust_surface_labels(decl, unit=unit),
        )

    def _flow_agent_detail_lines(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, ...]:
        for field in agent.fields:
            if isinstance(field, model.RoleScalar):
                return (
                    self._interpolate_authored_prose_string(
                        field.text,
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                        surface_label="role prose",
                    ),
                )
            if isinstance(field, model.RoleBlock):
                if not field.lines:
                    return (field.title,)
                return (
                    self._interpolate_authored_prose_string(
                        field.lines[0].text if isinstance(field.lines[0], model.EmphasizedLine) else field.lines[0],
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                        surface_label="role prose",
                    ),
                )
        return ()

    def _flow_input_detail_lines(
        self,
        decl: model.InputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, ...]:
        scalar_items, _section_items, _extras = self._split_record_items(
            decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {decl.name}",
        )
        source_item = scalar_items.get("source")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        if source_item is None or not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input source must stay typed: {decl.name}")
        if shape_item is None or requirement_item is None:
            raise CompileError(f"Input is missing required fields: {decl.name}")

        source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
        lines = [f"Source: {source_spec.title}"]
        lines.extend(
            self._flow_config_lines(
                source_item.body or (),
                spec=source_spec,
                unit=unit,
                owner_label=f"input {decl.name} source",
            )
        )
        lines.append(
            f"Shape: {self._display_symbol_value(shape_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        lines.append(
            f"Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        return tuple(lines)

    def _flow_output_detail_lines(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, ...]:
        scalar_items, section_items, _extras = self._split_record_items(
            decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {decl.name}",
        )
        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        lines: list[str] = []
        if files_section is not None:
            lines.extend(
                self._flow_output_files_detail_lines(
                    files_section,
                    unit=unit,
                    output_name=decl.name,
                )
            )
        else:
            if target_item is None or not isinstance(target_item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {decl.name}")
            if shape_item is None:
                raise CompileError(f"Output must define a shape: {decl.name}")
            target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
            lines.append(f"Target: {target_spec.title}")
            lines.extend(
                self._flow_config_lines(
                    target_item.body or (),
                    spec=target_spec,
                    unit=unit,
                    owner_label=f"output {decl.name} target",
                )
            )
            lines.append(
                f"Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {decl.name}', surface_label='output fields')}"
            )

        if requirement_item is not None:
            lines.append(
                f"Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'output {decl.name}', surface_label='output fields')}"
            )
        return tuple(lines)

    def _flow_output_files_detail_lines(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
    ) -> tuple[str, ...]:
        lines: list[str] = ["Target: Files"]
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise CompileError(
                    f"`files` entries must be titled sections in output {output_name}"
                )
            scalar_items, _section_items, _extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise CompileError(
                    f"Output file entry is missing string path in {output_name}: {item.key}"
                )
            if shape_item is None:
                raise CompileError(
                    f"Output file entry is missing shape in {output_name}: {item.key}"
                )
            lines.append(f"{item.title}: {path_item.value}")
            lines.append(
                f"{item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {output_name} file {item.key}', surface_label='output file fields')}"
            )
        return tuple(lines)

    def _flow_config_lines(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[str, ...]:
        lines: list[str] = []
        seen_keys: set[str] = set()
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(f"Config entries must be scalar key/value lines in {owner_label}")
            if item.key in seen_keys:
                raise CompileError(f"Duplicate config key in {owner_label}: {item.key}")
            seen_keys.add(item.key)
            if item.key not in allowed_keys:
                raise CompileError(f"Unknown config key in {owner_label}: {item.key}")
            lines.append(
                f"{allowed_keys[item.key]}: {self._display_scalar_value(item.value, unit=unit, owner_label=f'{owner_label}.{item.key}', surface_label='config values').text}"
            )

        missing_required = [key for key in spec.required_keys if key not in seen_keys]
        if missing_required:
            missing = ", ".join(missing_required)
            raise CompileError(f"Missing required config key in {owner_label}: {missing}")

        return tuple(lines)

    def _flow_trust_surface_labels(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, ...]:
        if not decl.trust_surface:
            return ()
        section = self._compile_trust_surface_section(decl, unit=unit)
        return tuple(
            item[2:]
            for item in section.body
            if isinstance(item, str) and item.startswith("- ")
        )

    def _flow_carrier_label(
        self,
        resolved: ResolvedLawPath,
        *,
        owner_label: str,
    ) -> str:
        if not isinstance(resolved.decl, model.OutputDecl):
            return self._display_readable_decl(resolved.decl)
        field_node = self._resolve_output_field_node(
            resolved.decl,
            path=resolved.remainder,
            unit=resolved.unit,
            owner_label=owner_label,
            surface_label="flow graph",
        )
        field_label = self._display_addressable_target_value(
            field_node,
            owner_label=owner_label,
            surface_label="flow graph",
        ).text
        return f"{resolved.decl.title}.{field_label}"

    def _flow_append_artifact_note(
        self,
        *,
        input_notes: dict[FlowArtifactKey, list[str]],
        output_notes: dict[FlowArtifactKey, list[str]],
        resolved: ResolvedLawPath,
        note: str,
    ) -> None:
        key = (resolved.unit.module_parts, resolved.decl.name)
        if isinstance(resolved.decl, model.InputDecl):
            self._flow_append_note(input_notes, key, note)
            return
        if isinstance(resolved.decl, model.OutputDecl):
            self._flow_append_note(output_notes, key, note)

    def _flow_append_note(
        self,
        notes_by_key: dict[tuple[tuple[str, ...], str], list[str]],
        key: tuple[tuple[str, ...], str],
        note: str,
    ) -> None:
        bucket = notes_by_key.setdefault(key, [])
        if note not in bucket:
            bucket.append(note)

    def _flow_add_edge(
        self,
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ],
        edge: FlowEdge,
    ) -> None:
        key = (
            edge.kind,
            edge.source_kind,
            edge.source_module_parts,
            edge.source_name,
            edge.target_kind,
            edge.target_module_parts,
            edge.target_name,
            edge.label,
        )
        edges.setdefault(key, edge)

    def _compile_agent_decl(self, agent: model.Agent, *, unit: IndexedUnit) -> CompiledAgent:
        self._enforce_legacy_role_workflow_order(agent)
        resolved_slot_states = self._resolve_agent_slots(agent, unit=unit)
        agent_contract = self._resolve_agent_contract(agent, unit=unit)
        unresolved_abstract_slots = [
            slot.key
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAbstractAgentSlot)
        ]
        if unresolved_abstract_slots:
            missing = ", ".join(unresolved_abstract_slots)
            raise CompileError(
                f"E209 Concrete agent is missing abstract authored slots in agent {agent.name}: {missing}"
            )
        resolved_slots = {
            slot.key: slot.body
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAgentSlot)
        }
        has_workflow_slot = "workflow" in resolved_slots
        review_fields = [
            field for field in agent.fields if isinstance(field, model.ReviewField)
        ]
        if has_workflow_slot and review_fields:
            raise CompileError(
                f"Concrete agent may not define both `workflow` and `review`: {agent.name}"
            )
        review_output_contexts = self._review_output_contexts_for_agent(agent, unit=unit)
        field_specs: list[AgentFieldCompileSpec] = []
        seen_role = False
        seen_typed_fields: set[str] = set()

        for field in agent.fields:
            if isinstance(field, model.RoleScalar):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                seen_role = True
                field_specs.append(AgentFieldCompileSpec(field=field))
                continue

            if isinstance(field, model.RoleBlock):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                seen_role = True
                field_specs.append(AgentFieldCompileSpec(field=field))
                continue

            if isinstance(
                field,
                (
                    model.AuthoredSlotField,
                    model.AuthoredSlotAbstract,
                    model.AuthoredSlotInherit,
                    model.AuthoredSlotOverride,
                ),
            ):
                slot_body = resolved_slots.get(field.key)
                if slot_body is None:
                    raise CompileError(
                        f"Internal compiler error: missing resolved authored slot in agent {agent.name}: {field.key}"
                    )
                field_specs.append(AgentFieldCompileSpec(field=field, slot_body=slot_body))
                continue

            field_key = self._typed_field_key(field)
            if field_key in seen_typed_fields:
                raise CompileError(f"Duplicate typed field in agent {agent.name}: {field_key}")
            seen_typed_fields.add(field_key)
            field_specs.append(AgentFieldCompileSpec(field=field))

        if not seen_role:
            raise CompileError(f"Concrete agent is missing role field: {agent.name}")

        compiled_fields = self._compile_agent_fields(
            field_specs,
            agent_name=agent.name,
            unit=unit,
            agent_contract=agent_contract,
            review_output_contexts=review_output_contexts,
        )
        return CompiledAgent(name=agent.name, fields=compiled_fields)

    def _compile_agent_fields(
        self,
        specs: list[AgentFieldCompileSpec],
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
    ) -> tuple[CompiledField, ...]:
        if len(specs) <= 1:
            return tuple(
                self._compile_agent_field(
                    spec,
                    agent_name=agent_name,
                    unit=unit,
                    agent_contract=agent_contract,
                    review_output_contexts=review_output_contexts,
                )
                for spec in specs
            )

        with ThreadPoolExecutor(max_workers=_default_worker_count(len(specs))) as executor:
            futures = [
                executor.submit(
                    self.session._compile_agent_field_task,
                    spec,
                    agent_name=agent_name,
                    unit=unit,
                    agent_contract=agent_contract,
                    review_output_contexts=review_output_contexts,
                )
                for spec in specs
            ]
            return tuple(future.result() for future in futures)

    def _compile_agent_field(
        self,
        spec: AgentFieldCompileSpec,
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
    ) -> CompiledField:
        field = spec.field

        if isinstance(field, model.RoleScalar):
            return model.RoleScalar(
                text=self._interpolate_authored_prose_string(
                    field.text,
                    unit=unit,
                    owner_label=f"agent {agent_name}",
                    surface_label="role prose",
                )
            )

        if isinstance(field, model.RoleBlock):
            return CompiledSection(
                title=field.title,
                body=tuple(
                    self._interpolate_authored_prose_line(
                        line,
                        unit=unit,
                        owner_label=f"agent {agent_name}",
                        surface_label="role prose",
                    )
                    for line in field.lines
                ),
            )

        if isinstance(
            field,
            (
                model.AuthoredSlotField,
                model.AuthoredSlotAbstract,
                model.AuthoredSlotInherit,
                model.AuthoredSlotOverride,
            ),
        ):
            if spec.slot_body is None:
                raise CompileError(
                    f"Internal compiler error: missing resolved authored slot in agent {agent_name}"
                )
            if field.key == "workflow":
                return self._compile_resolved_workflow(
                    spec.slot_body,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=f"agent {agent_name} workflow",
                )
            return self._compile_resolved_workflow(spec.slot_body)

        if isinstance(field, model.InputsField):
            return self._compile_inputs_field(
                field,
                unit=unit,
                owner_label=f"agent {agent_name}",
            )
        if isinstance(field, model.OutputsField):
            return self._compile_outputs_field(
                field,
                unit=unit,
                owner_label=f"agent {agent_name}",
                review_output_contexts=review_output_contexts,
            )
        if isinstance(field, model.SkillsField):
            return self._compile_skills_field(field, unit=unit)
        if isinstance(field, model.ReviewField):
            review_unit, review_decl = self._resolve_review_ref(field.value, unit=unit)
            if review_decl.abstract:
                raise CompileError(
                    "Concrete agents may not attach abstract reviews directly: "
                    f"{_dotted_decl_name(review_unit.module_parts, review_decl.name)}"
                )
            return self._compile_review_decl(
                review_decl,
                unit=review_unit,
                agent_contract=agent_contract,
                owner_label=f"agent {agent_name} review",
            )

        raise CompileError(
            f"Unsupported agent field in {agent_name}: {type(field).__name__}"
        )

    def _review_output_contexts_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> frozenset[tuple[OutputDeclKey, ReviewSemanticContext]]:
        output_contexts: set[tuple[OutputDeclKey, ReviewSemanticContext]] = set()
        for field in agent.fields:
            if not isinstance(field, model.ReviewField):
                continue
            review_unit, review_decl = self._resolve_review_ref(field.value, unit=unit)
            resolved = self._resolve_review_decl(review_decl, unit=review_unit)
            if resolved.comment_output is None:
                continue
            output_unit, output_decl = self._resolve_output_decl(
                resolved.comment_output.output_ref,
                unit=review_unit,
            )
            contract_gates: tuple[ReviewContractGate, ...] = ()
            if resolved.contract is not None:
                try:
                    contract_gates = self._resolve_review_contract_spec(
                        resolved.contract.workflow_ref,
                        unit=review_unit,
                        owner_label=f"review {_dotted_decl_name(review_unit.module_parts, review_decl.name)}",
                    ).gates
                except CompileError:
                    contract_gates = ()
            field_bindings: list[tuple[str, tuple[str, ...]]] = []
            seen_bindings: set[str] = set()
            if resolved.fields is not None:
                for binding in resolved.fields.bindings:
                    if binding.semantic_field in seen_bindings:
                        continue
                    seen_bindings.add(binding.semantic_field)
                    field_bindings.append((binding.semantic_field, binding.field_path))
            output_contexts.add(
                (
                    (output_unit.module_parts, output_decl.name),
                    ReviewSemanticContext(
                        output_module_parts=output_unit.module_parts,
                        output_name=output_decl.name,
                        field_bindings=tuple(field_bindings),
                        contract_gates=contract_gates,
                    ),
                )
            )
        return frozenset(output_contexts)

    def _review_output_context_for_key(
        self,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        output_key: OutputDeclKey,
    ) -> ReviewSemanticContext | None:
        for key, context in review_output_contexts:
            if key == output_key:
                return context
        return None

    def _review_semantic_field_path(
        self,
        review_semantics: ReviewSemanticContext,
        field_name: str,
    ) -> tuple[str, ...] | None:
        for name, path in review_semantics.field_bindings:
            if name == field_name:
                return path
        return None

    def _review_semantic_contract_gate(
        self,
        review_semantics: ReviewSemanticContext,
        gate_key: str,
    ) -> ReviewContractGate | None:
        for gate in review_semantics.contract_gates:
            if gate.key == gate_key:
                return gate
        return None

    def _review_semantic_addressable_parts(
        self,
        ref: model.AddressableRef,
    ) -> tuple[str, ...] | None:
        parts = (*ref.root.module_parts, ref.root.declaration_name, *ref.path)
        if len(parts) < 2 or parts[0] not in {"contract", "fields"}:
            return None
        return parts

    def _resolve_review_semantic_output_decl(
        self,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        if review_semantics.output_module_parts:
            output_unit = self._load_module(review_semantics.output_module_parts)
        else:
            output_unit = self.root_unit
        output_decl = output_unit.outputs_by_name.get(review_semantics.output_name)
        if output_decl is None:
            raise CompileError(
                "Internal compiler error: missing review comment output while resolving "
                f"review semantics: {review_semantics.output_name}"
            )
        return output_unit, output_decl

    def _review_semantic_root_node(
        self,
        root_key: str,
        review_semantics: ReviewSemanticContext,
    ) -> AddressableNode | None:
        if root_key == "fields":
            root = ReviewSemanticFieldsRoot(review_semantics)
        elif root_key == "contract":
            root = ReviewSemanticContractRoot(review_semantics)
        else:
            return None
        output_unit, _output_decl = self._resolve_review_semantic_output_decl(review_semantics)
        return AddressableNode(
            unit=output_unit,
            root_decl=root,
            target=root,
        )

    def _resolve_review_semantic_root_decl(
        self,
        ref: model.NameRef,
        *,
        review_semantics: ReviewSemanticContext | None,
    ) -> ReviewSemanticFieldsRoot | ReviewSemanticContractRoot | None:
        if review_semantics is None or ref.module_parts:
            return None
        node = self._review_semantic_root_node(ref.declaration_name, review_semantics)
        if node is None:
            return None
        target = node.target
        if isinstance(target, (ReviewSemanticFieldsRoot, ReviewSemanticContractRoot)):
            return target
        return None

    def _resolve_review_semantic_node(
        self,
        ref: model.AddressableRef,
        *,
        review_semantics: ReviewSemanticContext | None,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> AddressableNode | None:
        if review_semantics is None:
            return None
        parts = self._review_semantic_addressable_parts(ref)
        if parts is None:
            return None
        root_node = self._review_semantic_root_node(parts[0], review_semantics)
        if root_node is None:
            return None
        return self._resolve_addressable_path_node(
            root_node,
            parts[1:],
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

    def _output_path_has_guarded_section(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
    ) -> bool:
        return bool(self._output_path_guards(output_decl.items, path=path))

    def _typed_field_key(self, field: model.Field) -> str:
        if isinstance(field, model.InputsField):
            return "inputs"
        if isinstance(field, model.OutputsField):
            return "outputs"
        if isinstance(field, model.SkillsField):
            return "skills"
        if isinstance(field, model.ReviewField):
            return "review"
        return type(field).__name__

    def _resolve_agent_contract(self, agent: model.Agent, *, unit: IndexedUnit) -> AgentContract:
        inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]] = {}
        input_bindings_by_path: dict[tuple[str, ...], ContractBinding] = {}
        outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]] = {}
        output_bindings_by_path: dict[tuple[str, ...], ContractBinding] = {}

        for field in agent.fields:
            if isinstance(field, model.InputsField):
                summary = self._summarize_contract_field(
                    field,
                    unit=unit,
                    field_kind="inputs",
                    owner_label=f"agent {agent.name}",
                )
                self._merge_contract_summary(
                    summary,
                    decls_sink=inputs,
                    bindings_sink=input_bindings_by_path,
                )
            elif isinstance(field, model.OutputsField):
                summary = self._summarize_contract_field(
                    field,
                    unit=unit,
                    field_kind="outputs",
                    owner_label=f"agent {agent.name}",
                )
                self._merge_contract_summary(
                    summary,
                    decls_sink=outputs,
                    bindings_sink=output_bindings_by_path,
                )

        return AgentContract(
            inputs=inputs,
            input_bindings_by_path=input_bindings_by_path,
            outputs=outputs,
            output_bindings_by_path=output_bindings_by_path,
        )

    def _summarize_contract_field(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractBodySummary:
        if field.parent_ref is not None:
            return self._summarize_contract_field_patch(
                field,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
            )
        if isinstance(field.value, tuple):
            inline_owner_label = (
                f"{field_kind} field `{field.title}`" if field.title is not None else owner_label
            )
            return self._summarize_non_inherited_contract_items(
                field.value,
                unit=unit,
                field_kind=field_kind,
                owner_label=inline_owner_label,
            )
        if isinstance(field.value, model.IoBody):
            inline_owner_label = (
                f"{field_kind} field `{field.title}`" if field.title is not None else owner_label
            )
            return self._summarize_contract_io_body(
                field.value,
                unit=unit,
                field_kind=field_kind,
                owner_label=inline_owner_label,
            )
        if isinstance(field.value, model.NameRef):
            return self._summarize_contract_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
            )
        raise CompileError(
            f"Internal compiler error: unsupported {field_kind} field value in {owner_label}: "
            f"{type(field.value).__name__}"
        )

    def _merge_contract_summary(
        self,
        body: ContractBodySummary,
        *,
        decls_sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl | model.OutputDecl]],
        bindings_sink: dict[tuple[str, ...], ContractBinding],
    ) -> None:
        for artifact in body.artifacts:
            decls_sink[(artifact.unit.module_parts, artifact.decl.name)] = (
                artifact.unit,
                artifact.decl,
            )
        for binding in body.bindings:
            existing = bindings_sink.get(binding.binding_path)
            if existing is None:
                bindings_sink[binding.binding_path] = binding
                continue
            if (
                existing.artifact.kind != binding.artifact.kind
                or existing.artifact.unit.module_parts != binding.artifact.unit.module_parts
                or existing.artifact.decl.name != binding.artifact.decl.name
            ):
                raise CompileError(
                    "Conflicting concrete-turn binding roots resolve different artifacts: "
                    f"{'.'.join(binding.binding_path)}"
                )

    def _summarize_contract_field_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
    ) -> ContractBodySummary:
        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(ref)}"
                )
            target_unit, inputs_decl = self._resolve_inputs_block_ref(ref, unit=unit)
            return self._summarize_contract_io_body(
                inputs_decl.body,
                unit=target_unit,
                field_kind=field_kind,
                owner_label=_dotted_decl_name(target_unit.module_parts, inputs_decl.name),
                parent_ref=inputs_decl.parent_ref,
            )

        if self._ref_exists_in_registry(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(ref)}"
            )
        target_unit, outputs_decl = self._resolve_outputs_block_ref(ref, unit=unit)
        return self._summarize_contract_io_body(
            outputs_decl.body,
            unit=target_unit,
            field_kind=field_kind,
            owner_label=_dotted_decl_name(target_unit.module_parts, outputs_decl.name),
            parent_ref=outputs_decl.parent_ref,
        )

    def _summarize_contract_field_patch(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractBodySummary:
        parent_ref = field.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing parent ref in {owner_label}"
            )
        if not isinstance(field.value, model.IoBody):
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing body in {owner_label}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs patch fields must inherit from inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
        else:
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="inputs_blocks_by_name",
            ):
                raise CompileError(
                    "Outputs patch fields must inherit from outputs blocks, not inputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
        return self._summarize_contract_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_ref=parent_ref,
        )

    def _summarize_contract_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_ref: model.NameRef | None = None,
    ) -> ContractBodySummary:
        if parent_ref is None:
            return self._summarize_non_inherited_contract_items(
                io_body.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
            )

        parent_summary: ContractBodySummary
        parent_label: str
        if field_kind == "inputs":
            parent_unit, parent_decl = self._resolve_inputs_block_ref(parent_ref, unit=unit)
            parent_summary = self._summarize_contract_io_body(
                parent_decl.body,
                unit=parent_unit,
                field_kind=field_kind,
                owner_label=_dotted_decl_name(parent_unit.module_parts, parent_decl.name),
                parent_ref=parent_decl.parent_ref,
            )
            parent_label = f"inputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
        else:
            parent_unit, parent_decl = self._resolve_outputs_block_ref(parent_ref, unit=unit)
            parent_summary = self._summarize_contract_io_body(
                parent_decl.body,
                unit=parent_unit,
                field_kind=field_kind,
                owner_label=_dotted_decl_name(parent_unit.module_parts, parent_decl.name),
                parent_ref=parent_decl.parent_ref,
            )
            parent_label = f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

        if parent_summary.unkeyed_artifacts:
            details = ", ".join(
                self._display_readable_decl(artifact.decl)
                for artifact in parent_summary.unkeyed_artifacts
            )
            raise CompileError(
                f"Cannot inherit {field_kind} block with unkeyed top-level refs in {parent_label}: {details}"
            )

        parent_items_by_key = {item.key: item for item in parent_summary.keyed_items}
        resolved_items: list[ContractSectionSummary] = []
        unkeyed_artifacts: list[ContractArtifact] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in io_body.items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            if isinstance(item, model.RecordRef):
                unkeyed_artifacts.append(
                    self._resolve_contract_artifact_ref(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._summarize_contract_section(
                        key=key,
                        items=item.items,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=f"{field_kind} section `{item.title}`",
                        binding_path=(key,),
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined {field_kind} entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined {field_kind} entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if not isinstance(item, model.OverrideIoSection):
                raise CompileError(
                    f"Internal compiler error: unsupported {field_kind} override in {owner_label}: {type(item).__name__}"
                )
            resolved_items.append(
                self._summarize_contract_section(
                    key=key,
                    items=item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=(
                        f"{field_kind} section `{item.title if item.title is not None else key}`"
                    ),
                    binding_path=(key,),
                )
            )

        missing_keys = [
            item.key for item in parent_summary.keyed_items if item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited {field_kind} entry in {owner_label}: {missing}"
            )

        artifacts = [*unkeyed_artifacts]
        bindings: list[ContractBinding] = []
        for item in resolved_items:
            artifacts.extend(item.artifacts)
            bindings.extend(item.bindings)
        return ContractBodySummary(
            keyed_items=tuple(resolved_items),
            unkeyed_artifacts=tuple(unkeyed_artifacts),
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
        )

    def _summarize_non_inherited_contract_items(
        self,
        io_items: tuple[model.IoItem, ...] | tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractBodySummary:
        resolved_items: list[ContractSectionSummary] = []
        unkeyed_artifacts: list[ContractArtifact] = []
        seen_keys: set[str] = set()

        for item in io_items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            if isinstance(item, model.RecordRef):
                unkeyed_artifacts.append(
                    self._resolve_contract_artifact_ref(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._summarize_contract_section(
                        key=key,
                        items=item.items,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=f"{field_kind} section `{item.title}`",
                        binding_path=(key,),
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited {field_kind} block in {owner_label}: {key}"
            )

        artifacts = [*unkeyed_artifacts]
        bindings: list[ContractBinding] = []
        for item in resolved_items:
            artifacts.extend(item.artifacts)
            bindings.extend(item.bindings)
        return ContractBodySummary(
            keyed_items=tuple(resolved_items),
            unkeyed_artifacts=tuple(unkeyed_artifacts),
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
        )

    def _summarize_contract_section(
        self,
        *,
        key: str,
        items: tuple[model.RecordItem, ...],
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        binding_path: tuple[str, ...],
    ) -> ContractSectionSummary:
        artifacts: list[ContractArtifact] = []
        bindings: list[ContractBinding] = []
        direct_artifacts: list[ContractArtifact] = []
        has_keyed_children = False

        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            if isinstance(item, model.RecordSection):
                has_keyed_children = True
                child = self._summarize_contract_section(
                    key=item.key,
                    items=item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} section `{item.title}`",
                    binding_path=(*binding_path, item.key),
                )
                artifacts.extend(child.artifacts)
                bindings.extend(child.bindings)
                continue
            if isinstance(item, model.RecordRef):
                artifact = self._resolve_contract_artifact_ref(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                )
                artifacts.append(artifact)
                direct_artifacts.append(artifact)
                continue
            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )
            raise CompileError(
                f"Unsupported {field_kind} bucket item in {owner_label}: {type(item).__name__}"
            )

        if not has_keyed_children and len(direct_artifacts) == 1:
            bindings.append(
                ContractBinding(
                    binding_path=binding_path,
                    artifact=direct_artifacts[0],
                )
            )
        return ContractSectionSummary(
            key=key,
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
        )

    def _resolve_contract_artifact_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractArtifact:
        if item.body is not None:
            raise CompileError(
                f"Declaration refs cannot define inline bodies in {owner_label}: "
                f"{_dotted_ref_name(item.ref)}"
            )
        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise CompileError(
                    "Inputs refs must resolve to input declarations, not output declarations: "
                    f"{_dotted_ref_name(item.ref)}"
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return ContractArtifact(kind="input", unit=target_unit, decl=decl)

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise CompileError(
                "Outputs refs must resolve to output declarations, not input declarations: "
                f"{_dotted_ref_name(item.ref)}"
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        return ContractArtifact(kind="output", unit=target_unit, decl=decl)

    def _resolved_io_body_artifacts(
        self,
        items: tuple[ResolvedIoItem, ...],
    ) -> tuple[ContractArtifact, ...]:
        artifacts: list[ContractArtifact] = []
        for item in items:
            if isinstance(item, ResolvedIoSection):
                artifacts.extend(item.artifacts)
            else:
                artifacts.append(item.artifact)
        return tuple(artifacts)

    def _resolved_io_body_bindings(
        self,
        items: tuple[ResolvedIoItem, ...],
    ) -> tuple[ContractBinding, ...]:
        bindings: list[ContractBinding] = []
        for item in items:
            if isinstance(item, ResolvedIoSection):
                bindings.extend(item.bindings)
        return tuple(bindings)

    def _enforce_legacy_role_workflow_order(self, agent: model.Agent) -> None:
        if len(agent.fields) != 2:
            return

        first, second = agent.fields
        if isinstance(first, (model.RoleScalar, model.RoleBlock)):
            return
        if not isinstance(second, (model.RoleScalar, model.RoleBlock)):
            return
        if not isinstance(first, model.AuthoredSlotField) or first.key != "workflow":
            return

        raise CompileError(
            f"Agent {agent.name} is outside the shipped subset: expected `role` followed by `workflow`."
        )

    def _resolve_agent_slots(
        self, agent: model.Agent, *, unit: IndexedUnit
    ) -> tuple[ResolvedAgentSlotState, ...]:
        agent_key = (unit.module_parts, agent.name)
        cached = self._resolved_agent_slot_cache.get(agent_key)
        if cached is not None:
            return cached

        if agent_key in self._agent_slot_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._agent_slot_resolution_stack, agent_key]
            )
            raise CompileError(f"Cyclic agent inheritance: {cycle}")

        self._agent_slot_resolution_stack.append(agent_key)
        try:
            parent_slots: tuple[ResolvedAgentSlotState, ...] = ()
            parent_label: str | None = None
            if agent.parent_ref is not None:
                parent_unit, parent_agent = self._resolve_parent_agent_decl(agent, unit=unit)
                parent_slots = self._resolve_agent_slots(parent_agent, unit=parent_unit)
                parent_label = f"agent {_dotted_decl_name(parent_unit.module_parts, parent_agent.name)}"

            parent_slots_by_key = {slot.key: slot for slot in parent_slots}
            resolved_slots: list[ResolvedAgentSlotState] = []
            seen_slot_keys: set[str] = set()
            accounted_parent_concrete_keys: set[str] = set()

            for field in agent.fields:
                if isinstance(field, model.AuthoredSlotField):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)

                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        if field.key == "workflow" and isinstance(field.value, model.WorkflowBody):
                            resolved_body = self._resolve_workflow_body(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot workflow",
                                parent_workflow=parent_slot.body,
                                parent_label=f"{parent_label} slot workflow",
                            )
                            accounted_parent_concrete_keys.add(field.key)
                            resolved_slots.append(
                                ResolvedAgentSlot(key=field.key, body=resolved_body)
                            )
                            continue
                        raise CompileError(
                            f"Inherited authored slot requires `inherit {field.key}` or `override {field.key}` in agent {agent.name}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        resolved_slots.append(
                            ResolvedAgentSlot(
                                key=field.key,
                                body=self._resolve_slot_value(
                                    field.value,
                                    unit=unit,
                                    owner_label=f"agent {agent.name} slot {field.key}",
                                ),
                            )
                        )
                        continue

                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )
                    continue

                if isinstance(field, model.AuthoredSlotAbstract):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(ResolvedAbstractAgentSlot(key=field.key))
                    continue

                if isinstance(field, model.AuthoredSlotInherit):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"Cannot inherit undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(parent_slot)
                    continue

                if isinstance(field, model.AuthoredSlotOverride):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E001 Cannot override undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )

            missing_parent_keys = [
                parent_slot.key
                for parent_slot in parent_slots
                if isinstance(parent_slot, ResolvedAgentSlot)
                and parent_slot.key not in accounted_parent_concrete_keys
            ]
            if missing_parent_keys:
                missing = ", ".join(missing_parent_keys)
                raise CompileError(
                    f"E003 Missing inherited authored slot in agent {agent.name}: {missing}"
                )

            for parent_slot in parent_slots:
                if (
                    isinstance(parent_slot, ResolvedAbstractAgentSlot)
                    and parent_slot.key not in seen_slot_keys
                ):
                    resolved_slots.append(parent_slot)

            resolved = tuple(resolved_slots)
            self._resolved_agent_slot_cache[agent_key] = resolved
            return resolved
        finally:
            self._agent_slot_resolution_stack.pop()

    def _ensure_valid_authored_slot_key(self, key: str, agent_name: str) -> None:
        if key in _RESERVED_AGENT_FIELD_KEYS:
            raise CompileError(
                f"Reserved typed agent field cannot be used as authored slot in {agent_name}: {key}"
            )

    def _resolve_slot_value(
        self,
        value: model.WorkflowSlotValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedWorkflowBody:
        if isinstance(value, model.WorkflowBody):
            return self._resolve_workflow_body(
                value,
                unit=unit,
                owner_label=owner_label,
            )
        target_unit, workflow_decl = self._resolve_workflow_ref(value, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=target_unit)

    def _compile_inputs_field(
        self,
        field: model.InputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> CompiledSection:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="inputs",
            owner_label=owner_label,
        )

    def _compile_outputs_field(
        self,
        field: model.OutputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> CompiledSection:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="outputs",
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
        )

    def _compile_io_field(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> CompiledSection:
        if field.parent_ref is not None:
            resolved = self._resolve_io_field_patch(
                field,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
                review_output_contexts=review_output_contexts,
            )
            return self._compile_resolved_io_body(resolved)

        if isinstance(field.value, tuple):
            if field.title is None:
                raise CompileError(
                    f"Internal compiler error: {field_kind} field is missing title in {owner_label}"
                )
            return CompiledSection(
                title=field.title,
                body=self._compile_contract_bucket_items(
                    field.value,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} field `{field.title}`",
                    review_output_contexts=review_output_contexts,
                ),
            )

        if isinstance(field.value, model.NameRef):
            resolved = self._resolve_io_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
                review_output_contexts=review_output_contexts,
            )
            return self._compile_resolved_io_body(resolved)

        raise CompileError(
            f"Internal compiler error: unsupported {field_kind} field value in {owner_label}: "
            f"{type(field.value).__name__}"
        )

    def _compile_resolved_io_body(self, io_body: ResolvedIoBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(io_body.preamble)
        for item in io_body.items:
            body.append(item.section)
        return CompiledSection(title=io_body.title, body=tuple(body))

    def _resolve_io_field_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> ResolvedIoBody:
        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(ref)}"
                )
            target_unit, inputs_decl = self._resolve_inputs_block_ref(ref, unit=unit)
            return self._resolve_inputs_decl(inputs_decl, unit=target_unit)

        if self._ref_exists_in_registry(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(ref)}"
            )
        target_unit, outputs_decl = self._resolve_outputs_block_ref(ref, unit=unit)
        return self._resolve_outputs_decl(
            outputs_decl,
            unit=target_unit,
            review_output_contexts=review_output_contexts,
        )

    def _resolve_io_field_patch(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> ResolvedIoBody:
        parent_ref = field.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing parent ref in {owner_label}"
            )
        if not isinstance(field.value, model.IoBody) or field.title is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing body in {owner_label}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs patch fields must inherit from inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_inputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
        else:
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="inputs_blocks_by_name",
            ):
                raise CompileError(
                    "Outputs patch fields must inherit from outputs blocks, not inputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_outputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_outputs_decl(
                parent_decl,
                unit=parent_unit,
                review_output_contexts=review_output_contexts,
            )

        return self._resolve_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_io=parent_body,
            parent_label=f"{field_kind} {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}",
            review_output_contexts=review_output_contexts,
        )

    def _compile_skills_field(
        self, field: model.SkillsField, *, unit: IndexedUnit
    ) -> CompiledSection:
        return self._compile_resolved_skills(
            self._resolve_skills_value(
                field.value,
                unit=unit,
                owner_label="agent skills field",
            )
        )

    def _compile_contract_bucket_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> tuple[CompiledBodyItem, ...]:
        return self._resolve_contract_bucket_items(
            items,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
        ).body

    def _resolve_contract_bucket_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        path_prefix: tuple[str, ...] = (),
    ) -> ResolvedContractBucket:
        body: list[CompiledBodyItem] = []
        artifacts: list[ContractArtifact] = []
        bindings: list[ContractBinding] = []
        direct_artifacts: list[ContractArtifact] = []
        has_keyed_children = False

        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label=f"{field_kind} prose",
                    )
                )
                continue

            if isinstance(item, model.RecordSection):
                has_keyed_children = True
                resolved_section = self._resolve_io_section_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    binding_path=(*path_prefix, item.key),
                    review_output_contexts=review_output_contexts,
                )
                body.append(resolved_section.section)
                artifacts.extend(resolved_section.artifacts)
                bindings.extend(resolved_section.bindings)
                continue

            if isinstance(item, model.RecordRef):
                compiled_section, artifact = self._resolve_contract_bucket_ref_entry(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                    review_output_contexts=review_output_contexts,
                )
                body.append(compiled_section)
                artifacts.append(artifact)
                direct_artifacts.append(artifact)
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            raise CompileError(
                f"Unsupported {field_kind} bucket item in {owner_label}: {type(item).__name__}"
            )

        return ResolvedContractBucket(
            body=tuple(body),
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
            direct_artifacts=tuple(direct_artifacts),
            has_keyed_children=has_keyed_children,
        )

    def _compile_contract_bucket_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> CompiledSection:
        section, _artifact = self._resolve_contract_bucket_ref_entry(
            item,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
        )
        return section

    def _resolve_contract_bucket_ref_entry(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> tuple[CompiledSection, ContractArtifact]:
        if item.body is not None:
            raise CompileError(
                f"Declaration refs cannot define inline bodies in {owner_label}: "
                f"{_dotted_ref_name(item.ref)}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise CompileError(
                    "Inputs refs must resolve to input declarations, not output declarations: "
                    f"{_dotted_ref_name(item.ref)}"
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return (
                self._compile_input_decl(decl, unit=target_unit),
                ContractArtifact(kind="input", unit=target_unit, decl=decl),
            )

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise CompileError(
                "Outputs refs must resolve to output declarations, not input declarations: "
                f"{_dotted_ref_name(item.ref)}"
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        review_semantics = self._review_output_context_for_key(
            review_output_contexts,
            (target_unit.module_parts, decl.name),
        )
        return (
            self._compile_output_decl(
                decl,
                unit=target_unit,
                allow_review_semantics=review_semantics is not None,
                review_semantics=review_semantics,
            ),
            ContractArtifact(kind="output", unit=target_unit, decl=decl),
        )

    def _compile_resolved_skills(self, skills_body: ResolvedSkillsBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(skills_body.preamble)
        for item in skills_body.items:
            if isinstance(item, ResolvedSkillsSection):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_resolved_skills_section_items(item.items),
                    )
                )
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return CompiledSection(title=skills_body.title, body=tuple(body))

    def _compile_resolved_skills_section_items(
        self,
        items: tuple[ResolvedSkillsSectionBodyItem, ...],
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return tuple(body)

    def _compile_resolved_skill_entry(self, entry: ResolvedSkillEntry) -> CompiledSection:
        target_unit = entry.target_unit
        skill_decl = entry.skill_decl
        scalar_items, _section_items, extras = self._split_record_items(
            skill_decl.items,
            scalar_keys={"purpose"},
            owner_label=f"skill {skill_decl.name}",
        )
        purpose_item = scalar_items.get("purpose")
        if purpose_item is None or not isinstance(purpose_item.value, str):
            raise CompileError(f"Skill is missing string purpose: {skill_decl.name}")

        metadata_scalars, _metadata_sections, metadata_extras = self._split_record_items(
            entry.items,
            scalar_keys={"requirement", "reason"},
            owner_label=f"skill reference {skill_decl.name}",
        )

        body: list[CompiledBodyItem] = []
        purpose_body: list[CompiledBodyItem] = [
            self._interpolate_authored_prose_string(
                purpose_item.value,
                unit=target_unit,
                owner_label=f"skill {skill_decl.name}",
                surface_label="skill purpose",
            )
        ]
        requirement = metadata_scalars.get("requirement")
        if (
            requirement is not None
            and self._value_to_symbol(
                requirement.value,
                unit=entry.metadata_unit,
                owner_label=f"skill reference {skill_decl.name}",
                surface_label="skill reference metadata",
            )
            == "Required"
        ):
            purpose_body.extend(
                [
                    "",
                    "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
                ]
            )
        body.append(CompiledSection(title="Purpose", body=tuple(purpose_body)))

        for extra in extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=target_unit,
                    owner_label=f"skill {skill_decl.name}",
                    surface_label="skill prose",
                )
            )

        reason = metadata_scalars.get("reason")
        if reason is not None:
            if not isinstance(reason.value, str):
                raise CompileError(
                    f"Skill reference reason must be a string in {skill_decl.name}"
                )
            body.append(
                CompiledSection(
                    title="Reason",
                    body=(
                        self._interpolate_authored_prose_string(
                            reason.value,
                            unit=entry.metadata_unit,
                            owner_label=f"skill reference {skill_decl.name}",
                            surface_label="skill reason",
                        ),
                    ),
                )
            )

        for extra in metadata_extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=entry.metadata_unit,
                    owner_label=f"skill reference {skill_decl.name}",
                    surface_label="skill reference prose",
                )
            )

        return CompiledSection(title=skill_decl.title, body=tuple(body))

    def _compile_input_decl(self, decl: model.InputDecl, *, unit: IndexedUnit) -> CompiledSection:
        scalar_items, _section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {decl.name}",
        )
        source_item = scalar_items.get("source")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        if source_item is None:
            raise CompileError(f"Input is missing typed source: {decl.name}")
        if not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input source must stay typed: {decl.name}")
        if shape_item is None:
            raise CompileError(f"Input is missing shape: {decl.name}")
        if requirement_item is None:
            raise CompileError(f"Input is missing requirement: {decl.name}")

        source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
        body: list[CompiledBodyItem] = [f"- Source: {source_spec.title}"]
        body.extend(
            self._compile_config_lines(
                source_item.body or (),
                spec=source_spec,
                unit=unit,
                owner_label=f"input {decl.name} source",
            )
        )
        body.append(
            f"- Shape: {self._display_symbol_value(shape_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        body.append(
            f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )

        if extras:
            body.append("")
            body.extend(
                self._compile_record_support_items(
                    extras,
                    unit=unit,
                    owner_label=f"input {decl.name}",
                    surface_label="input prose",
                )
            )

        return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_output_decl(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> CompiledSection:
        self._validate_output_guard_sections(
            decl,
            unit=unit,
            allow_review_semantics=allow_review_semantics,
            review_semantics=review_semantics,
        )
        scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {decl.name}",
        )

        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        if files_section is not None and (target_item is not None or shape_item is not None):
            raise CompileError(
                f"Output mixes `files` with `target` or `shape`: {decl.name}"
            )
        if files_section is None and (target_item is None or shape_item is None):
            raise CompileError(
                f"Output must define either `files` or both `target` and `shape`: {decl.name}"
            )

        body: list[CompiledBodyItem] = []
        if files_section is not None:
            body.extend(
                self._compile_output_files(
                    files_section,
                    unit=unit,
                    output_name=decl.name,
                    review_semantics=review_semantics,
                )
            )
        else:
            if not isinstance(target_item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {decl.name}")
            target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
            body.append(f"- Target: {target_spec.title}")
            body.extend(
                self._compile_config_lines(
                    target_item.body or (),
                    spec=target_spec,
                    unit=unit,
                    owner_label=f"output {decl.name} target",
                )
            )
            body.append(
                f"- Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=decl.name, surface_label='output fields')}"
            )

        if requirement_item is not None:
            body.append(
                f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'output {decl.name}', surface_label='output fields')}"
            )

        trust_surface_section = (
            self._compile_trust_surface_section(decl, unit=unit)
            if decl.trust_surface
            else None
        )

        if extras:
            support_items: list[CompiledBodyItem] = []
            rendered_trust_surface = False
            for item in extras:
                if (
                    trust_surface_section is not None
                    and not rendered_trust_surface
                    and isinstance(item, model.RecordSection)
                    and item.key == "standalone_read"
                ):
                    support_items.append(trust_surface_section)
                    rendered_trust_surface = True
                support_items.extend(
                    self._compile_record_item(
                        item,
                        unit=unit,
                        owner_label=f"output {decl.name}",
                        surface_label="output prose",
                        review_semantics=review_semantics,
                    )
                )
            if trust_surface_section is not None and not rendered_trust_surface:
                support_items.append(trust_surface_section)
            body.append("")
            body.extend(support_items)
        elif trust_surface_section is not None:
            body.append("")
            body.append(trust_surface_section)

        return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> CompiledSection:
        resolved = self._resolve_review_decl(review_decl, unit=unit)
        if resolved.subject is None:
            raise CompileError(f"Review is missing subject: {review_decl.name}")
        if resolved.contract is None:
            raise CompileError(f"Review is missing contract: {review_decl.name}")
        if resolved.comment_output is None:
            raise CompileError(f"Review is missing comment_output: {review_decl.name}")
        if resolved.fields is None:
            raise CompileError(f"Review is missing fields: {review_decl.name}")

        subjects = self._resolve_review_subjects(
            resolved.subject,
            unit=unit,
            owner_label=owner_label,
        )
        subject_keys = {
            (subject_unit.module_parts, subject_decl.name) for subject_unit, subject_decl in subjects
        }
        contract_spec = self._resolve_review_contract_spec(
            resolved.contract.workflow_ref,
            unit=unit,
            owner_label=owner_label,
        )
        comment_output_unit, comment_output_decl = self._resolve_output_decl(
            resolved.comment_output.output_ref,
            unit=unit,
        )
        comment_output_key = (comment_output_unit.module_parts, comment_output_decl.name)
        if comment_output_key not in agent_contract.outputs:
            raise CompileError(
                f"Review comment_output must be emitted by the concrete turn in {owner_label}: "
                f"{comment_output_decl.name}"
            )

        pre_sections: list[model.ReviewSection] = []
        on_accept: model.ReviewOutcomeSection | None = None
        on_reject: model.ReviewOutcomeSection | None = None
        for item in resolved.items:
            if isinstance(item, model.ReviewSection):
                pre_sections.append(item)
                continue
            if item.key == "on_accept":
                on_accept = item
            elif item.key == "on_reject":
                on_reject = item

        if on_accept is None:
            raise CompileError(f"Review is missing on_accept: {review_decl.name}")
        if on_reject is None:
            raise CompileError(f"Review is missing on_reject: {review_decl.name}")

        section_titles = {section.key: section.title for section in pre_sections}
        accept_gate_count = 0
        any_block_gates = False
        for section in pre_sections:
            accept_gate_count += self._count_review_accept_stmts(section.items)
            any_block_gates = any_block_gates or self._review_items_contain_blocks(section.items)
            self._validate_review_pre_outcome_items(
                section.items,
                unit=unit,
                owner_label=f"{owner_label}.{section.key}",
                contract_spec=contract_spec,
                section_titles=section_titles,
                agent_contract=agent_contract,
            )
        if accept_gate_count != 1:
            raise CompileError(
                f"Review must define exactly one accept gate in {owner_label}: found {accept_gate_count}"
            )
        pre_outcome_branches = self._resolve_review_pre_outcome_branches(
            pre_sections,
            unit=unit,
            contract_spec=contract_spec,
            section_titles=section_titles,
            owner_label=owner_label,
        )
        accept_gate_branches = tuple(
            branch for branch in pre_outcome_branches if branch.verdict == _REVIEW_VERDICT_TEXT["accept"]
        )
        reject_gate_branches = tuple(
            branch
            for branch in pre_outcome_branches
            if branch.verdict == _REVIEW_VERDICT_TEXT["changes_requested"]
        )

        carried_fields = {
            field_name
            for field_name in (
                *self._collect_review_carried_fields(on_accept.items),
                *self._collect_review_carried_fields(on_reject.items),
            )
        }
        field_bindings = self._validate_review_field_bindings(
            resolved.fields,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
            require_blocked_gate=any_block_gates,
            require_active_mode="active_mode" in carried_fields,
            require_trigger_reason="trigger_reason" in carried_fields,
        )
        review_semantics = ReviewSemanticContext(
            output_module_parts=comment_output_unit.module_parts,
            output_name=comment_output_decl.name,
            field_bindings=tuple(field_bindings.items()),
            contract_gates=contract_spec.gates,
        )

        accept_branches = self._validate_review_outcome_section(
            on_accept,
            unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=accept_gate_branches,
        )
        reject_branches = self._validate_review_outcome_section(
            on_reject,
            unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=reject_gate_branches,
        )
        _ = accept_branches, reject_branches

        body: list[CompiledBodyItem] = [
            self._render_review_subject_summary(subjects),
            f"Shared review contract: {contract_spec.workflow_body.title}.",
        ]
        for section in pre_sections:
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=section.title,
                    body=self._compile_review_pre_outcome_section_body(
                        section.items,
                        unit=unit,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                        owner_label=f"{owner_label}.{section.key}",
                        review_semantics=review_semantics,
                    ),
                )
            )

        for key, section in (("on_accept", on_accept), ("on_reject", on_reject)):
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=section.title or ("If Accepted" if key == "on_accept" else "If Rejected"),
                    body=self._compile_review_outcome_section_body(
                        section.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                        review_semantics=review_semantics,
                    ),
                )
            )

        return CompiledSection(title=resolved.title, body=tuple(body))

    def _resolve_review_subjects(
        self,
        subject: model.ReviewSubjectConfig,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[IndexedUnit, model.InputDecl | model.OutputDecl], ...]:
        resolved: list[tuple[IndexedUnit, model.InputDecl | model.OutputDecl]] = []
        seen: set[tuple[tuple[str, ...], str]] = set()
        for ref in subject.subjects:
            target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
            input_decl = target_unit.inputs_by_name.get(ref.declaration_name)
            output_decl = target_unit.outputs_by_name.get(ref.declaration_name)
            if input_decl is not None and output_decl is not None:
                raise CompileError(
                    f"Ambiguous review subject in {owner_label}: {_dotted_ref_name(ref)}"
                )
            if input_decl is None and output_decl is None:
                raise CompileError(
                    f"Review subject must resolve to an input or output declaration in {owner_label}: "
                    f"{_dotted_ref_name(ref)}"
                )
            decl = input_decl if input_decl is not None else output_decl
            key = (target_unit.module_parts, decl.name)
            if key in seen:
                raise CompileError(
                    f"Duplicate review subject in {owner_label}: {_dotted_ref_name(ref)}"
                )
            seen.add(key)
            resolved.append((target_unit, decl))
        return tuple(resolved)

    def _resolve_review_contract_spec(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ReviewContractSpec:
        contract_unit, workflow_decl = self._resolve_workflow_ref(ref, unit=unit)
        workflow_body = self._resolve_workflow_decl(workflow_decl, unit=contract_unit)
        gates = self._collect_review_contract_gates(
            workflow_body,
            owner_label=f"{owner_label} contract {_dotted_decl_name(contract_unit.module_parts, workflow_decl.name)}",
        )
        if not gates:
            raise CompileError(
                f"Review contract must export at least one gate in {owner_label}: {workflow_decl.name}"
            )
        return ReviewContractSpec(
            workflow_unit=contract_unit,
            workflow_decl=workflow_decl,
            workflow_body=workflow_body,
            gates=gates,
        )

    def _collect_review_contract_gates(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        owner_label: str,
    ) -> tuple[ReviewContractGate, ...]:
        if workflow_body.law is not None:
            raise CompileError(f"Review contract may not define workflow law in {owner_label}")

        gates: list[ReviewContractGate] = []
        seen: set[str] = set()
        for item in workflow_body.items:
            if isinstance(item, ResolvedWorkflowSkillsItem):
                raise CompileError(f"Review contract may not define skills in {owner_label}")
            if isinstance(item, ResolvedSectionItem):
                if item.key in seen:
                    raise CompileError(f"Duplicate review contract gate in {owner_label}: {item.key}")
                seen.add(item.key)
                gates.append(ReviewContractGate(key=item.key, title=item.title))
                continue
            nested = self._collect_review_contract_gates(
                self._resolve_workflow_decl(item.workflow_decl, unit=item.target_unit),
                owner_label=owner_label,
            )
            for gate in nested:
                if gate.key in seen:
                    raise CompileError(
                        f"Duplicate review contract gate in {owner_label}: {gate.key}"
                    )
                seen.add(gate.key)
                gates.append(gate)
        return tuple(gates)

    def _validate_review_field_bindings(
        self,
        fields: model.ReviewFieldsConfig,
        *,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        owner_label: str,
        require_blocked_gate: bool,
        require_active_mode: bool,
        require_trigger_reason: bool,
    ) -> dict[str, tuple[str, ...]]:
        bindings: dict[str, tuple[str, ...]] = {}
        for binding in fields.bindings:
            if binding.semantic_field in bindings:
                raise CompileError(
                    f"Duplicate review field binding in {owner_label}: {binding.semantic_field}"
                )
            self._resolve_output_field_node(
                output_decl,
                path=binding.field_path,
                unit=output_unit,
                owner_label=owner_label,
                surface_label="review field binding",
            )
            bindings[binding.semantic_field] = binding.field_path

        required = set(_REVIEW_REQUIRED_FIELD_NAMES)
        if require_blocked_gate:
            required.add("blocked_gate")
        if require_active_mode:
            required.add("active_mode")
        if require_trigger_reason:
            required.add("trigger_reason")
        missing = sorted(required - set(bindings))
        if missing:
            raise CompileError(
                f"Review fields are incomplete in {owner_label}: {', '.join(missing)}"
            )
        return bindings

    def _count_review_accept_stmts(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
    ) -> int:
        count = 0
        for item in items:
            if isinstance(item, model.ReviewAcceptStmt):
                count += 1
            elif isinstance(item, model.ReviewPreOutcomeWhenStmt):
                count += self._count_review_accept_stmts(item.items)
            elif isinstance(item, model.ReviewPreOutcomeMatchStmt):
                for case in item.cases:
                    count += self._count_review_accept_stmts(case.items)
        return count

    def _review_items_contain_blocks(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
    ) -> bool:
        for item in items:
            if isinstance(item, model.ReviewBlockStmt):
                return True
            if isinstance(item, model.ReviewPreOutcomeWhenStmt) and self._review_items_contain_blocks(
                item.items
            ):
                return True
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                for case in item.cases:
                    if self._review_items_contain_blocks(case.items):
                        return True
        return False

    def _collect_review_carried_fields(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
    ) -> tuple[str, ...]:
        fields: list[str] = []
        for item in items:
            if isinstance(item, model.ReviewCarryStmt):
                fields.append(item.field_name)
                continue
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                fields.extend(self._collect_review_carried_fields(item.items))
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                for case in item.cases:
                    fields.extend(self._collect_review_carried_fields(case.items))
        return tuple(fields)

    def _validate_review_pre_outcome_items(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        agent_contract: AgentContract,
    ) -> None:
        for item in items:
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                self._validate_review_pre_outcome_items(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    agent_contract=agent_contract,
                )
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                self._validate_review_match_cases(
                    item.cases,
                    unit=unit,
                    owner_label=owner_label,
                )
                for case in item.cases:
                    self._validate_review_pre_outcome_items(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                        agent_contract=agent_contract,
                    )
                continue
            if isinstance(item, (model.ReviewBlockStmt, model.ReviewRejectStmt, model.ReviewAcceptStmt)):
                self._validate_review_gate_label(
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    owner_label=owner_label,
                )
                continue
            if isinstance(item, (model.SupportOnlyStmt, model.IgnoreStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, model.PreserveStmt):
                allowed_kinds = ("enum",) if item.kind == "vocabulary" else ("input", "output")
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=f"preserve {item.kind}",
                    allowed_kinds=allowed_kinds,
                )

    def _validate_review_gate_label(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
    ) -> None:
        if isinstance(gate, model.ContractGateRef):
            if gate.key not in {item.key for item in contract_spec.gates}:
                raise CompileError(
                    f"Unknown review contract gate in {owner_label}: contract.{gate.key}"
                )
            return
        if isinstance(gate, model.SectionGateRef) and gate.key not in section_titles:
            raise CompileError(f"Unknown review section gate in {owner_label}: {gate.key}")

    def _resolve_review_pre_outcome_branches(
        self,
        sections: list[model.ReviewSection],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
    ) -> tuple[ResolvedReviewGateBranch, ...]:
        pre_branches = (ReviewPreOutcomeBranch(),)
        for section in sections:
            section_branches = self._collect_review_pre_section_branches(
                section,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=section_titles,
                owner_label=f"{owner_label}.{section.key}",
            )
            next_branches: list[ReviewPreOutcomeBranch] = []
            for branch in pre_branches:
                for section_branch in section_branches:
                    next_branches.append(
                        ReviewPreOutcomeBranch(
                            block_checks=(*branch.block_checks, *section_branch.block_checks),
                            reject_checks=(*branch.reject_checks, *section_branch.reject_checks),
                            accept_checks=(*branch.accept_checks, *section_branch.accept_checks),
                            assertion_gate_ids=(
                                *branch.assertion_gate_ids,
                                *((section.key,) if section_branch.has_assertions else ()),
                            ),
                        )
                    )
            pre_branches = tuple(next_branches)

        resolved: list[ResolvedReviewGateBranch] = []
        for branch in pre_branches:
            resolved.extend(
                self._resolve_review_gate_branch(
                    branch,
                    unit=unit,
                    contract_spec=contract_spec,
                )
            )
        return tuple(resolved)

    def _collect_review_pre_section_branches(
        self,
        section: model.ReviewSection,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        return self._collect_review_pre_outcome_leaf_branches(
            section.items,
            unit=unit,
            contract_spec=contract_spec,
            section_titles=section_titles,
            owner_label=owner_label,
        )

    def _collect_review_pre_outcome_leaf_branches(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        branch: ReviewPreSectionBranch | None = None,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        branches = (branch or ReviewPreSectionBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                next_branches: list[ReviewPreSectionBranch] = []
                for current_branch in branches:
                    condition = self._evaluate_review_condition(
                        item.expr,
                        unit=unit,
                        branch=ReviewOutcomeBranch(),
                    )
                    if condition is not False:
                        next_branches.extend(
                            self._collect_review_pre_outcome_leaf_branches(
                                item.items,
                                unit=unit,
                                contract_spec=contract_spec,
                                section_titles=section_titles,
                                owner_label=owner_label,
                                branch=current_branch,
                            )
                        )
                    if condition is not True:
                        next_branches.append(current_branch)
                branches = tuple(next_branches)
                index += 1
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                next_branches: list[ReviewPreSectionBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_review_pre_match_branches(
                            item,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
                index += 1
                continue

            next_branches = []
            for current_branch in branches:
                next_branches.append(
                    self._branch_with_review_pre_outcome_stmt(
                        current_branch,
                        item,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                    )
                )
            branches = tuple(next_branches)
            index += 1
        return branches

    def _collect_review_pre_match_branches(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        branch: ReviewPreSectionBranch,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        selected: list[ReviewPreSectionBranch] = []
        pending = [branch]
        empty_branch = ReviewOutcomeBranch()

        for case in stmt.cases:
            next_pending: list[ReviewPreSectionBranch] = []
            for current_branch in pending:
                if case.head is None:
                    selected.extend(
                        self._collect_review_pre_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                    continue
                condition = self._review_match_head_matches(
                    stmt.expr,
                    case.head,
                    unit=unit,
                    branch=empty_branch,
                )
                if condition is not False:
                    selected.extend(
                        self._collect_review_pre_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                if condition is not True:
                    next_pending.append(current_branch)
            pending = next_pending

        if pending and not self._review_pre_match_is_exhaustive(stmt, unit=unit):
            selected.extend(pending)
        return tuple(selected)

    def _review_pre_match_is_exhaustive(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
    ) -> bool:
        outcome_stmt = model.ReviewOutcomeMatchStmt(
            expr=stmt.expr,
            cases=tuple(
                model.ReviewOutcomeMatchArm(head=case.head, items=())
                for case in stmt.cases
            ),
        )
        return self._review_match_is_exhaustive(outcome_stmt, unit=unit)

    def _branch_with_review_pre_outcome_stmt(
        self,
        branch: ReviewPreSectionBranch,
        stmt: model.ReviewPreOutcomeStmt,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> ReviewPreSectionBranch:
        if isinstance(stmt, model.ReviewBlockStmt):
            return replace(
                branch,
                block_checks=(
                    *branch.block_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, model.ReviewRejectStmt):
            return replace(
                branch,
                reject_checks=(
                    *branch.reject_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, model.ReviewAcceptStmt):
            return replace(
                branch,
                accept_checks=(
                    *branch.accept_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, (model.PreserveStmt, model.SupportOnlyStmt, model.IgnoreStmt)):
            return replace(branch, has_assertions=True)
        return branch

    def _resolve_review_gate_branch(
        self,
        branch: ReviewPreOutcomeBranch,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
    ) -> tuple[ResolvedReviewGateBranch, ...]:
        block_states = [tuple[str, ...]()]
        for check in branch.block_checks:
            next_states: list[tuple[str, ...]] = []
            for state in block_states:
                result = self._evaluate_review_gate_condition(
                    check.expr,
                    unit=unit,
                    contract_failed_gate_ids=(),
                )
                if result is not False:
                    next_states.append((*state, check.identity))
                if result is not True:
                    next_states.append(state)
            block_states = next_states

        resolved: list[ResolvedReviewGateBranch] = []
        for block_failed_gate_ids in block_states:
            if block_failed_gate_ids:
                resolved.append(
                    ResolvedReviewGateBranch(
                        verdict=_REVIEW_VERDICT_TEXT["changes_requested"],
                        failing_gate_ids=tuple(block_failed_gate_ids),
                        blocked_gate_id=block_failed_gate_ids[0],
                    )
                )
                continue

            reject_states = [tuple[str, ...]()]
            for check in branch.reject_checks:
                next_reject_states: list[tuple[str, ...]] = []
                for state in reject_states:
                    result = self._evaluate_review_gate_condition(
                        check.expr,
                        unit=unit,
                        contract_failed_gate_ids=(),
                    )
                    if result is not False:
                        next_reject_states.append((*state, check.identity))
                    if result is not True:
                        next_reject_states.append(state)
                reject_states = next_reject_states

            for reject_failed_gate_ids in reject_states:
                assertion_states = [tuple[str, ...]()]
                for assertion_gate_id in branch.assertion_gate_ids:
                    next_assertion_states: list[tuple[str, ...]] = []
                    for state in assertion_states:
                        next_assertion_states.append((*state, assertion_gate_id))
                        next_assertion_states.append(state)
                    assertion_states = next_assertion_states

                for assertion_failed_gate_ids in assertion_states:
                    contract_states = [tuple[str, ...]()]
                    for gate in contract_spec.gates:
                        identity = f"contract.{gate.key}"
                        next_contract_states: list[tuple[str, ...]] = []
                        for state in contract_states:
                            next_contract_states.append((*state, identity))
                            next_contract_states.append(state)
                        contract_states = next_contract_states

                    for contract_failed_gate_ids in contract_states:
                        earlier_failures = (
                            *reject_failed_gate_ids,
                            *assertion_failed_gate_ids,
                            *contract_failed_gate_ids,
                        )
                        if earlier_failures:
                            resolved.append(
                                ResolvedReviewGateBranch(
                                    verdict=_REVIEW_VERDICT_TEXT["changes_requested"],
                                    failing_gate_ids=tuple(earlier_failures),
                                )
                            )
                            continue

                        accept_states = [ResolvedReviewGateBranch(verdict=_REVIEW_VERDICT_TEXT["accept"])]
                        for check in branch.accept_checks:
                            next_accept_states: list[ResolvedReviewGateBranch] = []
                            for state in accept_states:
                                result = self._evaluate_review_gate_condition(
                                    check.expr,
                                    unit=unit,
                                    contract_failed_gate_ids=contract_failed_gate_ids,
                                )
                                if result is not False:
                                    next_accept_states.append(state)
                                if result is not True:
                                    next_accept_states.append(
                                        ResolvedReviewGateBranch(
                                            verdict=_REVIEW_VERDICT_TEXT["changes_requested"],
                                            failing_gate_ids=(check.identity,),
                                        )
                                    )
                            accept_states = next_accept_states
                        resolved.extend(accept_states)

        return tuple(resolved)

    def _evaluate_review_gate_condition(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> bool | None:
        return self._evaluate_review_gate_condition_with_branch(
            expr,
            unit=unit,
            branch=ReviewOutcomeBranch(),
            contract_failed_gate_ids=contract_failed_gate_ids,
        )

    def _evaluate_review_gate_condition_with_branch(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> bool | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._evaluate_review_gate_condition_with_branch(
                    expr.left,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                right = self._evaluate_review_gate_condition_with_branch(
                    expr.right,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if left is False or right is False:
                    return False
                if left is True and right is True:
                    return True
                return None
            if expr.op == "or":
                left = self._evaluate_review_gate_condition_with_branch(
                    expr.left,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                right = self._evaluate_review_gate_condition_with_branch(
                    expr.right,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if left is True or right is True:
                    return True
                if left is False and right is False:
                    return False
                return None

        left = self._resolve_review_gate_expr_constant(
            expr,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        if isinstance(left, bool):
            return left
        if not isinstance(expr, model.ExprBinary):
            return None
        left = self._resolve_review_gate_expr_constant(
            expr.left,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        right = self._resolve_review_gate_expr_constant(
            expr.right,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        if left is None or right is None:
            return None
        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        if expr.op == ">":
            return left > right
        if expr.op == ">=":
            return left >= right
        if expr.op == "<":
            return left < right
        if expr.op == "<=":
            return left <= right
        return None

    def _resolve_review_gate_expr_constant(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> str | int | bool | tuple[str | int | bool, ...] | None:
        if isinstance(expr, (str, int, bool)):
            return expr
        if isinstance(expr, model.ExprSet):
            values: list[str | int | bool] = []
            for item in expr.items:
                value = self._resolve_review_gate_expr_constant(
                    item,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if value is None or isinstance(value, tuple):
                    return None
                values.append(value)
            return tuple(values)
        if isinstance(expr, model.ExprCall):
            if expr.name in {"failed", "passed"} and len(expr.args) == 1:
                gate_identity = self._resolve_review_contract_gate_identity(expr.args[0])
                if gate_identity is None:
                    return None
                is_failed = gate_identity in contract_failed_gate_ids
                return is_failed if expr.name == "failed" else not is_failed
            if (
                expr.name in {"present", "missing"}
                and len(expr.args) == 1
                and isinstance(expr.args[0], model.ExprRef)
                and len(expr.args[0].parts) == 1
            ):
                field_name = expr.args[0].parts[0]
                is_present = any(carry.field_name == field_name for carry in branch.carries)
                return is_present if expr.name == "present" else not is_present
            return None
        if isinstance(expr, model.ExprRef):
            contract_value = self._resolve_review_contract_expr_constant(
                expr,
                contract_failed_gate_ids=contract_failed_gate_ids,
            )
            if contract_value is not None:
                return contract_value
            return self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        if isinstance(expr, model.ExprBinary):
            return self._evaluate_review_gate_condition_with_branch(
                expr,
                unit=unit,
                branch=branch,
                contract_failed_gate_ids=contract_failed_gate_ids,
            )
        return None

    def _resolve_review_contract_gate_identity(self, expr: model.Expr) -> str | None:
        if not isinstance(expr, model.ExprRef):
            return None
        if len(expr.parts) != 2 or expr.parts[0] != "contract":
            return None
        return f"contract.{expr.parts[1]}"

    def _resolve_review_contract_expr_constant(
        self,
        expr: model.ExprRef,
        *,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> str | bool | tuple[str, ...] | None:
        if len(expr.parts) < 2 or expr.parts[0] != "contract":
            return None
        if expr.parts[1] == "passes" and len(expr.parts) == 2:
            return not contract_failed_gate_ids
        if expr.parts[1] == "failed_gates" and len(expr.parts) == 2:
            return contract_failed_gate_ids
        if expr.parts[1] == "first_failed_gate" and len(expr.parts) == 2:
            return contract_failed_gate_ids[0] if contract_failed_gate_ids else None
        return None

    def _validate_review_match_cases(
        self,
        cases: tuple[model.ReviewPreOutcomeMatchArm | model.ReviewOutcomeMatchArm, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if any(case.head is None for case in cases):
            return

        enum_decl: model.EnumDecl | None = None
        seen_members: set[str] = set()
        for case in cases:
            if case.head is None:
                continue
            for option in case.head.options:
                resolved = self._resolve_review_match_option(option, unit=unit)
                if resolved is None:
                    return
                option_enum_decl, member_value = resolved
                if enum_decl is None:
                    enum_decl = option_enum_decl
                elif enum_decl.name != option_enum_decl.name:
                    return
                seen_members.add(member_value)

        if enum_decl is None:
            return

        expected_members = {member.value for member in enum_decl.members}
        if seen_members != expected_members:
            raise CompileError(
                f"Review match must be exhaustive or include else in {owner_label}"
            )

    def _resolve_review_match_option(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> tuple[model.EnumDecl, str] | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 2:
            return None
        enum_ref = _name_ref_from_dotted_name(".".join(expr.parts[:-1]))
        enum_decl = self._try_resolve_enum_decl(enum_ref, unit=unit)
        if enum_decl is None:
            return None
        member = next((member for member in enum_decl.members if member.key == expr.parts[-1]), None)
        if member is None:
            return None
        return enum_decl, member.value

    def _compress_review_gate_branches_for_validation(
        self,
        gate_branches: tuple[ResolvedReviewGateBranch, ...],
        *,
        output_decl: model.OutputDecl,
    ) -> tuple[ResolvedReviewGateBranch, ...]:
        observation = self._review_gate_observation(output_decl)
        deduped: dict[tuple[object, ...], ResolvedReviewGateBranch] = {}
        for branch in gate_branches:
            deduped.setdefault(
                self._review_gate_branch_validation_key(
                    branch,
                    observation=observation,
                ),
                branch,
            )
        return tuple(deduped.values())

    def _review_gate_branch_validation_key(
        self,
        branch: ResolvedReviewGateBranch,
        *,
        observation: ReviewGateObservation,
    ) -> tuple[object, ...]:
        contract_failed_gate_ids = tuple(
            gate_id for gate_id in branch.failing_gate_ids if gate_id.startswith("contract.")
        )
        key: list[object] = [branch.verdict]

        if observation.needs_failing_gates_value:
            key.append(branch.failing_gate_ids)
        elif observation.needs_failing_gates_presence:
            key.append(bool(branch.failing_gate_ids))

        if observation.needs_blocked_gate_value:
            key.append(branch.blocked_gate_id)
        elif observation.needs_blocked_gate_presence:
            key.append(branch.blocked_gate_id is not None)

        if observation.needs_contract_failed_gates_value:
            key.append(contract_failed_gate_ids)
        elif observation.needs_contract_first_failed_gate:
            key.append(contract_failed_gate_ids[0] if contract_failed_gate_ids else None)
        elif observation.needs_contract_passes:
            key.append(not contract_failed_gate_ids)

        if observation.referenced_contract_gate_ids:
            key.append(
                tuple(
                    gate_id in contract_failed_gate_ids
                    for gate_id in observation.referenced_contract_gate_ids
                )
            )

        return tuple(key)

    def _review_gate_observation(self, output_decl: model.OutputDecl) -> ReviewGateObservation:
        flags = {
            "needs_blocked_gate_presence": False,
            "needs_blocked_gate_value": False,
            "needs_failing_gates_presence": False,
            "needs_failing_gates_value": False,
            "needs_contract_failed_gates_value": False,
            "needs_contract_first_failed_gate": False,
            "needs_contract_passes": False,
        }
        referenced_contract_gate_ids: set[str] = set()

        self._collect_review_gate_observation_from_output_items(
            output_decl.items,
            flags=flags,
            referenced_contract_gate_ids=referenced_contract_gate_ids,
        )
        for item in output_decl.trust_surface:
            if item.when_expr is None:
                continue
            self._collect_review_gate_observation_from_expr(
                item.when_expr,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )

        return ReviewGateObservation(
            needs_blocked_gate_presence=flags["needs_blocked_gate_presence"],
            needs_blocked_gate_value=flags["needs_blocked_gate_value"],
            needs_failing_gates_presence=flags["needs_failing_gates_presence"],
            needs_failing_gates_value=flags["needs_failing_gates_value"],
            needs_contract_failed_gates_value=flags["needs_contract_failed_gates_value"],
            needs_contract_first_failed_gate=flags["needs_contract_first_failed_gate"],
            needs_contract_passes=flags["needs_contract_passes"],
            referenced_contract_gate_ids=tuple(sorted(referenced_contract_gate_ids)),
        )

    def _collect_review_gate_observation_from_output_items(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        flags: dict[str, bool],
        referenced_contract_gate_ids: set[str],
    ) -> None:
        for item in items:
            if isinstance(item, model.GuardedOutputSection):
                self._collect_review_gate_observation_from_expr(
                    item.when_expr,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
                self._collect_review_gate_observation_from_output_items(
                    item.items,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
                continue
            if isinstance(item, model.RecordSection):
                self._collect_review_gate_observation_from_output_items(
                    item.items,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
                continue
            if isinstance(item, model.RecordScalar) and item.body is not None:
                self._collect_review_gate_observation_from_output_items(
                    item.body,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )

    def _collect_review_gate_observation_from_expr(
        self,
        expr: model.Expr,
        *,
        flags: dict[str, bool],
        referenced_contract_gate_ids: set[str],
    ) -> None:
        if isinstance(expr, model.ExprBinary):
            self._collect_review_gate_observation_from_expr(
                expr.left,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
            self._collect_review_gate_observation_from_expr(
                expr.right,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
            return

        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._collect_review_gate_observation_from_expr(
                    item,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
            return

        if isinstance(expr, model.ExprCall):
            if expr.name in {"present", "missing"} and len(expr.args) == 1:
                field_name = (
                    self._review_semantic_field_ref_name(expr.args[0])
                    if isinstance(expr.args[0], model.ExprRef)
                    else None
                )
                if field_name == "blocked_gate":
                    flags["needs_blocked_gate_presence"] = True
                elif field_name == "failing_gates":
                    flags["needs_failing_gates_presence"] = True
                return
            if expr.name in {"failed", "passed"} and len(expr.args) == 1:
                gate_identity = self._resolve_review_contract_gate_identity(expr.args[0])
                if gate_identity is not None:
                    referenced_contract_gate_ids.add(gate_identity)
            for arg in expr.args:
                self._collect_review_gate_observation_from_expr(
                    arg,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
            return

        if isinstance(expr, model.ExprRef):
            field_name = self._review_semantic_field_ref_name(expr)
            if field_name == "blocked_gate":
                flags["needs_blocked_gate_value"] = True
                return
            if field_name == "failing_gates":
                flags["needs_failing_gates_value"] = True
                return
            if len(expr.parts) == 2 and expr.parts[0] == "contract":
                if expr.parts[1] == "failed_gates":
                    flags["needs_contract_failed_gates_value"] = True
                elif expr.parts[1] == "first_failed_gate":
                    flags["needs_contract_first_failed_gate"] = True
                elif expr.parts[1] == "passes":
                    flags["needs_contract_passes"] = True

    def _validate_review_outcome_section(
        self,
        section: model.ReviewOutcomeSection,
        *,
        unit: IndexedUnit,
        owner_label: str,
        agent_contract: AgentContract,
        comment_output_decl: model.OutputDecl,
        comment_output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        blocked_gate_required: bool,
        gate_branches: tuple[ResolvedReviewGateBranch, ...],
    ) -> tuple[ResolvedReviewAgreementBranch, ...]:
        self._validate_review_outcome_items(
            section.items,
            unit=unit,
            owner_label=f"{owner_label}.{section.key}",
        )
        gate_branches = self._compress_review_gate_branches_for_validation(
            gate_branches,
            output_decl=comment_output_decl,
        )
        branches = self._collect_review_outcome_leaf_branches(section.items, unit=unit)
        if not branches:
            raise CompileError(f"Review outcome is not total in {owner_label}: {section.key}")

        resolved_branches: list[ResolvedReviewAgreementBranch] = []
        for branch in branches:
            if not branch.currents or not branch.routes:
                raise CompileError(
                    f"Review outcome is not total in {owner_label}: {section.key}"
                )
            if len(branch.routes) > 1:
                raise CompileError(
                    f"Review outcome resolves more than one route in {owner_label}: {section.key}"
                )
            if len(branch.currents) > 1:
                raise CompileError(
                    f"Review outcome resolves more than one currentness result in {owner_label}: {section.key}"
                )

            for gate_branch in gate_branches:
                resolved_branch = self._resolve_review_agreement_branch(
                    branch,
                    section_key=section.key,
                    unit=unit,
                    owner_label=f"{owner_label}.{section.key}",
                    agent_contract=agent_contract,
                    comment_output_decl=comment_output_decl,
                    comment_output_unit=comment_output_unit,
                    field_bindings=field_bindings,
                    subject_keys=subject_keys,
                    subject_map=subject_map,
                    blocked_gate_required=blocked_gate_required,
                    gate_branch=gate_branch,
                )

                branch_proves_subject = self._review_branch_proves_subject(
                    branch,
                    unit=unit,
                    subject_keys=subject_keys,
                    subject_map=subject_map,
                    current_subject_key=resolved_branch.current_subject_key,
                    reviewed_subject_key=resolved_branch.reviewed_subject_key,
                )
                blocked_before_subject_review = (
                    (
                        resolved_branch.blocked_gate_id is not None
                        or (section.key == "on_reject" and blocked_gate_required)
                    )
                    and isinstance(resolved_branch.current, model.ReviewCurrentNoneStmt)
                )
                if len(subject_keys) > 1 and not branch_proves_subject and not blocked_before_subject_review:
                    raise CompileError(
                        f"Review subject set requires disambiguation in {owner_label}: {section.key}"
                    )

                self._validate_review_output_agreement_branch(
                    resolved_branch,
                    unit=unit,
                    output_decl=comment_output_decl,
                    output_unit=comment_output_unit,
                    next_owner_field_path=next_owner_field_path,
                    field_bindings=field_bindings,
                    owner_label=f"{owner_label}.{section.key}",
                )
                resolved_branches.append(resolved_branch)

        return tuple(resolved_branches)

    def _resolve_review_agreement_branch(
        self,
        branch: ReviewOutcomeBranch,
        *,
        section_key: str,
        unit: IndexedUnit,
        owner_label: str,
        agent_contract: AgentContract,
        comment_output_decl: model.OutputDecl,
        comment_output_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        blocked_gate_required: bool,
        gate_branch: ResolvedReviewGateBranch,
    ) -> ResolvedReviewAgreementBranch:
        route = branch.routes[0]
        self._validate_route_target(route.target, unit=unit)

        current = branch.currents[0]
        current_subject_key: tuple[tuple[str, ...], str] | None = None
        if isinstance(current, model.ReviewCurrentArtifactStmt):
            synthetic_current = model.CurrentArtifactStmt(
                target=_law_path_from_name_ref(current.artifact_ref),
                carrier=model.LawPath(parts=current.carrier.parts),
            )
            current_subject_key = self._validate_current_artifact_stmt(
                synthetic_current,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
            )
            if (
                current_subject_key not in subject_keys
                and current_subject_key not in agent_contract.outputs
            ):
                raise CompileError(
                    "Review current artifact must stay rooted in a review subject or emitted "
                    f"output in {owner_label}: {_dotted_ref_name(current.artifact_ref)}"
                )

        carried_values: dict[str, model.ReviewCarryStmt] = {}
        for carry in branch.carries:
            if carry.field_name in carried_values:
                raise CompileError(
                    f"Duplicate carried review field in {owner_label}: {carry.field_name}"
                )
            carried_values[carry.field_name] = carry
            if carry.field_name not in field_bindings:
                raise CompileError(
                    f"Carried review field is missing a binding in {owner_label}: {carry.field_name}"
                )

        return ResolvedReviewAgreementBranch(
            section_key=section_key,
            verdict=gate_branch.verdict,
            route=route,
            current=current,
            current_subject_key=current_subject_key,
            reviewed_subject_key=self._resolve_reviewed_artifact_subject_key(
                current_subject_key=current_subject_key,
                subject_keys=subject_keys,
                subject_map=subject_map,
                branch=branch,
                output_decl=comment_output_decl,
                output_unit=comment_output_unit,
                field_path=field_bindings["reviewed_artifact"],
                owner_label=owner_label,
            ),
            carries=tuple(carried_values.values()),
            requires_failure_detail=bool(gate_branch.failing_gate_ids),
            blocked_gate_required=blocked_gate_required and section_key == "on_reject",
            failing_gate_ids=gate_branch.failing_gate_ids,
            blocked_gate_id=gate_branch.blocked_gate_id,
        )

    def _resolve_reviewed_artifact_subject_key(
        self,
        *,
        current_subject_key: tuple[tuple[str, ...], str] | None,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        branch: ReviewOutcomeBranch,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_path: tuple[str, ...],
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        if current_subject_key in subject_keys:
            return current_subject_key
        if len(subject_keys) == 1:
            return next(iter(subject_keys))
        if subject_map is not None:
            mapped = self._review_subject_key_from_subject_map(
                branch,
                unit=output_unit,
                subject_keys=subject_keys,
                subject_map=subject_map,
            )
            if mapped is not None:
                return mapped

        field_node = self._resolve_output_field_node(
            output_decl,
            path=field_path,
            unit=output_unit,
            owner_label=owner_label,
            surface_label="reviewed_artifact binding",
        )
        referenced_subjects = self._record_item_subject_keys(
            field_node.target,
            subject_keys=subject_keys,
            unit=output_unit,
            owner_label=owner_label,
        )
        if len(referenced_subjects) == 1:
            return referenced_subjects[0]
        return None

    def _review_subject_key_from_subject_map(
        self,
        branch: ReviewOutcomeBranch,
        *,
        unit: IndexedUnit,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig,
    ) -> tuple[tuple[str, ...], str] | None:
        active_mode = next((carry for carry in branch.carries if carry.field_name == "active_mode"), None)
        if active_mode is None:
            return None
        member_value = self._resolve_constant_enum_member(active_mode.expr, unit=unit)
        if member_value is None:
            return None

        mapping: dict[str, tuple[tuple[str, ...], str]] = {}
        for entry in subject_map.entries:
            resolved = self._resolve_review_match_option(
                model.ExprRef(parts=(*entry.enum_member_ref.module_parts, entry.enum_member_ref.declaration_name)),
                unit=unit,
            )
            if resolved is None:
                return None
            _enum_decl, enum_member_value = resolved
            subject_unit, subject_decl = self._resolve_review_subjects(
                model.ReviewSubjectConfig(subjects=(entry.artifact_ref,)),
                unit=unit,
                owner_label="review subject_map",
            )[0]
            mapping[enum_member_value] = (subject_unit.module_parts, subject_decl.name)
        mapped = mapping.get(member_value)
        if mapped in subject_keys:
            return mapped
        return None

    def _record_item_subject_keys(
        self,
        item: AddressableTarget,
        *,
        subject_keys: set[tuple[tuple[str, ...], str]],
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[tuple[str, ...], str], ...]:
        referenced: list[tuple[tuple[str, ...], str]] = []
        seen: set[tuple[tuple[str, ...], str]] = set()

        def add_subject_key(key: tuple[tuple[str, ...], str] | None) -> None:
            if key is None or key not in subject_keys or key in seen:
                return
            seen.add(key)
            referenced.append(key)

        if isinstance(item, model.RecordScalar):
            if isinstance(item.value, model.NameRef):
                add_subject_key(
                    self._review_subject_key_from_name_ref(
                        item.value,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
            elif isinstance(item.value, model.AddressableRef):
                add_subject_key(
                    self._review_subject_key_from_addressable_ref(
                        item.value,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
        for ref in self._iter_record_item_interpolation_refs(item):
            add_subject_key(
                self._review_subject_key_from_addressable_ref(
                    ref,
                    unit=unit,
                    owner_label=owner_label,
                )
            )
        return tuple(referenced)

    def _review_subject_key_from_name_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        try:
            target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        input_decl = target_unit.inputs_by_name.get(ref.declaration_name)
        output_decl = target_unit.outputs_by_name.get(ref.declaration_name)
        if input_decl is None and output_decl is None:
            return None
        if input_decl is not None and output_decl is not None:
            _ = owner_label
            return None
        decl = input_decl if input_decl is not None else output_decl
        return (target_unit.module_parts, decl.name)

    def _review_subject_key_from_addressable_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        try:
            root_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="reviewed_artifact interpolation ref",
                missing_local_label="reviewed_artifact",
            )
        except CompileError:
            return None
        if not isinstance(root_decl, (model.InputDecl, model.OutputDecl)):
            return None
        if ref.path and ref.path not in {("name",), ("title",)}:
            return None
        return (root_unit.module_parts, root_decl.name)

    def _validate_review_output_agreement_branch(
        self,
        branch: ResolvedReviewAgreementBranch,
        *,
        unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
        owner_label: str,
    ) -> None:
        verdict_path = field_bindings["verdict"]
        if not self._review_output_path_is_live(
            output_decl,
            path=verdict_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review verdict field is not live for semantic verdict in "
                f"{owner_label}: {output_decl.name}.{'.'.join(verdict_path)}"
            )

        if not self._review_output_path_is_live(
            output_decl,
            path=next_owner_field_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review next_owner field is not live for routed target in "
                f"{owner_label}: {output_decl.name}.{'.'.join(next_owner_field_path)} -> "
                f"{branch.route.target.declaration_name}"
            )
        self._validate_review_next_owner_binding(
            branch.route,
            output_decl=output_decl,
            output_unit=output_unit,
            field_path=next_owner_field_path,
            owner_label=owner_label,
        )

        if isinstance(branch.current, model.ReviewCurrentArtifactStmt) and not self._review_output_path_is_live(
            output_decl,
            path=branch.current.carrier.parts,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review current artifact carrier field is not live for semantic currentness in "
                f"{owner_label}: {output_decl.name}.{'.'.join(branch.current.carrier.parts)}"
            )

        for carry in branch.carries:
            bound_path = field_bindings[carry.field_name]
            if not self._review_output_path_is_live(
                output_decl,
                path=bound_path,
                unit=output_unit,
                branch=branch,
            ) or not self._review_trust_surface_path_is_live(
                output_decl,
                path=bound_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review carried field is not live when semantic value exists in "
                    f"{owner_label}: {carry.field_name} -> {output_decl.name}.{'.'.join(bound_path)}"
                )

        failing_gates_path = field_bindings["failing_gates"]
        if branch.requires_failure_detail:
            if not self._review_output_path_has_matching_failure_guard(
                output_decl,
                path=failing_gates_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review conditional output field is not aligned with resolved review semantics "
                    f"in {owner_label}: failing_gates -> {output_decl.name}.{'.'.join(failing_gates_path)}"
                )
            if branch.blocked_gate_required:
                blocked_gate_path = field_bindings["blocked_gate"]
                if not self._review_output_path_has_matching_failure_guard(
                    output_decl,
                    path=blocked_gate_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    raise CompileError(
                        "Review conditional output field is not aligned with resolved review semantics "
                        f"in {owner_label}: blocked_gate -> {output_decl.name}.{'.'.join(blocked_gate_path)}"
                    )
        elif self._review_output_path_is_live(
            output_decl,
            path=failing_gates_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review conditional output field is not aligned with resolved review semantics "
                f"in {owner_label}: failing_gates -> {output_decl.name}.{'.'.join(failing_gates_path)}"
            )

    def _review_output_path_is_live(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        status, _has_guards = self._review_output_path_guard_status(
            output_decl,
            path=path,
            unit=unit,
            branch=branch,
        )
        return status is True

    def _review_output_path_has_matching_failure_guard(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        status, has_guards = self._review_output_path_guard_status(
            output_decl,
            path=path,
            unit=unit,
            branch=branch,
        )
        return has_guards and status is True

    def _review_trust_surface_path_is_live(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        statuses: list[bool | None] = []
        for item in output_decl.trust_surface:
            if item.path != path:
                continue
            if item.when_expr is None:
                return True
            statuses.append(
                self._evaluate_review_semantic_guard(
                    item.when_expr,
                    unit=unit,
                    branch=branch,
                )
            )
        if not statuses:
            return False
        if any(status is True for status in statuses):
            return True
        return False

    def _review_output_path_guard_status(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> tuple[bool | None, bool]:
        guards = self._output_path_guards(output_decl.items, path=path)
        if not guards:
            return True, False
        seen_unknown = False
        for guard in guards:
            status = self._evaluate_review_semantic_guard(
                guard,
                unit=unit,
                branch=branch,
            )
            if status is False:
                return False, True
            if status is None:
                seen_unknown = True
        return (None if seen_unknown else True), True

    def _output_path_guards(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        path: tuple[str, ...],
    ) -> tuple[model.Expr, ...]:
        guards: list[model.Expr] = []
        current_items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...] = items
        for segment in path:
            matched_item: model.AnyRecordItem | None = None
            for item in current_items:
                if isinstance(item, (model.RecordSection, model.GuardedOutputSection, model.RecordScalar)):
                    if item.key == segment:
                        matched_item = item
                        break
            if matched_item is None:
                break
            if isinstance(matched_item, model.GuardedOutputSection):
                guards.append(matched_item.when_expr)
                current_items = matched_item.items
                continue
            if isinstance(matched_item, model.RecordSection):
                current_items = matched_item.items
                continue
            if isinstance(matched_item, model.RecordScalar) and matched_item.body is not None:
                current_items = matched_item.body
                continue
            current_items = ()
        return tuple(guards)

    def _evaluate_review_semantic_guard(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._evaluate_review_semantic_guard(expr.left, unit=unit, branch=branch)
                right = self._evaluate_review_semantic_guard(expr.right, unit=unit, branch=branch)
                if left is False or right is False:
                    return False
                if left is True and right is True:
                    return True
                return None
            if expr.op == "or":
                left = self._evaluate_review_semantic_guard(expr.left, unit=unit, branch=branch)
                right = self._evaluate_review_semantic_guard(expr.right, unit=unit, branch=branch)
                if left is True or right is True:
                    return True
                if left is False and right is False:
                    return False
                return None

        if not isinstance(expr, model.ExprBinary):
            constant = self._resolve_review_semantic_expr_constant(expr, unit=unit, branch=branch)
            if isinstance(constant, bool):
                return constant
            return None

        left = self._resolve_review_semantic_expr_constant(expr.left, unit=unit, branch=branch)
        right = self._resolve_review_semantic_expr_constant(expr.right, unit=unit, branch=branch)
        if left is None or right is None:
            return None
        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        return None

    def _resolve_review_semantic_expr_constant(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> str | int | bool | tuple[str | int | bool, ...] | None:
        if isinstance(expr, (str, int, bool)):
            return expr
        if isinstance(expr, model.ExprSet):
            values: list[str | int | bool] = []
            for item in expr.items:
                value = self._resolve_review_semantic_expr_constant(
                    item,
                    unit=unit,
                    branch=branch,
                )
                if value is None or isinstance(value, tuple):
                    return None
                values.append(value)
            return tuple(values)
        if isinstance(expr, model.ExprCall):
            if expr.name in {"present", "missing"} and len(expr.args) == 1 and isinstance(
                expr.args[0], model.ExprRef
            ):
                field_name = self._review_semantic_field_ref_name(expr.args[0])
                if field_name is not None:
                    present = self._review_semantic_field_present(
                        field_name,
                        unit=unit,
                        branch=branch,
                    )
                    if present is None:
                        return None
                    return present if expr.name == "present" else not present
            if expr.name in {"failed", "passed"} and len(expr.args) == 1:
                gate_identity = self._resolve_review_contract_gate_identity(expr.args[0])
                if gate_identity is None:
                    return None
                contract_failed_gate_ids = tuple(
                    gate_id
                    for gate_id in branch.failing_gate_ids
                    if gate_id.startswith("contract.")
                )
                is_failed = gate_identity in contract_failed_gate_ids
                return is_failed if expr.name == "failed" else not is_failed
            return None
        if isinstance(expr, model.ExprRef):
            contract_failed_gate_ids = tuple(
                gate_id
                for gate_id in branch.failing_gate_ids
                if gate_id.startswith("contract.")
            )
            contract_value = self._resolve_review_contract_expr_constant(
                expr,
                contract_failed_gate_ids=contract_failed_gate_ids,
            )
            if contract_value is not None:
                return contract_value
            field_name = self._review_semantic_field_ref_name(expr)
            if field_name is not None:
                return self._review_semantic_ref_value(
                    field_name,
                    unit=unit,
                    branch=branch,
                )
            return self._resolve_constant_enum_member(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            return self._evaluate_review_semantic_guard(expr, unit=unit, branch=branch)
        return None

    def _review_semantic_field_present(
        self,
        field_name: str,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool | None:
        if field_name == "current_artifact":
            return isinstance(branch.current, model.ReviewCurrentArtifactStmt)
        if field_name == "blocked_gate":
            return branch.blocked_gate_required
        return self._review_semantic_ref_value(
            field_name,
            unit=unit,
            branch=branch,
        ) is not None

    def _review_semantic_field_ref_name(self, ref: model.ExprRef) -> str | None:
        if len(ref.parts) == 1:
            return ref.parts[0]
        if len(ref.parts) == 2 and ref.parts[0] == "fields":
            return ref.parts[1]
        return None

    def _review_semantic_ref_value(
        self,
        field_name: str,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> str | None:
        if field_name == "verdict":
            return branch.verdict
        if field_name == "next_owner":
            return branch.route.target.declaration_name
        if field_name == "current_artifact":
            if branch.current_subject_key is None:
                return None
            module_parts, decl_name = branch.current_subject_key
            return _dotted_decl_name(module_parts, decl_name)
        if field_name == "reviewed_artifact":
            if branch.reviewed_subject_key is None:
                return None
            module_parts, decl_name = branch.reviewed_subject_key
            return _dotted_decl_name(module_parts, decl_name)
        if field_name == "failing_gates":
            return ",".join(branch.failing_gate_ids) if branch.failing_gate_ids else None
        if field_name == "blocked_gate":
            return branch.blocked_gate_id
        for carry in reversed(branch.carries):
            if carry.field_name == field_name:
                if isinstance(carry.expr, model.ExprRef):
                    return self._resolve_constant_enum_member(carry.expr, unit=unit) or ".".join(carry.expr.parts)
                resolved = self._resolve_constant_enum_member(carry.expr, unit=unit)
                if resolved is not None:
                    return resolved
                if isinstance(carry.expr, str):
                    return carry.expr
        return None

    def _validate_review_outcome_items(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        for item in items:
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                self._validate_review_outcome_items(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                )
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                self._validate_review_match_cases(
                    item.cases,
                    unit=unit,
                    owner_label=owner_label,
                )
                for case in item.cases:
                    self._validate_review_outcome_items(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                    )
                continue
            if isinstance(item, model.ReviewOutcomeRouteStmt):
                self._validate_route_target(item.target, unit=unit)

    def _collect_review_outcome_leaf_branches(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch | None = None,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        branches = (branch or ReviewOutcomeBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                next_branches: list[ReviewOutcomeBranch] = []
                for current_branch in branches:
                    condition = self._evaluate_review_condition(
                        item.expr,
                        unit=unit,
                        branch=current_branch,
                    )
                    if condition is not False:
                        next_branches.extend(
                            self._collect_review_outcome_leaf_branches(
                                item.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                    if condition is not True:
                        next_branches.append(current_branch)
                branches = tuple(next_branches)
            elif isinstance(item, model.ReviewOutcomeMatchStmt):
                next_branches: list[ReviewOutcomeBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_review_outcome_match_branches(
                            item,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
            else:
                next_branches = []
                for current_branch in branches:
                    next_branches.extend(
                        self._branch_with_review_outcome_stmt(
                            current_branch,
                            item,
                            unit=unit,
                        )
                    )
                branches = tuple(next_branches)
            index += 1
        return branches

    def _branch_with_review_outcome_stmt(
        self,
        branch: ReviewOutcomeBranch,
        stmt: model.ReviewOutcomeStmt,
        *,
        unit: IndexedUnit,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        if isinstance(stmt, (model.ReviewCurrentArtifactStmt, model.ReviewCurrentNoneStmt)):
            return (replace(branch, currents=(*branch.currents, stmt)),)
        if isinstance(stmt, model.ReviewCarryStmt):
            return (replace(branch, carries=(*branch.carries, stmt)),)
        if isinstance(stmt, model.ReviewOutcomeRouteStmt):
            if branch.route_selected:
                return (branch,)
            if stmt.when_expr is None:
                return (
                    replace(
                        branch,
                        routes=(*branch.routes, stmt),
                        route_selected=True,
                    ),
                )
            condition = self._evaluate_review_condition(
                stmt.when_expr,
                unit=unit,
                branch=branch,
            )
            if condition is True:
                return (
                    replace(
                        branch,
                        routes=(*branch.routes, stmt),
                        route_selected=True,
                    ),
                )
            if condition is False:
                return (branch,)
            return (
                replace(
                    branch,
                    routes=(*branch.routes, stmt),
                    route_selected=True,
                ),
                branch,
            )
        return (branch,)

    def _collect_review_outcome_match_branches(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        selected: list[ReviewOutcomeBranch] = []
        pending = [branch]

        for case in stmt.cases:
            next_pending: list[ReviewOutcomeBranch] = []
            for current_branch in pending:
                if case.head is None:
                    selected.extend(
                        self._collect_review_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                    continue

                condition = self._review_match_head_matches(
                    stmt.expr,
                    case.head,
                    unit=unit,
                    branch=current_branch,
                )
                if condition is not False:
                    selected.extend(
                        self._collect_review_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                if condition is not True:
                    next_pending.append(current_branch)
            pending = next_pending

        if pending and not self._review_match_is_exhaustive(stmt, unit=unit):
            selected.extend(pending)
        return tuple(selected)

    def _review_match_head_matches(
        self,
        expr: model.Expr,
        head: model.ReviewMatchHead,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> bool | None:
        subject_value = self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        matched = False
        saw_unknown_option = False
        if subject_value is None:
            option_result: bool | None = None
        else:
            option_result = False
            for option in head.options:
                option_value = self._resolve_review_expr_constant(option, unit=unit, branch=branch)
                if option_value is None:
                    saw_unknown_option = True
                    continue
                if subject_value == option_value:
                    matched = True
                    option_result = True
                    break
            if not matched and saw_unknown_option:
                option_result = None
        if option_result is False:
            return False
        if head.when_expr is None:
            return option_result
        guard_result = self._evaluate_review_condition(
            head.when_expr,
            unit=unit,
            branch=branch,
        )
        return self._combine_review_condition(option_result, guard_result)

    def _review_match_is_exhaustive(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
    ) -> bool:
        if any(case.head is None for case in stmt.cases):
            return True

        enum_decl: model.EnumDecl | None = None
        seen_members: set[str] = set()
        for case in stmt.cases:
            if case.head is None or case.head.when_expr is not None:
                return False
            for option in case.head.options:
                resolved = self._resolve_review_match_option(option, unit=unit)
                if resolved is None:
                    return False
                option_enum_decl, member_value = resolved
                if enum_decl is None:
                    enum_decl = option_enum_decl
                elif enum_decl.name != option_enum_decl.name:
                    return False
                seen_members.add(member_value)

        if enum_decl is None:
            return False
        return seen_members == {member.value for member in enum_decl.members}

    def _evaluate_review_condition(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> bool | None:
        constant = self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        if isinstance(constant, bool):
            return constant
        if not isinstance(expr, model.ExprBinary):
            return None

        if expr.op == "and":
            left = self._evaluate_review_condition(expr.left, unit=unit, branch=branch)
            right = self._evaluate_review_condition(expr.right, unit=unit, branch=branch)
            if left is False or right is False:
                return False
            if left is True and right is True:
                return True
            return None
        if expr.op == "or":
            left = self._evaluate_review_condition(expr.left, unit=unit, branch=branch)
            right = self._evaluate_review_condition(expr.right, unit=unit, branch=branch)
            if left is True or right is True:
                return True
            if left is False and right is False:
                return False
            return None

        left = self._resolve_review_expr_constant(expr.left, unit=unit, branch=branch)
        right = self._resolve_review_expr_constant(expr.right, unit=unit, branch=branch)
        if left is None or right is None:
            return None

        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        if expr.op == ">":
            return left > right
        if expr.op == ">=":
            return left >= right
        if expr.op == "<":
            return left < right
        if expr.op == "<=":
            return left <= right
        return None

    def _resolve_review_expr_constant(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> str | int | bool | tuple[str | int | bool, ...] | None:
        if isinstance(expr, (str, int, bool)):
            return expr
        if isinstance(expr, model.ExprRef):
            for carry in reversed(branch.carries):
                if len(expr.parts) == 1 and carry.field_name == expr.parts[0]:
                    return self._resolve_review_expr_constant(
                        carry.expr,
                        unit=unit,
                        branch=branch,
                    )
            return self._resolve_constant_enum_member(expr, unit=unit)
        if isinstance(expr, model.ExprSet):
            values: list[str | int | bool] = []
            for item in expr.items:
                value = self._resolve_review_expr_constant(item, unit=unit, branch=branch)
                if value is None or isinstance(value, tuple):
                    return None
                values.append(value)
            return tuple(values)
        if (
            isinstance(expr, model.ExprCall)
            and expr.name in {"present", "missing"}
            and len(expr.args) == 1
            and isinstance(expr.args[0], model.ExprRef)
            and len(expr.args[0].parts) == 1
        ):
            field_name = expr.args[0].parts[0]
            is_present = any(carry.field_name == field_name for carry in branch.carries)
            return is_present if expr.name == "present" else not is_present
        if isinstance(expr, model.ExprBinary):
            return self._evaluate_review_condition(expr, unit=unit, branch=branch)
        return None

    def _combine_review_condition(
        self,
        left: bool | None,
        right: bool | None,
    ) -> bool | None:
        if left is False or right is False:
            return False
        if left is True and right is True:
            return True
        return None

    def _review_membership_contains(
        self,
        container: str | int | bool | tuple[str | int | bool, ...],
        value: str | int | bool,
    ) -> bool:
        if isinstance(container, tuple):
            return value in container
        return value == container

    def _review_branch_proves_subject(
        self,
        branch: ReviewOutcomeBranch,
        *,
        unit: IndexedUnit,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        current_subject_key: tuple[tuple[str, ...], str] | None,
        reviewed_subject_key: tuple[tuple[str, ...], str] | None,
    ) -> bool:
        if current_subject_key is not None and current_subject_key in subject_keys:
            return True
        if reviewed_subject_key is not None and reviewed_subject_key in subject_keys:
            return True
        if subject_map is None:
            return False
        return (
            self._review_subject_key_from_subject_map(
                branch,
                unit=unit,
                subject_keys=subject_keys,
                subject_map=subject_map,
            )
            in subject_keys
        )

    def _validate_review_next_owner_binding(
        self,
        route: model.ReviewOutcomeRouteStmt,
        *,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_path: tuple[str, ...],
        owner_label: str,
    ) -> None:
        route_unit, route_agent = self._resolve_agent_ref(route.target, unit=output_unit)
        field_node = self._resolve_output_field_node(
            output_decl,
            path=field_path,
            unit=output_unit,
            owner_label=owner_label,
            surface_label="review next_owner binding",
        )
        target = field_node.target
        if not isinstance(
            target,
            (model.RecordScalar, model.RecordSection, model.GuardedOutputSection),
        ):
            raise CompileError(
                f"Review next_owner binding must point at an output field in {owner_label}: "
                f"{output_decl.name}.{'.'.join(field_path)}"
            )
        if not self._record_item_mentions_agent(
            target,
            target_unit=route_unit,
            target_agent_name=route_agent.name,
            unit=output_unit,
            owner_label=f"output {output_decl.name}.{'.'.join(field_path)}",
        ):
            raise CompileError(
                f"Review next_owner field must structurally bind the routed target in {owner_label}: "
                f"{output_decl.name}.{'.'.join(field_path)} -> {route_agent.name}"
            )

    def _render_review_subject_summary(
        self,
        subjects: tuple[tuple[IndexedUnit, model.InputDecl | model.OutputDecl], ...],
    ) -> str:
        titles = [decl.title for _unit, decl in subjects]
        if len(titles) == 1:
            return f"Review subject: {titles[0]}."
        return "Review subjects: " + ", ".join(titles[:-1]) + f", and {titles[-1]}."

    def _compile_review_pre_outcome_section_body(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[CompiledBodyItem, ...]:
        lines: list[CompiledBodyItem] = []
        for item in items:
            rendered = self._render_review_pre_outcome_item(
                item,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=section_titles,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
            if not rendered:
                continue
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(rendered)
        return tuple(lines)

    def _render_review_pre_outcome_item(
        self,
        item: model.ReviewPreOutcomeStmt,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return [
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label="review prose",
                    review_semantics=review_semantics,
                )
            ]
        if isinstance(item, model.ReviewPreOutcomeWhenStmt):
            lines: list[CompiledBodyItem] = [
                f"If {self._render_condition_expr(item.expr, unit=unit)}:"
            ]
            for child in item.items:
                rendered = self._render_review_pre_outcome_item(
                    child,
                    unit=unit,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(
                    f"- {line}" if isinstance(line, str) else line
                    for line in rendered
                    if isinstance(line, str)
                )
            return lines
        if isinstance(item, model.ReviewPreOutcomeMatchStmt):
            return self._render_review_pre_outcome_match_stmt(
                item,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=section_titles,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
        if isinstance(item, model.ReviewBlockStmt):
            return [
                self._review_gate_sentence(
                    "Block",
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                )
            ]
        if isinstance(item, model.ReviewRejectStmt):
            return [
                self._review_gate_sentence(
                    "Reject",
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                )
            ]
        if isinstance(item, model.ReviewAcceptStmt):
            return [
                self._review_gate_sentence(
                    "Accept only if",
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                )
            ]
        return list(
            self._render_law_stmt_lines(
                item,
                unit=unit,
                owner_label=owner_label,
                bullet=False,
            )
        )

    def _render_review_pre_outcome_match_stmt(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        lines: list[CompiledBodyItem] = [f"Match {self._render_expr(stmt.expr, unit=unit)}:"]
        for case in stmt.cases:
            heading = "Else:" if case.head is None else f"If {self._render_review_match_head(case.head, unit=unit)}:"
            lines.append(heading)
            for item in case.items:
                rendered = self._render_review_pre_outcome_item(
                    item,
                    unit=unit,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(f"- {line}" for line in rendered if isinstance(line, str))
        return lines

    def _compile_review_outcome_section_body(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[CompiledBodyItem, ...]:
        lines: list[CompiledBodyItem] = []
        for item in items:
            rendered = self._render_review_outcome_item(
                item,
                unit=unit,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
            if not rendered:
                continue
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(rendered)
        return tuple(lines)

    def _render_review_outcome_item(
        self,
        item: model.ReviewOutcomeStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return [
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label="review prose",
                    review_semantics=review_semantics,
                )
            ]
        if isinstance(item, model.ReviewOutcomeWhenStmt):
            lines: list[CompiledBodyItem] = [
                f"If {self._render_condition_expr(item.expr, unit=unit)}:"
            ]
            for child in item.items:
                rendered = self._render_review_outcome_item(
                    child,
                    unit=unit,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(f"- {line}" for line in rendered if isinstance(line, str))
            return lines
        if isinstance(item, model.ReviewOutcomeMatchStmt):
            return self._render_review_outcome_match_stmt(
                item,
                unit=unit,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
        if isinstance(item, model.ReviewCurrentArtifactStmt):
            return [f"Current artifact: {self._display_ref(item.artifact_ref)}."]
        if isinstance(item, model.ReviewCurrentNoneStmt):
            return ["There is no current artifact for this outcome."]
        if isinstance(item, model.ReviewCarryStmt):
            return [
                f"Carry {_humanize_key(item.field_name).lower()}: {self._render_expr(item.expr, unit=unit)}."
            ]
        if isinstance(item, model.ReviewOutcomeRouteStmt):
            text = self._interpolate_authored_prose_string(
                item.label,
                unit=unit,
                owner_label=owner_label,
                surface_label="review prose",
                review_semantics=review_semantics,
            )
            text = text if text.endswith(".") else f"{text}."
            return [text]
        return []

    def _render_review_outcome_match_stmt(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        lines: list[CompiledBodyItem] = [f"Match {self._render_expr(stmt.expr, unit=unit)}:"]
        for case in stmt.cases:
            heading = "Else:" if case.head is None else f"If {self._render_review_match_head(case.head, unit=unit)}:"
            lines.append(heading)
            for item in case.items:
                rendered = self._render_review_outcome_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(f"- {line}" for line in rendered if isinstance(line, str))
        return lines

    def _render_review_match_head(
        self,
        head: model.ReviewMatchHead,
        *,
        unit: IndexedUnit,
    ) -> str:
        options = " or ".join(self._render_expr(option, unit=unit) for option in head.options)
        if head.when_expr is None:
            return options
        return f"{options} when {self._render_condition_expr(head.when_expr, unit=unit)}"

    def _review_gate_sentence(
        self,
        prefix: str,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        gate_text = self._review_gate_text(
            gate,
            contract_spec=contract_spec,
            section_titles=section_titles,
        )
        gate_text = gate_text.rstrip(".")
        if prefix.endswith("if"):
            return f"{prefix} {gate_text}."
        return f"{prefix}: {gate_text}."

    def _review_gate_text(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        if isinstance(gate, str):
            return gate
        if isinstance(gate, model.ContractGateRef):
            for item in contract_spec.gates:
                if item.key == gate.key:
                    return item.title
            return f"contract.{gate.key}"
        return section_titles.get(gate.key, gate.key)

    def _review_gate_identity(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        if isinstance(gate, str):
            return gate
        if isinstance(gate, model.ContractGateRef):
            _ = contract_spec
            return f"contract.{gate.key}"
        _ = section_titles
        return gate.key

    def _validate_output_guard_sections(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> None:
        self._validate_output_record_items(
            decl.items,
            decl=decl,
            unit=unit,
            owner_label=f"output {decl.name}",
            allow_review_semantics=allow_review_semantics,
            review_semantics=review_semantics,
        )
        for item in decl.trust_surface:
            if item.when_expr is None:
                continue
            self._validate_output_guard_expr(
                item.when_expr,
                decl=decl,
                unit=unit,
                owner_label=f"output {decl.name}.trust_surface",
                allow_review_semantics=allow_review_semantics,
                review_semantics=review_semantics,
            )
        self._validate_standalone_read_guard_contract(
            decl,
            unit=unit,
            review_semantics=review_semantics,
        )

    def _validate_output_record_items(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> None:
        for item in items:
            if isinstance(item, model.GuardedOutputSection):
                self._validate_output_guard_expr(
                    item.when_expr,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    review_semantics=review_semantics,
                )
                self._validate_output_record_items(
                    item.items,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    review_semantics=review_semantics,
                )
                continue
            if isinstance(item, model.RecordSection):
                self._validate_output_record_items(
                    item.items,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    review_semantics=review_semantics,
                )
                continue
            if isinstance(item, model.RecordScalar) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    review_semantics=review_semantics,
                )
                continue
            if isinstance(item, model.RecordRef) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    allow_review_semantics=allow_review_semantics,
                    review_semantics=review_semantics,
                )

    def _validate_output_guard_expr(
        self,
        expr: model.Expr,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> None:
        if isinstance(expr, model.ExprRef):
            self._validate_output_guard_ref(
                expr,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                review_semantics=review_semantics,
            )
            return
        if isinstance(expr, model.ExprBinary):
            self._validate_output_guard_expr(
                expr.left,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                review_semantics=review_semantics,
            )
            self._validate_output_guard_expr(
                expr.right,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                review_semantics=review_semantics,
            )
            return
        if isinstance(expr, model.ExprCall):
            for arg in expr.args:
                self._validate_output_guard_expr(
                    arg,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    review_semantics=review_semantics,
                )
            return
        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._validate_output_guard_expr(
                    item,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    review_semantics=review_semantics,
                )

    def _validate_output_guard_ref(
        self,
        ref: model.ExprRef,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> None:
        if self._output_guard_ref_allowed(
            ref,
            unit=unit,
            allow_review_semantics=allow_review_semantics,
            review_semantics=review_semantics,
        ):
            return
        raise CompileError(
            f"Output guard reads disallowed source in {owner_label}: {'.'.join(ref.parts)}"
        )

    def _output_guard_ref_allowed(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> bool:
        return (
            self._expr_ref_matches_input_decl(ref, unit=unit)
            or self._expr_ref_matches_enum_member(ref, unit=unit)
            or (
                allow_review_semantics
                and (
                    self._expr_ref_matches_review_field(ref)
                    or self._expr_ref_matches_review_semantic_ref(
                        ref,
                        review_semantics=review_semantics,
                    )
                    or self._expr_ref_matches_review_verdict(ref)
                )
            )
        )

    def _validate_standalone_read_guard_contract(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> None:
        for path, item in self._iter_output_items_with_paths(decl.items):
            if not path or path[-1] != "standalone_read":
                continue
            owner_label = f"output {decl.name}.{'.'.join(path)}"
            for ref in self._iter_record_item_interpolation_refs(item):
                if self._interpolation_ref_enters_guarded_output_section(
                    ref,
                    unit=unit,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                ):
                    raise CompileError(
                        "standalone_read cannot interpolate guarded output detail "
                        f"in {owner_label}: {_display_addressable_ref(ref)}"
                    )

    def _iter_output_items_with_paths(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        prefix: tuple[str, ...] = (),
    ) -> tuple[tuple[tuple[str, ...], model.AnyRecordItem], ...]:
        entries: list[tuple[tuple[str, ...], model.AnyRecordItem]] = []
        for item in items:
            if isinstance(item, model.RecordSection):
                path = (*prefix, item.key)
                entries.append((path, item))
                entries.extend(self._iter_output_items_with_paths(item.items, prefix=path))
                continue
            if isinstance(item, model.GuardedOutputSection):
                path = (*prefix, item.key)
                entries.append((path, item))
                entries.extend(self._iter_output_items_with_paths(item.items, prefix=path))
                continue
            if isinstance(item, model.RecordScalar):
                path = (*prefix, item.key)
                entries.append((path, item))
                if item.body is not None:
                    entries.extend(self._iter_output_items_with_paths(item.body, prefix=path))
                continue
            if isinstance(item, model.RecordRef) and item.body is not None:
                entries.extend(self._iter_output_items_with_paths(item.body, prefix=prefix))
        return tuple(entries)

    def _iter_record_item_interpolation_refs(
        self,
        item: model.AnyRecordItem,
    ) -> tuple[model.AddressableRef, ...]:
        if isinstance(item, model.RecordScalar):
            refs = self._interpolation_refs_from_scalar_value(item.value)
            if item.body is not None:
                refs = (*refs, *self._iter_record_body_interpolation_refs(item.body))
            return refs
        if isinstance(item, (model.RecordSection, model.GuardedOutputSection)):
            return self._iter_record_body_interpolation_refs(item.items)
        if isinstance(item, model.RecordRef) and item.body is not None:
            return self._iter_record_body_interpolation_refs(item.body)
        return ()

    def _iter_record_body_interpolation_refs(
        self,
        items: tuple[model.AnyRecordItem, ...],
    ) -> tuple[model.AddressableRef, ...]:
        refs: list[model.AddressableRef] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                refs.extend(self._interpolation_refs_from_prose_line(item))
                continue
            refs.extend(self._iter_record_item_interpolation_refs(item))
        return tuple(refs)

    def _interpolation_refs_from_prose_line(
        self,
        value: model.ProseLine,
    ) -> tuple[model.AddressableRef, ...]:
        text = value if isinstance(value, str) else value.text
        return self._interpolation_refs_from_text(text)

    def _interpolation_refs_from_scalar_value(
        self,
        value: model.RecordScalarValue,
    ) -> tuple[model.AddressableRef, ...]:
        if isinstance(value, str):
            return self._interpolation_refs_from_text(value)
        if isinstance(value, model.AddressableRef):
            return (value,)
        return ()

    def _interpolation_refs_from_text(
        self,
        text: str,
    ) -> tuple[model.AddressableRef, ...]:
        if "{{" not in text or "}}" not in text:
            return ()
        refs: list[model.AddressableRef] = []
        for match in _INTERPOLATION_RE.finditer(text):
            ref = self._parse_interpolation_expr_ref(match.group(1))
            if ref is not None:
                refs.append(ref)
        return tuple(refs)

    def _parse_interpolation_expr_ref(
        self,
        expression: str,
    ) -> model.AddressableRef | None:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            return None
        return model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )

    def _interpolation_ref_enters_guarded_output_section(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> bool:
        semantic_parts = self._review_semantic_addressable_parts(ref)
        if (
            review_semantics is not None
            and semantic_parts is not None
            and semantic_parts[0] == "fields"
        ):
            field_path = self._review_semantic_field_path(review_semantics, semantic_parts[1])
            if field_path is None:
                return False
            _output_unit, output_decl = self._resolve_review_semantic_output_decl(review_semantics)
            return self._output_path_has_guarded_section(
                output_decl,
                path=(*field_path, *semantic_parts[2:]),
            )
        try:
            target_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="standalone_read interpolation ref",
                missing_local_label="standalone_read",
                review_semantics=review_semantics,
            )
        except CompileError:
            return False

        if not isinstance(root_decl, model.OutputDecl):
            return False

        current = AddressableNode(unit=target_unit, root_decl=root_decl, target=root_decl)
        for segment in ref.path:
            children = self._get_addressable_children(current)
            if children is None:
                return False
            current = children.get(segment)
            if current is None:
                return False
            if isinstance(current.target, model.GuardedOutputSection):
                return True
        return False

    def _expr_ref_matches_input_decl(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        for split_at in range(len(ref.parts), 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            if not self._ref_exists_in_registry(root, unit=unit, registry_name="inputs_by_name"):
                continue
            _target_unit, _decl = self._resolve_input_decl(root, unit=unit)
            return True
        return False

    def _expr_ref_matches_review_field(self, ref: model.ExprRef) -> bool:
        return len(ref.parts) == 1 and ref.parts[0] in _REVIEW_GUARD_FIELD_NAMES

    def _expr_ref_matches_review_semantic_ref(
        self,
        ref: model.ExprRef,
        *,
        review_semantics: ReviewSemanticContext | None,
    ) -> bool:
        if review_semantics is None or len(ref.parts) < 2:
            return False
        if ref.parts[0] == "fields":
            return self._review_semantic_field_path(review_semantics, ref.parts[1]) is not None
        if ref.parts[0] == "contract":
            if ref.parts[1] in _REVIEW_CONTRACT_FACT_KEYS and len(ref.parts) == 2:
                return True
            return (
                len(ref.parts) == 2
                and self._review_semantic_contract_gate(review_semantics, ref.parts[1]) is not None
            )
        return False

    def _expr_ref_matches_review_verdict(self, ref: model.ExprRef) -> bool:
        return (
            len(ref.parts) == 2
            and ref.parts[0] == "ReviewVerdict"
            and ref.parts[1] in _REVIEW_VERDICT_TEXT
        )

    def _expr_ref_matches_enum_member(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        if len(ref.parts) < 2:
            return False
        for split_at in range(len(ref.parts) - 1, 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            enum_decl = self._try_resolve_enum_decl(root, unit=unit)
            if enum_decl is None:
                continue
            remainder = ref.parts[split_at:]
            return len(remainder) == 1 and any(member.key == remainder[0] for member in enum_decl.members)
        return False

    def _compile_trust_surface_section(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        lines: list[CompiledBodyItem] = []
        for item in decl.trust_surface:
            field_node = self._resolve_output_field_node(
                decl,
                path=item.path,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
            )
            label = self._display_addressable_target_value(
                field_node,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
            ).text
            if item.when_expr is not None:
                label = self._render_trust_surface_label(
                    label,
                    item.when_expr,
                    unit=unit,
                )
            lines.append(f"- {label}")
        return CompiledSection(title="Trust Surface", body=tuple(lines))

    def _render_trust_surface_label(
        self,
        label: str,
        when_expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str:
        if (
            isinstance(when_expr, model.ExprBinary)
            and when_expr.op == "=="
            and self._resolve_constant_enum_member(when_expr.right, unit=unit) == "rewrite"
        ):
            return f"{label} on rewrite passes"

        condition = self._render_condition_expr(when_expr, unit=unit)
        if condition.startswith("peer comparison"):
            return f"{label} when peer comparison is used"
        return f"{label} when {condition}"

    def _compile_output_files(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise CompileError(
                    f"`files` entries must be titled sections in output {output_name}"
                )
            scalar_items, _section_items, extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise CompileError(
                    f"Output file entry is missing string path in {output_name}: {item.key}"
                )
            if shape_item is None:
                raise CompileError(
                    f"Output file entry is missing shape in {output_name}: {item.key}"
                )
            body.append(f"- {item.title}: `{path_item.value}`")
            body.append(
                f"- {item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {output_name} file {item.key}', surface_label='output file fields')}"
            )
            if extras:
                body.append("")
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_record_support_items(
                            extras,
                            unit=unit,
                            owner_label=f"output {output_name} file {item.key}",
                            surface_label="output file prose",
                            review_semantics=review_semantics,
                        ),
                    )
                )
        return tuple(body)

    def _compile_record_support_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            body.extend(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                )
            )
        return tuple(body)

    def _compile_record_item(
        self,
        item: model.AnyRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return (
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                ),
            )

        if isinstance(item, model.RecordSection):
            return (
                CompiledSection(
                    title=item.title,
                    body=self._compile_record_support_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label=surface_label,
                        review_semantics=review_semantics,
                    ),
                ),
            )

        if isinstance(item, model.GuardedOutputSection):
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            body: list[CompiledBodyItem] = [f"Rendered only when {condition}."]
            compiled_items = self._compile_record_support_items(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
            )
            if compiled_items:
                body.append("")
                body.extend(compiled_items)
            return (CompiledSection(title=item.title, body=tuple(body)),)

        if isinstance(item, model.RecordScalar):
            return self._compile_fallback_scalar(
                item,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                review_semantics=review_semantics,
            )

        if isinstance(item, model.RecordRef):
            body = (
                self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                )
                if item.body is not None
                else ()
            )
            return (
                CompiledSection(
                    title=self._display_ref(item.ref),
                    body=body,
                ),
            )

        raise CompileError(f"Unsupported record item: {type(item).__name__}")

    def _compile_fallback_scalar(
        self,
        item: model.RecordScalar,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        label = _humanize_key(item.key)
        value = self._format_scalar_value(
            item.value,
            unit=unit,
            owner_label=f"{owner_label}.{item.key}",
            surface_label=surface_label,
            review_semantics=review_semantics,
        )
        if item.body is None:
            return (f"- {label}: {value}",)

        body: list[CompiledBodyItem] = [value]
        body.extend(
            self._compile_record_support_items(
                item.body,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
            )
        )
        return (CompiledSection(title=label, body=tuple(body)),)

    def _compile_config_lines(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        seen_keys: set[str] = set()
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(f"Config entries must be scalar key/value lines in {owner_label}")
            if item.key in seen_keys:
                raise CompileError(f"Duplicate config key in {owner_label}: {item.key}")
            seen_keys.add(item.key)
            if item.key not in allowed_keys:
                raise CompileError(f"Unknown config key in {owner_label}: {item.key}")
            body.append(
                f"- {allowed_keys[item.key]}: {self._format_scalar_value(item.value, unit=unit, owner_label=f'{owner_label}.{item.key}', surface_label='config values')}"
            )

        missing_required = [
            key for key in spec.required_keys if key not in seen_keys
        ]
        if missing_required:
            missing = ", ".join(missing_required)
            raise CompileError(f"Missing required config key in {owner_label}: {missing}")

        return tuple(body)

    def _resolve_input_source_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_INPUT_SOURCES.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.input_sources_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(local_decl, owner_label=f"input source {local_decl.name}")

        target_unit, decl = self._resolve_input_source_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"input source {decl.name}")

    def _resolve_output_target_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_OUTPUT_TARGETS.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.output_targets_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(
                    local_decl,
                    owner_label=f"output target {local_decl.name}",
                )

        target_unit, decl = self._resolve_output_target_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"output target {decl.name}")

    def _config_spec_from_decl(
        self,
        decl: model.InputSourceDecl | model.OutputTargetDecl,
        *,
        owner_label: str,
    ) -> ConfigSpec:
        _scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            section_keys={"required", "optional"},
            owner_label=owner_label,
        )
        if extras:
            # Extra prose is fine on the declaration; it does not affect config validation.
            pass
        required_section = section_items.get("required")
        optional_section = section_items.get("optional")
        required_keys = (
            self._key_labels_from_section(required_section, owner_label=owner_label)
            if required_section is not None
            else {}
        )
        optional_keys = (
            self._key_labels_from_section(optional_section, owner_label=owner_label)
            if optional_section is not None
            else {}
        )
        return ConfigSpec(title=decl.title, required_keys=required_keys, optional_keys=optional_keys)

    def _key_labels_from_section(
        self,
        section: model.RecordSection,
        *,
        owner_label: str,
    ) -> dict[str, str]:
        labels: dict[str, str] = {}
        for item in section.items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(
                    f"Config key declarations must be simple titled scalars in {owner_label}"
                )
            if not isinstance(item.value, str):
                raise CompileError(
                    f"Config key declarations must use string labels in {owner_label}: {item.key}"
                )
            if item.key in labels:
                raise CompileError(f"Duplicate config key declaration in {owner_label}: {item.key}")
            labels[item.key] = item.value
        return labels

    def _display_output_shape(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, model.AddressableRef):
            raise CompileError(
                f"Output shape must stay typed: {owner_label or surface_label or 'output'}"
            )
        if value.module_parts:
            _target_unit, decl = self._resolve_output_shape_decl(value, unit=unit)
            return decl.title
        local_decl = unit.output_shapes_by_name.get(value.declaration_name)
        if local_decl is not None:
            return local_decl.title
        return _humanize_key(value.declaration_name)

    def _display_symbol_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        return self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        ).text

    def _format_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            review_semantics=review_semantics,
        )
        if display.kind == "string_literal":
            return f"`{display.text}`"
        return display.text

    def _display_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> DisplayValue:
        if isinstance(value, str):
            return DisplayValue(text=value, kind="string_literal")
        if isinstance(value, model.NameRef):
            enum_decl = self._try_resolve_enum_decl(value, unit=unit)
            if enum_decl is not None:
                return DisplayValue(text=enum_decl.title, kind="title")
            return DisplayValue(text=self._display_ref(value), kind="symbol")
        if owner_label is None or surface_label is None:
            raise CompileError(
                "Internal compiler error: addressable refs require an owner label and surface label"
            )
        return self._resolve_addressable_ref_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=f"{surface_label} addressable ref",
            missing_local_label=surface_label,
            review_semantics=review_semantics,
        )

    def _value_to_symbol(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
        return display.text

    def _display_ref(self, ref: model.NameRef) -> str:
        if ref.module_parts:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return _humanize_key(ref.declaration_name)

    def _try_resolve_enum_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> model.EnumDecl | None:
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        return lookup_unit.enums_by_name.get(ref.declaration_name)

    def _resolve_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._resolved_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_resolution_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._resolved_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_resolution_stack.pop()

    def _resolve_review_decl(
        self, review_decl: model.ReviewDecl, *, unit: IndexedUnit
    ) -> ResolvedReviewBody:
        review_key = (unit.module_parts, review_decl.name)
        cached = self._resolved_review_cache.get(review_key)
        if cached is not None:
            return cached

        if review_key in self._review_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._review_resolution_stack, review_key]
            )
            raise CompileError(f"Cyclic review inheritance: {cycle}")

        self._review_resolution_stack.append(review_key)
        try:
            parent_review: ResolvedReviewBody | None = None
            parent_label: str | None = None
            if review_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_decl_ref(
                    review_decl.parent_ref,
                    unit=unit,
                    registry_name="reviews_by_name",
                    missing_label="review declaration",
                )
                parent_review = self._resolve_review_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"review {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_review_body(
                review_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, review_decl.name),
                parent_review=parent_review,
                parent_label=parent_label,
            )
            self._resolved_review_cache[review_key] = resolved
            return resolved
        finally:
            self._review_resolution_stack.pop()

    def _resolve_review_body(
        self,
        review_body: model.ReviewBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_review: ResolvedReviewBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedReviewBody:
        subject = parent_review.subject if parent_review is not None else None
        subject_map = parent_review.subject_map if parent_review is not None else None
        contract = parent_review.contract if parent_review is not None else None
        comment_output = parent_review.comment_output if parent_review is not None else None
        fields = parent_review.fields if parent_review is not None else None

        if parent_review is None:
            fields_accounted = True
            parent_items_by_key: dict[str, model.ReviewSection | model.ReviewOutcomeSection] = {}
        else:
            fields_accounted = parent_review.fields is None
            parent_items_by_key = {item.key: item for item in parent_review.items}

        resolved_items: list[model.ReviewSection | model.ReviewOutcomeSection] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in review_body.items:
            if isinstance(item, model.ReviewSubjectConfig):
                subject = item
                continue
            if isinstance(item, model.ReviewSubjectMapConfig):
                subject_map = item
                continue
            if isinstance(item, model.ReviewContractConfig):
                contract = item
                continue
            if isinstance(item, model.ReviewCommentOutputConfig):
                comment_output = item
                continue
            if isinstance(item, model.ReviewFieldsConfig):
                if parent_review is not None and parent_review.fields is not None:
                    raise CompileError(
                        f"Inherited review fields require `inherit fields` or `override fields` in {owner_label}"
                    )
                fields = item
                fields_accounted = True
                continue

            if isinstance(item, model.InheritItem) and item.key == "fields":
                if parent_review is None or parent_review.fields is None:
                    raise CompileError(
                        f"Cannot inherit undefined review entry in {parent_label or owner_label}: fields"
                    )
                fields = parent_review.fields
                fields_accounted = True
                continue

            if isinstance(item, model.ReviewOverrideFields):
                if parent_review is None or parent_review.fields is None:
                    raise CompileError(
                        f"`override` requires an inherited review in {owner_label}: fields"
                    )
                fields = model.ReviewFieldsConfig(bindings=item.bindings)
                fields_accounted = True
                continue

            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate review item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.ReviewSection):
                resolved_items.append(
                    model.ReviewSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_review_pre_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReviewOutcomeSection):
                resolved_items.append(
                    model.ReviewOutcomeSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_review_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined review entry in {parent_label or owner_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"`override` requires an inherited review in {owner_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.ReviewOverrideSection):
                if not isinstance(parent_item, model.ReviewSection):
                    raise CompileError(
                        f"Override kind mismatch for review entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    model.ReviewSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_review_pre_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, model.ReviewOutcomeSection):
                raise CompileError(
                    f"Override kind mismatch for review entry in {owner_label}: {key}"
                )
            resolved_items.append(
                model.ReviewOutcomeSection(
                    key=key,
                    title=item.title if item.title is not None else parent_item.title,
                    items=self._resolve_review_outcome_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                    ),
                )
            )

        if parent_review is not None:
            missing_keys = [
                parent_item.key
                for parent_item in parent_review.items
                if parent_item.key not in accounted_keys
            ]
            if missing_keys:
                raise CompileError(
                    f"Missing inherited review entry in {owner_label}: {', '.join(missing_keys)}"
                )
            if parent_review.fields is not None and not fields_accounted:
                raise CompileError(
                    f"Missing inherited review entry in {owner_label}: fields"
                )

        return ResolvedReviewBody(
            title=review_body.title,
            subject=subject,
            subject_map=subject_map,
            contract=contract,
            comment_output=comment_output,
            fields=fields,
            items=tuple(resolved_items),
        )

    def _resolve_review_pre_outcome_items(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ReviewPreOutcomeStmt, ...]:
        resolved: list[model.ReviewPreOutcomeStmt] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(item)
                continue
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                resolved.append(
                    model.ReviewPreOutcomeWhenStmt(
                        expr=item.expr,
                        items=self._resolve_review_pre_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=owner_label,
                        ),
                    )
                )
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                resolved.append(
                    model.ReviewPreOutcomeMatchStmt(
                        expr=item.expr,
                        cases=tuple(
                            model.ReviewPreOutcomeMatchArm(
                                head=case.head,
                                items=self._resolve_review_pre_outcome_items(
                                    case.items,
                                    unit=unit,
                                    owner_label=owner_label,
                                ),
                            )
                            for case in item.cases
                        ),
                    )
                )
                continue
            resolved.append(item)
        return tuple(resolved)

    def _resolve_review_outcome_items(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ReviewOutcomeStmt, ...]:
        resolved: list[model.ReviewOutcomeStmt] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(item)
                continue
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                resolved.append(
                    model.ReviewOutcomeWhenStmt(
                        expr=item.expr,
                        items=self._resolve_review_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=owner_label,
                        ),
                    )
                )
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                resolved.append(
                    model.ReviewOutcomeMatchStmt(
                        expr=item.expr,
                        cases=tuple(
                            model.ReviewOutcomeMatchArm(
                                head=case.head,
                                items=self._resolve_review_outcome_items(
                                    case.items,
                                    unit=unit,
                                    owner_label=owner_label,
                                ),
                            )
                            for case in item.cases
                        ),
                    )
                )
                continue
            resolved.append(item)
        return tuple(resolved)

    def _resolve_skills_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._resolved_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._skills_resolution_stack, skills_key]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._resolved_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_resolution_stack.pop()

    def _resolve_workflow_for_addressable_paths(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if (
            workflow_key in self._workflow_resolution_stack
            or workflow_key in self._workflow_addressable_resolution_stack
        ):
            return self._resolve_workflow_addressable_decl(workflow_decl, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=unit)

    def _resolve_skills_for_addressable_paths(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        if (
            skills_key in self._skills_resolution_stack
            or skills_key in self._skills_addressable_resolution_stack
        ):
            return self._resolve_skills_addressable_decl(skills_decl, unit=unit)
        return self._resolve_skills_decl(skills_decl, unit=unit)

    def _resolve_workflow_addressable_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._addressable_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._workflow_addressable_resolution_stack,
                    workflow_key,
                ]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_addressable_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_addressable_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._addressable_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_addressable_resolution_stack.pop()

    def _resolve_skills_addressable_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._addressable_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._skills_addressable_resolution_stack,
                    skills_key,
                ]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_addressable_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_addressable_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._addressable_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_addressable_resolution_stack.pop()

    def _resolve_inputs_decl(
        self, inputs_decl: model.InputsDecl, *, unit: IndexedUnit
    ) -> ResolvedIoBody:
        inputs_key = (unit.module_parts, inputs_decl.name)
        cached = self._resolved_inputs_cache.get(inputs_key)
        if cached is not None:
            return cached

        if inputs_key in self._inputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._inputs_resolution_stack, inputs_key]
            )
            raise CompileError(f"Cyclic inputs inheritance: {cycle}")

        self._inputs_resolution_stack.append(inputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if inputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_inputs_decl(
                    inputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"inputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_io_body(
                inputs_decl.body,
                unit=unit,
                field_kind="inputs",
                owner_label=_dotted_decl_name(unit.module_parts, inputs_decl.name),
                parent_io=parent_io,
                parent_label=parent_label,
            )
            self._resolved_inputs_cache[inputs_key] = resolved
            return resolved
        finally:
            self._inputs_resolution_stack.pop()

    def _resolve_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> ResolvedIoBody:
        outputs_key = (unit.module_parts, outputs_decl.name, review_output_contexts)
        cached = self._resolved_outputs_cache.get(outputs_key)
        if cached is not None:
            return cached

        if outputs_key in self._outputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name, _review_keys in [*self._outputs_resolution_stack, outputs_key]
            )
            raise CompileError(f"Cyclic outputs inheritance: {cycle}")

        self._outputs_resolution_stack.append(outputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if outputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_outputs_decl(
                    outputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_outputs_decl(
                    parent_decl,
                    unit=parent_unit,
                    review_output_contexts=review_output_contexts,
                )
                parent_label = f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_io_body(
                outputs_decl.body,
                unit=unit,
                field_kind="outputs",
                owner_label=_dotted_decl_name(unit.module_parts, outputs_decl.name),
                parent_io=parent_io,
                parent_label=parent_label,
                review_output_contexts=review_output_contexts,
            )
            self._resolved_outputs_cache[outputs_key] = resolved
            return resolved
        finally:
            self._outputs_resolution_stack.pop()

    def _resolve_skills_value(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_decl(skills_decl, unit=target_unit)
        return self._resolve_skills_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_skills_value_for_addressable_paths(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_for_addressable_paths(skills_decl, unit=target_unit)
        return self._resolve_skills_addressable_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_io: ResolvedIoBody | None = None,
        parent_label: str | None = None,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> ResolvedIoBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{field_kind} prose",
                ambiguous_label=f"{field_kind} prose interpolation ref",
            )
            for line in io_body.preamble
        )
        if parent_io is None:
            resolved_items = self._resolve_non_inherited_io_items(
                io_body.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
                review_output_contexts=review_output_contexts,
            )
            return ResolvedIoBody(
                title=io_body.title,
                preamble=resolved_preamble,
                items=resolved_items,
                artifacts=self._resolved_io_body_artifacts(resolved_items),
                bindings=self._resolved_io_body_bindings(resolved_items),
            )

        unkeyed_parent_titles = [
            item.section.title for item in parent_io.items if isinstance(item, ResolvedIoRef)
        ]
        if unkeyed_parent_titles:
            details = ", ".join(unkeyed_parent_titles)
            raise CompileError(
                f"Cannot inherit {field_kind} block with unkeyed top-level refs in {parent_label}: {details}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_io.items if isinstance(item, ResolvedIoSection)
        }
        resolved_items: list[ResolvedIoItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in io_body.items:
            if isinstance(item, model.RecordRef):
                resolved_items.append(
                    self._resolve_io_ref_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._resolve_io_section_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        binding_path=(item.key,),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined {field_kind} entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined {field_kind} entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if not isinstance(item, model.OverrideIoSection):
                raise CompileError(
                    f"Internal compiler error: unsupported {field_kind} override in {owner_label}: {type(item).__name__}"
                )
            resolved_bucket = self._resolve_contract_bucket_items(
                item.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=(
                    f"{field_kind} section `{item.title if item.title is not None else parent_item.section.title}`"
                ),
                review_output_contexts=review_output_contexts,
                path_prefix=(key,),
            )
            bindings = list(resolved_bucket.bindings)
            if not resolved_bucket.has_keyed_children and len(resolved_bucket.direct_artifacts) == 1:
                bindings.append(
                    ContractBinding(
                        binding_path=(key,),
                        artifact=resolved_bucket.direct_artifacts[0],
                    )
                )
            resolved_items.append(
                ResolvedIoSection(
                    key=key,
                    section=CompiledSection(
                        title=item.title if item.title is not None else parent_item.section.title,
                        body=resolved_bucket.body,
                    ),
                    artifacts=resolved_bucket.artifacts,
                    bindings=tuple(bindings),
                )
            )

        missing_keys = [
            item.key for item in parent_io.items if isinstance(item, ResolvedIoSection) and item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited {field_kind} entry in {owner_label}: {missing}"
            )

        return ResolvedIoBody(
            title=io_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
            artifacts=self._resolved_io_body_artifacts(tuple(resolved_items)),
            bindings=self._resolved_io_body_bindings(tuple(resolved_items)),
        )

    def _resolve_skills_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="skills prose",
                ambiguous_label="skills prose interpolation ref",
            )
            for line in skills_body.preamble
        )
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(
                    self._resolve_skill_entry(
                        item,
                        unit=unit,
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined skills entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined skills entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise CompileError(
                        f"Override kind mismatch for skills entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(
                self._resolve_skill_entry(
                    item,
                    unit=unit,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited skills entry in {owner_label}: {missing}"
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_workflow_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="workflow strings",
                ambiguous_label="workflow string interpolation ref",
            )
            for line in workflow_body.preamble
        )
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_law_body(
        self,
        law_body: model.LawBody | None,
        *,
        owner_label: str,
        parent_law: model.LawBody | None = None,
        parent_label: str | None = None,
    ) -> model.LawBody | None:
        if law_body is None:
            return parent_law
        if parent_law is None:
            return law_body

        parent_items = parent_law.items
        parent_has_sections = all(
            isinstance(item, model.LawSection) for item in parent_items
        )
        child_has_named_items = all(
            isinstance(
                item,
                (model.LawSection, model.LawInherit, model.LawOverrideSection),
            )
            for item in law_body.items
        )

        if not parent_has_sections or not child_has_named_items:
            raise CompileError(
                f"Inherited law blocks must use named sections only in {owner_label}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_items if isinstance(item, model.LawSection)
        }
        resolved_items: list[model.LawTopLevelItem] = []
        accounted_keys: set[str] = set()

        for item in law_body.items:
            if isinstance(item, model.LawSection):
                if item.key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                    )
                resolved_items.append(item)
                continue

            parent_item = parent_items_by_key.get(item.key)
            if parent_item is None:
                raise CompileError(
                    f"Cannot override undefined law section in {parent_label}: {item.key}"
                )
            if item.key in accounted_keys:
                raise CompileError(
                    f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                )
            accounted_keys.add(item.key)

            if isinstance(item, model.LawInherit):
                resolved_items.append(parent_item)
            else:
                resolved_items.append(model.LawSection(key=item.key, items=item.items))

        missing_keys = sorted(set(parent_items_by_key) - accounted_keys)
        if missing_keys:
            raise CompileError(
                f"Inherited law block omits parent subsection(s) in {owner_label}: {', '.join(missing_keys)}"
            )

        return model.LawBody(items=tuple(resolved_items))

    def _resolve_skills_addressable_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined skills entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined skills entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise CompileError(
                        f"Override kind mismatch for skills entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(self._resolve_skill_entry(item, unit=unit))

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited skills entry in {owner_label}: {missing}"
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=(),
            items=tuple(resolved_items),
        )

    def _resolve_workflow_addressable_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_workflow_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=(),
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_non_inherited_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_addressable_workflow_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: set[str] = set()

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited skills block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_addressable_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: set[str] = set()

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited skills block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_io_items(
        self,
        io_items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> tuple[ResolvedIoItem, ...]:
        resolved_items: list[ResolvedIoItem] = []
        seen_keys: set[str] = set()

        for item in io_items:
            if isinstance(item, model.RecordRef):
                resolved_items.append(
                    self._resolve_io_ref_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                        review_output_contexts=review_output_contexts,
                    )
                )
                continue

            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._resolve_io_section_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        binding_path=(item.key,),
                        review_output_contexts=review_output_contexts,
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited {field_kind} block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_io_section_item(
        self,
        item: model.RecordSection,
        *,
        unit: IndexedUnit,
        field_kind: str,
        binding_path: tuple[str, ...],
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> ResolvedIoSection:
        resolved_bucket = self._resolve_contract_bucket_items(
            item.items,
            unit=unit,
            field_kind=field_kind,
            owner_label=f"{field_kind} section `{item.title}`",
            review_output_contexts=review_output_contexts,
            path_prefix=binding_path,
        )
        bindings = list(resolved_bucket.bindings)
        if not resolved_bucket.has_keyed_children and len(resolved_bucket.direct_artifacts) == 1:
            bindings.append(
                ContractBinding(
                    binding_path=binding_path,
                    artifact=resolved_bucket.direct_artifacts[0],
                )
            )
        return ResolvedIoSection(
            key=item.key,
            section=CompiledSection(
                title=item.title,
                body=resolved_bucket.body,
            ),
            artifacts=resolved_bucket.artifacts,
            bindings=tuple(bindings),
        )

    def _resolve_io_ref_item(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
    ) -> ResolvedIoRef:
        section, artifact = self._resolve_contract_bucket_ref_entry(
            item,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
        )
        return ResolvedIoRef(
            section=section,
            artifact=artifact,
        )

    def _resolve_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="skills prose",
                        ambiguous_label="skills prose interpolation ref",
                    )
                )
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_addressable_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_skill_entry(
        self,
        entry: model.SkillEntry | model.OverrideSkillEntry,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillEntry:
        target_unit, skill_decl = self._resolve_skill_decl(entry.target, unit=unit)
        return ResolvedSkillEntry(
            key=entry.key,
            metadata_unit=unit,
            target_unit=target_unit,
            skill_decl=skill_decl,
            items=entry.items,
        )

    def _resolve_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if isinstance(item, str):
                resolved.append(
                    self._interpolate_authored_prose_string(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.EmphasizedLine):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.LocalSection):
                resolved.append(
                    ResolvedSectionItem(
                        key=item.key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                    )
                )
                continue
            if isinstance(item, model.SectionBodyRef):
                resolved.append(
                    self._resolve_section_body_ref(item.ref, unit=unit, owner_label=owner_label)
                )
                continue
            target_unit, target_agent = self._resolve_agent_ref(item.target, unit=unit)
            if target_agent.abstract:
                dotted_name = _dotted_ref_name(item.target)
                raise CompileError(f"Route target must be a concrete agent: {dotted_name}")
            resolved.append(
                ResolvedRouteLine(
                    label=self._interpolate_authored_prose_string(
                        item.label,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="route labels",
                    ),
                    target_module_parts=target_unit.module_parts,
                    target_name=target_agent.name,
                )
            )
        return tuple(resolved)

    def _resolve_addressable_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if not isinstance(item, model.LocalSection):
                continue
            resolved.append(
                ResolvedSectionItem(
                    key=item.key,
                    title=item.title,
                    items=self._resolve_addressable_section_body_items(
                        item.items,
                        unit=unit,
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_section_body_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSectionRef:
        value = self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label="workflow section bodies",
            ambiguous_label="workflow section declaration ref",
            missing_local_label="workflow section body",
        )
        return ResolvedSectionRef(label=value.text)

    def _interpolate_authored_prose_string(
        self,
        value: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> str:
        if "{{" not in value and "}}" not in value:
            return value

        parts: list[str] = []
        cursor = 0
        for match in _INTERPOLATION_RE.finditer(value):
            between = value[cursor:match.start()]
            if "{{" in between or "}}" in between:
                raise CompileError(
                    f"Malformed interpolation in {owner_label}: {value}"
                )
            parts.append(between)
            parts.append(
                self._resolve_authored_prose_interpolation_expr(
                    match.group(1),
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    ambiguous_label=ambiguous_label,
                    review_semantics=review_semantics,
                )
            )
            cursor = match.end()

        tail = value[cursor:]
        if "{{" in tail or "}}" in tail:
            raise CompileError(
                f"Malformed interpolation in {owner_label}: {value}"
            )
        parts.append(tail)
        return "".join(parts)

    def _interpolate_authored_prose_line(
        self,
        value: model.ProseLine,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> model.ProseLine:
        if isinstance(value, str):
            return self._interpolate_authored_prose_string(
                value,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                review_semantics=review_semantics,
            )
        return model.EmphasizedLine(
            kind=value.kind,
            text=self._interpolate_authored_prose_string(
                value.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                review_semantics=review_semantics,
            ),
        )

    def _resolve_authored_prose_interpolation_expr(
        self,
        expression: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> str:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            raise CompileError(
                f"Invalid interpolation in {owner_label}: {{{{{expression}}}}}"
            )

        ref = model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )
        return self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=ambiguous_label or f"{surface_label} interpolation ref",
            missing_local_label=surface_label,
            review_semantics=review_semantics,
        ).text

    def _resolve_readable_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
    ) -> tuple[IndexedUnit, ReadableDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_readable_decl_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    f"Abstract agent refs are not allowed in {surface_label}; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if target_unit.workflows_by_name.get(ref.declaration_name) is not None:
            raise CompileError(
                f"Workflow refs are not allowed in {surface_label}; "
                f"use `use` for workflow composition: {dotted_name}"
            )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> DisplayValue:
        ref_label = _display_addressable_ref(ref)
        semantic_node = self._resolve_review_semantic_node(
            ref,
            review_semantics=review_semantics,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )
        if semantic_node is not None:
            return self._display_addressable_target_value(
                semantic_node,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        if not ref.path:
            target_unit, decl = self._resolve_readable_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                missing_local_label=missing_local_label,
            )
            return self._display_addressable_target_value(
                AddressableNode(unit=target_unit, root_decl=decl, target=decl),
                owner_label=owner_label,
                surface_label=surface_label,
            )

        target_unit, decl = self._resolve_addressable_root_decl(
            ref.root,
            unit=unit,
            owner_label=owner_label,
            ambiguous_label=ambiguous_label,
            missing_local_label=missing_local_label,
            review_semantics=review_semantics,
        )
        return self._resolve_addressable_path_value(
            AddressableNode(unit=target_unit, root_decl=decl, target=decl),
            ref.path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

    def _resolve_addressable_root_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[IndexedUnit, AddressableRootDecl]:
        semantic_root = self._resolve_review_semantic_root_decl(
            ref,
            review_semantics=review_semantics,
        )
        if semantic_root is not None and review_semantics is not None:
            output_unit, _output_decl = self._resolve_review_semantic_output_decl(review_semantics)
            return output_unit, semantic_root
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_addressable_root_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    "Abstract agent refs are not allowed in addressable paths; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_path_value(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> DisplayValue:
        current = self._resolve_addressable_path_node(
            start,
            path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

        return self._display_addressable_target_value(
            current,
            owner_label=owner_label,
            surface_label=surface_label,
        )

    def _resolve_addressable_path_node(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> AddressableNode:
        current = start

        for index, segment in enumerate(path):
            is_last = index == len(path) - 1
            if is_last and isinstance(current.target, model.Agent) and segment == "name":
                return AddressableNode(
                    unit=current.unit,
                    root_decl=current.root_decl,
                    target=current.target,
                )
            if is_last and segment == "title":
                title = self._display_addressable_title(
                    current,
                    owner_label=owner_label,
                    surface_label=surface_label,
                )
                if title is not None:
                    return current
            if is_last and segment in {"name", "title"}:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )

            children = self._get_addressable_children(current)
            if children is None:
                raise CompileError(
                    "Addressable path must stay addressable on "
                    f"{surface_label} in {owner_label}: {ref_label}"
                )
            next_node = children.get(segment)
            if next_node is None:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )
            current = next_node

        return current

    def _get_addressable_children(
        self,
        node: AddressableNode,
    ) -> dict[str, AddressableNode] | None:
        target = node.target
        if isinstance(target, ReviewSemanticFieldsRoot):
            children: dict[str, AddressableNode] = {}
            output_unit, _output_decl = self._resolve_review_semantic_output_decl(target.context)
            for field_name, field_path in target.context.field_bindings:
                children[field_name] = AddressableNode(
                    unit=output_unit,
                    root_decl=node.root_decl,
                    target=ReviewSemanticFieldTarget(
                        field_name=field_name,
                        field_path=field_path,
                        context=target.context,
                    ),
                )
            return children
        if isinstance(target, ReviewSemanticContractRoot):
            output_unit, _output_decl = self._resolve_review_semantic_output_decl(target.context)
            children = {
                key: AddressableNode(
                    unit=output_unit,
                    root_decl=node.root_decl,
                    target=ReviewSemanticContractFactTarget(key=key),
                )
                for key in _REVIEW_CONTRACT_FACT_KEYS
            }
            for gate in target.context.contract_gates:
                children[gate.key] = AddressableNode(
                    unit=output_unit,
                    root_decl=node.root_decl,
                    target=ReviewSemanticContractGateTarget(gate=gate),
                )
            return children
        if isinstance(target, ReviewSemanticFieldTarget):
            output_unit, output_decl = self._resolve_review_semantic_output_decl(target.context)
            field_node = self._resolve_output_field_node(
                output_decl,
                path=target.field_path,
                unit=output_unit,
                owner_label=f"review field {target.field_name}",
                surface_label="review fields",
            )
            children = self._get_addressable_children(field_node)
            if children is None:
                return None
            return {
                key: AddressableNode(
                    unit=child.unit,
                    root_decl=node.root_decl,
                    target=child.target,
                )
                for key, child in children.items()
            }
        if isinstance(
            target,
            (
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.JsonSchemaDecl,
                model.SkillDecl,
            ),
        ):
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.RecordScalar):
            if target.body is None:
                return None
            return self._record_items_to_addressable_children(
                target.body,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.RecordSection):
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.GuardedOutputSection):
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.WorkflowDecl):
            workflow_body = self._resolve_workflow_for_addressable_paths(
                target,
                unit=node.unit,
            )
            return self._workflow_items_to_addressable_children(
                workflow_body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSectionItem):
            return self._workflow_section_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedUseItem):
            workflow_body = self._resolve_workflow_for_addressable_paths(
                target.workflow_decl,
                unit=target.target_unit,
            )
            return self._workflow_items_to_addressable_children(
                workflow_body.items,
                unit=target.target_unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedWorkflowSkillsItem):
            return self._skills_items_to_addressable_children(
                target.body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.SkillsDecl):
            skills_body = self._resolve_skills_for_addressable_paths(
                target,
                unit=node.unit,
            )
            return self._skills_items_to_addressable_children(
                skills_body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSkillsSection):
            return self._skills_section_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSkillEntry):
            if not target.items:
                return None
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.EnumDecl):
            return {
                member.key: AddressableNode(
                    unit=node.unit,
                    root_decl=node.root_decl,
                    target=member,
                )
                for member in target.members
            }
        return None

    def _record_items_to_addressable_children(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, (model.RecordScalar, model.RecordSection, model.GuardedOutputSection)):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _workflow_items_to_addressable_children(
        self,
        items: tuple[ResolvedWorkflowItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(unit=unit, root_decl=root_decl, target=item)
        return children

    def _workflow_section_items_to_addressable_children(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, ResolvedSectionItem):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _skills_items_to_addressable_children(
        self,
        items: tuple[ResolvedSkillsItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(unit=unit, root_decl=root_decl, target=item)
        return children

    def _skills_section_items_to_addressable_children(
        self,
        items: tuple[ResolvedSkillsSectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, ResolvedSkillEntry):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _display_addressable_target_value(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
    ) -> DisplayValue:
        target = node.target
        if isinstance(target, ReviewSemanticFieldsRoot):
            return DisplayValue(text="Review Fields", kind="title")
        if isinstance(target, ReviewSemanticContractRoot):
            return DisplayValue(text="Review Contract", kind="title")
        if isinstance(target, ReviewSemanticFieldTarget):
            output_unit, output_decl = self._resolve_review_semantic_output_decl(target.context)
            field_node = self._resolve_output_field_node(
                output_decl,
                path=target.field_path,
                unit=output_unit,
                owner_label=f"review field {target.field_name}",
                surface_label=surface_label,
            )
            return self._display_addressable_target_value(
                field_node,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        if isinstance(target, ReviewSemanticContractFactTarget):
            return DisplayValue(text=f"contract.{target.key}", kind="symbol")
        if isinstance(target, ReviewSemanticContractGateTarget):
            return DisplayValue(text=target.gate.title, kind="title")
        if isinstance(target, model.Agent):
            return DisplayValue(text=target.name, kind="symbol")
        if isinstance(target, model.WorkflowDecl):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, model.SkillsDecl):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, model.EnumDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(
            target,
            (
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.JsonSchemaDecl,
                model.SkillDecl,
            ),
        ):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, (model.RecordSection, model.GuardedOutputSection)):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.RecordScalar):
            if target.body is not None:
                return DisplayValue(
                    text=self._display_record_scalar_title(
                        target,
                        node=node,
                        owner_label=owner_label,
                        surface_label=surface_label,
                    ),
                    kind="title",
                )
            return self._display_scalar_value(
                target.value,
                unit=node.unit,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        if isinstance(target, model.EnumMember):
            return DisplayValue(text=target.value, kind="symbol")
        if isinstance(target, ResolvedSectionItem):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedUseItem):
            return DisplayValue(text=target.workflow_decl.body.title, kind="title")
        if isinstance(target, ResolvedWorkflowSkillsItem):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, ResolvedSkillsSection):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedSkillEntry):
            return DisplayValue(text=target.skill_decl.title, kind="title")
        raise CompileError(
            f"Internal compiler error: unsupported addressable target {type(target).__name__}"
        )

    def _display_addressable_title(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
    ) -> str | None:
        target = node.target
        if isinstance(target, model.Agent):
            return None
        if isinstance(target, model.RecordScalar):
            return self._display_record_scalar_title(
                target,
                node=node,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        return self._display_addressable_target_value(
            node,
            owner_label=owner_label,
            surface_label=surface_label,
        ).text

    def _display_record_scalar_title(
        self,
        item: model.RecordScalar,
        *,
        node: AddressableNode,
        owner_label: str,
        surface_label: str,
    ) -> str:
        root_decl = node.root_decl
        if isinstance(root_decl, model.InputDecl) and item.key == "source":
            if not isinstance(item.value, model.NameRef):
                raise CompileError(f"Input source must stay typed: {root_decl.name}")
            return self._resolve_input_source_spec(item.value, unit=node.unit).title

        if isinstance(root_decl, model.OutputDecl) and item.key == "target":
            if not isinstance(item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {root_decl.name}")
            return self._resolve_output_target_spec(item.value, unit=node.unit).title

        if isinstance(root_decl, model.OutputDecl) and item.key == "shape":
            return self._display_output_shape(
                item.value,
                unit=node.unit,
                owner_label=root_decl.name,
                surface_label=surface_label,
            )

        return self._display_symbol_value(
            item.value,
            unit=node.unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )

    def _resolve_readable_decl_lookup_unit(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> IndexedUnit:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            return unit

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")
        return target_unit

    def _find_readable_decl_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ReadableDecl], ...]:
        matches: list[tuple[str, ReadableDecl]] = []
        for label, registry_name in _READABLE_DECL_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _find_addressable_root_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, AddressableRootDecl], ...]:
        matches: list[tuple[str, AddressableRootDecl]] = []
        for label, registry_name in _ADDRESSABLE_ROOT_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _display_readable_decl(self, decl: ReadableDecl) -> str:
        if isinstance(decl, model.Agent):
            return decl.name
        return decl.title

    def _validate_route_target(self, ref: model.NameRef, *, unit: IndexedUnit) -> None:
        _target_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        if agent.abstract:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Route target must be a concrete agent: {dotted_name}")

    def _compile_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> CompiledSection:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if workflow_key in self._workflow_compile_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_compile_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow composition: {cycle}")

        self._workflow_compile_stack.append(workflow_key)
        try:
            return self._compile_resolved_workflow(
                self._resolve_workflow_decl(workflow_decl, unit=unit),
                unit=unit,
                agent_contract=agent_contract,
                owner_label=f"workflow {_dotted_decl_name(unit.module_parts, workflow_decl.name)}",
            )
        finally:
            self._workflow_compile_stack.pop()

    def _compile_resolved_workflow(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str | None = None,
    ) -> CompiledSection:
        body: list[CompiledBodyItem] = list(workflow_body.preamble)
        if workflow_body.law is not None:
            if unit is None or agent_contract is None or owner_label is None:
                raise CompileError(
                    "Internal compiler error: workflow law requires unit, agent contract, and owner label"
                )
            if body and body[-1] != "":
                body.append("")
            body.extend(
                self._compile_workflow_law(
                    workflow_body.law,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
            )
        for item in workflow_body.items:
            if body and body[-1] != "":
                body.append("")
            if isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(item.items),
                    )
                )
                continue

            if isinstance(item, ResolvedWorkflowSkillsItem):
                body.append(self._compile_resolved_skills(item.body))
                continue

            body.append(
                self._compile_workflow_decl(
                    item.workflow_decl,
                    unit=item.target_unit,
                    agent_contract=agent_contract,
                )
            )

        return CompiledSection(title=workflow_body.title, body=tuple(body))

    def _compile_workflow_law(
        self,
        law_body: model.LawBody,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        flat_items = self._flatten_law_items(law_body, owner_label=owner_label)
        self._validate_workflow_law(
            flat_items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

        lines: list[str] = []
        mode_bindings: dict[str, model.ModeStmt] = {}
        for item in flat_items:
            rendered: list[str] = []
            if isinstance(item, model.ActiveWhenStmt):
                rendered.append(
                    f"This pass runs only when {self._render_condition_expr(item.expr, unit=unit)}."
                )
            elif isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
                fixed_mode = self._resolve_constant_enum_member(item.expr, unit=unit)
                if fixed_mode is not None:
                    rendered.append(f"Active mode: {fixed_mode}.")
            elif isinstance(item, model.MatchStmt):
                rendered.extend(
                    self._render_match_stmt(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            elif isinstance(item, model.WhenStmt):
                rendered.extend(
                    self._render_when_stmt(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            else:
                rendered.extend(
                    self._render_law_stmt_lines(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        bullet=False,
                    )
                )

            if not rendered:
                continue
            if lines:
                lines.append("")
            lines.extend(rendered)

        return tuple(lines)

    def _flatten_law_items(
        self,
        law_body: model.LawBody,
        *,
        owner_label: str,
    ) -> tuple[model.LawStmt, ...]:
        has_sections = any(isinstance(item, model.LawSection) for item in law_body.items)
        if has_sections:
            if not all(isinstance(item, model.LawSection) for item in law_body.items):
                raise CompileError(
                    f"Law blocks may not mix named sections with bare law statements in {owner_label}"
                )
            flattened: list[model.LawStmt] = []
            for item in law_body.items:
                flattened.extend(item.items)
            return tuple(flattened)
        return tuple(law_body.items)

    def _render_match_stmt(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> list[str]:
        fixed_mode: str | None = None
        if isinstance(stmt.expr, model.ExprRef) and len(stmt.expr.parts) == 1:
            mode_stmt = mode_bindings.get(stmt.expr.parts[0])
            if mode_stmt is not None:
                fixed_mode = self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)

        if fixed_mode is not None:
            for case in stmt.cases:
                if case.head is None or self._render_expr(case.head, unit=unit) == fixed_mode:
                    return self._render_law_stmt_block(
                        case.items,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        bullet=False,
                    )
            return []

        labels = [
            self._render_expr(case.head, unit=unit)
            for case in stmt.cases
            if case.head is not None
        ]
        lines = ["Work in exactly one mode:"]
        lines.extend(f"- {label}" for label in labels)
        for case in stmt.cases:
            if case.head is None:
                heading = "Else:"
            else:
                heading = f"If mode is {self._render_expr(case.head, unit=unit)}:"
            lines.extend(["", heading])
            lines.extend(
                self._render_law_stmt_block(
                    case.items,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    bullet=True,
                )
            )
        return lines

    def _render_when_stmt(
        self,
        stmt: model.WhenStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> list[str]:
        lines = [f"If {self._render_condition_expr(stmt.expr, unit=unit)}:"]
        lines.extend(
            self._render_law_stmt_block(
                stmt.items,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                bullet=True,
                mode_bindings=mode_bindings,
            )
        )
        return lines

    def _render_law_stmt_block(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        bullet: bool,
        mode_bindings: dict[str, model.ModeStmt] | None = None,
    ) -> list[str]:
        mode_bindings = dict(mode_bindings or {})
        lines: list[str] = []
        for item in items:
            if isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
            if isinstance(item, model.MatchStmt):
                rendered = self._render_match_stmt(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                )
            elif isinstance(item, model.WhenStmt):
                rendered = self._render_when_stmt(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                )
            else:
                rendered = self._render_law_stmt_lines(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    bullet=bullet,
                )
            if (
                lines
                and rendered
                and not (
                    bullet
                    and lines[-1].startswith("- ")
                    and all(line.startswith("- ") for line in rendered)
                )
            ):
                lines.append("")
            lines.extend(rendered)
        return lines

    def _render_law_stmt_lines(
        self,
        stmt: model.LawStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        bullet: bool,
    ) -> list[str]:
        if isinstance(stmt, model.CurrentArtifactStmt):
            text = f"Current artifact: {self._display_law_path_root(stmt.target, unit=unit, agent_contract=agent_contract)}."
        elif isinstance(stmt, model.CurrentNoneStmt):
            text = "There is no current artifact for this turn."
        elif isinstance(stmt, model.MustStmt):
            text = self._render_must_stmt(stmt, unit=unit)
        elif isinstance(stmt, model.OwnOnlyStmt):
            text = f"Own only {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.PreserveStmt):
            text = f"Preserve {stmt.kind} {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.SupportOnlyStmt):
            text = (
                f"{self._render_path_set_subject(stmt.target, unit=unit, agent_contract=agent_contract)} is comparison-only support."
            )
        elif isinstance(stmt, model.IgnoreStmt):
            text = self._render_ignore_stmt(stmt, unit=unit, agent_contract=agent_contract)
        elif isinstance(stmt, model.ForbidStmt):
            text = f"Do not modify {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.InvalidateStmt):
            text = f"{self._display_law_path_root(stmt.target, unit=unit, agent_contract=agent_contract)} is no longer current."
        elif isinstance(stmt, model.StopStmt):
            message = stmt.message or ""
            if message and not message.endswith("."):
                message += "."
            text = "Stop." if stmt.message is None else f"Stop: {message}"
            if stmt.when_expr is not None:
                text = f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, {_lowercase_initial(text)}"
        elif isinstance(stmt, model.LawRouteStmt):
            text = stmt.label if stmt.label.endswith(".") else f"{stmt.label}."
            if stmt.when_expr is not None:
                text = (
                    f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, "
                    f"{_lowercase_initial(text)}"
                )
        elif isinstance(stmt, model.ActiveWhenStmt):
            text = f"This pass runs only when {self._render_condition_expr(stmt.expr, unit=unit)}."
        elif isinstance(stmt, model.ModeStmt):
            fixed_mode = self._resolve_constant_enum_member(stmt.expr, unit=unit)
            return [] if fixed_mode is None else [f"Active mode: {fixed_mode}."]
        else:
            return []

        if bullet:
            return [f"- {text}"]
        return [text]

    def _render_must_stmt(self, stmt: model.MustStmt, *, unit: IndexedUnit) -> str:
        if (
            isinstance(stmt.expr, model.ExprBinary)
            and stmt.expr.op == "=="
            and isinstance(stmt.expr.left, model.ExprRef)
        ):
            return f"Must {self._render_expr(stmt.expr.left, unit=unit)} == {self._render_expr(stmt.expr.right, unit=unit)}."
        return f"Must {self._render_expr(stmt.expr, unit=unit)}."

    def _render_ignore_stmt(
        self,
        stmt: model.IgnoreStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> str:
        target = self._render_path_set(stmt.target)
        if stmt.bases == ("rewrite_evidence",):
            prefix = "Ignore"
            if stmt.when_expr is not None:
                prefix = f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, ignore"
            return f"{prefix} {target} for rewrite evidence."
        if stmt.bases == ("truth",) or not stmt.bases:
            return f"{self._render_path_set_subject(stmt.target, unit=unit, agent_contract=agent_contract)} does not count as truth for this pass."
        return f"Ignore {target} for {', '.join(stmt.bases)}."

    def _render_path_set_subject(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> str:
        target = self._coerce_path_set(target)
        if len(target.paths) == 1 and not target.except_paths:
            path = target.paths[0]
            if not path.wildcard:
                return self._display_law_path_root(path, unit=unit, agent_contract=agent_contract)
        return self._render_path_set(target)

    def _render_path_set(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> str:
        target = self._coerce_path_set(target)
        parts = [self._render_law_path(path) for path in target.paths]
        rendered = ", ".join(parts)
        if len(parts) > 1:
            rendered = "{" + rendered + "}"
        if target.except_paths:
            rendered += " except " + ", ".join(
                self._render_law_path(path) for path in target.except_paths
            )
        return rendered

    def _render_law_path(self, path: model.LawPath) -> str:
        text = ".".join(path.parts)
        if path.wildcard:
            text += ".*"
        return f"`{text}`"

    def _render_condition_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_condition_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            if expr.op in {"==", "!="} and isinstance(expr.right, bool):
                expected = expr.right if expr.op == "==" else not expr.right
                return self._render_boolean_condition_expr(expr.left, expected=expected, unit=unit)
            if expr.op in {"==", "!="} and isinstance(expr.left, bool):
                expected = expr.left if expr.op == "==" else not expr.left
                return self._render_boolean_condition_expr(expr.right, expected=expected, unit=unit)
            if expr.op == "in" and isinstance(expr.right, model.ExprSet):
                subject = self._render_condition_subject(expr.left, unit=unit)
                choices = [self._render_condition_choice(item, unit=unit) for item in expr.right.items]
                if not choices:
                    return f"{subject} is in {{}}"
                if len(choices) == 1:
                    return f"{subject} is {choices[0]}"
                if len(choices) == 2:
                    return f"{subject} is {choices[0]} or {choices[1]}"
                return f"{subject} is {', '.join(choices[:-1])}, or {choices[-1]}"
            left = self._render_condition_expr(expr.left, unit=unit)
            right = self._render_condition_expr(expr.right, unit=unit)
            joiner = expr.op
            if expr.op == "==":
                return f"{left} is {right}"
            if expr.op == "!=":
                return f"{left} is not {right}"
            return f"{left} {joiner} {right}"
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{_humanize_key(expr.name).lower()}({args})"
        return self._render_expr(expr, unit=unit)

    def _render_boolean_condition_expr(
        self,
        expr: model.Expr,
        *,
        expected: bool,
        unit: IndexedUnit,
    ) -> str:
        rendered = self._render_condition_expr(expr, unit=unit)
        if expected:
            return rendered
        return self._negate_condition_text(rendered)

    def _negate_condition_text(self, text: str) -> str:
        if " is not " in text:
            head, tail = text.rsplit(" is not ", 1)
            return f"{head} is {tail}"
        if " is " in text:
            head, tail = text.rsplit(" is ", 1)
            return f"{head} is not {tail}"
        if text.startswith("not "):
            return text.removeprefix("not ")
        return f"not ({text})"

    def _render_condition_choice(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, str):
            return expr.replace("_", " ")
        return self._render_expr(expr, unit=unit)

    def _render_condition_subject(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            parts = expr.parts
            if len(parts) == 1:
                return _humanize_key(parts[0]).lower()
            return f"{self._render_ref_root(parts[:-1], unit=unit)} {_humanize_key(parts[-1]).lower()}"
        return self._render_condition_expr(expr, unit=unit)

    def _render_condition_ref(self, ref: model.ExprRef, *, unit: IndexedUnit) -> str:
        parts = ref.parts
        if not parts:
            return ""
        key = parts[-1]
        if key == "missing":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is missing"
        if key == "unclear":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is unclear"
        if key.endswith("_missing"):
            return f"{_humanize_key(key.removesuffix('_missing')).lower()} is missing"
        if key.endswith("_unknown"):
            return f"{_humanize_key(key.removesuffix('_unknown')).lower()} is unknown"
        if key.endswith("_repeated"):
            return f"{_humanize_key(key.removesuffix('_repeated')).lower()} is repeated"
        if key.startswith("owes_"):
            return f"{_humanize_key(key.removeprefix('owes_')).lower()} is owed now"
        if key.endswith("_changed"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_invalidated"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_requested"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_used"):
            return f"{_humanize_key(key).lower()}"
        return self._render_expr(ref, unit=unit)

    def _render_ref_root(self, parts: tuple[str, ...], *, unit: IndexedUnit) -> str:
        if not parts:
            return "this turn"
        try:
            root_path = model.LawPath(parts=parts)
            return self._display_law_path_root(root_path, unit=unit).lower()
        except CompileError:
            return _humanize_key(parts[-1]).lower()

    def _render_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_expr_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            return (
                f"{self._render_expr(expr.left, unit=unit)} {expr.op} "
                f"{self._render_expr(expr.right, unit=unit)}"
            )
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{expr.name}({args})"
        if isinstance(expr, model.ExprSet):
            rendered = ", ".join(self._render_expr(item, unit=unit) for item in expr.items)
            return "{" + rendered + "}"
        if isinstance(expr, str):
            return expr
        if isinstance(expr, bool):
            return "true" if expr else "false"
        return str(expr)

    def _render_expr_ref(self, expr: model.ExprRef, *, unit: IndexedUnit) -> str:
        constant = self._resolve_constant_enum_member(expr, unit=unit)
        if constant is not None:
            return constant
        return ".".join(expr.parts)

    def _resolve_constant_enum_member(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if isinstance(expr, str):
            return expr
        if isinstance(expr, model.ExprRef) and self._expr_ref_matches_review_verdict(expr):
            return _REVIEW_VERDICT_TEXT[expr.parts[1]]
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 2:
            return None
        name_ref = _name_ref_from_dotted_name(".".join(expr.parts[:-1]))
        enum_decl = self._try_resolve_enum_decl(name_ref, unit=unit)
        if enum_decl is None:
            return None
        member = next((member for member in enum_decl.members if member.key == expr.parts[-1]), None)
        if member is None:
            return None
        return member.value

    def _validate_workflow_law(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        self._validate_law_stmt_tree(
            items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )
        branches = self._collect_law_leaf_branches(items, unit=unit)
        if not branches:
            branches = (LawBranch(),)

        route_only_branch_seen = False
        for branch in branches:
            if len(branch.current_subjects) != 1:
                current_labels = ", ".join(
                    "current none"
                    if isinstance(subject, model.CurrentNoneStmt)
                    else "current artifact"
                    for subject in branch.current_subjects
                )
                if current_labels:
                    raise CompileError(
                        "Active leaf branch resolves more than one current-subject form "
                        f"({current_labels}) in {owner_label}"
                    )
                raise CompileError(
                    f"Active leaf branch must resolve exactly one current-subject form in {owner_label}"
                )
            current = branch.current_subjects[0]
            if isinstance(current, model.CurrentNoneStmt) and branch.owns:
                raise CompileError(
                    f"`current none` cannot appear with owned scope in {owner_label}"
                )
            if isinstance(current, model.CurrentNoneStmt):
                route_only_branch_seen = True
            current_target_key: tuple[tuple[str, ...], str] | None = None
            if isinstance(current, model.CurrentArtifactStmt):
                current_target_key = self._validate_current_artifact_stmt(
                    current,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
                for own in branch.owns:
                    self._validate_owned_scope(
                        own,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        current_target=current,
                    )
                for invalidate in branch.invalidations:
                    if self._law_paths_match(
                        current.target,
                        invalidate.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                    ):
                        raise CompileError(
                            f"The current artifact cannot be invalidated in the same active branch in {owner_label}"
                        )
            for invalidate in branch.invalidations:
                self._validate_invalidation_stmt(
                    invalidate,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
            for support in branch.supports:
                for ignore in branch.ignores:
                    if "comparison" in ignore.bases and self._path_sets_overlap(
                        support.target,
                        ignore.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                    ):
                        raise CompileError(
                            f"support_only and ignore for comparison contradict in {owner_label}"
                        )
            if current_target_key is not None:
                for ignore in branch.ignores:
                    if ("truth" in ignore.bases or not ignore.bases) and self._path_set_contains_path(
                        ignore.target,
                        current.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                    ):
                        raise CompileError(
                            f"The current artifact cannot be ignored for truth in {owner_label}"
                        )
            for own in branch.owns:
                own_target = self._coerce_path_set(own.target)
                for forbid in branch.forbids:
                    if self._path_sets_overlap(
                        own_target,
                        forbid.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                    ):
                        raise CompileError(
                            f"Owned and forbidden scope overlap in {owner_label}"
                        )
                for preserve in branch.preserves:
                    if preserve.kind == "exact" and any(
                        self._path_set_contains_path(
                            preserve.target,
                            path,
                            unit=unit,
                            agent_contract=agent_contract,
                            owner_label=owner_label,
                            statement_label="workflow law",
                        )
                        for path in own_target.paths
                    ):
                        raise CompileError(
                            f"Owned scope overlaps exact-preserved scope in {owner_label}"
                        )
            if isinstance(current, model.CurrentNoneStmt) and branch.routes:
                self._validate_route_only_next_owner_contract(
                    branch,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )

        if route_only_branch_seen:
            self._validate_route_only_standalone_read_contract(
                agent_contract=agent_contract,
                unit=unit,
                owner_label=owner_label,
            )

    def _validate_route_only_next_owner_contract(
        self,
        branch: LawBranch,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        output_items = tuple(agent_contract.outputs.items())
        if not output_items:
            return

        for route in branch.routes:
            route_unit, route_agent = self._resolve_agent_ref(route.target, unit=unit)
            next_owner_fields_found = False
            for (_output_key, (output_unit, output_decl)) in output_items:
                for path, item in self._iter_output_items_with_paths(output_decl.items):
                    if not path or path[-1] != "next_owner":
                        continue
                    next_owner_fields_found = True
                    if self._record_item_mentions_agent(
                        item,
                        target_unit=route_unit,
                        target_agent_name=route_agent.name,
                        unit=output_unit,
                        owner_label=f"output {output_decl.name}.{'.'.join(path)}",
                    ):
                        continue
                    raise CompileError(
                        "next_owner field must interpolate routed target "
                        f"in {owner_label}: {output_decl.name}.{'.'.join(path)} -> {route_agent.name}"
                    )
            if next_owner_fields_found:
                continue

    def _record_item_mentions_agent(
        self,
        item: model.AnyRecordItem,
        *,
        target_unit: IndexedUnit,
        target_agent_name: str,
        unit: IndexedUnit,
        owner_label: str,
    ) -> bool:
        if (
            isinstance(item, model.RecordScalar)
            and isinstance(item.value, model.NameRef)
            and self._name_ref_matches_agent(
                item.value,
                target_unit=target_unit,
                target_agent_name=target_agent_name,
                unit=unit,
                owner_label=owner_label,
            )
        ):
            return True

        return any(
            self._addressable_ref_matches_agent(
                ref,
                target_unit=target_unit,
                target_agent_name=target_agent_name,
                unit=unit,
                owner_label=owner_label,
            )
            for ref in self._iter_record_item_interpolation_refs(item)
        )

    def _addressable_ref_matches_agent(
        self,
        ref: model.AddressableRef,
        *,
        target_unit: IndexedUnit,
        target_agent_name: str,
        unit: IndexedUnit,
        owner_label: str,
    ) -> bool:
        try:
            root_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="next_owner interpolation ref",
                missing_local_label="next_owner",
            )
        except CompileError:
            return False

        if not isinstance(root_decl, model.Agent):
            return False
        if root_decl.name != target_agent_name or root_unit.module_parts != target_unit.module_parts:
            return False
        return not ref.path or ref.path == ("name",)

    def _name_ref_matches_agent(
        self,
        ref: model.NameRef,
        *,
        target_unit: IndexedUnit,
        target_agent_name: str,
        unit: IndexedUnit,
        owner_label: str,
    ) -> bool:
        try:
            ref_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        except CompileError:
            return False
        _ = owner_label
        return agent.name == target_agent_name and ref_unit.module_parts == target_unit.module_parts

    def _validate_route_only_standalone_read_contract(
        self,
        *,
        agent_contract: AgentContract,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        _ = unit
        _ = owner_label
        for _output_key, (output_unit, output_decl) in agent_contract.outputs.items():
            self._validate_standalone_read_guard_contract(output_decl, unit=output_unit)

    def _validate_law_stmt_tree(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt] | None = None,
    ) -> None:
        local_mode_bindings = dict(mode_bindings or {})
        for item in items:
            if isinstance(item, model.ModeStmt):
                self._validate_mode_stmt(item, unit=unit, owner_label=owner_label)
                local_mode_bindings[item.name] = item
                continue
            if isinstance(item, model.MatchStmt):
                self._validate_match_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                for case in item.cases:
                    self._validate_law_stmt_tree(
                        case.items,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=local_mode_bindings,
                    )
                continue
            if isinstance(item, model.WhenStmt):
                self._validate_law_stmt_tree(
                    item.items,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                continue
            if isinstance(item, model.CurrentArtifactStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="current artifact",
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, model.InvalidateStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="invalidate",
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, (model.OwnOnlyStmt, model.SupportOnlyStmt, model.IgnoreStmt, model.ForbidStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, model.PreserveStmt):
                if item.kind == "vocabulary":
                    self._validate_path_set_roots(
                        item.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="preserve vocabulary",
                        allowed_kinds=("enum",),
                    )
                else:
                    self._validate_path_set_roots(
                        item.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label=f"preserve {item.kind}",
                        allowed_kinds=("input", "output"),
                    )
                continue
            if isinstance(item, model.LawRouteStmt):
                self._validate_route_target(item.target, unit=unit)

    def _validate_mode_stmt(
        self,
        stmt: model.ModeStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        enum_unit, enum_decl = self._resolve_decl_ref(
            stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        fixed_mode = self._resolve_constant_enum_member(stmt.expr, unit=enum_unit)
        if fixed_mode is None:
            return
        if not any(member.value == fixed_mode for member in enum_decl.members):
            raise CompileError(
                f"Mode value is outside enum {enum_decl.name} in {owner_label}: {fixed_mode}"
            )

    def _validate_match_stmt(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> None:
        enum_decl = self._resolve_match_enum_decl(
            stmt.expr,
            unit=unit,
            mode_bindings=mode_bindings,
        )
        if enum_decl is None:
            return

        if any(case.head is None for case in stmt.cases):
            return

        seen_members: set[str] = set()
        for case in stmt.cases:
            if case.head is None:
                continue
            member_value = self._resolve_constant_enum_member(case.head, unit=unit)
            if member_value is None:
                continue
            if not any(member.value == member_value for member in enum_decl.members):
                raise CompileError(
                    f"Match arm is outside enum {enum_decl.name} in {owner_label}: {member_value}"
                )
            seen_members.add(member_value)

        expected_members = {member.value for member in enum_decl.members}
        if seen_members != expected_members:
            raise CompileError(
                f"match on {enum_decl.name} must be exhaustive or include else in {owner_label}"
            )

    def _resolve_match_enum_decl(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> model.EnumDecl | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        mode_stmt = mode_bindings.get(expr.parts[0])
        if mode_stmt is None:
            return None
        enum_unit, enum_decl = self._resolve_decl_ref(
            mode_stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        _ = enum_unit
        return enum_decl

    def _collect_law_leaf_branches(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        branch: LawBranch | None = None,
    ) -> tuple[LawBranch, ...]:
        branches = (branch or LawBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.WhenStmt):
                when_items: list[model.WhenStmt] = []
                while index < len(items) and isinstance(items[index], model.WhenStmt):
                    when_items.append(items[index])
                    index += 1
                next_branches: list[LawBranch] = []
                for current_branch in branches:
                    for when_item in when_items:
                        next_branches.extend(
                            self._collect_law_leaf_branches(
                                when_item.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                branches = tuple(next_branches)
                continue
            if isinstance(item, model.WhenStmt):
                next_branches: list[LawBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_law_leaf_branches(
                            item.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
                continue
            if isinstance(item, model.MatchStmt):
                next_branches = []
                for current_branch in branches:
                    for case in self._select_match_cases(
                        item,
                        unit=unit,
                        branch=current_branch,
                    ):
                        next_branches.extend(
                            self._collect_law_leaf_branches(
                                case.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                branches = tuple(next_branches)
                index += 1
                continue
            branches = tuple(self._branch_with_stmt(current_branch, item) for current_branch in branches)
            index += 1
        return branches

    def _select_match_cases(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        branch: LawBranch,
    ) -> tuple[model.MatchArm, ...]:
        fixed_mode = self._resolve_fixed_match_value(stmt.expr, unit=unit, branch=branch)
        if fixed_mode is None:
            return stmt.cases

        exact_matches = tuple(
            case
            for case in stmt.cases
            if case.head is not None
            and self._resolve_constant_enum_member(case.head, unit=unit) == fixed_mode
        )
        if exact_matches:
            return exact_matches
        else_matches = tuple(case for case in stmt.cases if case.head is None)
        if else_matches:
            return else_matches
        return stmt.cases

    def _resolve_fixed_match_value(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: LawBranch,
    ) -> str | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        for mode_stmt in reversed(branch.mode_bindings):
            if mode_stmt.name == expr.parts[0]:
                return self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)
        return None

    def _branch_with_stmt(self, branch: LawBranch, stmt: model.LawStmt) -> LawBranch:
        if isinstance(stmt, model.ActiveWhenStmt):
            return replace(branch, activation_exprs=(*branch.activation_exprs, stmt.expr))
        if isinstance(stmt, model.ModeStmt):
            return replace(branch, mode_bindings=(*branch.mode_bindings, stmt))
        if isinstance(stmt, (model.CurrentArtifactStmt, model.CurrentNoneStmt)):
            return replace(branch, current_subjects=(*branch.current_subjects, stmt))
        if isinstance(stmt, model.MustStmt):
            return replace(branch, musts=(*branch.musts, stmt))
        if isinstance(stmt, model.OwnOnlyStmt):
            return replace(branch, owns=(*branch.owns, stmt))
        if isinstance(stmt, model.PreserveStmt):
            return replace(branch, preserves=(*branch.preserves, stmt))
        if isinstance(stmt, model.SupportOnlyStmt):
            return replace(branch, supports=(*branch.supports, stmt))
        if isinstance(stmt, model.IgnoreStmt):
            return replace(branch, ignores=(*branch.ignores, stmt))
        if isinstance(stmt, model.ForbidStmt):
            return replace(branch, forbids=(*branch.forbids, stmt))
        if isinstance(stmt, model.InvalidateStmt):
            return replace(branch, invalidations=(*branch.invalidations, stmt))
        if isinstance(stmt, model.StopStmt):
            return replace(branch, stops=(*branch.stops, stmt))
        if isinstance(stmt, model.LawRouteStmt):
            return replace(branch, routes=(*branch.routes, stmt))
        return branch

    def _validate_current_artifact_stmt(
        self,
        stmt: model.CurrentArtifactStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str]:
        target = self._validate_law_path_root(
            stmt.target,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
            allowed_kinds=("input", "output"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"current artifact must stay rooted at one input or output artifact in {owner_label}: "
                f"{'.'.join(stmt.target.parts)}"
            )

        carrier = self._validate_carrier_path(
            stmt.carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
        )
        if isinstance(target.decl, model.OutputDecl):
            target_key = (target.unit.module_parts, target.decl.name)
            if target_key not in agent_contract.outputs:
                raise CompileError(
                    f"current artifact output must be emitted by the concrete turn in {owner_label}: "
                    f"{target.decl.name}"
                )
        return (target.unit.module_parts, target.decl.name)

    def _validate_invalidation_stmt(
        self,
        stmt: model.InvalidateStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        target = self._validate_law_path_root(
            stmt.target,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="invalidate",
            allowed_kinds=("input", "output"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"invalidate must name one full input or output artifact in {owner_label}: "
                f"{'.'.join(stmt.target.parts)}"
            )
        self._validate_carrier_path(
            stmt.carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="invalidate",
        )

    def _validate_carrier_path(
        self,
        carrier: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        statement_label: str,
    ) -> ResolvedLawPath:
        resolved = self._validate_law_path_root(
            carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=f"{statement_label} carrier",
            allowed_kinds=("output",),
        )
        if not isinstance(resolved.decl, model.OutputDecl):
            raise CompileError(
                f"{statement_label} via carrier must stay rooted in an emitted output in {owner_label}"
            )
        if not resolved.remainder or resolved.wildcard:
            raise CompileError(
                f"{statement_label} requires an explicit `via` field on an emitted output in {owner_label}"
            )

        output_key = (resolved.unit.module_parts, resolved.decl.name)
        if output_key not in agent_contract.outputs:
            raise CompileError(
                f"{statement_label} carrier output must be emitted by the concrete turn in {owner_label}: "
                f"{resolved.decl.name}"
            )

        self._resolve_output_field_node(
            resolved.decl,
            path=resolved.remainder,
            unit=resolved.unit,
            owner_label=owner_label,
            surface_label=f"{statement_label} via",
        )
        if not any(item.path == resolved.remainder for item in resolved.decl.trust_surface):
            raise CompileError(
                f"{statement_label} carrier field must be listed in trust_surface in {owner_label}: "
                f"{'.'.join(resolved.remainder)}"
            )
        return resolved

    def _validate_owned_scope(
        self,
        stmt: model.OwnOnlyStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        current_target: model.CurrentArtifactStmt,
    ) -> None:
        target = self._coerce_path_set(stmt.target)
        current_root = self._validate_law_path_root(
            current_target.target,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
            allowed_kinds=("input", "output"),
        )
        for path in target.paths:
            resolved = self._validate_law_path_root(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label="own only",
                allowed_kinds=("input", "output"),
            )
            if (
                resolved.unit.module_parts != current_root.unit.module_parts
                or resolved.decl.name != current_root.decl.name
            ):
                raise CompileError(
                    f"own only must stay rooted in the current artifact in {owner_label}: "
                    f"{'.'.join(path.parts)}"
                )

    def _validate_path_set_roots(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> None:
        target = self._coerce_path_set(target)
        for path in (*target.paths, *target.except_paths):
            self._validate_law_path_root(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )

    def _validate_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        resolved = self._resolve_law_path(
            path,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        if isinstance(resolved.decl, model.EnumDecl) and resolved.remainder:
            raise CompileError(
                f"{statement_label} enum targets must not descend through fields in {owner_label}: "
                f"{'.'.join(path.parts)}"
            )
        return resolved

    def _resolve_law_path(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        matches: list[ResolvedLawPath] = []
        if agent_contract is not None:
            matches.extend(
                self._resolve_bound_law_matches(
                    path,
                    agent_contract=agent_contract,
                    allowed_kinds=allowed_kinds,
                )
            )
        for split_index in range(1, len(path.parts) + 1):
            ref = model.NameRef(
                module_parts=path.parts[: split_index - 1],
                declaration_name=path.parts[split_index - 1],
            )
            try:
                lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
            except CompileError:
                continue
            remainder = path.parts[split_index:]
            if "input" in allowed_kinds:
                input_decl = lookup_unit.inputs_by_name.get(ref.declaration_name)
                if input_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=input_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "output" in allowed_kinds:
                output_decl = lookup_unit.outputs_by_name.get(ref.declaration_name)
                if output_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=output_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "enum" in allowed_kinds:
                enum_decl = lookup_unit.enums_by_name.get(ref.declaration_name)
                if enum_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=enum_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )

        unique_matches: list[ResolvedLawPath] = []
        seen: set[tuple[tuple[str, ...], str, tuple[str, ...], str]] = set()
        for match in matches:
            key = self._law_path_match_key(match)
            if key in seen:
                continue
            seen.add(key)
            unique_matches.append(match)

        if len(unique_matches) == 1:
            return unique_matches[0]
        if len(unique_matches) > 1:
            choices = ", ".join(
                _dotted_decl_name(match.unit.module_parts, match.decl.name)
                for match in unique_matches
            )
            raise CompileError(
                f"Ambiguous {statement_label} path in {owner_label}: "
                f"{'.'.join(path.parts)} matches {choices}"
            )

        allowed_text = self._law_path_allowed_text(
            allowed_kinds,
            agent_contract=agent_contract,
        )
        raise CompileError(
            f"{statement_label} target must resolve to a {allowed_text} in {owner_label}: "
            f"{'.'.join(path.parts)}"
        )

    def _resolve_bound_law_matches(
        self,
        path: model.LawPath,
        *,
        agent_contract: AgentContract,
        allowed_kinds: tuple[str, ...],
    ) -> tuple[ResolvedLawPath, ...]:
        for split_index in range(len(path.parts), 0, -1):
            prefix = path.parts[:split_index]
            candidates: list[ContractBinding] = []
            if "input" in allowed_kinds:
                binding = agent_contract.input_bindings_by_path.get(prefix)
                if binding is not None:
                    candidates.append(binding)
            if "output" in allowed_kinds:
                binding = agent_contract.output_bindings_by_path.get(prefix)
                if binding is not None:
                    candidates.append(binding)
            if not candidates:
                continue
            return tuple(
                ResolvedLawPath(
                    unit=binding.artifact.unit,
                    decl=binding.artifact.decl,
                    remainder=path.parts[len(binding.binding_path) :],
                    wildcard=path.wildcard,
                    binding_path=binding.binding_path,
                )
                for binding in candidates
            )
        return ()

    def _law_path_match_key(
        self,
        match: ResolvedLawPath,
    ) -> tuple[tuple[str, ...], str, tuple[str, ...], str]:
        return (
            match.unit.module_parts,
            match.decl.name,
            match.remainder,
            type(match.decl).__name__,
        )

    def _law_path_allowed_text(
        self,
        allowed_kinds: tuple[str, ...],
        *,
        agent_contract: AgentContract | None,
    ) -> str:
        labels: list[str] = []
        for kind in allowed_kinds:
            if kind == "input":
                labels.append(
                    "declared or bound concrete-turn input"
                    if agent_contract is not None
                    else "declared input"
                )
                continue
            if kind == "output":
                labels.append(
                    "declared or bound concrete-turn output"
                    if agent_contract is not None
                    else "declared output"
                )
                continue
            if kind == "enum":
                labels.append("declared enum")
        return " or ".join(labels)

    def _resolve_output_field_node(
        self,
        decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> AddressableNode:
        current_node = AddressableNode(unit=unit, root_decl=decl, target=decl)
        if not path:
            return current_node
        for segment in path:
            children = self._get_addressable_children(current_node)
            if children is None or segment not in children:
                raise CompileError(
                    f"Unknown output field on {surface_label} in {owner_label}: "
                    f"{decl.name}.{'.'.join(path)}"
                )
            current_node = children[segment]
        return current_node

    def _law_paths_match(
        self,
        left: model.LawPath,
        right: model.LawPath,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        return self._law_path_contains_path(
            left,
            right,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        ) or self._law_path_contains_path(
            right,
            left,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )

    def _law_path_contains_path(
        self,
        container: model.LawPath,
        path: model.LawPath,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        if unit is None or agent_contract is None:
            if len(container.parts) > len(path.parts):
                return False
            if path.parts[: len(container.parts)] != container.parts:
                return False
            if len(container.parts) == len(path.parts):
                return container.wildcard or not path.wildcard or container.wildcard == path.wildcard
            return container.wildcard

        canonical_container = self._canonicalize_law_path(
            container,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        canonical_path = self._canonicalize_law_path(
            path,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        return self._canonical_law_path_contains_path(canonical_container, canonical_path)

    def _canonicalize_law_path(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> CanonicalLawPath:
        resolved = self._validate_law_path_root(
            path,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        return CanonicalLawPath(
            unit=resolved.unit,
            decl=resolved.decl,
            remainder=resolved.remainder,
            wildcard=resolved.wildcard,
        )

    def _canonical_law_path_contains_path(
        self,
        container: CanonicalLawPath,
        path: CanonicalLawPath,
    ) -> bool:
        if (
            container.unit.module_parts != path.unit.module_parts
            or container.decl.name != path.decl.name
            or type(container.decl) is not type(path.decl)
        ):
            return False
        if len(container.remainder) > len(path.remainder):
            return False
        if path.remainder[: len(container.remainder)] != container.remainder:
            return False
        if len(container.remainder) == len(path.remainder):
            return (
                container.wildcard
                or not path.wildcard
                or container.wildcard == path.wildcard
            )
        return container.wildcard

    def _path_set_contains_path(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        path: model.LawPath,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        target = self._coerce_path_set(target)
        if not any(
            self._law_path_contains_path(
                base,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )
            for base in target.paths
        ):
            return False
        if any(
            self._law_path_contains_path(
                excluded,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )
            for excluded in target.except_paths
        ):
            return False
        return True

    def _path_sets_overlap(
        self,
        left: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        right: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        left = self._coerce_path_set(left)
        right = self._coerce_path_set(right)
        for path in left.paths:
            if self._path_set_contains_path(
                right,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            ):
                return True
        for path in right.paths:
            if self._path_set_contains_path(
                left,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            ):
                return True
        return False

    def _display_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> str:
        try:
            resolved = self._resolve_law_path(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label="workflow law",
                statement_label="law path",
                allowed_kinds=("input", "output", "enum"),
            )
        except CompileError:
            return ".".join(path.parts)
        title = self._display_readable_decl(resolved.decl)
        if not resolved.remainder:
            return title
        return f"{title}.{'.'.join(resolved.remainder)}"

    def _coerce_path_set(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> model.LawPathSet:
        if isinstance(target, model.LawPathSet):
            return target
        if isinstance(target, tuple):
            return model.LawPathSet(paths=target)
        return model.LawPathSet(paths=(target,))

    def _law_stmt_name(self, stmt: model.LawStmt) -> str:
        if isinstance(stmt, model.OwnOnlyStmt):
            return "own only"
        if isinstance(stmt, model.SupportOnlyStmt):
            return "support_only"
        if isinstance(stmt, model.IgnoreStmt):
            return "ignore"
        if isinstance(stmt, model.ForbidStmt):
            return "forbid"
        return type(stmt).__name__

    def _compile_section_body(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        previous_kind: str | None = None

        for item in items:
            current_kind = "ref" if isinstance(item, ResolvedSectionRef) else "prose"
            if previous_kind is not None and current_kind != previous_kind and body:
                if body[-1] != "":
                    body.append("")

            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
            elif isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(item.items),
                    )
                )
            elif isinstance(item, ResolvedRouteLine):
                body.append(f"{item.label} -> {item.target_name}")
            else:
                body.append(f"- {item.label}")

            previous_kind = current_kind

        return tuple(body)

    def _split_record_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        scalar_keys: set[str] | None = None,
        section_keys: set[str] | None = None,
        owner_label: str,
    ) -> tuple[dict[str, model.RecordScalar], dict[str, model.RecordSection], tuple[model.AnyRecordItem, ...]]:
        scalar_keys = scalar_keys or set()
        section_keys = section_keys or set()
        scalar_items: dict[str, model.RecordScalar] = {}
        section_items: dict[str, model.RecordSection] = {}
        extras: list[model.AnyRecordItem] = []

        for item in items:
            if isinstance(item, model.RecordScalar) and item.key in scalar_keys:
                if item.key in scalar_items:
                    raise CompileError(f"Duplicate record key in {owner_label}: {item.key}")
                scalar_items[item.key] = item
                continue
            if isinstance(item, model.RecordSection) and item.key in section_keys:
                if item.key in section_items:
                    raise CompileError(f"Duplicate record key in {owner_label}: {item.key}")
                section_items[item.key] = item
                continue
            extras.append(item)

        return scalar_items, section_items, tuple(extras)

    def _resolve_workflow_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="workflows_by_name",
            missing_label="workflow declaration",
        )

    def _resolve_review_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.ReviewDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="reviews_by_name",
            missing_label="review declaration",
        )

    def _resolve_skills_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_blocks_by_name",
            missing_label="skills declaration",
        )

    def _resolve_inputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
            missing_label="inputs block",
        )

    def _resolve_outputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_blocks_by_name",
            missing_label="outputs block",
        )

    def _resolve_parent_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        parent_ref = workflow_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: workflow has no parent ref: {workflow_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.workflows_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent workflow for {workflow_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_workflow_ref(parent_ref, unit=unit)

    def _resolve_parent_skills_decl(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        parent_ref = skills_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: skills has no parent ref: {skills_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.skills_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent skills for {skills_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_skills_ref(parent_ref, unit=unit)

    def _resolve_parent_inputs_decl(
        self,
        inputs_decl: model.InputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        parent_ref = inputs_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: inputs block has no parent ref: {inputs_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.inputs_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent inputs block for {inputs_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_inputs_block_ref(parent_ref, unit=unit)

    def _resolve_parent_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        parent_ref = outputs_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: outputs block has no parent ref: {outputs_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.outputs_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent outputs block for {outputs_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_outputs_block_ref(parent_ref, unit=unit)

    def _resolve_input_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_by_name",
            missing_label="input declaration",
        )

    def _resolve_input_source_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputSourceDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="input_sources_by_name",
            missing_label="input source declaration",
        )

    def _resolve_output_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_by_name",
            missing_label="output declaration",
        )

    def _resolve_output_target_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputTargetDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_targets_by_name",
            missing_label="output target declaration",
        )

    def _resolve_output_shape_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputShapeDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_shapes_by_name",
            missing_label="output shape declaration",
        )

    def _resolve_skill_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_by_name",
            missing_label="skill declaration",
        )

    def _resolve_agent_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.Agent]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="agents_by_name",
            missing_label="agent declaration",
        )

    def _resolve_parent_agent_decl(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.Agent]:
        parent_ref = agent.parent_ref
        if parent_ref is None:
            raise CompileError(f"Internal compiler error: agent has no parent ref: {agent.name}")
        if not parent_ref.module_parts:
            parent_agent = unit.agents_by_name.get(parent_ref.declaration_name)
            if parent_agent is None:
                raise CompileError(
                    f"Missing parent agent for {agent.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_agent
        return self._resolve_agent_ref(parent_ref, unit=unit)

    def _resolve_decl_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
        missing_label: str,
    ):
        if not ref.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                raise CompileError(f"Missing local {missing_label}: {ref.declaration_name}")
            return unit, decl

        if ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                dotted_name = _dotted_ref_name(ref)
                raise CompileError(f"Missing imported declaration: {dotted_name}")
            return unit, decl

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")

        registry = getattr(target_unit, registry_name)
        decl = registry.get(ref.declaration_name)
        if decl is None:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Missing imported declaration: {dotted_name}")
        return target_unit, decl

    def _ref_exists_in_registry(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
    ) -> bool:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            return registry.get(ref.declaration_name) is not None

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            return False

        registry = getattr(target_unit, registry_name)
        return registry.get(ref.declaration_name) is not None

    def _load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        return self.session.load_module(module_parts)


def compile_prompt(prompt_file: model.PromptFile, agent_name: str) -> CompiledAgent:
    return CompilationSession(prompt_file).compile_agent(agent_name)


def extract_target_flow_graph(
    prompt_file: model.PromptFile,
    agent_names: tuple[str, ...],
) -> FlowGraph:
    return CompilationSession(prompt_file).extract_target_flow_graph(agent_names)


def _resolve_prompt_root(source_path: Path | None) -> Path:
    if source_path is None:
        raise CompileError("Prompt source path is required for compilation.")

    resolved = source_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            return candidate

    raise CompileError(f"Could not resolve prompts/ root for {resolved}.")


def _resolve_import_path(
    import_path: model.ImportPath, *, module_parts: tuple[str, ...]
) -> tuple[str, ...]:
    if import_path.level == 0:
        return import_path.module_parts

    current_package_parts = module_parts[:-1] if module_parts else ()
    parent_walk = import_path.level - 1
    package_parts = (
        current_package_parts[:-parent_walk] if parent_walk else current_package_parts
    )
    if parent_walk > len(current_package_parts):
        dotted_import = "." * import_path.level + ".".join(import_path.module_parts)
        raise CompileError(f"Relative import walks above prompts root: {dotted_import}")

    return (*package_parts, *import_path.module_parts)


def _dotted_decl_name(module_parts: tuple[str, ...], name: str) -> str:
    return ".".join((*module_parts, name)) if module_parts else name


def _dotted_ref_name(ref: model.NameRef) -> str:
    return ".".join((*ref.module_parts, ref.declaration_name))


def _name_ref_from_dotted_name(dotted_name: str) -> model.NameRef:
    parts = tuple(dotted_name.split("."))
    return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])


def _law_path_from_name_ref(ref: model.NameRef) -> model.LawPath:
    return model.LawPath(parts=(*ref.module_parts, ref.declaration_name))


def _path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())


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
