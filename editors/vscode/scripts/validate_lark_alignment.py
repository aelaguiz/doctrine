from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[3]
LARK_PATH = ROOT / "pyprompt" / "grammars" / "pyprompt.lark"
PACKAGE_PATH = ROOT / "editors" / "vscode" / "package.json"
LANGUAGE_CONFIG_PATH = ROOT / "editors" / "vscode" / "language-configuration.json"
TM_LANGUAGE_PATH = ROOT / "editors" / "vscode" / "syntaxes" / "pyprompt.tmLanguage.json"

WORD_LITERAL_RE = re.compile(r'"([a-z]+)"')
IDENTIFIER_LIKE_RE = re.compile(r"^[a-z]+$")


def _iter_regex_strings(node: object) -> Iterator[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in {"match", "begin", "end"} and isinstance(value, str):
                yield value
            else:
                yield from _iter_regex_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_regex_strings(value)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text())


def _grammar_keywords() -> set[str]:
    literals = {
        literal
        for literal in WORD_LITERAL_RE.findall(LARK_PATH.read_text())
        if IDENTIFIER_LIKE_RE.fullmatch(literal)
    }
    return literals


def _missing_keywords(expected: set[str], regexes: list[str]) -> list[str]:
    missing: list[str] = []
    for keyword in sorted(expected):
        keyword_pattern = re.compile(rf"(?<![A-Za-z]){re.escape(keyword)}(?![A-Za-z])")
        if not any(keyword_pattern.search(regex_text) for regex_text in regexes):
            missing.append(keyword)
    return missing


def main() -> int:
    package = _load_json(PACKAGE_PATH)
    language_config = _load_json(LANGUAGE_CONFIG_PATH)
    tm_language = _load_json(TM_LANGUAGE_PATH)

    errors: list[str] = []

    languages = package.get("contributes", {}).get("languages", [])
    grammars = package.get("contributes", {}).get("grammars", [])
    if not languages or languages[0].get("id") != "pyprompt":
        errors.append("package.json must contribute the `pyprompt` language id.")
    if not languages or ".prompt" not in languages[0].get("extensions", []):
        errors.append("package.json must associate the language with `.prompt` files.")
    if not grammars or grammars[0].get("scopeName") != "source.pyprompt":
        errors.append("package.json must contribute the `source.pyprompt` grammar scope.")
    if tm_language.get("scopeName") != "source.pyprompt":
        errors.append("tmLanguage scopeName must stay `source.pyprompt`.")
    if language_config.get("comments", {}).get("lineComment") != "#":
        errors.append("language-configuration.json must keep `#` as the line comment token.")
    if language_config.get("folding", {}).get("offSide") is not True:
        errors.append("language-configuration.json must keep off-side folding enabled.")

    expected_keywords = _grammar_keywords()
    regex_strings = list(_iter_regex_strings(tm_language))
    missing_keywords = _missing_keywords(expected_keywords, regex_strings)
    if missing_keywords:
        errors.append(
            "tmLanguage regex coverage is missing shipped Lark keywords: "
            + ", ".join(missing_keywords)
        )

    if not any("#" in regex_text for regex_text in regex_strings):
        errors.append("tmLanguage regex coverage must include a `#` comment rule.")
    if not any("->" in regex_text for regex_text in regex_strings):
        errors.append("tmLanguage regex coverage must include the route arrow operator.")

    if errors:
        print("PyPrompt VS Code alignment check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "PyPrompt VS Code alignment check passed for "
        f"{len(expected_keywords)} shipped keywords."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
