from __future__ import annotations

from doctrine import model
from doctrine._compiler.resolved_types import (
    CompileError,
    CompiledBodyItem,
    CompiledSection,
    IndexedUnit,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)


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
        if source_item is None:
            raise CompileError(f"Input is missing typed source: {decl.name}")
        if not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input source must stay typed: {decl.name}")
        if shape_item is None:
            raise CompileError(f"Input is missing shape: {decl.name}")
        if requirement_item is None:
            raise CompileError(f"Input is missing requirement: {decl.name}")

        source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
        body: list[CompiledBodyItem] = [f"- Source: {source_spec.title}"]
        body.extend(
            self._compile_config_lines(
                source_item.body or (),
                spec=source_spec,
                unit=unit,
                owner_label=f"input {decl.name} source",
            )
        )
        body.append(
            f"- Shape: {self._display_symbol_value(shape_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        body.append(
            f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        if decl.structure_ref is not None:
            document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            if not self._is_markdown_shape_value(shape_item.value, unit=unit):
                raise CompileError(
                    f"Input structure requires a markdown-bearing shape in input {decl.name}"
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
            raise CompileError(
                f"Output mixes `files` with `target` or `shape`: {decl.name}"
            )
        if files_section is None and (target_item is None or shape_item is None):
            raise CompileError(
                f"Output must define either `files` or both `target` and `shape`: {decl.name}"
            )

        explicit_render_profile, render_profile = self._resolve_output_render_profiles(
            decl,
            unit=unit,
            files_section=files_section,
            shape_item=shape_item,
        )

        body: list[CompiledBodyItem] = []
        if files_section is not None:
            body.extend(
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
                raise CompileError(f"Output target must stay typed: {decl.name}")
            target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
            body.append(f"- Target: {target_spec.title}")
            body.extend(
                self._compile_config_lines(
                    target_item.body or (),
                    spec=target_spec,
                    unit=unit,
                    owner_label=f"output {decl.name} target",
                )
            )
            body.append(
                f"- Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=decl.name, surface_label='output fields')}"
            )

        if requirement_item is not None:
            body.append(
                f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'output {decl.name}', surface_label='output fields')}"
            )
        if decl.schema_ref is not None:
            schema_unit, schema_decl = self._resolve_schema_ref(decl.schema_ref, unit=unit)
            resolved_schema = self._resolve_schema_decl(schema_decl, unit=schema_unit)
            if not resolved_schema.sections:
                raise CompileError(
                    f"Output-attached schema must export at least one section in output {decl.name}: {schema_decl.name}"
                )
            body.append(f"- Schema: {schema_decl.title}")
            body.append("")
            body.append(self._compile_schema_sections_block(resolved_schema))
        if decl.structure_ref is not None:
            if files_section is not None:
                raise CompileError(
                    f"Output structure requires one markdown-bearing output artifact in {decl.name}"
                )
            if shape_item is None or not self._is_markdown_shape_value(shape_item.value, unit=unit):
                raise CompileError(
                    f"Output structure requires a markdown-bearing shape in output {decl.name}"
                )
            document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            resolved_document = self._resolve_document_decl(document_decl, unit=document_unit)
            body.append(f"- Structure: {document_decl.title}")
            body.append("")
            body.append(
                CompiledSection(
                    title=f"Structure: {document_decl.title}",
                    body=self._compile_document_body(
                        resolved_document,
                        unit=document_unit,
                    ),
                    render_profile=explicit_render_profile or resolved_document.render_profile,
                )
            )

        trust_surface_section = (
            self._compile_trust_surface_section(
                decl,
                unit=unit,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if decl.trust_surface
            else None
        )

        if extras:
            support_items = self._compile_output_support_items(
                extras,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="output prose",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
                trust_surface_section=trust_surface_section,
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
    ) -> CompiledSection:
        lines: list[CompiledBodyItem] = []
        for item in decl.trust_surface:
            field_node = self._resolve_output_field_node(
                decl,
                path=item.path,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
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
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise CompileError(
                    f"`files` entries must be titled sections in output {output_name}"
                )
            scalar_items, _section_items, extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise CompileError(
                    f"Output file entry is missing string path in {output_name}: {item.key}"
                )
            if shape_item is None:
                raise CompileError(
                    f"Output file entry is missing shape in {output_name}: {item.key}"
                )
            body.append(f"- {item.title}: `{path_item.value}`")
            body.append(
                f"- {item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {output_name} file {item.key}', surface_label='output file fields')}"
            )
            if extras:
                body.append("")
                body.append(
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
        return tuple(body)
