from __future__ import annotations

from dataclasses import dataclass

import doctrine._model.declarations as model


@dataclass(frozen=True, slots=True)
class DeclarationKind:
    name: str
    label: str
    registry_attr: str
    decl_type: type
    readable: bool
    addressable_root: bool


DECLARATION_KINDS: tuple[DeclarationKind, ...] = (
    DeclarationKind(
        name="agent",
        label="agent declaration",
        registry_attr="agents_by_name",
        decl_type=model.Agent,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="analysis",
        label="analysis declaration",
        registry_attr="analyses_by_name",
        decl_type=model.AnalysisDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="decision",
        label="decision declaration",
        registry_attr="decisions_by_name",
        decl_type=model.DecisionDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="schema",
        label="schema declaration",
        registry_attr="schemas_by_name",
        decl_type=model.SchemaDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="table",
        label="table declaration",
        registry_attr="tables_by_name",
        decl_type=model.TableDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="document",
        label="document declaration",
        registry_attr="documents_by_name",
        decl_type=model.DocumentDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="input",
        label="input declaration",
        registry_attr="inputs_by_name",
        decl_type=model.InputDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="input_source",
        label="input source declaration",
        registry_attr="input_sources_by_name",
        decl_type=model.InputSourceDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="output",
        label="output declaration",
        registry_attr="outputs_by_name",
        decl_type=model.OutputDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="output_target",
        label="output target declaration",
        registry_attr="output_targets_by_name",
        decl_type=model.OutputTargetDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="output_shape",
        label="output shape declaration",
        registry_attr="output_shapes_by_name",
        decl_type=model.OutputShapeDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="output_schema",
        label="output schema declaration",
        registry_attr="output_schemas_by_name",
        decl_type=model.OutputSchemaDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="skill",
        label="skill declaration",
        registry_attr="skills_by_name",
        decl_type=model.SkillDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="enum",
        label="enum declaration",
        registry_attr="enums_by_name",
        decl_type=model.EnumDecl,
        readable=True,
        addressable_root=True,
    ),
    DeclarationKind(
        name="workflow",
        label="workflow declaration",
        registry_attr="workflows_by_name",
        decl_type=model.WorkflowDecl,
        readable=False,
        addressable_root=True,
    ),
    DeclarationKind(
        name="skills_block",
        label="skills block",
        registry_attr="skills_blocks_by_name",
        decl_type=model.SkillsDecl,
        readable=False,
        addressable_root=True,
    ),
    DeclarationKind(
        name="render_profile",
        label="render_profile declaration",
        registry_attr="render_profiles_by_name",
        decl_type=model.RenderProfileDecl,
        readable=False,
        addressable_root=False,
    ),
    DeclarationKind(
        name="route_only",
        label="route_only declaration",
        registry_attr="route_onlys_by_name",
        decl_type=model.RouteOnlyDecl,
        readable=False,
        addressable_root=False,
    ),
    DeclarationKind(
        name="grounding",
        label="grounding declaration",
        registry_attr="groundings_by_name",
        decl_type=model.GroundingDecl,
        readable=False,
        addressable_root=False,
    ),
    DeclarationKind(
        name="review",
        label="review declaration",
        registry_attr="reviews_by_name",
        decl_type=model.ReviewDecl,
        readable=False,
        addressable_root=False,
    ),
    DeclarationKind(
        name="inputs_block",
        label="inputs block",
        registry_attr="inputs_blocks_by_name",
        decl_type=model.InputsDecl,
        readable=False,
        addressable_root=False,
    ),
    DeclarationKind(
        name="outputs_block",
        label="outputs block",
        registry_attr="outputs_blocks_by_name",
        decl_type=model.OutputsDecl,
        readable=False,
        addressable_root=False,
    ),
    DeclarationKind(
        name="skill_package",
        label="skill_package declaration",
        registry_attr="skill_packages_by_name",
        decl_type=model.SkillPackageDecl,
        readable=False,
        addressable_root=False,
    ),
)


READABLE_DECLARATION_KINDS: tuple[DeclarationKind, ...] = tuple(
    kind for kind in DECLARATION_KINDS if kind.readable
)
ADDRESSABLE_ROOT_DECLARATION_KINDS: tuple[DeclarationKind, ...] = tuple(
    kind for kind in DECLARATION_KINDS if kind.addressable_root
)
