from __future__ import annotations

from dataclasses import replace

from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.resolved_types import *  # noqa: F401,F403
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveSchemasMixin:
    """Schema resolution helpers for ResolveMixin."""

    def _resolve_schema_decl(
        self, schema_decl: model.SchemaDecl, *, unit: IndexedUnit
    ) -> ResolvedSchemaBody:
        schema_key = (unit.module_parts, schema_decl.name)
        cached = self._resolved_schema_cache.get(schema_key)
        if cached is not None:
            return cached

        if schema_key in self._schema_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._schema_resolution_stack, schema_key]
            )
            raise CompileError(f"Cyclic schema inheritance: {cycle}")

        self._schema_resolution_stack.append(schema_key)
        try:
            parent_schema: ResolvedSchemaBody | None = None
            parent_label: str | None = None
            if schema_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_schema_decl(
                    schema_decl,
                    unit=unit,
                )
                parent_schema = self._resolve_schema_decl(parent_decl, unit=parent_unit)
                parent_label = f"schema {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_schema_body(
                schema_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, schema_decl.name),
                parent_schema=parent_schema,
                parent_label=parent_label,
            )
            resolved = replace(
                resolved,
                render_profile=(
                    self._resolve_render_profile_ref(schema_decl.render_profile_ref, unit=unit)
                    if schema_decl.render_profile_ref is not None
                    else parent_schema.render_profile if parent_schema is not None else None
                ),
            )
            self._resolved_schema_cache[schema_key] = resolved
            return resolved
        finally:
            self._schema_resolution_stack.pop()

    def _resolve_schema_body(
        self,
        schema_body: model.SchemaBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_schema: ResolvedSchemaBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSchemaBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="schema prose",
                ambiguous_label="schema prose interpolation ref",
            )
            for line in schema_body.preamble
        )
        sections_mode, sections_items = self._schema_body_action(schema_body.items, block_key="sections")
        gates_mode, gates_items = self._schema_body_action(schema_body.items, block_key="gates")
        artifacts_mode, artifacts_items = self._schema_body_action(
            schema_body.items,
            block_key="artifacts",
        )
        groups_mode, groups_items = self._schema_body_action(schema_body.items, block_key="groups")

        if parent_schema is None:
            for block_key, mode in (
                ("sections", sections_mode),
                ("gates", gates_mode),
                ("artifacts", artifacts_mode),
                ("groups", groups_mode),
            ):
                if mode not in {"define", None}:
                    raise CompileError(
                        f"{mode} requires an inherited schema declaration in {owner_label}: {block_key}"
                    )
            resolved_sections = self._resolve_schema_sections(sections_items, unit=unit, owner_label=owner_label)
            resolved_gates = self._resolve_schema_gates(gates_items, unit=unit, owner_label=owner_label)
            resolved_artifacts = self._resolve_schema_artifacts(
                artifacts_items,
                unit=unit,
                owner_label=owner_label,
            )
            resolved_groups = self._resolve_schema_groups(groups_items, owner_label=owner_label)
        else:
            resolved_sections = self._resolve_schema_block_with_parent(
                block_key="sections",
                mode=sections_mode,
                items=sections_items,
                parent_items=parent_schema.sections,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )
            resolved_gates = self._resolve_schema_block_with_parent(
                block_key="gates",
                mode=gates_mode,
                items=gates_items,
                parent_items=parent_schema.gates,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )
            resolved_artifacts = self._resolve_schema_block_with_parent(
                block_key="artifacts",
                mode=artifacts_mode,
                items=artifacts_items,
                parent_items=parent_schema.artifacts,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )
            resolved_groups = self._resolve_schema_block_with_parent(
                block_key="groups",
                mode=groups_mode,
                items=groups_items,
                parent_items=parent_schema.groups,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )

        if not resolved_sections and not resolved_artifacts:
            raise CompileError(
                f"Schema must export at least one `sections:` or `artifacts:` block in {owner_label}"
            )
        self._validate_schema_group_members(
            resolved_groups,
            artifacts=resolved_artifacts,
            owner_label=owner_label,
        )

        return ResolvedSchemaBody(
            title=schema_body.title,
            preamble=resolved_preamble,
            sections=resolved_sections,
            gates=resolved_gates,
            artifacts=resolved_artifacts,
            groups=resolved_groups,
        )

    def _resolve_schema_block_with_parent(
        self,
        *,
        block_key: str,
        mode: str | None,
        items: tuple[object, ...],
        parent_items: tuple[object, ...],
        unit: IndexedUnit,
        owner_label: str,
        parent_label: str | None,
    ) -> tuple[object, ...]:
        if parent_items:
            if mode == "inherit":
                return parent_items
            if mode == "override":
                return self._resolve_schema_block_items(
                    block_key=block_key,
                    items=items,
                    unit=unit,
                    owner_label=owner_label,
                )
            if mode == "define":
                raise CompileError(
                    f"Inherited schema must use `override {block_key}:` in {owner_label}"
                )
            raise CompileError(f"E003 Missing inherited schema block in {owner_label}: {block_key}")

        if mode == "inherit":
            raise CompileError(
                f"Cannot inherit undefined schema block in {parent_label}: {block_key}"
            )
        if mode == "override":
            raise CompileError(
                f"E001 Cannot override undefined schema block in {parent_label}: {block_key}"
            )
        return self._resolve_schema_block_items(
            block_key=block_key,
            items=items,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_schema_block_items(
        self,
        *,
        block_key: str,
        items: tuple[object, ...],
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[object, ...]:
        if block_key == "sections":
            return self._resolve_schema_sections(
                items,
                unit=unit,
                owner_label=owner_label,
            )
        if block_key == "gates":
            return self._resolve_schema_gates(
                items,
                unit=unit,
                owner_label=owner_label,
            )
        if block_key == "artifacts":
            return self._resolve_schema_artifacts(
                items,
                unit=unit,
                owner_label=owner_label,
            )
        if block_key == "groups":
            return self._resolve_schema_groups(items, owner_label=owner_label)
        raise CompileError(
            f"Internal compiler error: unsupported schema block key in {owner_label}: {block_key}"
        )

    def _resolve_schema_sections(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.SchemaSection, ...]:
        seen: set[str] = set()
        resolved: list[model.SchemaSection] = []
        for item in items:
            if not isinstance(item, model.SchemaSection):
                raise CompileError(
                    f"Internal compiler error: unsupported schema section item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema section key in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                replace(
                    item,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                            surface_label="schema section prose",
                            ambiguous_label="schema prose interpolation ref",
                        )
                        for line in item.body
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_schema_gates(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.SchemaGate, ...]:
        seen: set[str] = set()
        resolved: list[model.SchemaGate] = []
        for item in items:
            if not isinstance(item, model.SchemaGate):
                raise CompileError(
                    f"Internal compiler error: unsupported schema gate item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema gate key in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                replace(
                    item,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                            surface_label="schema gate prose",
                            ambiguous_label="schema prose interpolation ref",
                        )
                        for line in item.body
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_schema_artifacts(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSchemaArtifact, ...]:
        seen: set[str] = set()
        resolved: list[ResolvedSchemaArtifact] = []
        for item in items:
            if not isinstance(item, model.SchemaArtifact):
                raise CompileError(
                    f"Internal compiler error: unsupported schema artifact item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema artifact key in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                ResolvedSchemaArtifact(
                    key=item.key,
                    title=item.title,
                    ref=item.ref,
                    artifact=self._resolve_schema_artifact_ref(
                        item.ref,
                        unit=unit,
                        owner_label=owner_label,
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_schema_artifact_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ContractArtifact:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        if (decl := target_unit.inputs_by_name.get(ref.declaration_name)) is not None:
            return ContractArtifact(kind="input", unit=target_unit, decl=decl)
        if (decl := target_unit.outputs_by_name.get(ref.declaration_name)) is not None:
            return ContractArtifact(kind="output", unit=target_unit, decl=decl)

        dotted_name = _dotted_ref_name(ref)
        if ref.module_parts:
            if self._find_readable_decl_matches(ref.declaration_name, unit=target_unit):
                raise CompileError(
                    f"Schema artifact refs must resolve to input or output declarations in {owner_label}: {dotted_name}"
                )
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        if self._find_readable_decl_matches(ref.declaration_name, unit=target_unit):
            raise CompileError(
                f"Schema artifact refs must resolve to input or output declarations in {owner_label}: {ref.declaration_name}"
            )
        raise CompileError(
            f"Missing local declaration ref in schema artifact {owner_label}: {ref.declaration_name}"
        )

    def _resolve_schema_groups(
        self,
        items: tuple[object, ...],
        *,
        owner_label: str,
    ) -> tuple[ResolvedSchemaGroup, ...]:
        seen: set[str] = set()
        resolved: list[ResolvedSchemaGroup] = []
        for item in items:
            if not isinstance(item, model.SchemaGroup):
                raise CompileError(
                    f"Internal compiler error: unsupported schema group item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema group key in {owner_label}: {item.key}")
            if not item.members:
                raise CompileError(f"Schema groups may not be empty in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                ResolvedSchemaGroup(
                    key=item.key,
                    title=item.title,
                    members=item.members,
                )
            )
        return tuple(resolved)
