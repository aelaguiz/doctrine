from __future__ import annotations

import json
from pathlib import Path

from doctrine import model
from doctrine._compiler.constants import _RESERVED_AGENT_FIELD_KEYS
from doctrine._compiler.output_schema_validation import (
    OutputSchemaValidationError,
    validate_lowered_output_schema,
    validate_output_example_instance,
)
from doctrine._compiler.resolved_types import (
    CompileError,
    FinalOutputJsonShapeSummary,
    IndexedUnit,
    ResolvedIoBody,
)
from doctrine._compiler.validate.addressable_children import ValidateAddressableChildrenMixin
from doctrine._compiler.validate.addressable_display import ValidateAddressableDisplayMixin
from doctrine._compiler.validate.agents import ValidateAgentsMixin
from doctrine._compiler.validate.contracts import ValidateContractsMixin
from doctrine._compiler.validate.display import ValidateDisplayMixin
from doctrine._compiler.validate.law_paths import ValidateLawPathsMixin
from doctrine._compiler.validate.outputs import ValidateOutputsMixin
from doctrine._compiler.validate.readables import ValidateReadablesMixin
from doctrine._compiler.validate.reviews import ValidateReviewsMixin
from doctrine._compiler.validate.route_semantics import ValidateRouteSemanticsMixin
from doctrine._compiler.validate.routes import ValidateRoutesMixin
from doctrine._compiler.validate.schema_helpers import ValidateSchemaHelpersMixin


