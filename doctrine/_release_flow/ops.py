from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile

from doctrine._release_flow.common import run_checked
from doctrine._release_flow.models import (
    HEADER_FIELD_ORDER,
    LanguageVersion,
    ReleaseEntry,
    ReleasePlan,
    ReleaseTag,
    language_header_value,
)
from doctrine._release_flow.parsing import (
    describe_package_metadata_status,
    describe_changelog_status,
    find_release_section,
    load_changelog_sections,
    load_current_language_version,
    load_package_metadata_version,
    expected_package_metadata_version,
    require_matching_package_metadata_version,
    require_validated_release_entry,
    resolve_requested_language_version,
)
from doctrine._release_flow.tags import (
    expected_release_kind_for_tag,
    latest_tag_for_channel,
    load_release_tags,
    parse_release_tag,
    require_clean_worktree,
    require_pushed_public_release_tag,
    require_signing_key,
    resolve_previous_tag,
    validate_release_move,
)


def _require_release_ready(
    *,
    repo_root: Path,
    release_tag: ReleaseTag,
    current_language_version: LanguageVersion,
) -> ReleaseEntry:
    # Single cross-file consistency gate shared by `tag_release` and
    # `draft_release`. Blocks on CHANGELOG entry / docs/VERSIONING.md mismatch
    # via `require_validated_release_entry`, and on pyproject.toml mismatch
    # via `require_matching_package_metadata_version`. `prepare_release`
    # reports the same status read-only but does not call this helper, because
    # its job is to surface every remaining gap on one worksheet rather than
    # stop at the first one.
    release_entry = require_validated_release_entry(
        repo_root=repo_root,
        release_tag=release_tag,
        current_language_version=current_language_version,
        expected_release_kind=expected_release_kind_for_tag(
            repo_root=repo_root,
            requested_tag=release_tag,
        ),
    )
    require_matching_package_metadata_version(
        repo_root=repo_root,
        release_tag=release_tag,
    )
    return release_entry


def prepare_release(
    *,
    repo_root: Path,
    release: str,
    release_class: str,
    language_version: str,
    channel: str,
) -> ReleasePlan:
    # `prepare_release` is the planning / worksheet command. It raises on
    # inputs that cannot be resolved at all (bad tag, bad bump, missing
    # CHANGELOG / VERSIONING file) but deliberately returns status strings
    # for CHANGELOG-entry, package-version, and language-header mismatch so
    # the worksheet can list every remaining gap in one shot. The three-file
    # consistency gate is enforced at `tag_release` / `draft_release` via
    # `_require_release_ready`.
    requested_tag = parse_release_tag(release, channel=channel)
    current_language_version = load_current_language_version(repo_root)
    current_package_version = load_package_metadata_version(repo_root)
    requested_package_version = expected_package_metadata_version(requested_tag)
    tags = load_release_tags(repo_root)
    previous_stable_tag = latest_tag_for_channel(
        tags,
        repo_root=repo_root,
        channel="stable",
        before=requested_tag,
    )
    previous_same_channel_tag = latest_tag_for_channel(
        tags,
        repo_root=repo_root,
        channel=channel,
        before=requested_tag,
    )
    release_kind = "Breaking" if release_class == "breaking" else "Non-breaking"

    validate_release_move(
        requested=requested_tag,
        previous_stable=previous_stable_tag,
        release_class=release_class,
    )
    requested_language_version = resolve_requested_language_version(
        current=current_language_version,
        requested=language_version,
        release_class=release_class,
    )

    changelog = load_changelog_sections(repo_root)
    release_section = find_release_section(changelog, requested_tag.raw)
    changelog_status = describe_changelog_status(
        release_section=release_section,
        requested_tag=requested_tag,
        current_language_version=current_language_version,
        requested_language_version=requested_language_version,
        release_kind=release_kind,
    )
    package_version_status = describe_package_metadata_status(
        current_version=current_package_version,
        requested_tag=requested_tag,
    )

    return ReleasePlan(
        release_tag=requested_tag,
        release_class=release_class,
        release_kind=release_kind,
        current_language_version=current_language_version,
        requested_language_version=requested_language_version,
        language_version_changed=requested_language_version != current_language_version,
        current_package_version=current_package_version,
        requested_package_version=requested_package_version,
        package_version_status=package_version_status,
        previous_stable_tag=previous_stable_tag,
        previous_same_channel_tag=previous_same_channel_tag,
        changelog_status=changelog_status,
        changelog_header=f"## {requested_tag.raw} - {date.today().isoformat()}",
        release_header_lines=build_release_header_lines(
            release_tag=requested_tag,
            release_kind=release_kind,
            current_language_version=current_language_version,
            requested_language_version=requested_language_version,
        ),
    )


