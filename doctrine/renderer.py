from __future__ import annotations

from doctrine._compiler.types import (
    CompiledAgent,
    CompiledBodyItem,
    CompiledBulletsBlock,
    CompiledCalloutBlock,
    CompiledChecklistBlock,
    CompiledCodeBlock,
    CompiledDefinitionsBlock,
    CompiledFootnotesBlock,
    CompiledGuardBlock,
    CompiledImageBlock,
    CompiledPropertiesBlock,
    CompiledRawTextBlock,
    CompiledReadableBlock,
    CompiledRuleBlock,
    CompiledSection,
    CompiledSequenceBlock,
    CompiledTableBlock,
    ResolvedRenderProfile,
)
from doctrine.model import EmphasizedLine, ReadableInlineSchemaData, RoleScalar


_DEFAULT_PROFILE = ResolvedRenderProfile(name="ContractMarkdown")
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


def _render_block(
    block: CompiledReadableBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> str:
    if isinstance(block, CompiledSection):
        active_profile = block.render_profile or profile
        semantic_render = _render_semantic_section(
            block,
            depth=depth,
            profile=active_profile,
        )
        if semantic_render is not None:
            return semantic_render
        return _render_titled_block(
            block.title,
            block.body,
            depth=depth,
            profile=active_profile,
            metadata=_render_metadata_line(
                requirement=block.requirement,
                kind_label="section" if block.emit_metadata else None,
                when_text=block.when_text,
            ),
        )
    if isinstance(block, CompiledSequenceBlock):
        return _render_list_block(block, depth=depth, profile=profile, marker="1.")
    if isinstance(block, CompiledBulletsBlock):
        return _render_list_block(block, depth=depth, profile=profile, marker="-")
    if isinstance(block, CompiledChecklistBlock):
        return _render_list_block(block, depth=depth, profile=profile, marker="- [ ]")
    if isinstance(block, CompiledDefinitionsBlock):
        return _render_definitions_block(block, depth=depth, profile=profile)
    if isinstance(block, CompiledPropertiesBlock):
        return _render_properties_block(block, depth=depth, profile=profile)
    if isinstance(block, CompiledTableBlock):
        return _render_table_block(block, depth=depth, profile=profile)
    if isinstance(block, CompiledCalloutBlock):
        return _render_callout_block(block, profile=profile)
    if isinstance(block, CompiledCodeBlock):
        return _render_code_block(block, depth=depth)
    if isinstance(block, CompiledRawTextBlock):
        return _render_raw_text_block(block, depth=depth)
    if isinstance(block, CompiledFootnotesBlock):
        return _render_footnotes_block(block, depth=depth, profile=profile)
    if isinstance(block, CompiledImageBlock):
        return _render_image_block(block, depth=depth)
    if isinstance(block, CompiledGuardBlock):
        return _render_guard_block(block, depth=depth, profile=profile)
    if isinstance(block, CompiledRuleBlock):
        return _render_rule_block(block)
    raise TypeError(f"Unsupported compiled readable block: {type(block).__name__}")


def _render_titled_block(
    title: str,
    body: tuple[CompiledBodyItem, ...],
    *,
    depth: int,
    profile: ResolvedRenderProfile,
    line_prefix: str = "",
    metadata: str | None = None,
) -> str:
    lines = [f"{'#' * depth} {title}"]
    body_lines = _render_body_lines(
        body,
        depth=depth,
        profile=profile,
        line_prefix=line_prefix,
    )

    if metadata is not None:
        if body_lines:
            body_lines = [metadata, "", *body_lines]
        else:
            body_lines = [metadata]

    if not body_lines:
        return "\n".join(lines)

    return "\n".join([*lines, "", *body_lines]).rstrip()


def _render_body_lines(
    body: tuple[CompiledBodyItem, ...],
    *,
    depth: int,
    profile: ResolvedRenderProfile,
    line_prefix: str = "",
) -> list[str]:
    body_lines: list[str] = []
    previous_was_block = False
    analysis_stage_counter = 1

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
        if (
            isinstance(item, CompiledSection)
            and item.semantic_target == "analysis.stages"
            and _resolve_profile_mode(profile, "analysis.stages") == "natural_ordered_prose"
        ):
            if body_lines and body_lines[-1] != "":
                body_lines.append("")
            stage_lines = _render_analysis_stage_lines(
                item,
                index=analysis_stage_counter,
                profile=profile,
            )
            analysis_stage_counter += 1
            if line_prefix:
                stage_lines = [f"{line_prefix}{line}" if line else line for line in stage_lines]
            body_lines.extend(stage_lines)
            previous_was_block = True
            continue

        if body_lines and body_lines[-1] != "":
            body_lines.append("")
        nested = _render_block(item, depth=depth + 1, profile=profile).splitlines()
        if line_prefix:
            nested = [f"{line_prefix}{line}" if line else line for line in nested]
        body_lines.extend(nested)
        previous_was_block = True

    while body_lines and body_lines[-1] == "":
        body_lines.pop()
    return body_lines


def _render_list_block(
    block: CompiledSequenceBlock | CompiledBulletsBlock | CompiledChecklistBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
    marker: str,
) -> str:
    if (
        block.semantic_target == "control.invalidations"
        and _resolve_profile_mode(profile, "control.invalidations") == "sentence"
    ):
        rendered_items = [_render_prose_line(item, profile=profile) for item in block.items]
        if not rendered_items:
            return block.title
        return f"{block.title}: {'; '.join(rendered_items)}"

    kind_label = {
        CompiledSequenceBlock: "ordered list",
        CompiledBulletsBlock: "unordered list",
        CompiledChecklistBlock: "checklist",
    }[type(block)]
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label=kind_label,
        when_text=block.when_text,
    )
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])

    schema_lines = _render_inline_schema("Item Schema", block.item_schema, profile=profile)
    if schema_lines:
        lines.extend(schema_lines)
        lines.append("")

    rendered_items: list[str] = []
    counter = 1
    for item in block.items:
        current_marker = marker
        if marker == "1.":
            current_marker = f"{counter}."
            counter += 1
        rendered_items.append(f"{current_marker} {_render_prose_line(item, profile=profile)}")

    if not rendered_items:
        return "\n".join(lines).rstrip()
    return "\n".join([*lines, *rendered_items]).rstrip()


