from __future__ import annotations

from pyprompt.compiler import CompiledAgent, CompiledSection
from pyprompt.model import RoleScalar


def render_markdown(agent: CompiledAgent) -> str:
    sections: list[str] = []
    if isinstance(agent.role, RoleScalar):
        sections.append(agent.role.text)
    else:
        sections.append(_render_section(agent.role, depth=2))
    sections.append(_render_section(agent.workflow, depth=2))
    return "\n\n".join(section for section in sections if section) + "\n"


def _render_section(section: CompiledSection, *, depth: int) -> str:
    lines = [f"{'#' * depth} {section.title}", ""]
    lines.extend(section.preamble)

    if section.children:
        if section.preamble:
            lines.append("")
        for index, child in enumerate(section.children):
            lines.extend(_render_section(child, depth=depth + 1).splitlines())
            if index != len(section.children) - 1:
                lines.append("")

    return "\n".join(lines)
