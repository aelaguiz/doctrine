from __future__ import annotations

from doctrine.compiler import (
    CompiledAgent,
    CompiledBodyItem,
    CompiledBulletsBlock,
    CompiledCalloutBlock,
    CompiledChecklistBlock,
    CompiledCodeBlock,
    CompiledDefinitionsBlock,
    CompiledReadableBlock,
    CompiledRuleBlock,
    CompiledSection,
    CompiledSequenceBlock,
    CompiledTableBlock,
)
from doctrine.model import EmphasizedLine, RoleScalar


def render_markdown(agent: CompiledAgent) -> str:
    sections: list[str] = []
    for field in agent.fields:
        if isinstance(field, RoleScalar):
            sections.append(field.text)
            continue
        sections.append(_render_block(field, depth=2))
    return "\n\n".join(section for section in sections if section) + "\n"


def _render_block(block: CompiledReadableBlock, *, depth: int) -> str:
    if isinstance(block, CompiledSection):
        return _render_titled_block(block.title, block.body, depth=depth)
    if isinstance(block, CompiledSequenceBlock):
        return _render_list_block(block.title, block.body, depth=depth, marker="1.")
    if isinstance(block, CompiledBulletsBlock):
        return _render_list_block(block.title, block.body, depth=depth, marker="-")
    if isinstance(block, CompiledChecklistBlock):
        return _render_list_block(block.title, block.body, depth=depth, marker="- [ ]")
    if isinstance(block, CompiledDefinitionsBlock):
        return _render_titled_block(block.title, block.body, depth=depth)
    if isinstance(block, CompiledTableBlock):
        return _render_titled_block(block.title, block.body, depth=depth)
    if isinstance(block, CompiledCalloutBlock):
        return _render_titled_block(block.title, block.body, depth=depth, line_prefix="> ")
    if isinstance(block, CompiledCodeBlock):
        return _render_code_block(block.title, block.body, depth=depth)
    if isinstance(block, CompiledRuleBlock):
        return _render_rule_block(block.title, depth=depth)
    raise TypeError(f"Unsupported compiled readable block: {type(block).__name__}")


def _render_titled_block(
    title: str,
    body: tuple[CompiledBodyItem, ...],
    *,
    depth: int,
    line_prefix: str = "",
) -> str:
    lines = [f"{'#' * depth} {title}"]
    body_lines: list[str] = []

    for item in body:
        if isinstance(item, str):
            body_lines.append(f"{line_prefix}{item}" if line_prefix else item)
            continue
        if isinstance(item, EmphasizedLine):
            rendered = f"**{item.kind.upper()}**: {item.text}"
            body_lines.append(f"{line_prefix}{rendered}" if line_prefix else rendered)
            continue

        if body_lines and body_lines[-1] != "":
            body_lines.append("")
        nested = _render_block(item, depth=depth + 1).splitlines()
        if line_prefix:
            nested = [f"{line_prefix}{line}" if line else line for line in nested]
        body_lines.extend(nested)

    while body_lines and body_lines[-1] == "":
        body_lines.pop()

    if not body_lines:
        return "\n".join(lines)

    return "\n".join([*lines, "", *body_lines])


def _render_list_block(
    title: str,
    body: tuple[CompiledBodyItem, ...],
    *,
    depth: int,
    marker: str,
) -> str:
    lines = [f"{'#' * depth} {title}", ""]
    rendered_items: list[str] = []
    counter = 1

    for item in body:
        current_marker = marker
        if marker == "1.":
            current_marker = f"{counter}."
            counter += 1
        if isinstance(item, str):
            rendered_items.append(f"{current_marker} {item}")
            continue
        if isinstance(item, EmphasizedLine):
            rendered_items.append(f"{current_marker} **{item.kind.upper()}**: {item.text}")
            continue
        nested = _render_block(item, depth=depth + 1).splitlines()
        if nested:
            rendered_items.append(f"{current_marker} {nested[0]}")
            rendered_items.extend(nested[1:])

    return "\n".join([*lines, *rendered_items]).rstrip()


def _render_code_block(title: str, body: tuple[CompiledBodyItem, ...], *, depth: int) -> str:
    lines = [f"{'#' * depth} {title}", "", "```"]
    for item in body:
        if isinstance(item, str):
            lines.append(item)
            continue
        if isinstance(item, EmphasizedLine):
            lines.append(f"{item.kind.upper()}: {item.text}")
            continue
        lines.extend(_render_block(item, depth=depth + 1).splitlines())
    lines.append("```")
    return "\n".join(lines)


def _render_rule_block(title: str, *, depth: int) -> str:
    return "\n".join([f"{'#' * depth} {title}", "", "---"])
