from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import _REVIEW_OPTIONAL_FIELD_NAMES
from doctrine._compiler.review_diagnostics import review_compile_error, review_related_site
from doctrine._compiler.resolved_types import (
    AddressableTarget,
    AgentContract,
    CompileError,
    IndexedUnit,
    ResolvedReviewAgreementBranch,
    ResolvedReviewGateBranch,
    ReviewOutcomeBranch,
)


class ValidateReviewAgreementMixin:
    """Review outcome agreement helpers for ValidateMixin."""

    def _review_field_binding_source_spans(
        self,
        fields: model.ReviewFieldsConfig,
    ) -> dict[str, model.SourceSpan | None]:
        return {
            binding.semantic_field: binding.source_span
            for binding in fields.bindings
        }

    def _review_output_field_source_span(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        owner_label: str,
    ) -> model.SourceSpan | None:
        try:
            node = self._resolve_output_field_node(
                output_decl,
                path=path,
                unit=unit,
                owner_label=owner_label,
                surface_label="review output agreement",
            )
        except CompileError:
            return None
        return getattr(node.target, "source_span", None)

    def _review_output_field_related_sites(
        self,
        *,
        label: str,
        output_decl: model.OutputDecl,
        path: tuple[str, ...],
        output_unit: IndexedUnit,
        owner_label: str,
    ) -> tuple:
        source_span = self._review_output_field_source_span(
            output_decl,
            path=path,
            unit=output_unit,
            owner_label=owner_label,
        )
        if source_span is None:
            return ()
        return (
            review_related_site(
                label=label,
                unit=output_unit,
                source_span=source_span,
            ),
        )

    def _review_bound_field_location(
        self,
        field_name: str,
        *,
        field_binding_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        field_binding_spans: dict[str, model.SourceSpan | None],
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[IndexedUnit, model.SourceSpan | None]:
        source_span = field_binding_spans.get(field_name)
        if source_span is not None:
            return field_binding_unit, source_span
        bound_path = field_bindings.get(field_name)
        if bound_path is None:
            return field_binding_unit, None
        return (
            output_unit,
            self._review_output_field_source_span(
                output_decl,
                path=bound_path,
                unit=output_unit,
                owner_label=owner_label,
            ),
        )

    def _validate_review_outcome_section(
        self,
        section: model.ReviewOutcomeSection,
        *,
        unit: IndexedUnit,
        field_binding_unit: IndexedUnit,
        owner_label: str,
        agent_contract: AgentContract,
        comment_output_decl: model.OutputDecl,
        comment_output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
        field_binding_spans: dict[str, model.SourceSpan | None],
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        blocked_gate_required: bool,
        gate_branches: tuple[ResolvedReviewGateBranch, ...],
    ) -> tuple[ResolvedReviewAgreementBranch, ...]:
        self._validate_review_outcome_items(
            section.items,
            unit=unit,
            owner_label=f"{owner_label}.{section.key}",
        )
        gate_branches = self._compress_review_gate_branches_for_validation(
            gate_branches,
            output_decl=comment_output_decl,
            field_bindings=field_bindings,
        )
        branches = self._collect_review_outcome_leaf_branches(section.items, unit=unit)
        if not branches:
            raise review_compile_error(
                code="E484",
                summary="Review outcome is not total",
                detail=(
                    f"Review outcome branch `{section.key}` is not total in {owner_label}."
                ),
                unit=unit,
                source_span=section.source_span,
            )

        resolved_branches: list[ResolvedReviewAgreementBranch] = []
        for branch in branches:
            if not branch.currents:
                raise review_compile_error(
                    code="E484",
                    summary="Review outcome is not total",
                    detail=(
                        f"Review outcome branch `{section.key}` is not total in {owner_label}."
                    ),
                    unit=unit,
                    source_span=section.source_span,
                )
            if len(branch.routes) > 1:
                raise review_compile_error(
                    code="E485",
                    summary="Review outcome resolves more than one route",
                    detail=(
                        f"Review outcome branch `{section.key}` resolves more than one route "
                        f"in {owner_label}."
                    ),
                    unit=unit,
                    source_span=branch.routes[-1].source_span or section.source_span,
                    related=(
                        ()
                        if branch.routes[0].source_span is None
                        else (
                            review_related_site(
                                label="first route",
                                unit=unit,
                                source_span=branch.routes[0].source_span,
                            ),
                        )
                    ),
                )
            if len(branch.currents) > 1:
                raise review_compile_error(
                    code="E486",
                    summary="Review outcome resolves more than one currentness result",
                    detail=(
                        f"Review outcome branch `{section.key}` resolves more than one "
                        f"currentness result in {owner_label}."
                    ),
                    unit=unit,
                    source_span=branch.currents[-1].source_span or section.source_span,
                    related=(
                        ()
                        if branch.currents[0].source_span is None
                        else (
                            review_related_site(
                                label="first currentness result",
                                unit=unit,
                                source_span=branch.currents[0].source_span,
                            ),
                        )
                    ),
                )

            for gate_branch in gate_branches:
                if (
                    branch.blocked_gate_present is not None
                    and branch.blocked_gate_present != (gate_branch.blocked_gate_id is not None)
                ):
                    continue
                resolved_branch = self._resolve_review_agreement_branch(
                    branch,
                    section_key=section.key,
                    unit=unit,
                    owner_label=f"{owner_label}.{section.key}",
                    agent_contract=agent_contract,
                    comment_output_decl=comment_output_decl,
                    comment_output_unit=comment_output_unit,
                    field_bindings=field_bindings,
                    subject_keys=subject_keys,
                    subject_map=subject_map,
                    blocked_gate_required=blocked_gate_required,
                    gate_branch=gate_branch,
                )

                branch_proves_subject = self._review_branch_proves_subject(
                    branch,
                    unit=unit,
                    subject_keys=subject_keys,
                    subject_map=subject_map,
                    current_subject_key=resolved_branch.current_subject_key,
                    reviewed_subject_key=resolved_branch.reviewed_subject_key,
                    owner_label=f"{owner_label}.{section.key}",
                )
                blocked_before_subject_review = (
                    (
                        resolved_branch.blocked_gate_id is not None
                        or (section.key == "on_reject" and blocked_gate_required)
                    )
                    and isinstance(resolved_branch.current, model.ReviewCurrentNoneStmt)
                )
                if len(subject_keys) > 1 and not branch_proves_subject and not blocked_before_subject_review:
                    raise review_compile_error(
                        code="E489",
                        summary="Review subject set requires disambiguation",
                        detail=(
                            f"Review subject set requires disambiguation in {owner_label} "
                            f"branch `{section.key}`."
                        ),
                        unit=unit,
                        source_span=section.source_span,
                    )

                self._validate_review_output_agreement_branch(
                    resolved_branch,
                    unit=unit,
                    field_binding_unit=field_binding_unit,
                    output_decl=comment_output_decl,
                    output_unit=comment_output_unit,
                    next_owner_field_path=next_owner_field_path,
                    field_bindings=field_bindings,
                    field_binding_spans=field_binding_spans,
                    owner_label=f"{owner_label}.{section.key}",
                )
                resolved_branches.append(resolved_branch)

        return tuple(resolved_branches)

    def _review_subject_key_from_subject_map(
        self,
        branch: ReviewOutcomeBranch,
        *,
        unit: IndexedUnit,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        active_mode = next((carry for carry in branch.carries if carry.field_name == "active_mode"), None)
        if active_mode is None:
            return None
        active_mode_identity = self._resolve_enum_member_identity(active_mode.expr, unit=unit)
        if active_mode_identity is None:
            return None
        mapping = self._resolved_review_subject_map(
            subject_map,
            unit=unit,
            owner_label=owner_label,
            subject_keys=subject_keys,
        )
        return mapping.get(active_mode_identity)

    def _record_item_subject_keys(
        self,
        item: AddressableTarget,
        *,
        subject_keys: set[tuple[tuple[str, ...], str]],
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[tuple[str, ...], str], ...]:
        referenced: list[tuple[tuple[str, ...], str]] = []
        seen: set[tuple[tuple[str, ...], str]] = set()

        def add_subject_key(key: tuple[tuple[str, ...], str] | None) -> None:
            if key is None or key not in subject_keys or key in seen:
                return
            seen.add(key)
            referenced.append(key)

        if isinstance(item, model.RecordScalar):
            if isinstance(item.value, model.NameRef):
                add_subject_key(
                    self._review_subject_key_from_name_ref(
                        item.value,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
            elif isinstance(item.value, model.AddressableRef):
                add_subject_key(
                    self._review_subject_key_from_addressable_ref(
                        item.value,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
        for ref in self._iter_record_item_interpolation_refs(item):
            add_subject_key(
                self._review_subject_key_from_addressable_ref(
                    ref,
                    unit=unit,
                    owner_label=owner_label,
                )
            )
        return tuple(referenced)

    def _review_subject_key_from_name_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        matches: list[tuple[IndexedUnit, model.InputDecl | model.OutputDecl]] = []
        try:
            lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        except CompileError:
            return None
        for lookup_target in lookup_targets:
            input_decl = lookup_target.unit.inputs_by_name.get(lookup_target.declaration_name)
            output_decl = self._resolve_local_output_decl(
                lookup_target.declaration_name,
                unit=lookup_target.unit,
            )
            if input_decl is None and output_decl is None:
                continue
            if input_decl is not None and output_decl is not None:
                _ = owner_label
                return None
            decl = input_decl if input_decl is not None else output_decl
            assert decl is not None
            matches.append((lookup_target.unit, decl))
        if len(matches) != 1:
            return None
        target_unit, decl = matches[0]
        return (target_unit.module_parts, decl.name)

    def _review_subject_key_from_addressable_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        try:
            ref = self._rebind_self_addressable_ref(
                ref,
                unit=unit,
                owner_label=owner_label,
                surface_label="reviewed_artifact",
            )
            root_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="reviewed_artifact interpolation ref",
                missing_local_label="reviewed_artifact",
            )
        except CompileError:
            return None
        if not isinstance(root_decl, (model.InputDecl, model.OutputDecl)):
            return None
        if ref.path and ref.path not in {("name",), ("title",)}:
            return None
        return (root_unit.module_parts, root_decl.name)

    def _validate_review_output_agreement_branch(
        self,
        branch: ResolvedReviewAgreementBranch,
        *,
        unit: IndexedUnit,
        field_binding_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
        field_binding_spans: dict[str, model.SourceSpan | None],
        owner_label: str,
    ) -> None:
        verdict_path = field_bindings["verdict"]
        verdict_location_unit, verdict_source_span = self._review_bound_field_location(
            "verdict",
            field_binding_unit=field_binding_unit,
            field_bindings=field_bindings,
            field_binding_spans=field_binding_spans,
            output_decl=output_decl,
            output_unit=output_unit,
            owner_label=owner_label,
        )
        if not self._review_output_path_is_live(
            output_decl,
            path=verdict_path,
            unit=output_unit,
            branch=branch,
        ):
            raise review_compile_error(
                code="E495",
                summary="Review verdict does not match the bound output field",
                detail=(
                    "Resolved review verdict is not guaranteed to reach bound output field "
                    f"`{output_decl.name}.{'.'.join(verdict_path)}` in {owner_label}."
                ),
                unit=verdict_location_unit,
                source_span=verdict_source_span,
            )

        route = self._resolved_review_route(branch, unit=unit)
        next_owner_location_unit, next_owner_source_span = self._review_bound_field_location(
            "next_owner",
            field_binding_unit=field_binding_unit,
            field_bindings=field_bindings,
            field_binding_spans=field_binding_spans,
            output_decl=output_decl,
            output_unit=output_unit,
            owner_label=owner_label,
        )
        if route is not None:
            if not self._review_output_path_is_live(
                output_decl,
                path=next_owner_field_path,
                unit=output_unit,
                branch=branch,
            ):
                raise review_compile_error(
                    code="E496",
                    summary="Review next owner does not match the bound output field",
                    detail=(
                        f"Resolved next owner `{route.target.declaration_name}` is not "
                        "guaranteed to reach bound output field "
                        f"`{output_decl.name}.{'.'.join(next_owner_field_path)}` "
                        f"in {owner_label}."
                    ),
                    unit=next_owner_location_unit,
                    source_span=next_owner_source_span,
                    related=(
                        ()
                        if route.source_span is None
                        else (
                            review_related_site(
                                label="resolved route",
                                unit=unit,
                                source_span=route.source_span,
                            ),
                        )
                    ),
                )
            self._validate_review_next_owner_binding(
                route,
                review_unit=unit,
                field_location_unit=next_owner_location_unit,
                field_source_span=next_owner_source_span,
                output_decl=output_decl,
                output_unit=output_unit,
                field_path=next_owner_field_path,
                owner_label=owner_label,
            )
        elif self._review_output_path_is_live(
            output_decl,
            path=next_owner_field_path,
            unit=output_unit,
            branch=branch,
        ):
            raise review_compile_error(
                code="E499",
                summary="Required conditional review output section is missing after its guard resolves true",
                detail=(
                    "Conditional review output field "
                    f"`{output_decl.name}.{'.'.join(next_owner_field_path)}` for semantic "
                    f"channel `next_owner` is not aligned with resolved review semantics in "
                    f"{owner_label}."
                ),
                unit=next_owner_location_unit,
                source_span=next_owner_source_span,
            )

        if isinstance(branch.current, model.ReviewCurrentArtifactStmt):
            if branch.current_carrier_path is None:
                raise review_compile_error(
                    code="E299",
                    summary="Invalid review agreement state",
                    detail=(
                        f"Internal compiler error: missing review current carrier path in "
                        f"{owner_label}."
                    ),
                    unit=unit,
                    source_span=branch.current.source_span,
                )
            if not self._review_output_path_is_live(
                output_decl,
                path=branch.current_carrier_path,
                unit=output_unit,
                branch=branch,
            ):
                raise review_compile_error(
                    code="E497",
                    summary="Review currentness does not match the declared carrier field",
                    detail=(
                        "Resolved review currentness is not guaranteed to reach carrier field "
                        f"`{output_decl.name}.{'.'.join(branch.current_carrier_path)}` "
                        f"in {owner_label}."
                    ),
                    unit=unit,
                    source_span=branch.current.source_span,
                    related=self._review_output_field_related_sites(
                        label="carrier field",
                        output_decl=output_decl,
                        path=branch.current_carrier_path,
                        output_unit=output_unit,
                        owner_label=owner_label,
                    ),
                )

        for carry in branch.carries:
            bound_path = field_bindings[carry.field_name]
            carry_location_unit, carry_source_span = self._review_bound_field_location(
                carry.field_name,
                field_binding_unit=field_binding_unit,
                field_bindings=field_bindings,
                field_binding_spans=field_binding_spans,
                output_decl=output_decl,
                output_unit=output_unit,
                owner_label=owner_label,
            )
            if not self._review_output_path_is_live(
                output_decl,
                path=bound_path,
                unit=output_unit,
                branch=branch,
            ) or not self._review_trust_surface_path_is_live(
                output_decl,
                path=bound_path,
                unit=output_unit,
                branch=branch,
            ):
                raise review_compile_error(
                    code="E498",
                    summary="Required carried review field is omitted when semantic value exists",
                    detail=(
                        f"Carried review field `{carry.field_name}` is not guaranteed to reach "
                        "bound output field "
                        f"`{output_decl.name}.{'.'.join(bound_path)}` in {owner_label}."
                    ),
                    unit=carry_location_unit,
                    source_span=carry_source_span,
                    related=(
                        ()
                        if carry.source_span is None
                        else (
                            review_related_site(
                                label=f"semantic `{carry.field_name}` carry",
                                unit=unit,
                                source_span=carry.source_span,
                            ),
                        )
                    ),
                )

        failing_gates_path = field_bindings["failing_gates"]
        failing_gates_location_unit, failing_gates_source_span = self._review_bound_field_location(
            "failing_gates",
            field_binding_unit=field_binding_unit,
            field_bindings=field_bindings,
            field_binding_spans=field_binding_spans,
            output_decl=output_decl,
            output_unit=output_unit,
            owner_label=owner_label,
        )
        if branch.requires_failure_detail:
            if not self._review_output_path_has_matching_failure_guard(
                output_decl,
                path=failing_gates_path,
                unit=output_unit,
                branch=branch,
            ):
                raise review_compile_error(
                    code="E499",
                    summary="Required conditional review output section is missing after its guard resolves true",
                    detail=(
                        "Conditional review output field "
                        f"`{output_decl.name}.{'.'.join(failing_gates_path)}` for semantic "
                        f"channel `failing_gates` is not aligned with resolved review semantics "
                        f"in {owner_label}."
                    ),
                    unit=failing_gates_location_unit,
                    source_span=failing_gates_source_span,
                )
            if branch.blocked_gate_id is not None:
                blocked_gate_path = field_bindings["blocked_gate"]
                blocked_gate_location_unit, blocked_gate_source_span = self._review_bound_field_location(
                    "blocked_gate",
                    field_binding_unit=field_binding_unit,
                    field_bindings=field_bindings,
                    field_binding_spans=field_binding_spans,
                    output_decl=output_decl,
                    output_unit=output_unit,
                    owner_label=owner_label,
                )
                if not self._review_output_path_has_matching_failure_guard(
                    output_decl,
                    path=blocked_gate_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    raise review_compile_error(
                        code="E499",
                        summary="Required conditional review output section is missing after its guard resolves true",
                        detail=(
                            "Conditional review output field "
                            f"`{output_decl.name}.{'.'.join(blocked_gate_path)}` for semantic "
                            f"channel `blocked_gate` is not aligned with resolved review semantics "
                            f"in {owner_label}."
                        ),
                        unit=blocked_gate_location_unit,
                        source_span=blocked_gate_source_span,
                    )
        elif self._review_output_path_is_live(
            output_decl,
            path=failing_gates_path,
            unit=output_unit,
            branch=branch,
        ):
            raise review_compile_error(
                code="E499",
                summary="Required conditional review output section is missing after its guard resolves true",
                detail=(
                    "Conditional review output field "
                    f"`{output_decl.name}.{'.'.join(failing_gates_path)}` for semantic channel "
                    f"`failing_gates` is not aligned with resolved review semantics in "
                    f"{owner_label}."
                ),
                unit=failing_gates_location_unit,
                source_span=failing_gates_source_span,
            )

    def _validate_review_current_artifact_alignment(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        review_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        carrier_paths = tuple(
            dict.fromkeys(
                branch.current_carrier_path
                for branch in branches
                if (
                    isinstance(branch.current, model.ReviewCurrentArtifactStmt)
                    and branch.current_carrier_path is not None
                )
            )
        )
        if not carrier_paths:
            return

        for branch in branches:
            if not isinstance(branch.current, model.ReviewCurrentNoneStmt):
                continue
            for carrier_path in carrier_paths:
                if not self._review_output_path_is_live(
                    output_decl,
                    path=carrier_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    continue
                raise review_compile_error(
                    code="E497",
                    summary="Review currentness does not match the declared carrier field",
                    detail=(
                        f"Carrier field `{output_decl.name}.{'.'.join(carrier_path)}` stays "
                        "live even though the review resolves `current none` in "
                        f"{owner_label}.{branch.section_key}."
                    ),
                    unit=review_unit,
                    source_span=branch.current.source_span,
                    related=self._review_output_field_related_sites(
                        label="carrier field",
                        output_decl=output_decl,
                        path=carrier_path,
                        output_unit=output_unit,
                        owner_label=f"{owner_label}.{branch.section_key}",
                    ),
                )

    def _validate_review_optional_field_alignment(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        field_binding_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        field_binding_spans: dict[str, model.SourceSpan | None],
        owner_label: str,
    ) -> None:
        for field_name in _REVIEW_OPTIONAL_FIELD_NAMES:
            bound_path = field_bindings.get(field_name)
            if bound_path is None:
                continue
            field_location_unit, field_source_span = self._review_bound_field_location(
                field_name,
                field_binding_unit=field_binding_unit,
                field_bindings=field_bindings,
                field_binding_spans=field_binding_spans,
                output_decl=output_decl,
                output_unit=output_unit,
                owner_label=owner_label,
            )
            for branch in branches:
                field_present = (
                    branch.blocked_gate_id is not None
                    if field_name == "blocked_gate"
                    else any(carry.field_name == field_name for carry in branch.carries)
                )
                if field_present:
                    continue
                if not self._review_output_path_is_live(
                    output_decl,
                    path=bound_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    continue
                raise review_compile_error(
                    code="E499",
                    summary="Required conditional review output section is missing after its guard resolves true",
                    detail=(
                        "Conditional review output field "
                        f"`{output_decl.name}.{'.'.join(bound_path)}` for semantic channel "
                        f"`{field_name}` is not aligned with resolved review semantics in "
                        f"{owner_label}.{branch.section_key}."
                    ),
                    unit=field_location_unit,
                    source_span=field_source_span,
                )

    def _validate_review_semantic_output_bindings(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        review_unit: IndexedUnit,
        field_binding_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        field_binding_spans: dict[str, model.SourceSpan | None],
        owner_label: str,
    ) -> None:
        for branch in branches:
            for field_name, bound_path in field_bindings.items():
                field_location_unit, field_source_span = self._review_bound_field_location(
                    field_name,
                    field_binding_unit=field_binding_unit,
                    field_bindings=field_bindings,
                    field_binding_spans=field_binding_spans,
                    output_decl=output_decl,
                    output_unit=output_unit,
                    owner_label=owner_label,
                )
                if field_name == "verdict":
                    if self._review_output_path_is_live(
                        output_decl,
                        path=bound_path,
                        unit=output_unit,
                        branch=branch,
                    ):
                        continue
                    raise review_compile_error(
                        code="E495",
                        summary="Review verdict does not match the bound output field",
                        detail=(
                            "Resolved review verdict is not guaranteed to reach bound output "
                            f"field `{output_decl.name}.{'.'.join(bound_path)}` in "
                            f"{owner_label}."
                        ),
                        unit=field_location_unit,
                        source_span=field_source_span,
                    )

                if field_name == "next_owner":
                    route = self._resolved_review_route(branch, unit=review_unit)
                    if route is None:
                        if not self._review_output_path_is_live(
                            output_decl,
                            path=bound_path,
                            unit=output_unit,
                            branch=branch,
                        ):
                            continue
                        raise review_compile_error(
                            code="E499",
                            summary="Required conditional review output section is missing after its guard resolves true",
                            detail=(
                                "Conditional review output field "
                                f"`{output_decl.name}.{'.'.join(bound_path)}` for semantic "
                                f"channel `next_owner` is not aligned with resolved review "
                                f"semantics in {owner_label}."
                            ),
                            unit=field_location_unit,
                            source_span=field_source_span,
                        )
                    if not self._review_output_path_is_live(
                        output_decl,
                        path=bound_path,
                        unit=output_unit,
                        branch=branch,
                    ):
                        raise review_compile_error(
                            code="E496",
                            summary="Review next owner does not match the bound output field",
                            detail=(
                                f"Resolved next owner `{route.target.declaration_name}` is not "
                                "guaranteed to reach bound output field "
                                f"`{output_decl.name}.{'.'.join(bound_path)}` in {owner_label}."
                            ),
                            unit=field_location_unit,
                            source_span=field_source_span,
                            related=(
                                ()
                                if route.source_span is None
                                else (
                                    review_related_site(
                                        label="resolved route",
                                        unit=review_unit,
                                        source_span=route.source_span,
                                    ),
                                )
                            ),
                        )
                    self._validate_review_next_owner_binding(
                        route,
                        review_unit=review_unit,
                        field_location_unit=field_location_unit,
                        field_source_span=field_source_span,
                        output_decl=output_decl,
                        output_unit=output_unit,
                        field_path=bound_path,
                        owner_label=owner_label,
                    )
                    continue

                if field_name in {"analysis", "readback"}:
                    continue

                semantic_present = self._review_semantic_field_present(
                    field_name,
                    unit=review_unit,
                    branch=branch,
                )
                field_live = self._review_output_path_is_live(
                    output_decl,
                    path=bound_path,
                    unit=output_unit,
                    branch=branch,
                )
                if semantic_present and not field_live:
                    raise review_compile_error(
                        code="E499",
                        summary="Required conditional review output section is missing after its guard resolves true",
                        detail=(
                            "Conditional review output field "
                            f"`{output_decl.name}.{'.'.join(bound_path)}` for semantic channel "
                            f"`{field_name}` is not aligned with resolved review semantics in "
                            f"{owner_label}."
                        ),
                        unit=field_location_unit,
                        source_span=field_source_span,
                    )
                if not semantic_present and field_live:
                    raise review_compile_error(
                        code="E499",
                        summary="Required conditional review output section is missing after its guard resolves true",
                        detail=(
                            "Conditional review output field "
                            f"`{output_decl.name}.{'.'.join(bound_path)}` for semantic channel "
                            f"`{field_name}` is not aligned with resolved review semantics in "
                            f"{owner_label}."
                        ),
                        unit=field_location_unit,
                        source_span=field_source_span,
                    )
