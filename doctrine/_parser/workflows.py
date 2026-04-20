from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    WorkflowLawPart,
    WorkflowBodyParts,
    _body_prose_location,
    _body_prose_value,
    _expand_grouped_inherit,
    _flatten_grouped_items,
    _item_line_column,
    _positioned_body_prose,
    _positioned_workflow_law,
    _source_span_from_meta,
    _with_source_span,
)
from doctrine.diagnostics import TransformParseFailure


class WorkflowTransformerMixin:
    """Shared workflow and workflow-law lowering for the public parser boundary."""

    @v_args(meta=True, inline=True)
    def agent_slot_field(self, meta, key, value, body=None):
        return _with_source_span(
            model.AuthoredSlotField(key=key, value=self._workflow_slot_value(value, body)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def agent_slot_abstract(self, meta, key, declared_type=None):
        return _with_source_span(
            model.AuthoredSlotAbstract(key=key, declared_type=declared_type),
            meta,
        )

    @v_args(meta=True, inline=True)
    def agent_slot_inherit(self, meta, key):
        return _with_source_span(model.AuthoredSlotInherit(key=key), meta)

    @v_args(meta=True, inline=True)
    def agent_slot_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.AuthoredSlotInherit)

    @v_args(meta=True, inline=True)
    def agent_slot_override(self, meta, key, value, body=None):
        return _with_source_span(
            model.AuthoredSlotOverride(
                key=key,
                value=self._workflow_slot_value(value, body),
            ),
            meta,
        )

    def slot_body(self, items):
        return items[0]

    @v_args(meta=True, inline=True)
    def workflow_decl(self, meta, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        workflow_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            workflow_body = body
        return _with_source_span(
            model.WorkflowDecl(
                name=name,
                body=model.WorkflowBody(
                    title=title,
                    preamble=workflow_body.preamble,
                    items=workflow_body.items,
                    law=workflow_body.law,
                ),
                parent_ref=parent_ref,
            ),
            meta,
        )

    def workflow_preamble(self, items):
        return tuple(items)

    def workflow_items(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def workflow_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def workflow_body_line(self, value):
        return value

    def workflow_body(self, items):
        preamble: list[model.ProseLine] = []
        workflow_items: list[model.WorkflowItem] = []
        law: model.LawBody | None = None
        items = _flatten_grouped_items(items)
        for item in items:
            law_body = item.body if isinstance(item, WorkflowLawPart) else item if isinstance(item, model.LawBody) else None
            if law_body is not None:
                if law is not None:
                    line, column = _item_line_column(item)
                    raise TransformParseFailure(
                        "Workflow declarations may define `law` only once.",
                        hints=("Keep exactly one `law:` block per workflow body.",),
                        line=line,
                        column=column,
                    )
                law = law_body
                continue
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if workflow_items or law is not None:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Workflow prose lines must appear before keyed workflow entries.",
                        hints=(
                            "Move prose lines to the top of the workflow body or put them inside a titled section.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            workflow_items.append(item)
        return WorkflowBodyParts(
            preamble=tuple(preamble),
            items=tuple(workflow_items),
            law=law,
        )

    def workflow_section_body(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def workflow_section_ref_item(self, meta, ref):
        if isinstance(ref, model.NameRef):
            ref = model.AddressableRef(root=ref, source_span=_source_span_from_meta(meta))
        return _with_source_span(model.SectionBodyRef(ref=ref), meta)

    @v_args(meta=True, inline=True)
    def local_section(self, meta, key, title, items):
        return _with_source_span(
            model.LocalSection(key=key, title=title, items=tuple(items)),
            meta,
        )

    @v_args(inline=True)
    def workflow_readable_block(self, value):
        return value

    @v_args(inline=True)
    def workflow_root_readable_block(self, value):
        return value

    @v_args(meta=True, inline=True)
    def workflow_section_block(self, meta, key, title, *parts):
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return _with_source_span(
            model.ReadableBlock(
                kind="section",
                key=key,
                title=title,
                payload=tuple(payload),
                requirement=requirement,
                when_expr=when_expr,
                item_schema=item_schema,
                row_schema=row_schema,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def workflow_use(self, meta, key, target):
        return _with_source_span(model.WorkflowUse(key=key, target=target), meta)

    @v_args(meta=True, inline=True)
    def workflow_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def workflow_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    @v_args(meta=True, inline=True)
    def workflow_skills_inline(self, meta, title, body):
        return _with_source_span(
            model.WorkflowSkillsItem(
                key="skills",
                value=self._skills_value(title, body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def workflow_skills_ref(self, meta, ref):
        return _with_source_span(
            model.WorkflowSkillsItem(
                key="skills",
                value=self._skills_value(ref, None),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def workflow_override_skills_inline(self, meta, title, body):
        return _with_source_span(
            model.OverrideWorkflowSkillsItem(
                key="skills",
                value=self._skills_value(title, body),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def workflow_override_skills_ref(self, meta, ref):
        return _with_source_span(
            model.OverrideWorkflowSkillsItem(
                key="skills",
                value=self._skills_value(ref, None),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def workflow_override_section(self, meta, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return _with_source_span(
            model.OverrideSection(key=key, title=title, items=tuple(section_items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def workflow_override_use(self, meta, key, target):
        return _with_source_span(model.OverrideUse(key=key, target=target), meta)

    @v_args(meta=True, inline=True)
    def law_block(self, meta, body):
        return _positioned_workflow_law(meta, body)

    @v_args(meta=True)
    def law_body(self, meta, items):
        return _with_source_span(model.LawBody(items=_flatten_grouped_items(items)), meta)

    @v_args(meta=True)
    def law_section(self, meta, items):
        return _with_source_span(
            model.LawSection(key=items[0], items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True, inline=True)
    def law_inherit(self, meta, key):
        return _with_source_span(model.LawInherit(key=key), meta)

    @v_args(meta=True, inline=True)
    def law_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.LawInherit)

    @v_args(meta=True)
    def law_override_section(self, meta, items):
        return _with_source_span(
            model.LawOverrideSection(key=items[0], items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True, inline=True)
    def active_when_stmt(self, meta, expr):
        return _with_source_span(model.ActiveWhenStmt(expr=expr), meta)

    @v_args(meta=True, inline=True)
    def mode_stmt(self, meta, name, expr, enum_ref):
        return _with_source_span(
            model.ModeStmt(name=name, expr=expr, enum_ref=enum_ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def must_stmt(self, meta, expr):
        return _with_source_span(model.MustStmt(expr=expr), meta)

    @v_args(meta=True, inline=True)
    def current_artifact_stmt(self, meta, target, carrier):
        return _with_source_span(
            model.CurrentArtifactStmt(target=target, carrier=carrier),
            meta,
        )

    @v_args(meta=True)
    def current_none_stmt(self, meta, _items):
        return _with_source_span(model.CurrentNoneStmt(), meta)

    @v_args(meta=True, inline=True)
    def own_only_stmt(self, meta, target, when_expr=None):
        return _with_source_span(
            model.OwnOnlyStmt(target=target, when_expr=when_expr),
            meta,
        )

    @v_args(meta=True)
    def preserve_stmt(self, meta, items):
        kind = items[0]
        target = items[1]
        when_expr: model.Expr | None = items[2] if len(items) > 2 else None
        return _with_source_span(
            model.PreserveStmt(kind=kind, target=target, when_expr=when_expr),
            meta,
        )

    @v_args(meta=True, inline=True)
    def support_only_stmt(self, meta, target, when_expr=None):
        return _with_source_span(
            model.SupportOnlyStmt(target=target, when_expr=when_expr),
            meta,
        )

    @v_args(meta=True)
    def ignore_stmt(self, meta, items):
        target = items[0]
        bases: tuple[str, ...] = ()
        when_expr: model.Expr | None = None
        for extra in items[1:]:
            if isinstance(extra, tuple):
                bases = extra
            else:
                when_expr = extra
        return _with_source_span(
            model.IgnoreStmt(target=target, bases=bases, when_expr=when_expr),
            meta,
        )

    @v_args(meta=True, inline=True)
    def invalidate_stmt(self, meta, target, carrier, when_expr=None):
        return _with_source_span(
            model.InvalidateStmt(target=target, carrier=carrier, when_expr=when_expr),
            meta,
        )

    @v_args(meta=True, inline=True)
    def forbid_stmt(self, meta, target, when_expr=None):
        return _with_source_span(
            model.ForbidStmt(target=target, when_expr=when_expr),
            meta,
        )

    @v_args(meta=True)
    def when_stmt(self, meta, items):
        return _with_source_span(
            model.WhenStmt(expr=items[0], items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True, inline=True)
    def match_stmt(self, meta, expr, *cases):
        return _with_source_span(model.MatchStmt(expr=expr, cases=tuple(cases)), meta)

    @v_args(meta=True)
    def match_case(self, meta, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return _with_source_span(
            model.MatchArm(head=head, items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True, inline=True)
    def route_from_stmt(self, meta, expr, enum_ref, *cases):
        return _with_source_span(
            model.RouteFromStmt(expr=expr, enum_ref=enum_ref, cases=tuple(cases)),
            meta,
        )

    @v_args(meta=True)
    def route_from_case(self, meta, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return _with_source_span(model.RouteFromArm(head=head, route=items[1]), meta)

    def else_match_head(self, _items):
        return "__ELSE__"

    @v_args(meta=True, inline=True)
    def stop_stmt(self, meta, message=None, when_expr=None):
        if message is not None and not isinstance(message, str):
            when_expr = message
            message = None
        return _with_source_span(
            model.StopStmt(message=message, when_expr=when_expr),
            meta,
        )

    @v_args(meta=True, inline=True)
    def law_route_stmt(self, meta, label, target, when_expr=None):
        return _with_source_span(
            model.LawRouteStmt(label=label, target=target, when_expr=when_expr),
            meta,
        )

    def preserve_exact(self, _items):
        return "exact"

    def preserve_structure(self, _items):
        return "structure"

    def preserve_decisions(self, _items):
        return "decisions"

    def preserve_mapping(self, _items):
        return "mapping"

    def preserve_vocabulary(self, _items):
        return "vocabulary"

    def ignore_basis_list(self, items):
        return tuple(items)

    def ignore_basis_truth(self, _items):
        return "truth"

    def ignore_basis_comparison(self, _items):
        return "comparison"

    def ignore_basis_rewrite_evidence(self, _items):
        return "rewrite_evidence"

    @v_args(inline=True)
    def law_when_clause(self, expr):
        return expr

    @v_args(meta=True)
    def path_set_expr(self, meta, items):
        paths: list[model.LawPath] = []
        except_paths: list[model.LawPath] = []
        if items:
            first = items[0]
            if isinstance(first, tuple):
                paths.extend(first)
            else:
                paths.append(first)
            for extra in items[1:]:
                if isinstance(extra, tuple):
                    except_paths.extend(extra)
                else:
                    except_paths.append(extra)
        return _with_source_span(
            model.LawPathSet(paths=tuple(paths), except_paths=tuple(except_paths)),
            meta,
        )

    def path_set_base(self, items):
        if len(items) == 1 and isinstance(items[0], model.LawPath):
            return items[0]
        return tuple(items)

    @v_args(meta=True)
    def law_path(self, meta, items):
        parts = list(items[0])
        wildcard = len(items) > 1
        return _with_source_span(
            model.LawPath(parts=tuple(parts), wildcard=wildcard),
            meta,
        )

    def law_path_wildcard(self, _items):
        return "*"
