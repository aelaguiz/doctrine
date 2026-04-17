from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from doctrine._compiler.output_schema_validation import (
    OutputSchemaValidationError,
    validate_lowered_output_schema,
)
from doctrine.validate_output_schema import OutputSchemaFileError, load_schema_file


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    try:
        schema_path = Path(args.schema).resolve()
        schema_data = load_schema_file(schema_path)
        owner_label = args.owner_label or f"schema file {schema_path}"
        validate_lowered_output_schema(schema_data, owner_label=owner_label)

        client = _new_openai_client()
        schema_name = args.name or _schema_name_from_path(schema_path)
        response = client.responses.create(
            model=args.model,
            input=args.prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": schema_data,
                    "strict": True,
                }
            },
        )
        print(f"accepted {schema_path} with model {args.model} as schema `{schema_name}`")
        response_id = getattr(response, "id", None)
        if isinstance(response_id, str) and response_id:
            print(f"response_id: {response_id}")
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text:
            print(output_text)
        return 0
    except (LiveOpenAIProofError, OutputSchemaFileError, OutputSchemaValidationError) as exc:
        print(exc, file=sys.stderr)
        return 1


class LiveOpenAIProofError(RuntimeError):
    pass


def _new_openai_client() -> object:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LiveOpenAIProofError(
            "OPENAI_API_KEY is not set. Run this proof with a real OpenAI API key."
        )
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise LiveOpenAIProofError(
            "The official `openai` SDK is not installed. Run this proof with "
            "`uv run --with openai python -m doctrine.prove_output_schema_openai ...`."
        ) from exc
    return OpenAI(api_key=api_key)


def _schema_name_from_path(path: Path) -> str:
    if path.name.endswith(".schema.json"):
        return path.name[: -len(".schema.json")]
    return path.stem.replace(".", "_")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Submit one emitted Doctrine structured-output schema file to the official OpenAI "
            "Responses API as a live acceptance check."
        )
    )
    parser.add_argument(
        "--schema",
        required=True,
        help="Path to the emitted schema JSON file.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="OpenAI model name used for the live proof request.",
    )
    parser.add_argument(
        "--name",
        help="Optional schema name override. Defaults to the schema filename stem.",
    )
    parser.add_argument(
        "--prompt",
        default="Return the smallest valid JSON object that matches this schema.",
        help="Prompt text used for the live proof request.",
    )
    parser.add_argument(
        "--owner-label",
        help="Optional owner label used in validator messages before the API call.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
