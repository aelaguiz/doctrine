from __future__ import annotations

from doctrine._compiler.constants import LATE_ROOT
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.late_binding import bind_home
from doctrine._compiler.teams import find_home_team, team_members
from doctrine._compiler.types import (
    CompiledTableBlock, CompiledTableColumn, CompiledTableData,
    CompiledTableRow, CompiledTableCell,
)
from doctrine.diagnostics import CompileError


def compile_roster(context, block, *, unit):
    def error(detail, item):
        return compile_error(
            code="E609", summary="Invalid roster", detail=detail,
            path=unit.prompt_file.source_path, source_span=item.source_span,
        )

    active = context._active_skill_bind_agent_context
    match = find_home_team(context, active.agent, unit=active.unit) if active is not None else None
    if match is None:
        raise error(f"`roster {block.key}` needs a team, and this home has none.", block)
    owner, team = match
    columns = block.payload.columns
    for column in columns:
        if not any(match[1] == "agent" for match in LATE_ROOT.finditer(column.body[0])):
            raise error(f"Column `{column.key}` has no `{{{{agent:...}}}}` in its cell.", column)
    rows = []
    skipped = None
    for member in team_members(context, team, unit=owner):
        try:
            cells = bind_home(context, tuple(
                CompiledTableCell(key=column.key, text=context._interpolate_authored_prose_string(
                    column.body[0], unit=unit,
                    owner_label=f"roster {block.key}", surface_label="roster cell",
                ))
                for column in columns
            ), member, unit=owner)
        except CompileError as exc:
            if exc.code != "E601" or "\n- `team:" in exc.diagnostic.detail:
                raise
            skipped = exc
            continue
        rows.append(CompiledTableRow(key=member.key, cells=cells))
    if not rows and skipped is not None:
        raise skipped
    for row in block.payload.rows:
        by_key = {cell.key: cell for cell in row.cells}
        for cell in row.cells:
            if cell.key not in {column.key for column in columns}:
                raise error(f"`rows:` names unknown column `{cell.key}`.", cell)
        for column in columns:
            if column.key not in by_key:
                raise error(f"Row `{row.key}` leaves column `{column.key}` empty.", row)
        cells = tuple(
            CompiledTableCell(
                key=cell.key,
                text=None if cell.text is None else context._interpolate_authored_prose_string(
                    cell.text, unit=unit,
                    owner_label=f"roster {block.key}", surface_label="roster cell",
                ),
                body=None if cell.body is None else context._compile_section_body(
                    context._resolve_section_body_items(
                        cell.body, unit=unit, owner_label=f"roster {block.key}",
                    ),
                    unit=unit, owner_label=f"roster {block.key}",
                ),
            )
            for cell in row.cells
        )
        rows.append(CompiledTableRow(key=row.key, cells=cells))
    return CompiledTableBlock(title=block.title, table=CompiledTableData(
        columns=tuple(CompiledTableColumn(key=column.key, title=column.title, body=()) for column in columns),
        rows=tuple(rows),
    ))
