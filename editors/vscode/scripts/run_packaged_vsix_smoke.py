from __future__ import annotations

import json
import zipfile
from pathlib import Path


EXTENSION_DIR = Path(__file__).resolve().parents[1]
PACKAGE_ID = "aelaguiz.doctrine-language"


def _latest_vsix() -> Path:
    candidates = sorted(
        EXTENSION_DIR.glob("*.vsix"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    if not candidates:
        raise SystemExit(
            "No packaged VSIX found. Run scripts/package_vsix.py before packaged smoke."
        )
    return candidates[0]


def _read_vsix_package(vsix_path: Path) -> dict:
    with zipfile.ZipFile(vsix_path) as archive:
        names = set(archive.namelist())
        required_files = {
            "extension/package.json",
            "extension/extension.js",
            "extension/resolver.js",
            "extension/syntaxes/doctrine.tmLanguage.json",
        }
        missing = sorted(required_files - names)
        if missing:
            raise SystemExit(f"Packaged VSIX is missing required files: {', '.join(missing)}")
        return json.loads(archive.read("extension/package.json"))


def _assert_vsix_manifest(vsix_path: Path) -> None:
    package = _read_vsix_package(vsix_path)
    if f"{package.get('publisher')}.{package.get('name')}" != PACKAGE_ID:
        raise SystemExit(f"Packaged VSIX id does not match {PACKAGE_ID}.")
    if package.get("main") != "./extension.js":
        raise SystemExit("Packaged VSIX does not point at extension.js.")
    if "onLanguage:doctrine" not in package.get("activationEvents", []):
        raise SystemExit("Packaged VSIX does not activate on Doctrine files.")

    languages = package.get("contributes", {}).get("languages", [])
    doctrine_language = next(
        (language for language in languages if language.get("id") == "doctrine"),
        None,
    )
    if not doctrine_language:
        raise SystemExit("Packaged VSIX does not register the Doctrine language.")
    if ".prompt" not in doctrine_language.get("extensions", []):
        raise SystemExit("Packaged VSIX does not bind Doctrine to .prompt files.")

    grammars = package.get("contributes", {}).get("grammars", [])
    doctrine_grammar = next(
        (grammar for grammar in grammars if grammar.get("language") == "doctrine"),
        None,
    )
    if not doctrine_grammar:
        raise SystemExit("Packaged VSIX does not register a Doctrine grammar.")
    if doctrine_grammar.get("path") != "./syntaxes/doctrine.tmLanguage.json":
        raise SystemExit("Packaged VSIX points at the wrong Doctrine grammar path.")


def main() -> int:
    vsix_path = _latest_vsix()
    print(f"Running packaged VSIX smoke against {vsix_path.name}")
    _assert_vsix_manifest(vsix_path)
    print(f"Packaged VSIX smoke passed for {PACKAGE_ID}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
