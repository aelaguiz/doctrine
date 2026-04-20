from __future__ import annotations

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.resolved_types import IndexedUnit


class ValidateOutputStructureMixin:
    """Structural placement checks for `case` and `via` clauses."""

    def _validate_output_declaration_structure(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        self._walk_output_decl_items(
            decl.items,
            unit=unit,
            owner_label=f"output {decl.name}",
            next_owner_host=False,
        )

    def _validate_output_shape_declaration_structure(
        self,
        shape_decl: model.OutputShapeDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        self._walk_output_shape_items(
            shape_decl.items,
            unit=unit,
            owner_label=f"output shape {shape_decl.name}",
        )

    def _walk_output_decl_items(
        self,
        items: tuple[model.OutputRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        next_owner_host: bool,
    ) -> None:
        for item in items:
            if isinstance(item, model.OutputRecordCase):
                raise compile_error(
                    code="E318",
                    summary="Output `case` block outside an output shape",
                    detail=(
                        f"`case` blocks are only legal inside an output shape body, not in "
                        f"{owner_label}."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=item.source_span,
                    hints=(
                        "Move the `case` into an `output shape` declaration, or replace it "
                        "with a plain record field.",
                    ),
                )
            if isinstance(item, model.ReviewRouteVia):
                if not next_owner_host:
                    raise compile_error(
                        code="E317",
                        summary="`via review` clause outside a next_owner field",
                        detail=(
                            f"`via review.{item.section}.route` is only legal inside a "
                            f"`next_owner:` field body in {owner_label}."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=item.source_span,
                        hints=(
                            "Move the `via review.<section>.route` clause inside a "
                            "`next_owner:` scalar or section body.",
                        ),
                    )
                continue
            self._recurse_output_decl_item(
                item,
                unit=unit,
                owner_label=owner_label,
            )

    def _recurse_output_decl_item(
        self,
        item: model.OutputRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if isinstance(item, model.RecordScalar):
            if item.body is not None:
                self._walk_output_decl_items(
                    item.body,
                    unit=unit,
                    owner_label=owner_label,
                    next_owner_host=(item.key == "next_owner"),
                )
            return
        if isinstance(item, model.GuardedOutputScalar):
            if item.body is not None:
                self._walk_output_decl_items(
                    item.body,
                    unit=unit,
                    owner_label=owner_label,
                    next_owner_host=(item.key == "next_owner"),
                )
            return
        if isinstance(item, model.RecordSection):
            self._walk_output_decl_items(
                item.items,
                unit=unit,
                owner_label=owner_label,
                next_owner_host=(item.key == "next_owner"),
            )
            return
        if isinstance(item, model.GuardedOutputSection):
            self._walk_output_decl_items(
                item.items,
                unit=unit,
                owner_label=owner_label,
                next_owner_host=(item.key == "next_owner"),
            )
            return
        if isinstance(item, model.RecordRef):
            if item.body is not None:
                self._walk_output_decl_items(
                    item.body,
                    unit=unit,
                    owner_label=owner_label,
                    next_owner_host=False,
                )
            return

    def _walk_output_shape_items(
        self,
        items: tuple[model.OutputRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        for item in items:
            if isinstance(item, model.ReviewRouteVia):
                raise compile_error(
                    code="E317",
                    summary="`via review` clause inside an output shape",
                    detail=(
                        f"`via review.{item.section}.route` is only legal inside a "
                        f"`next_owner:` field on an output declaration, not inside "
                        f"{owner_label}."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=item.source_span,
                    hints=(
                        "Move the `via review.<section>.route` clause onto a concrete "
                        "`output` declaration's `next_owner:` field.",
                    ),
                )
            if isinstance(item, model.OutputRecordCase):
                self._walk_output_shape_items(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                )
                continue
            self._recurse_output_shape_item(
                item,
                unit=unit,
                owner_label=owner_label,
            )

    def _recurse_output_shape_item(
        self,
        item: model.OutputRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if isinstance(item, model.RecordScalar):
            if item.body is not None:
                self._walk_output_shape_items(
                    item.body,
                    unit=unit,
                    owner_label=owner_label,
                )
            return
        if isinstance(item, model.GuardedOutputScalar):
            if item.body is not None:
                self._walk_output_shape_items(
                    item.body,
                    unit=unit,
                    owner_label=owner_label,
                )
            return
        if isinstance(item, model.RecordSection):
            self._walk_output_shape_items(
                item.items,
                unit=unit,
                owner_label=owner_label,
            )
            return
        if isinstance(item, model.GuardedOutputSection):
            self._walk_output_shape_items(
                item.items,
                unit=unit,
                owner_label=owner_label,
            )
            return
        if isinstance(item, model.RecordRef):
            if item.body is not None:
                self._walk_output_shape_items(
                    item.body,
                    unit=unit,
                    owner_label=owner_label,
                )
            return
