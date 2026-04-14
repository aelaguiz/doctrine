from __future__ import annotations

from pathlib import Path
import subprocess

from doctrine._release_flow.common import release_error, run_checked
from doctrine._release_flow.models import RELEASE_TAG_RE, ReleaseTag, sort_key


def load_release_tags(repo_root: Path) -> tuple[ReleaseTag, ...]:
    completed = run_checked(
        ["git", "tag", "--list"],
        cwd=repo_root,
        code="E527",
        summary="Release tag preflight failed",
        detail="Could not list git tags for the release flow.",
    )
    parsed: list[ReleaseTag] = []
    for line in completed.stdout.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        match = RELEASE_TAG_RE.match(candidate)
        if match is not None:
            parsed.append(build_release_tag(match))
    return tuple(parsed)


def latest_tag_for_channel(
    tags: tuple[ReleaseTag, ...],
    *,
    repo_root: Path,
    channel: str,
    before: ReleaseTag | None = None,
) -> ReleaseTag | None:
    matching = [tag for tag in tags if tag.channel == channel]
    if before is not None:
        matching = [tag for tag in matching if sort_key(tag) < sort_key(before)]
    if not matching:
        return None
    candidate = max(matching, key=sort_key)
    require_public_release_tag(repo_root, candidate)
    return candidate


def resolve_previous_tag(
    *,
    repo_root: Path,
    requested_tag: ReleaseTag,
    previous_tag: str,
) -> str | None:
    if previous_tag != "auto":
        explicit = parse_release_tag(previous_tag)
        require_public_release_tag(repo_root, explicit)
        return explicit.raw

    tags = load_release_tags(repo_root)
    previous_same_channel = latest_tag_for_channel(
        tags,
        repo_root=repo_root,
        channel=requested_tag.channel,
        before=requested_tag,
    )
    if previous_same_channel is not None:
        return previous_same_channel.raw
    previous_stable = latest_tag_for_channel(
        tags,
        repo_root=repo_root,
        channel="stable",
        before=requested_tag,
    )
    if previous_stable is not None:
        return previous_stable.raw
    return None


def expected_release_kind_for_tag(
    *,
    repo_root: Path,
    requested_tag: ReleaseTag,
) -> str | None:
    previous_stable = latest_tag_for_channel(
        load_release_tags(repo_root),
        repo_root=repo_root,
        channel="stable",
        before=requested_tag,
    )
    if previous_stable is None:
        return None
    move = classify_release_move(previous_stable, requested_tag)
    if move == "major":
        return "Breaking"
    if move in {"minor", "patch"}:
        return "Non-breaking"
    raise release_error(
        "E525",
        "Invalid release version move",
        f"`{requested_tag.raw}` is not a valid patch, minor, or major bump after `{previous_stable.raw}`.",
    )


def validate_release_move(
    *,
    requested: ReleaseTag,
    previous_stable: ReleaseTag | None,
    release_class: str,
) -> None:
    if previous_stable is None:
        return

    if requested.base <= previous_stable.base:
        raise release_error(
            "E525",
            "Invalid release version move",
            f"`{requested.raw}` must be newer than the previous stable tag `{previous_stable.raw}`.",
        )

    if release_class == "internal":
        expected_move = "patch"
    elif release_class in {"additive", "soft-deprecated"}:
        expected_move = "minor"
    else:
        expected_move = "major"

    actual_move = classify_release_move(previous_stable, requested)
    if actual_move != expected_move:
        raise release_error(
            "E525",
            "Invalid release version move",
            f"`{release_class}` releases must use a {expected_move} release bump after `{previous_stable.raw}`. `{requested.raw}` is a {actual_move} bump.",
        )


def classify_release_move(previous: ReleaseTag, requested: ReleaseTag) -> str:
    if requested.major == previous.major and requested.minor == previous.minor and requested.patch > previous.patch:
        return "patch"
    if requested.major == previous.major and requested.minor > previous.minor and requested.patch == 0:
        return "minor"
    if requested.major > previous.major and requested.minor == 0 and requested.patch == 0:
        return "major"
    return "invalid"


