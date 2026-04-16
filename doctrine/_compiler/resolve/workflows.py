from __future__ import annotations

from doctrine import model
from doctrine._compiler.workflow_diagnostics import (
    workflow_compile_error,
    workflow_related_site,
)
from doctrine._compiler.resolved_types import (
    CompileError,
    IndexedUnit,
    ResolvedSectionItem,
    ResolvedSkillsBody,
    ResolvedUseItem,
    ResolvedWorkflowBody,
    ResolvedWorkflowItem,
    ResolvedWorkflowSkillsItem,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveWorkflowsMixin:
    """Workflow and law resolution helpers for ResolveMixin."""

    def _workflow_item_by_key(
        self,
        items: tuple[model.WorkflowItem, ...],
        key: str,
    ) -> model.WorkflowItem | None:
        return next((item for item in items if item.key == key), None)

    def _law_item_by_key(
        self,
        items: tuple[model.LawTopLevelItem, ...],
        key: str,
    ) -> model.LawSection | model.LawInherit | model.LawOverrideSection | None:
        return next(
            (
                item
                for item in items
                if isinstance(item, (model.LawSection, model.LawInherit, model.LawOverrideSection))
                and item.key == key
            ),
            None,
        )

    def _first_non_named_law_item(
        self,
        items: tuple[model.LawTopLevelItem, ...],
    ) -> model.LawTopLevelItem | None:
        return next(
            (
                item
                for item in items
                if not isinstance(item, (model.LawSection, model.LawInherit, model.LawOverrideSection))
            ),
            None,
        )

    def _workflow_missing_related_sites(
        self,
        *,
        parent_unit: IndexedUnit | None,
        parent_body: model.WorkflowBody | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None or parent_body is None:
            return ()
        related = []
        for key in missing_keys:
            parent_item = self._workflow_item_by_key(parent_body.items, key)
            if parent_item is None:
                continue
            related.append(
                workflow_related_site(
                    label=f"inherited `{key}` entry",
                    unit=parent_unit,
                    source_span=parent_item.source_span,
                )
            )
        return tuple(related)

    def _resolve_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._resolved_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_resolution_stack, workflow_key]
            )
            raise workflow_compile_error(
                code="E240",
                summary="Cyclic workflow inheritance",
                detail=f"Workflow inheritance cycle: {cycle}.",
                unit=unit,
                source_span=workflow_decl.source_span,
            )

        self._workflow_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_decl(parent_decl, unit=parent_unit)
                parent_label = f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_workflow_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                owner_source_span=workflow_decl.source_span,
                parent_workflow=parent_workflow,
                parent_body=parent_decl.body if workflow_decl.parent_ref is not None else None,
                parent_unit=parent_unit if workflow_decl.parent_ref is not None else None,
                parent_label=parent_label,
            )
            self._resolved_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_resolution_stack.pop()

    def _resolve_workflow_for_addressable_paths(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if (
            workflow_key in self._workflow_resolution_stack
            or workflow_key in self._workflow_addressable_resolution_stack
        ):
            return self._resolve_workflow_addressable_decl(workflow_decl, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=unit)

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

    def _resolve_workflow_addressable_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._addressable_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._workflow_addressable_resolution_stack,
                    workflow_key,
                ]
            )
            raise workflow_compile_error(
                code="E240",
                summary="Cyclic workflow inheritance",
                detail=f"Workflow inheritance cycle: {cycle}.",
                unit=unit,
                source_span=workflow_decl.source_span,
            )

        self._workflow_addressable_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_workflow_addressable_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                owner_source_span=workflow_decl.source_span,
                parent_workflow=parent_workflow,
                parent_body=parent_decl.body if workflow_decl.parent_ref is not None else None,
                parent_unit=parent_unit if workflow_decl.parent_ref is not None else None,
                parent_label=parent_label,
            )
            self._addressable_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_addressable_resolution_stack.pop()

    def _resolve_workflow_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        owner_source_span: model.SourceSpan | None,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_body: model.WorkflowBody | None = None,
        parent_unit: IndexedUnit | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="workflow strings",
                ambiguous_label="workflow string interpolation ref",
            )
            for line in workflow_body.preamble
        )
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                    owner_source_span=owner_source_span,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_items: dict[str, model.WorkflowItem] = {}
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_items:
                raise workflow_compile_error(
                    code="E261",
                    summary="Duplicate workflow item key",
                    detail=f"Workflow owner `{owner_label}` repeats key `{key}`.",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        workflow_related_site(
                            label=f"first `{key}` entry",
                            unit=unit,
                            source_span=emitted_items[key].source_span,
                        ),
                    ),
                )
            emitted_items[key] = item

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReadableBlock):
                if key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited workflow requires `override {key}` in {owner_label}"
                    )
                resolved_items.append(item)
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise workflow_compile_error(
                        code="E241",
                        summary="Cannot inherit undefined workflow entry",
                        detail=(
                            f"Workflow owner `{owner_label}` cannot inherit undefined key `{key}`."
                        ),
                        unit=unit,
                        source_span=item.source_span or owner_source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise workflow_compile_error(
                    code="E001",
                    summary="Cannot override undefined inherited entry",
                    detail=f"Cannot override undefined workflow entry in {parent_label}: {key}",
                    unit=unit,
                    source_span=item.source_span or owner_source_span,
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise workflow_compile_error(
                        code="E242",
                        summary="Override kind mismatch",
                        detail=(
                            f"Workflow owner `{owner_label}` overrides `{key}` with the wrong kind."
                        ),
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            workflow_related_site(
                                label=f"inherited `{key}` entry",
                                unit=parent_unit or unit,
                                source_span=(
                                    None
                                    if parent_body is None
                                    else getattr(
                                        self._workflow_item_by_key(parent_body.items, key),
                                        "source_span",
                                        None,
                                    )
                                ),
                            ),
                        ),
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReadableOverrideBlock):
                resolved_items.append(
                    self._merge_workflow_root_readable_override(
                        item,
                        unit=unit,
                        parent_item=parent_item,
                        parent_body=parent_body,
                        parent_unit=parent_unit or unit,
                        owner_label=owner_label,
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise workflow_compile_error(
                        code="E242",
                        summary="Override kind mismatch",
                        detail=(
                            f"Workflow owner `{owner_label}` overrides `{key}` with the wrong kind."
                        ),
                        unit=unit,
                        source_span=item.source_span,
                        related=(
                            workflow_related_site(
                                label=f"inherited `{key}` entry",
                                unit=parent_unit or unit,
                                source_span=(
                                    None
                                    if parent_body is None
                                    else getattr(
                                        self._workflow_item_by_key(parent_body.items, key),
                                        "source_span",
                                        None,
                                    )
                                ),
                            ),
                        ),
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise workflow_compile_error(
                    code="E242",
                    summary="Override kind mismatch",
                    detail=(
                        f"Workflow owner `{owner_label}` overrides `{key}` with the wrong kind."
                    ),
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        workflow_related_site(
                            label=f"inherited `{key}` entry",
                            unit=parent_unit or unit,
                            source_span=(
                                None
                                if parent_body is None
                                else getattr(
                                    self._workflow_item_by_key(parent_body.items, key),
                                    "source_span",
                                    None,
                                )
                            ),
                        ),
                    ),
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = tuple(
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        )
        if missing_keys:
            raise workflow_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=(
                    f"Missing inherited workflow entry in {owner_label}: "
                    f"{', '.join(missing_keys)}"
                ),
                unit=unit,
                source_span=owner_source_span,
                related=self._workflow_missing_related_sites(
                    parent_unit=parent_unit,
                    parent_body=parent_body,
                    missing_keys=missing_keys,
                ),
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                unit=unit,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_unit=parent_unit,
                parent_label=parent_label,
            ),
        )

    def _resolve_law_body(
        self,
        law_body: model.LawBody | None,
        *,
        owner_label: str,
        parent_law: model.LawBody | None = None,
        parent_label: str | None = None,
    ) -> model.LawBody | None:
        if law_body is None:
            return parent_law
        if parent_law is None:
            return law_body

        parent_items = parent_law.items
        parent_has_sections = all(
            isinstance(item, model.LawSection) for item in parent_items
        )
        child_has_named_items = all(
            isinstance(
                item,
                (model.LawSection, model.LawInherit, model.LawOverrideSection),
            )
            for item in law_body.items
        )

        if not parent_has_sections or not child_has_named_items:
            raise CompileError(
                f"Inherited law blocks must use named sections only in {owner_label}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_items if isinstance(item, model.LawSection)
        }
        resolved_items: list[model.LawTopLevelItem] = []
        accounted_keys: set[str] = set()

        for item in law_body.items:
            if isinstance(item, model.LawSection):
                if item.key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                    )
                resolved_items.append(item)
                continue

            parent_item = parent_items_by_key.get(item.key)
            if parent_item is None:
                raise CompileError(
                    f"Cannot override undefined law section in {parent_label}: {item.key}"
                )
            if item.key in accounted_keys:
                raise CompileError(
                    f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                )
            accounted_keys.add(item.key)

            if isinstance(item, model.LawInherit):
                resolved_items.append(parent_item)
            else:
                resolved_items.append(model.LawSection(key=item.key, items=item.items))

        missing_keys = sorted(set(parent_items_by_key) - accounted_keys)
        if missing_keys:
            raise CompileError(
                f"Inherited law block omits parent subsection(s) in {owner_label}: {', '.join(missing_keys)}"
            )

        return model.LawBody(items=tuple(resolved_items))

    def _resolve_workflow_addressable_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_workflow_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReadableBlock):
                if key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited workflow requires `override {key}` in {owner_label}"
                    )
                resolved_items.append(item)
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReadableOverrideBlock):
                resolved_items.append(
                    self._merge_workflow_root_readable_override(
                        item,
                        parent_item=parent_item,
                        owner_label=owner_label,
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=(),
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_non_inherited_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReadableBlock):
                resolved_items.append(item)
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_addressable_workflow_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReadableBlock):
                resolved_items.append(item)
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _merge_workflow_root_readable_override(
        self,
        item: model.ReadableOverrideBlock,
        *,
        parent_item: ResolvedWorkflowItem | None,
        owner_label: str,
    ) -> model.ReadableBlock:
        key = item.key
        if not isinstance(parent_item, model.ReadableBlock):
            raise CompileError(
                f"Override kind mismatch for workflow entry in {owner_label}: {key}"
            )
        if item.kind != parent_item.kind:
            raise CompileError(
                f"Override kind mismatch for workflow entry in {owner_label}: {key}"
            )
        return model.ReadableBlock(
            kind=item.kind,
            key=item.key,
            title=self._workflow_root_readable_override_title(item, parent_item=parent_item),
            payload=item.payload,
            requirement=(
                item.requirement
                if item.requirement is not None
                else parent_item.requirement
            ),
            when_expr=item.when_expr if item.when_expr is not None else parent_item.when_expr,
            item_schema=item.item_schema if item.item_schema is not None else parent_item.item_schema,
            row_schema=item.row_schema if item.row_schema is not None else parent_item.row_schema,
            anonymous=parent_item.anonymous,
            legacy_section=parent_item.legacy_section,
        )

    def _workflow_root_readable_override_title(
        self,
        item: model.ReadableOverrideBlock,
        *,
        parent_item: model.ReadableBlock,
    ) -> str | None:
        if item.title is not None:
            return item.title
        if item.kind in {"sequence", "bullets", "checklist"}:
            return None
        return parent_item.title
