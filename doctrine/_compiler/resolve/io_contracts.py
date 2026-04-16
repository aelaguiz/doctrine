from __future__ import annotations

from doctrine import model
from doctrine._compiler.authored_diagnostics import (
    authored_compile_error,
    authored_related_site,
)
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompiledBodyItem,
    CompiledSection,
    ContractArtifact,
    ContractBinding,
    IndexedUnit,
    OutputDeclKey,
    ResolvedContractBucket,
    ResolvedIoBody,
    ResolvedIoItem,
    ReviewSemanticContext,
    RouteSemanticContext,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveIoContractsMixin:
    """Contract and first-class IO resolution helpers for ResolveMixin."""

    def _authored_source_span(self, value: object | None) -> model.SourceSpan | None:
        return getattr(value, "source_span", None)

    def _resolve_agent_contract(self, agent: model.Agent, *, unit: IndexedUnit) -> AgentContract:
        inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]] = {}
        input_bindings_by_path: dict[tuple[str, ...], ContractBinding] = {}
        outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]] = {}
        output_bindings_by_path: dict[tuple[str, ...], ContractBinding] = {}

        for field in agent.fields:
            if isinstance(field, model.InputsField):
                summary = self._summarize_contract_field(
                    field,
                    unit=unit,
                    field_kind="inputs",
                    owner_label=f"agent {agent.name}",
                )
                self._merge_contract_summary(
                    summary,
                    decls_sink=inputs,
                    bindings_sink=input_bindings_by_path,
                )
            elif isinstance(field, model.OutputsField):
                summary = self._summarize_contract_field(
                    field,
                    unit=unit,
                    field_kind="outputs",
                    owner_label=f"agent {agent.name}",
                )
                self._merge_contract_summary(
                    summary,
                    decls_sink=outputs,
                    bindings_sink=output_bindings_by_path,
                )

        return AgentContract(
            inputs=inputs,
            input_bindings_by_path=input_bindings_by_path,
            outputs=outputs,
            output_bindings_by_path=output_bindings_by_path,
        )

    def _resolve_contract_artifact_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractArtifact:
        dotted_name = _dotted_ref_name(item.ref)
        if item.body is not None:
            raise authored_compile_error(
                code="E301",
                summary="Invalid IO bucket item",
                detail=(
                    f"Declaration refs cannot define inline bodies in {owner_label}: "
                    f"{dotted_name}"
                ),
                unit=unit,
                source_span=item.source_span,
                hints=(
                    "Keep declaration refs bare inside inputs and outputs buckets.",
                    "Use a titled group when you need nested prose around multiple declarations.",
                ),
            )
        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise authored_compile_error(
                    code="E301",
                    summary="Invalid IO bucket item",
                    detail=(
                        "Inputs refs must resolve to input declarations, not output declarations: "
                        f"{dotted_name}"
                    ),
                    unit=unit,
                    source_span=item.source_span,
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return ContractArtifact(
                kind="input",
                unit=target_unit,
                decl=decl,
                source_span=item.source_span,
            )

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise authored_compile_error(
                code="E301",
                summary="Invalid IO bucket item",
                detail=(
                    "Outputs refs must resolve to output declarations, not input declarations: "
                    f"{dotted_name}"
                ),
                unit=unit,
                source_span=item.source_span,
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        return ContractArtifact(
            kind="output",
            unit=target_unit,
            decl=decl,
            source_span=item.source_span,
        )

    def _resolve_contract_bucket_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
        path_prefix: tuple[str, ...] = (),
    ) -> ResolvedContractBucket:
        body: list[CompiledBodyItem] = []
        artifacts: list[ContractArtifact] = []
        bindings: list[ContractBinding] = []
        direct_artifacts: list[ContractArtifact] = []
        direct_sections: list[tuple[int, CompiledSection]] = []
        has_keyed_children = False

        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label=f"{field_kind} prose",
                    )
                )
                continue

            if isinstance(item, model.RecordSection):
                resolved_section = self._resolve_io_section_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    binding_path=(*path_prefix, item.key),
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_section is None:
                    continue
                has_keyed_children = True
                body.append(resolved_section.section)
                artifacts.extend(resolved_section.artifacts)
                bindings.extend(resolved_section.bindings)
                continue

            if isinstance(item, model.RecordRef):
                resolved_ref = self._resolve_contract_bucket_ref_entry(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_ref is None:
                    continue
                compiled_section, artifact = resolved_ref
                body_index = len(body)
                body.append(compiled_section)
                artifacts.append(artifact)
                direct_artifacts.append(artifact)
                direct_sections.append((body_index, compiled_section))
                continue

            if isinstance(item, model.RecordScalar):
                raise authored_compile_error(
                    code="E301",
                    summary="Invalid IO bucket item",
                    detail=(
                        f"IO bucket `{owner_label}` cannot contain scalar keyed item "
                        f"`{item.key}`."
                    ),
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
                source_span=self._authored_source_span(item),
            )

        return ResolvedContractBucket(
            body=tuple(body),
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
            direct_artifacts=tuple(direct_artifacts),
            direct_sections=tuple(direct_sections),
            has_keyed_children=has_keyed_children,
        )

    def _resolve_contract_bucket_ref_entry(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> tuple[CompiledSection, ContractArtifact] | None:
        dotted_name = _dotted_ref_name(item.ref)
        if item.body is not None:
            raise authored_compile_error(
                code="E301",
                summary="Invalid IO bucket item",
                detail=(
                    f"Declaration refs cannot define inline bodies in {owner_label}: "
                    f"{dotted_name}"
                ),
                unit=unit,
                source_span=item.source_span,
                hints=(
                    "Keep declaration refs bare inside inputs and outputs buckets.",
                    "Use a titled group when you need nested prose around multiple declarations.",
                ),
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise authored_compile_error(
                    code="E301",
                    summary="Invalid IO bucket item",
                    detail=(
                        "Inputs refs must resolve to input declarations, not output declarations: "
                        f"{dotted_name}"
                    ),
                    unit=unit,
                    source_span=item.source_span,
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return (
                self._compile_input_decl(decl, unit=target_unit),
                ContractArtifact(
                    kind="input",
                    unit=target_unit,
                    decl=decl,
                    source_span=item.source_span,
                ),
            )

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise authored_compile_error(
                code="E301",
                summary="Invalid IO bucket item",
                detail=(
                    "Outputs refs must resolve to output declarations, not input declarations: "
                    f"{dotted_name}"
                ),
                unit=unit,
                source_span=item.source_span,
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        output_key = (target_unit.module_parts, decl.name)
        if output_key in excluded_output_keys:
            return None
        review_semantics = self._review_output_context_for_key(
            review_output_contexts,
            output_key,
        )
        route_semantics = self._route_output_context_for_key(
            route_output_contexts,
            output_key,
        )
        return (
            self._compile_output_decl(
                decl,
                unit=target_unit,
                allow_review_semantics=review_semantics is not None,
                allow_route_semantics=route_semantics is not None,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            ),
            ContractArtifact(
                kind="output",
                unit=target_unit,
                decl=decl,
                source_span=item.source_span,
            ),
        )

    def _resolve_inputs_decl(
        self, inputs_decl: model.InputsDecl, *, unit: IndexedUnit
    ) -> ResolvedIoBody:
        inputs_key = (unit.module_parts, inputs_decl.name)
        cached = self._resolved_inputs_cache.get(inputs_key)
        if cached is not None:
            return cached

        if inputs_key in self._inputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._inputs_resolution_stack, inputs_key]
            )
            raise authored_compile_error(
                code="E244",
                summary="Cyclic IO block inheritance",
                detail=f"Inputs inheritance cycle: {cycle}.",
                unit=unit,
                source_span=inputs_decl.source_span,
            )

        self._inputs_resolution_stack.append(inputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if inputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_inputs_decl(
                    inputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"inputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_io_body(
                inputs_decl.body,
                unit=unit,
                field_kind="inputs",
                owner_label=_dotted_decl_name(unit.module_parts, inputs_decl.name),
                parent_io=parent_io,
                parent_label=parent_label,
            )
            self._resolved_inputs_cache[inputs_key] = resolved
            return resolved
        finally:
            self._inputs_resolution_stack.pop()

    def _resolve_non_inherited_io_items(
        self,
        io_items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> tuple[ResolvedIoItem, ...]:
        resolved_items: list[ResolvedIoItem] = []
        seen_items: dict[str, model.IoSection | model.InheritItem | model.OverrideIoSection] = {}

        for item in io_items:
            if isinstance(item, model.RecordRef):
                resolved_item = self._resolve_io_ref_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_item is not None:
                    resolved_items.append(resolved_item)
                continue

            key = item.key
            first_item = seen_items.get(key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Duplicate {field_kind} item key in {owner_label}: {key}",
                    unit=unit,
                    source_span=self._authored_source_span(item),
                    related=(
                        authored_related_site(
                            label=f"first `{key}` entry",
                            unit=unit,
                            source_span=self._authored_source_span(first_item),
                        ),
                    )
                    if self._authored_source_span(first_item) is not None
                    else (),
                )
            seen_items[key] = item

            if isinstance(item, model.IoSection):
                resolved_item = self._resolve_io_section_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    binding_path=(item.key,),
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_item is not None:
                    resolved_items.append(resolved_item)
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise authored_compile_error(
                code="E246",
                summary="IO block patch requires an inherited IO block",
                detail=(
                    f"`{item_label}` for key `{key}` requires an inherited "
                    f"{field_kind} block in `{owner_label}`."
                ),
                unit=unit,
                source_span=self._authored_source_span(item),
            )

        return tuple(resolved_items)
