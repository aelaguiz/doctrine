from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from doctrine import model
from doctrine._compiler.constants import (
    _ADDRESSABLE_ROOT_REGISTRIES,
    _BUILTIN_RENDER_PROFILE_NAMES,
    _READABLE_DECL_REGISTRIES,
    _REVIEW_VERDICT_TEXT,
)
from doctrine._compiler.indexing import ImportedSymbolBinding, index_unit, skill_package_id
from doctrine._compiler.naming import _dotted_ref_name, _humanize_key
from doctrine._compiler.reference_diagnostics import reference_compile_error, reference_related_site
from doctrine._compiler.resolved_types import (
    AddressableRootDecl,
    CompileError,
    IndexedUnit,
    ReadableDecl,
    ResolvedRenderProfile,
)
from doctrine.parser import parse_file


@dataclass(slots=True, frozen=True)
class _RefLookupTarget:
    unit: IndexedUnit
    declaration_name: str
    imported_symbol: ImportedSymbolBinding | None = None


class ResolveRefsMixin:
    """Ref lookup helpers for ResolveMixin."""

    def _visible_skill_package_lookup_units(self, *, unit: IndexedUnit) -> tuple[IndexedUnit, ...]:
        units: list[IndexedUnit] = []
        seen: set[tuple[Path | None, tuple[str, ...]]] = set()

        def _add(target_unit: IndexedUnit) -> None:
            key = (target_unit.prompt_root, target_unit.module_parts)
            if key in seen:
                return
            seen.add(key)
            units.append(target_unit)

        _add(unit)
        for imported_unit in unit.visible_imported_units.values():
            _add(imported_unit)
        for binding in unit.imported_symbols_by_name.values():
            _add(binding.target_unit)
        return tuple(units)

    def _scanned_skill_package_matches(
        self,
        package_id: str,
    ) -> tuple[tuple[IndexedUnit, model.SkillPackageDecl], ...]:
        cache = self.session.skill_package_scan_cache
        if cache is None:
            matches_by_id: dict[str, list[tuple[IndexedUnit, model.SkillPackageDecl]]] = {}
            seen_paths: set[Path] = set()
            for prompt_root in self.session.import_roots:
                for prompt_path in prompt_root.rglob("SKILL.prompt"):
                    resolved_prompt_path = prompt_path.resolve()
                    if resolved_prompt_path in seen_paths:
                        continue
                    seen_paths.add(resolved_prompt_path)
                    prompt_file = parse_file(prompt_path)
                    package_unit = index_unit(
                        self.session,
                        prompt_file,
                        prompt_root=prompt_root,
                        module_parts=prompt_path.relative_to(prompt_root).parts[:-1],
                        module_source_kind="runtime_package",
                        package_root=prompt_path.parent,
                        ancestry=(),
                        allow_parallel_imports=True,
                    )
                    for declaration in package_unit.skill_packages_by_name.values():
                        matches_by_id.setdefault(skill_package_id(declaration), []).append(
                            (package_unit, declaration)
                        )
            self.session.skill_package_scan_cache = {
                key: tuple(value) for key, value in matches_by_id.items()
            }
            cache = self.session.skill_package_scan_cache
        return () if cache is None else cache.get(package_id, ())

    def _resolve_skill_package_id(
        self,
        package_id: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span: model.SourceSpan | None,
    ) -> tuple[IndexedUnit, model.SkillPackageDecl]:
        matches: list[tuple[IndexedUnit, model.SkillPackageDecl]] = []
        for lookup_unit in self._visible_skill_package_lookup_units(unit=unit):
            decl = lookup_unit.skill_packages_by_id.get(package_id)
            if decl is not None:
                matches.append((lookup_unit, decl))

        if not matches:
            matches.extend(self._scanned_skill_package_matches(package_id))

        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:
            labels = ", ".join(
                skill_package_id(decl)
                if lookup_unit.module_parts == ()
                else f"{'.'.join(lookup_unit.module_parts)} ({skill_package_id(decl)})"
                for lookup_unit, decl in matches
            )
            raise reference_compile_error(
                code="E270",
                summary="Ambiguous skill package id",
                detail=(
                    f"Skill package id `{package_id}` in {owner_label} is visible from more than "
                    f"one package: {labels}"
                ),
                unit=unit,
                source_span=source_span,
                hints=("Keep visible skill package ids unique, or change the package id.",),
            )

        raise reference_compile_error(
            code="E299",
            summary="Compile failure",
            detail=f"Missing skill package id in {owner_label}: {package_id}",
            unit=unit,
            source_span=source_span,
            hints=("Add the missing `skill package`, or fix the `package:` id.",),
        )

    def _resolve_visible_imported_unit(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> IndexedUnit:
        target_unit = unit.visible_imported_units.get(ref.module_parts)
        if target_unit is None:
            raise reference_compile_error(
                code="E280",
                summary="Missing import module",
                detail=f"Missing import module: {'.'.join(ref.module_parts)}",
                unit=unit,
                source_span=ref.source_span,
            )
        return target_unit

    def _decl_lookup_targets(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> tuple[_RefLookupTarget, ...]:
        if ref.module_parts:
            if ref.module_parts == unit.module_parts:
                return (_RefLookupTarget(unit=unit, declaration_name=ref.declaration_name),)
            return (
                _RefLookupTarget(
                    unit=self._resolve_visible_imported_unit(ref, unit=unit),
                    declaration_name=ref.declaration_name,
                ),
            )

        targets = [_RefLookupTarget(unit=unit, declaration_name=ref.declaration_name)]
        imported_symbol = unit.imported_symbols_by_name.get(ref.declaration_name)
        if imported_symbol is None:
            return tuple(targets)

        imported_target = _RefLookupTarget(
            unit=imported_symbol.target_unit,
            declaration_name=imported_symbol.target_name,
            imported_symbol=imported_symbol,
        )
        local_target = targets[0]
        if (
            imported_target.unit.prompt_root != local_target.unit.prompt_root
            or imported_target.unit.module_parts != local_target.unit.module_parts
            or imported_target.declaration_name != local_target.declaration_name
        ):
            targets.append(imported_target)
        return tuple(targets)

    def _raise_imported_symbol_ambiguity(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        binding: ImportedSymbolBinding,
        detail: str,
        local_decl: object | None = None,
        local_label: str = "local declaration",
    ) -> None:
        related = [reference_related_site(label="import line", unit=unit, source_span=binding.import_decl.source_span)]
        if local_decl is not None:
            related.insert(
                0,
                reference_related_site(
                    label=local_label,
                    unit=unit,
                    source_span=getattr(local_decl, "source_span", None),
                ),
            )
        raise reference_compile_error(
            code="E308",
            summary="Ambiguous imported symbol ownership",
            detail=detail,
            unit=unit,
            source_span=ref.source_span,
            related=tuple(related),
            hints=(
                "Rename the imported symbol with `as`, or rename the local declaration.",
                "Use a module alias when you want the imported owner to stay explicit.",
            ),
        )

    def _resolve_workflow_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="workflows_by_name",
            missing_label="workflow declaration",
        )

    def _resolve_review_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.ReviewDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="reviews_by_name",
            missing_label="review declaration",
        )

    def _resolve_skills_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_blocks_by_name",
            missing_label="skills declaration",
        )

    def _resolve_render_profile_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ResolvedRenderProfile:
        if not ref.module_parts:
            local_profile = unit.render_profiles_by_name.get(ref.declaration_name)
            if local_profile is not None:
                return ResolvedRenderProfile(name=local_profile.name, rules=local_profile.rules)
            if ref.declaration_name in _BUILTIN_RENDER_PROFILE_NAMES:
                return ResolvedRenderProfile(name=ref.declaration_name)
        profile_unit, profile_decl = self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="render_profiles_by_name",
            missing_label="render_profile declaration",
        )
        return ResolvedRenderProfile(name=profile_decl.name, rules=profile_decl.rules)

    def _resolve_analysis_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.AnalysisDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="analyses_by_name",
            missing_label="analysis declaration",
        )

    def _resolve_decision_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.DecisionDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="decisions_by_name",
            missing_label="decision declaration",
        )

    def _resolve_schema_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SchemaDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="schemas_by_name",
            missing_label="schema declaration",
        )

    def _resolve_document_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.DocumentDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="documents_by_name",
            missing_label="document declaration",
        )

    def _resolve_table_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.TableDecl]:
        lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        matching_targets: list[tuple[_RefLookupTarget, model.TableDecl]] = []
        for lookup_target in lookup_targets:
            decl = lookup_target.unit.tables_by_name.get(lookup_target.declaration_name)
            if decl is not None:
                matching_targets.append((lookup_target, decl))
        if len(matching_targets) == 1:
            lookup_target, decl = matching_targets[0]
            return lookup_target.unit, decl
        if len(matching_targets) > 1:
            imported_target = next(
                (
                    lookup_target
                    for lookup_target, _decl in matching_targets
                    if lookup_target.imported_symbol is not None
                ),
                None,
            )
            if imported_target is not None:
                local_decl = next(
                    (
                        decl
                        for lookup_target, decl in matching_targets
                        if lookup_target.imported_symbol is None
                    ),
                    None,
                )
                self._raise_imported_symbol_ambiguity(
                    ref,
                    unit=unit,
                    binding=imported_target.imported_symbol,
                    detail=(
                        f"Named table ref `{ref.declaration_name}` matches both a local table "
                        "and an imported symbol."
                    ),
                    local_decl=local_decl,
                    local_label="local table",
                )

        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name
        for lookup_target in lookup_targets:
            actual_kind = self._named_non_output_decl_kind(
                lookup_target.declaration_name,
                unit=lookup_target.unit,
            )
            if actual_kind is not None:
                raise reference_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        "Named table use expects a table declaration, "
                        f"but `{dotted_name}` is a {actual_kind}."
                    ),
                    unit=unit,
                    source_span=ref.source_span,
                )
        if ref.module_parts:
            raise reference_compile_error(
                code="E281",
                summary="Missing imported declaration",
                detail=f"Missing imported table declaration: {dotted_name}",
                unit=unit,
                source_span=ref.source_span,
            )
        raise reference_compile_error(
            code="E276",
            summary="Missing local declaration reference",
            detail=f"Missing local table declaration: {ref.declaration_name}",
            unit=unit,
            source_span=ref.source_span,
        )

    def _resolve_enum_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.EnumDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )

    def _resolve_inputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
            missing_label="inputs block",
        )

    def _resolve_outputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_blocks_by_name",
            missing_label="outputs block",
        )

    def _resolve_parent_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=workflow_decl.name,
            child_label="workflow",
            parent_ref=workflow_decl.parent_ref,
            registry_name="workflows_by_name",
            resolve_parent_ref=self._resolve_workflow_ref,
        )

    def _resolve_parent_analysis_decl(
        self,
        analysis_decl: model.AnalysisDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.AnalysisDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=analysis_decl.name,
            child_label="analysis",
            parent_ref=analysis_decl.parent_ref,
            registry_name="analyses_by_name",
            resolve_parent_ref=self._resolve_analysis_ref,
        )

    def _resolve_parent_schema_decl(
        self,
        schema_decl: model.SchemaDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.SchemaDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=schema_decl.name,
            child_label="schema",
            parent_ref=schema_decl.parent_ref,
            registry_name="schemas_by_name",
            resolve_parent_ref=self._resolve_schema_ref,
        )

    def _resolve_parent_document_decl(
        self,
        document_decl: model.DocumentDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.DocumentDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=document_decl.name,
            child_label="document",
            parent_ref=document_decl.parent_ref,
            registry_name="documents_by_name",
            resolve_parent_ref=self._resolve_document_ref,
        )

    def _resolve_parent_skills_decl(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=skills_decl.name,
            child_label="skills",
            parent_ref=skills_decl.parent_ref,
            registry_name="skills_blocks_by_name",
            resolve_parent_ref=self._resolve_skills_ref,
        )

    def _resolve_parent_inputs_decl(
        self,
        inputs_decl: model.InputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=inputs_decl.name,
            child_label="inputs block",
            parent_ref=inputs_decl.parent_ref,
            registry_name="inputs_blocks_by_name",
            resolve_parent_ref=self._resolve_inputs_block_ref,
        )

    def _resolve_parent_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=outputs_decl.name,
            child_label="outputs block",
            parent_ref=outputs_decl.parent_ref,
            registry_name="outputs_blocks_by_name",
            resolve_parent_ref=self._resolve_outputs_block_ref,
        )

    def _resolve_parent_output_decl(
        self,
        output_decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=output_decl.name,
            child_label="output",
            parent_ref=output_decl.parent_ref,
            registry_name="outputs_by_name",
            resolve_parent_ref=self._resolve_output_decl,
        )

    def _resolve_parent_output_shape_decl(
        self,
        output_shape_decl: model.OutputShapeDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputShapeDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=output_shape_decl.name,
            child_label="output shape",
            parent_ref=output_shape_decl.parent_ref,
            registry_name="output_shapes_by_name",
            resolve_parent_ref=self._resolve_output_shape_decl,
        )

    def _resolve_parent_output_schema_decl(
        self,
        output_schema_decl: model.OutputSchemaDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputSchemaDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=output_schema_decl.name,
            child_label="output schema",
            parent_ref=output_schema_decl.parent_ref,
            registry_name="output_schemas_by_name",
            resolve_parent_ref=self._resolve_output_schema_decl,
        )

    def _resolve_input_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_by_name",
            missing_label="input declaration",
        )

    def _resolve_input_source_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputSourceDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="input_sources_by_name",
            missing_label="input source declaration",
        )

    def _resolve_output_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_by_name",
            missing_label="output declaration",
        )

    def _resolve_output_target_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputTargetDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_targets_by_name",
            missing_label="output target declaration",
        )

    def _resolve_output_shape_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputShapeDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_shapes_by_name",
            missing_label="output shape declaration",
        )

    def _resolve_output_schema_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputSchemaDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_schemas_by_name",
            missing_label="output schema declaration",
        )

    def _resolve_skill_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_by_name",
            missing_label="skill declaration",
        )

    def _resolve_agent_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.Agent]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="agents_by_name",
            missing_label="agent declaration",
        )

    def _resolve_parent_agent_decl(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.Agent]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=agent.name,
            child_label="agent",
            parent_ref=agent.parent_ref,
            registry_name="agents_by_name",
            resolve_parent_ref=self._resolve_agent_ref,
        )

    def _resolve_parent_decl(
        self,
        *,
        unit: IndexedUnit,
        child_name: str,
        child_label: str,
        parent_ref: model.NameRef | None,
        registry_name: str,
        resolve_parent_ref,
    ):
        if parent_ref is None:
            raise reference_compile_error(
                code="E901",
                summary="Internal compiler error",
                detail=f"Internal compiler error: {child_label} has no parent ref: {child_name}",
                unit=unit,
                source_span=None,
                hints=("This is a compiler bug, not a prompt authoring error.",),
            )
        try:
            return resolve_parent_ref(parent_ref, unit=unit)
        except CompileError as error:
            if parent_ref.module_parts or error.diagnostic.code not in {"E276", "E299"}:
                raise
            raise reference_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Missing parent {child_label} for {child_name}: "
                    f"{parent_ref.declaration_name}"
                ),
                unit=unit,
                source_span=parent_ref.source_span,
            ) from error

    def _resolve_decl_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
        missing_label: str,
    ):
        lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        matches: list[tuple[_RefLookupTarget, object]] = []
        for lookup_target in lookup_targets:
            registry = getattr(lookup_target.unit, registry_name)
            decl = registry.get(lookup_target.declaration_name)
            if decl is not None:
                matches.append((lookup_target, decl))
        if len(matches) == 1:
            lookup_target, decl = matches[0]
            return lookup_target.unit, decl
        if len(matches) > 1:
            imported_target = next(
                (
                    lookup_target
                    for lookup_target, _decl in matches
                    if lookup_target.imported_symbol is not None
                ),
                None,
            )
            if imported_target is not None:
                local_decl = next(
                    (
                        decl
                        for lookup_target, decl in matches
                        if lookup_target.imported_symbol is None
                    ),
                    None,
                )
                self._raise_imported_symbol_ambiguity(
                    ref,
                    unit=unit,
                    binding=imported_target.imported_symbol,
                    detail=(
                        f"Reference `{ref.declaration_name}` is visible both as a local "
                        f"{missing_label} and as an imported symbol."
                    ),
                    local_decl=local_decl,
                )

        if ref.module_parts:
            dotted_name = _dotted_ref_name(ref)
            raise reference_compile_error(
                code="E281",
                summary="Missing imported declaration",
                detail=f"Missing imported declaration: {dotted_name}",
                unit=unit,
                source_span=ref.source_span,
            )
        raise self._missing_local_decl_error(
            ref,
            unit=unit,
            missing_label=missing_label,
        )

    def _missing_local_decl_error(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        missing_label: str,
    ) -> CompileError:
        code = "E299"
        summary = "Compile failure"
        if missing_label in {
            "analysis declaration",
            "output shape declaration",
            "table declaration",
        }:
            code = "E276"
            summary = "Missing local declaration reference"
        return reference_compile_error(
            code=code,
            summary=summary,
            detail=f"Missing local {missing_label}: {ref.declaration_name}",
            unit=unit,
            source_span=ref.source_span,
        )

    def _expr_ref_matches_review_verdict(self, ref: model.ExprRef) -> bool:
        return (
            len(ref.parts) == 2
            and ref.parts[0] == "ReviewVerdict"
            and ref.parts[1] in _REVIEW_VERDICT_TEXT
        )

    def _display_ref(self, ref: model.NameRef, *, unit: IndexedUnit) -> str:
        matches: list[tuple[str, ReadableDecl]] = []
        try:
            for lookup_target in self._decl_lookup_targets(ref, unit=unit):
                matches.extend(
                    self._find_readable_decl_matches(
                        lookup_target.declaration_name,
                        unit=lookup_target.unit,
                    )
                )
        except CompileError:
            matches = []
        if len(matches) == 1:
            return self._display_readable_decl(matches[0][1])
        if ref.module_parts:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return _humanize_key(ref.declaration_name)

    def _try_resolve_enum_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> model.EnumDecl | None:
        try:
            lookup_unit, decl = self._resolve_decl_ref(
                ref,
                unit=unit,
                registry_name="enums_by_name",
                missing_label="enum declaration",
            )
        except CompileError:
            return None
        _ = lookup_unit
        return decl

    def _find_readable_decl_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ReadableDecl], ...]:
        matches: list[tuple[str, ReadableDecl]] = []
        for label, registry_name in _READABLE_DECL_REGISTRIES:
            if registry_name == "outputs_by_name":
                decl = self._resolve_local_output_decl(declaration_name, unit=unit)
            elif registry_name == "output_shapes_by_name":
                decl = self._resolve_local_output_shape_decl(declaration_name, unit=unit)
            else:
                decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _find_addressable_root_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, AddressableRootDecl], ...]:
        matches: list[tuple[str, AddressableRootDecl]] = []
        for label, registry_name in _ADDRESSABLE_ROOT_REGISTRIES:
            if registry_name == "outputs_by_name":
                decl = self._resolve_local_output_decl(declaration_name, unit=unit)
            elif registry_name == "output_shapes_by_name":
                decl = self._resolve_local_output_shape_decl(declaration_name, unit=unit)
            else:
                decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _display_readable_decl(self, decl: ReadableDecl) -> str:
        if isinstance(decl, model.Agent):
            return decl.title or _humanize_key(decl.name)
        return decl.title