def parse_release_tag(value: str, *, channel: str | None = None) -> ReleaseTag:
    match = RELEASE_TAG_RE.match(value.strip())
    if match is None:
        raise release_error(
            "E522",
            "Invalid release version",
            f"`{value}` is not a valid Doctrine release tag. Use `vX.Y.Z`, `vX.Y.Z-beta.N`, or `vX.Y.Z-rc.N`.",
        )
    tag = build_release_tag(match)
    if channel is not None and tag.channel != channel:
        raise release_error(
            "E522",
            "Invalid release version",
            f"`{value}` does not match `CHANNEL={channel}`.",
        )
    return tag


def build_release_tag(match) -> ReleaseTag:  # type: ignore[no-untyped-def]
    channel = match.group("channel") or "stable"
    prerelease = match.group("prerelease")
    return ReleaseTag(
        raw=match.group(0),
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        channel=channel,
        prerelease_number=int(prerelease) if prerelease is not None else None,
    )


def require_clean_worktree(repo_root: Path) -> None:
    completed = run_checked(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        code="E527",
        summary="Release tag preflight failed",
        detail="Could not inspect the git worktree state.",
    )
    if completed.stdout.strip():
        raise release_error(
            "E527",
            "Release tag preflight failed",
            "The git worktree must be clean before Doctrine creates a signed public tag.",
        )


def require_signing_key(repo_root: Path) -> None:
    try:
        completed = subprocess.run(
            ["git", "config", "--get", "user.signingkey"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise release_error(
            "E528",
            "Release tag signing is not configured",
            "Missing command: `git`.",
        ) from exc
    if completed.returncode != 0 or not completed.stdout.strip():
        raise release_error(
            "E528",
            "Release tag signing is not configured",
            "Set `git config user.signingkey <key>` before running `release-tag`.",
        )


def require_public_release_tag(repo_root: Path, release_tag: ReleaseTag) -> str:
    object_type = run_checked(
        ["git", "for-each-ref", f"refs/tags/{release_tag.raw}", "--format=%(objecttype)"],
        cwd=repo_root,
        code="E527",
        summary="Release tag preflight failed",
        detail=f"Could not inspect public release tag `{release_tag.raw}`.",
    ).stdout.strip()
    if not object_type:
        raise release_error(
            "E527",
            "Release tag preflight failed",
            f"Public release tag `{release_tag.raw}` is missing. Create and push the signed annotated tag before GitHub publication.",
        )
    if object_type != "tag":
        raise release_error(
            "E527",
            "Release tag preflight failed",
            f"Public release tag `{release_tag.raw}` must be an annotated tag, not a lightweight tag.",
        )

    local_tag_object = run_checked(
        ["git", "rev-parse", f"refs/tags/{release_tag.raw}"],
        cwd=repo_root,
        code="E527",
        summary="Release tag preflight failed",
        detail=f"Could not resolve tag object for `{release_tag.raw}`.",
    ).stdout.strip()

    try:
        completed = subprocess.run(
            ["git", "verify-tag", release_tag.raw],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise release_error(
            "E527",
            "Release tag preflight failed",
            "Missing command: `git`.",
        ) from exc

    if completed.returncode != 0:
        detail_lines = [
            f"Public release tag `{release_tag.raw}` must pass `git verify-tag` before Doctrine uses it as public release truth.",
        ]
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        if stderr:
            detail_lines.append(stderr)
        elif stdout:
            detail_lines.append(stdout)
        raise release_error(
            "E527",
            "Release tag preflight failed",
            "\n".join(detail_lines),
        )
    return local_tag_object


def require_pushed_public_release_tag(repo_root: Path, release_tag: ReleaseTag) -> str:
    local_tag_object = require_public_release_tag(repo_root, release_tag)
    remote_listing = run_checked(
        ["git", "ls-remote", "--tags", "origin", f"refs/tags/{release_tag.raw}"],
        cwd=repo_root,
        code="E527",
        summary="Release tag preflight failed",
        detail=f"Could not inspect pushed release tag `{release_tag.raw}` on `origin`.",
    ).stdout.strip()
    if not remote_listing:
        raise release_error(
            "E527",
            "Release tag preflight failed",
            f"Public release tag `{release_tag.raw}` is not pushed to `origin`. Push the verified signed annotated tag before GitHub publication.",
        )

    remote_tag_object = remote_listing.split()[0]
    if remote_tag_object != local_tag_object:
        raise release_error(
            "E527",
            "Release tag preflight failed",
            f"Public release tag `{release_tag.raw}` on `origin` does not match the verified local signed annotated tag object.",
        )
    return local_tag_object
