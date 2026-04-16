from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[3]
LARK_PATH = ROOT / "doctrine" / "grammars" / "doctrine.lark"
PACKAGE_PATH = ROOT / "editors" / "vscode" / "package.json"
LANGUAGE_CONFIG_PATH = ROOT / "editors" / "vscode" / "language-configuration.json"
TM_LANGUAGE_PATH = ROOT / "editors" / "vscode" / "syntaxes" / "doctrine.tmLanguage.json"

WORD_LITERAL_RE = re.compile(r'"([a-z_]+)"')
IDENTIFIER_LIKE_RE = re.compile(r"^[a-z_]+$")
EXTRA_GRAMMAR_KEYWORDS = {"important", "note", "required", "warning"}
GENERIC_KEY_STRING_KEYS = (
    "abstract",
    "agent",
    "import",
    "important",
    "inherit",
    "input",
    "json",
    "note",
    "output",
    "override",
    "required",
    "route",
    "schema",
    "shape",
    "skill",
    "skills",
    "source",
    "target",
    "structure",
    "use",
    "warning",
    "workflow",
)
GENERIC_STANDALONE_REFS = (
    "abstract",
    "agent",
    "import",
    "important",
    "inherit",
    "input",
    "json",
    "note",
    "output",
    "override",
    "required",
    "schema",
    "shape",
    "skill",
    "source",
    "target",
    "use",
    "warning",
    "workflow",
)


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
    return literals | EXTRA_GRAMMAR_KEYWORDS


def _missing_keywords(expected: set[str], regexes: list[str]) -> list[str]:
    missing: list[str] = []
    for keyword in sorted(expected):
        keyword_pattern = re.compile(rf"(?<![A-Za-z]){re.escape(keyword)}(?![A-Za-z])")
        if not any(keyword_pattern.search(regex_text) for regex_text in regexes):
            missing.append(keyword)
    return missing


def _require_pattern_match(
    repository: dict[str, object],
    pattern_name: str,
    samples: list[str],
    *,
    should_match: bool,
    errors: list[str],
) -> None:
    pattern = repository.get(pattern_name, {}).get("match")
    if not isinstance(pattern, str):
        errors.append(f"tmLanguage repository must define a `{pattern_name}` match pattern.")
        return
    compiled = re.compile(pattern)
    for sample in samples:
        matched = compiled.match(sample) is not None
        if matched != should_match:
            expectation = "match" if should_match else "reject"
            errors.append(
                f"`{pattern_name}` must {expectation} sample `{sample}`."
            )


def _require_begin_end_pattern(
    repository: dict[str, object],
    pattern_name: str,
    *,
    begin_samples: list[str],
    end_samples: list[str],
    errors: list[str],
) -> None:
    pattern = repository.get(pattern_name, {})
    begin = pattern.get("begin")
    end = pattern.get("end")
    if not isinstance(begin, str) or not isinstance(end, str):
        errors.append(
            f"tmLanguage repository must define `{pattern_name}` as a begin/end pattern."
        )
        return
    compiled_begin = re.compile(begin)
    compiled_end = re.compile(end)
    for sample in begin_samples:
        if compiled_begin.match(sample) is None:
            errors.append(f"`{pattern_name}` begin must match sample `{sample}`.")
    for sample in end_samples:
        if compiled_end.match(sample) is None:
            errors.append(f"`{pattern_name}` end must match sample `{sample}`.")


