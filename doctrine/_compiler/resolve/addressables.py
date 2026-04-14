from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import _INTERPOLATION_EXPR_RE
from doctrine._compiler.naming import _display_addressable_ref, _dotted_ref_name, _name_ref_from_dotted_name
from doctrine._compiler.resolved_types import (
    AddressableNode,
    AddressableProjectionTarget,
    AddressableRootDecl,
    CompileError,
    DisplayValue,
    IndexedUnit,
    ReadableDecl,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)


class ResolveAddressablesMixin:
    """Addressable and interpolation resolution helpers for ResolveMixin."""

    def _resolve_authored_prose_interpolation_expr(
        self,
        expression: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            raise CompileError(
                f"Invalid interpolation in {owner_label}: {{{{{expression}}}}}"
            )

        ref = model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )
        return self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=ambiguous_label or f"{surface_label} interpolation ref",
            missing_local_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        ).text

    def _resolve_readable_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[IndexedUnit, ReadableDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_readable_decl_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    f"Abstract agent refs are not allowed in {surface_label}; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if target_unit.workflows_by_name.get(ref.declaration_name) is not None:
            raise CompileError(
                f"Workflow refs are not allowed in {surface_label}; "
                f"use `use` for workflow composition: {dotted_name}"
            )

        fallback_unit = self._review_semantic_fallback_lookup_unit(
            ref,
            unit=unit,
            review_semantics=review_semantics,
        )
        if fallback_unit is not None:
            fallback_matches = self._find_readable_decl_matches(
                ref.declaration_name,
                unit=fallback_unit,
            )
            if len(fallback_matches) == 1:
                decl = fallback_matches[0][1]
                if isinstance(decl, model.Agent) and decl.abstract:
                    raise CompileError(
                        f"Abstract agent refs are not allowed in {surface_label}; "
                        f"mention a concrete agent instead: {dotted_name}"
                    )
                return fallback_unit, decl
            if len(fallback_matches) > 1:
                labels = ", ".join(label for label, _decl in fallback_matches)
                raise CompileError(
                    f"Ambiguous {ambiguous_label} in {owner_label}: "
                    f"{dotted_name} matches {labels}"
                )
            if fallback_unit.workflows_by_name.get(ref.declaration_name) is not None:
                raise CompileError(
                    f"Workflow refs are not allowed in {surface_label}; "
                    f"use `use` for workflow composition: {dotted_name}"
                )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        ref_label = _display_addressable_ref(ref)
        route_value = self._resolve_route_semantic_ref_value(
            ref,
            owner_label=owner_label,
            surface_label=surface_label,
            route_semantics=route_semantics,
        )
        if route_value is not None:
            return route_value
        semantic_node = self._resolve_review_semantic_node(
            ref,
            review_semantics=review_semantics,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )
        if semantic_node is not None:
            return self._display_addressable_target_value(
                semantic_node,
                owner_label=owner_label,
                surface_label=surface_label,
                render_profile=render_profile,
            )
        if not ref.path:
            target_unit, decl = self._resolve_readable_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                missing_local_label=missing_local_label,
                review_semantics=review_semantics,
            )
            return self._display_addressable_target_value(
                AddressableNode(unit=target_unit, root_decl=decl, target=decl),
                owner_label=owner_label,
                surface_label=surface_label,
                render_profile=render_profile,
            )

        target_unit, decl = self._resolve_addressable_root_decl(
            ref.root,
            unit=unit,
            owner_label=owner_label,
            ambiguous_label=ambiguous_label,
            missing_local_label=missing_local_label,
            review_semantics=review_semantics,
        )
        return self._resolve_addressable_path_value(
            AddressableNode(unit=target_unit, root_decl=decl, target=decl),
            ref.path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
            render_profile=render_profile,
        )

    def _resolve_addressable_root_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[IndexedUnit, AddressableRootDecl]:
        semantic_root = self._resolve_review_semantic_root_decl(
            ref,
            review_semantics=review_semantics,
        )
        if semantic_root is not None and review_semantics is not None:
            output_unit, _output_decl = self._resolve_review_semantic_output_decl(review_semantics)
            return output_unit, semantic_root
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_addressable_root_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    "Abstract agent refs are not allowed in addressable paths; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        fallback_unit = self._review_semantic_fallback_lookup_unit(
            ref,
            unit=unit,
            review_semantics=review_semantics,
        )
        if fallback_unit is not None:
            fallback_matches = self._find_addressable_root_matches(
                ref.declaration_name,
                unit=fallback_unit,
            )
            if len(fallback_matches) == 1:
                decl = fallback_matches[0][1]
                if isinstance(decl, model.Agent) and decl.abstract:
                    raise CompileError(
                        "Abstract agent refs are not allowed in addressable paths; "
                        f"mention a concrete agent instead: {dotted_name}"
                    )
                return fallback_unit, decl
            if len(fallback_matches) > 1:
                labels = ", ".join(label for label, _decl in fallback_matches)
                raise CompileError(
                    f"Ambiguous {ambiguous_label} in {owner_label}: "
                    f"{dotted_name} matches {labels}"
                )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_path_value(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        current = self._resolve_addressable_path_node(
            start,
            path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

        return self._display_addressable_target_value(
            current,
            owner_label=owner_label,
            surface_label=surface_label,
            render_profile=render_profile,
        )

    def _resolve_addressable_path_node(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> AddressableNode:
        current = start

        for index, segment in enumerate(path):
            is_last = index == len(path) - 1
            if is_last:
                projection = self._resolve_addressable_projection(
                    current,
                    segment=segment,
                    owner_label=owner_label,
                    surface_label=surface_label,
                )
                if projection is not None:
                    return AddressableNode(
                        unit=current.unit,
                        root_decl=current.root_decl,
                        target=projection,
                    )
            if is_last and segment in {"name", "title", "key", "wire"}:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )

            children = self._get_addressable_children(current)
            if children is None:
                raise CompileError(
                    "Addressable path must stay addressable on "
                    f"{surface_label} in {owner_label}: {ref_label}"
                )
            next_node = children.get(segment)
            if next_node is None:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )
            current = next_node

        return current

    def _resolve_addressable_projection(
        self,
        node: AddressableNode,
        *,
        segment: str,
        owner_label: str,
        surface_label: str,
    ) -> AddressableProjectionTarget | None:
        target = node.target
        if segment == "title":
            title = self._display_addressable_title(
                node,
                owner_label=owner_label,
                surface_label=surface_label,
            )
            if title is not None:
                return AddressableProjectionTarget(text=title, kind="title")
            return None
        if isinstance(target, model.Agent):
            if segment in {"name", "key"}:
                return AddressableProjectionTarget(text=target.name, kind="symbol")
            return None
        if isinstance(target, model.EnumMember):
            if segment == "key":
                return AddressableProjectionTarget(text=target.key, kind="symbol")
            if segment == "wire":
                return AddressableProjectionTarget(text=target.value, kind="symbol")
            return None
        return None

    def _resolve_readable_decl_lookup_unit(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> IndexedUnit:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            return unit

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")
        return target_unit
