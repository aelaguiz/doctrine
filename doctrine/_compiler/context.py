from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.indexing import unit_declarations
from doctrine._compiler.resolved_types import (
    CompileError,
    CompiledAgent,
    CompiledSection,
    CompiledSkillPackage,
    FlowAgentKey,
    FlowArtifactKey,
    IndexedUnit,
    OutputDeclKey,
    ActiveSkillBindAgentContext,
    PreviousTurnAgentContext,
    ResolvedAgentSlotState,
    ResolvedAnalysisBody,
    ResolvedDocumentBody,
    ResolvedIoBody,
    ResolvedReviewBody,
    ResolvedSchemaBody,
    ResolvedSkillsBody,
    ResolvedWorkflowBody,
    ReviewSemanticContext,
    RouteSemanticContext,
    SkillPackageHostCompileContext,
)
from doctrine._compiler.display import DisplayMixin
from doctrine._compiler.compile import CompileMixin
from doctrine._compiler.resolve import ResolveMixin
from doctrine._compiler.flow import FlowMixin
from doctrine._compiler.validate import ValidateMixin

if TYPE_CHECKING:
    from doctrine._compiler.session import CompilationSession

# Thin compile-context boundary: task-local state and public entrypoints live
# here, while the subsystem helper families are owned by the internal mixins.


def _context_compile_error(
    *,
    path,
    detail: str,
    code: str = "E299",
    summary: str = "Compile failure",
    hints: tuple[str, ...] = (),
) -> CompileError:
    return compile_error(
        code=code,
        summary=summary,
        detail=detail,
        path=path,
        hints=hints,
    )

