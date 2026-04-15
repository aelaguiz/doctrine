from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.naming import _humanize_key
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    CompiledBodyItem,
    CompiledFinalOutputSpec,
    CompiledReviewSpec,
    CompiledSection,
    FinalOutputJsonShapeSummary,
    IndexedUnit,
    OutputDeclKey,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)
from doctrine._compiler.support_files import _dotted_decl_name
from doctrine.emit_common import name_slug


class CompileFinalOutputMixin:
    """Final-output compile helpers for CompilationContext."""

    def _compile_final_output_spec(
        self,
        *,
        agent_name: str,
        field: model.FinalOutputField,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        review_contract: CompiledReviewSpec | None = None,
        fallback_review_semantics: ReviewSemanticContext | None = None,
    ) -> CompiledFinalOutputSpec:
        owner_label = f"agent {agent_name} final_output"
        output_unit, output_decl = self._resolve_final_output_decl(
            field.value,
            unit=unit,
            owner_label=owner_label,
        )
        output_key = (output_unit.module_parts, output_decl.name)
        if output_key not in agent_contract.outputs:
            raise CompileError(
                "E212 final_output output is not emitted by the concrete turn in "
                f"agent {agent_name}: {_dotted_decl_name(output_unit.module_parts, output_decl.name)}"
            )
        review_semantics = self._review_output_context_for_key(
            review_output_contexts,
            output_key,
        )
        if review_semantics is None:
            review_semantics = fallback_review_semantics
        route_semantics = self._route_output_context_for_key(
            route_output_contexts,
            output_key,
        )

        scalar_items, section_items, extras = self._split_record_items(
            output_decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {output_decl.name}",
        )
        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        if (
            files_section is not None
            or target_item is None
            or shape_item is None
            or not isinstance(target_item.value, model.NameRef)
            or not self._is_builtin_turn_response_target_ref(target_item.value)
        ):
            raise CompileError(
                "E213 final_output must designate one TurnResponse output, not files or another "
                f"target, in agent {agent_name}: {_dotted_decl_name(output_unit.module_parts, output_decl.name)}"
            )
        explicit_render_profile, render_profile = self._resolve_output_render_profiles(
            output_decl,
            unit=output_unit,
            files_section=files_section,
            shape_item=shape_item,
        )
        self._validate_output_guard_sections(
            output_decl,
            unit=output_unit,
            allow_review_semantics=review_semantics is not None,
            allow_route_semantics=route_semantics is not None,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )

        requirement = (
            self._display_symbol_value(
                requirement_item.value,
                unit=output_unit,
                owner_label=f"output {output_decl.name}",
                surface_label="output fields",
            )
            if requirement_item is not None
            else None
        )
        shape_name = self._final_output_shape_name(shape_item.value)
        shape_title = self._display_output_shape(
            shape_item.value,
            unit=output_unit,
            owner_label=output_decl.name,
            surface_label="output fields",
        )
        json_summary = self._resolve_final_output_json_shape_summary(
            shape_item.value,
            unit=output_unit,
        )
        generated_schema_relpath = (
            self._generated_final_output_schema_relpath(output_decl.name)
            if json_summary is not None
            else None
        )
        section = self._compile_final_output_section(
            output_decl,
            unit=output_unit,
            requirement=requirement,
            shape_title=shape_title,
            json_summary=json_summary,
            generated_schema_relpath=generated_schema_relpath,
            extras=extras,
            review_contract=review_contract,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
            explicit_render_profile=explicit_render_profile,
        )
        return CompiledFinalOutputSpec(
            output_key=output_key,
            output_name=output_decl.name,
            output_title=output_decl.title,
            target_title="Turn Response",
            shape_name=shape_name,
            shape_title=shape_title,
            requirement=requirement,
            format_mode="json_object" if json_summary is not None else "prose",
            schema_name=json_summary.schema_decl.name if json_summary is not None else None,
            schema_title=json_summary.schema_decl.title if json_summary is not None else None,
            schema_profile=json_summary.schema_profile if json_summary is not None else None,
            generated_schema_relpath=generated_schema_relpath,
            lowered_schema=json_summary.lowered_schema if json_summary is not None else None,
            section=section,
        )

    def _compile_final_output_section(
        self,
        output_decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        requirement: str | None,
        shape_title: str,
        json_summary: FinalOutputJsonShapeSummary | None,
        generated_schema_relpath: str | None,
        extras: tuple[model.AnyRecordItem, ...],
        review_contract: CompiledReviewSpec | None,
        review_semantics: ReviewSemanticContext | None,
        route_semantics: RouteSemanticContext | None,
        render_profile: ResolvedRenderProfile | None,
        explicit_render_profile: ResolvedRenderProfile | None,
    ) -> CompiledSection:
        format_label = self._final_output_format_label(
            output_decl,
            unit=unit,
            json_summary=json_summary,
        )
        metadata_rows = [
            ("Message type", "Final assistant message"),
            ("Format", format_label),
            ("Shape", shape_title),
        ]
        if json_summary is not None:
            metadata_rows.append(("Schema", json_summary.schema_decl.title))
            if json_summary.schema_profile is not None:
                metadata_rows.append(("Profile", json_summary.schema_profile))
            if generated_schema_relpath is not None:
                metadata_rows.append(("Generated Schema", f"`{generated_schema_relpath}`"))
        if requirement is not None:
            metadata_rows.append(("Requirement", requirement))

        body: list[CompiledBodyItem] = [
            "> **Final answer contract**",
            "> "
            + (
                "End the turn with one final assistant message that follows this schema."
                if json_summary is not None
                else "End the turn with one final assistant message that follows this contract."
            ),
            "",
            *self._pipe_table_lines(("Contract", "Value"), tuple(metadata_rows)),
        ]

        if json_summary is not None and json_summary.payload_rows:
            body.extend(
                [
                    "",
                    CompiledSection(
                        title="Payload Fields",
                        body=tuple(
                            self._pipe_table_lines(
                                ("Field", "Type", "Required On Wire", "Null Allowed", "Meaning"),
                                json_summary.payload_rows,
                            )
                        ),
                    ),
                ]
            )

        if json_summary is not None and json_summary.example_text is not None:
            body.extend(
                [
                    "",
                    CompiledSection(
                        title="Example",
                        body=(
                            "```json",
                            *json_summary.example_text.rstrip("\n").splitlines(),
                            "```",
                        ),
                    ),
                ]
            )

        review_response_semantics = self._compile_final_output_review_response_semantics(
            review_contract=review_contract,
        )
        if review_response_semantics is not None:
            body.extend(["", review_response_semantics])

        if output_decl.schema_ref is not None:
            schema_unit, schema_decl = self._resolve_schema_ref(
                output_decl.schema_ref,
                unit=unit,
            )
            resolved_schema = self._resolve_schema_decl(schema_decl, unit=schema_unit)
            if not resolved_schema.sections:
                raise CompileError(
                    f"Output-attached schema must export at least one section in output {output_decl.name}: {schema_decl.name}"
                )
            body.extend(
                [
                    "",
                    CompiledSection(
                        title=f"Schema: {schema_decl.title}",
                        body=(self._compile_schema_sections_block(resolved_schema),),
                    ),
                ]
            )

        if output_decl.structure_ref is not None:
            document_unit, document_decl = self._resolve_document_ref(
                output_decl.structure_ref,
                unit=unit,
            )
            resolved_document = self._resolve_document_decl(document_decl, unit=document_unit)
            body.extend(
                [
                    "",
                    CompiledSection(
                        title=f"Structure: {document_decl.title}",
                        body=self._compile_document_body(
                            resolved_document,
                            unit=document_unit,
                        ),
                        render_profile=explicit_render_profile or resolved_document.render_profile,
                    ),
                ]
            )

        trust_surface_section = (
            self._compile_trust_surface_section(
                output_decl,
                unit=unit,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if output_decl.trust_surface
            else None
        )

        if json_summary is not None:
            body.extend(
                self._compile_output_support_items(
                    json_summary.extra_items,
                    unit=json_summary.shape_unit,
                    owner_label=f"output shape {json_summary.shape_decl.name}",
                    surface_label="final_output shape support",
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                    insert_item_spacers=True,
                )
            )
        body.extend(
            self._compile_output_support_items(
                extras,
                unit=unit,
                owner_label=f"output {output_decl.name}",
                surface_label="final_output support",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
                trust_surface_section=trust_surface_section,
                standalone_title="Read on Its Own",
                insert_item_spacers=True,
            )
        )

        return CompiledSection(
            title="Final Output",
            body=(
                CompiledSection(
                    title=output_decl.title,
                    body=tuple(body),
                    render_profile=render_profile,
                ),
            ),
        )

    def _generated_final_output_schema_relpath(self, output_name: str) -> str:
        return f"schemas/{name_slug(output_name)}.schema.json"

    def _compile_final_output_review_response_semantics(
        self,
        *,
        review_contract: CompiledReviewSpec | None,
    ) -> CompiledSection | None:
        if review_contract is None or review_contract.final_response.mode != "split":
            return None

        body: list[CompiledBodyItem] = [
            (
                "This final response is separate from the review carrier: "
                f"{review_contract.comment_output.output_name}."
            )
        ]

        if review_contract.final_response.review_fields:
            body.extend(
                [
                    "",
                    *self._pipe_table_lines(
                        ("Meaning", "Field"),
                        tuple(
                            (
                                _humanize_key(field_name),
                                f"`{'.'.join(field_path)}`",
                            )
                            for field_name, field_path in review_contract.final_response.review_fields
                        ),
                    ),
                ]
            )
        else:
            body.extend(["", "This final response does not carry review fields on its own."])

        body.append("")
        if review_contract.final_response.control_ready:
            body.append(
                "This final response is control-ready. A host may read it as the review outcome."
            )
        else:
            body.append(
                "This final response is not control-ready. Read the review carrier for the full review outcome."
            )

        return CompiledSection(
            title="Review Response Semantics",
            body=tuple(body),
        )

    def _compile_output_support_items(
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
        standalone_title: str = "Standalone Read",
        insert_item_spacers: bool = False,
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
            rendered_items = list(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
            if (
                isinstance(item, model.RecordSection)
                and item.key == "standalone_read"
                and standalone_title != "Standalone Read"
            ):
                rendered_items = [
                    replace(rendered, title=standalone_title)
                    if isinstance(rendered, CompiledSection)
                    else rendered
                    for rendered in rendered_items
                ]
            if compiled and insert_item_spacers:
                compiled.append("")
            compiled.extend(rendered_items)
        if trust_surface_section is not None and not rendered_trust_surface:
            if compiled and insert_item_spacers:
                compiled.append("")
            compiled.append(trust_surface_section)
        return compiled
