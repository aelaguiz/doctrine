from __future__ import annotations

from dataclasses import replace

from doctrine import model
from doctrine._compiler.final_output_diagnostics import (
    final_output_compile_error,
    final_output_related_site,
)
from doctrine._compiler.resolved_types import (
    IndexedUnit,
    OutputSelectorDispatchContext,
)


class CompileOutputSelectorsMixin:
    """Output-shape selector dispatch helpers for CompilationContext."""

    def _build_output_selector_dispatch_context(
        self,
        *,
        shape_decl: model.OutputShapeDecl,
        shape_unit: IndexedUnit,
        selectors_field: model.SelectorsField | None,
        agent_name: str,
        agent_unit: IndexedUnit,
        final_output_field_span: model.SourceSpan | None,
    ) -> OutputSelectorDispatchContext | None:
        self._validate_output_shape_declaration_structure(shape_decl, unit=shape_unit)
        selector = shape_decl.selector
        if selector is None:
            if _shape_items_contain_case(shape_decl.items):
                raise final_output_compile_error(
                    code="E318",
                    summary="Output shape case without selector",
                    detail=(
                        f"Output shape `{shape_decl.name}` uses `case ...:` dispatch but "
                        "declares no `selector:` block."
                    ),
                    unit=shape_unit,
                    source_span=shape_decl.source_span,
                    hints=(
                        "Add `selector:` with one `mode <name> as <Enum>` entry to the output shape.",
                    ),
                )
            self._reject_unknown_selector_bindings(
                selectors_field=selectors_field,
                shape_decl=shape_decl,
                agent_name=agent_name,
                agent_unit=agent_unit,
            )
            return None

        resolved_selector_enum = self._try_resolve_enum_decl_with_unit(
            selector.enum_ref, unit=shape_unit
        )
        if resolved_selector_enum is None:
            raise final_output_compile_error(
                code="E318",
                summary="Output shape selector must resolve to a closed enum",
                detail=(
                    f"Output shape `{shape_decl.name}` selector `{selector.field_name}` must "
                    "point at a closed enum."
                ),
                unit=shape_unit,
                source_span=selector.source_span or shape_decl.source_span,
                hints=("Point `mode <name> as <Enum>` at a closed enum.",),
            )
        selector_enum_unit, selector_enum_decl = resolved_selector_enum
        selector_enum_identity = (
            selector_enum_unit.module_parts,
            selector_enum_decl.name,
        )

        expected_members = {member.key for member in selector_enum_decl.members}
        seen_members: dict[str, model.OutputRecordCase] = {}
        self._validate_output_shape_cases(
            shape_decl.items,
            shape_decl=shape_decl,
            shape_unit=shape_unit,
            enum_decl=selector_enum_decl,
            enum_identity=selector_enum_identity,
            seen_members=seen_members,
        )
        missing = expected_members - set(seen_members)
        if missing:
            raise final_output_compile_error(
                code="E318",
                summary="Output shape cases are not exhaustive",
                detail=(
                    f"Output shape `{shape_decl.name}` is missing cases for selector values: "
                    f"{', '.join(sorted(missing))}."
                ),
                unit=shape_unit,
                source_span=selector.source_span or shape_decl.source_span,
                hints=("Cover every enum member with a `case EnumType.member:` block.",),
            )

        self._reject_duplicate_selector_bindings(
            selectors_field=selectors_field,
            shape_decl=shape_decl,
            selector=selector,
            agent_name=agent_name,
            agent_unit=agent_unit,
            shape_unit=shape_unit,
        )
        self._reject_unknown_selector_bindings(
            selectors_field=selectors_field,
            shape_decl=shape_decl,
            expected_selector_name=selector.field_name,
            agent_name=agent_name,
            agent_unit=agent_unit,
            selector_source_span=selector.source_span or shape_decl.source_span,
            shape_unit=shape_unit,
        )

        bindings = selectors_field.bindings if selectors_field is not None else ()
        matched = next(
            (b for b in bindings if b.selector_name == selector.field_name),
            None,
        )
        if matched is None:
            raise final_output_compile_error(
                code="E319",
                summary="Agent missing selector binding for output shape",
                detail=(
                    f"Agent `{agent_name}` uses output shape `{shape_decl.name}`, which "
                    f"declares selector `{selector.field_name}`, but the agent does not bind "
                    f"it in `selectors:`."
                ),
                unit=agent_unit,
                source_span=(
                    selectors_field.source_span
                    if selectors_field is not None
                    else final_output_field_span
                ),
                related=(
                    final_output_related_site(
                        label=f"output shape `{shape_decl.name}` selector",
                        unit=shape_unit,
                        source_span=selector.source_span or shape_decl.source_span,
                    ),
                ),
                hints=(
                    f"Add `selectors:` with `{selector.field_name}: {selector_enum_decl.name}.<member>` "
                    "to the agent.",
                ),
            )

        binding_enum_identity = self._resolve_enum_member_ref_identity(
            matched.enum_member_ref,
            unit=agent_unit,
        )
        member_key = matched.enum_member_ref.declaration_name
        if (
            binding_enum_identity != selector_enum_identity
            or member_key not in expected_members
        ):
            raise final_output_compile_error(
                code="E319",
                summary="Agent selector binding does not match output shape selector",
                detail=(
                    f"Agent `{agent_name}` binds selector `{selector.field_name}` to "
                    f"`{'.'.join((*matched.enum_member_ref.module_parts, matched.enum_member_ref.declaration_name))}`, "
                    f"but output shape `{shape_decl.name}` expects a member of "
                    f"`{'.'.join((*selector_enum_identity[0], selector_enum_identity[1]))}`."
                ),
                unit=agent_unit,
                source_span=matched.source_span,
                related=(
                    final_output_related_site(
                        label=f"output shape `{shape_decl.name}` selector",
                        unit=shape_unit,
                        source_span=selector.source_span or shape_decl.source_span,
                    ),
                ),
                hints=(
                    f"Use `{selector.field_name}: {selector_enum_decl.name}.<member>` on the agent.",
                ),
            )

        return OutputSelectorDispatchContext(
            field_name=selector.field_name,
            enum_module_parts=tuple(selector.enum_ref.module_parts),
            enum_name=selector_enum_decl.name,
            bound_member_value=member_key,
        )

    def _resolve_enum_member_ref_identity(
        self,
        enum_member_ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ...], str] | None:
        if not enum_member_ref.module_parts:
            return None
        enum_ref = model.NameRef(
            module_parts=enum_member_ref.module_parts[:-1],
            declaration_name=enum_member_ref.module_parts[-1],
            rebound_imported=enum_member_ref.rebound_imported,
        )
        resolved = self._try_resolve_enum_decl_with_unit(enum_ref, unit=unit)
        if resolved is None:
            return None
        lookup_unit, decl = resolved
        return lookup_unit.module_parts, decl.name

    def _reject_duplicate_selector_bindings(
        self,
        *,
        selectors_field: model.SelectorsField | None,
        shape_decl: model.OutputShapeDecl,
        selector: model.OutputShapeSelectorConfig,
        agent_name: str,
        agent_unit: IndexedUnit,
        shape_unit: IndexedUnit,
    ) -> None:
        if selectors_field is None:
            return
        seen: dict[str, model.AgentSelectorBinding] = {}
        for binding in selectors_field.bindings:
            previous = seen.get(binding.selector_name)
            if previous is not None:
                raise final_output_compile_error(
                    code="E319",
                    summary="Duplicate selector binding",
                    detail=(
                        f"Agent `{agent_name}` binds selector `{binding.selector_name}` more "
                        f"than once in `selectors:`."
                    ),
                    unit=agent_unit,
                    source_span=binding.source_span,
                    related=(
                        final_output_related_site(
                            label=f"first `{binding.selector_name}` binding",
                            unit=agent_unit,
                            source_span=previous.source_span,
                        ),
                    ),
                    hints=(
                        f"Keep one `{binding.selector_name}: {selector_enum_hint(shape_decl, selector)}` entry.",
                    ),
                )
            seen[binding.selector_name] = binding

    def _reject_unknown_selector_bindings(
        self,
        *,
        selectors_field: model.SelectorsField | None,
        shape_decl: model.OutputShapeDecl,
        agent_name: str,
        agent_unit: IndexedUnit,
        expected_selector_name: str | None = None,
        selector_source_span: model.SourceSpan | None = None,
        shape_unit: IndexedUnit | None = None,
    ) -> None:
        if selectors_field is None:
            return
        for binding in selectors_field.bindings:
            if (
                expected_selector_name is not None
                and binding.selector_name == expected_selector_name
            ):
                continue
            if expected_selector_name is None:
                detail = (
                    f"Agent `{agent_name}` binds selector `{binding.selector_name}`, but "
                    f"output shape `{shape_decl.name}` declares no `selector:` block."
                )
                hints = (
                    "Remove the `selectors:` binding, or declare a `selector:` on the shape.",
                )
                related: tuple = ()
            else:
                detail = (
                    f"Agent `{agent_name}` binds unknown selector `{binding.selector_name}`; "
                    f"output shape `{shape_decl.name}` declares only `{expected_selector_name}`."
                )
                hints = (
                    f"Remove the `{binding.selector_name}:` entry, or rename it to "
                    f"`{expected_selector_name}:`.",
                )
                related = (
                    final_output_related_site(
                        label=f"output shape `{shape_decl.name}` selector",
                        unit=shape_unit or agent_unit,
                        source_span=selector_source_span,
                    ),
                ) if shape_unit is not None else ()
            raise final_output_compile_error(
                code="E319",
                summary="Unknown selector binding",
                detail=detail,
                unit=agent_unit,
                source_span=binding.source_span,
                related=related,
                hints=hints,
            )

    def _validate_output_shape_cases(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        shape_decl: model.OutputShapeDecl,
        shape_unit: IndexedUnit,
        enum_decl: model.EnumDecl,
        enum_identity: tuple[tuple[str, ...], str],
        seen_members: dict[str, model.OutputRecordCase],
    ) -> None:
        expected_members = {member.key for member in enum_decl.members}
        for item in items:
            if isinstance(item, model.OutputRecordCase):
                member_ref = item.enum_member_ref
                if not member_ref.module_parts:
                    raise final_output_compile_error(
                        code="E318",
                        summary="Output shape case must reference an enum member",
                        detail=(
                            f"Output shape `{shape_decl.name}` case `{member_ref.declaration_name}` "
                            f"must reference a member of `{enum_decl.name}`."
                        ),
                        unit=shape_unit,
                        source_span=item.source_span or shape_decl.source_span,
                        hints=("Use `case EnumType.member:` to select a member.",),
                    )
                member_key = member_ref.declaration_name
                case_enum_identity = self._resolve_enum_member_ref_identity(
                    member_ref,
                    unit=shape_unit,
                )
                if case_enum_identity != enum_identity or member_key not in expected_members:
                    case_path = ".".join(member_ref.module_parts + (member_ref.declaration_name,))
                    selector_path = ".".join((*enum_identity[0], enum_identity[1]))
                    raise final_output_compile_error(
                        code="E318",
                        summary="Output shape case does not match selector enum",
                        detail=(
                            f"Output shape `{shape_decl.name}` case `{case_path}` must select a "
                            f"member of `{selector_path}`."
                        ),
                        unit=shape_unit,
                        source_span=item.source_span or shape_decl.source_span,
                        hints=("Use members of the selector's enum in each `case ...:` block.",),
                    )
                previous = seen_members.get(member_key)
                if previous is not None:
                    raise final_output_compile_error(
                        code="E318",
                        summary="Output shape cases overlap on a selector value",
                        detail=(
                            f"Output shape `{shape_decl.name}` has overlapping cases for "
                            f"`{enum_decl.name}.{member_key}`."
                        ),
                        unit=shape_unit,
                        source_span=item.source_span or shape_decl.source_span,
                        related=(
                            final_output_related_site(
                                label=f"first case for `{enum_decl.name}.{member_key}`",
                                unit=shape_unit,
                                source_span=previous.source_span or shape_decl.source_span,
                            ),
                        ),
                        hints=("Keep each selector value in exactly one case.",),
                    )
                seen_members[member_key] = item
                self._validate_output_shape_cases(
                    item.items,
                    shape_decl=shape_decl,
                    shape_unit=shape_unit,
                    enum_decl=enum_decl,
                    enum_identity=enum_identity,
                    seen_members=seen_members,
                )
                continue
            nested = _nested_record_items(item)
            if nested:
                self._validate_output_shape_cases(
                    nested,
                    shape_decl=shape_decl,
                    shape_unit=shape_unit,
                    enum_decl=enum_decl,
                    enum_identity=enum_identity,
                    seen_members=seen_members,
                )

    def _apply_output_selector_dispatch(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        context: OutputSelectorDispatchContext | None,
    ) -> tuple[model.AnyRecordItem, ...]:
        if not _items_contain_case(items):
            return items
        return tuple(self._dispatch_record_items(items, context=context))

    def _dispatch_record_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        context: OutputSelectorDispatchContext | None,
    ) -> list[model.AnyRecordItem]:
        result: list[model.AnyRecordItem] = []
        for item in items:
            if isinstance(item, model.OutputRecordCase):
                if context is None:
                    continue
                if item.enum_member_ref.declaration_name == context.bound_member_value:
                    result.extend(
                        self._dispatch_record_items(item.items, context=context)
                    )
                continue
            rewritten = self._dispatch_nested_item(item, context=context)
            if rewritten is not None:
                result.append(rewritten)
        return result

    def _dispatch_nested_item(
        self,
        item: model.AnyRecordItem,
        *,
        context: OutputSelectorDispatchContext | None,
    ) -> model.AnyRecordItem | None:
        if isinstance(item, model.RecordSection):
            return replace(
                item,
                items=tuple(self._dispatch_record_items(item.items, context=context)),
            )
        if isinstance(item, model.GuardedOutputSection):
            return replace(
                item,
                items=tuple(self._dispatch_record_items(item.items, context=context)),
            )
        if isinstance(item, model.GuardedOutputScalar) and item.body is not None:
            return replace(
                item,
                body=tuple(self._dispatch_record_items(item.body, context=context)),
            )
        if isinstance(item, model.RecordScalar) and item.body is not None:
            return replace(
                item,
                body=tuple(self._dispatch_record_items(item.body, context=context)),
            )
        if isinstance(item, model.RecordRef) and item.body is not None:
            return replace(
                item,
                body=tuple(self._dispatch_record_items(item.body, context=context)),
            )
        return item


def selector_enum_hint(
    shape_decl: model.OutputShapeDecl,
    selector: model.OutputShapeSelectorConfig,
) -> str:
    _ = shape_decl
    if selector.enum_ref.module_parts:
        return ".".join((*selector.enum_ref.module_parts, selector.enum_ref.declaration_name)) + ".<member>"
    return f"{selector.enum_ref.declaration_name}.<member>"


def _shape_items_contain_case(items: tuple[model.AnyRecordItem, ...]) -> bool:
    return _items_contain_case(items)


def _items_contain_case(items: tuple[model.AnyRecordItem, ...]) -> bool:
    for item in items:
        if isinstance(item, model.OutputRecordCase):
            return True
        nested = _nested_record_items(item)
        if nested and _items_contain_case(nested):
            return True
    return False


def _nested_record_items(item: model.AnyRecordItem) -> tuple[model.AnyRecordItem, ...]:
    if isinstance(item, model.RecordSection):
        return item.items
    if isinstance(item, model.GuardedOutputSection):
        return item.items
    if isinstance(item, model.GuardedOutputScalar):
        return item.body or ()
    if isinstance(item, model.RecordScalar):
        return item.body or ()
    if isinstance(item, model.RecordRef):
        return item.body or ()
    return ()