class CompilationContext(FlowMixin, ValidateMixin, CompileMixin, DisplayMixin, ResolveMixin):
    def __init__(
        self,
        session: CompilationSession,
        *,
        previous_turn_contexts: dict[FlowAgentKey, PreviousTurnAgentContext] | None = None,
    ):
        self.session = session
        self.prompt_root = session.prompt_root
        self._previous_turn_contexts = previous_turn_contexts or {}
        self._active_agent_key: FlowAgentKey | None = None
        self._active_previous_turn_input_specs: dict[
            tuple[tuple[str, ...], str],
            "ResolvedPreviousTurnInputSpec",
        ] = {}
        self._addressable_self_root_stack: list[model.NameRef] = []
        self._skill_package_host_context_stack: list[SkillPackageHostCompileContext] = (
            []
            if session.skill_package_host_context is None
            else [session.skill_package_host_context]
        )
        self._workflow_compile_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._analysis_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._schema_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._document_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._output_decl_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._output_shape_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._output_schema_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._output_schema_lowering_stack: list[tuple[tuple[str, ...], str]] = []
        self._review_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._inputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._outputs_resolution_stack: list[
            tuple[
                tuple[str, ...],
                str,
                frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
                frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
                frozenset[OutputDeclKey],
            ]
        ] = []
        self._agent_slot_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._resolved_workflow_cache: dict[tuple[tuple[str, ...], str], ResolvedWorkflowBody] = {}
        self._resolved_analysis_cache: dict[tuple[tuple[str, ...], str], ResolvedAnalysisBody] = {}
        self._resolved_schema_cache: dict[tuple[tuple[str, ...], str], ResolvedSchemaBody] = {}
        self._resolved_document_cache: dict[tuple[tuple[str, ...], str], ResolvedDocumentBody] = {}
        self._resolved_output_decl_cache: dict[
            tuple[tuple[str, ...], str], model.OutputDecl
        ] = {}
        self._resolved_output_shape_cache: dict[
            tuple[tuple[str, ...], str], model.OutputShapeDecl
        ] = {}
        self._resolved_output_schema_cache: dict[
            tuple[tuple[str, ...], str], model.OutputSchemaDecl
        ] = {}
        self._lowered_output_schema_cache: dict[
            tuple[tuple[str, ...], str], dict[str, object]
        ] = {}
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
                frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
                frozenset[OutputDeclKey],
            ],
            ResolvedIoBody,
        ] = {}
        self._resolved_agent_slot_cache: dict[
            tuple[tuple[str, ...], str],
            tuple[ResolvedAgentSlotState, ...],
        ] = {}
        self._compiled_skill_package_cache: dict[
            tuple[tuple[str, ...], str],
            CompiledSkillPackage,
        ] = {}
        self._active_skill_bind_agent_context: ActiveSkillBindAgentContext | None = None
        # Mutable resolution stacks and caches remain local to one compile task.
        self.root_flow = session.root_flow
        self.root_entrypoint_unit = session.root_flow.entrypoint_unit

    def _flow_identity(self, unit: IndexedUnit) -> tuple[Path, Path]:
        flow = self.session.flow_for_unit(unit)
        return (flow.prompt_root.resolve(), flow.flow_root.resolve())

    def _flow_parts_for_unit(self, unit: IndexedUnit) -> tuple[str, ...]:
        return self.session.flow_for_unit(unit).flow_parts

    def _flow_agent_key(self, unit: IndexedUnit, agent_name: str) -> FlowAgentKey:
        prompt_root, flow_root = self._flow_identity(unit)
        return (prompt_root, flow_root, agent_name)

    def _flow_artifact_key(self, unit: IndexedUnit, declaration_name: str) -> FlowArtifactKey:
        prompt_root, flow_root = self._flow_identity(unit)
        return (prompt_root, flow_root, declaration_name)

    def _resolve_flow_agent_key(
        self,
        agent_key: FlowAgentKey,
    ) -> tuple[IndexedUnit, model.Agent] | None:
        prompt_root, flow_root, agent_name = agent_key
        flow = self.session.flow_by_key(prompt_root, flow_root)
        if flow is None:
            return None
        agent = flow.agents_by_name.get(agent_name)
        if agent is None:
            return None
        owner_unit = flow.declaration_owner_units_by_id[id(agent)]
        return owner_unit, agent

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        agent = self.root_flow.agents_by_name.get(agent_name)
        if agent is None:
            raise _context_compile_error(
                path=self.root_flow.entrypoint_path,
                code="E201",
                summary="Missing target agent",
                detail=f"Target agent `{agent_name}` does not exist in the root flow.",
            )
        owner_unit = self.root_flow.declaration_owner_units_by_id[id(agent)]
        return self.compile_agent_from_unit(owner_unit, agent_name)

    def compile_agent_from_unit(
        self,
        unit: IndexedUnit,
        agent_name: str,
    ) -> CompiledAgent:
        agent = unit_declarations(unit).agents_by_name.get(agent_name)
        if agent is None:
            raise _context_compile_error(
                path=unit.prompt_file.source_path,
                code="E201",
                summary="Missing target agent",
                detail=f"Target agent `{agent_name}` does not exist in the root prompt file.",
            )
        if agent.abstract:
            raise _context_compile_error(
                path=unit.prompt_file.source_path,
                code="E202",
                summary="Abstract agent does not render",
                detail=f"Agent `{agent_name}` is marked abstract and cannot render output directly.",
                hints=("Render a concrete child agent instead.",),
            )
        flow = self.session.flow_for_unit(unit)
        self._validate_all_rules_in_flow(flow)
        self._validate_all_stages_in_flow(flow)
        self._validate_all_skill_flows_in_flow(flow)
        return self._compile_agent_decl(agent, unit=unit)

    def compile_skill_package(
        self,
        package_name: str | None = None,
    ) -> CompiledSkillPackage:
        if package_name is None:
            packages = tuple(self.root_flow.skill_packages_by_name.values())
            if not packages:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail="Missing target skill package.",
                )
            if len(packages) != 1:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail="Root flow defines multiple skill packages; choose one explicitly.",
                )
            declaration = packages[0]
        else:
            declaration = self.root_flow.skill_packages_by_name.get(package_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail=f"Missing target skill package: {package_name}",
                )
        owner_unit = self.root_flow.declaration_owner_units_by_id[id(declaration)]
        flow = self.session.flow_for_unit(owner_unit)
        self._validate_all_stages_in_flow(flow)
        self._validate_all_skill_flows_in_flow(flow)
        return self._compile_skill_package_decl(declaration, unit=owner_unit)

    def compile_skill_graph(
        self,
        graph_name: str | None = None,
    ) -> model.ResolvedSkillGraph:
        flow = self.root_flow
        if graph_name is None:
            graphs = tuple(flow.skill_graphs_by_name.values())
            if not graphs:
                raise _context_compile_error(
                    path=flow.entrypoint_path,
                    code="E563",
                    summary="Invalid skill graph target",
                    detail="Missing target skill graph.",
                )
            if len(graphs) != 1:
                raise _context_compile_error(
                    path=flow.entrypoint_path,
                    code="E563",
                    summary="Invalid skill graph target",
                    detail=(
                        "Root flow defines multiple skill graphs; choose one explicitly."
                    ),
                )
            declaration = graphs[0]
            owner_unit = flow.declaration_owner_units_by_id[id(declaration)]
        else:
            ref = model.NameRef(module_parts=(), declaration_name=graph_name)
            try:
                owner_unit, declaration = self._resolve_decl_ref(
                    ref,
                    unit=self.root_entrypoint_unit,
                    registry_name="skill_graphs_by_name",
                    missing_label="skill_graph declaration",
                )
            except CompileError as exc:
                raise _context_compile_error(
                    path=flow.entrypoint_path,
                    code="E563",
                    summary="Invalid skill graph target",
                    detail=f"Missing target skill graph: {graph_name}",
                ) from exc
        owner_flow = self.session.flow_for_unit(owner_unit)
        self._validate_all_stages_in_flow(owner_flow)
        return self._resolve_skill_graph_decl(declaration, unit=owner_unit)

    def compile_readable_declaration(
        self, declaration_kind: str, declaration_name: str
    ) -> CompiledSection:
        if declaration_kind == "analysis":
            declaration = self.root_flow.analyses_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail=f"Missing target analysis declaration: {declaration_name}",
                )
            owner_unit = self.root_flow.declaration_owner_units_by_id[id(declaration)]
            return self._compile_analysis_decl(declaration, unit=owner_unit)
        if declaration_kind == "decision":
            declaration = self.root_flow.decisions_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail=f"Missing target decision declaration: {declaration_name}",
                )
            owner_unit = self.root_flow.declaration_owner_units_by_id[id(declaration)]
            return self._compile_decision_decl(declaration, unit=owner_unit)
        if declaration_kind == "schema":
            declaration = self.root_flow.schemas_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail=f"Missing target schema declaration: {declaration_name}",
                )
            owner_unit = self.root_flow.declaration_owner_units_by_id[id(declaration)]
            return self._compile_schema_decl(declaration, unit=owner_unit)
        if declaration_kind == "table":
            declaration = self.root_flow.tables_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail=f"Missing target table declaration: {declaration_name}",
                )
            owner_unit = self.root_flow.declaration_owner_units_by_id[id(declaration)]
            return self._compile_table_decl(declaration, unit=owner_unit)
        if declaration_kind == "document":
            declaration = self.root_flow.documents_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_flow.entrypoint_path,
                    detail=f"Missing target document declaration: {declaration_name}",
                )
            owner_unit = self.root_flow.declaration_owner_units_by_id[id(declaration)]
            return self._compile_document_decl(declaration, unit=owner_unit)
        raise _context_compile_error(
            path=self.root_flow.entrypoint_path,
            detail=f"Unsupported readable declaration kind: {declaration_kind}",
        )

    def _load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        return self.session.load_module(module_parts)
