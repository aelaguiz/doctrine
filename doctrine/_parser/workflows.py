from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    WorkflowLawPart,
    WorkflowBodyParts,
    _body_prose_location,
    _body_prose_value,
    _item_line_column,
    _positioned_body_prose,
    _positioned_workflow_law,
)
from doctrine.diagnostics import TransformParseFailure


class WorkflowTransformerMixin:
    """Shared workflow and workflow-law lowering for the public parser boundary."""

    @v_args(inline=True)
    def agent_slot_field(self, key, value, body=None):
        return model.AuthoredSlotField(key=key, value=self._workflow_slot_value(value, body))

    @v_args(inline=True)
    def agent_slot_abstract(self, key):
        return model.AuthoredSlotAbstract(key=key)

    @v_args(inline=True)
    def agent_slot_inherit(self, key):
        return model.AuthoredSlotInherit(key=key)

    @v_args(inline=True)
    def agent_slot_override(self, key, value, body=None):
        return model.AuthoredSlotOverride(
            key=key,
            value=self._workflow_slot_value(value, body),
        )

    def slot_body(self, items):
        return items[0]

    @v_args(inline=True)
    def workflow_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        workflow_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            workflow_body = body
        return model.WorkflowDecl(
            name=name,
            body=model.WorkflowBody(
                title=title,
                preamble=workflow_body.preamble,
                items=workflow_body.items,
                law=workflow_body.law,
            ),
            parent_ref=parent_ref,
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

    @v_args(inline=True)
    def workflow_section_ref_item(self, ref):
        if isinstance(ref, model.NameRef):
            ref = model.AddressableRef(root=ref)
        return model.SectionBodyRef(ref=ref)

    @v_args(inline=True)
    def local_section(self, key, title, items):
        return model.LocalSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def workflow_readable_block(self, value):
        return value

    @v_args(inline=True)
    def workflow_root_readable_block(self, value):
        return value

    @v_args(inline=True)
    def workflow_section_block(self, key, title, *parts):
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return model.ReadableBlock(
            kind="section",
            key=key,
            title=title,
            payload=tuple(payload),
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )

    @v_args(inline=True)
    def workflow_use(self, key, target):
        return model.WorkflowUse(key=key, target=target)

    @v_args(inline=True)
    def workflow_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def workflow_skills_inline(self, title, body):
        return model.WorkflowSkillsItem(
            key="skills",
            value=self._skills_value(title, body),
        )

    @v_args(inline=True)
    def workflow_skills_ref(self, ref):
        return model.WorkflowSkillsItem(
            key="skills",
            value=self._skills_value(ref, None),
        )

    @v_args(inline=True)
    def workflow_override_skills_inline(self, title, body):
        return model.OverrideWorkflowSkillsItem(
            key="skills",
            value=self._skills_value(title, body),
        )

    @v_args(inline=True)
    def workflow_override_skills_ref(self, ref):
        return model.OverrideWorkflowSkillsItem(
            key="skills",
            value=self._skills_value(ref, None),
        )

    @v_args(inline=True)
    def workflow_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideSection(key=key, title=title, items=tuple(section_items))

    @v_args(inline=True)
    def workflow_override_use(self, key, target):
        return model.OverrideUse(key=key, target=target)

    @v_args(meta=True, inline=True)
    def law_block(self, meta, body):
        return _positioned_workflow_law(meta, body)

    def law_body(self, items):
        return model.LawBody(items=tuple(items))

    def law_section(self, items):
        return model.LawSection(key=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def law_inherit(self, key):
        return model.LawInherit(key=key)

    def law_override_section(self, items):
        return model.LawOverrideSection(key=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def active_when_stmt(self, expr):
        return model.ActiveWhenStmt(expr=expr)

    @v_args(inline=True)
    def mode_stmt(self, name, expr, enum_ref):
        return model.ModeStmt(name=name, expr=expr, enum_ref=enum_ref)

    @v_args(inline=True)
    def must_stmt(self, expr):
        return model.MustStmt(expr=expr)

    @v_args(inline=True)
    def current_artifact_stmt(self, target, carrier):
        return model.CurrentArtifactStmt(target=target, carrier=carrier)

    def current_none_stmt(self, _items):
        return model.CurrentNoneStmt()

    @v_args(inline=True)
    def own_only_stmt(self, target, when_expr=None):
        return model.OwnOnlyStmt(target=target, when_expr=when_expr)

    def preserve_stmt(self, items):
        kind = items[0]
        target = items[1]
        when_expr: model.Expr | None = items[2] if len(items) > 2 else None
        return model.PreserveStmt(kind=kind, target=target, when_expr=when_expr)

    @v_args(inline=True)
    def support_only_stmt(self, target, when_expr=None):
        return model.SupportOnlyStmt(target=target, when_expr=when_expr)

    def ignore_stmt(self, items):
        target = items[0]
        bases: tuple[str, ...] = ()
        when_expr: model.Expr | None = None
        for extra in items[1:]:
            if isinstance(extra, tuple):
                bases = extra
            else:
                when_expr = extra
        return model.IgnoreStmt(target=target, bases=bases, when_expr=when_expr)

    @v_args(inline=True)
    def invalidate_stmt(self, target, carrier, when_expr=None):
        return model.InvalidateStmt(target=target, carrier=carrier, when_expr=when_expr)

    @v_args(inline=True)
    def forbid_stmt(self, target, when_expr=None):
        return model.ForbidStmt(target=target, when_expr=when_expr)

    def when_stmt(self, items):
        return model.WhenStmt(expr=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def match_stmt(self, expr, *cases):
        return model.MatchStmt(expr=expr, cases=tuple(cases))

    def match_case(self, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return model.MatchArm(head=head, items=tuple(items[1:]))

    @v_args(inline=True)
    def route_from_stmt(self, expr, enum_ref, *cases):
        return model.RouteFromStmt(expr=expr, enum_ref=enum_ref, cases=tuple(cases))

    def route_from_case(self, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return model.RouteFromArm(head=head, route=items[1])

    def else_match_head(self, _items):
        return "__ELSE__"

    @v_args(inline=True)
    def stop_stmt(self, message=None, when_expr=None):
        if message is not None and not isinstance(message, str):
            when_expr = message
            message = None
        return model.StopStmt(message=message, when_expr=when_expr)

    @v_args(inline=True)
    def law_route_stmt(self, label, target, when_expr=None):
        return model.LawRouteStmt(label=label, target=target, when_expr=when_expr)

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

    def path_set_expr(self, items):
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
        return model.LawPathSet(paths=tuple(paths), except_paths=tuple(except_paths))

    def path_set_base(self, items):
        if len(items) == 1 and isinstance(items[0], model.LawPath):
            return items[0]
        return tuple(items)

    def law_path(self, items):
        parts = list(items[0])
        wildcard = len(items) > 1
        return model.LawPath(parts=tuple(parts), wildcard=wildcard)

    def law_path_wildcard(self, _items):
        return "*"
