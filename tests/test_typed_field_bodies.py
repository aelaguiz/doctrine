from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.resolve.field_types import BuiltinTypeRef, EnumTypeRef
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file


def _write_prompt(root: Path, source: str) -> Path:
    prompt_path = root / "prompts" / "AGENTS.prompt"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
    return prompt_path


def _resolve_document(source: str, name: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        prompt_path = _write_prompt(root, source)
        prompt = parse_file(prompt_path)
        session = CompilationSession(prompt)
        context = CompilationContext(session)
        unit = session.root_flow.entrypoint_unit
        decls = {d.name: d for d in unit.prompt_file.declarations if isinstance(d, model.DocumentDecl)}
        if name not in decls:
            raise AssertionError(f"Document {name} not found in unit")
        return context._resolve_document_decl(decls[name], unit=unit)


def _resolve_output(source: str, name: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        prompt_path = _write_prompt(root, source)
        prompt = parse_file(prompt_path)
        session = CompilationSession(prompt)
        context = CompilationContext(session)
        unit = session.root_flow.entrypoint_unit
        decls = {d.name: d for d in unit.prompt_file.declarations if isinstance(d, model.OutputDecl)}
        if name not in decls:
            raise AssertionError(f"Output {name} not found in unit")
        return context._resolve_output_decl_body(decls[name], unit=unit)


def _find_readable_block(body, key: str) -> model.ReadableBlock:
    for item in body.items:
        if isinstance(item, model.ReadableBlock) and item.key == key:
            return item
    raise AssertionError(f"ReadableBlock {key} not found")


def _find_table_column(block: model.ReadableBlock, column_key: str) -> model.ReadableTableColumn:
    payload = block.payload
    assert isinstance(payload, model.ReadableTableData), f"expected table payload, got {type(payload)}"
    for column in payload.columns:
        if column.key == column_key:
            return column
    raise AssertionError(f"Table column {column_key} not found")


def _find_row_schema_entry(block: model.ReadableBlock, entry_key: str) -> model.ReadableSchemaEntry:
    assert block.row_schema is not None, "block has no row_schema"
    for entry in block.row_schema.entries:
        if entry.key == entry_key:
            return entry
    raise AssertionError(f"Row schema entry {entry_key} not found")


def _find_item_schema_entry(block: model.ReadableBlock, entry_key: str) -> model.ReadableSchemaEntry:
    assert block.item_schema is not None, "block has no item_schema"
    for entry in block.item_schema.entries:
        if entry.key == entry_key:
            return entry
    raise AssertionError(f"Item schema entry {entry_key} not found")


def _find_record_scalar(output_decl: model.OutputDecl, key: str) -> model.RecordScalar:
    for item in output_decl.items:
        if isinstance(item, model.RecordScalar) and item.key == key:
            return item
    raise AssertionError(f"RecordScalar {key} not found")


class TypedFieldBodyRowSchemaTests(unittest.TestCase):
    def test_row_schema_entry_resolves_builtin_type(self) -> None:
        body = _resolve_document(
            """\
            document StatusDoc: "Status Doc"
                table StatusTable: "Status Table"
                    row_schema:
                        count: "Count"
                            type: integer
                            "How many items."
                    columns:
                        count: "Count"
                    rows:
                        first:
                            count: "1"
            """,
            "StatusDoc",
        )
        block = _find_readable_block(body, "StatusTable")
        entry = _find_row_schema_entry(block, "count")
        self.assertIsInstance(entry.type_ref, BuiltinTypeRef)
        self.assertEqual(entry.type_ref.name, "integer")

    def test_row_schema_entry_resolves_enum_type(self) -> None:
        body = _resolve_document(
            """\
            enum Status: "Status"
                ok: "OK"
                blocked: "Blocked"

            document StatusDoc: "Status Doc"
                table StatusTable: "Status Table"
                    row_schema:
                        status: "Status"
                            type: Status
                            "Current status."
                    columns:
                        status: "Status"
                    rows:
                        first:
                            status: "ok"
            """,
            "StatusDoc",
        )
        block = _find_readable_block(body, "StatusTable")
        entry = _find_row_schema_entry(block, "status")
        self.assertIsInstance(entry.type_ref, EnumTypeRef)
        self.assertEqual(entry.type_ref.decl.name, "Status")

    def test_row_schema_entry_unknown_type_raises_E320(self) -> None:
        with self.assertRaises(CompileError) as ctx:
            _resolve_document(
                """\
                document StatusDoc: "Status Doc"
                    table StatusTable: "Status Table"
                        row_schema:
                            status: "Status"
                                type: Nope
                                "Bad."
                        columns:
                            status: "Status"
                        rows:
                            first:
                                status: "ok"
                """,
                "StatusDoc",
            )
        self.assertEqual(ctx.exception.diagnostic.code, "E320")


class TypedFieldBodyItemSchemaTests(unittest.TestCase):
    def test_item_schema_entry_resolves_enum_type(self) -> None:
        body = _resolve_document(
            """\
            enum Status: "Status"
                ok: "OK"
                blocked: "Blocked"

            document ChecklistDoc: "Checklist Doc"
                sequence ThingsList: "Things"
                    item_schema:
                        state: "State"
                            type: Status
                            "State of the item."

                    first: "Take the first step."
                    second: "Take the second step."
            """,
            "ChecklistDoc",
        )
        block = _find_readable_block(body, "ThingsList")
        entry = _find_item_schema_entry(block, "state")
        self.assertIsInstance(entry.type_ref, EnumTypeRef)
        self.assertEqual(entry.type_ref.decl.name, "Status")


class TypedFieldBodyTableColumnTests(unittest.TestCase):
    def test_table_column_resolves_builtin_type(self) -> None:
        body = _resolve_document(
            """\
            document StatusDoc: "Status Doc"
                table StatusTable: "Status Table"
                    columns:
                        count: "Count"
                            type: integer
                            "How many items."
                    rows:
                        first:
                            count: "1"
            """,
            "StatusDoc",
        )
        block = _find_readable_block(body, "StatusTable")
        column = _find_table_column(block, "count")
        self.assertIsInstance(column.type_ref, BuiltinTypeRef)
        self.assertEqual(column.type_ref.name, "integer")

    def test_table_column_resolves_enum_type(self) -> None:
        body = _resolve_document(
            """\
            enum Status: "Status"
                ok: "OK"
                blocked: "Blocked"

            document StatusDoc: "Status Doc"
                table StatusTable: "Status Table"
                    columns:
                        status: "Status"
                            type: Status
                            "Column status."
                    rows:
                        first:
                            status: "ok"
            """,
            "StatusDoc",
        )
        block = _find_readable_block(body, "StatusTable")
        column = _find_table_column(block, "status")
        self.assertIsInstance(column.type_ref, EnumTypeRef)
        self.assertEqual(column.type_ref.decl.name, "Status")

    def test_table_column_unknown_type_raises_E320(self) -> None:
        with self.assertRaises(CompileError) as ctx:
            _resolve_document(
                """\
                document StatusDoc: "Status Doc"
                    table StatusTable: "Status Table"
                        columns:
                            status: "Status"
                                type: Nope
                                "Bad."
                        rows:
                            first:
                                status: "ok"
                """,
                "StatusDoc",
            )
        self.assertEqual(ctx.exception.diagnostic.code, "E320")


class TypedFieldBodyRecordScalarTests(unittest.TestCase):
    def test_output_record_scalar_resolves_builtin_type(self) -> None:
        decl = _resolve_output(
            """\
            output shape ShapeOne: "Shape One"
                kind: JsonObject

            output ShapeResponse: "Shape Response"
                target: TurnResponse
                shape: ShapeOne
                requirement: Required
                summary: "One-line summary."
                    type: string
            """,
            "ShapeResponse",
        )
        scalar = _find_record_scalar(decl, "summary")
        self.assertIsInstance(scalar.type_ref, BuiltinTypeRef)
        self.assertEqual(scalar.type_ref.name, "string")

    def test_output_record_scalar_resolves_enum_type(self) -> None:
        decl = _resolve_output(
            """\
            enum Verdict: "Verdict"
                accept: "Accept"
                reject: "Reject"

            output shape ShapeOne: "Shape One"
                kind: JsonObject

            output ReviewResponse: "Review Response"
                target: TurnResponse
                shape: ShapeOne
                requirement: Required
                verdict: "Review verdict"
                    type: Verdict
            """,
            "ReviewResponse",
        )
        scalar = _find_record_scalar(decl, "verdict")
        self.assertIsInstance(scalar.type_ref, EnumTypeRef)
        self.assertEqual(scalar.type_ref.decl.name, "Verdict")

    def test_output_record_scalar_unknown_type_raises_E320(self) -> None:
        with self.assertRaises(CompileError) as ctx:
            _resolve_output(
                """\
                output shape ShapeOne: "Shape One"
                    kind: JsonObject

                output BadResponse: "Bad Response"
                    target: TurnResponse
                    shape: ShapeOne
                    requirement: Required
                    note: "Bad note"
                        type: Nope
                """,
                "BadResponse",
            )
        self.assertEqual(ctx.exception.diagnostic.code, "E320")


if __name__ == "__main__":
    unittest.main()
