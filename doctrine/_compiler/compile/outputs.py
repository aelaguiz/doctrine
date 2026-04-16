from __future__ import annotations

import re
from dataclasses import replace

from doctrine import model
from doctrine._compiler.naming import _humanize_key
from doctrine._compiler.output_diagnostics import output_compile_error, output_related_site
from doctrine._compiler.resolved_types import (
    CompileError,
    CompiledBodyItem,
    CompiledSection,
    IndexedUnit,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)


_SUPPORT_SURFACE_PATTERN = re.compile(r"`([^`]+)`")


def _source_span(value: object | None) -> model.SourceSpan | None:
    return getattr(value, "source_span", None)


class CompileOutputsMixin:
    """Input and output surface compile helpers for CompilationContext."""

    def _compile_input_decl(self, decl: model.InputDecl, *, unit: IndexedUnit) -> CompiledSection:
        scalar_items, _section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {decl.name}",
        )
        source_item = scalar_items.get("source")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        previous_turn_spec = self._active_previous_turn_input_specs.get(
            (unit.module_parts, decl.name)
        )
        if source_item is None:
            raise output_compile_error(
                code="E221",
                summary="Input is missing typed source",
                detail=f"Input `{decl.name}` is missing a typed `source` field.",
                unit=unit,
                source_span=decl.source_span,
            )
        if not isinstance(source_item.value, model.NameRef):
            raise output_compile_error(
                code="E275",
                summary="Input source must stay typed",
                detail=f"Input `{decl.name}` must keep a typed `source`.",
                unit=unit,
                source_span=source_item.source_span or decl.source_span,
            )
        if shape_item is None and previous_turn_spec is None:
            raise output_compile_error(
                code="E222",
                summary="Input is missing shape",
                detail=f"Input `{decl.name}` is missing a `shape` field.",
                unit=unit,
                source_span=decl.source_span,
            )
        if requirement_item is None:
            raise output_compile_error(
                code="E223",
                summary="Input is missing requirement",
                detail=f"Input `{decl.name}` is missing a `requirement` field.",
                unit=unit,
                source_span=decl.source_span,
            )

        with self._with_addressable_self_root(
            self._local_addressable_self_root_ref(decl.name)
        ):
            source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
            body: list[CompiledBodyItem] = [f"- Source: {source_spec.title}"]
            if previous_turn_spec is None:
                body.extend(
                    self._compile_config_lines(
                        source_item.body or (),
                        spec=source_spec,
                        unit=unit,
                        owner_label=f"input {decl.name} source",
                        owner_source_span=source_item.source_span or decl.source_span,
                    )
                )
                body.append(
                    f"- Shape: {self._display_symbol_value(shape_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
                )
                body.append(
                    f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
                )
            else:
                contract_label = (
                    "Structured JSON"
                    if previous_turn_spec.derived_contract_mode == "structured_json"
                    else "Readable Text"
                )
                body.append(f"- Previous Output: {previous_turn_spec.selector_text}")
                body.append(f"- Derived Contract: {contract_label}")
                if previous_turn_spec.shape_title is not None:
                    body.append(f"- Derived Shape: {previous_turn_spec.shape_title}")
                if previous_turn_spec.schema_title is not None:
                    body.append(f"- Derived Schema: {previous_turn_spec.schema_title}")
                body.append(f"- Requirement: {previous_turn_spec.requirement}")
            if decl.structure_ref is not None and previous_turn_spec is None:
                document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
                if not self._is_markdown_shape_value(shape_item.value, unit=unit):
                    raise output_compile_error(
                        code="E299",
                        summary="Compile failure",
                        detail=(
                            f"Input structure requires a markdown-bearing shape in input "
                            f"{decl.name}"
                        ),
                        unit=unit,
                        source_span=shape_item.source_span or decl.source_span,
                    )
                body.append(f"- Structure: {document_decl.title}")
                body.append("")
                body.append(
                    CompiledSection(
                        title=f"Structure: {document_decl.title}",
                        body=self._compile_document_body(
                            self._resolve_document_decl(document_decl, unit=document_unit),
                            unit=document_unit,
                        ),
                    )
                )

            if extras:
                body.append("")
                body.extend(
                    self._compile_record_support_items(
                        extras,
                        unit=unit,
                        owner_label=f"input {decl.name}",
                        surface_label="input prose",
                    )
                )

            return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_output_decl(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> CompiledSection:
        self._validate_output_guard_sections(
            decl,
            unit=unit,
            allow_review_semantics=allow_review_semantics,
            allow_route_semantics=allow_route_semantics,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )
        scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {decl.name}",
        )

        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        if files_section is not None and (target_item is not None or shape_item is not None):
            related = []
            if target_item is not None:
                related.append(
                    output_related_site(
                        label="conflicting `target` field",
                        unit=unit,
                        source_span=target_item.source_span,
                    )
                )
            if shape_item is not None:
                related.append(
                    output_related_site(
                        label="conflicting `shape` field",
                        unit=unit,
                        source_span=shape_item.source_span,
                    )
                )
            raise output_compile_error(
                code="E224",
                summary="Output mixes files with target or shape",
                detail=f"Output `{decl.name}` mixes `files` with `target` or `shape`.",
                unit=unit,
                source_span=files_section.source_span or decl.source_span,
                related=tuple(related),
                hints=(
                    "Choose either `files:` or the `target:` / `shape:` pair, not both.",
                ),
            )
        if files_section is None and (target_item is None or shape_item is None):
            primary_span = (
                _source_span(target_item)
                or _source_span(shape_item)
                or decl.source_span
            )
            raise output_compile_error(
                code="E224",
                summary="Output declaration is incomplete",
                detail=(
                    f"Output `{decl.name}` must define either `files` or both `target` and "
                    "`shape`."
                ),
                unit=unit,
                source_span=primary_span,
                hints=(
                    "Add `files:` for a file set, or add both `target:` and `shape:`.",
                ),
            )

        with self._with_addressable_self_root(
            self._local_addressable_self_root_ref(decl.name)
        ):
            explicit_render_profile, render_profile = self._resolve_output_render_profiles(
                decl,
                unit=unit,
                files_section=files_section,
                shape_item=shape_item,
            )

            body: list[CompiledBodyItem] = []
            schema_section: CompiledSection | None = None
            structure_items: tuple[CompiledBodyItem, ...] = ()
            use_compact_contract = False
            if files_section is not None:
                contract_rows = [
                    ("Target", "File Set"),
                ]
                if requirement_item is not None:
                    contract_rows.append(
                        (
                            "Requirement",
                            self._display_symbol_value(
                                requirement_item.value,
                                unit=unit,
                                owner_label=f"output {decl.name}",
                                surface_label="output fields",
                            ),
                        )
                    )
                body.extend(self._compile_ordinary_output_contract_table(tuple(contract_rows)))
                body.append("")
                body.append(
                    self._compile_output_files(
                        files_section,
                        unit=unit,
                        output_name=decl.name,
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                    )
                )
            else:
                if not isinstance(target_item.value, model.NameRef):
                    raise output_compile_error(
                        code="E275",
                        summary="Output target must stay typed",
                        detail=f"Output `{decl.name}` must keep a typed `target`.",
                        unit=unit,
                        source_span=target_item.source_span or decl.source_span,
                    )
                contract_rows = self._compile_ordinary_output_contract_rows(
                    decl,
                    unit=unit,
                    target_item=target_item,
                    shape_item=shape_item,
                    requirement_item=requirement_item,
                )
                use_compact_contract = self._should_compact_ordinary_output_contract(
                    decl,
                    unit=unit,
                    target_item=target_item,
                    shape_item=shape_item,
                    contract_rows=contract_rows,
                    extras=extras,
                )
                if use_compact_contract:
                    body.extend(self._compile_compact_ordinary_output_contract(contract_rows))
                else:
                    body.extend(self._compile_ordinary_output_contract_table(contract_rows))
            if decl.schema_ref is not None:
                schema_unit, schema_decl = self._resolve_schema_ref(decl.schema_ref, unit=unit)
                resolved_schema = self._resolve_schema_decl(schema_decl, unit=schema_unit)
                if not resolved_schema.sections:
                    raise output_compile_error(
                        code="E302",
                        summary="Invalid output attachment declaration",
                        detail=(
                            "Output-attached schema must export at least one section in output "
                            f"{decl.name}: {schema_decl.name}"
                        ),
                        unit=unit,
                        source_span=decl.source_span,
                        related=(
                            output_related_site(
                                label=f"attached schema `{schema_decl.name}`",
                                unit=schema_unit,
                                source_span=schema_decl.source_span,
                            ),
                        ),
                    )
                schema_section = self._compile_schema_sections_block(resolved_schema)
            if decl.structure_ref is not None:
                if files_section is not None:
                    raise output_compile_error(
                        code="E302",
                        summary="Invalid output attachment declaration",
                        detail=(
                            "Output structure requires one markdown-bearing output artifact in "
                            f"{decl.name}"
                        ),
                        unit=unit,
                        source_span=files_section.source_span or decl.source_span,
                    )
                if shape_item is None or not self._is_markdown_shape_value(shape_item.value, unit=unit):
                    raise output_compile_error(
                        code="E302",
                        summary="Invalid output attachment declaration",
                        detail=(
                            "Output structure requires a markdown-bearing shape in output "
                            f"{decl.name}"
                        ),
                        unit=unit,
                        source_span=_source_span(shape_item) or decl.source_span,
                    )
                document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
                resolved_document = self._resolve_document_decl(document_decl, unit=document_unit)
                structure_items = self._compile_output_structure_items(
                    resolved_document,
                    document_title=document_decl.title,
                    unit=document_unit,
                    render_profile=explicit_render_profile or resolved_document.render_profile,
                )

            trust_surface_section = (
                self._compile_trust_surface_section(
                    decl,
                    unit=unit,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                    inline_code_labels=True,
                )
                if decl.trust_surface
                else None
            )

            if schema_section is not None:
                body.append("")
                body.append(schema_section)
            if structure_items:
                body.append("")
                body.extend(structure_items)

            if extras:
                support_items = (
                    self._compile_compact_ordinary_output_support_items(
                        extras,
                        unit=unit,
                        owner_label=f"output {decl.name}",
                        surface_label="output prose",
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                        trust_surface_section=trust_surface_section,
                    )
                    if use_compact_contract
                    else self._compile_ordinary_output_support_items(
                        extras,
                        unit=unit,
                        owner_label=f"output {decl.name}",
                        surface_label="output prose",
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                        trust_surface_section=trust_surface_section,
                    )
                )
                body.append("")
                body.extend(support_items)
            elif trust_surface_section is not None:
                body.append("")
                body.append(trust_surface_section)

            return CompiledSection(
                title=decl.title,
                body=tuple(body),
                render_profile=render_profile,
            )

    def _compile_trust_surface_section(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
        inline_code_labels: bool = False,
    ) -> CompiledSection:
        lines: list[CompiledBodyItem] = []
        for item in decl.trust_surface:
            field_node = self._resolve_output_field_node(
                decl,
                path=item.path,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
                source_span=item.source_span,
                review_semantics=review_semantics,
            )
            label = self._display_addressable_target_value(
                field_node,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
                route_semantics=route_semantics,
                render_profile=render_profile,
            ).text
            if item.when_expr is not None:
                label = self._render_trust_surface_label(
                    label,
                    item.when_expr,
                    unit=unit,
                )
            elif inline_code_labels:
                label = f"`{label}`"
            lines.append(f"- {label}")
        return CompiledSection(title="Trust Surface", body=tuple(lines))

    def _compile_output_files(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> CompiledSection:
        rows: list[tuple[str, str, str]] = []
        detail_sections: list[CompiledBodyItem] = []
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise output_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"`files` entries must be titled sections in output {output_name}",
                    unit=unit,
                    source_span=_source_span(item) or section.source_span,
                )
            scalar_items, _section_items, extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise output_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        f"Output file entry is missing string path in {output_name}: "
                        f"{item.key}"
                    ),
                    unit=unit,
                    source_span=_source_span(path_item) or item.source_span,
                )
            if shape_item is None:
                raise output_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Output file entry is missing shape in {output_name}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                )
            rows.append(
                (
                    item.title,
                    f"`{path_item.value}`",
                    self._display_output_shape(
                        shape_item.value,
                        unit=unit,
                        owner_label=f"output {output_name} file {item.key}",
                        surface_label="output file fields",
                    ),
                )
            )
            if extras:
                detail_sections.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_record_support_items(
                            extras,
                            unit=unit,
                            owner_label=f"output {output_name} file {item.key}",
                            surface_label="output file prose",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        ),
                    )
                )
        body: list[CompiledBodyItem] = list(
            self._pipe_table_lines(("Artifact", "Path", "Shape"), tuple(rows))
        )
        for detail_section in detail_sections:
            body.extend(["", detail_section])
        return CompiledSection(title="Artifacts", body=tuple(body))

    def _compile_ordinary_output_contract_rows(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        target_item: model.RecordScalar,
        shape_item: model.RecordScalar,
        requirement_item: model.RecordScalar | None,
    ) -> tuple[tuple[str, str], ...]:
        if not isinstance(target_item.value, model.NameRef):
            raise output_compile_error(
                code="E275",
                summary="Output target must stay typed",
                detail=f"Output `{decl.name}` must keep a typed `target`.",
                unit=unit,
                source_span=target_item.source_span or decl.source_span,
            )
        target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
        rows: list[tuple[str, str]] = [("Target", target_spec.title)]
        if target_spec.delivery_skill is not None:
            rows.append(("Delivered Via", f"`{target_spec.delivery_skill.title}`"))
        rows.extend(
            self._compile_output_config_rows(
                target_item.body or (),
                spec=target_spec,
                unit=unit,
                owner_label=f"output {decl.name} target",
                owner_source_span=target_item.source_span,
            )
        )
        rows.append(
            (
                "Shape",
                self._display_output_shape(
                    shape_item.value,
                    unit=unit,
                    owner_label=decl.name,
                    surface_label="output fields",
                ),
            )
        )
        if requirement_item is not None:
            rows.append(
                (
                    "Requirement",
                    self._display_symbol_value(
                        requirement_item.value,
                        unit=unit,
                        owner_label=f"output {decl.name}",
                        surface_label="output fields",
                    ),
                )
            )
        if decl.schema_ref is not None:
            _schema_unit, schema_decl = self._resolve_schema_ref(decl.schema_ref, unit=unit)
            rows.append(("Schema", schema_decl.title))
        if decl.structure_ref is not None:
            _document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            rows.append(("Structure", document_decl.title))
        return tuple(rows)

    def _compile_output_config_rows(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec,
        unit: IndexedUnit,
        owner_label: str,
        owner_source_span: model.SourceSpan | None,
    ) -> tuple[tuple[str, str], ...]:
        rows: list[tuple[str, str]] = []
        seen_keys: dict[str, model.RecordScalar] = {}
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise output_compile_error(
                    code="E230",
                    summary="Config entries must be scalar key/value lines",
                    detail=(
                        f"Config entries must be scalar key/value lines in `{owner_label}`."
                    ),
                    unit=unit,
                    source_span=_source_span(item) or owner_source_span,
                )
            first_item = seen_keys.get(item.key)
            if first_item is not None:
                raise output_compile_error(
                    code="E231",
                    summary="Duplicate config key",
                    detail=(
                        f"Config owner `{owner_label}` repeats key `{item.key}`."
                    ),
                    unit=unit,
                    source_span=item.source_span or owner_source_span,
                    related=(
                        output_related_site(
                            label=f"first `{item.key}` config entry",
                            unit=unit,
                            source_span=first_item.source_span,
                        ),
                    ),
                )
            seen_keys[item.key] = item
            if item.key not in allowed_keys:
                raise output_compile_error(
                    code="E232",
                    summary="Unknown config key",
                    detail=(
                        f"Config owner `{owner_label}` uses unknown key `{item.key}`."
                    ),
                    unit=unit,
                    source_span=item.source_span or owner_source_span,
                )
            rows.append(
                (
                    allowed_keys[item.key],
                    self._format_scalar_value(
                        item.value,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label="config values",
                    ),
                )
            )

        missing_required = [key for key in spec.required_keys if key not in seen_keys]
        if missing_required:
            missing = ", ".join(missing_required)
            raise output_compile_error(
                code="E233",
                summary="Missing required config key",
                detail=(
                    f"Config owner `{owner_label}` is missing required key `{missing}`."
                ),
                unit=unit,
                source_span=owner_source_span,
            )

        return tuple(rows)

    def _compile_ordinary_output_contract_table(
        self,
        rows: tuple[tuple[str, str], ...],
    ) -> tuple[CompiledBodyItem, ...]:
        return tuple(self._pipe_table_lines(("Contract", "Value"), rows))

    def _should_compact_ordinary_output_contract(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        target_item: model.RecordScalar,
        shape_item: model.RecordScalar,
        contract_rows: tuple[tuple[str, str], ...],
        extras: tuple[model.AnyRecordItem, ...],
    ) -> bool:
        if decl.schema_ref is not None or decl.structure_ref is not None:
            return False
        if len(contract_rows) != 3:
            return False
        if not isinstance(target_item.value, model.NameRef):
            return False
        if not self._is_builtin_turn_response_target_ref(target_item.value):
            return False
        for item in extras:
            if isinstance(item, model.ReadableBlock):
                return False
            if isinstance(item, model.RecordSection) and item.key in {
                "must_include",
                "current_truth",
                "support_files",
                "notes",
            }:
                return False
        return not self._is_markdown_shape_value(shape_item.value, unit=unit)

    def _compile_compact_ordinary_output_contract(
        self,
        rows: tuple[tuple[str, str], ...],
    ) -> tuple[CompiledBodyItem, ...]:
        return tuple(f"- {label}: {value}" for label, value in rows)

    def _compile_compact_ordinary_output_support_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
        trust_surface_section: CompiledSection | None = None,
    ) -> list[CompiledBodyItem]:
        compiled: list[CompiledBodyItem] = []
        rendered_trust_surface = False
        for item in items:
            if (
                trust_surface_section is not None
                and not rendered_trust_surface
                and isinstance(item, model.RecordSection)
                and item.key == "standalone_read"
            ):
                if compiled and compiled[-1] != "":
                    compiled.append("")
                compiled.append(trust_surface_section)
                rendered_trust_surface = True

            compact_line = self._render_compact_record_item_line(
                item,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if compact_line is not None:
                compiled.append(compact_line)
                continue

            rendered_items = list(
                self._compile_ordinary_output_support_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
            if not rendered_items:
                continue
            if compiled and compiled[-1] != "":
                compiled.append("")
            compiled.extend(rendered_items)

        if trust_surface_section is not None and not rendered_trust_surface:
            if compiled and compiled[-1] != "":
                compiled.append("")
            compiled.append(trust_surface_section)
        return compiled

    def _compile_ordinary_output_support_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
        trust_surface_section: CompiledSection | None = None,
    ) -> list[CompiledBodyItem]:
        compiled: list[CompiledBodyItem] = []
        rendered_trust_surface = False
        for item in items:
            if (
                trust_surface_section is not None
                and not rendered_trust_surface
                and isinstance(item, model.RecordSection)
                and item.key == "standalone_read"
            ):
                compiled.append(trust_surface_section)
                rendered_trust_surface = True
            compiled.extend(
                self._compile_ordinary_output_support_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
        if trust_surface_section is not None and not rendered_trust_surface:
            compiled.append(trust_surface_section)
        return compiled

    def _compile_ordinary_output_support_item(
        self,
        item: model.AnyRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, model.RecordSection):
            if item.key == "must_include":
                return self._compile_output_record_table(
                    item,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            if item.key == "current_truth":
                return self._compile_output_record_table(
                    item,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            if item.key == "support_files":
                return self._compile_output_support_files_table(
                    item,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            if item.key == "notes":
                notes_table = self._compile_output_notes_table(
                    item,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
                if notes_table is not None:
                    return notes_table
        if (
            isinstance(item, model.ReadableBlock)
            and item.kind == "properties"
            and not item.anonymous
            and item.title is not None
        ):
            return self._compile_output_properties_table(
                item,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        return self._compile_record_item(
            item,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )

    def _compile_output_record_table(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        rows: list[tuple[str, str]] = []
        detail_sections: list[CompiledBodyItem] = []
        for item in section.items:
            if isinstance(item, model.RecordSection):
                summary = self._flatten_output_record_items(
                    item.items,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
                if summary is None:
                    summary = "See the detail below."
                    detail_sections.append(
                        CompiledSection(
                            title=item.title,
                            body=self._compile_record_support_items(
                                item.items,
                                unit=unit,
                                owner_label=f"{owner_label}.{item.key}",
                                surface_label=surface_label,
                                review_semantics=review_semantics,
                                route_semantics=route_semantics,
                                render_profile=render_profile,
                            ),
                        )
                    )
                rows.append((f"**{item.title}**", summary))
                continue
            if isinstance(item, model.RecordScalar):
                summary = self._format_scalar_value(
                    item.value,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
                rows.append((f"**{_humanize_key(item.key)}**", summary))
                if item.body is not None:
                    detail_sections.append(
                        CompiledSection(
                            title=_humanize_key(item.key),
                            body=self._compile_record_support_items(
                                item.body,
                                unit=unit,
                                owner_label=f"{owner_label}.{item.key}",
                                surface_label=surface_label,
                                review_semantics=review_semantics,
                                route_semantics=route_semantics,
                                render_profile=render_profile,
                            ),
                        )
                )
                continue
            raise output_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"{section.title} must stay record-shaped in {owner_label}",
                unit=unit,
                source_span=_source_span(item) or section.source_span,
            )
        body: list[CompiledBodyItem] = list(
            self._pipe_table_lines(("Field", "What to write"), tuple(rows))
        )
        for detail_section in detail_sections:
            body.extend(["", detail_section])
        return (CompiledSection(title=section.title, body=tuple(body)),)

    def _compile_output_properties_table(
        self,
        block: model.ReadableBlock,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        if block.when_expr is not None:
            self._validate_readable_guard_expr(
                block.when_expr,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=review_semantics is not None,
                allow_route_semantics=route_semantics is not None,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
        block_route_semantics = self._narrow_route_semantics(
            route_semantics,
            block.when_expr,
            unit=unit,
        )
        properties = self._resolve_readable_properties_payload(
            block.payload,
            unit=unit,
            owner_label=owner_label,
            review_semantics=review_semantics,
            route_semantics=block_route_semantics,
            render_profile=render_profile,
        )
        rows = []
        for entry in properties.entries:
            rows.append(
                (
                    f"**{entry.title}**",
                    self._flatten_output_prose_lines(
                        entry.body,
                        unit=unit,
                        owner_label=f"{owner_label}.{entry.key}",
                        surface_label="properties prose",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    or "See the detail below.",
                )
            )
        return (
            CompiledSection(
                title=block.title or _humanize_key(block.key),
                body=self._pipe_table_lines(("Field", "What to write"), tuple(rows)),
                requirement=block.requirement,
                when_text=self._readable_guard_text(block.when_expr, unit=unit),
            ),
        )

    def _compile_output_support_files_table(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        rows: list[tuple[str, str, str]] = []
        detail_sections: list[CompiledBodyItem] = []
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise output_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"support_files entries must be titled sections in {owner_label}",
                    unit=unit,
                    source_span=_source_span(item) or section.source_span,
                )
            scalar_items, _section_items, extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "when"},
                owner_label=f"{owner_label}.{item.key}",
            )
            path_item = scalar_items.get("path")
            if path_item is None or not isinstance(path_item.value, str):
                raise output_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        f"support_files entry is missing string path in {owner_label}: "
                        f"{item.key}"
                    ),
                    unit=unit,
                    source_span=_source_span(path_item) or item.source_span,
                )
            when_item = scalar_items.get("when")
            use_when = (
                self._display_symbol_value(
                    when_item.value,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}.when",
                    surface_label="support_files",
                    render_profile=render_profile,
                )
                if when_item is not None
                else ""
            )
            rows.append((f"`{item.title}`", f"`{path_item.value}`", use_when))
            if extras:
                detail_sections.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_record_support_items(
                            extras,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                            surface_label="support_files prose",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        ),
                    )
                )
        body: list[CompiledBodyItem] = list(
            self._pipe_table_lines(("Support Surface", "Path", "Use When"), tuple(rows))
        )
        for detail_section in detail_sections:
            body.extend(["", detail_section])
        return (CompiledSection(title=section.title, body=tuple(body)),)

    def _compile_output_notes_table(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...] | None:
        rows: list[tuple[str, str]] = []
        for index, item in enumerate(section.items):
            if not isinstance(item, (str, model.EmphasizedLine)):
                return None
            rendered_line = self._interpolate_authored_prose_line(
                item,
                unit=unit,
                owner_label=f"{owner_label}.{index}",
                surface_label="notes prose",
                ambiguous_label="notes prose interpolation ref",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            parsed = self._parse_output_support_note_row(rendered_line)
            if parsed is None:
                return None
            rows.append(parsed)
        if not rows:
            return None
        return (
            CompiledSection(
                title=section.title,
                body=self._pipe_table_lines(("Support Surface", "Rule"), tuple(rows)),
            ),
        )

    def _parse_output_support_note_row(
        self,
        rendered_line: str,
    ) -> tuple[str, str] | None:
        matches = _SUPPORT_SURFACE_PATTERN.findall(rendered_line)
        if len(matches) != 1:
            return None
        support_surface = f"`{matches[0]}`"
        rule = _SUPPORT_SURFACE_PATTERN.sub("", rendered_line, count=1)
        rule = " ".join(rule.split())
        if not rule:
            return None
        return support_surface, rule

    def _flatten_output_record_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str | None:
        lines: list[model.ProseLine] = []
        for item in items:
            if not isinstance(item, (str, model.EmphasizedLine)):
                return None
            lines.append(item)
        return self._flatten_output_prose_lines(
            tuple(lines),
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )

    def _flatten_output_prose_lines(
        self,
        lines: tuple[model.ProseLine, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str | None:
        rendered = [
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=f"{surface_label} interpolation ref",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            for line in lines
        ]
        text = " ".join(line.strip() for line in rendered if line.strip()).strip()
        return text or None

    def _compile_output_structure_items(
        self,
        document_body,
        *,
        document_title: str,
        unit: IndexedUnit,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        summary_rows, detail_blocks = self._compile_output_structure_summary_rows(
            document_body,
            unit=unit,
        )
        if not document_body.preamble and not detail_blocks:
            return (
                "Required Structure:",
                *tuple(
                    (
                        f"- {title.replace('**', '')}: {summary}"
                        if summary and summary != "See the detail below."
                        else f"- {title.replace('**', '')}"
                    )
                    for title, _kind, summary in summary_rows
                ),
            )

        body: list[CompiledBodyItem] = []
        if document_body.preamble:
            body.extend(document_body.preamble)
            body.append("")
        body.append(f"This artifact must follow the `{document_title}` structure below.")
        body.append("")
        body.extend(
            self._pipe_table_lines(
                ("Required Section", "Kind", "What it must do"),
                tuple(summary_rows),
            )
        )
        for detail_block in detail_blocks:
            body.extend(["", detail_block])
        return (
            CompiledSection(
                title="Artifact Structure",
                body=tuple(body),
                render_profile=render_profile,
            ),
        )

    def _compile_output_structure_summary_rows(
        self,
        document_body,
        *,
        unit: IndexedUnit,
    ) -> tuple[list[tuple[str, str, str]], list[CompiledBodyItem]]:
        rows: list[tuple[str, str, str]] = []
        detail_blocks: list[CompiledBodyItem] = []
        for block in document_body.items:
            summary_row, detail_block = self._compile_output_structure_summary_row(
                block,
                unit=unit,
            )
            rows.append(summary_row)
            if detail_block is not None:
                detail_blocks.append(detail_block)
        return rows, detail_blocks

    def _compile_output_structure_summary_row(
        self,
        block: model.DocumentBlock,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, str, str], CompiledBodyItem | None]:
        compiled_block = self._compile_document_block(block, unit=unit)
        title = block.title or _humanize_key(block.key)
        kind_label = self._output_structure_kind_label(block.kind)
        summary = self._output_structure_summary_text(block, unit=unit)
        detail_block: CompiledBodyItem | None = None

        if block.kind == "section" and summary is not None:
            return (f"**{title}**", kind_label, summary), None

        if block.kind == "definitions":
            detail_block = replace(compiled_block, title=f"{compiled_block.title} Definitions")
        elif block.kind == "table":
            detail_block = replace(compiled_block, title=f"{compiled_block.title} Contract")
        elif block.kind in {"checklist", "sequence", "bullets", "callout", "code", "markdown", "html", "footnotes", "image", "guard"}:
            detail_block = compiled_block
        elif block.kind == "rule":
            detail_block = compiled_block
        elif block.kind == "section":
            detail_block = compiled_block
        elif block.kind == "properties":
            detail_block = compiled_block

        return (
            (f"**{title}**", kind_label, summary or "See the detail below."),
            detail_block,
        )

    def _output_structure_kind_label(self, kind: str) -> str:
        return {
            "section": "Section",
            "definitions": "Definitions",
            "table": "Table",
            "sequence": "Ordered List",
            "bullets": "Bulleted List",
            "checklist": "Checklist",
            "callout": "Callout",
            "code": "Code Block",
            "markdown": "Markdown Block",
            "html": "HTML Block",
            "footnotes": "Footnotes",
            "image": "Image",
            "guard": "Guard",
            "properties": "Properties",
            "rule": "Rule",
        }.get(kind, _humanize_key(kind))

    def _output_structure_summary_text(
        self,
        block: model.DocumentBlock,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if block.kind == "section":
            payload = block.payload if isinstance(block.payload, tuple) else ()
            return self._flatten_output_prose_lines(
                payload,
                unit=unit,
                owner_label=f"document.{block.key}",
                surface_label="structure section prose",
            )
        if block.kind == "definitions" and isinstance(block.payload, tuple):
            titles = [f"`{item.title}`" for item in block.payload]
            return f"Define {self._natural_language_join(titles)}."
        if block.kind == "table" and isinstance(block.payload, model.ReadableTableData):
            note_summary = self._flatten_output_prose_lines(
                block.payload.notes,
                unit=unit,
                owner_label=f"document.{block.key}",
                surface_label="structure table notes",
            )
            if note_summary is not None:
                return note_summary
            column_titles = [f"`{column.title}`" for column in block.payload.columns]
            return f"Use the columns {self._natural_language_join(column_titles)}."
        if block.kind in {"sequence", "bullets", "checklist"} and isinstance(block.payload, tuple):
            item_lines = tuple(item.text for item in block.payload if isinstance(item, model.ReadableListItem))
            summary = self._flatten_output_prose_lines(
                item_lines,
                unit=unit,
                owner_label=f"document.{block.key}",
                surface_label="structure list prose",
            )
            return summary
        if block.kind == "callout" and isinstance(block.payload, model.ReadableCalloutData):
            return self._flatten_output_prose_lines(
                block.payload.body,
                unit=unit,
                owner_label=f"document.{block.key}",
                surface_label="structure callout prose",
            )
        if block.kind == "rule":
            return "Keep the divider rule."
        return None
