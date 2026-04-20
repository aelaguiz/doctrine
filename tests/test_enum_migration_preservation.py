"""Byte-identical JSON schema `enum` preservation for the Form A → canonical
migration landed in Phase 3 of the universal typed field bodies sweep.

The goldens here were captured from the Phase 2 tip, before any example
source rewrite. Each golden asserts the exact `enum` list (value and
order) that Form A (`type: enum` + `values:` block) lowered for the
named shipped example. After Phase 3 migrates each example to the
canonical `enum X: "..."` decl + `type: X` form, recompiling must
still emit the same list in the same order. This locks the Phase 3
migration's preservation claim with a positive-value test, not a
tautology.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from doctrine._compiler.session import CompilationSession
from doctrine.parser import parse_file


_REPO_ROOT = Path(__file__).resolve().parents[1]


def _lowered_schema_for(prompt_relpath: str, agent_name: str) -> dict:
    prompt = parse_file(_REPO_ROOT / prompt_relpath)
    session = CompilationSession(prompt)
    compiled = session.compile_agent(agent_name)
    assert compiled.final_output is not None, (
        f"expected {agent_name} to have final_output metadata"
    )
    schema = compiled.final_output.lowered_schema
    assert isinstance(schema, dict), (
        f"expected lowered_schema for {agent_name} to be a dict, got {type(schema)!r}"
    )
    return schema


class EnumMigrationPreservationTests(unittest.TestCase):
    """The five Form A examples that emit a preservable enum field."""

    def test_example_79_repo_status_preserves_enum(self) -> None:
        schema = _lowered_schema_for(
            "examples/79_final_output_output_schema/prompts/AGENTS.prompt",
            "RepoStatusAgent",
        )
        self.assertEqual(
            schema["properties"]["status"]["enum"],
            ["ok", "action_required"],
        )
        self.assertEqual(schema["properties"]["status"]["type"], "string")

    def test_example_79_optional_no_example_preserves_enum(self) -> None:
        schema = _lowered_schema_for(
            "examples/79_final_output_output_schema/prompts/optional_no_example/AGENTS.prompt",
            "RepoStatusAgent",
        )
        self.assertEqual(
            schema["properties"]["status"]["enum"],
            ["ok", "action_required"],
        )
        self.assertEqual(schema["properties"]["status"]["type"], "string")

    def test_example_85_review_split_preserves_route_enum(self) -> None:
        schema = _lowered_schema_for(
            "examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt",
            "AcceptanceReviewSplitJsonDemo",
        )
        self.assertEqual(
            schema["properties"]["route"]["enum"],
            ["follow_up", "revise"],
        )
        self.assertEqual(schema["properties"]["route"]["type"], "string")

    def test_example_90_shared_route_semantics_preserves_route_enum(self) -> None:
        schema = _lowered_schema_for(
            "examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt",
            "ReviewSplitRouteFinalOutputDemo",
        )
        self.assertEqual(
            schema["properties"]["route"]["enum"],
            ["follow_up", "revise"],
        )
        self.assertEqual(schema["properties"]["route"]["type"], "string")

    def test_example_121_nullable_route_preserves_kind_enum(self) -> None:
        schema = _lowered_schema_for(
            "examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt",
            "WriterNullableRouteFieldFinalOutputDemo",
        )
        self.assertEqual(
            schema["properties"]["kind"]["enum"],
            ["handoff", "done"],
        )
        self.assertEqual(schema["properties"]["kind"]["type"], "string")


if __name__ == "__main__":
    unittest.main()
