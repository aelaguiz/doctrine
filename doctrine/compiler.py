from __future__ import annotations

import re
from dataclasses import dataclass, replace
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
    | model.EnumDecl
)
AddressableRootDecl: TypeAlias = ReadableDecl | model.WorkflowDecl | model.SkillsDecl
AddressableTarget: TypeAlias = (
    AddressableRootDecl
    | model.RecordScalar
    | model.RecordSection
    | model.GuardedOutputSection
    | model.EnumMember
    | "ResolvedSectionItem"
    | "ResolvedUseItem"
    | "ResolvedWorkflowSkillsItem"
    | "ResolvedSkillsSection"
    | "ResolvedSkillEntry"
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
    enums_by_name: dict[str, model.EnumDecl]
    agents_by_name: dict[str, model.Agent]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]


@dataclass(slots=True, frozen=True)
class ResolvedRouteLine:
    label: str
    target_name: str


@dataclass(slots=True, frozen=True)
class ResolvedSectionRef:
    label: str


ResolvedSectionBodyItem: TypeAlias = (
    model.ProseLine | ResolvedRouteLine | ResolvedSectionRef | "ResolvedSectionItem"
)


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
    law: model.LawBody | None = None


@dataclass(slots=True, frozen=True)
class AgentContract:
    inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]]
    outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]]


@dataclass(slots=True, frozen=True)
class LawBranch:
    activation_exprs: tuple[model.Expr, ...] = ()
    mode_bindings: tuple[model.ModeStmt, ...] = ()
    current_subjects: tuple[model.CurrentArtifactStmt | model.CurrentNoneStmt, ...] = ()
    musts: tuple[model.MustStmt, ...] = ()
    owns: tuple[model.OwnOnlyStmt, ...] = ()
    preserves: tuple[model.PreserveStmt, ...] = ()
    supports: tuple[model.SupportOnlyStmt, ...] = ()
    ignores: tuple[model.IgnoreStmt, ...] = ()
    forbids: tuple[model.ForbidStmt, ...] = ()
    invalidations: tuple[model.InvalidateStmt, ...] = ()
    stops: tuple[model.StopStmt, ...] = ()
    routes: tuple[model.LawRouteStmt, ...] = ()


@dataclass(slots=True, frozen=True)
class ResolvedLawPath:
    unit: IndexedUnit
    decl: model.InputDecl | model.OutputDecl | model.EnumDecl
    remainder: tuple[str, ...]
    wildcard: bool = False


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


@dataclass(slots=True, frozen=True)
class DisplayValue:
    text: str
    kind: str


@dataclass(slots=True, frozen=True)
class AddressableNode:
    unit: IndexedUnit
    root_decl: AddressableRootDecl
    target: AddressableTarget


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

_READABLE_DECL_REGISTRIES = (
    ("agent declaration", "agents_by_name"),
    ("input declaration", "inputs_by_name"),
    ("input source declaration", "input_sources_by_name"),
    ("output declaration", "outputs_by_name"),
    ("output target declaration", "output_targets_by_name"),
    ("output shape declaration", "output_shapes_by_name"),
    ("json schema declaration", "json_schemas_by_name"),
    ("skill declaration", "skills_by_name"),
    ("enum declaration", "enums_by_name"),
)

_ADDRESSABLE_ROOT_REGISTRIES = (
    *_READABLE_DECL_REGISTRIES,
    ("workflow declaration", "workflows_by_name"),
    ("skills block", "skills_blocks_by_name"),
)


