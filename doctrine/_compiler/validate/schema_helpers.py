from __future__ import annotations

import json

from doctrine import model
from doctrine.project_config import project_file_path
from doctrine._compiler.authored_diagnostics import authored_compile_error
from doctrine._compiler.constants import _INTERPOLATION_RE
from doctrine._compiler.provenance import render_inline_quotes
from doctrine._compiler.naming import _name_ref_from_dotted_name
from doctrine._compiler.source_graph import declaration_match
from doctrine._compiler.readable_diagnostics import invalid_readable_block_error
from doctrine._compiler.resolved_types import (
    IndexedUnit,
    ResolvedRenderProfile,
    ResolvedSchemaArtifact,
    ResolvedSchemaGroup,
    ReviewSemanticContext,
    RouteSemanticContext,
)


class ValidateSchemaHelpersMixin:
    """Schema and interpolation helpers for ValidateMixin."""

    def _schema_body_item(
        self,
        items: tuple[model.SchemaItem, ...],
        *,
        block_key: str,
    ) -> model.SchemaItem | None:
        for item in items:
            if isinstance(item, model.InheritItem) and item.key == block_key:
                return item
            if block_key == "sections" and isinstance(item, model.SchemaSectionsBlock):
                return item
            if block_key == "gates" and isinstance(item, model.SchemaGatesBlock):
                return item
            if block_key == "artifacts" and isinstance(item, model.SchemaArtifactsBlock):
                return item
            if block_key == "groups" and isinstance(item, model.SchemaGroupsBlock):
                return item
            if block_key == "sections" and isinstance(item, model.SchemaOverrideSectionsBlock):
                return item
            if block_key == "gates" and isinstance(item, model.SchemaOverrideGatesBlock):
                return item
            if block_key == "artifacts" and isinstance(item, model.SchemaOverrideArtifactsBlock):
                return item
            if block_key == "groups" and isinstance(item, model.SchemaOverrideGroupsBlock):
                return item
        return None

    def _schema_body_action(
        self,
        items: tuple[model.SchemaItem, ...],
        *,
        block_key: str,
    ) -> tuple[str | None, tuple[object, ...]]:
        item = self._schema_body_item(items, block_key=block_key)
        if isinstance(item, model.InheritItem):
            return "inherit", ()
        if isinstance(
            item,
            (
                model.SchemaSectionsBlock,
                model.SchemaGatesBlock,
                model.SchemaArtifactsBlock,
                model.SchemaGroupsBlock,
            ),
        ):
            return "define", item.items
        if isinstance(
            item,
            (
                model.SchemaOverrideSectionsBlock,
                model.SchemaOverrideGatesBlock,
                model.SchemaOverrideArtifactsBlock,
                model.SchemaOverrideGroupsBlock,
            ),
        ):
            return "override", item.items
        return None, ()

    def _validate_schema_group_members(
        self,
        groups: tuple[ResolvedSchemaGroup, ...],
        *,
        artifacts: tuple[ResolvedSchemaArtifact, ...],
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        artifact_keys = {item.key for item in artifacts}
        for group in groups:
            for member_key in group.members:
                if member_key not in artifact_keys:
                    raise authored_compile_error(
                        code="E303",
                        summary="Invalid schema declaration",
                        detail=(
                            f"Unknown schema group member in {owner_label}: "
                            f"{group.key}.{member_key}"
                        ),
                        unit=unit,
                        source_span=group.source_span,
                    )

    def _require_tuple_payload(
        self,
        payload: model.ReadablePayload,
        *,
        owner_label: str,
        kind: str,
        unit: IndexedUnit,
        source_span: model.SourceSpan | None,
    ) -> tuple[object, ...]:
        if not isinstance(payload, tuple):
            raise invalid_readable_block_error(
                detail=f"Readable {kind} payload must stay block-shaped in {owner_label}.",
                unit=unit,
                source_span=source_span,
            )
        return payload

    def _interpolate_authored_prose_string(
        self,
        value: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        if isinstance(value, model.MarkdownProse):
            return value
        if "{{" not in value and "}}" not in value:
            return value

        value = render_inline_quotes(self, unit, value)
        parts: list[str] = []
        cursor = 0
        for match in _INTERPOLATION_RE.finditer(value):
            between = value[cursor:match.start()]
            if "{{" in between or "}}" in between:
                raise authored_compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Malformed interpolation in {owner_label}: {value}",
                    unit=unit,
                    source_span=None,
                )
            parts.append(between)
            expression = match.group(1).strip()
            name, separator, projection = expression.partition(":")
            is_load = name == "load" and bool(separator)
            ref_name = projection if is_load else name
            file_match = declaration_match(self, _name_ref_from_dotted_name(ref_name), unit)
            if file_match is not None and isinstance(file_match[1], model.FileDecl) and (
                is_load or not separator or projection == "title"
            ):
                file_unit, file_decl = self._resolve_addressable_root_decl(
                    _name_ref_from_dotted_name(ref_name), unit=unit, owner_label=owner_label,
                    ambiguous_label=ambiguous_label or surface_label,
                    missing_local_label=surface_label,
                )
                if self._active_skill_package_host_context() is not None:
                    raise authored_compile_error(code="E655", summary="File ref can't go here",
                        detail=f"A skill package has no home to link from, so it can't read `{{{{{ref_name}}}}}`.", unit=unit, source_span=None)
                if is_load and value[match.end():].split("\n", 1)[0].strip():
                    raise authored_compile_error(code="E655", summary="File ref can't go here",
                        detail=f"`{{{{load:{ref_name}}}}}` must end its line.", unit=unit, source_span=None)
                if is_load and any(c.isspace() for c in file_decl.path):
                    raise authored_compile_error(code="E655", summary="File ref can't go here",
                        detail=f"`{{{{load:{ref_name}}}}}` can't load `{file_decl.path}`, because an import path ends at a space. Rename the file.", unit=unit, source_span=None)
                base = self.session.emit_root if file_decl.body is not None else self.session.project_config.config_dir
                path = ((base / file_decl.path).resolve() if file_decl.body is not None
                        else project_file_path(self.session.project_config, file_decl.path))
                if file_decl.body is None and not path.is_file():
                    raise authored_compile_error(code="E652", summary="Missing Markdown source",
                        detail=f"`{file_decl.name}` names `{file_decl.path}`, which doesn't exist.", unit=file_unit, source_span=file_decl.source_span)
                parts.append(file_decl.title if projection == "title" and not is_load else
                    "\x1e" + json.dumps(["load" if is_load else "link", file_decl.title, str(path), None]) + "\x1f")
                cursor = match.end()
                continue
            parts.append(
                self._resolve_authored_prose_interpolation_expr(
                    match.group(1),
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    ambiguous_label=ambiguous_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
            cursor = match.end()

        tail = value[cursor:]
        if "{{" in tail or "}}" in tail:
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"Malformed interpolation in {owner_label}: {value}",
                unit=unit,
                source_span=None,
            )
        parts.append(tail)
        return "".join(parts)

    def _interpolate_authored_prose_line(
        self,
        value: model.ProseLine,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ProseLine:
        if isinstance(value, model.SuperItem):
            return value
        if isinstance(value, str):
            if isinstance(value, model.MarkdownProse):
                return value
            text = self._interpolate_authored_prose_string(
                value,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if sum(line.strip().startswith("```") for line in text.splitlines()) % 2:
                raise authored_compile_error(
                    code="E605",
                    summary="Code fence split across strings",
                    detail=f"A string in {owner_label} opens a code fence it doesn't close.",
                    unit=unit,
                    source_span=None,
                    hints=('Put the whole fence in one `"""` string, or use a `code` block.',),
                )
            return model.AuthoredProse(text)
        return model.EmphasizedLine(
            kind=value.kind,
            text=self._interpolate_authored_prose_string(
                value.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            ),
        )
