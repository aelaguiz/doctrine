from __future__ import annotations

import json
import unittest
from pathlib import Path

from doctrine._diagnostics.contracts import (
    DiagnosticExcerptLine,
    DiagnosticLocation,
    DiagnosticRelatedLocation,
    DoctrineDiagnostic,
)
from doctrine.diagnostics import diagnostic_to_dict, format_diagnostic


class DiagnosticFormattingTests(unittest.TestCase):
    def test_format_diagnostic_renders_related_locations(self) -> None:
        diagnostic = DoctrineDiagnostic(
            code="E255",
            stage="compile",
            summary="Invalid output inheritance patch",
            detail="Output `LessonsLeadOutput` overrides entry `must_include` with the wrong kind.",
            location=DiagnosticLocation(
                path=Path("/tmp/INVALID_OVERRIDE_KIND.prompt"),
                line=15,
                column=5,
            ),
            excerpt=(DiagnosticExcerptLine(number=15, text="    override must_include: TurnResponse"),),
            caret_column=5,
            related=(
                DiagnosticRelatedLocation(
                    label="inherited `must_include` section",
                    location=DiagnosticLocation(
                        path=Path("/tmp/INVALID_OVERRIDE_KIND.prompt"),
                        line=6,
                        column=5,
                    ),
                    excerpt=(
                        DiagnosticExcerptLine(number=6, text='    must_include: "Must Include"'),
                    ),
                    caret_column=5,
                ),
            ),
        )

        rendered = format_diagnostic(diagnostic)

        self.assertIn("Location:", rendered)
        self.assertIn("Source:", rendered)
        self.assertIn("Related:", rendered)
        self.assertIn("inherited `must_include` section", rendered)
        self.assertIn("override must_include: TurnResponse", rendered)
        self.assertIn('must_include: "Must Include"', rendered)

    def test_diagnostic_to_dict_keeps_related_locations_json_safe(self) -> None:
        diagnostic = DoctrineDiagnostic(
            code="E280",
            stage="compile",
            summary="Missing import module",
            location=DiagnosticLocation(path=Path("/tmp/AGENTS.prompt"), line=1, column=8),
            related=(
                DiagnosticRelatedLocation(
                    label="searched root",
                    location=DiagnosticLocation(path=Path("/tmp/prompts")),
                ),
            ),
        )

        payload = diagnostic_to_dict(diagnostic)

        json.dumps(payload)
        self.assertEqual(payload["related"][0]["label"], "searched root")
        self.assertEqual(payload["related"][0]["location"]["path"], "/tmp/prompts")
