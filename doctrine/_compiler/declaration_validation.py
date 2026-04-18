from __future__ import annotations

from pathlib import Path

import doctrine._model.declarations as model
from doctrine._compiler.diagnostics import compile_error, related_prompt_site

_KNOWN_RENDER_PROFILE_TARGETS = {
    "review.contract_checks",
    "analysis.stages",
    "control.invalidations",
    "guarded_sections",
    "identity.owner",
    "identity.debug",
    "identity.enum_wire",
    "properties",
    "guard",
    "sequence",
    "bullets",
    "checklist",
    "definitions",
    "table",
    "callout",
    "code",
    "markdown",
    "html",
    "footnotes",
    "image",
}
_KNOWN_RENDER_PROFILE_MODES = {
    "sentence",
    "titled_section",
    "expanded_sequence",
    "natural_ordered_prose",
    "concise_explanatory_shell",
    "title",
    "title_and_key",
    "wire_only",
}
_RENDER_PROFILE_TARGET_MODE_CONSTRAINTS = {
    "analysis.stages": {"natural_ordered_prose", "titled_section"},
    "review.contract_checks": {"sentence", "titled_section"},
    "control.invalidations": {"sentence", "expanded_sequence"},
    "identity.owner": {"title", "title_and_key"},
    "identity.debug": {"title", "title_and_key"},
    "identity.enum_wire": {"title", "title_and_key", "wire_only"},
}


def validate_enum_decl(
    decl: model.EnumDecl,
    *,
    owner_label: str,
    source_path: Path | None,
) -> None:
    seen_keys: dict[str, model.EnumMember] = {}
    seen_wire_values: dict[str, model.EnumMember] = {}
    for member in decl.members:
        existing_key = seen_keys.get(member.key)
        if existing_key is not None:
            raise compile_error(
                code="E293",
                summary="Duplicate enum member key",
                detail=f"Enum `{owner_label}` repeats member key `{member.key}`.",
                path=source_path,
                source_span=member.source_span,
                related=(
                    related_prompt_site(
                        label="first member",
                        path=source_path,
                        source_span=existing_key.source_span,
                    ),
                ),
                hints=("Keep each enum member key only once.",),
            )
        seen_keys[member.key] = member
        existing_wire = seen_wire_values.get(member.value)
        if existing_wire is not None:
            raise compile_error(
                code="E294",
                summary="Duplicate enum member wire",
                detail=f"Enum `{owner_label}` repeats wire value `{member.value}`.",
                path=source_path,
                source_span=member.source_span,
                related=(
                    related_prompt_site(
                        label="first member",
                        path=source_path,
                        source_span=existing_wire.source_span,
                    ),
                ),
                hints=("Keep each enum wire value only once.",),
            )
        seen_wire_values[member.value] = member


def validate_render_profile_decl(
    decl: model.RenderProfileDecl,
    *,
    owner_label: str,
    source_path: Path | None,
) -> None:
    seen_targets: dict[tuple[str, ...], model.RenderProfileRule] = {}
    for rule in decl.rules:
        target_text = ".".join(rule.target_parts)
        if target_text not in _KNOWN_RENDER_PROFILE_TARGETS:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Unknown render_profile target in {owner_label}: {target_text}",
                path=source_path,
                source_span=rule.source_span,
                hints=("Use only shipped render_profile targets.",),
            )
        if rule.mode not in _KNOWN_RENDER_PROFILE_MODES:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Unknown render_profile mode in {owner_label}: {rule.mode}",
                path=source_path,
                source_span=rule.source_span,
                hints=("Use only shipped render_profile modes.",),
            )
        allowed_modes = _RENDER_PROFILE_TARGET_MODE_CONSTRAINTS.get(target_text)
        if allowed_modes is not None and rule.mode not in allowed_modes:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Invalid render_profile mode for {target_text} in {owner_label}: {rule.mode}",
                path=source_path,
                source_span=rule.source_span,
                hints=("Keep each render_profile target on one of its shipped supported modes.",),
            )
        existing_rule = seen_targets.get(rule.target_parts)
        if existing_rule is not None:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Duplicate render_profile rule target in {owner_label}: {target_text}",
                path=source_path,
                source_span=rule.source_span,
                related=(
                    related_prompt_site(
                        label="first rule",
                        path=source_path,
                        source_span=existing_rule.source_span,
                    ),
                ),
                hints=("Declare each render_profile target at most once.",),
            )
        seen_targets[rule.target_parts] = rule
