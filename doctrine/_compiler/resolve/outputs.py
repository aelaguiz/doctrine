from __future__ import annotations

import json
from dataclasses import replace

from doctrine import model
from doctrine._compiler.constants import _BUILTIN_INPUT_SOURCES, _BUILTIN_OUTPUT_TARGETS
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.resolved_types import (
    AddressableNode,
    CompileError,
    CompiledSection,
    ConfigSpec,
    ContractBinding,
    FinalOutputJsonShapeSummary,
    IndexedUnit,
    OutputDeclKey,
    ResolvedIoBody,
    ResolvedIoItem,
    ResolvedIoRef,
    ResolvedIoSection,
    ResolvedOutputTargetDeliverySkill,
    ResolvedOutputTargetSpec,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveOutputsMixin:
    """Output and IO-body resolution helpers for ResolveMixin."""

    def _resolve_output_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        target_unit, decl = self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_by_name",
            missing_label="output declaration",
        )
        return target_unit, self._resolve_output_decl_body(decl, unit=target_unit)

    def _resolve_local_output_decl(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> model.OutputDecl | None:
        decl = unit.outputs_by_name.get(declaration_name)
        if decl is None:
            return None
        return self._resolve_output_decl_body(decl, unit=unit)

    def _resolve_output_shape_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputShapeDecl]:
        target_unit, decl = self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_shapes_by_name",
            missing_label="output shape declaration",
        )
        return target_unit, self._resolve_output_shape_decl_body(decl, unit=target_unit)

    def _resolve_local_output_shape_decl(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> model.OutputShapeDecl | None:
        decl = unit.output_shapes_by_name.get(declaration_name)
        if decl is None:
            return None
        return self._resolve_output_shape_decl_body(decl, unit=unit)

    def _resolve_output_shape_decl_body(
        self,
        output_shape_decl: model.OutputShapeDecl,
        *,
        unit: IndexedUnit,
    ) -> model.OutputShapeDecl:
        output_shape_key = (unit.module_parts, output_shape_decl.name)
        cached = self._resolved_output_shape_cache.get(output_shape_key)
        if cached is not None:
            return cached

        if output_shape_key in self._output_shape_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._output_shape_resolution_stack, output_shape_key]
            )
            raise CompileError(f"Cyclic output shape inheritance: {cycle}")

        self._output_shape_resolution_stack.append(output_shape_key)
        try:
            owner_label = _dotted_decl_name(unit.module_parts, output_shape_decl.name)
            parent_output_shape: model.OutputShapeDecl | None = None
            parent_label: str | None = None
            if output_shape_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_output_shape_decl(
                    output_shape_decl,
                    unit=unit,
                )
                parent_output_shape = self._resolve_output_shape_decl_body(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"output shape {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_inherited_output_shape_decl(
                output_shape_decl,
                owner_label=owner_label,
                parent_unit=parent_unit if output_shape_decl.parent_ref is not None else None,
                parent_output_shape=parent_output_shape,
                parent_label=parent_label,
            )
            self._resolved_output_shape_cache[output_shape_key] = resolved
            return resolved
        finally:
            self._output_shape_resolution_stack.pop()

    def _resolve_output_decl_body(
        self,
        output_decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> model.OutputDecl:
        output_key = (unit.module_parts, output_decl.name)
        cached = self._resolved_output_decl_cache.get(output_key)
        if cached is not None:
            return cached

        if output_key in self._output_decl_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._output_decl_resolution_stack, output_key]
            )
            raise CompileError(f"Cyclic output inheritance: {cycle}")

        self._output_decl_resolution_stack.append(output_key)
        try:
            owner_label = _dotted_decl_name(unit.module_parts, output_decl.name)
            parent_output: model.OutputDecl | None = None
            parent_label: str | None = None
            if output_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_output_decl(
                    output_decl,
                    unit=unit,
                )
                parent_output = self._resolve_output_decl_body(parent_decl, unit=parent_unit)
                parent_label = f"output {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_inherited_output_decl(
                output_decl,
                unit=unit,
                owner_label=owner_label,
                parent_unit=parent_unit if output_decl.parent_ref is not None else None,
                parent_output=parent_output,
                parent_label=parent_label,
            )
            self._resolved_output_decl_cache[output_key] = resolved
            return resolved
        finally:
            self._output_decl_resolution_stack.pop()

    def _resolve_inherited_output_shape_decl(
        self,
        output_shape_decl: model.OutputShapeDecl,
        *,
        owner_label: str,
        parent_unit: IndexedUnit | None = None,
        parent_output_shape: model.OutputShapeDecl | None = None,
        parent_label: str | None = None,
    ) -> model.OutputShapeDecl:
        if parent_output_shape is None:
            patch_key = self._first_output_shape_patch_key(output_shape_decl)
            if patch_key is not None:
                raise CompileError(
                    f"inherit requires an inherited output shape in {owner_label}: {patch_key}"
                )
            override_key = self._first_output_shape_override_key(output_shape_decl)
            if override_key is not None:
                raise CompileError(
                    f"override requires an inherited output shape in {owner_label}: {override_key}"
                )
            return replace(output_shape_decl, parent_ref=None)

        inherited_parent_output_shape = (
            parent_output_shape
            if parent_unit is None
            else self._rebind_inherited_output_shape_decl(
                parent_output_shape,
                parent_unit=parent_unit,
            )
        )

        unkeyed_parent_items = self._output_shape_unkeyed_parent_labels(inherited_parent_output_shape)
        if unkeyed_parent_items:
            details = ", ".join(unkeyed_parent_items)
            raise CompileError(
                "Cannot inherit output shape with unkeyed top-level items in "
                f"{parent_label}: {details}"
            )

        parent_items_by_key = {
            item.key
            : item
            for item in inherited_parent_output_shape.items
            if self._output_item_key(item) is not None
        }
        resolved_items: list[model.OutputRecordItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in output_shape_decl.items:
            key = self._output_item_key(item)
            if key is None:
                resolved_items.append(item)
                continue

            if key in emitted_keys:
                raise CompileError(f"Duplicate output shape item key in {owner_label}: {key}")
            emitted_keys.add(key)

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined output shape entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if self._is_output_override_item(item):
                if parent_item is None:
                    raise CompileError(
                        "E001 Cannot override undefined output shape entry in "
                        f"{parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(
                    self._resolve_output_override_item(
                        item,
                        parent_item=parent_item,
                        owner_label=owner_label,
                    )
                )
                continue

            if parent_item is not None:
                raise CompileError(
                    f"Inherited output shape requires `override {key}` in {owner_label}"
                )

            resolved_items.append(item)

        missing_keys = [
            item.key
            for item in inherited_parent_output_shape.items
            if self._output_item_key(item) is not None and item.key not in accounted_keys
        ]
        if missing_keys:
            raise CompileError(
                f"E003 Missing inherited output shape entry in {owner_label}: {', '.join(missing_keys)}"
            )

        return model.OutputShapeDecl(
            name=output_shape_decl.name,
            title=output_shape_decl.title,
            items=tuple(resolved_items),
            parent_ref=None,
        )

    def _resolve_inherited_output_decl(
        self,
        output_decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_unit: IndexedUnit | None = None,
        parent_output: model.OutputDecl | None = None,
        parent_label: str | None = None,
    ) -> model.OutputDecl:
        if parent_output is None:
            patch_key = self._first_output_patch_key(output_decl)
            if patch_key is not None:
                raise CompileError(
                    f"inherit requires an inherited output in {owner_label}: {patch_key}"
                )
            override_key = self._first_output_override_key(output_decl)
            if override_key is not None:
                raise CompileError(
                    f"override requires an inherited output in {owner_label}: {override_key}"
                )
            return replace(output_decl, parent_ref=None)

        inherited_parent_output = (
            parent_output
            if parent_unit is None
            else self._rebind_inherited_output_decl(parent_output, parent_unit=parent_unit)
        )

        unkeyed_parent_items = self._output_unkeyed_parent_labels(inherited_parent_output)
        if unkeyed_parent_items:
            details = ", ".join(unkeyed_parent_items)
            raise CompileError(
                f"Cannot inherit output with unkeyed top-level items in {parent_label}: {details}"
            )

        parent_items_by_key = {
            item.key
            : item
            for item in inherited_parent_output.items
            if self._output_item_key(item) is not None
        }
        resolved_items: list[model.OutputRecordItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in output_decl.items:
            key = self._output_item_key(item)
            if key is None:
                resolved_items.append(item)
                continue

            if key in emitted_keys:
                raise CompileError(f"Duplicate output item key in {owner_label}: {key}")
            emitted_keys.add(key)

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined output entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if self._is_output_override_item(item):
                if parent_item is None:
                    raise CompileError(
                        f"E001 Cannot override undefined output entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(
                    self._resolve_output_override_item(
                        item,
                        parent_item=parent_item,
                        owner_label=owner_label,
                    )
                )
                continue

            if parent_item is not None:
                raise CompileError(f"Inherited output requires `override {key}` in {owner_label}")

            resolved_items.append(item)

        resolved_schema, schema_accounted = self._resolve_output_attachment(
            output_decl,
            parent_output=inherited_parent_output,
            owner_label=owner_label,
            parent_label=parent_label,
            key="schema",
        )
        resolved_structure, structure_accounted = self._resolve_output_attachment(
            output_decl,
            parent_output=inherited_parent_output,
            owner_label=owner_label,
            parent_label=parent_label,
            key="structure",
        )
        resolved_render_profile, render_profile_accounted = self._resolve_output_attachment(
            output_decl,
            parent_output=inherited_parent_output,
            owner_label=owner_label,
            parent_label=parent_label,
            key="render_profile",
        )
        resolved_trust_surface, trust_surface_accounted = self._resolve_output_attachment(
            output_decl,
            parent_output=inherited_parent_output,
            owner_label=owner_label,
            parent_label=parent_label,
            key="trust_surface",
        )

        missing_keys = [
            item.key
            for item in inherited_parent_output.items
            if self._output_item_key(item) is not None and item.key not in accounted_keys
        ]
        if self._output_decl_has_attachment(inherited_parent_output, "schema") and not schema_accounted:
            missing_keys.append("schema")
        if self._output_decl_has_attachment(inherited_parent_output, "structure") and not structure_accounted:
            missing_keys.append("structure")
        if self._output_decl_has_attachment(inherited_parent_output, "render_profile") and not render_profile_accounted:
            missing_keys.append("render_profile")
        if self._output_decl_has_attachment(inherited_parent_output, "trust_surface") and not trust_surface_accounted:
            missing_keys.append("trust_surface")
        if missing_keys:
            raise CompileError(
                f"E003 Missing inherited output entry in {owner_label}: {', '.join(missing_keys)}"
            )

        return model.OutputDecl(
            name=output_decl.name,
            title=output_decl.title,
            items=tuple(resolved_items),
            schema=resolved_schema,
            structure=resolved_structure,
            render_profile_ref=resolved_render_profile,
            trust_surface=resolved_trust_surface or (),
            parent_ref=None,
            schema_mode="set" if resolved_schema is not None else None,
            structure_mode="set" if resolved_structure is not None else None,
            render_profile_mode="set" if resolved_render_profile is not None else None,
            trust_surface_mode="set" if resolved_trust_surface else None,
        )

    def _first_output_patch_key(self, output_decl: model.OutputDecl) -> str | None:
        for item in output_decl.items:
            if isinstance(item, model.InheritItem):
                return item.key
        for key in ("schema", "structure", "render_profile", "trust_surface"):
            if getattr(output_decl, f"{key}_mode") == "inherit":
                return key
        return None

    def _first_output_override_key(self, output_decl: model.OutputDecl) -> str | None:
        for item in output_decl.items:
            if self._is_output_override_item(item):
                return item.key
        for key in ("schema", "structure", "render_profile", "trust_surface"):
            if getattr(output_decl, f"{key}_mode") == "override":
                return key
        return None

    def _first_output_shape_patch_key(
        self,
        output_shape_decl: model.OutputShapeDecl,
    ) -> str | None:
        for item in output_shape_decl.items:
            if isinstance(item, model.InheritItem):
                return item.key
        return None

    def _first_output_shape_override_key(
        self,
        output_shape_decl: model.OutputShapeDecl,
    ) -> str | None:
        for item in output_shape_decl.items:
            if self._is_output_override_item(item):
                return item.key
        return None

    def _output_item_key(self, item: object) -> str | None:
        if isinstance(
            item,
            (
                model.RecordScalar,
                model.RecordSection,
                model.GuardedOutputSection,
                model.GuardedOutputScalar,
                model.ReadableBlock,
                model.InheritItem,
                model.OutputOverrideRecordScalar,
                model.OutputOverrideRecordSection,
                model.OutputOverrideGuardedOutputSection,
                model.OutputOverrideGuardedOutputScalar,
                model.ReadableOverrideBlock,
            ),
        ):
            return item.key
        return None

    def _is_output_override_item(self, item: object) -> bool:
        return isinstance(
            item,
            (
                model.OutputOverrideRecordScalar,
                model.OutputOverrideRecordSection,
                model.OutputOverrideGuardedOutputSection,
                model.OutputOverrideGuardedOutputScalar,
                model.ReadableOverrideBlock,
            ),
        )

    def _output_unkeyed_parent_labels(self, output_decl: model.OutputDecl) -> tuple[str, ...]:
        labels: list[str] = []
        for item in output_decl.items:
            if isinstance(item, (str, model.EmphasizedLine)):
                labels.append("prose")
            elif isinstance(item, model.RecordRef):
                labels.append(_dotted_ref_name(item.ref))
        return tuple(labels)

    def _output_shape_unkeyed_parent_labels(
        self,
        output_shape_decl: model.OutputShapeDecl,
    ) -> tuple[str, ...]:
        labels: list[str] = []
        for item in output_shape_decl.items:
            if isinstance(item, (str, model.EmphasizedLine)):
                labels.append("prose")
            elif isinstance(item, model.RecordRef):
                labels.append(_dotted_ref_name(item.ref))
        return tuple(labels)

    def _resolve_output_override_item(
        self,
        item: model.OutputOverrideItem,
        *,
        parent_item: model.OutputRecordItem,
        owner_label: str,
    ) -> model.OutputRecordItem:
        key = item.key
        if isinstance(item, model.OutputOverrideRecordScalar):
            if not isinstance(parent_item, model.RecordScalar):
                raise CompileError(
                    f"Override kind mismatch for output entry in {owner_label}: {key}"
                )
            return model.RecordScalar(key=key, value=item.value, body=item.body)

        if isinstance(item, model.OutputOverrideRecordSection):
            if not isinstance(parent_item, model.RecordSection):
                raise CompileError(
                    f"Override kind mismatch for output entry in {owner_label}: {key}"
                )
            return model.RecordSection(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                items=item.items,
            )

        if isinstance(item, model.OutputOverrideGuardedOutputSection):
            if not isinstance(parent_item, model.GuardedOutputSection):
                raise CompileError(
                    f"Override kind mismatch for output entry in {owner_label}: {key}"
                )
            return model.GuardedOutputSection(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                when_expr=item.when_expr,
                items=item.items,
            )

        if isinstance(item, model.OutputOverrideGuardedOutputScalar):
            if not isinstance(parent_item, model.GuardedOutputScalar):
                raise CompileError(
                    f"Override kind mismatch for output entry in {owner_label}: {key}"
                )
            return model.GuardedOutputScalar(
                key=key,
                value=item.value,
                when_expr=item.when_expr,
                body=item.body,
            )

        if not isinstance(parent_item, model.ReadableBlock):
            raise CompileError(
                f"Override kind mismatch for output entry in {owner_label}: {key}"
            )
        if item.kind != parent_item.kind:
            raise CompileError(
                f"Override kind mismatch for output entry in {owner_label}: {key}"
            )
        return model.ReadableBlock(
            kind=item.kind,
            key=item.key,
            title=(
                item.title
                if item.title is not None
                else None
                if item.kind in {"sequence", "bullets", "checklist"}
                else parent_item.title
            ),
            payload=item.payload,
            requirement=item.requirement if item.requirement is not None else parent_item.requirement,
            when_expr=item.when_expr if item.when_expr is not None else parent_item.when_expr,
            item_schema=item.item_schema if item.item_schema is not None else parent_item.item_schema,
            row_schema=item.row_schema if item.row_schema is not None else parent_item.row_schema,
            anonymous=parent_item.anonymous,
            legacy_section=parent_item.legacy_section,
        )

    def _rebind_inherited_output_decl(
        self,
        output_decl: model.OutputDecl,
        *,
        parent_unit: IndexedUnit,
    ) -> model.OutputDecl:
        return replace(
            output_decl,
            items=tuple(
                self._rebind_inherited_output_item(item, parent_unit=parent_unit)
                for item in output_decl.items
            ),
            schema=(
                None
                if output_decl.schema is None
                else model.OutputSchemaConfig(
                    schema_ref=self._rebind_inherited_output_name_ref(
                        output_decl.schema.schema_ref,
                        parent_unit=parent_unit,
                    )
                )
            ),
            structure=(
                None
                if output_decl.structure is None
                else model.OutputStructureConfig(
                    structure_ref=self._rebind_inherited_output_name_ref(
                        output_decl.structure.structure_ref,
                        parent_unit=parent_unit,
                    )
                )
            ),
            render_profile_ref=(
                None
                if output_decl.render_profile_ref is None
                else self._rebind_inherited_output_name_ref(
                    output_decl.render_profile_ref,
                    parent_unit=parent_unit,
                )
            ),
            trust_surface=tuple(
                self._rebind_inherited_trust_surface_item(item, parent_unit=parent_unit)
                for item in output_decl.trust_surface
            ),
        )

    def _rebind_inherited_output_shape_decl(
        self,
        output_shape_decl: model.OutputShapeDecl,
        *,
        parent_unit: IndexedUnit,
    ) -> model.OutputShapeDecl:
        return replace(
            output_shape_decl,
            items=tuple(
                self._rebind_inherited_output_item(item, parent_unit=parent_unit)
                for item in output_shape_decl.items
            ),
            parent_ref=None,
        )

    def _rebind_inherited_output_item(
        self,
        item: model.OutputRecordItem,
        *,
        parent_unit: IndexedUnit,
    ) -> model.OutputRecordItem:
        if isinstance(item, (str, model.EmphasizedLine)):
            return item
        if isinstance(item, model.RecordScalar):
            return model.RecordScalar(
                key=item.key,
                value=self._rebind_inherited_output_scalar_value(
                    item.value,
                    parent_unit=parent_unit,
                ),
                body=(
                    None
                    if item.body is None
                    else tuple(
                        self._rebind_inherited_output_item(child, parent_unit=parent_unit)
                        for child in item.body
                    )
                ),
            )
        if isinstance(item, model.RecordSection):
            return model.RecordSection(
                key=item.key,
                title=item.title,
                items=tuple(
                    self._rebind_inherited_output_item(child, parent_unit=parent_unit)
                    for child in item.items
                ),
            )
        if isinstance(item, model.GuardedOutputSection):
            return model.GuardedOutputSection(
                key=item.key,
                title=item.title,
                when_expr=self._rebind_inherited_output_expr(
                    item.when_expr,
                    parent_unit=parent_unit,
                ),
                items=tuple(
                    self._rebind_inherited_output_item(child, parent_unit=parent_unit)
                    for child in item.items
                ),
            )
        if isinstance(item, model.GuardedOutputScalar):
            return model.GuardedOutputScalar(
                key=item.key,
                value=self._rebind_inherited_output_scalar_value(
                    item.value,
                    parent_unit=parent_unit,
                ),
                when_expr=self._rebind_inherited_output_expr(
                    item.when_expr,
                    parent_unit=parent_unit,
                ),
                body=(
                    None
                    if item.body is None
                    else tuple(
                        self._rebind_inherited_output_item(child, parent_unit=parent_unit)
                        for child in item.body
                    )
                ),
            )
        if isinstance(item, model.RecordRef):
            return model.RecordRef(
                ref=self._rebind_inherited_output_name_ref(
                    item.ref,
                    parent_unit=parent_unit,
                ),
                body=(
                    None
                    if item.body is None
                    else tuple(
                        self._rebind_inherited_output_item(child, parent_unit=parent_unit)
                        for child in item.body
                    )
                ),
            )
        if isinstance(item, model.ReadableBlock):
            return self._rebind_inherited_output_readable_block(item, parent_unit=parent_unit)
        return item

    def _rebind_inherited_output_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        parent_unit: IndexedUnit,
    ) -> model.RecordScalarValue:
        if isinstance(value, str):
            return value
        if isinstance(value, model.NameRef):
            return self._rebind_inherited_output_name_ref(value, parent_unit=parent_unit)
        return model.AddressableRef(
            root=self._rebind_inherited_output_name_ref(
                value.root,
                parent_unit=parent_unit,
            ),
            path=value.path,
        )

    def _rebind_inherited_output_name_ref(
        self,
        ref: model.NameRef,
        *,
        parent_unit: IndexedUnit,
    ) -> model.NameRef:
        if ref.module_parts:
            return ref
        if not self._inherited_output_ref_has_parent_decl(ref, parent_unit=parent_unit):
            return ref
        return model.NameRef(
            module_parts=parent_unit.module_parts,
            declaration_name=ref.declaration_name,
        )

    def _rebind_inherited_output_expr(
        self,
        expr: model.Expr,
        *,
        parent_unit: IndexedUnit,
    ) -> model.Expr:
        if isinstance(expr, model.ExprRef):
            if not expr.parts:
                return expr
            rebound_root = self._rebind_inherited_output_name_ref(
                model.NameRef(module_parts=(), declaration_name=expr.parts[0]),
                parent_unit=parent_unit,
            )
            if not rebound_root.module_parts:
                return expr
            return model.ExprRef(
                parts=(*rebound_root.module_parts, rebound_root.declaration_name, *expr.parts[1:])
            )
        if isinstance(expr, model.ExprCall):
            return model.ExprCall(
                name=expr.name,
                args=tuple(
                    self._rebind_inherited_output_expr(arg, parent_unit=parent_unit)
                    for arg in expr.args
                ),
            )
        if isinstance(expr, model.ExprSet):
            return model.ExprSet(
                items=tuple(
                    self._rebind_inherited_output_expr(item, parent_unit=parent_unit)
                    for item in expr.items
                )
            )
        if isinstance(expr, model.ExprBinary):
            return model.ExprBinary(
                op=expr.op,
                left=self._rebind_inherited_output_expr(expr.left, parent_unit=parent_unit),
                right=self._rebind_inherited_output_expr(expr.right, parent_unit=parent_unit),
            )
        return expr

    def _rebind_inherited_output_readable_block(
        self,
        block: model.ReadableBlock,
        *,
        parent_unit: IndexedUnit,
    ) -> model.ReadableBlock:
        return model.ReadableBlock(
            kind=block.kind,
            key=block.key,
            title=block.title,
            payload=self._rebind_inherited_output_readable_payload(
                block.payload,
                parent_unit=parent_unit,
            ),
            requirement=block.requirement,
            when_expr=(
                None
                if block.when_expr is None
                else self._rebind_inherited_output_expr(block.when_expr, parent_unit=parent_unit)
            ),
            item_schema=block.item_schema,
            row_schema=block.row_schema,
            anonymous=block.anonymous,
            legacy_section=block.legacy_section,
        )

    def _rebind_inherited_output_readable_payload(
        self,
        payload: model.ReadablePayload,
        *,
        parent_unit: IndexedUnit,
    ) -> model.ReadablePayload:
        if payload is None:
            return None
        if isinstance(payload, tuple):
            rebound_items: list[object] = []
            changed = False
            for item in payload:
                if isinstance(item, model.ReadableBlock):
                    rebound_item = self._rebind_inherited_output_readable_block(
                        item,
                        parent_unit=parent_unit,
                    )
                    changed = changed or rebound_item != item
                    rebound_items.append(rebound_item)
                    continue
                rebound_items.append(item)
            return payload if not changed else tuple(rebound_items)
        if isinstance(payload, model.ReadableTableData):
            return model.ReadableTableData(
                columns=payload.columns,
                rows=tuple(
                    model.ReadableTableRow(
                        key=row.key,
                        cells=tuple(
                            model.ReadableTableCell(
                                key=cell.key,
                                text=cell.text,
                                body=(
                                    None
                                    if cell.body is None
                                    else tuple(
                                        (
                                            self._rebind_inherited_output_readable_block(
                                                item,
                                                parent_unit=parent_unit,
                                            )
                                            if isinstance(item, model.ReadableBlock)
                                            else item
                                        )
                                        for item in cell.body
                                    )
                                ),
                            )
                            for cell in row.cells
                        ),
                    )
                    for row in payload.rows
                ),
                notes=payload.notes,
                row_schema=payload.row_schema,
            )
        return payload

    def _rebind_inherited_trust_surface_item(
        self,
        item: model.TrustSurfaceItem,
        *,
        parent_unit: IndexedUnit,
    ) -> model.TrustSurfaceItem:
        if item.when_expr is None:
            return item
        return model.TrustSurfaceItem(
            path=item.path,
            when_expr=self._rebind_inherited_output_expr(
                item.when_expr,
                parent_unit=parent_unit,
            ),
        )

    def _inherited_output_ref_has_parent_decl(
        self,
        ref: model.NameRef,
        *,
        parent_unit: IndexedUnit,
    ) -> bool:
        for registry_name in (
            "render_profiles_by_name",
            "analyses_by_name",
            "decisions_by_name",
            "schemas_by_name",
            "documents_by_name",
            "workflows_by_name",
            "route_onlys_by_name",
            "groundings_by_name",
            "reviews_by_name",
            "skills_blocks_by_name",
            "inputs_blocks_by_name",
            "inputs_by_name",
            "input_sources_by_name",
            "outputs_blocks_by_name",
            "outputs_by_name",
            "output_targets_by_name",
            "output_shapes_by_name",
            "output_schemas_by_name",
            "skills_by_name",
            "agents_by_name",
            "enums_by_name",
        ):
            if self._ref_exists_in_registry(ref, unit=parent_unit, registry_name=registry_name):
                return True
        return False

    def _resolve_output_attachment(
        self,
        output_decl: model.OutputDecl,
        *,
        parent_output: model.OutputDecl,
        owner_label: str,
        parent_label: str | None,
        key: str,
    ) -> tuple[object, bool]:
        parent_has = self._output_decl_has_attachment(parent_output, key)
        child_mode = getattr(output_decl, f"{key}_mode")
        child_value = self._output_decl_attachment_value(output_decl, key)

        if child_mode == "inherit":
            if not parent_has:
                raise CompileError(f"Cannot inherit undefined output entry in {parent_label}: {key}")
            return self._output_decl_attachment_value(parent_output, key), True

        if child_mode == "override":
            if not parent_has:
                raise CompileError(
                    f"E001 Cannot override undefined output entry in {parent_label}: {key}"
                )
            return child_value, True

        if child_mode == "set":
            if parent_has:
                raise CompileError(f"Inherited output requires `override {key}` in {owner_label}")
            return child_value, False

        return (None if not parent_has else self._output_decl_attachment_value(parent_output, key), False)

    def _output_decl_has_attachment(self, output_decl: model.OutputDecl, key: str) -> bool:
        value = self._output_decl_attachment_value(output_decl, key)
        if key == "trust_surface":
            return bool(value)
        return value is not None

    def _output_decl_attachment_value(self, output_decl: model.OutputDecl, key: str) -> object:
        if key == "render_profile":
            return output_decl.render_profile_ref
        if key == "trust_surface":
            return output_decl.trust_surface
        return getattr(output_decl, key)

    def _resolve_final_output_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        local_decl = self._resolve_local_output_decl(ref.declaration_name, unit=target_unit)
        if local_decl is not None:
            return target_unit, local_decl

        other_kind = self._named_non_output_decl_kind(ref.declaration_name, unit=target_unit)
        if other_kind is not None:
            raise CompileError(
                "E211 final_output must point at an output declaration in "
                f"{owner_label}: {_dotted_ref_name(ref)} resolves to {other_kind}"
            )
        return self._resolve_output_decl(ref, unit=unit)

    def _resolve_final_output_json_shape_summary(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
    ) -> FinalOutputJsonShapeSummary | None:
        if isinstance(value, (str, model.AddressableRef)):
            return None
        resolved_shape = self._try_resolve_output_shape_decl(value, unit=unit)
        if resolved_shape is None:
            return None

        shape_unit, shape_decl = resolved_shape
        shape_scalars, _shape_sections, shape_extras = self._split_record_items(
            shape_decl.items,
            scalar_keys={"schema", "example_file"},
            owner_label=f"output shape {shape_decl.name}",
        )
        schema_item = shape_scalars.get("schema")
        if schema_item is None or not isinstance(schema_item.value, model.NameRef):
            return None

        schema_unit, schema_decl = self._resolve_output_schema_decl(
            schema_item.value,
            unit=shape_unit,
        )
        lowered_schema = self._lower_output_schema_decl(schema_decl, unit=schema_unit)
        self._validate_final_output_lowered_schema(
            lowered_schema,
            owner_label=f"output schema {schema_decl.name}",
        )
        example_file_item = shape_scalars.get("example_file")
        if example_file_item is not None:
            raise CompileError(
                "E215 final_output example_file is retired in "
                f"output shape {shape_decl.name}: retire `example_file`; add optional "
                f"`example:` to output schema {schema_decl.name} only when you want a "
                "rendered example block"
            )
        example_value = self._output_schema_example_value(
            schema_decl,
            owner_label=f"output schema {schema_decl.name}",
        )
        payload_rows = self._build_output_schema_payload_rows(schema_data=lowered_schema)
        example_text: str | None = None
        if example_value is not None:
            example_instance = self._materialize_output_schema_example_value(
                example_value,
                owner_label=f"output schema {schema_decl.name}.example",
            )
            self._validate_final_output_example_instance(
                example_instance,
                lowered_schema,
                owner_label=f"output schema {schema_decl.name}",
            )
            example_text = json.dumps(example_instance, indent=2) + "\n"
        return FinalOutputJsonShapeSummary(
            shape_unit=shape_unit,
            shape_decl=shape_decl,
            schema_unit=schema_unit,
            schema_decl=schema_decl,
            schema_profile="OpenAIStructuredOutput",
            lowered_schema=lowered_schema,
            payload_rows=payload_rows,
            example_text=example_text,
            extra_items=shape_extras,
        )

    def _resolve_output_render_profiles(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        files_section: model.RecordSection | None,
        shape_item: model.RecordScalar | None,
    ) -> tuple[ResolvedRenderProfile | None, ResolvedRenderProfile | None]:
        explicit_render_profile: ResolvedRenderProfile | None = None
        if decl.render_profile_ref is not None:
            if files_section is not None:
                raise CompileError(
                    f"Output render_profile requires one markdown-bearing output artifact in {decl.name}"
                )
            if shape_item is None or not (
                self._is_markdown_shape_value(shape_item.value, unit=unit)
                or self._is_comment_shape_value(shape_item.value, unit=unit)
            ):
                raise CompileError(
                    f"Output render_profile requires a markdown-bearing shape in output {decl.name}"
                )
            explicit_render_profile = self._resolve_render_profile_ref(
                decl.render_profile_ref,
                unit=unit,
            )

        default_render_profile: ResolvedRenderProfile | None = None
        if files_section is None and shape_item is not None:
            if self._is_comment_shape_value(shape_item.value, unit=unit):
                default_render_profile = ResolvedRenderProfile(name="CommentMarkdown")
            elif self._is_markdown_shape_value(shape_item.value, unit=unit):
                default_render_profile = ResolvedRenderProfile(name="ArtifactMarkdown")

        return explicit_render_profile, (explicit_render_profile or default_render_profile)

    def _resolve_io_field_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(ref)}"
                )
            target_unit, inputs_decl = self._resolve_inputs_block_ref(ref, unit=unit)
            return self._resolve_inputs_decl(inputs_decl, unit=target_unit)

        if self._ref_exists_in_registry(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(ref)}"
            )
        target_unit, outputs_decl = self._resolve_outputs_block_ref(ref, unit=unit)
        return self._resolve_outputs_decl(
            outputs_decl,
            unit=target_unit,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )

    def _resolve_io_field_patch(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        parent_ref = field.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing parent ref in {owner_label}"
            )
        if not isinstance(field.value, model.IoBody) or field.title is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing body in {owner_label}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs patch fields must inherit from inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_inputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
            inheritance_parent_body = parent_body
        else:
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="inputs_blocks_by_name",
            ):
                raise CompileError(
                    "Outputs patch fields must inherit from outputs blocks, not inputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_outputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_outputs_decl(
                parent_decl,
                unit=parent_unit,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            inheritance_parent_body = parent_body
            if excluded_output_keys:
                inheritance_parent_body = self._resolve_outputs_decl(
                    parent_decl,
                    unit=parent_unit,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=frozenset(),
                )

        return self._resolve_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_io=parent_body,
            inheritance_parent_io=inheritance_parent_body,
            parent_label=f"{field_kind} {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}",
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )

    def _resolve_input_source_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_INPUT_SOURCES.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.input_sources_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(
                    local_decl,
                    owner_label=f"input source {local_decl.name}",
                )

        target_unit, decl = self._resolve_input_source_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"input source {decl.name}")

    def _resolve_output_target_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ResolvedOutputTargetSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_OUTPUT_TARGETS.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.output_targets_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._output_target_spec_from_decl(
                    local_decl,
                    unit=unit,
                    owner_label=f"output target {local_decl.name}",
                )

        target_unit, decl = self._resolve_output_target_decl(ref, unit=unit)
        return self._output_target_spec_from_decl(
            decl,
            unit=target_unit,
            owner_label=f"output target {decl.name}",
        )

    def _output_target_spec_from_decl(
        self,
        decl: model.OutputTargetDecl,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedOutputTargetSpec:
        required_keys, optional_keys = self._config_keys_from_decl(
            decl,
            owner_label=owner_label,
        )
        delivery_skill: ResolvedOutputTargetDeliverySkill | None = None
        if decl.delivery_skill_ref is not None:
            _skill_unit, skill_decl = self._resolve_skill_decl(
                decl.delivery_skill_ref,
                unit=unit,
            )
            delivery_skill = ResolvedOutputTargetDeliverySkill(title=skill_decl.title)
        return ResolvedOutputTargetSpec(
            title=decl.title,
            required_keys=required_keys,
            optional_keys=optional_keys,
            delivery_skill=delivery_skill,
        )

    def _resolve_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        outputs_key = (
            unit.module_parts,
            outputs_decl.name,
            review_output_contexts,
            route_output_contexts,
            excluded_output_keys,
        )
        cached = self._resolved_outputs_cache.get(outputs_key)
        if cached is not None:
            return cached

        if outputs_key in self._outputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name, _review_keys, _route_keys, _excluded_keys in [
                    *self._outputs_resolution_stack,
                    outputs_key,
                ]
            )
            raise CompileError(f"Cyclic outputs inheritance: {cycle}")

        self._outputs_resolution_stack.append(outputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            inheritance_parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if outputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_outputs_decl(
                    outputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_outputs_decl(
                    parent_decl,
                    unit=parent_unit,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                inheritance_parent_io = parent_io
                if excluded_output_keys:
                    inheritance_parent_io = self._resolve_outputs_decl(
                        parent_decl,
                        unit=parent_unit,
                        review_output_contexts=review_output_contexts,
                        route_output_contexts=route_output_contexts,
                        excluded_output_keys=frozenset(),
                    )
                parent_label = f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_io_body(
                outputs_decl.body,
                unit=unit,
                field_kind="outputs",
                owner_label=_dotted_decl_name(unit.module_parts, outputs_decl.name),
                parent_io=parent_io,
                inheritance_parent_io=inheritance_parent_io,
                parent_label=parent_label,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            self._resolved_outputs_cache[outputs_key] = resolved
            return resolved
        finally:
            self._outputs_resolution_stack.pop()

    def _resolve_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_io: ResolvedIoBody | None = None,
        inheritance_parent_io: ResolvedIoBody | None = None,
        parent_label: str | None = None,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{field_kind} prose",
                ambiguous_label=f"{field_kind} prose interpolation ref",
            )
            for line in io_body.preamble
        )
        if parent_io is None:
            resolved_items = self._resolve_non_inherited_io_items(
                io_body.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            return ResolvedIoBody(
                title=io_body.title,
                preamble=resolved_preamble,
                items=resolved_items,
                artifacts=self._resolved_io_body_artifacts(resolved_items),
                bindings=self._resolved_io_body_bindings(resolved_items),
            )

        inherited_parent_io = inheritance_parent_io if inheritance_parent_io is not None else parent_io
        unkeyed_parent_titles = [
            item.section.title for item in inherited_parent_io.items if isinstance(item, ResolvedIoRef)
        ]
        if unkeyed_parent_titles:
            details = ", ".join(unkeyed_parent_titles)
            raise CompileError(
                f"Cannot inherit {field_kind} block with unkeyed top-level refs in {parent_label}: {details}"
            )

        parent_items_by_key = {
            item.key: item for item in inherited_parent_io.items if isinstance(item, ResolvedIoSection)
        }
        visible_parent_items_by_key = {
            item.key: item for item in parent_io.items if isinstance(item, ResolvedIoSection)
        }
        resolved_items: list[ResolvedIoItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in io_body.items:
            if isinstance(item, model.RecordRef):
                resolved_item = self._resolve_io_ref_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_item is not None:
                    resolved_items.append(resolved_item)
                continue

            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.IoSection):
                resolved_item = self._resolve_io_section_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    binding_path=(item.key,),
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_item is not None:
                    resolved_items.append(resolved_item)
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined {field_kind} entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                visible_parent_item = visible_parent_items_by_key.get(key)
                if visible_parent_item is not None:
                    resolved_items.append(visible_parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined {field_kind} entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if not isinstance(item, model.OverrideIoSection):
                raise CompileError(
                    f"Internal compiler error: unsupported {field_kind} override in {owner_label}: {type(item).__name__}"
                )
            resolved_bucket = self._resolve_contract_bucket_items(
                item.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=(
                    f"{field_kind} section `{item.title if item.title is not None else parent_item.section.title}`"
                ),
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                path_prefix=(key,),
                excluded_output_keys=excluded_output_keys,
            )
            bindings = list(resolved_bucket.bindings)
            if not resolved_bucket.has_keyed_children and len(resolved_bucket.direct_artifacts) == 1:
                bindings.append(
                    ContractBinding(
                        binding_path=(key,),
                        artifact=resolved_bucket.direct_artifacts[0],
                    )
                )
            if resolved_bucket.body or resolved_bucket.artifacts or bindings:
                resolved_items.append(
                    ResolvedIoSection(
                        key=key,
                        section=CompiledSection(
                            title=item.title if item.title is not None else parent_item.section.title,
                            body=resolved_bucket.body,
                        ),
                        artifacts=resolved_bucket.artifacts,
                        bindings=tuple(bindings),
                    )
                )

        missing_keys = [
            item.key
            for item in inherited_parent_io.items
            if isinstance(item, ResolvedIoSection) and item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited {field_kind} entry in {owner_label}: {missing}"
            )

        return ResolvedIoBody(
            title=io_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
            artifacts=self._resolved_io_body_artifacts(tuple(resolved_items)),
            bindings=self._resolved_io_body_bindings(tuple(resolved_items)),
        )

    def _resolve_io_section_item(
        self,
        item: model.IoSection,
        *,
        unit: IndexedUnit,
        field_kind: str,
        binding_path: tuple[str, ...],
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoSection | None:
        resolved_bucket = self._resolve_contract_bucket_items(
            item.items,
            unit=unit,
            field_kind=field_kind,
            owner_label=f"{field_kind} section `{item.title if item.title is not None else item.key}`",
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            path_prefix=binding_path,
            excluded_output_keys=excluded_output_keys,
        )
        bindings = list(resolved_bucket.bindings)
        if not resolved_bucket.has_keyed_children and len(resolved_bucket.direct_artifacts) == 1:
            bindings.append(
                ContractBinding(
                    binding_path=binding_path,
                    artifact=resolved_bucket.direct_artifacts[0],
                )
            )
        if not resolved_bucket.body and not resolved_bucket.artifacts and not bindings:
            return None
        section = (
            self._lower_omitted_io_section(
                item,
                field_kind=field_kind,
                resolved_bucket=resolved_bucket,
            )
            if item.title is None
            else CompiledSection(
                title=item.title,
                body=resolved_bucket.body,
            )
        )
        return ResolvedIoSection(
            key=item.key,
            section=section,
            artifacts=resolved_bucket.artifacts,
            bindings=tuple(bindings),
        )

    def _resolve_io_section_title(
        self,
        item: model.IoSection,
        *,
        field_kind: str,
        resolved_bucket: ResolvedContractBucket,
    ) -> str:
        if item.title is not None:
            return item.title
        if (
            resolved_bucket.has_keyed_children
            or len(resolved_bucket.direct_artifacts) != 1
            or len(resolved_bucket.direct_sections) != 1
        ):
            raise CompileError(
                f"Omitted title in {field_kind} section `{item.key}` requires exactly one lowerable direct declaration"
            )
        return resolved_bucket.direct_sections[0][1].title

    def _lower_omitted_io_section(
        self,
        item: model.IoSection,
        *,
        field_kind: str,
        resolved_bucket: ResolvedContractBucket,
    ) -> CompiledSection:
        section_title = self._resolve_io_section_title(
            item,
            field_kind=field_kind,
            resolved_bucket=resolved_bucket,
        )
        direct_index, direct_section = resolved_bucket.direct_sections[0]
        lowered_body = (
            *resolved_bucket.body[:direct_index],
            *direct_section.body,
            *resolved_bucket.body[direct_index + 1 :],
        )
        return CompiledSection(title=section_title, body=lowered_body)

    def _resolve_io_ref_item(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoRef | None:
        resolved_ref = self._resolve_contract_bucket_ref_entry(
            item,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )
        if resolved_ref is None:
            return None
        section, artifact = resolved_ref
        return ResolvedIoRef(
            section=section,
            artifact=artifact,
        )

    def _resolve_output_field_node(
        self,
        decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> AddressableNode:
        def resolve_from_root(
            root_decl: model.OutputDecl,
            *,
            root_unit: IndexedUnit,
            field_path: tuple[str, ...],
        ) -> AddressableNode | None:
            current_node = AddressableNode(unit=root_unit, root_decl=root_decl, target=root_decl)
            if not field_path:
                return current_node
            for segment in field_path:
                children = self._get_addressable_children(current_node)
                if children is None or segment not in children:
                    return None
                current_node = children[segment]
            return current_node

        current_node = resolve_from_root(decl, root_unit=unit, field_path=path)
        if current_node is not None:
            return current_node

        if review_semantics is not None and path:
            semantic_field_path = self._review_semantic_field_path(review_semantics, path[0])
            if semantic_field_path is not None:
                semantic_unit, semantic_output_decl = self._resolve_review_semantic_output_decl(
                    review_semantics
                )
                semantic_node = resolve_from_root(
                    semantic_output_decl,
                    root_unit=semantic_unit,
                    field_path=(*semantic_field_path, *path[1:]),
                )
                if semantic_node is not None:
                    return semantic_node

        raise CompileError(
            f"Unknown output field on {surface_label} in {owner_label}: "
            f"{decl.name}.{'.'.join(path)}"
        )
