from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.naming import _dotted_ref_name, _name_ref_from_dotted_name
from doctrine._compiler.workflow_diagnostics import (
    workflow_compile_error,
    workflow_related_site,
)
from doctrine._compiler.resolved_types import (
    AddressableNode,
    AgentContract,
    CompileError,
    IndexedUnit,
    LawBranch,
    ResolvedLawPath,
    ResolvedSchemaGroup,
    RouteSemanticBranch,
    RouteSemanticContext,
    SchemaFamilyTarget,
)

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
            raise compile_error(
                code="E282",
                summary="Route target must be a concrete agent",
                detail=f"Route target `{dotted_name}` is not a concrete agent.",
                path=unit.prompt_file.source_path,
                source_span=ref.source_span,
            )

    def _flatten_law_items(
        self,
        law_body: model.LawBody,
        *,
        owner_label: str,
        unit: IndexedUnit,
    ) -> tuple[model.LawStmt, ...]:
        has_sections = any(isinstance(item, model.LawSection) for item in law_body.items)
        if has_sections:
            if not all(isinstance(item, model.LawSection) for item in law_body.items):
                first_section = next(
                    (item for item in law_body.items if isinstance(item, model.LawSection)),
                    None,
                )
                first_bare_stmt = next(
                    (item for item in law_body.items if not isinstance(item, model.LawSection)),
                    None,
                )
                raise workflow_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        "Law blocks may not mix named sections with bare law statements "
                        f"in {owner_label}"
                    ),
                    unit=unit,
                    source_span=(
                        getattr(first_bare_stmt, "source_span", None) or law_body.source_span
                    ),
                    related=(
                        workflow_related_site(
                            label="first named law section",
                            unit=unit,
                            source_span=(
                                first_section.source_span if first_section is not None else None
                            ),
                        ),
                    )
                    if first_section is not None
                    else (),
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
                    first_current = branch.current_subjects[0]
                    second_current = branch.current_subjects[1]
                    raise workflow_compile_error(
                        code="E332",
                        summary="Multiple current-subject forms",
                        detail=(
                            "One active workflow-law leaf branch declares multiple "
                            f"current-subject forms ({current_labels}) in {owner_label}."
                        ),
                        unit=unit,
                        source_span=second_current.source_span,
                        related=(
                            workflow_related_site(
                                label="first current-subject form",
                                unit=unit,
                                source_span=first_current.source_span,
                            ),
                        ),
                    )
                raise workflow_compile_error(
                    code="E331",
                    summary="Missing current-subject form",
                    detail=(
                        "Each active workflow-law leaf branch must declare exactly one "
                        f"current subject in {owner_label}."
                    ),
                    unit=unit,
                    source_span=self._workflow_branch_anchor_source_span(branch),
                    hints=(
                        "Add either `current artifact ... via ...` or `current none` in each active branch.",
                    ),
                )
            current = branch.current_subjects[0]
            if isinstance(current, model.CurrentNoneStmt) and branch.owns:
                first_own = branch.owns[0]
                raise workflow_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"`current none` cannot appear with owned scope in {owner_label}",
                    unit=unit,
                    source_span=first_own.source_span,
                    related=(
                        workflow_related_site(
                            label="`current none` statement",
                            unit=unit,
                            source_span=current.source_span,
                        ),
                    ),
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
                        raise workflow_compile_error(
                            code="E371",
                            summary="Current artifact invalidated in same branch",
                            detail=(
                                "The current artifact is invalidated in the same active "
                                f"branch in {owner_label}."
                            ),
                            unit=unit,
                            source_span=invalidate.source_span,
                            related=(
                                workflow_related_site(
                                    label="current artifact statement",
                                    unit=unit,
                                    source_span=current.source_span,
                                ),
                            ),
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
                        raise workflow_compile_error(
                            code="E362",
                            summary="Comparison-only basis contradiction",
                            detail=(
                                "`support_only` and `ignore ... for comparison` contradict "
                                f"in {owner_label}."
                            ),
                            unit=unit,
                            source_span=ignore.source_span,
                            related=(
                                workflow_related_site(
                                    label="overlapping `support_only` statement",
                                    unit=unit,
                                    source_span=support.source_span,
                                ),
                            ),
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
                        raise workflow_compile_error(
                            code="E361",
                            summary="Current artifact ignored for truth",
                            detail=(
                                "The current artifact is being ignored for truth in "
                                f"{owner_label}."
                            ),
                            unit=unit,
                            source_span=ignore.source_span,
                            related=(
                                workflow_related_site(
                                    label="current artifact statement",
                                    unit=unit,
                                    source_span=current.source_span,
                                ),
                            ),
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
                        raise workflow_compile_error(
                            code="E354",
                            summary="Owned scope overlaps forbidden scope",
                            detail=(
                                f"Owned scope overlaps forbidden scope in {owner_label}."
                            ),
                            unit=unit,
                            source_span=forbid.source_span,
                            related=(
                                workflow_related_site(
                                    label="overlapping `own only` statement",
                                    unit=unit,
                                    source_span=own.source_span,
                                ),
                            ),
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
                        raise workflow_compile_error(
                            code="E353",
                            summary="Owned scope overlaps exact preservation",
                            detail=(
                                "Owned scope overlaps exact-preserved scope in "
                                f"{owner_label}."
                            ),
                            unit=unit,
                            source_span=preserve.source_span,
                            related=(
                                workflow_related_site(
                                    label="overlapping `own only` statement",
                                    unit=unit,
                                    source_span=own.source_span,
                                ),
                            ),
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
            if isinstance(item, model.ActiveWhenStmt):
                self._validate_active_when_expr(
                    item.expr,
                    unit=unit,
                    owner_label=owner_label,
                )
                continue
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
            if isinstance(item, model.StopStmt):
                continue
            raise workflow_compile_error(
                code="E344",
                summary="handoff_routing law uses a non-routing statement",
                detail=(
                    f"`handoff_routing` law in {owner_label} uses unsupported statement "
                    f"`{self._law_stmt_name(item)}`."
                ),
                unit=unit,
                source_span=getattr(item, "source_span", None),
                hints=(
                    "Use only `active when`, `mode`, `when`, `match`, `route_from`, `stop`, and `route` in `handoff_routing` law.",
                    "Keep currentness, preservation, invalidation, and other workflow-law truth controls on `workflow:`.",
                ),
            )

    def _validate_active_when_expr(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if isinstance(expr, model.ExprRef):
            if (
                self._expr_ref_matches_input_decl(expr, unit=unit)
                or self._expr_ref_matches_input_binding(expr)
                or self._expr_ref_matches_output_decl(expr, unit=unit)
                or self._expr_ref_matches_enum_member(expr, unit=unit)
                or self._expr_ref_matches_review_verdict(expr)
            ):
                return
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"active when reads invalid input source in {owner_label}: "
                    f"{'.'.join(expr.parts)}"
                ),
                unit=unit,
                source_span=expr.source_span,
                hints=(
                    "Read only declared inputs, input bindings, emitted outputs, enum members, or review verdicts in `active when`.",
                ),
            )
        if isinstance(expr, model.ExprBinary):
            self._validate_active_when_expr(
                expr.left,
                unit=unit,
                owner_label=owner_label,
            )
            self._validate_active_when_expr(
                expr.right,
                unit=unit,
                owner_label=owner_label,
            )
            return
        if isinstance(expr, model.ExprCall):
            for arg in expr.args:
                self._validate_active_when_expr(
                    arg,
                    unit=unit,
                    owner_label=owner_label,
                )
            return
        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._validate_active_when_expr(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                )
            return

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
                        route_unit=unit,
                        route_source_span=route.source_span,
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
        route_unit: IndexedUnit | None = None,
        route_source_span: model.SourceSpan | None = None,
        error_code: str = "E339",
        error_summary: str = "Routed next_owner field is not structurally bound",
        error_hints: tuple[str, ...] = (
            "Use an explicit interpolation such as `{{RoutingOwner}}` or `{{RoutingOwner:name}}` inside the `next_owner` field for routed branches.",
            "If ownership stays local, keep the field generic and do not emit a semantic route.",
        ),
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
        raise compile_error(
            code=error_code,
            summary=error_summary,
            detail=error_message,
            path=unit.prompt_file.source_path,
            source_span=getattr(item, "source_span", None),
            related=(
                workflow_related_site(
                    label="routed branch",
                    unit=route_unit,
                    source_span=route_source_span,
                ),
            )
            if route_unit is not None and route_source_span is not None
            else (),
            hints=error_hints,
        )

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
        ref = self._rebind_self_addressable_ref(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label="next_owner",
        )
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
            if isinstance(item, model.ActiveWhenStmt):
                self._validate_active_when_expr(
                    item.expr,
                    unit=unit,
                    owner_label=owner_label,
                )
                continue
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
                continue

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
            raise workflow_compile_error(
                code="E341",
                summary="Mode value outside enum",
                detail=(
                    f"Mode value `{fixed_mode}` is outside enum `{enum_decl.name}` "
                    f"in {owner_label}."
                ),
                unit=unit,
                source_span=getattr(stmt.expr, "source_span", None) or stmt.source_span,
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
                raise workflow_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        f"Match arm is outside enum {enum_decl.name} in {owner_label}: "
                        f"{member_value}"
                    ),
                    unit=unit,
                    source_span=case.head.source_span,
                    hints=(
                        f"Name one member of `{enum_decl.name}`, or add `else` for the remaining cases.",
                    ),
                )
            seen_members.add(member_value)

        expected_members = {member.value for member in enum_decl.members}
        if seen_members != expected_members:
            raise workflow_compile_error(
                code="E342",
                summary="Non-exhaustive mode match",
                detail=(
                    f"`match` on `{enum_decl.name}` must cover every enum member or include "
                    f"`else` in {owner_label}."
                ),
                unit=unit,
                source_span=stmt.source_span,
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
        cases_by_value: dict[str, model.RouteFromArm] = {}
        else_case: model.RouteFromArm | None = None
        for case in stmt.cases:
            if case.head is None:
                if saw_else:
                    raise compile_error(
                        code="E348",
                        summary="Duplicate route_from arm",
                        detail=f"`route_from` in {owner_label} names `else` more than once.",
                        path=unit.prompt_file.source_path,
                        source_span=case.source_span,
                        related=(
                            related_prompt_site(
                                label="first `else` arm",
                                path=unit.prompt_file.source_path,
                                source_span=else_case.source_span if else_case is not None else None,
                            ),
                        ),
                        hints=(
                            "Name each enum member at most once in `route_from`.",
                            "Use `else` at most once, and only when you need the remaining members.",
                        ),
                    )
                saw_else = True
                else_case = case
                continue
            member = self._resolve_route_from_member(
                case.head,
                enum_decl=enum_decl,
                enum_unit=enum_unit,
                unit=unit,
                owner_label=owner_label,
                fallback_source_span=case.source_span,
            )
            if member.value in seen_members:
                raise compile_error(
                    code="E348",
                    summary="Duplicate route_from arm",
                    detail=f"`route_from` in {owner_label} names `{member.value}` more than once.",
                    path=unit.prompt_file.source_path,
                    source_span=case.source_span,
                    related=(
                        related_prompt_site(
                            label=f"first `{member.value}` arm",
                            path=unit.prompt_file.source_path,
                            source_span=cases_by_value[member.value].source_span,
                        ),
                    ),
                    hints=(
                        "Name each enum member at most once in `route_from`.",
                        "Use `else` at most once, and only when you need the remaining members.",
                    ),
                )
            seen_members.add(member.value)
            cases_by_value[member.value] = case

        self._validate_route_from_selector_expr(
            stmt.expr,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            fallback_source_span=stmt.source_span,
        )
        fixed_choice = self._resolve_constant_enum_member(stmt.expr, unit=unit)
        if fixed_choice is not None and not any(
            member.value == fixed_choice for member in enum_decl.members
        ):
            raise compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"route_from selector is outside enum {enum_decl.name} in "
                    f"{owner_label}: {fixed_choice}"
                ),
                path=unit.prompt_file.source_path,
                source_span=stmt.expr.source_span,
                hints=(
                    f"Make the selector resolve to one member of `{enum_decl.name}`.",
                ),
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
                    unit=unit,
                    owner_label=owner_label,
                    fallback_source_span=case.source_span,
                )
                explicit_values.add(member.value)
            if explicit_values == {member.value for member in enum_decl.members}:
                raise compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"route_from else is unreachable in {owner_label}: {enum_decl.name}",
                    path=unit.prompt_file.source_path,
                    source_span=else_case.source_span if else_case is not None else stmt.source_span,
                    hints=(
                        "Remove `else`, or stop naming every enum member explicitly.",
                    ),
                )
        else:
            seen_members = set()
            for case in stmt.cases:
                member = self._resolve_route_from_member(
                    case.head,
                    enum_decl=enum_decl,
                    enum_unit=enum_unit,
                    unit=unit,
                    owner_label=owner_label,
                    fallback_source_span=case.source_span,
                )
                seen_members.add(member.value)
            expected_members = {member.value for member in enum_decl.members}
            if seen_members != expected_members:
                raise compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        f"route_from on {enum_decl.name} must be exhaustive or include "
                        f"else in {owner_label}"
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=stmt.source_span,
                    hints=(
                        f"Name every member of `{enum_decl.name}`, or add one `else` arm.",
                    ),
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
        fallback_source_span: model.SourceSpan | None = None,
    ) -> None:
        if not isinstance(expr, model.ExprRef):
            source_span = getattr(expr, "source_span", None) or fallback_source_span
            raise workflow_compile_error(
                code="E346",
                summary="route_from selector reads invalid source",
                detail=(
                    f"`route_from` selector in {owner_label} reads invalid source "
                    f"`{self._render_expr(expr, unit=unit)}`."
                ),
                unit=unit,
                source_span=source_span,
                hints=(
                    "Read only declared inputs, emitted outputs, or enum members in a `route_from` selector.",
                    "Do not read workflow-local bindings or other compiler-local names there.",
                ),
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
        raise workflow_compile_error(
            code="E346",
            summary="route_from selector reads invalid source",
            detail=(
                f"`route_from` selector in {owner_label} reads invalid source "
                f"`{'.'.join(ref.parts)}`."
            ),
            unit=unit,
            source_span=ref.source_span,
            hints=(
                "Read only declared inputs, emitted outputs, or enum members in a `route_from` selector.",
                "Do not read workflow-local bindings or other compiler-local names there.",
            ),
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
        unit: IndexedUnit,
        owner_label: str,
        fallback_source_span: model.SourceSpan | None = None,
    ) -> model.EnumMember:
        if expr is None:
            raise compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"route_from arm must name an enum member in {owner_label}",
                path=unit.prompt_file.source_path,
                source_span=fallback_source_span,
            )
        member_value = self._resolve_constant_enum_member(expr, unit=enum_unit)
        if member_value is None:
            raise compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"route_from arm must name a member of {enum_decl.name} in {owner_label}",
                path=unit.prompt_file.source_path,
                source_span=expr.source_span,
                hints=(
                    f"Name one member of `{enum_decl.name}`, or use `else` for the remaining members.",
                ),
            )
        member = next((item for item in enum_decl.members if item.value == member_value), None)
        if member is None:
            raise compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"route_from arm is outside enum {enum_decl.name} in {owner_label}: "
                    f"{member_value}"
                ),
                path=unit.prompt_file.source_path,
                source_span=expr.source_span,
                hints=(
                    f"Name one member of `{enum_decl.name}`, or use `else` for the remaining members.",
                ),
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
                                branch=self._branch_with_match_case(
                                    current_branch,
                                    item,
                                    case,
                                    unit=unit,
                                ),
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
                        branch=current_branch,
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
        branch: LawBranch,
    ) -> tuple[model.RouteFromArm, ...]:
        fixed_value = self._resolve_fixed_match_value(stmt.expr, unit=unit, branch=branch)
        if fixed_value is None:
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

    def _branch_with_match_case(
        self,
        branch: LawBranch,
        stmt: model.MatchStmt,
        case: model.MatchArm,
        *,
        unit: IndexedUnit,
    ) -> LawBranch:
        if not isinstance(stmt.expr, model.ExprRef):
            return branch
        fixed_value = self._resolve_match_case_fixed_value(stmt, case, unit=unit)
        if fixed_value is None:
            return branch
        return replace(
            branch,
            match_bindings=(*branch.match_bindings, (tuple(stmt.expr.parts), fixed_value)),
        )

    def _validate_current_artifact_stmt(
        self,
        stmt: model.CurrentArtifactStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        carrier_output_not_emitted_code: str | None = None,
        carrier_output_not_emitted_summary: str | None = None,
        carrier_output_not_emitted_detail: str | None = None,
        carrier_field_not_trusted_code: str | None = None,
        carrier_field_not_trusted_summary: str | None = None,
        carrier_field_not_trusted_detail: str | None = None,
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
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    "current artifact must stay rooted at one input or output artifact "
                    f"in {owner_label}: {'.'.join(stmt.target.parts)}"
                ),
                unit=unit,
                source_span=stmt.source_span,
            )

        carrier = self._validate_carrier_path(
            stmt.carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
            output_not_emitted_code=carrier_output_not_emitted_code,
            output_not_emitted_summary=carrier_output_not_emitted_summary,
            output_not_emitted_detail=carrier_output_not_emitted_detail,
            field_not_trusted_code=carrier_field_not_trusted_code,
            field_not_trusted_summary=carrier_field_not_trusted_summary,
            field_not_trusted_detail=carrier_field_not_trusted_detail,
        )
        _ = carrier
        if isinstance(target.decl, model.OutputDecl):
            target_key = (target.unit.module_parts, target.decl.name)
            if target_key not in agent_contract.outputs:
                raise workflow_compile_error(
                    code="E334",
                    summary="Current output not emitted",
                    detail=(
                        f"Current-artifact output `{target.decl.name}` is not emitted by "
                        f"{owner_label}."
                    ),
                    unit=unit,
                    source_span=stmt.source_span,
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
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    "invalidate must name one full input or output artifact or schema "
                    f"group in {owner_label}: {'.'.join(stmt.target.parts)}"
                ),
                unit=unit,
                source_span=stmt.source_span or stmt.target.source_span,
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
        output_not_emitted_code: str | None = None,
        output_not_emitted_summary: str | None = None,
        output_not_emitted_detail: str | None = None,
        field_not_trusted_code: str | None = None,
        field_not_trusted_summary: str | None = None,
        field_not_trusted_detail: str | None = None,
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
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"{statement_label} via carrier must stay rooted in an emitted output "
                    f"in {owner_label}"
                ),
                unit=unit,
                source_span=carrier.source_span,
            )
        if not resolved.remainder or resolved.wildcard:
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"{statement_label} requires an explicit `via` field on an emitted "
                    f"output in {owner_label}"
                ),
                unit=unit,
                source_span=carrier.source_span,
            )

        output_key = (resolved.unit.module_parts, resolved.decl.name)
        if output_key not in agent_contract.outputs:
            default_output_summary = (
                "Current carrier output not emitted"
                if statement_label == "current artifact"
                else "Compile failure"
            )
            default_output_detail = (
                f"Current-artifact carrier output `{resolved.decl.name}` is not emitted "
                f"by {owner_label}."
                if statement_label == "current artifact"
                else f"{statement_label} carrier output must be emitted by the concrete "
                f"turn in {owner_label}: {resolved.decl.name}"
            )
            raise workflow_compile_error(
                code=output_not_emitted_code or "E333" if statement_label == "current artifact" else output_not_emitted_code or "E299",
                summary=output_not_emitted_summary or default_output_summary,
                detail=(
                    output_not_emitted_detail.format(
                        output=resolved.decl.name,
                        owner=owner_label,
                        field=".".join(resolved.remainder),
                        statement_label=statement_label,
                    )
                    if output_not_emitted_detail is not None
                    else default_output_detail
                ),
                unit=unit,
                source_span=carrier.source_span,
            )

        self._resolve_output_field_node(
            resolved.decl,
            path=resolved.remainder,
            unit=resolved.unit,
            owner_label=owner_label,
            surface_label=f"{statement_label} via",
            source_span=carrier.source_span,
        )
        if not any(item.path == resolved.remainder for item in resolved.decl.trust_surface):
            default_field_summary = (
                "Current carrier field missing from trust surface"
                if statement_label == "current artifact"
                else "Invalidation carrier field missing from trust surface"
                if statement_label == "invalidate"
                else "Compile failure"
            )
            default_field_detail = (
                f"Current-artifact carrier field `{'.'.join(resolved.remainder)}` is "
                f"not listed in `trust_surface` in {owner_label}."
                if statement_label == "current artifact"
                else f"Invalidation carrier field `{'.'.join(resolved.remainder)}` is "
                f"not listed in `trust_surface` in {owner_label}."
                if statement_label == "invalidate"
                else f"{statement_label} carrier field must be listed in trust_surface "
                f"in {owner_label}: {'.'.join(resolved.remainder)}"
            )
            raise workflow_compile_error(
                code=(
                    field_not_trusted_code
                    or "E336"
                    if statement_label == "current artifact"
                    else field_not_trusted_code
                    or "E372"
                    if statement_label == "invalidate"
                    else field_not_trusted_code
                    or "E299"
                ),
                summary=field_not_trusted_summary or default_field_summary,
                detail=(
                    field_not_trusted_detail.format(
                        output=resolved.decl.name,
                        owner=owner_label,
                        field=".".join(resolved.remainder),
                        statement_label=statement_label,
                    )
                    if field_not_trusted_detail is not None
                    else default_field_detail
                ),
                unit=unit,
                source_span=carrier.source_span,
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
            raise workflow_compile_error(
                code="E351",
                summary="Owned scope is outside the allowed modeled surface",
                detail=(
                    f"Owned scope `{'.'.join(path.parts)}` is not rooted in the current "
                    f"artifact, an emitted output surface, or a declared schema family in "
                    f"{owner_label}."
                ),
                unit=unit,
                source_span=path.source_span or stmt.source_span,
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
            raise compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"{statement_label} enum, schema-family, schema-group, and grounding "
                    f"targets must not descend through fields in {owner_label}: "
                    f"{'.'.join(path.parts)}"
                ),
                path=unit.prompt_file.source_path,
                source_span=path.source_span,
                hints=(
                    "Point the statement at the enum, schema family, schema group, or grounding root directly.",
                ),
            )
        return resolved

    def _workflow_branch_anchor_source_span(
        self,
        branch: LawBranch,
    ) -> model.SourceSpan | None:
        candidates = (
            [expr.source_span for expr in branch.activation_exprs]
            + [stmt.source_span for stmt in branch.mode_bindings]
            + [stmt.source_span for stmt in branch.musts]
            + [stmt.source_span for stmt in branch.owns]
            + [stmt.source_span for stmt in branch.preserves]
            + [stmt.source_span for stmt in branch.supports]
            + [stmt.source_span for stmt in branch.ignores]
            + [stmt.source_span for stmt in branch.forbids]
            + [stmt.source_span for stmt in branch.invalidations]
            + [stmt.source_span for stmt in branch.stops]
            + [stmt.source_span for stmt in branch.routes]
        )
        anchored = [span for span in candidates if span is not None]
        if not anchored:
            return None
        return max(anchored, key=lambda span: (span.line, span.column))
