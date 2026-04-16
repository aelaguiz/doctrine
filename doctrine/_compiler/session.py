from __future__ import annotations

import threading
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import doctrine._model.declarations as model
from doctrine._diagnostics.formatting import _build_excerpt
from doctrine._compiler.indexing import IndexedUnit, ModuleLoadKey, index_unit, load_module
from doctrine._compiler.types import (
    CompiledAgent,
    CompiledField,
    CompiledFinalOutputSpec,
    CompiledSection,
    CompiledSkillPackage,
    FlowGraph,
)
from doctrine.diagnostics import CompileError, DiagnosticLocation, DoctrineError
from doctrine.project_config import (
    ProvidedPromptRoot,
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
        provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
    ):
        self.prompt_root = resolve_prompt_root(prompt_file.source_path)
        resolved_project_config = project_config
        try:
            if resolved_project_config is None:
                resolved_project_config = load_project_config_for_source(
                    prompt_file.source_path,
                    provided_prompt_roots=provided_prompt_roots,
                )
            elif provided_prompt_roots:
                resolved_project_config = (
                    resolved_project_config.with_provided_prompt_roots(
                        provided_prompt_roots
                    )
                )
            compile_config = resolved_project_config.resolve_compile_config()
        except tomllib.TOMLDecodeError as exc:
            config_path = project_config.path if project_config is not None else None
            if config_path is None and prompt_file.source_path is not None:
                config_path = find_nearest_pyproject(prompt_file.source_path.parent)
            location, excerpt, caret_column = _toml_decode_site(config_path, exc)
            raise CompileError.from_parts(
                code="E299",
                summary="Compile failure",
                detail="The Doctrine project config is not valid TOML.",
                location=location,
                excerpt=excerpt,
                caret_column=caret_column,
                cause=getattr(exc, "msg", str(exc)),
            ) from exc
        except ProjectConfigError as exc:
            config_path = (
                resolved_project_config.path
                if resolved_project_config is not None
                else None
            )
            raise CompileError(str(exc)).ensure_location(path=config_path) from exc

        self.project_config = resolved_project_config
        self.provided_prompt_roots = compile_config.provided_prompt_roots
        self.import_root_labels = _import_root_labels(
            self.prompt_root,
            compile_config.additional_prompt_roots,
            compile_config.provided_prompt_roots,
        )
        self.import_roots = resolve_import_roots(
            self.prompt_root,
            compile_config.additional_prompt_roots,
            compile_config.provided_prompt_roots,
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

    def provided_prompt_root_for(
        self,
        prompt_root: Path,
    ) -> ProvidedPromptRoot | None:
        resolved_prompt_root = prompt_root.resolve()
        for provided_root in self.provided_prompt_roots:
            if Path(provided_root.path).resolve() == resolved_prompt_root:
                return provided_root
        return None


def _toml_decode_site(
    config_path: Path | None,
    exc: tomllib.TOMLDecodeError,
) -> tuple[DiagnosticLocation | None, tuple[object, ...], int | None]:
    if config_path is None:
        return None, (), None
    resolved_path = config_path.resolve()
    line = getattr(exc, "lineno", None)
    column = getattr(exc, "colno", None)
    if line is None or column is None:
        return path_location(resolved_path), (), None
    try:
        source = resolved_path.read_text(encoding="utf-8")
    except OSError:
        return DiagnosticLocation(path=resolved_path, line=line, column=column), (), None
    excerpt, caret_column = _build_excerpt(source, line=line, column=column)
    return (
        DiagnosticLocation(path=resolved_path, line=line, column=column),
        excerpt,
        caret_column,
    )


def compile_prompt(
    prompt_file: model.PromptFile,
    agent_name: str,
    *,
    project_config: ProjectConfig | None = None,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> CompiledAgent:
    return CompilationSession(
        prompt_file,
        project_config=project_config,
        provided_prompt_roots=provided_prompt_roots,
    ).compile_agent(agent_name)


def extract_target_flow_graph(
    prompt_file: model.PromptFile,
    agent_names: tuple[str, ...],
    *,
    project_config: ProjectConfig | None = None,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> FlowGraph:
    return CompilationSession(
        prompt_file,
        project_config=project_config,
        provided_prompt_roots=provided_prompt_roots,
    ).extract_target_flow_graph(agent_names)


def _import_root_labels(
    prompt_root: Path,
    additional_prompt_roots: tuple[Path, ...],
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...],
) -> dict[Path, str]:
    labels = {prompt_root.resolve(): f"entrypoint prompts root `{prompt_root}`"}
    for root in additional_prompt_roots:
        labels[root.resolve()] = f"configured prompts root `{root}`"
    for root in provided_prompt_roots:
        resolved_path = Path(root.path).resolve()
        labels[resolved_path] = (
            f"provided prompts root `{root.name}` at `{resolved_path}`"
        )
    return labels
