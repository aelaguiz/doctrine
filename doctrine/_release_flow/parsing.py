from __future__ import annotations

from pathlib import Path
import re

from doctrine._package_release import load_package_release_metadata
from doctrine._release_flow.common import release_error, run_checked
from doctrine._release_flow.models import (
    CHANGELOG_SECTION_RE,
    CURRENT_LANGUAGE_VERSION_RE,
    HEADER_FIELD_ORDER,
    LANGUAGE_VERSION_RE,
    ChangelogSection,
    LanguageVersion,
    ReleaseEntry,
    ReleaseTag,
    language_header_value,
)

LANGUAGE_HEADER_RE = re.compile(
    r"^(?:unchanged \(still (?P<same>\d+\.\d+)\)|(?P<from>\d+\.\d+) -> (?P<to>\d+\.\d+))$"
)
PLACEHOLDER_SUBSTRINGS = (
    "fill this in",
    "update for this release",
    "tbd",
    "todo",
    "placeholder",
)
PLACEHOLDER_VALUES = {"...", "n/a", "na", "pending"}


def repo_root() -> Path:
    completed = run_checked(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path.cwd(),
        code="E527",
        summary="Release tag preflight failed",
        detail="Could not resolve the repo root from git.",
    )
    return Path(completed.stdout.strip()).resolve()


def load_current_language_version(repo_root: Path) -> LanguageVersion:
    versioning_path = repo_root / "docs" / "VERSIONING.md"
    try:
        text = versioning_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise release_error(
            "E523",
            "Missing current language version",
            "`docs/VERSIONING.md` is missing, so Doctrine cannot read the current language version.",
            location=versioning_path,
        ) from exc
    match = CURRENT_LANGUAGE_VERSION_RE.search(text)
    if match is None:
        raise release_error(
            "E523",
            "Missing current language version",
            "`docs/VERSIONING.md` must contain one `Current Doctrine language version:` line.",
            location=versioning_path,
        )
    return parse_language_version(match.group("version"), location=versioning_path)


def load_package_metadata_version(repo_root: Path) -> str:
    try:
        return load_package_release_metadata(repo_root).version
    except RuntimeError as exc:
        raise release_error(
            "E530",
            "Release package metadata version is missing or does not match",
            str(exc),
            location=repo_root / "pyproject.toml",
        ) from exc


def expected_package_metadata_version(release_tag: ReleaseTag) -> str:
    base = f"{release_tag.major}.{release_tag.minor}.{release_tag.patch}"
    if release_tag.channel == "stable":
        return base
    if release_tag.channel == "beta":
        assert release_tag.prerelease_number is not None
        return f"{base}b{release_tag.prerelease_number}"
    assert release_tag.prerelease_number is not None
    return f"{base}rc{release_tag.prerelease_number}"


def describe_package_metadata_status(
    *,
    current_version: str,
    requested_tag: ReleaseTag,
) -> str:
    expected_version = expected_package_metadata_version(requested_tag)
    if current_version == expected_version:
        return f"ready (`{expected_version}`)"
    return f"needs `[project].version = \"{expected_version}\"` in `pyproject.toml`"


def require_matching_package_metadata_version(
    *,
    repo_root: Path,
    release_tag: ReleaseTag,
) -> str:
    current_version = load_package_metadata_version(repo_root)
    expected_version = expected_package_metadata_version(release_tag)
    if current_version != expected_version:
        raise release_error(
            "E530",
            "Release package metadata version is missing or does not match",
            f"`pyproject.toml` package version `{current_version}` does not match requested release `{release_tag.raw}`. "
            f"Set `[project].version = \"{expected_version}\"` before tagging or drafting this release.",
            location=repo_root / "pyproject.toml",
        )
    return current_version


def load_changelog_sections(repo_root: Path) -> tuple[ChangelogSection, ...]:
    changelog_path = repo_root / "CHANGELOG.md"
    try:
        text = changelog_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise release_error(
            "E526",
            "Release changelog entry is missing or incomplete",
            "`CHANGELOG.md` is required for the release flow.",
            location=changelog_path,
        ) from exc

    matches = list(CHANGELOG_SECTION_RE.finditer(text))
    sections: list[ChangelogSection] = []
    for index, match in enumerate(matches):
        title = match.group("title").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append(
            ChangelogSection(
                title=title,
                key=normalize_changelog_key(title),
                body=body,
            )
        )
    return tuple(sections)


def find_release_section(
    sections: tuple[ChangelogSection, ...],
    release: str,
) -> ChangelogSection | None:
    for section in sections:
        if section.key == release:
            return section
    return None


