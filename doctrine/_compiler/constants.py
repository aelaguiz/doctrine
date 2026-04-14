from __future__ import annotations

import re

from doctrine._compiler.resolved_types import ConfigSpec
from doctrine._compiler.types import ResolvedRenderProfile

# Canonical constants and small policy helpers previously mixed into shared.py.

_INTERPOLATION_EXPR_RE = re.compile(
    r"\s*"
    r"([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
    r"(?:\s*:\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*))?"
    r"\s*"
)
_INTERPOLATION_RE = re.compile(r"\{\{([^{}]+)\}\}")
_RESERVED_AGENT_FIELD_KEYS = {
    "role",
    "inputs",
    "outputs",
    "analysis",
    "skills",
    "review",
    "final_output",
}
_LAW_BEARING_AUTHORED_SLOT_KEYS = frozenset({"workflow", "handoff_routing"})
_ROUTE_BEARING_AUTHORED_SLOT_KEYS = frozenset({"handoff_routing"})

_BUILTIN_INPUT_SOURCES = {
    "Prompt": ConfigSpec(title="Prompt", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
    "EnvVar": ConfigSpec(title="EnvVar", required_keys={"env": "Env"}, optional_keys={}),
}

_BUILTIN_OUTPUT_TARGETS = {
    "TurnResponse": ConfigSpec(title="Turn Response", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
}

_BUILTIN_RENDER_PROFILE_NAMES = ("ContractMarkdown", "ArtifactMarkdown", "CommentMarkdown")


def _semantic_render_target_for_block(kind: str, key: str) -> str | None:
    if kind == "section" and key == "contract_checks":
        return "review.contract_checks"
    if kind in {"sequence", "bullets", "checklist"} and key == "invalidations":
        return "control.invalidations"
    return None


def _resolve_render_profile_mode(
    profile: ResolvedRenderProfile,
    *targets: str,
) -> str | None:
    authored = {".".join(rule.target_parts): rule.mode for rule in profile.rules}
    for target in targets:
        mode = authored.get(target)
        if mode is not None:
            return mode
    return None


_READABLE_DECL_REGISTRIES = (
    ("agent declaration", "agents_by_name"),
    ("analysis declaration", "analyses_by_name"),
    ("decision declaration", "decisions_by_name"),
    ("schema declaration", "schemas_by_name"),
    ("document declaration", "documents_by_name"),
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
_SCHEMA_FAMILY_TITLES = {
    "sections": "Required Sections",
    "gates": "Contract Gates",
    "artifacts": "Artifact Inventory",
    "groups": "Surface Groups",
}

_REVIEW_REQUIRED_FIELD_NAMES = frozenset(
    {
        "verdict",
        "reviewed_artifact",
        "analysis",
        "readback",
        "failing_gates",
        "next_owner",
    }
)
_REVIEW_OPTIONAL_FIELD_NAMES = frozenset({"blocked_gate", "active_mode", "trigger_reason"})
_REVIEW_CONTEXT_FIELD_NAMES = frozenset({"current_artifact"})
_REVIEW_FIELD_NAMES = (
    _REVIEW_REQUIRED_FIELD_NAMES | _REVIEW_OPTIONAL_FIELD_NAMES | _REVIEW_CONTEXT_FIELD_NAMES
)
_REVIEW_GUARD_FIELD_NAMES = _REVIEW_FIELD_NAMES | frozenset({"current_artifact"})
_REVIEW_VERDICT_TEXT = {
    "accept": "accepted",
    "changes_requested": "changes requested",
}
_REVIEW_CONTRACT_FACT_KEYS = ("passes", "failed_gates", "first_failed_gate")
