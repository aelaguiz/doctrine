from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.emit_common import load_emit_targets
from doctrine.emit_skill import emit_target_skill


class EmitSkillTests(unittest.TestCase):
    def test_emit_skill_keeps_runtime_metadata_in_agents_tree(self) -> None:
        # This protects the real skill-package shape where bundled agent prompts
        # and runtime metadata live in the same `agents/` tree. Users need both
        # files after emit, not just the compiled markdown companions.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "mixed_agents"
            (prompts / "agents").mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package MixedAgents: "Mixed Agents"
                        metadata:
                            name: "mixed-agents"
                        "Keep runtime metadata and bundled agent prompts in one `agents/` tree."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "agents" / "reviewer.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the package."
                    """
                ),
                encoding="utf-8",
            )
            runtime_metadata = textwrap.dedent(
                """\
                interface:
                  display_name: Mixed Agents
                default_prompt: SKILL.md
                """
            )
            (prompts / "agents" / "openai.yaml").write_text(
                runtime_metadata,
                encoding="utf-8",
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/skills/mixed_agents/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            target = load_emit_targets(pyproject)["demo"]
            emitted = emit_target_skill(target)

            skill_path = root / "build" / "skills" / "mixed_agents" / "SKILL.md"
            reviewer_path = root / "build" / "skills" / "mixed_agents" / "agents" / "reviewer.md"
            metadata_path = root / "build" / "skills" / "mixed_agents" / "agents" / "openai.yaml"
            self.assertEqual(emitted[0], skill_path)
            self.assertCountEqual(emitted[1:], (reviewer_path, metadata_path))
            self.assertTrue(skill_path.is_file())
            self.assertTrue(reviewer_path.is_file())
            self.assertTrue(metadata_path.is_file())
            self.assertEqual(metadata_path.read_text(encoding="utf-8"), runtime_metadata)

    def test_emit_skill_preserves_binary_assets_byte_for_byte(self) -> None:
        # This protects the user-visible outcome where skill packages can ship
        # real binary assets. The emitted file must keep the exact bytes so the
        # asset still opens and renders correctly downstream.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "binary_assets"
            (prompts / "assets").mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package BinaryAssets: "Binary Assets"
                        metadata:
                            name: "binary-assets"
                        "Keep bundled binary assets byte-for-byte."
                    """
                ),
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
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/skills/binary_assets/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            target = load_emit_targets(pyproject)["demo"]
            emit_target_skill(target)

            emitted_path = root / "build" / "skills" / "binary_assets" / "assets" / "icon.png"
            self.assertTrue(emitted_path.is_file())
            self.assertEqual(emitted_path.read_bytes(), asset_bytes)


if __name__ == "__main__":
    unittest.main()
