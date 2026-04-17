from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.authored_diagnostics import (
    authored_compile_error,
    authored_related_site,
)
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.reference_diagnostics import reference_compile_error
from doctrine._compiler.resolved_types import (
    CompileError,
    ContractArtifact,
    IndexedUnit,
    ResolvedSchemaArtifact,
    ResolvedSchemaBody,
    ResolvedSchemaGroup,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveSchemasMixin:
    """Schema resolution helpers for ResolveMixin."""

    def _schema_item_by_key(
        self,
        items: tuple[object, ...],
        key: str,
    ) -> object | None:
        return next((item for item in items if getattr(item, "key", None) == key), None)

    def _schema_block_source_span(
        self,
        items: tuple[model.SchemaItem, ...],
        *,
        block_key: str,
    ) -> model.SourceSpan | None:
        item = self._schema_body_item(items, block_key=block_key)
        return getattr(item, "source_span", None)

    def _schema_missing_related_sites(
        self,
        *,
        parent_unit: IndexedUnit | None,
        parent_body: model.SchemaBody | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None or parent_body is None:
            return ()
        related = []
        for key in missing_keys:
            source_span = self._schema_block_source_span(parent_body.items, block_key=key)
            if source_span is None:
                continue
            related.append(
                authored_related_site(
                    label=f"inherited `{key}` block",
                    unit=parent_unit,
                    source_span=source_span,
                )
            )
        return tuple(related)

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
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"Cyclic schema inheritance: {cycle}",
                unit=unit,
                source_span=schema_decl.source_span,
            )

        self._schema_resolution_stack.append(schema_key)
        try:
            parent_schema: ResolvedSchemaBody | None = None
            parent_body: model.SchemaBody | None = None
            parent_unit: IndexedUnit | None = None
            parent_label: str | None = None
            if schema_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_schema_decl(
                    schema_decl,
                    unit=unit,
                )
                parent_schema = self._resolve_schema_decl(parent_decl, unit=parent_unit)
                parent_body = parent_decl.body
                parent_label = f"schema {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            with self._with_addressable_self_root(
                self._local_addressable_self_root_ref(schema_decl.name)
            ):
                resolved = self._resolve_schema_body(
                    schema_decl.body,
                    unit=unit,
                    owner_label=_dotted_decl_name(unit.module_parts, schema_decl.name),
                    owner_source_span=schema_decl.source_span,
                    parent_schema=parent_schema,
                    parent_body=parent_body,
                    parent_unit=parent_unit,
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
        owner_source_span: model.SourceSpan | None = None,
        parent_schema: ResolvedSchemaBody | None = None,
        parent_body: model.SchemaBody | None = None,
        parent_unit: IndexedUnit | None = None,
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
                    raise authored_compile_error(
                        code="E299",
                        summary="Compile failure",
                        detail=(
                            f"{mode} requires an inherited schema declaration in "
                            f"{owner_label}: {block_key}"
                        ),
                        unit=unit,
                        source_span=self._schema_block_source_span(
                            schema_body.items,
                            block_key=block_key,
                        )
                        or owner_source_span,
                    )
            resolved_sections = self._resolve_schema_sections(sections_items, unit=unit, owner_label=owner_label)
            resolved_gates = self._resolve_schema_gates(gates_items, unit=unit, owner_label=owner_label)
            resolved_artifacts = self._resolve_schema_artifacts(
                artifacts_items,
                unit=unit,
                owner_label=owner_label,
            )
            resolved_groups = self._resolve_schema_groups(
                groups_items,
                unit=unit,
                owner_label=owner_label,
            )
        else:
            resolved_sections = self._resolve_schema_block_with_parent(
                block_key="sections",
                mode=sections_mode,
                items=sections_items,
                parent_items=parent_schema.sections,
                unit=unit,
                owner_label=owner_label,
                owner_source_span=owner_source_span,
                parent_label=parent_label,
                parent_body=parent_body,
                parent_unit=parent_unit,
            )
            resolved_gates = self._resolve_schema_block_with_parent(
                block_key="gates",
                mode=gates_mode,
                items=gates_items,
                parent_items=parent_schema.gates,
                unit=unit,
                owner_label=owner_label,
                owner_source_span=owner_source_span,
                parent_label=parent_label,
                parent_body=parent_body,
                parent_unit=parent_unit,
            )
            resolved_artifacts = self._resolve_schema_block_with_parent(
                block_key="artifacts",
                mode=artifacts_mode,
                items=artifacts_items,
                parent_items=parent_schema.artifacts,
                unit=unit,
                owner_label=owner_label,
                owner_source_span=owner_source_span,
                parent_label=parent_label,
                parent_body=parent_body,
                parent_unit=parent_unit,
            )
            resolved_groups = self._resolve_schema_block_with_parent(
                block_key="groups",
                mode=groups_mode,
                items=groups_items,
                parent_items=parent_schema.groups,
                unit=unit,
                owner_label=owner_label,
                owner_source_span=owner_source_span,
                parent_label=parent_label,
                parent_body=parent_body,
                parent_unit=parent_unit,
            )

        if not resolved_sections and not resolved_artifacts:
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    "Schema must export at least one `sections:` or `artifacts:` block "
                    f"in {owner_label}"
                ),
                unit=unit,
                source_span=owner_source_span,
            )
        self._validate_schema_group_members(
            resolved_groups,
            artifacts=resolved_artifacts,
            unit=unit,
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
        owner_source_span: model.SourceSpan | None,
        parent_label: str | None,
        parent_body: model.SchemaBody | None,
        parent_unit: IndexedUnit | None,
    ) -> tuple[object, ...]:
        source_span = self._schema_block_source_span(items, block_key=block_key) or owner_source_span
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
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Inherited schema must use `override {block_key}:` in {owner_label}",
                    unit=unit,
                    source_span=source_span,
                    related=self._schema_missing_related_sites(
                        parent_unit=parent_unit,
                        parent_body=parent_body,
                        missing_keys=(block_key,),
                    ),
                )
            raise authored_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=f"Missing inherited schema block in {owner_label}: {block_key}",
                unit=unit,
                source_span=owner_source_span,
                related=self._schema_missing_related_sites(
                    parent_unit=parent_unit,
                    parent_body=parent_body,
                    missing_keys=(block_key,),
                ),
            )

        if mode == "inherit":
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"Cannot inherit undefined schema block in {parent_label}: {block_key}",
                unit=unit,
                source_span=source_span,
            )
        if mode == "override":
            raise authored_compile_error(
                code="E001",
                summary="Cannot override undefined inherited entry",
                detail=f"Cannot override undefined schema block in {parent_label}: {block_key}",
                unit=unit,
                source_span=source_span,
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
            return self._resolve_schema_groups(
                items,
                unit=unit,
                owner_label=owner_label,
            )
        raise authored_compile_error(
            code="E299",
            summary="Compile failure",
            detail=(
                f"Internal compiler error: unsupported schema block key in "
                f"{owner_label}: {block_key}"
            ),
            unit=unit,
            source_span=None,
        )

    def _resolve_schema_sections(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.SchemaSection, ...]:
        seen: dict[str, model.SchemaSection] = {}
        resolved: list[model.SchemaSection] = []
        for item in items:
            if not isinstance(item, model.SchemaSection):
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        "Internal compiler error: unsupported schema section item in "
                        f"{owner_label}: {type(item).__name__}"
                    ),
                    unit=unit,
                    source_span=None,
                )
            first_item = seen.get(item.key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Duplicate schema section key in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        authored_related_site(
                            label=f"first `{item.key}` entry",
                            unit=unit,
                            source_span=first_item.source_span,
                        ),
                    )
                    if first_item.source_span is not None
                    else (),
                )
            seen[item.key] = item
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
        seen: dict[str, model.SchemaGate] = {}
        resolved: list[model.SchemaGate] = []
        for item in items:
            if not isinstance(item, model.SchemaGate):
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        f"Internal compiler error: unsupported schema gate item in "
                        f"{owner_label}: {type(item).__name__}"
                    ),
                    unit=unit,
                    source_span=None,
                )
            first_item = seen.get(item.key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Duplicate schema gate key in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        authored_related_site(
                            label=f"first `{item.key}` entry",
                            unit=unit,
                            source_span=first_item.source_span,
                        ),
                    )
                    if first_item.source_span is not None
                    else (),
                )
            seen[item.key] = item
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
        seen: dict[str, model.SchemaArtifact] = {}
        resolved: list[ResolvedSchemaArtifact] = []
        for item in items:
            if not isinstance(item, model.SchemaArtifact):
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        "Internal compiler error: unsupported schema artifact item in "
                        f"{owner_label}: {type(item).__name__}"
                    ),
                    unit=unit,
                    source_span=None,
                )
            first_item = seen.get(item.key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Duplicate schema artifact key in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        authored_related_site(
                            label=f"first `{item.key}` entry",
                            unit=unit,
                            source_span=first_item.source_span,
                        ),
                    )
                    if first_item.source_span is not None
                    else (),
                )
            seen[item.key] = item
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
                    source_span=item.source_span,
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
        lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        matches: list[tuple[IndexedUnit, ContractArtifact, object | None]] = []
        for lookup_target in lookup_targets:
            if (decl := lookup_target.unit.inputs_by_name.get(lookup_target.declaration_name)) is not None:
                matches.append(
                    (
                        lookup_target.unit,
                        ContractArtifact(kind="input", unit=lookup_target.unit, decl=decl),
                        lookup_target.imported_symbol,
                    )
                )
            if (decl := self._resolve_local_output_decl(lookup_target.declaration_name, unit=lookup_target.unit)) is not None:
                matches.append(
                    (
                        lookup_target.unit,
                        ContractArtifact(kind="output", unit=lookup_target.unit, decl=decl),
                        lookup_target.imported_symbol,
                    )
                )
        if len(matches) == 1:
            _target_unit, artifact, _imported_symbol = matches[0]
            return artifact
        if len(matches) > 1:
            imported_symbol = next(
                (
                    imported_symbol
                    for _target_unit, _artifact, imported_symbol in matches
                    if imported_symbol is not None
                ),
                None,
            )
            if imported_symbol is not None:
                local_decl = next(
                    (
                        artifact.decl
                        for _target_unit, artifact, imported_symbol in matches
                        if imported_symbol is None
                    ),
                    None,
                )
                self._raise_imported_symbol_ambiguity(
                    ref,
                    unit=unit,
                    binding=imported_symbol,
                    detail=(
                        f"Schema artifact ref `{ref.declaration_name}` in {owner_label} "
                        "matches both local and imported declarations."
                    ),
                    local_decl=local_decl,
                )

        dotted_name = _dotted_ref_name(ref)
        for lookup_target in lookup_targets:
            if self._find_readable_decl_matches(
                lookup_target.declaration_name,
                unit=lookup_target.unit,
            ):
                raise reference_compile_error(
                    code="E303",
                    summary="Invalid schema declaration",
                    detail=(
                        "Schema artifact refs must resolve to input or output declarations "
                        f"in {owner_label}: {dotted_name}"
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
            code="E299",
            summary="Compile failure",
            detail=(
                "Missing local declaration ref in schema artifact "
                f"{owner_label}: {ref.declaration_name}"
            ),
            unit=unit,
            source_span=ref.source_span,
        )

    def _resolve_schema_groups(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSchemaGroup, ...]:
        seen: dict[str, model.SchemaGroup] = {}
        resolved: list[ResolvedSchemaGroup] = []
        for item in items:
            if not isinstance(item, model.SchemaGroup):
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        "Internal compiler error: unsupported schema group item in "
                        f"{owner_label}: {type(item).__name__}"
                    ),
                    unit=unit,
                    source_span=None,
                )
            first_item = seen.get(item.key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Duplicate schema group key in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        authored_related_site(
                            label=f"first `{item.key}` entry",
                            unit=unit,
                            source_span=first_item.source_span,
                        ),
                    )
                    if first_item.source_span is not None
                    else (),
                )
            if not item.members:
                raise authored_compile_error(
                    code="E303",
                    summary="Invalid schema declaration",
                    detail=f"Schema groups may not be empty in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                )
            seen[item.key] = item
            resolved.append(
                ResolvedSchemaGroup(
                    key=item.key,
                    title=item.title,
                    members=item.members,
                    source_span=item.source_span,
                )
            )
        return tuple(resolved)