def _render_properties_block(
    block: CompiledPropertiesBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> str:
    rendered_entries = _render_property_entries(block.entries, profile=profile)
    if not rendered_entries:
        return ""

    mode = _resolve_profile_mode(profile, "properties")
    if block.title is not None and mode == "titled_section":
        return _render_titled_block(
            block.title,
            tuple(rendered_entries),
            depth=depth,
            profile=profile,
            metadata=_render_metadata_line(
                requirement=block.requirement,
                kind_label="properties",
                when_text=block.when_text,
            ),
        )

    if block.title is not None and mode is None and profile.name == "ContractMarkdown" and not block.anonymous:
        return _render_titled_block(
            block.title,
            tuple(rendered_entries),
            depth=depth,
            profile=profile,
            metadata=_render_metadata_line(
                requirement=block.requirement,
                kind_label="properties",
                when_text=block.when_text,
            ),
        )

    return "\n".join(rendered_entries).rstrip()


def _render_semantic_section(
    block: CompiledSection,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> str | None:
    if (
        block.semantic_target == "review.contract_checks"
        and _resolve_profile_mode(profile, "review.contract_checks") == "sentence"
    ):
        text = _flatten_body_to_sentence(block.body, profile=profile)
        if text is not None:
            return f"{block.title}: {text}"
    return None


def _flatten_body_to_sentence(
    body: tuple[CompiledBodyItem, ...],
    *,
    profile: ResolvedRenderProfile,
) -> str | None:
    parts: list[str] = []
    for item in body:
        if item == "":
            continue
        if isinstance(item, (str, EmphasizedLine)):
            parts.append(_render_prose_line(item, profile=profile))
            continue
        return None
    return " ".join(part.strip() for part in parts if part.strip()) or None


def _render_analysis_stage_lines(
    block: CompiledSection,
    *,
    index: int,
    profile: ResolvedRenderProfile,
) -> list[str]:
    intro = _flatten_body_to_sentence(block.body, profile=profile)
    head = f"{index}. **{block.title}**"
    if intro is not None:
        return [f"{head} — {intro}"]

    lines = [head]
    rendered_body = _render_body_lines(block.body, depth=0, profile=profile, line_prefix="   ")
    lines.extend(rendered_body)
    return lines


def _render_property_entries(
    entries: tuple,
    *,
    profile: ResolvedRenderProfile,
) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        if not entry.body:
            lines.append(f"- {entry.title}")
            continue
        first, *rest = entry.body
        first_text = _render_prose_line(first, profile=profile)
        if first_text:
            lines.append(f"- {entry.title}: {first_text}")
        else:
            lines.append(f"- {entry.title}")
        for line in rest:
            lines.append(f"  {_render_prose_line(line, profile=profile)}")
    return lines


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
    return "\n".join(lines).rstrip()


def _render_raw_text_block(block: CompiledRawTextBlock, *, depth: int) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label=block.kind,
        when_text=block.when_text,
    )
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])
    lines.extend(block.text.splitlines())
    return "\n".join(lines).rstrip()


def _render_rule_block(block: CompiledRuleBlock) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="rule",
        when_text=block.when_text,
    )
    if metadata is None:
        return "---"
    return f"{metadata}\n\n---"


