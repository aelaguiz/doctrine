from __future__ import annotations

from doctrine._compiler.shared import *  # noqa: F401,F403
from doctrine._compiler.shared import (
    _ADDRESSABLE_ROOT_REGISTRIES,
    _BUILTIN_INPUT_SOURCES,
    _BUILTIN_OUTPUT_TARGETS,
    _BUILTIN_RENDER_PROFILE_NAMES,
    _INTERPOLATION_EXPR_RE,
    _INTERPOLATION_RE,
    _READABLE_DECL_REGISTRIES,
    _RESERVED_AGENT_FIELD_KEYS,
    _REVIEW_CONTRACT_FACT_KEYS,
    _REVIEW_GUARD_FIELD_NAMES,
    _REVIEW_OPTIONAL_FIELD_NAMES,
    _REVIEW_REQUIRED_FIELD_NAMES,
    _REVIEW_VERDICT_TEXT,
    _SCHEMA_FAMILY_TITLES,
    _default_worker_count,
    _display_addressable_ref,
    _dotted_decl_name,
    _dotted_ref_name,
    _humanize_key,
    _law_path_from_name_ref,
    _lowercase_initial,
    _name_ref_from_dotted_name,
    _resolve_render_profile_mode,
    _semantic_render_target_for_block,
)
from doctrine._compiler.display import DisplayMixin
from doctrine._compiler.compile import CompileMixin
from doctrine._compiler.resolve import ResolveMixin
from doctrine._compiler.flow import FlowMixin
from doctrine._compiler.validate import ValidateMixin

# Thin compile-context boundary: task-local state and public entrypoints live
# here, while the subsystem helper families are owned by the internal mixins.

class CompilationContext(FlowMixin, ValidateMixin, CompileMixin, DisplayMixin, ResolveMixin):
    def __init__(self, session: CompilationSession):
        self.session = session
        self.prompt_root = session.prompt_root
        self._workflow_compile_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._analysis_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._schema_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._document_resolution_stack: list[tuple[tuple[str, ...], str]] = []
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
        agent = self.root_unit.agents_by_name.get(agent_name)
        if agent is None:
            raise CompileError(f"Missing target agent: {agent_name}")
        if agent.abstract:
            raise CompileError(f"Abstract agent does not render: {agent_name}")
        return self._compile_agent_decl(agent, unit=self.root_unit)

    def compile_skill_package(
        self,
        package_name: str | None = None,
    ) -> CompiledSkillPackage:
        if package_name is None:
            packages = tuple(self.root_unit.skill_packages_by_name.values())
            if not packages:
                raise CompileError("Missing target skill package.")
            if len(packages) != 1:
                raise CompileError(
                    "Prompt file defines multiple skill packages; choose one explicitly."
                )
            declaration = packages[0]
        else:
            declaration = self.root_unit.skill_packages_by_name.get(package_name)
            if declaration is None:
                raise CompileError(f"Missing target skill package: {package_name}")
        return self._compile_skill_package_decl(declaration, unit=self.root_unit)

    def compile_readable_declaration(
        self, declaration_kind: str, declaration_name: str
    ) -> CompiledSection:
        if declaration_kind == "analysis":
            declaration = self.root_unit.analyses_by_name.get(declaration_name)
            if declaration is None:
                raise CompileError(f"Missing target analysis declaration: {declaration_name}")
            return self._compile_analysis_decl(declaration, unit=self.root_unit)
        if declaration_kind == "decision":
            declaration = self.root_unit.decisions_by_name.get(declaration_name)
            if declaration is None:
                raise CompileError(f"Missing target decision declaration: {declaration_name}")
            return self._compile_decision_decl(declaration, unit=self.root_unit)
        if declaration_kind == "schema":
            declaration = self.root_unit.schemas_by_name.get(declaration_name)
            if declaration is None:
                raise CompileError(f"Missing target schema declaration: {declaration_name}")
            return self._compile_schema_decl(declaration, unit=self.root_unit)
        if declaration_kind == "document":
            declaration = self.root_unit.documents_by_name.get(declaration_name)
            if declaration is None:
                raise CompileError(f"Missing target document declaration: {declaration_name}")
            return self._compile_document_decl(declaration, unit=self.root_unit)
        raise CompileError(f"Unsupported readable declaration kind: {declaration_kind}")

    def _load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        return self.session.load_module(module_parts)
