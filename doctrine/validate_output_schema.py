from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from doctrine._compiler.output_schema_validation import (
    OutputSchemaValidationError,
    validate_lowered_output_schema,
    validate_output_example_instance,
)


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    try:
        schema_path = Path(args.schema).resolve()
        schema_data = load_schema_file(schema_path)
        owner_label = args.owner_label or f"schema file {schema_path}"
        validate_lowered_output_schema(schema_data, owner_label=owner_label)
        if args.example is not None:
            example_path = Path(args.example).resolve()
            example_data = load_json_file(example_path, label="example file")
            validate_output_example_instance(
                example_data,
                schema_data,
                owner_label=owner_label,
            )
            print(
                f"validated {schema_path} and {example_path} against the OpenAI structured-output subset"
            )
        else:
            print(f"validated {schema_path} against the OpenAI structured-output subset")
        return 0
    except (OutputSchemaFileError, OutputSchemaValidationError) as exc:
        print(exc, file=sys.stderr)
        return 1


def load_schema_file(path: Path) -> dict[str, object]:
    payload = load_json_file(path, label="schema file")
    if not isinstance(payload, dict):
        raise OutputSchemaFileError(f"schema file must contain one JSON object: {path}")
    return payload


def load_json_file(path: Path, *, label: str) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise OutputSchemaFileError(f"{label} does not exist: {path}") from exc
    except OSError as exc:
        raise OutputSchemaFileError(f"{label} is unreadable: {path}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise OutputSchemaFileError(f"{label} is not valid JSON: {path}") from exc


class OutputSchemaFileError(RuntimeError):
    pass


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate one emitted Doctrine structured-output schema file against Draft 2020-12 "
            "and Doctrine's OpenAI structured-output subset checks."
        )
    )
    parser.add_argument(
        "--schema",
        required=True,
        help="Path to the emitted schema JSON file.",
    )
    parser.add_argument(
        "--example",
        help="Optional path to one JSON instance file to validate against the schema.",
    )
    parser.add_argument(
        "--owner-label",
        help="Optional owner label used in validator messages.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
