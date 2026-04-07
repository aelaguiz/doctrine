from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from doctrine import model
from doctrine.diagnostics import CompileError, DiagnosticLocation, DoctrineError
from doctrine.parser import parse_file


@dataclass(slots=True, frozen=True)
class CompiledSection:
    title: str
    body: tuple[CompiledBodyItem, ...]


@dataclass(slots=True, frozen=True)
class CompiledAgent:
    name: str
    fields: tuple[CompiledField, ...]


CompiledBodyItem: TypeAlias = model.ProseLine | CompiledSection
CompiledField: TypeAlias = model.RoleScalar | CompiledSection
ReadableDecl: TypeAlias = (
    model.Agent
    | model.InputDecl
    | model.InputSourceDecl
    | model.OutputDecl
    | model.OutputTargetDecl
    | model.OutputShapeDecl
    | model.JsonSchemaDecl
    | model.SkillDecl
)


@dataclass(slots=True, frozen=True)
class IndexedUnit:
    module_parts: tuple[str, ...]
    prompt_file: model.PromptFile
    imports: tuple[model.ImportDecl, ...]
    workflows_by_name: dict[str, model.WorkflowDecl]
    inputs_blocks_by_name: dict[str, model.InputsDecl]
    inputs_by_name: dict[str, model.InputDecl]
    input_sources_by_name: dict[str, model.InputSourceDecl]
    outputs_blocks_by_name: dict[str, model.OutputsDecl]
    outputs_by_name: dict[str, model.OutputDecl]
    output_targets_by_name: dict[str, model.OutputTargetDecl]
    output_shapes_by_name: dict[str, model.OutputShapeDecl]
    json_schemas_by_name: dict[str, model.JsonSchemaDecl]
    skills_by_name: dict[str, model.SkillDecl]
    skills_blocks_by_name: dict[str, model.SkillsDecl]
    agents_by_name: dict[str, model.Agent]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]


@dataclass(slots=True, frozen=True)
class ResolvedRouteLine:
    label: str
    target_name: str


@dataclass(slots=True, frozen=True)
class ResolvedSectionRef:
    label: str


ResolvedSectionBodyItem: TypeAlias = model.ProseLine | ResolvedRouteLine | ResolvedSectionRef


