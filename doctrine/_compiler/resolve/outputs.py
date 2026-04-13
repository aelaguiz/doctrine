from __future__ import annotations

from doctrine._compiler.constants import _BUILTIN_INPUT_SOURCES, _BUILTIN_OUTPUT_TARGETS
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.resolved_types import *  # noqa: F401,F403
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveOutputsMixin:
    """Output and IO-body resolution helpers for ResolveMixin."""

    def _resolve_final_output_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        local_decl = target_unit.outputs_by_name.get(ref.declaration_name)
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
        if not self._ref_exists_in_registry(value, unit=unit, registry_name="output_shapes_by_name"):
            return None

        shape_unit, shape_decl = self._resolve_output_shape_decl(value, unit=unit)
        shape_scalars, _shape_sections, shape_extras = self._split_record_items(
            shape_decl.items,
            scalar_keys={"kind", "schema", "example_file"},
            owner_label=f"output shape {shape_decl.name}",
        )
        schema_item = shape_scalars.get("schema")
        if schema_item is None or not isinstance(schema_item.value, model.NameRef):
            return None

        schema_unit, schema_decl = self._resolve_json_schema_ref(schema_item.value, unit=shape_unit)
        schema_scalars, _schema_sections, _schema_extras = self._split_record_items(
            schema_decl.items,
            scalar_keys={"profile", "file"},
            owner_label=f"json schema {schema_decl.name}",
        )
        profile_item = schema_scalars.get("profile")
        schema_file_item = schema_scalars.get("file")
        example_file_item = shape_scalars.get("example_file")
        if profile_item is None:
            schema_profile = None
        elif isinstance(profile_item.value, model.NameRef) and not profile_item.value.module_parts:
            schema_profile = profile_item.value.declaration_name
        else:
            schema_profile = self._display_symbol_value(
                profile_item.value,
                unit=schema_unit,
                owner_label=f"json schema {schema_decl.name}",
                surface_label="json schema fields",
            )
        if schema_file_item is None:
            schema_file = None
        elif isinstance(schema_file_item.value, str):
            schema_file = schema_file_item.value
        else:
            schema_file = self._display_symbol_value(
                schema_file_item.value,
                unit=schema_unit,
                owner_label=f"json schema {schema_decl.name}",
                surface_label="json schema fields",
            )
        example_file = (
            example_file_item.value
            if example_file_item is not None and isinstance(example_file_item.value, str)
            else None
        )
        payload_rows = self._load_json_schema_payload_rows(
            schema_unit=schema_unit,
            schema_decl=schema_decl,
            schema_file=schema_file,
        )
        resolved_schema_file = (
            self._resolve_declared_support_path(schema_unit, schema_file)
            if schema_file is not None
            else None
        )
        resolved_example_file = (
            self._resolve_declared_support_path(shape_unit, example_file)
            if example_file is not None
            else None
        )
        example_text = (
            self._read_required_final_output_support_text(
                shape_unit,
                example_file,
                owner_label=f"output shape {shape_decl.name}",
            )
            if example_file is not None
            else None
        )
        return FinalOutputJsonShapeSummary(
            shape_unit=shape_unit,
            shape_decl=shape_decl,
            schema_unit=schema_unit,
            schema_decl=schema_decl,
            schema_profile=schema_profile,
            schema_file=schema_file,
            example_file=example_file,
            resolved_schema_file=resolved_schema_file,
            resolved_example_file=resolved_example_file,
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
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_OUTPUT_TARGETS.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.output_targets_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(
                    local_decl,
                    owner_label=f"output target {local_decl.name}",
                )

        target_unit, decl = self._resolve_output_target_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"output target {decl.name}")

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

            if isinstance(item, model.RecordSection):
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
        item: model.RecordSection,
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
            owner_label=f"{field_kind} section `{item.title}`",
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
        return ResolvedIoSection(
            key=item.key,
            section=CompiledSection(
                title=item.title,
                body=resolved_bucket.body,
            ),
            artifacts=resolved_bucket.artifacts,
            bindings=tuple(bindings),
        )

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