def require_release_entry(repo_root: Path, release_tag: ReleaseTag) -> ReleaseEntry:
    section = find_release_section(load_changelog_sections(repo_root), release_tag.raw)
    if section is None:
        raise release_error(
            "E526",
            "Release changelog entry is missing or incomplete",
            f"`CHANGELOG.md` must contain one `## {release_tag.raw} - YYYY-MM-DD` section before `{release_tag.raw}` can be tagged or drafted.",
            location=repo_root / "CHANGELOG.md",
        )
    metadata, body = parse_release_entry_metadata(section, repo_root / "CHANGELOG.md")
    expected_channel = release_tag.channel_display
    if metadata["Release version"] != release_tag.raw or metadata["Release channel"] != expected_channel:
        raise release_error(
            "E526",
            "Release changelog entry is missing or incomplete",
            f"`CHANGELOG.md` release entry `{section.title}` does not match `{release_tag.raw}` and `{expected_channel}`.",
            location=repo_root / "CHANGELOG.md",
        )
    return ReleaseEntry(section=section, metadata=metadata, body=body)


def require_validated_release_entry(
    *,
    repo_root: Path,
    release_tag: ReleaseTag,
    current_language_version: LanguageVersion,
    expected_release_kind: str | None,
    requested_language_version: LanguageVersion | None = None,
) -> ReleaseEntry:
    entry = require_release_entry(repo_root, release_tag)
    error = validate_release_entry_truth(
        entry=entry,
        release_tag=release_tag,
        current_language_version=current_language_version,
        expected_release_kind=expected_release_kind,
        requested_language_version=requested_language_version,
    )
    if error is not None:
        raise release_error(
            "E526",
            "Release changelog entry is missing or incomplete",
            error,
            location=repo_root / "CHANGELOG.md",
        )
    return entry


def parse_release_entry_metadata(
    section: ChangelogSection,
    changelog_path: Path,
) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    lines = section.body.splitlines()
    body_start = 0
    started = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if started:
                body_start = index + 1
                break
            continue
        if ":" not in stripped:
            body_start = index
            break
        key, value = stripped.split(":", 1)
        key = key.strip()
        if key not in HEADER_FIELD_ORDER:
            body_start = index
            break
        metadata[key] = value.strip()
        started = True
    else:
        body_start = len(lines)

    missing = [field for field in HEADER_FIELD_ORDER if field not in metadata]
    if missing:
        raise release_error(
            "E526",
            "Release changelog entry is missing or incomplete",
            f"`CHANGELOG.md` release entry `{section.title}` is missing: {', '.join(missing)}.",
            location=changelog_path,
        )
    return metadata, "\n".join(lines[body_start:]).strip()


def describe_changelog_status(
    *,
    release_section: ChangelogSection | None,
    requested_tag: ReleaseTag,
    current_language_version: LanguageVersion,
    requested_language_version: LanguageVersion,
    release_kind: str,
) -> str:
    if release_section is None:
        return f"missing `## {requested_tag.raw} - YYYY-MM-DD`"

    metadata, _body = parse_release_entry_metadata(
        release_section,
        Path("CHANGELOG.md"),
    )
    expected_channel = requested_tag.channel_display
    if metadata["Release channel"] != expected_channel:
        return f"needs `Release channel: {expected_channel}` in `{release_section.title}`"
    if metadata["Release version"] != requested_tag.raw:
        return f"needs `Release version: {requested_tag.raw}` in `{release_section.title}`"
    entry = ReleaseEntry(section=release_section, metadata=metadata, body=_body)
    error = validate_release_entry_truth(
        entry=entry,
        release_tag=requested_tag,
        current_language_version=current_language_version,
        expected_release_kind=release_kind,
        requested_language_version=requested_language_version,
    )
    if error is not None:
        return error
    return f"ready (`{release_section.title}`)"


def resolve_requested_language_version(
    *,
    current: LanguageVersion,
    requested: str,
    release_class: str,
) -> LanguageVersion:
    if requested == "unchanged":
        return current

    next_version = parse_language_version(requested)
    if release_class == "internal":
        raise release_error(
            "E524",
            "Invalid language version move",
            "Internal-only releases must keep the Doctrine language version unchanged.",
        )
    if release_class == "soft-deprecated":
        raise release_error(
            "E524",
            "Invalid language version move",
            "Soft-deprecated releases must keep the Doctrine language version unchanged.",
        )
    if release_class == "additive":
        expected = LanguageVersion(current.major, current.minor + 1)
        if next_version != expected:
            raise release_error(
                "E524",
                "Invalid language version move",
                f"Additive releases may change the Doctrine language version only by one minor step: {current.text} -> {expected.text}.",
            )
        return next_version

    expected = LanguageVersion(current.major + 1, 0)
    if next_version != expected:
        raise release_error(
            "E524",
            "Invalid language version move",
            f"Breaking language releases must move the Doctrine language version by one major step: {current.text} -> {expected.text}.",
    )
    return next_version


