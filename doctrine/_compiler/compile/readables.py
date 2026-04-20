from __future__ import annotations

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.constants import _semantic_render_target_for_block
from doctrine._compiler.naming import _humanize_key
from doctrine._compiler.readable_diagnostics import (
    invalid_readable_block_error,
    readable_source_span,
)
from doctrine._compiler.resolved_types import (
    CompileError,
    CompiledBodyItem,
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
    ResolvedAnalysisSectionItem,
    ResolvedDocumentBody,
    ResolvedRenderProfile,
    ResolvedSchemaBody,
    ResolvedSectionRef,
)


class CompileReadablesMixin:
    """Readable declaration compile helpers for CompilationContext."""

    def _internal_readable_compile_error(
        self,
        *,
        detail: str,
        unit: IndexedUnit,
        source_span: model.SourceSpan | None,
    ) -> CompileError:
        return compile_error(
            code="E901",
            summary="Internal compiler error",
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=source_span,
            hints=("This is a compiler bug, not a prompt authoring error.",),
        )

    def _compile_analysis_decl(
        self,
        decl: model.AnalysisDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        resolved = self._resolve_analysis_decl(decl, unit=unit)
        body: list[CompiledBodyItem] = list(resolved.preamble)
        for item in resolved.items:
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=item.title,
                    body=self._compile_analysis_section_body(item.items, unit=item.unit),
                    semantic_target="analysis.stages",
                )
            )
        return CompiledSection(
            title=resolved.title,
            body=tuple(body),
            render_profile=resolved.render_profile or ResolvedRenderProfile(name="ContractMarkdown"),
        )

    def _compile_analysis_section_body(
        self,
        items: tuple[ResolvedAnalysisSectionItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            if isinstance(item, ResolvedSectionRef):
                body.append(f"- {item.label}")
                continue
            if isinstance(item, model.ProveStmt):
                body.append(
                    f"Prove {item.target_title} from {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                continue
            if isinstance(item, model.DeriveStmt):
                body.append(
                    f"Derive {item.target_title} from {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                continue
            if isinstance(item, model.ClassifyStmt):
                _enum_unit, enum_decl = self._resolve_enum_ref(item.enum_ref, unit=unit)
                body.append(f"Classify {item.target_title} using {enum_decl.title}.")
                continue
            if isinstance(item, model.CompareStmt):
                sentence = (
                    f"Compare {item.target_title} against {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                if item.using_expr is not None:
                    sentence += (
                        f" Use {self._render_analysis_using_expr(item.using_expr, unit=unit)} as the comparison basis."
                    )
                body.append(sentence)
                continue
            if isinstance(item, model.DefendStmt):
                body.append(
                    f"Defend {item.target_title} using {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                continue
            raise self._internal_readable_compile_error(
                detail=(
                    "Internal compiler error: unsupported analysis item "
                    f"{type(item).__name__}"
                ),
                unit=unit,
                source_span=readable_source_span(item),
            )
        return tuple(body)

    def _compile_decision_decl(
        self,
        decl: model.DecisionDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        body: list[CompiledBodyItem] = [
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=f"decision {decl.name}",
                surface_label="decision prose",
                ambiguous_label="decision prose interpolation ref",
            )
            for line in decl.body.preamble
        ]
        for item in decl.body.items:
            if isinstance(item, model.DecisionMinimumCandidates):
                body.append(
                    f"Build at least {item.count} candidates before choosing a winner."
                )
                continue
            if isinstance(item, model.DecisionRequiredItem):
                body.append(self._render_decision_required_item(item))
                continue
            if isinstance(item, model.DecisionChooseWinner):
                body.append("Choose exactly one winner.")
                continue
            if isinstance(item, model.DecisionRankBy):
                dimensions = self._natural_language_join(
                    [_humanize_key(dimension) for dimension in item.dimensions]
                )
                body.append(f"Rank by {dimensions}.")
                continue
            raise self._internal_readable_compile_error(
                detail=(
                    "Internal compiler error: unsupported decision item "
                    f"{type(item).__name__}"
                ),
                unit=unit,
                source_span=readable_source_span(item),
            )
        render_profile = (
            self._resolve_render_profile_ref(decl.render_profile_ref, unit=unit)
            if decl.render_profile_ref is not None
            else ResolvedRenderProfile(name="ContractMarkdown")
        )
        return CompiledSection(
            title=decl.title,
            body=tuple(body),
            render_profile=render_profile,
        )

    def _compile_schema_decl(
        self,
        decl: model.SchemaDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        resolved = self._resolve_schema_decl(decl, unit=unit)
        body: list[CompiledBodyItem] = list(resolved.preamble)
        blocks: list[CompiledReadableBlock] = []
        if resolved.sections:
            blocks.append(self._compile_schema_sections_block(resolved))
        if resolved.gates:
            blocks.append(self._compile_schema_gates_block(resolved))
        if resolved.artifacts:
            blocks.append(self._compile_schema_artifacts_block(resolved))
        if resolved.groups:
            blocks.append(self._compile_schema_groups_block(resolved))
        for index, block in enumerate(blocks):
            if body and index == 0:
                body.append("")
            elif index > 0:
                body.append("")
            body.append(block)
        return CompiledSection(
            title=resolved.title,
            body=tuple(body),
            render_profile=resolved.render_profile or ResolvedRenderProfile(name="ContractMarkdown"),
        )

    def _compile_schema_sections_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledSection:
        return CompiledSection(
            title="Required Sections",
            body=tuple(
                CompiledSection(title=item.title, body=item.body) for item in schema_body.sections
            ),
        )

    def _compile_schema_gates_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledSection:
        return CompiledSection(
            title="Contract Gates",
            body=tuple(
                CompiledSection(title=item.title, body=item.body) for item in schema_body.gates
            ),
        )

    def _compile_schema_artifacts_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledBulletsBlock:
        return CompiledBulletsBlock(
            title="Artifact Inventory",
            items=tuple(item.title for item in schema_body.artifacts),
        )

    def _compile_schema_groups_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledSection:
        artifact_titles = {item.key: item.title for item in schema_body.artifacts}
        body: list[str] = []
        for group in schema_body.groups:
            body.append(f"- {group.title}")
            for member_key in group.members:
                body.append(f"  - {artifact_titles[member_key]}")
        return CompiledSection(title="Surface Groups", body=tuple(body))

    def _compile_document_decl(
        self,
        decl: model.DocumentDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        resolved = self._resolve_document_decl(decl, unit=unit)
        return CompiledSection(
            title=resolved.title,
            body=self._compile_document_body(resolved, unit=unit),
            render_profile=resolved.render_profile or ResolvedRenderProfile(name="ContractMarkdown"),
        )

    def _compile_table_decl(
        self,
        decl: model.TableDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        return CompiledSection(
            title=decl.title,
            body=(
                CompiledTableBlock(
                    title=f"{decl.title} Contract",
                    table=self._compile_resolved_readable_table_payload(
                        self._resolve_table_decl_data(decl, unit=unit),
                        unit=unit,
                        owner_label=f"table declaration `{decl.name}`",
                        source_span=decl.source_span,
                    ),
                ),
            ),
            render_profile=ResolvedRenderProfile(name="ContractMarkdown"),
        )

    def _compile_document_body(
        self,
        document_body: ResolvedDocumentBody,
        *,
        unit: IndexedUnit,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = list(document_body.preamble)
        for item in document_body.items:
            if body and body[-1] != "":
                body.append("")
            body.append(self._compile_document_block(item, unit=unit))
        return tuple(body)

    def _compile_document_block(
        self,
        block: model.DocumentBlock,
        *,
        unit: IndexedUnit,
    ) -> CompiledReadableBlock:
        when_text = self._readable_guard_text(block.when_expr, unit=unit)
        if block.anonymous:
            title = None
        elif block.kind in {"sequence", "bullets", "checklist"}:
            title = block.title
        else:
            title = block.title or _humanize_key(block.key)
        if block.kind == "section":
            return CompiledSection(
                title=title or _humanize_key(block.key),
                body=self._compile_document_section_payload(
                    block.payload,
                    unit=unit,
                    owner_label=f"document block `{block.key}`",
                    source_span=block.source_span,
                ),
                requirement=block.requirement,
                when_text=when_text,
                emit_metadata=block.requirement is not None or block.when_expr is not None,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind in {"sequence", "bullets", "checklist"}:
            compiled_cls = {
                "sequence": CompiledSequenceBlock,
                "bullets": CompiledBulletsBlock,
                "checklist": CompiledChecklistBlock,
            }[block.kind]
            return compiled_cls(
                title=title,
                items=self._compile_readable_list_payload(
                    block.payload,
                    unit=unit,
                    owner_label=f"document block `{block.key}`",
                    source_span=block.source_span,
                ),
                requirement=block.requirement,
                when_text=when_text,
                item_schema=block.item_schema,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
                anonymous=block.anonymous,
            )
        if block.kind == "properties":
            payload = self._compile_readable_properties_payload(
                block.payload,
                unit=unit,
                owner_label=f"document block `{block.key}`",
                source_span=block.source_span,
            )
            return CompiledPropertiesBlock(
                title=title,
                entries=payload.entries,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "definitions":
            return CompiledDefinitionsBlock(
                title=title,
                items=self._compile_readable_definitions_payload(
                    block.payload,
                    unit=unit,
                    owner_label=f"document block `{block.key}`",
                    source_span=block.source_span,
                ),
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "table":
            return CompiledTableBlock(
                title=title,
                table=self._compile_resolved_readable_table_payload(
                    block.payload,
                    unit=unit,
                    owner_label=f"document block `{block.key}`",
                    source_span=block.source_span,
                ),
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "guard":
            if when_text is None:
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable guard shell `{block.key}` must define a guard expression."
                    ),
                    unit=unit,
                    source_span=block.source_span,
                    hints=("Add a `when ...` guard expression to the guard block.",),
                )
            return CompiledGuardBlock(
                title=title or _humanize_key(block.key),
                body=self._compile_document_section_payload(
                    block.payload,
                    unit=unit,
                    owner_label=f"document block `{block.key}`",
                    source_span=block.source_span,
                ),
                when_text=when_text,
            )
        if block.kind == "callout":
            payload = self._compile_readable_callout_payload(
                block.payload,
                unit=unit,
                owner_label=f"document block `{block.key}`",
                source_span=block.source_span,
            )
            return CompiledCalloutBlock(
                title=title,
                body=payload.body,
                kind=payload.kind,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "code":
            payload = self._compile_readable_code_payload(
                block.payload,
                unit=unit,
                owner_label=f"document block `{block.key}`",
                source_span=block.source_span,
            )
            return CompiledCodeBlock(
                title=title,
                text=payload.text,
                language=payload.language,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind in {"markdown", "html"}:
            payload = self._compile_readable_raw_text_payload(
                block.payload,
                unit=unit,
                owner_label=f"document block `{block.key}`",
                source_span=block.source_span,
            )
            return CompiledRawTextBlock(
                title=title,
                text=payload.text,
                kind=block.kind,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "footnotes":
            payload = self._compile_readable_footnotes_payload(
                block.payload,
                unit=unit,
                owner_label=f"document block `{block.key}`",
                source_span=block.source_span,
            )
            return CompiledFootnotesBlock(
                title=title,
                entries=payload.entries,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "image":
            payload = self._compile_readable_image_payload(
                block.payload,
                unit=unit,
                owner_label=f"document block `{block.key}`",
                source_span=block.source_span,
            )
            return CompiledImageBlock(
                title=title,
                src=payload.src,
                alt=payload.alt,
                caption=payload.caption,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "rule":
            return CompiledRuleBlock(
                requirement=block.requirement,
                when_text=when_text,
            )
        raise self._internal_readable_compile_error(
            detail=f"Internal compiler error: unsupported document block kind {block.kind}",
            unit=unit,
            source_span=block.source_span,
        )

    def _compile_document_section_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> tuple[CompiledBodyItem, ...]:
        if not isinstance(payload, tuple):
            raise invalid_readable_block_error(
                detail=f"Document section payload must stay block-like in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        body: list[CompiledBodyItem] = []
        for item in payload:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            if not isinstance(item, model.ReadableBlock):
                raise invalid_readable_block_error(
                    detail=f"Document section payload contains an invalid item in {owner_label}.",
                    unit=unit,
                    source_span=readable_source_span(item) or source_span,
                )
            body.append(self._compile_document_block(item, unit=unit))
        return tuple(body)

    def _compile_readable_list_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> tuple[model.ProseLine, ...]:
        if not isinstance(payload, tuple):
            raise invalid_readable_block_error(
                detail=f"Readable list payload must stay list-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        items: list[model.ProseLine] = []
        for item in payload:
            if not isinstance(item, model.ReadableListItem):
                raise invalid_readable_block_error(
                    detail=f"Readable list payload contains an invalid item in {owner_label}.",
                    unit=unit,
                    source_span=readable_source_span(item) or source_span,
                )
            items.append(item.text)
        return tuple(items)

    def _compile_readable_definitions_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> tuple[model.ReadableDefinitionItem, ...]:
        if not isinstance(payload, tuple):
            raise invalid_readable_block_error(
                detail=(
                    f"Readable definitions payload must stay definition-shaped in {owner_label}."
                ),
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        items: list[model.ReadableDefinitionItem] = []
        for item in payload:
            if not isinstance(item, model.ReadableDefinitionItem):
                raise invalid_readable_block_error(
                    detail=(
                        f"Readable definitions payload contains an invalid item in "
                        f"{owner_label}."
                    ),
                    unit=unit,
                    source_span=readable_source_span(item) or source_span,
                )
            items.append(item)
        return tuple(items)

    def _compile_readable_properties_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> model.ReadablePropertiesData:
        if not isinstance(payload, model.ReadablePropertiesData):
            raise invalid_readable_block_error(
                detail=(
                    f"Readable properties payload must stay properties-shaped in "
                    f"{owner_label}."
                ),
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        return payload

    def _compile_readable_table_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> model.ReadableTableData:
        if not isinstance(payload, model.ReadableTableData):
            raise invalid_readable_block_error(
                detail=f"Readable table payload must stay table-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        if not payload.columns:
            raise invalid_readable_block_error(
                detail="Readable table must declare at least one column.",
                unit=unit,
                source_span=payload.source_span or source_span,
                hints=("Declare at least one table column before rows or notes.",),
            )
        return payload

    def _compile_resolved_readable_table_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> CompiledTableData:
        table = self._compile_readable_table_payload(
            payload,
            unit=unit,
            owner_label=owner_label,
            source_span=source_span,
        )
        compiled_rows: list[CompiledTableRow] = []
        for row in table.rows:
            compiled_cells: list[CompiledTableCell] = []
            for cell in row.cells:
                if cell.body is not None:
                    compiled_cells.append(
                        CompiledTableCell(
                            key=cell.key,
                            body=self._compile_document_section_payload(
                                cell.body,
                                unit=unit,
                                owner_label=f"{owner_label}.{row.key}.{cell.key}",
                                source_span=cell.source_span or row.source_span,
                            ),
                        )
                    )
                    continue
                compiled_cells.append(CompiledTableCell(key=cell.key, text=cell.text or ""))
            compiled_rows.append(CompiledTableRow(key=row.key, cells=tuple(compiled_cells)))

        return CompiledTableData(
            columns=tuple(
                CompiledTableColumn(
                    key=column.key,
                    title=column.title,
                    body=column.body,
                    type_ref=column.type_ref,
                )
                for column in table.columns
            ),
            rows=tuple(compiled_rows),
            notes=table.notes,
            row_schema=table.row_schema,
        )

    def _compile_readable_callout_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> model.ReadableCalloutData:
        if not isinstance(payload, model.ReadableCalloutData):
            raise invalid_readable_block_error(
                detail=f"Readable callout payload must stay callout-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        return payload

    def _compile_readable_code_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> model.ReadableCodeData:
        if not isinstance(payload, model.ReadableCodeData):
            raise invalid_readable_block_error(
                detail=f"Readable code payload must stay code-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        return payload

    def _compile_readable_raw_text_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> model.ReadableRawTextData:
        if not isinstance(payload, model.ReadableRawTextData):
            raise invalid_readable_block_error(
                detail=f"Readable raw text payload must stay text-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        if "\n" not in payload.text:
            raise invalid_readable_block_error(
                detail="Raw text readable blocks must use a multiline string.",
                unit=unit,
                source_span=payload.source_span or source_span,
                hints=("Use a multiline string for raw markdown or html readable blocks.",),
            )
        return payload

    def _compile_readable_footnotes_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> model.ReadableFootnotesData:
        if not isinstance(payload, model.ReadableFootnotesData):
            raise invalid_readable_block_error(
                detail=f"Readable footnotes payload must stay footnotes-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        return payload

    def _compile_readable_image_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> model.ReadableImageData:
        if not isinstance(payload, model.ReadableImageData):
            raise invalid_readable_block_error(
                detail=f"Readable image payload must stay image-shaped in {owner_label}.",
                unit=unit,
                source_span=readable_source_span(payload) or source_span,
            )
        return payload
