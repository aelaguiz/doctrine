from __future__ import annotations

from doctrine import model
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
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        for mode_stmt in reversed(branch.mode_bindings):
            if mode_stmt.name == expr.parts[0]:
                return self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)
        return None

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
                lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
            except CompileError:
                continue
            remainder = path.parts[split_index:]
            if "input" in allowed_kinds:
                input_decl = lookup_unit.inputs_by_name.get(ref.declaration_name)
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
                output_decl = lookup_unit.outputs_by_name.get(ref.declaration_name)
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
                enum_decl = lookup_unit.enums_by_name.get(ref.declaration_name)
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
                grounding_decl = lookup_unit.groundings_by_name.get(ref.declaration_name)
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
                schema_decl = lookup_unit.schemas_by_name.get(ref.declaration_name)
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
                schema_decl = lookup_unit.schemas_by_name.get(ref.declaration_name)
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
            raise CompileError(
                f"Ambiguous {statement_label} path in {owner_label}: "
                f"{'.'.join(path.parts)} matches {choices}"
            )

        allowed_text = self._law_path_allowed_text(
            allowed_kinds,
            agent_contract=agent_contract,
        )
        raise CompileError(
            f"{statement_label} target must resolve to a {allowed_text} in {owner_label}: "
            f"{'.'.join(path.parts)}"
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
