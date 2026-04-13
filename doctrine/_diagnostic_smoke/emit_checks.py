from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.diagnostics import diagnostic_to_dict
from doctrine.emit_docs import main as emit_docs_main
from doctrine.emit_skill import main as emit_skill_main
from doctrine.parser import parse_file

from doctrine._diagnostic_smoke.fixtures import SmokeFailure, _expect, _write_prompt


def run_emit_checks() -> None:
    _check_emit_docs_handles_invalid_toml_without_traceback()
    _check_emit_docs_uses_specific_code_for_missing_entrypoint()
    _check_emit_docs_rejects_support_files_outside_project_root()
    _check_emit_docs_rejects_output_dir_outside_project_root()
    _check_emit_docs_uses_entrypoint_stem_for_output_name()
    _check_emit_skill_uses_source_root_bundle_outputs()
    _check_emit_skill_keeps_mixed_agents_tree_files()
    _check_emit_skill_preserves_binary_assets()
    _check_diagnostic_to_dict_is_json_safe()


def _check_emit_docs_handles_invalid_toml_without_traceback() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        pyproject = root / "pyproject.toml"
        pyproject.write_text("[tool.doctrine.emit\n")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "x"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E506 emit error: Invalid emit config TOML" in output, output)
        _expect("Traceback" not in output, output)


def _check_emit_docs_uses_specific_code_for_missing_entrypoint() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "bad"
entrypoint = "prompts/OTHER.prompt"
output_dir = "build"
"""
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "bad"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E512 emit error" in output, output)
        _expect("entrypoint does not exist" in output, output)


def _check_emit_docs_rejects_support_files_outside_project_root() -> None:
    with TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        root = base / "project"
        prompts = root / "prompts"
        prompts.mkdir(parents=True)
        (base / "external.schema.json").write_text(
            '{\n  "type": "object",\n  "properties": {}\n}\n',
            encoding="utf-8",
        )
        (base / "external.example.json").write_text("{ }\n", encoding="utf-8")
        (prompts / "AGENTS.prompt").write_text(
            """json schema RepoStatusSchema: "Repo Status Schema"
    profile: OpenAIStructuredOutput
    file: "../external.schema.json"

output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema
    example_file: "../external.example.json"

output RepoStatusFinalResponse: "Repo Status Final Response"
    target: TurnResponse
    shape: RepoStatusJson
    requirement: Required

agent RepoStatusAgent:
    role: "Report repo status."
    workflow: "Summarize"
        "Summarize the repo state."
    outputs: "Outputs"
        RepoStatusFinalResponse
    final_output: RepoStatusFinalResponse
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

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "demo"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E519 emit error" in output, output)
        _expect("outside the target project root" in output, output)