class CompilationContext:
    def __init__(self, prompt_file: model.PromptFile):
        self.prompt_root = _resolve_prompt_root(prompt_file.source_path)
        self._module_cache: dict[tuple[str, ...], IndexedUnit] = {}
        self._loading_modules: set[tuple[str, ...]] = set()
        self._workflow_compile_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._inputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._outputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._agent_slot_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._resolved_workflow_cache: dict[tuple[tuple[str, ...], str], ResolvedWorkflowBody] = {}
        self._addressable_workflow_cache: dict[
            tuple[tuple[str, ...], str], ResolvedWorkflowBody
        ] = {}
        self._resolved_skills_cache: dict[tuple[tuple[str, ...], str], ResolvedSkillsBody] = {}
        self._addressable_skills_cache: dict[
            tuple[tuple[str, ...], str], ResolvedSkillsBody
        ] = {}
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
        agent_contract = self._resolve_agent_contract(agent, unit=unit)
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
                if field.key == "workflow":
                    compiled_fields.append(
                        self._compile_resolved_workflow(
                            slot_body,
                            unit=unit,
                            agent_contract=agent_contract,
                            owner_label=f"agent {agent.name} workflow",
                        )
                    )
                else:
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

    def _resolve_agent_contract(self, agent: model.Agent, *, unit: IndexedUnit) -> AgentContract:
        inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]] = {}
        outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]] = {}

        for field in agent.fields:
            if isinstance(field, model.InputsField):
                self._collect_input_decls_from_io_value(field.value, unit=unit, sink=inputs)
            elif isinstance(field, model.OutputsField):
                self._collect_output_decls_from_io_value(field.value, unit=unit, sink=outputs)

        return AgentContract(inputs=inputs, outputs=outputs)

    def _collect_input_decls_from_io_value(
        self,
        value: model.IoFieldValue,
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]],
    ) -> None:
        if isinstance(value, tuple):
            self._collect_input_decls_from_record_items(value, unit=unit, sink=sink)
            return
        if isinstance(value, model.IoBody):
            self._collect_input_decls_from_io_items(value.items, unit=unit, sink=sink)
            return
        if self._ref_exists_in_registry(
            value,
            unit=unit,
            registry_name="outputs_blocks_by_name",
        ):
            raise CompileError(
                "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                f"{_dotted_ref_name(value)}"
            )
        target_unit, decl = self._resolve_inputs_block_ref(value, unit=unit)
        self._collect_input_decls_from_io_items(decl.body.items, unit=target_unit, sink=sink)

    def _collect_output_decls_from_io_value(
        self,
        value: model.IoFieldValue,
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]],
    ) -> None:
        if isinstance(value, tuple):
            self._collect_output_decls_from_record_items(value, unit=unit, sink=sink)
            return
        if isinstance(value, model.IoBody):
            self._collect_output_decls_from_io_items(value.items, unit=unit, sink=sink)
            return
        if self._ref_exists_in_registry(
            value,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(value)}"
            )
        target_unit, decl = self._resolve_outputs_block_ref(value, unit=unit)
        self._collect_output_decls_from_io_items(decl.body.items, unit=target_unit, sink=sink)

    def _collect_input_decls_from_io_items(
        self,
        items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_input_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="outputs_by_name",
                ):
                    raise CompileError(
                        "Inputs refs must resolve to input declarations, not output declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)
            elif isinstance(item, model.OverrideIoSection):
                self._collect_input_decls_from_record_items(item.items, unit=unit, sink=sink)

    def _collect_output_decls_from_io_items(
        self,
        items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_output_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="inputs_by_name",
                ):
                    raise CompileError(
                        "Outputs refs must resolve to output declarations, not input declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)
            elif isinstance(item, model.OverrideIoSection):
                self._collect_output_decls_from_record_items(item.items, unit=unit, sink=sink)

    def _collect_input_decls_from_record_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_input_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="outputs_by_name",
                ):
                    raise CompileError(
                        "Inputs refs must resolve to input declarations, not output declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)

    def _collect_output_decls_from_record_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_output_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="inputs_by_name",
                ):
                    raise CompileError(
                        "Outputs refs must resolve to output declarations, not input declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)

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
        if (
            requirement is not None
            and self._value_to_symbol(
                requirement.value,
                unit=entry.metadata_unit,
                owner_label=f"skill reference {skill_decl.name}",
                surface_label="skill reference metadata",
            )
            == "Required"
        ):
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
        if source_item is None:
            raise CompileError(f"Input is missing typed source: {decl.name}")
        if not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input source must stay typed: {decl.name}")
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
        body.append(
            f"- Shape: {self._display_symbol_value(shape_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        body.append(
            f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
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
        self._validate_output_guard_sections(decl, unit=unit)
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
                raise CompileError(f"Output target must stay typed: {decl.name}")
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
            body.append(
                f"- Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=decl.name, surface_label='output fields')}"
            )

        if requirement_item is not None:
            body.append(
                f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'output {decl.name}', surface_label='output fields')}"
            )

        trust_surface_section = (
            self._compile_trust_surface_section(decl, unit=unit)
            if decl.trust_surface
            else None
        )

        if extras:
            support_items: list[CompiledBodyItem] = []
            rendered_trust_surface = False
            for item in extras:
                if (
                    trust_surface_section is not None
                    and not rendered_trust_surface
                    and isinstance(item, model.RecordSection)
                    and item.key == "standalone_read"
                ):
                    support_items.append(trust_surface_section)
                    rendered_trust_surface = True
                support_items.extend(
                    self._compile_record_item(
                        item,
                        unit=unit,
                        owner_label=f"output {decl.name}",
                        surface_label="output prose",
                    )
                )
            if trust_surface_section is not None and not rendered_trust_surface:
                support_items.append(trust_surface_section)
            body.append("")
            body.extend(support_items)
        elif trust_surface_section is not None:
            body.append("")
            body.append(trust_surface_section)

        return CompiledSection(title=decl.title, body=tuple(body))

    def _validate_output_guard_sections(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        self._validate_output_record_items(
            decl.items,
            decl=decl,
            unit=unit,
            owner_label=f"output {decl.name}",
        )

    def _validate_output_record_items(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        for item in items:
            if isinstance(item, model.GuardedOutputSection):
                self._validate_output_guard_expr(
                    item.when_expr,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                )
                self._validate_output_record_items(
                    item.items,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                )
                continue
            if isinstance(item, model.RecordSection):
                self._validate_output_record_items(
                    item.items,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                )
                continue
            if isinstance(item, model.RecordScalar) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                )
                continue
            if isinstance(item, model.RecordRef) and item.body is not None:
                self._validate_output_record_items(
                    item.body,
                    decl=decl,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                )

    def _validate_output_guard_expr(
        self,
        expr: model.Expr,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if isinstance(expr, model.ExprRef):
            self._validate_output_guard_ref(
                expr,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
            )
            return
        if isinstance(expr, model.ExprBinary):
            self._validate_output_guard_expr(
                expr.left,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
            )
            self._validate_output_guard_expr(
                expr.right,
                decl=decl,
                unit=unit,
                owner_label=owner_label,
            )
            return
        if isinstance(expr, model.ExprCall):
            for arg in expr.args:
                self._validate_output_guard_expr(
                    arg,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                )
            return
        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._validate_output_guard_expr(
                    item,
                    decl=decl,
                    unit=unit,
                    owner_label=owner_label,
                )

    def _validate_output_guard_ref(
        self,
        ref: model.ExprRef,
        *,
        decl: model.OutputDecl,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if self._output_guard_ref_allowed(ref, unit=unit):
            return
        raise CompileError(
            f"Output guard reads disallowed source in {owner_label}: {'.'.join(ref.parts)}"
        )

    def _output_guard_ref_allowed(
        self,
        ref: model.ExprRef,
        *,
        unit: IndexedUnit,
    ) -> bool:
        return self._expr_ref_matches_input_decl(ref, unit=unit) or self._expr_ref_matches_enum_member(
            ref,
            unit=unit,
        )

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

    def _compile_trust_surface_section(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        lines: list[CompiledBodyItem] = []
        for item in decl.trust_surface:
            field_node = self._resolve_output_field_node(
                decl,
                path=item.path,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
            )
            label = self._display_addressable_target_value(
                field_node,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
            ).text
            if item.when_expr is not None:
                label = self._render_trust_surface_label(
                    label,
                    item.when_expr,
                    unit=unit,
                )
            lines.append(f"- {label}")
        return CompiledSection(title="Trust Surface", body=tuple(lines))

    def _render_trust_surface_label(
        self,
        label: str,
        when_expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str:
        if (
            isinstance(when_expr, model.ExprBinary)
            and when_expr.op == "=="
            and self._resolve_constant_enum_member(when_expr.right, unit=unit) == "rewrite"
        ):
            return f"{label} on rewrite passes"

        condition = self._render_condition_expr(when_expr, unit=unit)
        if condition.startswith("peer comparison"):
            return f"{label} when peer comparison is used"
        return f"{label} when {condition}"

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
                f"- {item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {output_name} file {item.key}', surface_label='output file fields')}"
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
        items: tuple[model.AnyRecordItem, ...],
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
        item: model.AnyRecordItem,
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

        if isinstance(item, model.GuardedOutputSection):
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            body: list[CompiledBodyItem] = [f"Rendered only when {condition}."]
            compiled_items = self._compile_record_support_items(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
            )
            if compiled_items:
                body.append("")
                body.extend(compiled_items)
            return (CompiledSection(title=item.title, body=tuple(body)),)

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
        value = self._format_scalar_value(
            item.value,
            unit=unit,
            owner_label=f"{owner_label}.{item.key}",
            surface_label=surface_label,
        )
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
                f"- {allowed_keys[item.key]}: {self._format_scalar_value(item.value, unit=unit, owner_label=f'{owner_label}.{item.key}', surface_label='config values')}"
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

    def _display_symbol_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        return self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        ).text

    def _format_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
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
    ) -> DisplayValue:
        if isinstance(value, str):
            return DisplayValue(text=value, kind="string_literal")
        if isinstance(value, model.NameRef):
            enum_decl = self._try_resolve_enum_decl(value, unit=unit)
            if enum_decl is not None:
                return DisplayValue(text=enum_decl.title, kind="title")
            return DisplayValue(text=self._display_ref(value), kind="symbol")
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

    def _display_ref(self, ref: model.NameRef) -> str:
        if ref.module_parts:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return _humanize_key(ref.declaration_name)

    def _try_resolve_enum_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> model.EnumDecl | None:
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        return lookup_unit.enums_by_name.get(ref.declaration_name)

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

    def _resolve_workflow_for_addressable_paths(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if (
            workflow_key in self._workflow_resolution_stack
            or workflow_key in self._workflow_addressable_resolution_stack
        ):
            return self._resolve_workflow_addressable_decl(workflow_decl, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=unit)

    def _resolve_skills_for_addressable_paths(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        if (
            skills_key in self._skills_resolution_stack
            or skills_key in self._skills_addressable_resolution_stack
        ):
            return self._resolve_skills_addressable_decl(skills_decl, unit=unit)
        return self._resolve_skills_decl(skills_decl, unit=unit)

    def _resolve_workflow_addressable_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._addressable_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._workflow_addressable_resolution_stack,
                    workflow_key,
                ]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_addressable_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_addressable_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._addressable_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_addressable_resolution_stack.pop()

    def _resolve_skills_addressable_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._addressable_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._skills_addressable_resolution_stack,
                    skills_key,
                ]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_addressable_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_addressable_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._addressable_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_addressable_resolution_stack.pop()

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

    def _resolve_skills_value_for_addressable_paths(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_for_addressable_paths(skills_decl, unit=target_unit)
        return self._resolve_skills_addressable_body(
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
                law=self._resolve_law_body(
                    workflow_body.law,
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
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_law_body(
        self,
        law_body: model.LawBody | None,
        *,
        owner_label: str,
        parent_law: model.LawBody | None = None,
        parent_label: str | None = None,
    ) -> model.LawBody | None:
        if law_body is None:
            return parent_law
        if parent_law is None:
            return law_body

        parent_items = parent_law.items
        parent_has_sections = all(
            isinstance(item, model.LawSection) for item in parent_items
        )
        child_has_named_items = all(
            isinstance(
                item,
                (model.LawSection, model.LawInherit, model.LawOverrideSection),
            )
            for item in law_body.items
        )

        if not parent_has_sections or not child_has_named_items:
            raise CompileError(
                f"Inherited law blocks must use named sections only in {owner_label}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_items if isinstance(item, model.LawSection)
        }
        resolved_items: list[model.LawTopLevelItem] = []
        accounted_keys: set[str] = set()

        for item in law_body.items:
            if isinstance(item, model.LawSection):
                if item.key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                    )
                resolved_items.append(item)
                continue

            parent_item = parent_items_by_key.get(item.key)
            if parent_item is None:
                raise CompileError(
                    f"Cannot override undefined law section in {parent_label}: {item.key}"
                )
            if item.key in accounted_keys:
                raise CompileError(
                    f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                )
            accounted_keys.add(item.key)

            if isinstance(item, model.LawInherit):
                resolved_items.append(parent_item)
            else:
                resolved_items.append(model.LawSection(key=item.key, items=item.items))

        missing_keys = sorted(set(parent_items_by_key) - accounted_keys)
        if missing_keys:
            raise CompileError(
                f"Inherited law block omits parent subsection(s) in {owner_label}: {', '.join(missing_keys)}"
            )

        return model.LawBody(items=tuple(resolved_items))

    def _resolve_skills_addressable_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_skills_items(
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
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
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
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(self._resolve_skill_entry(item, unit=unit))

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
            preamble=(),
            items=tuple(resolved_items),
        )

    def _resolve_workflow_addressable_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_workflow_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
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
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
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
                        body=self._resolve_skills_value_for_addressable_paths(
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
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
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
                        body=self._resolve_skills_value_for_addressable_paths(
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
            preamble=(),
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
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

    def _resolve_non_inherited_addressable_workflow_items(
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
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
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
                        body=self._resolve_skills_value_for_addressable_paths(
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

    def _resolve_non_inherited_addressable_skills_items(
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
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
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

    def _resolve_addressable_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
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
            if isinstance(item, model.LocalSection):
                resolved.append(
                    ResolvedSectionItem(
                        key=item.key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
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

    def _resolve_addressable_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if not isinstance(item, model.LocalSection):
                continue
            resolved.append(
                ResolvedSectionItem(
                    key=item.key,
                    title=item.title,
                    items=self._resolve_addressable_section_body_items(
                        item.items,
                        unit=unit,
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_section_body_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSectionRef:
        value = self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label="workflow section bodies",
            ambiguous_label="workflow section declaration ref",
            missing_local_label="workflow section body",
        )
        return ResolvedSectionRef(label=value.text)

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

        ref = model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )
        return self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=ambiguous_label or f"{surface_label} interpolation ref",
            missing_local_label=surface_label,
        ).text

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

    def _resolve_addressable_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
    ) -> DisplayValue:
        ref_label = _display_addressable_ref(ref)
        if not ref.path:
            target_unit, decl = self._resolve_readable_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                missing_local_label=missing_local_label,
            )
            return self._display_addressable_target_value(
                AddressableNode(unit=target_unit, root_decl=decl, target=decl),
                owner_label=owner_label,
                surface_label=surface_label,
            )

        target_unit, decl = self._resolve_addressable_root_decl(
            ref.root,
            unit=unit,
            owner_label=owner_label,
            ambiguous_label=ambiguous_label,
            missing_local_label=missing_local_label,
        )
        return self._resolve_addressable_path_value(
            AddressableNode(unit=target_unit, root_decl=decl, target=decl),
            ref.path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

    def _resolve_addressable_root_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        ambiguous_label: str,
        missing_local_label: str,
    ) -> tuple[IndexedUnit, AddressableRootDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_addressable_root_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    "Abstract agent refs are not allowed in addressable paths; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_path_value(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> DisplayValue:
        current = self._resolve_addressable_path_node(
            start,
            path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

        return self._display_addressable_target_value(
            current,
            owner_label=owner_label,
            surface_label=surface_label,
        )

    def _resolve_addressable_path_node(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> AddressableNode:
        current = start

        for index, segment in enumerate(path):
            is_last = index == len(path) - 1
            if is_last and isinstance(current.target, model.Agent) and segment == "name":
                return AddressableNode(
                    unit=current.unit,
                    root_decl=current.root_decl,
                    target=current.target,
                )
            if is_last and segment == "title":
                title = self._display_addressable_title(
                    current,
                    owner_label=owner_label,
                    surface_label=surface_label,
                )
                if title is not None:
                    return current
            if is_last and segment in {"name", "title"}:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )

            children = self._get_addressable_children(current)
            if children is None:
                raise CompileError(
                    "Addressable path must stay addressable on "
                    f"{surface_label} in {owner_label}: {ref_label}"
                )
            next_node = children.get(segment)
            if next_node is None:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )
            current = next_node

        return current

    def _get_addressable_children(
        self,
        node: AddressableNode,
    ) -> dict[str, AddressableNode] | None:
        target = node.target
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
            return self._record_items_to_addressable_children(
                target.items,
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
            if isinstance(item, (model.RecordScalar, model.RecordSection, model.GuardedOutputSection)):
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

    def _display_addressable_target_value(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
    ) -> DisplayValue:
        target = node.target
        if isinstance(target, model.Agent):
            return DisplayValue(text=target.name, kind="symbol")
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
        if isinstance(target, model.RecordScalar):
            if target.body is not None:
                return DisplayValue(
                    text=self._display_record_scalar_title(
                        target,
                        node=node,
                        owner_label=owner_label,
                        surface_label=surface_label,
                    ),
                    kind="title",
                )
            return self._display_scalar_value(
                target.value,
                unit=node.unit,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        if isinstance(target, model.EnumMember):
            return DisplayValue(text=target.value, kind="symbol")
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
        raise CompileError(
            f"Internal compiler error: unsupported addressable target {type(target).__name__}"
        )

    def _display_addressable_title(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
    ) -> str | None:
        target = node.target
        if isinstance(target, model.Agent):
            return None
        if isinstance(target, model.RecordScalar):
            return self._display_record_scalar_title(
                target,
                node=node,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        return self._display_addressable_target_value(
            node,
            owner_label=owner_label,
            surface_label=surface_label,
        ).text

    def _display_record_scalar_title(
        self,
        item: model.RecordScalar,
        *,
        node: AddressableNode,
        owner_label: str,
        surface_label: str,
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
        )

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
        for label, registry_name in _READABLE_DECL_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _find_addressable_root_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, AddressableRootDecl], ...]:
        matches: list[tuple[str, AddressableRootDecl]] = []
        for label, registry_name in _ADDRESSABLE_ROOT_REGISTRIES:
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
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
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
                self._resolve_workflow_decl(workflow_decl, unit=unit),
                unit=unit,
                agent_contract=agent_contract,
                owner_label=f"workflow {_dotted_decl_name(unit.module_parts, workflow_decl.name)}",
            )
        finally:
            self._workflow_compile_stack.pop()

    def _compile_resolved_workflow(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str | None = None,
    ) -> CompiledSection:
        body: list[CompiledBodyItem] = list(workflow_body.preamble)
        if workflow_body.law is not None:
            if unit is None or agent_contract is None or owner_label is None:
                raise CompileError(
                    "Internal compiler error: workflow law requires unit, agent contract, and owner label"
                )
            if body and body[-1] != "":
                body.append("")
            body.extend(
                self._compile_workflow_law(
                    workflow_body.law,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
            )
        for item in workflow_body.items:
            if body and body[-1] != "":
                body.append("")
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
                self._compile_workflow_decl(
                    item.workflow_decl,
                    unit=item.target_unit,
                    agent_contract=agent_contract,
                )
            )

        return CompiledSection(title=workflow_body.title, body=tuple(body))

    def _compile_workflow_law(
        self,
        law_body: model.LawBody,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        flat_items = self._flatten_law_items(law_body, owner_label=owner_label)
        self._validate_workflow_law(
            flat_items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

        lines: list[str] = []
        mode_bindings: dict[str, model.ModeStmt] = {}
        for item in flat_items:
            rendered: list[str] = []
            if isinstance(item, model.ActiveWhenStmt):
                rendered.append(
                    f"This pass runs only when {self._render_condition_expr(item.expr, unit=unit)}."
                )
            elif isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
                fixed_mode = self._resolve_constant_enum_member(item.expr, unit=unit)
                if fixed_mode is not None:
                    rendered.append(f"Active mode: {fixed_mode}.")
            elif isinstance(item, model.MatchStmt):
                rendered.extend(
                    self._render_match_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            elif isinstance(item, model.WhenStmt):
                rendered.extend(
                    self._render_when_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            else:
                rendered.extend(
                    self._render_law_stmt_lines(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        bullet=False,
                    )
                )

            if not rendered:
                continue
            if lines:
                lines.append("")
            lines.extend(rendered)

        return tuple(lines)

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

    def _render_match_stmt(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> list[str]:
        fixed_mode: str | None = None
        if isinstance(stmt.expr, model.ExprRef) and len(stmt.expr.parts) == 1:
            mode_stmt = mode_bindings.get(stmt.expr.parts[0])
            if mode_stmt is not None:
                fixed_mode = self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)

        if fixed_mode is not None:
            for case in stmt.cases:
                if case.head is None or self._render_expr(case.head, unit=unit) == fixed_mode:
                    return self._render_law_stmt_block(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                        bullet=False,
                    )
            return []

        labels = [
            self._render_expr(case.head, unit=unit)
            for case in stmt.cases
            if case.head is not None
        ]
        lines = ["Work in exactly one mode:"]
        lines.extend(f"- {label}" for label in labels)
        for case in stmt.cases:
            if case.head is None:
                heading = "Else:"
            else:
                heading = f"If mode is {self._render_expr(case.head, unit=unit)}:"
            lines.extend(["", heading])
            lines.extend(
                self._render_law_stmt_block(
                    case.items,
                    unit=unit,
                    owner_label=owner_label,
                    bullet=True,
                )
            )
        return lines

    def _render_when_stmt(
        self,
        stmt: model.WhenStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> list[str]:
        lines = [f"If {self._render_condition_expr(stmt.expr, unit=unit)}:"]
        lines.extend(
            self._render_law_stmt_block(
                stmt.items,
                unit=unit,
                owner_label=owner_label,
                bullet=True,
                mode_bindings=mode_bindings,
            )
        )
        return lines

    def _render_law_stmt_block(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        bullet: bool,
        mode_bindings: dict[str, model.ModeStmt] | None = None,
    ) -> list[str]:
        mode_bindings = dict(mode_bindings or {})
        lines: list[str] = []
        for item in items:
            if isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
            if isinstance(item, model.MatchStmt):
                rendered = self._render_match_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                )
            elif isinstance(item, model.WhenStmt):
                rendered = self._render_when_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                )
            else:
                rendered = self._render_law_stmt_lines(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    bullet=bullet,
                )
            if (
                lines
                and rendered
                and not (
                    bullet
                    and lines[-1].startswith("- ")
                    and all(line.startswith("- ") for line in rendered)
                )
            ):
                lines.append("")
            lines.extend(rendered)
        return lines

    def _render_law_stmt_lines(
        self,
        stmt: model.LawStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        bullet: bool,
    ) -> list[str]:
        if isinstance(stmt, model.CurrentArtifactStmt):
            text = f"Current artifact: {self._display_law_path_root(stmt.target, unit=unit)}."
        elif isinstance(stmt, model.CurrentNoneStmt):
            text = "There is no current artifact for this turn."
        elif isinstance(stmt, model.MustStmt):
            text = self._render_must_stmt(stmt, unit=unit)
        elif isinstance(stmt, model.OwnOnlyStmt):
            text = f"Own only {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.PreserveStmt):
            text = f"Preserve {stmt.kind} {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.SupportOnlyStmt):
            text = (
                f"{self._render_path_set_subject(stmt.target, unit=unit)} is comparison-only support."
            )
        elif isinstance(stmt, model.IgnoreStmt):
            text = self._render_ignore_stmt(stmt, unit=unit)
        elif isinstance(stmt, model.ForbidStmt):
            text = f"Do not modify {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.InvalidateStmt):
            text = f"{self._display_law_path_root(stmt.target, unit=unit)} is no longer current."
        elif isinstance(stmt, model.StopStmt):
            message = stmt.message or ""
            if message and not message.endswith("."):
                message += "."
            text = "Stop." if stmt.message is None else f"Stop: {message}"
            if stmt.when_expr is not None:
                text = f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, {_lowercase_initial(text)}"
        elif isinstance(stmt, model.LawRouteStmt):
            text = stmt.label if stmt.label.endswith(".") else f"{stmt.label}."
            if stmt.when_expr is not None:
                text = (
                    f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, "
                    f"{_lowercase_initial(text)}"
                )
        elif isinstance(stmt, model.ActiveWhenStmt):
            text = f"This pass runs only when {self._render_condition_expr(stmt.expr, unit=unit)}."
        elif isinstance(stmt, model.ModeStmt):
            fixed_mode = self._resolve_constant_enum_member(stmt.expr, unit=unit)
            return [] if fixed_mode is None else [f"Active mode: {fixed_mode}."]
        else:
            return []

        if bullet:
            return [f"- {text}"]
        return [text]

    def _render_must_stmt(self, stmt: model.MustStmt, *, unit: IndexedUnit) -> str:
        if (
            isinstance(stmt.expr, model.ExprBinary)
            and stmt.expr.op == "=="
            and isinstance(stmt.expr.left, model.ExprRef)
        ):
            return f"Must {self._render_expr(stmt.expr.left, unit=unit)} == {self._render_expr(stmt.expr.right, unit=unit)}."
        return f"Must {self._render_expr(stmt.expr, unit=unit)}."

    def _render_ignore_stmt(self, stmt: model.IgnoreStmt, *, unit: IndexedUnit) -> str:
        target = self._render_path_set(stmt.target)
        if stmt.bases == ("rewrite_evidence",):
            prefix = "Ignore"
            if stmt.when_expr is not None:
                prefix = f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, ignore"
            return f"{prefix} {target} for rewrite evidence."
        if stmt.bases == ("truth",) or not stmt.bases:
            return f"{self._render_path_set_subject(stmt.target, unit=unit)} does not count as truth for this pass."
        return f"Ignore {target} for {', '.join(stmt.bases)}."

    def _render_path_set_subject(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
    ) -> str:
        target = self._coerce_path_set(target)
        if len(target.paths) == 1 and not target.except_paths:
            path = target.paths[0]
            if not path.wildcard:
                return self._display_law_path_root(path, unit=unit)
        return self._render_path_set(target)

    def _render_path_set(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> str:
        target = self._coerce_path_set(target)
        parts = [self._render_law_path(path) for path in target.paths]
        rendered = ", ".join(parts)
        if len(parts) > 1:
            rendered = "{" + rendered + "}"
        if target.except_paths:
            rendered += " except " + ", ".join(
                self._render_law_path(path) for path in target.except_paths
            )
        return rendered

    def _render_law_path(self, path: model.LawPath) -> str:
        text = ".".join(path.parts)
        if path.wildcard:
            text += ".*"
        return f"`{text}`"

    def _render_condition_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_condition_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            if expr.op == "in" and isinstance(expr.right, model.ExprSet):
                subject = self._render_condition_subject(expr.left, unit=unit)
                choices = [self._render_condition_choice(item, unit=unit) for item in expr.right.items]
                if not choices:
                    return f"{subject} is in {{}}"
                if len(choices) == 1:
                    return f"{subject} is {choices[0]}"
                if len(choices) == 2:
                    return f"{subject} is {choices[0]} or {choices[1]}"
                return f"{subject} is {', '.join(choices[:-1])}, or {choices[-1]}"
            left = self._render_condition_expr(expr.left, unit=unit)
            right = self._render_condition_expr(expr.right, unit=unit)
            joiner = expr.op
            if expr.op == "==":
                return f"{left} is {right}"
            if expr.op == "!=":
                return f"{left} is not {right}"
            return f"{left} {joiner} {right}"
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{_humanize_key(expr.name).lower()}({args})"
        return self._render_expr(expr, unit=unit)

    def _render_condition_choice(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, str):
            return expr.replace("_", " ")
        return self._render_expr(expr, unit=unit)

    def _render_condition_subject(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            parts = expr.parts
            if len(parts) == 1:
                return _humanize_key(parts[0]).lower()
            return f"{self._render_ref_root(parts[:-1], unit=unit)} {_humanize_key(parts[-1]).lower()}"
        return self._render_condition_expr(expr, unit=unit)

    def _render_condition_ref(self, ref: model.ExprRef, *, unit: IndexedUnit) -> str:
        parts = ref.parts
        if not parts:
            return ""
        key = parts[-1]
        if key == "missing":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is missing"
        if key == "unclear":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is unclear"
        if key.endswith("_missing"):
            return f"{_humanize_key(key.removesuffix('_missing')).lower()} is missing"
        if key.endswith("_unknown"):
            return f"{_humanize_key(key.removesuffix('_unknown')).lower()} is unknown"
        if key.endswith("_repeated"):
            return f"{_humanize_key(key.removesuffix('_repeated')).lower()} is repeated"
        if key.startswith("owes_"):
            return f"{_humanize_key(key.removeprefix('owes_')).lower()} is owed now"
        if key.endswith("_changed"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_invalidated"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_requested"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_used"):
            return f"{_humanize_key(key).lower()}"
        return self._render_expr(ref, unit=unit)

    def _render_ref_root(self, parts: tuple[str, ...], *, unit: IndexedUnit) -> str:
        if not parts:
            return "this turn"
        try:
            root_path = model.LawPath(parts=parts)
            return self._display_law_path_root(root_path, unit=unit).lower()
        except CompileError:
            return _humanize_key(parts[-1]).lower()

    def _render_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_expr_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            return (
                f"{self._render_expr(expr.left, unit=unit)} {expr.op} "
                f"{self._render_expr(expr.right, unit=unit)}"
            )
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{expr.name}({args})"
        if isinstance(expr, model.ExprSet):
            rendered = ", ".join(self._render_expr(item, unit=unit) for item in expr.items)
            return "{" + rendered + "}"
        if isinstance(expr, str):
            return expr
        if isinstance(expr, bool):
            return "true" if expr else "false"
        return str(expr)

    def _render_expr_ref(self, expr: model.ExprRef, *, unit: IndexedUnit) -> str:
        constant = self._resolve_constant_enum_member(expr, unit=unit)
        if constant is not None:
            return constant
        return ".".join(expr.parts)

    def _resolve_constant_enum_member(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if isinstance(expr, str):
            return expr
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
            owner_label=owner_label,
        )
        branches = self._collect_law_leaf_branches(items, unit=unit)
        if not branches:
            branches = (LawBranch(),)

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
                        owner_label=owner_label,
                        current_target=current,
                    )
                for invalidate in branch.invalidations:
                    if self._law_paths_match(current.target, invalidate.target):
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
                    ):
                        raise CompileError(
                            f"support_only and ignore for comparison contradict in {owner_label}"
                        )
            if current_target_key is not None:
                for ignore in branch.ignores:
                    if ("truth" in ignore.bases or not ignore.bases) and self._path_set_contains_path(
                        ignore.target,
                        current.target,
                    ):
                        raise CompileError(
                            f"The current artifact cannot be ignored for truth in {owner_label}"
                        )
            for own in branch.owns:
                own_target = self._coerce_path_set(own.target)
                for forbid in branch.forbids:
                    if self._path_sets_overlap(own_target, forbid.target):
                        raise CompileError(
                            f"Owned and forbidden scope overlap in {owner_label}"
                        )
                for preserve in branch.preserves:
                    if preserve.kind == "exact" and any(
                        self._path_set_contains_path(preserve.target, path)
                        for path in own_target.paths
                    ):
                            raise CompileError(
                                f"Owned scope overlaps exact-preserved scope in {owner_label}"
                            )

    def _validate_law_stmt_tree(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
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
                        owner_label=owner_label,
                        mode_bindings=local_mode_bindings,
                    )
                continue
            if isinstance(item, model.WhenStmt):
                self._validate_law_stmt_tree(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                continue
            if isinstance(item, model.CurrentArtifactStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    owner_label=owner_label,
                    statement_label="current artifact",
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, model.InvalidateStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    owner_label=owner_label,
                    statement_label="invalidate",
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, (model.OwnOnlyStmt, model.SupportOnlyStmt, model.IgnoreStmt, model.ForbidStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, model.PreserveStmt):
                if item.kind == "vocabulary":
                    self._validate_path_set_roots(
                        item.target,
                        unit=unit,
                        owner_label=owner_label,
                        statement_label="preserve vocabulary",
                        allowed_kinds=("enum",),
                    )
                else:
                    self._validate_path_set_roots(
                        item.target,
                        unit=unit,
                        owner_label=owner_label,
                        statement_label=f"preserve {item.kind}",
                        allowed_kinds=("input", "output"),
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
            owner_label=owner_label,
            statement_label="invalidate",
            allowed_kinds=("input", "output"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"invalidate must name one full input or output artifact in {owner_label}: "
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
        owner_label: str,
        current_target: model.CurrentArtifactStmt,
    ) -> None:
        target = self._coerce_path_set(stmt.target)
        current_root = self._validate_law_path_root(
            current_target.target,
            unit=unit,
            owner_label=owner_label,
            statement_label="current artifact",
            allowed_kinds=("input", "output"),
        )
        for path in target.paths:
            resolved = self._validate_law_path_root(
                path,
                unit=unit,
                owner_label=owner_label,
                statement_label="own only",
                allowed_kinds=("input", "output"),
            )
            if (
                resolved.unit.module_parts != current_root.unit.module_parts
                or resolved.decl.name != current_root.decl.name
            ):
                raise CompileError(
                    f"own only must stay rooted in the current artifact in {owner_label}: "
                    f"{'.'.join(path.parts)}"
                )

    def _validate_path_set_roots(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> None:
        target = self._coerce_path_set(target)
        for path in (*target.paths, *target.except_paths):
            self._validate_law_path_root(
                path,
                unit=unit,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )

    def _validate_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        resolved = self._resolve_law_path(
            path,
            unit=unit,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        if isinstance(resolved.decl, model.EnumDecl) and resolved.remainder:
            raise CompileError(
                f"{statement_label} enum targets must not descend through fields in {owner_label}: "
                f"{'.'.join(path.parts)}"
            )
        return resolved

    def _resolve_law_path(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        matches: list[ResolvedLawPath] = []
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

        unique_matches: list[ResolvedLawPath] = []
        seen: set[tuple[tuple[str, ...], str, tuple[str, ...], str]] = set()
        for match in matches:
            key = (
                match.unit.module_parts,
                match.decl.name,
                match.remainder,
                type(match.decl).__name__,
            )
            if key in seen:
                continue
            seen.add(key)
            unique_matches.append(match)

        if len(unique_matches) == 1:
            return unique_matches[0]
        if len(unique_matches) > 1:
            choices = ", ".join(
                _dotted_decl_name(match.unit.module_parts, match.decl.name)
                for match in unique_matches
            )
            raise CompileError(
                f"Ambiguous {statement_label} path in {owner_label}: "
                f"{'.'.join(path.parts)} matches {choices}"
            )

        allowed_text = " or ".join(allowed_kinds)
        raise CompileError(
            f"{statement_label} target must resolve to a declared {allowed_text} in {owner_label}: "
            f"{'.'.join(path.parts)}"
        )

    def _resolve_output_field_node(
        self,
        decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> AddressableNode:
        current_node = AddressableNode(unit=unit, root_decl=decl, target=decl)
        if not path:
            return current_node
        for segment in path:
            children = self._get_addressable_children(current_node)
            if children is None or segment not in children:
                raise CompileError(
                    f"Unknown output field on {surface_label} in {owner_label}: "
                    f"{decl.name}.{'.'.join(path)}"
                )
            current_node = children[segment]
        return current_node

    def _law_paths_match(self, left: model.LawPath, right: model.LawPath) -> bool:
        return self._law_path_contains_path(left, right) or self._law_path_contains_path(right, left)

    def _law_path_contains_path(self, container: model.LawPath, path: model.LawPath) -> bool:
        if len(container.parts) > len(path.parts):
            return False
        if path.parts[: len(container.parts)] != container.parts:
            return False
        if len(container.parts) == len(path.parts):
            return container.wildcard or not path.wildcard or container.wildcard == path.wildcard
        return container.wildcard

    def _path_set_contains_path(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        path: model.LawPath,
    ) -> bool:
        target = self._coerce_path_set(target)
        if not any(self._law_path_contains_path(base, path) for base in target.paths):
            return False
        if any(self._law_path_contains_path(excluded, path) for excluded in target.except_paths):
            return False
        return True

    def _path_sets_overlap(
        self,
        left: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        right: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> bool:
        left = self._coerce_path_set(left)
        right = self._coerce_path_set(right)
        for path in left.paths:
            if self._path_set_contains_path(right, path):
                return True
        for path in right.paths:
            if self._path_set_contains_path(left, path):
                return True
        return False

    def _display_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
    ) -> str:
        try:
            resolved = self._resolve_law_path(
                path,
                unit=unit,
                owner_label="workflow law",
                statement_label="law path",
                allowed_kinds=("input", "output", "enum"),
            )
        except CompileError:
            return ".".join(path.parts)
        title = self._display_readable_decl(resolved.decl)
        if not resolved.remainder:
            return title
        return f"{title}.{'.'.join(resolved.remainder)}"

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

    def _compile_section_body(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        previous_kind: str | None = None

        for item in items:
            current_kind = "ref" if isinstance(item, ResolvedSectionRef) else "prose"
            if previous_kind is not None and current_kind != previous_kind and body:
                if body[-1] != "":
                    body.append("")

            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
            elif isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(item.items),
                    )
                )
            elif isinstance(item, ResolvedRouteLine):
                body.append(f"{item.label} -> {item.target_name}")
            else:
                body.append(f"- {item.label}")

            previous_kind = current_kind

        return tuple(body)

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
        enums_by_name: dict[str, model.EnumDecl] = {}

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
            if isinstance(declaration, model.EnumDecl):
                self._register_decl(enums_by_name, declaration.name, module_parts)
                self._validate_enum_decl(
                    declaration,
                    owner_label=f"enum {_dotted_decl_name(module_parts, declaration.name)}",
                )
                enums_by_name[declaration.name] = declaration
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
            enums_by_name=enums_by_name,
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

    def _validate_enum_decl(self, decl: model.EnumDecl, *, owner_label: str) -> None:
        seen_keys: set[str] = set()
        for member in decl.members:
            if member.key in seen_keys:
                raise CompileError(f"Duplicate enum member key in {owner_label}: {member.key}")
            seen_keys.add(member.key)

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


def _lowercase_initial(value: str) -> str:
    if not value:
        return value
    return value[0].lower() + value[1:]


def _display_addressable_ref(ref: model.AddressableRef) -> str:
    root = _dotted_ref_name(ref.root)
    if not ref.path:
        return root
    return f"{root}:{'.'.join(ref.path)}"
