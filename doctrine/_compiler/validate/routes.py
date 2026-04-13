from __future__ import annotations

from dataclasses import replace

from doctrine._compiler.naming import _dotted_ref_name, _name_ref_from_dotted_name
from doctrine._compiler.resolved_types import *  # noqa: F401,F403

_LAW_TARGET_ALLOWED_KINDS = {
    "current_artifact": ("input", "output"),
    "invalidate": ("input", "output", "schema_group"),
    "own_only": ("input", "output", "schema_family"),
    "path_set": ("input", "output"),
}
_PRESERVE_TARGET_ALLOWED_KINDS = {
    "exact": ("input", "output", "schema_family"),
    "structure": ("input", "output"),
    "decisions": ("input", "output"),
    "mapping": ("input", "output", "schema_family", "grounding"),
    "vocabulary": ("enum", "input", "output", "schema_family"),
}


class ValidateRoutesMixin:
    """Route and workflow-law validation helpers for ValidateMixin."""

    def _validate_route_target(self, ref: model.NameRef, *, unit: IndexedUnit) -> None:
        _target_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        if agent.abstract:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Route target must be a concrete agent: {dotted_name}")

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
                        allowed_kinds=("input", "output", "schema_group"),
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
                    if (
                        "truth" in ignore.bases or not ignore.bases
                    ) and self._path_set_contains_path(
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
                        allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
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
                            allowed_kinds=_PRESERVE_TARGET_ALLOWED_KINDS["exact"],
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

    def _validate_handoff_routing_law(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        self._validate_handoff_routing_law_stmt_tree(
            items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

    def _validate_handoff_routing_law_stmt_tree(
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
                    self._validate_handoff_routing_law_stmt_tree(
                        case.items,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=local_mode_bindings,
                    )
                continue
            if isinstance(item, model.RouteFromStmt):
                self._validate_route_from_stmt(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
                continue
            if isinstance(item, model.WhenStmt):
                self._validate_handoff_routing_law_stmt_tree(
                    item.items,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                continue
            if isinstance(item, model.LawRouteStmt):
                self._validate_route_target(item.target, unit=unit)
                continue
            if isinstance(item, (model.ActiveWhenStmt, model.StopStmt)):
                continue
            raise CompileError(
                "handoff_routing law only supports active when, mode, when, match, route_from, stop, "
                f"and route in {owner_label}: {self._law_stmt_name(item)}"
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
            route_branch = self._route_semantic_branch_from_route(
                route,
                label=route.label,
                unit=unit,
            )
            next_owner_fields_found = False
            for (_output_key, (output_unit, output_decl)) in output_items:
                for path, item in self._iter_output_items_with_paths(output_decl.items):
                    if not path or path[-1] != "next_owner":
                        continue
                    next_owner_fields_found = True
                    self._validate_route_owner_alignment(
                        item,
                        route_branch=route_branch,
                        unit=output_unit,
                        owner_label=f"output {output_decl.name}.{'.'.join(path)}",
                        error_message=(
                            "next_owner field must interpolate routed target "
                            f"in {owner_label}: {output_decl.name}.{'.'.join(path)} -> "
                            f"{route_branch.target_name}"
                        ),
                    )
            if next_owner_fields_found:
                continue

    def _validate_route_owner_alignment(
        self,
        item: model.AnyRecordItem,
        *,
        route_branch: RouteSemanticBranch,
        unit: IndexedUnit,
        owner_label: str,
        error_message: str,
        fallback_unit: IndexedUnit | None = None,
    ) -> None:
        route_semantics = RouteSemanticContext(
            branches=(route_branch,),
            route_required=True,
        )
        if self._record_item_mentions_agent(
            item,
            target_unit_module_parts=route_branch.target_module_parts,
            target_agent_name=route_branch.target_name,
            unit=unit,
            fallback_unit=fallback_unit,
            owner_label=owner_label,
            route_semantics=route_semantics,
        ):
            return
        raise CompileError(error_message)

    def _record_item_mentions_agent(
        self,
        item: model.AnyRecordItem,
        *,
        target_unit_module_parts: tuple[str, ...],
        target_agent_name: str,
        unit: IndexedUnit,
        fallback_unit: IndexedUnit | None = None,
        owner_label: str,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        if (
            isinstance(item, (model.RecordScalar, model.GuardedOutputScalar))
            and isinstance(item.value, model.NameRef)
            and self._name_ref_matches_agent(
                item.value,
                target_unit_module_parts=target_unit_module_parts,
                target_agent_name=target_agent_name,
                unit=unit,
                fallback_unit=fallback_unit,
                owner_label=owner_label,
            )
        ):
            return True
        if (
            isinstance(item, (model.RecordScalar, model.GuardedOutputScalar))
            and isinstance(item.value, model.NameRef)
            and self._addressable_ref_matches_agent(
                model.AddressableRef(root=item.value, path=()),
                target_unit_module_parts=target_unit_module_parts,
                target_agent_name=target_agent_name,
                unit=unit,
                fallback_unit=fallback_unit,
                owner_label=owner_label,
                route_semantics=route_semantics,
            )
        ):
            return True

        return any(
            self._addressable_ref_matches_agent(
                ref,
                target_unit_module_parts=target_unit_module_parts,
                target_agent_name=target_agent_name,
                unit=unit,
                fallback_unit=fallback_unit,
                owner_label=owner_label,
                route_semantics=route_semantics,
            )
            for ref in self._iter_record_item_interpolation_refs(item)
        )

    def _addressable_ref_matches_agent(
        self,
        ref: model.AddressableRef,
        *,
        target_unit_module_parts: tuple[str, ...],
        target_agent_name: str,
        unit: IndexedUnit,
        fallback_unit: IndexedUnit | None = None,
        owner_label: str,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        route_parts = self._route_semantic_parts(ref)
        if (
            route_semantics is not None
            and route_parts in {
                ("route", "next_owner"),
                ("route", "next_owner", "name"),
                ("route", "next_owner", "key"),
                ("route", "next_owner", "title"),
            }
        ):
            return any(
                branch.target_name == target_agent_name
                and branch.target_module_parts == target_unit_module_parts
                for branch in route_semantics.branches
            )
        try:
            root_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="next_owner interpolation ref",
                missing_local_label="next_owner",
            )
        except CompileError:
            if fallback_unit is None:
                return False
            try:
                root_unit, root_decl = self._resolve_addressable_root_decl(
                    ref.root,
                    unit=fallback_unit,
                    owner_label=owner_label,
                    ambiguous_label="next_owner interpolation ref",
                    missing_local_label="next_owner",
                )
            except CompileError:
                return False

        if not isinstance(root_decl, model.Agent):
            return False
        if root_decl.name != target_agent_name or root_unit.module_parts != target_unit_module_parts:
            return False
        return not ref.path or ref.path in {("name",), ("key",), ("title",)}

    def _name_ref_matches_agent(
        self,
        ref: model.NameRef,
        *,
        target_unit_module_parts: tuple[str, ...],
        target_agent_name: str,
        unit: IndexedUnit,
        fallback_unit: IndexedUnit | None = None,
        owner_label: str,
    ) -> bool:
        try:
            ref_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        except CompileError:
            if fallback_unit is None:
                return False
            try:
                ref_unit, agent = self._resolve_agent_ref(ref, unit=fallback_unit)
            except CompileError:
                return False
        _ = owner_label
        return agent.name == target_agent_name and ref_unit.module_parts == target_unit_module_parts

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
            if isinstance(item, model.RouteFromStmt):
                self._validate_route_from_stmt(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
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
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["current_artifact"],
                )
                continue
            if isinstance(item, model.InvalidateStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="invalidate",
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["invalidate"],
                )
                continue
            if isinstance(item, model.OwnOnlyStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
                )
                continue
            if isinstance(item, (model.SupportOnlyStmt, model.IgnoreStmt, model.ForbidStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["path_set"],
                )
                continue
            if isinstance(item, model.PreserveStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=f"preserve {item.kind}",
                    allowed_kinds=_PRESERVE_TARGET_ALLOWED_KINDS[item.kind],
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

    def _validate_route_from_stmt(
        self,
        stmt: model.RouteFromStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        enum_unit, enum_decl = self._resolve_decl_ref(
            stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        seen_members: set[str] = set()
        saw_else = False
        for case in stmt.cases:
            if case.head is None:
                if saw_else:
                    raise CompileError(f"Duplicate route_from arm in {owner_label}: else")
                saw_else = True
                continue
            member = self._resolve_route_from_member(
                case.head,
                enum_decl=enum_decl,
                enum_unit=enum_unit,
                owner_label=owner_label,
            )
            if member.value in seen_members:
                raise CompileError(
                    f"Duplicate route_from arm in {owner_label}: {member.value}"
                )
            seen_members.add(member.value)

        self._validate_route_from_selector_expr(
            stmt.expr,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )
        fixed_choice = self._resolve_constant_enum_member(stmt.expr, unit=unit)
        if fixed_choice is not None and not any(
            member.value == fixed_choice for member in enum_decl.members
        ):
            raise CompileError(
                f"route_from selector is outside enum {enum_decl.name} in {owner_label}: {fixed_choice}"
            )

        if any(case.head is None for case in stmt.cases):
            explicit_values: set[str] = set()
            for case in stmt.cases:
                if case.head is None:
                    continue
                member = self._resolve_route_from_member(
                    case.head,
                    enum_decl=enum_decl,
                    enum_unit=enum_unit,
                    owner_label=owner_label,
                )
                explicit_values.add(member.value)
            if explicit_values == {member.value for member in enum_decl.members}:
                raise CompileError(
                    f"route_from else is unreachable in {owner_label}: {enum_decl.name}"
                )
        else:
            seen_members = set()
            for case in stmt.cases:
                member = self._resolve_route_from_member(
                    case.head,
                    enum_decl=enum_decl,
                    enum_unit=enum_unit,
                    owner_label=owner_label,
                )
                seen_members.add(member.value)
            expected_members = {member.value for member in enum_decl.members}
            if seen_members != expected_members:
                raise CompileError(
                    f"route_from on {enum_decl.name} must be exhaustive or include else in {owner_label}"
                )

        for case in stmt.cases:
            self._validate_route_target(case.route.target, unit=unit)

    def _validate_route_from_selector_expr(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        if not isinstance(expr, model.ExprRef):
            raise CompileError(
                "route_from selector reads invalid source in "
                f"{owner_label}: {self._render_expr(expr, unit=unit)}"
            )
        if self._expr_ref_matches_enum_member(expr, unit=unit):
            return
        self._validate_route_from_selector_ref(
            expr,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

    def _validate_route_from_selector_ref(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        for split_at in range(len(ref.parts), 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            field_path = ref.parts[split_at:]
            if self._ref_exists_in_registry(root, unit=unit, registry_name="inputs_by_name"):
                input_unit, input_decl = self._resolve_input_decl(root, unit=unit)
                if self._resolve_route_from_selector_field_node(
                    input_decl,
                    field_path=field_path,
                    unit=input_unit,
                ) is not None:
                    return
                break
            if self._ref_exists_in_registry(root, unit=unit, registry_name="outputs_by_name"):
                output_unit, output_decl = self._resolve_output_decl(root, unit=unit)
                if (output_unit.module_parts, output_decl.name) not in agent_contract.outputs:
                    break
                if self._resolve_route_from_selector_field_node(
                    output_decl,
                    field_path=field_path,
                    unit=output_unit,
                ) is not None:
                    return
                break
        raise CompileError(
            f"route_from selector reads invalid source in {owner_label}: {'.'.join(ref.parts)}"
        )

    def _resolve_route_from_selector_field_node(
        self,
        decl: model.InputDecl | model.OutputDecl,
        *,
        field_path: tuple[str, ...],
        unit: IndexedUnit,
    ) -> AddressableNode | None:
        if not field_path:
            return None
        current = AddressableNode(unit=unit, root_decl=decl, target=decl)
        for segment in field_path:
            children = self._get_addressable_children(current)
            if children is None:
                return None
            current = children.get(segment)
            if current is None:
                return None
        return current

    def _resolve_route_from_member(
        self,
        expr: model.Expr | None,
        *,
        enum_decl: model.EnumDecl,
        enum_unit: IndexedUnit,
        owner_label: str,
    ) -> model.EnumMember:
        if expr is None:
            raise CompileError(f"route_from arm must name an enum member in {owner_label}")
        member_value = self._resolve_constant_enum_member(expr, unit=enum_unit)
        if member_value is None:
            raise CompileError(
                f"route_from arm must name a member of {enum_decl.name} in {owner_label}"
            )
        member = next((item for item in enum_decl.members if item.value == member_value), None)
        if member is None:
            raise CompileError(
                f"route_from arm is outside enum {enum_decl.name} in {owner_label}: {member_value}"
            )
        return member

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
            if isinstance(item, model.RouteFromStmt):
                next_branches = []
                for current_branch in branches:
                    for case in self._select_route_from_cases(
                        item,
                        unit=unit,
                    ):
                        next_branches.append(
                            self._branch_with_stmt(
                                current_branch,
                                self._route_from_case_route(item, case),
                            )
                        )
                branches = tuple(next_branches)
                index += 1
                continue
            branches = tuple(
                self._branch_with_stmt(current_branch, item) for current_branch in branches
            )
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

    def _select_route_from_cases(
        self,
        stmt: model.RouteFromStmt,
        *,
        unit: IndexedUnit,
    ) -> tuple[model.RouteFromArm, ...]:
        fixed_value = self._resolve_constant_enum_member(stmt.expr, unit=unit)
        if fixed_value is None:
            return stmt.cases

        exact_matches = tuple(
            case
            for case in stmt.cases
            if case.head is not None
            and self._resolve_constant_enum_member(case.head, unit=unit) == fixed_value
        )
        if exact_matches:
            return exact_matches
        else_matches = tuple(case for case in stmt.cases if case.head is None)
        if else_matches:
            return else_matches
        return stmt.cases

    def _route_from_case_route(
        self,
        stmt: model.RouteFromStmt,
        case: model.RouteFromArm,
    ) -> model.LawRouteStmt:
        explicit_heads = tuple(arm.head for arm in stmt.cases if arm.head is not None)
        choice_heads = explicit_heads if case.head is None else (case.head,)
        return replace(
            case.route,
            choice_enum_ref=stmt.enum_ref,
            choice_case_heads=choice_heads,
            choice_else=case.head is None,
        )

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
        _ = carrier
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
            allowed_kinds=("input", "output", "schema_group"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"invalidate must name one full input or output artifact or schema group in {owner_label}: "
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
            allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["current_artifact"],
        )
        for path in target.paths:
            resolved = self._validate_law_path_root(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label="own only",
                allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
            )
            if (
                resolved.unit.module_parts == current_root.unit.module_parts
                and isinstance(resolved.decl, type(current_root.decl))
                and self._law_path_decl_identity(resolved.decl)
                == self._law_path_decl_identity(current_root.decl)
            ):
                continue
            if isinstance(resolved.decl, model.OutputDecl):
                output_key = (resolved.unit.module_parts, resolved.decl.name)
                if output_key in agent_contract.outputs:
                    continue
            if isinstance(resolved.decl, SchemaFamilyTarget):
                continue
            raise CompileError(
                "own only must stay rooted in the current artifact, an emitted output "
                f"surface, or a declared schema family in {owner_label}: "
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
        if isinstance(
            resolved.decl,
            (model.EnumDecl, SchemaFamilyTarget, ResolvedSchemaGroup, model.GroundingDecl),
        ) and resolved.remainder:
            raise CompileError(
                f"{statement_label} enum, schema-family, schema-group, and grounding targets must not descend through fields in {owner_label}: "
                f"{'.'.join(path.parts)}"
            )
        return resolved
