from __future__ import annotations

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.resolved_types import (
    AgentContract,
    CanonicalLawPath,
    CompileError,
    IndexedUnit,
    ResolvedLawPath,
    ResolvedSchemaArtifact,
    ResolvedSchemaGroup,
    SchemaFamilyTarget,
)


class ValidateLawPathsMixin:
    """Law-path and registry helpers for ValidateMixin."""

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
            return container.wildcard or not path.wildcard or container.wildcard == path.wildcard
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
            return tuple(artifacts_by_key[key] for key in group.members if key in artifacts_by_key)
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
        if isinstance(stmt, model.ActiveWhenStmt):
            return "active when"
        if isinstance(stmt, model.ModeStmt):
            return "mode"
        if isinstance(stmt, model.MatchStmt):
            return "match"
        if isinstance(stmt, model.RouteFromStmt):
            return "route_from"
        if isinstance(stmt, model.WhenStmt):
            return "when"
        if isinstance(stmt, model.CurrentArtifactStmt):
            return "current artifact"
        if isinstance(stmt, model.CurrentNoneStmt):
            return "current none"
        if isinstance(stmt, model.MustStmt):
            return "must"
        if isinstance(stmt, model.OwnOnlyStmt):
            return "own only"
        if isinstance(stmt, model.PreserveStmt):
            return f"preserve {stmt.kind}"
        if isinstance(stmt, model.SupportOnlyStmt):
            return "support_only"
        if isinstance(stmt, model.IgnoreStmt):
            return "ignore"
        if isinstance(stmt, model.ForbidStmt):
            return "forbid"
        if isinstance(stmt, model.InvalidateStmt):
            return "invalidate"
        if isinstance(stmt, model.StopStmt):
            return "stop"
        if isinstance(stmt, model.LawRouteStmt):
            return "route"
        return type(stmt).__name__

    def _split_record_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        scalar_keys: set[str] | None = None,
        section_keys: set[str] | None = None,
        owner_label: str,
    ) -> tuple[
        dict[str, model.RecordScalar],
        dict[str, model.RecordSection],
        tuple[model.AnyRecordItem, ...],
    ]:
        scalar_keys = scalar_keys or set()
        section_keys = section_keys or set()
        scalar_items: dict[str, model.RecordScalar] = {}
        section_items: dict[str, model.RecordSection] = {}
        extras: list[model.AnyRecordItem] = []

        for item in items:
            if isinstance(item, model.RecordScalar) and item.key in scalar_keys:
                if item.key in scalar_items:
                    raise compile_error(
                        code="E284",
                        summary="Duplicate record key",
                        detail=f"Record owner `{owner_label}` repeats key `{item.key}`.",
                        source_span=item.source_span,
                    )
                scalar_items[item.key] = item
                continue
            if isinstance(item, model.RecordSection) and item.key in section_keys:
                if item.key in section_items:
                    raise compile_error(
                        code="E284",
                        summary="Duplicate record key",
                        detail=f"Record owner `{owner_label}` repeats key `{item.key}`.",
                        source_span=item.source_span,
                    )
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
            target_unit, decl = self._resolve_decl_ref(
                ref,
                unit=unit,
                registry_name="route_onlys_by_name",
                missing_label="route_only declaration",
            )
        except CompileError:
            return None
        return target_unit, decl

    def _try_resolve_grounding_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.GroundingDecl] | None:
        try:
            target_unit, decl = self._resolve_decl_ref(
                ref,
                unit=unit,
                registry_name="groundings_by_name",
                missing_label="grounding declaration",
            )
        except CompileError:
            return None
        return target_unit, decl

    def _ref_exists_in_registry(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
    ) -> bool:
        try:
            lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        except CompileError:
            return False
        for lookup_target in lookup_targets:
            registry = getattr(lookup_target.unit, registry_name)
            if registry.get(lookup_target.declaration_name) is not None:
                return True
        return False
