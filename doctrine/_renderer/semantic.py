from __future__ import annotations

from doctrine._compiler.types import CompiledBodyItem, CompiledSection, ResolvedRenderProfile
from doctrine.model import EmphasizedLine


DEFAULT_PROFILE = ResolvedRenderProfile(name="ContractMarkdown")
_BUILTIN_PROFILE_MODES = {
    "ContractMarkdown": {
        "properties": "titled_section",
        "guarded_sections": "titled_section",
        "analysis.stages": "titled_section",
        "review.contract_checks": "titled_section",
        "control.invalidations": "expanded_sequence",
        "identity.owner": "title",
        "identity.debug": "title",
        "identity.enum_wire": "title",
    },
    "ArtifactMarkdown": {
        "properties": "sentence",
        "guarded_sections": "concise_explanatory_shell",
        "analysis.stages": "natural_ordered_prose",
        "review.contract_checks": "sentence",
        "control.invalidations": "expanded_sequence",
        "identity.owner": "title",
        "identity.debug": "title",
        "identity.enum_wire": "title",
    },
    "CommentMarkdown": {
        "properties": "sentence",
        "guarded_sections": "concise_explanatory_shell",
        "analysis.stages": "natural_ordered_prose",
        "review.contract_checks": "sentence",
        "control.invalidations": "expanded_sequence",
        "identity.owner": "title",
        "identity.debug": "title",
        "identity.enum_wire": "title",
    },
}


def render_semantic_section(
    block: CompiledSection,
    *,
    profile: ResolvedRenderProfile,
    flatten_body_to_sentence,
) -> str | None:
    if (
        block.semantic_target == "review.contract_checks"
        and resolve_profile_mode(profile, "review.contract_checks") == "sentence"
    ):
        text = flatten_body_to_sentence(block.body, profile=profile)
        if text is not None:
            return f"{block.title}: {text}"
    return None


def flatten_body_to_sentence(
    body: tuple[CompiledBodyItem, ...],
    *,
    profile: ResolvedRenderProfile,
    render_prose_line,
) -> str | None:
    parts: list[str] = []
    for item in body:
        if item == "":
            continue
        if isinstance(item, (str, EmphasizedLine)):
            parts.append(render_prose_line(item, profile=profile))
            continue
        return None
    return " ".join(part.strip() for part in parts if part.strip()) or None


def resolve_profile_mode(profile: ResolvedRenderProfile, *targets: str) -> str | None:
    authored = {".".join(rule.target_parts): rule.mode for rule in profile.rules}
    for target in targets:
        mode = authored.get(target)
        if mode is not None:
            return mode
    builtin = _BUILTIN_PROFILE_MODES.get(profile.name, {})
    for target in targets:
        mode = builtin.get(target)
        if mode is not None:
            return mode
    return None


def humanize_key(value: str) -> str:
    return value.replace("_", " ").strip().title()
