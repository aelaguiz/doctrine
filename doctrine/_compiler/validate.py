from __future__ import annotations

from doctrine._compiler.shared import *  # noqa: F401,F403
from doctrine._compiler.shared import (
    _ADDRESSABLE_ROOT_REGISTRIES,
    _BUILTIN_INPUT_SOURCES,
    _BUILTIN_OUTPUT_TARGETS,
    _BUILTIN_RENDER_PROFILE_NAMES,
    _INTERPOLATION_EXPR_RE,
    _INTERPOLATION_RE,
    _READABLE_DECL_REGISTRIES,
    _RESERVED_AGENT_FIELD_KEYS,
    _REVIEW_CONTRACT_FACT_KEYS,
    _REVIEW_GUARD_FIELD_NAMES,
    _REVIEW_OPTIONAL_FIELD_NAMES,
    _REVIEW_REQUIRED_FIELD_NAMES,
    _REVIEW_VERDICT_TEXT,
    _SCHEMA_FAMILY_TITLES,
    _agent_typed_field_key,
    _default_worker_count,
    _display_addressable_ref,
    _dotted_decl_name,
    _dotted_ref_name,
    _humanize_key,
    _law_path_from_name_ref,
    _lowercase_initial,
    _name_ref_from_dotted_name,
    _resolve_render_profile_mode,
    _semantic_render_target_for_block,
)

_LAW_TARGET_ALLOWED_KINDS = {
    "current_artifact": ("input", "output"),
    "invalidate": ("input", "output", "schema_group"),
    "own_only": ("input", "output", "schema_family"),
    "path_set": ("input", "output"),
}
_PRESERVE_TARGET_ALLOWED_KINDS = {
    "exact": ("input", "output", "schema_family"),
    "structure": ("input", "output"),
    "decisions": ("input", "output"),
    "mapping": ("input", "output", "schema_family", "grounding"),
    "vocabulary": ("enum", "input", "output", "schema_family"),
}


