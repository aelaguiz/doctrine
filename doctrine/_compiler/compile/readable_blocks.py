from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.constants import _semantic_render_target_for_block
from doctrine._compiler.naming import _humanize_key
from doctrine._compiler.readable_diagnostics import (
    duplicate_readable_key_error,
    invalid_readable_block_error,
    readable_source_span,
)
from doctrine._compiler.resolved_types import (
    CompiledBulletsBlock,
    CompiledCalloutBlock,
    CompiledChecklistBlock,
    CompiledCodeBlock,
    CompiledDefinitionsBlock,
    CompiledFootnotesBlock,
    CompiledGuardBlock,
    CompiledImageBlock,
    CompiledPropertiesBlock,
    CompiledRawTextBlock,
    CompiledReadableBlock,
    CompiledRuleBlock,
    CompiledSection,
    CompiledSequenceBlock,
    CompiledTableBlock,
    CompiledTableCell,
    CompiledTableColumn,
    CompiledTableData,
    CompiledTableRow,
    IndexedUnit,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)


class CompileReadableBlocksMixin:
    """Readable block compile helpers for CompilationContext."""

    def _internal_readable_block_compile_error(
        self,
        *,
        detail: str,
        unit: IndexedUnit,
        source_span: model.SourceSpan | None,
    ):
        return compile_error(
            code="E901",
            summary="Internal compiler error",
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=source_span,
            hints=("This is a compiler bug, not a prompt authoring error.",),
        )

    def _compile_authored_readable_block(
        self,
        block: model.ReadableBlock,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        section_body_compiler,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> CompiledReadableBlock:
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
        when_text = self._readable_guard_text(block.when_expr, unit=unit)
        title = None if block.kind == "properties" and block.anonymous else (
            block.title if block.kind in {"sequence", "bullets", "checklist"} else (
                block.title or _humanize_key(block.key)
            )
        )
        block_owner_label = f"{owner_label}.{block.key}"
        if block.kind == "section":
            payload = self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="section",
            )
            return CompiledSection(
                title=title or _humanize_key(block.key),
                body=section_body_compiler(payload, block_owner_label),
                requirement=block.requirement,
                when_text=when_text,
                emit_metadata=True,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
        )
        if block.kind in {"sequence", "bullets", "checklist"}:
            items: list[model.ProseLine] = []
            seen_keys: dict[str, model.ReadableListItem] = {}
            for list_item in self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind=block.kind,
            ):
                if not isinstance(list_item, model.ReadableListItem):
                    raise invalid_readable_block_error(
                        detail=(
                            f"Readable {block.kind} items must stay list entries in "
                            f"{block_owner_label}."
                        ),
                        unit=unit,
                        source_span=readable_source_span(list_item) or block.source_span,
                    )
                if list_item.key is not None:
                    if list_item.key in seen_keys:
                        raise duplicate_readable_key_error(
                            subject_label="Readable surface",
                            owner_label=block_owner_label,
                            kind_label=f"{block.kind} item",
                            key=list_item.key,
                            unit=unit,
                            source_span=list_item.source_span,
                            first_source_span=seen_keys[list_item.key].source_span,
                        )
                    seen_keys[list_item.key] = list_item
                items.append(
                    self._interpolate_authored_prose_line(
                        list_item.text,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label=f"{block.kind} item prose",
                        ambiguous_label=f"{block.kind} item interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                )
            item_schema = self._resolve_readable_inline_schema(
                block.item_schema,
                unit=unit,
                owner_label=block_owner_label,
                schema_label="item_schema",
                surface_label=f"{block.kind} item schema",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            compiled_cls = {
                "sequence": CompiledSequenceBlock,
                "bullets": CompiledBulletsBlock,
                "checklist": CompiledChecklistBlock,
            }[block.kind]
            return compiled_cls(
                title=title,
                items=tuple(items),
                requirement=block.requirement,
                when_text=when_text,
                item_schema=item_schema,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind == "properties":
            properties = self._resolve_readable_properties_payload(
                block.payload,
                unit=unit,
                owner_label=block_owner_label,
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledPropertiesBlock(
                title=title,
                entries=properties.entries,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "definitions":
            definitions: list[model.ReadableDefinitionItem] = []
            seen_keys: dict[str, model.ReadableDefinitionItem] = {}
            for definition in self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="definitions",
            ):
                if not isinstance(definition, model.ReadableDefinitionItem):
                    raise invalid_readable_block_error(
                        detail=(
                            "Readable definitions entries must stay definition items in "
                            f"{block_owner_label}."
                        ),
                        unit=unit,
                        source_span=readable_source_span(definition) or block.source_span,
                    )
                if definition.key in seen_keys:
                    raise duplicate_readable_key_error(
                        subject_label="Readable surface",
                        owner_label=block_owner_label,
                        kind_label="definitions item",
                        key=definition.key,
                        unit=unit,
                        source_span=definition.source_span,
                        first_source_span=seen_keys[definition.key].source_span,
                    )
                seen_keys[definition.key] = definition
                definitions.append(
                    replace(
                        definition,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{block_owner_label}.{definition.key}",
                                surface_label="definitions prose",
                                ambiguous_label="definitions prose interpolation ref",
                                review_semantics=review_semantics,
                                route_semantics=block_route_semantics,
                                render_profile=render_profile,
                            )
                            for line in definition.body
                        ),
                    )
                )
            return CompiledDefinitionsBlock(
                title=title,
                items=tuple(definitions),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "table":
            if not isinstance(block.payload, model.ReadableTableData):
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable table payload must stay table-shaped in "
                        f"{block_owner_label}."
                    ),
                    unit=unit,
                    source_span=readable_source_span(block.payload) or block.source_span,
                )
            resolved_columns: list[CompiledTableColumn] = []
            column_keys: dict[str, model.ReadableTableColumn] = {}
            for column in block.payload.columns:
                if column.key in column_keys:
                    raise duplicate_readable_key_error(
                        subject_label="Readable surface",
                        owner_label=block_owner_label,
                        kind_label="table column",
                        key=column.key,
                        unit=unit,
                        source_span=column.source_span,
                        first_source_span=column_keys[column.key].source_span,
                    )
                column_keys[column.key] = column
                resolved_columns.append(
                    CompiledTableColumn(
                        key=column.key,
                        title=column.title,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{block_owner_label}.columns.{column.key}",
                                surface_label="table column prose",
                                ambiguous_label="table column interpolation ref",
                                review_semantics=review_semantics,
                                route_semantics=block_route_semantics,
                                render_profile=render_profile,
                            )
                            for line in column.body
                        ),
                    )
                )
            if not resolved_columns:
                raise invalid_readable_block_error(
                    detail=f"Readable table `{block_owner_label}` must declare at least one column.",
                    unit=unit,
                    source_span=block.source_span,
                    hints=("Declare at least one table column before rows or notes.",),
                )
            resolved_rows: list[CompiledTableRow] = []
            row_keys: dict[str, model.ReadableTableRow] = {}
            for row in block.payload.rows:
                if row.key in row_keys:
                    raise duplicate_readable_key_error(
                        subject_label="Readable surface",
                        owner_label=block_owner_label,
                        kind_label="table row",
                        key=row.key,
                        unit=unit,
                        source_span=row.source_span,
                        first_source_span=row_keys[row.key].source_span,
                    )
                row_keys[row.key] = row
                cell_keys: dict[str, model.ReadableTableCell] = {}
                resolved_cells: list[CompiledTableCell] = []
                for cell in row.cells:
                    if cell.key not in column_keys:
                        raise invalid_readable_block_error(
                            detail=(
                                f"Readable table row in `{block_owner_label}` references "
                                f"unknown column `{cell.key}`."
                            ),
                            unit=unit,
                            source_span=cell.source_span or row.source_span,
                            hints=("Match each table cell key to a declared table column key.",),
                        )
                    if cell.key in cell_keys:
                        raise duplicate_readable_key_error(
                            subject_label="Readable surface",
                            owner_label=f"{block_owner_label}.{row.key}",
                            kind_label="table row cell",
                            key=cell.key,
                            unit=unit,
                            source_span=cell.source_span,
                            first_source_span=cell_keys[cell.key].source_span,
                        )
                    cell_keys[cell.key] = cell
                    if cell.body is not None:
                        resolved_cells.append(
                            CompiledTableCell(
                                key=cell.key,
                                body=section_body_compiler(
                                    cell.body,
                                    f"{block_owner_label}.{row.key}.{cell.key}",
                                ),
                            )
                        )
                        continue
                    cell_text = self._interpolate_authored_prose_string(
                        cell.text or "",
                        unit=unit,
                        owner_label=f"{block_owner_label}.{row.key}.{cell.key}",
                        surface_label="table cell prose",
                        ambiguous_label="table cell interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    if "\n" in cell_text:
                        raise invalid_readable_block_error(
                            detail=(
                                f"Readable table inline cell "
                                f"`{block_owner_label}.{row.key}.{cell.key}` must stay "
                                "single-line unless it uses a structured cell body."
                            ),
                            unit=unit,
                            source_span=cell.source_span or row.source_span,
                            hints=(
                                "Move multi-line cell content into a structured cell body instead "
                                "of an inline table cell.",
                            ),
                        )
                    resolved_cells.append(CompiledTableCell(key=cell.key, text=cell_text))
                resolved_rows.append(CompiledTableRow(key=row.key, cells=tuple(resolved_cells)))
            resolved_notes = tuple(
                self._interpolate_authored_prose_line(
                    line,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="table notes",
                    ambiguous_label="table note interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                )
                for line in block.payload.notes
            )
            row_schema = self._resolve_readable_inline_schema(
                block.row_schema or block.payload.row_schema,
                unit=unit,
                owner_label=block_owner_label,
                schema_label="row_schema",
                surface_label="table row schema",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledTableBlock(
                title=title or _humanize_key(block.key),
                table=CompiledTableData(
                    columns=tuple(resolved_columns),
                    rows=tuple(resolved_rows),
                    notes=resolved_notes,
                    row_schema=row_schema,
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "guard":
            payload = self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="guard",
            )
            if when_text is None:
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable guard shell `{block_owner_label}` must define a guard "
                        "expression."
                    ),
                    unit=unit,
                    source_span=block.source_span,
                    hints=("Add a `when ...` guard expression to the guard block.",),
                )
            return CompiledGuardBlock(
                title=title or _humanize_key(block.key),
                body=section_body_compiler(payload, block_owner_label),
                when_text=when_text,
            )
        if block.kind == "callout":
            if not isinstance(block.payload, model.ReadableCalloutData):
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable callout payload must stay callout-shaped in "
                        f"{block_owner_label}."
                    ),
                    unit=unit,
                    source_span=readable_source_span(block.payload) or block.source_span,
                )
            if block.payload.kind is not None and block.payload.kind not in {
                "required",
                "important",
                "warning",
                "note",
            }:
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable block `{block_owner_label}` uses unknown callout kind "
                        f"`{block.payload.kind}`."
                    ),
                    unit=unit,
                    source_span=block.payload.source_span or block.source_span,
                    hints=(
                        "Use one of the shipped callout kinds: `required`, `important`, "
                        "`warning`, or `note`.",
                    ),
                )
            return CompiledCalloutBlock(
                title=title or _humanize_key(block.key),
                kind=block.payload.kind,
                body=tuple(
                    self._interpolate_authored_prose_line(
                        line,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label="callout prose",
                        ambiguous_label="callout interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    for line in block.payload.body
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "code":
            if not isinstance(block.payload, model.ReadableCodeData):
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable code payload must stay code-shaped in "
                        f"{block_owner_label}."
                    ),
                    unit=unit,
                    source_span=readable_source_span(block.payload) or block.source_span,
                )
            if "\n" not in block.payload.text:
                raise invalid_readable_block_error(
                    detail=f"Readable code block `{block_owner_label}` must use a multiline string.",
                    unit=unit,
                    source_span=block.payload.source_span or block.source_span,
                    hints=("Use a multiline string for readable code block text.",),
                )
            return CompiledCodeBlock(
                title=title or _humanize_key(block.key),
                text=block.payload.text,
                language=block.payload.language,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind in {"markdown", "html"}:
            if not isinstance(block.payload, model.ReadableRawTextData):
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable {block.kind} payload must stay text-shaped in "
                        f"{block_owner_label}."
                    ),
                    unit=unit,
                    source_span=readable_source_span(block.payload) or block.source_span,
                )
            text = self._interpolate_authored_prose_string(
                block.payload.text,
                unit=unit,
                owner_label=block_owner_label,
                surface_label=f"{block.kind} text",
                ambiguous_label=f"{block.kind} interpolation ref",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            if "\n" not in text:
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable {block.kind} block `{block_owner_label}` must use a "
                        "multiline string."
                    ),
                    unit=unit,
                    source_span=block.payload.source_span or block.source_span,
                    hints=("Use a multiline string for raw markdown or html readable blocks.",),
                )
            return CompiledRawTextBlock(
                title=title or _humanize_key(block.key),
                text=text,
                kind=block.kind,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "footnotes":
            footnotes = self._resolve_readable_footnotes_payload(
                block.payload,
                unit=unit,
                owner_label=block_owner_label,
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledFootnotesBlock(
                title=title or _humanize_key(block.key),
                entries=footnotes.entries,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "image":
            if not isinstance(block.payload, model.ReadableImageData):
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable image payload must stay image-shaped in "
                        f"{block_owner_label}."
                    ),
                    unit=unit,
                    source_span=readable_source_span(block.payload) or block.source_span,
                )
            return CompiledImageBlock(
                title=title or _humanize_key(block.key),
                src=self._interpolate_authored_prose_string(
                    block.payload.src,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="image src",
                    ambiguous_label="image src interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                ),
                alt=self._interpolate_authored_prose_string(
                    block.payload.alt,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="image alt",
                    ambiguous_label="image alt interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                ),
                caption=(
                    self._interpolate_authored_prose_string(
                        block.payload.caption,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label="image caption",
                        ambiguous_label="image caption interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    if block.payload.caption is not None
                    else None
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "rule":
            return CompiledRuleBlock(
                requirement=block.requirement,
                when_text=when_text,
            )
        raise self._internal_readable_block_compile_error(
            detail=(
                f"Internal compiler error: unsupported readable block kind in "
                f"{block_owner_label}: {block.kind}"
            ),
            unit=unit,
            source_span=block.source_span,
        )
