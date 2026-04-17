from __future__ import annotations

from doctrine import model
from doctrine._compiler.authored_diagnostics import (
    authored_compile_error,
    authored_related_site,
)
from doctrine._compiler.naming import _agent_typed_field_key, _dotted_ref_name
from doctrine._compiler.resolved_types import (
    ContractArtifact,
    ContractBinding,
    ContractBodySummary,
    ContractSectionSummary,
    IndexedUnit,
    ResolvedIoItem,
    ResolvedIoSection,
)
from doctrine._compiler.support_files import _dotted_decl_name


def _source_span(value: object | None) -> model.SourceSpan | None:
    return getattr(value, "source_span", None)


class ValidateContractsMixin:
    """Contract summary helpers for ValidateMixin."""

    def _typed_field_key(self, field: model.Field) -> str:
        return _agent_typed_field_key(field)

    def _summarize_contract_field(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractBodySummary:
        if field.parent_ref is not None:
            return self._summarize_contract_field_patch(
                field,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
            )
        if isinstance(field.value, tuple):
            inline_owner_label = (
                f"{field_kind} field `{field.title}`" if field.title is not None else owner_label
            )
            return self._summarize_non_inherited_contract_items(
                field.value,
                unit=unit,
                field_kind=field_kind,
                owner_label=inline_owner_label,
                owner_source_span=field.source_span,
            )
        if isinstance(field.value, model.IoBody):
            inline_owner_label = (
                f"{field_kind} field `{field.title}`" if field.title is not None else owner_label
            )
            return self._summarize_contract_io_body(
                field.value,
                unit=unit,
                field_kind=field_kind,
                owner_label=inline_owner_label,
                owner_source_span=field.source_span,
            )
        if isinstance(field.value, model.NameRef):
            return self._summarize_contract_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
            )
        raise authored_compile_error(
            code="E299",
            summary="Compile failure",
            detail=(
                f"Internal compiler error: unsupported {field_kind} field value in "
                f"{owner_label}: {type(field.value).__name__}"
            ),
            unit=unit,
            source_span=field.source_span,
        )

    def _merge_contract_summary(
        self,
        body: ContractBodySummary,
        *,
        decls_sink: dict[
            tuple[tuple[str, ...], str],
            tuple[IndexedUnit, model.InputDecl | model.OutputDecl],
        ],
        bindings_sink: dict[tuple[str, ...], ContractBinding],
    ) -> None:
        for artifact in body.artifacts:
            decls_sink[(artifact.unit.module_parts, artifact.decl.name)] = (
                artifact.unit,
                artifact.decl,
            )
        for binding in body.bindings:
            existing = bindings_sink.get(binding.binding_path)
            if existing is None:
                bindings_sink[binding.binding_path] = binding
                continue
            if (
                existing.artifact.kind != binding.artifact.kind
                or existing.artifact.unit.module_parts != binding.artifact.unit.module_parts
                or existing.artifact.decl.name != binding.artifact.decl.name
            ):
                raise authored_compile_error(
                    code="E260",
                    summary="Conflicting concrete-turn binding roots",
                    detail=(
                        f"Concrete-turn binding root `{'.'.join(binding.binding_path)}` "
                        "resolves to different artifacts."
                    ),
                    unit=binding.artifact.unit,
                    source_span=binding.source_span,
                    related=(
                        authored_related_site(
                            label=f"first `{'.'.join(binding.binding_path)}` binding root",
                            unit=existing.artifact.unit,
                            source_span=existing.source_span,
                        ),
                    )
                    if existing.source_span is not None
                    else (),
                )

    def _summarize_contract_field_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
    ) -> ContractBodySummary:
        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                dotted_name = _dotted_ref_name(ref)
                raise authored_compile_error(
                    code="E248",
                    summary="IO field ref kind mismatch",
                    detail=(
                        "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                        f"{dotted_name}"
                    ),
                    unit=unit,
                    source_span=ref.source_span,
                )
            target_unit, inputs_decl = self._resolve_inputs_block_ref(ref, unit=unit)
            return self._summarize_contract_io_body(
                inputs_decl.body,
                unit=target_unit,
                field_kind=field_kind,
                owner_label=_dotted_decl_name(target_unit.module_parts, inputs_decl.name),
                parent_ref=inputs_decl.parent_ref,
                owner_source_span=inputs_decl.source_span,
            )

        if self._ref_exists_in_registry(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            dotted_name = _dotted_ref_name(ref)
            raise authored_compile_error(
                code="E248",
                summary="IO field ref kind mismatch",
                detail=(
                    "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                    f"{dotted_name}"
                ),
                unit=unit,
                source_span=ref.source_span,
            )
        target_unit, outputs_decl = self._resolve_outputs_block_ref(ref, unit=unit)
        return self._summarize_contract_io_body(
            outputs_decl.body,
            unit=target_unit,
            field_kind=field_kind,
            owner_label=_dotted_decl_name(target_unit.module_parts, outputs_decl.name),
            parent_ref=outputs_decl.parent_ref,
            owner_source_span=outputs_decl.source_span,
        )

    def _summarize_contract_field_patch(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractBodySummary:
        parent_ref = field.parent_ref
        if parent_ref is None:
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Internal compiler error: {field_kind} patch field is missing "
                    f"parent ref in {owner_label}"
                ),
                unit=unit,
                source_span=field.source_span,
            )
        if not isinstance(field.value, model.IoBody):
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Internal compiler error: {field_kind} patch field is missing "
                    f"body in {owner_label}"
                ),
                unit=unit,
                source_span=field.source_span,
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                dotted_name = _dotted_ref_name(parent_ref)
                raise authored_compile_error(
                    code="E249",
                    summary="IO patch base kind mismatch",
                    detail=(
                        "Inputs patch fields must inherit from inputs blocks, not outputs "
                        f"blocks: {dotted_name}"
                    ),
                    unit=unit,
                    source_span=parent_ref.source_span,
                )
        else:
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="inputs_blocks_by_name",
            ):
                dotted_name = _dotted_ref_name(parent_ref)
                raise authored_compile_error(
                    code="E249",
                    summary="IO patch base kind mismatch",
                    detail=(
                        "Outputs patch fields must inherit from outputs blocks, not inputs "
                        f"blocks: {dotted_name}"
                    ),
                    unit=unit,
                    source_span=parent_ref.source_span,
                )
        return self._summarize_contract_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_ref=parent_ref,
            owner_source_span=field.source_span,
        )

    def _summarize_contract_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_ref: model.NameRef | None = None,
        owner_source_span: model.SourceSpan | None = None,
    ) -> ContractBodySummary:
        if parent_ref is None:
            return self._summarize_non_inherited_contract_items(
                io_body.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
                owner_source_span=owner_source_span,
            )

        parent_summary: ContractBodySummary
        parent_label: str
        if field_kind == "inputs":
            parent_unit, parent_decl = self._resolve_inputs_block_ref(parent_ref, unit=unit)
            parent_summary = self._summarize_contract_io_body(
                parent_decl.body,
                unit=parent_unit,
                field_kind=field_kind,
                owner_label=_dotted_decl_name(parent_unit.module_parts, parent_decl.name),
                parent_ref=parent_decl.parent_ref,
                owner_source_span=parent_decl.source_span,
            )
            parent_label = f"inputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
        else:
            parent_unit, parent_decl = self._resolve_outputs_block_ref(parent_ref, unit=unit)
            parent_summary = self._summarize_contract_io_body(
                parent_decl.body,
                unit=parent_unit,
                field_kind=field_kind,
                owner_label=_dotted_decl_name(parent_unit.module_parts, parent_decl.name),
                parent_ref=parent_decl.parent_ref,
                owner_source_span=parent_decl.source_span,
            )
            parent_label = f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

        if parent_summary.unkeyed_artifacts:
            details = ", ".join(
                self._display_readable_decl(artifact.decl)
                for artifact in parent_summary.unkeyed_artifacts
            )
            raise authored_compile_error(
                code="E247",
                summary="Inherited IO block needs keyed top-level entries",
                detail=(
                    f"{field_kind.title()} block `{parent_label}` contains unkeyed "
                    f"top-level refs: {details}."
                ),
                unit=unit,
                source_span=parent_ref.source_span,
                related=tuple(
                    authored_related_site(
                        label=f"unkeyed top-level `{self._display_readable_decl(artifact.decl)}` ref",
                        unit=artifact.unit,
                        source_span=artifact.source_span,
                    )
                    for artifact in parent_summary.unkeyed_artifacts
                    if artifact.source_span is not None
                ),
                hints=(
                    "Give inherited inputs and outputs blocks stable keyed sections before patching them.",
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_summary.keyed_items}
        resolved_items: list[ContractSectionSummary] = []
        unkeyed_artifacts: list[ContractArtifact] = []
        emitted_keys: dict[str, model.IoSection | model.RecordScalar | model.InheritItem | model.OverrideIoSection] = {}
        accounted_keys: set[str] = set()

        for item in io_body.items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            if isinstance(item, model.RecordRef):
                unkeyed_artifacts.append(
                    self._resolve_contract_artifact_ref(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            key = item.key
            first_item = emitted_keys.get(key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Duplicate {field_kind} item key in {owner_label}: {key}",
                    unit=unit,
                    source_span=item.source_span,
                    related=(
                        authored_related_site(
                            label=f"first `{key}` entry",
                            unit=unit,
                            source_span=_source_span(first_item),
                        ),
                    )
                    if _source_span(first_item) is not None
                    else (),
                )
            emitted_keys[key] = item

            if isinstance(item, model.IoSection):
                resolved_items.append(
                    self._summarize_contract_section(
                        key=key,
                        title=item.title,
                        items=item.items,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=(
                            f"{field_kind} section `{item.title if item.title is not None else item.key}`"
                        ),
                        binding_path=(key,),
                        source_span=item.source_span,
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise authored_compile_error(
                    code="E301",
                    summary="Invalid IO bucket item",
                    detail=f"Scalar keyed items are not allowed in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    hints=(
                        "Keep inputs and outputs buckets limited to declaration refs or titled groups.",
                    ),
                )

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise authored_compile_error(
                        code="E245",
                        summary="Cannot inherit undefined IO block entry",
                        detail=(
                            f"{field_kind.title()} block `{parent_label}` cannot inherit "
                            f"undefined key `{key}`."
                        ),
                        unit=unit,
                        source_span=item.source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise authored_compile_error(
                    code="E001",
                    summary="Cannot override undefined inherited entry",
                    detail=f"Cannot override undefined {field_kind} entry in {parent_label}: {key}",
                    unit=unit,
                    source_span=_source_span(item),
                )

            accounted_keys.add(key)
            if not isinstance(item, model.OverrideIoSection):
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        f"Internal compiler error: unsupported {field_kind} override in "
                        f"{owner_label}: {type(item).__name__}"
                    ),
                    unit=unit,
                    source_span=_source_span(item),
                )
            resolved_items.append(
                self._summarize_contract_section(
                    key=key,
                    title=item.title if item.title is not None else parent_item.title,
                    items=item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=(
                        f"{field_kind} section `{item.title if item.title is not None else parent_item.title}`"
                    ),
                    binding_path=(key,),
                    source_span=item.source_span,
                )
            )

        missing_keys = [
            item.key for item in parent_summary.keyed_items if item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise authored_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=f"Missing inherited {field_kind} entry in {owner_label}: {missing}",
                unit=unit,
                source_span=owner_source_span or parent_ref.source_span,
                related=tuple(
                    authored_related_site(
                        label=f"inherited `{key}` entry",
                        unit=parent_unit,
                        source_span=parent_items_by_key[key].source_span,
                    )
                    for key in missing_keys
                    if parent_items_by_key[key].source_span is not None
                ),
            )

        artifacts = [*unkeyed_artifacts]
        bindings: list[ContractBinding] = []
        for item in resolved_items:
            artifacts.extend(item.artifacts)
            bindings.extend(item.bindings)
        return ContractBodySummary(
            keyed_items=tuple(resolved_items),
            unkeyed_artifacts=tuple(unkeyed_artifacts),
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
        )

    def _summarize_non_inherited_contract_items(
        self,
        io_items: tuple[model.IoItem, ...] | tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        owner_source_span: model.SourceSpan | None = None,
    ) -> ContractBodySummary:
        resolved_items: list[ContractSectionSummary] = []
        unkeyed_artifacts: list[ContractArtifact] = []
        seen_keys: dict[str, model.IoSection | model.RecordSection | model.RecordScalar | model.InheritItem | model.OverrideIoSection] = {}

        for item in io_items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            if isinstance(item, model.RecordRef):
                unkeyed_artifacts.append(
                    self._resolve_contract_artifact_ref(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            key = item.key
            first_item = seen_keys.get(key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Duplicate {field_kind} item key in {owner_label}: {key}",
                    unit=unit,
                    source_span=_source_span(item),
                    related=(
                        authored_related_site(
                            label=f"first `{key}` entry",
                            unit=unit,
                            source_span=_source_span(first_item),
                        ),
                    )
                    if _source_span(first_item) is not None
                    else (),
                )
            seen_keys[key] = item

            if isinstance(item, (model.IoSection, model.RecordSection)):
                resolved_items.append(
                    self._summarize_contract_section(
                        key=key,
                        title=item.title,
                        items=item.items,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=(
                            f"{field_kind} section `{item.title if item.title is not None else item.key}`"
                        ),
                        binding_path=(key,),
                        source_span=_source_span(item),
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise authored_compile_error(
                    code="E301",
                    summary="Invalid IO bucket item",
                    detail=f"Scalar keyed items are not allowed in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    hints=(
                        "Keep inputs and outputs buckets limited to declaration refs or titled groups.",
                    ),
                )

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise authored_compile_error(
                code="E246",
                summary="IO block patch requires an inherited IO block",
                detail=(
                    f"`{item_label}` for key `{key}` requires an inherited "
                    f"{field_kind} block in `{owner_label}`."
                ),
                unit=unit,
                source_span=_source_span(item) or owner_source_span,
            )

        artifacts = [*unkeyed_artifacts]
        bindings: list[ContractBinding] = []
        for item in resolved_items:
            artifacts.extend(item.artifacts)
            bindings.extend(item.bindings)
        return ContractBodySummary(
            keyed_items=tuple(resolved_items),
            unkeyed_artifacts=tuple(unkeyed_artifacts),
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
        )

    def _summarize_contract_section(
        self,
        *,
        key: str,
        title: str | None,
        items: tuple[model.RecordItem, ...],
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        binding_path: tuple[str, ...],
        source_span: model.SourceSpan | None = None,
    ) -> ContractSectionSummary:
        artifacts: list[ContractArtifact] = []
        bindings: list[ContractBinding] = []
        direct_artifacts: list[ContractArtifact] = []
        has_keyed_children = False

        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            if isinstance(item, model.RecordSection):
                has_keyed_children = True
                child = self._summarize_contract_section(
                    key=item.key,
                    title=item.title,
                    items=item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} section `{item.title}`",
                    binding_path=(*binding_path, item.key),
                    source_span=item.source_span,
                )
                artifacts.extend(child.artifacts)
                bindings.extend(child.bindings)
                continue
            if isinstance(item, model.RecordRef):
                artifact = self._resolve_contract_artifact_ref(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                )
                artifacts.append(artifact)
                direct_artifacts.append(artifact)
                continue
            if isinstance(item, model.RecordScalar):
                raise authored_compile_error(
                    code="E301",
                    summary="Invalid IO bucket item",
                    detail=f"Scalar keyed items are not allowed in {owner_label}: {item.key}",
                    unit=unit,
                    source_span=item.source_span,
                    hints=(
                        "Keep inputs and outputs buckets limited to declaration refs or titled groups.",
                    ),
                )
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"Unsupported {field_kind} bucket item in {owner_label}: "
                    f"{type(item).__name__}"
                ),
                unit=unit,
                source_span=_source_span(item),
            )

        section_source_span = source_span or next(
            (
                artifact.source_span
                for artifact in direct_artifacts
                if artifact.source_span is not None
            ),
            None,
        )
        if not has_keyed_children and len(direct_artifacts) == 1:
            bindings.append(
                ContractBinding(
                    binding_path=binding_path,
                    artifact=direct_artifacts[0],
                    source_span=section_source_span or direct_artifacts[0].source_span,
                )
            )
        if title is None:
            if has_keyed_children or len(direct_artifacts) != 1:
                related = tuple(
                    authored_related_site(
                        label=f"direct `{self._display_readable_decl(artifact.decl)}` declaration",
                        unit=artifact.unit,
                        source_span=artifact.source_span,
                    )
                    for artifact in direct_artifacts
                    if artifact.source_span is not None
                )
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=(
                        f"Omitted title in {field_kind} section `{key}` requires "
                        "exactly one lowerable direct declaration"
                    ),
                    unit=unit,
                    source_span=section_source_span,
                    related=related,
                )
            title = direct_artifacts[0].decl.title
        return ContractSectionSummary(
            key=key,
            title=title,
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
            source_span=section_source_span,
        )

    def _resolved_io_body_artifacts(
        self,
        items: tuple[ResolvedIoItem, ...],
    ) -> tuple[ContractArtifact, ...]:
        artifacts: list[ContractArtifact] = []
        for item in items:
            if isinstance(item, ResolvedIoSection):
                artifacts.extend(item.artifacts)
            else:
                artifacts.append(item.artifact)
        return tuple(artifacts)

    def _resolved_io_body_bindings(
        self,
        items: tuple[ResolvedIoItem, ...],
    ) -> tuple[ContractBinding, ...]:
        bindings: list[ContractBinding] = []
        for item in items:
            if isinstance(item, ResolvedIoSection):
                bindings.extend(item.bindings)
        return tuple(bindings)
