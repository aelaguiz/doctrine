from __future__ import annotations

from dataclasses import dataclass, replace

from doctrine import model
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.output_schema_diagnostics import (
    output_schema_compile_error,
    output_schema_related_site,
)
from doctrine._compiler.resolved_types import CompileError, IndexedUnit
from doctrine._compiler.support_files import _dotted_decl_name

_OUTPUT_SCHEMA_BUILTIN_TYPES = frozenset(
    {
        "array",
        "boolean",
        "integer",
        "null",
        "number",
        "object",
        "string",
    }
)
_OUTPUT_SCHEMA_JSON_KEY_MAP = {
    "min_length": "minLength",
    "max_length": "maxLength",
    "minimum": "minimum",
    "maximum": "maximum",
    "exclusive_minimum": "exclusiveMinimum",
    "exclusive_maximum": "exclusiveMaximum",
    "multiple_of": "multipleOf",
    "min_items": "minItems",
    "max_items": "maxItems",
}


@dataclass(slots=True)
class _OutputSchemaNodeParts:
    type_name: str | None = None
    type_source_span: model.SourceSpan | None = None
    note: str | None = None
    format_name: str | None = None
    pattern: str | None = None
    ref: model.NameRef | None = None
    items_value: model.NameRef | tuple[model.OutputSchemaBodyItem, ...] | None = None
    enum_values: tuple[model.OutputSchemaLiteralValue, ...] = ()
    legacy_enum_values: tuple[model.OutputSchemaLiteralValue, ...] = ()
    legacy_enum_source_span: model.SourceSpan | None = None
    inline_enum_values: tuple[model.OutputSchemaLiteralValue, ...] = ()
    inline_enum_source_span: model.SourceSpan | None = None
    any_of: tuple[model.OutputSchemaVariant, ...] = ()
    fields: tuple[model.OutputSchemaField | model.OutputSchemaRouteField, ...] = ()
    defs: tuple[model.OutputSchemaDef, ...] = ()
    route_choices: tuple[model.OutputSchemaRouteChoice, ...] = ()
    constraints: tuple[tuple[str, int | float], ...] = ()
    const_value: model.OutputSchemaLiteralValue | None = None
    has_const: bool = False
    nullable: bool = False