def _render_definitions_block(
    block: CompiledDefinitionsBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> str:
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
        first_text = _render_prose_line(first, profile=profile)
        if rest:
            lines.append(f"- **{item.title}**")
            lines.append(f"  {first_text}")
            for line in rest:
                lines.append(f"  {_render_prose_line(line, profile=profile)}")
            continue
        lines.append(f"- **{item.title}** — {first_text}")
    return "\n".join(lines).rstrip()


def _render_table_block(
    block: CompiledTableBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="table",
        when_text=block.when_text,
    )
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])

    schema_lines = _render_inline_schema("Row Schema", block.table.row_schema, profile=profile)
    if schema_lines:
        lines.extend(schema_lines)
        lines.append("")

    if any(cell.body is not None for row in block.table.rows for cell in row.cells):
        lines.extend(_render_structured_table(block, depth=depth, profile=profile))
    elif block.table.rows:
        lines.extend(_render_pipe_table(block))
    else:
        lines.append("| Column | Meaning |")
        lines.append("| --- | --- |")
        for column in block.table.columns:
            meaning = " ".join(_render_prose_line(line, profile=profile) for line in column.body).strip()
            lines.append(f"| {column.title} | {meaning} |")

    if block.table.notes:
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend(_render_prose_line(note, profile=profile) for note in block.table.notes)

    return "\n".join(lines).rstrip()


def _render_pipe_table(block: CompiledTableBlock) -> list[str]:
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


def _render_structured_table(
    block: CompiledTableBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> list[str]:
    lines: list[str] = []
    for row in block.table.rows:
        if lines:
            lines.append("")
        lines.append(f"{'#' * (depth + 1)} {_humanize_key(row.key)}")
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
            lines.extend(_render_body_lines(cell.body, depth=depth + 2, profile=profile))
            lines.append("")
        while lines and lines[-1] == "":
            lines.pop()
    return lines


def _render_callout_block(block: CompiledCalloutBlock, *, profile: ResolvedRenderProfile) -> str:
    label = (block.kind or "note").upper()
    title = f"{label} — {block.title}" if block.title else label
    lines = [f"> **{title}**"]
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="callout",
        when_text=block.when_text,
    )
    if metadata is not None:
        lines.append(f"> {metadata}")
    for line in block.body:
        text = _render_prose_line(line, profile=profile)
        lines.append(f"> {text}" if text else ">")
    return "\n".join(lines).rstrip()


def _render_guard_block(
    block: CompiledGuardBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> str:
    mode = _resolve_profile_mode(profile, "guarded_sections", "guard")
    if mode == "concise_explanatory_shell":
        lines = [f"_Show this only when {block.when_text}._"]
        body_lines = _render_body_lines(block.body, depth=depth, profile=profile)
        if body_lines:
            lines.extend(["", *body_lines])
        return "\n".join(lines).rstrip()

    return _render_titled_block(
        block.title or "Condition",
        block.body,
        depth=depth,
        profile=profile,
        metadata=_render_metadata_line(
            requirement=None,
            kind_label="guard",
            when_text=block.when_text,
        ),
    )


def _render_footnotes_block(
    block: CompiledFootnotesBlock,
    *,
    depth: int,
    profile: ResolvedRenderProfile,
) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="footnotes",
        when_text=block.when_text,
    )
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])
    for entry in block.entries:
        lines.append(f"[^{entry.key}]: {_render_prose_line(entry.text, profile=profile)}")
    return "\n".join(lines).rstrip()


def _render_image_block(block: CompiledImageBlock, *, depth: int) -> str:
    metadata = _render_metadata_line(
        requirement=block.requirement,
        kind_label="image",
        when_text=block.when_text,
    )
    lines = [f"{'#' * depth} {block.title}", ""]
    if metadata is not None:
        lines.extend([metadata, ""])
    lines.append(f"![{block.alt}]({block.src})")
    if block.caption:
        lines.extend(["", block.caption])
    return "\n".join(lines).rstrip()


def _render_inline_schema(
    label: str,
    schema: ReadableInlineSchemaData | None,
    *,
    profile: ResolvedRenderProfile,
) -> list[str]:
    if schema is None or profile.name != "ContractMarkdown":
        return []
    lines = [f"_{label}_"]
    for entry in schema.entries:
        if not entry.body:
            lines.append(f"- {entry.title}")
            continue
        first, *rest = entry.body
        first_text = _render_prose_line(first, profile=profile)
        if first_text:
            lines.append(f"- {entry.title}: {first_text}")
        else:
            lines.append(f"- {entry.title}")
        for line in rest:
            lines.append(f"  {_render_prose_line(line, profile=profile)}")
    return lines


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


def _render_prose_line(item: CompiledBodyItem, *, profile: ResolvedRenderProfile) -> str:
    if isinstance(item, EmphasizedLine):
        return f"**{item.kind.upper()}**: {item.text}"
    if isinstance(item, str):
        return item
    return _render_block(item, depth=0, profile=profile)


def _resolve_profile_mode(profile: ResolvedRenderProfile, *targets: str) -> str | None:
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


def _humanize_key(value: str) -> str:
    return value.replace("_", " ").strip().title()