@dataclass(slots=True, frozen=True)
class ResolvedSectionItem:
    key: str
    title: str
    items: tuple[ResolvedSectionBodyItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedUseItem:
    key: str
    target_unit: IndexedUnit
    workflow_decl: model.WorkflowDecl


@dataclass(slots=True, frozen=True)
class ResolvedSkillEntry:
    key: str
    metadata_unit: IndexedUnit
    target_unit: IndexedUnit
    skill_decl: model.SkillDecl
    items: tuple[model.RecordItem, ...]


ResolvedSkillsSectionBodyItem: TypeAlias = model.ProseLine | ResolvedSkillEntry


@dataclass(slots=True, frozen=True)
class ResolvedSkillsSection:
    key: str
    title: str
    items: tuple[ResolvedSkillsSectionBodyItem, ...]


ResolvedSkillsItem = ResolvedSkillsSection | ResolvedSkillEntry


@dataclass(slots=True, frozen=True)
class ResolvedSkillsBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedSkillsItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedIoSection:
    key: str
    section: CompiledSection


@dataclass(slots=True, frozen=True)
class ResolvedIoRef:
    section: CompiledSection


ResolvedIoItem = ResolvedIoSection | ResolvedIoRef


@dataclass(slots=True, frozen=True)
class ResolvedIoBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedIoItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedWorkflowSkillsItem:
    key: str
    body: ResolvedSkillsBody


ResolvedWorkflowItem = ResolvedSectionItem | ResolvedUseItem | ResolvedWorkflowSkillsItem


@dataclass(slots=True, frozen=True)
class ResolvedWorkflowBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedWorkflowItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedAgentSlot:
    key: str
    body: ResolvedWorkflowBody


@dataclass(slots=True, frozen=True)
class ResolvedAbstractAgentSlot:
    key: str


ResolvedAgentSlotState = ResolvedAgentSlot | ResolvedAbstractAgentSlot


@dataclass(slots=True, frozen=True)
class ConfigSpec:
    title: str
    required_keys: dict[str, str]
    optional_keys: dict[str, str]


_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
_INTERPOLATION_EXPR_RE = re.compile(
    r"\s*"
    r"([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
    r"(?:\s*:\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*))?"
    r"\s*"
)
_INTERPOLATION_RE = re.compile(r"\{\{([^{}]+)\}\}")
# Reserved typed fields get their own compiler paths. Every other key is an
# authored workflow slot, with one legacy carve-out: the old `workflow` field
# still preserves 01-06 body inheritance semantics instead of switching to a
# second slot-patching dialect.
_RESERVED_AGENT_FIELD_KEYS = {"role", "inputs", "outputs", "skills"}

_BUILTIN_INPUT_SOURCES = {
    "Prompt": ConfigSpec(title="Prompt", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
    "EnvVar": ConfigSpec(title="EnvVar", required_keys={"env": "Env"}, optional_keys={}),
}

_BUILTIN_OUTPUT_TARGETS = {
    "TurnResponse": ConfigSpec(title="Turn Response", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
}

_WORKFLOW_MENTION_REGISTRIES = (
    ("agent declaration", "agents_by_name"),
    ("input declaration", "inputs_by_name"),
    ("input source declaration", "input_sources_by_name"),
    ("output declaration", "outputs_by_name"),
    ("output target declaration", "output_targets_by_name"),
    ("output shape declaration", "output_shapes_by_name"),
    ("json schema declaration", "json_schemas_by_name"),
    ("skill declaration", "skills_by_name"),
)


class CompilationContext:
    def __init__(self, prompt_file: model.PromptFile):
        self.prompt_root = _resolve_prompt_root(prompt_file.source_path)
        self._module_cache: dict[tuple[str, ...], IndexedUnit] = {}
        self._loading_modules: set[tuple[str, ...]] = set()
        self._workflow_compile_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._inputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._outputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._agent_slot_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._resolved_workflow_cache: dict[tuple[tuple[str, ...], str], ResolvedWorkflowBody] = {}
        self._resolved_skills_cache: dict[tuple[tuple[str, ...], str], ResolvedSkillsBody] = {}
        self._resolved_inputs_cache: dict[tuple[tuple[str, ...], str], ResolvedIoBody] = {}
        self._resolved_outputs_cache: dict[tuple[tuple[str, ...], str], ResolvedIoBody] = {}
        self._resolved_agent_slot_cache: dict[
            tuple[tuple[str, ...], str],
            tuple[ResolvedAgentSlotState, ...],
        ] = {}
        self.root_unit = self._index_unit(prompt_file, module_parts=())

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        agent = self.root_unit.agents_by_name.get(agent_name)
        if agent is None:
            raise CompileError(f"Missing target agent: {agent_name}")
        if agent.abstract:
            raise CompileError(f"Abstract agent does not render: {agent_name}")
        return self._compile_agent_decl(agent, unit=self.root_unit)

    def _compile_agent_decl(self, agent: model.Agent, *, unit: IndexedUnit) -> CompiledAgent:
        self._enforce_legacy_role_workflow_order(agent)
        resolved_slot_states = self._resolve_agent_slots(agent, unit=unit)
        unresolved_abstract_slots = [
            slot.key
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAbstractAgentSlot)
        ]
        if unresolved_abstract_slots:
            missing = ", ".join(unresolved_abstract_slots)
            raise CompileError(
                f"E209 Concrete agent is missing abstract authored slots in agent {agent.name}: {missing}"
            )
        resolved_slots = {
            slot.key: slot.body
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAgentSlot)
        }
        compiled_fields: list[CompiledField] = []
        seen_role = False
        seen_typed_fields: set[str] = set()

        for field in agent.fields:
            if isinstance(field, model.RoleScalar):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                compiled_fields.append(
                    model.RoleScalar(
                        text=self._interpolate_authored_prose_string(
                            field.text,
                            unit=unit,
                            owner_label=f"agent {agent.name}",
                            surface_label="role prose",
                        )
                    )
                )
                seen_role = True
                continue

            if isinstance(field, model.RoleBlock):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                compiled_fields.append(
                    CompiledSection(
                        title=field.title,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"agent {agent.name}",
                                surface_label="role prose",
                            )
                            for line in field.lines
                        ),
                    )
                )
                seen_role = True
                continue

            if isinstance(
                field,
                (
                    model.AuthoredSlotField,
                    model.AuthoredSlotAbstract,
                    model.AuthoredSlotInherit,
                    model.AuthoredSlotOverride,
                ),
            ):
                slot_body = resolved_slots.get(field.key)
                if slot_body is None:
                    raise CompileError(
                        f"Internal compiler error: missing resolved authored slot in agent {agent.name}: {field.key}"
                    )
                compiled_fields.append(self._compile_resolved_workflow(slot_body))
                continue

            field_key = self._typed_field_key(field)
            if field_key in seen_typed_fields:
                raise CompileError(f"Duplicate typed field in agent {agent.name}: {field_key}")
            seen_typed_fields.add(field_key)

            if isinstance(field, model.InputsField):
                compiled_fields.append(
                    self._compile_inputs_field(
                        field,
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                    )
                )
                continue
            if isinstance(field, model.OutputsField):
                compiled_fields.append(
                    self._compile_outputs_field(
                        field,
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                    )
                )
                continue
            if isinstance(field, model.SkillsField):
                compiled_fields.append(self._compile_skills_field(field, unit=unit))
                continue

            raise CompileError(
                f"Unsupported agent field in {agent.name}: {type(field).__name__}"
            )

        if not seen_role:
            raise CompileError(f"Concrete agent is missing role field: {agent.name}")

        return CompiledAgent(name=agent.name, fields=tuple(compiled_fields))

    def _typed_field_key(self, field: model.Field) -> str:
        if isinstance(field, model.InputsField):
            return "inputs"
        if isinstance(field, model.OutputsField):
            return "outputs"
        if isinstance(field, model.SkillsField):
            return "skills"
        return type(field).__name__

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

    def _resolve_agent_slots(
        self, agent: model.Agent, *, unit: IndexedUnit
    ) -> tuple[ResolvedAgentSlotState, ...]:
        agent_key = (unit.module_parts, agent.name)
        cached = self._resolved_agent_slot_cache.get(agent_key)
        if cached is not None:
            return cached

        if agent_key in self._agent_slot_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._agent_slot_resolution_stack, agent_key]
            )
            raise CompileError(f"Cyclic agent inheritance: {cycle}")

        self._agent_slot_resolution_stack.append(agent_key)
        try:
            parent_slots: tuple[ResolvedAgentSlotState, ...] = ()
            parent_label: str | None = None
            if agent.parent_ref is not None:
                parent_unit, parent_agent = self._resolve_parent_agent_decl(agent, unit=unit)
                parent_slots = self._resolve_agent_slots(parent_agent, unit=parent_unit)
                parent_label = f"agent {_dotted_decl_name(parent_unit.module_parts, parent_agent.name)}"

            parent_slots_by_key = {slot.key: slot for slot in parent_slots}
            resolved_slots: list[ResolvedAgentSlotState] = []
            seen_slot_keys: set[str] = set()
            accounted_parent_concrete_keys: set[str] = set()

            for field in agent.fields:
                if isinstance(field, model.AuthoredSlotField):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)

                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        if field.key == "workflow" and isinstance(field.value, model.WorkflowBody):
                            resolved_body = self._resolve_workflow_body(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot workflow",
                                parent_workflow=parent_slot.body,
                                parent_label=f"{parent_label} slot workflow",
                            )
                            accounted_parent_concrete_keys.add(field.key)
                            resolved_slots.append(
                                ResolvedAgentSlot(key=field.key, body=resolved_body)
                            )
                            continue
                        raise CompileError(
                            f"Inherited authored slot requires `inherit {field.key}` or `override {field.key}` in agent {agent.name}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        resolved_slots.append(
                            ResolvedAgentSlot(
                                key=field.key,
                                body=self._resolve_slot_value(
                                    field.value,
                                    unit=unit,
                                    owner_label=f"agent {agent.name} slot {field.key}",
                                ),
                            )
                        )
                        continue

                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )
                    continue

                if isinstance(field, model.AuthoredSlotAbstract):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(ResolvedAbstractAgentSlot(key=field.key))
                    continue

                if isinstance(field, model.AuthoredSlotInherit):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"Cannot inherit undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(parent_slot)
                    continue

                if isinstance(field, model.AuthoredSlotOverride):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E001 Cannot override undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )

            missing_parent_keys = [
                parent_slot.key
                for parent_slot in parent_slots
                if isinstance(parent_slot, ResolvedAgentSlot)
                and parent_slot.key not in accounted_parent_concrete_keys
            ]
            if missing_parent_keys:
                missing = ", ".join(missing_parent_keys)
                raise CompileError(
                    f"E003 Missing inherited authored slot in agent {agent.name}: {missing}"
                )

            for parent_slot in parent_slots:
                if (
                    isinstance(parent_slot, ResolvedAbstractAgentSlot)
                    and parent_slot.key not in seen_slot_keys
                ):
                    resolved_slots.append(parent_slot)

            resolved = tuple(resolved_slots)
            self._resolved_agent_slot_cache[agent_key] = resolved
            return resolved
        finally:
            self._agent_slot_resolution_stack.pop()

    def _ensure_valid_authored_slot_key(self, key: str, agent_name: str) -> None:
        if key in _RESERVED_AGENT_FIELD_KEYS:
            raise CompileError(
                f"Reserved typed agent field cannot be used as authored slot in {agent_name}: {key}"
            )

    def _resolve_slot_value(
        self,
        value: model.WorkflowSlotValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedWorkflowBody:
        if isinstance(value, model.WorkflowBody):
            return self._resolve_workflow_body(
                value,
                unit=unit,
                owner_label=owner_label,
            )
        target_unit, workflow_decl = self._resolve_workflow_ref(value, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=target_unit)

    def _compile_inputs_field(
        self,
        field: model.InputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> CompiledSection:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="inputs",
            owner_label=owner_label,
        )

    def _compile_outputs_field(
        self,
        field: model.OutputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> CompiledSection:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="outputs",
            owner_label=owner_label,
        )

    def _compile_io_field(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> CompiledSection:
        if field.parent_ref is not None:
            resolved = self._resolve_io_field_patch(
                field,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
            )
            return self._compile_resolved_io_body(resolved)

        if isinstance(field.value, tuple):
            if field.title is None:
                raise CompileError(
                    f"Internal compiler error: {field_kind} field is missing title in {owner_label}"
                )
            return CompiledSection(
                title=field.title,
                body=self._compile_contract_bucket_items(
                    field.value,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} field `{field.title}`",
                ),
            )

        if isinstance(field.value, model.NameRef):
            resolved = self._resolve_io_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
            )
            return self._compile_resolved_io_body(resolved)

        raise CompileError(
            f"Internal compiler error: unsupported {field_kind} field value in {owner_label}: "
            f"{type(field.value).__name__}"
        )

    def _compile_resolved_io_body(self, io_body: ResolvedIoBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(io_body.preamble)
        for item in io_body.items:
            body.append(item.section)
        return CompiledSection(title=io_body.title, body=tuple(body))

    def _resolve_io_field_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
    ) -> ResolvedIoBody:
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
            return self._resolve_inputs_decl(inputs_decl, unit=target_unit)

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
        return self._resolve_outputs_decl(outputs_decl, unit=target_unit)

    def _resolve_io_field_patch(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ResolvedIoBody:
        parent_ref = field.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing parent ref in {owner_label}"
            )
        if not isinstance(field.value, model.IoBody) or field.title is None:
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
            parent_unit, parent_decl = self._resolve_inputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
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
            parent_unit, parent_decl = self._resolve_outputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_outputs_decl(parent_decl, unit=parent_unit)

        return self._resolve_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_io=parent_body,
            parent_label=f"{field_kind} {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}",
        )

    def _compile_skills_field(
        self, field: model.SkillsField, *, unit: IndexedUnit
    ) -> CompiledSection:
        return self._compile_resolved_skills(
            self._resolve_skills_value(
                field.value,
                unit=unit,
                owner_label="agent skills field",
            )
        )

    def _compile_contract_bucket_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
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
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_contract_bucket_items(
                            item.items,
                            unit=unit,
                            field_kind=field_kind,
                            owner_label=f"{field_kind} section `{item.title}`",
                        ),
                    )
                )
                continue

            if isinstance(item, model.RecordRef):
                body.append(
                    self._compile_contract_bucket_ref(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            raise CompileError(
                f"Unsupported {field_kind} bucket item in {owner_label}: {type(item).__name__}"
            )

        return tuple(body)

    def _compile_contract_bucket_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> CompiledSection:
        if item.body is not None:
            raise CompileError(
                f"Declaration refs cannot define inline bodies in {owner_label}: "
                f"{_dotted_ref_name(item.ref)}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise CompileError(
                    "Inputs refs must resolve to input declarations, not output declarations: "
                    f"{_dotted_ref_name(item.ref)}"
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return self._compile_input_decl(decl, unit=target_unit)

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise CompileError(
                "Outputs refs must resolve to output declarations, not input declarations: "
                f"{_dotted_ref_name(item.ref)}"
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        return self._compile_output_decl(decl, unit=target_unit)

    def _compile_resolved_skills(self, skills_body: ResolvedSkillsBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(skills_body.preamble)
        for item in skills_body.items:
            if isinstance(item, ResolvedSkillsSection):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_resolved_skills_section_items(item.items),
                    )
                )
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return CompiledSection(title=skills_body.title, body=tuple(body))

    def _compile_resolved_skills_section_items(
        self,
        items: tuple[ResolvedSkillsSectionBodyItem, ...],
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return tuple(body)

    def _compile_resolved_skill_entry(self, entry: ResolvedSkillEntry) -> CompiledSection:
        target_unit = entry.target_unit
        skill_decl = entry.skill_decl
        scalar_items, _section_items, extras = self._split_record_items(
            skill_decl.items,
            scalar_keys={"purpose"},
            owner_label=f"skill {skill_decl.name}",
        )
        purpose_item = scalar_items.get("purpose")
        if purpose_item is None or not isinstance(purpose_item.value, str):
            raise CompileError(f"Skill is missing string purpose: {skill_decl.name}")

        metadata_scalars, _metadata_sections, metadata_extras = self._split_record_items(
            entry.items,
            scalar_keys={"requirement", "reason"},
            owner_label=f"skill reference {skill_decl.name}",
        )

        body: list[CompiledBodyItem] = []
        purpose_body: list[CompiledBodyItem] = [
            self._interpolate_authored_prose_string(
                purpose_item.value,
                unit=target_unit,
                owner_label=f"skill {skill_decl.name}",
                surface_label="skill purpose",
            )
        ]
        requirement = metadata_scalars.get("requirement")
        if requirement is not None and _value_to_symbol(requirement.value) == "Required":
            purpose_body.extend(
                [
                    "",
                    "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
                ]
            )
        body.append(CompiledSection(title="Purpose", body=tuple(purpose_body)))

        for extra in extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=target_unit,
                    owner_label=f"skill {skill_decl.name}",
                    surface_label="skill prose",
                )
            )

        reason = metadata_scalars.get("reason")
        if reason is not None:
            if not isinstance(reason.value, str):
                raise CompileError(
                    f"Skill reference reason must be a string in {skill_decl.name}"
                )
            body.append(
                CompiledSection(
                    title="Reason",
                    body=(
                        self._interpolate_authored_prose_string(
                            reason.value,
                            unit=entry.metadata_unit,
                            owner_label=f"skill reference {skill_decl.name}",
                            surface_label="skill reason",
                        ),
                    ),
                )
            )

        for extra in metadata_extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=entry.metadata_unit,
                    owner_label=f"skill reference {skill_decl.name}",
                    surface_label="skill reference prose",
                )
            )

        return CompiledSection(title=skill_decl.title, body=tuple(body))

    def _compile_input_decl(self, decl: model.InputDecl, *, unit: IndexedUnit) -> CompiledSection:
        scalar_items, _section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {decl.name}",
        )
        source_item = scalar_items.get("source")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        if source_item is None or not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input is missing typed source: {decl.name}")
        if shape_item is None:
            raise CompileError(f"Input is missing shape: {decl.name}")
        if requirement_item is None:
            raise CompileError(f"Input is missing requirement: {decl.name}")

        source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
        body: list[CompiledBodyItem] = [f"- Source: {source_spec.title}"]
        body.extend(
            self._compile_config_lines(
                source_item.body or (),
                spec=source_spec,
                unit=unit,
                owner_label=f"input {decl.name} source",
            )
        )
        body.append(f"- Shape: {self._display_symbol_value(shape_item.value, unit=unit)}")
        body.append(
            f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit)}"
        )

        if extras:
            body.append("")
            body.extend(
                self._compile_record_support_items(
                    extras,
                    unit=unit,
                    owner_label=f"input {decl.name}",
                    surface_label="input prose",
                )
            )

        return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_output_decl(
        self, decl: model.OutputDecl, *, unit: IndexedUnit
    ) -> CompiledSection:
        scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {decl.name}",
        )

        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        if files_section is not None and (target_item is not None or shape_item is not None):
            raise CompileError(
                f"Output mixes `files` with `target` or `shape`: {decl.name}"
            )
        if files_section is None and (target_item is None or shape_item is None):
            raise CompileError(
                f"Output must define either `files` or both `target` and `shape`: {decl.name}"
            )

        body: list[CompiledBodyItem] = []
        if files_section is not None:
            body.extend(self._compile_output_files(files_section, unit=unit, output_name=decl.name))
        else:
            if not isinstance(target_item.value, model.NameRef):
                raise CompileError(f"Output target must be typed: {decl.name}")
            target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
            body.append(f"- Target: {target_spec.title}")
            body.extend(
                self._compile_config_lines(
                    target_item.body or (),
                    spec=target_spec,
                    unit=unit,
                    owner_label=f"output {decl.name} target",
                )
            )
            body.append(f"- Shape: {self._display_output_shape(shape_item.value, unit=unit)}")

        if requirement_item is not None:
            body.append(
                f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit)}"
            )

        if extras:
            body.append("")
            body.extend(
                self._compile_record_support_items(
                    extras,
                    unit=unit,
                    owner_label=f"output {decl.name}",
                    surface_label="output prose",
                )
            )

        return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_output_files(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise CompileError(
                    f"`files` entries must be titled sections in output {output_name}"
                )
            scalar_items, _section_items, extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise CompileError(
                    f"Output file entry is missing string path in {output_name}: {item.key}"
                )
            if shape_item is None:
                raise CompileError(
                    f"Output file entry is missing shape in {output_name}: {item.key}"
                )
            body.append(f"- {item.title}: `{path_item.value}`")
            body.append(
                f"- {item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit)}"
            )
            if extras:
                body.append("")
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_record_support_items(
                            extras,
                            unit=unit,
                            owner_label=f"output {output_name} file {item.key}",
                            surface_label="output file prose",
                        ),
                    )
                )
        return tuple(body)

    def _compile_record_support_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            body.extend(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                )
            )
        return tuple(body)

    def _compile_record_item(
        self,
        item: model.RecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return (
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                ),
            )

        if isinstance(item, model.RecordSection):
            return (
                CompiledSection(
                    title=item.title,
                    body=self._compile_record_support_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label=surface_label,
                    ),
                ),
            )

        if isinstance(item, model.RecordScalar):
            return self._compile_fallback_scalar(
                item,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
            )

        if isinstance(item, model.RecordRef):
            body = (
                self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    surface_label=surface_label,
                )
                if item.body is not None
                else ()
            )
            return (
                CompiledSection(
                    title=self._display_ref(item.ref),
                    body=body,
                ),
            )

        raise CompileError(f"Unsupported record item: {type(item).__name__}")

    def _compile_fallback_scalar(
        self,
        item: model.RecordScalar,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        label = _humanize_key(item.key)
        value = self._format_scalar_value(item.value, unit=unit)
        if item.body is None:
            return (f"- {label}: {value}",)

        body: list[CompiledBodyItem] = [value]
        body.extend(
            self._compile_record_support_items(
                item.body,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
            )
        )
        return (CompiledSection(title=label, body=tuple(body)),)

    def _compile_config_lines(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        seen_keys: set[str] = set()
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(f"Config entries must be scalar key/value lines in {owner_label}")
            if item.key in seen_keys:
                raise CompileError(f"Duplicate config key in {owner_label}: {item.key}")
            seen_keys.add(item.key)
            if item.key not in allowed_keys:
                raise CompileError(f"Unknown config key in {owner_label}: {item.key}")
            body.append(
                f"- {allowed_keys[item.key]}: {self._format_scalar_value(item.value, unit=unit)}"
            )

        missing_required = [
            key for key in spec.required_keys if key not in seen_keys
        ]
        if missing_required:
            missing = ", ".join(missing_required)
            raise CompileError(f"Missing required config key in {owner_label}: {missing}")

        return tuple(body)

    def _resolve_input_source_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_INPUT_SOURCES.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.input_sources_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(local_decl, owner_label=f"input source {local_decl.name}")

        target_unit, decl = self._resolve_input_source_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"input source {decl.name}")

    def _resolve_output_target_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_OUTPUT_TARGETS.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.output_targets_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(
                    local_decl,
                    owner_label=f"output target {local_decl.name}",
                )

        target_unit, decl = self._resolve_output_target_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"output target {decl.name}")

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
        self, value: model.RecordScalarValue, *, unit: IndexedUnit
    ) -> str:
        if isinstance(value, str):
            return value
        if value.module_parts:
            _target_unit, decl = self._resolve_output_shape_decl(value, unit=unit)
            return decl.title
        local_decl = unit.output_shapes_by_name.get(value.declaration_name)
        if local_decl is not None:
            return local_decl.title
        return _humanize_key(value.declaration_name)

    def _display_symbol_value(
        self, value: model.RecordScalarValue, *, unit: IndexedUnit
    ) -> str:
        if isinstance(value, str):
            return value
        return self._display_ref(value)

    def _format_scalar_value(
        self, value: model.RecordScalarValue, *, unit: IndexedUnit
    ) -> str:
        if isinstance(value, str):
            return f"`{value}`"
        return self._display_ref(value)

    def _display_ref(self, ref: model.NameRef) -> str:
        if ref.module_parts:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return _humanize_key(ref.declaration_name)

    def _resolve_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._resolved_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_resolution_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._resolved_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_resolution_stack.pop()

    def _resolve_skills_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._resolved_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._skills_resolution_stack, skills_key]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._resolved_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_resolution_stack.pop()

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
            raise CompileError(f"Cyclic inputs inheritance: {cycle}")

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

    def _resolve_outputs_decl(
        self, outputs_decl: model.OutputsDecl, *, unit: IndexedUnit
    ) -> ResolvedIoBody:
        outputs_key = (unit.module_parts, outputs_decl.name)
        cached = self._resolved_outputs_cache.get(outputs_key)
        if cached is not None:
            return cached

        if outputs_key in self._outputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._outputs_resolution_stack, outputs_key]
            )
            raise CompileError(f"Cyclic outputs inheritance: {cycle}")

        self._outputs_resolution_stack.append(outputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if outputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_outputs_decl(
                    outputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_outputs_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_io_body(
                outputs_decl.body,
                unit=unit,
                field_kind="outputs",
                owner_label=_dotted_decl_name(unit.module_parts, outputs_decl.name),
                parent_io=parent_io,
                parent_label=parent_label,
            )
            self._resolved_outputs_cache[outputs_key] = resolved
            return resolved
        finally:
            self._outputs_resolution_stack.pop()

    def _resolve_skills_value(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_decl(skills_decl, unit=target_unit)
        return self._resolve_skills_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_io: ResolvedIoBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedIoBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{field_kind} prose",
                ambiguous_label=f"{field_kind} prose interpolation ref",
            )
            for line in io_body.preamble
        )
        if parent_io is None:
            return ResolvedIoBody(
                title=io_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_io_items(
                    io_body.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                ),
            )

        unkeyed_parent_titles = [
            item.section.title for item in parent_io.items if isinstance(item, ResolvedIoRef)
        ]
        if unkeyed_parent_titles:
            details = ", ".join(unkeyed_parent_titles)
            raise CompileError(
                f"Cannot inherit {field_kind} block with unkeyed top-level refs in {parent_label}: {details}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_io.items if isinstance(item, ResolvedIoSection)
        }
        resolved_items: list[ResolvedIoItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in io_body.items:
            if isinstance(item, model.RecordRef):
                resolved_items.append(
                    self._resolve_io_ref_item(
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
                    self._resolve_io_section_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                    )
                )
                continue

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
                ResolvedIoSection(
                    key=key,
                    section=CompiledSection(
                        title=item.title if item.title is not None else parent_item.section.title,
                        body=self._compile_contract_bucket_items(
                            item.items,
                            unit=unit,
                            field_kind=field_kind,
                            owner_label=(
                                f"{field_kind} section `{item.title if item.title is not None else parent_item.section.title}`"
                            ),
                        ),
                    ),
                )
            )

        missing_keys = [
            item.key for item in parent_io.items if isinstance(item, ResolvedIoSection) and item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited {field_kind} entry in {owner_label}: {missing}"
            )

        return ResolvedIoBody(
            title=io_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_skills_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="skills prose",
                ambiguous_label="skills prose interpolation ref",
            )
            for line in skills_body.preamble
        )
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(
                    self._resolve_skill_entry(
                        item,
                        unit=unit,
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined skills entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined skills entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise CompileError(
                        f"Override kind mismatch for skills entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(
                self._resolve_skill_entry(
                    item,
                    unit=unit,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited skills entry in {owner_label}: {missing}"
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_workflow_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="workflow strings",
                ambiguous_label="workflow string interpolation ref",
            )
            for line in workflow_body.preamble
        )
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_non_inherited_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: set[str] = set()

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited skills block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_io_items(
        self,
        io_items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> tuple[ResolvedIoItem, ...]:
        resolved_items: list[ResolvedIoItem] = []
        seen_keys: set[str] = set()

        for item in io_items:
            if isinstance(item, model.RecordRef):
                resolved_items.append(
                    self._resolve_io_ref_item(
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
                    self._resolve_io_section_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited {field_kind} block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_io_section_item(
        self,
        item: model.RecordSection,
        *,
        unit: IndexedUnit,
        field_kind: str,
    ) -> ResolvedIoSection:
        return ResolvedIoSection(
            key=item.key,
            section=CompiledSection(
                title=item.title,
                body=self._compile_contract_bucket_items(
                    item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} section `{item.title}`",
                ),
            ),
        )

    def _resolve_io_ref_item(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ResolvedIoRef:
        return ResolvedIoRef(
            section=self._compile_contract_bucket_ref(
                item,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
            )
        )

    def _resolve_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="skills prose",
                        ambiguous_label="skills prose interpolation ref",
                    )
                )
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_skill_entry(
        self,
        entry: model.SkillEntry | model.OverrideSkillEntry,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillEntry:
        target_unit, skill_decl = self._resolve_skill_decl(entry.target, unit=unit)
        return ResolvedSkillEntry(
            key=entry.key,
            metadata_unit=unit,
            target_unit=target_unit,
            skill_decl=skill_decl,
            items=entry.items,
        )

    def _resolve_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if isinstance(item, str):
                resolved.append(
                    self._interpolate_authored_prose_string(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.EmphasizedLine):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.SectionBodyRef):
                resolved.append(
                    self._resolve_section_body_ref(item.ref, unit=unit, owner_label=owner_label)
                )
                continue
            self._validate_route_target(item.target, unit=unit)
            resolved.append(
                ResolvedRouteLine(
                    label=self._interpolate_authored_prose_string(
                        item.label,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="route labels",
                    ),
                    target_name=item.target.declaration_name,
                )
            )
        return tuple(resolved)

    def _resolve_section_body_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSectionRef:
        _target_unit, decl = self._resolve_readable_decl(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label="workflow section bodies",
            ambiguous_label="workflow section declaration ref",
            missing_local_label="workflow section body",
        )
        return ResolvedSectionRef(label=self._display_readable_decl(decl))

    def _interpolate_authored_prose_string(
        self,
        value: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
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
    ) -> model.ProseLine:
        if isinstance(value, str):
            return self._interpolate_authored_prose_string(
                value,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
            )
        return model.EmphasizedLine(
            kind=value.kind,
            text=self._interpolate_authored_prose_string(
                value.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
            ),
        )

    def _resolve_authored_prose_interpolation_expr(
        self,
        expression: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
    ) -> str:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            raise CompileError(
                f"Invalid interpolation in {owner_label}: {{{{{expression}}}}}"
            )

        ref = _name_ref_from_dotted_name(match.group(1))
        field_path = tuple(match.group(2).split(".")) if match.group(2) is not None else None
        target_unit, decl = self._resolve_readable_decl(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=ambiguous_label or f"{surface_label} interpolation ref",
            missing_local_label=surface_label,
        )
        return self._resolve_readable_decl_field(
            decl,
            field_path,
            unit=target_unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=_dotted_ref_name(ref) if ref.module_parts else ref.declaration_name,
        )

    def _resolve_readable_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
    ) -> tuple[IndexedUnit, ReadableDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_readable_decl_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    f"Abstract agent refs are not allowed in {surface_label}; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if target_unit.workflows_by_name.get(ref.declaration_name) is not None:
            raise CompileError(
                f"Workflow refs are not allowed in {surface_label}; "
                f"use `use` for workflow composition: {dotted_name}"
            )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_readable_decl_field(
        self,
        decl: ReadableDecl,
        field_path: tuple[str, ...] | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> str:
        if field_path is None:
            return self._display_readable_decl(decl)

        if isinstance(decl, model.Agent):
            if field_path == ("name",):
                return decl.name
            field_name = ".".join(field_path)
            raise CompileError(
                f"Unknown interpolation field on {surface_label} in {owner_label}: "
                f"{ref_label}:{field_name}"
            )

        if field_path == ("title",):
            return decl.title

        field_name = ".".join(field_path)
        return self._resolve_record_items_interpolation_field(
            decl.items,
            field_path,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
            decl=decl,
            full_field_name=field_name,
        )

    def _resolve_record_items_interpolation_field(
        self,
        items: tuple[model.RecordItem, ...],
        field_path: tuple[str, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        decl: ReadableDecl,
        full_field_name: str,
    ) -> str:
        first = field_path[0]
        record_scalar: model.RecordScalar | None = None
        conflicting_item: model.RecordItem | None = None

        for item in items:
            if isinstance(item, model.RecordScalar) and item.key == first:
                record_scalar = item
                break
            if isinstance(item, model.RecordSection) and item.key == first:
                conflicting_item = item
                break

        if record_scalar is None:
            if conflicting_item is not None:
                raise CompileError(
                    "Interpolation field must resolve to a scalar on "
                    f"{surface_label} in {owner_label}: {ref_label}:{full_field_name}"
                )
            raise CompileError(
                f"Unknown interpolation field on {surface_label} in {owner_label}: "
                f"{ref_label}:{full_field_name}"
            )

        return self._resolve_record_scalar_interpolation_field(
            record_scalar,
            field_path[1:],
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
            decl=decl,
            full_field_name=full_field_name,
        )

    def _resolve_record_scalar_interpolation_field(
        self,
        item: model.RecordScalar,
        field_path: tuple[str, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        decl: ReadableDecl,
        full_field_name: str,
    ) -> str:
        if not field_path:
            if item.body is not None:
                raise CompileError(
                    "Interpolation field must resolve to a scalar on "
                    f"{surface_label} in {owner_label}: {ref_label}:{full_field_name}"
                )
            return self._display_interpolation_scalar(
                item,
                unit=unit,
                decl=decl,
            )

        if field_path == ("title",):
            return self._display_interpolation_head_title(
                item,
                unit=unit,
                decl=decl,
            )

        if item.body is None:
            raise CompileError(
                f"Unknown interpolation field on {surface_label} in {owner_label}: "
                f"{ref_label}:{full_field_name}"
            )

        nested_key = field_path[0]
        nested_scalar: model.RecordScalar | None = None
        conflicting_item: model.RecordItem | None = None
        for nested_item in item.body:
            if isinstance(nested_item, model.RecordScalar) and nested_item.key == nested_key:
                nested_scalar = nested_item
                break
            if isinstance(nested_item, model.RecordSection) and nested_item.key == nested_key:
                conflicting_item = nested_item
                break

        if nested_scalar is None:
            if conflicting_item is not None:
                raise CompileError(
                    "Interpolation field must resolve to a scalar on "
                    f"{surface_label} in {owner_label}: {ref_label}:{full_field_name}"
                )
            raise CompileError(
                f"Unknown interpolation field on {surface_label} in {owner_label}: "
                f"{ref_label}:{full_field_name}"
            )

        if len(field_path) > 1:
            if field_path[1:] == ("title",):
                return self._display_interpolation_scalar(
                    nested_scalar,
                    unit=unit,
                    decl=decl,
                )
            raise CompileError(
                f"Unknown interpolation field on {surface_label} in {owner_label}: "
                f"{ref_label}:{full_field_name}"
            )

        if nested_scalar.body is not None:
            raise CompileError(
                "Interpolation field must resolve to a scalar on "
                f"{surface_label} in {owner_label}: {ref_label}:{full_field_name}"
            )

        return self._display_interpolation_scalar(
            nested_scalar,
            unit=unit,
            decl=decl,
        )

    def _display_interpolation_scalar(
        self,
        item: model.RecordScalar,
        *,
        unit: IndexedUnit,
        decl: ReadableDecl,
    ) -> str:
        if item.body is not None:
            return self._display_interpolation_head_title(item, unit=unit, decl=decl)
        return self._display_symbol_value(item.value, unit=unit)

    def _display_interpolation_head_title(
        self,
        item: model.RecordScalar,
        *,
        unit: IndexedUnit,
        decl: ReadableDecl,
    ) -> str:
        if isinstance(decl, model.InputDecl) and item.key == "source":
            if not isinstance(item.value, model.NameRef):
                raise CompileError(f"Input source must stay typed in interpolation: {decl.name}")
            return self._resolve_input_source_spec(item.value, unit=unit).title

        if isinstance(decl, model.OutputDecl) and item.key == "target":
            if not isinstance(item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed in interpolation: {decl.name}")
            return self._resolve_output_target_spec(item.value, unit=unit).title

        if isinstance(decl, model.OutputDecl) and item.key == "shape":
            return self._display_output_shape(item.value, unit=unit)

        return self._display_symbol_value(item.value, unit=unit)

    def _resolve_readable_decl_lookup_unit(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> IndexedUnit:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            return unit

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")
        return target_unit

    def _find_readable_decl_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ReadableDecl], ...]:
        matches: list[tuple[str, ReadableDecl]] = []
        for label, registry_name in _WORKFLOW_MENTION_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _display_readable_decl(self, decl: ReadableDecl) -> str:
        if isinstance(decl, model.Agent):
            return decl.name
        return decl.title

    def _validate_route_target(self, ref: model.NameRef, *, unit: IndexedUnit) -> None:
        _target_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        if agent.abstract:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Route target must be a concrete agent: {dotted_name}")

    def _compile_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> CompiledSection:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if workflow_key in self._workflow_compile_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_compile_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow composition: {cycle}")

        self._workflow_compile_stack.append(workflow_key)
        try:
            return self._compile_resolved_workflow(
                self._resolve_workflow_decl(workflow_decl, unit=unit)
            )
        finally:
            self._workflow_compile_stack.pop()

    def _compile_resolved_workflow(self, workflow_body: ResolvedWorkflowBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(workflow_body.preamble)
        for item in workflow_body.items:
            if isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(item.items),
                    )
                )
                continue

            if isinstance(item, ResolvedWorkflowSkillsItem):
                body.append(self._compile_resolved_skills(item.body))
                continue

            body.append(
                self._compile_workflow_decl(item.workflow_decl, unit=item.target_unit)
            )

        return CompiledSection(title=workflow_body.title, body=tuple(body))

    def _compile_section_body(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
    ) -> tuple[model.ProseLine, ...]:
        body: list[model.ProseLine] = []
        previous_kind: str | None = None

        for item in items:
            current_kind = "ref" if isinstance(item, ResolvedSectionRef) else "prose"
            if previous_kind is not None and current_kind != previous_kind and body:
                if body[-1] != "":
                    body.append("")

            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
            elif isinstance(item, ResolvedRouteLine):
                body.append(f"{item.label} -> {item.target_name}")
            else:
                body.append(f"- {item.label}")

            previous_kind = current_kind

        return tuple(body)

    def _split_record_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        scalar_keys: set[str] | None = None,
        section_keys: set[str] | None = None,
        owner_label: str,
    ) -> tuple[dict[str, model.RecordScalar], dict[str, model.RecordSection], tuple[model.RecordItem, ...]]:
        scalar_keys = scalar_keys or set()
        section_keys = section_keys or set()
        scalar_items: dict[str, model.RecordScalar] = {}
        section_items: dict[str, model.RecordSection] = {}
        extras: list[model.RecordItem] = []

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

    def _resolve_workflow_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="workflows_by_name",
            missing_label="workflow declaration",
        )

    def _resolve_skills_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_blocks_by_name",
            missing_label="skills declaration",
        )

    def _resolve_inputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
            missing_label="inputs block",
        )

    def _resolve_outputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_blocks_by_name",
            missing_label="outputs block",
        )

    def _resolve_parent_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        parent_ref = workflow_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: workflow has no parent ref: {workflow_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.workflows_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent workflow for {workflow_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_workflow_ref(parent_ref, unit=unit)

    def _resolve_parent_skills_decl(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        parent_ref = skills_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: skills has no parent ref: {skills_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.skills_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent skills for {skills_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_skills_ref(parent_ref, unit=unit)

    def _resolve_parent_inputs_decl(
        self,
        inputs_decl: model.InputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        parent_ref = inputs_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: inputs block has no parent ref: {inputs_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.inputs_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent inputs block for {inputs_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_inputs_block_ref(parent_ref, unit=unit)

    def _resolve_parent_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        parent_ref = outputs_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: outputs block has no parent ref: {outputs_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.outputs_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent outputs block for {outputs_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_outputs_block_ref(parent_ref, unit=unit)

    def _resolve_input_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_by_name",
            missing_label="input declaration",
        )

    def _resolve_input_source_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputSourceDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="input_sources_by_name",
            missing_label="input source declaration",
        )

    def _resolve_output_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_by_name",
            missing_label="output declaration",
        )

    def _resolve_output_target_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputTargetDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_targets_by_name",
            missing_label="output target declaration",
        )

    def _resolve_output_shape_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputShapeDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_shapes_by_name",
            missing_label="output shape declaration",
        )

    def _resolve_skill_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_by_name",
            missing_label="skill declaration",
        )

    def _resolve_agent_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.Agent]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="agents_by_name",
            missing_label="agent declaration",
        )

    def _resolve_parent_agent_decl(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.Agent]:
        parent_ref = agent.parent_ref
        if parent_ref is None:
            raise CompileError(f"Internal compiler error: agent has no parent ref: {agent.name}")
        if not parent_ref.module_parts:
            parent_agent = unit.agents_by_name.get(parent_ref.declaration_name)
            if parent_agent is None:
                raise CompileError(
                    f"Missing parent agent for {agent.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_agent
        return self._resolve_agent_ref(parent_ref, unit=unit)

    def _resolve_decl_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
        missing_label: str,
    ):
        if not ref.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                raise CompileError(f"Missing local {missing_label}: {ref.declaration_name}")
            return unit, decl

        if ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                dotted_name = _dotted_ref_name(ref)
                raise CompileError(f"Missing imported declaration: {dotted_name}")
            return unit, decl

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")

        registry = getattr(target_unit, registry_name)
        decl = registry.get(ref.declaration_name)
        if decl is None:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Missing imported declaration: {dotted_name}")
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

    def _index_unit(
        self, prompt_file: model.PromptFile, *, module_parts: tuple[str, ...]
    ) -> IndexedUnit:
        imports: list[model.ImportDecl] = []
        workflows_by_name: dict[str, model.WorkflowDecl] = {}
        skills_blocks_by_name: dict[str, model.SkillsDecl] = {}
        inputs_blocks_by_name: dict[str, model.InputsDecl] = {}
        inputs_by_name: dict[str, model.InputDecl] = {}
        input_sources_by_name: dict[str, model.InputSourceDecl] = {}
        outputs_blocks_by_name: dict[str, model.OutputsDecl] = {}
        outputs_by_name: dict[str, model.OutputDecl] = {}
        output_targets_by_name: dict[str, model.OutputTargetDecl] = {}
        output_shapes_by_name: dict[str, model.OutputShapeDecl] = {}
        json_schemas_by_name: dict[str, model.JsonSchemaDecl] = {}
        skills_by_name: dict[str, model.SkillDecl] = {}
        agents_by_name: dict[str, model.Agent] = {}

        for declaration in prompt_file.declarations:
            if isinstance(declaration, model.ImportDecl):
                imports.append(declaration)
                continue
            if isinstance(declaration, model.WorkflowDecl):
                self._register_decl(workflows_by_name, declaration.name, module_parts)
                workflows_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.SkillsDecl):
                self._register_decl(skills_blocks_by_name, declaration.name, module_parts)
                skills_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputsDecl):
                self._register_decl(inputs_blocks_by_name, declaration.name, module_parts)
                inputs_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputDecl):
                self._register_decl(inputs_by_name, declaration.name, module_parts)
                inputs_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputSourceDecl):
                self._register_decl(input_sources_by_name, declaration.name, module_parts)
                input_sources_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputsDecl):
                self._register_decl(outputs_blocks_by_name, declaration.name, module_parts)
                outputs_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputDecl):
                self._register_decl(outputs_by_name, declaration.name, module_parts)
                outputs_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputTargetDecl):
                self._register_decl(output_targets_by_name, declaration.name, module_parts)
                output_targets_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputShapeDecl):
                self._register_decl(output_shapes_by_name, declaration.name, module_parts)
                output_shapes_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.JsonSchemaDecl):
                self._register_decl(json_schemas_by_name, declaration.name, module_parts)
                json_schemas_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.SkillDecl):
                self._register_decl(skills_by_name, declaration.name, module_parts)
                skills_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.Agent):
                self._register_decl(agents_by_name, declaration.name, module_parts)
                agents_by_name[declaration.name] = declaration
                continue
            raise CompileError(f"Unsupported declaration type: {type(declaration).__name__}")

        imported_units: dict[tuple[str, ...], IndexedUnit] = {}
        for import_decl in imports:
            resolved_module_parts = _resolve_import_path(import_decl.path, module_parts=module_parts)
            try:
                imported_units[resolved_module_parts] = self._load_module(resolved_module_parts)
            except DoctrineError as exc:
                importer_path = prompt_file.source_path
                raise exc.prepend_trace(
                    f"resolve import `{'.'.join(resolved_module_parts)}`",
                    location=_path_location(importer_path),
                )

        return IndexedUnit(
            module_parts=module_parts,
            prompt_file=prompt_file,
            imports=tuple(imports),
            workflows_by_name=workflows_by_name,
            inputs_blocks_by_name=inputs_blocks_by_name,
            inputs_by_name=inputs_by_name,
            input_sources_by_name=input_sources_by_name,
            outputs_blocks_by_name=outputs_blocks_by_name,
            outputs_by_name=outputs_by_name,
            output_targets_by_name=output_targets_by_name,
            output_shapes_by_name=output_shapes_by_name,
            json_schemas_by_name=json_schemas_by_name,
            skills_by_name=skills_by_name,
            skills_blocks_by_name=skills_blocks_by_name,
            agents_by_name=agents_by_name,
            imported_units=imported_units,
        )

    def _register_decl(
        self,
        registry: dict[str, object],
        name: str,
        module_parts: tuple[str, ...],
    ) -> None:
        if name in registry:
            dotted_name = ".".join((*module_parts, name)) or name
            raise CompileError(f"Duplicate declaration name: {dotted_name}")

    def _load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        cached = self._module_cache.get(module_parts)
        if cached is not None:
            return cached

        if module_parts in self._loading_modules:
            raise CompileError(f"Cyclic import module: {'.'.join(module_parts)}")

        module_path = self.prompt_root.joinpath(*module_parts).with_suffix(".prompt")
        if not module_path.is_file():
            raise CompileError(f"Missing import module: {'.'.join(module_parts)}")

        self._loading_modules.add(module_parts)
        try:
            try:
                prompt_file = parse_file(module_path)
                indexed = self._index_unit(prompt_file, module_parts=module_parts)
            except DoctrineError as exc:
                raise exc.prepend_trace(
                    f"load import module `{'.'.join(module_parts)}`",
                    location=_path_location(module_path),
                ).ensure_location(path=module_path)
            self._module_cache[module_parts] = indexed
            return indexed
        finally:
            self._loading_modules.remove(module_parts)


