from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path


EXTENSION_DIR = Path(__file__).resolve().parents[1]
PACKAGE_JSON_PATH = EXTENSION_DIR / "package.json"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def _load_package_json() -> dict[str, object]:
    try:
        raw = json.loads(PACKAGE_JSON_PATH.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid package.json at {PACKAGE_JSON_PATH}: {exc}") from exc
    if not isinstance(raw, dict):
        raise SystemExit(f"Invalid package.json at {PACKAGE_JSON_PATH}: expected a JSON object.")
    return raw


def _next_patch(major: str, minor: str, package_name: str) -> int:
    candidate = time.time_ns() // 1_000_000
    prefix = f"{package_name}-{major}.{minor}."
    max_existing = -1

    for path in EXTENSION_DIR.glob(f"{package_name}-{major}.{minor}.*.vsix"):
        version = path.stem.removeprefix(prefix)
        if version.isdigit():
            max_existing = max(max_existing, int(version))

    return max(candidate, max_existing + 1)


def _generated_version(base_version: str, package_name: str) -> str:
    match = SEMVER_RE.fullmatch(base_version)
    if match is None:
        raise SystemExit(
            f"Extension version must be semver in {PACKAGE_JSON_PATH}: {base_version!r}"
        )
    major, minor, _patch = match.groups()
    patch = _next_patch(major, minor, package_name)
    return f"{major}.{minor}.{patch}"


def main() -> int:
    package_json = _load_package_json()
    package_name = package_json.get("name")
    base_version = package_json.get("version")

    if not isinstance(package_name, str) or not package_name:
        raise SystemExit(f"Extension package name must be a non-empty string in {PACKAGE_JSON_PATH}.")
    if not isinstance(base_version, str):
        raise SystemExit(f"Extension version must be a string in {PACKAGE_JSON_PATH}.")

    version = _generated_version(base_version, package_name)
    output_path = EXTENSION_DIR / f"{package_name}-{version}.vsix"

    result = subprocess.run(
        [
            "npx",
            "@vscode/vsce",
            "package",
            version,
            "--no-git-tag-version",
            "--no-update-package-json",
            "--out",
            str(output_path),
        ],
        cwd=EXTENSION_DIR,
        check=False,
    )
    if result.returncode != 0:
        return result.returncode

    print(f"Packaged VSIX: {output_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
