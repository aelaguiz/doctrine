from __future__ import annotations

import threading
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import doctrine._model.declarations as model
from doctrine._diagnostics.formatting import _build_excerpt
from doctrine._compiler.indexing import (
    FlowLoadKey,
    IndexedFlow,
    IndexedUnit,
    build_indexed_flow,
    load_flow,
    load_module,
    resolve_flow_entrypoint,
)
from doctrine._compiler.types import (
    CompiledAgent,
    CompiledField,
    CompiledFinalOutputSpec,
    CompiledSection,
    CompiledSkillPackage,
    FlowGraph,
)
from doctrine._compiler.resolved_types import (
    ActiveSkillBindAgentContext,
    FlowAgentKey,
    PreviousTurnAgentContext,
    SkillPackageHostCompileContext,
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
    """Stable boundary for compiling agents from one root prompt.

    `doctrine.compiler` re-exports this class. Module-level `compile_prompt`
    and `extract_target_flow_graph` are one-shot wrappers; hold a session
    directly when compiling several agents against the same root, since
    building the prompt graph is expensive and the flow cache must be shared
    across the calls.

    Lifecycle. `__init__` resolves the prompt root, loads the project config
    (translating `tomllib.TOMLDecodeError` to E299 and `ProjectConfigError`
    to E285), and pre-builds the root `IndexedFlow` into `_flow_cache`. Public
    methods: `compile_agent[_from_unit]`, `compile_agents[_from_units]`,
    `compile_skill_package`, `compile_readable_declaration`,
    `extract_target_flow_graph[_from_units]`. Every public compile catches
    `DoctrineError`, then calls `prepend_trace` + `ensure_location` so the
    surfaced diagnostic always pins a truthful site even when raised deep.

    Flow cache. `_flow_cache` maps `(resolved_prompt_root, resolved_flow_root)`
    to the already-loaded `IndexedFlow`. It is **shared across threads**, not
    thread-local: `_flow_lock` plus per-key `_flow_loading` events coordinate
    concurrent loads so each flow is built at most once. The root flow is
    seeded during `__init__` before any compile runs.

    Order preservation. `compile_agents` runs parallel agent compiles on a
    `ThreadPoolExecutor` but returns results in the caller's input order. It
    keys futures by bare `agent_name`, so the input tuple must contain
    distinct names; `compile_agents_from_units` keys on `(prompt_root,
    flow_root, agent_name)` so the same name across different flows is safe.

    `CompilationContext` (from `_compiler.context`) is built fresh per
    compile call. Per-call mutable state (active agent key, skill-bind
    context, previous-turn specs) lives on the context, not the session, so
    it never leaks between threads.

    `provided_prompt_roots` is a caller-owned input (see `project_config.py`
    for the contract). When both a `project_config` and non-empty provided
    roots are passed, the session merges them via
    `with_provided_prompt_roots` before resolving the compile config.
    """

    def __init__(
        self,
        prompt_file: model.PromptFile,
        *,
        project_config: ProjectConfig | None = None,
        provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
        skill_package_host_context: SkillPackageHostCompileContext | None = None,
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
                exc.path
                if exc.path is not None
                else resolved_project_config.path
                if resolved_project_config is not None
                else None
            )
            location, excerpt, caret_column = _project_config_site(
                config_path,
                line=exc.line,
                column=exc.column,
            )
            raise CompileError.from_parts(
                code="E285",
                summary="Invalid compile config",
                detail=str(exc),
                location=location,
                excerpt=excerpt,
                caret_column=caret_column,
            ) from exc

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
        self.skill_package_host_context = skill_package_host_context
        self.skill_package_scan_cache: dict[str, tuple[tuple["IndexedUnit", model.SkillPackageDecl], ...]] | None = None
        self._flow_cache: dict[FlowLoadKey, IndexedFlow] = {}
        self._flow_load_errors: dict[FlowLoadKey, Exception] = {}
        self._flow_loading: dict[FlowLoadKey, threading.Event] = {}
        self._flow_waits: dict[FlowLoadKey, FlowLoadKey] = {}
        self._flow_lock = threading.Lock()
        # Shared prompt graph data lives on the session; compile contexts stay task-local.
        root_entrypoint = resolve_flow_entrypoint(
            prompt_file.source_path,
            prompt_root=self.prompt_root,
        )
        prompt_file_overrides = (
            {}
            if prompt_file.source_path is None
            else {prompt_file.source_path.resolve(): prompt_file}
        )
        self.root_flow = build_indexed_flow(
            prompt_root=self.prompt_root,
            entrypoint_path=root_entrypoint,
            session=self,
            prompt_file_overrides=prompt_file_overrides,
        )
        self._flow_cache[
            (
                self.root_flow.prompt_root.resolve(),
                self.root_flow.flow_root.resolve(),
            )
        ] = self.root_flow

    def _new_flow_ready_event(self) -> threading.Event:
        return threading.Event()

    def compile_agent(
        self,
        agent_name: str,
        *,
        previous_turn_contexts: dict[FlowAgentKey, PreviousTurnAgentContext] | None = None,
    ) -> CompiledAgent:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(
                self,
                previous_turn_contexts=previous_turn_contexts,
            ).compile_agent(agent_name)
        except DoctrineError as exc:
            # Trace frames add session context, but only fill the primary site
            # when the inner diagnostic did not already prove one.
            raise exc.prepend_trace(
                f"compile agent `{agent_name}`",
                location=path_location(self.root_flow.entrypoint_path),
            ).ensure_location(path=self.root_flow.entrypoint_path)

    def compile_agent_from_unit(
        self,
        unit: IndexedUnit,
        agent_name: str,
        *,
        previous_turn_contexts: dict[FlowAgentKey, PreviousTurnAgentContext] | None = None,
    ) -> CompiledAgent:
        from doctrine._compiler.context import CompilationContext

        try:
            return CompilationContext(
                self,
                previous_turn_contexts=previous_turn_contexts,
            ).compile_agent_from_unit(unit, agent_name)
        except DoctrineError as exc:
            source_path = unit.prompt_file.source_path
            dotted_name = ".".join((*unit.module_parts, agent_name)) or agent_name
            raise exc.prepend_trace(
                f"compile agent `{dotted_name}`",
                location=path_location(source_path),
            ).ensure_location(path=source_path)

    def compile_agents(
        self,
        agent_names: tuple[str, ...],
        *,
        previous_turn_contexts: dict[FlowAgentKey, PreviousTurnAgentContext] | None = None,
    ) -> tuple[CompiledAgent, ...]:
        if len(agent_names) <= 1:
            return tuple(
                self.compile_agent(
                    agent_name,
                    previous_turn_contexts=previous_turn_contexts,
                )
                for agent_name in agent_names
            )

        with ThreadPoolExecutor(max_workers=default_worker_count(len(agent_names))) as executor:
            futures = {
                agent_name: executor.submit(
                    self.compile_agent,
                    agent_name,
                    previous_turn_contexts=previous_turn_contexts,
                )
                for agent_name in agent_names
            }
            return tuple(futures[agent_name].result() for agent_name in agent_names)

    def compile_agents_from_units(
        self,
        agent_roots: tuple[tuple[IndexedUnit, str], ...],
        *,
        previous_turn_contexts: dict[FlowAgentKey, PreviousTurnAgentContext] | None = None,
    ) -> tuple[CompiledAgent, ...]:
        if len(agent_roots) <= 1:
            return tuple(
                self.compile_agent_from_unit(
                    unit,
                    agent_name,
                    previous_turn_contexts=previous_turn_contexts,
                )
                for unit, agent_name in agent_roots
            )

        keys = []
        for unit, agent_name in agent_roots:
            flow = self.flow_for_unit(unit)
            keys.append(
                (flow.prompt_root.resolve(), flow.flow_root.resolve(), agent_name)
            )
        with ThreadPoolExecutor(max_workers=default_worker_count(len(agent_roots))) as executor:
            futures = {
                key: executor.submit(
                    self.compile_agent_from_unit,
                    unit,
                    agent_name,
                    previous_turn_contexts=previous_turn_contexts,
                )
                for key, (unit, agent_name) in zip(keys, agent_roots)
            }
            return tuple(futures[key].result() for key in keys)

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
                location=path_location(self.root_flow.entrypoint_path),
            ).ensure_location(path=self.root_flow.entrypoint_path)

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
                location=path_location(self.root_flow.entrypoint_path),
            ).ensure_location(path=self.root_flow.entrypoint_path)

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
        previous_turn_contexts: dict[FlowAgentKey, PreviousTurnAgentContext] | None = None,
        active_agent_key: FlowAgentKey | None = None,
        active_skill_bind_agent_context: ActiveSkillBindAgentContext | None = None,
        active_previous_turn_input_specs: dict[tuple[tuple[str, ...], str], object]
        | None = None,
    ) -> CompiledField | None:
        from doctrine._compiler.context import CompilationContext

        context = CompilationContext(
            self,
            previous_turn_contexts=previous_turn_contexts,
        )
        context._active_agent_key = active_agent_key
        context._active_skill_bind_agent_context = active_skill_bind_agent_context
        context._active_previous_turn_input_specs = active_previous_turn_input_specs or {}
        return context._compile_agent_field(
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
                location=path_location(self.root_flow.entrypoint_path),
            ).ensure_location(path=self.root_flow.entrypoint_path)

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
                location=path_location(self.root_flow.entrypoint_path),
            ).ensure_location(path=self.root_flow.entrypoint_path)

    def load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        if not module_parts:
            return self.root_flow.entrypoint_unit
        return load_module(
            self,
            module_parts,
            prompt_root=None,
            package_import_root=self.root_flow.entrypoint_unit.package_root,
            ancestry=(),
        )

    def flow_for_unit(self, unit: IndexedUnit) -> IndexedFlow:
        source_path = unit.prompt_file.source_path
        if source_path is None:
            return self.root_flow
        entrypoint_path = resolve_flow_entrypoint(
            source_path,
            prompt_root=unit.prompt_root,
        )
        flow_key = (unit.prompt_root.resolve(), entrypoint_path.parent.resolve())
        cached = self._flow_cache.get(flow_key)
        if cached is not None:
            return cached
        return load_flow(
            self,
            source_path=source_path,
            prompt_root=unit.prompt_root,
            ancestry=(),
            entrypoint_module_source_kind=unit.module_source_kind,
        )

    def flow_by_key(
        self,
        prompt_root: Path,
        flow_root: Path,
    ) -> IndexedFlow | None:
        return self._flow_cache.get((prompt_root.resolve(), flow_root.resolve()))

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


def _project_config_site(
    config_path: Path | None,
    *,
    line: int | None,
    column: int | None,
) -> tuple[DiagnosticLocation | None, tuple[object, ...], int | None]:
    if config_path is None:
        return None, (), None
    resolved_path = config_path.resolve()
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
    """One-shot convenience wrapper: build a session, compile one agent, discard.

    Prefer holding a `CompilationSession` directly when compiling more than
    one agent against the same prompt — the per-session flow cache is the
    reason building a fresh session per agent is wasteful.
    """
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
    """One-shot convenience wrapper: build a session and extract a flow graph.

    Equivalent to `CompilationSession(...).extract_target_flow_graph(agent_names)`.
    """
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
