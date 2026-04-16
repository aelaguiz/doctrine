from __future__ import annotations

from doctrine import model
from doctrine._compiler.naming import _humanize_key
from doctrine._compiler.resolved_types import (
    IndexedUnit,
    RouteChoiceMember,
    RouteSemanticBranch,
    RouteSemanticContext,
)
from doctrine._compiler.workflow_diagnostics import workflow_compile_error


class ValidateRouteSemanticsReadsMixin:
    """Route-semantic read helpers for ValidateMixin."""

    def _route_semantic_branch_title(self, branch: RouteSemanticBranch) -> str:
        return branch.target_title or _humanize_key(branch.target_name)

    def _route_semantic_branch_summary(self, branch: RouteSemanticBranch) -> str:
        return f"{branch.label} Next owner: {self._route_semantic_branch_title(branch)}."

    def _route_semantic_parts(
        self,
        ref: model.AddressableRef,
    ) -> tuple[str, ...] | None:
        parts = (*ref.root.module_parts, ref.root.declaration_name, *ref.path)
        if not parts or parts[0] != "route":
            return None
        return parts

    def _route_semantic_branches_for_read(
        self,
        route_semantics: RouteSemanticContext | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        source_span: model.SourceSpan | None,
    ) -> tuple[RouteSemanticBranch, ...]:
        if route_semantics is None:
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"Missing route semantics in {surface_label} {owner_label}: {ref_label}",
                unit=unit,
                source_span=source_span,
            )
        if route_semantics.has_unrouted_branch and not route_semantics.route_required:
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    "route semantics are not live on every branch in "
                    f"{surface_label} {owner_label}: {ref_label}; guard the read "
                    "with `route.exists`."
                ),
                unit=unit,
                source_span=source_span,
            )
        if not route_semantics.branches:
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"route semantics require a routed branch in {surface_label} "
                    f"{owner_label}: {ref_label}"
                ),
                unit=unit,
                source_span=source_span,
            )
        return route_semantics.branches

    def _unique_route_semantic_branch(
        self,
        branches: tuple[RouteSemanticBranch, ...],
        *,
        key_fn,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        detail_label: str,
        source_span: model.SourceSpan | None,
    ) -> RouteSemanticBranch:
        unique_keys = {key_fn(branch) for branch in branches}
        if len(unique_keys) != 1:
            code = "E347" if detail_label in {"route.label", "route.summary"} else "E299"
            summary = (
                "Route detail needs one selected branch"
                if code == "E347"
                else "Compile failure"
            )
            detail = (
                f"`{detail_label}` in {owner_label} needs one selected route branch, "
                f"but `{ref_label}` still sees more than one."
                if code == "E347"
                else f"Ambiguous {detail_label} in {surface_label} {owner_label}: {ref_label}"
            )
            raise workflow_compile_error(
                code=code,
                summary=summary,
                detail=detail,
                unit=unit,
                source_span=source_span,
            )
        return branches[0]

    def _unique_route_choice_member(
        self,
        branches: tuple[RouteSemanticBranch, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        detail_label: str,
        source_span: model.SourceSpan | None,
    ) -> RouteChoiceMember:
        if not any(branch.choice_members for branch in branches):
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"Missing {detail_label} in {surface_label} {owner_label}: {ref_label}",
                unit=unit,
                source_span=source_span,
            )
        if not self._route_choice_branches_are_live(branches):
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Ambiguous {detail_label} in {surface_label} {owner_label}: "
                    f"{ref_label}"
                ),
                unit=unit,
                source_span=source_span,
            )
        members: list[RouteChoiceMember] = []
        seen: set[tuple[tuple[str, ...], str, str, str]] = set()
        for branch in branches:
            for member in branch.choice_members:
                key = (
                    member.enum_module_parts,
                    member.enum_name,
                    member.member_key,
                    member.member_wire,
                )
                if key in seen:
                    continue
                seen.add(key)
                members.append(member)
        if len(members) != 1:
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Ambiguous {detail_label} in {surface_label} {owner_label}: "
                    f"{ref_label}"
                ),
                unit=unit,
                source_span=source_span,
            )
        return members[0]