class ValidateMixin(
    ValidateAgentsMixin,
    ValidateReviewsMixin,
    ValidateReadablesMixin,
    ValidateRoutesMixin,
    ValidateOutputsMixin,
    ValidateRouteSemanticsMixin,
    ValidateContractsMixin,
    ValidateDisplayMixin,
    ValidateSchemaHelpersMixin,
    ValidateAddressableChildrenMixin,
    ValidateAddressableDisplayMixin,
    ValidateLawPathsMixin,
):
    """Validation, review, and route helper boundary for CompilationContext."""

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
            ("output schema declaration", unit.output_schemas_by_name),
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

    def _build_output_schema_payload_rows(
        self,
        *,
        schema_data: dict[str, object],
    ) -> tuple[tuple[str, ...], ...]:
        properties = schema_data.get("properties")
        if not isinstance(properties, dict):
            return ()
        required_names = schema_data.get("required")
        required_set = set(required_names) if isinstance(required_names, list) else set()
        rows: list[tuple[str, ...]] = []
        for field_name, field_schema in properties.items():
            if not isinstance(field_schema, dict):
                continue
            stripped_schema, null_allowed = self._strip_nullable_json_schema(
                field_schema,
                root_schema=schema_data,
            )
            rows.append(
                (
                    f"`{field_name}`",
                    self._json_schema_type_label(
                        stripped_schema,
                        root_schema=schema_data,
                    ),
                    "Yes" if field_name in required_set else "No",
                    "Yes" if null_allowed else "No",
                    self._json_schema_meaning(
                        field_schema,
                        root_schema=schema_data,
                    ),
                )
            )
        return tuple(rows)

    def _json_schema_type_label(
        self,
        field_schema: dict[str, object],
        *,
        root_schema: dict[str, object],
    ) -> str:
        resolved_schema = self._resolve_local_json_schema_refs(
            field_schema,
            root_schema=root_schema,
        )
        if "anyOf" in resolved_schema:
            any_of = resolved_schema.get("anyOf")
            if isinstance(any_of, list):
                labels = [
                    self._json_schema_type_label(
                        branch,
                        root_schema=root_schema,
                    )
                    for branch in any_of
                    if isinstance(branch, dict) and not self._json_schema_is_null_only(branch)
                ]
                labels = [label for label in labels if label]
                return " | ".join(labels) if labels else "value"
        schema_type = resolved_schema.get("type")
        if isinstance(schema_type, list):
            labels = []
            for item in schema_type:
                if item == "array":
                    labels.append(
                        self._json_schema_array_type_label(
                            field_schema,
                            root_schema=root_schema,
                        )
                    )
                    continue
                labels.append("null" if item == "null" else str(item))
            return " | ".join(labels)
        if isinstance(schema_type, str):
            if schema_type == "array":
                return self._json_schema_array_type_label(
                    field_schema,
                    root_schema=root_schema,
                )
            return schema_type
        if "enum" in resolved_schema and isinstance(resolved_schema["enum"], list):
            return "enum"
        return "value"

    def _json_schema_array_type_label(
        self,
        field_schema: dict[str, object],
        *,
        root_schema: dict[str, object],
    ) -> str:
        resolved_schema = self._resolve_local_json_schema_refs(
            field_schema,
            root_schema=root_schema,
        )
        items = resolved_schema.get("items")
        if isinstance(items, dict):
            item_label = self._json_schema_type_label(items, root_schema=root_schema)
            return f"array<{item_label}>"
        return "array"

    def _json_schema_meaning(
        self,
        field_schema: dict[str, object],
        *,
        root_schema: dict[str, object],
    ) -> str:
        resolved_schema = self._resolve_local_json_schema_refs(
            field_schema,
            root_schema=root_schema,
        )
        description = field_schema.get("description")
        if not isinstance(description, str) or not description.strip():
            description = resolved_schema.get("description")
        if isinstance(description, str) and description.strip():
            return description.strip()
        enum_values = resolved_schema.get("enum")
        if isinstance(enum_values, list) and enum_values:
            rendered = ", ".join(f"`{value}`" for value in enum_values)
            return f"One of {rendered}."
        return ""

    def _strip_nullable_json_schema(
        self,
        field_schema: dict[str, object],
        *,
        root_schema: dict[str, object],
    ) -> tuple[dict[str, object], bool]:
        if "anyOf" in field_schema:
            any_of = field_schema.get("anyOf")
            if isinstance(any_of, list):
                non_null = [
                    branch for branch in any_of
                    if isinstance(branch, dict) and not self._json_schema_is_null_only(branch)
                ]
                null_allowed = len(non_null) != len(any_of)
                if len(non_null) == 1:
                    outer = {
                        key: value
                        for key, value in field_schema.items()
                        if key != "anyOf"
                    }
                    return ({**outer, **non_null[0]} if outer else non_null[0], null_allowed)
                return (field_schema, null_allowed)

        schema_type = field_schema.get("type")
        if isinstance(schema_type, list) and "null" in schema_type:
            non_null = [item for item in schema_type if item != "null"]
            if len(non_null) == 1:
                return ({**field_schema, "type": non_null[0]}, True)
            return ({**field_schema, "type": non_null}, True)
        return (field_schema, False)

    def _resolve_local_json_schema_refs(
        self,
        field_schema: dict[str, object],
        *,
        root_schema: dict[str, object],
    ) -> dict[str, object]:
        ref = field_schema.get("$ref")
        if not isinstance(ref, str) or not ref.startswith("#/"):
            return field_schema
        current: object = root_schema
        for part in ref[2:].split("/"):
            key = part.replace("~1", "/").replace("~0", "~")
            if not isinstance(current, dict) or key not in current:
                return field_schema
            current = current[key]
        if not isinstance(current, dict):
            return field_schema
        return current

    def _json_schema_is_null_only(self, field_schema: dict[str, object]) -> bool:
        schema_type = field_schema.get("type")
        if schema_type == "null":
            return True
        if isinstance(schema_type, list):
            return all(item == "null" for item in schema_type)
        return False

    def _validate_final_output_lowered_schema(
        self,
        schema_data: dict[str, object],
        *,
        owner_label: str,
    ) -> None:
        try:
            validate_lowered_output_schema(schema_data, owner_label=owner_label)
        except OutputSchemaValidationError as exc:
            raise CompileError(str(exc)) from exc

    def _validate_final_output_example_instance(
        self,
        example_instance: object,
        schema_data: dict[str, object],
        *,
        owner_label: str,
    ) -> None:
        try:
            validate_output_example_instance(
                example_instance,
                schema_data,
                owner_label=owner_label,
            )
        except OutputSchemaValidationError as exc:
            raise CompileError(str(exc)) from exc

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

    def _read_required_final_output_json_object_text(
        self,
        unit: IndexedUnit,
        relative_path: str,
        *,
        owner_label: str,
    ) -> str:
        text = self._read_required_final_output_support_text(
            unit,
            relative_path,
            owner_label=owner_label,
        )
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise CompileError(
                "E216 final_output example file must contain valid JSON object in "
                f"{owner_label}: {relative_path}"
            ) from exc
        if not isinstance(payload, dict):
            raise CompileError(
                "E216 final_output example file must contain valid JSON object in "
                f"{owner_label}: {relative_path}"
            )
        return text

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