def parse_language_version(
    value: str,
    *,
    location: Path | None = None,
) -> LanguageVersion:
    match = LANGUAGE_VERSION_RE.match(value.strip())
    if match is None:
        raise release_error(
            "E523",
            "Missing current language version",
            f"`{value}` is not a valid Doctrine language version. Use `X.Y`.",
            location=location,
        )
    return LanguageVersion(major=int(match.group("major")), minor=int(match.group("minor")))


def normalize_changelog_key(title: str) -> str:
    stripped = title.strip()
    if stripped.startswith("[") and "]" in stripped:
        stripped = stripped[1 : stripped.index("]")]
    if " - " in stripped:
        stripped = stripped.split(" - ", 1)[0]
    return stripped.strip()


def validate_release_entry_truth(
    *,
    entry: ReleaseEntry,
    release_tag: ReleaseTag,
    current_language_version: LanguageVersion,
    expected_release_kind: str | None,
    requested_language_version: LanguageVersion | None = None,
) -> str | None:
    metadata = entry.metadata
    section_title = entry.section.title

    if expected_release_kind is None:
        if metadata["Release kind"] not in {"Breaking", "Non-breaking"}:
            return (
                f"needs exact `Release kind: Breaking` or `Release kind: Non-breaking` "
                f"in `{section_title}`"
            )
    elif metadata["Release kind"] != expected_release_kind:
        return f"needs `Release kind: {expected_release_kind}` in `{section_title}`"

    language_error = _language_header_error(
        value=metadata["Language version"],
        current_language_version=current_language_version,
        requested_language_version=requested_language_version,
    )
    if language_error is not None:
        return f"{language_error} in `{section_title}`"

    for field in ("Affected surfaces", "Who must act", "Who does not need to act"):
        if _is_placeholder_text(metadata[field]):
            return f"needs non-placeholder `{field}` in `{section_title}`"

    if _is_placeholder_text(metadata["Verification"]) or _is_no_action_text(metadata["Verification"]):
        return f"needs exact `Verification` steps in `{section_title}`"

    if _is_placeholder_text(metadata["Support-surface version changes"]) or "unless" in _normalize_text(
        metadata["Support-surface version changes"]
    ):
        return f"needs exact `Support-surface version changes` text in `{section_title}`"

    if metadata["Release kind"] == "Breaking":
        if _is_placeholder_text(metadata["Upgrade steps"]) or _is_no_action_text(metadata["Upgrade steps"]):
            return f"needs exact `Upgrade steps` in `{section_title}`"
    elif _is_placeholder_text(metadata["Upgrade steps"]):
        return f"needs non-placeholder `Upgrade steps` in `{section_title}`"

    if not entry.body.strip():
        return f"needs one curated changelog body below the fixed release header in `{section_title}`"
    return None


def _language_header_error(
    *,
    value: str,
    current_language_version: LanguageVersion,
    requested_language_version: LanguageVersion | None,
) -> str | None:
    if requested_language_version is not None:
        expected = language_header_value(
            current=current_language_version,
            requested=requested_language_version,
            changed=requested_language_version != current_language_version,
        )
        if value != expected:
            return f"needs `Language version: {expected}`"
        return None

    match = LANGUAGE_HEADER_RE.match(value.strip())
    if match is None:
        return "needs exact `Language version: unchanged (still X.Y)` or `Language version: X.Y -> Z.W`"
    same = match.group("same")
    if same is not None:
        if same != current_language_version.text:
            return f"needs `Language version: unchanged (still {current_language_version.text})`"
        return None

    previous = match.group("from")
    current = match.group("to")
    if current != current_language_version.text or previous == current:
        return f"needs a `Language version:` value that ends at `{current_language_version.text}`"
    return None


def _is_placeholder_text(value: str) -> bool:
    normalized = _normalize_text(value)
    if not normalized:
        return True
    if normalized in PLACEHOLDER_VALUES:
        return True
    return any(marker in normalized for marker in PLACEHOLDER_SUBSTRINGS)


def _is_no_action_text(value: str) -> bool:
    normalized = _normalize_text(value)
    return normalized in {"none", "no action", "no action required"}


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())
