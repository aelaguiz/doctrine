from __future__ import annotations

from pyprompt.compiler import CompiledAgent, CompiledSection
from pyprompt.model import EmphasizedLine, RoleScalar


def render_markdown(agent: CompiledAgent) -> str:
    sections: list[str] = []
    for field in agent.fields:
        if isinstance(field, RoleScalar):
            sections.append(field.text)
            continue
        sections.append(_render_section(field, depth=2))
    return "\n\n".join(section for section in sections if section) + "\n"


def _render_section(section: CompiledSection, *, depth: int) -> str:
    lines = [f"{'#' * depth} {section.title}"]
    body_lines: list[str] = []

    for item in section.body:
        if isinstance(item, str):
            body_lines.append(item)
            continue
        if isinstance(item, EmphasizedLine):
            body_lines.append(f"**{item.kind.upper()}**: {item.text}")
            continue

        if body_lines and body_lines[-1] != "":
            body_lines.append("")
        body_lines.extend(_render_section(item, depth=depth + 1).splitlines())
        body_lines.append("")

    while body_lines and body_lines[-1] == "":
        body_lines.pop()

    if not body_lines:
        return "\n".join(lines)

    return "\n".join([*lines, "", *body_lines])
