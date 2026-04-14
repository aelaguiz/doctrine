from __future__ import annotations

from dataclasses import dataclass
import re

RELEASE_TAG_RE = re.compile(
    r"^v(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<channel>beta|rc)\.(?P<prerelease>0|[1-9]\d*))?$"
)
LANGUAGE_VERSION_RE = re.compile(r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)$")
CURRENT_LANGUAGE_VERSION_RE = re.compile(
    r"^Current Doctrine language version:\s*(?P<version>\d+\.\d+)\s*$",
    re.MULTILINE,
)
CHANGELOG_SECTION_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)

HEADER_FIELD_ORDER = (
    "Release kind",
    "Release channel",
    "Release version",
    "Language version",
    "Affected surfaces",
    "Who must act",
    "Who does not need to act",
    "Upgrade steps",
    "Verification",
    "Support-surface version changes",
)


@dataclass(frozen=True)
class LanguageVersion:
    major: int
    minor: int

    @property
    def text(self) -> str:
        return f"{self.major}.{self.minor}"


@dataclass(frozen=True)
class ReleaseTag:
    raw: str
    major: int
    minor: int
    patch: int
    channel: str
    prerelease_number: int | None = None

    @property
    def base(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    @property
    def channel_display(self) -> str:
        if self.channel == "stable":
            return "stable"
        return f"{self.channel}.{self.prerelease_number}"

    @property
    def release_title(self) -> str:
        return f"Doctrine {self.raw}"


@dataclass(frozen=True)
class ReleasePlan:
    release_tag: ReleaseTag
    release_class: str
    release_kind: str
    current_language_version: LanguageVersion
    requested_language_version: LanguageVersion
    language_version_changed: bool
    previous_stable_tag: ReleaseTag | None
    previous_same_channel_tag: ReleaseTag | None
    changelog_status: str
    changelog_header: str
    release_header_lines: tuple[str, ...]


@dataclass(frozen=True)
class ChangelogSection:
    title: str
    key: str
    body: str


@dataclass(frozen=True)
class ReleaseEntry:
    section: ChangelogSection
    metadata: dict[str, str]
    body: str


def language_header_value(
    *,
    current: LanguageVersion | None,
    requested: LanguageVersion,
    changed: bool | None,
) -> str:
    if current is None or changed is None:
        return requested.text
    if changed:
        return f"{current.text} -> {requested.text}"
    return f"unchanged (still {current.text})"


def sort_key(tag: ReleaseTag) -> tuple[int, int, int, int]:
    prerelease = tag.prerelease_number if tag.prerelease_number is not None else 0
    return (*tag.base, prerelease)
