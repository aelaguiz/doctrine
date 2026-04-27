from __future__ import annotations

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.indexing import unit_declarations
from doctrine._compiler.package_diagnostics import package_compile_error
from doctrine._compiler.resolved_types import CompileError, IndexedUnit


_RECEIPT_BUILTIN_TYPES: frozenset[str] = frozenset(
    {"string", "integer", "number", "boolean"}
)


class ResolveReceiptsMixin:
    """Top-level receipt resolution helpers for ResolveMixin.

    A `receipt` declaration is the typed handoff fact a skill package or graph
    stage shares. Resolution follows the explicit `inherit`/`override` patching
    model used by `output`, `workflow`, and `document`. After resolution, the
    receipt carries a deterministic ordered field tuple where each field type
    falls into a closed family: builtin scalar, declared receipt, schema,
    table, or enum.
    """

    def _resolve_receipt_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.ReceiptDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="receipts_by_name",
            missing_label="receipt declaration",
        )

    def _resolve_parent_receipt_decl(
        self,
        receipt_decl: model.ReceiptDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.ReceiptDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=receipt_decl.name,
            child_label="receipt",
            parent_ref=receipt_decl.parent_ref,
            registry_name="receipts_by_name",
            resolve_parent_ref=self._resolve_receipt_ref,
        )

    def _resolved_receipt_cache(self) -> dict[tuple[int, str], model.ResolvedReceipt]:
        cache = getattr(self, "_resolved_receipt_decl_cache", None)
        if cache is None:
            cache = {}
            object.__setattr__(self, "_resolved_receipt_decl_cache", cache)
        return cache

    def _resolved_receipt_stack(self) -> list[tuple[int, str]]:
        stack = getattr(self, "_resolved_receipt_decl_stack", None)
        if stack is None:
            stack = []
            object.__setattr__(self, "_resolved_receipt_decl_stack", stack)
        return stack

    def _resolve_resolved_receipt(
        self,
        receipt_decl: model.ReceiptDecl,
        *,
        unit: IndexedUnit,
    ) -> model.ResolvedReceipt:
        cache_key = (id(unit), receipt_decl.name)
        cache = self._resolved_receipt_cache()
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        stack = self._resolved_receipt_stack()
        if cache_key in stack:
            owner_label = self._receipt_owner_label(receipt_decl, unit=unit)
            raise package_compile_error(
                code="E544",
                summary="Invalid receipt declaration",
                detail=(
                    f"Receipt `{owner_label}` is part of a receipt inheritance "
                    "or field-type cycle."
                ),
                path=unit.prompt_file.source_path,
                source_span=receipt_decl.source_span,
                hints=(
                    "Break the cycle so the receipt can resolve in a finite chain.",
                ),
            )
        stack.append(cache_key)
        try:
            resolved_fields = self._merge_resolved_receipt_fields(
                receipt_decl, unit=unit
            )
            resolved_routes = self._lower_resolved_receipt_routes(
                receipt_decl, unit=unit
            )
            resolved = model.ResolvedReceipt(
                canonical_name=receipt_decl.name,
                title=receipt_decl.title,
                module_parts=unit.module_parts,
                fields=resolved_fields,
                routes=resolved_routes,
                source_span=receipt_decl.source_span,
            )
            cache[cache_key] = resolved
            return resolved
        finally:
            stack.pop()

    def _merge_resolved_receipt_fields(
        self,
        receipt_decl: model.ReceiptDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[model.ResolvedReceiptField, ...]:
        owner_label = self._receipt_owner_label(receipt_decl, unit=unit)
        parent_fields_by_key: dict[str, model.ResolvedReceiptField] = {}
        if receipt_decl.parent_ref is not None:
            parent_unit, parent_decl = self._resolve_parent_receipt_decl(
                receipt_decl, unit=unit
            )
            parent_resolved = self._resolve_resolved_receipt(
                parent_decl, unit=parent_unit
            )
            parent_fields_by_key = {
                field.key: field for field in parent_resolved.fields
            }
        else:
            for item in receipt_decl.items:
                if isinstance(item, model.InheritItem):
                    raise package_compile_error(
                        code="E544",
                        summary="Invalid receipt declaration",
                        detail=(
                            f"Receipt `{owner_label}` uses `inherit {item.key}` "
                            "but declares no parent receipt."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=item.source_span or receipt_decl.source_span,
                        hints=(
                            "Add a `[ParentReceipt]` clause to the receipt head, "
                            "or drop the `inherit` line.",
                        ),
                    )
                if isinstance(item, model.ReceiptDeclOverride):
                    raise package_compile_error(
                        code="E544",
                        summary="Invalid receipt declaration",
                        detail=(
                            f"Receipt `{owner_label}` uses `override {item.key}` "
                            "but declares no parent receipt."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=item.source_span or receipt_decl.source_span,
                        hints=(
                            "Add a `[ParentReceipt]` clause to the receipt head, "
                            "or rewrite this line as a normal field.",
                        ),
                    )

        emitted_keys: set[str] = set()
        accounted_parent_keys: set[str] = set()
        merged: list[model.ResolvedReceiptField] = []

        for item in receipt_decl.items:
            if isinstance(item, model.InheritItem):
                parent_field = parent_fields_by_key.get(item.key)
                if parent_field is None:
                    raise package_compile_error(
                        code="E544",
                        summary="Invalid receipt declaration",
                        detail=(
                            f"Receipt `{owner_label}` cannot inherit undefined "
                            f"parent field `{item.key}`."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=item.source_span or receipt_decl.source_span,
                        hints=(
                            "Inherit only fields that the parent receipt declares.",
                        ),
                    )
                self._raise_if_duplicate_field(
                    item.key,
                    emitted_keys=emitted_keys,
                    decl=receipt_decl,
                    item=item,
                    unit=unit,
                    owner_label=owner_label,
                )
                emitted_keys.add(item.key)
                accounted_parent_keys.add(item.key)
                merged.append(parent_field)
                continue
            if isinstance(item, model.ReceiptDeclOverride):
                if item.key not in parent_fields_by_key:
                    raise package_compile_error(
                        code="E544",
                        summary="Invalid receipt declaration",
                        detail=(
                            f"Receipt `{owner_label}` cannot override undefined "
                            f"parent field `{item.key}`."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=item.source_span or receipt_decl.source_span,
                        hints=(
                            "Override only fields that the parent receipt declares.",
                        ),
                    )
                self._raise_if_duplicate_field(
                    item.key,
                    emitted_keys=emitted_keys,
                    decl=receipt_decl,
                    item=item,
                    unit=unit,
                    owner_label=owner_label,
                )
                replacement_field = model.ReceiptDeclField(
                    key=item.key,
                    type_ref=item.type_ref,
                    list_element=item.list_element,
                    source_span=item.source_span,
                )
                resolved_field = self._lower_receipt_field(
                    replacement_field, decl=receipt_decl, unit=unit
                )
                emitted_keys.add(item.key)
                accounted_parent_keys.add(item.key)
                merged.append(resolved_field)
                continue
            if isinstance(item, model.ReceiptDeclField):
                if item.key in parent_fields_by_key:
                    raise package_compile_error(
                        code="E544",
                        summary="Invalid receipt declaration",
                        detail=(
                            f"Receipt `{owner_label}` redeclares inherited field "
                            f"`{item.key}` without `inherit` or `override`."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=item.source_span or receipt_decl.source_span,
                        hints=(
                            "Account for inherited fields with `inherit "
                            f"{item.key}` or `override {item.key}: <Type>`.",
                        ),
                    )
                self._raise_if_duplicate_field(
                    item.key,
                    emitted_keys=emitted_keys,
                    decl=receipt_decl,
                    item=item,
                    unit=unit,
                    owner_label=owner_label,
                )
                resolved_field = self._lower_receipt_field(
                    item, decl=receipt_decl, unit=unit
                )
                emitted_keys.add(item.key)
                merged.append(resolved_field)
                continue

        missing_keys = tuple(
            key for key in parent_fields_by_key if key not in accounted_parent_keys
        )
        if missing_keys:
            raise package_compile_error(
                code="E544",
                summary="Invalid receipt declaration",
                detail=(
                    f"Receipt `{owner_label}` is missing inherited fields: "
                    f"{', '.join(missing_keys)}."
                ),
                path=unit.prompt_file.source_path,
                source_span=receipt_decl.source_span,
                hints=(
                    "Account for every inherited field with `inherit <key>` or "
                    "`override <key>: <Type>`.",
                ),
            )

        if not merged:
            raise package_compile_error(
                code="E544",
                summary="Invalid receipt declaration",
                detail=(
                    f"Receipt `{owner_label}` declares no typed fields. Receipts "
                    "must list at least one typed field."
                ),
                path=unit.prompt_file.source_path,
                source_span=receipt_decl.source_span,
                hints=(
                    "Add at least one `<field>: <Type>` line, or `inherit` "
                    "fields from a parent receipt.",
                ),
            )
        return tuple(merged)

    def _raise_if_duplicate_field(
        self,
        key: str,
        *,
        emitted_keys: set[str],
        decl: model.ReceiptDecl,
        item: object,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if key not in emitted_keys:
            return
        raise package_compile_error(
            code="E544",
            summary="Invalid receipt declaration",
            detail=(
                f"Receipt `{owner_label}` declares field `{key}` more than once."
            ),
            path=unit.prompt_file.source_path,
            source_span=getattr(item, "source_span", None) or decl.source_span,
            hints=("Use a unique key for each receipt field.",),
        )

    def _lower_receipt_field(
        self,
        field: model.ReceiptDeclField,
        *,
        decl: model.ReceiptDecl,
        unit: IndexedUnit,
    ) -> model.ResolvedReceiptField:
        type_ref = field.type_ref
        owner_label = self._receipt_owner_label(decl, unit=unit)
        type_name = (
            ".".join((*type_ref.module_parts, type_ref.declaration_name))
            if type_ref.module_parts
            else type_ref.declaration_name
        )
        if (
            not type_ref.module_parts
            and type_ref.declaration_name in _RECEIPT_BUILTIN_TYPES
        ):
            return model.ResolvedReceiptField(
                key=field.key,
                type_kind="builtin",
                type_name=type_ref.declaration_name,
                list_element=field.list_element,
                source_span=field.source_span,
            )

        lookup_targets = self._decl_lookup_targets(type_ref, unit=unit)
        for lookup_target in lookup_targets:
            target_decls = unit_declarations(lookup_target.unit)
            target_name = lookup_target.declaration_name
            if target_name in target_decls.receipts_by_name:
                nested_decl = target_decls.receipts_by_name[target_name]
                # Recurse so receipt-of-receipt cycles surface through the same
                # resolver stack and produce the E544 cycle diagnostic.
                self._resolve_resolved_receipt(nested_decl, unit=lookup_target.unit)
                return model.ResolvedReceiptField(
                    key=field.key,
                    type_kind="receipt",
                    type_name=target_name,
                    list_element=field.list_element,
                    source_span=field.source_span,
                )
            if target_name in target_decls.enums_by_name:
                return model.ResolvedReceiptField(
                    key=field.key,
                    type_kind="enum",
                    type_name=target_name,
                    list_element=field.list_element,
                    source_span=field.source_span,
                )
            if target_name in target_decls.tables_by_name:
                return model.ResolvedReceiptField(
                    key=field.key,
                    type_kind="table",
                    type_name=target_name,
                    list_element=field.list_element,
                    source_span=field.source_span,
                )
            if target_name in target_decls.schemas_by_name:
                return model.ResolvedReceiptField(
                    key=field.key,
                    type_kind="schema",
                    type_name=target_name,
                    list_element=field.list_element,
                    source_span=field.source_span,
                )

        raise package_compile_error(
            code="E544",
            summary="Invalid receipt declaration",
            detail=(
                f"Receipt `{owner_label}` field `{field.key}` has type "
                f"`{type_name}`, but that name does not resolve to a builtin "
                "scalar (string, integer, number, boolean), a declared "
                "`receipt`, `enum`, `table`, or `schema`."
            ),
            path=unit.prompt_file.source_path,
            source_span=field.source_span or decl.source_span,
            hints=(
                "Receipt field types must be a builtin scalar or a declared "
                "receipt, enum, table, or schema in scope.",
            ),
        )

    def _receipt_owner_label(
        self,
        decl: model.ReceiptDecl,
        *,
        unit: IndexedUnit,
    ) -> str:
        if unit.module_parts:
            return ".".join((*unit.module_parts, decl.name))
        return decl.name

    # Receipt route fields ------------------------------------------------

    def _lower_resolved_receipt_routes(
        self,
        receipt_decl: model.ReceiptDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[model.ResolvedReceiptRouteField, ...]:
        owner_label = self._receipt_owner_label(receipt_decl, unit=unit)
        seen_route_keys: set[str] = set()
        routes: list[model.ResolvedReceiptRouteField] = []
        for item in receipt_decl.items:
            if not isinstance(item, model.ReceiptDeclRouteField):
                continue
            if item.key in seen_route_keys:
                raise package_compile_error(
                    code="E544",
                    summary="Invalid receipt declaration",
                    detail=(
                        f"Receipt `{owner_label}` declares route field "
                        f"`{item.key}` more than once."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=item.source_span or receipt_decl.source_span,
                    hints=("Use a unique key for each receipt route field.",),
                )
            seen_route_keys.add(item.key)
            seen_choice_keys: set[str] = set()
            resolved_choices: list[model.ResolvedReceiptRouteChoice] = []
            for choice in item.choices:
                if choice.key in seen_choice_keys:
                    raise package_compile_error(
                        code="E544",
                        summary="Invalid receipt declaration",
                        detail=(
                            f"Receipt `{owner_label}` route field "
                            f"`{item.key}` declares choice `{choice.key}` "
                            "more than once."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=choice.source_span or item.source_span,
                        hints=(
                            "Use a unique key for each route choice.",
                        ),
                    )
                seen_choice_keys.add(choice.key)
                (
                    target_kind,
                    target_name,
                    target_module_parts,
                ) = self._resolve_receipt_route_target(
                    choice.target,
                    receipt_decl=receipt_decl,
                    route_field=item,
                    choice=choice,
                    unit=unit,
                    owner_label=owner_label,
                )
                resolved_choices.append(
                    model.ResolvedReceiptRouteChoice(
                        key=choice.key,
                        title=choice.title,
                        target_kind=target_kind,
                        target_name=target_name,
                        target_module_parts=target_module_parts,
                        source_span=choice.source_span,
                    )
                )
            routes.append(
                model.ResolvedReceiptRouteField(
                    key=item.key,
                    title=item.title,
                    choices=tuple(resolved_choices),
                    source_span=item.source_span,
                )
            )
        return tuple(routes)

    def _resolve_receipt_route_target(
        self,
        target: model.ReceiptRouteTarget,
        *,
        receipt_decl: model.ReceiptDecl,
        route_field: model.ReceiptDeclRouteField,
        choice: model.ReceiptRouteChoice,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[str, str, tuple[str, ...]]:
        if isinstance(target, model.ReceiptRouteSentinelTarget):
            return ("sentinel", target.sentinel, ())
        if isinstance(target, model.ReceiptRouteStageTarget):
            try:
                stage_unit, stage_decl = self._resolve_decl_ref(
                    target.stage_ref,
                    unit=unit,
                    registry_name="stages_by_name",
                    missing_label="stage declaration",
                )
            except CompileError as exc:
                ref = target.stage_ref
                dotted = (
                    ".".join((*ref.module_parts, ref.declaration_name))
                    if ref.module_parts
                    else ref.declaration_name
                )
                raise package_compile_error(
                    code="E560",
                    summary="Receipt route target is invalid",
                    detail=(
                        f"Receipt `{owner_label}` route field `{route_field.key}` "
                        f"choice `{choice.key}` points at stage `{dotted}`, but "
                        "no top-level `stage` declaration with that name is in scope."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=ref.source_span or choice.source_span,
                    hints=(
                        "Declare `stage <Name>: \"<Title>\"` at the top level, or "
                        "fix the stage ref to point at an existing declaration.",
                    ),
                ) from exc
            return ("stage", stage_decl.name, stage_unit.module_parts)
        if isinstance(target, model.ReceiptRouteFlowTarget):
            try:
                flow_unit, flow_decl = self._resolve_decl_ref(
                    target.flow_ref,
                    unit=unit,
                    registry_name="skill_flows_by_name",
                    missing_label="skill_flow declaration",
                )
            except CompileError as exc:
                ref = target.flow_ref
                dotted = (
                    ".".join((*ref.module_parts, ref.declaration_name))
                    if ref.module_parts
                    else ref.declaration_name
                )
                raise package_compile_error(
                    code="E560",
                    summary="Receipt route target is invalid",
                    detail=(
                        f"Receipt `{owner_label}` route field `{route_field.key}` "
                        f"choice `{choice.key}` points at flow `{dotted}`, but "
                        "no top-level `skill_flow` declaration with that name is "
                        "in scope."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=ref.source_span or choice.source_span,
                    hints=(
                        "Declare `skill_flow <Name>: \"<Title>\"` at the top "
                        "level, or fix the flow ref to point at an existing "
                        "declaration.",
                    ),
                ) from exc
            return ("flow", flow_decl.name, flow_unit.module_parts)
        raise compile_error(
            code="E901",
            summary="Internal compiler error",
            detail=(
                "Internal compiler error: unsupported receipt route target "
                f"type: {type(target).__name__}"
            ),
            path=unit.prompt_file.source_path,
            source_span=getattr(target, "source_span", None) or choice.source_span,
            hints=("This is a compiler bug, not a prompt authoring error.",),
        )
