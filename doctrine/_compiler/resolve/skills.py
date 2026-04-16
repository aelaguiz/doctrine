from __future__ import annotations

from doctrine import model

from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import (
    IndexedUnit,
    ResolvedSkillEntry,
    ResolvedSkillsBody,
    ResolvedSkillsItem,
    ResolvedSkillsSection,
    ResolvedSkillsSectionBodyItem,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveSkillsMixin:
    """Skills-body and skills-decl resolution helpers for ResolveMixin."""

    def _skills_compile_error(
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

    def _skills_related_site(
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

    def _missing_skills_related_sites(
        self,
        *,
        parent_unit: IndexedUnit | None,
        parent_skills: ResolvedSkillsBody | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None or parent_skills is None:
            return ()
        related = []
        for key in missing_keys:
            parent_item = next((item for item in parent_skills.items if item.key == key), None)
            if parent_item is None:
                continue
            related.append(
                self._skills_related_site(
                    label=f"inherited `{key}` entry",
                    unit=parent_unit,
                    source_span=parent_item.source_span,
                )
            )
        return tuple(related)

    def _resolve_skills_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._resolved_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._skills_resolution_stack, skills_key]
            )
            raise self._skills_compile_error(
                code="E250",
                summary="Cyclic skills inheritance",
                detail=f"Cyclic skills inheritance: {cycle}",
                unit=unit,
                source_span=skills_decl.source_span,
            )

        self._skills_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_unit: IndexedUnit | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            with self._with_addressable_self_root(
                self._local_addressable_self_root_ref(skills_decl.name)
            ):
                resolved = self._resolve_skills_body(
                    skills_decl.body,
                    unit=unit,
                    owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                    owner_source_span=skills_decl.source_span,
                    parent_skills=parent_skills,
                    parent_unit=parent_unit,
                    parent_label=parent_label,
                )
            self._resolved_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_resolution_stack.pop()

    def _resolve_skills_for_addressable_paths(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        if (
            skills_key in self._skills_resolution_stack
            or skills_key in self._skills_addressable_resolution_stack
        ):
            return self._resolve_skills_addressable_decl(skills_decl, unit=unit)
        return self._resolve_skills_decl(skills_decl, unit=unit)

    def _resolve_skills_value(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_decl(skills_decl, unit=target_unit)
        return self._resolve_skills_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_skills_value_for_addressable_paths(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_for_addressable_paths(skills_decl, unit=target_unit)
        return self._resolve_skills_addressable_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_skills_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        owner_source_span: model.SourceSpan | None = None,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_unit: IndexedUnit | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="skills prose",
                ambiguous_label="skills prose interpolation ref",
            )
            for line in skills_body.preamble
        )
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: dict[str, model.SkillsItem] = {}
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise self._skills_compile_error(
                    detail=f"Duplicate skills item key in {owner_label}: {key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        self._skills_related_site(
                            label=f"first `{key}` skills entry",
                            unit=unit,
                            source_span=emitted_keys[key].source_span,
                        ),
                    ),
                )
            emitted_keys[key] = item

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                        source_span=item.source_span,
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(
                    self._resolve_skill_entry(
                        item,
                        unit=unit,
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise self._skills_compile_error(
                        detail=f"Cannot inherit undefined skills entry in {parent_label}: {key}",
                        unit=unit,
                        source_span=item.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise self._skills_compile_error(
                    code="E001",
                    summary="Cannot override undefined inherited entry",
                    detail=f"Cannot override undefined skills entry in {parent_label}: {key}",
                    unit=unit,
                    source_span=item.source_span,
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise self._skills_compile_error(
                        detail=f"Override kind mismatch for skills entry in {owner_label}: {key}",
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            self._skills_related_site(
                                label=f"inherited `{key}` entry",
                                unit=parent_unit or unit,
                                source_span=parent_item.source_span,
                            ),
                        ),
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                        source_span=item.source_span,
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise self._skills_compile_error(
                    detail=f"Override kind mismatch for skills entry in {owner_label}: {key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        self._skills_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit or unit,
                            source_span=parent_item.source_span,
                        ),
                    ),
                )
            resolved_items.append(
                self._resolve_skill_entry(
                    item,
                    unit=unit,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise self._skills_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=f"Missing inherited skills entry in {owner_label}: {missing}",
                unit=unit,
                source_span=owner_source_span,
                related=self._missing_skills_related_sites(
                    parent_unit=parent_unit,
                    parent_skills=parent_skills,
                    missing_keys=tuple(missing_keys),
                ),
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_non_inherited_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: dict[str, model.SkillsItem] = {}

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise self._skills_compile_error(
                    detail=f"Duplicate skills item key in {owner_label}: {key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        self._skills_related_site(
                            label=f"first `{key}` skills entry",
                            unit=unit,
                            source_span=seen_keys[key].source_span,
                        ),
                    ),
                )
            seen_keys[key] = item

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                        source_span=item.source_span,
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise self._skills_compile_error(
                detail=f"{item_label} requires an inherited skills block in {owner_label}: {key}",
                unit=unit,
                source_span=item.source_span,
            )

        return tuple(resolved_items)

    def _resolve_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="skills prose",
                        ambiguous_label="skills prose interpolation ref",
                    )
                )
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_skill_entry(
        self,
        entry: model.SkillEntry | model.OverrideSkillEntry,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillEntry:
        target_unit, skill_decl = self._resolve_skill_decl(entry.target, unit=unit)
        return ResolvedSkillEntry(
            key=entry.key,
            metadata_unit=unit,
            target_unit=target_unit,
            skill_decl=skill_decl,
            items=entry.items,
            source_span=entry.source_span,
        )
