from __future__ import annotations

from pyprompt.compiler import CompiledAgent
from pyprompt.model import RoleBlock, RoleScalar


def render_markdown(agent: CompiledAgent) -> str:
    sections = [_render_role(agent.role), _render_section(agent.workflow.title, agent.workflow.lines)]
    return "\n\n".join(section for section in sections if section) + "\n"


def _render_role(role: RoleScalar | RoleBlock) -> str:
    if isinstance(role, RoleScalar):
        return role.text
    return _render_section(role.title, role.lines)


def _render_section(title: str, lines: tuple[str, ...]) -> str:
    # Headings come only from explicit authored titles and preserve source order.
    return "\n".join([f"## {title}", "", *lines])
