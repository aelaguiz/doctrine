from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine._release_flow.tags import (
    parse_release_tag,
    require_public_release_tag,
    require_pushed_public_release_tag,
)
from doctrine.release_flow import (
    draft_release,
    prepare_release,
    publish_release,
    render_release_worksheet,
    tag_release,
)


class ReleaseFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.docs_dir = self.root / "docs"
        self.docs_dir.mkdir(parents=True)

        self._git("init", "-b", "main")
        self._git("config", "user.name", "Doctrine Test")
        self._git("config", "user.email", "doctrine@example.com")

        (self.root / "README.md").write_text("# Doctrine test repo\n", encoding="utf-8")
        self._write_pyproject(package_version="1.0.0")
        self._write_versioning(language_version="1.0")
        self._write_changelog(unreleased="- No public release yet.\n")
        self._commit("initial state")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_prepare_release_renders_ready_minor_release_worksheet(self) -> None:
        self._tag("v1.0.0")
        self._write_pyproject(package_version="1.1.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )

        with patch("doctrine._release_flow.tags.require_public_release_tag"):
            plan = prepare_release(
                repo_root=self.root,
                release="v1.1.0",
                release_class="additive",
                language_version="unchanged",
                channel="stable",
            )
        worksheet = render_release_worksheet(plan)

        self.assertEqual(plan.release_kind, "Non-breaking")
        self.assertEqual(plan.previous_stable_tag.raw, "v1.0.0")
        self.assertEqual(plan.requested_language_version.text, "1.0")
        self.assertIn("Changelog entry status: ready (`v1.1.0 - 2026-04-13`)", worksheet)
        self.assertIn("Requested release version: v1.1.0", worksheet)
        self.assertIn("Requested language version state: unchanged (still 1.0)", worksheet)
        self.assertIn("Package metadata status: ready (`1.1.0`)", worksheet)
        self.assertIn("- make verify-package", worksheet)
        self.assertIn("- uv run --locked python -m unittest tests.test_package_release", worksheet)
        self.assertIn("- pyproject.toml", worksheet)
        self.assertIn(
            "make release-draft RELEASE=v1.1.0 CHANNEL=stable PREVIOUS_TAG=auto",
            worksheet,
        )

    def test_prepare_release_reports_package_metadata_status(self) -> None:
        self._tag("v1.0.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.0.1",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )

        with patch("doctrine._release_flow.tags.require_public_release_tag"):
            plan = prepare_release(
                repo_root=self.root,
                release="v1.0.1",
                release_class="internal",
                language_version="unchanged",
                channel="stable",
            )
        worksheet = render_release_worksheet(plan)

        self.assertIn("Current package metadata version: 1.0.0", worksheet)
        self.assertIn("Requested package metadata version: 1.0.1", worksheet)
        self.assertIn(
            'Package metadata status: needs `[project].version = "1.0.1"` in `pyproject.toml`',
            worksheet,
        )

    def test_prepare_release_rejects_internal_minor_bump(self) -> None:
        self._tag("v1.0.0")

        with (
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            self.assertRaisesRegex(RuntimeError, "E525 emit error: Invalid release version move"),
        ):
            prepare_release(
                repo_root=self.root,
                release="v1.1.0",
                release_class="internal",
                language_version="unchanged",
                channel="stable",
            )

    def test_prepare_release_rejects_additive_major_language_jump(self) -> None:
        self._tag("v1.0.0")

        with (
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            self.assertRaisesRegex(RuntimeError, "E524 emit error: Invalid language version move"),
        ):
            prepare_release(
                repo_root=self.root,
                release="v1.1.0",
                release_class="additive",
                language_version="2.0",
                channel="stable",
            )

    def test_prepare_release_rejects_lightweight_previous_tag(self) -> None:
        self._tag("v1.0.0")

        with self.assertRaisesRegex(RuntimeError, "must be an annotated tag, not a lightweight tag"):
            prepare_release(
                repo_root=self.root,
                release="v1.1.0",
                release_class="additive",
                language_version="unchanged",
                channel="stable",
            )

    def test_prepare_release_rejects_unsigned_annotated_previous_tag(self) -> None:
        self._annotated_tag("v1.0.0")

        with self.assertRaisesRegex(RuntimeError, "must pass `git verify-tag`"):
            prepare_release(
                repo_root=self.root,
                release="v1.1.0",
                release_class="additive",
                language_version="unchanged",
                channel="stable",
            )

    def test_tag_release_requires_signing_key(self) -> None:
        self._tag("v1.0.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )
        self._commit("prepare release entry")

        with self.assertRaisesRegex(
            RuntimeError,
            "E528 emit error: Release tag signing is not configured",
        ):
            tag_release(repo_root=self.root, release="v1.1.0", channel="stable")

    def test_tag_release_rejects_wrong_release_kind(self) -> None:
        self._tag("v1.0.0")
        self._git("config", "user.signingkey", "fake-key")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v2.0.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )
        self._commit("prepare wrong-kind release entry")

        with (
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            self.assertRaisesRegex(RuntimeError, "needs `Release kind: Breaking`"),
        ):
            tag_release(repo_root=self.root, release="v2.0.0", channel="stable")

    def test_tag_release_rejects_mismatched_package_version(self) -> None:
        self._tag("v1.0.0")
        self._git("config", "user.signingkey", "fake-key")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.0.1",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )
        self._commit("prepare patch release entry with stale package version")

        with (
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            self.assertRaisesRegex(
                RuntimeError,
                r'E530 emit error: Release package metadata version is missing or does not match',
            ),
        ):
            tag_release(repo_root=self.root, release="v1.0.1", channel="stable")

    def test_draft_release_builds_prerelease_github_command_and_notes(self) -> None:
        self._tag("v1.0.0")
        self._tag("v2.0.0-beta.1")
        self._write_pyproject(package_version="2.0.0b2")
        self._write_versioning(language_version="2.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v2.0.0-beta.2",
                    release_kind="Breaking",
                    channel="beta.2",
                    language_version="1.0 -> 2.0",
                    upgrade_steps="Replace the old release flow with the new signed tag and draft flow.",
                ),
            ),
        )
        self._commit("prepare prerelease entry")

        real_run = subprocess.run
        gh_calls: list[list[str]] = []

        def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
            command = args[0]
            if command[0] == "gh":
                gh_calls.append(command)
                return subprocess.CompletedProcess(command, 0, "", "")
            return real_run(*args, **kwargs)

        with (
            patch("doctrine._release_flow.ops.require_pushed_public_release_tag"),
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            patch("doctrine._release_flow.common.subprocess.run", side_effect=fake_run),
        ):
            draft_release(
                repo_root=self.root,
                release="v2.0.0-beta.2",
                channel="beta",
                previous_tag="auto",
            )

        self.assertEqual(len(gh_calls), 1)
        command = gh_calls[0]
        self.assertIn("--draft", command)
        self.assertIn("--verify-tag", command)
        self.assertIn("--generate-notes", command)
        self.assertIn("--prerelease", command)
        self.assertIn("--latest=false", command)
        self.assertIn("--notes-start-tag", command)
        self.assertIn("v2.0.0-beta.1", command)
        notes_path = Path(command[command.index("--notes-file") + 1])
        notes_text = notes_path.read_text(encoding="utf-8")
        self.assertIn("Release kind: Breaking", notes_text)
        self.assertIn("Release channel: beta.2", notes_text)
        self.assertIn("Release version: v2.0.0-beta.2", notes_text)
        self.assertIn("### Changed", notes_text)

    def test_draft_release_builds_stable_github_command_and_notes(self) -> None:
        self._tag("v1.0.0")
        self._write_pyproject(package_version="1.1.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )
        self._commit("prepare stable release entry")

        real_run = subprocess.run
        gh_calls: list[list[str]] = []

        def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
            command = args[0]
            if command[0] == "gh":
                gh_calls.append(command)
                return subprocess.CompletedProcess(command, 0, "", "")
            return real_run(*args, **kwargs)

        with (
            patch("doctrine._release_flow.ops.require_pushed_public_release_tag"),
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            patch("doctrine._release_flow.common.subprocess.run", side_effect=fake_run),
        ):
            draft_release(
                repo_root=self.root,
                release="v1.1.0",
                channel="stable",
                previous_tag="auto",
            )

        command = gh_calls[0]
        self.assertNotIn("--prerelease", command)
        self.assertNotIn("--latest=false", command)
        notes_path = Path(command[command.index("--notes-file") + 1])
        notes_text = notes_path.read_text(encoding="utf-8")
        self.assertIn("Release kind: Non-breaking", notes_text)
        self.assertIn("Release channel: stable", notes_text)
        self.assertIn("Release version: v1.1.0", notes_text)

    def test_draft_release_rejects_wrong_language_header(self) -> None:
        self._tag("v1.0.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 0.9)",
                ),
            ),
        )
        self._commit("prepare wrong-language release entry")

        with (
            patch("doctrine._release_flow.ops.require_pushed_public_release_tag"),
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            self.assertRaisesRegex(RuntimeError, "needs `Language version: unchanged \\(still 1.0\\)`"),
        ):
            draft_release(
                repo_root=self.root,
                release="v1.1.0",
                channel="stable",
                previous_tag="auto",
            )

    def test_draft_release_rejects_placeholder_verification_text(self) -> None:
        self._tag("v1.0.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                    verification="fill this in before tagging",
                ),
            ),
        )
        self._commit("prepare placeholder release entry")

        with (
            patch("doctrine._release_flow.ops.require_pushed_public_release_tag"),
            patch("doctrine._release_flow.tags.require_public_release_tag"),
            self.assertRaisesRegex(RuntimeError, "needs exact `Verification` steps"),
        ):
            draft_release(
                repo_root=self.root,
                release="v1.1.0",
                channel="stable",
                previous_tag="auto",
            )

    def test_publish_release_builds_github_edit_command(self) -> None:
        real_run = subprocess.run
        gh_calls: list[list[str]] = []

        def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
            command = args[0]
            if command[0] == "gh":
                gh_calls.append(command)
                return subprocess.CompletedProcess(command, 0, "", "")
            return real_run(*args, **kwargs)

        with (
            patch("doctrine._release_flow.ops.require_pushed_public_release_tag"),
            patch("doctrine._release_flow.common.subprocess.run", side_effect=fake_run),
        ):
            publish_release(repo_root=self.root, release="v1.1.0")

        self.assertEqual(
            gh_calls,
            [["gh", "release", "edit", "v1.1.0", "--draft=false"]],
        )

    def test_draft_release_rejects_missing_current_tag(self) -> None:
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )
        self._commit("prepare missing-tag release entry")

        with self.assertRaisesRegex(RuntimeError, "Public release tag `v1.1.0` is missing"):
            draft_release(
                repo_root=self.root,
                release="v1.1.0",
                channel="stable",
                previous_tag="auto",
            )

    def test_draft_release_rejects_lightweight_current_tag(self) -> None:
        self._tag("v1.1.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )
        self._commit("prepare lightweight-tag release entry")

        with self.assertRaisesRegex(RuntimeError, "must be an annotated tag, not a lightweight tag"):
            draft_release(
                repo_root=self.root,
                release="v1.1.0",
                channel="stable",
                previous_tag="auto",
            )

    def test_draft_release_rejects_unsigned_current_tag(self) -> None:
        self._annotated_tag("v1.1.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v1.1.0",
                    release_kind="Non-breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                ),
            ),
        )
        self._commit("prepare unsigned-tag release entry")

        with self.assertRaisesRegex(RuntimeError, "must pass `git verify-tag`"):
            draft_release(
                repo_root=self.root,
                release="v1.1.0",
                channel="stable",
                previous_tag="auto",
            )

    def test_publish_release_rejects_missing_current_tag(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Public release tag `v1.1.0` is missing"):
            publish_release(repo_root=self.root, release="v1.1.0")

    def test_publish_release_rejects_lightweight_current_tag(self) -> None:
        self._tag("v1.1.0")
        with self.assertRaisesRegex(RuntimeError, "must be an annotated tag, not a lightweight tag"):
            publish_release(repo_root=self.root, release="v1.1.0")

    def test_publish_release_rejects_unsigned_current_tag(self) -> None:
        self._annotated_tag("v1.1.0")
        with self.assertRaisesRegex(RuntimeError, "must pass `git verify-tag`"):
            publish_release(repo_root=self.root, release="v1.1.0")

    def test_public_release_tag_uses_git_verify_tag_not_marker_text(self) -> None:
        self._annotated_tag(
            "v1.1.0",
            message=(
                "Release v1.1.0\n"
                "-----BEGIN PGP SIGNATURE-----\n"
                "fake\n"
                "-----END PGP SIGNATURE-----"
            ),
        )

        with self.assertRaisesRegex(RuntimeError, "must pass `git verify-tag`"):
            require_public_release_tag(self.root, parse_release_tag("v1.1.0"))

    def test_pushed_public_release_tag_rejects_missing_origin_tag(self) -> None:
        release_tag = parse_release_tag("v1.1.0")

        with (
            patch("doctrine._release_flow.tags.require_public_release_tag", return_value="local-object"),
            patch(
                "doctrine._release_flow.tags.run_checked",
                return_value=subprocess.CompletedProcess(["git"], 0, "", ""),
            ),
            self.assertRaisesRegex(RuntimeError, "is not pushed to `origin`"),
        ):
            require_pushed_public_release_tag(self.root, release_tag)

    def test_pushed_public_release_tag_rejects_origin_mismatch(self) -> None:
        release_tag = parse_release_tag("v1.1.0")

        with (
            patch("doctrine._release_flow.tags.require_public_release_tag", return_value="local-object"),
            patch(
                "doctrine._release_flow.tags.run_checked",
                return_value=subprocess.CompletedProcess(
                    ["git"],
                    0,
                    "remote-object\trefs/tags/v1.1.0\n",
                    "",
                ),
            ),
            self.assertRaisesRegex(
                RuntimeError,
                "does not match the verified local signed annotated tag object",
            ),
        ):
            require_pushed_public_release_tag(self.root, release_tag)

    def test_prepare_breaking_non_language_release_lists_required_surfaces(self) -> None:
        self._tag("v1.0.0")
        self._write_changelog(
            unreleased="- Next release planning starts after this cut.\n",
            released_sections=(
                self._release_section(
                    tag="v2.0.0",
                    release_kind="Breaking",
                    channel="stable",
                    language_version="unchanged (still 1.0)",
                    upgrade_steps="Move callers to the new release workflow.",
                ),
            ),
        )

        with patch("doctrine._release_flow.tags.require_public_release_tag"):
            plan = prepare_release(
                repo_root=self.root,
                release="v2.0.0",
                release_class="breaking",
                language_version="unchanged",
                channel="stable",
            )
        worksheet = render_release_worksheet(plan)

        self.assertIn("- pyproject.toml", worksheet)
        self.assertIn("- docs/VERSIONING.md", worksheet)
        self.assertIn("- affected live docs and contributor instructions", worksheet)
        self.assertIn("- AGENTS.md", worksheet)
        self.assertIn("- release-note header and body", worksheet)
        self.assertIn("- proof for the touched public surface", worksheet)

    def _write_versioning(self, *, language_version: str) -> None:
        (self.docs_dir / "VERSIONING.md").write_text(
            textwrap.dedent(
                f"""\
                # Versioning

                Current Doctrine language version: {language_version}
                """
            ),
            encoding="utf-8",
        )

    def _write_pyproject(self, *, package_version: str) -> None:
        (self.root / "pyproject.toml").write_text(
            textwrap.dedent(
                f"""\
                [project]
                name = "doctrine"
                version = "{package_version}"

                [tool.doctrine.package]
                import_name = "doctrine"
                pypi_environment = "pypi"
                testpypi_environment = "testpypi"
                """
            ),
            encoding="utf-8",
        )

    def _write_changelog(
        self,
        *,
        unreleased: str,
        released_sections: tuple[str, ...] = (),
    ) -> None:
        sections = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            unreleased.strip(),
        ]
        for section in released_sections:
            sections.extend(["", section.strip()])
        (self.root / "CHANGELOG.md").write_text("\n".join(sections).strip() + "\n", encoding="utf-8")

    def _release_section(
        self,
        *,
        tag: str,
        release_kind: str,
        channel: str,
        language_version: str,
        verification: str = "uv run --locked python -m unittest tests.test_release_flow",
        upgrade_steps: str = "none",
    ) -> str:
        return textwrap.dedent(
            f"""\
            ## {tag} - 2026-04-13

            Release kind: {release_kind}
            Release channel: {channel}
            Release version: {tag}
            Language version: {language_version}
            Affected surfaces: release flow and live docs
            Who must act: maintainers cutting this release
            Who does not need to act: users who do not depend on the touched surfaces
            Upgrade steps: {upgrade_steps}
            Verification: {verification}
            Support-surface version changes: none

            ### Changed
            - Prepared {tag} for release.
            """
        )

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def _commit(self, message: str) -> None:
        self._git("add", ".")
        self._git("commit", "-m", message)

    def _tag(self, tag: str) -> None:
        self._git("tag", tag)

    def _annotated_tag(self, tag: str, *, message: str | None = None) -> None:
        self._git("tag", "-a", tag, "-m", message or f"Release {tag}")


if __name__ == "__main__":
    unittest.main()
