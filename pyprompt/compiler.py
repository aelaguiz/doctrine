from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from pyprompt import model


class CompileError(RuntimeError):
    """Fail-loud compiler error for the bootstrap subset."""


@dataclass(slots=True, frozen=True)
class CompiledAgent:
    name: str
    role: model.RoleScalar | model.RoleBlock
    workflow: model.Workflow


def compile_prompt(prompt_file: model.PromptFile, agent_name: str) -> CompiledAgent:
    duplicate_names = [
        name for name, count in Counter(agent.name for agent in prompt_file.agents).items() if count > 1
    ]
    if duplicate_names:
        raise CompileError(f"Duplicate agent name(s): {', '.join(sorted(duplicate_names))}")

    selected = [agent for agent in prompt_file.agents if agent.name == agent_name]
    if not selected:
        raise CompileError(f"Missing target agent: {agent_name}")

    return validate_agent(selected[0])


def validate_agent(agent: model.Agent) -> CompiledAgent:
    # The bootstrap has no implicit target or flexible field ordering.
    if len(agent.fields) != 2:
        raise CompileError(
            f"Agent {agent.name} is outside the bootstrap subset: expected exactly one role and one workflow."
        )

    role, workflow = agent.fields
    if not isinstance(role, (model.RoleScalar, model.RoleBlock)) or not isinstance(workflow, model.Workflow):
        raise CompileError(
            f"Agent {agent.name} is outside the bootstrap subset: expected `role` followed by `workflow`."
        )

    return CompiledAgent(name=agent.name, role=role, workflow=workflow)
