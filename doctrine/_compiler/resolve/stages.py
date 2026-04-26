from __future__ import annotations

from doctrine import model
from doctrine._compiler.indexing import unit_declarations
from doctrine._compiler.package_diagnostics import package_compile_error
from doctrine._compiler.resolved_types import CompileError, IndexedUnit


_STAGE_CHECKPOINT_VALUES: frozenset[str] = frozenset(
    {"durable", "review_only", "diagnostic", "none"}
)
_STAGE_DURABLE_CHECKPOINTS: frozenset[str] = frozenset({"durable"})


class ResolveStagesMixin:
    """Top-level stage resolution helpers for ResolveMixin.

    Sub-plan 2 ships the typed-fields surface only. The resolver enforces:
      * `owner:` resolves to a top-level `skill`
      * `lane:` resolves to an enum member
      * each `supports:` entry resolves to a top-level `skill`
      * each `applies_to:` entry resolves to a top-level `skill_flow`
      * `inputs:` keys are unique and each value resolves to a top-level
        `receipt`, `document`, `schema`, or `table`
      * `emits:` resolves to a top-level `receipt`
      * required fields exist (`owner:`, `intent:`, `advance_condition:`)
      * `checkpoint:` is one of `durable`, `review_only`, `diagnostic`, `none`
        (default `durable`)
      * durable stages declare `durable_target:` and `durable_evidence:`

    Flow membership, closure expansion, and route binding belong to later
    sub-plans.
    """

    def _stage_owner_label(
        self,
        decl: model.StageDecl,
        *,
        unit: IndexedUnit,
    ) -> str:
        if unit.module_parts:
            return ".".join((*unit.module_parts, decl.name))
        return decl.name

    def _resolve_stage_decl(
        self,
        stage_decl: model.StageDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        cache = self._resolved_stage_cache()
        cache_key = (id(unit), stage_decl.name)
        if cache_key in cache:
            return
        owner_label = self._stage_owner_label(stage_decl, unit=unit)

        owner_items: list[model.StageOwnerItem] = []
        lane_items: list[model.StageLaneItem] = []
        supports_items: list[model.StageSupportsItem] = []
        applies_to_items: list[model.StageAppliesToItem] = []
        inputs_items: list[model.StageInputsItem] = []
        emits_items: list[model.StageEmitsItem] = []
        forbidden_items: list[model.StageForbiddenOutputsItem] = []
        scalars_by_key: dict[str, model.StageScalarItem] = {}

        for item in stage_decl.items:
            if isinstance(item, model.StageOwnerItem):
                owner_items.append(item)
                continue
            if isinstance(item, model.StageLaneItem):
                lane_items.append(item)
                continue
            if isinstance(item, model.StageSupportsItem):
                supports_items.append(item)
                continue
            if isinstance(item, model.StageAppliesToItem):
                applies_to_items.append(item)
                continue
            if isinstance(item, model.StageInputsItem):
                inputs_items.append(item)
                continue
            if isinstance(item, model.StageEmitsItem):
                emits_items.append(item)
                continue
            if isinstance(item, model.StageForbiddenOutputsItem):
                forbidden_items.append(item)
                continue
            if isinstance(item, model.StageScalarItem):
                if item.key in scalars_by_key:
                    raise package_compile_error(
                        code="E559",
                        summary="Invalid stage declaration",
                        detail=(
                            f"Stage `{owner_label}` declares `{item.key}:` more "
                            "than once."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=item.source_span or stage_decl.source_span,
                        hints=("Keep one value per stage scalar field.",),
                    )
                scalars_by_key[item.key] = item
                continue

        for label, items in (
            ("owner", owner_items),
            ("lane", lane_items),
            ("supports", supports_items),
            ("applies_to", applies_to_items),
            ("inputs", inputs_items),
            ("emits", emits_items),
            ("forbidden_outputs", forbidden_items),
        ):
            if len(items) > 1:
                raise package_compile_error(
                    code="E559",
                    summary="Invalid stage declaration",
                    detail=(
                        f"Stage `{owner_label}` declares `{label}:` more than once."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=items[1].source_span or stage_decl.source_span,
                    hints=(f"Keep one `{label}:` block per stage.",),
                )

        if not owner_items:
            raise package_compile_error(
                code="E559",
                summary="Invalid stage declaration",
                detail=(
                    f"Stage `{owner_label}` is missing the required `owner:` "
                    "field."
                ),
                path=unit.prompt_file.source_path,
                source_span=stage_decl.source_span,
                hints=(
                    "Add `owner: <SkillRef>` so the stage knows which skill "
                    "owns this graph node.",
                ),
            )
        owner_item = owner_items[0]
        owner_skill_unit, _owner_skill = self._resolve_stage_skill_ref(
            owner_item.owner_ref,
            unit=unit,
            owner_label=owner_label,
            role="owner",
            error_code="E546",
        )

        owner_skill_key = (
            owner_skill_unit.prompt_root.resolve(),
            owner_skill_unit.module_parts,
            owner_item.owner_ref.declaration_name,
        )

        if lane_items:
            self._resolve_stage_lane_ref(
                lane_items[0].lane_ref,
                unit=unit,
                owner_label=owner_label,
                source_span=lane_items[0].source_span,
            )

        if supports_items:
            seen_support_keys: set[
                tuple[object, tuple[str, ...], str]
            ] = set()
            for support_ref in supports_items[0].skill_refs:
                support_unit, _support_decl = self._resolve_stage_skill_ref(
                    support_ref,
                    unit=unit,
                    owner_label=owner_label,
                    role="support",
                    error_code="E547",
                )
                support_key = (
                    support_unit.prompt_root.resolve(),
                    support_unit.module_parts,
                    support_ref.declaration_name,
                )
                if support_key == owner_skill_key:
                    raise package_compile_error(
                        code="E559",
                        summary="Invalid stage declaration",
                        detail=(
                            f"Stage `{owner_label}` lists owner skill "
                            f"`{support_ref.declaration_name}` under "
                            "`supports:`."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=support_ref.source_span
                        or supports_items[0].source_span,
                        hints=(
                            "Drop the duplicate from `supports:`. The owner "
                            "skill is already the stage owner.",
                        ),
                    )
                if support_key in seen_support_keys:
                    raise package_compile_error(
                        code="E559",
                        summary="Invalid stage declaration",
                        detail=(
                            f"Stage `{owner_label}` lists support skill "
                            f"`{support_ref.declaration_name}` more than once."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=support_ref.source_span
                        or supports_items[0].source_span,
                        hints=("List each support skill once per stage.",),
                    )
                seen_support_keys.add(support_key)

        if applies_to_items:
            seen_flow_keys: set[
                tuple[object, tuple[str, ...], str]
            ] = set()
            for flow_ref in applies_to_items[0].flow_refs:
                flow_unit, flow_decl = self._resolve_stage_skill_flow_ref(
                    flow_ref,
                    unit=unit,
                    owner_label=owner_label,
                    source_span=flow_ref.source_span or applies_to_items[0].source_span,
                )
                flow_key = (
                    flow_unit.prompt_root.resolve(),
                    flow_unit.module_parts,
                    flow_decl.name,
                )
                if flow_key in seen_flow_keys:
                    raise package_compile_error(
                        code="E559",
                        summary="Invalid stage declaration",
                        detail=(
                            f"Stage `{owner_label}` lists flow "
                            f"`{flow_decl.name}` more than once under "
                            "`applies_to:`."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=flow_ref.source_span
                        or applies_to_items[0].source_span,
                        hints=("List each `skill_flow` once per stage.",),
                    )
                seen_flow_keys.add(flow_key)

        if inputs_items:
            seen_input_keys: set[str] = set()
            for entry in inputs_items[0].entries:
                if entry.key in seen_input_keys:
                    raise package_compile_error(
                        code="E559",
                        summary="Invalid stage declaration",
                        detail=(
                            f"Stage `{owner_label}` declares input `{entry.key}` "
                            "more than once."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=entry.source_span or inputs_items[0].source_span,
                        hints=("Use a unique key for each stage input.",),
                    )
                seen_input_keys.add(entry.key)
                self._resolve_stage_input_ref(
                    entry.type_ref,
                    unit=unit,
                    owner_label=owner_label,
                    input_key=entry.key,
                    source_span=entry.source_span or inputs_items[0].source_span,
                )

        if emits_items:
            self._resolve_stage_emits_ref(
                emits_items[0].receipt_ref,
                unit=unit,
                owner_label=owner_label,
                source_span=emits_items[0].source_span,
            )

        # Required scalar fields: intent and advance_condition.
        for required_key in ("intent", "advance_condition"):
            if required_key not in scalars_by_key:
                raise package_compile_error(
                    code="E559",
                    summary="Invalid stage declaration",
                    detail=(
                        f"Stage `{owner_label}` is missing required "
                        f"`{required_key}:` field."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=stage_decl.source_span,
                    hints=(
                        f"Add `{required_key}: \"<text>\"` so the stage states "
                        "its purpose.",
                    ),
                )

        checkpoint_value = "durable"
        if "checkpoint" in scalars_by_key:
            checkpoint_item = scalars_by_key["checkpoint"]
            if checkpoint_item.value not in _STAGE_CHECKPOINT_VALUES:
                allowed = ", ".join(sorted(_STAGE_CHECKPOINT_VALUES))
                raise package_compile_error(
                    code="E559",
                    summary="Invalid stage declaration",
                    detail=(
                        f"Stage `{owner_label}` declares `checkpoint: "
                        f"\"{checkpoint_item.value}\"`, but the closed value set "
                        f"is {{{allowed}}}."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=checkpoint_item.source_span
                    or stage_decl.source_span,
                    hints=(
                        "Use one of `durable`, `review_only`, `diagnostic`, or "
                        "`none`.",
                    ),
                )
            checkpoint_value = checkpoint_item.value

        if checkpoint_value in _STAGE_DURABLE_CHECKPOINTS:
            for required_durable_key in ("durable_target", "durable_evidence"):
                if required_durable_key not in scalars_by_key:
                    raise package_compile_error(
                        code="E559",
                        summary="Invalid stage declaration",
                        detail=(
                            f"Stage `{owner_label}` has `checkpoint: durable` "
                            f"but is missing required `{required_durable_key}:` "
                            "field."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=stage_decl.source_span,
                        hints=(
                            "Add the durable evidence the stage owns, or set "
                            "`checkpoint: review_only`, `diagnostic`, or "
                            "`none` if the stage does not own a durable "
                            "artifact.",
                        ),
                    )

        cache.add(cache_key)

    def _resolved_stage_cache(self) -> set[tuple[int, str]]:
        cache = getattr(self, "_resolved_stage_decl_cache", None)
        if cache is None:
            cache = set()
            object.__setattr__(self, "_resolved_stage_decl_cache", cache)
        return cache

    def _resolve_stage_skill_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        role: str,
        error_code: str,
    ) -> tuple[IndexedUnit, model.SkillDecl]:
        try:
            target_unit, target_decl = self._resolve_decl_ref(
                ref,
                unit=unit,
                registry_name="skills_by_name",
                missing_label="skill declaration",
            )
        except CompileError as exc:
            dotted = (
                ".".join((*ref.module_parts, ref.declaration_name))
                if ref.module_parts
                else ref.declaration_name
            )
            role_summary = {
                "owner": "Stage owner is not a declared skill",
                "support": "Stage support is not a declared skill",
            }.get(role, "Stage skill ref is invalid")
            role_hint = {
                "owner": (
                    "Declare the owner skill at the top level, or fix the "
                    "`owner:` ref."
                ),
                "support": (
                    "Declare the support skill at the top level, or fix the "
                    "`supports:` entry."
                ),
            }.get(role, "Fix the stage skill ref.")
            raise package_compile_error(
                code=error_code,
                summary=role_summary,
                detail=(
                    f"Stage `{owner_label}` {role} skill ref `{dotted}` does "
                    "not resolve to a top-level `skill` declaration."
                ),
                path=unit.prompt_file.source_path,
                source_span=ref.source_span,
                hints=(role_hint,),
            ) from exc
        return target_unit, target_decl

    def _resolve_stage_lane_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span,
    ) -> None:
        # The lane ref is `EnumName.member`. The last dotted part is the member
        # key; the rest names the enum declaration. The compiler already has a
        # `_try_resolve_enum_decl` helper for this shape.
        dotted = (
            ".".join((*ref.module_parts, ref.declaration_name))
            if ref.module_parts
            else ref.declaration_name
        )
        if not ref.module_parts:
            raise package_compile_error(
                code="E559",
                summary="Invalid stage declaration",
                detail=(
                    f"Stage `{owner_label}` `lane:` value `{dotted}` is not a "
                    "dotted `EnumName.member` reference."
                ),
                path=unit.prompt_file.source_path,
                source_span=ref.source_span or source_span,
                hints=(
                    "Use `lane: <EnumName>.<member>` so the lane resolves to a "
                    "declared enum member.",
                ),
            )
        enum_ref = model.NameRef(
            module_parts=ref.module_parts[:-1],
            declaration_name=ref.module_parts[-1],
            source_span=ref.source_span,
        )
        member_key = ref.declaration_name
        enum_decl = self._try_resolve_enum_decl(enum_ref, unit=unit)
        if enum_decl is None:
            raise package_compile_error(
                code="E559",
                summary="Invalid stage declaration",
                detail=(
                    f"Stage `{owner_label}` `lane:` value `{dotted}` does not "
                    "resolve to a declared enum member."
                ),
                path=unit.prompt_file.source_path,
                source_span=ref.source_span or source_span,
                hints=(
                    "Declare the enum at the top level, or fix the `lane:` "
                    "ref.",
                ),
            )
        if not any(member.key == member_key for member in enum_decl.members):
            raise package_compile_error(
                code="E559",
                summary="Invalid stage declaration",
                detail=(
                    f"Stage `{owner_label}` `lane:` value `{dotted}` names a "
                    f"member that is not on enum `{enum_decl.name}`."
                ),
                path=unit.prompt_file.source_path,
                source_span=ref.source_span or source_span,
                hints=(
                    "Use one of the enum members declared on the lane enum.",
                ),
            )

    def _resolve_stage_skill_flow_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span,
    ) -> tuple[IndexedUnit, model.SkillFlowDecl]:
        try:
            return self._resolve_decl_ref(
                ref,
                unit=unit,
                registry_name="skill_flows_by_name",
                missing_label="skill_flow declaration",
            )
        except CompileError as exc:
            dotted = (
                ".".join((*ref.module_parts, ref.declaration_name))
                if ref.module_parts
                else ref.declaration_name
            )
            raise package_compile_error(
                code="E559",
                summary="Invalid stage declaration",
                detail=(
                    f"Stage `{owner_label}` `applies_to:` ref `{dotted}` does "
                    "not resolve to a top-level `skill_flow` declaration."
                ),
                path=unit.prompt_file.source_path,
                source_span=ref.source_span or source_span,
                hints=(
                    "Declare the `skill_flow` at the top level, or fix the "
                    "`applies_to:` ref.",
                ),
            ) from exc

    def _resolve_stage_input_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        input_key: str,
        source_span,
    ) -> None:
        lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        for lookup_target in lookup_targets:
            target_decls = unit_declarations(lookup_target.unit)
            target_name = lookup_target.declaration_name
            if (
                target_name in target_decls.receipts_by_name
                or target_name in target_decls.documents_by_name
                or target_name in target_decls.schemas_by_name
                or target_name in target_decls.tables_by_name
            ):
                return
        dotted = (
            ".".join((*ref.module_parts, ref.declaration_name))
            if ref.module_parts
            else ref.declaration_name
        )
        raise package_compile_error(
            code="E548",
            summary="Stage input type is invalid",
            detail=(
                f"Stage `{owner_label}` input `{input_key}` is typed as "
                f"`{dotted}`, but that name does not resolve to a top-level "
                "`receipt`, `document`, `schema`, or `table` declaration."
            ),
            path=unit.prompt_file.source_path,
            source_span=ref.source_span or source_span,
            hints=(
                "Stage inputs must point at a top-level `receipt`, `document`, "
                "`schema`, or `table` declaration in scope.",
            ),
        )

    def _resolve_stage_emits_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span,
    ) -> None:
        lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        for lookup_target in lookup_targets:
            target_decls = unit_declarations(lookup_target.unit)
            if lookup_target.declaration_name in target_decls.receipts_by_name:
                return
        dotted = (
            ".".join((*ref.module_parts, ref.declaration_name))
            if ref.module_parts
            else ref.declaration_name
        )
        raise package_compile_error(
            code="E549",
            summary="Stage emit type is invalid",
            detail=(
                f"Stage `{owner_label}` `emits:` value `{dotted}` does not "
                "resolve to a top-level `receipt` declaration."
            ),
            path=unit.prompt_file.source_path,
            source_span=ref.source_span or source_span,
            hints=(
                "Declare the emitted receipt at the top level, or fix the "
                "`emits:` ref to point at one.",
            ),
        )

    def _validate_all_stages_in_flow(self, flow) -> None:
        registry = getattr(flow, "stages_by_name", None)
        if not registry:
            return
        validated_key = (flow.prompt_root.resolve(), flow.flow_root.resolve())
        cache = getattr(self, "_stages_validated_flows", None)
        if cache is None:
            cache = set()
            object.__setattr__(self, "_stages_validated_flows", cache)
        if validated_key in cache:
            return
        cache.add(validated_key)
        for stage_decl in registry.values():
            owner_unit = flow.declaration_owner_units_by_id[id(stage_decl)]
            self._resolve_stage_decl(stage_decl, unit=owner_unit)
