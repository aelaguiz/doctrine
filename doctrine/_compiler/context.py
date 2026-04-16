from __future__ import annotations

from typing import TYPE_CHECKING

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.resolved_types import (
    CompileError,
    CompiledAgent,
    CompiledSection,
    IndexedUnit,
    OutputDeclKey,
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
        previous_turn_contexts: dict[tuple[tuple[str, ...], str], PreviousTurnAgentContext]
        | None = None,
    ):
        self.session = session
        self.prompt_root = session.prompt_root
        self._previous_turn_contexts = previous_turn_contexts or {}
        self._active_agent_key: tuple[tuple[str, ...], str] | None = None
        self._active_previous_turn_input_specs: dict[
            tuple[tuple[str, ...], str],
            "ResolvedPreviousTurnInputSpec",
        ] = {}
        self._addressable_self_root_stack: list[model.NameRef] = []
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
        # Mutable resolution stacks and caches remain local to one compile task.
        self.root_unit = session.root_unit

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        return self.compile_agent_from_unit(self.root_unit, agent_name)

    def compile_agent_from_unit(
        self,
        unit: IndexedUnit,
        agent_name: str,
    ) -> CompiledAgent:
        agent = unit.agents_by_name.get(agent_name)
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
        return self._compile_agent_decl(agent, unit=unit)

    def compile_skill_package(
        self,
        package_name: str | None = None,
    ) -> CompiledSkillPackage:
        if package_name is None:
            packages = tuple(self.root_unit.skill_packages_by_name.values())
            if not packages:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail="Missing target skill package.",
                )
            if len(packages) != 1:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail="Prompt file defines multiple skill packages; choose one explicitly.",
                )
            declaration = packages[0]
        else:
            declaration = self.root_unit.skill_packages_by_name.get(package_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail=f"Missing target skill package: {package_name}",
                )
        return self._compile_skill_package_decl(declaration, unit=self.root_unit)

    def compile_readable_declaration(
        self, declaration_kind: str, declaration_name: str
    ) -> CompiledSection:
        if declaration_kind == "analysis":
            declaration = self.root_unit.analyses_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail=f"Missing target analysis declaration: {declaration_name}",
                )
            return self._compile_analysis_decl(declaration, unit=self.root_unit)
        if declaration_kind == "decision":
            declaration = self.root_unit.decisions_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail=f"Missing target decision declaration: {declaration_name}",
                )
            return self._compile_decision_decl(declaration, unit=self.root_unit)
        if declaration_kind == "schema":
            declaration = self.root_unit.schemas_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail=f"Missing target schema declaration: {declaration_name}",
                )
            return self._compile_schema_decl(declaration, unit=self.root_unit)
        if declaration_kind == "table":
            declaration = self.root_unit.tables_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail=f"Missing target table declaration: {declaration_name}",
                )
            return self._compile_table_decl(declaration, unit=self.root_unit)
        if declaration_kind == "document":
            declaration = self.root_unit.documents_by_name.get(declaration_name)
            if declaration is None:
                raise _context_compile_error(
                    path=self.root_unit.prompt_file.source_path,
                    detail=f"Missing target document declaration: {declaration_name}",
                )
            return self._compile_document_decl(declaration, unit=self.root_unit)
        raise _context_compile_error(
            path=self.root_unit.prompt_file.source_path,
            detail=f"Unsupported readable declaration kind: {declaration_kind}",
        )

    def _load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        return self.session.load_module(module_parts)
