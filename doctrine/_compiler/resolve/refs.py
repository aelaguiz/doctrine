from __future__ import annotations

from doctrine._compiler.constants import (
    _ADDRESSABLE_ROOT_REGISTRIES,
    _BUILTIN_RENDER_PROFILE_NAMES,
    _READABLE_DECL_REGISTRIES,
    _REVIEW_VERDICT_TEXT,
)
from doctrine._compiler.naming import _dotted_ref_name, _humanize_key
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class ResolveRefsMixin:
    """Ref lookup helpers for ResolveMixin."""

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

    def _resolve_json_schema_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.JsonSchemaDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="json_schemas_by_name",
            missing_label="json schema declaration",
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
            raise CompileError(
                f"Internal compiler error: {child_label} has no parent ref: {child_name}"
            )
        if not parent_ref.module_parts:
            registry = getattr(unit, registry_name)
            parent_decl = registry.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent {child_label} for {child_name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return resolve_parent_ref(parent_ref, unit=unit)

    def _resolve_decl_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
        missing_label: str,
    ):
        if not ref.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                raise CompileError(f"Missing local {missing_label}: {ref.declaration_name}")
            return unit, decl

        if ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                dotted_name = _dotted_ref_name(ref)
                raise CompileError(f"Missing imported declaration: {dotted_name}")
            return unit, decl

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")

        registry = getattr(target_unit, registry_name)
        decl = registry.get(ref.declaration_name)
        if decl is None:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Missing imported declaration: {dotted_name}")
        return target_unit, decl

    def _expr_ref_matches_review_verdict(self, ref: model.ExprRef) -> bool:
        return (
            len(ref.parts) == 2
            and ref.parts[0] == "ReviewVerdict"
            and ref.parts[1] in _REVIEW_VERDICT_TEXT
        )

    def _display_ref(self, ref: model.NameRef, *, unit: IndexedUnit) -> str:
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            lookup_unit = None
        if lookup_unit is not None:
            matches = self._find_readable_decl_matches(ref.declaration_name, unit=lookup_unit)
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
            lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        return lookup_unit.enums_by_name.get(ref.declaration_name)

    def _find_readable_decl_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ReadableDecl], ...]:
        matches: list[tuple[str, ReadableDecl]] = []
        for label, registry_name in _READABLE_DECL_REGISTRIES:
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
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _display_readable_decl(self, decl: ReadableDecl) -> str:
        if isinstance(decl, model.Agent):
            return decl.title or _humanize_key(decl.name)
        return decl.title
