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
        return _render_titled_block(
            block.title,
            block.body,
            depth=depth,
            metadata=_render_metadata_line(
                requirement=block.requirement,
                kind_label="section" if block.emit_metadata else None,
                when_text=block.when_text,
            ),
        )
    if isinstance(block, CompiledSequenceBlock):
        return _render_list_block(
            block.title,
            block.items,
            depth=depth,
            marker="1.",
            metadata=_render_metadata_line(
                requirement=block.requirement,
                kind_label="ordered list",
                when_text=block.when_text,
            ),
        )
    if isinstance(block, CompiledBulletsBlock):
        return _render_list_block(
            block.title,
            block.items,
            depth=depth,
            marker="-",
            metadata=_render_metadata_line(
                requirement=block.requirement,
                kind_label="unordered list",
                when_text=block.when_text,
            ),
        )
    if isinstance(block, CompiledChecklistBlock):
        return _render_list_block(
            block.title,
            block.items,
            depth=depth,
            marker="- [ ]",
            metadata=_render_metadata_line(
                requirement=block.requirement,
                kind_label="checklist",
                when_text=block.when_text,
            ),
        )
    if isinstance(block, CompiledDefinitionsBlock):
        return _render_definitions_block(block, depth=depth)
    if isinstance(block, CompiledTableBlock):
        return _render_table_block(block, depth=depth)
    if isinstance(block, CompiledCalloutBlock):
        return _render_callout_block(block)
    if isinstance(block, CompiledCodeBlock):
        return _render_code_block(block, depth=depth)
    if isinstance(block, CompiledRuleBlock):
        return _render_rule_block(block)
    raise TypeError(f"Unsupported compiled readable block: {type(block).__name__}")


def _render_titled_block(
    title: str,
    body: tuple[CompiledBodyItem, ...],
    *,
    depth: int,
    line_prefix: str = "",
    metadata: str | None = None,
) -> str:
    lines = [f"{'#' * depth} {title}"]
    body_lines: list[str] = []
    previous_was_block = False

    if metadata is not None:
        body_lines.extend(["", metadata])

    for item in body:
        if isinstance(item, str):
            if not item:
                if body_lines and body_lines[-1] != "":
                    body_lines.append("")
                previous_was_block = False
                continue
            if previous_was_block and body_lines and body_lines[-1] != "":
                body_lines.append("")
            body_lines.append(f"{line_prefix}{item}" if line_prefix else item)
            previous_was_block = False
            continue
        if isinstance(item, EmphasizedLine):
            rendered = f"**{item.kind.upper()}**: {item.text}"
            if previous_was_block and body_lines and body_lines[-1] != "":
                body_lines.append("")
            body_lines.append(f"{line_prefix}{rendered}" if line_prefix else rendered)
            previous_was_block = False
            continue

        if body_lines and body_lines[-1] != "":
            body_lines.append("")
        nested = _render_block(item, depth=depth + 1).splitlines()
        if line_prefix:
            nested = [f"{line_prefix}{line}" if line else line for line in nested]
        body_lines.extend(nested)
        previous_was_block = True

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
    metadata: str | None = None,
) -> str:
    lines = [f"{'#' * depth} {title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])
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

    if not rendered_items:
        return "\n".join(lines).rstrip()
    return "\n".join([*lines, *rendered_items]).rstrip()


def _render_code_block(block: CompiledCodeBlock, *, depth: int) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="code",
        when_text=block.when_text,
        extra=block.language,
    )
    fence = f"```{block.language or ''}".rstrip()
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])
    lines.extend([fence, *block.text.splitlines(), "```"])
    return "\n".join(lines)


def _render_rule_block(block: CompiledRuleBlock) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="rule",
        when_text=block.when_text,
    )
    if metadata is None:
        return "---"
    return f"{metadata}\n\n---"


def _render_definitions_block(block: CompiledDefinitionsBlock, *, depth: int) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="definitions",
        when_text=block.when_text,
    )
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])
    for item in block.items:
        if not item.body:
            lines.append(f"- **{item.title}**")
            continue
        first, *rest = item.body
        first_text = _render_prose_line(first)
        if rest:
            lines.append(f"- **{item.title}**")
            lines.append(f"  {first_text}")
            for line in rest:
                lines.append(f"  {_render_prose_line(line)}")
            continue
        lines.append(f"- **{item.title}** \u2014 {first_text}")
    return "\n".join(lines).rstrip()


def _render_table_block(block: CompiledTableBlock, *, depth: int) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="table",
        when_text=block.when_text,
    )
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])
    if block.table.rows:
        headers = [column.title for column in block.table.columns]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in block.table.rows:
            cell_map = {cell.key: cell.text for cell in row.cells}
            lines.append(
                "| "
                + " | ".join(cell_map.get(column.key, "") for column in block.table.columns)
                + " |"
            )
    else:
        lines.append("| Column | Meaning |")
        lines.append("| --- | --- |")
        for column in block.table.columns:
            meaning = " ".join(_render_prose_line(line) for line in column.body).strip()
            lines.append(f"| {column.title} | {meaning} |")
    if block.table.notes:
        lines.append("")
        lines.extend(_render_prose_line(note) for note in block.table.notes)
    return "\n".join(lines).rstrip()


def _render_callout_block(block: CompiledCalloutBlock) -> str:
    label = (block.kind or "note").upper()
    title = f"{label} \u2014 {block.title}" if block.title else label
    lines = [f"> **{title}**"]
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="callout",
        when_text=block.when_text,
    )
    if metadata is not None:
        lines.append(f"> {metadata}")
    for line in block.body:
        text = _render_prose_line(line)
        if text:
            lines.append(f"> {text}")
        else:
            lines.append(">")
    return "\n".join(lines)


def _render_metadata_line(
    *,
    requirement: str | None,
    kind_label: str | None,
    when_text: str | None,
    extra: str | None = None,
) -> str | None:
    parts: list[str] = []
    if requirement is not None:
        parts.append(requirement.capitalize())
    if kind_label is not None:
        parts.append(kind_label)
    if extra is not None:
        parts.append(extra)
    if when_text is not None:
        parts.append(f"when {when_text}")
    if not parts:
        return None
    return "_" + " · ".join(parts) + "_"


def _render_prose_line(item: CompiledBodyItem) -> str:
    if isinstance(item, EmphasizedLine):
        return f"**{item.kind.upper()}**: {item.text}"
    if isinstance(item, str):
        return item
    return _render_block(item, depth=0)
