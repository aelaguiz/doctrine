from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown


class TableDeclarationTests(unittest.TestCase):
    def _compile_agent(
        self,
        source: str,
        *,
        agent_name: str = "Demo",
        extra_files: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            for rel_path, contents in (extra_files or {}).items():
                target_path = root / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(textwrap.dedent(contents), encoding="utf-8")
            prompt = parse_file(prompt_path)
            return CompilationSession(prompt).compile_agent(agent_name)

    def _compile_error(self, source: str) -> Exception:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            with self.assertRaises(Exception) as caught:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")
            return caught.exception

    def test_parses_top_level_table_and_named_document_use(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """
                table ReleaseGates: "Release Gates"
                    columns:
                        gate: "Gate"
                            "What must pass before shipment."

                document ReleaseGuide: "Release Guide"
                    table release_gates: ReleaseGates required
                """
            )
        )

        table_decl = prompt.declarations[0]
        document_decl = prompt.declarations[1]
        self.assertEqual(type(table_decl).__name__, "TableDecl")
        self.assertEqual(table_decl.name, "ReleaseGates")
        self.assertEqual(table_decl.table.columns[0].title, "Gate")
        self.assertEqual(document_decl.body.items[0].payload.table_ref.declaration_name, "ReleaseGates")

    def test_named_use_renders_same_row_backed_table_shape_as_inline_tables(self) -> None:
        agent = self._compile_agent(
            """
            table ReleaseGates: "Release Gates"
                columns:
                    gate: "Gate"
                        "What must pass before shipment."

                    evidence: "Evidence"
                        "What proves the gate passed."

            document ReleaseGuide: "Release Guide"
                table release_gates: ReleaseGates required
                    rows:
                        release_notes:
                            gate: "Release notes"
                            evidence: "Linked to the shipped proof."

                        package_smoke:
                            gate: "Package smoke"
                            evidence: "`make verify-package` passed."

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )

        rendered = render_markdown(agent)
        self.assertIn("| **Release Gates** | Table | Use the columns `Gate` and `Evidence`. |", rendered)
        self.assertIn("##### Release Gates Contract", rendered)
        self.assertIn("_Required · table_", rendered)
        self.assertIn("| Gate | Evidence |", rendered)
        self.assertIn("| Release notes | Linked to the shipped proof. |", rendered)
        self.assertIn("| Package smoke | `make verify-package` passed. |", rendered)

    def test_empty_named_use_renders_current_contract_table_shape(self) -> None:
        agent = self._compile_agent(
            """
            table ReleaseGates: "Release Gates"
                columns:
                    gate: "Gate"
                        "What must pass before shipment."

                    evidence: "Evidence"
                        "What proves the gate passed."

            document ReleaseGuide: "Release Guide"
                table release_gates: ReleaseGates advisory

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )

        rendered = render_markdown(agent)
        self.assertIn("##### Release Gates Contract", rendered)
        self.assertIn("_Advisory · table_", rendered)
        self.assertIn("| Column | Meaning |", rendered)
        self.assertIn("| Gate | What must pass before shipment. |", rendered)
        self.assertIn("| Evidence | What proves the gate passed. |", rendered)

    def test_addressable_paths_work_on_declaration_and_document_local_table(self) -> None:
        agent = self._compile_agent(
            """
            table ReleaseGates: "Release Gates"
                columns:
                    gate: "Gate"
                        "What must pass before shipment."

                    evidence: "Evidence"
                        "What proves the gate passed."

            document ReleaseGuide: "Release Guide"
                table release_gates: ReleaseGates required
                    rows:
                        package_smoke:
                            gate: "Package smoke"
                            evidence: "`make verify-package` passed."

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

                notes: "Notes"
                    "Declaration column: {{ ReleaseGates:columns.evidence.title }}."
                    "Local column: {{ ReleaseGuide:release_gates.columns.evidence.title }}."
                    "Local row: {{ ReleaseGuide:release_gates.rows.package_smoke }}."

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )

        rendered = render_markdown(agent)
        self.assertIn("Declaration column: Evidence.", rendered)
        self.assertIn("Local column: Evidence.", rendered)
        self.assertIn("Local row: Package Smoke.", rendered)

    def test_imported_table_refs_resolve_like_other_named_declarations(self) -> None:
        agent = self._compile_agent(
            """
            import shared.tables

            document ReleaseGuide: "Release Guide"
                table release_gates: shared.tables.ReleaseGates required
                    rows:
                        release_notes:
                            gate: "Release notes"
                            evidence: "Linked to the shipped proof."

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """,
            extra_files={
                "prompts/shared/tables.prompt": """
                table ReleaseGates: "Release Gates"
                    columns:
                        gate: "Gate"
                            "What must pass before shipment."

                        evidence: "Evidence"
                            "What proves the gate passed."
                """
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("| **Release Gates** | Table | Use the columns `Gate` and `Evidence`. |", rendered)
        self.assertIn("| Release notes | Linked to the shipped proof. |", rendered)

    def test_named_override_table_uses_existing_table_override_kind(self) -> None:
        agent = self._compile_agent(
            """
            table ReleaseGates: "Release Gates"
                columns:
                    gate: "Gate"
                        "What must pass before shipment."

                    evidence: "Evidence"
                        "What proves the gate passed."

            document BaseGuide: "Base Guide"
                table release_gates: "Old Release Gates" required
                    columns:
                        old: "Old"
                            "Old column."

            document ReleaseGuide [BaseGuide]: "Release Guide"
                override table release_gates: ReleaseGates required
                    rows:
                        release_notes:
                            gate: "Release notes"
                            evidence: "Linked to the shipped proof."

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )

        rendered = render_markdown(agent)
        self.assertIn("| **Release Gates** | Table | Use the columns `Gate` and `Evidence`. |", rendered)
        self.assertIn("| Release notes | Linked to the shipped proof. |", rendered)
        self.assertNotIn("Old Release Gates", rendered)

    def test_row_schema_and_structured_cells_work_on_named_tables(self) -> None:
        agent = self._compile_agent(
            """
            table ReleaseGates: "Release Gates"
                row_schema:
                    owner: "Owner"
                        "Name the owner for this gate."

                columns:
                    gate: "Gate"
                        "What must pass before shipment."

                    evidence: "Evidence"
                        "What proves the gate passed."

            document ReleaseGuide: "Release Guide"
                table release_gates: ReleaseGates required
                    rows:
                        package_smoke:
                            gate: "Package smoke"
                            evidence:
                                bullets proof_points: "Proof Points"
                                    "Run `make verify-package`."

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

                notes: "Notes"
                    "Row schema: {{ ReleaseGuide:release_gates.row_schema.owner.title }}."

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )

        rendered = render_markdown(agent)
        self.assertIn("###### Package Smoke", rendered)
        self.assertIn("####### Evidence", rendered)
        self.assertIn("- Run `make verify-package`.", rendered)
        self.assertIn("Row schema: Owner.", rendered)

    def test_wrong_kind_and_missing_table_refs_fail_loud(self) -> None:
        wrong_kind = self._compile_error(
            """
            document NotATable: "Not A Table"
                section intro: "Intro"
                    "Body."

            document ReleaseGuide: "Release Guide"
                table release_gates: NotATable required

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )
        self.assertIn("expects a table declaration", str(wrong_kind))
        self.assertIn("document declaration", str(wrong_kind))

        missing = self._compile_error(
            """
            document ReleaseGuide: "Release Guide"
                table release_gates: MissingTable required

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )
        self.assertIn("Missing local table declaration: MissingTable", str(missing))

    def test_invalid_table_ownership_fails_during_parse(self) -> None:
        with self.assertRaises(Exception) as named_use_error:
            parse_text(
                textwrap.dedent(
                    """
                    table ReleaseGates: "Release Gates"
                        columns:
                            gate: "Gate"

                    document ReleaseGuide: "Release Guide"
                        table release_gates: ReleaseGates required
                            columns:
                                gate: "Gate"
                    """
                ),
                source_path="/tmp/invalid-named-table-use.prompt",
            )
        self.assertIn("Named table uses may define only `rows:` and `notes:`", str(named_use_error.exception))

        with self.assertRaises(Exception) as declaration_error:
            parse_text(
                textwrap.dedent(
                    """
                    table ReleaseGates: "Release Gates"
                        columns:
                            gate: "Gate"
                        rows:
                            release_notes:
                                gate: "Release notes"
                    """
                ),
                source_path="/tmp/invalid-table-declaration.prompt",
            )
        self.assertIn("Table declarations may not define `rows:`", str(declaration_error.exception))

    def test_duplicate_table_declaration_names_fail_loud(self) -> None:
        error = self._compile_error(
            """
            table ReleaseGates: "Release Gates"
                columns:
                    gate: "Gate"

            table ReleaseGates: "Duplicate Release Gates"
                columns:
                    gate: "Gate"

            document ReleaseGuide: "Release Guide"
                table release_gates: ReleaseGates required

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """
        )
        error_text = str(error)
        self.assertIn("E288 compile error: Duplicate declaration name", error_text)
        self.assertIn("Declaration `ReleaseGates` is defined more than once", error_text)
        self.assertIn("Related:", error_text)


if __name__ == "__main__":
    unittest.main()
