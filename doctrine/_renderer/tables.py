from __future__ import annotations

from doctrine._compiler.types import CompiledTableBlock, ResolvedRenderProfile


def render_pipe_table(block: CompiledTableBlock) -> list[str]:
    lines: list[str] = []
    headers = [column.title for column in block.table.columns]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in block.table.rows:
        cell_map = {cell.key: cell.text or "" for cell in row.cells}
        lines.append(
            "| "
            + " | ".join(cell_map.get(column.key, "") for column in block.table.columns)
            + " |"
        )
    return lines


def render_structured_table(
    block: CompiledTableBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
    render_body_lines,
    humanize_key,
) -> list[str]:
    lines: list[str] = []
    for row in block.table.rows:
        if lines:
            lines.append("")
        lines.append(f"{'#' * (depth + 1)} {humanize_key(row.key)}")
        lines.append("")
        cell_map = {cell.key: cell for cell in row.cells}
        for column in block.table.columns:
            cell = cell_map.get(column.key)
            if cell is None:
                continue
            if cell.body is None:
                lines.append(f"- {column.title}: {cell.text or ''}".rstrip())
                continue
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(f"{'#' * (depth + 2)} {column.title}")
            lines.append("")
            lines.extend(render_body_lines(cell.body, depth=depth + 2, profile=profile))
            lines.append("")
        while lines and lines[-1] == "":
            lines.pop()
    return lines
