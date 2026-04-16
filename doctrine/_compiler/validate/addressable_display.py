from __future__ import annotations

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.naming import _humanize_key
from doctrine._compiler.readable_diagnostics import readable_compile_error
from doctrine._compiler.resolved_types import (
    AddressableNode,
    AddressableProjectionTarget,
    DisplayValue,
    ReadableColumnsTarget,
    ReadableRowsTarget,
    ReadableSchemaTarget,
    ResolvedAnalysisSection,
    ResolvedRenderProfile,
    ResolvedSchemaArtifact,
    ResolvedSchemaGroup,
    ResolvedSectionItem,
    ResolvedSkillEntry,
    ResolvedSkillsSection,
    ResolvedUseItem,
    ResolvedWorkflowSkillsItem,
    ReviewSemanticContractFactTarget,
    ReviewSemanticContractGateTarget,
    ReviewSemanticContractRoot,
    ReviewSemanticFieldTarget,
    ReviewSemanticFieldsRoot,
    RouteSemanticContext,
    SchemaFamilyTarget,
)


class ValidateAddressableDisplayMixin:
    """Addressable display helpers for ValidateMixin."""

    def _format_profile_identity_text(
        self,
        *,
        title: str | None,
        symbol: str | None,
        mode: str | None,
    ) -> str | None:
        if mode is None or mode == "title":
            return title or symbol
        if mode == "title_and_key":
            if title and symbol:
                return f"{title} (`{symbol}`)"
            return title or symbol
        if mode == "wire_only":
            return symbol or title
        return title or symbol

    def _profiled_identity_display(
        self,
        target: object,
        *,
        render_profile: ResolvedRenderProfile | None,
    ) -> DisplayValue | None:
        mode = self._render_profile_identity_mode(target, render_profile=render_profile)
        if mode is None:
            return None

        if isinstance(target, model.Agent):
            text = self._format_profile_identity_text(
                title=target.title,
                symbol=target.name,
                mode=mode,
            )
            if text is None:
                return None
            return DisplayValue(text=text, kind="title")
        if isinstance(target, model.EnumMember):
            text = self._format_profile_identity_text(
                title=target.title,
                symbol=target.value,
                mode=mode,
            )
            if text is None:
                return None
            kind = "symbol" if mode == "wire_only" else "title"
            return DisplayValue(text=text, kind=kind)

        title: str | None = None
        symbol: str | None = None
        if isinstance(
            target,
            (
                model.AnalysisDecl,
                model.SchemaDecl,
                model.TableDecl,
                model.DocumentDecl,
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.OutputSchemaDecl,
                model.SkillDecl,
                model.EnumDecl,
            ),
        ):
            title = target.title
            symbol = target.name
        elif isinstance(target, model.WorkflowDecl):
            title = target.body.title
            symbol = target.name
        elif isinstance(target, model.SkillsDecl):
            title = target.body.title
            symbol = target.name
        elif isinstance(target, ResolvedSectionItem):
            title = target.title
            symbol = target.key
        elif isinstance(target, ResolvedUseItem):
            title = target.workflow_decl.body.title
            symbol = target.workflow_decl.name
        elif isinstance(target, ResolvedWorkflowSkillsItem):
            title = target.body.title
            symbol = "skills"
        elif isinstance(target, ResolvedSkillsSection):
            title = target.title
            symbol = target.key
        elif isinstance(target, ResolvedSkillEntry):
            title = target.skill_decl.title
            symbol = target.key
        elif isinstance(target, ResolvedAnalysisSection):
            title = target.title
            symbol = target.key
        elif isinstance(target, SchemaFamilyTarget):
            title = target.title
            symbol = target.family_key
        elif isinstance(target, model.SchemaSection):
            title = target.title
            symbol = target.key
        elif isinstance(target, model.SchemaGate):
            title = target.title
            symbol = target.key
        elif isinstance(target, ResolvedSchemaArtifact):
            title = target.title
            symbol = target.key
        elif isinstance(target, ResolvedSchemaGroup):
            title = target.title
            symbol = target.key
        elif isinstance(target, model.DocumentBlock):
            title = target.title or _humanize_key(target.key)
            symbol = target.key
        elif isinstance(target, model.ReadablePropertyItem):
            title = target.title
            symbol = target.key
        elif isinstance(target, model.ReadableDefinitionItem):
            title = target.title
            symbol = target.key
        elif isinstance(target, model.ReadableSchemaEntry):
            title = target.title
            symbol = target.key
        elif isinstance(target, model.ReadableTableColumn):
            title = target.title
            symbol = target.key
        elif isinstance(target, model.ReadableTableRow):
            title = _humanize_key(target.key)
            symbol = target.key
        elif isinstance(target, ReadableColumnsTarget):
            title = "Columns"
            symbol = "columns"
        elif isinstance(target, ReadableRowsTarget):
            title = "Rows"
            symbol = "rows"
        elif isinstance(target, ReadableSchemaTarget):
            title = target.title
            symbol = target.title.replace(" ", "_").lower()

        if title is not None or symbol is not None:
            text = self._format_profile_identity_text(
                title=title,
                symbol=symbol,
                mode=mode,
            )
            if text is None:
                return None
            return DisplayValue(text=text, kind="title")
        return None

    def _display_addressable_target_value(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        target = node.target
        if isinstance(target, AddressableProjectionTarget):
            return DisplayValue(text=target.text, kind=target.kind)
        if isinstance(target, ReviewSemanticFieldsRoot):
            return DisplayValue(text="Review Fields", kind="title")
        if isinstance(target, ReviewSemanticContractRoot):
            return DisplayValue(text="Review Contract", kind="title")
        if isinstance(target, ReviewSemanticFieldTarget):
            output_unit, output_decl = self._resolve_review_semantic_output_decl(target.context)
            field_node = self._resolve_output_field_node(
                output_decl,
                path=target.field_path,
                unit=output_unit,
                owner_label=f"review field {target.field_name}",
                surface_label=surface_label,
            )
            return self._display_addressable_target_value(
                field_node,
                owner_label=owner_label,
                surface_label=surface_label,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        if isinstance(target, ReviewSemanticContractFactTarget):
            return DisplayValue(text=f"contract.{target.key}", kind="symbol")
        if isinstance(target, ReviewSemanticContractGateTarget):
            return DisplayValue(text=target.gate.title, kind="title")
        profiled_identity = self._profiled_identity_display(
            target,
            render_profile=render_profile,
        )
        if profiled_identity is not None:
            return profiled_identity
        if isinstance(target, model.Agent):
            if target.title is not None:
                return DisplayValue(text=target.title, kind="title")
            return DisplayValue(text=target.name, kind="symbol")
        if isinstance(target, model.AnalysisDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.DecisionDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.SchemaDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.TableDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.DocumentDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.WorkflowDecl):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, model.SkillsDecl):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, model.EnumDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(
            target,
            (
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.OutputSchemaDecl,
                model.SkillDecl,
            ),
        ):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(
            target,
            (
                model.OutputSchemaField,
                model.OutputSchemaDef,
                model.OutputSchemaOverrideField,
                model.OutputSchemaOverrideDef,
            ),
        ):
            return DisplayValue(
                text=target.title if target.title is not None else _humanize_key(target.key),
                kind="title",
            )
        if isinstance(target, (model.RecordSection, model.GuardedOutputSection)):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.GuardedOutputScalar):
            if target.body is not None:
                return DisplayValue(text=_humanize_key(target.key), kind="title")
            return self._display_scalar_value(
                target.value,
                unit=node.unit,
                owner_label=owner_label,
                surface_label=surface_label,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        if isinstance(target, model.RecordScalar):
            if target.body is not None:
                return DisplayValue(
                    text=self._display_record_scalar_title(
                        target,
                        node=node,
                        owner_label=owner_label,
                        surface_label=surface_label,
                        render_profile=render_profile,
                    ),
                    kind="title",
                )
            return self._display_scalar_value(
                target.value,
                unit=node.unit,
                owner_label=owner_label,
                surface_label=surface_label,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        if isinstance(target, model.EnumMember):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedSectionItem):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedUseItem):
            return DisplayValue(text=target.workflow_decl.body.title, kind="title")
        if isinstance(target, ResolvedWorkflowSkillsItem):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, ResolvedSkillsSection):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedSkillEntry):
            return DisplayValue(text=target.skill_decl.title, kind="title")
        if isinstance(target, ResolvedAnalysisSection):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, SchemaFamilyTarget):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.SchemaSection):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.SchemaGate):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedSchemaArtifact):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedSchemaGroup):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.DocumentBlock):
            return DisplayValue(
                text=(target.title or _humanize_key(target.key)),
                kind="title",
            )
        if isinstance(target, model.ReadableListItem):
            text = target.text.text if isinstance(target.text, model.EmphasizedLine) else target.text
            return DisplayValue(text=text, kind="symbol")
        if isinstance(target, model.ReadablePropertyItem):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.ReadableDefinitionItem):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.ReadableSchemaEntry):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.ReadableTableColumn):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.ReadableTableRow):
            return DisplayValue(text=_humanize_key(target.key), kind="title")
        if isinstance(target, model.ReadableFootnoteItem):
            text = target.text.text if isinstance(target.text, model.EmphasizedLine) else target.text
            return DisplayValue(text=text, kind="symbol")
        if isinstance(target, ReadableColumnsTarget):
            return DisplayValue(text="Columns", kind="title")
        if isinstance(target, ReadableRowsTarget):
            return DisplayValue(text="Rows", kind="title")
        if isinstance(target, ReadableSchemaTarget):
            return DisplayValue(text=target.title, kind="title")
        raise compile_error(
            code="E901",
            summary="Internal compiler error",
            detail=(
                "Internal compiler error: unsupported addressable target "
                f"{type(target).__name__}"
            ),
            path=node.unit.prompt_file.source_path,
            source_span=getattr(target, "source_span", None),
        )

    def _display_addressable_title(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str | None:
        target = node.target
        if isinstance(target, model.Agent):
            return target.title
        if isinstance(target, model.ReadableListItem):
            return None
        if isinstance(target, model.RecordScalar):
            return self._display_record_scalar_title(
                target,
                node=node,
                owner_label=owner_label,
                surface_label=surface_label,
                render_profile=render_profile,
            )
        return self._display_addressable_target_value(
            node,
            owner_label=owner_label,
            surface_label=surface_label,
            render_profile=render_profile,
        ).text

    def _display_record_scalar_title(
        self,
        item: model.RecordScalar,
        *,
        node: AddressableNode,
        owner_label: str,
        surface_label: str,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        root_decl = node.root_decl
        if isinstance(root_decl, model.InputDecl) and item.key == "source":
            if not isinstance(item.value, model.NameRef):
                raise readable_compile_error(
                    code="E275",
                    summary="Input source must stay typed",
                    detail=f"Input source must stay typed: {root_decl.name}",
                    unit=node.unit,
                    source_span=item.source_span,
                )
            return self._resolve_input_source_spec(item.value, unit=node.unit).title

        if isinstance(root_decl, model.OutputDecl) and item.key == "target":
            if not isinstance(item.value, model.NameRef):
                raise readable_compile_error(
                    code="E275",
                    summary="Output target must stay typed",
                    detail=f"Output target must stay typed: {root_decl.name}",
                    unit=node.unit,
                    source_span=item.source_span,
                )
            return self._resolve_output_target_spec(item.value, unit=node.unit).title

        if isinstance(root_decl, model.OutputDecl) and item.key == "shape":
            return self._display_output_shape(
                item.value,
                unit=node.unit,
                owner_label=root_decl.name,
                surface_label=surface_label,
            )

        return self._display_symbol_value(
            item.value,
            unit=node.unit,
            owner_label=owner_label,
            surface_label=surface_label,
            render_profile=render_profile,
        )
