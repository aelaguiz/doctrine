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
    _check_emit_docs_rejects_legacy_example_file_on_output_shape()
    _check_emit_docs_emits_generated_schema_for_structured_final_output()
    _check_emit_docs_emits_route_contract_for_routed_final_output()
    _check_emit_docs_emits_runtime_package_trees()
    _check_emit_docs_rejects_output_dir_outside_project_root()
    _check_emit_docs_rejects_entrypoint_outside_project_root()
    _check_emit_docs_uses_entrypoint_stem_for_output_name()
    _check_emit_skill_uses_source_root_bundle_outputs()
    _check_emit_skill_emits_document_companions_from_emit_block()
    _check_emit_skill_keeps_mixed_agents_tree_files()
    _check_emit_skill_emits_contract_json_for_host_bound_packages()
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


def _check_emit_docs_rejects_legacy_example_file_on_output_shape() -> None:
    with TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        root = base / "project"
        prompts = root / "prompts"
        prompts.mkdir(parents=True)
        (prompts / "AGENTS.prompt").write_text(
            """output schema RepoStatusSchema: "Repo Status Schema"
    field summary: "Summary"
        type: string

    example:
        summary: "Branch is clean."

output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema
    example_file: "examples/repo_status.example.json"

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
        _expect("E215 compile error" in output, output)
        _expect("retire `example_file`" in output, output)


def _check_emit_docs_emits_generated_schema_for_structured_final_output() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir(parents=True)
        (prompts / "AGENTS.prompt").write_text(
            """output schema RepoStatusSchema: "Repo Status Schema"
    field summary: "Summary"
        type: string

output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema

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

        exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "demo"])
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        agents_path = root / "build" / "repo_status_agent" / "AGENTS.md"
        schema_path = (
            root
            / "build"
            / "repo_status_agent"
            / "schemas"
            / "repo_status_final_response.schema.json"
        )
        contract_path = root / "build" / "repo_status_agent" / "final_output.contract.json"
        _expect(agents_path.is_file(), f"missing emitted AGENTS.md: {agents_path}")
        _expect(schema_path.is_file(), f"missing emitted schema file: {schema_path}")
        _expect(contract_path.is_file(), f"missing emitted final-output contract: {contract_path}")
        schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
        _expect(schema_data.get("type") == "object", str(schema_data))
        _expect(schema_data.get("required") == ["summary"], str(schema_data))
        rendered = agents_path.read_text(encoding="utf-8")
        _expect("#### Payload Fields" in rendered, rendered)
        _expect("#### Example" not in rendered, rendered)
        contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
        _expect(
            contract_data.get("final_output", {}).get("emitted_schema_relpath")
            == "schemas/repo_status_final_response.schema.json",
            str(contract_data),
        )
        _expect(
            contract_data.get("route")
            == {
                "exists": False,
                "behavior": "never",
                "has_unrouted_branch": False,
                "unrouted_review_verdicts": [],
                "branches": [],
            },
            str(contract_data),
        )


