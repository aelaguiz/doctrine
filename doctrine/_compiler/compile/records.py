from __future__ import annotations

from doctrine import model
from doctrine._compiler.authored_diagnostics import (
    authored_compile_error,
    authored_related_site,
)
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.naming import _dotted_ref_name, _humanize_key
from doctrine._compiler.resolved_types import (
    CompiledBodyItem,
    CompiledSection,
    ConfigSpec,
    IndexedUnit,
    ResolvedRenderProfile,
    ReviewSemanticContext,
    RouteSemanticContext,
)


class CompileRecordsMixin:
    """Record and config compile helpers for CompilationContext."""

    def _render_compact_record_item_line(
        self,
        item: model.AnyRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str | None:
        if isinstance(item, model.RecordSection):
            summary = self._flatten_output_record_items(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if summary is None:
                return None
            return f"- {item.title}: {summary}"

        if isinstance(item, model.GuardedOutputSection):
            summary = self._flatten_output_record_items(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=self._narrow_route_semantics(
                    route_semantics,
                    item.when_expr,
                    unit=unit,
                ),
                render_profile=render_profile,
            )
            if summary is None:
                return None
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            return f"- {item.title}: Show this only when {condition}. {summary}"

        if isinstance(item, model.RecordScalar):
            label = _humanize_key(item.key)
            if item.body is None:
                summary = self._format_scalar_value(
                    item.value,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            else:
                summary = self._flatten_output_record_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            if summary is None:
                return None
            return f"- {label}: {summary}"

        if isinstance(item, model.GuardedOutputScalar):
            guarded_route_semantics = self._narrow_route_semantics(
                route_semantics,
                item.when_expr,
                unit=unit,
            )
            label = _humanize_key(item.key)
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            parts = [f"Show this only when {condition}."]
            parts.append(
                self._format_scalar_value(
                    item.value,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=guarded_route_semantics,
                    render_profile=render_profile,
                )
            )
            if item.body is not None:
                summary = self._flatten_output_record_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=guarded_route_semantics,
                    render_profile=render_profile,
                )
                if summary is None:
                    return None
                parts.append(summary)
            return f"- {label}: {' '.join(part for part in parts if part).strip()}"

        return None

    def _compile_record_support_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            body.extend(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
        return tuple(body)

    def _compile_record_item(
        self,
        item: model.AnyRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return (
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                ),
            )

        if isinstance(item, model.RecordSection):
            return (
                CompiledSection(
                    title=item.title,
                    body=self._compile_record_support_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label=surface_label,
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                    ),
                ),
            )

        if isinstance(item, model.ReadableBlock):
            return (
                self._compile_authored_readable_block(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                    section_body_compiler=lambda payload, nested_owner_label: self._compile_record_support_items(
                        payload,
                        unit=unit,
                        owner_label=nested_owner_label,
                        surface_label=surface_label,
                        review_semantics=review_semantics,
                        route_semantics=self._narrow_route_semantics(
                            route_semantics,
                            item.when_expr,
                            unit=unit,
                        ) if item.when_expr is not None else route_semantics,
                        render_profile=render_profile,
                    ),
                ),
            )

        if isinstance(item, model.GuardedOutputSection):
            guarded_route_semantics = self._narrow_route_semantics(
                route_semantics,
                item.when_expr,
                unit=unit,
            )
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            body: list[CompiledBodyItem] = [f"Show this only when {condition}."]
            compiled_items = self._compile_record_support_items(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=guarded_route_semantics,
                render_profile=render_profile,
            )
            if compiled_items:
                body.append("")
                body.extend(compiled_items)
            return (CompiledSection(title=item.title, body=tuple(body)),)

        if isinstance(item, model.GuardedOutputScalar):
            guarded_route_semantics = self._narrow_route_semantics(
                route_semantics,
                item.when_expr,
                unit=unit,
            )
            label = _humanize_key(item.key)
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            value = self._format_scalar_value(
                item.value,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=guarded_route_semantics,
                render_profile=render_profile,
            )
            body: list[CompiledBodyItem] = [f"Show this only when {condition}.", "", value]
            if item.body is not None:
                compiled_items = self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=guarded_route_semantics,
                    render_profile=render_profile,
                )
                if compiled_items:
                    body.append("")
                    body.extend(compiled_items)
            return (CompiledSection(title=label, body=tuple(body)),)

        if isinstance(item, model.RecordScalar):
            return self._compile_fallback_scalar(
                item,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )

        if isinstance(item, model.RecordRef):
            body = (
                self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
                if item.body is not None
                else ()
            )
            return (
                CompiledSection(
                    title=self._display_ref(item.ref, unit=unit),
                    body=body,
                ),
            )

        raise compile_error(
            code="E901",
            summary="Internal compiler error",
            detail=f"Internal compiler error: unsupported record item `{type(item).__name__}`",
            path=unit.prompt_file.source_path,
            source_span=getattr(item, "source_span", None),
        )

    def _compile_fallback_scalar(
        self,
        item: model.RecordScalar,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        label = _humanize_key(item.key)
        value = self._format_scalar_value(
            item.value,
            unit=unit,
            owner_label=f"{owner_label}.{item.key}",
            surface_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )
        if item.body is None:
            return (f"- {label}: {value}",)

        body: list[CompiledBodyItem] = [value]
        body.extend(
            self._compile_record_support_items(
                item.body,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        )
        return (CompiledSection(title=label, body=tuple(body)),)

    def _compile_config_lines(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
        owner_source_span: model.SourceSpan | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        seen_keys: dict[str, model.RecordScalar] = {}
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise authored_compile_error(
                    code="E230",
                    summary="Config entries must be scalar key/value lines",
                    detail=f"Config entries must be scalar key/value lines in `{owner_label}`.",
                    unit=unit,
                    source_span=getattr(item, "source_span", None) or owner_source_span,
                )
            first_item = seen_keys.get(item.key)
            if first_item is not None:
                raise authored_compile_error(
                    code="E231",
                    summary="Duplicate config key",
                    detail=f"Config owner `{owner_label}` repeats key `{item.key}`.",
                    unit=unit,
                    source_span=item.source_span or owner_source_span,
                    related=(
                        authored_related_site(
                            label=f"first `{item.key}` config entry",
                            unit=unit,
                            source_span=first_item.source_span,
                        ),
                    ),
                )
            seen_keys[item.key] = item
            if item.key not in allowed_keys:
                raise authored_compile_error(
                    code="E232",
                    summary="Unknown config key",
                    detail=f"Config owner `{owner_label}` uses unknown key `{item.key}`.",
                    unit=unit,
                    source_span=item.source_span or owner_source_span,
                )
            body.append(
                f"- {allowed_keys[item.key]}: {self._format_scalar_value(item.value, unit=unit, owner_label=f'{owner_label}.{item.key}', surface_label='config values')}"
            )

        missing_required = [
            key for key in spec.required_keys if key not in seen_keys
        ]
        if missing_required:
            missing = ", ".join(missing_required)
            raise authored_compile_error(
                code="E233",
                summary="Missing required config key",
                detail=f"Config owner `{owner_label}` is missing required key `{missing}`.",
                unit=unit,
                source_span=owner_source_span,
            )

        return tuple(body)
