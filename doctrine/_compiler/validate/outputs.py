from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import (
    _INTERPOLATION_EXPR_RE,
    _INTERPOLATION_RE,
    _REVIEW_GUARD_FIELD_NAMES,
)
from doctrine._compiler.naming import (
    _display_addressable_ref,
    _dotted_ref_name,
    _name_ref_from_dotted_name,
)
from doctrine._compiler.resolved_types import (
    AddressableNode,
    CompileError,
    IndexedUnit,
    ReviewSemanticContext,
    RouteSemanticContext,
)


class ValidateOutputsMixin:
    """Output guard and interpolation validation helpers for ValidateMixin."""

    def _validate_output_guard_sections(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        self._validate_output_record_items(
            decl.items,
            decl=decl,
            unit=unit,
            owner_label=f"output {decl.name}",
            allow_review_semantics=allow_review_semantics,
            allow_route_semantics=allow_route_semantics,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )
        for item in decl.trust_surface:
            if item.when_expr is None:
                continue
            self._validate_output_guard_expr(
                item.when_expr,
                decl=decl,
                unit=unit,
                owner_label=f"output {decl.name}.trust_surface",
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
        self._validate_standalone_read_guard_contract(
            decl,
            unit=unit,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )

    def _validate_output_record_items(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        for item in items:
            if isinstance(item, (model.GuardedOutputSection, model.GuardedOutputScalar)):
                guarded_route_semantics = self._narrow_route_semantics(
                    route_semantics,
                    item.when_expr,
                    unit=unit,
                )
                self._validate_output_guard_expr(
                    item.when_expr,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
                nested_items = (
                    item.items if isinstance(item, model.GuardedOutputSection) else item.body
                )
                if nested_items is not None:
                    self._validate_output_record_items(
                        nested_items,
                        decl=decl,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        allow_review_semantics=allow_review_semantics,
                        allow_route_semantics=allow_route_semantics,
                        review_semantics=review_semantics,
                        route_semantics=guarded_route_semantics,
                    )
                continue
            if isinstance(item, model.RecordSection):
                self._validate_output_record_items(
                    item.items,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
                continue
            if isinstance(item, model.RecordScalar) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
                continue
            if isinstance(item, model.RecordRef) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )

    def _validate_output_guard_expr(
        self,
        expr: model.Expr,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        if isinstance(expr, model.ExprRef):
            self._validate_output_guard_ref(
                expr,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            return
        if isinstance(expr, model.ExprBinary):
            self._validate_output_guard_expr(
                expr.left,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            self._validate_output_guard_expr(
                expr.right,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            return
        if isinstance(expr, model.ExprCall):
            for arg in expr.args:
                self._validate_output_guard_expr(
                    arg,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
            return
        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._validate_output_guard_expr(
                    item,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )

    def _validate_output_guard_ref(
        self,
        ref: model.ExprRef,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        _ = decl
        if self._output_guard_ref_allowed(
            ref,
            unit=unit,
            allow_review_semantics=allow_review_semantics,
            allow_route_semantics=allow_route_semantics,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        ):
            return
        raise CompileError(
            f"Output guard reads disallowed source in {owner_label}: {'.'.join(ref.parts)}"
        )

    def _output_guard_ref_allowed(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        return (
            self._expr_ref_matches_input_decl(ref, unit=unit)
            or self._expr_ref_matches_enum_member(ref, unit=unit)
            or (
                allow_route_semantics
                and self._expr_ref_matches_route_semantic_ref(
                    ref,
                    route_semantics=route_semantics,
                )
            )
            or (
                allow_review_semantics
                and (
                    self._expr_ref_matches_review_field(ref)
                    or self._expr_ref_matches_review_semantic_ref(
                        ref,
                        review_semantics=review_semantics,
                    )
                    or self._expr_ref_matches_review_verdict(ref)
                )
            )
        )

    def _validate_standalone_read_guard_contract(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        for path, item in self._iter_output_items_with_paths(decl.items):
            if not path or path[-1] != "standalone_read":
                continue
            owner_label = f"output {decl.name}.{'.'.join(path)}"
            for ref in self._iter_record_item_interpolation_refs(item):
                if self._interpolation_ref_enters_guarded_output_detail(
                    ref,
                    unit=unit,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                ):
                    raise CompileError(
                        "standalone_read cannot interpolate guarded output detail "
                        f"in {owner_label}: {_display_addressable_ref(ref)}"
                    )

    def _iter_output_items_with_paths(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        prefix: tuple[str, ...] = (),
    ) -> tuple[tuple[tuple[str, ...], model.AnyRecordItem], ...]:
        entries: list[tuple[tuple[str, ...], model.AnyRecordItem]] = []
        for item in items:
            if isinstance(item, model.RecordSection):
                path = (*prefix, item.key)
                entries.append((path, item))
                entries.extend(self._iter_output_items_with_paths(item.items, prefix=path))
                continue
            if isinstance(item, model.GuardedOutputSection):
                path = (*prefix, item.key)
                entries.append((path, item))
                entries.extend(self._iter_output_items_with_paths(item.items, prefix=path))
                continue
            if isinstance(item, model.GuardedOutputScalar):
                path = (*prefix, item.key)
                entries.append((path, item))
                if item.body is not None:
                    entries.extend(self._iter_output_items_with_paths(item.body, prefix=path))
                continue
            if isinstance(item, model.RecordScalar):
                path = (*prefix, item.key)
                entries.append((path, item))
                if item.body is not None:
                    entries.extend(self._iter_output_items_with_paths(item.body, prefix=path))
                continue
            if isinstance(item, model.RecordRef) and item.body is not None:
                entries.extend(self._iter_output_items_with_paths(item.body, prefix=prefix))
        return tuple(entries)

    def _iter_record_item_interpolation_refs(
        self,
        item: model.AnyRecordItem,
    ) -> tuple[model.AddressableRef, ...]:
        if isinstance(item, model.GuardedOutputScalar):
            refs = self._interpolation_refs_from_scalar_value(item.value)
            if item.body is not None:
                refs = (*refs, *self._iter_record_body_interpolation_refs(item.body))
            return refs
        if isinstance(item, model.RecordScalar):
            refs = self._interpolation_refs_from_scalar_value(item.value)
            if item.body is not None:
                refs = (*refs, *self._iter_record_body_interpolation_refs(item.body))
            return refs
        if isinstance(item, (model.RecordSection, model.GuardedOutputSection)):
            return self._iter_record_body_interpolation_refs(item.items)
        if isinstance(item, model.RecordRef):
            refs: tuple[model.AddressableRef, ...] = (model.AddressableRef(root=item.ref, path=()),)
            if item.body is not None:
                refs = (*refs, *self._iter_record_body_interpolation_refs(item.body))
            return refs
        return ()

    def _iter_record_body_interpolation_refs(
        self,
        items: tuple[model.AnyRecordItem, ...],
    ) -> tuple[model.AddressableRef, ...]:
        refs: list[model.AddressableRef] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                refs.extend(self._interpolation_refs_from_prose_line(item))
                continue
            refs.extend(self._iter_record_item_interpolation_refs(item))
        return tuple(refs)

    def _interpolation_refs_from_prose_line(
        self,
        value: model.ProseLine,
    ) -> tuple[model.AddressableRef, ...]:
        text = value if isinstance(value, str) else value.text
        return self._interpolation_refs_from_text(text)

    def _interpolation_refs_from_scalar_value(
        self,
        value: model.RecordScalarValue,
    ) -> tuple[model.AddressableRef, ...]:
        if isinstance(value, str):
            return self._interpolation_refs_from_text(value)
        if isinstance(value, model.AddressableRef):
            return (value,)
        return ()

    def _interpolation_refs_from_text(
        self,
        text: str,
    ) -> tuple[model.AddressableRef, ...]:
        if "{{" not in text or "}}" not in text:
            return ()
        refs: list[model.AddressableRef] = []
        for match in _INTERPOLATION_RE.finditer(text):
            ref = self._parse_interpolation_expr_ref(match.group(1))
            if ref is not None:
                refs.append(ref)
        return tuple(refs)

    def _parse_interpolation_expr_ref(
        self,
        expression: str,
    ) -> model.AddressableRef | None:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            return None
        return model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )

    def _interpolation_ref_enters_guarded_output_detail(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        _ = route_semantics
        semantic_parts = self._review_semantic_addressable_parts(ref)
        if (
            review_semantics is not None
            and semantic_parts is not None
            and semantic_parts[0] == "fields"
        ):
            field_path = self._review_semantic_field_path(review_semantics, semantic_parts[1])
            if field_path is None:
                return False
            _output_unit, output_decl = self._resolve_review_semantic_output_decl(review_semantics)
            return self._output_path_has_guarded_detail(
                output_decl,
                path=(*field_path, *semantic_parts[2:]),
            )
        try:
            target_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="standalone_read interpolation ref",
                missing_local_label="standalone_read",
                review_semantics=review_semantics,
            )
        except CompileError:
            return False

        if not isinstance(root_decl, model.OutputDecl):
            return False

        current = AddressableNode(unit=target_unit, root_decl=root_decl, target=root_decl)
        for segment in ref.path:
            children = self._get_addressable_children(current)
            if children is None:
                return False
            current = children.get(segment)
            if current is None:
                return False
            if isinstance(current.target, (model.GuardedOutputSection, model.GuardedOutputScalar)):
                return True
        return False

    def _expr_ref_matches_input_decl(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        for split_at in range(len(ref.parts), 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            if not self._ref_exists_in_registry(root, unit=unit, registry_name="inputs_by_name"):
                continue
            _target_unit, _decl = self._resolve_input_decl(root, unit=unit)
            return True
        return False

    def _expr_ref_matches_output_decl(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        for split_at in range(len(ref.parts), 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            if not self._ref_exists_in_registry(root, unit=unit, registry_name="outputs_by_name"):
                continue
            _target_unit, _decl = self._resolve_output_decl(root, unit=unit)
            return True
        return False

    def _expr_ref_matches_review_field(self, ref: model.ExprRef) -> bool:
        return len(ref.parts) == 1 and ref.parts[0] in _REVIEW_GUARD_FIELD_NAMES
