from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyprompt import model
from pyprompt.parser import parse_file


class CompileError(RuntimeError):
    """Fail-loud compiler error for the shipped subset."""


@dataclass(slots=True, frozen=True)
class CompiledSection:
    title: str
    preamble: tuple[str, ...]
    children: tuple["CompiledSection", ...]


@dataclass(slots=True, frozen=True)
class CompiledAgent:
    name: str
    role: model.RoleScalar | CompiledSection
    workflow: CompiledSection


@dataclass(slots=True, frozen=True)
class IndexedUnit:
    module_parts: tuple[str, ...]
    prompt_file: model.PromptFile
    imports: tuple[model.ImportDecl, ...]
    workflows_by_name: dict[str, model.WorkflowDecl]
    agents_by_name: dict[str, model.Agent]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]


@dataclass(slots=True, frozen=True)
class ResolvedSectionItem:
    key: str
    title: str
    lines: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ResolvedUseItem:
    key: str
    target_unit: IndexedUnit
    workflow_decl: model.WorkflowDecl


ResolvedWorkflowItem = ResolvedSectionItem | ResolvedUseItem


@dataclass(slots=True, frozen=True)
class ResolvedWorkflowBody:
    title: str
    preamble: tuple[str, ...]
    items: tuple[ResolvedWorkflowItem, ...]


