from __future__ import annotations

import re
from dataclasses import dataclass, field, replace

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.indexing import unit_declarations
from doctrine._compiler.resolved_types import CompileError, IndexedUnit
from doctrine._compiler.support import dotted_decl_name


@dataclass(slots=True)
class _NodeExpansion:
    start_stages: tuple[str, ...] = ()
    terminal_stages: tuple[str, ...] = ()
    reached_stage_names: set[str] = field(default_factory=set)
    reached_flow_names: set[str] = field(default_factory=set)
    stage_edges: list[model.ResolvedSkillGraphStageEdge] = field(default_factory=list)
    stage_reaching_flows: dict[str, set[str]] = field(default_factory=dict)
    stage_reaching_flow_identities: dict[str, set[str]] = field(default_factory=dict)


@dataclass(slots=True)
class _FlowExpansion:
    graph_flow: model.ResolvedSkillGraphFlow
    owner_unit: IndexedUnit
    start_stages: tuple[str, ...]
    terminal_stages: tuple[str, ...]
    reached_stage_names: tuple[str, ...]
    reached_flow_names: tuple[str, ...]
    stage_edges: tuple[model.ResolvedSkillGraphStageEdge, ...]
    stage_reaching_flows: dict[str, tuple[str, ...]]
    stage_reaching_flow_identities: dict[str, tuple[str, ...]]


_CHECKED_SKILL_MENTION_RE = re.compile(
    r"\{\{skill:(?P<target>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\}\}"
)


def _truthy(value: str | None) -> bool:
    return value is not None and value.strip().casefold() in {"1", "true", "yes", "on"}


