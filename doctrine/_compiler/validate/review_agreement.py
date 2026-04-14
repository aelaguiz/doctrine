from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import _REVIEW_OPTIONAL_FIELD_NAMES
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

    def _validate_review_outcome_section(
        self,
        section: model.ReviewOutcomeSection,
        *,
        unit: IndexedUnit,
        owner_label: str,
        agent_contract: AgentContract,
        comment_output_decl: model.OutputDecl,
        comment_output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
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
            raise CompileError(f"Review outcome is not total in {owner_label}: {section.key}")

        resolved_branches: list[ResolvedReviewAgreementBranch] = []
        for branch in branches:
            if not branch.currents:
                raise CompileError(
                    f"Review outcome is not total in {owner_label}: {section.key}"
                )
            if len(branch.routes) > 1:
                raise CompileError(
                    f"Review outcome resolves more than one route in {owner_label}: {section.key}"
                )
            if len(branch.currents) > 1:
                raise CompileError(
                    f"Review outcome resolves more than one currentness result in {owner_label}: {section.key}"
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
                    raise CompileError(
                        f"Review subject set requires disambiguation in {owner_label}: {section.key}"
                    )

                self._validate_review_output_agreement_branch(
                    resolved_branch,
                    unit=unit,
                    output_decl=comment_output_decl,
                    output_unit=comment_output_unit,
                    next_owner_field_path=next_owner_field_path,
                    field_bindings=field_bindings,
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
        try:
            target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        input_decl = target_unit.inputs_by_name.get(ref.declaration_name)
        output_decl = target_unit.outputs_by_name.get(ref.declaration_name)
        if input_decl is None and output_decl is None:
            return None
        if input_decl is not None and output_decl is not None:
            _ = owner_label
            return None
        decl = input_decl if input_decl is not None else output_decl
        return (target_unit.module_parts, decl.name)

    def _review_subject_key_from_addressable_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        try:
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
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
        owner_label: str,
    ) -> None:
        verdict_path = field_bindings["verdict"]
        if not self._review_output_path_is_live(
            output_decl,
            path=verdict_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review verdict field is not live for semantic verdict in "
                f"{owner_label}: {output_decl.name}.{'.'.join(verdict_path)}"
            )

        route = self._resolved_review_route(branch, unit=unit)
        if route is not None:
            if not self._review_output_path_is_live(
                output_decl,
                path=next_owner_field_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review next_owner field is not live for routed target in "
                    f"{owner_label}: {output_decl.name}.{'.'.join(next_owner_field_path)} -> "
                    f"{route.target.declaration_name}"
                )
            self._validate_review_next_owner_binding(
                route,
                review_unit=unit,
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
            raise CompileError(
                "Review conditional output field is not aligned with resolved review semantics "
                f"in {owner_label}: next_owner -> {output_decl.name}.{'.'.join(next_owner_field_path)}"
            )

        if isinstance(branch.current, model.ReviewCurrentArtifactStmt):
            if branch.current_carrier_path is None:
                raise CompileError(
                    f"Internal compiler error: missing review current carrier path in {owner_label}"
                )
            if not self._review_output_path_is_live(
                output_decl,
                path=branch.current_carrier_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review current artifact carrier field is not live for semantic currentness in "
                    f"{owner_label}: {output_decl.name}.{'.'.join(branch.current_carrier_path)}"
                )

        for carry in branch.carries:
            bound_path = field_bindings[carry.field_name]
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
                raise CompileError(
                    "Review carried field is not live when semantic value exists in "
                    f"{owner_label}: {carry.field_name} -> {output_decl.name}.{'.'.join(bound_path)}"
                )

        failing_gates_path = field_bindings["failing_gates"]
        if branch.requires_failure_detail:
            if not self._review_output_path_has_matching_failure_guard(
                output_decl,
                path=failing_gates_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review conditional output field is not aligned with resolved review semantics "
                    f"in {owner_label}: failing_gates -> {output_decl.name}.{'.'.join(failing_gates_path)}"
                )
            if branch.blocked_gate_id is not None:
                blocked_gate_path = field_bindings["blocked_gate"]
                if not self._review_output_path_has_matching_failure_guard(
                    output_decl,
                    path=blocked_gate_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    raise CompileError(
                        "Review conditional output field is not aligned with resolved review semantics "
                        f"in {owner_label}: blocked_gate -> {output_decl.name}.{'.'.join(blocked_gate_path)}"
                    )
        elif self._review_output_path_is_live(
            output_decl,
            path=failing_gates_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review conditional output field is not aligned with resolved review semantics "
                f"in {owner_label}: failing_gates -> {output_decl.name}.{'.'.join(failing_gates_path)}"
            )

    def _validate_review_current_artifact_alignment(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
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
                raise CompileError(
                    "Review current artifact carrier field stays live without semantic currentness in "
                    f"{owner_label}.{branch.section_key}: {output_decl.name}.{'.'.join(carrier_path)}"
                )

    def _validate_review_optional_field_alignment(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        owner_label: str,
    ) -> None:
        for field_name in _REVIEW_OPTIONAL_FIELD_NAMES:
            bound_path = field_bindings.get(field_name)
            if bound_path is None:
                continue
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
                raise CompileError(
                    "Review conditional output field is not aligned with resolved review semantics "
                    f"in {owner_label}.{branch.section_key}: {field_name} -> "
                    f"{output_decl.name}.{'.'.join(bound_path)}"
                )

    def _validate_review_semantic_output_bindings(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        review_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        owner_label: str,
    ) -> None:
        for branch in branches:
            for field_name, bound_path in field_bindings.items():
                if field_name == "verdict":
                    if self._review_output_path_is_live(
                        output_decl,
                        path=bound_path,
                        unit=output_unit,
                        branch=branch,
                    ):
                        continue
                    raise CompileError(
                        "Review verdict field is not live for semantic verdict in "
                        f"{owner_label}: {output_decl.name}.{'.'.join(bound_path)}"
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
                        raise CompileError(
                            "Review conditional output field is not aligned with resolved review semantics "
                            f"in {owner_label}: next_owner -> {output_decl.name}.{'.'.join(bound_path)}"
                        )
                    if not self._review_output_path_is_live(
                        output_decl,
                        path=bound_path,
                        unit=output_unit,
                        branch=branch,
                    ):
                        raise CompileError(
                            "Review next_owner field is not live for routed target in "
                            f"{owner_label}: {output_decl.name}.{'.'.join(bound_path)} -> "
                            f"{route.target.declaration_name}"
                        )
                    self._validate_review_next_owner_binding(
                        route,
                        review_unit=review_unit,
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
                    raise CompileError(
                        "Review conditional output field is not aligned with resolved review semantics "
                        f"in {owner_label}: {field_name} -> {output_decl.name}.{'.'.join(bound_path)}"
                    )
                if not semantic_present and field_live:
                    raise CompileError(
                        "Review conditional output field is not aligned with resolved review semantics "
                        f"in {owner_label}: {field_name} -> {output_decl.name}.{'.'.join(bound_path)}"
                    )