def render_release_worksheet(plan: ReleasePlan) -> str:
    required_updates = [
        "pyproject.toml",
        "CHANGELOG.md",
        "release-note header and body",
        "tests/test_release_flow.py",
    ]
    verify_commands = [
        "uv run --locked python -m unittest tests.test_release_flow",
        "uv run --locked python -m unittest tests.test_package_release",
        "make verify-package",
    ]

    if plan.language_version_changed:
        required_updates.extend(
            [
                "docs/VERSIONING.md",
                "README.md",
                "docs/README.md",
                "docs/LANGUAGE_REFERENCE.md",
                "docs/LANGUAGE_DESIGN_NOTES.md",
            ]
        )
        verify_commands.append("make verify-examples")
    elif plan.release_class == "breaking":
        required_updates.extend(
            [
                "docs/VERSIONING.md",
                "affected live docs and contributor instructions",
            ]
        )
    if plan.release_class == "breaking":
        required_updates.extend(
            [
                "AGENTS.md",
                "proof for the touched public surface",
            ]
        )

    lines = [
        "Doctrine release worksheet",
        "",
        f"Derived release kind: {plan.release_kind}",
        f"Derived release channel: {plan.release_tag.channel_display}",
        f"Previous stable tag: {plan.previous_stable_tag.raw if plan.previous_stable_tag else 'none'}",
        (
            "Previous same-channel tag: "
            f"{plan.previous_same_channel_tag.raw if plan.previous_same_channel_tag else 'none'}"
        ),
        f"Previous language version: {plan.current_language_version.text}",
        f"Requested release version: {plan.release_tag.raw}",
        f"Requested language version state: {language_state_text(plan)}",
        f"Current package metadata version: {plan.current_package_version}",
        f"Requested package metadata version: {plan.requested_package_version}",
        f"Package metadata status: {plan.package_version_status}",
        f"Changelog entry status: {plan.changelog_status}",
        "Required docs and proof surfaces to update:",
        *[f"- {item}" for item in required_updates],
        "Exact changelog entry header:",
        f"- {plan.changelog_header}",
        "Exact release-note header:",
        *[f"- {line}" for line in plan.release_header_lines],
        "Exact verify commands to run:",
        *[f"- {command}" for command in verify_commands],
        "Next commands:",
        f"- make release-tag RELEASE={plan.release_tag.raw} CHANNEL={plan.release_tag.channel}",
        (
            "- make release-draft "
            f"RELEASE={plan.release_tag.raw} CHANNEL={plan.release_tag.channel} PREVIOUS_TAG=auto"
        ),
        f"- make release-publish RELEASE={plan.release_tag.raw}",
    ]
    return "\n".join(lines)


def tag_release(*, repo_root: Path, release: str, channel: str) -> None:
    release_tag = parse_release_tag(release, channel=channel)
    current_language_version = load_current_language_version(repo_root)
    require_clean_worktree(repo_root)
    require_signing_key(repo_root)
    release_entry = _require_release_ready(
        repo_root=repo_root,
        release_tag=release_tag,
        current_language_version=current_language_version,
    )
    tag_message = build_tag_message(release_entry)
    run_checked(
        ["git", "tag", "-s", "-a", release_tag.raw, "-m", tag_message],
        cwd=repo_root,
        code="E527",
        summary="Release tag preflight failed",
        detail=f"Could not create signed annotated tag `{release_tag.raw}`.",
    )
    run_checked(
        ["git", "push", "origin", release_tag.raw],
        cwd=repo_root,
        code="E527",
        summary="Release tag preflight failed",
        detail=f"Could not push signed annotated tag `{release_tag.raw}` to `origin`.",
    )
    print(f"Created and pushed signed annotated tag `{release_tag.raw}`.")