def _check_emit_docs_emits_route_contract_for_routed_final_output() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir(parents=True)
        (prompts / "AGENTS.prompt").write_text(
            """agent ReviewLead:
    role: "Own routed follow-up."
    workflow: "Follow Up"
        "Take the routed follow-up."

output RouteReply: "Route Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

agent Router:
    role: "Route and answer."
    workflow: "Route"
        law:
            active when true
            current none
            route "Go to review." -> ReviewLead
    outputs: "Outputs"
        RouteReply
    final_output: RouteReply
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

        exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "demo"])
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        contract_path = root / "build" / "router" / "final_output.contract.json"
        _expect(contract_path.is_file(), f"missing emitted final-output contract: {contract_path}")
        contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
        _expect(
            contract_data.get("route")
            == {
                "exists": True,
                "behavior": "always",
                "has_unrouted_branch": False,
                "unrouted_review_verdicts": [],
                "branches": [
                    {
                        "target": {
                            "key": "ReviewLead",
                            "module_parts": [],
                            "name": "ReviewLead",
                            "title": "Review Lead",
                        },
                        "label": "Go to review.",
                        "summary": "Go to review. Next owner: Review Lead.",
                        "choice_members": [],
                    }
                ],
            },
            str(contract_data),
        )


def _check_emit_docs_emits_runtime_package_trees() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        (prompts / "writer_home").mkdir(parents=True)
        (prompts / "editor_home" / "references").mkdir(parents=True)
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
            """export agent BriefEditor:
    role: "Polish the brief and stop."
    workflow: "Polish"
        "Polish the brief and stop."
""",
            encoding="utf-8",
        )
        (prompts / "editor_home" / "SOUL.prompt").write_text(
            """agent BriefEditor:
    role: "Carry the editor background for the package."
""",
            encoding="utf-8",
        )
        runtime_note = "Keep the brief crisp and direct.\n"
        (prompts / "editor_home" / "references" / "style.txt").write_text(
            runtime_note,
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

        exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "demo"])
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        writer_path = root / "build" / "writer_home" / "AGENTS.md"
        editor_path = root / "build" / "editor_home" / "AGENTS.md"
        soul_path = root / "build" / "editor_home" / "SOUL.md"
        note_path = root / "build" / "editor_home" / "references" / "style.txt"
        _expect(writer_path.is_file(), f"missing emitted writer AGENTS.md: {writer_path}")
        _expect(editor_path.is_file(), f"missing emitted editor AGENTS.md: {editor_path}")
        _expect(soul_path.is_file(), f"missing emitted editor SOUL.md: {soul_path}")
        _expect(note_path.is_file(), f"missing bundled peer file: {note_path}")
        _expect(note_path.read_text(encoding="utf-8") == runtime_note, note_path.read_text(encoding="utf-8"))


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


def _check_emit_docs_rejects_entrypoint_outside_project_root() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir).resolve()
        outside = root.parent / f"{root.name}_outside"
        (outside / "prompts").mkdir(parents=True)
        (outside / "prompts" / "AGENTS.prompt").write_text(
            """agent DemoAgent:
    role: "Own the emitted surface."
""",
            encoding="utf-8",
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            f"""[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo"
entrypoint = "../{outside.name}/prompts/AGENTS.prompt"
output_dir = "build"
""",
            encoding="utf-8",
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "demo"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E521 emit error" in output, output)
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
        soul_path = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.md"
        _expect(agents_path.is_file(), f"missing emitted AGENTS.md: {agents_path}")
        _expect(soul_path.is_file(), f"missing emitted SOUL.md: {soul_path}")
        _expect(
            not (agents_path.parent / "AGENTS.contract.json").exists(),
            "did not expect emitted AGENTS.contract.json",
        )
        _expect(
            not (soul_path.parent / "SOUL.contract.json").exists(),
            "did not expect emitted SOUL.contract.json",
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
        _expect(
            not (root / "build" / "skills" / "demo_package" / "SKILL.contract.json").exists(),
            "did not expect SKILL.contract.json for a package with no host-binding truth",
        )
        _expect(checklist_path.is_file(), f"missing bundled reference file: {checklist_path}")
        _expect(reviewer_path.is_file(), f"missing compiled bundled agent file: {reviewer_path}")


def _check_emit_skill_emits_document_companions_from_emit_block() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "skills" / "emitted_docs"
        (prompts / "refs").mkdir(parents=True)
        skill_prompt = prompts / "SKILL.prompt"
        skill_prompt.write_text(
            """skill package EmittedDocs: "Emitted Docs"
    metadata:
        name: "emitted-docs"
    emit:
        "references/query-patterns.md": QueryPatterns
        "references/receipts-template.md": ReceiptsTemplate
    "Keep the root file short."
""",
            encoding="utf-8",
        )
        (prompts / "refs" / "query_patterns.prompt").write_text(
            """document QueryPatterns: "Query Patterns"
    section summary: "Summary"
        "Pick the right query before you search."
""",
            encoding="utf-8",
        )
        (prompts / "refs" / "receipts_template.prompt").write_text(
            """document ReceiptsTemplate: "Receipts Template"
    section summary: "Summary"
        "Keep one clear proof trail for each claim."
""",
            encoding="utf-8",
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "emitted_docs"
entrypoint = "prompts/skills/emitted_docs/SKILL.prompt"
output_dir = "build"
""",
            encoding="utf-8",
        )
        exit_code = emit_skill_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "emitted_docs",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        query_patterns_path = (
            root / "build" / "skills" / "emitted_docs" / "references" / "query-patterns.md"
        )
        receipts_path = (
            root / "build" / "skills" / "emitted_docs" / "references" / "receipts-template.md"
        )
        _expect(
            not (root / "build" / "skills" / "emitted_docs" / "SKILL.contract.json").exists(),
            "did not expect SKILL.contract.json for a package with no host-binding truth",
        )
        _expect(query_patterns_path.is_file(), f"missing emitted companion doc: {query_patterns_path}")
        _expect(receipts_path.is_file(), f"missing emitted companion doc: {receipts_path}")


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
        _expect(
            not (root / "build" / "skills" / "mixed_agents" / "SKILL.contract.json").exists(),
            "did not expect SKILL.contract.json for a package with no host-binding truth",
        )
        _expect(reviewer_path.is_file(), f"missing compiled bundled agent file: {reviewer_path}")
        _expect(metadata_path.is_file(), f"missing bundled runtime metadata file: {metadata_path}")
        _expect(metadata_path.read_text(encoding="utf-8") == runtime_metadata, metadata_path.read_text(encoding="utf-8"))


def _check_emit_skill_emits_contract_json_for_host_bound_packages() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "skills" / "host_bound"
        (prompts / "refs").mkdir(parents=True)
        (prompts / "agents").mkdir(parents=True)
        skill_prompt = prompts / "SKILL.prompt"
        skill_prompt.write_text(
            """skill package HostBound: "Host Bound"
    metadata:
        name: "host-bound"
    emit:
        "references/query-patterns.md": QueryPatterns
    host_contract:
        document section_map: "Section Map"
        final_output final_response: "Final Response"
    "Read {{host:section_map.title}}."
""",
            encoding="utf-8",
        )
        (prompts / "refs" / "query_patterns.prompt").write_text(
            """document QueryPatterns: "Query Patterns"
    section summary: "Summary"
        "Keep {{host:section_map.title}} stable."
""",
            encoding="utf-8",
        )
        (prompts / "agents" / "reviewer.prompt").write_text(
            """agent Reviewer:
    role: "Review {{host:final_response}}."
    workflow: "Review"
        output: "Output"
            host:final_response
""",
            encoding="utf-8",
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "host_bound"
entrypoint = "prompts/skills/host_bound/SKILL.prompt"
output_dir = "build"
""",
            encoding="utf-8",
        )
        exit_code = emit_skill_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "host_bound",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        contract_path = root / "build" / "skills" / "host_bound" / "SKILL.contract.json"
        _expect(contract_path.is_file(), f"missing emitted SKILL.contract.json: {contract_path}")
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
        _expect(payload["package"]["name"] == "host-bound", str(payload))
        _expect(
            payload["artifacts"]["SKILL.md"]["referenced_host_paths"] == ["section_map.title"],
            str(payload),
        )
        _expect(
            payload["artifacts"]["agents/reviewer.md"]["referenced_host_paths"] == ["final_response"],
            str(payload),
        )


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
