from __future__ import annotations

from dataclasses import dataclass, replace

from doctrine import model
from doctrine._compiler.naming import _dotted_ref_name
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
    note: str | None = None
    format_name: str | None = None
    pattern: str | None = None
    ref: model.NameRef | None = None
    items_value: model.NameRef | tuple[model.OutputSchemaBodyItem, ...] | None = None
    enum_values: tuple[model.OutputSchemaLiteralValue, ...] = ()
    any_of: tuple[model.OutputSchemaVariant, ...] = ()
    fields: tuple[model.OutputSchemaField, ...] = ()
    defs: tuple[model.OutputSchemaDef, ...] = ()
    constraints: tuple[tuple[str, int | float], ...] = ()
    const_value: model.OutputSchemaLiteralValue | None = None
    has_const: bool = False
    required_explicit: bool = False
    optional: bool = False


class ResolveOutputSchemasMixin:
    """Inherited output-schema resolution and lowering helpers."""

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
            raise CompileError(f"Cyclic output schema inheritance: {cycle}")

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
        owner_label: str,
        parent_unit: IndexedUnit | None = None,
        parent_output_schema: model.OutputSchemaDecl | None = None,
        parent_label: str | None = None,
    ) -> model.OutputSchemaDecl:
        if parent_output_schema is None:
            patch_key = self._first_output_schema_patch_key(output_schema_decl)
            if patch_key is not None:
                raise CompileError(
                    f"inherit requires an inherited output schema in {owner_label}: {patch_key}"
                )
            override_key = self._first_output_schema_override_key(output_schema_decl)
            if override_key is not None:
                raise CompileError(
                    f"override requires an inherited output schema in {owner_label}: {override_key}"
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
                    model.OutputSchemaDef,
                    model.OutputSchemaExample,
                ),
            )
        }
        resolved_items: list[model.OutputSchemaAuthoredItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in output_schema_decl.items:
            key = self._output_schema_item_key(item)
            if key is None:
                raise CompileError(
                    "Internal compiler error: unsupported output schema item in "
                    f"{owner_label}: {type(item).__name__}"
                )
            if key in emitted_keys:
                raise CompileError(f"Duplicate output schema item key in {owner_label}: {key}")
            emitted_keys.add(key)

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined output schema entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if self._is_output_schema_override_item(item):
                if parent_item is None:
                    raise CompileError(
                        "E001 Cannot override undefined output schema entry in "
                        f"{parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(
                    self._resolve_output_schema_override_item(
                        item,
                        parent_item=parent_item,
                        owner_label=owner_label,
                    )
                )
                continue

            if parent_item is not None:
                raise CompileError(
                    f"Inherited output schema requires `override {key}` in {owner_label}"
                )
            resolved_items.append(item)

        missing_keys = [
            item.key
            for item in inherited_parent_output_schema.items
            if isinstance(
                item,
                (
                    model.OutputSchemaField,
                    model.OutputSchemaDef,
                    model.OutputSchemaExample,
                ),
            )
            and item.key not in accounted_keys
        ]
        if missing_keys:
            raise CompileError(
                f"E003 Missing inherited output schema entry in {owner_label}: "
                + ", ".join(missing_keys)
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
                model.OutputSchemaDef,
                model.OutputSchemaExample,
                model.InheritItem,
                model.OutputSchemaOverrideField,
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
                model.OutputSchemaOverrideDef,
                model.OutputSchemaOverrideExample,
            ),
        )

    def _resolve_output_schema_override_item(
        self,
        item: (
            model.OutputSchemaOverrideField
            | model.OutputSchemaOverrideDef
            | model.OutputSchemaOverrideExample
        ),
        *,
        parent_item: model.OutputSchemaField | model.OutputSchemaDef | model.OutputSchemaExample,
        owner_label: str,
    ) -> model.OutputSchemaField | model.OutputSchemaDef | model.OutputSchemaExample:
        key = item.key
        if isinstance(item, model.OutputSchemaOverrideField):
            if not isinstance(parent_item, model.OutputSchemaField):
                raise CompileError(
                    f"Override kind mismatch for output schema entry in {owner_label}: {key}"
                )
            return model.OutputSchemaField(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                items=item.items,
            )
        if isinstance(item, model.OutputSchemaOverrideDef):
            if not isinstance(parent_item, model.OutputSchemaDef):
                raise CompileError(
                    f"Override kind mismatch for output schema entry in {owner_label}: {key}"
                )
            return model.OutputSchemaDef(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                items=item.items,
            )
        if not isinstance(parent_item, model.OutputSchemaExample):
            raise CompileError(
                f"Override kind mismatch for output schema entry in {owner_label}: {key}"
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
            )
        if isinstance(item, model.OutputSchemaItems):
            if isinstance(item.value, model.NameRef):
                return model.OutputSchemaItems(
                    value=self._rebind_output_schema_ref(
                        item.value,
                        parent_unit=parent_unit,
                        local_def_scopes=local_def_scopes,
                    )
                )
            return model.OutputSchemaItems(
                value=self._rebind_output_schema_node_items(
                    item.value,
                    parent_unit=parent_unit,
                    local_def_scopes=local_def_scopes,
                )
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
                    )
                    for variant in item.variants
                )
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
            raise CompileError(f"Cyclic output schema lowering: {cycle}")

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
                allow_presence_flags=False,
            )
            if not pointer:
                self._lowered_output_schema_cache[output_schema_key] = lowered
            return lowered
        finally:
            self._output_schema_lowering_stack.pop()

    def _lower_output_schema_node(
        self,
        items: tuple[model.OutputSchemaBodyItem, ...] | tuple[model.OutputSchemaAuthoredItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        title: str | None,
        local_def_scopes: tuple[dict[str, tuple[str, ...]], ...],
        pointer: tuple[str, ...],
        allow_presence_flags: bool,
    ) -> dict[str, object]:
        parts = self._collect_output_schema_node_parts(
            items,
            owner_label=owner_label,
        )
        if parts.required_explicit and parts.optional:
            raise CompileError(
                f"Output schema entry cannot be both required and optional in {owner_label}"
            )
        if not allow_presence_flags and (parts.required_explicit or parts.optional):
            raise CompileError(
                f"Output schema presence flags are only valid on fields in {owner_label}"
            )

        schema: dict[str, object] = {}
        if title is not None:
            schema["title"] = title
        if parts.note is not None:
            schema["description"] = parts.note

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
                    allow_presence_flags=False,
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
            if parts.optional:
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
            if parts.optional:
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

        if parts.optional:
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
                allow_presence_flags=False,
            )
        return lowered

    def _lower_output_schema_field(
        self,
        field: model.OutputSchemaField,
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
            allow_presence_flags=True,
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
            raise CompileError(
                f"Unknown output schema ref in {owner_label}: {_dotted_ref_name(ref)}"
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
            allow_presence_flags=False,
        )

    def _collect_output_schema_node_parts(
        self,
        items: tuple[model.OutputSchemaBodyItem, ...] | tuple[model.OutputSchemaAuthoredItem, ...],
        *,
        owner_label: str,
    ) -> _OutputSchemaNodeParts:
        parts = _OutputSchemaNodeParts()
        fields: list[model.OutputSchemaField] = []
        defs: list[model.OutputSchemaDef] = []
        enum_values: tuple[model.OutputSchemaLiteralValue, ...] = ()
        variants: tuple[model.OutputSchemaVariant, ...] = ()
        constraints: list[tuple[str, int | float]] = []
        seen_child_keys: set[str] = set()
        seen_settings: set[str] = set()
        for item in items:
            if isinstance(item, model.OutputSchemaSetting):
                if item.key in seen_settings:
                    raise CompileError(
                        f"Duplicate output schema setting in {owner_label}: {item.key}"
                    )
                seen_settings.add(item.key)
                if item.key == "type":
                    if not isinstance(item.value, str):
                        raise CompileError(
                            f"Output schema type must be a name in {owner_label}"
                        )
                    parts.type_name = item.value
                    continue
                if item.key == "note":
                    if not isinstance(item.value, str):
                        raise CompileError(
                            f"Output schema note must be a string in {owner_label}"
                        )
                    parts.note = item.value
                    continue
                if item.key == "format":
                    if not isinstance(item.value, str):
                        raise CompileError(
                            f"Output schema format must be a name in {owner_label}"
                        )
                    parts.format_name = item.value
                    continue
                if item.key == "pattern":
                    if not isinstance(item.value, str):
                        raise CompileError(
                            f"Output schema pattern must be a string in {owner_label}"
                        )
                    parts.pattern = item.value
                    continue
                if item.key == "const":
                    parts.const_value = item.value
                    parts.has_const = True
                    continue
                if item.key == "ref":
                    if not isinstance(item.value, model.NameRef):
                        raise CompileError(
                            f"Output schema ref must point at a named schema in {owner_label}"
                        )
                    parts.ref = item.value
                    continue
                if item.key in _OUTPUT_SCHEMA_JSON_KEY_MAP:
                    if not isinstance(item.value, (int, float)):
                        raise CompileError(
                            f"Output schema constraint must be numeric in {owner_label}: {item.key}"
                        )
                    constraints.append((item.key, item.value))
                    continue
                raise CompileError(
                    f"Unsupported output schema setting in {owner_label}: {item.key}"
                )
            if isinstance(item, model.OutputSchemaFlag):
                if item.key == "required":
                    if parts.required_explicit:
                        raise CompileError(
                            f"Duplicate output schema flag in {owner_label}: required"
                        )
                    parts.required_explicit = True
                    continue
                if item.key == "optional":
                    if parts.optional:
                        raise CompileError(
                            f"Duplicate output schema flag in {owner_label}: optional"
                        )
                    parts.optional = True
                    continue
                raise CompileError(
                    f"Unsupported output schema flag in {owner_label}: {item.key}"
                )
            if isinstance(item, model.OutputSchemaEnum):
                if enum_values:
                    raise CompileError(f"Duplicate output schema enum in {owner_label}")
                enum_values = item.values
                continue
            if isinstance(item, model.OutputSchemaItems):
                if parts.items_value is not None:
                    raise CompileError(f"Duplicate output schema items block in {owner_label}")
                parts.items_value = item.value
                continue
            if isinstance(item, model.OutputSchemaAnyOf):
                if variants:
                    raise CompileError(f"Duplicate output schema any_of block in {owner_label}")
                variants = item.variants
                continue
            if isinstance(item, model.OutputSchemaField):
                if item.key in seen_child_keys:
                    raise CompileError(
                        f"Duplicate output schema child key in {owner_label}: {item.key}"
                    )
                seen_child_keys.add(item.key)
                fields.append(item)
                continue
            if isinstance(item, model.OutputSchemaDef):
                if item.key in seen_child_keys:
                    raise CompileError(
                        f"Duplicate output schema child key in {owner_label}: {item.key}"
                    )
                seen_child_keys.add(item.key)
                defs.append(item)
                continue
            raise CompileError(
                f"Internal compiler error: unsupported output schema node item in {owner_label}: "
                f"{type(item).__name__}"
            )

        parts.fields = tuple(fields)
        parts.defs = tuple(defs)
        parts.enum_values = enum_values
        parts.any_of = variants
        parts.constraints = tuple(constraints)
        return parts

    def _output_schema_example_value(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        owner_label: str,
    ) -> model.OutputSchemaExampleObject | None:
        example_item: model.OutputSchemaExample | None = None
        for item in output_schema_decl.items:
            if not isinstance(item, model.OutputSchemaExample):
                continue
            if example_item is not None:
                raise CompileError(f"Duplicate output schema example in {owner_label}")
            example_item = item
        return None if example_item is None else example_item.value

    def _materialize_output_schema_example_value(
        self,
        value: model.OutputSchemaExampleValue,
        *,
        owner_label: str,
    ) -> object:
        if isinstance(value, model.OutputSchemaExampleObject):
            entries: dict[str, object] = {}
            for entry in value.entries:
                if entry.key in entries:
                    raise CompileError(
                        f"Duplicate output schema example key in {owner_label}: {entry.key}"
                    )
                entries[entry.key] = self._materialize_output_schema_example_value(
                    entry.value,
                    owner_label=f"{owner_label}.{entry.key}",
                )
            return entries
        if isinstance(value, model.OutputSchemaExampleArray):
            return [
                self._materialize_output_schema_example_value(
                    item,
                    owner_label=f"{owner_label}[]",
                )
                for item in value.items
            ]
        return value

    def _wrap_nullable_output_schema(self, schema: dict[str, object]) -> dict[str, object]:
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
