from __future__ import annotations

import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.emit_flow import main as emit_flow_main

from doctrine._diagnostic_smoke.fixtures import _expect, _flow_visualizer_showcase_source


def run_flow_emit_checks() -> None:
    _check_emit_flow_uses_entrypoint_stem_for_output_name()
    _check_emit_flow_roots_on_runtime_package_frontier()
    _check_emit_flow_rejects_skill_entrypoints()
    _check_emit_flow_direct_mode_groups_shared_surfaces()
    _check_emit_flow_direct_mode_requires_output_dir()
    _check_emit_flow_direct_mode_rejects_output_dir_outside_project_root()


def _check_emit_flow_uses_entrypoint_stem_for_output_name() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "demo" / "agents" / "demo_agent"
        prompts.mkdir(parents=True)
        agents_prompt = prompts / "AGENTS.prompt"
        soul_prompt = prompts / "SOUL.prompt"
        source = """input SharedInput: "Shared Input"
    source: Prompt
    shape: JsonObject
    requirement: Required

output SharedComment: "Shared Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

agent DemoAgent:
    role: "Own the demo flow."
    workflow: "Demo Flow"
        "Read the shared input and leave one comment."
    inputs: "Inputs"
        SharedInput
    outputs: "Outputs"
        SharedComment
"""
        agents_prompt.write_text(source)
        soul_prompt.write_text(source)
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_agents"
entrypoint = "prompts/demo/agents/demo_agent/AGENTS.prompt"
output_dir = "build"

[[tool.doctrine.emit.targets]]
name = "demo_soul"
entrypoint = "prompts/demo/agents/demo_agent/SOUL.prompt"
output_dir = "build"
"""
        )
        exit_code = emit_flow_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "demo_agents",
                "--target",
                "demo_soul",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        agents_d2 = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.flow.d2"
        agents_svg = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.flow.svg"
        soul_d2 = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.flow.d2"
        soul_svg = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.flow.svg"
        _expect(agents_d2.is_file(), f"missing emitted AGENTS.flow.d2: {agents_d2}")
        _expect(agents_svg.is_file(), f"missing emitted AGENTS.flow.svg: {agents_svg}")
        _expect(soul_d2.is_file(), f"missing emitted SOUL.flow.d2: {soul_d2}")
        _expect(soul_svg.is_file(), f"missing emitted SOUL.flow.svg: {soul_svg}")


def _check_emit_flow_rejects_skill_entrypoints() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "skill_pkg"
        prompts.mkdir(parents=True)
        entrypoint = prompts / "SKILL.prompt"
        entrypoint.write_text(
            """skill package DemoSkill: "Demo Skill"
    metadata:
        name: "demo-skill"
    "This package should not emit flow artifacts."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_skill"
entrypoint = "prompts/skill_pkg/SKILL.prompt"
output_dir = "build"
"""
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_flow_main(
                [
                    "--pyproject",
                    str(pyproject),
                    "--target",
                    "demo_skill",
                ]
            )
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E510 emit error" in output, output)
        _expect("must point at `AGENTS.prompt` or `SOUL.prompt`" in output, output)


def _check_emit_flow_roots_on_runtime_package_frontier() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        (prompts / "writer_home").mkdir(parents=True)
        (prompts / "editor_home").mkdir(parents=True)
        (prompts / "AGENTS.prompt").write_text(
            "import writer_home\n",
            encoding="utf-8",
        )
        (prompts / "writer_home" / "AGENTS.prompt").write_text(
            """import editor_home

agent BriefWriter:
    role: "Draft the first brief and hand it to the editor."
    workflow: "Draft"
        "Write the first brief for the editor."
        routing: "Routing"
            route "Hand the brief to BriefEditor." -> editor_home.BriefEditor
""",
            encoding="utf-8",
        )
        (prompts / "editor_home" / "AGENTS.prompt").write_text(
            """agent BriefEditor:
    role: "Polish the brief and stop."
    workflow: "Polish"
        "Polish the brief and stop."
""",
            encoding="utf-8",
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo"
entrypoint = "prompts/AGENTS.prompt"
output_dir = "build"
""",
            encoding="utf-8",
        )

        exit_code = emit_flow_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "demo",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        d2_path = root / "build" / "AGENTS.flow.d2"
        _expect(d2_path.is_file(), f"missing emitted AGENTS.flow.d2: {d2_path}")
        rendered = d2_path.read_text(encoding="utf-8")
        _expect("BriefWriter" in rendered, rendered)
        _expect("BriefEditor" in rendered, rendered)


def _check_emit_flow_direct_mode_groups_shared_surfaces() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "showcase"
        prompts.mkdir(parents=True)
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(_flow_visualizer_showcase_source())
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        exit_code = emit_flow_main(
            [
                "--pyproject",
                str(pyproject),
                "--entrypoint",
                str(entrypoint.relative_to(root)),
                "--output-dir",
                "build",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")

        d2_path = root / "build" / "showcase" / "AGENTS.flow.d2"
        svg_path = root / "build" / "showcase" / "AGENTS.flow.svg"
        _expect(d2_path.is_file(), f"missing emitted AGENTS.flow.d2: {d2_path}")
        _expect(svg_path.is_file(), f"missing emitted AGENTS.flow.svg: {svg_path}")

        rendered = d2_path.read_text()
        _expect("shared_inputs: {" in rendered, rendered)
        _expect("agent_handoffs: {" in rendered, rendered)
        _expect("shared_outputs_and_carriers: {" in rendered, rendered)
        _expect(rendered.startswith("direction: down\n"), rendered)
        _expect("Shared Input" in rendered, rendered)
        _expect("Shared Output / Carrier" in rendered, rendered)
        _expect("Used by:" in rendered, rendered)
        _expect("Produced by:" in rendered, rendered)
        _expect('primary_lane: {\n    label: ""\n    direction: down' in rendered, rendered)
        _expect(
            "agent_handoffs.primary_lane.agent_projectlead -> agent_handoffs.primary_lane.agent_researchspecialist"
            in rendered,
            rendered,
        )
        _expect(
            "agent_handoffs.primary_lane.agent_researchspecialist -> agent_handoffs.primary_lane.agent_writingspecialist"
            in rendered,
            rendered,
        )
        _expect(
            "agent_handoffs.primary_lane.agent_writingspecialist -> agent_handoffs.primary_lane.agent_projectlead"
            in rendered,
            rendered,
        )
        _expect("Start research with" in rendered, rendered)
        _expect("Return the draft to" in rendered, rendered)


def _check_emit_flow_direct_mode_requires_output_dir() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir()
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(
            """agent DemoAgent:
    role: "Own the demo flow."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_flow_main(
                [
                    "--pyproject",
                    str(pyproject),
                    "--entrypoint",
                    str(entrypoint.relative_to(root)),
                ]
            )
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E518 emit error" in output, output)
        _expect("Direct emit flow mode requires entrypoint and output_dir" in output, output)


def _check_emit_flow_direct_mode_rejects_output_dir_outside_project_root() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir()
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(
            """agent DemoAgent:
    role: "Own the demo flow."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_flow_main(
                [
                    "--pyproject",
                    str(pyproject),
                    "--entrypoint",
                    str(entrypoint.relative_to(root)),
                    "--output-dir",
                    "../outside",
                ]
            )
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E520 emit error" in output, output)
        _expect("outside the target project root" in output, output)
