from __future__ import annotations

from doctrine import model
from doctrine._compiler.naming import _authored_slot_allows_law
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    CompiledBodyItem,
    CompiledSection,
    IndexedUnit,
    ResolvedRouteLine,
    ResolvedSectionBodyItem,
    ResolvedSectionItem,
    ResolvedSectionRef,
    ResolvedWorkflowBody,
    ResolvedWorkflowSkillsItem,
)
from doctrine._compiler.support_files import _dotted_decl_name


class CompileWorkflowsMixin:
    """Workflow compile helpers for CompilationContext."""

    def _compile_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        slot_key: str = "workflow",
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
                slot_key=slot_key,
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
        slot_key: str = "workflow",
    ) -> CompiledSection:
        body: list[CompiledBodyItem] = list(workflow_body.preamble)
        if workflow_body.law is not None:
            if unit is None or agent_contract is None or owner_label is None:
                raise CompileError(
                    "Internal compiler error: workflow law requires unit, agent contract, and owner label"
                )
            if not _authored_slot_allows_law(slot_key):
                raise CompileError(
                    f"law may appear only on workflow or handoff_routing in {owner_label}: {slot_key}"
                )
            if body and body[-1] != "":
                body.append("")
            if slot_key == "handoff_routing":
                body.extend(
                    self._compile_handoff_routing_law(
                        workflow_body.law,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                    )
                )
            else:
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
                        body=self._compile_section_body(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReadableBlock):
                if unit is None or owner_label is None:
                    raise CompileError(
                        "Internal compiler error: workflow readable block compilation requires unit and owner label"
                    )
                body.append(
                    self._compile_workflow_root_readable_block(
                        item,
                        unit=unit,
                        owner_label=owner_label,
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
                    slot_key=slot_key,
                )
            )

        return CompiledSection(title=workflow_body.title, body=tuple(body))

    def _compile_workflow_root_readable_block(
        self,
        block: model.ReadableBlock,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ):
        return self._compile_authored_readable_block(
            block,
            unit=unit,
            owner_label=owner_label,
            surface_label="workflow bodies",
            section_body_compiler=lambda payload, nested_owner_label: self._compile_section_body(
                self._resolve_section_body_items(
                    payload,
                    unit=unit,
                    owner_label=nested_owner_label,
                ),
                unit=unit,
                owner_label=nested_owner_label,
            ),
        )

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
        match_bindings: dict[tuple[str, ...], str] = {}
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
                        match_bindings=match_bindings,
                    )
                )
            elif isinstance(item, model.RouteFromStmt):
                rendered.extend(
                    self._render_route_from_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                        match_bindings=match_bindings,
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
                        match_bindings=match_bindings,
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

    def _compile_handoff_routing_law(
        self,
        law_body: model.LawBody,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        flat_items = self._flatten_law_items(law_body, owner_label=owner_label)
        self._validate_handoff_routing_law(
            flat_items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

        lines: list[str] = []
        mode_bindings: dict[str, model.ModeStmt] = {}
        match_bindings: dict[tuple[str, ...], str] = {}
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
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                        match_bindings=match_bindings,
                    )
                )
            elif isinstance(item, model.RouteFromStmt):
                rendered.extend(
                    self._render_route_from_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                        match_bindings=match_bindings,
                    )
                )
            elif isinstance(item, model.WhenStmt):
                rendered.extend(
                    self._render_when_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                        match_bindings=match_bindings,
                    )
                )
            else:
                rendered.extend(
                    self._render_law_stmt_lines(
                        item,
                        unit=unit,
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

    def _compile_section_body(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        unit: IndexedUnit | None = None,
        owner_label: str | None = None,
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
                        body=self._compile_section_body(
                            item.items,
                            unit=unit,
                            owner_label=(
                                f"{owner_label}.{item.key}" if owner_label is not None else None
                            ),
                        ),
                    )
                )
            elif isinstance(item, model.ReadableBlock):
                if unit is None or owner_label is None:
                    raise CompileError(
                        "Internal compiler error: workflow readable block compilation requires unit and owner label"
                    )
                body.append(
                    self._compile_authored_readable_block(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow section bodies",
                        section_body_compiler=lambda payload, nested_owner_label: self._compile_section_body(
                            self._resolve_section_body_items(
                                payload,
                                unit=unit,
                                owner_label=nested_owner_label,
                            ),
                            unit=unit,
                            owner_label=nested_owner_label,
                        ),
                    )
                )
            elif isinstance(item, ResolvedRouteLine):
                body.append(f"{item.label} -> {item.target_display_name}")
            else:
                body.append(f"- {item.label}")

            previous_kind = current_kind

        return tuple(body)
