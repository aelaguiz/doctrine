from __future__ import annotations

from lark import Token, Tree
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
)

def _extract_tree_position(obj: object) -> tuple[int | None, int | None]:
    if isinstance(obj, Token):
        return getattr(obj, "line", None), getattr(obj, "column", None)
    if isinstance(obj, Tree):
        for child in obj.children:
            line, column = _extract_tree_position(child)
            if line is not None:
                return line, column
    return None, None


def _extract_toml_decode_position(
    source: str,
    pos: int | None,
) -> tuple[int | None, int | None]:
    if pos is None:
        return None, None
    bounded_pos = max(0, min(pos, len(source)))
    prefix = source[:bounded_pos]
    line = prefix.count("\n") + 1
    last_newline = prefix.rfind("\n")
    if last_newline == -1:
        column = bounded_pos + 1
    else:
        column = bounded_pos - last_newline
    return line, column


def _classify_unexpected_token(
    exc: UnexpectedToken,
) -> tuple[str, str, tuple[str, ...]]:
    previous = exc.token_history[-1] if exc.token_history else None
    expected = set(exc.expected or ())
    token_value = exc.token.value
    if previous is not None and previous.type == "ROUTE" and exc.token.value == "->":
        return (
            "E131",
            "Missing route label",
            ("Add a quoted route label before `->`.",),
        )
    if "CNAME" in expected and exc.token.type == "_NL":
        return (
            "E132",
            "Missing route target",
            ("Add an explicit agent target after `->`.",),
        )
    if _is_review_statement_placement_error(token_value=token_value, expected=expected):
        return (
            "E471",
            "Illegal statement placement in review body",
            (
                "Keep `block`, `reject`, `accept`, `preserve`, `support_only`, and `ignore` in named pre-outcome review sections.",
                "Keep `current`, `carry`, and `route` inside `on_accept:` or `on_reject:` only.",
            ),
        )
    if previous is not None and previous.type == "ELSE" and token_value == "when":
        return (
            "E472",
            "Invalid guarded match head",
            (
                "Use `else:` for the fallback arm, or move the guard onto an explicit non-else match head.",
            ),
        )
    if "VIA" in expected:
        return (
            "E133",
            "Missing `via` carrier",
            ("Add `via Output.field` after the current artifact or invalidation target.",),
        )
    token_type = exc.token.type
    if token_type == "_INDENT":
        return (
            "E104",
            "Unexpected indented block",
            ("Indent this block only after a declaration line that opens a nested body.",),
        )
    if token_type == "_DEDENT":
        return (
            "E104",
            "Unexpected dedent",
            ("Keep indentation aligned with the current block structure.",),
        )
    if token_type == "_NL":
        return (
            "E101",
            "Unexpected newline",
            ("Finish the current declaration before starting a new line.",),
        )
    return (
        "E101",
        "Unexpected token",
        ("Check the expected token list and the surrounding punctuation.",),
    )


def _is_review_statement_placement_error(
    *,
    token_value: str,
    expected: set[str],
) -> bool:
    illegal_pre_outcome_tokens = {
        "block",
        "reject",
        "accept",
        "preserve",
        "support_only",
        "ignore",
    }
    illegal_outcome_tokens = {"current", "carry", "route"}
    pre_outcome_expected_tokens = {
        "ACCEPT",
        "BLOCK",
        "IGNORE",
        "PRESERVE",
        "REJECT",
        "SUPPORT_ONLY",
    }
    outcome_expected_tokens = {"CARRY", "CURRENT", "ROUTE"}
    return (
        token_value in illegal_pre_outcome_tokens
        and bool(expected & outcome_expected_tokens)
    ) or (
        token_value in illegal_outcome_tokens
        and bool(expected & pre_outcome_expected_tokens)
    )


def _format_unexpected_token_cause(exc: UnexpectedToken) -> str:
    token = exc.token
    token_value = token.value.replace("\n", "\\n")
    parts = [f"Unexpected token `{token.type}` with value `{token_value}`."]
    expected = _format_expected_tokens(exc.expected)
    if expected:
        parts.append(expected)
    return " ".join(parts)


def _format_expected_tokens(expected: set[str] | list[str] | None) -> str | None:
    if not expected:
        return None
    normalized = ", ".join(f"`{token}`" for token in sorted(expected))
    return f"Expected one of: {normalized}."


def _format_parse_detail(exc: UnexpectedInput) -> str:
    if isinstance(exc, UnexpectedToken):
        token_type = exc.token.type
        if token_type == "_NL":
            return "The parser hit a line break where the current grammar still expected more input."
        if token_type == "_INDENT":
            return "The parser entered an indented block that is not valid at this point in the grammar."
        if token_type == "_DEDENT":
            return "The parser left an indented block before the current declaration was complete."
    if isinstance(exc, UnexpectedCharacters):
        return "The parser hit a character that does not belong to any token on this surface."
    if isinstance(exc, UnexpectedEOF):
        return "The file ended before the current declaration or block was complete."
    return "The parser could not match the current source against the shipped grammar."