class ValidateMixin:
    """Validation, review, and route helper owner for CompilationContext."""

    def _named_non_output_decl_kind(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        registry_order = (
            ("render_profile declaration", unit.render_profiles_by_name),
            ("analysis declaration", unit.analyses_by_name),
            ("decision declaration", unit.decisions_by_name),
            ("schema declaration", unit.schemas_by_name),
            ("document declaration", unit.documents_by_name),
            ("workflow declaration", unit.workflows_by_name),
            ("route_only declaration", unit.route_onlys_by_name),
            ("grounding declaration", unit.groundings_by_name),
            ("review declaration", unit.reviews_by_name),
            ("skills declaration", unit.skills_blocks_by_name),
            ("inputs block", unit.inputs_blocks_by_name),
            ("input declaration", unit.inputs_by_name),
            ("input source declaration", unit.input_sources_by_name),
            ("outputs block", unit.outputs_blocks_by_name),
            ("output target declaration", unit.output_targets_by_name),
            ("output shape declaration", unit.output_shapes_by_name),
            ("json schema declaration", unit.json_schemas_by_name),
            ("skill declaration", unit.skills_by_name),
            ("agent declaration", unit.agents_by_name),
            ("enum declaration", unit.enums_by_name),
        )
        for label, registry in registry_order:
            if declaration_name in registry:
                return label
        return None

    def _is_builtin_turn_response_target_ref(self, ref: model.NameRef) -> bool:
        return not ref.module_parts and ref.declaration_name == "TurnResponse"

    def _final_output_shape_name(self, value: model.RecordScalarValue) -> str | None:
        if isinstance(value, model.AddressableRef):
            return None
        if isinstance(value, str):
            return value
        return value.declaration_name

    def _final_output_format_label(
        self,
        output_decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        json_summary: FinalOutputJsonShapeSummary | None,
    ) -> str:
        if json_summary is not None:
            return "Structured JSON"
        shape_ref = next(
            (
                item.value
                for item in output_decl.items
                if isinstance(item, model.RecordScalar) and item.key == "shape" and item.body is None
            ),
            None,
        )
        if shape_ref is not None and (
            self._is_markdown_shape_value(shape_ref, unit=unit)
            or self._is_comment_shape_value(shape_ref, unit=unit)
        ):
            return "Natural-language markdown"
        return "Natural-language text"

    def _pipe_table_lines(
        self,
        headers: tuple[str, ...],
        rows: tuple[tuple[str, ...], ...],
    ) -> tuple[str, ...]:
        escaped_headers = tuple(header.replace("|", "\\|") for header in headers)
        lines = [
            "| " + " | ".join(escaped_headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for row in rows:
            lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
        return tuple(lines)

    def _load_json_schema_payload_rows(
        self,
        *,
        schema_unit: IndexedUnit,
        schema_decl: model.JsonSchemaDecl,
        schema_file: str | None,
    ) -> tuple[tuple[str, str, str], ...]:
        if schema_file is None:
            return ()
        payload = self._read_required_final_output_support_text(
            schema_unit,
            schema_file,
            owner_label=f"json schema {schema_decl.name}",
        )
        try:
            schema_data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise CompileError(
                "E216 final_output schema file must contain valid JSON object in "
                f"json schema {schema_decl.name}: {schema_file}"
            ) from exc
        if not isinstance(schema_data, dict):
            raise CompileError(
                "E216 final_output schema file must contain valid JSON object in "
                f"json schema {schema_decl.name}: {schema_file}"
            )
        properties = schema_data.get("properties")
        if not isinstance(properties, dict):
            return ()
        rows: list[tuple[str, str, str]] = []
        for field_name, field_schema in properties.items():
            if not isinstance(field_schema, dict):
                continue
            rows.append(
                (
                    f"`{field_name}`",
                    self._json_schema_type_label(field_schema),
                    self._json_schema_meaning(field_schema),
                )
            )
        return tuple(rows)

    def _json_schema_type_label(self, field_schema: dict[str, object]) -> str:
        schema_type = field_schema.get("type")
        if isinstance(schema_type, list):
            labels = []
            for item in schema_type:
                if item == "array":
                    labels.append(self._json_schema_array_type_label(field_schema))
                    continue
                labels.append("null" if item == "null" else str(item))
            return " | ".join(labels)
        if isinstance(schema_type, str):
            if schema_type == "array":
                return self._json_schema_array_type_label(field_schema)
            return schema_type
        if "enum" in field_schema and isinstance(field_schema["enum"], list):
            return "enum"
        return "value"

    def _json_schema_array_type_label(self, field_schema: dict[str, object]) -> str:
        items = field_schema.get("items")
        if isinstance(items, dict):
            item_type = items.get("type")
            if isinstance(item_type, str):
                return f"array<{item_type}>"
        return "array"

    def _json_schema_meaning(self, field_schema: dict[str, object]) -> str:
        description = field_schema.get("description")
        if isinstance(description, str) and description.strip():
            return description.strip()
        enum_values = field_schema.get("enum")
        if isinstance(enum_values, list) and enum_values:
            rendered = ", ".join(f"`{value}`" for value in enum_values)
            return f"One of {rendered}."
        return ""

    def _read_declared_support_text(
        self,
        unit: IndexedUnit,
        relative_path: str | None,
    ) -> str | None:
        if relative_path is None:
            return None
        path = self._resolve_declared_support_path(unit, relative_path)
        try:
            return path.read_text()
        except OSError:
            return None

    def _resolve_declared_support_path(
        self,
        unit: IndexedUnit,
        relative_path: str,
    ) -> Path:
        return (unit.prompt_root.parent / relative_path).resolve()

    def _read_required_final_output_support_text(
        self,
        unit: IndexedUnit,
        relative_path: str,
        *,
        owner_label: str,
    ) -> str:
        text = self._read_declared_support_text(unit, relative_path)
        if text is not None:
            return text
        raise CompileError(
            "E215 final_output support file is missing or unreadable in "
            f"{owner_label}: {relative_path}"
        )

    def _review_output_contexts_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> frozenset[tuple[OutputDeclKey, ReviewSemanticContext]]:
        output_contexts: set[tuple[OutputDeclKey, ReviewSemanticContext]] = set()
        for field in agent.fields:
            if not isinstance(field, model.ReviewField):
                continue
            review_unit, review_decl = self._resolve_review_ref(field.value, unit=unit)
            resolved = self._resolve_review_decl(review_decl, unit=review_unit)
            if resolved.comment_output is None:
                continue
            output_unit, output_decl = self._resolve_output_decl(
                resolved.comment_output.output_ref,
                unit=review_unit,
            )
            contract_gates: tuple[ReviewContractGate, ...] = ()
            if resolved.cases:
                collected: list[ReviewContractGate] = []
                seen_gate_keys: set[str] = set()
                for case in resolved.cases:
                    try:
                        case_gates = self._resolve_review_contract_spec(
                            case.contract.contract_ref,
                            unit=review_unit,
                            owner_label=(
                                f"review {_dotted_decl_name(review_unit.module_parts, review_decl.name)}"
                            ),
                        ).gates
                    except CompileError:
                        continue
                    for gate in case_gates:
                        if gate.key in seen_gate_keys:
                            continue
                        seen_gate_keys.add(gate.key)
                        collected.append(gate)
                contract_gates = tuple(collected)
            elif resolved.contract is not None:
                try:
                    contract_gates = self._resolve_review_contract_spec(
                        resolved.contract.contract_ref,
                        unit=review_unit,
                        owner_label=f"review {_dotted_decl_name(review_unit.module_parts, review_decl.name)}",
                    ).gates
                except CompileError:
                    contract_gates = ()
            field_bindings: list[tuple[str, tuple[str, ...]]] = []
            seen_bindings: set[str] = set()
            if resolved.fields is not None:
                for binding in resolved.fields.bindings:
                    if binding.semantic_field in seen_bindings:
                        continue
                    seen_bindings.add(binding.semantic_field)
                    field_bindings.append((binding.semantic_field, binding.field_path))
            output_contexts.add(
                (
                    (output_unit.module_parts, output_decl.name),
                    ReviewSemanticContext(
                        review_module_parts=review_unit.module_parts,
                        output_module_parts=output_unit.module_parts,
                        output_name=output_decl.name,
                        field_bindings=tuple(field_bindings),
                        contract_gates=contract_gates,
                    ),
                )
            )
        return frozenset(output_contexts)

    def _review_output_context_for_key(
        self,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        output_key: OutputDeclKey,
    ) -> ReviewSemanticContext | None:
        for key, context in review_output_contexts:
            if key == output_key:
                return context
        return None

    def _primary_review_output_context(
        self,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
    ) -> tuple[OutputDeclKey, ReviewSemanticContext] | None:
        if not review_output_contexts:
            return None
        return sorted(
            review_output_contexts,
            key=lambda item: _dotted_decl_name(item[0][0], item[0][1]),
        )[0]

    def _route_output_contexts_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
        resolved_slots: dict[str, ResolvedWorkflowBody],
        agent_contract: AgentContract,
    ) -> frozenset[tuple[OutputDeclKey, RouteSemanticContext]]:
        emitted_output_keys = tuple(agent_contract.outputs.keys())
        if not emitted_output_keys:
            return frozenset()

        context: RouteSemanticContext | None = None
        review_fields = [field for field in agent.fields if isinstance(field, model.ReviewField)]
        if review_fields:
            review_unit, review_decl = self._resolve_review_ref(review_fields[0].value, unit=unit)
            context = self._route_semantic_context_from_review_decl(
                review_decl,
                unit=review_unit,
            )
        elif (workflow_body := resolved_slots.get("workflow")) is not None and workflow_body.law is not None:
            context = self._route_semantic_context_from_law_items(
                workflow_body.law.items,
                unit=unit,
            )

        if context is None:
            return frozenset()
        return frozenset((output_key, context) for output_key in emitted_output_keys)

    def _route_output_context_for_key(
        self,
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        output_key: OutputDeclKey,
    ) -> RouteSemanticContext | None:
        for key, context in route_output_contexts:
            if key == output_key:
                return context
        return None

    def _route_semantic_context_from_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        unit: IndexedUnit,
    ) -> RouteSemanticContext | None:
        resolved = self._resolve_review_decl(review_decl, unit=unit)
        branches: list[RouteSemanticBranch] = []
        has_unrouted_branch = False

        def collect_section(
            section: model.ReviewOutcomeSection,
            *,
            verdict: str,
        ) -> None:
            nonlocal has_unrouted_branch
            for branch in self._collect_review_outcome_leaf_branches(section.items, unit=unit):
                if not branch.routes:
                    has_unrouted_branch = True
                    continue
                for route in branch.routes:
                    branches.append(
                        self._route_semantic_branch_from_route(
                            route.target,
                            label=route.label,
                            unit=unit,
                            review_verdict=verdict,
                        )
                    )

        if resolved.cases:
            for case in resolved.cases:
                collect_section(case.on_accept, verdict=_REVIEW_VERDICT_TEXT["accept"])
                collect_section(case.on_reject, verdict=_REVIEW_VERDICT_TEXT["changes_requested"])
        else:
            for item in resolved.items:
                if not isinstance(item, model.ReviewOutcomeSection):
                    continue
                verdict = (
                    _REVIEW_VERDICT_TEXT["accept"]
                    if item.key == "on_accept"
                    else _REVIEW_VERDICT_TEXT["changes_requested"]
                )
                collect_section(item, verdict=verdict)

        return self._build_route_semantic_context(
            branches,
            has_unrouted_branch=has_unrouted_branch,
        )

    def _route_semantic_context_from_law_items(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
    ) -> RouteSemanticContext | None:
        branches: list[RouteSemanticBranch] = []
        has_unrouted_branch = False
        for branch in self._collect_law_leaf_branches(items, unit=unit):
            if not branch.routes:
                has_unrouted_branch = True
                continue
            if not any(route.when_expr is None for route in branch.routes):
                has_unrouted_branch = True
            for route in branch.routes:
                branches.append(
                    self._route_semantic_branch_from_route(
                        route.target,
                        label=route.label,
                        unit=unit,
                    )
                )
        return self._build_route_semantic_context(
            branches,
            has_unrouted_branch=has_unrouted_branch,
        )

    def _route_semantic_branch_from_route(
        self,
        target: model.NameRef,
        *,
        label: str,
        unit: IndexedUnit,
        review_verdict: str | None = None,
    ) -> RouteSemanticBranch:
        route_unit, route_agent = self._resolve_agent_ref(target, unit=unit)
        return RouteSemanticBranch(
            target_module_parts=route_unit.module_parts,
            target_name=route_agent.name,
            target_title=route_agent.title,
            label=label,
            review_verdict=review_verdict,
        )

    def _build_route_semantic_context(
        self,
        branches: list[RouteSemanticBranch],
        *,
        has_unrouted_branch: bool,
    ) -> RouteSemanticContext | None:
        if not branches and not has_unrouted_branch:
            return None
        seen: set[tuple[tuple[str, ...], str, str, str | None]] = set()
        deduped: list[RouteSemanticBranch] = []
        for branch in branches:
            key = (
                branch.target_module_parts,
                branch.target_name,
                branch.label,
                branch.review_verdict,
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(branch)
        return RouteSemanticContext(
            branches=tuple(deduped),
            has_unrouted_branch=has_unrouted_branch,
        )

    def _narrow_route_semantics(
        self,
        route_semantics: RouteSemanticContext | None,
        expr: model.Expr | None,
        *,
        unit: IndexedUnit,
    ) -> RouteSemanticContext | None:
        if route_semantics is None or expr is None:
            return route_semantics

        narrowed = route_semantics
        exists_state = self._route_guard_exists_state(expr)
        if exists_state is True:
            narrowed = replace(narrowed, route_required=True)
        elif exists_state is False:
            narrowed = RouteSemanticContext(branches=(), has_unrouted_branch=False)

        verdict = self._route_guard_review_verdict(expr, unit=unit)
        if verdict is not None:
            narrowed = self._route_semantics_for_review_verdict(narrowed, verdict)
        return narrowed

    def _route_guard_exists_state(self, expr: model.Expr) -> bool | None:
        if isinstance(expr, model.ExprRef):
            return True if expr.parts == ("route", "exists") else None
        if isinstance(expr, model.ExprBinary):
            if expr.op in {"==", "!="}:
                left_is_route = isinstance(expr.left, model.ExprRef) and expr.left.parts == (
                    "route",
                    "exists",
                )
                right_is_route = isinstance(expr.right, model.ExprRef) and expr.right.parts == (
                    "route",
                    "exists",
                )
                if left_is_route and isinstance(expr.right, bool):
                    return expr.right if expr.op == "==" else not expr.right
                if right_is_route and isinstance(expr.left, bool):
                    return expr.left if expr.op == "==" else not expr.left
            if expr.op == "and":
                left = self._route_guard_exists_state(expr.left)
                right = self._route_guard_exists_state(expr.right)
                if left is False or right is False:
                    return False
                if left is True or right is True:
                    return True
        return None

    def _route_guard_review_verdict(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._route_guard_review_verdict(expr.left, unit=unit)
                right = self._route_guard_review_verdict(expr.right, unit=unit)
                if left is None:
                    return right
                if right is None:
                    return left
                return left if left == right else None
            if expr.op == "==":
                left_is_verdict = isinstance(expr.left, model.ExprRef) and expr.left.parts == ("verdict",)
                right_is_verdict = isinstance(expr.right, model.ExprRef) and expr.right.parts == ("verdict",)
                if left_is_verdict:
                    return self._resolve_constant_enum_member(expr.right, unit=unit)
                if right_is_verdict:
                    return self._resolve_constant_enum_member(expr.left, unit=unit)
        return None

    def _route_semantics_for_review_verdict(
        self,
        route_semantics: RouteSemanticContext,
        verdict: str,
    ) -> RouteSemanticContext:
        matching = tuple(
            branch for branch in route_semantics.branches if branch.review_verdict in {None, verdict}
        )
        has_unrouted_branch = route_semantics.has_unrouted_branch and not matching
        return RouteSemanticContext(
            branches=matching,
            has_unrouted_branch=has_unrouted_branch,
            route_required=route_semantics.route_required,
        )

    def _route_semantic_branch_title(self, branch: RouteSemanticBranch) -> str:
        return branch.target_title or _humanize_key(branch.target_name)

    def _route_semantic_branch_summary(self, branch: RouteSemanticBranch) -> str:
        return f"{branch.label} Next owner: {self._route_semantic_branch_title(branch)}."

    def _route_semantic_parts(
        self,
        ref: model.AddressableRef,
    ) -> tuple[str, ...] | None:
        parts = (*ref.root.module_parts, ref.root.declaration_name, *ref.path)
        if not parts or parts[0] != "route":
            return None
        return parts

    def _route_semantic_branches_for_read(
        self,
        route_semantics: RouteSemanticContext | None,
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> tuple[RouteSemanticBranch, ...]:
        if route_semantics is None:
            raise CompileError(
                f"Missing route semantics in {surface_label} {owner_label}: {ref_label}"
            )
        if route_semantics.has_unrouted_branch and not route_semantics.route_required:
            raise CompileError(
                "route semantics are not live on every branch in "
                f"{surface_label} {owner_label}: {ref_label}; guard the read with `route.exists`."
            )
        if not route_semantics.branches:
            raise CompileError(
                f"route semantics require a routed branch in {surface_label} {owner_label}: {ref_label}"
            )
        return route_semantics.branches

    def _unique_route_semantic_branch(
        self,
        branches: tuple[RouteSemanticBranch, ...],
        *,
        key_fn,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        detail_label: str,
    ) -> RouteSemanticBranch:
        unique_keys = {key_fn(branch) for branch in branches}
        if len(unique_keys) != 1:
            raise CompileError(
                f"Ambiguous {detail_label} in {surface_label} {owner_label}: {ref_label}"
            )
        return branches[0]

    def _review_semantic_field_path(
        self,
        review_semantics: ReviewSemanticContext,
        field_name: str,
    ) -> tuple[str, ...] | None:
        for name, path in review_semantics.field_bindings:
            if name == field_name:
                return path
        return None

    def _review_semantic_contract_gate(
        self,
        review_semantics: ReviewSemanticContext,
        gate_key: str,
    ) -> ReviewContractGate | None:
        for gate in review_semantics.contract_gates:
            if gate.key == gate_key:
                return gate
        return None

    def _review_semantic_addressable_parts(
        self,
        ref: model.AddressableRef,
    ) -> tuple[str, ...] | None:
        parts = (*ref.root.module_parts, ref.root.declaration_name, *ref.path)
        if len(parts) < 2 or parts[0] not in {"contract", "fields"}:
            return None
        return parts

    def _review_semantic_root_node(
        self,
        root_key: str,
        review_semantics: ReviewSemanticContext,
    ) -> AddressableNode | None:
        if root_key == "fields":
            root = ReviewSemanticFieldsRoot(review_semantics)
        elif root_key == "contract":
            root = ReviewSemanticContractRoot(review_semantics)
        else:
            return None
        output_unit, _output_decl = self._resolve_review_semantic_output_decl(review_semantics)
        return AddressableNode(
            unit=output_unit,
            root_decl=root,
            target=root,
        )

    def _output_path_has_guarded_detail(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
    ) -> bool:
        return bool(self._output_path_guards(output_decl.items, path=path))

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
            )
        if isinstance(field.value, model.NameRef):
            return self._summarize_contract_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
            )
        raise CompileError(
            f"Internal compiler error: unsupported {field_kind} field value in {owner_label}: "
            f"{type(field.value).__name__}"
        )

    def _merge_contract_summary(
        self,
        body: ContractBodySummary,
        *,
        decls_sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl | model.OutputDecl]],
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
                raise CompileError(
                    "Conflicting concrete-turn binding roots resolve different artifacts: "
                    f"{'.'.join(binding.binding_path)}"
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
                raise CompileError(
                    "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(ref)}"
                )
            target_unit, inputs_decl = self._resolve_inputs_block_ref(ref, unit=unit)
            return self._summarize_contract_io_body(
                inputs_decl.body,
                unit=target_unit,
                field_kind=field_kind,
                owner_label=_dotted_decl_name(target_unit.module_parts, inputs_decl.name),
                parent_ref=inputs_decl.parent_ref,
            )

        if self._ref_exists_in_registry(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(ref)}"
            )
        target_unit, outputs_decl = self._resolve_outputs_block_ref(ref, unit=unit)
        return self._summarize_contract_io_body(
            outputs_decl.body,
            unit=target_unit,
            field_kind=field_kind,
            owner_label=_dotted_decl_name(target_unit.module_parts, outputs_decl.name),
            parent_ref=outputs_decl.parent_ref,
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
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing parent ref in {owner_label}"
            )
        if not isinstance(field.value, model.IoBody):
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing body in {owner_label}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs patch fields must inherit from inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
        else:
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="inputs_blocks_by_name",
            ):
                raise CompileError(
                    "Outputs patch fields must inherit from outputs blocks, not inputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
        return self._summarize_contract_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_ref=parent_ref,
        )

    def _summarize_contract_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_ref: model.NameRef | None = None,
    ) -> ContractBodySummary:
        if parent_ref is None:
            return self._summarize_non_inherited_contract_items(
                io_body.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
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
            )
            parent_label = f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

        if parent_summary.unkeyed_artifacts:
            details = ", ".join(
                self._display_readable_decl(artifact.decl)
                for artifact in parent_summary.unkeyed_artifacts
            )
            raise CompileError(
                f"Cannot inherit {field_kind} block with unkeyed top-level refs in {parent_label}: {details}"
            )

        parent_items_by_key = {item.key: item for item in parent_summary.keyed_items}
        resolved_items: list[ContractSectionSummary] = []
        unkeyed_artifacts: list[ContractArtifact] = []
        emitted_keys: set[str] = set()
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
            if key in emitted_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._summarize_contract_section(
                        key=key,
                        items=item.items,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=f"{field_kind} section `{item.title}`",
                        binding_path=(key,),
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined {field_kind} entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined {field_kind} entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if not isinstance(item, model.OverrideIoSection):
                raise CompileError(
                    f"Internal compiler error: unsupported {field_kind} override in {owner_label}: {type(item).__name__}"
                )
            resolved_items.append(
                self._summarize_contract_section(
                    key=key,
                    items=item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=(
                        f"{field_kind} section `{item.title if item.title is not None else key}`"
                    ),
                    binding_path=(key,),
                )
            )

        missing_keys = [
            item.key for item in parent_summary.keyed_items if item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited {field_kind} entry in {owner_label}: {missing}"
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
    ) -> ContractBodySummary:
        resolved_items: list[ContractSectionSummary] = []
        unkeyed_artifacts: list[ContractArtifact] = []
        seen_keys: set[str] = set()

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
            if key in seen_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._summarize_contract_section(
                        key=key,
                        items=item.items,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=f"{field_kind} section `{item.title}`",
                        binding_path=(key,),
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited {field_kind} block in {owner_label}: {key}"
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
        items: tuple[model.RecordItem, ...],
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        binding_path: tuple[str, ...],
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
                    items=item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} section `{item.title}`",
                    binding_path=(*binding_path, item.key),
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
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )
            raise CompileError(
                f"Unsupported {field_kind} bucket item in {owner_label}: {type(item).__name__}"
            )

        if not has_keyed_children and len(direct_artifacts) == 1:
            bindings.append(
                ContractBinding(
                    binding_path=binding_path,
                    artifact=direct_artifacts[0],
                )
            )
        return ContractSectionSummary(
            key=key,
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
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

    def _enforce_legacy_role_workflow_order(self, agent: model.Agent) -> None:
        if len(agent.fields) != 2:
            return

        first, second = agent.fields
        if isinstance(first, (model.RoleScalar, model.RoleBlock)):
            return
        if not isinstance(second, (model.RoleScalar, model.RoleBlock)):
            return
        if not isinstance(first, model.AuthoredSlotField) or first.key != "workflow":
            return

        raise CompileError(
            f"Agent {agent.name} is outside the shipped subset: expected `role` followed by `workflow`."
        )

    def _ensure_valid_authored_slot_key(self, key: str, agent_name: str) -> None:
        if key in _RESERVED_AGENT_FIELD_KEYS:
            raise CompileError(
                f"Reserved typed agent field cannot be used as authored slot in {agent_name}: {key}"
            )

    def _validate_route_only_guarded_output(
        self,
        output_decl: model.OutputDecl,
        *,
        facts_ref: model.NameRef,
        guarded: tuple[model.RouteOnlyGuard, ...],
        owner_label: str,
    ) -> None:
        top_level_guards = {
            item.key: item
            for item in output_decl.items
            if isinstance(item, (model.GuardedOutputSection, model.GuardedOutputScalar))
        }
        for guard in guarded:
            output_guard = top_level_guards.get(guard.key)
            if output_guard is None:
                raise CompileError(
                    f"route_only guarded output item is missing from {output_decl.name} in {owner_label}: "
                    f"{guard.key}"
                )
            expected_expr = self._prefix_route_only_expr(guard.expr, facts_ref)
            if output_guard.when_expr != expected_expr:
                raise CompileError(
                    f"route_only guarded output item does not match output guard in {owner_label}: "
                    f"{guard.key}"
                )

    def _prefix_route_only_expr(
        self,
        expr: model.Expr,
        facts_ref: model.NameRef,
    ) -> model.Expr:
        facts_root = (*facts_ref.module_parts, facts_ref.declaration_name)
        if isinstance(expr, model.ExprRef):
            if len(expr.parts) == 1:
                return model.ExprRef(parts=(*facts_root, *expr.parts))
            return expr
        if isinstance(expr, model.ExprCall):
            return model.ExprCall(
                name=expr.name,
                args=tuple(self._prefix_route_only_expr(arg, facts_ref) for arg in expr.args),
            )
        if isinstance(expr, model.ExprSet):
            return model.ExprSet(
                items=tuple(self._prefix_route_only_expr(item, facts_ref) for item in expr.items)
            )
        if isinstance(expr, model.ExprBinary):
            return model.ExprBinary(
                op=expr.op,
                left=self._prefix_route_only_expr(expr.left, facts_ref),
                right=self._prefix_route_only_expr(expr.right, facts_ref),
            )
        return expr

    def _combine_exprs_with_and(
        self,
        exprs: tuple[model.Expr, ...],
    ) -> model.Expr | None:
        if not exprs:
            return None
        combined = exprs[0]
        for expr in exprs[1:]:
            combined = model.ExprBinary(op="and", left=combined, right=expr)
        return combined

    def _resolved_io_body_is_empty(self, io_body: ResolvedIoBody) -> bool:
        return not io_body.preamble and not io_body.items

    def _review_section_title(
        self,
        section: model.ReviewSection,
    ) -> str:
        return section.title or _humanize_key(section.key)

    def _resolved_review_subject_map(
        self,
        subject_map: model.ReviewSubjectMapConfig,
        *,
        unit: IndexedUnit,
        owner_label: str,
        subject_keys: set[tuple[tuple[str, ...], str]],
    ) -> dict[tuple[tuple[str, ...], str, str], tuple[tuple[str, ...], str]]:
        mapping: dict[tuple[tuple[str, ...], str, str], tuple[tuple[str, ...], str]] = {}
        for entry in subject_map.entries:
            entry_identity = self._resolve_enum_member_identity(
                model.ExprRef(
                    parts=(*entry.enum_member_ref.module_parts, entry.enum_member_ref.declaration_name)
                ),
                unit=unit,
            )
            if entry_identity is None:
                raise CompileError(
                    "Review subject_map entry must resolve to an enum member in "
                    f"{owner_label}: {_dotted_ref_name(entry.enum_member_ref)}"
                )
            if entry_identity in mapping:
                raise CompileError(
                    f"Duplicate review subject_map entry in {owner_label}: "
                    f"{_dotted_ref_name(entry.enum_member_ref)}"
                )

            subject_unit, subject_decl = self._resolve_review_subjects(
                model.ReviewSubjectConfig(subjects=(entry.artifact_ref,)),
                unit=unit,
                owner_label=f"{owner_label} subject_map",
            )[0]
            subject_key = (subject_unit.module_parts, subject_decl.name)
            if subject_key not in subject_keys:
                raise CompileError(
                    "Review subject_map target must be one of the declared review subjects in "
                    f"{owner_label}: {_dotted_ref_name(entry.artifact_ref)}"
                )
            mapping[entry_identity] = subject_key

        return mapping

    def _collect_review_contract_gates(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        owner_label: str,
    ) -> tuple[ReviewContractGate, ...]:
        if workflow_body.law is not None:
            raise CompileError(f"Review contract may not define workflow law in {owner_label}")

        gates: list[ReviewContractGate] = []
        seen: set[str] = set()
        for item in workflow_body.items:
            if isinstance(item, ResolvedWorkflowSkillsItem):
                raise CompileError(f"Review contract may not define skills in {owner_label}")
            if isinstance(item, ResolvedSectionItem):
                if item.key in seen:
                    raise CompileError(f"Duplicate review contract gate in {owner_label}: {item.key}")
                seen.add(item.key)
                gates.append(ReviewContractGate(key=item.key, title=item.title))
                continue
            nested = self._collect_review_contract_gates(
                self._resolve_workflow_decl(item.workflow_decl, unit=item.target_unit),
                owner_label=owner_label,
            )
            for gate in nested:
                if gate.key in seen:
                    raise CompileError(
                        f"Duplicate review contract gate in {owner_label}: {gate.key}"
                    )
                seen.add(gate.key)
                gates.append(gate)
        return tuple(gates)

    def _collect_schema_review_contract_gates(
        self,
        schema_body: ResolvedSchemaBody,
        *,
        owner_label: str,
    ) -> tuple[ReviewContractGate, ...]:
        gates: list[ReviewContractGate] = []
        seen: set[str] = set()
        for item in schema_body.gates:
            if item.key in seen:
                raise CompileError(
                    f"Duplicate review contract gate in {owner_label}: {item.key}"
                )
            seen.add(item.key)
            gates.append(ReviewContractGate(key=item.key, title=item.title))
        return tuple(gates)

    def _validate_review_field_bindings(
        self,
        fields: model.ReviewFieldsConfig,
        *,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        owner_label: str,
        require_blocked_gate: bool,
        require_active_mode: bool,
        require_trigger_reason: bool,
    ) -> dict[str, tuple[str, ...]]:
        bindings: dict[str, tuple[str, ...]] = {}
        for binding in fields.bindings:
            if binding.semantic_field in bindings:
                raise CompileError(
                    f"Duplicate review field binding in {owner_label}: {binding.semantic_field}"
                )
            self._resolve_output_field_node(
                output_decl,
                path=binding.field_path,
                unit=output_unit,
                owner_label=owner_label,
                surface_label="review field binding",
            )
            bindings[binding.semantic_field] = binding.field_path

        required = set(_REVIEW_REQUIRED_FIELD_NAMES)
        if require_blocked_gate:
            required.add("blocked_gate")
        if require_active_mode:
            required.add("active_mode")
        if require_trigger_reason:
            required.add("trigger_reason")
        missing = sorted(required - set(bindings))
        if missing:
            raise CompileError(
                f"Review fields are incomplete in {owner_label}: {', '.join(missing)}"
            )
        return bindings

    def _count_review_accept_stmts(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
    ) -> int:
        count = 0
        for item in items:
            if isinstance(item, model.ReviewAcceptStmt):
                count += 1
            elif isinstance(item, model.ReviewPreOutcomeWhenStmt):
                count += self._count_review_accept_stmts(item.items)
            elif isinstance(item, model.ReviewPreOutcomeMatchStmt):
                for case in item.cases:
                    count += self._count_review_accept_stmts(case.items)
        return count

    def _review_items_contain_blocks(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
    ) -> bool:
        for item in items:
            if isinstance(item, model.ReviewBlockStmt):
                return True
            if isinstance(item, model.ReviewPreOutcomeWhenStmt) and self._review_items_contain_blocks(
                item.items
            ):
                return True
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                for case in item.cases:
                    if self._review_items_contain_blocks(case.items):
                        return True
        return False

    def _collect_review_carried_fields(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
    ) -> tuple[str, ...]:
        fields: list[str] = []
        for item in items:
            if isinstance(item, model.ReviewCarryStmt):
                fields.append(item.field_name)
                continue
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                fields.extend(self._collect_review_carried_fields(item.items))
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                for case in item.cases:
                    fields.extend(self._collect_review_carried_fields(case.items))
        return tuple(fields)

    def _validate_review_pre_outcome_items(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        agent_contract: AgentContract,
    ) -> None:
        for item in items:
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                self._validate_review_pre_outcome_items(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    agent_contract=agent_contract,
                )
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                self._validate_review_match_cases(
                    item.cases,
                    unit=unit,
                    owner_label=owner_label,
                )
                for case in item.cases:
                    self._validate_review_pre_outcome_items(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                        agent_contract=agent_contract,
                    )
                continue
            if isinstance(item, (model.ReviewBlockStmt, model.ReviewRejectStmt, model.ReviewAcceptStmt)):
                self._validate_review_gate_label(
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    owner_label=owner_label,
                )
                continue
            if isinstance(item, model.OwnOnlyStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
                )
                continue
            if isinstance(item, (model.SupportOnlyStmt, model.IgnoreStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["path_set"],
                )
                continue
            if isinstance(item, model.PreserveStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=f"preserve {item.kind}",
                    allowed_kinds=_PRESERVE_TARGET_ALLOWED_KINDS[item.kind],
                )

    def _validate_review_gate_label(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
    ) -> None:
        if isinstance(gate, model.ContractGateRef):
            if gate.key not in {item.key for item in contract_spec.gates}:
                raise CompileError(
                    f"Unknown review contract gate in {owner_label}: contract.{gate.key}"
                )
            return
        if isinstance(gate, model.SectionGateRef) and gate.key not in section_titles:
            raise CompileError(f"Unknown review section gate in {owner_label}: {gate.key}")

    def _collect_review_pre_section_branches(
        self,
        section: model.ReviewSection,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        return self._collect_review_pre_outcome_leaf_branches(
            section.items,
            unit=unit,
            contract_spec=contract_spec,
            section_titles=section_titles,
            owner_label=owner_label,
        )

    def _collect_review_pre_outcome_leaf_branches(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        branch: ReviewPreSectionBranch | None = None,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        branches = (branch or ReviewPreSectionBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                next_branches: list[ReviewPreSectionBranch] = []
                for current_branch in branches:
                    condition = self._evaluate_review_condition(
                        item.expr,
                        unit=unit,
                        branch=ReviewOutcomeBranch(),
                    )
                    if condition is not False:
                        next_branches.extend(
                            self._collect_review_pre_outcome_leaf_branches(
                                item.items,
                                unit=unit,
                                contract_spec=contract_spec,
                                section_titles=section_titles,
                                owner_label=owner_label,
                                branch=current_branch,
                            )
                        )
                    if condition is not True:
                        next_branches.append(current_branch)
                branches = tuple(next_branches)
                index += 1
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                next_branches: list[ReviewPreSectionBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_review_pre_match_branches(
                            item,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
                index += 1
                continue

            next_branches = []
            for current_branch in branches:
                next_branches.append(
                    self._branch_with_review_pre_outcome_stmt(
                        current_branch,
                        item,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                    )
                )
            branches = tuple(next_branches)
            index += 1
        return branches

    def _collect_review_pre_match_branches(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        branch: ReviewPreSectionBranch,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        selected: list[ReviewPreSectionBranch] = []
        pending = [branch]
        empty_branch = ReviewOutcomeBranch()

        for case in stmt.cases:
            next_pending: list[ReviewPreSectionBranch] = []
            for current_branch in pending:
                if case.head is None:
                    selected.extend(
                        self._collect_review_pre_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                    continue
                condition = self._review_match_head_matches(
                    stmt.expr,
                    case.head,
                    unit=unit,
                    branch=empty_branch,
                )
                if condition is not False:
                    selected.extend(
                        self._collect_review_pre_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                if condition is not True:
                    next_pending.append(current_branch)
            pending = next_pending

        if pending and not self._review_pre_match_is_exhaustive(stmt, unit=unit):
            selected.extend(pending)
        return tuple(selected)

    def _review_pre_match_is_exhaustive(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
    ) -> bool:
        outcome_stmt = model.ReviewOutcomeMatchStmt(
            expr=stmt.expr,
            cases=tuple(
                model.ReviewOutcomeMatchArm(head=case.head, items=())
                for case in stmt.cases
            ),
        )
        return self._review_match_is_exhaustive(outcome_stmt, unit=unit)

    def _branch_with_review_pre_outcome_stmt(
        self,
        branch: ReviewPreSectionBranch,
        stmt: model.ReviewPreOutcomeStmt,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> ReviewPreSectionBranch:
        if isinstance(stmt, model.ReviewBlockStmt):
            return replace(
                branch,
                block_checks=(
                    *branch.block_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, model.ReviewRejectStmt):
            return replace(
                branch,
                reject_checks=(
                    *branch.reject_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, model.ReviewAcceptStmt):
            return replace(
                branch,
                accept_checks=(
                    *branch.accept_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, (model.PreserveStmt, model.SupportOnlyStmt, model.IgnoreStmt)):
            return replace(branch, has_assertions=True)
        return branch

    def _review_gate_observation_with_accept_checks(
        self,
        observation: ReviewGateObservation,
        *,
        accept_checks: tuple[ReviewGateCheck, ...],
    ) -> ReviewGateObservation:
        flags = {
            "needs_blocked_gate_presence": observation.needs_blocked_gate_presence,
            "needs_blocked_gate_value": observation.needs_blocked_gate_value,
            "needs_failing_gates_presence": observation.needs_failing_gates_presence,
            "needs_failing_gates_value": observation.needs_failing_gates_value,
            "needs_contract_failed_gates_value": observation.needs_contract_failed_gates_value,
            "needs_contract_first_failed_gate": observation.needs_contract_first_failed_gate,
            "needs_contract_passes": observation.needs_contract_passes,
        }
        referenced_contract_gate_ids = set(observation.referenced_contract_gate_ids)
        for check in accept_checks:
            self._collect_review_gate_observation_from_expr(
                check.expr,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
        return ReviewGateObservation(
            needs_blocked_gate_presence=flags["needs_blocked_gate_presence"],
            needs_blocked_gate_value=flags["needs_blocked_gate_value"],
            needs_failing_gates_presence=flags["needs_failing_gates_presence"],
            needs_failing_gates_value=flags["needs_failing_gates_value"],
            needs_contract_failed_gates_value=flags["needs_contract_failed_gates_value"],
            needs_contract_first_failed_gate=flags["needs_contract_first_failed_gate"],
            needs_contract_passes=flags["needs_contract_passes"],
            referenced_contract_gate_ids=tuple(sorted(referenced_contract_gate_ids)),
        )

    def _review_contract_failure_states(
        self,
        contract_spec: ReviewContractSpec,
        *,
        observation: ReviewGateObservation,
    ) -> tuple[tuple[str, ...], ...]:
        gate_ids = tuple(f"contract.{gate.key}" for gate in contract_spec.gates)
        if not gate_ids:
            return ((),)

        # Full failed-gates tuple observation is the one remaining surface that
        # genuinely needs every contract subset. Keep the exact behavior there.
        if observation.needs_contract_failed_gates_value:
            return self._enumerate_review_contract_failure_states(gate_ids)

        referenced = set(observation.referenced_contract_gate_ids)
        referenced_gate_ids = tuple(gate_id for gate_id in gate_ids if gate_id in referenced)
        unreferenced_gate_ids = tuple(gate_id for gate_id in gate_ids if gate_id not in referenced)

        states: list[tuple[str, ...]] = [()]
        seen = {()}

        def add(state: tuple[str, ...]) -> None:
            if state in seen:
                return
            seen.add(state)
            states.append(state)

        # For explicit failed()/passed() checks, enumerate only the referenced
        # gate subset, not the whole contract.
        for state in self._enumerate_review_contract_failure_states(referenced_gate_ids):
            if state:
                add(state)

        # Preserve generic "some other contract gate failed" behavior so
        # contract.passes and implicit full-contract failure still validate.
        if unreferenced_gate_ids:
            add((unreferenced_gate_ids[0],))

        # first_failed_gate needs one representative state per gate so callers
        # can distinguish which gate was first.
        if observation.needs_contract_first_failed_gate:
            for gate_id in gate_ids:
                add((gate_id,))

        # contract.passes needs at least one failing contract state.
        if observation.needs_contract_passes and len(states) == 1:
            add((gate_ids[0],))

        if len(states) == 1:
            add((gate_ids[0],))

        return tuple(states)

    def _enumerate_review_contract_failure_states(
        self,
        gate_ids: tuple[str, ...],
    ) -> tuple[tuple[str, ...], ...]:
        states: list[tuple[str, ...]] = [()]
        for gate_id in gate_ids:
            next_states: list[tuple[str, ...]] = []
            for state in states:
                next_states.append(state)
                next_states.append((*state, gate_id))
            states = next_states
        return tuple(states)

    def _evaluate_review_gate_condition(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> bool | None:
        return self._evaluate_review_gate_condition_with_branch(
            expr,
            unit=unit,
            branch=ReviewOutcomeBranch(),
            contract_failed_gate_ids=contract_failed_gate_ids,
        )

    def _evaluate_review_gate_condition_with_branch(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> bool | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._evaluate_review_gate_condition_with_branch(
                    expr.left,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                right = self._evaluate_review_gate_condition_with_branch(
                    expr.right,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if left is False or right is False:
                    return False
                if left is True and right is True:
                    return True
                return None
            if expr.op == "or":
                left = self._evaluate_review_gate_condition_with_branch(
                    expr.left,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                right = self._evaluate_review_gate_condition_with_branch(
                    expr.right,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if left is True or right is True:
                    return True
                if left is False and right is False:
                    return False
                return None

        left = self._resolve_review_gate_expr_constant(
            expr,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        if isinstance(left, bool):
            return left
        if not isinstance(expr, model.ExprBinary):
            return None
        left = self._resolve_review_gate_expr_constant(
            expr.left,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        right = self._resolve_review_gate_expr_constant(
            expr.right,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        if left is None or right is None:
            return None
        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        if expr.op == ">":
            return left > right
        if expr.op == ">=":
            return left >= right
        if expr.op == "<":
            return left < right
        if expr.op == "<=":
            return left <= right
        return None

    def _validate_review_match_cases(
        self,
        cases: tuple[model.ReviewPreOutcomeMatchArm | model.ReviewOutcomeMatchArm, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if any(case.head is None for case in cases):
            return

        enum_decl: model.EnumDecl | None = None
        seen_members: set[str] = set()
        for case in cases:
            if case.head is None:
                continue
            for option in case.head.options:
                resolved = self._resolve_review_match_option(option, unit=unit)
                if resolved is None:
                    return
                option_enum_decl, member_value = resolved
                if enum_decl is None:
                    enum_decl = option_enum_decl
                elif enum_decl.name != option_enum_decl.name:
                    return
                seen_members.add(member_value)

        if enum_decl is None:
            return

        expected_members = {member.value for member in enum_decl.members}
        if seen_members != expected_members:
            raise CompileError(
                f"Review match must be exhaustive or include else in {owner_label}"
            )

    def _compress_review_gate_branches_for_validation(
        self,
        gate_branches: tuple[ResolvedReviewGateBranch, ...],
        *,
        output_decl: model.OutputDecl,
        field_bindings: dict[str, tuple[str, ...]],
    ) -> tuple[ResolvedReviewGateBranch, ...]:
        observation = self._review_gate_observation(output_decl)
        deduped: dict[tuple[object, ...], ResolvedReviewGateBranch] = {}
        for branch in gate_branches:
            deduped.setdefault(
                self._review_gate_branch_validation_key(
                    branch,
                    observation=observation,
                    preserve_blocked_gate_presence="blocked_gate" in field_bindings,
                ),
                branch,
            )
        return tuple(deduped.values())

    def _review_gate_branch_validation_key(
        self,
        branch: ResolvedReviewGateBranch,
        *,
        observation: ReviewGateObservation,
        preserve_blocked_gate_presence: bool = False,
    ) -> tuple[object, ...]:
        contract_failed_gate_ids = tuple(
            gate_id for gate_id in branch.failing_gate_ids if gate_id.startswith("contract.")
        )
        key: list[object] = [branch.verdict]

        if observation.needs_failing_gates_value:
            key.append(branch.failing_gate_ids)
        elif observation.needs_failing_gates_presence:
            key.append(bool(branch.failing_gate_ids))

        if observation.needs_blocked_gate_value:
            key.append(branch.blocked_gate_id)
        elif observation.needs_blocked_gate_presence:
            key.append(branch.blocked_gate_id is not None)
        elif preserve_blocked_gate_presence:
            key.append(branch.blocked_gate_id is not None)

        if observation.needs_contract_failed_gates_value:
            key.append(contract_failed_gate_ids)
        elif observation.needs_contract_first_failed_gate:
            key.append(contract_failed_gate_ids[0] if contract_failed_gate_ids else None)
        elif observation.needs_contract_passes:
            key.append(not contract_failed_gate_ids)

        if observation.referenced_contract_gate_ids:
            key.append(
                tuple(
                    gate_id in contract_failed_gate_ids
                    for gate_id in observation.referenced_contract_gate_ids
                )
            )

        return tuple(key)

    def _review_gate_observation(self, output_decl: model.OutputDecl) -> ReviewGateObservation:
        flags = {
            "needs_blocked_gate_presence": False,
            "needs_blocked_gate_value": False,
            "needs_failing_gates_presence": False,
            "needs_failing_gates_value": False,
            "needs_contract_failed_gates_value": False,
            "needs_contract_first_failed_gate": False,
            "needs_contract_passes": False,
        }
        referenced_contract_gate_ids: set[str] = set()

        self._collect_review_gate_observation_from_output_items(
            output_decl.items,
            flags=flags,
            referenced_contract_gate_ids=referenced_contract_gate_ids,
        )
        for item in output_decl.trust_surface:
            if item.when_expr is None:
                continue
            self._collect_review_gate_observation_from_expr(
                item.when_expr,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )

        return ReviewGateObservation(
            needs_blocked_gate_presence=flags["needs_blocked_gate_presence"],
            needs_blocked_gate_value=flags["needs_blocked_gate_value"],
            needs_failing_gates_presence=flags["needs_failing_gates_presence"],
            needs_failing_gates_value=flags["needs_failing_gates_value"],
            needs_contract_failed_gates_value=flags["needs_contract_failed_gates_value"],
            needs_contract_first_failed_gate=flags["needs_contract_first_failed_gate"],
            needs_contract_passes=flags["needs_contract_passes"],
            referenced_contract_gate_ids=tuple(sorted(referenced_contract_gate_ids)),
        )

    def _collect_review_gate_observation_from_output_items(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        flags: dict[str, bool],
        referenced_contract_gate_ids: set[str],
    ) -> None:
        for item in items:
            if isinstance(item, (model.GuardedOutputSection, model.GuardedOutputScalar)):
                self._collect_review_gate_observation_from_expr(
                    item.when_expr,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
                nested_items = item.items if isinstance(item, model.GuardedOutputSection) else item.body
                if nested_items is not None:
                    self._collect_review_gate_observation_from_output_items(
                        nested_items,
                        flags=flags,
                        referenced_contract_gate_ids=referenced_contract_gate_ids,
                    )
                continue
            if isinstance(item, model.RecordSection):
                self._collect_review_gate_observation_from_output_items(
                    item.items,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
                continue
            if isinstance(item, model.RecordScalar) and item.body is not None:
                self._collect_review_gate_observation_from_output_items(
                    item.body,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )

    def _collect_review_gate_observation_from_expr(
        self,
        expr: model.Expr,
        *,
        flags: dict[str, bool],
        referenced_contract_gate_ids: set[str],
    ) -> None:
        if isinstance(expr, model.ExprBinary):
            self._collect_review_gate_observation_from_expr(
                expr.left,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
            self._collect_review_gate_observation_from_expr(
                expr.right,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
            return

        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._collect_review_gate_observation_from_expr(
                    item,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
            return

        if isinstance(expr, model.ExprCall):
            if expr.name in {"present", "missing"} and len(expr.args) == 1:
                field_name = (
                    self._review_semantic_field_ref_name(expr.args[0])
                    if isinstance(expr.args[0], model.ExprRef)
                    else None
                )
                if field_name == "blocked_gate":
                    flags["needs_blocked_gate_presence"] = True
                elif field_name == "failing_gates":
                    flags["needs_failing_gates_presence"] = True
                return
            if expr.name in {"failed", "passed"} and len(expr.args) == 1:
                gate_identity = self._resolve_review_contract_gate_identity(expr.args[0])
                if gate_identity is not None:
                    referenced_contract_gate_ids.add(gate_identity)
            for arg in expr.args:
                self._collect_review_gate_observation_from_expr(
                    arg,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
            return

        if isinstance(expr, model.ExprRef):
            field_name = self._review_semantic_field_ref_name(expr)
            if field_name == "blocked_gate":
                flags["needs_blocked_gate_value"] = True
                return
            if field_name == "failing_gates":
                flags["needs_failing_gates_value"] = True
                return
            if len(expr.parts) == 2 and expr.parts[0] == "contract":
                if expr.parts[1] == "failed_gates":
                    flags["needs_contract_failed_gates_value"] = True
                elif expr.parts[1] == "first_failed_gate":
                    flags["needs_contract_first_failed_gate"] = True
                elif expr.parts[1] == "passes":
                    flags["needs_contract_passes"] = True

    def _validate_review_outcome_section(
        self,
        section: model.ReviewOutcomeSection,
        *,
        unit: IndexedUnit,
        owner_label: str,
        agent_contract: AgentContract,
        comment_output_decl: model.OutputDecl,
        comment_output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        blocked_gate_required: bool,
        gate_branches: tuple[ResolvedReviewGateBranch, ...],
    ) -> tuple[ResolvedReviewAgreementBranch, ...]:
        self._validate_review_outcome_items(
            section.items,
            unit=unit,
            owner_label=f"{owner_label}.{section.key}",
        )
        gate_branches = self._compress_review_gate_branches_for_validation(
            gate_branches,
            output_decl=comment_output_decl,
            field_bindings=field_bindings,
        )
        branches = self._collect_review_outcome_leaf_branches(section.items, unit=unit)
        if not branches:
            raise CompileError(f"Review outcome is not total in {owner_label}: {section.key}")

        resolved_branches: list[ResolvedReviewAgreementBranch] = []
        for branch in branches:
            if not branch.currents or not branch.routes:
                raise CompileError(
                    f"Review outcome is not total in {owner_label}: {section.key}"
                )
            if len(branch.routes) > 1:
                raise CompileError(
                    f"Review outcome resolves more than one route in {owner_label}: {section.key}"
                )
            if len(branch.currents) > 1:
                raise CompileError(
                    f"Review outcome resolves more than one currentness result in {owner_label}: {section.key}"
                )

            for gate_branch in gate_branches:
                if (
                    branch.blocked_gate_present is not None
                    and branch.blocked_gate_present != (gate_branch.blocked_gate_id is not None)
                ):
                    continue
                resolved_branch = self._resolve_review_agreement_branch(
                    branch,
                    section_key=section.key,
                    unit=unit,
                    owner_label=f"{owner_label}.{section.key}",
                    agent_contract=agent_contract,
                    comment_output_decl=comment_output_decl,
                    comment_output_unit=comment_output_unit,
                    field_bindings=field_bindings,
                    subject_keys=subject_keys,
                    subject_map=subject_map,
                    blocked_gate_required=blocked_gate_required,
                    gate_branch=gate_branch,
                )

                branch_proves_subject = self._review_branch_proves_subject(
                    branch,
                    unit=unit,
                    subject_keys=subject_keys,
                    subject_map=subject_map,
                    current_subject_key=resolved_branch.current_subject_key,
                    reviewed_subject_key=resolved_branch.reviewed_subject_key,
                    owner_label=f"{owner_label}.{section.key}",
                )
                blocked_before_subject_review = (
                    (
                        resolved_branch.blocked_gate_id is not None
                        or (section.key == "on_reject" and blocked_gate_required)
                    )
                    and isinstance(resolved_branch.current, model.ReviewCurrentNoneStmt)
                )
                if len(subject_keys) > 1 and not branch_proves_subject and not blocked_before_subject_review:
                    raise CompileError(
                        f"Review subject set requires disambiguation in {owner_label}: {section.key}"
                    )

                self._validate_review_output_agreement_branch(
                    resolved_branch,
                    unit=unit,
                    output_decl=comment_output_decl,
                    output_unit=comment_output_unit,
                    next_owner_field_path=next_owner_field_path,
                    field_bindings=field_bindings,
                    owner_label=f"{owner_label}.{section.key}",
                )
                resolved_branches.append(resolved_branch)

        return tuple(resolved_branches)

    def _review_subject_key_from_subject_map(
        self,
        branch: ReviewOutcomeBranch,
        *,
        unit: IndexedUnit,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        active_mode = next((carry for carry in branch.carries if carry.field_name == "active_mode"), None)
        if active_mode is None:
            return None
        active_mode_identity = self._resolve_enum_member_identity(active_mode.expr, unit=unit)
        if active_mode_identity is None:
            return None
        mapping = self._resolved_review_subject_map(
            subject_map,
            unit=unit,
            owner_label=owner_label,
            subject_keys=subject_keys,
        )
        return mapping.get(active_mode_identity)

    def _record_item_subject_keys(
        self,
        item: AddressableTarget,
        *,
        subject_keys: set[tuple[tuple[str, ...], str]],
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[tuple[str, ...], str], ...]:
        referenced: list[tuple[tuple[str, ...], str]] = []
        seen: set[tuple[tuple[str, ...], str]] = set()

        def add_subject_key(key: tuple[tuple[str, ...], str] | None) -> None:
            if key is None or key not in subject_keys or key in seen:
                return
            seen.add(key)
            referenced.append(key)

        if isinstance(item, model.RecordScalar):
            if isinstance(item.value, model.NameRef):
                add_subject_key(
                    self._review_subject_key_from_name_ref(
                        item.value,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
            elif isinstance(item.value, model.AddressableRef):
                add_subject_key(
                    self._review_subject_key_from_addressable_ref(
                        item.value,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
        for ref in self._iter_record_item_interpolation_refs(item):
            add_subject_key(
                self._review_subject_key_from_addressable_ref(
                    ref,
                    unit=unit,
                    owner_label=owner_label,
                )
            )
        return tuple(referenced)

    def _review_subject_key_from_name_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        try:
            target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        input_decl = target_unit.inputs_by_name.get(ref.declaration_name)
        output_decl = target_unit.outputs_by_name.get(ref.declaration_name)
        if input_decl is None and output_decl is None:
            return None
        if input_decl is not None and output_decl is not None:
            _ = owner_label
            return None
        decl = input_decl if input_decl is not None else output_decl
        return (target_unit.module_parts, decl.name)

    def _review_subject_key_from_addressable_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        try:
            root_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="reviewed_artifact interpolation ref",
                missing_local_label="reviewed_artifact",
            )
        except CompileError:
            return None
        if not isinstance(root_decl, (model.InputDecl, model.OutputDecl)):
            return None
        if ref.path and ref.path not in {("name",), ("title",)}:
            return None
        return (root_unit.module_parts, root_decl.name)

    def _validate_review_output_agreement_branch(
        self,
        branch: ResolvedReviewAgreementBranch,
        *,
        unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        next_owner_field_path: tuple[str, ...],
        field_bindings: dict[str, tuple[str, ...]],
        owner_label: str,
    ) -> None:
        verdict_path = field_bindings["verdict"]
        if not self._review_output_path_is_live(
            output_decl,
            path=verdict_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review verdict field is not live for semantic verdict in "
                f"{owner_label}: {output_decl.name}.{'.'.join(verdict_path)}"
            )

        if not self._review_output_path_is_live(
            output_decl,
            path=next_owner_field_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review next_owner field is not live for routed target in "
                f"{owner_label}: {output_decl.name}.{'.'.join(next_owner_field_path)} -> "
                f"{branch.route.target.declaration_name}"
            )
        self._validate_review_next_owner_binding(
            branch.route,
            review_unit=unit,
            output_decl=output_decl,
            output_unit=output_unit,
            field_path=next_owner_field_path,
            owner_label=owner_label,
        )

        if isinstance(branch.current, model.ReviewCurrentArtifactStmt):
            if branch.current_carrier_path is None:
                raise CompileError(
                    f"Internal compiler error: missing review current carrier path in {owner_label}"
                )
            if not self._review_output_path_is_live(
                output_decl,
                path=branch.current_carrier_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review current artifact carrier field is not live for semantic currentness in "
                    f"{owner_label}: {output_decl.name}.{'.'.join(branch.current_carrier_path)}"
                )

        for carry in branch.carries:
            bound_path = field_bindings[carry.field_name]
            if not self._review_output_path_is_live(
                output_decl,
                path=bound_path,
                unit=output_unit,
                branch=branch,
            ) or not self._review_trust_surface_path_is_live(
                output_decl,
                path=bound_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review carried field is not live when semantic value exists in "
                    f"{owner_label}: {carry.field_name} -> {output_decl.name}.{'.'.join(bound_path)}"
                )

        failing_gates_path = field_bindings["failing_gates"]
        if branch.requires_failure_detail:
            if not self._review_output_path_has_matching_failure_guard(
                output_decl,
                path=failing_gates_path,
                unit=output_unit,
                branch=branch,
            ):
                raise CompileError(
                    "Review conditional output field is not aligned with resolved review semantics "
                    f"in {owner_label}: failing_gates -> {output_decl.name}.{'.'.join(failing_gates_path)}"
                )
            if branch.blocked_gate_id is not None:
                blocked_gate_path = field_bindings["blocked_gate"]
                if not self._review_output_path_has_matching_failure_guard(
                    output_decl,
                    path=blocked_gate_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    raise CompileError(
                        "Review conditional output field is not aligned with resolved review semantics "
                        f"in {owner_label}: blocked_gate -> {output_decl.name}.{'.'.join(blocked_gate_path)}"
                    )
        elif self._review_output_path_is_live(
            output_decl,
            path=failing_gates_path,
            unit=output_unit,
            branch=branch,
        ):
            raise CompileError(
                "Review conditional output field is not aligned with resolved review semantics "
                f"in {owner_label}: failing_gates -> {output_decl.name}.{'.'.join(failing_gates_path)}"
            )

    def _validate_review_current_artifact_alignment(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        carrier_paths = tuple(
            dict.fromkeys(
                branch.current_carrier_path
                for branch in branches
                if (
                    isinstance(branch.current, model.ReviewCurrentArtifactStmt)
                    and branch.current_carrier_path is not None
                )
            )
        )
        if not carrier_paths:
            return

        for branch in branches:
            if not isinstance(branch.current, model.ReviewCurrentNoneStmt):
                continue
            for carrier_path in carrier_paths:
                if not self._review_output_path_is_live(
                    output_decl,
                    path=carrier_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    continue
                raise CompileError(
                    "Review current artifact carrier field stays live without semantic currentness in "
                    f"{owner_label}.{branch.section_key}: {output_decl.name}.{'.'.join(carrier_path)}"
                )

    def _validate_review_optional_field_alignment(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        owner_label: str,
    ) -> None:
        for field_name in _REVIEW_OPTIONAL_FIELD_NAMES:
            bound_path = field_bindings.get(field_name)
            if bound_path is None:
                continue
            for branch in branches:
                field_present = (
                    branch.blocked_gate_id is not None
                    if field_name == "blocked_gate"
                    else any(carry.field_name == field_name for carry in branch.carries)
                )
                if field_present:
                    continue
                if not self._review_output_path_is_live(
                    output_decl,
                    path=bound_path,
                    unit=output_unit,
                    branch=branch,
                ):
                    continue
                raise CompileError(
                    "Review conditional output field is not aligned with resolved review semantics "
                    f"in {owner_label}.{branch.section_key}: {field_name} -> "
                    f"{output_decl.name}.{'.'.join(bound_path)}"
                )

    def _review_output_path_is_live(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        status, _has_guards = self._review_output_path_guard_status(
            output_decl,
            path=path,
            unit=unit,
            branch=branch,
        )
        return status is True

    def _review_output_path_has_matching_failure_guard(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        status, has_guards = self._review_output_path_guard_status(
            output_decl,
            path=path,
            unit=unit,
            branch=branch,
        )
        return has_guards and status is True

    def _review_trust_surface_path_is_live(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool:
        statuses: list[bool | None] = []
        for item in output_decl.trust_surface:
            if item.path != path:
                continue
            if item.when_expr is None:
                return True
            statuses.append(
                self._evaluate_review_semantic_guard(
                    item.when_expr,
                    unit=unit,
                    branch=branch,
                )
            )
        if not statuses:
            return False
        if any(status is True for status in statuses):
            return True
        return False

    def _review_output_path_guard_status(
        self,
        output_decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> tuple[bool | None, bool]:
        guards = self._output_path_guards(output_decl.items, path=path)
        if not guards:
            return True, False
        seen_unknown = False
        for guard in guards:
            status = self._evaluate_review_semantic_guard(
                guard,
                unit=unit,
                branch=branch,
            )
            if status is False:
                return False, True
            if status is None:
                seen_unknown = True
        return (None if seen_unknown else True), True

    def _output_path_guards(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        path: tuple[str, ...],
    ) -> tuple[model.Expr, ...]:
        guards: list[model.Expr] = []
        current_items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...] = items
        for segment in path:
            matched_item: model.AnyRecordItem | None = None
            for item in current_items:
                if isinstance(
                    item,
                    (
                        model.RecordSection,
                        model.GuardedOutputSection,
                        model.GuardedOutputScalar,
                        model.RecordScalar,
                    ),
                ):
                    if item.key == segment:
                        matched_item = item
                        break
            if matched_item is None:
                break
            if isinstance(matched_item, model.GuardedOutputSection):
                guards.append(matched_item.when_expr)
                current_items = matched_item.items
                continue
            if isinstance(matched_item, model.GuardedOutputScalar):
                guards.append(matched_item.when_expr)
                current_items = matched_item.body or ()
                continue
            if isinstance(matched_item, model.RecordSection):
                current_items = matched_item.items
                continue
            if isinstance(matched_item, model.RecordScalar) and matched_item.body is not None:
                current_items = matched_item.body
                continue
            current_items = ()
        return tuple(guards)

    def _evaluate_review_semantic_guard(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._evaluate_review_semantic_guard(expr.left, unit=unit, branch=branch)
                right = self._evaluate_review_semantic_guard(expr.right, unit=unit, branch=branch)
                if left is False or right is False:
                    return False
                if left is True and right is True:
                    return True
                return None
            if expr.op == "or":
                left = self._evaluate_review_semantic_guard(expr.left, unit=unit, branch=branch)
                right = self._evaluate_review_semantic_guard(expr.right, unit=unit, branch=branch)
                if left is True or right is True:
                    return True
                if left is False and right is False:
                    return False
                return None

        if not isinstance(expr, model.ExprBinary):
            constant = self._resolve_review_semantic_expr_constant(expr, unit=unit, branch=branch)
            if isinstance(constant, bool):
                return constant
            return None

        left = self._resolve_review_semantic_expr_constant(expr.left, unit=unit, branch=branch)
        right = self._resolve_review_semantic_expr_constant(expr.right, unit=unit, branch=branch)
        if left is None or right is None:
            return None
        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        return None

    def _review_semantic_field_present(
        self,
        field_name: str,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> bool | None:
        if field_name == "current_artifact":
            return isinstance(branch.current, model.ReviewCurrentArtifactStmt)
        if field_name == "blocked_gate":
            return branch.blocked_gate_id is not None
        return self._review_semantic_ref_value(
            field_name,
            unit=unit,
            branch=branch,
        ) is not None

    def _review_semantic_field_ref_name(self, ref: model.ExprRef) -> str | None:
        if len(ref.parts) == 1:
            return ref.parts[0]
        if len(ref.parts) == 2 and ref.parts[0] == "fields":
            return ref.parts[1]
        return None

    def _review_semantic_ref_value(
        self,
        field_name: str,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> str | None:
        if field_name == "verdict":
            return branch.verdict
        if field_name == "next_owner":
            return branch.route.target.declaration_name
        if field_name == "current_artifact":
            if branch.current_subject_key is None:
                return None
            module_parts, decl_name = branch.current_subject_key
            return _dotted_decl_name(module_parts, decl_name)
        if field_name == "reviewed_artifact":
            if branch.reviewed_subject_key is None:
                return None
            module_parts, decl_name = branch.reviewed_subject_key
            return _dotted_decl_name(module_parts, decl_name)
        if field_name == "failing_gates":
            return ",".join(branch.failing_gate_ids) if branch.failing_gate_ids else None
        if field_name == "blocked_gate":
            return branch.blocked_gate_id
        for carry in reversed(branch.carries):
            if carry.field_name == field_name:
                if isinstance(carry.expr, model.ExprRef):
                    return self._resolve_constant_enum_member(carry.expr, unit=unit) or ".".join(carry.expr.parts)
                resolved = self._resolve_constant_enum_member(carry.expr, unit=unit)
                if resolved is not None:
                    return resolved
                if isinstance(carry.expr, str):
                    return carry.expr
        return None

    def _validate_review_outcome_items(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        for item in items:
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                self._validate_review_outcome_items(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                )
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                self._validate_review_match_cases(
                    item.cases,
                    unit=unit,
                    owner_label=owner_label,
                )
                for case in item.cases:
                    self._validate_review_outcome_items(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                    )
                continue
            if isinstance(item, model.ReviewOutcomeRouteStmt):
                self._validate_route_target(item.target, unit=unit)

    def _collect_review_outcome_leaf_branches(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch | None = None,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        branches = (branch or ReviewOutcomeBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                next_branches: list[ReviewOutcomeBranch] = []
                for current_branch in branches:
                    condition = self._evaluate_review_condition(
                        item.expr,
                        unit=unit,
                        branch=current_branch,
                    )
                    if condition is not False:
                        next_branches.extend(
                            self._collect_review_outcome_leaf_branches(
                                item.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                    if condition is not True:
                        next_branches.append(current_branch)
                branches = tuple(next_branches)
            elif isinstance(item, model.ReviewOutcomeMatchStmt):
                next_branches: list[ReviewOutcomeBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_review_outcome_match_branches(
                            item,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
            else:
                next_branches = []
                for current_branch in branches:
                    next_branches.extend(
                        self._branch_with_review_outcome_stmt(
                            current_branch,
                            item,
                            unit=unit,
                        )
                    )
                branches = tuple(next_branches)
            index += 1
        return branches

    def _branch_with_review_outcome_stmt(
        self,
        branch: ReviewOutcomeBranch,
        stmt: model.ReviewOutcomeStmt,
        *,
        unit: IndexedUnit,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        if isinstance(stmt, (model.ReviewCurrentArtifactStmt, model.ReviewCurrentNoneStmt)):
            if stmt.when_expr is None:
                return (replace(branch, currents=(*branch.currents, stmt)),)
            condition = self._evaluate_review_condition(
                stmt.when_expr,
                unit=unit,
                branch=branch,
            )
            if condition is True:
                return (replace(branch, currents=(*branch.currents, stmt)),)
            if condition is False:
                return (branch,)
            true_branch = self._assume_review_outcome_condition(
                branch,
                stmt.when_expr,
                expected=True,
            )
            false_branch = self._assume_review_outcome_condition(
                branch,
                stmt.when_expr,
                expected=False,
            )
            branches: list[ReviewOutcomeBranch] = []
            if true_branch is not None:
                branches.append(replace(true_branch, currents=(*true_branch.currents, stmt)))
            if false_branch is not None:
                branches.append(false_branch)
            if branches:
                return tuple(branches)
            return (
                replace(branch, currents=(*branch.currents, stmt)),
                branch,
            )
        if isinstance(stmt, model.ReviewCarryStmt):
            return (replace(branch, carries=(*branch.carries, stmt)),)
        if isinstance(stmt, model.ReviewOutcomeRouteStmt):
            if branch.route_selected:
                return (branch,)
            if stmt.when_expr is None:
                return (
                    replace(
                        branch,
                        routes=(*branch.routes, stmt),
                        route_selected=True,
                    ),
                )
            condition = self._evaluate_review_condition(
                stmt.when_expr,
                unit=unit,
                branch=branch,
            )
            if condition is True:
                return (
                    replace(
                        branch,
                        routes=(*branch.routes, stmt),
                        route_selected=True,
                    ),
                )
            if condition is False:
                return (branch,)
            return (
                replace(
                    branch,
                    routes=(*branch.routes, stmt),
                    route_selected=True,
                ),
                branch,
            )
        return (branch,)

    def _assume_review_outcome_condition(
        self,
        branch: ReviewOutcomeBranch,
        expr: model.Expr,
        *,
        expected: bool,
    ) -> ReviewOutcomeBranch | None:
        if (
            isinstance(expr, model.ExprCall)
            and expr.name in {"present", "missing"}
            and len(expr.args) == 1
            and isinstance(expr.args[0], model.ExprRef)
            and expr.args[0].parts == ("blocked_gate",)
        ):
            blocked_gate_present = expected if expr.name == "present" else not expected
            if (
                branch.blocked_gate_present is not None
                and branch.blocked_gate_present != blocked_gate_present
            ):
                return None
            return replace(branch, blocked_gate_present=blocked_gate_present)
        return None

    def _collect_review_outcome_match_branches(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        selected: list[ReviewOutcomeBranch] = []
        pending = [branch]

        for case in stmt.cases:
            next_pending: list[ReviewOutcomeBranch] = []
            for current_branch in pending:
                if case.head is None:
                    selected.extend(
                        self._collect_review_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                    continue

                condition = self._review_match_head_matches(
                    stmt.expr,
                    case.head,
                    unit=unit,
                    branch=current_branch,
                )
                if condition is not False:
                    selected.extend(
                        self._collect_review_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                if condition is not True:
                    next_pending.append(current_branch)
            pending = next_pending

        if pending and not self._review_match_is_exhaustive(stmt, unit=unit):
            selected.extend(pending)
        return tuple(selected)

    def _review_match_head_matches(
        self,
        expr: model.Expr,
        head: model.ReviewMatchHead,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> bool | None:
        subject_value = self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        matched = False
        saw_unknown_option = False
        if subject_value is None:
            option_result: bool | None = None
        else:
            option_result = False
            for option in head.options:
                option_value = self._resolve_review_expr_constant(option, unit=unit, branch=branch)
                if option_value is None:
                    saw_unknown_option = True
                    continue
                if subject_value == option_value:
                    matched = True
                    option_result = True
                    break
            if not matched and saw_unknown_option:
                option_result = None
        if option_result is False:
            return False
        if head.when_expr is None:
            return option_result
        guard_result = self._evaluate_review_condition(
            head.when_expr,
            unit=unit,
            branch=branch,
        )
        return self._combine_review_condition(option_result, guard_result)

    def _review_match_is_exhaustive(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
    ) -> bool:
        if any(case.head is None for case in stmt.cases):
            return True

        enum_decl: model.EnumDecl | None = None
        seen_members: set[str] = set()
        for case in stmt.cases:
            if case.head is None or case.head.when_expr is not None:
                return False
            for option in case.head.options:
                resolved = self._resolve_review_match_option(option, unit=unit)
                if resolved is None:
                    return False
                option_enum_decl, member_value = resolved
                if enum_decl is None:
                    enum_decl = option_enum_decl
                elif enum_decl.name != option_enum_decl.name:
                    return False
                seen_members.add(member_value)

        if enum_decl is None:
            return False
        return seen_members == {member.value for member in enum_decl.members}

    def _evaluate_review_condition(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> bool | None:
        constant = self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        if isinstance(constant, bool):
            return constant
        if not isinstance(expr, model.ExprBinary):
            return None

        if expr.op == "and":
            left = self._evaluate_review_condition(expr.left, unit=unit, branch=branch)
            right = self._evaluate_review_condition(expr.right, unit=unit, branch=branch)
            if left is False or right is False:
                return False
            if left is True and right is True:
                return True
            return None
        if expr.op == "or":
            left = self._evaluate_review_condition(expr.left, unit=unit, branch=branch)
            right = self._evaluate_review_condition(expr.right, unit=unit, branch=branch)
            if left is True or right is True:
                return True
            if left is False and right is False:
                return False
            return None

        left = self._resolve_review_expr_constant(expr.left, unit=unit, branch=branch)
        right = self._resolve_review_expr_constant(expr.right, unit=unit, branch=branch)
        if left is None or right is None:
            return None

        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        if expr.op == ">":
            return left > right
        if expr.op == ">=":
            return left >= right
        if expr.op == "<":
            return left < right
        if expr.op == "<=":
            return left <= right
        return None

    def _combine_review_condition(
        self,
        left: bool | None,
        right: bool | None,
    ) -> bool | None:
        if left is False or right is False:
            return False
        if left is True and right is True:
            return True
        return None

    def _review_membership_contains(
        self,
        container: str | int | bool | tuple[str | int | bool, ...],
        value: str | int | bool,
    ) -> bool:
        if isinstance(container, tuple):
            return value in container
        return value == container

    def _review_branch_proves_subject(
        self,
        branch: ReviewOutcomeBranch,
        *,
        unit: IndexedUnit,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        current_subject_key: tuple[tuple[str, ...], str] | None,
        reviewed_subject_key: tuple[tuple[str, ...], str] | None,
        owner_label: str,
    ) -> bool:
        if current_subject_key is not None and current_subject_key in subject_keys:
            return True
        if reviewed_subject_key is not None and reviewed_subject_key in subject_keys:
            return True
        if subject_map is None:
            return False
        return (
            self._review_subject_key_from_subject_map(
                branch,
                unit=unit,
                subject_keys=subject_keys,
                subject_map=subject_map,
                owner_label=owner_label,
            )
            in subject_keys
        )

    def _validate_review_next_owner_binding(
        self,
        route: model.ReviewOutcomeRouteStmt,
        *,
        review_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_path: tuple[str, ...],
        owner_label: str,
    ) -> None:
        field_node = self._resolve_output_field_node(
            output_decl,
            path=field_path,
            unit=output_unit,
            owner_label=owner_label,
            surface_label="review next_owner binding",
        )
        target = field_node.target
        if not isinstance(
            target,
            (
                model.RecordScalar,
                model.RecordSection,
                model.GuardedOutputSection,
                model.GuardedOutputScalar,
            ),
        ):
            raise CompileError(
                f"Review next_owner binding must point at an output field in {owner_label}: "
                f"{output_decl.name}.{'.'.join(field_path)}"
            )
        route_branch = self._route_semantic_branch_from_route(
            route.target,
            label=route.label,
            unit=review_unit,
        )
        self._validate_route_owner_alignment(
            target,
            route_branch=route_branch,
            unit=output_unit,
            fallback_unit=(
                review_unit if review_unit.module_parts != output_unit.module_parts else None
            ),
            owner_label=f"output {output_decl.name}.{'.'.join(field_path)}",
            error_message=(
                f"Review next_owner field must structurally bind the routed target in {owner_label}: "
                f"{output_decl.name}.{'.'.join(field_path)} -> {route_branch.target_name}"
            ),
        )

    def _review_gate_sentence(
        self,
        prefix: str,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        gate_text = self._review_gate_text(
            gate,
            contract_spec=contract_spec,
            section_titles=section_titles,
        )
        gate_text = gate_text.rstrip(".")
        if prefix.endswith("if"):
            return f"{prefix} {gate_text}."
        return f"{prefix}: {gate_text}."

    def _review_gate_text(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        if isinstance(gate, str):
            return gate
        if isinstance(gate, model.ContractGateRef):
            for item in contract_spec.gates:
                if item.key == gate.key:
                    return item.title
            return f"contract.{gate.key}"
        return section_titles.get(gate.key, gate.key)

    def _review_gate_identity(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> str:
        if isinstance(gate, str):
            return gate
        if isinstance(gate, model.ContractGateRef):
            _ = contract_spec
            return f"contract.{gate.key}"
        _ = section_titles
        return gate.key

    def _validate_output_guard_sections(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        self._validate_output_record_items(
            decl.items,
            decl=decl,
            unit=unit,
            owner_label=f"output {decl.name}",
            allow_review_semantics=allow_review_semantics,
            allow_route_semantics=allow_route_semantics,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )
        for item in decl.trust_surface:
            if item.when_expr is None:
                continue
            self._validate_output_guard_expr(
                item.when_expr,
                decl=decl,
                unit=unit,
                owner_label=f"output {decl.name}.trust_surface",
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
        self._validate_standalone_read_guard_contract(
            decl,
            unit=unit,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )

    def _validate_output_record_items(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        for item in items:
            if isinstance(item, (model.GuardedOutputSection, model.GuardedOutputScalar)):
                guarded_route_semantics = self._narrow_route_semantics(
                    route_semantics,
                    item.when_expr,
                    unit=unit,
                )
                self._validate_output_guard_expr(
                    item.when_expr,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
                nested_items = item.items if isinstance(item, model.GuardedOutputSection) else item.body
                if nested_items is not None:
                    self._validate_output_record_items(
                        nested_items,
                        decl=decl,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        allow_review_semantics=allow_review_semantics,
                        allow_route_semantics=allow_route_semantics,
                        review_semantics=review_semantics,
                        route_semantics=guarded_route_semantics,
                    )
                continue
            if isinstance(item, model.RecordSection):
                self._validate_output_record_items(
                    item.items,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
                continue
            if isinstance(item, model.RecordScalar) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
                continue
            if isinstance(item, model.RecordRef) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )

    def _validate_output_guard_expr(
        self,
        expr: model.Expr,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        if isinstance(expr, model.ExprRef):
            self._validate_output_guard_ref(
                expr,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            return
        if isinstance(expr, model.ExprBinary):
            self._validate_output_guard_expr(
                expr.left,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            self._validate_output_guard_expr(
                expr.right,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            return
        if isinstance(expr, model.ExprCall):
            for arg in expr.args:
                self._validate_output_guard_expr(
                    arg,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
            return
        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._validate_output_guard_expr(
                    item,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )

    def _validate_output_guard_ref(
        self,
        ref: model.ExprRef,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        if self._output_guard_ref_allowed(
            ref,
            unit=unit,
            allow_review_semantics=allow_review_semantics,
            allow_route_semantics=allow_route_semantics,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        ):
            return
        raise CompileError(
            f"Output guard reads disallowed source in {owner_label}: {'.'.join(ref.parts)}"
        )

    def _output_guard_ref_allowed(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        return (
            self._expr_ref_matches_input_decl(ref, unit=unit)
            or self._expr_ref_matches_enum_member(ref, unit=unit)
            or (
                allow_route_semantics
                and self._expr_ref_matches_route_semantic_ref(
                    ref,
                    route_semantics=route_semantics,
                )
            )
            or (
                allow_review_semantics
                and (
                    self._expr_ref_matches_review_field(ref)
                    or self._expr_ref_matches_review_semantic_ref(
                        ref,
                        review_semantics=review_semantics,
                    )
                    or self._expr_ref_matches_review_verdict(ref)
                )
            )
        )

    def _validate_standalone_read_guard_contract(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        for path, item in self._iter_output_items_with_paths(decl.items):
            if not path or path[-1] != "standalone_read":
                continue
            owner_label = f"output {decl.name}.{'.'.join(path)}"
            for ref in self._iter_record_item_interpolation_refs(item):
                if self._interpolation_ref_enters_guarded_output_detail(
                    ref,
                    unit=unit,
                    owner_label=owner_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                ):
                    raise CompileError(
                        "standalone_read cannot interpolate guarded output detail "
                        f"in {owner_label}: {_display_addressable_ref(ref)}"
                    )

    def _iter_output_items_with_paths(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        prefix: tuple[str, ...] = (),
    ) -> tuple[tuple[tuple[str, ...], model.AnyRecordItem], ...]:
        entries: list[tuple[tuple[str, ...], model.AnyRecordItem]] = []
        for item in items:
            if isinstance(item, model.RecordSection):
                path = (*prefix, item.key)
                entries.append((path, item))
                entries.extend(self._iter_output_items_with_paths(item.items, prefix=path))
                continue
            if isinstance(item, model.GuardedOutputSection):
                path = (*prefix, item.key)
                entries.append((path, item))
                entries.extend(self._iter_output_items_with_paths(item.items, prefix=path))
                continue
            if isinstance(item, model.GuardedOutputScalar):
                path = (*prefix, item.key)
                entries.append((path, item))
                if item.body is not None:
                    entries.extend(self._iter_output_items_with_paths(item.body, prefix=path))
                continue
            if isinstance(item, model.RecordScalar):
                path = (*prefix, item.key)
                entries.append((path, item))
                if item.body is not None:
                    entries.extend(self._iter_output_items_with_paths(item.body, prefix=path))
                continue
            if isinstance(item, model.RecordRef) and item.body is not None:
                entries.extend(self._iter_output_items_with_paths(item.body, prefix=prefix))
        return tuple(entries)

    def _iter_record_item_interpolation_refs(
        self,
        item: model.AnyRecordItem,
    ) -> tuple[model.AddressableRef, ...]:
        if isinstance(item, model.GuardedOutputScalar):
            refs = self._interpolation_refs_from_scalar_value(item.value)
            if item.body is not None:
                refs = (*refs, *self._iter_record_body_interpolation_refs(item.body))
            return refs
        if isinstance(item, model.RecordScalar):
            refs = self._interpolation_refs_from_scalar_value(item.value)
            if item.body is not None:
                refs = (*refs, *self._iter_record_body_interpolation_refs(item.body))
            return refs
        if isinstance(item, (model.RecordSection, model.GuardedOutputSection)):
            return self._iter_record_body_interpolation_refs(item.items)
        if isinstance(item, model.RecordRef):
            refs: tuple[model.AddressableRef, ...] = (model.AddressableRef(root=item.ref, path=()),)
            if item.body is not None:
                refs = (*refs, *self._iter_record_body_interpolation_refs(item.body))
            return refs
        return ()

    def _iter_record_body_interpolation_refs(
        self,
        items: tuple[model.AnyRecordItem, ...],
    ) -> tuple[model.AddressableRef, ...]:
        refs: list[model.AddressableRef] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                refs.extend(self._interpolation_refs_from_prose_line(item))
                continue
            refs.extend(self._iter_record_item_interpolation_refs(item))
        return tuple(refs)

    def _interpolation_refs_from_prose_line(
        self,
        value: model.ProseLine,
    ) -> tuple[model.AddressableRef, ...]:
        text = value if isinstance(value, str) else value.text
        return self._interpolation_refs_from_text(text)

    def _interpolation_refs_from_scalar_value(
        self,
        value: model.RecordScalarValue,
    ) -> tuple[model.AddressableRef, ...]:
        if isinstance(value, str):
            return self._interpolation_refs_from_text(value)
        if isinstance(value, model.AddressableRef):
            return (value,)
        return ()

    def _interpolation_refs_from_text(
        self,
        text: str,
    ) -> tuple[model.AddressableRef, ...]:
        if "{{" not in text or "}}" not in text:
            return ()
        refs: list[model.AddressableRef] = []
        for match in _INTERPOLATION_RE.finditer(text):
            ref = self._parse_interpolation_expr_ref(match.group(1))
            if ref is not None:
                refs.append(ref)
        return tuple(refs)

    def _parse_interpolation_expr_ref(
        self,
        expression: str,
    ) -> model.AddressableRef | None:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            return None
        return model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )

    def _interpolation_ref_enters_guarded_output_detail(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        _ = route_semantics
        semantic_parts = self._review_semantic_addressable_parts(ref)
        if (
            review_semantics is not None
            and semantic_parts is not None
            and semantic_parts[0] == "fields"
        ):
            field_path = self._review_semantic_field_path(review_semantics, semantic_parts[1])
            if field_path is None:
                return False
            _output_unit, output_decl = self._resolve_review_semantic_output_decl(review_semantics)
            return self._output_path_has_guarded_detail(
                output_decl,
                path=(*field_path, *semantic_parts[2:]),
            )
        try:
            target_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="standalone_read interpolation ref",
                missing_local_label="standalone_read",
                review_semantics=review_semantics,
            )
        except CompileError:
            return False

        if not isinstance(root_decl, model.OutputDecl):
            return False

        current = AddressableNode(unit=target_unit, root_decl=root_decl, target=root_decl)
        for segment in ref.path:
            children = self._get_addressable_children(current)
            if children is None:
                return False
            current = children.get(segment)
            if current is None:
                return False
            if isinstance(current.target, (model.GuardedOutputSection, model.GuardedOutputScalar)):
                return True
        return False

    def _expr_ref_matches_input_decl(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        for split_at in range(len(ref.parts), 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            if not self._ref_exists_in_registry(root, unit=unit, registry_name="inputs_by_name"):
                continue
            _target_unit, _decl = self._resolve_input_decl(root, unit=unit)
            return True
        return False

    def _expr_ref_matches_review_field(self, ref: model.ExprRef) -> bool:
        return len(ref.parts) == 1 and ref.parts[0] in _REVIEW_GUARD_FIELD_NAMES

    def _expr_ref_matches_review_semantic_ref(
        self,
        ref: model.ExprRef,
        *,
        review_semantics: ReviewSemanticContext | None,
    ) -> bool:
        if review_semantics is None or len(ref.parts) < 2:
            return False
        if ref.parts[0] == "fields":
            return self._review_semantic_field_path(review_semantics, ref.parts[1]) is not None
        if ref.parts[0] == "contract":
            if ref.parts[1] in _REVIEW_CONTRACT_FACT_KEYS and len(ref.parts) == 2:
                return True
            return (
                len(ref.parts) == 2
                and self._review_semantic_contract_gate(review_semantics, ref.parts[1]) is not None
            )
        return False

    def _expr_ref_matches_route_semantic_ref(
        self,
        ref: model.ExprRef,
        *,
        route_semantics: RouteSemanticContext | None,
    ) -> bool:
        if route_semantics is None or not ref.parts or ref.parts[0] != "route":
            return False
        if len(ref.parts) == 2 and ref.parts[1] == "exists":
            return True
        if len(ref.parts) == 2 and ref.parts[1] in {"label", "summary", "next_owner"}:
            return True
        return len(ref.parts) == 3 and ref.parts[1] == "next_owner" and ref.parts[2] in {
            "name",
            "key",
            "title",
        }

    def _expr_ref_matches_enum_member(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        if len(ref.parts) < 2:
            return False
        for split_at in range(len(ref.parts) - 1, 0, -1):
            root = _name_ref_from_dotted_name(".".join(ref.parts[:split_at]))
            enum_decl = self._try_resolve_enum_decl(root, unit=unit)
            if enum_decl is None:
                continue
            remainder = ref.parts[split_at:]
            return len(remainder) == 1 and any(member.key == remainder[0] for member in enum_decl.members)
        return False

    def _config_spec_from_decl(
        self,
        decl: model.InputSourceDecl | model.OutputTargetDecl,
        *,
        owner_label: str,
    ) -> ConfigSpec:
        _scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            section_keys={"required", "optional"},
            owner_label=owner_label,
        )
        if extras:
            # Extra prose is fine on the declaration; it does not affect config validation.
            pass
        required_section = section_items.get("required")
        optional_section = section_items.get("optional")
        required_keys = (
            self._key_labels_from_section(required_section, owner_label=owner_label)
            if required_section is not None
            else {}
        )
        optional_keys = (
            self._key_labels_from_section(optional_section, owner_label=owner_label)
            if optional_section is not None
            else {}
        )
        return ConfigSpec(title=decl.title, required_keys=required_keys, optional_keys=optional_keys)

    def _key_labels_from_section(
        self,
        section: model.RecordSection,
        *,
        owner_label: str,
    ) -> dict[str, str]:
        labels: dict[str, str] = {}
        for item in section.items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(
                    f"Config key declarations must be simple titled scalars in {owner_label}"
                )
            if not isinstance(item.value, str):
                raise CompileError(
                    f"Config key declarations must use string labels in {owner_label}: {item.key}"
                )
            if item.key in labels:
                raise CompileError(f"Duplicate config key declaration in {owner_label}: {item.key}")
            labels[item.key] = item.value
        return labels

    def _display_output_shape(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, model.AddressableRef):
            raise CompileError(
                f"Output shape must stay typed: {owner_label or surface_label or 'output'}"
            )
        if value.module_parts:
            _target_unit, decl = self._resolve_output_shape_decl(value, unit=unit)
            return decl.title
        local_decl = unit.output_shapes_by_name.get(value.declaration_name)
        if local_decl is not None:
            return local_decl.title
        return _humanize_key(value.declaration_name)

    def _is_markdown_shape_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
    ) -> bool:
        markdown_shape_names = {"MarkdownDocument", "AgentOutputDocument"}
        if isinstance(value, model.AddressableRef):
            return False
        if isinstance(value, str):
            return value in markdown_shape_names
        if self._ref_exists_in_registry(value, unit=unit, registry_name="output_shapes_by_name"):
            shape_unit, shape_decl = self._resolve_output_shape_decl(value, unit=unit)
            kind_item = next(
                (
                    item
                    for item in shape_decl.items
                    if isinstance(item, model.RecordScalar)
                    and item.key == "kind"
                    and item.body is None
                ),
                None,
            )
            if kind_item is None:
                return shape_decl.name in markdown_shape_names
            return self._is_markdown_shape_value(kind_item.value, unit=shape_unit)
        return value.declaration_name in markdown_shape_names

    def _is_comment_shape_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
    ) -> bool:
        comment_shape_names = {"Comment", "CommentText"}
        if isinstance(value, model.AddressableRef):
            return False
        if isinstance(value, str):
            return value in comment_shape_names
        if self._ref_exists_in_registry(value, unit=unit, registry_name="output_shapes_by_name"):
            shape_unit, shape_decl = self._resolve_output_shape_decl(value, unit=unit)
            kind_item = next(
                (
                    item
                    for item in shape_decl.items
                    if isinstance(item, model.RecordScalar)
                    and item.key == "kind"
                    and item.body is None
                ),
                None,
            )
            if kind_item is None:
                return shape_decl.name in comment_shape_names
            return self._is_comment_shape_value(kind_item.value, unit=shape_unit)
        return value.declaration_name in comment_shape_names

    def _display_symbol_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        return self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            render_profile=render_profile,
        ).text

    def _format_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )
        if display.kind == "string_literal":
            return f"`{display.text}`"
        return display.text

    def _display_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        if isinstance(value, str):
            return DisplayValue(text=value, kind="string_literal")
        if isinstance(value, model.NameRef):
            if value.module_parts and value.module_parts[0] == "route":
                if owner_label is None or surface_label is None:
                    raise CompileError(
                        "Internal compiler error: route refs require an owner label and surface label"
                    )
                route_value = self._resolve_route_semantic_ref_value(
                    model.AddressableRef(root=value, path=()),
                    owner_label=owner_label,
                    surface_label=surface_label,
                    route_semantics=route_semantics,
                )
                if route_value is not None:
                    return route_value
            enum_decl = self._try_resolve_enum_decl(value, unit=unit)
            if enum_decl is not None:
                return DisplayValue(text=enum_decl.title, kind="title")
            return DisplayValue(text=self._display_ref(value, unit=unit), kind="symbol")
        if owner_label is None or surface_label is None:
            raise CompileError(
                "Internal compiler error: addressable refs require an owner label and surface label"
            )
        return self._resolve_addressable_ref_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=f"{surface_label} addressable ref",
            missing_local_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )

    def _value_to_symbol(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
        return display.text

    def _schema_body_action(
        self,
        items: tuple[model.SchemaItem, ...],
        *,
        block_key: str,
    ) -> tuple[str | None, tuple[object, ...]]:
        for item in items:
            if isinstance(item, model.InheritItem) and item.key == block_key:
                return "inherit", ()
            if block_key == "sections" and isinstance(item, model.SchemaSectionsBlock):
                return "define", item.items
            if block_key == "gates" and isinstance(item, model.SchemaGatesBlock):
                return "define", item.items
            if block_key == "artifacts" and isinstance(item, model.SchemaArtifactsBlock):
                return "define", item.items
            if block_key == "groups" and isinstance(item, model.SchemaGroupsBlock):
                return "define", item.items
            if block_key == "sections" and isinstance(item, model.SchemaOverrideSectionsBlock):
                return "override", item.items
            if block_key == "gates" and isinstance(item, model.SchemaOverrideGatesBlock):
                return "override", item.items
            if block_key == "artifacts" and isinstance(item, model.SchemaOverrideArtifactsBlock):
                return "override", item.items
            if block_key == "groups" and isinstance(item, model.SchemaOverrideGroupsBlock):
                return "override", item.items
        return None, ()

    def _validate_schema_group_members(
        self,
        groups: tuple[ResolvedSchemaGroup, ...],
        *,
        artifacts: tuple[ResolvedSchemaArtifact, ...],
        owner_label: str,
    ) -> None:
        artifact_keys = {item.key for item in artifacts}
        for group in groups:
            for member_key in group.members:
                if member_key not in artifact_keys:
                    raise CompileError(
                        f"Unknown schema group member in {owner_label}: {group.key}.{member_key}"
                    )

    def _require_tuple_payload(
        self,
        payload: model.ReadablePayload,
        *,
        owner_label: str,
        kind: str,
    ) -> tuple[object, ...]:
        if not isinstance(payload, tuple):
            raise CompileError(f"Readable {kind} payload must stay block-shaped in {owner_label}")
        return payload

    def _validate_readable_guard_expr(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        if isinstance(expr, model.ExprRef):
            if self._output_guard_ref_allowed(
                expr,
                unit=unit,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            ):
                return
            raise CompileError(
                f"Readable guard reads disallowed source in {owner_label}: {'.'.join(expr.parts)}"
            )
        if isinstance(expr, model.ExprBinary):
            self._validate_readable_guard_expr(
                expr.left,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            self._validate_readable_guard_expr(
                expr.right,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            return
        if isinstance(expr, model.ExprCall):
            for arg in expr.args:
                self._validate_readable_guard_expr(
                    arg,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
            return
        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._validate_readable_guard_expr(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )

    def _readable_guard_text(
        self,
        expr: model.Expr | None,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if expr is None:
            return None
        return self._render_condition_expr(expr, unit=unit)

    def _interpolate_authored_prose_string(
        self,
        value: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        if "{{" not in value and "}}" not in value:
            return value

        parts: list[str] = []
        cursor = 0
        for match in _INTERPOLATION_RE.finditer(value):
            between = value[cursor:match.start()]
            if "{{" in between or "}}" in between:
                raise CompileError(
                    f"Malformed interpolation in {owner_label}: {value}"
                )
            parts.append(between)
            parts.append(
                self._resolve_authored_prose_interpolation_expr(
                    match.group(1),
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    ambiguous_label=ambiguous_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
            cursor = match.end()

        tail = value[cursor:]
        if "{{" in tail or "}}" in tail:
            raise CompileError(
                f"Malformed interpolation in {owner_label}: {value}"
            )
        parts.append(tail)
        return "".join(parts)

    def _interpolate_authored_prose_line(
        self,
        value: model.ProseLine,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ProseLine:
        if isinstance(value, str):
            return self._interpolate_authored_prose_string(
                value,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        return model.EmphasizedLine(
            kind=value.kind,
            text=self._interpolate_authored_prose_string(
                value.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            ),
        )

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
        # Schema families stay namespace-first so similarly keyed items never
        # collide across sections, gates, artifacts, and groups.
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
                model.DocumentDecl,
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.JsonSchemaDecl,
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
                model.JsonSchemaDecl,
                model.SkillDecl,
            ),
        ):
            return DisplayValue(text=target.title, kind="title")
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
        raise CompileError(
            f"Internal compiler error: unsupported addressable target {type(target).__name__}"
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
                raise CompileError(f"Input source must stay typed: {root_decl.name}")
            return self._resolve_input_source_spec(item.value, unit=node.unit).title

        if isinstance(root_decl, model.OutputDecl) and item.key == "target":
            if not isinstance(item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {root_decl.name}")
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

    def _review_semantic_fallback_lookup_unit(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None,
    ) -> IndexedUnit | None:
        if review_semantics is None or ref.module_parts:
            return None
        if review_semantics.review_module_parts == unit.module_parts:
            return None
        return self._load_module(review_semantics.review_module_parts)

    def _validate_route_target(self, ref: model.NameRef, *, unit: IndexedUnit) -> None:
        _target_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        if agent.abstract:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Route target must be a concrete agent: {dotted_name}")

    def _flatten_law_items(
        self,
        law_body: model.LawBody,
        *,
        owner_label: str,
    ) -> tuple[model.LawStmt, ...]:
        has_sections = any(isinstance(item, model.LawSection) for item in law_body.items)
        if has_sections:
            if not all(isinstance(item, model.LawSection) for item in law_body.items):
                raise CompileError(
                    f"Law blocks may not mix named sections with bare law statements in {owner_label}"
                )
            flattened: list[model.LawStmt] = []
            for item in law_body.items:
                flattened.extend(item.items)
            return tuple(flattened)
        return tuple(law_body.items)

    def _validate_workflow_law(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        self._validate_law_stmt_tree(
            items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )
        branches = self._collect_law_leaf_branches(items, unit=unit)
        if not branches:
            branches = (LawBranch(),)

        route_only_branch_seen = False
        for branch in branches:
            if len(branch.current_subjects) != 1:
                current_labels = ", ".join(
                    "current none"
                    if isinstance(subject, model.CurrentNoneStmt)
                    else "current artifact"
                    for subject in branch.current_subjects
                )
                if current_labels:
                    raise CompileError(
                        "Active leaf branch resolves more than one current-subject form "
                        f"({current_labels}) in {owner_label}"
                    )
                raise CompileError(
                    f"Active leaf branch must resolve exactly one current-subject form in {owner_label}"
                )
            current = branch.current_subjects[0]
            if isinstance(current, model.CurrentNoneStmt) and branch.owns:
                raise CompileError(
                    f"`current none` cannot appear with owned scope in {owner_label}"
                )
            if isinstance(current, model.CurrentNoneStmt):
                route_only_branch_seen = True
            current_target_key: tuple[tuple[str, ...], str] | None = None
            if isinstance(current, model.CurrentArtifactStmt):
                current_target_key = self._validate_current_artifact_stmt(
                    current,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
                for own in branch.owns:
                    self._validate_owned_scope(
                        own,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        current_target=current,
                    )
                for invalidate in branch.invalidations:
                    if self._law_paths_match(
                        current.target,
                        invalidate.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                        allowed_kinds=("input", "output", "schema_group"),
                    ):
                        raise CompileError(
                            f"The current artifact cannot be invalidated in the same active branch in {owner_label}"
                        )
            for invalidate in branch.invalidations:
                self._validate_invalidation_stmt(
                    invalidate,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
            for support in branch.supports:
                for ignore in branch.ignores:
                    if "comparison" in ignore.bases and self._path_sets_overlap(
                        support.target,
                        ignore.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                    ):
                        raise CompileError(
                            f"support_only and ignore for comparison contradict in {owner_label}"
                        )
            if current_target_key is not None:
                for ignore in branch.ignores:
                    if ("truth" in ignore.bases or not ignore.bases) and self._path_set_contains_path(
                        ignore.target,
                        current.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                    ):
                        raise CompileError(
                            f"The current artifact cannot be ignored for truth in {owner_label}"
                        )
            for own in branch.owns:
                own_target = self._coerce_path_set(own.target)
                for forbid in branch.forbids:
                    if self._path_sets_overlap(
                        own_target,
                        forbid.target,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        statement_label="workflow law",
                        allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
                    ):
                        raise CompileError(
                            f"Owned and forbidden scope overlap in {owner_label}"
                        )
                for preserve in branch.preserves:
                    if preserve.kind == "exact" and any(
                        self._path_set_contains_path(
                            preserve.target,
                            path,
                            unit=unit,
                            agent_contract=agent_contract,
                            owner_label=owner_label,
                            statement_label="workflow law",
                            allowed_kinds=_PRESERVE_TARGET_ALLOWED_KINDS["exact"],
                        )
                        for path in own_target.paths
                    ):
                        raise CompileError(
                            f"Owned scope overlaps exact-preserved scope in {owner_label}"
                        )
            if isinstance(current, model.CurrentNoneStmt) and branch.routes:
                self._validate_route_only_next_owner_contract(
                    branch,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )

        if route_only_branch_seen:
            self._validate_route_only_standalone_read_contract(
                agent_contract=agent_contract,
                unit=unit,
                owner_label=owner_label,
            )

    def _validate_route_only_next_owner_contract(
        self,
        branch: LawBranch,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        output_items = tuple(agent_contract.outputs.items())
        if not output_items:
            return

        for route in branch.routes:
            route_branch = self._route_semantic_branch_from_route(
                route.target,
                label=route.label,
                unit=unit,
            )
            next_owner_fields_found = False
            for (_output_key, (output_unit, output_decl)) in output_items:
                for path, item in self._iter_output_items_with_paths(output_decl.items):
                    if not path or path[-1] != "next_owner":
                        continue
                    next_owner_fields_found = True
                    self._validate_route_owner_alignment(
                        item,
                        route_branch=route_branch,
                        unit=output_unit,
                        owner_label=f"output {output_decl.name}.{'.'.join(path)}",
                        error_message=(
                            "next_owner field must interpolate routed target "
                            f"in {owner_label}: {output_decl.name}.{'.'.join(path)} -> "
                            f"{route_branch.target_name}"
                        ),
                    )
            if next_owner_fields_found:
                continue

    def _validate_route_owner_alignment(
        self,
        item: model.AnyRecordItem,
        *,
        route_branch: RouteSemanticBranch,
        unit: IndexedUnit,
        owner_label: str,
        error_message: str,
        fallback_unit: IndexedUnit | None = None,
    ) -> None:
        route_semantics = RouteSemanticContext(
            branches=(route_branch,),
            route_required=True,
        )
        if self._record_item_mentions_agent(
            item,
            target_unit_module_parts=route_branch.target_module_parts,
            target_agent_name=route_branch.target_name,
            unit=unit,
            fallback_unit=fallback_unit,
            owner_label=owner_label,
            route_semantics=route_semantics,
        ):
            return
        raise CompileError(error_message)

    def _record_item_mentions_agent(
        self,
        item: model.AnyRecordItem,
        *,
        target_unit_module_parts: tuple[str, ...],
        target_agent_name: str,
        unit: IndexedUnit,
        fallback_unit: IndexedUnit | None = None,
        owner_label: str,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        if (
            isinstance(item, (model.RecordScalar, model.GuardedOutputScalar))
            and isinstance(item.value, model.NameRef)
            and self._name_ref_matches_agent(
                item.value,
                target_unit_module_parts=target_unit_module_parts,
                target_agent_name=target_agent_name,
                unit=unit,
                fallback_unit=fallback_unit,
                owner_label=owner_label,
            )
        ):
            return True
        if (
            isinstance(item, (model.RecordScalar, model.GuardedOutputScalar))
            and isinstance(item.value, model.NameRef)
            and self._addressable_ref_matches_agent(
                model.AddressableRef(root=item.value, path=()),
                target_unit_module_parts=target_unit_module_parts,
                target_agent_name=target_agent_name,
                unit=unit,
                fallback_unit=fallback_unit,
                owner_label=owner_label,
                route_semantics=route_semantics,
            )
        ):
            return True

        return any(
            self._addressable_ref_matches_agent(
                ref,
                target_unit_module_parts=target_unit_module_parts,
                target_agent_name=target_agent_name,
                unit=unit,
                fallback_unit=fallback_unit,
                owner_label=owner_label,
                route_semantics=route_semantics,
            )
            for ref in self._iter_record_item_interpolation_refs(item)
        )

    def _addressable_ref_matches_agent(
        self,
        ref: model.AddressableRef,
        *,
        target_unit_module_parts: tuple[str, ...],
        target_agent_name: str,
        unit: IndexedUnit,
        fallback_unit: IndexedUnit | None = None,
        owner_label: str,
        route_semantics: RouteSemanticContext | None = None,
    ) -> bool:
        route_parts = self._route_semantic_parts(ref)
        if (
            route_semantics is not None
            and route_parts in {
                ("route", "next_owner"),
                ("route", "next_owner", "name"),
                ("route", "next_owner", "key"),
                ("route", "next_owner", "title"),
            }
        ):
            return any(
                branch.target_name == target_agent_name
                and branch.target_module_parts == target_unit_module_parts
                for branch in route_semantics.branches
            )
        try:
            root_unit, root_decl = self._resolve_addressable_root_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                ambiguous_label="next_owner interpolation ref",
                missing_local_label="next_owner",
            )
        except CompileError:
            if fallback_unit is None:
                return False
            try:
                root_unit, root_decl = self._resolve_addressable_root_decl(
                    ref.root,
                    unit=fallback_unit,
                    owner_label=owner_label,
                    ambiguous_label="next_owner interpolation ref",
                    missing_local_label="next_owner",
                )
            except CompileError:
                return False

        if not isinstance(root_decl, model.Agent):
            return False
        if root_decl.name != target_agent_name or root_unit.module_parts != target_unit_module_parts:
            return False
        return not ref.path or ref.path in {("name",), ("key",), ("title",)}

    def _name_ref_matches_agent(
        self,
        ref: model.NameRef,
        *,
        target_unit_module_parts: tuple[str, ...],
        target_agent_name: str,
        unit: IndexedUnit,
        fallback_unit: IndexedUnit | None = None,
        owner_label: str,
    ) -> bool:
        try:
            ref_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        except CompileError:
            if fallback_unit is None:
                return False
            try:
                ref_unit, agent = self._resolve_agent_ref(ref, unit=fallback_unit)
            except CompileError:
                return False
        _ = owner_label
        return agent.name == target_agent_name and ref_unit.module_parts == target_unit_module_parts

    def _validate_route_only_standalone_read_contract(
        self,
        *,
        agent_contract: AgentContract,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        _ = unit
        _ = owner_label
        for _output_key, (output_unit, output_decl) in agent_contract.outputs.items():
            self._validate_standalone_read_guard_contract(output_decl, unit=output_unit)

    def _validate_law_stmt_tree(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt] | None = None,
    ) -> None:
        local_mode_bindings = dict(mode_bindings or {})
        for item in items:
            if isinstance(item, model.ModeStmt):
                self._validate_mode_stmt(item, unit=unit, owner_label=owner_label)
                local_mode_bindings[item.name] = item
                continue
            if isinstance(item, model.MatchStmt):
                self._validate_match_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                for case in item.cases:
                    self._validate_law_stmt_tree(
                        case.items,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=local_mode_bindings,
                    )
                continue
            if isinstance(item, model.WhenStmt):
                self._validate_law_stmt_tree(
                    item.items,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                continue
            if isinstance(item, model.CurrentArtifactStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="current artifact",
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["current_artifact"],
                )
                continue
            if isinstance(item, model.InvalidateStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="invalidate",
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["invalidate"],
                )
                continue
            if isinstance(item, model.OwnOnlyStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
                )
                continue
            if isinstance(item, (model.SupportOnlyStmt, model.IgnoreStmt, model.ForbidStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["path_set"],
                )
                continue
            if isinstance(item, model.PreserveStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=f"preserve {item.kind}",
                    allowed_kinds=_PRESERVE_TARGET_ALLOWED_KINDS[item.kind],
                )
                continue
            if isinstance(item, model.LawRouteStmt):
                self._validate_route_target(item.target, unit=unit)

    def _validate_mode_stmt(
        self,
        stmt: model.ModeStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        enum_unit, enum_decl = self._resolve_decl_ref(
            stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        fixed_mode = self._resolve_constant_enum_member(stmt.expr, unit=enum_unit)
        if fixed_mode is None:
            return
        if not any(member.value == fixed_mode for member in enum_decl.members):
            raise CompileError(
                f"Mode value is outside enum {enum_decl.name} in {owner_label}: {fixed_mode}"
            )

    def _validate_match_stmt(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> None:
        enum_decl = self._resolve_match_enum_decl(
            stmt.expr,
            unit=unit,
            mode_bindings=mode_bindings,
        )
        if enum_decl is None:
            return

        if any(case.head is None for case in stmt.cases):
            return

        seen_members: set[str] = set()
        for case in stmt.cases:
            if case.head is None:
                continue
            member_value = self._resolve_constant_enum_member(case.head, unit=unit)
            if member_value is None:
                continue
            if not any(member.value == member_value for member in enum_decl.members):
                raise CompileError(
                    f"Match arm is outside enum {enum_decl.name} in {owner_label}: {member_value}"
                )
            seen_members.add(member_value)

        expected_members = {member.value for member in enum_decl.members}
        if seen_members != expected_members:
            raise CompileError(
                f"match on {enum_decl.name} must be exhaustive or include else in {owner_label}"
            )

    def _collect_law_leaf_branches(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        branch: LawBranch | None = None,
    ) -> tuple[LawBranch, ...]:
        branches = (branch or LawBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.WhenStmt):
                when_items: list[model.WhenStmt] = []
                while index < len(items) and isinstance(items[index], model.WhenStmt):
                    when_items.append(items[index])
                    index += 1
                next_branches: list[LawBranch] = []
                for current_branch in branches:
                    for when_item in when_items:
                        next_branches.extend(
                            self._collect_law_leaf_branches(
                                when_item.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                branches = tuple(next_branches)
                continue
            if isinstance(item, model.WhenStmt):
                next_branches: list[LawBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_law_leaf_branches(
                            item.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
                continue
            if isinstance(item, model.MatchStmt):
                next_branches = []
                for current_branch in branches:
                    for case in self._select_match_cases(
                        item,
                        unit=unit,
                        branch=current_branch,
                    ):
                        next_branches.extend(
                            self._collect_law_leaf_branches(
                                case.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                branches = tuple(next_branches)
                index += 1
                continue
            branches = tuple(self._branch_with_stmt(current_branch, item) for current_branch in branches)
            index += 1
        return branches

    def _select_match_cases(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        branch: LawBranch,
    ) -> tuple[model.MatchArm, ...]:
        fixed_mode = self._resolve_fixed_match_value(stmt.expr, unit=unit, branch=branch)
        if fixed_mode is None:
            return stmt.cases

        exact_matches = tuple(
            case
            for case in stmt.cases
            if case.head is not None
            and self._resolve_constant_enum_member(case.head, unit=unit) == fixed_mode
        )
        if exact_matches:
            return exact_matches
        else_matches = tuple(case for case in stmt.cases if case.head is None)
        if else_matches:
            return else_matches
        return stmt.cases

    def _branch_with_stmt(self, branch: LawBranch, stmt: model.LawStmt) -> LawBranch:
        if isinstance(stmt, model.ActiveWhenStmt):
            return replace(branch, activation_exprs=(*branch.activation_exprs, stmt.expr))
        if isinstance(stmt, model.ModeStmt):
            return replace(branch, mode_bindings=(*branch.mode_bindings, stmt))
        if isinstance(stmt, (model.CurrentArtifactStmt, model.CurrentNoneStmt)):
            return replace(branch, current_subjects=(*branch.current_subjects, stmt))
        if isinstance(stmt, model.MustStmt):
            return replace(branch, musts=(*branch.musts, stmt))
        if isinstance(stmt, model.OwnOnlyStmt):
            return replace(branch, owns=(*branch.owns, stmt))
        if isinstance(stmt, model.PreserveStmt):
            return replace(branch, preserves=(*branch.preserves, stmt))
        if isinstance(stmt, model.SupportOnlyStmt):
            return replace(branch, supports=(*branch.supports, stmt))
        if isinstance(stmt, model.IgnoreStmt):
            return replace(branch, ignores=(*branch.ignores, stmt))
        if isinstance(stmt, model.ForbidStmt):
            return replace(branch, forbids=(*branch.forbids, stmt))
        if isinstance(stmt, model.InvalidateStmt):
            return replace(branch, invalidations=(*branch.invalidations, stmt))
        if isinstance(stmt, model.StopStmt):
            return replace(branch, stops=(*branch.stops, stmt))
        if isinstance(stmt, model.LawRouteStmt):
            return replace(branch, routes=(*branch.routes, stmt))
        return branch

    def _validate_current_artifact_stmt(
        self,
        stmt: model.CurrentArtifactStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str]:
        target = self._validate_law_path_root(
            stmt.target,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
            allowed_kinds=("input", "output"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"current artifact must stay rooted at one input or output artifact in {owner_label}: "
                f"{'.'.join(stmt.target.parts)}"
            )

        carrier = self._validate_carrier_path(
            stmt.carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
        )
        if isinstance(target.decl, model.OutputDecl):
            target_key = (target.unit.module_parts, target.decl.name)
            if target_key not in agent_contract.outputs:
                raise CompileError(
                    f"current artifact output must be emitted by the concrete turn in {owner_label}: "
                    f"{target.decl.name}"
                )
        return (target.unit.module_parts, target.decl.name)

    def _validate_invalidation_stmt(
        self,
        stmt: model.InvalidateStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        target = self._validate_law_path_root(
            stmt.target,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="invalidate",
            allowed_kinds=("input", "output", "schema_group"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"invalidate must name one full input or output artifact or schema group in {owner_label}: "
                f"{'.'.join(stmt.target.parts)}"
            )
        self._validate_carrier_path(
            stmt.carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="invalidate",
        )

    def _validate_carrier_path(
        self,
        carrier: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        statement_label: str,
    ) -> ResolvedLawPath:
        resolved = self._validate_law_path_root(
            carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=f"{statement_label} carrier",
            allowed_kinds=("output",),
        )
        if not isinstance(resolved.decl, model.OutputDecl):
            raise CompileError(
                f"{statement_label} via carrier must stay rooted in an emitted output in {owner_label}"
            )
        if not resolved.remainder or resolved.wildcard:
            raise CompileError(
                f"{statement_label} requires an explicit `via` field on an emitted output in {owner_label}"
            )

        output_key = (resolved.unit.module_parts, resolved.decl.name)
        if output_key not in agent_contract.outputs:
            raise CompileError(
                f"{statement_label} carrier output must be emitted by the concrete turn in {owner_label}: "
                f"{resolved.decl.name}"
            )

        self._resolve_output_field_node(
            resolved.decl,
            path=resolved.remainder,
            unit=resolved.unit,
            owner_label=owner_label,
            surface_label=f"{statement_label} via",
        )
        if not any(item.path == resolved.remainder for item in resolved.decl.trust_surface):
            raise CompileError(
                f"{statement_label} carrier field must be listed in trust_surface in {owner_label}: "
                f"{'.'.join(resolved.remainder)}"
            )
        return resolved

    def _validate_owned_scope(
        self,
        stmt: model.OwnOnlyStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        current_target: model.CurrentArtifactStmt,
    ) -> None:
        target = self._coerce_path_set(stmt.target)
        current_root = self._validate_law_path_root(
            current_target.target,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
            allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["current_artifact"],
        )
        for path in target.paths:
            resolved = self._validate_law_path_root(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label="own only",
                allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
            )
            if (
                resolved.unit.module_parts == current_root.unit.module_parts
                and isinstance(resolved.decl, type(current_root.decl))
                and self._law_path_decl_identity(resolved.decl)
                == self._law_path_decl_identity(current_root.decl)
            ):
                continue
            if isinstance(resolved.decl, model.OutputDecl):
                output_key = (resolved.unit.module_parts, resolved.decl.name)
                if output_key in agent_contract.outputs:
                    continue
            if isinstance(resolved.decl, SchemaFamilyTarget):
                continue
            raise CompileError(
                "own only must stay rooted in the current artifact, an emitted output "
                f"surface, or a declared schema family in {owner_label}: "
                f"{'.'.join(path.parts)}"
            )

    def _validate_path_set_roots(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> None:
        target = self._coerce_path_set(target)
        for path in (*target.paths, *target.except_paths):
            self._validate_law_path_root(
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )

    def _validate_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        resolved = self._resolve_law_path(
            path,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        if isinstance(
            resolved.decl,
            (model.EnumDecl, SchemaFamilyTarget, ResolvedSchemaGroup, model.GroundingDecl),
        ) and resolved.remainder:
            raise CompileError(
                f"{statement_label} enum, schema-family, schema-group, and grounding targets must not descend through fields in {owner_label}: "
                f"{'.'.join(path.parts)}"
            )
        return resolved

    def _law_path_match_key(
        self,
        match: ResolvedLawPath,
    ) -> tuple[tuple[str, ...], str, tuple[str, ...], str]:
        return (
            match.unit.module_parts,
            self._law_path_decl_identity(match.decl),
            match.remainder,
            type(match.decl).__name__,
        )

    def _law_path_allowed_text(
        self,
        allowed_kinds: tuple[str, ...],
        *,
        agent_contract: AgentContract | None,
    ) -> str:
        labels: list[str] = []
        for kind in allowed_kinds:
            if kind == "input":
                labels.append(
                    "declared or bound concrete-turn input"
                    if agent_contract is not None
                    else "declared input"
                )
                continue
            if kind == "output":
                labels.append(
                    "declared or bound concrete-turn output"
                    if agent_contract is not None
                    else "declared output"
                )
                continue
            if kind == "enum":
                labels.append("declared enum")
                continue
            if kind == "grounding":
                labels.append("declared grounding")
                continue
            if kind == "schema_family":
                labels.append("declared schema family")
                continue
            if kind == "schema_group":
                labels.append("declared schema group")
        return " or ".join(labels)

    def _law_paths_match(
        self,
        left: model.LawPath,
        right: model.LawPath,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        return self._law_path_contains_path(
            left,
            right,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        ) or self._law_path_contains_path(
            right,
            left,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )

    def _law_path_contains_path(
        self,
        container: model.LawPath,
        path: model.LawPath,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        if unit is None or agent_contract is None:
            if len(container.parts) > len(path.parts):
                return False
            if path.parts[: len(container.parts)] != container.parts:
                return False
            if len(container.parts) == len(path.parts):
                return container.wildcard or not path.wildcard or container.wildcard == path.wildcard
            return container.wildcard

        canonical_container = self._canonicalize_law_path(
            container,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        canonical_path = self._canonicalize_law_path(
            path,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        return self._canonical_law_path_contains_path(canonical_container, canonical_path)

    def _canonicalize_law_path(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> CanonicalLawPath:
        resolved = self._validate_law_path_root(
            path,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        return CanonicalLawPath(
            unit=resolved.unit,
            decl=resolved.decl,
            remainder=resolved.remainder,
            wildcard=resolved.wildcard,
        )

    def _canonical_law_path_contains_path(
        self,
        container: CanonicalLawPath,
        path: CanonicalLawPath,
    ) -> bool:
        if isinstance(container.decl, ResolvedSchemaGroup):
            if container.remainder or container.wildcard:
                return False
            return any(
                self._canonical_law_path_contains_path(
                    CanonicalLawPath(
                        unit=member.artifact.unit,
                        decl=member.artifact.decl,
                        remainder=(),
                        wildcard=False,
                    ),
                    path,
                )
                for member in self._schema_group_member_artifacts(
                    container.decl,
                    unit=container.unit,
                )
            )
        if (
            container.unit.module_parts != path.unit.module_parts
            or self._law_path_decl_identity(container.decl)
            != self._law_path_decl_identity(path.decl)
            or type(container.decl) is not type(path.decl)
        ):
            return False
        if len(container.remainder) > len(path.remainder):
            return False
        if path.remainder[: len(container.remainder)] != container.remainder:
            return False
        if len(container.remainder) == len(path.remainder):
            return (
                container.wildcard
                or not path.wildcard
                or container.wildcard == path.wildcard
            )
        return container.wildcard

    def _law_path_decl_identity(
        self,
        decl: (
            model.InputDecl
            | model.OutputDecl
            | model.EnumDecl
            | model.GroundingDecl
            | SchemaFamilyTarget
            | ResolvedSchemaGroup
        ),
    ) -> str:
        if isinstance(decl, SchemaFamilyTarget):
            return decl.family_key
        if isinstance(decl, ResolvedSchemaGroup):
            return decl.key
        return decl.name

    def _path_set_contains_path(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        path: model.LawPath,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        target = self._coerce_path_set(target)
        if not any(
            self._law_path_contains_path(
                base,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )
            for base in target.paths
        ):
            return False
        if any(
            self._law_path_contains_path(
                excluded,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )
            for excluded in target.except_paths
        ):
            return False
        return True

    def _path_sets_overlap(
        self,
        left: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        right: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str = "workflow law",
        statement_label: str = "law path",
        allowed_kinds: tuple[str, ...] = ("input", "output"),
    ) -> bool:
        left = self._coerce_path_set(left)
        right = self._coerce_path_set(right)
        for path in left.paths:
            if self._path_set_contains_path(
                right,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            ):
                return True
        for path in right.paths:
            if self._path_set_contains_path(
                left,
                path,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            ):
                return True
        return False

    def _schema_group_member_artifacts(
        self,
        group: ResolvedSchemaGroup,
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSchemaArtifact, ...]:
        for schema_decl in unit.schemas_by_name.values():
            resolved_schema = self._resolve_schema_decl(schema_decl, unit=unit)
            if group not in resolved_schema.groups:
                continue
            artifacts_by_key = {artifact.key: artifact for artifact in resolved_schema.artifacts}
            return tuple(
                artifacts_by_key[key]
                for key in group.members
                if key in artifacts_by_key
            )
        return ()

    def _coerce_path_set(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> model.LawPathSet:
        if isinstance(target, model.LawPathSet):
            return target
        if isinstance(target, tuple):
            return model.LawPathSet(paths=target)
        return model.LawPathSet(paths=(target,))

    def _law_stmt_name(self, stmt: model.LawStmt) -> str:
        if isinstance(stmt, model.OwnOnlyStmt):
            return "own only"
        if isinstance(stmt, model.SupportOnlyStmt):
            return "support_only"
        if isinstance(stmt, model.IgnoreStmt):
            return "ignore"
        if isinstance(stmt, model.ForbidStmt):
            return "forbid"
        return type(stmt).__name__

    def _split_record_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        scalar_keys: set[str] | None = None,
        section_keys: set[str] | None = None,
        owner_label: str,
    ) -> tuple[dict[str, model.RecordScalar], dict[str, model.RecordSection], tuple[model.AnyRecordItem, ...]]:
        scalar_keys = scalar_keys or set()
        section_keys = section_keys or set()
        scalar_items: dict[str, model.RecordScalar] = {}
        section_items: dict[str, model.RecordSection] = {}
        extras: list[model.AnyRecordItem] = []

        for item in items:
            if isinstance(item, model.RecordScalar) and item.key in scalar_keys:
                if item.key in scalar_items:
                    raise CompileError(f"Duplicate record key in {owner_label}: {item.key}")
                scalar_items[item.key] = item
                continue
            if isinstance(item, model.RecordSection) and item.key in section_keys:
                if item.key in section_items:
                    raise CompileError(f"Duplicate record key in {owner_label}: {item.key}")
                section_items[item.key] = item
                continue
            extras.append(item)

        return scalar_items, section_items, tuple(extras)

    def _try_resolve_route_only_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.RouteOnlyDecl] | None:
        try:
            target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        decl = target_unit.route_onlys_by_name.get(ref.declaration_name)
        if decl is None:
            return None
        return target_unit, decl

    def _try_resolve_grounding_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.GroundingDecl] | None:
        try:
            target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        decl = target_unit.groundings_by_name.get(ref.declaration_name)
        if decl is None:
            return None
        return target_unit, decl

    def _ref_exists_in_registry(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
    ) -> bool:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            return registry.get(ref.declaration_name) is not None

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            return False

        registry = getattr(target_unit, registry_name)
        return registry.get(ref.declaration_name) is not None