def draft_release(
    *,
    repo_root: Path,
    release: str,
    channel: str,
    previous_tag: str,
) -> None:
    release_tag = parse_release_tag(release, channel=channel)
    require_pushed_public_release_tag(repo_root, release_tag)
    release_entry = _require_release_ready(
        repo_root=repo_root,
        release_tag=release_tag,
        current_language_version=load_current_language_version(repo_root),
    )
    previous = resolve_previous_tag(
        repo_root=repo_root,
        requested_tag=release_tag,
        previous_tag=previous_tag,
    )
    notes_text = build_release_notes(release_entry)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(notes_text)
        notes_path = Path(handle.name)

    command = [
        "gh",
        "release",
        "create",
        release_tag.raw,
        "--draft",
        "--verify-tag",
        "--title",
        release_tag.release_title,
        "--notes-file",
        str(notes_path),
        "--generate-notes",
    ]
    if previous is not None:
        command.extend(["--notes-start-tag", previous])
    if release_tag.channel != "stable":
        command.extend(["--prerelease", "--latest=false"])

    run_checked(
        command,
        cwd=repo_root,
        code="E529",
        summary="GitHub release command failed",
        detail=f"Could not create GitHub draft release `{release_tag.raw}`.",
        hints=("Make sure `gh auth status` works for this repo.",),
    )
    print(f"Created GitHub draft release `{release_tag.raw}`.")


def publish_release(*, repo_root: Path, release: str) -> None:
    release_tag = parse_release_tag(release)
    require_pushed_public_release_tag(repo_root, release_tag)
    run_checked(
        ["gh", "release", "edit", release_tag.raw, "--draft=false"],
        cwd=repo_root,
        code="E529",
        summary="GitHub release command failed",
        detail=f"Could not publish GitHub release `{release_tag.raw}`.",
        hints=("Make sure `gh auth status` works for this repo.",),
    )
    print(f"Published GitHub release `{release_tag.raw}`.")


def build_release_header_lines(
    *,
    release_tag: ReleaseTag,
    release_kind: str,
    current_language_version: LanguageVersion,
    requested_language_version: LanguageVersion,
) -> tuple[str, ...]:
    changed = requested_language_version != current_language_version
    return (
        f"Release kind: {release_kind}",
        f"Release channel: {release_tag.channel_display}",
        f"Release version: {release_tag.raw}",
        "Language version: "
        + language_header_value(
            current=current_language_version,
            requested=requested_language_version,
            changed=changed,
        ),
        "Affected surfaces: update for this release",
        "Who must act: fill this in before tagging",
        "Who does not need to act: fill this in before tagging",
        "Upgrade steps: fill this in before tagging",
        "Verification: fill this in before tagging",
        "Support-surface version changes: none unless a narrow contract changed",
    )


def build_tag_message(release_entry: ReleaseEntry) -> str:
    lines = [f"Doctrine release {release_entry.metadata['Release version']}", ""]
    for field in HEADER_FIELD_ORDER[:4]:
        lines.append(f"{field}: {release_entry.metadata[field]}")
    lines.extend(
        [
            "",
            "See CHANGELOG.md for the release record and docs/VERSIONING.md for release policy.",
        ]
    )
    return "\n".join(lines)


def build_release_notes(release_entry: ReleaseEntry) -> str:
    header = [f"{field}: {release_entry.metadata[field]}" for field in HEADER_FIELD_ORDER]
    if release_entry.body:
        return "\n".join([*header, "", release_entry.body]).strip() + "\n"
    return "\n".join(header).strip() + "\n"


def language_state_text(plan: ReleasePlan) -> str:
    if plan.language_version_changed:
        return f"{plan.current_language_version.text} -> {plan.requested_language_version.text}"
    return f"unchanged (still {plan.current_language_version.text})"
