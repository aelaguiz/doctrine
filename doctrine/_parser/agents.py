from __future__ import annotations

from lark import v_args

from doctrine import model


class AgentTransformerMixin:
    """Shared agent and agent-field lowering for the public parser boundary."""

    def agent(self, items):
        return self._agent(items, abstract=False)

    def abstract_agent(self, items):
        return self._agent(items, abstract=True)

    def role_body(self, items):
        return items[0]

    @v_args(inline=True)
    def role_field(self, title_or_text, body=None):
        if body is None:
            return model.RoleScalar(text=title_or_text)
        return model.RoleBlock(title=title_or_text, lines=tuple(body))

    @v_args(inline=True)
    def skills_field(self, title_or_ref, body=None):
        return model.SkillsField(value=self._skills_value(title_or_ref, body))

    @v_args(inline=True)
    def review_field(self, ref):
        return model.ReviewField(value=ref)

    @v_args(inline=True)
    def final_output_field(self, ref):
        return model.FinalOutputField(value=ref)
