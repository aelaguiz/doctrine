from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import (
    _REVIEW_VERDICT_TEXT,
    _resolve_render_profile_mode,
)
from doctrine._compiler.naming import (
    _display_addressable_ref,
    _humanize_key,
    _lowercase_initial,
    _name_ref_from_dotted_name,
)
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    CompiledBodyItem,
    IndexedUnit,
    ReadableColumnsTarget,
    ReadableRowsTarget,
    ReadableSchemaTarget,
    ResolvedAnalysisSection,
    ResolvedRenderProfile,
    ResolvedSchemaArtifact,
    ResolvedSchemaGroup,
    ResolvedSectionItem,
    ResolvedSkillEntry,
    ResolvedSkillsSection,
    ResolvedUseItem,
    ResolvedWorkflowSkillsItem,
    ReviewContractSpec,
    ReviewSemanticContext,
    SchemaFamilyTarget,
)


class DisplayMixin:
    """Display and render helper owner for CompilationContext."""

    def _render_decision_required_item(self, item: model.DecisionRequiredItem) -> str:
        decision_required_text = {
            "rank": "You must rank the candidates.",
            "rejects": "You must name clear rejects.",
            "candidate_pool": "You must show the candidate pool.",
            "kept": "You must show the kept candidates.",
            "rejected": "You must show the rejected candidates.",
            "sequencing_proof": "You must show the sequencing proof.",
            "winner_reasons": "You must explain why the winner won.",
        }
        text = decision_required_text.get(item.key)
        if text is None:
            raise CompileError(
                f"Internal compiler error: unsupported decision required item `{item.key}`"
            )
        return text

    def _render_review_subject_summary(
        self,
        subjects: tuple[tuple[IndexedUnit, model.InputDecl | model.OutputDecl], ...],
    ) -> str:
        titles = [decl.title for _unit, decl in subjects]
        if len(titles) == 1:
            return f"Review subject: {titles[0]}."
        return "Review subjects: " + ", ".join(titles[:-1]) + f", and {titles[-1]}."

    def _render_review_pre_outcome_item(
        self,
        item: model.ReviewPreOutcomeStmt,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return [
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label="review prose",
                    review_semantics=review_semantics,
                )
            ]
        if isinstance(item, model.ReviewPreOutcomeWhenStmt):
            lines: list[CompiledBodyItem] = [
                f"If {self._render_condition_expr(item.expr, unit=unit)}:"
            ]
            for child in item.items:
                rendered = self._render_review_pre_outcome_item(
                    child,
                    unit=unit,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(
                    f"- {line}" if isinstance(line, str) else line
                    for line in rendered
                    if isinstance(line, str)
                )
            return lines
        if isinstance(item, model.ReviewPreOutcomeMatchStmt):
            return self._render_review_pre_outcome_match_stmt(
                item,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=section_titles,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
        if isinstance(item, model.ReviewBlockStmt):
            return [
                self._review_gate_sentence(
                    "Block",
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                )
            ]
        if isinstance(item, model.ReviewRejectStmt):
            return [
                self._review_gate_sentence(
                    "Reject",
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                )
            ]
        if isinstance(item, model.ReviewAcceptStmt):
            return [
                self._review_gate_sentence(
                    "Accept only if",
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                )
            ]
        return list(
            self._render_law_stmt_lines(
                item,
                unit=unit,
                owner_label=owner_label,
                bullet=False,
            )
        )

    def _render_review_pre_outcome_match_stmt(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        lines: list[CompiledBodyItem] = [f"Match {self._render_expr(stmt.expr, unit=unit)}:"]
        for case in stmt.cases:
            heading = "Else:" if case.head is None else f"If {self._render_review_match_head(case.head, unit=unit)}:"
            lines.append(heading)
            for item in case.items:
                rendered = self._render_review_pre_outcome_item(
                    item,
                    unit=unit,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(f"- {line}" for line in rendered if isinstance(line, str))
        return lines

    def _render_review_outcome_item(
        self,
        item: model.ReviewOutcomeStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return [
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label="review prose",
                    review_semantics=review_semantics,
                )
            ]
        if isinstance(item, model.ReviewOutcomeWhenStmt):
            lines: list[CompiledBodyItem] = [
                f"If {self._render_condition_expr(item.expr, unit=unit)}:"
            ]
            for child in item.items:
                rendered = self._render_review_outcome_item(
                    child,
                    unit=unit,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(f"- {line}" for line in rendered if isinstance(line, str))
            return lines
        if isinstance(item, model.ReviewOutcomeMatchStmt):
            return self._render_review_outcome_match_stmt(
                item,
                unit=unit,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
        if isinstance(item, model.ReviewCurrentArtifactStmt):
            text = f"Current artifact: {self._display_ref(item.artifact_ref, unit=unit)}."
            if item.when_expr is not None:
                text = (
                    f"When {self._render_condition_expr(item.when_expr, unit=unit)}, "
                    f"{_lowercase_initial(text)}"
                )
            return [text]
        if isinstance(item, model.ReviewCurrentNoneStmt):
            text = "No artifact is current for this outcome."
            if item.when_expr is not None:
                text = (
                    f"When {self._render_condition_expr(item.when_expr, unit=unit)}, "
                    f"{_lowercase_initial(text)}"
                )
            return [text]
        if isinstance(item, model.ReviewCarryStmt):
            return [
                f"Carry {_humanize_key(item.field_name).lower()}: {self._render_expr(item.expr, unit=unit)}."
            ]
        if isinstance(item, model.ReviewOutcomeRouteStmt):
            text = self._interpolate_authored_prose_string(
                item.label,
                unit=unit,
                owner_label=owner_label,
                surface_label="review prose",
                review_semantics=review_semantics,
            )
            text = text if text.endswith(".") else f"{text}."
            return [text]
        return []

    def _render_review_outcome_match_stmt(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> list[CompiledBodyItem]:
        lines: list[CompiledBodyItem] = [f"Match {self._render_expr(stmt.expr, unit=unit)}:"]
        for case in stmt.cases:
            heading = "Else:" if case.head is None else f"If {self._render_review_match_head(case.head, unit=unit)}:"
            lines.append(heading)
            for item in case.items:
                rendered = self._render_review_outcome_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                )
                lines.extend(f"- {line}" for line in rendered if isinstance(line, str))
        return lines

    def _render_review_match_head(
        self,
        head: model.ReviewMatchHead,
        *,
        unit: IndexedUnit,
    ) -> str:
        options = " or ".join(self._render_expr(option, unit=unit) for option in head.options)
        if head.when_expr is None:
            return options
        return f"{options} when {self._render_condition_expr(head.when_expr, unit=unit)}"

    def _render_trust_surface_label(
        self,
        label: str,
        when_expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str:
        if (
            isinstance(when_expr, model.ExprBinary)
            and when_expr.op == "=="
            and self._resolve_constant_enum_member(when_expr.right, unit=unit) == "rewrite"
        ):
            return f"{label} on rewrite passes"

        condition = self._render_condition_expr(when_expr, unit=unit)
        if condition.startswith("peer comparison"):
            return f"{label} when peer comparison is used"
        return f"{label} when {condition}"

    def _render_profile_identity_mode(
        self,
        target: object,
        *,
        render_profile: ResolvedRenderProfile | None,
    ) -> str | None:
        if render_profile is None:
            return None
        if isinstance(target, model.Agent):
            return _resolve_render_profile_mode(render_profile, "identity.owner")
        if isinstance(target, model.EnumMember):
            return _resolve_render_profile_mode(render_profile, "identity.enum_wire")
        if isinstance(
            target,
            (
                model.AnalysisDecl,
                model.SchemaDecl,
                model.DocumentDecl,
                model.WorkflowDecl,
                model.SkillsDecl,
                model.EnumDecl,
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.OutputSchemaDecl,
                model.SkillDecl,
                ResolvedSectionItem,
                ResolvedUseItem,
                ResolvedWorkflowSkillsItem,
                ResolvedSkillsSection,
                ResolvedSkillEntry,
                ResolvedAnalysisSection,
                SchemaFamilyTarget,
                model.SchemaSection,
                model.SchemaGate,
                ResolvedSchemaArtifact,
                ResolvedSchemaGroup,
                model.DocumentBlock,
                model.ReadablePropertyItem,
                model.ReadableDefinitionItem,
                model.ReadableSchemaEntry,
                model.ReadableTableColumn,
                model.ReadableTableRow,
                ReadableColumnsTarget,
                ReadableRowsTarget,
                ReadableSchemaTarget,
            ),
        ):
            return _resolve_render_profile_mode(render_profile, "identity.debug")
        return None

    def _render_match_stmt(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
        match_bindings: dict[tuple[str, ...], str],
    ) -> list[str]:
        fixed_mode = self._render_fixed_match_value(
            stmt.expr,
            unit=unit,
            mode_bindings=mode_bindings,
            match_bindings=match_bindings,
        )

        if fixed_mode is not None:
            for case in stmt.cases:
                if case.head is None or self._render_expr(case.head, unit=unit) == fixed_mode:
                    return self._render_law_stmt_block(
                        case.items,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        bullet=False,
                        mode_bindings=mode_bindings,
                        match_bindings=self._render_match_case_bindings(
                            stmt,
                            case,
                            unit=unit,
                            match_bindings=match_bindings,
                        ),
                    )
            return []

        labels = [
            case.display_label or self._render_expr(case.head, unit=unit)
            for case in stmt.cases
            if case.head is not None
        ]
        lines = ["Use exactly one mode:"]
        lines.extend(f"- {label}" for label in labels)
        for case in stmt.cases:
            if case.head is None:
                heading = "Else:"
            else:
                heading = (
                    f"If the mode is {case.display_label or self._render_expr(case.head, unit=unit)}:"
                )
            lines.extend(["", heading])
            lines.extend(
                self._render_law_stmt_block(
                    case.items,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    bullet=True,
                    mode_bindings=mode_bindings,
                    match_bindings=self._render_match_case_bindings(
                        stmt,
                        case,
                        unit=unit,
                        match_bindings=match_bindings,
                    ),
                )
            )
        return lines

    def _render_route_from_stmt(
        self,
        stmt: model.RouteFromStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
        match_bindings: dict[tuple[str, ...], str],
    ) -> list[str]:
        fixed_choice = self._render_fixed_match_value(
            stmt.expr,
            unit=unit,
            mode_bindings=mode_bindings,
            match_bindings=match_bindings,
        )
        if fixed_choice is None:
            fixed_choice = self._resolve_constant_enum_member(stmt.expr, unit=unit)
        if fixed_choice is not None:
            for case in stmt.cases:
                if (
                    case.head is not None
                    and self._resolve_constant_enum_member(case.head, unit=unit) == fixed_choice
                ):
                    return self._render_law_stmt_lines(
                        case.route,
                        unit=unit,
                        owner_label=owner_label,
                        bullet=False,
                    )
            for case in stmt.cases:
                if case.head is None:
                    return self._render_law_stmt_lines(
                        case.route,
                        unit=unit,
                        owner_label=owner_label,
                        bullet=False,
                    )
            return []

        lines = [
            f"Select one route from {self._render_expr(stmt.expr, unit=unit)}.",
            "Use exactly one route choice:",
        ]
        lines.extend(
            f"- {self._render_expr(case.head, unit=unit)}"
            for case in stmt.cases
            if case.head is not None
        )
        for case in stmt.cases:
            heading = (
                "Else:"
                if case.head is None
                else f"If the route choice is {self._render_expr(case.head, unit=unit)}:"
            )
            lines.extend(["", heading])
            lines.extend(
                self._render_law_stmt_lines(
                    case.route,
                    unit=unit,
                    owner_label=owner_label,
                    bullet=True,
                )
            )
        return lines

    def _render_when_stmt(
        self,
        stmt: model.WhenStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
        match_bindings: dict[tuple[str, ...], str],
    ) -> list[str]:
        lines = [f"If {self._render_condition_expr(stmt.expr, unit=unit)}:"]
        lines.extend(
            self._render_law_stmt_block(
                stmt.items,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                bullet=True,
                mode_bindings=mode_bindings,
                match_bindings=match_bindings,
            )
        )
        return lines

    def _render_law_stmt_block(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        bullet: bool,
        mode_bindings: dict[str, model.ModeStmt] | None = None,
        match_bindings: dict[tuple[str, ...], str] | None = None,
    ) -> list[str]:
        mode_bindings = dict(mode_bindings or {})
        match_bindings = dict(match_bindings or {})
        lines: list[str] = []
        for item in items:
            if isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
            if isinstance(item, model.MatchStmt):
                rendered = self._render_match_stmt(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                    match_bindings=match_bindings,
                )
            elif isinstance(item, model.RouteFromStmt):
                rendered = self._render_route_from_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                    match_bindings=match_bindings,
                )
            elif isinstance(item, model.WhenStmt):
                rendered = self._render_when_stmt(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                    match_bindings=match_bindings,
                )
            else:
                rendered = self._render_law_stmt_lines(
                    item,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    bullet=bullet,
                )
            if (
                lines
                and rendered
                and not (
                    bullet
                    and lines[-1].startswith("- ")
                    and all(line.startswith("- ") for line in rendered)
                )
            ):
                lines.append("")
            lines.extend(rendered)
        return lines

    def _render_fixed_match_value(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        mode_bindings: dict[str, model.ModeStmt],
        match_bindings: dict[tuple[str, ...], str],
    ) -> str | None:
        if not isinstance(expr, model.ExprRef):
            return None
        bound = match_bindings.get(tuple(expr.parts))
        if bound is not None:
            return bound
        if len(expr.parts) != 1:
            return None
        mode_stmt = mode_bindings.get(expr.parts[0])
        if mode_stmt is None:
            return None
        return self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)

    def _render_match_case_bindings(
        self,
        stmt: model.MatchStmt,
        case: model.MatchArm,
        *,
        unit: IndexedUnit,
        match_bindings: dict[tuple[str, ...], str],
    ) -> dict[tuple[str, ...], str]:
        if not isinstance(stmt.expr, model.ExprRef):
            return dict(match_bindings)
        fixed_value = self._resolve_match_case_fixed_value(stmt, case, unit=unit)
        if fixed_value is None:
            return dict(match_bindings)
        updated = dict(match_bindings)
        updated[tuple(stmt.expr.parts)] = fixed_value
        return updated

    def _render_law_stmt_lines(
        self,
        stmt: model.LawStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        owner_label: str,
        bullet: bool,
    ) -> list[str]:
        if isinstance(stmt, model.CurrentArtifactStmt):
            text = f"Current artifact: {self._display_law_path_root(stmt.target, unit=unit, agent_contract=agent_contract)}."
        elif isinstance(stmt, model.CurrentNoneStmt):
            text = "No artifact is current for this turn."
        elif isinstance(stmt, model.MustStmt):
            text = self._render_must_stmt(stmt, unit=unit)
        elif isinstance(stmt, model.OwnOnlyStmt):
            text = f"Own only {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.PreserveStmt):
            text = f"Preserve {stmt.kind} {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.SupportOnlyStmt):
            text = (
                f"{self._render_path_set_subject(stmt.target, unit=unit, agent_contract=agent_contract)} is support only for comparison."
            )
        elif isinstance(stmt, model.IgnoreStmt):
            text = self._render_ignore_stmt(stmt, unit=unit, agent_contract=agent_contract)
        elif isinstance(stmt, model.ForbidStmt):
            text = f"Do not modify {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.InvalidateStmt):
            rendered = [
                f"{label} is no longer current."
                for label in self._render_invalidation_targets(
                    stmt.target,
                    unit=unit,
                    agent_contract=agent_contract,
                )
            ]
            if bullet:
                return [f"- {line}" for line in rendered]
            return rendered
        elif isinstance(stmt, model.StopStmt):
            message = stmt.message or ""
            if message and not message.endswith("."):
                message += "."
            text = "Stop." if stmt.message is None else f"Stop: {message}"
            if stmt.when_expr is not None:
                text = f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, {_lowercase_initial(text)}"
        elif isinstance(stmt, model.LawRouteStmt):
            label = self._interpolate_authored_prose_string(
                stmt.label,
                unit=unit,
                owner_label=owner_label,
                surface_label="route labels",
            )
            text = label if label.endswith(".") else f"{label}."
            if stmt.when_expr is not None:
                text = (
                    f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, "
                    f"{_lowercase_initial(text)}"
                )
        elif isinstance(stmt, model.ActiveWhenStmt):
            text = f"Run this pass only when {self._render_condition_expr(stmt.expr, unit=unit)}."
        elif isinstance(stmt, model.ModeStmt):
            fixed_mode = self._resolve_constant_enum_member(stmt.expr, unit=unit)
            return [] if fixed_mode is None else [f"Active mode: {fixed_mode}."]
        else:
            return []

        if bullet:
            return [f"- {text}"]
        return [text]

    def _render_must_stmt(self, stmt: model.MustStmt, *, unit: IndexedUnit) -> str:
        if (
            isinstance(stmt.expr, model.ExprBinary)
            and stmt.expr.op == "=="
            and isinstance(stmt.expr.left, model.ExprRef)
        ):
            return f"Make sure {self._render_expr(stmt.expr.left, unit=unit)} == {self._render_expr(stmt.expr.right, unit=unit)}."
        return f"Make sure {self._render_expr(stmt.expr, unit=unit)}."

    def _render_ignore_stmt(
        self,
        stmt: model.IgnoreStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> str:
        target = self._render_path_set(stmt.target)
        if stmt.bases == ("rewrite_evidence",):
            prefix = "Ignore"
            if stmt.when_expr is not None:
                prefix = f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, ignore"
            return f"{prefix} {target} for rewrite evidence."
        if stmt.bases == ("truth",) or not stmt.bases:
            return f"Do not treat {self._render_path_set_subject(stmt.target, unit=unit, agent_contract=agent_contract)} as truth for this pass."
        return f"Ignore {target} for {', '.join(stmt.bases)}."

    def _render_path_set_subject(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> str:
        target = self._coerce_path_set(target)
        if len(target.paths) == 1 and not target.except_paths:
            path = target.paths[0]
            if not path.wildcard:
                return self._display_law_path_root(path, unit=unit, agent_contract=agent_contract)
        return self._render_path_set(target)

    def _render_path_set(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> str:
        target = self._coerce_path_set(target)
        parts = [self._render_law_path(path) for path in target.paths]
        rendered = ", ".join(parts)
        if len(parts) > 1:
            rendered = "{" + rendered + "}"
        if target.except_paths:
            rendered += " except " + ", ".join(
                self._render_law_path(path) for path in target.except_paths
            )
        return rendered

    def _render_analysis_basis(
        self,
        basis: model.LawPathSet,
        *,
        unit: IndexedUnit,
    ) -> str:
        if len(basis.paths) == 1 and not basis.except_paths and not basis.paths[0].wildcard:
            return self._display_law_path_root(basis.paths[0], unit=unit)
        if not basis.except_paths and all(not path.wildcard for path in basis.paths):
            return self._natural_language_join(
                [self._display_law_path_root(path, unit=unit) for path in basis.paths]
            )
        return self._render_path_set(basis)

    def _render_analysis_using_expr(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str:
        if isinstance(expr, model.ExprSet):
            return self._natural_language_join(
                [self._render_expr(item, unit=unit) for item in expr.items]
            )
        return self._render_expr(expr, unit=unit)

    def _natural_language_join(self, items: list[str] | tuple[str, ...]) -> str:
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f", and {items[-1]}"

    def _render_law_path(self, path: model.LawPath) -> str:
        text = ".".join(path.parts)
        if path.wildcard:
            text += ".*"
        return f"`{text}`"

    def _render_condition_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_condition_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            if expr.op in {"==", "!="} and isinstance(expr.right, bool):
                expected = expr.right if expr.op == "==" else not expr.right
                return self._render_boolean_condition_expr(expr.left, expected=expected, unit=unit)
            if expr.op in {"==", "!="} and isinstance(expr.left, bool):
                expected = expr.left if expr.op == "==" else not expr.left
                return self._render_boolean_condition_expr(expr.right, expected=expected, unit=unit)
            if expr.op == "in" and isinstance(expr.right, model.ExprSet):
                subject = self._render_condition_subject(expr.left, unit=unit)
                choices = [self._render_condition_choice(item, unit=unit) for item in expr.right.items]
                if not choices:
                    return f"{subject} is in {{}}"
                if len(choices) == 1:
                    return f"{subject} is {choices[0]}"
                if len(choices) == 2:
                    return f"{subject} is {choices[0]} or {choices[1]}"
                return f"{subject} is {', '.join(choices[:-1])}, or {choices[-1]}"
            left = self._render_condition_expr(expr.left, unit=unit)
            right = self._render_condition_expr(expr.right, unit=unit)
            joiner = expr.op
            if expr.op == "==":
                return f"{left} is {right}"
            if expr.op == "!=":
                return f"{left} is not {right}"
            return f"{left} {joiner} {right}"
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{_humanize_key(expr.name).lower()}({args})"
        return self._render_expr(expr, unit=unit)

    def _render_boolean_condition_expr(
        self,
        expr: model.Expr,
        *,
        expected: bool,
        unit: IndexedUnit,
    ) -> str:
        rendered = self._render_condition_expr(expr, unit=unit)
        if expected:
            return rendered
        return self._negate_condition_text(rendered)

    def _negate_condition_text(self, text: str) -> str:
        if " is not " in text:
            head, tail = text.rsplit(" is not ", 1)
            return f"{head} is {tail}"
        if " is " in text:
            head, tail = text.rsplit(" is ", 1)
            return f"{head} is not {tail}"
        if text.startswith("not "):
            return text.removeprefix("not ")
        return f"not ({text})"

    def _render_condition_choice(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, str):
            return expr.replace("_", " ")
        return self._render_expr(expr, unit=unit)

    def _render_condition_subject(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            parts = expr.parts
            if len(parts) == 1:
                return _humanize_key(parts[0]).lower()
            return f"{self._render_ref_root(parts[:-1], unit=unit)} {_humanize_key(parts[-1]).lower()}"
        return self._render_condition_expr(expr, unit=unit)

    def _render_condition_ref(self, ref: model.ExprRef, *, unit: IndexedUnit) -> str:
        parts = ref.parts
        if not parts:
            return ""
        if parts == ("route", "exists"):
            return "a routed owner exists"
        key = parts[-1]
        if key == "missing":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is missing"
        if key == "unclear":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is unclear"
        if key.endswith("_missing"):
            return f"{_humanize_key(key.removesuffix('_missing')).lower()} is missing"
        if key.endswith("_unknown"):
            return f"{_humanize_key(key.removesuffix('_unknown')).lower()} is unknown"
        if key.endswith("_repeated"):
            return f"{_humanize_key(key.removesuffix('_repeated')).lower()} is repeated"
        if key.startswith("owes_"):
            return f"{_humanize_key(key.removeprefix('owes_')).lower()} is owed now"
        if key.endswith("_changed"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_invalidated"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_requested"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_used"):
            return f"{_humanize_key(key).lower()}"
        return self._render_expr(ref, unit=unit)

    def _render_ref_root(self, parts: tuple[str, ...], *, unit: IndexedUnit) -> str:
        if not parts:
            return "this turn"
        try:
            root_path = model.LawPath(parts=parts)
            return self._display_law_path_root(root_path, unit=unit).lower()
        except CompileError:
            return _humanize_key(parts[-1]).lower()

    def _render_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_expr_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            return (
                f"{self._render_expr(expr.left, unit=unit)} {expr.op} "
                f"{self._render_expr(expr.right, unit=unit)}"
            )
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{expr.name}({args})"
        if isinstance(expr, model.ExprSet):
            rendered = ", ".join(self._render_expr(item, unit=unit) for item in expr.items)
            return "{" + rendered + "}"
        if isinstance(expr, str):
            return expr
        if isinstance(expr, bool):
            return "true" if expr else "false"
        return str(expr)

    def _render_expr_ref(self, expr: model.ExprRef, *, unit: IndexedUnit) -> str:
        constant = self._resolve_constant_enum_member(expr, unit=unit)
        if constant is not None:
            return constant
        return ".".join(expr.parts)

    def _display_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> str:
        try:
            resolved = self._resolve_law_path(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label="workflow law",
                statement_label="law path",
                allowed_kinds=("input", "output", "enum", "schema_group"),
            )
        except CompileError:
            return ".".join(path.parts)
        if isinstance(resolved.decl, ResolvedSchemaGroup):
            title = resolved.decl.title
        else:
            title = self._display_readable_decl(resolved.decl)
        if not resolved.remainder:
            return title
        return f"{title}.{'.'.join(resolved.remainder)}"

    def _render_invalidation_targets(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> tuple[str, ...]:
        try:
            resolved = self._resolve_law_path(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label="workflow law",
                statement_label="invalidate",
                allowed_kinds=("input", "output", "schema_group"),
            )
        except CompileError:
            return (".".join(path.parts),)
        if isinstance(resolved.decl, ResolvedSchemaGroup):
            members = self._schema_group_member_artifacts(resolved.decl, unit=resolved.unit)
            if not members:
                return (resolved.decl.title,)
            return tuple(member.title for member in members)
        return (self._display_law_path_root(path, unit=unit, agent_contract=agent_contract),)
