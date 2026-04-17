from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import _with_source_span


class ExpressionTransformerMixin:
    """Shared expression and small syntax lowering for the public parser boundary."""

    @v_args(inline=True)
    def required_line(self, _keyword, text):
        return model.EmphasizedLine(kind="required", text=text)

    @v_args(inline=True)
    def important_line(self, _keyword, text):
        return model.EmphasizedLine(kind="important", text=text)

    @v_args(inline=True)
    def warning_line(self, _keyword, text):
        return model.EmphasizedLine(kind="warning", text=text)

    @v_args(inline=True)
    def note_line(self, _keyword, text):
        return model.EmphasizedLine(kind="note", text=text)

    def field_path(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def expr_ref(self, meta, parts):
        return _with_source_span(model.ExprRef(parts=tuple(parts)), meta)

    @v_args(inline=True)
    def expr_number(self, value):
        return value

    def expr_true(self, _items):
        return True

    def expr_false(self, _items):
        return False

    def expr_call(self, items):
        return model.ExprCall(name=items[0], args=tuple(items[1:]))

    def expr_set(self, items):
        return model.ExprSet(items=tuple(items))

    @v_args(inline=True)
    def expr_or(self, left, right):
        return model.ExprBinary(op="or", left=left, right=right)

    @v_args(inline=True)
    def expr_and(self, left, right):
        return model.ExprBinary(op="and", left=left, right=right)

    @v_args(inline=True)
    def expr_eq(self, left, right):
        return model.ExprBinary(op="==", left=left, right=right)

    @v_args(inline=True)
    def expr_ne(self, left, right):
        return model.ExprBinary(op="!=", left=left, right=right)

    @v_args(inline=True)
    def expr_gt(self, left, right):
        return model.ExprBinary(op=">", left=left, right=right)

    @v_args(inline=True)
    def expr_gte(self, left, right):
        return model.ExprBinary(op=">=", left=left, right=right)

    @v_args(inline=True)
    def expr_lt(self, left, right):
        return model.ExprBinary(op="<", left=left, right=right)

    @v_args(inline=True)
    def expr_lte(self, left, right):
        return model.ExprBinary(op="<=", left=left, right=right)

    @v_args(inline=True)
    def expr_in(self, left, right):
        return model.ExprBinary(op="in", left=left, right=right)

    @v_args(inline=True)
    def expr_not_in(self, left, right):
        return model.ExprBinary(op="not in", left=left, right=right)

    def ref_list(self, items):
        return tuple(items)

    @v_args(inline=True)
    def ref_item(self, ref):
        return ref

    @v_args(meta=True, inline=True)
    def route_stmt(self, meta, label, target):
        return _with_source_span(model.RouteLine(label=label, target=target), meta)

    def block_lines(self, items):
        return tuple(items)
