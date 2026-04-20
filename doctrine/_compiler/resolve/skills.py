from __future__ import annotations

from doctrine import model

from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import (
    ActiveSkillBindAgentContext,
    AddressableNode,
    AddressableRootDecl,
    CompiledSkillPackageContract,
    IndexedUnit,
    ResolvedSkillBindTarget,
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

    def _compiled_skill_package_contract(
        self,
        *,
        package_unit: IndexedUnit,
        package_decl: model.SkillPackageDecl,
    ) -> CompiledSkillPackageContract:
        package_key = (package_unit.module_parts, package_decl.name)
        cached = self._compiled_skill_package_cache.get(package_key)
        if cached is None:
            cached = self._compile_skill_package_decl(package_decl, unit=package_unit)
            self._compiled_skill_package_cache[package_key] = cached
        return cached.contract

    def _resolve_skill_entry_bind_target(
        self,
        target: model.NameRef | model.AddressableRef,
        *,
        bind_key: str,
        unit: IndexedUnit,
        agent_context: ActiveSkillBindAgentContext,
    ) -> ResolvedSkillBindTarget:
        owner_label = f"skill bind `{bind_key}`"
        if isinstance(target, model.AddressableRef):
            root = target.root
            if not target.self_rooted and root is not None and not root.module_parts:
                if root.declaration_name == "inputs":
                    if not target.path:
                        raise self._skills_compile_error(
                            detail=f"`inputs:` bind target in {owner_label} must name an input key.",
                            unit=unit,
                            source_span=target.source_span,
                        )
                    binding = agent_context.agent_contract.input_bindings_by_path.get(
                        (target.path[0],)
                    )
                    if binding is None:
                        raise self._skills_compile_error(
                            detail=(
                                f"Unknown input bind target in {owner_label}: "
                                f"inputs:{'.'.join(target.path)}"
                            ),
                            unit=unit,
                            source_span=target.source_span,
                        )
                    return ResolvedSkillBindTarget(
                        family="input",
                        unit=binding.artifact.unit,
                        root_decl=binding.artifact.decl,
                        path=target.path[1:],
                    )
                if root.declaration_name == "outputs":
                    if not target.path:
                        raise self._skills_compile_error(
                            detail=f"`outputs:` bind target in {owner_label} must name an output key.",
                            unit=unit,
                            source_span=target.source_span,
                        )
                    binding = agent_context.agent_contract.output_bindings_by_path.get(
                        (target.path[0],)
                    )
                    if binding is None:
                        raise self._skills_compile_error(
                            detail=(
                                f"Unknown output bind target in {owner_label}: "
                                f"outputs:{'.'.join(target.path)}"
                            ),
                            unit=unit,
                            source_span=target.source_span,
                        )
                    return ResolvedSkillBindTarget(
                        family="output",
                        unit=binding.artifact.unit,
                        root_decl=binding.artifact.decl,
                        path=target.path[1:],
                    )
                if root.declaration_name == "analysis":
                    analysis_field = agent_context.analysis_field
                    if analysis_field is None:
                        raise self._skills_compile_error(
                            detail=(
                                f"Bind target in {owner_label} uses `analysis:`, but agent "
                                f"`{agent_context.agent.name}` has no `analysis:` field."
                            ),
                            unit=unit,
                            source_span=target.source_span,
                        )
                    analysis_unit, analysis_decl = self._resolve_analysis_ref(
                        analysis_field.value,
                        unit=agent_context.unit,
                    )
                    return ResolvedSkillBindTarget(
                        family="analysis",
                        unit=analysis_unit,
                        root_decl=analysis_decl,
                        path=target.path,
                    )
                if root.declaration_name == "final_output":
                    final_output_field = agent_context.final_output_field
                    if final_output_field is None:
                        raise self._skills_compile_error(
                            detail=(
                                f"Bind target in {owner_label} uses `final_output:`, but agent "
                                f"`{agent_context.agent.name}` has no `final_output:` field."
                            ),
                            unit=unit,
                            source_span=target.source_span,
                        )
                    output_unit, output_decl = self._resolve_final_output_decl(
                        final_output_field.value,
                        unit=agent_context.unit,
                        owner_label=f"agent {agent_context.agent.name} final_output",
                        source_span=final_output_field.source_span,
                    )
                    return ResolvedSkillBindTarget(
                        family="final_output",
                        unit=output_unit,
                        root_decl=output_decl,
                        path=target.path,
                    )

            target_unit, root_decl = self._resolve_addressable_root_decl(
                target.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="skill bind target",
                missing_local_label="skill bind target",
            )
            return ResolvedSkillBindTarget(
                family=self._skill_bind_family_for_root(root_decl),
                unit=target_unit,
                root_decl=root_decl,
                path=target.path,
            )

        if not target.module_parts:
            if target.declaration_name == "analysis":
                analysis_field = agent_context.analysis_field
                if analysis_field is None:
                    raise self._skills_compile_error(
                        detail=(
                            f"Bind target in {owner_label} uses `analysis`, but agent "
                            f"`{agent_context.agent.name}` has no `analysis:` field."
                        ),
                        unit=unit,
                        source_span=target.source_span,
                    )
                analysis_unit, analysis_decl = self._resolve_analysis_ref(
                    analysis_field.value,
                    unit=agent_context.unit,
                )
                return ResolvedSkillBindTarget(
                    family="analysis",
                    unit=analysis_unit,
                    root_decl=analysis_decl,
                )
            if target.declaration_name == "final_output":
                final_output_field = agent_context.final_output_field
                if final_output_field is None:
                    raise self._skills_compile_error(
                        detail=(
                            f"Bind target in {owner_label} uses `final_output`, but agent "
                            f"`{agent_context.agent.name}` has no `final_output:` field."
                        ),
                        unit=unit,
                        source_span=target.source_span,
                    )
                output_unit, output_decl = self._resolve_final_output_decl(
                    final_output_field.value,
                    unit=agent_context.unit,
                    owner_label=f"agent {agent_context.agent.name} final_output",
                    source_span=final_output_field.source_span,
                )
                return ResolvedSkillBindTarget(
                    family="final_output",
                    unit=output_unit,
                    root_decl=output_decl,
                )

        target_unit, root_decl = self._resolve_addressable_root_decl(
            target,
            unit=unit,
            owner_label=owner_label,
            ambiguous_label="skill bind target",
            missing_local_label="skill bind target",
        )
        return ResolvedSkillBindTarget(
            family=self._skill_bind_family_for_root(root_decl),
            unit=target_unit,
            root_decl=root_decl,
        )

    def _skill_bind_family_for_root(
        self,
        root_decl: AddressableRootDecl,
    ) -> str:
        if isinstance(root_decl, model.InputDecl):
            return "input"
        if isinstance(root_decl, model.OutputDecl):
            return "output"
        if isinstance(root_decl, model.DocumentDecl):
            return "document"
        if isinstance(root_decl, model.AnalysisDecl):
            return "analysis"
        if isinstance(root_decl, model.SchemaDecl):
            return "schema"
        if isinstance(root_decl, model.TableDecl):
            return "table"
        raise ValueError(f"Unsupported skill bind root: {type(root_decl).__name__}")

    def _validate_skill_entry_package_binds(
        self,
        entry: model.SkillEntry | model.OverrideSkillEntry,
        *,
        skill_decl: model.SkillDecl,
        metadata_unit: IndexedUnit,
        package_contract: CompiledSkillPackageContract,
        agent_context: ActiveSkillBindAgentContext,
    ) -> None:
        slot_map = {
            slot.key: slot
            for slot in package_contract.host_contract
            if not isinstance(slot, model.ReceiptHostSlot)
        }
        bind_map = {bind.key: bind for bind in entry.binds}

        if not slot_map:
            if entry.binds:
                raise self._skills_compile_error(
                    detail=(
                        f"Skill entry `{entry.key}` binds package-backed skill "
                        f"`{skill_decl.name}`, but package `{package_contract.package_name}` "
                        "declares no host slots."
                    ),
                    unit=metadata_unit,
                    source_span=entry.binds[0].source_span,
                )
            return

        missing_keys = sorted(set(slot_map) - set(bind_map))
        if missing_keys:
            raise self._skills_compile_error(
                detail=(
                    f"Skill entry `{entry.key}` is missing required binds for package "
                    f"`{package_contract.package_name}`: {', '.join(missing_keys)}"
                ),
                unit=metadata_unit,
                source_span=entry.source_span,
            )

        extra_keys = sorted(set(bind_map) - set(slot_map))
        if extra_keys:
            first_extra = bind_map[extra_keys[0]]
            raise self._skills_compile_error(
                detail=(
                    f"Skill entry `{entry.key}` binds unknown package host slots for "
                    f"`{package_contract.package_name}`: {', '.join(extra_keys)}"
                ),
                unit=metadata_unit,
                source_span=first_extra.source_span,
            )

        resolved_binds = {
            bind.key: self._resolve_skill_entry_bind_target(
                bind.target,
                bind_key=bind.key,
                unit=metadata_unit,
                agent_context=agent_context,
            )
            for bind in entry.binds
        }
        for key, slot in slot_map.items():
            resolved_bind = resolved_binds[key]
            if resolved_bind.family != slot.family:
                bind = bind_map[key]
                raise self._skills_compile_error(
                    detail=(
                        f"Skill entry `{entry.key}` binds slot `{key}` as "
                        f"`{resolved_bind.family}`, but package "
                        f"`{package_contract.package_name}` requires `{slot.family}`."
                    ),
                    unit=metadata_unit,
                    source_span=bind.source_span,
                )

        for artifact in package_contract.artifacts:
            for host_path in artifact.referenced_host_paths:
                slot_key, *tail = host_path.split(".")
                bound_target = resolved_binds[slot_key]
                if not tail:
                    continue
                self._resolve_addressable_path_node(
                    AddressableNode(
                        unit=bound_target.unit,
                        root_decl=bound_target.root_decl,
                        target=bound_target.root_decl,
                    ),
                    (*bound_target.path, *tail),
                    owner_label=(
                        f"skill entry `{entry.key}` host bind for "
                        f"{package_contract.package_name}"
                    ),
                    surface_label="skill bind validation",
                    ref_label=f"{slot_key}:{'.'.join(tail)}",
                    source_span=bind_map[slot_key].source_span,
                )

    def _resolve_skill_entry(
        self,
        entry: model.SkillEntry | model.OverrideSkillEntry,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillEntry:
        target_unit, skill_decl = self._resolve_skill_decl(entry.target, unit=unit)
        package_unit: IndexedUnit | None = None
        package_decl: model.SkillPackageDecl | None = None
        package_contract: CompiledSkillPackageContract | None = None
        if entry.binds and skill_decl.package_link is None:
            raise self._skills_compile_error(
                detail=(
                    f"Skill entry `{entry.key}` uses `bind:`, but skill `{skill_decl.name}` "
                    "does not declare `package:`."
                ),
                unit=unit,
                source_span=entry.binds[0].source_span,
            )
        if skill_decl.package_link is not None:
            package_unit, package_decl = self._resolve_skill_package_id(
                skill_decl.package_link.package_id,
                unit=target_unit,
                owner_label=f"skill `{skill_decl.name}` package link",
                source_span=skill_decl.package_link.source_span,
            )
            package_contract = self._compiled_skill_package_contract(
                package_unit=package_unit,
                package_decl=package_decl,
            )
            active_agent_context = self._active_skill_bind_agent_context
            if active_agent_context is None and (
                entry.binds or package_contract.host_contract
            ):
                raise self._skills_compile_error(
                    detail=(
                        f"Package-backed skill `{skill_decl.name}` needs a concrete agent "
                        "context before Doctrine can validate host binds."
                    ),
                    unit=unit,
                    source_span=entry.source_span,
                )
            if active_agent_context is not None:
                self._validate_skill_entry_package_binds(
                    entry,
                    skill_decl=skill_decl,
                    metadata_unit=unit,
                    package_contract=package_contract,
                    agent_context=active_agent_context,
                )
        return ResolvedSkillEntry(
            key=entry.key,
            metadata_unit=unit,
            target_unit=target_unit,
            skill_decl=skill_decl,
            items=entry.items,
            binds=entry.binds,
            package_unit=package_unit,
            package_decl=package_decl,
            package_contract=package_contract,
            source_span=entry.source_span,
        )
