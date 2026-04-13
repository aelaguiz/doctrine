from __future__ import annotations

from doctrine._compiler.naming import _humanize_key, _name_ref_from_dotted_name
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class ValidateDisplayMixin:
    """Display and scalar rendering helpers for ValidateMixin."""

    def _expr_ref_matches_route_semantic_ref(
        self,
        ref: model.ExprRef,
        *,
        route_semantics: RouteSemanticContext | None,
    ) -> bool:
        if route_semantics is None or not ref.parts or ref.parts[0] != "route":
            return False
        if len(ref.parts) == 2 and ref.parts[1] == "exists":
            return True
        if len(ref.parts) == 2 and ref.parts[1] in {"label", "summary", "next_owner"}:
            return True
        if len(ref.parts) == 2 and ref.parts[1] == "choice":
            return self._route_choice_is_live(route_semantics)
        if len(ref.parts) == 3 and ref.parts[1] == "choice" and ref.parts[2] in {
            "key",
            "title",
            "wire",
        }:
            return self._route_choice_is_live(route_semantics)
        return len(ref.parts) == 3 and ref.parts[1] == "next_owner" and ref.parts[2] in {
            "name",
            "key",
            "title",
        }

    def _expr_ref_matches_enum_member(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        if len(ref.parts) < 2:
            return False
        for split_at in range(len(ref.parts) - 1, 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            enum_decl = self._try_resolve_enum_decl(root, unit=unit)
            if enum_decl is None:
                continue
            remainder = ref.parts[split_at:]
            return len(remainder) == 1 and any(member.key == remainder[0] for member in enum_decl.members)
        return False

    def _config_spec_from_decl(
        self,
        decl: model.InputSourceDecl | model.OutputTargetDecl,
        *,
        owner_label: str,
    ) -> ConfigSpec:
        _scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            section_keys={"required", "optional"},
            owner_label=owner_label,
        )
        if extras:
            pass
        required_section = section_items.get("required")
        optional_section = section_items.get("optional")
        required_keys = (
            self._key_labels_from_section(required_section, owner_label=owner_label)
            if required_section is not None
            else {}
        )
        optional_keys = (
            self._key_labels_from_section(optional_section, owner_label=owner_label)
            if optional_section is not None
            else {}
        )
        return ConfigSpec(title=decl.title, required_keys=required_keys, optional_keys=optional_keys)

    def _key_labels_from_section(
        self,
        section: model.RecordSection,
        *,
        owner_label: str,
    ) -> dict[str, str]:
        labels: dict[str, str] = {}
        for item in section.items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(
                    f"Config key declarations must be simple titled scalars in {owner_label}"
                )
            if not isinstance(item.value, str):
                raise CompileError(
                    f"Config key declarations must use string labels in {owner_label}: {item.key}"
                )
            if item.key in labels:
                raise CompileError(f"Duplicate config key declaration in {owner_label}: {item.key}")
            labels[item.key] = item.value
        return labels

    def _display_output_shape(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, model.AddressableRef):
            raise CompileError(
                f"Output shape must stay typed: {owner_label or surface_label or 'output'}"
            )
        if value.module_parts:
            _target_unit, decl = self._resolve_output_shape_decl(value, unit=unit)
            return decl.title
        local_decl = unit.output_shapes_by_name.get(value.declaration_name)
        if local_decl is not None:
            return local_decl.title
        return _humanize_key(value.declaration_name)

    def _is_markdown_shape_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
    ) -> bool:
        markdown_shape_names = {"MarkdownDocument", "AgentOutputDocument"}
        if isinstance(value, model.AddressableRef):
            return False
        if isinstance(value, str):
            return value in markdown_shape_names
        if self._ref_exists_in_registry(value, unit=unit, registry_name="output_shapes_by_name"):
            shape_unit, shape_decl = self._resolve_output_shape_decl(value, unit=unit)
            kind_item = next(
                (
                    item
                    for item in shape_decl.items
                    if isinstance(item, model.RecordScalar)
                    and item.key == "kind"
                    and item.body is None
                ),
                None,
            )
            if kind_item is None:
                return shape_decl.name in markdown_shape_names
            return self._is_markdown_shape_value(kind_item.value, unit=shape_unit)
        return value.declaration_name in markdown_shape_names

    def _is_comment_shape_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
    ) -> bool:
        comment_shape_names = {"Comment", "CommentText"}
        if isinstance(value, model.AddressableRef):
            return False
        if isinstance(value, str):
            return value in comment_shape_names
        if self._ref_exists_in_registry(value, unit=unit, registry_name="output_shapes_by_name"):
            shape_unit, shape_decl = self._resolve_output_shape_decl(value, unit=unit)
            kind_item = next(
                (
                    item
                    for item in shape_decl.items
                    if isinstance(item, model.RecordScalar)
                    and item.key == "kind"
                    and item.body is None
                ),
                None,
            )
            if kind_item is None:
                return shape_decl.name in comment_shape_names
            return self._is_comment_shape_value(kind_item.value, unit=shape_unit)
        return value.declaration_name in comment_shape_names

    def _display_symbol_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        return self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            render_profile=render_profile,
        ).text

    def _format_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )
        if display.kind == "string_literal":
            return f"`{display.text}`"
        return display.text

    def _display_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        if isinstance(value, str):
            return DisplayValue(text=value, kind="string_literal")
        if isinstance(value, model.NameRef):
            if value.module_parts and value.module_parts[0] == "route":
                if owner_label is None or surface_label is None:
                    raise CompileError(
                        "Internal compiler error: route refs require an owner label and surface label"
                    )
                route_value = self._resolve_route_semantic_ref_value(
                    model.AddressableRef(root=value, path=()),
                    owner_label=owner_label,
                    surface_label=surface_label,
                    route_semantics=route_semantics,
                )
                if route_value is not None:
                    return route_value
            enum_decl = self._try_resolve_enum_decl(value, unit=unit)
            if enum_decl is not None:
                return DisplayValue(text=enum_decl.title, kind="title")
            return DisplayValue(text=self._display_ref(value, unit=unit), kind="symbol")
        if owner_label is None or surface_label is None:
            raise CompileError(
                "Internal compiler error: addressable refs require an owner label and surface label"
            )
        return self._resolve_addressable_ref_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=f"{surface_label} addressable ref",
            missing_local_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )

    def _value_to_symbol(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
        return display.text
