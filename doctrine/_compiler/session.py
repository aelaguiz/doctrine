from __future__ import annotations

import threading
import tomllib
from concurrent.futures import ThreadPoolExecutor

import doctrine._model.declarations as model
from doctrine._compiler.indexing import IndexedUnit, ModuleLoadKey, index_unit, load_module
from doctrine._compiler.types import (
    CompiledAgent,
    CompiledField,
    CompiledFinalOutputSpec,
    CompiledSection,
    CompiledSkillPackage,
    FlowGraph,
)
from doctrine.diagnostics import CompileError, DoctrineError
from doctrine.project_config import (
    ProjectConfig,
    ProjectConfigError,
    find_nearest_pyproject,
    load_project_config_for_source,
)
from doctrine._compiler.support import (
    default_worker_count,
    path_location,
    resolve_import_roots,
    resolve_prompt_root,
)


class CompilationSession:
    """Stable compile session boundary; doctrine.compiler re-exports this owner."""

    def __init__(
        self,
        prompt_file: model.PromptFile,
        *,
        project_config: ProjectConfig | None = None,
    ):
        self.prompt_root = resolve_prompt_root(prompt_file.source_path)
        try:
            resolved_project_config = project_config or load_project_config_for_source(
                prompt_file.source_path
            )
            compile_config = resolved_project_config.resolve_compile_config()
        except tomllib.TOMLDecodeError as exc:
            config_path = project_config.path if project_config is not None else None
            if config_path is None and prompt_file.source_path is not None:
                config_path = find_nearest_pyproject(prompt_file.source_path.parent)
            raise CompileError.from_parts(
                code="E299",
                summary="Compile failure",
                detail="The Doctrine project config is not valid TOML.",
                location=path_location(config_path),
                cause=getattr(exc, "msg", str(exc)),
            ) from exc
        except ProjectConfigError as exc:
            raise CompileError(str(exc)).ensure_location(
                path=resolved_project_config.path
            ) from exc

        self.project_config = resolved_project_config
        self.import_roots = resolve_import_roots(
            self.prompt_root,
            compile_config.additional_prompt_roots,
        )
        self._module_cache: dict[ModuleLoadKey, IndexedUnit] = {}
        self._module_load_errors: dict[ModuleLoadKey, Exception] = {}
        self._module_loading: dict[ModuleLoadKey, threading.Event] = {}
        self._module_waits: dict[ModuleLoadKey, ModuleLoadKey] = {}
        self._module_lock = threading.Lock()
        # Shared prompt graph data lives on the session; compile contexts stay task-local.
        self.root_unit = index_unit(
            self,
            prompt_file,
            prompt_root=self.prompt_root,
            module_parts=(),
            module_source_kind="entrypoint",
            package_root=None,
            ancestry=(),
            allow_parallel_imports=True,
        )

    def _new_module_ready_event(self) -> threading.Event:
        return threading.Event()

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(self).compile_agent(agent_name)
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"compile agent `{agent_name}`",
                location=path_location(self.root_unit.prompt_file.source_path),
            ).ensure_location(path=self.root_unit.prompt_file.source_path)

    def compile_agent_from_unit(
        self,
        unit: IndexedUnit,
        agent_name: str,
    ) -> CompiledAgent:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(self).compile_agent_from_unit(unit, agent_name)
        except DoctrineError as exc:
            source_path = unit.prompt_file.source_path
            dotted_name = ".".join((*unit.module_parts, agent_name)) or agent_name
            raise exc.prepend_trace(
                f"compile agent `{dotted_name}`",
                location=path_location(source_path),
            ).ensure_location(path=source_path)

    def compile_agents(self, agent_names: tuple[str, ...]) -> tuple[CompiledAgent, ...]:
        if len(agent_names) <= 1:
            return tuple(self.compile_agent(agent_name) for agent_name in agent_names)

        with ThreadPoolExecutor(max_workers=default_worker_count(len(agent_names))) as executor:
            futures = {
                agent_name: executor.submit(self.compile_agent, agent_name)
                for agent_name in agent_names
            }
            return tuple(futures[agent_name].result() for agent_name in agent_names)

    def compile_agents_from_units(
        self,
        agent_roots: tuple[tuple[IndexedUnit, str], ...],
    ) -> tuple[CompiledAgent, ...]:
        if len(agent_roots) <= 1:
            return tuple(
                self.compile_agent_from_unit(unit, agent_name)
                for unit, agent_name in agent_roots
            )

        with ThreadPoolExecutor(max_workers=default_worker_count(len(agent_roots))) as executor:
            futures = {
                (unit.prompt_root, unit.module_parts, agent_name): executor.submit(
                    self.compile_agent_from_unit,
                    unit,
                    agent_name,
                )
                for unit, agent_name in agent_roots
            }
            return tuple(
                futures[(unit.prompt_root, unit.module_parts, agent_name)].result()
                for unit, agent_name in agent_roots
            )

    def compile_skill_package(
        self,
        package_name: str | None = None,
    ) -> CompiledSkillPackage:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(self).compile_skill_package(package_name)
        except DoctrineError as exc:
            label = (
                f"compile skill package `{package_name}`"
                if package_name is not None
                else "compile skill package"
            )
            raise exc.prepend_trace(
                label,
                location=path_location(self.root_unit.prompt_file.source_path),
            ).ensure_location(path=self.root_unit.prompt_file.source_path)

    def compile_readable_declaration(
        self, declaration_kind: str, declaration_name: str
    ) -> CompiledSection:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(self).compile_readable_declaration(
                declaration_kind, declaration_name
            )
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"compile {declaration_kind} declaration `{declaration_name}`",
                location=path_location(self.root_unit.prompt_file.source_path),
            ).ensure_location(path=self.root_unit.prompt_file.source_path)

    def _compile_agent_field_task(
        self,
        spec: "AgentFieldCompileSpec",
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: "AgentContract",
        review_output_contexts: frozenset[tuple["OutputDeclKey", "ReviewSemanticContext"]],
        route_output_contexts: frozenset[tuple["OutputDeclKey", "RouteSemanticContext"]],
        final_output: CompiledFinalOutputSpec | None,
    ) -> CompiledField | None:
        from doctrine._compiler.context import CompilationContext

        return CompilationContext(self)._compile_agent_field(
            spec,
            agent_name=agent_name,
            unit=unit,
            agent_contract=agent_contract,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            final_output=final_output,
        )

    def extract_target_flow_graph(self, agent_names: tuple[str, ...]) -> FlowGraph:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(self).extract_target_flow_graph(agent_names)
        except DoctrineError as exc:
            raise exc.prepend_trace(
                "extract flow graph",
                location=path_location(self.root_unit.prompt_file.source_path),
            ).ensure_location(path=self.root_unit.prompt_file.source_path)

    def extract_target_flow_graph_from_units(
        self,
        agent_roots: tuple[tuple[IndexedUnit, str], ...],
    ) -> FlowGraph:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(self).extract_target_flow_graph_from_units(
                agent_roots
            )
        except DoctrineError as exc:
            raise exc.prepend_trace(
                "extract flow graph",
                location=path_location(self.root_unit.prompt_file.source_path),
            ).ensure_location(path=self.root_unit.prompt_file.source_path)

    def load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        if not module_parts:
            return self.root_unit
        return load_module(self, module_parts, prompt_root=None, ancestry=())


def compile_prompt(
    prompt_file: model.PromptFile,
    agent_name: str,
    *,
    project_config: ProjectConfig | None = None,
) -> CompiledAgent:
    return CompilationSession(prompt_file, project_config=project_config).compile_agent(
        agent_name
    )


def extract_target_flow_graph(
    prompt_file: model.PromptFile,
    agent_names: tuple[str, ...],
    *,
    project_config: ProjectConfig | None = None,
) -> FlowGraph:
    return CompilationSession(
        prompt_file,
        project_config=project_config,
    ).extract_target_flow_graph(agent_names)
