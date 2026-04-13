from __future__ import annotations

from doctrine._compiler.constants import _REVIEW_CONTRACT_FACT_KEYS, _SCHEMA_FAMILY_TITLES
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class ValidateAddressableChildrenMixin:
    """Addressable tree-child helpers for ValidateMixin."""

    def _get_addressable_children(
        self,
        node: AddressableNode,
    ) -> dict[str, AddressableNode] | None:
        target = node.target
        if isinstance(target, ReviewSemanticFieldsRoot):
            children: dict[str, AddressableNode] = {}
            output_unit, _output_decl = self._resolve_review_semantic_output_decl(target.context)
            for field_name, field_path in target.context.field_bindings:
                children[field_name] = AddressableNode(
                    unit=output_unit,
                    root_decl=node.root_decl,
                    target=ReviewSemanticFieldTarget(
                        field_name=field_name,
                        field_path=field_path,
                        context=target.context,
                    ),
                )
            return children
        if isinstance(target, ReviewSemanticContractRoot):
            output_unit, _output_decl = self._resolve_review_semantic_output_decl(target.context)
            children = {
                key: AddressableNode(
                    unit=output_unit,
                    root_decl=node.root_decl,
                    target=ReviewSemanticContractFactTarget(key=key),
                )
                for key in _REVIEW_CONTRACT_FACT_KEYS
            }
            for gate in target.context.contract_gates:
                children[gate.key] = AddressableNode(
                    unit=output_unit,
                    root_decl=node.root_decl,
                    target=ReviewSemanticContractGateTarget(gate=gate),
                )
            return children
        if isinstance(target, ReviewSemanticFieldTarget):
            output_unit, output_decl = self._resolve_review_semantic_output_decl(target.context)
            field_node = self._resolve_output_field_node(
                output_decl,
                path=target.field_path,
                unit=output_unit,
                owner_label=f"review field {target.field_name}",
                surface_label="review fields",
            )
            children = self._get_addressable_children(field_node)
            if children is None:
                return None
            return {
                key: AddressableNode(
                    unit=child.unit,
                    root_decl=node.root_decl,
                    target=child.target,
                )
                for key, child in children.items()
            }
        if isinstance(
            target,
            (
                model.AnalysisDecl,
                model.SchemaDecl,
                model.DocumentDecl,
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.JsonSchemaDecl,
                model.SkillDecl,
            ),
        ):
            if isinstance(target, model.AnalysisDecl):
                analysis_body = self._resolve_analysis_decl(target, unit=node.unit)
                return {
                    item.key: AddressableNode(
                        unit=item.unit,
                        root_decl=node.root_decl,
                        target=item,
                    )
                    for item in analysis_body.items
                }
            if isinstance(target, model.SchemaDecl):
                return self._schema_items_to_addressable_children(
                    self._resolve_schema_decl(target, unit=node.unit),
                    unit=node.unit,
                    root_decl=node.root_decl,
                )
            if isinstance(target, model.DocumentDecl):
                return self._document_items_to_addressable_children(
                    self._resolve_document_decl(target, unit=node.unit).items,
                    unit=node.unit,
                    root_decl=node.root_decl,
                )
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.DocumentBlock):
            return self._readable_block_to_addressable_children(
                target,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.RecordScalar):
            if target.body is None:
                return None
            return self._record_items_to_addressable_children(
                target.body,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.RecordSection):
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.GuardedOutputSection):
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.GuardedOutputScalar):
            if target.body is None:
                return None
            return self._record_items_to_addressable_children(
                target.body,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.WorkflowDecl):
            workflow_body = self._resolve_workflow_for_addressable_paths(
                target,
                unit=node.unit,
            )
            return self._workflow_items_to_addressable_children(
                workflow_body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSectionItem):
            return self._workflow_section_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedUseItem):
            workflow_body = self._resolve_workflow_for_addressable_paths(
                target.workflow_decl,
                unit=target.target_unit,
            )
            return self._workflow_items_to_addressable_children(
                workflow_body.items,
                unit=target.target_unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedWorkflowSkillsItem):
            return self._skills_items_to_addressable_children(
                target.body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.SkillsDecl):
            skills_body = self._resolve_skills_for_addressable_paths(
                target,
                unit=node.unit,
            )
            return self._skills_items_to_addressable_children(
                skills_body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSkillsSection):
            return self._skills_section_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSkillEntry):
            if not target.items:
                return None
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, SchemaFamilyTarget):
            return self._schema_family_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ReadableColumnsTarget):
            return {
                column.key: AddressableNode(
                    unit=node.unit,
                    root_decl=node.root_decl,
                    target=column,
                )
                for column in target.columns
            }
        if isinstance(target, ReadableRowsTarget):
            return {
                row.key: AddressableNode(
                    unit=node.unit,
                    root_decl=node.root_decl,
                    target=row,
                )
                for row in target.rows
            }
        if isinstance(target, ReadableSchemaTarget):
            return {
                entry.key: AddressableNode(
                    unit=node.unit,
                    root_decl=node.root_decl,
                    target=entry,
                )
                for entry in target.entries
            }
        if isinstance(
            target,
            (
                ResolvedAnalysisSection,
                model.SchemaSection,
                model.SchemaGate,
                ResolvedSchemaArtifact,
                ResolvedSchemaGroup,
            ),
        ):
            return None
        if isinstance(target, model.EnumDecl):
            return {
                member.key: AddressableNode(
                    unit=node.unit,
                    root_decl=node.root_decl,
                    target=member,
                )
                for member in target.members
            }
        return None

    def _record_items_to_addressable_children(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(
                item,
                (
                    model.RecordScalar,
                    model.RecordSection,
                    model.GuardedOutputSection,
                    model.GuardedOutputScalar,
                    model.ReadableBlock,
                ),
            ):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _workflow_items_to_addressable_children(
        self,
        items: tuple[ResolvedWorkflowItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(unit=unit, root_decl=root_decl, target=item)
        return children

    def _workflow_section_items_to_addressable_children(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, ResolvedSectionItem):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _skills_items_to_addressable_children(
        self,
        items: tuple[ResolvedSkillsItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(unit=unit, root_decl=root_decl, target=item)
        return children

    def _skills_section_items_to_addressable_children(
        self,
        items: tuple[ResolvedSkillsSectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, ResolvedSkillEntry):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _schema_items_to_addressable_children(
        self,
        schema_body: ResolvedSchemaBody,
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        families: tuple[tuple[str, tuple[SchemaAddressableItem, ...]], ...] = (
            ("sections", schema_body.sections),
            ("gates", schema_body.gates),
            ("artifacts", schema_body.artifacts),
            ("groups", schema_body.groups),
        )
        children: dict[str, AddressableNode] = {}
        for family_key, items in families:
            if not items:
                continue
            children[family_key] = AddressableNode(
                unit=unit,
                root_decl=root_decl,
                target=SchemaFamilyTarget(
                    family_key=family_key,
                    title=_SCHEMA_FAMILY_TITLES[family_key],
                    items=items,
                ),
            )
        return children

    def _schema_family_items_to_addressable_children(
        self,
        items: tuple[SchemaAddressableItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(
                unit=unit,
                root_decl=root_decl,
                target=item,
            )
        return children

    def _document_items_to_addressable_children(
        self,
        items: tuple[model.DocumentBlock, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(
                unit=unit,
                root_decl=root_decl,
                target=item,
            )
        return children

    def _readable_block_to_addressable_children(
        self,
        block: model.DocumentBlock,
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode] | None:
        children: dict[str, AddressableNode] = {}
        if block.item_schema is not None:
            children["item_schema"] = AddressableNode(
                unit=unit,
                root_decl=root_decl,
                target=ReadableSchemaTarget(
                    title="Item Schema",
                    entries=block.item_schema.entries,
                ),
            )
        if block.row_schema is not None:
            children["row_schema"] = AddressableNode(
                unit=unit,
                root_decl=root_decl,
                target=ReadableSchemaTarget(
                    title="Row Schema",
                    entries=block.row_schema.entries,
                ),
            )

        if block.kind in {"section", "guard"}:
            payload = block.payload if isinstance(block.payload, tuple) else ()
            for item in payload:
                if isinstance(item, model.ReadableBlock):
                    children[item.key] = AddressableNode(
                        unit=unit,
                        root_decl=root_decl,
                        target=item,
                    )
            return children or None
        if block.kind in {"sequence", "bullets", "checklist"}:
            payload = block.payload if isinstance(block.payload, tuple) else ()
            for item in payload:
                if isinstance(item, model.ReadableListItem) and item.key is not None:
                    children[item.key] = AddressableNode(
                        unit=unit,
                        root_decl=root_decl,
                        target=item,
                    )
            return children or None
        if block.kind == "properties" and isinstance(block.payload, model.ReadablePropertiesData):
            for item in block.payload.entries:
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
            return children or None
        if block.kind == "definitions":
            payload = block.payload if isinstance(block.payload, tuple) else ()
            for item in payload:
                if isinstance(item, model.ReadableDefinitionItem):
                    children[item.key] = AddressableNode(
                        unit=unit,
                        root_decl=root_decl,
                        target=item,
                    )
            return children or None
        if block.kind == "table" and isinstance(block.payload, model.ReadableTableData):
            if block.payload.columns:
                children["columns"] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=ReadableColumnsTarget(columns=block.payload.columns),
                )
            if block.payload.rows:
                children["rows"] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=ReadableRowsTarget(rows=block.payload.rows),
                )
            if block.payload.row_schema is not None and "row_schema" not in children:
                children["row_schema"] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=ReadableSchemaTarget(
                        title="Row Schema",
                        entries=block.payload.row_schema.entries,
                    ),
                )
            return children or None
        if block.kind == "footnotes" and isinstance(block.payload, model.ReadableFootnotesData):
            for item in block.payload.entries:
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
            return children or None
        return None