def _check_emit_docs_rejects_output_dir_outside_project_root() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir(parents=True)
        (prompts / "AGENTS.prompt").write_text(
            """agent DemoAgent:
    role: "Own the emitted surface."
""",
            encoding="utf-8",
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo"
entrypoint = "prompts/AGENTS.prompt"
output_dir = "../outside"
""",
            encoding="utf-8",
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "demo"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E520 emit error" in output, output)
        _expect("outside the target project root" in output, output)


def _check_emit_docs_uses_entrypoint_stem_for_output_name() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "demo" / "agents" / "demo_agent"
        prompts.mkdir(parents=True)
        agents_prompt = prompts / "AGENTS.prompt"
        soul_prompt = prompts / "SOUL.prompt"
        agents_prompt.write_text(
            """agent DemoAgent:
    role: "You are Demo Agent."
"""
        )
        soul_prompt.write_text(
            """agent DemoAgent:
    role: "You are Demo Agent. Let this background shape your tone."
"""
        )
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
        exit_code = emit_docs_main(
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
        agents_path = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.md"
        agents_contract_path = (
            root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.contract.json"
        )
        soul_path = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.md"
        soul_contract_path = (
            root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.contract.json"
        )
        _expect(agents_path.is_file(), f"missing emitted AGENTS.md: {agents_path}")
        _expect(
            agents_contract_path.is_file(),
            f"missing emitted AGENTS.contract.json: {agents_contract_path}",
        )
        _expect(soul_path.is_file(), f"missing emitted SOUL.md: {soul_path}")
        _expect(
            soul_contract_path.is_file(),
            f"missing emitted SOUL.contract.json: {soul_contract_path}",
        )


def _check_emit_skill_uses_source_root_bundle_outputs() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "skills" / "demo_package"
        (prompts / "agents").mkdir(parents=True)
        (prompts / "references").mkdir(parents=True)
        skill_prompt = prompts / "SKILL.prompt"
        skill_prompt.write_text(
            """skill package DemoPackage: "Demo Package"
    metadata:
        name: "demo-package"
        description: "Emit bundled package files from the source root."
        version: "1.0.0"
        license: "MIT"
    "Consult the bundled files before you continue."
"""
        )
        (prompts / "references" / "checklist.md").write_text(
            "# Checklist\n\nReview the package before you ship it.\n"
        )
        (prompts / "agents" / "reviewer.prompt").write_text(
            """agent Reviewer:
    role: "Review the package."
    workflow: "Review"
        "Read the package cold."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_skill"
entrypoint = "prompts/skills/demo_package/SKILL.prompt"
output_dir = "build"
"""
        )
        exit_code = emit_skill_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "demo_skill",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        skill_path = root / "build" / "skills" / "demo_package" / "SKILL.md"
        checklist_path = (
            root / "build" / "skills" / "demo_package" / "references" / "checklist.md"
        )
        reviewer_path = (
            root / "build" / "skills" / "demo_package" / "agents" / "reviewer.md"
        )
        _expect(skill_path.is_file(), f"missing emitted SKILL.md: {skill_path}")
        _expect(checklist_path.is_file(), f"missing bundled reference file: {checklist_path}")
        _expect(reviewer_path.is_file(), f"missing compiled bundled agent file: {reviewer_path}")


def _check_emit_skill_keeps_mixed_agents_tree_files() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "skills" / "mixed_agents"
        (prompts / "agents").mkdir(parents=True)
        skill_prompt = prompts / "SKILL.prompt"
        skill_prompt.write_text(
            """skill package MixedAgents: "Mixed Agents"
    metadata:
        name: "mixed-agents"
    "Keep runtime metadata and bundled agent prompts in one `agents/` tree."
""",
            encoding="utf-8",
        )
        (prompts / "agents" / "reviewer.prompt").write_text(
            """agent Reviewer:
    role: "Review the package."
""",
            encoding="utf-8",
        )
        runtime_metadata = """interface:
  display_name: Mixed Agents
default_prompt: SKILL.md
"""
        (prompts / "agents" / "openai.yaml").write_text(
            runtime_metadata,
            encoding="utf-8",
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "mixed_agents"
entrypoint = "prompts/skills/mixed_agents/SKILL.prompt"
output_dir = "build"
""",
            encoding="utf-8",
        )
        exit_code = emit_skill_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "mixed_agents",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        reviewer_path = root / "build" / "skills" / "mixed_agents" / "agents" / "reviewer.md"
        metadata_path = root / "build" / "skills" / "mixed_agents" / "agents" / "openai.yaml"
        _expect(reviewer_path.is_file(), f"missing compiled bundled agent file: {reviewer_path}")
        _expect(metadata_path.is_file(), f"missing bundled runtime metadata file: {metadata_path}")
        _expect(metadata_path.read_text(encoding="utf-8") == runtime_metadata, metadata_path.read_text(encoding="utf-8"))


def _check_emit_skill_preserves_binary_assets() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "skills" / "binary_assets"
        (prompts / "assets").mkdir(parents=True)
        skill_prompt = prompts / "SKILL.prompt"
        skill_prompt.write_text(
            """skill package BinaryAssets: "Binary Assets"
    metadata:
        name: "binary-assets"
    "Keep bundled binary assets byte-for-byte."
""",
            encoding="utf-8",
        )
        asset_bytes = bytes.fromhex(
            "89504e470d0a1a0a"
            "0000000d4948445200000001000000010802000000907753de"
            "0000000c4944415408d763f8ffff3f0005fe02fea7e58f7f"
            "0000000049454e44ae426082"
        )
        (prompts / "assets" / "icon.png").write_bytes(asset_bytes)
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "binary_assets"
entrypoint = "prompts/skills/binary_assets/SKILL.prompt"
output_dir = "build"
""",
            encoding="utf-8",
        )
        exit_code = emit_skill_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "binary_assets",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        asset_path = root / "build" / "skills" / "binary_assets" / "assets" / "icon.png"
        _expect(asset_path.is_file(), f"missing bundled binary asset: {asset_path}")
        _expect(asset_path.read_bytes() == asset_bytes, "expected bundled binary asset bytes to round-trip")


def _check_diagnostic_to_dict_is_json_safe() -> None:
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, 'agent Broken\n    role: "x"\n')
        try:
            parse_file(prompt_path)
        except Exception as exc:
            payload = diagnostic_to_dict(exc)
            json.dumps(payload)
            return
        raise SmokeFailure("expected parse failure for JSON-safety check, but parsing succeeded")
