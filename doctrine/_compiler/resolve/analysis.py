from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import (
    IndexedUnit,
    ResolvedAnalysisBody,
    ResolvedAnalysisSection,
    ResolvedAnalysisSectionItem,
    ResolvedSectionRef,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveAnalysisMixin:
    """Analysis resolution helpers for ResolveMixin."""

    def _analysis_compile_error(
        self,
        *,
        detail: str,
        unit: IndexedUnit,
        source_span: model.SourceSpan | None,
        code: str = "E299",
        summary: str = "Compile failure",
        related=(),
        hints: tuple[str, ...] = (),
    ):
        return compile_error(
            code=code,
            summary=summary,
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=source_span,
            related=related,
            hints=hints,
        )

    def _analysis_related_site(
        self,
        *,
        label: str,
        unit: IndexedUnit,
        source_span: model.SourceSpan | None,
    ):
        return related_prompt_site(
            label=label,
            path=unit.prompt_file.source_path,
            source_span=source_span,
        )

    def _missing_analysis_related_sites(
        self,
        *,
        parent_analysis: ResolvedAnalysisBody | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_analysis is None:
            return ()
        related = []
        for key in missing_keys:
            parent_item = next((item for item in parent_analysis.items if item.key == key), None)
            if parent_item is None:
                continue
            related.append(
                self._analysis_related_site(
                    label=f"inherited `{key}` entry",
                    unit=parent_item.unit,
                    source_span=parent_item.source_span,
                )
            )
        return tuple(related)

    def _resolve_analysis_decl(
        self, analysis_decl: model.AnalysisDecl, *, unit: IndexedUnit
    ) -> ResolvedAnalysisBody:
        analysis_key = (unit.module_parts, analysis_decl.name)
        cached = self._resolved_analysis_cache.get(analysis_key)
        if cached is not None:
            return cached

        if analysis_key in self._analysis_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._analysis_resolution_stack, analysis_key]
            )
            raise self._analysis_compile_error(
                detail=f"Cyclic analysis inheritance: {cycle}",
                unit=unit,
                source_span=analysis_decl.source_span,
            )

        self._analysis_resolution_stack.append(analysis_key)
        try:
            parent_analysis: ResolvedAnalysisBody | None = None
            parent_label: str | None = None
            if analysis_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_analysis_decl(
                    analysis_decl,
                    unit=unit,
                )
                parent_analysis = self._resolve_analysis_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"analysis {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_analysis_body(
                analysis_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, analysis_decl.name),
                owner_source_span=analysis_decl.source_span,
                parent_analysis=parent_analysis,
                parent_label=parent_label,
            )
            resolved = replace(
                resolved,
                render_profile=(
                    self._resolve_render_profile_ref(analysis_decl.render_profile_ref, unit=unit)
                    if analysis_decl.render_profile_ref is not None
                    else parent_analysis.render_profile if parent_analysis is not None else None
                ),
            )
            self._resolved_analysis_cache[analysis_key] = resolved
            return resolved
        finally:
            self._analysis_resolution_stack.pop()

    def _resolve_analysis_body(
        self,
        analysis_body: model.AnalysisBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        owner_source_span: model.SourceSpan | None = None,
        parent_analysis: ResolvedAnalysisBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedAnalysisBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="analysis prose",
                ambiguous_label="analysis prose interpolation ref",
            )
            for line in analysis_body.preamble
        )
        if parent_analysis is None:
            resolved_items = self._resolve_non_inherited_analysis_items(
                analysis_body.items,
                unit=unit,
                owner_label=owner_label,
            )
            return ResolvedAnalysisBody(
                title=analysis_body.title,
                preamble=resolved_preamble,
                items=resolved_items,
            )

        parent_items_by_key = {item.key: item for item in parent_analysis.items}
        resolved_items: list[ResolvedAnalysisSection] = []
        emitted_keys: dict[str, model.AnalysisItem] = {}
        accounted_keys: set[str] = set()

        for item in analysis_body.items:
            key = item.key
            if key in emitted_keys:
                raise self._analysis_compile_error(
                    detail=f"Duplicate analysis section key in {owner_label}: {key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        self._analysis_related_site(
                            label=f"first `{key}` analysis section",
                            unit=unit,
                            source_span=emitted_keys[key].source_span,
                        ),
                    ),
                )
            emitted_keys[key] = item

            if isinstance(item, model.AnalysisSection):
                if key in parent_items_by_key:
                    raise self._analysis_compile_error(
                        detail=f"Inherited analysis requires `override {key}` in {owner_label}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                resolved_items.append(
                    ResolvedAnalysisSection(
                        unit=unit,
                        key=key,
                        title=item.title,
                        items=self._resolve_analysis_section_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                        source_span=item.source_span,
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise self._analysis_compile_error(
                        detail=f"Cannot inherit undefined analysis entry in {parent_label}: {key}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise self._analysis_compile_error(
                    code="E001",
                    summary="Cannot override undefined inherited entry",
                    detail=f"Cannot override undefined analysis entry in {parent_label}: {key}",
                    unit=unit,
                    source_span=item.source_span,
                )

            accounted_keys.add(key)
            resolved_items.append(
                ResolvedAnalysisSection(
                    unit=unit,
                    key=key,
                    title=item.title if item.title is not None else parent_item.title,
                    items=self._resolve_analysis_section_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                    ),
                    source_span=item.source_span,
                )
            )

        missing_keys = [
            parent_item.key for parent_item in parent_analysis.items if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise self._analysis_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=f"Missing inherited analysis entry in {owner_label}: {missing}",
                unit=unit,
                source_span=owner_source_span,
                related=self._missing_analysis_related_sites(
                    parent_analysis=parent_analysis,
                    missing_keys=tuple(missing_keys),
                ),
            )

        return ResolvedAnalysisBody(
            title=analysis_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_non_inherited_analysis_items(
        self,
        items: tuple[model.AnalysisItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedAnalysisSection, ...]:
        resolved_items: list[ResolvedAnalysisSection] = []
        seen_keys: dict[str, model.AnalysisSection] = {}
        for item in items:
            if isinstance(item, model.AnalysisSection):
                if item.key in seen_keys:
                    raise self._analysis_compile_error(
                        detail=f"Duplicate analysis section key in {owner_label}: {item.key}",
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            self._analysis_related_site(
                                label=f"first `{item.key}` analysis section",
                                unit=unit,
                                source_span=seen_keys[item.key].source_span,
                            ),
                        ),
                    )
                seen_keys[item.key] = item
                resolved_items.append(
                    ResolvedAnalysisSection(
                        unit=unit,
                        key=item.key,
                        title=item.title,
                        items=self._resolve_analysis_section_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                        source_span=item.source_span,
                    )
                )
                continue
            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise self._analysis_compile_error(
                detail=f"{item_label} requires an inherited analysis declaration in {owner_label}: {item.key}",
                unit=unit,
                source_span=item.source_span,
            )
        return tuple(resolved_items)

    def _resolve_analysis_section_items(
        self,
        items: tuple[model.AnalysisSectionItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedAnalysisSectionItem, ...]:
        resolved: list[ResolvedAnalysisSectionItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="analysis prose",
                        ambiguous_label="analysis prose interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.SectionBodyRef):
                display = self._resolve_addressable_ref_value(
                    item.ref,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label="analysis refs",
                    ambiguous_label="analysis ref",
                    missing_local_label="analysis",
                )
                resolved.append(ResolvedSectionRef(label=display.text))
                continue
            if isinstance(item, (model.ProveStmt, model.DeriveStmt, model.CompareStmt, model.DefendStmt)):
                basis = self._coerce_path_set(item.basis)
                if not basis.paths:
                    raise self._analysis_compile_error(
                        detail=f"Analysis basis may not be empty in {owner_label}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                self._validate_path_set_roots(
                    basis,
                    unit=unit,
                    agent_contract=None,
                    owner_label=owner_label,
                    statement_label="analysis basis",
                    allowed_kinds=("input", "output", "enum"),
                )
                resolved.append(replace(item, basis=basis))
                continue
            if isinstance(item, model.ClassifyStmt):
                self._resolve_enum_ref(item.enum_ref, unit=unit)
                resolved.append(item)
                continue
            raise self._analysis_compile_error(
                detail=f"Unsupported analysis item in {owner_label}: {type(item).__name__}",
                unit=unit,
                source_span=getattr(item, "source_span", None),
            )
        return tuple(resolved)