class ResolveSkillGraphsMixin:
    """Top-level skill_graph resolution helpers for ResolveMixin."""

    def _resolved_skill_graph_cache(self):
        cache = getattr(self, "_resolved_skill_graph_decl_cache", None)
        if cache is None:
            cache = {}
            object.__setattr__(self, "_resolved_skill_graph_decl_cache", cache)
        return cache

    def _skill_graph_error(
        self,
        *,
        detail: str,
        unit: IndexedUnit,
        source_span,
        hints: tuple[str, ...] = (),
    ) -> CompileError:
        return compile_error(
            code="E562",
            summary="Invalid skill graph",
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=source_span,
            hints=hints,
        )

    def _skill_relation_error(
        self,
        *,
        detail: str,
        unit: IndexedUnit,
        source_span,
        hints: tuple[str, ...] = (),
    ) -> CompileError:
        return compile_error(
            code="E566",
            summary="Invalid skill relation",
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=source_span,
            hints=hints,
        )

    def _check_public_graph_name_collision(
        self,
        *,
        owner_label: str,
        kind: str,
        public_name: str,
        existing_unit: IndexedUnit | None,
        owner_unit: IndexedUnit,
        source_span,
        fallback_span,
        keyed_by: str | None = None,
        plural_kind: str | None = None,
    ) -> None:
        if (
            existing_unit is None
            or existing_unit.module_parts == owner_unit.module_parts
        ):
            return
        existing_label = dotted_decl_name(
            existing_unit.module_parts,
            public_name,
        )
        new_label = dotted_decl_name(owner_unit.module_parts, public_name)
        keyed_by = keyed_by or f"{kind} name"
        plural_kind = plural_kind or f"{kind}s"
        raise self._skill_graph_error(
            detail=(
                f"Skill graph `{owner_label}` reaches {kind} name "
                f"`{public_name}` from both `{existing_label}` and "
                f"`{new_label}`. Public graph artifacts are keyed by "
                f"{keyed_by}, so this graph cannot include both."
            ),
            unit=owner_unit,
            source_span=source_span or fallback_span,
            hints=(
                f"Rename one {kind}, or keep one of the same-named "
                f"{plural_kind} outside this graph.",
            ),
        )

    def _resolve_skill_graph_decl(
        self,
        graph_decl: model.SkillGraphDecl,
        *,
        unit: IndexedUnit,
    ) -> model.ResolvedSkillGraph:
        cache = self._resolved_skill_graph_cache()
        cache_key = (id(unit), graph_decl.name)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        owner_label = (
            ".".join((*unit.module_parts, graph_decl.name))
            if unit.module_parts
            else graph_decl.name
        )
        purpose_items: list[model.SkillGraphPurposeItem] = []
        roots_items: list[model.SkillGraphRootsItem] = []
        sets_items: list[model.SkillGraphSetsItem] = []
        recovery_items: list[model.SkillGraphRecoveryItem] = []
        policy_items: list[model.SkillGraphPolicyItem] = []
        views_items: list[model.SkillGraphViewsItem] = []
        for item in graph_decl.items:
            if isinstance(item, model.SkillGraphPurposeItem):
                purpose_items.append(item)
            elif isinstance(item, model.SkillGraphRootsItem):
                roots_items.append(item)
            elif isinstance(item, model.SkillGraphSetsItem):
                sets_items.append(item)
            elif isinstance(item, model.SkillGraphRecoveryItem):
                recovery_items.append(item)
            elif isinstance(item, model.SkillGraphPolicyItem):
                policy_items.append(item)
            elif isinstance(item, model.SkillGraphViewsItem):
                views_items.append(item)

        for label, items in (
            ("purpose", purpose_items),
            ("roots", roots_items),
            ("sets", sets_items),
            ("recovery", recovery_items),
            ("policy", policy_items),
            ("views", views_items),
        ):
            if len(items) > 1:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares `{label}:` more "
                        "than once."
                    ),
                    unit=unit,
                    source_span=items[1].source_span or graph_decl.source_span,
                    hints=(f"Keep one `{label}:` block per skill graph.",),
                )

        if not purpose_items:
            raise self._skill_graph_error(
                detail=f"Skill graph `{owner_label}` is missing required `purpose:`.",
                unit=unit,
                source_span=graph_decl.source_span,
                hints=("Add `purpose: \"...\"` to state what this graph owns.",),
            )
        if not roots_items:
            raise self._skill_graph_error(
                detail=f"Skill graph `{owner_label}` is missing required `roots:`.",
                unit=unit,
                source_span=graph_decl.source_span,
                hints=(
                    "Add one or more `flow <Ref>` or `stage <Ref>` lines under `roots:`.",
                ),
            )

        graph_sets = self._resolve_skill_graph_sets(
            sets_items[0] if sets_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )
        set_names = {entry.name for entry in graph_sets}
        graph_policies = self._resolve_skill_graph_policies(
            policy_items[0] if policy_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )

        def policy_enabled(action: str, key: str) -> bool:
            return any(
                policy.action == action and policy.key == key
                for policy in graph_policies
            )

        allow_unbound_edges = policy_enabled("allow", "unbound_edges")
        allow_graph_cycles = policy_enabled("dag", "allow_cycle")
        require_checked_skill_mentions = policy_enabled(
            "require",
            "checked_skill_mentions",
        )
        require_relation_reason = policy_enabled("require", "relation_reason")
        require_branch_coverage = policy_enabled("require", "branch_coverage")
        warn_branch_coverage = policy_enabled("warn", "branch_coverage_incomplete")
        graph_warnings: list[model.ResolvedSkillGraphWarning] = []

        def warn_enabled(key: str) -> bool:
            return policy_enabled("warn", key)

        def append_warning(
            *,
            code: str,
            policy_key: str,
            summary: str,
            owner_kind: str,
            owner_name: str,
            detail: str,
            source_span,
        ) -> None:
            if not warn_enabled(policy_key):
                return
            graph_warnings.append(
                model.ResolvedSkillGraphWarning(
                    code=code,
                    policy_key=policy_key,
                    summary=summary,
                    owner_kind=owner_kind,
                    owner_name=owner_name,
                    detail=detail,
                    source_span=source_span,
                )
            )

        def append_branch_coverage_warning(
            flow_name: str,
            source_name: str,
            enum_name: str,
            missing_members: tuple[str, ...],
            source_span,
        ) -> None:
            missing_text = ", ".join(missing_members)
            append_warning(
                code="W205",
                policy_key="branch_coverage_incomplete",
                summary="Branch coverage is incomplete",
                owner_kind="skill_flow",
                owner_name=flow_name,
                detail=(
                    f"Skill flow `{flow_name}` source `{source_name}` "
                    f"branches on enum `{enum_name}` but does not cover "
                    f"member(s): {missing_text}."
                ),
                source_span=source_span or graph_decl.source_span,
            )

        graph_views = self._resolve_skill_graph_views(
            views_items[0] if views_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )
        graph_recovery = self._resolve_skill_graph_recovery(
            recovery_items[0] if recovery_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )
        graph_roots, root_decls = self._resolve_skill_graph_roots(
            roots_items[0],
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )

        flow_cache: dict[tuple[int, str], _FlowExpansion] = {}
        flow_stack: list[tuple[int, str]] = []
        reached_stage_order: list[str] = []
        reached_stage_seen: set[str] = set()
        reached_stage_units: dict[str, IndexedUnit] = {}
        reached_stage_decls: dict[str, model.StageDecl] = {}
        reached_flow_order: list[str] = []
        reached_flow_seen: set[str] = set()
        reached_flow_units: dict[str, IndexedUnit] = {}
        reached_skill_units: dict[str, IndexedUnit] = {}
        reached_skill_decls: dict[str, model.SkillDecl] = {}
        processed_relation_skills: set[tuple[int, str]] = set()
        skill_relation_seen: set[tuple[str, str, str, str | None]] = set()
        skill_relations: list[model.ResolvedSkillGraphSkillRelation] = []
        reached_package_units: dict[str, IndexedUnit] = {}
        reached_package_decls: dict[str, model.SkillPackageDecl] = {}
        reached_artifact_units: dict[str, IndexedUnit] = {}
        reached_artifact_decls: dict[str, model.ArtifactDecl] = {}
        reached_artifact_path_family_units: dict[tuple[str, str], IndexedUnit] = {}
        reached_receipt_units: dict[str, IndexedUnit] = {}
        reached_receipt_decls: dict[str, model.ReceiptDecl] = {}
        aggregate_edges: list[model.ResolvedSkillGraphStageEdge] = []
        aggregate_stage_reaching_flows: dict[str, set[str]] = {}
        aggregate_stage_reaching_flow_identities: dict[str, set[str]] = {}

        def fail_on_public_name_collision(
            *,
            kind: str,
            public_name: str,
            existing_unit: IndexedUnit | None,
            owner_unit: IndexedUnit,
            source_span,
        ) -> None:
            self._check_public_graph_name_collision(
                owner_label=owner_label,
                kind=kind,
                public_name=public_name,
                existing_unit=existing_unit,
                owner_unit=owner_unit,
                source_span=source_span,
                fallback_span=graph_decl.source_span,
            )

        def remember_stage(
            stage_name: str,
            *,
            owner_unit: IndexedUnit,
            stage_decl: model.StageDecl,
        ) -> None:
            fail_on_public_name_collision(
                kind="stage",
                public_name=stage_name,
                existing_unit=reached_stage_units.get(stage_name),
                owner_unit=owner_unit,
                source_span=stage_decl.source_span,
            )
            if stage_name not in reached_stage_seen:
                reached_stage_seen.add(stage_name)
                reached_stage_order.append(stage_name)
            reached_stage_units.setdefault(stage_name, owner_unit)
            reached_stage_decls.setdefault(stage_name, stage_decl)

        def remember_flow(
            flow_name: str,
            *,
            owner_unit: IndexedUnit,
            source_span,
        ) -> None:
            fail_on_public_name_collision(
                kind="skill_flow",
                public_name=flow_name,
                existing_unit=reached_flow_units.get(flow_name),
                owner_unit=owner_unit,
                source_span=source_span,
            )
            if flow_name not in reached_flow_seen:
                reached_flow_seen.add(flow_name)
                reached_flow_order.append(flow_name)
            reached_flow_units.setdefault(flow_name, owner_unit)

        def remember_receipt(
            receipt_name: str,
            *,
            owner_unit: IndexedUnit,
            receipt_decl: model.ReceiptDecl,
        ) -> None:
            fail_on_public_name_collision(
                kind="receipt",
                public_name=receipt_name,
                existing_unit=reached_receipt_units.get(receipt_name),
                owner_unit=owner_unit,
                source_span=receipt_decl.source_span,
            )
            reached_receipt_units.setdefault(receipt_name, owner_unit)
            reached_receipt_decls.setdefault(receipt_name, receipt_decl)

        def remember_artifact(
            artifact_name: str,
            *,
            owner_unit: IndexedUnit,
            artifact_decl: model.ArtifactDecl,
        ) -> None:
            fail_on_public_name_collision(
                kind="artifact",
                public_name=artifact_name,
                existing_unit=reached_artifact_units.get(artifact_name),
                owner_unit=owner_unit,
                source_span=artifact_decl.source_span,
            )
            reached_artifact_units.setdefault(artifact_name, owner_unit)
            reached_artifact_decls.setdefault(artifact_name, artifact_decl)

        def remember_skill(
            skill_name: str,
            *,
            owner_unit: IndexedUnit,
            skill_decl: model.SkillDecl,
        ) -> None:
            fail_on_public_name_collision(
                kind="skill",
                public_name=skill_name,
                existing_unit=reached_skill_units.get(skill_name),
                owner_unit=owner_unit,
                source_span=skill_decl.source_span,
            )
            reached_skill_units.setdefault(skill_name, owner_unit)
            reached_skill_decls.setdefault(skill_name, skill_decl)
            if skill_decl.package_link is None:
                process_skill_relations(
                    skill_name,
                    owner_unit=owner_unit,
                    skill_decl=skill_decl,
                )
                return
            package_unit, package_decl = self._resolve_skill_package_id(
                skill_decl.package_link.package_id,
                unit=owner_unit,
                owner_label=f"skill `{skill_decl.name}` package link",
                source_span=skill_decl.package_link.source_span,
            )
            package_id = skill_decl.package_link.package_id
            self._check_public_graph_name_collision(
                owner_label=owner_label,
                kind="skill package",
                public_name=package_id,
                existing_unit=reached_package_units.get(package_id),
                owner_unit=package_unit,
                source_span=skill_decl.package_link.source_span,
                fallback_span=graph_decl.source_span,
                keyed_by="package id",
                plural_kind="skill packages",
            )
            reached_package_units.setdefault(package_id, package_unit)
            reached_package_decls.setdefault(package_id, package_decl)
            process_skill_relations(
                skill_name,
                owner_unit=owner_unit,
                skill_decl=skill_decl,
            )

        def process_skill_relations(
            skill_name: str,
            *,
            owner_unit: IndexedUnit,
            skill_decl: model.SkillDecl,
        ) -> None:
            relation_owner_key = (id(owner_unit), skill_name)
            if relation_owner_key in processed_relation_skills:
                return
            processed_relation_skills.add(relation_owner_key)
            for relation in skill_decl.relations:
                if relation.kind not in model.SKILL_RELATION_KINDS:
                    allowed = ", ".join(sorted(model.SKILL_RELATION_KINDS))
                    raise self._skill_relation_error(
                        detail=(
                            f"Skill `{skill_name}` declares relation kind "
                            f"`{relation.kind}`, but the closed value set is "
                            f"{{{allowed}}}."
                        ),
                        unit=owner_unit,
                        source_span=relation.source_span or skill_decl.source_span,
                        hints=("Use one of the shipped skill relation kinds.",),
                    )
                try:
                    target_unit, target_decl = self._resolve_decl_ref(
                        relation.target_ref,
                        unit=owner_unit,
                        registry_name="skills_by_name",
                        missing_label="skill declaration",
                    )
                except CompileError as exc:
                    dotted = self._dotted_ref(relation.target_ref)
                    raise self._skill_relation_error(
                        detail=(
                            f"Skill `{skill_name}` relation "
                            f"`{relation.kind} {dotted}` does not resolve to "
                            "a top-level `skill` declaration."
                        ),
                        unit=owner_unit,
                        source_span=relation.source_span or skill_decl.source_span,
                        hints=(
                            "Declare the target skill at the top level, or fix "
                            "the relation ref.",
                        ),
                    ) from exc
                if require_relation_reason and not relation.why:
                    raise self._skill_relation_error(
                        detail=(
                            f"Skill graph `{owner_label}` requires "
                            "`relation_reason`, but skill "
                            f"`{skill_name}` relation "
                            f"`{relation.kind} {target_decl.name}` has no "
                            "`why:` line."
                        ),
                        unit=owner_unit,
                        source_span=relation.source_span or skill_decl.source_span,
                        hints=("Add `why: \"...\"` under the relation.",),
                    )
                if not relation.why:
                    append_warning(
                        code="W210",
                        policy_key="relation_without_reason",
                        summary="Skill relation has no reason",
                        owner_kind="skill",
                        owner_name=skill_name,
                        detail=(
                            f"Relation `{relation.kind} {target_decl.name}` "
                            "does not declare `why:`."
                        ),
                        source_span=relation.source_span or skill_decl.source_span,
                    )
                remember_skill(
                    target_decl.name,
                    owner_unit=target_unit,
                    skill_decl=target_decl,
                )
                relation_why = (
                    None
                    if relation.why is None
                    else interpolate_checked_skill_mentions(
                        relation.why,
                        current_unit=owner_unit,
                        owner_text=(
                            f"skill `{skill_name}` relation "
                            f"`{relation.kind} {target_decl.name}`"
                        ),
                        source_span=relation.source_span or skill_decl.source_span,
                    )
                )
                relation_key = (
                    skill_name,
                    target_decl.name,
                    relation.kind,
                    relation_why,
                )
                if relation_key in skill_relation_seen:
                    continue
                skill_relation_seen.add(relation_key)
                skill_relations.append(
                    model.ResolvedSkillGraphSkillRelation(
                        source_skill_name=skill_name,
                        target_skill_name=target_decl.name,
                        kind=relation.kind,
                        why=relation_why,
                        source_span=relation.source_span,
                    )
                )

        def resolve_skill_ref_for_checked_mention(
            skill_name: str,
            *,
            current_unit: IndexedUnit,
            owner_text: str,
            source_span,
        ) -> tuple[IndexedUnit, model.SkillDecl] | None:
            ref = model.NameRef(
                module_parts=(),
                declaration_name=skill_name,
                source_span=source_span,
            )
            try:
                return self._resolve_decl_ref(
                    ref,
                    unit=current_unit,
                    registry_name="skills_by_name",
                    missing_label="skill declaration",
                )
            except CompileError:
                detail = (
                    f"{owner_text} references checked skill mention "
                    f"`{{{{skill:{skill_name}}}}}`, but no visible top-level "
                    "`skill` declaration has that name."
                )
                if require_checked_skill_mentions:
                    raise self._skill_graph_error(
                        detail=detail,
                        unit=current_unit,
                        source_span=source_span,
                        hints=("Declare the skill, import it, or fix the checked mention.",),
                    )
                append_warning(
                    code="W204",
                    policy_key="checked_skill_mention_unknown",
                    summary="Checked skill mention does not resolve",
                    owner_kind="text",
                    owner_name=owner_text,
                    detail=detail,
                    source_span=source_span,
                )
                return None

        def interpolate_checked_skill_mentions(
            text: str,
            *,
            current_unit: IndexedUnit,
            owner_text: str,
            source_span,
        ) -> str:
            if "{{skill:" not in text:
                return text

            def render_match(match: re.Match[str]) -> str:
                target_text = match.group("target")
                parts = target_text.split(".")
                skill_name = parts[0]
                projection = None if len(parts) == 1 else parts[1]
                if len(parts) > 2 or projection not in {None, "package", "purpose"}:
                    detail = (
                        f"{owner_text} references `{{{{skill:{target_text}}}}}`, "
                        "but checked skill mentions only allow "
                        "`{{skill:Name}}`, `{{skill:Name.package}}`, or "
                        "`{{skill:Name.purpose}}`."
                    )
                    if require_checked_skill_mentions:
                        raise self._skill_graph_error(
                            detail=detail,
                            unit=current_unit,
                            source_span=source_span,
                            hints=("Use one of the supported checked skill projections.",),
                        )
                    append_warning(
                        code="W204",
                        policy_key="checked_skill_mention_unknown",
                        summary="Checked skill mention projection is unknown",
                        owner_kind="text",
                        owner_name=owner_text,
                        detail=detail,
                        source_span=source_span,
                    )
                    return match.group(0)
                resolved = resolve_skill_ref_for_checked_mention(
                    skill_name,
                    current_unit=current_unit,
                    owner_text=owner_text,
                    source_span=source_span,
                )
                if resolved is None:
                    return match.group(0)
                target_unit, target_decl = resolved
                remember_skill(
                    target_decl.name,
                    owner_unit=target_unit,
                    skill_decl=target_decl,
                )
                if projection == "package":
                    if target_decl.package_link is None:
                        return ""
                    return target_decl.package_link.package_id
                if projection == "purpose":
                    return self._skill_decl_purpose(target_decl) or ""
                return target_decl.title

            return _CHECKED_SKILL_MENTION_RE.sub(render_match, text)

        def merge_node_expansion(dest: _NodeExpansion, src: _NodeExpansion) -> None:
            dest.reached_stage_names.update(src.reached_stage_names)
            dest.reached_flow_names.update(src.reached_flow_names)
            dest.stage_edges.extend(src.stage_edges)
            for stage_name, flow_names in src.stage_reaching_flows.items():
                dest.stage_reaching_flows.setdefault(stage_name, set()).update(flow_names)
            for stage_name, flow_ids in src.stage_reaching_flow_identities.items():
                dest.stage_reaching_flow_identities.setdefault(stage_name, set()).update(
                    flow_ids
                )

        def augment_with_parent_flow(
            expansion: _FlowExpansion,
            *,
            parent_flow_name: str,
            parent_flow_identity: str,
        ) -> _NodeExpansion:
            stage_reaching_flows = {
                stage_name: set(flow_names)
                for stage_name, flow_names in expansion.stage_reaching_flows.items()
            }
            stage_reaching_flow_identities = {
                stage_name: set(flow_ids)
                for stage_name, flow_ids in (
                    expansion.stage_reaching_flow_identities.items()
                )
            }
            for stage_name in expansion.reached_stage_names:
                stage_reaching_flows.setdefault(stage_name, set()).add(parent_flow_name)
                stage_reaching_flow_identities.setdefault(stage_name, set()).add(
                    parent_flow_identity
                )
            return _NodeExpansion(
                start_stages=expansion.start_stages,
                terminal_stages=expansion.terminal_stages,
                reached_stage_names=set(expansion.reached_stage_names),
                reached_flow_names=set(expansion.reached_flow_names),
                stage_edges=list(expansion.stage_edges),
                stage_reaching_flows=stage_reaching_flows,
                stage_reaching_flow_identities=stage_reaching_flow_identities,
            )

        def resolve_unit_for_module_parts(
            module_parts: tuple[str, ...],
            *,
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> IndexedUnit:
            if not module_parts or module_parts == current_unit.module_parts:
                return current_unit
            try:
                return self.session.load_module(module_parts)
            except CompileError as exc:
                dotted = ".".join(module_parts)
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} module `{dotted}` "
                        "does not resolve."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Import the module or fix the qualified ref.",),
                ) from exc

        def resolve_stage_by_name(
            stage_name: str,
            *,
            module_parts: tuple[str, ...],
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> tuple[IndexedUnit, model.StageDecl]:
            if module_parts:
                target_unit = resolve_unit_for_module_parts(
                    module_parts,
                    current_unit=current_unit,
                    source_span=source_span,
                    role=role,
                )
                stage_decl = unit_declarations(target_unit).stages_by_name.get(stage_name)
                if stage_decl is not None:
                    return target_unit, stage_decl
            ref = model.NameRef(
                module_parts=(),
                declaration_name=stage_name,
                source_span=source_span,
            )
            try:
                return self._resolve_decl_ref(
                    ref,
                    unit=current_unit,
                    registry_name="stages_by_name",
                    missing_label="stage declaration",
                )
            except CompileError as exc:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} stage `{stage_name}` "
                        "does not resolve to a top-level `stage` declaration."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Declare the stage at the top level, or fix the ref.",),
                ) from exc

        def resolve_flow_by_name(
            flow_name: str,
            *,
            module_parts: tuple[str, ...],
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> tuple[IndexedUnit, model.SkillFlowDecl]:
            if module_parts:
                target_unit = resolve_unit_for_module_parts(
                    module_parts,
                    current_unit=current_unit,
                    source_span=source_span,
                    role=role,
                )
                flow_decl = unit_declarations(target_unit).skill_flows_by_name.get(
                    flow_name
                )
                if flow_decl is not None:
                    return target_unit, flow_decl
            ref = model.NameRef(
                module_parts=(),
                declaration_name=flow_name,
                source_span=source_span,
            )
            try:
                return self._resolve_decl_ref(
                    ref,
                    unit=current_unit,
                    registry_name="skill_flows_by_name",
                    missing_label="skill_flow declaration",
                )
            except CompileError as exc:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} flow `{flow_name}` "
                        "does not resolve to a top-level `skill_flow` declaration."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Declare the flow at the top level, or fix the ref.",),
                ) from exc

        def resolve_receipt_by_name(
            receipt_name: str,
            *,
            module_parts: tuple[str, ...] = (),
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> tuple[IndexedUnit, model.ReceiptDecl]:
            if module_parts:
                target_unit = resolve_unit_for_module_parts(
                    module_parts,
                    current_unit=current_unit,
                    source_span=source_span,
                    role=role,
                )
                receipt_decl = unit_declarations(target_unit).receipts_by_name.get(
                    receipt_name
                )
                if receipt_decl is not None:
                    return target_unit, receipt_decl
            ref = model.NameRef(
                module_parts=(),
                declaration_name=receipt_name,
                source_span=source_span,
            )
            try:
                return self._resolve_receipt_ref(ref, unit=current_unit)
            except CompileError as exc:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} receipt `{receipt_name}` "
                        "does not resolve to a top-level `receipt` declaration."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Declare the receipt at the top level, or fix the ref.",),
                ) from exc

        def resolve_artifact_by_name(
            artifact_name: str,
            *,
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> tuple[IndexedUnit, model.ArtifactDecl]:
            ref = model.NameRef(
                module_parts=(),
                declaration_name=artifact_name,
                source_span=source_span,
            )
            try:
                return self._resolve_decl_ref(
                    ref,
                    unit=current_unit,
                    registry_name="artifacts_by_name",
                    missing_label="artifact declaration",
                )
            except CompileError as exc:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} artifact "
                        f"`{artifact_name}` does not resolve to a top-level "
                        "`artifact` declaration."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Declare the artifact at the top level, or fix the ref.",),
                ) from exc

        def resolve_artifact_decl(
            artifact_decl: model.ArtifactDecl,
            *,
            owner_unit: IndexedUnit,
        ) -> model.ResolvedSkillGraphArtifact:
            owner_items: list[model.ArtifactOwnerItem] = []
            path_family_items: list[model.ArtifactPathFamilyItem] = []
            scalars_by_key: dict[str, model.ArtifactScalarItem] = {}
            for item in artifact_decl.items:
                if isinstance(item, model.ArtifactOwnerItem):
                    owner_items.append(item)
                    continue
                if isinstance(item, model.ArtifactPathFamilyItem):
                    path_family_items.append(item)
                    continue
                if isinstance(item, model.ArtifactScalarItem):
                    if item.key in scalars_by_key:
                        raise self._skill_graph_error(
                            detail=(
                                f"Artifact `{artifact_decl.name}` declares "
                                f"`{item.key}:` more than once."
                            ),
                            unit=owner_unit,
                            source_span=item.source_span or artifact_decl.source_span,
                            hints=("Keep one value per artifact scalar field.",),
                        )
                    scalars_by_key[item.key] = item
            for label, items in (
                ("owner", owner_items),
                ("path_family", path_family_items),
            ):
                if len(items) > 1:
                    raise self._skill_graph_error(
                        detail=(
                            f"Artifact `{artifact_decl.name}` declares "
                            f"`{label}:` more than once."
                        ),
                        unit=owner_unit,
                        source_span=items[1].source_span or artifact_decl.source_span,
                        hints=(f"Keep one `{label}:` line per artifact.",),
                    )
            if not owner_items:
                raise self._skill_graph_error(
                    detail=(
                        f"Artifact `{artifact_decl.name}` is missing required "
                        "`owner:`."
                    ),
                    unit=owner_unit,
                    source_span=artifact_decl.source_span,
                    hints=("Add `owner: <StageRef>` so the graph knows who writes it.",),
                )
            try:
                owner_stage_unit, owner_stage_decl = self._resolve_decl_ref(
                    owner_items[0].stage_ref,
                    unit=owner_unit,
                    registry_name="stages_by_name",
                    missing_label="stage declaration",
                )
                _ = owner_stage_unit
            except CompileError as exc:
                dotted = self._dotted_ref(owner_items[0].stage_ref)
                raise self._skill_graph_error(
                    detail=(
                        f"Artifact `{artifact_decl.name}` owner `{dotted}` "
                        "does not resolve to a top-level `stage` declaration."
                    ),
                    unit=owner_unit,
                    source_span=owner_items[0].source_span or artifact_decl.source_span,
                    hints=("Declare the owner stage, or fix the artifact owner ref.",),
                ) from exc

            path_family_kind: str | None = None
            path_family_name: str | None = None
            if path_family_items:
                path_family_kind, path_family_name = resolve_artifact_path_family(
                    path_family_items[0].target_ref,
                    owner_unit=owner_unit,
                    artifact_decl=artifact_decl,
                    source_span=path_family_items[0].source_span,
                )
            if not any(key in scalars_by_key for key in ("path", "section", "anchor")):
                raise self._skill_graph_error(
                    detail=(
                        f"Artifact `{artifact_decl.name}` must declare at least "
                        "one of `path:`, `section:`, or `anchor:`."
                    ),
                    unit=owner_unit,
                    source_span=artifact_decl.source_span,
                    hints=("Give the artifact a stable authored location hint.",),
                )
            return model.ResolvedSkillGraphArtifact(
                name=artifact_decl.name,
                title=artifact_decl.title,
                owner_stage_name=owner_stage_decl.name,
                path_family_kind=path_family_kind,
                path_family_name=path_family_name,
                path=(
                    scalars_by_key["path"].value
                    if "path" in scalars_by_key
                    else None
                ),
                section=(
                    scalars_by_key["section"].value
                    if "section" in scalars_by_key
                    else None
                ),
                anchor=(
                    scalars_by_key["anchor"].value
                    if "anchor" in scalars_by_key
                    else None
                ),
                intent=(
                    scalars_by_key["intent"].value
                    if "intent" in scalars_by_key
                    else None
                ),
                source_span=artifact_decl.source_span,
            )

        def resolve_artifact_path_family(
            ref: model.NameRef,
            *,
            owner_unit: IndexedUnit,
            artifact_decl: model.ArtifactDecl,
            source_span,
        ) -> tuple[str, str]:
            lookup_targets = self._decl_lookup_targets(ref, unit=owner_unit)
            registry_kinds = (
                ("document", "documents_by_name"),
                ("schema", "schemas_by_name"),
                ("table", "tables_by_name"),
                ("enum", "enums_by_name"),
                ("receipt", "receipts_by_name"),
                ("output", "outputs_by_name"),
                ("input", "inputs_by_name"),
                ("output_target", "output_targets_by_name"),
            )
            for lookup_target in lookup_targets:
                target_decls = unit_declarations(lookup_target.unit)
                target_name = lookup_target.declaration_name
                for kind, registry_name in registry_kinds:
                    if target_name in getattr(target_decls, registry_name):
                        path_family_key = (kind, target_name)
                        self._check_public_graph_name_collision(
                            owner_label=owner_label,
                            kind="artifact path_family",
                            public_name=target_name,
                            existing_unit=reached_artifact_path_family_units.get(
                                path_family_key
                            ),
                            owner_unit=lookup_target.unit,
                            source_span=ref.source_span or source_span,
                            fallback_span=artifact_decl.source_span,
                            keyed_by="artifact path_family kind and name",
                            plural_kind="artifact path_family refs",
                        )
                        reached_artifact_path_family_units.setdefault(
                            path_family_key,
                            lookup_target.unit,
                        )
                        return kind, target_name
            dotted = self._dotted_ref(ref)
            raise self._skill_graph_error(
                detail=(
                    f"Artifact `{artifact_decl.name}` path family `{dotted}` "
                    "does not resolve to a supported top-level declaration."
                ),
                unit=owner_unit,
                source_span=ref.source_span or source_span or artifact_decl.source_span,
                hints=(
                    "Point `path_family:` at a document, schema, table, enum, "
                    "receipt, input, output, or output target declaration.",
                ),
            )

        def resolve_stage_dependencies(
            stage_decl: model.StageDecl,
            *,
            owner_unit: IndexedUnit,
        ) -> None:
            stage_label = self._stage_owner_label(stage_decl, unit=owner_unit)
            for item in stage_decl.items:
                if isinstance(item, model.StageOwnerItem):
                    skill_unit, skill_decl = self._resolve_stage_skill_ref(
                        item.owner_ref,
                        unit=owner_unit,
                        owner_label=stage_label,
                        role="owner",
                        error_code="E546",
                    )
                    remember_skill(skill_decl.name, owner_unit=skill_unit, skill_decl=skill_decl)
                elif isinstance(item, model.StageSupportsItem):
                    for support_ref in item.skill_refs:
                        skill_unit, skill_decl = self._resolve_stage_skill_ref(
                            support_ref,
                            unit=owner_unit,
                            owner_label=stage_label,
                            role="support",
                            error_code="E547",
                        )
                        remember_skill(
                            skill_decl.name,
                            owner_unit=skill_unit,
                            skill_decl=skill_decl,
                        )

            resolved_stage = self._resolve_stage_decl(stage_decl, unit=owner_unit)
            for input_entry in resolved_stage.inputs:
                if input_entry.type_kind == "receipt":
                    receipt_unit, receipt_decl = resolve_receipt_by_name(
                        input_entry.type_name,
                        current_unit=owner_unit,
                        source_span=stage_decl.source_span,
                        role="stage input",
                    )
                    remember_receipt(
                        receipt_decl.name,
                        owner_unit=receipt_unit,
                        receipt_decl=receipt_decl,
                    )
                if input_entry.type_kind == "artifact":
                    artifact_unit, artifact_decl = resolve_artifact_by_name(
                        input_entry.type_name,
                        current_unit=owner_unit,
                        source_span=stage_decl.source_span,
                        role="stage input",
                    )
                    remember_artifact(
                        artifact_decl.name,
                        owner_unit=artifact_unit,
                        artifact_decl=artifact_decl,
                    )
            for artifact_name in resolved_stage.artifact_names:
                artifact_unit, artifact_decl = resolve_artifact_by_name(
                    artifact_name,
                    current_unit=owner_unit,
                    source_span=stage_decl.source_span,
                    role="stage owned",
                )
                remember_artifact(
                    artifact_decl.name,
                    owner_unit=artifact_unit,
                    artifact_decl=artifact_decl,
                )
            if resolved_stage.emits_receipt_name is not None:
                receipt_unit, receipt_decl = resolve_receipt_by_name(
                    resolved_stage.emits_receipt_name,
                    current_unit=owner_unit,
                    source_span=stage_decl.source_span,
                    role="stage emit",
                )
                remember_receipt(
                    receipt_decl.name,
                    owner_unit=receipt_unit,
                    receipt_decl=receipt_decl,
                )

        def node_expansion(
            node: model.ResolvedSkillFlowNode,
            *,
            current_unit: IndexedUnit,
            current_flow_name: str,
            current_flow_identity: str,
            graph_flow: model.ResolvedSkillGraphFlow,
        ) -> _NodeExpansion:
            if node.kind == "stage":
                stage_unit, stage_decl = resolve_stage_by_name(
                    node.name,
                    module_parts=node.module_parts,
                    current_unit=current_unit,
                    source_span=node.source_span,
                    role="reached",
                )
                remember_stage(node.name, owner_unit=stage_unit, stage_decl=stage_decl)
                resolve_stage_dependencies(stage_decl, owner_unit=stage_unit)
                return _NodeExpansion(
                    start_stages=(node.name,),
                    terminal_stages=(node.name,),
                    reached_stage_names={node.name},
                    stage_reaching_flows={node.name: {current_flow_name}},
                    stage_reaching_flow_identities={
                        node.name: {current_flow_identity}
                    },
                )
            if node.kind == "flow":
                child_unit, child_decl = resolve_flow_by_name(
                    node.name,
                    module_parts=node.module_parts,
                    current_unit=current_unit,
                    source_span=node.source_span,
                    role="reached",
                )
                child = expand_flow(child_decl, owner_unit=child_unit)
                return augment_with_parent_flow(
                    child,
                    parent_flow_name=current_flow_name,
                    parent_flow_identity=current_flow_identity,
                )
            repeat = next(
                (entry for entry in graph_flow.repeats if entry.name == node.name),
                None,
            )
            if repeat is None:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` cannot expand repeat "
                        f"`{node.name}` because the flow repeat metadata is missing."
                    ),
                    unit=current_unit,
                    source_span=node.source_span,
                    hints=("This is a compiler bug, not an authoring error.",),
                )
            child_unit, child_decl = resolve_flow_by_name(
                repeat.target_flow_name,
                module_parts=repeat.target_flow_module_parts,
                current_unit=current_unit,
                source_span=node.source_span,
                role="repeat target",
            )
            child = expand_flow(child_decl, owner_unit=child_unit)
            return augment_with_parent_flow(
                child,
                parent_flow_name=current_flow_name,
                parent_flow_identity=current_flow_identity,
            )

        def flow_terminal_nodes(
            graph_flow: model.ResolvedSkillGraphFlow,
        ) -> tuple[model.ResolvedSkillFlowNode, ...]:
            if not graph_flow.nodes:
                return tuple()
            incoming = {self._flow_node_key(edge.target) for edge in graph_flow.edges}
            outgoing = {self._flow_node_key(edge.source) for edge in graph_flow.edges}
            if not graph_flow.edges:
                if graph_flow.start is not None:
                    return (graph_flow.start,)
                return tuple(graph_flow.nodes)
            terminal_nodes = tuple(
                node
                for node in graph_flow.nodes
                if self._flow_node_key(node) not in outgoing
            )
            if terminal_nodes:
                return terminal_nodes
            if graph_flow.start is not None:
                return (graph_flow.start,)
            return tuple(
                node
                for node in graph_flow.nodes
                if self._flow_node_key(node) not in incoming
            )

        def expand_flow(
            flow_decl: model.SkillFlowDecl,
            *,
            owner_unit: IndexedUnit,
        ) -> _FlowExpansion:
            cache_key = (id(owner_unit), flow_decl.name)
            cached_flow = flow_cache.get(cache_key)
            if cached_flow is not None:
                return cached_flow
            if cache_key in flow_stack:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` expands flow `{flow_decl.name}` "
                        "through a nested flow cycle."
                    ),
                    unit=owner_unit,
                    source_span=flow_decl.source_span,
                    hints=(
                        "Break the nested flow cycle, or rewrite the loop as a typed repeat.",
                    ),
                )
            flow_stack.append(cache_key)
            try:
                flow_identity = dotted_decl_name(owner_unit.module_parts, flow_decl.name)
                resolved_flow = self._resolve_skill_flow_decl(
                    flow_decl,
                    unit=owner_unit,
                    allow_graph_set_candidates=True,
                    allow_unbound_edges=allow_unbound_edges,
                    allow_incomplete_branch_coverage=(
                        warn_branch_coverage and not require_branch_coverage
                    ),
                    branch_coverage_warning_callback=append_branch_coverage_warning,
                )
                resolved_edges = tuple(
                    replace(
                        edge,
                        why=interpolate_checked_skill_mentions(
                            edge.why,
                            current_unit=owner_unit,
                            owner_text=(
                                f"skill_flow `{flow_decl.name}` edge "
                                f"`{edge.source.name} -> {edge.target.name}`"
                            ),
                            source_span=edge.source_span or flow_decl.source_span,
                        ),
                    )
                    for edge in resolved_flow.edges
                )
                graph_repeats: list[model.ResolvedSkillGraphRepeat] = []
                for repeat in resolved_flow.repeats:
                    over_kind = repeat.over_kind
                    if over_kind == "graph_set_candidate":
                        if repeat.over_name in set_names:
                            over_kind = "graph_set"
                        elif "." in repeat.over_name:
                            over_kind = "graph_path"
                        else:
                            raise self._skill_graph_error(
                                detail=(
                                    f"Skill graph `{owner_label}` repeat "
                                    f"`{repeat.name}` in flow `{flow_decl.name}` "
                                    f"uses graph set `{repeat.over_name}`, but "
                                    "that set is not declared under `sets:`."
                                ),
                                unit=owner_unit,
                                source_span=repeat.source_span or flow_decl.source_span,
                                hints=(
                                    "Declare the graph set under `sets:`, or point `over:` at a declared enum, table, or schema.",
                                ),
                            )
                    graph_repeats.append(
                        model.ResolvedSkillGraphRepeat(
                            name=repeat.name,
                            target_flow_name=repeat.target_flow_name,
                            over_kind=over_kind,
                            over_name=repeat.over_name,
                            order=repeat.order,
                            why=interpolate_checked_skill_mentions(
                                repeat.why,
                                current_unit=owner_unit,
                                owner_text=(
                                    f"skill_flow `{flow_decl.name}` repeat "
                                    f"`{repeat.name}`"
                                ),
                                source_span=repeat.source_span or flow_decl.source_span,
                            ),
                            target_flow_module_parts=repeat.target_flow_module_parts,
                            source_span=repeat.source_span,
                        )
                    )
                graph_flow = model.ResolvedSkillGraphFlow(
                    canonical_name=resolved_flow.canonical_name,
                    title=resolved_flow.title,
                    intent=(
                        None
                        if resolved_flow.intent is None
                        else interpolate_checked_skill_mentions(
                            resolved_flow.intent,
                            current_unit=owner_unit,
                            owner_text=f"skill_flow `{flow_decl.name}` intent",
                            source_span=flow_decl.source_span,
                        )
                    ),
                    start=resolved_flow.start,
                    approve=resolved_flow.approve,
                    approve_module_parts=resolved_flow.approve_module_parts,
                    nodes=resolved_flow.nodes,
                    edges=resolved_edges,
                    repeats=tuple(graph_repeats),
                    variations=resolved_flow.variations,
                    unsafe_variations=resolved_flow.unsafe_variations,
                    changed_workflow=resolved_flow.changed_workflow,
                    terminals=resolved_flow.terminals,
                    source_span=resolved_flow.source_span,
                )
                remember_flow(
                    flow_decl.name,
                    owner_unit=owner_unit,
                    source_span=flow_decl.source_span,
                )

                result = _NodeExpansion()
                if graph_flow.start is not None:
                    start_expansion = node_expansion(
                        graph_flow.start,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        current_flow_identity=flow_identity,
                        graph_flow=graph_flow,
                    )
                    if not result.start_stages:
                        result.start_stages = start_expansion.start_stages
                    merge_node_expansion(result, start_expansion)
                elif graph_flow.nodes:
                    incoming = {
                        self._flow_node_key(edge.target)
                        for edge in graph_flow.edges
                    }
                    start_nodes = tuple(
                        node
                        for node in graph_flow.nodes
                        if self._flow_node_key(node) not in incoming
                    )
                    start_stages: list[str] = []
                    for start_node in start_nodes:
                        start_expansion = node_expansion(
                            start_node,
                            current_unit=owner_unit,
                            current_flow_name=flow_decl.name,
                            current_flow_identity=flow_identity,
                            graph_flow=graph_flow,
                        )
                        merge_node_expansion(result, start_expansion)
                        for stage_name in start_expansion.start_stages:
                            if stage_name not in start_stages:
                                start_stages.append(stage_name)
                    result.start_stages = tuple(start_stages)

                for edge in graph_flow.edges:
                    source_expansion = node_expansion(
                        edge.source,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        current_flow_identity=flow_identity,
                        graph_flow=graph_flow,
                    )
                    target_expansion = node_expansion(
                        edge.target,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        current_flow_identity=flow_identity,
                        graph_flow=graph_flow,
                    )
                    merge_node_expansion(result, source_expansion)
                    merge_node_expansion(result, target_expansion)
                    for source_stage in source_expansion.terminal_stages:
                        for target_stage in target_expansion.start_stages:
                            result.stage_edges.append(
                                model.ResolvedSkillGraphStageEdge(
                                    source_stage_name=source_stage,
                                    target_stage_name=target_stage,
                                    via_flow_name=flow_decl.name,
                                    kind=edge.kind,
                                    why=edge.why,
                                    route_receipt_name=(
                                        None if edge.route is None else edge.route.receipt_name
                                    ),
                                    route_field_key=(
                                        None if edge.route is None else edge.route.route_field_key
                                    ),
                                    route_choice_key=(
                                        None if edge.route is None else edge.route.choice_key
                                    ),
                                    source_span=edge.source_span,
                                )
                            )
                            if edge.route is not None:
                                receipt_unit, receipt_decl = resolve_receipt_by_name(
                                    edge.route.receipt_name,
                                    current_unit=owner_unit,
                                    source_span=edge.source_span,
                                    role="route binding",
                                )
                                remember_receipt(
                                    receipt_decl.name,
                                    owner_unit=receipt_unit,
                                    receipt_decl=receipt_decl,
                                )

                terminal_nodes = flow_terminal_nodes(graph_flow)
                terminal_stages: list[str] = []
                for terminal_node in terminal_nodes:
                    terminal_expansion = node_expansion(
                        terminal_node,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        current_flow_identity=flow_identity,
                        graph_flow=graph_flow,
                    )
                    merge_node_expansion(result, terminal_expansion)
                    for stage_name in terminal_expansion.terminal_stages:
                        if stage_name not in terminal_stages:
                            terminal_stages.append(stage_name)

                if graph_flow.approve is not None:
                    approve_unit, approve_decl = resolve_flow_by_name(
                        graph_flow.approve,
                        module_parts=graph_flow.approve_module_parts,
                        current_unit=owner_unit,
                        source_span=graph_flow.source_span,
                        role="approve",
                    )
                    approve_expansion = expand_flow(approve_decl, owner_unit=approve_unit)
                    approve_node = augment_with_parent_flow(
                        approve_expansion,
                        parent_flow_name=flow_decl.name,
                        parent_flow_identity=flow_identity,
                    )
                    merge_node_expansion(result, approve_node)
                    for source_stage in terminal_stages:
                        for target_stage in approve_node.start_stages:
                            result.stage_edges.append(
                                model.ResolvedSkillGraphStageEdge(
                                    source_stage_name=source_stage,
                                    target_stage_name=target_stage,
                                    via_flow_name=flow_decl.name,
                                    kind="approval",
                                    why=(
                                        f"Approval flow `{graph_flow.approve}` runs after "
                                        f"`{flow_decl.name}`."
                                    ),
                                    source_span=graph_flow.source_span,
                                )
                            )
                    terminal_stages = list(approve_node.terminal_stages)

                result.terminal_stages = tuple(terminal_stages)
                expansion = _FlowExpansion(
                    graph_flow=graph_flow,
                    owner_unit=owner_unit,
                    start_stages=result.start_stages,
                    terminal_stages=result.terminal_stages,
                    reached_stage_names=tuple(sorted(result.reached_stage_names)),
                    reached_flow_names=tuple(
                        sorted({flow_decl.name, *result.reached_flow_names})
                    ),
                    stage_edges=tuple(result.stage_edges),
                    stage_reaching_flows={
                        stage_name: tuple(sorted(flow_names))
                        for stage_name, flow_names in result.stage_reaching_flows.items()
                    },
                    stage_reaching_flow_identities={
                        stage_name: tuple(sorted(flow_ids))
                        for stage_name, flow_ids in (
                            result.stage_reaching_flow_identities.items()
                        )
                    },
                )
                flow_cache[cache_key] = expansion
                return expansion
            finally:
                flow_stack.pop()

        for root_kind, root_unit, root_decl, root_entry in root_decls:
            if root_kind == "stage":
                resolved_stage = self._resolve_stage_decl(root_decl, unit=root_unit)
                remember_stage(root_decl.name, owner_unit=root_unit, stage_decl=root_decl)
                resolve_stage_dependencies(root_decl, owner_unit=root_unit)
                aggregate_stage_reaching_flows.setdefault(root_decl.name, set())
                aggregate_stage_reaching_flow_identities.setdefault(root_decl.name, set())
            else:
                flow_expansion = expand_flow(root_decl, owner_unit=root_unit)
                aggregate_edges.extend(flow_expansion.stage_edges)
                for stage_name in flow_expansion.reached_stage_names:
                    stage_decl = reached_stage_decls[stage_name]
                    stage_unit = reached_stage_units[stage_name]
                    remember_stage(stage_name, owner_unit=stage_unit, stage_decl=stage_decl)
                for stage_name, flow_names in flow_expansion.stage_reaching_flows.items():
                    aggregate_stage_reaching_flows.setdefault(stage_name, set()).update(flow_names)
                for stage_name, flow_ids in (
                    flow_expansion.stage_reaching_flow_identities.items()
                ):
                    aggregate_stage_reaching_flow_identities.setdefault(
                        stage_name,
                        set(),
                    ).update(flow_ids)

        if graph_recovery is not None:
            if graph_recovery.flow_receipt_name is not None:
                receipt_unit, receipt_decl = resolve_receipt_by_name(
                    graph_recovery.flow_receipt_name,
                    module_parts=graph_recovery.flow_receipt_module_parts,
                    current_unit=unit,
                    source_span=graph_decl.source_span,
                    role="recovery",
                )
                remember_receipt(
                    receipt_decl.name,
                    owner_unit=receipt_unit,
                    receipt_decl=receipt_decl,
                )

        resolved_stages: list[model.ResolvedStage] = []
        for stage_name in sorted(reached_stage_order):
            stage_unit = reached_stage_units[stage_name]
            stage_decl = reached_stage_decls[stage_name]
            resolved_stage = self._resolve_stage_decl(stage_decl, unit=stage_unit)
            resolved_stage = replace(
                resolved_stage,
                intent=interpolate_checked_skill_mentions(
                    resolved_stage.intent,
                    current_unit=stage_unit,
                    owner_text=f"stage `{stage_name}` intent",
                    source_span=resolved_stage.source_span or stage_decl.source_span,
                ),
                durable_target=(
                    None
                    if resolved_stage.durable_target is None
                    else interpolate_checked_skill_mentions(
                        resolved_stage.durable_target,
                        current_unit=stage_unit,
                        owner_text=f"stage `{stage_name}` durable_target",
                        source_span=resolved_stage.source_span or stage_decl.source_span,
                    )
                ),
                durable_evidence=(
                    None
                    if resolved_stage.durable_evidence is None
                    else interpolate_checked_skill_mentions(
                        resolved_stage.durable_evidence,
                        current_unit=stage_unit,
                        owner_text=f"stage `{stage_name}` durable_evidence",
                        source_span=resolved_stage.source_span or stage_decl.source_span,
                    )
                ),
                advance_condition=interpolate_checked_skill_mentions(
                    resolved_stage.advance_condition,
                    current_unit=stage_unit,
                    owner_text=f"stage `{stage_name}` advance_condition",
                    source_span=resolved_stage.source_span or stage_decl.source_span,
                ),
                risk_guarded=(
                    None
                    if resolved_stage.risk_guarded is None
                    else interpolate_checked_skill_mentions(
                        resolved_stage.risk_guarded,
                        current_unit=stage_unit,
                        owner_text=f"stage `{stage_name}` risk_guarded",
                        source_span=resolved_stage.source_span or stage_decl.source_span,
                    )
                ),
                entry=(
                    None
                    if resolved_stage.entry is None
                    else interpolate_checked_skill_mentions(
                        resolved_stage.entry,
                        current_unit=stage_unit,
                        owner_text=f"stage `{stage_name}` entry",
                        source_span=resolved_stage.source_span or stage_decl.source_span,
                    )
                ),
                repair_routes=(
                    None
                    if resolved_stage.repair_routes is None
                    else interpolate_checked_skill_mentions(
                        resolved_stage.repair_routes,
                        current_unit=stage_unit,
                        owner_text=f"stage `{stage_name}` repair_routes",
                        source_span=resolved_stage.source_span or stage_decl.source_span,
                    )
                ),
                waiver_policy=(
                    None
                    if resolved_stage.waiver_policy is None
                    else interpolate_checked_skill_mentions(
                        resolved_stage.waiver_policy,
                        current_unit=stage_unit,
                        owner_text=f"stage `{stage_name}` waiver_policy",
                        source_span=resolved_stage.source_span or stage_decl.source_span,
                    )
                ),
            )
            reaching_flow_identities = aggregate_stage_reaching_flow_identities.get(
                stage_name,
                set(),
            )
            if resolved_stage.applies_to_flow_names:
                allowed_flows = set(
                    resolved_stage.applies_to_flow_identities
                    or resolved_stage.applies_to_flow_names
                )
                missing_flows = sorted(
                    set(reaching_flow_identities) - allowed_flows
                )
                if missing_flows:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` reaches stage `{stage_name}` "
                            f"through flow(s) {', '.join(missing_flows)}, but stage "
                            "`applies_to:` does not list them."
                        ),
                        unit=stage_unit,
                        source_span=stage_decl.source_span,
                        hints=(
                            "List every reaching `skill_flow` under `applies_to:`, or remove the restriction.",
                        ),
                    )
            resolved_stages.append(resolved_stage)

        if any(
            policy.action == "require" and policy.key == "stage_lane"
            for policy in graph_policies
        ):
            for stage in resolved_stages:
                if stage.lane_name is not None:
                    continue
                stage_unit = reached_stage_units[stage.canonical_name]
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` requires `stage_lane`, but "
                        f"stage `{stage.canonical_name}` has no `lane:`."
                    ),
                    unit=stage_unit,
                    source_span=stage.source_span,
                    hints=("Add `lane: <EnumName>.<member>` to the stage.",),
                )

        dedup_stage_edges: list[model.ResolvedSkillGraphStageEdge] = []
        seen_stage_edges: set[
            tuple[str, str, str, str, str, str | None, str | None, str | None]
        ] = set()
        for edge in aggregate_edges:
            edge_key = (
                edge.source_stage_name,
                edge.target_stage_name,
                edge.via_flow_name,
                edge.kind,
                edge.why,
                edge.route_receipt_name,
                edge.route_field_key,
                edge.route_choice_key,
            )
            if edge_key in seen_stage_edges:
                continue
            seen_stage_edges.add(edge_key)
            dedup_stage_edges.append(edge)

        stage_successors: dict[str, list[str]] = {}
        stage_predecessors: dict[str, list[str]] = {}
        for edge in dedup_stage_edges:
            stage_successors.setdefault(edge.source_stage_name, [])
            if edge.target_stage_name not in stage_successors[edge.source_stage_name]:
                stage_successors[edge.source_stage_name].append(edge.target_stage_name)
            stage_predecessors.setdefault(edge.target_stage_name, [])
            if edge.source_stage_name not in stage_predecessors[edge.target_stage_name]:
                stage_predecessors[edge.target_stage_name].append(edge.source_stage_name)

        self._validate_skill_graph_dag(
            graph_name=graph_decl.name,
            stage_edges=tuple(dedup_stage_edges),
            unit=unit,
            source_span=graph_decl.source_span,
            allow_cycles=allow_graph_cycles,
        )

        resolved_flows = [
            flow_cache[key].graph_flow
            for key in sorted(flow_cache, key=lambda item: item[1])
        ]

        graph_purpose_text = interpolate_checked_skill_mentions(
            purpose_items[0].value,
            current_unit=unit,
            owner_text=f"skill_graph `{graph_decl.name}` purpose",
            source_span=purpose_items[0].source_span or graph_decl.source_span,
        )

        self._append_skill_graph_policy_warnings(
            graph_decl=graph_decl,
            graph_name=graph_decl.name,
            flow=self.session.flow_for_unit(unit),
            graph_unit=unit,
            reached_stage_units=reached_stage_units,
            reached_skill_units=reached_skill_units,
            reached_receipt_decls=reached_receipt_decls,
            resolved_stages=tuple(resolved_stages),
            resolved_flows=tuple(resolved_flows),
            graph_recovery=graph_recovery,
            append_warning=append_warning,
        )

        resolved_skills: list[model.ResolvedSkillGraphSkill] = []
        for skill_name in sorted(reached_skill_decls):
            skill_decl = reached_skill_decls[skill_name]
            resolved_skills.append(
                model.ResolvedSkillGraphSkill(
                    name=skill_decl.name,
                    title=skill_decl.title,
                    purpose=self._skill_decl_purpose(skill_decl),
                    package_id=(
                        None
                        if skill_decl.package_link is None
                        else skill_decl.package_link.package_id
                    ),
                    category=self._skill_decl_scalar(skill_decl, "category"),
                    visibility=self._skill_decl_scalar(skill_decl, "visibility"),
                    manual_only=self._skill_decl_scalar(skill_decl, "manual_only"),
                    default_flow_member=self._skill_decl_scalar(
                        skill_decl,
                        "default_flow_member",
                    ),
                    aliases=self._skill_decl_scalar(skill_decl, "aliases"),
                    source_span=skill_decl.source_span,
                )
            )
        for skill in resolved_skills:
            if _truthy(skill.manual_only) and _truthy(skill.default_flow_member):
                append_warning(
                    code="W211",
                    policy_key="manual_only_default_flow_conflict",
                    summary="Manual-only skill is marked as a default flow member",
                    owner_kind="skill",
                    owner_name=skill.name,
                    detail=(
                        f"Skill `{skill.name}` has `manual_only: \"true\"` "
                        "and `default_flow_member: \"true\"`."
                    ),
                    source_span=skill.source_span or graph_decl.source_span,
                )

        resolved_packages: list[model.ResolvedSkillGraphPackage] = []
        for package_id in sorted(reached_package_decls):
            package_decl = reached_package_decls[package_id]
            resolved_packages.append(
                model.ResolvedSkillGraphPackage(
                    package_id=package_id,
                    package_name=package_decl.name,
                    package_title=package_decl.title,
                    source_span=package_decl.source_span,
                )
            )

        resolved_artifacts: list[model.ResolvedSkillGraphArtifact] = []
        for artifact_name in sorted(reached_artifact_decls):
            artifact_decl = reached_artifact_decls[artifact_name]
            artifact_unit = reached_artifact_units[artifact_name]
            resolved_artifacts.append(
                resolve_artifact_decl(artifact_decl, owner_unit=artifact_unit)
            )
        artifacts_by_name = {artifact.name: artifact for artifact in resolved_artifacts}
        anchors_by_key: dict[str, model.ResolvedSkillGraphArtifact] = {}
        for artifact in resolved_artifacts:
            if artifact.anchor is None:
                continue
            anchor_key = artifact.anchor.casefold()
            existing_artifact = anchors_by_key.get(anchor_key)
            if existing_artifact is not None:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{graph_decl.name}` reaches artifacts "
                        f"`{existing_artifact.name}` and `{artifact.name}` with "
                        f"the same anchor `{artifact.anchor}`."
                    ),
                    unit=reached_artifact_units[artifact.name],
                    source_span=artifact.source_span or graph_decl.source_span,
                    hints=("Keep artifact anchors unique within one graph.",),
                )
            anchors_by_key[anchor_key] = artifact
        for stage in resolved_stages:
            for artifact_name in stage.artifact_names:
                artifact = artifacts_by_name[artifact_name]
                if artifact.owner_stage_name == stage.canonical_name:
                    continue
                raise self._skill_graph_error(
                    detail=(
                        f"Stage `{stage.canonical_name}` lists artifact "
                        f"`{artifact_name}` under `artifacts:`, but that "
                        f"artifact declares owner `{artifact.owner_stage_name}`."
                    ),
                    unit=reached_stage_units[stage.canonical_name],
                    source_span=stage.source_span or graph_decl.source_span,
                    hints=(
                        "Only the artifact owner stage may list it under "
                        "`artifacts:`. Other stages can read it through "
                        "`inputs:`.",
                    ),
                )

        resolved_receipts: list[model.ResolvedReceipt] = []
        for receipt_name in sorted(reached_receipt_decls):
            receipt_decl = reached_receipt_decls[receipt_name]
            receipt_unit = reached_receipt_units[receipt_name]
            resolved_receipts.append(
                self._resolve_resolved_receipt(receipt_decl, unit=receipt_unit)
            )

        resolved = model.ResolvedSkillGraph(
            canonical_name=graph_decl.name,
            title=graph_decl.title,
            purpose=graph_purpose_text,
            roots=graph_roots,
            sets=graph_sets,
            recovery=graph_recovery,
            policies=graph_policies,
            views=graph_views,
            flows=tuple(resolved_flows),
            stages=tuple(resolved_stages),
            skills=tuple(resolved_skills),
            skill_relations=tuple(skill_relations),
            artifacts=tuple(resolved_artifacts),
            receipts=tuple(resolved_receipts),
            packages=tuple(resolved_packages),
            warnings=tuple(graph_warnings),
            stage_edges=tuple(dedup_stage_edges),
            stage_successors={
                key: tuple(values) for key, values in sorted(stage_successors.items())
            },
            stage_predecessors={
                key: tuple(values) for key, values in sorted(stage_predecessors.items())
            },
            stage_reaching_flows={
                key: tuple(sorted(values))
                for key, values in sorted(aggregate_stage_reaching_flows.items())
            },
            source_span=graph_decl.source_span,
        )
        cache[cache_key] = resolved
        return resolved

    def _resolve_skill_graph_sets(
        self,
        sets_item: model.SkillGraphSetsItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[model.ResolvedSkillGraphSet, ...]:
        if sets_item is None:
            return tuple()
        seen: set[str] = set()
        resolved: list[model.ResolvedSkillGraphSet] = []
        for entry in sets_item.entries:
            if entry.name in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares graph set "
                        f"`{entry.name}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Keep one entry per graph set name.",),
                )
            seen.add(entry.name)
            resolved.append(
                model.ResolvedSkillGraphSet(
                    name=entry.name,
                    title=entry.title,
                    source_span=entry.source_span,
                )
            )
        return tuple(resolved)

    def _resolve_skill_graph_recovery(
        self,
        recovery_item: model.SkillGraphRecoveryItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> model.ResolvedSkillGraphRecovery | None:
        if recovery_item is None:
            return None
        seen: set[str] = set()
        recovery_enum_units: dict[str, IndexedUnit] = {}
        flow_receipt_module_parts: tuple[str, ...] = ()
        values: dict[str, str] = {}
        for entry in recovery_item.entries:
            if entry.key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares recovery key "
                        f"`{entry.key}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Keep one ref per recovery key.",),
                )
            seen.add(entry.key)
            if entry.key == "flow_receipt":
                receipt_unit, receipt_decl = self._resolve_receipt_ref(
                    entry.target_ref,
                    unit=unit,
                )
                flow_receipt_module_parts = receipt_unit.module_parts
                values[entry.key] = receipt_decl.name
                continue
            resolved_enum = self._try_resolve_enum_decl_with_unit(entry.target_ref, unit=unit)
            if resolved_enum is None:
                dotted = self._dotted_ref(entry.target_ref)
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` recovery ref `{entry.key}: "
                        f"{dotted}` does not resolve to a top-level `enum`."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Point recovery enum refs at declared top-level enums.",),
                )
            enum_unit, enum_decl = resolved_enum
            self._check_public_graph_name_collision(
                owner_label=owner_label,
                kind="recovery enum",
                public_name=enum_decl.name,
                existing_unit=recovery_enum_units.get(enum_decl.name),
                owner_unit=enum_unit,
                source_span=entry.source_span or enum_decl.source_span,
                fallback_span=graph_decl.source_span,
                keyed_by="recovery enum name",
                plural_kind="recovery enum refs",
            )
            recovery_enum_units.setdefault(enum_decl.name, enum_unit)
            values[entry.key] = enum_decl.name
        return model.ResolvedSkillGraphRecovery(
            flow_receipt_name=values.get("flow_receipt"),
            stage_status_name=values.get("stage_status"),
            durable_artifact_status_name=values.get("durable_artifact_status"),
            flow_receipt_module_parts=flow_receipt_module_parts,
            source_span=recovery_item.source_span,
        )

    def _resolve_skill_graph_policies(
        self,
        policy_item: model.SkillGraphPolicyItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[model.ResolvedSkillGraphPolicy, ...]:
        if policy_item is None:
            return tuple()
        seen: set[tuple[str, str]] = set()
        seen_dag_key: str | None = None
        resolved: list[model.ResolvedSkillGraphPolicy] = []
        for entry in policy_item.entries:
            policy_key = (entry.action, entry.key)
            if policy_key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` repeats policy "
                        f"`{entry.action} {entry.key}`."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("List each graph policy once.",),
                )
            seen.add(policy_key)
            if entry.action == "dag":
                if seen_dag_key is not None and entry.key != seen_dag_key:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares both "
                            "`dag acyclic` and `dag allow_cycle`. These DAG "
                            "policies are mutually exclusive."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=("Choose one DAG policy for the graph.",),
                    )
                seen_dag_key = entry.key
                if entry.key not in model.SKILL_GRAPH_DAG_POLICY_KEYS:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares unsupported "
                            f"`dag {entry.key}` policy."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=(
                            "Use `dag acyclic` or `dag allow_cycle \"...\"`.",
                        ),
                    )
                if entry.key == "allow_cycle" and not entry.reason:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares "
                            "`dag allow_cycle` without a reason."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=("Write `dag allow_cycle \"Reason\"`.",),
                    )
            elif entry.action == "allow":
                if entry.key not in model.SKILL_GRAPH_ALLOW_POLICY_KEYS:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares unsupported "
                            f"`allow {entry.key}` policy."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=(
                            "Use a shipped graph allow-policy key such as "
                            "`unbound_edges`.",
                        ),
                    )
            elif entry.action == "require":
                if entry.key not in model.SKILL_GRAPH_STRICT_POLICY_KEYS:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares unsupported "
                            f"`require {entry.key}` policy."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=(
                            "Sub-plan 4 accepts only shipped strict graph policy keys.",
                        ),
                    )
            elif entry.action == "warn":
                if entry.key not in model.SKILL_GRAPH_WARNING_POLICY_KEYS:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares unsupported "
                            f"`warn {entry.key}` policy."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=(
                            "Sub-plan 4 accepts warning policy keys only as inert metadata.",
                        ),
                    )
            resolved.append(
                model.ResolvedSkillGraphPolicy(
                    action=entry.action,
                    key=entry.key,
                    reason=entry.reason,
                    source_span=entry.source_span,
                )
            )
        return tuple(resolved)

    def _resolve_skill_graph_views(
        self,
        views_item: model.SkillGraphViewsItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[model.ResolvedSkillGraphView, ...]:
        if views_item is None:
            return tuple()
        seen: set[str] = set()
        resolved: list[model.ResolvedSkillGraphView] = []
        for entry in views_item.entries:
            if entry.key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares view key "
                        f"`{entry.key}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Keep one output path per graph view key.",),
                )
            seen.add(entry.key)
            resolved.append(
                model.ResolvedSkillGraphView(
                    key=entry.key,
                    path=entry.path,
                    source_span=entry.source_span,
                )
            )
        return tuple(resolved)

    def _resolve_skill_graph_roots(
        self,
        roots_item: model.SkillGraphRootsItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[
        tuple[model.ResolvedSkillGraphRoot, ...],
        tuple[tuple[str, IndexedUnit, object, model.SkillGraphRootEntry], ...],
    ]:
        seen: set[tuple[str, str]] = set()
        resolved_roots: list[model.ResolvedSkillGraphRoot] = []
        resolved_decls: list[tuple[str, IndexedUnit, object, model.SkillGraphRootEntry]] = []
        for entry in roots_item.entries:
            try:
                owner_unit, declaration = self._resolve_decl_ref(
                    entry.target_ref,
                    unit=unit,
                    registry_name=(
                        "skill_flows_by_name" if entry.kind == "flow" else "stages_by_name"
                    ),
                    missing_label=(
                        "skill_flow declaration" if entry.kind == "flow" else "stage declaration"
                    ),
                )
            except CompileError as exc:
                dotted = self._dotted_ref(entry.target_ref)
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` root `{entry.kind} {dotted}` "
                        "does not resolve."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=(
                        "Point roots at visible top-level `stage` or `skill_flow` declarations.",
                    ),
                ) from exc
            root_name = declaration.name
            root_key = (entry.kind, root_name)
            if root_key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` lists root "
                        f"`{entry.kind} {root_name}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("List each graph root once.",),
                )
            seen.add(root_key)
            resolved_roots.append(
                model.ResolvedSkillGraphRoot(
                    kind=entry.kind,
                    name=root_name,
                    source_span=entry.source_span,
                )
            )
            resolved_decls.append((entry.kind, owner_unit, declaration, entry))
        return tuple(resolved_roots), tuple(resolved_decls)

    def _append_skill_graph_policy_warnings(
        self,
        *,
        graph_decl: model.SkillGraphDecl,
        graph_name: str,
        flow,
        graph_unit: IndexedUnit,
        reached_stage_units: dict[str, IndexedUnit],
        reached_skill_units: dict[str, IndexedUnit],
        reached_receipt_decls: dict[str, model.ReceiptDecl],
        resolved_stages: tuple[model.ResolvedStage, ...],
        resolved_flows: tuple[model.ResolvedSkillGraphFlow, ...],
        graph_recovery: model.ResolvedSkillGraphRecovery | None,
        append_warning,
    ) -> None:
        def reached_from_graph_unit(reached_unit: IndexedUnit | None) -> bool:
            return (
                reached_unit is not None
                and reached_unit.prompt_root == graph_unit.prompt_root
                and reached_unit.module_parts == graph_unit.module_parts
            )

        def reached_elsewhere_label(
            *,
            kind: str,
            name: str,
            reached_unit: IndexedUnit | None,
        ) -> str | None:
            if reached_unit is None or reached_from_graph_unit(reached_unit):
                return None
            dotted_name = dotted_decl_name(reached_unit.module_parts, name)
            if dotted_name == name:
                return f"another imported {kind} named `{name}`"
            return f"{kind} `{dotted_name}`"

        for stage_name, stage_decl in sorted(flow.stages_by_name.items()):
            reached_unit = reached_stage_units.get(stage_name)
            if reached_from_graph_unit(reached_unit):
                continue
            same_public_name_reached = reached_elsewhere_label(
                kind="stage",
                name=stage_name,
                reached_unit=reached_unit,
            )
            if same_public_name_reached is None:
                detail = (
                    f"Skill graph `{graph_name}` does not reach stage "
                    f"`{stage_name}` from any root."
                )
            else:
                detail = (
                    f"Skill graph `{graph_name}` reaches {same_public_name_reached}, "
                    f"but does not reach local stage `{stage_name}` from the "
                    "graph entrypoint module."
                )
            append_warning(
                code="W201",
                policy_key="orphan_stage",
                summary="Stage is not reached by this graph",
                owner_kind="stage",
                owner_name=stage_name,
                detail=detail,
                source_span=stage_decl.source_span or graph_decl.source_span,
            )

        for skill_name, skill_decl in sorted(flow.skills_by_name.items()):
            reached_unit = reached_skill_units.get(skill_name)
            if reached_from_graph_unit(reached_unit):
                continue
            same_public_name_reached = reached_elsewhere_label(
                kind="skill",
                name=skill_name,
                reached_unit=reached_unit,
            )
            if same_public_name_reached is None:
                detail = (
                    f"Skill graph `{graph_name}` does not reach skill "
                    f"`{skill_name}` from a stage owner, stage support, "
                    "relation, or checked skill mention."
                )
            else:
                detail = (
                    f"Skill graph `{graph_name}` reaches {same_public_name_reached}, "
                    f"but does not reach local skill `{skill_name}` from a stage "
                    "owner, stage support, relation, or checked skill mention in "
                    "the graph entrypoint module."
                )
            append_warning(
                code="W202",
                policy_key="orphan_skill",
                summary="Skill is not reached by this graph",
                owner_kind="skill",
                owner_name=skill_name,
                detail=detail,
                source_span=skill_decl.source_span or graph_decl.source_span,
            )

        stages_by_owner: dict[str, list[model.ResolvedStage]] = {}
        for stage in resolved_stages:
            stages_by_owner.setdefault(stage.owner_skill_name, []).append(stage)
            if stage.risk_guarded is None:
                append_warning(
                    code="W208",
                    policy_key="stage_without_risk_guard",
                    summary="Stage has no risk guard",
                    owner_kind="stage",
                    owner_name=stage.canonical_name,
                    detail=(
                        f"Stage `{stage.canonical_name}` has no "
                        "`risk_guarded:` field."
                    ),
                    source_span=stage.source_span or graph_decl.source_span,
                )
        for owner_skill, owner_stages in sorted(stages_by_owner.items()):
            if len(owner_stages) < 2:
                continue
            stage_list = ", ".join(stage.canonical_name for stage in owner_stages)
            append_warning(
                code="W203",
                policy_key="stage_owner_shared",
                summary="One skill owns multiple stages",
                owner_kind="skill",
                owner_name=owner_skill,
                detail=(
                    f"Skill `{owner_skill}` owns multiple reached stages in "
                    f"`{graph_name}`: {stage_list}."
                ),
                source_span=owner_stages[0].source_span or graph_decl.source_span,
            )

        for graph_flow in resolved_flows:
            if graph_flow.approve is None:
                append_warning(
                    code="W207",
                    policy_key="flow_without_approve",
                    summary="Flow has no approve route",
                    owner_kind="skill_flow",
                    owner_name=graph_flow.canonical_name,
                    detail=(
                        f"Skill flow `{graph_flow.canonical_name}` has no "
                        "`approve:` flow."
                    ),
                    source_span=graph_flow.source_span or graph_decl.source_span,
                )
            for edge in graph_flow.edges:
                if edge.route is not None or edge.source.kind != "stage":
                    continue
                stage_unit = reached_stage_units.get(edge.source.name)
                if stage_unit is None:
                    continue
                emitted_receipt = self._lookup_stage_emitted_receipt(
                    stage_name=edge.source.name,
                    unit=stage_unit,
                )
                if emitted_receipt is None:
                    continue
                if not any(
                    self._receipt_route_choice_matches_target(
                        choice,
                        target_node=edge.target,
                    )
                    for route_field in emitted_receipt.routes
                    for choice in route_field.choices
                ):
                    continue
                append_warning(
                    code="W209",
                    policy_key="edge_route_binding_missing",
                    summary="Edge route binding is missing",
                    owner_kind="skill_flow",
                    owner_name=graph_flow.canonical_name,
                    detail=(
                        f"Skill flow `{graph_flow.canonical_name}` edge "
                        f"`{edge.source.name} -> {edge.target.name}` is "
                        "allowed by graph policy but has no `route:` binding."
                    ),
                    source_span=edge.source_span or graph_flow.source_span,
                )

        consumed_receipts = {
            entry.type_name
            for stage in resolved_stages
            for entry in stage.inputs
            if entry.type_kind == "receipt"
        }
        recovery_receipts = set()
        if graph_recovery is not None and graph_recovery.flow_receipt_name is not None:
            recovery_receipts.add(graph_recovery.flow_receipt_name)
        for receipt_name, receipt_decl in sorted(reached_receipt_decls.items()):
            if receipt_name in consumed_receipts or receipt_name in recovery_receipts:
                continue
            append_warning(
                code="W206",
                policy_key="receipt_without_consumer",
                summary="Receipt has no reached consumer",
                owner_kind="receipt",
                owner_name=receipt_name,
                detail=(
                    f"Receipt `{receipt_name}` is reached by `{graph_name}` "
                    "but no reached stage lists it under `inputs:`."
                ),
                source_span=receipt_decl.source_span or graph_decl.source_span,
            )

    def _validate_skill_graph_dag(
        self,
        *,
        graph_name: str,
        stage_edges: tuple[model.ResolvedSkillGraphStageEdge, ...],
        unit: IndexedUnit,
        source_span,
        allow_cycles: bool = False,
    ) -> None:
        adjacency: dict[str, tuple[str, ...]] = {}
        edge_by_pair: dict[tuple[str, str], model.ResolvedSkillGraphStageEdge] = {}
        for edge in stage_edges:
            adjacency.setdefault(edge.source_stage_name, tuple())
            targets = list(adjacency[edge.source_stage_name])
            if edge.target_stage_name not in targets:
                targets.append(edge.target_stage_name)
                adjacency[edge.source_stage_name] = tuple(targets)
            edge_by_pair.setdefault(
                (edge.source_stage_name, edge.target_stage_name),
                edge,
            )

        white = 0
        gray = 1
        black = 2
        color: dict[str, int] = {}
        cycle_edge: model.ResolvedSkillGraphStageEdge | None = None

        def visit(node: str) -> None:
            nonlocal cycle_edge
            color[node] = gray
            for target in adjacency.get(node, ()):
                state = color.get(target, white)
                if state == gray:
                    cycle_edge = edge_by_pair[(node, target)]
                    return
                if state == white:
                    visit(target)
                    if cycle_edge is not None:
                        return
            color[node] = black

        for node in sorted(adjacency):
            if color.get(node, white) != white:
                continue
            visit(node)
            if cycle_edge is not None:
                break

        if cycle_edge is None:
            return
        if allow_cycles:
            return
        raise self._skill_graph_error(
            detail=(
                f"Skill graph `{graph_name}` expands to a stage cycle through "
                f"`{cycle_edge.source_stage_name} -> {cycle_edge.target_stage_name}`."
            ),
            unit=unit,
            source_span=cycle_edge.source_span or source_span,
            hints=(
                "Break the cross-flow cycle, or rewrite the loop as a typed repeat.",
            ),
        )

    def _skill_decl_purpose(
        self,
        skill_decl: model.SkillDecl,
    ) -> str | None:
        return self._skill_decl_scalar(skill_decl, "purpose")

    def _skill_decl_scalar(
        self,
        skill_decl: model.SkillDecl,
        key: str,
    ) -> str | None:
        for item in skill_decl.items:
            if isinstance(item, model.RecordScalar) and item.key == key:
                if isinstance(item.value, str):
                    return item.value
        return None

    def _validate_all_skill_graphs_in_flow(self, flow) -> None:
        registry = getattr(flow, "skill_graphs_by_name", None)
        if not registry:
            return
        validated_key = (flow.prompt_root.resolve(), flow.flow_root.resolve())
        cache = getattr(self, "_skill_graphs_validated_flows", None)
        if cache is None:
            cache = set()
            object.__setattr__(self, "_skill_graphs_validated_flows", cache)
        if validated_key in cache:
            return
        cache.add(validated_key)
        for graph_decl in registry.values():
            owner_unit = flow.declaration_owner_units_by_id[id(graph_decl)]
            self._resolve_skill_graph_decl(graph_decl, unit=owner_unit)
