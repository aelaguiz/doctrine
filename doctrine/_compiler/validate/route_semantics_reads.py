from __future__ import annotations

from doctrine._compiler.naming import _humanize_key
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


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
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> tuple[RouteSemanticBranch, ...]:
        if route_semantics is None:
            raise CompileError(
                f"Missing route semantics in {surface_label} {owner_label}: {ref_label}"
            )
        if route_semantics.has_unrouted_branch and not route_semantics.route_required:
            raise CompileError(
                "route semantics are not live on every branch in "
                f"{surface_label} {owner_label}: {ref_label}; guard the read with `route.exists`."
            )
        if not route_semantics.branches:
            raise CompileError(
                f"route semantics require a routed branch in {surface_label} {owner_label}: {ref_label}"
            )
        return route_semantics.branches

    def _unique_route_semantic_branch(
        self,
        branches: tuple[RouteSemanticBranch, ...],
        *,
        key_fn,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        detail_label: str,
    ) -> RouteSemanticBranch:
        unique_keys = {key_fn(branch) for branch in branches}
        if len(unique_keys) != 1:
            raise CompileError(
                f"Ambiguous {detail_label} in {surface_label} {owner_label}: {ref_label}"
            )
        return branches[0]

    def _unique_route_choice_member(
        self,
        branches: tuple[RouteSemanticBranch, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        detail_label: str,
    ) -> RouteChoiceMember:
        if not any(branch.choice_members for branch in branches):
            raise CompileError(
                f"Missing {detail_label} in {surface_label} {owner_label}: {ref_label}"
            )
        if not self._route_choice_branches_are_live(branches):
            raise CompileError(
                f"Ambiguous {detail_label} in {surface_label} {owner_label}: {ref_label}"
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
            raise CompileError(
                f"Ambiguous {detail_label} in {surface_label} {owner_label}: {ref_label}"
            )
        return members[0]
