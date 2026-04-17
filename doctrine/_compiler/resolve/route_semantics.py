from __future__ import annotations

from doctrine import model
from doctrine._compiler.naming import _display_addressable_ref
from doctrine._compiler.resolved_types import (
    DisplayValue,
    IndexedUnit,
    RouteSemanticContext,
)
from doctrine._compiler.workflow_diagnostics import workflow_compile_error


class ResolveRouteSemanticsMixin:
    """Route-semantic read resolution helpers for ResolveMixin."""

    def _resolve_route_semantic_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        route_semantics: RouteSemanticContext | None,
    ) -> DisplayValue | None:
        parts = self._route_semantic_parts(ref)
        if route_semantics is None or parts is None:
            return None
        ref_label = _display_addressable_ref(ref)
        if parts == ("route",):
            return DisplayValue(text="Route", kind="title")
        if parts == ("route", "exists"):
            if route_semantics.route_required:
                return DisplayValue(text="true", kind="symbol")
            if route_semantics.branches and not route_semantics.has_unrouted_branch:
                return DisplayValue(text="true", kind="symbol")
            if not route_semantics.branches:
                return DisplayValue(text="false", kind="symbol")
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"route.exists is branch-dependent in {surface_label} "
                    f"{owner_label}: {ref_label}"
                ),
                unit=unit,
                source_span=ref.source_span,
            )

        branches = self._route_semantic_branches_for_read(
            route_semantics,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
            source_span=ref.source_span,
        )
        if parts[1] == "next_owner":
            unique_targets = {
                (branch.target_module_parts, branch.target_name)
                for branch in branches
            }
            if len(unique_targets) == 1:
                branch = branches[0]
                if len(parts) == 2:
                    return DisplayValue(
                        text=self._route_semantic_branch_title(branch),
                        kind="title",
                    )
                if len(parts) == 3 and parts[2] in {"name", "key"}:
                    return DisplayValue(text=branch.target_name, kind="symbol")
                if len(parts) == 3 and parts[2] == "title":
                    return DisplayValue(text=self._route_semantic_branch_title(branch), kind="title")
            if self._route_choice_branches_are_live(branches):
                if len(parts) == 2 or (len(parts) == 3 and parts[2] == "title"):
                    return DisplayValue(text="the selected route's next owner", kind="title")
                if len(parts) == 3 and parts[2] in {"name", "key"}:
                    return DisplayValue(text="the selected route's next owner key", kind="symbol")
            raise workflow_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Ambiguous route.next_owner in {surface_label} "
                    f"{owner_label}: {ref_label}"
                ),
                unit=unit,
                source_span=ref.source_span,
            )
        if parts[1] == "choice":
            member = self._unique_route_choice_member(
                branches,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ref_label=ref_label,
                detail_label="route.choice",
                source_span=ref.source_span,
            )
            if len(parts) == 2:
                return DisplayValue(text=member.member_title, kind="title")
            if len(parts) == 3 and parts[2] == "key":
                return DisplayValue(text=member.member_key, kind="symbol")
            if len(parts) == 3 and parts[2] == "title":
                return DisplayValue(text=member.member_title, kind="title")
            if len(parts) == 3 and parts[2] == "wire":
                return DisplayValue(text=member.member_wire, kind="symbol")
        if parts == ("route", "label"):
            branch = self._unique_route_semantic_branch(
                branches,
                key_fn=lambda item: item.label,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ref_label=ref_label,
                detail_label="route.label",
                source_span=ref.source_span,
            )
            return DisplayValue(text=branch.label, kind="title")
        if parts == ("route", "summary"):
            branch = self._unique_route_semantic_branch(
                branches,
                key_fn=lambda item: self._route_semantic_branch_summary(item),
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ref_label=ref_label,
                detail_label="route.summary",
                source_span=ref.source_span,
            )
            return DisplayValue(
                text=self._route_semantic_branch_summary(branch),
                kind="title",
            )
        raise workflow_compile_error(
            code="E299",
            summary="Compile failure",
            detail=(
                f"Unknown route semantic path on {surface_label} in {owner_label}: "
                f"{ref_label}"
            ),
            unit=unit,
            source_span=ref.source_span,
        )
