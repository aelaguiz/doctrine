from __future__ import annotations

import json
from dataclasses import replace

from doctrine import model
from doctrine._compiler.constants import _BUILTIN_INPUT_SOURCES, _BUILTIN_OUTPUT_TARGETS
from doctrine._compiler.final_output_diagnostics import final_output_compile_error
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.output_diagnostics import output_compile_error, output_related_site
from doctrine._compiler.resolved_types import (
    AddressableNode,
    CompileError,
    CompiledSection,
    ConfigSpec,
    ContractBinding,
    FinalOutputRouteBinding,
    FinalOutputJsonShapeSummary,
    IndexedUnit,
    OutputDeclKey,
    PreviousTurnAgentContext,
    ResolvedPreviousTurnInputSpec,
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

    def _authored_source_span(self, value: object | None) -> model.SourceSpan | None:
        return getattr(value, "source_span", None)

    def _output_decl_item_by_key(
        self,
        output_decl: model.OutputDecl,
        key: str,
    ) -> object | None:
        return next((item for item in output_decl.items if self._output_item_key(item) == key), None)

    def _output_shape_item_by_key(
        self,
        output_shape_decl: model.OutputShapeDecl,
        key: str,
    ) -> object | None:
        return next(
            (item for item in output_shape_decl.items if self._output_item_key(item) == key),
            None,
        )

    def _output_shape_missing_related_sites(
        self,
        *,
        parent_output_shape: model.OutputShapeDecl,
        parent_unit: IndexedUnit | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None:
            return ()
        related = []
        for key in missing_keys:
            parent_item = self._output_shape_item_by_key(parent_output_shape, key)
            if parent_item is None:
                continue
            related.append(
                output_related_site(
                    label=f"inherited `{key}` entry",
                    unit=parent_unit,
                    source_span=self._authored_source_span(parent_item),
                )
            )
        return tuple(related)

    def _output_missing_related_sites(
        self,
        *,
        parent_output: model.OutputDecl,
        parent_unit: IndexedUnit | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None:
            return ()
        related = []
        for key in missing_keys:
            parent_item = self._output_decl_item_by_key(parent_output, key)
            if parent_item is None:
                continue
            related.append(
                output_related_site(
                    label=f"inherited `{key}` entry",
                    unit=parent_unit,
                    source_span=self._authored_source_span(parent_item),
                )
            )
        return tuple(related)

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
                unit=unit,
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
        unit: IndexedUnit,
        owner_label: str,
        parent_unit: IndexedUnit | None = None,
        parent_output_shape: model.OutputShapeDecl | None = None,
        parent_label: str | None = None,
    ) -> model.OutputShapeDecl:
        if parent_output_shape is None:
            patch_key = self._first_output_shape_patch_key(output_shape_decl)
            if patch_key is not None:
                patch_item = self._output_shape_item_by_key(output_shape_decl, patch_key)
                raise output_compile_error(
                    code="E252",
                    summary="Output patch requires an inherited output",
                    detail=(
                        f"`inherit` for key `{patch_key}` requires an inherited output in "
                        f"`{owner_label}`."
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(patch_item)
                    or output_shape_decl.source_span,
                )
            override_key = self._first_output_shape_override_key(output_shape_decl)
            if override_key is not None:
                override_item = self._output_shape_item_by_key(output_shape_decl, override_key)
                raise output_compile_error(
                    code="E252",
                    summary="Output patch requires an inherited output",
                    detail=(
                        f"`override` for key `{override_key}` requires an inherited output in "
                        f"`{owner_label}`."
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(override_item)
                    or output_shape_decl.source_span,
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
            raise output_compile_error(
                code="E254",
                summary="Inherited output needs keyed top-level entries",
                detail=(
                    f"Output `{parent_label}` contains unkeyed top-level items: {details}."
                ),
                unit=parent_unit or unit,
                source_span=inherited_parent_output_shape.source_span,
                hints=(
                    "Give inherited outputs stable keyed top-level items before patching them.",
                ),
            )

        parent_items_by_key = {
            item.key
            : item
            for item in inherited_parent_output_shape.items
            if self._output_item_key(item) is not None
        }
        resolved_items: list[model.OutputRecordItem] = []
        emitted_items: dict[str, object] = {}
        accounted_keys: set[str] = set()

        for item in output_shape_decl.items:
            key = self._output_item_key(item)
            if key is None:
                resolved_items.append(item)
                continue

            if key in emitted_items:
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=f"Output `{owner_label}` repeats output item key `{key}`.",
                    unit=unit,
                    source_span=self._authored_source_span(item),
                    related=(
                        output_related_site(
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
                    raise output_compile_error(
                        code="E253",
                        summary="Cannot inherit undefined output entry",
                        detail=(
                            f"Output `{owner_label}` cannot inherit undefined key `{key}`."
                        ),
                        unit=unit,
                        source_span=item.source_span or output_shape_decl.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if self._is_output_override_item(item):
                if parent_item is None:
                    raise output_compile_error(
                        code="E001",
                        summary="Cannot override undefined inherited entry",
                        detail=(
                            f"Cannot override undefined output shape entry in "
                            f"{parent_label}: {key}"
                        ),
                        unit=unit,
                        source_span=self._authored_source_span(item)
                        or output_shape_decl.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(
                    self._resolve_output_override_item(
                        item,
                        unit=unit,
                        parent_item=parent_item,
                        parent_unit=parent_unit or unit,
                        owner_label=owner_label,
                    )
                )
                continue

            if parent_item is not None:
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=(
                        f"Output `{owner_label}` must use `override {key}` when it patches "
                        "an inherited output item."
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(item)
                    or output_shape_decl.source_span,
                    related=(
                        output_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit or unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )

            resolved_items.append(item)

        missing_keys = tuple(
            item.key
            for item in inherited_parent_output_shape.items
            if self._output_item_key(item) is not None and item.key not in accounted_keys
        )
        if missing_keys:
            raise output_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=(
                    f"Missing inherited output shape entry in {owner_label}: "
                    f"{', '.join(missing_keys)}"
                ),
                unit=unit,
                source_span=output_shape_decl.source_span,
                related=self._output_shape_missing_related_sites(
                    parent_output_shape=inherited_parent_output_shape,
                    parent_unit=parent_unit,
                    missing_keys=missing_keys,
                ),
            )

        return model.OutputShapeDecl(
            name=output_shape_decl.name,
            title=output_shape_decl.title,
            items=tuple(resolved_items),
            parent_ref=None,
            source_span=output_shape_decl.source_span,
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
                patch_item = self._output_decl_item_by_key(output_decl, patch_key)
                raise output_compile_error(
                    code="E252",
                    summary="Output patch requires an inherited output",
                    detail=(
                        f"`inherit` for key `{patch_key}` requires an inherited output in "
                        f"`{owner_label}`."
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(patch_item) or output_decl.source_span,
                )
            override_key = self._first_output_override_key(output_decl)
            if override_key is not None:
                override_item = self._output_decl_item_by_key(output_decl, override_key)
                raise output_compile_error(
                    code="E252",
                    summary="Output patch requires an inherited output",
                    detail=(
                        f"`override` for key `{override_key}` requires an inherited output in "
                        f"`{owner_label}`."
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(override_item)
                    or output_decl.source_span,
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
            raise output_compile_error(
                code="E254",
                summary="Inherited output needs keyed top-level entries",
                detail=(
                    f"Output `{parent_label}` contains unkeyed top-level items: {details}."
                ),
                unit=parent_unit or unit,
                source_span=inherited_parent_output.source_span,
                hints=(
                    "Give inherited outputs stable keyed top-level items before patching them.",
                ),
            )

        parent_items_by_key = {
            item.key
            : item
            for item in inherited_parent_output.items
            if self._output_item_key(item) is not None
        }
        resolved_items: list[model.OutputRecordItem] = []
        emitted_items: dict[str, object] = {}
        accounted_keys: set[str] = set()

        for item in output_decl.items:
            key = self._output_item_key(item)
            if key is None:
                resolved_items.append(item)
                continue

            if key in emitted_items:
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=f"Output `{owner_label}` repeats output item key `{key}`.",
                    unit=unit,
                    source_span=self._authored_source_span(item),
                    related=(
                        output_related_site(
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
                    raise output_compile_error(
                        code="E253",
                        summary="Cannot inherit undefined output entry",
                        detail=(
                            f"Output `{owner_label}` cannot inherit undefined key `{key}`."
                        ),
                        unit=unit,
                        source_span=item.source_span or output_decl.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if self._is_output_override_item(item):
                if parent_item is None:
                    raise output_compile_error(
                        code="E001",
                        summary="Cannot override undefined inherited entry",
                        detail=(
                            f"Cannot override undefined output entry in {parent_label}: {key}"
                        ),
                        unit=unit,
                        source_span=self._authored_source_span(item) or output_decl.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(
                    self._resolve_output_override_item(
                        item,
                        unit=unit,
                        parent_item=parent_item,
                        parent_unit=parent_unit or unit,
                        owner_label=owner_label,
                    )
                )
                continue

            if parent_item is not None:
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=(
                        f"Output `{owner_label}` must use `override {key}` when it patches "
                        "an inherited output item."
                    ),
                    unit=unit,
                    source_span=self._authored_source_span(item) or output_decl.source_span,
                    related=(
                        output_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit or unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )

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
            raise output_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=f"Missing inherited output entry in {owner_label}: {', '.join(missing_keys)}",
                unit=unit,
                source_span=output_decl.source_span,
                related=self._output_missing_related_sites(
                    parent_output=inherited_parent_output,
                    parent_unit=parent_unit,
                    missing_keys=tuple(missing_keys),
                ),
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
            source_span=output_decl.source_span,
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
        unit: IndexedUnit,
        parent_item: model.OutputRecordItem,
        parent_unit: IndexedUnit,
        owner_label: str,
    ) -> model.OutputRecordItem:
        key = item.key
        if isinstance(item, model.OutputOverrideRecordScalar):
            if not isinstance(parent_item, model.RecordScalar):
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=(
                        f"Output `{owner_label}` overrides entry `{key}` with the wrong kind."
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            return model.RecordScalar(
                key=key,
                value=item.value,
                body=item.body,
                source_span=item.source_span,
            )

        if isinstance(item, model.OutputOverrideRecordSection):
            if not isinstance(parent_item, model.RecordSection):
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=(
                        f"Output `{owner_label}` overrides entry `{key}` with the wrong kind."
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            return model.RecordSection(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                items=item.items,
                source_span=item.source_span,
            )

        if isinstance(item, model.OutputOverrideGuardedOutputSection):
            if not isinstance(parent_item, model.GuardedOutputSection):
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=(
                        f"Output `{owner_label}` overrides entry `{key}` with the wrong kind."
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            return model.GuardedOutputSection(
                key=key,
                title=item.title if item.title is not None else parent_item.title,
                when_expr=item.when_expr,
                items=item.items,
                source_span=item.source_span,
            )

        if isinstance(item, model.OutputOverrideGuardedOutputScalar):
            if not isinstance(parent_item, model.GuardedOutputScalar):
                raise output_compile_error(
                    code="E255",
                    summary="Invalid output inheritance patch",
                    detail=(
                        f"Output `{owner_label}` overrides entry `{key}` with the wrong kind."
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        output_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit,
                            source_span=self._authored_source_span(parent_item),
                        ),
                    ),
                )
            return model.GuardedOutputScalar(
                key=key,
                value=item.value,
                when_expr=item.when_expr,
                body=item.body,
                source_span=item.source_span,
            )

        if not isinstance(parent_item, model.ReadableBlock):
            raise output_compile_error(
                code="E255",
                summary="Invalid output inheritance patch",
                detail=f"Output `{owner_label}` overrides entry `{key}` with the wrong kind.",
                unit=unit,
                source_span=item.source_span,
                related=(
                    output_related_site(
                        label=f"inherited `{key}` entry",
                        unit=parent_unit,
                        source_span=self._authored_source_span(parent_item),
                    ),
                ),
            )
        if item.kind != parent_item.kind:
            raise output_compile_error(
                code="E255",
                summary="Invalid output inheritance patch",
                detail=f"Output `{owner_label}` overrides entry `{key}` with the wrong kind.",
                unit=unit,
                source_span=item.source_span,
                related=(
                    output_related_site(
                        label=f"inherited `{key}` entry",
                        unit=parent_unit,
                        source_span=self._authored_source_span(parent_item),
                    ),
                ),
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
            source_span=item.source_span,
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
                source_span=item.source_span,
            )
        if isinstance(item, model.RecordSection):
            return model.RecordSection(
                key=item.key,
                title=item.title,
                items=tuple(
                    self._rebind_inherited_output_item(child, parent_unit=parent_unit)
                    for child in item.items
                ),
                source_span=item.source_span,
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
                source_span=item.source_span,
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
                source_span=item.source_span,
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
                source_span=item.source_span,
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
            source_span=block.source_span,
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
                                source_span=cell.source_span,
                            )
                            for cell in row.cells
                        ),
                        source_span=row.source_span,
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
            source_span=item.source_span,
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
        source_span: model.SourceSpan | None = None,
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        local_decl = self._resolve_local_output_decl(ref.declaration_name, unit=target_unit)
        if local_decl is not None:
            return target_unit, local_decl

        other_kind = self._named_non_output_decl_kind(ref.declaration_name, unit=target_unit)
        if other_kind is not None:
            raise final_output_compile_error(
                code="E211",
                summary="Final output must point at output declaration",
                detail=(
                    f"`final_output` in {owner_label} points at `{_dotted_ref_name(ref)}`, "
                    f"which resolves to {other_kind} instead of an `output` declaration."
                ),
                unit=unit,
                source_span=source_span,
                hints=("Point `final_output:` at a declared `output`.",),
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
            path=schema_unit.prompt_file.source_path,
            source_span=schema_decl.source_span,
        )
        example_file_item = shape_scalars.get("example_file")
        if example_file_item is not None:
            raise final_output_compile_error(
                code="E215",
                summary="Final output example_file is retired",
                detail=(
                    f"`final_output` in output shape {shape_decl.name} still uses retired "
                    f"`example_file`. retire `example_file`; add optional `example:` to "
                    f"output schema {schema_decl.name} only when you want a rendered "
                    "example block"
                ),
                unit=shape_unit,
                source_span=example_file_item.source_span or shape_decl.source_span,
                hints=(
                    "Delete `example_file` from the `output shape`.",
                    "Add `example:` on `output schema` only when you want a rendered example block.",
                ),
            )
        example_item = self._output_schema_example_item(
            schema_decl,
            owner_label=f"output schema {schema_decl.name}",
        )
        example_value = None if example_item is None else example_item.value
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
                path=schema_unit.prompt_file.source_path,
                source_span=example_item.source_span if example_item is not None else schema_decl.source_span,
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

    def _resolve_final_output_route_binding(
        self,
        *,
        agent_name: str,
        field: model.FinalOutputField,
        unit: IndexedUnit,
        agent_contract,
    ) -> FinalOutputRouteBinding | None:
        if field.route_path is None:
            return None

        owner_label = f"agent {agent_name} final_output.route"
        output_unit, output_decl = self._resolve_final_output_decl(
            field.value,
            unit=unit,
            owner_label=f"agent {agent_name} final_output",
            source_span=field.source_span,
        )
        output_key = (output_unit.module_parts, output_decl.name)
        if output_key not in agent_contract.outputs:
            raise final_output_compile_error(
                code="E212",
                summary="Final output is not emitted by the concrete turn",
                detail=(
                    f"Agent `{agent_name}` declares `final_output` as "
                    f"`{_dotted_decl_name(output_unit.module_parts, output_decl.name)}`, "
                    "but that output is not emitted by the concrete turn."
                ),
                unit=unit,
                source_span=field.source_span,
                hints=(
                    "Add the output to the agent `outputs:` contract, or point `final_output:` at one that already is.",
                ),
            )

        scalar_items, section_items, _extras = self._split_record_items(
            output_decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {output_decl.name}",
        )
        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        files_section = section_items.get("files")
        if (
            files_section is not None
            or target_item is None
            or shape_item is None
            or not isinstance(target_item.value, model.NameRef)
            or not self._is_builtin_turn_response_target_ref(target_item.value)
        ):
            raise CompileError(
                "final_output.route requires one TurnResponse output in "
                f"{owner_label}: {_dotted_decl_name(output_unit.module_parts, output_decl.name)}"
            )

        json_summary = self._resolve_final_output_json_shape_summary(
            shape_item.value,
            unit=output_unit,
        )
        if json_summary is None:
            raise CompileError(
                "final_output.route requires a structured final output with an output schema in "
                f"{owner_label}: {_dotted_decl_name(output_unit.module_parts, output_decl.name)}"
            )

        route_node = self._resolve_output_schema_field_node(
            json_summary.schema_decl,
            path=field.route_path,
            unit=json_summary.schema_unit,
            owner_label=owner_label,
            surface_label="output schema route fields",
        )
        if not isinstance(route_node.target, model.OutputSchemaRouteField):
            raise CompileError(
                "final_output.route must bind a `route field` in "
                f"{owner_label}: {json_summary.schema_decl.name}.{'.'.join(field.route_path)}"
            )

        route_parts = self._collect_output_schema_node_parts(
            route_node.target.items,
            unit=json_summary.schema_unit,
            owner_label=(
                f"output schema {json_summary.schema_decl.name}.{'.'.join(field.route_path)}"
            ),
        )
        if not route_parts.route_choices:
            raise CompileError(
                "route field must declare at least one route choice in "
                f"{owner_label}: {json_summary.schema_decl.name}.{'.'.join(field.route_path)}"
            )
        return FinalOutputRouteBinding(
            output_key=output_key,
            output_unit=output_unit,
            output_decl=output_decl,
            schema_unit=json_summary.schema_unit,
            schema_decl=json_summary.schema_decl,
            field_path=field.route_path,
            route_field=route_node.target,
            null_behavior="no_route" if route_parts.nullable else "invalid",
            choices=route_parts.route_choices,
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
                    unit=unit,
                    owner_label=f"input source {local_decl.name}",
                )

        target_unit, decl = self._resolve_input_source_decl(ref, unit=unit)
        return self._config_spec_from_decl(
            decl,
            unit=target_unit,
            owner_label=f"input source {decl.name}",
        )

    def _is_rally_previous_turn_input_source_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        try:
            target_unit, decl = self._resolve_input_source_decl(ref, unit=unit)
        except CompileError:
            return False
        return (
            target_unit.module_parts == ("rally", "base_agent")
            and decl.name == "RallyPreviousTurnOutput"
        )

    def _previous_turn_agent_context(
        self,
        *,
        agent_key: tuple[tuple[str, ...], str] | None,
    ) -> PreviousTurnAgentContext | None:
        if agent_key is None:
            return None
        return self._previous_turn_contexts.get(agent_key)

    def _resolve_previous_turn_input_spec(
        self,
        input_decl: model.InputDecl,
        *,
        unit: IndexedUnit,
        agent_key: tuple[tuple[str, ...], str] | None,
    ) -> ResolvedPreviousTurnInputSpec | None:
        scalar_items, _section_items, _extras = self._split_record_items(
            input_decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {input_decl.name}",
        )
        source_item = scalar_items.get("source")
        if source_item is None or not isinstance(source_item.value, model.NameRef):
            return None
        if not self._is_rally_previous_turn_input_source_ref(source_item.value, unit=unit):
            return None

        shape_item = scalar_items.get("shape")
        if shape_item is not None:
            raise CompileError(
                f"Previous-turn input `{input_decl.name}` must not declare `shape:`; "
                "the selected previous output owns that contract."
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=(shape_item.source_span or input_decl.source_span).line
                if (shape_item.source_span or input_decl.source_span) is not None
                else None,
                column=(shape_item.source_span or input_decl.source_span).column
                if (shape_item.source_span or input_decl.source_span) is not None
                else None,
            )
        if input_decl.structure_ref is not None:
            source_span = input_decl.source_span
            raise CompileError(
                f"Previous-turn input `{input_decl.name}` must not declare `structure:`; "
                "the selected previous output owns that contract."
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=source_span.line if source_span is not None else None,
                column=source_span.column if source_span is not None else None,
            )

        requirement_item = scalar_items.get("requirement")
        if requirement_item is None:
            raise CompileError(
                f"Input `{input_decl.name}` is missing a `requirement` field."
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=input_decl.source_span.line if input_decl.source_span is not None else None,
                column=input_decl.source_span.column if input_decl.source_span is not None else None,
            )
        requirement = self._display_symbol_value(
            requirement_item.value,
            unit=unit,
            owner_label=f"input {input_decl.name}",
            surface_label="input fields",
        )

        selector_items = tuple(source_item.body or ())
        seen_selector_keys: dict[str, model.RecordScalar] = {}
        for item in selector_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(
                    f"Previous-turn input source config must stay scalar in input {input_decl.name}."
                ).ensure_location(
                    path=unit.prompt_file.source_path,
                    line=(getattr(item, "source_span", None) or source_item.source_span or input_decl.source_span).line
                    if (getattr(item, "source_span", None) or source_item.source_span or input_decl.source_span) is not None
                    else None,
                    column=(getattr(item, "source_span", None) or source_item.source_span or input_decl.source_span).column
                    if (getattr(item, "source_span", None) or source_item.source_span or input_decl.source_span) is not None
                    else None,
                )
            first_item = seen_selector_keys.get(item.key)
            if first_item is not None:
                raise CompileError(
                    f"Previous-turn input source repeats config key `{item.key}` in input {input_decl.name}."
                ).ensure_location(
                    path=unit.prompt_file.source_path,
                    line=(item.source_span or source_item.source_span or input_decl.source_span).line
                    if (item.source_span or source_item.source_span or input_decl.source_span) is not None
                    else None,
                    column=(item.source_span or source_item.source_span or input_decl.source_span).column
                    if (item.source_span or source_item.source_span or input_decl.source_span) is not None
                    else None,
                )
            seen_selector_keys[item.key] = item
            if item.key != "output":
                raise CompileError(
                    f"Previous-turn input source uses unknown config key `{item.key}` in input {input_decl.name}."
                ).ensure_location(
                    path=unit.prompt_file.source_path,
                    line=(item.source_span or source_item.source_span or input_decl.source_span).line
                    if (item.source_span or source_item.source_span or input_decl.source_span) is not None
                    else None,
                    column=(item.source_span or source_item.source_span or input_decl.source_span).column
                    if (item.source_span or source_item.source_span or input_decl.source_span) is not None
                    else None,
                )

        output_selector = seen_selector_keys.get("output")
        if output_selector is None:
            previous_turn_context = self._previous_turn_agent_context(agent_key=agent_key)
            if previous_turn_context is None:
                raise CompileError(
                    f"Zero-config previous-turn input `{input_decl.name}` needs flow-owned predecessor facts; "
                    "compile this surface through emit-time target roots."
                ).ensure_location(
                    path=unit.prompt_file.source_path,
                    line=(source_item.source_span or input_decl.source_span).line
                    if (source_item.source_span or input_decl.source_span) is not None
                    else None,
                    column=(source_item.source_span or input_decl.source_span).column
                    if (source_item.source_span or input_decl.source_span) is not None
                    else None,
                )
            if previous_turn_context.exact_final_output_key is None:
                if previous_turn_context.predecessor_final_output_keys:
                    choices = ", ".join(
                        _dotted_decl_name(parts, name)
                        for parts, name in previous_turn_context.predecessor_final_output_keys
                    )
                    raise CompileError(
                        f"Zero-config previous-turn input `{input_decl.name}` is ambiguous; "
                        f"reachable predecessors disagree on previous final output: {choices}"
                    ).ensure_location(
                        path=unit.prompt_file.source_path,
                        line=(source_item.source_span or input_decl.source_span).line
                        if (source_item.source_span or input_decl.source_span) is not None
                        else None,
                        column=(source_item.source_span or input_decl.source_span).column
                        if (source_item.source_span or input_decl.source_span) is not None
                        else None,
                    )
                raise CompileError(
                    f"Zero-config previous-turn input `{input_decl.name}` has no reachable predecessor final output."
                ).ensure_location(
                    path=unit.prompt_file.source_path,
                    line=(source_item.source_span or input_decl.source_span).line
                    if (source_item.source_span or input_decl.source_span) is not None
                    else None,
                    column=(source_item.source_span or input_decl.source_span).column
                    if (source_item.source_span or input_decl.source_span) is not None
                    else None,
                )
            output_key = previous_turn_context.exact_final_output_key
            output_unit = self._load_module(output_key[0]) if output_key[0] else self.root_unit
            output_decl = self._resolve_output_decl_body(
                output_unit.outputs_by_name[output_key[1]],
                unit=output_unit,
            )
            binding_path = None
            selector_kind = "default_final_output"
            selector_text = "Exact previous final output"
        else:
            output_key, output_unit, output_decl, selector_kind, selector_text, binding_path = (
                self._resolve_previous_turn_selector_output(
                    selector=output_selector.value,
                    unit=unit,
                    owner_label=f"input {input_decl.name}",
                )
            )
            self._validate_previous_turn_explicit_selector_against_predecessors(
                selected_output_key=output_key,
                selected_binding_path=binding_path,
                selected_output_decl=output_decl,
                unit=unit,
                owner_label=f"input {input_decl.name}",
                source_span=output_selector.source_span or source_item.source_span or input_decl.source_span,
                previous_turn_context=self._previous_turn_agent_context(agent_key=agent_key),
            )

        (
            target_key,
            target_title,
            target_config,
            shape_name,
            shape_title,
            schema_name,
            schema_title,
            schema_profile,
            lowered_schema,
            derived_contract_mode,
        ) = self._resolve_previous_turn_output_contract(output_decl, unit=output_unit)

        return ResolvedPreviousTurnInputSpec(
            input_key=(unit.module_parts, input_decl.name),
            input_unit=unit,
            input_decl=input_decl,
            requirement=requirement,
            selector_kind=selector_kind,
            selector_text=selector_text,
            output_key=output_key,
            output_unit=output_unit,
            output_decl=output_decl,
            derived_contract_mode=derived_contract_mode,
            target_key=target_key,
            target_title=target_title,
            target_config=target_config,
            shape_name=shape_name,
            shape_title=shape_title,
            schema_name=schema_name,
            schema_title=schema_title,
            schema_profile=schema_profile,
            lowered_schema=lowered_schema,
            binding_path=binding_path,
        )

    def _resolve_previous_turn_selector_output(
        self,
        *,
        selector: model.RecordScalarValue,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[OutputDeclKey, IndexedUnit, model.OutputDecl, str, str, tuple[str, ...] | None]:
        if isinstance(selector, str):
            raise CompileError(
                f"Previous-turn selector must stay typed in {owner_label}; string selector values are not allowed."
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=None,
                column=None,
            )
        if isinstance(selector, model.NameRef):
            output_unit, output_decl = self._resolve_output_decl(selector, unit=unit)
            output_decl = self._resolve_output_decl_body(output_decl, unit=output_unit)
            return (
                (output_unit.module_parts, output_decl.name),
                output_unit,
                output_decl,
                "output_decl",
                _dotted_ref_name(selector),
                None,
            )
        outputs_unit, outputs_decl = self._resolve_outputs_block_ref(selector.root, unit=unit)
        resolved_outputs = self._resolve_outputs_decl(outputs_decl, unit=outputs_unit)
        if not selector.path:
            raise CompileError(
                f"Previous-turn output binding selector must include a bound output path in {owner_label}: "
                f"{_dotted_ref_name(selector.root)}"
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=selector.root.source_span.line if selector.root.source_span is not None else None,
                column=selector.root.source_span.column if selector.root.source_span is not None else None,
            )
        binding = next((item for item in resolved_outputs.bindings if item.binding_path == selector.path), None)
        if binding is None:
            raise CompileError(
                f"Unknown previous-turn output binding in {owner_label}: "
                f"{_dotted_ref_name(selector.root)}:{'.'.join(selector.path)}"
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=selector.root.source_span.line if selector.root.source_span is not None else None,
                column=selector.root.source_span.column if selector.root.source_span is not None else None,
            )
        if not isinstance(binding.artifact.decl, model.OutputDecl):
            raise CompileError(
                f"Previous-turn output binding must resolve to an output declaration in {owner_label}: "
                f"{_dotted_ref_name(selector.root)}:{'.'.join(selector.path)}"
            )
        output_decl = self._resolve_output_decl_body(binding.artifact.decl, unit=binding.artifact.unit)
        return (
            (binding.artifact.unit.module_parts, output_decl.name),
            binding.artifact.unit,
            output_decl,
            "output_binding",
            f"{_dotted_ref_name(selector.root)}:{'.'.join(selector.path)}",
            selector.path,
        )

    def _validate_previous_turn_explicit_selector_against_predecessors(
        self,
        *,
        selected_output_key: OutputDeclKey,
        selected_binding_path: tuple[str, ...] | None,
        selected_output_decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
        previous_turn_context: PreviousTurnAgentContext | None,
    ) -> None:
        if previous_turn_context is None:
            return
        if not previous_turn_context.predecessor_agent_keys:
            raise CompileError(
                f"Previous-turn selector in {owner_label} has no reachable predecessor agent."
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=source_span.line if source_span is not None else None,
                column=source_span.column if source_span is not None else None,
            )
        for predecessor_key in previous_turn_context.predecessor_agent_keys:
            predecessor_unit = self._load_module(predecessor_key[0]) if predecessor_key[0] else self.root_unit
            predecessor_agent = predecessor_unit.agents_by_name.get(predecessor_key[1])
            if predecessor_agent is None:
                raise CompileError(
                    f"Missing predecessor agent during previous-turn validation in {owner_label}: "
                    f"{_dotted_decl_name(predecessor_key[0], predecessor_key[1])}"
                )
            predecessor_contract = self._resolve_agent_contract(predecessor_agent, unit=predecessor_unit)
            predecessor_final_output_key: OutputDeclKey | None = None
            for field in predecessor_agent.fields:
                if isinstance(field, model.FinalOutputField):
                    final_output_unit, final_output_decl = self._resolve_final_output_decl(
                        field.value,
                        unit=predecessor_unit,
                        owner_label=f"agent {predecessor_agent.name} final_output",
                        source_span=field.source_span,
                    )
                    predecessor_final_output_key = (
                        final_output_unit.module_parts,
                        final_output_decl.name,
                    )
                    break
            if selected_binding_path is not None:
                binding = predecessor_contract.output_bindings_by_path.get(selected_binding_path)
                if binding is None:
                    raise CompileError(
                        f"Previous-turn binding selector in {owner_label} is not emitted by predecessor "
                        f"{_dotted_decl_name(predecessor_key[0], predecessor_key[1])}: "
                        f"{'.'.join(selected_binding_path)}"
                    ).ensure_location(
                        path=unit.prompt_file.source_path,
                        line=source_span.line if source_span is not None else None,
                        column=source_span.column if source_span is not None else None,
                    )
                if (binding.artifact.unit.module_parts, binding.artifact.decl.name) != selected_output_key:
                    raise CompileError(
                        f"Previous-turn binding selector in {owner_label} does not stay stable across predecessors."
                    ).ensure_location(
                        path=unit.prompt_file.source_path,
                        line=source_span.line if source_span is not None else None,
                        column=source_span.column if source_span is not None else None,
                    )
            elif selected_output_key not in predecessor_contract.outputs:
                raise CompileError(
                    f"Previous-turn output selector in {owner_label} is not emitted by predecessor "
                    f"{_dotted_decl_name(predecessor_key[0], predecessor_key[1])}: "
                    f"{_dotted_decl_name(selected_output_key[0], selected_output_key[1])}"
                ).ensure_location(
                    path=unit.prompt_file.source_path,
                    line=source_span.line if source_span is not None else None,
                    column=source_span.column if source_span is not None else None,
                )

            scalar_items, section_items, _extras = self._split_record_items(
                selected_output_decl.items,
                scalar_keys={"target", "shape", "requirement"},
                section_keys={"files"},
                owner_label=f"output {selected_output_decl.name}",
            )
            files_section = section_items.get("files")
            target_item = scalar_items.get("target")
            if files_section is None and target_item is not None and isinstance(target_item.value, model.NameRef):
                if self._is_builtin_turn_response_target_ref(target_item.value):
                    if predecessor_final_output_key != selected_output_key:
                        raise CompileError(
                            f"Previous-turn selector in {owner_label} points at a non-final `TurnResponse`; "
                            "only the actual previous `final_output` can be reopened from a prior turn."
                        ).ensure_location(
                            path=unit.prompt_file.source_path,
                            line=source_span.line if source_span is not None else None,
                            column=source_span.column if source_span is not None else None,
                        )

    def _resolve_previous_turn_output_contract(
        self,
        output_decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[
        str,
        str,
        tuple[tuple[str, str], ...],
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        dict[str, object] | None,
        str,
    ]:
        scalar_items, section_items, _extras = self._split_record_items(
            output_decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {output_decl.name}",
        )
        files_section = section_items.get("files")
        if files_section is not None:
            raise CompileError(
                f"Previous-turn selectors must resolve to one concrete output artifact, not a `files:` output bundle: "
                f"{_dotted_decl_name(unit.module_parts, output_decl.name)}"
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=files_section.source_span.line if files_section.source_span is not None else None,
                column=files_section.source_span.column if files_section.source_span is not None else None,
            )
        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        if target_item is None or shape_item is None or not isinstance(target_item.value, model.NameRef):
            raise CompileError(
                f"Previous-turn selector must resolve to a typed one-artifact output: "
                f"{_dotted_decl_name(unit.module_parts, output_decl.name)}"
            ).ensure_location(
                path=unit.prompt_file.source_path,
                line=output_decl.source_span.line if output_decl.source_span is not None else None,
                column=output_decl.source_span.column if output_decl.source_span is not None else None,
            )
        target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
        target_key = (
            _dotted_ref_name(target_item.value)
            if target_item.value.module_parts
            else target_item.value.declaration_name
        )
        target_config = tuple(
            (
                item.key,
                self._display_symbol_value(
                    item.value,
                    unit=unit,
                    owner_label=f"output {output_decl.name}",
                    surface_label="output target config",
                ),
            )
            for item in (target_item.body or ())
            if isinstance(item, model.RecordScalar) and item.body is None
        )
        shape_name = self._final_output_shape_name(shape_item.value)
        shape_title = self._display_output_shape(
            shape_item.value,
            unit=unit,
            owner_label=f"output {output_decl.name}",
            surface_label="output fields",
        )
        json_summary = self._resolve_final_output_json_shape_summary(
            shape_item.value,
            unit=unit,
        )
        return (
            target_key,
            target_spec.title,
            target_config,
            shape_name,
            shape_title,
            None if json_summary is None else json_summary.schema_decl.name,
            None if json_summary is None else json_summary.schema_decl.title,
            None if json_summary is None else json_summary.schema_profile,
            None if json_summary is None else json_summary.lowered_schema,
            "structured_json" if json_summary is not None else "readable_text",
        )

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
            unit=unit,
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

    def _resolve_output_schema_field_node(
        self,
        decl: model.OutputSchemaDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> AddressableNode:
        current_node = AddressableNode(unit=unit, root_decl=decl, target=decl)
        for segment in path:
            children = self._get_addressable_children(current_node)
            if children is None or segment not in children:
                raise CompileError(
                    f"Unknown output schema field on {surface_label} in {owner_label}: "
                    f"{decl.name}.{'.'.join(path)}"
                )
            current_node = children[segment]
        return current_node

    def _resolve_output_schema_route_choice_identity(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ...], str, str, model.OutputSchemaRouteChoice] | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 3:
            return None
        schema_ref = model.NameRef(
            module_parts=tuple(expr.parts[:-3]),
            declaration_name=expr.parts[-3],
        )
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(schema_ref, unit=unit)
        except CompileError:
            return None
        schema_decl = lookup_unit.output_schemas_by_name.get(schema_ref.declaration_name)
        if schema_decl is None:
            return None
        resolved_decl = self._resolve_output_schema_decl_body(schema_decl, unit=lookup_unit)
        field = next(
            (
                item
                for item in resolved_decl.items
                if isinstance(item, model.OutputSchemaRouteField) and item.key == expr.parts[-2]
            ),
            None,
        )
        if field is None:
            return None
        choice = next(
            (
                item
                for item in field.items
                if isinstance(item, model.OutputSchemaRouteChoice) and item.key == expr.parts[-1]
            ),
            None,
        )
        if choice is None:
            return None
        return (lookup_unit.module_parts, resolved_decl.name, field.key, choice)
