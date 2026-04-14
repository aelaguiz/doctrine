from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.resolved_types import (
    CompileError,
    IndexedUnit,
    ResolvedAnalysisBody,
    ResolvedAnalysisSection,
    ResolvedAnalysisSectionItem,
    ResolvedSectionRef,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveAnalysisMixin:
    """Analysis resolution helpers for ResolveMixin."""

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
            raise CompileError(f"Cyclic analysis inheritance: {cycle}")

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
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in analysis_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate analysis section key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.AnalysisSection):
                if key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited analysis requires `override {key}` in {owner_label}"
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
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined analysis entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined analysis entry in {parent_label}: {key}"
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
                )
            )

        missing_keys = [
            parent_item.key for parent_item in parent_analysis.items if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited analysis entry in {owner_label}: {missing}"
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
        seen_keys: set[str] = set()
        for item in items:
            if isinstance(item, model.AnalysisSection):
                if item.key in seen_keys:
                    raise CompileError(f"Duplicate analysis section key in {owner_label}: {item.key}")
                seen_keys.add(item.key)
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
                    )
                )
                continue
            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited analysis declaration in {owner_label}: {item.key}"
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
                    raise CompileError(f"Analysis basis may not be empty in {owner_label}")
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
            raise CompileError(
                f"Unsupported analysis item in {owner_label}: {type(item).__name__}"
            )
        return tuple(resolved)