def compile_prompt(prompt_file: model.PromptFile, agent_name: str) -> CompiledAgent:
    try:
        return CompilationContext(prompt_file).compile_agent(agent_name)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"compile agent `{agent_name}`",
            location=_path_location(prompt_file.source_path),
        ).ensure_location(path=prompt_file.source_path)


def _resolve_prompt_root(source_path: Path | None) -> Path:
    if source_path is None:
        raise CompileError("Prompt source path is required for compilation.")

    resolved = source_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            return candidate

    raise CompileError(f"Could not resolve prompts/ root for {resolved}.")


def _resolve_import_path(
    import_path: model.ImportPath, *, module_parts: tuple[str, ...]
) -> tuple[str, ...]:
    if import_path.level == 0:
        return import_path.module_parts

    current_package_parts = module_parts[:-1] if module_parts else ()
    parent_walk = import_path.level - 1
    package_parts = (
        current_package_parts[:-parent_walk] if parent_walk else current_package_parts
    )
    if parent_walk > len(current_package_parts):
        dotted_import = "." * import_path.level + ".".join(import_path.module_parts)
        raise CompileError(f"Relative import walks above prompts root: {dotted_import}")

    return (*package_parts, *import_path.module_parts)


def _dotted_decl_name(module_parts: tuple[str, ...], name: str) -> str:
    return ".".join((*module_parts, name)) if module_parts else name


def _dotted_ref_name(ref: model.NameRef) -> str:
    return ".".join((*ref.module_parts, ref.declaration_name))


def _name_ref_from_dotted_name(dotted_name: str) -> model.NameRef:
    parts = tuple(dotted_name.split("."))
    return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])


def _path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())


def _humanize_key(value: str) -> str:
    value = value.replace("_", " ")
    value = _CAMEL_BOUNDARY_RE.sub(" ", value)
    words = value.split()
    return " ".join(word if word.isupper() else word.capitalize() for word in words)


def _value_to_symbol(value: model.RecordScalarValue) -> str:
    if isinstance(value, str):
        return value
    return value.declaration_name
