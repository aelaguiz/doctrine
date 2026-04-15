from __future__ import annotations

from jsonschema import Draft202012Validator
from jsonschema import exceptions as jsonschema_exceptions

OPENAI_OUTPUT_SCHEMA_MAX_PROPERTIES = 100
OPENAI_OUTPUT_SCHEMA_MAX_NESTING = 5
OPENAI_OUTPUT_SCHEMA_MAX_ENUM_VALUES = 1000
OPENAI_OUTPUT_SCHEMA_MAX_TOTAL_STRING = 15000
OPENAI_OUTPUT_SCHEMA_LARGE_ENUM_THRESHOLD = 250
OPENAI_OUTPUT_SCHEMA_MAX_LARGE_ENUM_STRING = 7500
OPENAI_OUTPUT_SCHEMA_UNSUPPORTED_KEYWORDS = frozenset(
    {
        "allOf",
        "dependentRequired",
        "dependentSchemas",
        "else",
        "if",
        "not",
        "oneOf",
        "patternProperties",
        "then",
    }
)


class OutputSchemaValidationError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def validate_lowered_output_schema(
    schema_data: dict[str, object],
    *,
    owner_label: str,
) -> None:
    try:
        Draft202012Validator.check_schema(schema_data)
    except jsonschema_exceptions.SchemaError as exc:
        message = exc.message or str(exc)
        raise OutputSchemaValidationError(
            "E217",
            f"E217 final_output lowered schema failed Draft 2020-12 validation in {owner_label}: {message}",
        ) from exc
    validate_openai_structured_output_schema(schema_data, owner_label=owner_label)


def validate_output_example_instance(
    example_instance: object,
    schema_data: dict[str, object],
    *,
    owner_label: str,
) -> None:
    try:
        Draft202012Validator(schema_data).validate(example_instance)
    except jsonschema_exceptions.ValidationError as exc:
        message = exc.message or str(exc)
        raise OutputSchemaValidationError(
            "E216",
            f"E216 final_output example does not match lowered schema in {owner_label}: {message}",
        ) from exc


def validate_openai_structured_output_schema(
    schema_data: dict[str, object],
    *,
    owner_label: str,
) -> None:
    property_count = 0
    enum_count = 0
    total_string_size = 0

    def walk(node: object, *, path: str, depth: int, at_root: bool) -> None:
        nonlocal enum_count, property_count, total_string_size
        if not isinstance(node, dict):
            return

        unsupported = sorted(
            key for key in node.keys() if key in OPENAI_OUTPUT_SCHEMA_UNSUPPORTED_KEYWORDS
        )
        if unsupported:
            raise OutputSchemaValidationError(
                "E218",
                "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                f"{owner_label}: {path} uses unsupported keyword `{unsupported[0]}`",
            )

        if at_root:
            if "anyOf" in node:
                raise OutputSchemaValidationError(
                    "E218",
                    "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                    f"{owner_label}: root schema cannot use `anyOf`",
                )
            if not _json_schema_allows_type(node, "object"):
                raise OutputSchemaValidationError(
                    "E218",
                    "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                    f"{owner_label}: root schema must be an object",
                )

        if depth > OPENAI_OUTPUT_SCHEMA_MAX_NESTING:
            raise OutputSchemaValidationError(
                "E218",
                "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                f"{owner_label}: nesting exceeds {OPENAI_OUTPUT_SCHEMA_MAX_NESTING} levels at {path}",
            )

        properties = node.get("properties")
        if _json_schema_allows_type(node, "object"):
            if node.get("additionalProperties") is not False:
                raise OutputSchemaValidationError(
                    "E218",
                    "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                    f"{owner_label}: object schemas must set `additionalProperties: false` at {path}",
                )
            if isinstance(properties, dict):
                property_count += len(properties)
                total_string_size += sum(len(key) for key in properties.keys())
                if property_count > OPENAI_OUTPUT_SCHEMA_MAX_PROPERTIES:
                    raise OutputSchemaValidationError(
                        "E218",
                        "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                        f"{owner_label}: property count exceeds {OPENAI_OUTPUT_SCHEMA_MAX_PROPERTIES}",
                    )
                required = node.get("required")
                required_keys = (
                    list(required)
                    if isinstance(required, list) and all(isinstance(item, str) for item in required)
                    else None
                )
                if required_keys is None or required_keys != list(properties.keys()):
                    raise OutputSchemaValidationError(
                        "E218",
                        "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                        f"{owner_label}: object `required` must match property order at {path}",
                    )
                for field_name, field_schema in properties.items():
                    walk(
                        field_schema,
                        path=f"{path}.properties.{field_name}",
                        depth=depth + 1,
                        at_root=False,
                    )

        defs = node.get("$defs")
        if isinstance(defs, dict):
            total_string_size += sum(len(key) for key in defs.keys())
            for def_name, def_schema in defs.items():
                walk(
                    def_schema,
                    path=f"{path}.$defs.{def_name}",
                    depth=depth + 1,
                    at_root=False,
                )

        if _json_schema_allows_type(node, "array"):
            items = node.get("items")
            if not isinstance(items, dict):
                raise OutputSchemaValidationError(
                    "E218",
                    "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                    f"{owner_label}: array schemas must declare object `items` at {path}",
                )
            walk(
                items,
                path=f"{path}.items",
                depth=depth + 1,
                at_root=False,
            )

        any_of = node.get("anyOf")
        if isinstance(any_of, list):
            for index, branch in enumerate(any_of):
                walk(
                    branch,
                    path=f"{path}.anyOf[{index}]",
                    depth=depth + 1,
                    at_root=False,
                )

        enum_values = node.get("enum")
        if isinstance(enum_values, list):
            enum_count += len(enum_values)
            total_length = sum(len(str(value)) for value in enum_values)
            total_string_size += total_length
            if enum_count > OPENAI_OUTPUT_SCHEMA_MAX_ENUM_VALUES:
                raise OutputSchemaValidationError(
                    "E218",
                    "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                    f"{owner_label}: enum count exceeds {OPENAI_OUTPUT_SCHEMA_MAX_ENUM_VALUES}",
                )
            if (
                len(enum_values) > OPENAI_OUTPUT_SCHEMA_LARGE_ENUM_THRESHOLD
                and total_length > OPENAI_OUTPUT_SCHEMA_MAX_LARGE_ENUM_STRING
            ):
                raise OutputSchemaValidationError(
                    "E218",
                    "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                    f"{owner_label}: large enum string budget exceeds "
                    f"{OPENAI_OUTPUT_SCHEMA_MAX_LARGE_ENUM_STRING} characters at {path}",
                )

        if "const" in node:
            total_string_size += len(str(node["const"]))

        if total_string_size > OPENAI_OUTPUT_SCHEMA_MAX_TOTAL_STRING:
            raise OutputSchemaValidationError(
                "E218",
                "E218 final_output lowered schema is outside OpenAI structured outputs subset in "
                f"{owner_label}: schema string budget exceeds {OPENAI_OUTPUT_SCHEMA_MAX_TOTAL_STRING}",
            )

    walk(schema_data, path="root", depth=1, at_root=True)


def _json_schema_allows_type(schema_data: dict[str, object], target: str) -> bool:
    schema_type = schema_data.get("type")
    if schema_type == target:
        return True
    if isinstance(schema_type, list):
        return target in schema_type
    return False