class CompilationContext:
    def __init__(self, prompt_file: model.PromptFile):
        self.prompt_root = _resolve_prompt_root(prompt_file.source_path)
        self._module_cache: dict[tuple[str, ...], IndexedUnit] = {}
        self._loading_modules: set[tuple[str, ...]] = set()
        self._workflow_compile_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._agent_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._resolved_workflow_cache: dict[tuple[tuple[str, ...], str], ResolvedWorkflowBody] = {}
        self._resolved_agent_cache: dict[tuple[tuple[str, ...], str], ResolvedWorkflowBody] = {}
        self.root_unit = self._index_unit(prompt_file, module_parts=())

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        agent = self.root_unit.agents_by_name.get(agent_name)
        if agent is None:
            raise CompileError(f"Missing target agent: {agent_name}")
        if agent.abstract:
            raise CompileError(f"Abstract agent does not render: {agent_name}")

        return self._compile_agent_decl(agent, unit=self.root_unit)

    def _compile_agent_decl(self, agent: model.Agent, *, unit: IndexedUnit) -> CompiledAgent:
        role_field, _workflow_field = self._split_agent_fields(agent)

        compiled_role: model.RoleScalar | CompiledSection
        if isinstance(role_field, model.RoleScalar):
            compiled_role = role_field
        else:
            compiled_role = CompiledSection(
                title=role_field.title,
                preamble=role_field.lines,
                children=(),
            )

        return CompiledAgent(
            name=agent.name,
            role=compiled_role,
            workflow=self._compile_resolved_workflow(
                self._resolve_agent_workflow(agent, unit=unit),
            ),
        )

    def _compile_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
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
                self._resolve_workflow_decl(workflow_decl, unit=unit)
            )
        finally:
            self._workflow_compile_stack.pop()

    def _compile_resolved_workflow(
        self,
        workflow_body: ResolvedWorkflowBody,
    ) -> CompiledSection:
        compiled_children: list[CompiledSection] = []

        for item in workflow_body.items:
            if isinstance(item, ResolvedSectionItem):
                compiled_children.append(
                    CompiledSection(title=item.title, preamble=item.lines, children=())
                )
                continue

            compiled_children.append(
                self._compile_workflow_decl(item.workflow_decl, unit=item.target_unit)
            )

        return CompiledSection(
            title=workflow_body.title,
            preamble=workflow_body.preamble,
            children=tuple(compiled_children),
        )

    def _resolve_workflow_target(
        self, target: model.WorkflowTarget, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        if not target.module_parts:
            workflow_decl = unit.workflows_by_name.get(target.declaration_name)
            if workflow_decl is None:
                raise CompileError(f"Missing local workflow declaration: {target.declaration_name}")
            return unit, workflow_decl

        if target.module_parts == unit.module_parts:
            workflow_decl = unit.workflows_by_name.get(target.declaration_name)
            if workflow_decl is None:
                dotted_name = ".".join((*target.module_parts, target.declaration_name))
                raise CompileError(f"Missing imported declaration: {dotted_name}")
            return unit, workflow_decl

        target_unit = unit.imported_units.get(target.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(target.module_parts)}")

        workflow_decl = target_unit.workflows_by_name.get(target.declaration_name)
        if workflow_decl is None:
            dotted_name = ".".join((*target.module_parts, target.declaration_name))
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        return target_unit, workflow_decl

    def _resolve_agent_workflow(
        self, agent: model.Agent, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        agent_key = (unit.module_parts, agent.name)
        cached = self._resolved_agent_cache.get(agent_key)
        if cached is not None:
            return cached

        if agent_key in self._agent_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._agent_resolution_stack, agent_key]
            )
            raise CompileError(f"Cyclic agent inheritance: {cycle}")

        _role_field, workflow_field = self._split_agent_fields(agent)
        self._agent_resolution_stack.append(agent_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if agent.parent_name is not None:
                parent_agent = unit.agents_by_name.get(agent.parent_name)
                if parent_agent is None:
                    raise CompileError(
                        f"Missing parent agent for {agent.name}: {agent.parent_name}"
                    )
                parent_workflow = self._resolve_agent_workflow(parent_agent, unit=unit)
                parent_label = f"agent {parent_agent.name}"

            resolved = self._resolve_workflow_body(
                workflow_field,
                unit=unit,
                owner_label=f"agent {agent.name}",
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._resolved_agent_cache[agent_key] = resolved
            return resolved
        finally:
            self._agent_resolution_stack.pop()

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
            if workflow_decl.parent_name is not None:
                parent_decl = unit.workflows_by_name.get(workflow_decl.parent_name)
                if parent_decl is None:
                    raise CompileError(
                        f"Missing parent workflow for {workflow_decl.name}: {workflow_decl.parent_name}"
                    )
                parent_workflow = self._resolve_workflow_decl(parent_decl, unit=unit)
                parent_label = f"workflow {workflow_decl.parent_name}"

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

    def _resolve_workflow_body(
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
                preamble=workflow_body.preamble,
                items=self._resolve_non_inherited_items(
                    workflow_body.items,
                    unit=unit,
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
                    ResolvedSectionItem(key=key, title=item.title, lines=item.lines)
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_target(
                    item.target,
                    unit=unit,
                )
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
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
                        lines=item.lines,
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_target(item.target, unit=unit)
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
            preamble=workflow_body.preamble,
            items=tuple(resolved_items),
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
                    ResolvedSectionItem(key=key, title=item.title, lines=item.lines)
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_target(
                    item.target,
                    unit=unit,
                )
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _split_agent_fields(
        self, agent: model.Agent
    ) -> tuple[model.RoleScalar | model.RoleBlock, model.WorkflowBody]:
        if len(agent.fields) != 2:
            raise CompileError(
                f"Agent {agent.name} is outside the shipped subset: expected exactly one role and one workflow."
            )

        role_field, workflow_field = agent.fields
        if not isinstance(role_field, (model.RoleScalar, model.RoleBlock)) or not isinstance(
            workflow_field, model.WorkflowBody
        ):
            raise CompileError(
                f"Agent {agent.name} is outside the shipped subset: expected `role` followed by `workflow`."
            )
        return role_field, workflow_field

    def _index_unit(
        self, prompt_file: model.PromptFile, *, module_parts: tuple[str, ...]
    ) -> IndexedUnit:
        imports: list[model.ImportDecl] = []
        workflows_by_name: dict[str, model.WorkflowDecl] = {}
        agents_by_name: dict[str, model.Agent] = {}

        for declaration in prompt_file.declarations:
            if isinstance(declaration, model.ImportDecl):
                imports.append(declaration)
                continue
            if isinstance(declaration, model.WorkflowDecl):
                existing = workflows_by_name.get(declaration.name)
                if existing is not None:
                    dotted_name = ".".join((*module_parts, declaration.name)) or declaration.name
                    raise CompileError(f"Duplicate declaration name: {dotted_name}")
                workflows_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.Agent):
                existing = agents_by_name.get(declaration.name)
                if existing is not None:
                    raise CompileError(f"Duplicate agent name: {declaration.name}")
                agents_by_name[declaration.name] = declaration
                continue
            raise CompileError(f"Unsupported declaration type: {type(declaration).__name__}")

        imported_units: dict[tuple[str, ...], IndexedUnit] = {}
        for import_decl in imports:
            resolved_module_parts = _resolve_import_path(import_decl.path, module_parts=module_parts)
            imported_units[resolved_module_parts] = self._load_module(resolved_module_parts)

        return IndexedUnit(
            module_parts=module_parts,
            prompt_file=prompt_file,
            imports=tuple(imports),
            workflows_by_name=workflows_by_name,
            agents_by_name=agents_by_name,
            imported_units=imported_units,
        )

    def _load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        cached = self._module_cache.get(module_parts)
        if cached is not None:
            return cached

        if module_parts in self._loading_modules:
            raise CompileError(f"Cyclic import module: {'.'.join(module_parts)}")

        module_path = self.prompt_root.joinpath(*module_parts).with_suffix(".prompt")
        if not module_path.is_file():
            raise CompileError(f"Missing import module: {'.'.join(module_parts)}")

        self._loading_modules.add(module_parts)
        try:
            indexed = self._index_unit(parse_file(module_path), module_parts=module_parts)
            self._module_cache[module_parts] = indexed
            return indexed
        finally:
            self._loading_modules.remove(module_parts)


def compile_prompt(prompt_file: model.PromptFile, agent_name: str) -> CompiledAgent:
    return CompilationContext(prompt_file).compile_agent(agent_name)


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
        raise CompileError(
            f"Relative import walks above prompts root: {dotted_import}"
        )

    return (*package_parts, *import_path.module_parts)


def _dotted_decl_name(module_parts: tuple[str, ...], name: str) -> str:
    return ".".join((*module_parts, name)) if module_parts else name
