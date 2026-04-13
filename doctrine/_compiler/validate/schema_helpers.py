from __future__ import annotations

from doctrine._compiler.constants import _INTERPOLATION_RE
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class ValidateSchemaHelpersMixin:
    """Schema and interpolation helpers for ValidateMixin."""

    def _schema_body_action(
        self,
        items: tuple[model.SchemaItem, ...],
        *,
        block_key: str,
    ) -> tuple[str | None, tuple[object, ...]]:
        for item in items:
            if isinstance(item, model.InheritItem) and item.key == block_key:
                return "inherit", ()
            if block_key == "sections" and isinstance(item, model.SchemaSectionsBlock):
                return "define", item.items
            if block_key == "gates" and isinstance(item, model.SchemaGatesBlock):
                return "define", item.items
            if block_key == "artifacts" and isinstance(item, model.SchemaArtifactsBlock):
                return "define", item.items
            if block_key == "groups" and isinstance(item, model.SchemaGroupsBlock):
                return "define", item.items
            if block_key == "sections" and isinstance(item, model.SchemaOverrideSectionsBlock):
                return "override", item.items
            if block_key == "gates" and isinstance(item, model.SchemaOverrideGatesBlock):
                return "override", item.items
            if block_key == "artifacts" and isinstance(item, model.SchemaOverrideArtifactsBlock):
                return "override", item.items
            if block_key == "groups" and isinstance(item, model.SchemaOverrideGroupsBlock):
                return "override", item.items
        return None, ()

    def _validate_schema_group_members(
        self,
        groups: tuple[ResolvedSchemaGroup, ...],
        *,
        artifacts: tuple[ResolvedSchemaArtifact, ...],
        owner_label: str,
    ) -> None:
        artifact_keys = {item.key for item in artifacts}
        for group in groups:
            for member_key in group.members:
                if member_key not in artifact_keys:
                    raise CompileError(
                        f"Unknown schema group member in {owner_label}: {group.key}.{member_key}"
                    )

    def _require_tuple_payload(
        self,
        payload: model.ReadablePayload,
        *,
        owner_label: str,
        kind: str,
    ) -> tuple[object, ...]:
        if not isinstance(payload, tuple):
            raise CompileError(f"Readable {kind} payload must stay block-shaped in {owner_label}")
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
        if "{{" not in value and "}}" not in value:
            return value

        parts: list[str] = []
        cursor = 0
        for match in _INTERPOLATION_RE.finditer(value):
            between = value[cursor:match.start()]
            if "{{" in between or "}}" in between:
                raise CompileError(f"Malformed interpolation in {owner_label}: {value}")
            parts.append(between)
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
            raise CompileError(f"Malformed interpolation in {owner_label}: {value}")
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
        if isinstance(value, str):
            return self._interpolate_authored_prose_string(
                value,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
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
