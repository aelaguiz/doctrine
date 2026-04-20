from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import _REVIEW_CONTRACT_FACT_KEYS
from doctrine._compiler.naming import _dotted_ref_name, _humanize_key
from doctrine._compiler.review_diagnostics import review_compile_error, review_related_site
from doctrine._compiler.resolved_types import (
    AddressableNode,
    CompileError,
    IndexedUnit,
    ResolvedReviewAgreementBranch,
    ResolvedSchemaBody,
    ResolvedSectionItem,
    ResolvedWorkflowBody,
    ResolvedWorkflowSkillsItem,
    ReviewContractGate,
    ReviewContractSpec,
    ReviewSemanticContext,
    ReviewSemanticContractRoot,
    ReviewSemanticFieldsRoot,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ValidateReviewSemanticsMixin:
    """Review semantic lookup and output-guard helpers for ValidateMixin."""

    def _review_semantic_field_path(
        self,
        review_semantics: ReviewSemanticContext,
        field_name: str,
    ) -> tuple[str, ...] | None:
        for name, path in review_semantics.field_bindings:
            if name == field_name:
                return path
        return None

    def _review_semantic_contract_gate(
        self,
        review_semantics: ReviewSemanticContext,
        gate_key: str,
    ) -> ReviewContractGate | None:
        for gate in review_semantics.contract_gates:
            if gate.key == gate_key:
                return gate
        return None

    def _review_semantic_addressable_parts(
        self,
        ref: model.AddressableRef,
    ) -> tuple[str, ...] | None:
        if ref.self_rooted or ref.root is None:
            return None
        parts = (*ref.root.module_parts, ref.root.declaration_name, *ref.path)
        if len(parts) < 2 or parts[0] not in {"contract", "fields"}:
            return None
        return parts

    def _review_semantic_root_node(
        self,
        root_key: str,
        review_semantics: ReviewSemanticContext,
    ) -> AddressableNode | None:
        if root_key == "fields":
            root = ReviewSemanticFieldsRoot(review_semantics)
        elif root_key == "contract":
            root = ReviewSemanticContractRoot(review_semantics)
        else:
            return None
        output_unit, _output_decl = self._resolve_review_semantic_output_decl(review_semantics)
        return AddressableNode(
            unit=output_unit,
            root_decl=root,
            target=root,
        )

    def _output_path_has_guarded_detail(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
    ) -> bool:
        return bool(self._output_path_guards(output_decl.items, path=path))

    def _review_section_title(
        self,
        section: model.ReviewSection,
    ) -> str:
        return section.title or _humanize_key(section.key)

    def _resolved_review_subject_map(
        self,
        subject_map: model.ReviewSubjectMapConfig,
        *,
        unit: IndexedUnit,
        owner_label: str,
        subject_keys: set[tuple[tuple[str, ...], str]],
    ) -> dict[tuple[tuple[str, ...], str, str], tuple[tuple[str, ...], str]]:
        mapping: dict[tuple[tuple[str, ...], str, str], tuple[tuple[str, ...], str]] = {}
        seen_entries: dict[tuple[tuple[str, ...], str, str], model.ReviewSubjectMapEntry] = {}
        for entry in subject_map.entries:
            entry_identity = self._resolve_enum_member_identity(
                model.ExprRef(
                    parts=(*entry.enum_member_ref.module_parts, entry.enum_member_ref.declaration_name)
                ),
                unit=unit,
            )
            if entry_identity is None:
                raise review_compile_error(
                    code="E470",
                    summary="Invalid review declaration shape",
                    detail=(
                        "Review subject_map entry must resolve to an enum member in "
                        f"{owner_label}: {_dotted_ref_name(entry.enum_member_ref)}"
                    ),
                    unit=unit,
                    source_span=entry.source_span or subject_map.source_span,
                )
            first_entry = seen_entries.get(entry_identity)
            if first_entry is not None:
                raise review_compile_error(
                    code="E470",
                    summary="Invalid review declaration shape",
                    detail=(
                        f"Duplicate review subject_map entry in {owner_label}: "
                        f"{_dotted_ref_name(entry.enum_member_ref)}"
                    ),
                    unit=unit,
                    source_span=entry.source_span or subject_map.source_span,
                    related=(
                        ()
                        if first_entry.source_span is None
                        else (
                            review_related_site(
                                label="first `subject_map` entry",
                                unit=unit,
                                source_span=first_entry.source_span,
                            ),
                        )
                    ),
                )

            subject_unit, subject_decl = self._resolve_review_subjects(
                model.ReviewSubjectConfig(subjects=(entry.artifact_ref,)),
                unit=unit,
                owner_label=f"{owner_label} subject_map",
            )[0]
            subject_key = (subject_unit.module_parts, subject_decl.name)
            if subject_key not in subject_keys:
                raise review_compile_error(
                    code="E470",
                    summary="Invalid review declaration shape",
                    detail=(
                        "Review subject_map target must be one of the declared review "
                        f"subjects in {owner_label}: {_dotted_ref_name(entry.artifact_ref)}"
                    ),
                    unit=unit,
                    source_span=entry.source_span or subject_map.source_span,
                )
            mapping[entry_identity] = subject_key
            seen_entries[entry_identity] = entry

        return mapping

    def _collect_review_contract_gates(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ReviewContractGate, ...]:
        if workflow_body.law is not None:
            raise review_compile_error(
                code="E477",
                summary="Invalid review contract target",
                detail=f"Review contract uses unsupported workflow features in {owner_label}.",
                unit=unit,
                source_span=workflow_body.law.source_span,
            )

        gates: list[ReviewContractGate] = []
        seen: dict[str, ReviewContractGate] = {}
        for item in workflow_body.items:
            if isinstance(item, ResolvedWorkflowSkillsItem):
                raise review_compile_error(
                    code="E477",
                    summary="Invalid review contract target",
                    detail=f"Review contract uses unsupported workflow features in {owner_label}.",
                    unit=unit,
                    source_span=item.source_span,
                )
            if isinstance(item, ResolvedSectionItem):
                first_gate = seen.get(item.key)
                if first_gate is not None:
                    raise review_compile_error(
                        code="E477",
                        summary="Invalid review contract target",
                        detail=f"Duplicate review contract gate in {owner_label}: {item.key}",
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            ()
                            if first_gate.unit is None or first_gate.source_span is None
                            else (
                                review_related_site(
                                    label=f"first `{item.key}` gate",
                                    unit=first_gate.unit,
                                    source_span=first_gate.source_span,
                                ),
                            )
                        ),
                    )
                gate = ReviewContractGate(
                    key=item.key,
                    title=item.title,
                    unit=unit,
                    source_span=item.source_span,
                )
                seen[item.key] = gate
                gates.append(gate)
                continue
            nested = self._collect_review_contract_gates(
                self._resolve_workflow_decl(item.workflow_decl, unit=item.target_unit),
                unit=item.target_unit,
                owner_label=owner_label,
            )
            for gate in nested:
                first_gate = seen.get(gate.key)
                if first_gate is not None:
                    raise review_compile_error(
                        code="E477",
                        summary="Invalid review contract target",
                        detail=f"Duplicate review contract gate in {owner_label}: {gate.key}",
                        unit=gate.unit or unit,
                        source_span=gate.source_span,
                        related=(
                            ()
                            if first_gate.unit is None or first_gate.source_span is None
                            else (
                                review_related_site(
                                    label=f"first `{gate.key}` gate",
                                    unit=first_gate.unit,
                                    source_span=first_gate.source_span,
                                ),
                            )
                        ),
                    )
                seen[gate.key] = gate
                gates.append(gate)
        return tuple(gates)

    def _collect_schema_review_contract_gates(
        self,
        schema_body: ResolvedSchemaBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ReviewContractGate, ...]:
        gates: list[ReviewContractGate] = []
        seen: dict[str, model.SchemaGate] = {}
        for item in schema_body.gates:
            first_gate = seen.get(item.key)
            if first_gate is not None:
                raise review_compile_error(
                    code="E477",
                    summary="Invalid review contract target",
                    detail=f"Duplicate review contract gate in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        ()
                        if first_gate.source_span is None
                        else (
                            review_related_site(
                                label=f"first `{item.key}` gate",
                                unit=unit,
                                source_span=first_gate.source_span,
                            ),
                        )
                    ),
                )
            seen[item.key] = item
            gates.append(
                ReviewContractGate(
                    key=item.key,
                    title=item.title,
                    unit=unit,
                    source_span=item.source_span,
                )
            )
        return tuple(gates)

    def _validate_review_case_gate_override(
        self,
        case: model.ReviewCase,
        contract_spec: ReviewContractSpec,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ReviewContractGate, ...]:
        override = case.gates_override
        contract_gate_by_key: dict[str, ReviewContractGate] = {
            g.key: g for g in contract_spec.gates
        }
        if override is None:
            return contract_spec.gates

        effective: dict[str, ReviewContractGate] = dict(contract_gate_by_key)

        # E531: `remove` name must reference a declared contract gate.
        for remove_key in override.remove:
            if remove_key not in effective:
                raise review_compile_error(
                    code="E531",
                    summary="Gate removed from review case is not declared in the contract",
                    detail=(
                        f"Review case `{case.key}` in {owner_label} removes gate "
                        f"`{remove_key}`, but that gate is not declared by the case's contract."
                    ),
                    unit=unit,
                    source_span=override.source_span or case.source_span,
                    hints=(
                        "Remove gates that the contract actually declares, or drop the `remove` line.",
                    ),
                )
            del effective[remove_key]

        # E532: `add` must not collide with an existing effective gate.
        for add_gate in override.add:
            if add_gate.key in effective:
                raise review_compile_error(
                    code="E532",
                    summary="Gate added or modified in review case collides with an existing name",
                    detail=(
                        f"Review case `{case.key}` in {owner_label} adds gate "
                        f"`{add_gate.key}`, but that name is already declared in the case's "
                        "effective gate set."
                    ),
                    unit=unit,
                    source_span=add_gate.source_span or override.source_span or case.source_span,
                    hints=(
                        "Pick a unique gate name, or use `modify` to change the message of an existing gate.",
                    ),
                )
            effective[add_gate.key] = ReviewContractGate(
                key=add_gate.key,
                title=add_gate.title,
                unit=unit,
                source_span=add_gate.source_span,
            )

        # E531/E532: `modify` must target an existing effective gate and must not
        # collide with another `modify` entry on the same case.
        seen_modify: set[str] = set()
        for modify_gate in override.modify:
            if modify_gate.key in seen_modify:
                raise review_compile_error(
                    code="E532",
                    summary="Gate added or modified in review case collides with an existing name",
                    detail=(
                        f"Review case `{case.key}` in {owner_label} modifies gate "
                        f"`{modify_gate.key}` more than once."
                    ),
                    unit=unit,
                    source_span=modify_gate.source_span or override.source_span or case.source_span,
                    hints=("Keep at most one `modify` line per gate name in a review case.",),
                )
            seen_modify.add(modify_gate.key)
            if modify_gate.key not in effective:
                raise review_compile_error(
                    code="E531",
                    summary="Gate removed from review case is not declared in the contract",
                    detail=(
                        f"Review case `{case.key}` in {owner_label} modifies gate "
                        f"`{modify_gate.key}`, but that gate is not declared by the case's "
                        "contract (after `remove` entries apply)."
                    ),
                    unit=unit,
                    source_span=modify_gate.source_span or override.source_span or case.source_span,
                    hints=(
                        "Use `add` for new gates; reserve `modify` for gates the contract declares.",
                    ),
                )
            effective[modify_gate.key] = ReviewContractGate(
                key=modify_gate.key,
                title=modify_gate.title,
                unit=unit,
                source_span=modify_gate.source_span,
            )

        return tuple(effective.values())

    def _review_output_path_is_live(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        status, _has_guards = self._review_output_path_guard_status(
            output_decl,
            path=path,
            unit=unit,
            branch=branch,
        )
        return status is True

    def _review_output_path_has_matching_failure_guard(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        status, has_guards = self._review_output_path_guard_status(
            output_decl,
            path=path,
            unit=unit,
            branch=branch,
        )
        return has_guards and status is True

    def _review_trust_surface_path_is_live(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        statuses: list[bool | None] = []
        for item in output_decl.trust_surface:
            if item.path != path:
                continue
            if item.when_expr is None:
                return True
            statuses.append(
                self._evaluate_review_semantic_guard(
                    item.when_expr,
                    unit=unit,
                    branch=branch,
                )
            )
        if not statuses:
            return False
        if any(status is True for status in statuses):
            return True
        return False

    def _review_output_path_guard_status(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> tuple[bool | None, bool]:
        guards = self._output_path_guards(output_decl.items, path=path)
        if not guards:
            return True, False
        seen_unknown = False
        for guard in guards:
            status = self._evaluate_review_semantic_guard(
                guard,
                unit=unit,
                branch=branch,
            )
            if status is False:
                return False, True
            if status is None:
                seen_unknown = True
        return (None if seen_unknown else True), True

    def _output_path_guards(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        path: tuple[str, ...],
    ) -> tuple[model.Expr, ...]:
        guards: list[model.Expr] = []
        current_items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...] = items
        for segment in path:
            matched_item: model.AnyRecordItem | None = None
            for item in current_items:
                if isinstance(
                    item,
                    (
                        model.RecordSection,
                        model.GuardedOutputSection,
                        model.GuardedOutputScalar,
                        model.RecordScalar,
                    ),
                ):
                    if item.key == segment:
                        matched_item = item
                        break
            if matched_item is None:
                break
            if isinstance(matched_item, model.GuardedOutputSection):
                guards.append(matched_item.when_expr)
                current_items = matched_item.items
                continue
            if isinstance(matched_item, model.GuardedOutputScalar):
                guards.append(matched_item.when_expr)
                current_items = matched_item.body or ()
                continue
            if isinstance(matched_item, model.RecordSection):
                current_items = matched_item.items
                continue
            if isinstance(matched_item, model.RecordScalar) and matched_item.body is not None:
                current_items = matched_item.body
                continue
            current_items = ()
        return tuple(guards)

    def _evaluate_review_semantic_guard(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._evaluate_review_semantic_guard(expr.left, unit=unit, branch=branch)
                right = self._evaluate_review_semantic_guard(expr.right, unit=unit, branch=branch)
                if left is False or right is False:
                    return False
                if left is True and right is True:
                    return True
                return None
            if expr.op == "or":
                left = self._evaluate_review_semantic_guard(expr.left, unit=unit, branch=branch)
                right = self._evaluate_review_semantic_guard(expr.right, unit=unit, branch=branch)
                if left is True or right is True:
                    return True
                if left is False and right is False:
                    return False
                return None

        if not isinstance(expr, model.ExprBinary):
            constant = self._resolve_review_semantic_expr_constant(expr, unit=unit, branch=branch)
            if isinstance(constant, bool):
                return constant
            return None

        left = self._resolve_review_semantic_expr_constant(expr.left, unit=unit, branch=branch)
        right = self._resolve_review_semantic_expr_constant(expr.right, unit=unit, branch=branch)
        if left is None or right is None:
            return None
        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        return None

    def _review_semantic_field_present(
        self,
        field_name: str,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool | None:
        if field_name == "current_artifact":
            return isinstance(branch.current, model.ReviewCurrentArtifactStmt)
        if field_name == "blocked_gate":
            return branch.blocked_gate_id is not None
        return self._review_semantic_ref_value(
            field_name,
            unit=unit,
            branch=branch,
        ) is not None

    def _review_semantic_field_ref_name(self, ref: model.ExprRef) -> str | None:
        if len(ref.parts) == 1:
            return ref.parts[0]
        if len(ref.parts) == 2 and ref.parts[0] == "fields":
            return ref.parts[1]
        return None

    def _resolved_review_route(
        self,
        branch: ResolvedReviewAgreementBranch,
        *,
        unit: IndexedUnit,
    ) -> model.ReviewOutcomeRouteStmt | None:
        if branch.route is None:
            return None
        if branch.route.when_expr is None:
            return branch.route
        return (
            branch.route
            if self._evaluate_review_semantic_guard(
                branch.route.when_expr,
                unit=unit,
                branch=branch,
            )
            is True
            else None
        )

    def _review_semantic_ref_value(
        self,
        field_name: str,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> str | None:
        if field_name == "verdict":
            return branch.verdict
        if field_name == "next_owner":
            route = self._resolved_review_route(branch, unit=unit)
            return None if route is None else route.target.declaration_name
        if field_name == "current_artifact":
            if branch.current_subject_key is None:
                return None
            module_parts, decl_name = branch.current_subject_key
            return _dotted_decl_name(module_parts, decl_name)
        if field_name == "reviewed_artifact":
            if branch.reviewed_subject_key is None:
                return None
            module_parts, decl_name = branch.reviewed_subject_key
            return _dotted_decl_name(module_parts, decl_name)
        if field_name == "failing_gates":
            return ",".join(branch.failing_gate_ids) if branch.failing_gate_ids else None
        if field_name == "blocked_gate":
            return branch.blocked_gate_id
        for carry in reversed(branch.carries):
            if carry.field_name == field_name:
                if isinstance(carry.expr, model.ExprRef):
                    return self._resolve_constant_enum_member(carry.expr, unit=unit) or ".".join(carry.expr.parts)
                resolved = self._resolve_constant_enum_member(carry.expr, unit=unit)
                if resolved is not None:
                    return resolved
                if isinstance(carry.expr, str):
                    return carry.expr
        return None

    def _review_membership_contains(
        self,
        container: str | int | bool | tuple[str | int | bool, ...],
        value: str | int | bool,
    ) -> bool:
        if isinstance(container, tuple):
            return value in container
        return value == container

    def _review_gate_sentence(
        self,
        prefix: str,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        gate_text = self._review_gate_text(
            gate,
            contract_spec=contract_spec,
            section_titles=section_titles,
        )
        gate_text = gate_text.rstrip(".")
        if prefix.endswith("if"):
            return f"{prefix} {gate_text}."
        return f"{prefix}: {gate_text}."

    def _review_gate_text(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        if isinstance(gate, str):
            return gate
        if isinstance(gate, model.ContractGateRef):
            for item in contract_spec.gates:
                if item.key == gate.key:
                    return item.title
            return f"contract.{gate.key}"
        return section_titles.get(gate.key, gate.key)

    def _review_gate_identity(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        if isinstance(gate, str):
            return gate
        if isinstance(gate, model.ContractGateRef):
            _ = contract_spec
            return f"contract.{gate.key}"
        _ = section_titles
        return gate.key

    def _expr_ref_matches_review_semantic_ref(
        self,
        ref: model.ExprRef,
        *,
        review_semantics: ReviewSemanticContext | None,
    ) -> bool:
        if review_semantics is None or len(ref.parts) < 2:
            return False
        if ref.parts[0] == "fields":
            return self._review_semantic_field_path(review_semantics, ref.parts[1]) is not None
        if ref.parts[0] == "contract":
            if ref.parts[1] in _REVIEW_CONTRACT_FACT_KEYS and len(ref.parts) == 2:
                return True
            return (
                len(ref.parts) == 2
                and self._review_semantic_contract_gate(review_semantics, ref.parts[1]) is not None
            )
        return False

    def _review_semantic_fallback_lookup_unit(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None,
    ) -> IndexedUnit | None:
        if review_semantics is None or ref.module_parts:
            return None
        if review_semantics.review_module_parts == unit.module_parts:
            return None
        return self._load_module(review_semantics.review_module_parts)
