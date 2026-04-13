from __future__ import annotations

from doctrine._compiler.types import (
    CompiledAgent,
    CompiledReadableBlock,
)
from doctrine._renderer.blocks import _render_block
from doctrine._renderer.semantic import (
    DEFAULT_PROFILE as _DEFAULT_PROFILE,
)
from doctrine.model import RoleScalar


def render_markdown(agent: CompiledAgent) -> str:
    sections: list[str] = []
    for field in agent.fields:
        if isinstance(field, RoleScalar):
            sections.append(field.text)
            continue
        sections.append(render_readable_block(field, depth=2))
    return "\n\n".join(section for section in sections if section) + "\n"


def render_readable_block(block: CompiledReadableBlock, *, depth: int = 2) -> str:
    return _render_block(block, depth=depth, profile=_DEFAULT_PROFILE)
