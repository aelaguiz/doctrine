from __future__ import annotations

import types
import unittest
from pathlib import Path

from doctrine import model
from doctrine._compiler.resolve.field_types import (
    BUILTIN_TYPE_NAMES,
    BuiltinTypeRef,
    EnumTypeRef,
    resolve_field_type_ref,
)
from doctrine._model.core import SourceSpan
from doctrine.diagnostics import CompileError


def _fake_unit(path: str = "/tmp/doctrine-field-types-test.prompt") -> object:
    return types.SimpleNamespace(
        prompt_file=types.SimpleNamespace(source_path=Path(path)),
    )


def _enum(name: str, *member_keys: str) -> model.EnumDecl:
    members = tuple(
        model.EnumMember(key=key, title=key.replace("_", " ").title())
        for key in member_keys
    )
    return model.EnumDecl(name=name, title=name, members=members)


class FieldTypeRefTests(unittest.TestCase):
    def test_each_builtin_name_resolves_to_builtin_type_ref(self) -> None:
        for name in ("array", "boolean", "integer", "null", "number", "object", "string"):
            with self.subTest(name=name):
                ref = resolve_field_type_ref(
                    name,
                    span=SourceSpan(1, 1),
                    unit=_fake_unit(),
                    lookup_enum=lambda _ref, *, unit: None,
                )
                self.assertIsInstance(ref, BuiltinTypeRef)
                self.assertEqual(ref.name, name)

    def test_builtin_set_is_exactly_seven_names(self) -> None:
        self.assertEqual(
            BUILTIN_TYPE_NAMES,
            frozenset({"array", "boolean", "integer", "null", "number", "object", "string"}),
        )

    def test_same_unit_enum_name_resolves_to_enum_type_ref(self) -> None:
        enum_decl = _enum("StepRole", "introduce", "practice", "test", "capstone")
        captured_refs: list[model.NameRef] = []

        def lookup(ref: model.NameRef, *, unit: object) -> model.EnumDecl | None:
            captured_refs.append(ref)
            return enum_decl if ref.declaration_name == "StepRole" else None

        result = resolve_field_type_ref(
            "StepRole",
            span=SourceSpan(3, 5),
            unit=_fake_unit(),
            lookup_enum=lookup,
        )

        self.assertIsInstance(result, EnumTypeRef)
        self.assertIs(result.decl, enum_decl)
        self.assertEqual(result.ref.declaration_name, "StepRole")
        self.assertEqual(result.ref.module_parts, ())
        self.assertEqual(result.ref.source_span, SourceSpan(3, 5))
        self.assertEqual(len(captured_refs), 1)

    def test_imported_enum_name_resolves_through_lookup_callable(self) -> None:
        # The helper is callable-agnostic: whether the enum lives in the same
        # unit or in an imported flow is the lookup callable's concern. The
        # helper cares only that a non-None EnumDecl came back.
        imported_decl = _enum("Imported", "a", "b")

        def lookup(_ref: model.NameRef, *, unit: object) -> model.EnumDecl | None:
            return imported_decl

        result = resolve_field_type_ref(
            "Imported",
            span=SourceSpan(10, 2),
            unit=_fake_unit(),
            lookup_enum=lookup,
        )

        self.assertIsInstance(result, EnumTypeRef)
        self.assertIs(result.decl, imported_decl)

    def test_non_enum_decl_raises_e320(self) -> None:
        # A lookup callable that returns None models both "the name resolves to
        # a non-enum decl" and "the name does not resolve anywhere". The helper
        # raises E320 in both cases.
        with self.assertRaises(CompileError) as ctx:
            resolve_field_type_ref(
                "MyTable",
                span=SourceSpan(5, 10),
                unit=_fake_unit(),
                lookup_enum=lambda _ref, *, unit: None,
            )

        self.assertEqual(ctx.exception.diagnostic.code, "E320")
        self.assertIn("MyTable", ctx.exception.diagnostic.detail or "")

    def test_unknown_name_raises_e320(self) -> None:
        with self.assertRaises(CompileError) as ctx:
            resolve_field_type_ref(
                "Whatever",
                span=SourceSpan(7, 3),
                unit=_fake_unit(),
                lookup_enum=lambda _ref, *, unit: None,
            )

        self.assertEqual(ctx.exception.diagnostic.code, "E320")

    def test_e320_carries_cname_source_span(self) -> None:
        span = SourceSpan(42, 7)
        with self.assertRaises(CompileError) as ctx:
            resolve_field_type_ref(
                "Oops",
                span=span,
                unit=_fake_unit(),
                lookup_enum=lambda _ref, *, unit: None,
            )

        location = ctx.exception.diagnostic.location
        self.assertEqual(location.line, 42)
        self.assertEqual(location.column, 7)


if __name__ == "__main__":
    unittest.main()