class ResolveOutputSchemasMixin:
    """Inherited output-schema resolution and lowering helpers."""

    def _authored_source_span(self, value: object | None) -> model.SourceSpan | None:
        return getattr(value, "source_span", None)

    def _output_schema_item_by_key(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        key: str,
    ) -> object | None:
        return next(
            (
                item
                for item in output_schema_decl.items
                if self._output_schema_item_key(item) == key
            ),
            None,
        )

    def _output_schema_missing_related_sites(
        self,
        *,
        parent_output_schema: model.OutputSchemaDecl,
        parent_unit: IndexedUnit | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None:
            return ()
        related = []
        for key in missing_keys:
            parent_item = self._output_schema_item_by_key(parent_output_schema, key)
            if parent_item is None:
                continue
            related.append(
                output_schema_related_site(
                    label=f"inherited `{key}` entry",
                    unit=parent_unit,
                    source_span=self._authored_source_span(parent_item),
                )
            )
        return tuple(related)

    def _resolve_output_schema_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputSchemaDecl]:
        target_unit, decl = self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_schemas_by_name",
            missing_label="output schema declaration",
        )
        return target_unit, self._resolve_output_schema_decl_body(decl, unit=target_unit)

    def _resolve_local_output_schema_decl(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> model.OutputSchemaDecl | None:
        decl = unit.output_schemas_by_name.get(declaration_name)
        if decl is None:
            return None
        return self._resolve_output_schema_decl_body(decl, unit=unit)

    def _resolve_output_schema_decl_body(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        unit: IndexedUnit,
    ) -> model.OutputSchemaDecl:
        output_schema_key = (unit.module_parts, output_schema_decl.name)
        cached = self._resolved_output_schema_cache.get(output_schema_key)
        if cached is not None:
            return cached

        if output_schema_key in self._output_schema_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._output_schema_resolution_stack, output_schema_key]
            )
            raise output_schema_compile_error(
                code="E299",
                summary="Cyclic output schema inheritance",
                detail=f"Cyclic output schema inheritance: {cycle}",
                unit=unit,
                source_span=output_schema_decl.source_span,
            )

        self._output_schema_resolution_stack.append(output_schema_key)
        try:
            owner_label = _dotted_decl_name(unit.module_parts, output_schema_decl.name)
            parent_output_schema: model.OutputSchemaDecl | None = None
            parent_label: str | None = None
            if output_schema_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_output_schema_decl(
                    output_schema_decl,
                    unit=unit,
                )
                parent_output_schema = self._resolve_output_schema_decl_body(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    "output schema "
                    + _dotted_decl_name(parent_unit.module_parts, parent_decl.name)
                )

            resolved = self._resolve_inherited_output_schema_decl(
                output_schema_decl,
                unit=unit,
                owner_label=owner_label,
                parent_unit=parent_unit if output_schema_decl.parent_ref is not None else None,
                parent_output_schema=parent_output_schema,
                parent_label=parent_label,
            )
            self._resolved_output_schema_cache[output_schema_key] = resolved
            return resolved
        finally:
            self._output_schema_resolution_stack.pop()

    def _resolve_inherited_output_schema_decl(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_unit: IndexedUnit | None = None,
        parent_output_schema: model.OutputSchemaDecl | None = None,
        parent_label: str | None = None,
    ) -> model.OutputSchemaDecl:
        if parent_output_schema is None:
            patch_key = self._first_output_schema_patch_key(output_schema_decl)
            if patch_key is not None:
                patch_item = self._output_schema_item_by_key(output_schema_decl, patch_key)
                raise output_schema_compile_error(
                    code="E299",
                    summary="Output schema patch requires an inherited output schema",
                    detail=(
                        f"inherit requires an inherited output schema in {owner_label}: {patch_key}"
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(patch_item)
                    or output_schema_decl.source_span,
                )
            override_key = self._first_output_schema_override_key(output_schema_decl)
            if override_key is not None:
                override_item = self._output_schema_item_by_key(output_schema_decl, override_key)
                raise output_schema_compile_error(
                    code="E299",
                    summary="Output schema patch requires an inherited output schema",
                    detail=(
                        "override requires an inherited output schema in "
                        f"{owner_label}: {override_key}"
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(override_item)
                    or output_schema_decl.source_span,
                )
            return replace(output_schema_decl, parent_ref=None)

        inherited_parent_output_schema = (
            parent_output_schema
            if parent_unit is None
            else self._rebind_inherited_output_schema_decl(
                parent_output_schema,
                parent_unit=parent_unit,
            )
        )

        parent_items_by_key = {
            item.key: item
            for item in inherited_parent_output_schema.items
            if isinstance(
                item,
                (
                    model.OutputSchemaField,
                    model.OutputSchemaRouteField,
                    model.OutputSchemaDef,
                    model.OutputSchemaExample,
                ),
            )
        }
        resolved_items: list[model.OutputSchemaAuthoredItem] = []
        emitted_items: dict[str, object] = {}
        accounted_keys: set[str] = set()

        for item in output_schema_decl.items:
            key = self._output_schema_item_key(item)
            if key is None:
                raise CompileError(
                    "Internal compiler error: unsupported output schema item in "
                    f"{owner_label}: {type(item).__name__}"
                )
            if key in emitted_items:
                raise output_schema_compile_error(
                    code="E299",
                    summary="Duplicate output schema item key",
                    detail=f"Duplicate output schema item key in {owner_label}: {key}",
                    unit=unit,
                    source_span=self._authored_source_span(item)
                    or output_schema_decl.source_span,
                    related=(
                        output_schema_related_site(
                            label=f"first `{key}` entry",
                            unit=unit,
                            source_span=self._authored_source_span(emitted_items[key]),
                        ),
                    ),
                )
            emitted_items[key] = item

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Cannot inherit undefined output schema entry",
                        detail=(
                            f"Cannot inherit undefined output schema entry in {parent_label}: {key}"
                        ),
                        unit=unit,
                        source_span=item.source_span or output_schema_decl.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if self._is_output_schema_override_item(item):
                if parent_item is None:
                    raise output_schema_compile_error(
                        code="E001",
                        summary="Cannot override undefined inherited entry",
                        detail=(
                            "E001 Cannot override undefined output schema entry in "
                            f"{parent_label}: {key}"
                        ),
                        unit=unit,
                        source_span=self._authored_source_span(item)
                        or output_schema_decl.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(
                    self._resolve_output_schema_override_item(
                        item,
                        unit=unit,
                        parent_item=parent_item,
                        parent_unit=parent_unit or unit,
                        owner_label=owner_label,
                    )
                )
                continue

            if parent_item is not None:
                raise output_schema_compile_error(
                    code="E299",
                    summary="Invalid output schema inheritance patch",
                    detail=(
                        f"Inherited output schema requires `override {key}` in {owner_label}"
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(item)
                    or output_schema_decl.source_span,
                    related=(
                        output_schema_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit or unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            resolved_items.append(item)

        missing_keys = [
            item.key
            for item in inherited_parent_output_schema.items
            if isinstance(
                item,
                (
                    model.OutputSchemaField,
                    model.OutputSchemaRouteField,
                    model.OutputSchemaDef,
                    model.OutputSchemaExample,
                ),
            )
            and item.key not in accounted_keys
        ]
        if missing_keys:
            raise output_schema_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=(
                    f"E003 Missing inherited output schema entry in {owner_label}: "
                    + ", ".join(missing_keys)
                ),
                unit=unit,
                source_span=output_schema_decl.source_span,
                related=self._output_schema_missing_related_sites(
                    parent_output_schema=inherited_parent_output_schema,
                    parent_unit=parent_unit,
                    missing_keys=tuple(missing_keys),
                ),
            )

        return model.OutputSchemaDecl(
            name=output_schema_decl.name,
            title=output_schema_decl.title,
            items=tuple(resolved_items),
            parent_ref=None,
        )

    def _first_output_schema_patch_key(
        self,
        output_schema_decl: model.OutputSchemaDecl,
    ) -> str | None:
        for item in output_schema_decl.items:
            if isinstance(item, model.InheritItem):
                return item.key
        return None

    def _first_output_schema_override_key(
        self,
        output_schema_decl: model.OutputSchemaDecl,
    ) -> str | None:
        for item in output_schema_decl.items:
            if self._is_output_schema_override_item(item):
                return item.key
        return None

    def _output_schema_item_key(self, item: object) -> str | None:
        if isinstance(
            item,
            (
                model.OutputSchemaField,
                model.OutputSchemaRouteField,
                model.OutputSchemaDef,
                model.OutputSchemaExample,
                model.InheritItem,
                model.OutputSchemaOverrideField,
                model.OutputSchemaOverrideRouteField,
                model.OutputSchemaOverrideDef,
                model.OutputSchemaOverrideExample,
            ),
        ):
            return item.key
        return None

    def _is_output_schema_override_item(self, item: object) -> bool:
        return isinstance(
            item,
            (
                model.OutputSchemaOverrideField,
                model.OutputSchemaOverrideRouteField,
                model.OutputSchemaOverrideDef,
                model.OutputSchemaOverrideExample,
            ),
        )

    def _resolve_output_schema_override_item(
        self,
        item: (
            model.OutputSchemaOverrideField
            | model.OutputSchemaOverrideRouteField
            | model.OutputSchemaOverrideDef
            | model.OutputSchemaOverrideExample
        ),
        *,
        unit: IndexedUnit,
        parent_item: (
            model.OutputSchemaField
            | model.OutputSchemaRouteField
            | model.OutputSchemaDef
            | model.OutputSchemaExample
        ),
        parent_unit: IndexedUnit,
        owner_label: str,
    ) -> (
        model.OutputSchemaField
        | model.OutputSchemaRouteField
        | model.OutputSchemaDef
        | model.OutputSchemaExample
    ):
        key = item.key
        if isinstance(item, model.OutputSchemaOverrideField):
            if not isinstance(parent_item, model.OutputSchemaField):
                raise output_schema_compile_error(
                    code="E299",
                    summary="Output schema override kind mismatch",
                    detail=(
                        f"Override kind mismatch for output schema entry in {owner_label}: {key}"
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_schema_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            return model.OutputSchemaField(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                items=item.items,
            )
        if isinstance(item, model.OutputSchemaOverrideRouteField):
            if not isinstance(parent_item, model.OutputSchemaRouteField):
                raise output_schema_compile_error(
                    code="E299",
                    summary="Output schema override kind mismatch",
                    detail=(
                        f"Override kind mismatch for output schema entry in {owner_label}: {key}"
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_schema_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            return model.OutputSchemaRouteField(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                items=item.items,
            )
        if isinstance(item, model.OutputSchemaOverrideDef):
            if not isinstance(parent_item, model.OutputSchemaDef):
                raise output_schema_compile_error(
                    code="E299",
                    summary="Output schema override kind mismatch",
                    detail=(
                        f"Override kind mismatch for output schema entry in {owner_label}: {key}"
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_schema_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            return model.OutputSchemaDef(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                items=item.items,
            )
        if not isinstance(parent_item, model.OutputSchemaExample):
            raise output_schema_compile_error(
                code="E299",
                summary="Output schema override kind mismatch",
                detail=(
                    f"Override kind mismatch for output schema entry in {owner_label}: {key}"
                ),
                unit=unit,
                source_span=item.source_span,
                related=(
                    output_schema_related_site(
                        label=f"inherited `{key}` entry",
                        unit=parent_unit,
                        source_span=self._authored_source_span(parent_item),
                    ),
                ),
            )
        return model.OutputSchemaExample(
            key=key,
            value=item.value,
        )

    def _rebind_inherited_output_schema_decl(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        parent_unit: IndexedUnit,
    ) -> model.OutputSchemaDecl:
        rebound_items = self._rebind_output_schema_authored_items(
            output_schema_decl.items,
            parent_unit=parent_unit,
            local_def_scopes=(),
        )
        return replace(
            output_schema_decl,
            items=rebound_items,
            parent_ref=None,
        )

    def _rebind_output_schema_authored_items(
        self,
        items: tuple[model.OutputSchemaAuthoredItem, ...],
        *,
        parent_unit: IndexedUnit,
        local_def_scopes: tuple[frozenset[str], ...],
    ) -> tuple[model.OutputSchemaAuthoredItem, ...]:
        local_defs = frozenset(
            item.key
            for item in items
            if isinstance(
                item,
                (
                    model.OutputSchemaDef,
                    model.OutputSchemaOverrideDef,
                ),
            )
        )
        scopes = (*local_def_scopes, local_defs)
        return tuple(
            self._rebind_output_schema_authored_item(
                item,
                parent_unit=parent_unit,
                local_def_scopes=scopes,
            )
            for item in items
        )

    def _rebind_output_schema_authored_item(
        self,
        item: model.OutputSchemaAuthoredItem,
        *,
        parent_unit: IndexedUnit,
        local_def_scopes: tuple[frozenset[str], ...],
    ) -> model.OutputSchemaAuthoredItem:
        if isinstance(item, model.InheritItem):
            return item
        if isinstance(item, model.OutputSchemaField):
            return model.OutputSchemaField(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_node_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaRouteField):
            return model.OutputSchemaRouteField(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_route_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaDef):
            return model.OutputSchemaDef(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_node_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaOverrideField):
            return model.OutputSchemaOverrideField(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_node_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaOverrideRouteField):
            return model.OutputSchemaOverrideRouteField(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_route_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaOverrideDef):
            return model.OutputSchemaOverrideDef(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_node_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        return item

    def _rebind_output_schema_node_items(
        self,
        items: tuple[model.OutputSchemaBodyItem, ...],
        *,
        parent_unit: IndexedUnit,
        local_def_scopes: tuple[frozenset[str], ...],
    ) -> tuple[model.OutputSchemaBodyItem, ...]:
        local_defs = frozenset(
            item.key for item in items if isinstance(item, model.OutputSchemaDef)
        )
        scopes = (*local_def_scopes, local_defs)
        return tuple(
            self._rebind_output_schema_body_item(
                item,
                parent_unit=parent_unit,
                local_def_scopes=scopes,
            )
            for item in items
        )

    def _rebind_output_schema_route_items(
        self,
        items: tuple[model.OutputSchemaRouteBodyItem, ...],
        *,
        parent_unit: IndexedUnit,
        local_def_scopes: tuple[frozenset[str], ...],
    ) -> tuple[model.OutputSchemaRouteBodyItem, ...]:
        rebound: list[model.OutputSchemaRouteBodyItem] = []
        for item in items:
            if isinstance(item, model.OutputSchemaRouteChoice):
                rebound.append(
                    model.OutputSchemaRouteChoice(
                        key=item.key,
                        title=item.title,
                        target_ref=self._rebind_output_schema_ref(
                            item.target_ref,
                            parent_unit=parent_unit,
                            local_def_scopes=local_def_scopes,
                        ),
                        source_span=item.source_span,
                    )
                )
                continue
            rebound.append(
                self._rebind_output_schema_body_item(
                    item,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                )
            )
        return tuple(rebound)

    def _rebind_output_schema_body_item(
        self,
        item: model.OutputSchemaBodyItem,
        *,
        parent_unit: IndexedUnit,
        local_def_scopes: tuple[frozenset[str], ...],
    ) -> model.OutputSchemaBodyItem:
        if isinstance(item, model.OutputSchemaSetting):
            if not isinstance(item.value, model.NameRef):
                return item
            if item.key not in {"ref"}:
                return item
            return model.OutputSchemaSetting(
                key=item.key,
                value=self._rebind_output_schema_ref(
                    item.value,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaItems):
            if isinstance(item.value, model.NameRef):
                return model.OutputSchemaItems(
                    value=self._rebind_output_schema_ref(
                        item.value,
                        parent_unit=parent_unit,
                        local_def_scopes=local_def_scopes,
                    ),
                    source_span=item.source_span,
                )
            return model.OutputSchemaItems(
                value=self._rebind_output_schema_node_items(
                    item.value,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaAnyOf):
            return model.OutputSchemaAnyOf(
                variants=tuple(
                    model.OutputSchemaVariant(
                        key=variant.key,
                        items=self._rebind_output_schema_node_items(
                            variant.items,
                            parent_unit=parent_unit,
                            local_def_scopes=local_def_scopes,
                        ),
                        source_span=variant.source_span,
                    )
                    for variant in item.variants
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaField):
            return model.OutputSchemaField(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_node_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaRouteField):
            return model.OutputSchemaRouteField(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_route_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        if isinstance(item, model.OutputSchemaDef):
            return model.OutputSchemaDef(
                key=item.key,
                title=item.title,
                items=self._rebind_output_schema_node_items(
                    item.items,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                ),
                source_span=item.source_span,
            )
        return item

    def _rebind_output_schema_ref(
        self,
        ref: model.NameRef,
        *,
        parent_unit: IndexedUnit,
        local_def_scopes: tuple[frozenset[str], ...],
    ) -> model.NameRef:
        if ref.module_parts:
            return ref
        if self._output_schema_ref_targets_local_def(ref.declaration_name, local_def_scopes):
            return ref
        if not self._inherited_output_ref_has_parent_decl(ref, parent_unit=parent_unit):
            return ref
        return model.NameRef(
            module_parts=parent_unit.module_parts,
            declaration_name=ref.declaration_name,
            source_span=ref.source_span,
        )

    def _output_schema_ref_targets_local_def(
        self,
        name: str,
        local_def_scopes: tuple[frozenset[str], ...],
    ) -> bool:
        return any(name in scope for scope in reversed(local_def_scopes))

    def _lower_output_schema_decl(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        unit: IndexedUnit,
        pointer: tuple[str, ...] = (),
    ) -> dict[str, object]:
        output_schema_key = (unit.module_parts, output_schema_decl.name)
        if not pointer:
            cached = self._lowered_output_schema_cache.get(output_schema_key)
            if cached is not None:
                return cached

        if output_schema_key in self._output_schema_lowering_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._output_schema_lowering_stack, output_schema_key]
            )
            raise output_schema_compile_error(
                code="E299",
                summary="Cyclic output schema lowering",
                detail=f"Cyclic output schema lowering: {cycle}",
                unit=unit,
                source_span=output_schema_decl.source_span,
            )

        self._output_schema_lowering_stack.append(output_schema_key)
        try:
            lowered = self._lower_output_schema_node(
                tuple(
                    item
                    for item in output_schema_decl.items
                    if not isinstance(item, model.OutputSchemaExample)
                ),
                unit=unit,
                owner_label=f"output schema {_dotted_decl_name(unit.module_parts, output_schema_decl.name)}",
                title=output_schema_decl.title,
                local_def_scopes=(),
                pointer=pointer,
                allow_nullable_flag=False,
            )
            if not pointer:
                self._lowered_output_schema_cache[output_schema_key] = lowered
            return lowered
        finally:
            self._output_schema_lowering_stack.pop()

    def _lower_output_schema_node(
        self,
        items: (
            tuple[model.OutputSchemaBodyItem, ...]
            | tuple[model.OutputSchemaRouteBodyItem, ...]
            | tuple[model.OutputSchemaAuthoredItem, ...]
        ),
        *,
        unit: IndexedUnit,
        owner_label: str,
        title: str | None,
        local_def_scopes: tuple[dict[str, tuple[str, ...]], ...],
        pointer: tuple[str, ...],
        allow_nullable_flag: bool,
    ) -> dict[str, object]:
        parts = self._collect_output_schema_node_parts(
            items,
            unit=unit,
            owner_label=owner_label,
        )
        # Normalize the two authored inline-enum forms onto one lowered string-enum path.
        self._normalize_output_schema_inline_enum(
            parts,
            unit=unit,
            owner_label=owner_label,
        )
        if not allow_nullable_flag and parts.nullable:
            raise CompileError(
                f"Output schema `nullable` is only valid on fields in {owner_label}"
            )

        schema: dict[str, object] = {}
        if title is not None:
            schema["title"] = title
        if parts.note is not None:
            schema["description"] = parts.note

        if parts.route_choices:
            if (
                parts.type_name is not None
                or parts.ref is not None
                or parts.items_value is not None
                or parts.enum_values
                or parts.legacy_enum_values
                or parts.inline_enum_values
                or parts.any_of
                or parts.fields
                or parts.defs
                or parts.has_const
                or parts.format_name is not None
                or parts.pattern is not None
                or parts.constraints
            ):
                raise CompileError(
                    f"Route field cannot be combined with another primary shape in {owner_label}"
                )
            schema["type"] = "string"
            schema["enum"] = [choice.key for choice in parts.route_choices]
            if parts.nullable:
                return self._wrap_nullable_output_schema(schema)
            return schema

        if parts.any_of:
            if (
                parts.type_name is not None
                or parts.ref is not None
                or parts.items_value is not None
                or parts.enum_values
                or parts.has_const
                or parts.fields
            ):
                raise CompileError(
                    f"Output schema `any_of` cannot be combined with another primary shape in {owner_label}"
                )
            if parts.format_name is not None or parts.pattern is not None or parts.constraints:
                raise CompileError(
                    f"Output schema `any_of` cannot carry direct string or numeric constraints in {owner_label}"
                )
            schema["anyOf"] = [
                self._lower_output_schema_node(
                    variant.items,
                    unit=unit,
                    owner_label=(
                        f"{owner_label}.{variant.key}" if variant.key is not None else owner_label
                    ),
                    title=variant.key,
                    local_def_scopes=local_def_scopes,
                    pointer=(*pointer, "anyOf", str(index)),
                    allow_nullable_flag=False,
                )
                for index, variant in enumerate(parts.any_of)
            ]
            if parts.defs:
                schema["$defs"] = self._lower_output_schema_defs(
                    parts.defs,
                    unit=unit,
                    owner_label=owner_label,
                    local_def_scopes=local_def_scopes,
                    pointer=pointer,
                )
            if parts.nullable:
                return self._wrap_nullable_output_schema(schema)
            return schema

        if parts.ref is not None:
            if (
                parts.type_name is not None
                or parts.items_value is not None
                or parts.enum_values
                or parts.has_const
                or parts.fields
                or parts.format_name is not None
                or parts.pattern is not None
                or parts.constraints
            ):
                raise CompileError(
                    f"Output schema `ref` cannot be combined with another primary shape in {owner_label}"
                )
            schema.update(
                self._lower_output_schema_ref_value(
                    parts.ref,
                    unit=unit,
                    owner_label=owner_label,
                    local_def_scopes=local_def_scopes,
                    pointer=pointer,
                )
            )
            if parts.defs:
                schema["$defs"] = self._lower_output_schema_defs(
                    parts.defs,
                    unit=unit,
                    owner_label=owner_label,
                    local_def_scopes=local_def_scopes,
                    pointer=pointer,
                )
            if parts.nullable:
                return self._wrap_nullable_output_schema(schema)
            return schema

        resolved_type = parts.type_name
        if resolved_type is None:
            if parts.items_value is not None:
                resolved_type = "array"
            elif parts.fields or parts.defs:
                resolved_type = "object"
            else:
                raise CompileError(f"Output schema entry is missing a type in {owner_label}")

        schema["type"] = resolved_type

        local_defs = {
            item.key: (*pointer, "$defs", item.key)
            for item in parts.defs
        }
        nested_scopes = (*local_def_scopes, local_defs) if local_defs else local_def_scopes

        if parts.defs:
            schema["$defs"] = self._lower_output_schema_defs(
                parts.defs,
                unit=unit,
                owner_label=owner_label,
                local_def_scopes=local_def_scopes,
                pointer=pointer,
            )

        if resolved_type == "object":
            if parts.items_value is not None:
                raise CompileError(f"Object output schema cannot declare `items` in {owner_label}")
            schema["additionalProperties"] = False
            properties: dict[str, object] = {}
            required: list[str] = []
            for field in parts.fields:
                properties[field.key] = self._lower_output_schema_field(
                    field,
                    unit=unit,
                    owner_label=f"{owner_label}.{field.key}",
                    local_def_scopes=nested_scopes,
                    pointer=(*pointer, "properties", field.key),
                )
                required.append(field.key)
            schema["properties"] = properties
            schema["required"] = required
        elif parts.fields:
            raise CompileError(
                f"Non-object output schema cannot declare nested fields in {owner_label}"
            )

        if resolved_type == "array":
            if parts.items_value is None:
                raise CompileError(f"Array output schema must declare `items` in {owner_label}")
            schema["items"] = self._lower_output_schema_items_value(
                parts.items_value,
                unit=unit,
                owner_label=owner_label,
                local_def_scopes=nested_scopes,
                pointer=(*pointer, "items"),
            )
        elif parts.items_value is not None:
            raise CompileError(f"Only array output schemas can declare `items` in {owner_label}")

        if parts.format_name is not None:
            schema["format"] = parts.format_name
        if parts.pattern is not None:
            schema["pattern"] = parts.pattern
        if parts.enum_values:
            schema["enum"] = list(parts.enum_values)
        if parts.has_const:
            schema["const"] = parts.const_value
        for key, value in parts.constraints:
            schema[_OUTPUT_SCHEMA_JSON_KEY_MAP[key]] = value

        if parts.nullable:
            return self._wrap_nullable_output_schema(schema)
        return schema

    def _lower_output_schema_defs(
        self,
        defs: tuple[model.OutputSchemaDef, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        local_def_scopes: tuple[dict[str, tuple[str, ...]], ...],
        pointer: tuple[str, ...],
    ) -> dict[str, object]:
        current_scope = {
            item.key: (*pointer, "$defs", item.key)
            for item in defs
        }
        nested_scopes = (*local_def_scopes, current_scope)
        lowered: dict[str, object] = {}
        for item in defs:
            lowered[item.key] = self._lower_output_schema_node(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.$defs.{item.key}",
                title=item.title,
                local_def_scopes=nested_scopes,
                pointer=current_scope[item.key],
                allow_nullable_flag=False,
            )
        return lowered

    def _lower_output_schema_field(
        self,
        field: model.OutputSchemaField | model.OutputSchemaRouteField,
        *,
        unit: IndexedUnit,
        owner_label: str,
        local_def_scopes: tuple[dict[str, tuple[str, ...]], ...],
        pointer: tuple[str, ...],
    ) -> dict[str, object]:
        return self._lower_output_schema_node(
            field.items,
            unit=unit,
            owner_label=owner_label,
            title=field.title,
            local_def_scopes=local_def_scopes,
            pointer=pointer,
            allow_nullable_flag=True,
        )

    def _lower_output_schema_ref_value(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        local_def_scopes: tuple[dict[str, tuple[str, ...]], ...],
        pointer: tuple[str, ...],
    ) -> dict[str, object]:
        for scope in reversed(local_def_scopes):
            target_path = scope.get(ref.declaration_name)
            if target_path is not None and not ref.module_parts:
                return {"$ref": self._output_schema_pointer_fragment(target_path)}
        if not ref.module_parts and ref.declaration_name in _OUTPUT_SCHEMA_BUILTIN_TYPES:
            return {"type": ref.declaration_name}
        if not self._ref_exists_in_registry(ref, unit=unit, registry_name="output_schemas_by_name"):
            raise output_schema_compile_error(
                code="E299",
                summary="Unknown output schema ref",
                detail=(
                    f"Unknown output schema ref in {owner_label}: {_dotted_ref_name(ref)}"
                ),
                unit=unit,
                source_span=ref.source_span,
            )
        target_unit, target_decl = self._resolve_output_schema_decl(ref, unit=unit)
        return self._lower_output_schema_decl(
            target_decl,
            unit=target_unit,
            pointer=pointer,
        )

    def _lower_output_schema_items_value(
        self,
        value: model.NameRef | tuple[model.OutputSchemaBodyItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        local_def_scopes: tuple[dict[str, tuple[str, ...]], ...],
        pointer: tuple[str, ...],
    ) -> dict[str, object]:
        if isinstance(value, model.NameRef):
            return self._lower_output_schema_ref_value(
                value,
                unit=unit,
                owner_label=f"{owner_label}.items",
                local_def_scopes=local_def_scopes,
                pointer=pointer,
            )
        return self._lower_output_schema_node(
            value,
            unit=unit,
            owner_label=f"{owner_label}.items",
            title=None,
            local_def_scopes=local_def_scopes,
            pointer=pointer,
            allow_nullable_flag=False,
        )

    def _collect_output_schema_node_parts(
        self,
        items: (
            tuple[model.OutputSchemaBodyItem, ...]
            | tuple[model.OutputSchemaRouteBodyItem, ...]
            | tuple[model.OutputSchemaAuthoredItem, ...]
        ),
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> _OutputSchemaNodeParts:
        parts = _OutputSchemaNodeParts()
        fields: list[model.OutputSchemaField | model.OutputSchemaRouteField] = []
        defs: list[model.OutputSchemaDef] = []
        route_choices: list[model.OutputSchemaRouteChoice] = []
        legacy_enum_values: tuple[model.OutputSchemaLiteralValue, ...] = ()
        inline_enum_values: tuple[model.OutputSchemaLiteralValue, ...] = ()
        variants: tuple[model.OutputSchemaVariant, ...] = ()
        constraints: list[tuple[str, int | float]] = []
        seen_child_items: dict[str, object] = {}
        seen_settings: dict[str, object] = {}
        for item in items:
            if isinstance(item, model.OutputSchemaSetting):
                if item.key in seen_settings:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema setting",
                        detail=(
                            f"Duplicate output schema setting in {owner_label}: {item.key}"
                        ),
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            output_schema_related_site(
                                label=f"first `{item.key}` setting",
                                unit=unit,
                                source_span=self._authored_source_span(seen_settings[item.key]),
                            ),
                        ),
                    )
                seen_settings[item.key] = item
                if item.key == "type":
                    if not isinstance(item.value, str):
                        raise output_schema_compile_error(
                            code="E299",
                            summary="Invalid output schema setting",
                            detail=f"Output schema type must be a name in {owner_label}",
                            unit=unit,
                            source_span=item.source_span,
                        )
                    parts.type_name = item.value
                    parts.type_source_span = item.source_span
                    continue
                if item.key == "note":
                    if not isinstance(item.value, str):
                        raise output_schema_compile_error(
                            code="E299",
                            summary="Invalid output schema setting",
                            detail=f"Output schema note must be a string in {owner_label}",
                            unit=unit,
                            source_span=item.source_span,
                        )
                    parts.note = item.value
                    continue
                if item.key == "format":
                    if not isinstance(item.value, str):
                        raise output_schema_compile_error(
                            code="E299",
                            summary="Invalid output schema setting",
                            detail=f"Output schema format must be a name in {owner_label}",
                            unit=unit,
                            source_span=item.source_span,
                        )
                    parts.format_name = item.value
                    continue
                if item.key == "pattern":
                    if not isinstance(item.value, str):
                        raise output_schema_compile_error(
                            code="E299",
                            summary="Invalid output schema setting",
                            detail=f"Output schema pattern must be a string in {owner_label}",
                            unit=unit,
                            source_span=item.source_span,
                        )
                    parts.pattern = item.value
                    continue
                if item.key == "const":
                    parts.const_value = item.value
                    parts.has_const = True
                    continue
                if item.key == "ref":
                    if not isinstance(item.value, model.NameRef):
                        raise output_schema_compile_error(
                            code="E299",
                            summary="Invalid output schema setting",
                            detail=(
                                f"Output schema ref must point at a named schema in {owner_label}"
                            ),
                            unit=unit,
                            source_span=item.source_span,
                        )
                    parts.ref = item.value
                    continue
                if item.key in _OUTPUT_SCHEMA_JSON_KEY_MAP:
                    if not isinstance(item.value, (int, float)):
                        raise output_schema_compile_error(
                            code="E299",
                            summary="Invalid output schema setting",
                            detail=(
                                "Output schema constraint must be numeric in "
                                f"{owner_label}: {item.key}"
                            ),
                            unit=unit,
                            source_span=item.source_span,
                        )
                    constraints.append((item.key, item.value))
                    continue
                raise output_schema_compile_error(
                    code="E299",
                    summary="Unsupported output schema setting",
                    detail=f"Unsupported output schema setting in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                )
            if isinstance(item, model.OutputSchemaFlag):
                if item.key == "nullable":
                    if parts.nullable:
                        raise output_schema_compile_error(
                            code="E299",
                            summary="Duplicate output schema flag",
                            detail=f"Duplicate output schema flag in {owner_label}: nullable",
                            unit=unit,
                            source_span=item.source_span,
                        )
                    parts.nullable = True
                    continue
                if item.key == "required":
                    raise output_schema_compile_error(
                        code="E236",
                        summary="Output schema `required` is retired",
                        detail=(
                            f"{owner_label} still uses `required`. Delete `required`; "
                            "output schema fields are always present on the wire today."
                        ),
                        unit=unit,
                        source_span=item.source_span,
                        hints=(
                            "Delete `required` from this output schema entry.",
                        ),
                    )
                if item.key == "optional":
                    raise output_schema_compile_error(
                        code="E237",
                        summary="Output schema `optional` is retired",
                        detail=(
                            f"{owner_label} still uses `optional`. Replace `optional` "
                            "with `nullable` when the value may be `null`."
                        ),
                        unit=unit,
                        source_span=item.source_span,
                        hints=(
                            "Use `nullable` when the value may be `null`.",
                        ),
                    )
                    continue
                raise output_schema_compile_error(
                    code="E299",
                    summary="Unsupported output schema flag",
                    detail=f"Unsupported output schema flag in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                )
            if isinstance(item, model.OutputSchemaEnum):
                if legacy_enum_values:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema enum block",
                        detail=f"Duplicate output schema enum in {owner_label}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                legacy_enum_values = item.values
                parts.legacy_enum_source_span = item.source_span
                continue
            if isinstance(item, model.OutputSchemaValues):
                if inline_enum_values:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema values block",
                        detail=f"Duplicate output schema values block in {owner_label}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                inline_enum_values = item.values
                parts.inline_enum_source_span = item.source_span
                continue
            if isinstance(item, model.OutputSchemaItems):
                if parts.items_value is not None:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema items block",
                        detail=f"Duplicate output schema items block in {owner_label}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                parts.items_value = item.value
                continue
            if isinstance(item, model.OutputSchemaAnyOf):
                if variants:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema any_of block",
                        detail=f"Duplicate output schema any_of block in {owner_label}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                variants = item.variants
                continue
            if isinstance(item, model.OutputSchemaField):
                if item.key in seen_child_items:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema child key",
                        detail=f"Duplicate output schema child key in {owner_label}: {item.key}",
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            output_schema_related_site(
                                label=f"first `{item.key}` child",
                                unit=unit,
                                source_span=self._authored_source_span(seen_child_items[item.key]),
                            ),
                        ),
                    )
                seen_child_items[item.key] = item
                fields.append(item)
                continue
            if isinstance(item, model.OutputSchemaRouteField):
                if item.key in seen_child_items:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema child key",
                        detail=f"Duplicate output schema child key in {owner_label}: {item.key}",
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            output_schema_related_site(
                                label=f"first `{item.key}` child",
                                unit=unit,
                                source_span=self._authored_source_span(seen_child_items[item.key]),
                            ),
                        ),
                    )
                seen_child_items[item.key] = item
                fields.append(item)
                continue
            if isinstance(item, model.OutputSchemaDef):
                if item.key in seen_child_items:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema child key",
                        detail=f"Duplicate output schema child key in {owner_label}: {item.key}",
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            output_schema_related_site(
                                label=f"first `{item.key}` child",
                                unit=unit,
                                source_span=self._authored_source_span(seen_child_items[item.key]),
                            ),
                        ),
                    )
                seen_child_items[item.key] = item
                defs.append(item)
                continue
            if isinstance(item, model.OutputSchemaRouteChoice):
                if item.key in seen_child_items:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema child key",
                        detail=f"Duplicate output schema child key in {owner_label}: {item.key}",
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            output_schema_related_site(
                                label=f"first `{item.key}` child",
                                unit=unit,
                                source_span=self._authored_source_span(seen_child_items[item.key]),
                            ),
                        ),
                    )
                seen_child_items[item.key] = item
                route_choices.append(item)
                continue
            raise CompileError(
                f"Internal compiler error: unsupported output schema node item in {owner_label}: "
                f"{type(item).__name__}"
            )

        parts.fields = tuple(fields)
        parts.defs = tuple(defs)
        parts.route_choices = tuple(route_choices)
        parts.legacy_enum_values = legacy_enum_values
        parts.inline_enum_values = inline_enum_values
        parts.any_of = variants
        parts.constraints = tuple(constraints)
        return parts

    def _normalize_output_schema_inline_enum(
        self,
        parts: _OutputSchemaNodeParts,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if parts.type_name == "enum":
            if parts.legacy_enum_values:
                raise output_schema_compile_error(
                    code="E229",
                    summary="Output schema inline enum forms cannot be mixed",
                    detail=(
                        f"{owner_label} uses `type: enum` with legacy `enum:`."
                    ),
                    unit=unit,
                    source_span=parts.legacy_enum_source_span,
                    related=(
                        output_schema_related_site(
                            label="`type: enum`",
                            unit=unit,
                            source_span=parts.type_source_span,
                        ),
                    ),
                    hints=(
                        "Use `values:` with `type: enum` for the new inline form.",
                        "Keep legacy `enum:` only with `type: string`.",
                    ),
                )
            if not parts.inline_enum_values:
                raise output_schema_compile_error(
                    code="E227",
                    summary="Output schema inline enum is missing `values:`",
                    detail=(
                        f"{owner_label} uses `type: enum` without a `values:` block."
                    ),
                    unit=unit,
                    source_span=parts.type_source_span,
                    hints=(
                        "Add a `values:` block under this output schema entry.",
                    ),
                )
            parts.type_name = "string"
            parts.enum_values = parts.inline_enum_values
            return

        if parts.inline_enum_values:
            detail = (
                f"{owner_label} uses `values:` without `type: enum`."
                if parts.type_name is None
                else f"{owner_label} uses `values:` with `type: {parts.type_name}`."
            )
            related = ()
            if parts.type_source_span is not None:
                related = (
                    output_schema_related_site(
                        label=f"`type: {parts.type_name}`",
                        unit=unit,
                        source_span=parts.type_source_span,
                    ),
                )
            raise output_schema_compile_error(
                code="E228",
                summary="Output schema `values:` requires `type: enum`",
                detail=detail,
                unit=unit,
                source_span=parts.inline_enum_source_span,
                related=related,
                hints=(
                    "Use `type: enum` with `values:` for the new inline enum form.",
                    "Keep `type: string` plus `enum:` only for the legacy form.",
                ),
            )

        if parts.legacy_enum_values and parts.type_name not in {None, "string"}:
            raise output_schema_compile_error(
                code="E229",
                summary="Legacy output schema `enum:` requires `type: string`",
                detail=(
                    f"{owner_label} uses legacy `enum:` with `type: {parts.type_name}`."
                ),
                unit=unit,
                source_span=parts.legacy_enum_source_span,
                related=(
                    output_schema_related_site(
                        label=f"`type: {parts.type_name}`",
                        unit=unit,
                        source_span=parts.type_source_span,
                    ),
                ),
                hints=(
                    "Keep legacy `enum:` only with `type: string`.",
                    "Switch to `type: enum` plus `values:` if you want the new form.",
                ),
            )

        parts.enum_values = parts.legacy_enum_values

    def _output_schema_example_item(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        owner_label: str,
    ) -> model.OutputSchemaExample | None:
        example_item: model.OutputSchemaExample | None = None
        for item in output_schema_decl.items:
            if not isinstance(item, model.OutputSchemaExample):
                continue
            if example_item is not None:
                raise output_schema_compile_error(
                    code="E299",
                    summary="Duplicate output schema example",
                    detail=f"Duplicate output schema example in {owner_label}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_schema_related_site(
                            label="first `example:` block",
                            unit=unit,
                            source_span=example_item.source_span,
                        ),
                    ),
                )
            example_item = item
        return example_item

    def _output_schema_example_value(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        owner_label: str,
    ) -> model.OutputSchemaExampleObject | None:
        example_item = self._output_schema_example_item(
            output_schema_decl,
            owner_label=owner_label,
        )
        return None if example_item is None else example_item.value

    def _materialize_output_schema_example_value(
        self,
        value: model.OutputSchemaExampleValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> object:
        if isinstance(value, model.OutputSchemaExampleObject):
            entries: dict[str, object] = {}
            for entry in value.entries:
                if entry.key in entries:
                    raise output_schema_compile_error(
                        code="E299",
                        summary="Duplicate output schema example key",
                        detail=(
                            f"Duplicate output schema example key in {owner_label}: {entry.key}"
                        ),
                        unit=unit,
                        source_span=source_span,
                    )
                entries[entry.key] = self._materialize_output_schema_example_value(
                    entry.value,
                    unit=unit,
                    owner_label=f"{owner_label}.{entry.key}",
                    source_span=source_span,
                )
            return entries
        if isinstance(value, model.OutputSchemaExampleArray):
            return [
                self._materialize_output_schema_example_value(
                    item,
                    unit=unit,
                    owner_label=f"{owner_label}[]",
                    source_span=source_span,
                )
                for item in value.items
            ]
        return value

    def _wrap_nullable_output_schema(self, schema: dict[str, object]) -> dict[str, object]:
        if "const" in schema:
            outer: dict[str, object] = {}
            branch: dict[str, object] = {}
            for key, value in schema.items():
                if key in {"title", "description", "$defs"}:
                    outer[key] = value
                    continue
                branch[key] = value
            return {
                **outer,
                "anyOf": [branch, {"type": "null"}],
            }

        if isinstance(schema.get("enum"), list):
            enum_values = list(schema["enum"])
            if None not in enum_values:
                enum_values.append(None)
            schema = {**schema, "enum": enum_values}

        if "anyOf" in schema:
            any_of = schema.get("anyOf")
            if not isinstance(any_of, list):
                raise CompileError("Internal compiler error: output schema anyOf must be a list")
            return {**schema, "anyOf": [*any_of, {"type": "null"}]}

        schema_type = schema.get("type")
        if isinstance(schema_type, str):
            return {**schema, "type": [schema_type, "null"]}
        if isinstance(schema_type, list):
            values = [*schema_type]
            if "null" not in values:
                values.append("null")
            return {**schema, "type": values}

        outer: dict[str, object] = {}
        branch: dict[str, object] = {}
        for key, value in schema.items():
            if key in {"title", "description", "$defs"}:
                outer[key] = value
                continue
            branch[key] = value
        return {
            **outer,
            "anyOf": [branch, {"type": "null"}],
        }

    def _output_schema_pointer_fragment(self, path: tuple[str, ...]) -> str:
        if not path:
            return "#"
        escaped = tuple(part.replace("~", "~0").replace("/", "~1") for part in path)
        return "#/" + "/".join(escaped)