def main() -> int:
    package = _load_json(PACKAGE_PATH)
    language_config = _load_json(LANGUAGE_CONFIG_PATH)
    tm_language = _load_json(TM_LANGUAGE_PATH)

    errors: list[str] = []

    languages = package.get("contributes", {}).get("languages", [])
    grammars = package.get("contributes", {}).get("grammars", [])
    if not languages or languages[0].get("id") != "doctrine":
        errors.append("package.json must contribute the `doctrine` language id.")
    if not languages or ".prompt" not in languages[0].get("extensions", []):
        errors.append("package.json must associate the language with `.prompt` files.")
    if not grammars or grammars[0].get("scopeName") != "source.doctrine":
        errors.append("package.json must contribute the `source.doctrine` grammar scope.")
    if tm_language.get("scopeName") != "source.doctrine":
        errors.append("tmLanguage scopeName must stay `source.doctrine`.")
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

    repository = tm_language.get("repository", {})
    generic_key_string_samples = [f'    {keyword}: "X"' for keyword in GENERIC_KEY_STRING_KEYS]
    generic_key_ref_samples = [
        f"    {keyword}: shared.workflow.Opening" for keyword in GENERIC_KEY_STRING_KEYS
    ]
    generic_key_only_samples = [f"    {keyword}:" for keyword in GENERIC_KEY_STRING_KEYS]
    generic_standalone_ref_samples = [f"    {keyword}" for keyword in GENERIC_STANDALONE_REFS]

    _require_pattern_match(
        repository,
        "lawField",
        ["    law:"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "trustSurfaceField",
        ["    trust_surface:"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "lawKeyword",
        [
            "support_only",
            "rewrite_evidence",
            "route_from",
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "abstractField",
        ["    abstract workflow_core", "    abstract routing"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "abstractReview",
        ['abstract review SharedReview[shared.review.BaseReview]: "Review"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewDeclaration",
        ['review DraftReview[SharedReview]: "Review"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "analysisDeclaration",
        ['analysis SharedAnalysis[shared.analysis.BaseAnalysis]: "Analysis"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "schemaDeclaration",
        ['schema SharedSchema[shared.schema.BaseSchema]: "Schema"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "documentDeclaration",
        ['document SharedDocument[shared.document.BaseDocument]: "Document"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "skillsDeclaration",
        ['skills SharedSkills[shared.skills.BaseSkills]: "Skills"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "inputsDeclaration",
        ['inputs SharedInputs[shared.io.BaseInputs]: "Inputs"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "outputsDeclaration",
        ['outputs SharedOutputs[shared.io.BaseOutputs]: "Outputs"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "skillEntry",
        ["    skill grounding: shared.skills.GroundingSkill"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "ioFieldRef",
        ["    inputs: shared.io.BaseInputs", "    outputs: SharedOutputs"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "ioPatchField",
        ['    inputs[shared.io.BaseInputs]: "Inputs"', '    outputs[SharedOutputs]: "Outputs"'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "analysisField",
        ["    analysis: SharedAnalysis"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "skillsField",
        ['    skills: "Skills"', "    skills: shared.skills.SharedSkills"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewField",
        ["    review: DraftReview"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "finalOutputField",
        [
            "    final_output: FinalReply",
            "    final_output:",
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "finalOutputOutputField",
        ["        output: FinalReply"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "finalOutputRouteField",
        ["        route: next_route"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "outputSchemaRouteField",
        [
            '    route field next_route: "Next Route"',
            '    override route field next_route: "Next Route"',
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "outputSchemaRouteChoice",
        ['        seek_muse: "Send to Muse." -> Muse'],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewConfigFieldRef",
        [
            "    subject: DraftSpec",
            "    contract: DraftReviewContract",
            "    comment_output: DraftReviewComment",
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewSubjectMapField",
        ["    subject_map:"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewFieldsField",
        [
            "    fields:",
            "        review_fields:",
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "metadataField",
        ["    metadata:"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewOutcomeField",
        ['    on_accept: "If Accepted"', "    on_reject:"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewFieldBinding",
        [
            "        verdict: verdict",
            "        reviewed_artifact: reviewed_artifact",
            "        blocked_gate: failure_detail.blocked_gate",
            "        active_mode: active_mode",
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "readableBlockHeader",
        [
            '    section summary: "Summary"',
            '    sequence steps: "Steps"',
            '    bullets facts: "Facts"',
            '    checklist release: "Release"',
            '    definitions glossary: "Glossary"',
            '    table matrix: "Matrix"',
            '    callout warning_box: "Warning"',
            '    code snippet: "Snippet"',
            '    rule divider: "Divider"',
            '    gate requirements: "Requirements"',
            '    override section summary: "Updated Summary"',
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "reviewSemanticRef",
        ["contract.completeness", "fields.reviewed_artifact"],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "keyValueString",
        generic_key_string_samples,
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "guardedOutputHeader",
        [
            '    rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}:',
        ],
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "keyValueRef",
        generic_key_ref_samples,
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "keyOnly",
        generic_key_only_samples,
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "standaloneReference",
        generic_standalone_ref_samples,
        should_match=True,
        errors=errors,
    )
    _require_pattern_match(
        repository,
        "standaloneReference",
        ["    route"],
        should_match=False,
        errors=errors,
    )
    _require_begin_end_pattern(
        repository,
        "route",
        begin_samples=['    route "Keep the issue on RoutingOwner.'],
        end_samples=[
            '" -> RoutingOwner',
            '" -> RoutingOwner when RouteFacts.next_owner_unknown',
        ],
        errors=errors,
    )
    _require_begin_end_pattern(
        repository,
        "multilineStrings",
        begin_samples=['"""'],
        end_samples=['"""'],
        errors=errors,
    )

    if errors:
        print("Doctrine VS Code alignment check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Doctrine VS Code alignment check passed for "
        f"{len(expected_keywords)} shipped keywords."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
