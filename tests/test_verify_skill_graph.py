from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine.emit_common import load_emit_targets
from doctrine.emit_skill import emit_target_skill
from doctrine.emit_skill_graph import emit_target_skill_graph
from doctrine.skill_graph_source_receipts import receipt_path_for_target as graph_receipt_path_for_target
from doctrine.skill_source_receipts import receipt_path_for_target as skill_receipt_path_for_target
from doctrine.verify_skill_graph import verify_target_skill_graph

from tests.test_emit_skill_graph import _write_graph_repo


class VerifySkillGraphTests(unittest.TestCase):
    def test_verify_skill_graph_reports_current_and_stale_package_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject = _write_graph_repo(root)
            targets = load_emit_targets(pyproject)
            emit_target_skill(targets["skill_bundle"])
            with patch(
                "doctrine.emit_skill_graph.render_flow_svg",
                side_effect=lambda _d2, svg: svg.write_text("<svg>graph</svg>\n", encoding="utf-8"),
            ):
                emit_target_skill_graph(targets["graph_bundle"])
                current = verify_target_skill_graph(targets["graph_bundle"])
            self.assertEqual(current.status, "current")

            skill_receipt_path_for_target(targets["skill_bundle"]).write_text(
                "{}\n",
                encoding="utf-8",
            )
            with patch(
                "doctrine.emit_skill_graph.render_flow_svg",
                side_effect=lambda _d2, svg: svg.write_text("<svg>graph</svg>\n", encoding="utf-8"),
            ):
                stale = verify_target_skill_graph(targets["graph_bundle"])
            self.assertEqual(stale.status, "stale_package_receipt")

    def test_verify_skill_graph_reports_edited_graph_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject = _write_graph_repo(root)
            targets = load_emit_targets(pyproject)
            emit_target_skill(targets["skill_bundle"])
            with patch(
                "doctrine.emit_skill_graph.render_flow_svg",
                side_effect=lambda _d2, svg: svg.write_text("<svg>graph</svg>\n", encoding="utf-8"),
            ):
                emit_target_skill_graph(targets["graph_bundle"])

            emitted_dir = graph_receipt_path_for_target(targets["graph_bundle"]).parent
            (emitted_dir / "references" / "skill-graph.json").write_text(
                "{\n  \"edited\": true\n}\n",
                encoding="utf-8",
            )
            with patch(
                "doctrine.emit_skill_graph.render_flow_svg",
                side_effect=lambda _d2, svg: svg.write_text("<svg>graph</svg>\n", encoding="utf-8"),
            ):
                result = verify_target_skill_graph(targets["graph_bundle"])
            self.assertEqual(result.status, "edited_graph_artifact")
