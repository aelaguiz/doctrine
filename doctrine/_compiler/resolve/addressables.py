from __future__ import annotations

from contextlib import contextmanager

from doctrine import model
from doctrine._compiler.constants import _INTERPOLATION_EXPR_RE
from doctrine._compiler.naming import (
    _display_addressable_ref,
    _dotted_ref_name,
    _name_ref_from_dotted_name,
    _parse_interpolated_addressable_ref,
)
from doctrine._compiler.reference_diagnostics import reference_compile_error
from doctrine._compiler.resolved_types import (
    AddressableNode,
    AddressableProjectionTarget,
    AddressableRootDecl,
    DisplayValue,
    IndexedUnit,
    ReadableDecl,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
    SkillPackageHostCompileContext,
)


class ResolveAddressablesMixin:
    """Addressable and interpolation resolution helpers for ResolveMixin."""

    @contextmanager
    def _with_skill_package_host_context(self, context: SkillPackageHostCompileContext):
        self._skill_package_host_context_stack.append(context)
        try:
            yield
        finally:
            self._skill_package_host_context_stack.pop()

    @contextmanager
    def _with_skill_package_artifact_context(
        self,
        *,
        path: str,
        kind: str,
        source: str | None = None,
    ):
        context = self._active_skill_package_host_context()
        if context is None:
            yield
            return
        prior_path = context.current_artifact_path
        prior_kind = context.current_artifact_kind
        prior_source = context.current_artifact_source
        context.current_artifact_path = path
        context.current_artifact_kind = kind
        context.current_artifact_source = source
        try:
            yield
        finally:
            context.current_artifact_path = prior_path
            context.current_artifact_kind = prior_kind
            context.current_artifact_source = prior_source

    def _active_skill_package_host_context(self) -> SkillPackageHostCompileContext | None:
        if not self._skill_package_host_context_stack:
            return None
        return self._skill_package_host_context_stack[-1]

    @contextmanager
    def _with_addressable_self_root(self, root_ref: model.NameRef):
        self._addressable_self_root_stack.append(root_ref)
        try:
            yield
        finally:
            self._addressable_self_root_stack.pop()

    def _local_addressable_self_root_ref(self, declaration_name: str) -> model.NameRef:
        return model.NameRef(module_parts=(), declaration_name=declaration_name)

    def _current_addressable_self_root_ref(self) -> model.NameRef | None:
        if not self._addressable_self_root_stack:
            return None
        return self._addressable_self_root_stack[-1]

    def _rebind_self_addressable_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> model.AddressableRef:
        if not ref.self_rooted:
            return ref

        current_root = self._current_addressable_self_root_ref()
        if current_root is None:
            raise reference_compile_error(
                code="E312",
                summary="self ref needs a declaration root",
                detail=(
                    f"`self:` needs a declaration-root addressable context in "
                    f"{surface_label} {owner_label}: {_display_addressable_ref(ref)}"
                ),
                unit=unit,
                source_span=ref.source_span,
                hints=("Use an explicit `Root:path` ref here.",),
            )

        return model.AddressableRef(
            root=model.NameRef(
                module_parts=current_root.module_parts,
                declaration_name=current_root.declaration_name,
                source_span=ref.source_span,
            ),
            path=ref.path,
            source_span=ref.source_span,
        )

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
        ref = _parse_interpolated_addressable_ref(expression)
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if ref is None and match is None:
            raise reference_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"Invalid interpolation in {owner_label}: {{{{{expression}}}}}",
                unit=unit,
                source_span=None,
            )

        if ref is None:
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
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name
        match_sets: list[tuple[object, tuple[tuple[str, ReadableDecl], ...]]] = []
        workflow_target = None
        for lookup_target in self._decl_lookup_targets(ref, unit=unit):
            matches = self._find_readable_decl_matches(
                lookup_target.declaration_name,
                unit=lookup_target.unit,
            )
            if matches:
                match_sets.append((lookup_target, matches))
                continue
            if (
                workflow_target is None
                and lookup_target.unit.workflows_by_name.get(lookup_target.declaration_name)
                is not None
            ):
                workflow_target = lookup_target

        if len(match_sets) == 1:
            lookup_target, matches = match_sets[0]
            target_unit = lookup_target.unit
            if len(matches) == 1:
                decl = matches[0][1]
                if isinstance(decl, model.Agent) and decl.abstract:
                    raise reference_compile_error(
                        code="E272",
                        summary="Abstract agent ref is not allowed here",
                        detail=(
                            f"Abstract agent refs are not allowed in {surface_label}; "
                            f"mention a concrete agent instead: {dotted_name}"
                        ),
                        unit=unit,
                        source_span=ref.source_span,
                        hints=("Mention a concrete agent instead of an abstract base agent.",),
                    )
                return target_unit, decl

            labels = ", ".join(label for label, _decl in matches)
            raise reference_compile_error(
                code="E270",
                summary="Ambiguous declaration reference",
                detail=(
                    f"Ambiguous {ambiguous_label} in {owner_label}: "
                    f"{dotted_name} matches {labels}"
                ),
                unit=unit,
                source_span=ref.source_span,
            )

        if len(match_sets) > 1:
            imported_target = next(
                (
                    lookup_target
                    for lookup_target, _matches in match_sets
                    if lookup_target.imported_symbol is not None
                ),
                None,
            )
            if imported_target is not None:
                local_decl = next(
                    (
                        matches[0][1]
                        for lookup_target, matches in match_sets
                        if lookup_target.imported_symbol is None and matches
                    ),
                    None,
                )
                self._raise_imported_symbol_ambiguity(
                    ref,
                    unit=unit,
                    binding=imported_target.imported_symbol,
                    detail=(
                        f"Readable ref `{ref.declaration_name}` in {surface_label} "
                        f"of {owner_label} matches both local and imported declarations."
                    ),
                    local_decl=local_decl,
                )

        if workflow_target is not None:
            raise reference_compile_error(
                code="E271",
                summary="Workflow ref is not allowed here",
                detail=(
                    f"Workflow refs are not allowed in {surface_label}; "
                    f"use `use` for workflow composition: {dotted_name}"
                ),
                unit=unit,
                source_span=ref.source_span,
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
                    raise reference_compile_error(
                        code="E272",
                        summary="Abstract agent ref is not allowed here",
                        detail=(
                            f"Abstract agent refs are not allowed in {surface_label}; "
                            f"mention a concrete agent instead: {dotted_name}"
                        ),
                        unit=unit,
                        source_span=ref.source_span,
                        hints=(
                            "Mention a concrete agent instead of an abstract base agent.",
                        ),
                    )
                return fallback_unit, decl
            if len(fallback_matches) > 1:
                labels = ", ".join(label for label, _decl in fallback_matches)
                raise reference_compile_error(
                    code="E270",
                    summary="Ambiguous declaration reference",
                    detail=(
                        f"Ambiguous {ambiguous_label} in {owner_label}: "
                        f"{dotted_name} matches {labels}"
                    ),
                    unit=unit,
                    source_span=ref.source_span,
                )
            if fallback_unit.workflows_by_name.get(ref.declaration_name) is not None:
                raise reference_compile_error(
                    code="E271",
                    summary="Workflow ref is not allowed here",
                    detail=(
                        f"Workflow refs are not allowed in {surface_label}; "
                        f"use `use` for workflow composition: {dotted_name}"
                    ),
                    unit=unit,
                    source_span=ref.source_span,
                )

        if ref.module_parts:
            raise reference_compile_error(
                code="E281",
                summary="Missing imported declaration",
                detail=f"Missing imported declaration: {dotted_name}",
                unit=unit,
                source_span=ref.source_span,
            )

        raise reference_compile_error(
            code="E276",
            summary="Missing local declaration reference",
            detail=(
                f"Missing local declaration ref in {missing_local_label} {owner_label}: "
                f"{ref.declaration_name}"
            ),
            unit=unit,
            source_span=ref.source_span,
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
        ref = self._rebind_self_addressable_ref(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
        host_value = self._resolve_skill_package_host_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
        if host_value is not None:
            return host_value
        ref_label = _display_addressable_ref(ref)
        route_value = self._resolve_route_semantic_ref_value(
            ref,
            unit=unit,
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
            source_span=ref.source_span,
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
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name
        match_sets: list[tuple[object, tuple[tuple[str, AddressableRootDecl], ...]]] = []
        for lookup_target in self._decl_lookup_targets(ref, unit=unit):
            matches = self._find_addressable_root_matches(
                lookup_target.declaration_name,
                unit=lookup_target.unit,
            )
            if matches:
                match_sets.append((lookup_target, matches))

        if len(match_sets) == 1:
            lookup_target, matches = match_sets[0]
            target_unit = lookup_target.unit
            if len(matches) == 1:
                decl = matches[0][1]
                if isinstance(decl, model.Agent) and decl.abstract:
                    raise reference_compile_error(
                        code="E272",
                        summary="Abstract agent ref is not allowed here",
                        detail=(
                            "Abstract agent refs are not allowed in addressable paths; "
                            f"mention a concrete agent instead: {dotted_name}"
                        ),
                        unit=unit,
                        source_span=ref.source_span,
                        hints=("Mention a concrete agent instead of an abstract base agent.",),
                    )
                return target_unit, decl

            labels = ", ".join(label for label, _decl in matches)
            raise reference_compile_error(
                code="E270",
                summary="Ambiguous declaration reference",
                detail=(
                    f"Ambiguous {ambiguous_label} in {owner_label}: "
                    f"{dotted_name} matches {labels}"
                ),
                unit=unit,
                source_span=ref.source_span,
            )

        if len(match_sets) > 1:
            imported_target = next(
                (
                    lookup_target
                    for lookup_target, _matches in match_sets
                    if lookup_target.imported_symbol is not None
                ),
                None,
            )
            if imported_target is not None:
                local_decl = next(
                    (
                        matches[0][1]
                        for lookup_target, matches in match_sets
                        if lookup_target.imported_symbol is None and matches
                    ),
                    None,
                )
                self._raise_imported_symbol_ambiguity(
                    ref,
                    unit=unit,
                    binding=imported_target.imported_symbol,
                    detail=(
                        f"Addressable ref `{ref.declaration_name}` in {owner_label} matches "
                        "both local and imported roots."
                    ),
                    local_decl=local_decl,
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
                    raise reference_compile_error(
                        code="E272",
                        summary="Abstract agent ref is not allowed here",
                        detail=(
                            "Abstract agent refs are not allowed in addressable paths; "
                            f"mention a concrete agent instead: {dotted_name}"
                        ),
                        unit=unit,
                        source_span=ref.source_span,
                        hints=(
                            "Mention a concrete agent instead of an abstract base agent.",
                        ),
                    )
                return fallback_unit, decl
            if len(fallback_matches) > 1:
                labels = ", ".join(label for label, _decl in fallback_matches)
                raise reference_compile_error(
                    code="E270",
                    summary="Ambiguous declaration reference",
                    detail=(
                        f"Ambiguous {ambiguous_label} in {owner_label}: "
                        f"{dotted_name} matches {labels}"
                    ),
                    unit=unit,
                    source_span=ref.source_span,
                )

        if ref.module_parts:
            raise reference_compile_error(
                code="E281",
                summary="Missing imported declaration",
                detail=f"Missing imported declaration: {dotted_name}",
                unit=unit,
                source_span=ref.source_span,
            )

        raise reference_compile_error(
            code="E276",
            summary="Missing local declaration reference",
            detail=(
                f"Missing local declaration ref in {missing_local_label} {owner_label}: "
                f"{ref.declaration_name}"
            ),
            unit=unit,
            source_span=ref.source_span,
        )

    def _resolve_addressable_path_value(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        source_span: model.SourceSpan | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        current = self._resolve_addressable_path_node(
            start,
            path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
            source_span=source_span,
        )

        return self._display_addressable_target_value(
            current,
            owner_label=owner_label,
            surface_label=surface_label,
            render_profile=render_profile,
        )

    def _resolve_skill_package_host_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> DisplayValue | None:
        root = ref.root
        if ref.self_rooted or root is None:
            return None
        if root.module_parts or root.declaration_name != "host":
            return None

        context = self._active_skill_package_host_context()
        if context is None:
            raise reference_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"`host:` refs are only available inside prompt-authored skill package "
                    f"artifacts in {surface_label} {owner_label}."
                ),
                unit=unit,
                source_span=ref.source_span,
                hints=("Use `host:` only inside a compiled skill package prompt tree.",),
            )
        if not ref.path:
            raise reference_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"`host:` refs must include a slot key in {surface_label} {owner_label}.",
                unit=unit,
                source_span=ref.source_span,
                hints=("Use `host:slot_key` or `host:slot_key.path.to.child`.",),
            )

        slot_key, *tail = ref.path
        slot = context.host_slots_by_key.get(slot_key)
        if slot is None:
            raise reference_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Unknown `host:` slot in {surface_label} {owner_label}: {slot_key}"
                ),
                unit=unit,
                source_span=ref.source_span,
                hints=("Declare the slot in the package `host_contract:` block.",),
            )

        host_path = slot_key if not tail else f"{slot_key}.{'.'.join(tail)}"
        context.record_host_path(host_path)
        if not tail:
            return DisplayValue(text=slot.title, kind="title")
        return DisplayValue(text=f"{slot.title}:{'.'.join(tail)}", kind="symbol")

    def _resolve_addressable_path_node(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        source_span: model.SourceSpan | None = None,
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
                raise reference_compile_error(
                    code="E273",
                    summary="Unknown addressable path",
                    detail=(
                        f"Unknown addressable path on {surface_label} in {owner_label}: "
                        f"{ref_label}"
                    ),
                    unit=current.unit,
                    source_span=source_span,
                )

            children = self._get_addressable_children(current)
            if children is None:
                raise reference_compile_error(
                    code="E274",
                    summary="Addressable path must stay addressable",
                    detail=(
                        "Addressable path must stay addressable on "
                        f"{surface_label} in {owner_label}: {ref_label}"
                    ),
                    unit=current.unit,
                    source_span=source_span,
                )
            next_node = children.get(segment)
            if next_node is None:
                raise reference_compile_error(
                    code="E273",
                    summary="Unknown addressable path",
                    detail=(
                        f"Unknown addressable path on {surface_label} in {owner_label}: "
                        f"{ref_label}"
                    ),
                    unit=current.unit,
                    source_span=source_span,
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
        return self._resolve_visible_imported_unit(ref, unit=unit)
