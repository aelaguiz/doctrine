from __future__ import annotations

from collections import Counter
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
    agents: tuple[model.Agent, ...]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]


class CompilationContext:
    def __init__(self, prompt_file: model.PromptFile):
        self.prompt_root = _resolve_prompt_root(prompt_file.source_path)
        self._module_cache: dict[tuple[str, ...], IndexedUnit] = {}
        self._loading_modules: set[tuple[str, ...]] = set()
        self._workflow_stack: list[tuple[tuple[str, ...], str]] = []
        self.root_unit = self._index_unit(prompt_file, module_parts=())

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        duplicate_names = [
            name
            for name, count in Counter(agent.name for agent in self.root_unit.agents).items()
            if count > 1
        ]
        if duplicate_names:
            raise CompileError(f"Duplicate agent name(s): {', '.join(sorted(duplicate_names))}")

        selected = [agent for agent in self.root_unit.agents if agent.name == agent_name]
        if not selected:
            raise CompileError(f"Missing target agent: {agent_name}")

        return self._compile_agent_decl(selected[0], unit=self.root_unit)

    def _compile_agent_decl(self, agent: model.Agent, *, unit: IndexedUnit) -> CompiledAgent:
        # The shipped subset still requires one explicit role and one explicit workflow.
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
            workflow=self._compile_workflow_body(
                workflow_field,
                unit=unit,
                owner_label=f"agent {agent.name}",
            ),
        )

    def _compile_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> CompiledSection:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if workflow_key in self._workflow_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name for parts, name in [*self._workflow_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow composition: {cycle}")

        self._workflow_stack.append(workflow_key)
        try:
            return self._compile_workflow_body(
                workflow_decl.body,
                unit=unit,
                owner_label=".".join((*unit.module_parts, workflow_decl.name))
                if unit.module_parts
                else workflow_decl.name,
            )
        finally:
            self._workflow_stack.pop()

    def _compile_workflow_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> CompiledSection:
        seen_keys: set[str] = set()
        compiled_children: list[CompiledSection] = []

        for item in workflow_body.items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                compiled_children.append(
                    CompiledSection(title=item.title, preamble=item.lines, children=())
                )
                continue

            target_unit, workflow_decl = self._resolve_workflow_use(item, unit=unit)
            compiled_children.append(self._compile_workflow_decl(workflow_decl, unit=target_unit))

        return CompiledSection(
            title=workflow_body.title,
            preamble=workflow_body.preamble,
            children=tuple(compiled_children),
        )

    def _resolve_workflow_use(
        self, workflow_use: model.WorkflowUse, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        target = workflow_use.target

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

    def _index_unit(
        self, prompt_file: model.PromptFile, *, module_parts: tuple[str, ...]
    ) -> IndexedUnit:
        imports: list[model.ImportDecl] = []
        workflows_by_name: dict[str, model.WorkflowDecl] = {}
        agents: list[model.Agent] = []

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
                agents.append(declaration)
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
            agents=tuple(agents),
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
