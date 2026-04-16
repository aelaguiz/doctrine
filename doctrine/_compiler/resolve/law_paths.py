from __future__ import annotations

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.constants import _REVIEW_VERDICT_TEXT, _SCHEMA_FAMILY_TITLES
from doctrine._compiler.naming import _name_ref_from_dotted_name
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    ContractBinding,
    IndexedUnit,
    LawBranch,
    ResolvedLawPath,
    SchemaFamilyTarget,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveLawPathsMixin:
    """Enum, match, and law-path resolution helpers for ResolveMixin."""

    def _law_path_wrong_kind_diagnostic(
        self,
        *,
        unit: IndexedUnit,
        source_span: model.SourceSpan | None,
        owner_label: str,
        statement_label: str,
        allowed_text: str,
        dotted_path: str,
    ) -> CompileError:
        if statement_label == "current artifact":
            return compile_error(
                code="E335",
                summary="Current artifact target has wrong kind",
                detail=(
                    f"Current-artifact target `{dotted_path}` must resolve to a declared or "
                    f"bound concrete-turn input or output in {owner_label}."
                ),
                path=unit.prompt_file.source_path,
                source_span=source_span,
            )
        if statement_label == "own only":
            return compile_error(
                code="E352",
                summary="Owned scope target is unknown",
                detail=(
                    f"Owned scope target `{dotted_path}` must resolve to a declared or bound "
                    f"concrete-turn input or output or a declared schema family in "
                    f"{owner_label}."
                ),
                path=unit.prompt_file.source_path,
                source_span=source_span,
            )
        if statement_label.startswith("preserve "):
            return compile_error(
                code="E355",
                summary="Preserve target is unknown",
                detail=(
                    f"`{statement_label}` target `{dotted_path}` must resolve to a "
                    f"{allowed_text} in {owner_label}."
                ),
                path=unit.prompt_file.source_path,
                source_span=source_span,
            )
        if statement_label == "invalidate":
            return compile_error(
                code="E373",
                summary="Invalidation target is unknown",
                detail=(
                    f"Invalidation target `{dotted_path}` must resolve to a declared or bound "
                    f"concrete-turn input, output, or schema group in {owner_label}."
                ),
                path=unit.prompt_file.source_path,
                source_span=source_span,
            )
        return compile_error(
            code="E299",
            summary="Compile failure",
            detail=(
                f"{statement_label} target must resolve to a {allowed_text} in "
                f"{owner_label}: {dotted_path}"
            ),
            path=unit.prompt_file.source_path,
            source_span=source_span,
        )

    def _resolve_constant_enum_member(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if isinstance(expr, str):
            return expr
        if isinstance(expr, model.ExprRef) and self._expr_ref_matches_review_verdict(expr):
            return _REVIEW_VERDICT_TEXT[expr.parts[1]]
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 2:
            return None
        name_ref = _name_ref_from_dotted_name(".".join(expr.parts[:-1]))
        enum_decl = self._try_resolve_enum_decl(name_ref, unit=unit)
        if enum_decl is None:
            return None
        member = next((member for member in enum_decl.members if member.key == expr.parts[-1]), None)
        if member is None:
            return None
        return member.value

    def _resolve_match_enum_decl(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> model.EnumDecl | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        mode_stmt = mode_bindings.get(expr.parts[0])
        if mode_stmt is None:
            return None
        enum_unit, enum_decl = self._resolve_decl_ref(
            mode_stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        _ = enum_unit
        return enum_decl

    def _resolve_fixed_match_value(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: LawBranch,
    ) -> str | None:
        if not isinstance(expr, model.ExprRef):
            return None
        expr_parts = tuple(expr.parts)
        for bound_parts, bound_value in reversed(branch.match_bindings):
            if bound_parts == expr_parts:
                return bound_value
        if len(expr.parts) != 1:
            return None
        for mode_stmt in reversed(branch.mode_bindings):
            if mode_stmt.name == expr.parts[0]:
                return self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)
        return None

    def _resolve_match_case_fixed_value(
        self,
        stmt: model.MatchStmt,
        case: model.MatchArm,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if case.head is not None:
            return self._resolve_constant_enum_member(case.head, unit=unit)
        if not isinstance(stmt.expr, model.ExprRef):
            return None

        enum_identity: tuple[tuple[str, ...], str] | None = None
        explicit_values: set[str] = set()
        for candidate in stmt.cases:
            if candidate.head is None:
                continue
            if not isinstance(candidate.head, model.ExprRef):
                return None
            identity = self._resolve_enum_member_identity(candidate.head, unit=unit)
            if identity is None:
                return None
            candidate_identity = (identity[0], identity[1])
            if enum_identity is None:
                enum_identity = candidate_identity
            elif candidate_identity != enum_identity:
                return None
            value = self._resolve_constant_enum_member(candidate.head, unit=unit)
            if value is None:
                return None
            explicit_values.add(value)

        if enum_identity is None:
            return None

        enum_unit, enum_decl = self._resolve_decl_ref(
            model.NameRef(
                module_parts=enum_identity[0],
                declaration_name=enum_identity[1],
            ),
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        _ = enum_unit
        remaining = tuple(
            member.value for member in enum_decl.members if member.value not in explicit_values
        )
        if len(remaining) != 1:
            return None
        return remaining[0]

    def _resolve_law_path(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        matches: list[ResolvedLawPath] = []
        if agent_contract is not None:
            matches.extend(
                self._resolve_bound_law_matches(
                    path,
                    agent_contract=agent_contract,
                    allowed_kinds=allowed_kinds,
                )
            )
        for split_index in range(1, len(path.parts) + 1):
            ref = model.NameRef(
                module_parts=path.parts[: split_index - 1],
                declaration_name=path.parts[split_index - 1],
            )
            try:
                lookup_targets = self._decl_lookup_targets(ref, unit=unit)
            except CompileError:
                continue
            remainder = path.parts[split_index:]
            for lookup_target in lookup_targets:
                lookup_unit = lookup_target.unit
                target_name = lookup_target.declaration_name
                if "input" in allowed_kinds:
                    input_decl = lookup_unit.inputs_by_name.get(target_name)
                    if input_decl is not None:
                        matches.append(
                            ResolvedLawPath(
                                unit=lookup_unit,
                                decl=input_decl,
                                remainder=remainder,
                                wildcard=path.wildcard,
                            )
                        )
                if "output" in allowed_kinds:
                    output_decl = self._resolve_local_output_decl(target_name, unit=lookup_unit)
                    if output_decl is not None:
                        matches.append(
                            ResolvedLawPath(
                                unit=lookup_unit,
                                decl=output_decl,
                                remainder=remainder,
                                wildcard=path.wildcard,
                            )
                        )
                if "enum" in allowed_kinds:
                    enum_decl = lookup_unit.enums_by_name.get(target_name)
                    if enum_decl is not None:
                        matches.append(
                            ResolvedLawPath(
                                unit=lookup_unit,
                                decl=enum_decl,
                                remainder=remainder,
                                wildcard=path.wildcard,
                            )
                        )
                if "grounding" in allowed_kinds:
                    grounding_decl = lookup_unit.groundings_by_name.get(target_name)
                    if grounding_decl is not None:
                        matches.append(
                            ResolvedLawPath(
                                unit=lookup_unit,
                                decl=grounding_decl,
                                remainder=remainder,
                                wildcard=path.wildcard,
                            )
                        )
                if "schema_family" in allowed_kinds:
                    schema_decl = lookup_unit.schemas_by_name.get(target_name)
                    if schema_decl is not None and remainder:
                        resolved_schema = self._resolve_schema_decl(schema_decl, unit=lookup_unit)
                        family_items_by_key = {
                            "sections": resolved_schema.sections,
                            "gates": resolved_schema.gates,
                            "artifacts": resolved_schema.artifacts,
                            "groups": resolved_schema.groups,
                        }
                        family_items = family_items_by_key.get(remainder[0])
                        if family_items is not None:
                            matches.append(
                                ResolvedLawPath(
                                    unit=lookup_unit,
                                    decl=SchemaFamilyTarget(
                                        family_key=remainder[0],
                                        title=_SCHEMA_FAMILY_TITLES[remainder[0]],
                                        items=family_items,
                                    ),
                                    remainder=remainder[1:],
                                    wildcard=path.wildcard,
                                )
                            )
                if "schema_group" in allowed_kinds:
                    schema_decl = lookup_unit.schemas_by_name.get(target_name)
                    if schema_decl is not None and len(remainder) >= 2 and remainder[0] == "groups":
                        resolved_schema = self._resolve_schema_decl(schema_decl, unit=lookup_unit)
                        group = next(
                            (item for item in resolved_schema.groups if item.key == remainder[1]),
                            None,
                        )
                        if group is not None:
                            matches.append(
                                ResolvedLawPath(
                                    unit=lookup_unit,
                                    decl=group,
                                    remainder=remainder[2:],
                                    wildcard=path.wildcard,
                                )
                            )

        unique_matches: list[ResolvedLawPath] = []
        seen: set[tuple[tuple[str, ...], str, tuple[str, ...], str]] = set()
        for match in matches:
            key = self._law_path_match_key(match)
            if key in seen:
                continue
            seen.add(key)
            unique_matches.append(match)

        if len(unique_matches) == 1:
            return unique_matches[0]
        if len(unique_matches) > 1:
            choices = ", ".join(
                _dotted_decl_name(match.unit.module_parts, self._law_path_decl_identity(match.decl))
                for match in unique_matches
            )
            raise compile_error(
                code="E299",
                summary="Ambiguous law path",
                detail=(
                    f"Ambiguous {statement_label} path in {owner_label}: "
                    f"{'.'.join(path.parts)} matches {choices}"
                ),
                path=unit.prompt_file.source_path,
                source_span=path.source_span,
            )

        allowed_text = self._law_path_allowed_text(
            allowed_kinds,
            agent_contract=agent_contract,
        )
        raise self._law_path_wrong_kind_diagnostic(
            unit=unit,
            source_span=path.source_span,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_text=allowed_text,
            dotted_path=".".join(path.parts),
        )

    def _resolve_bound_law_matches(
        self,
        path: model.LawPath,
        *,
        agent_contract: AgentContract,
        allowed_kinds: tuple[str, ...],
    ) -> tuple[ResolvedLawPath, ...]:
        for split_index in range(len(path.parts), 0, -1):
            prefix = path.parts[:split_index]
            candidates: list[ContractBinding] = []
            if "input" in allowed_kinds:
                binding = agent_contract.input_bindings_by_path.get(prefix)
                if binding is not None:
                    candidates.append(binding)
            if "output" in allowed_kinds:
                binding = agent_contract.output_bindings_by_path.get(prefix)
                if binding is not None:
                    candidates.append(binding)
            if not candidates:
                continue
            return tuple(
                ResolvedLawPath(
                    unit=binding.artifact.unit,
                    decl=binding.artifact.decl,
                    remainder=path.parts[len(binding.binding_path) :],
                    wildcard=path.wildcard,
                    binding_path=binding.binding_path,
                )
                for binding in candidates
            )
        return ()
