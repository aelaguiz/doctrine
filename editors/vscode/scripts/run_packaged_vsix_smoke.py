from __future__ import annotations

import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path


EXTENSION_DIR = Path(__file__).resolve().parents[1]
PACKAGE_ID = "aelaguiz.doctrine-language"
EXECUTABLE_PATH_ENV = "DOCTRINE_VSCODE_EXECUTABLE_PATH"


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


def _run(command: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=EXTENSION_DIR,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def _resolve_vscode_executable() -> Path:
    configured_path = os.environ.get(EXECUTABLE_PATH_ENV)
    if configured_path:
        return Path(configured_path).resolve()

    node_script = """
const path = require("node:path");
const { downloadAndUnzipVSCode } = require("@vscode/test-electron");

(async () => {
  const cachePath = process.env.DOCTRINE_VSCODE_TEST_CACHE
    ? path.resolve(process.env.DOCTRINE_VSCODE_TEST_CACHE)
    : path.join(process.cwd(), ".vscode-test");
  const executablePath = await downloadAndUnzipVSCode({
    cachePath,
    extensionDevelopmentPath: process.cwd(),
  });
  console.log(executablePath);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""
    result = _run(["node", "-e", node_script], timeout=120)
    if result.returncode != 0:
        print(result.stdout, end="")
        raise SystemExit(result.returncode)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise SystemExit("Could not resolve VS Code executable path.")
    return Path(lines[-1]).resolve()


def _resolve_vscode_cli(executable_path: Path) -> Path:
    mac_cli = (executable_path.parent / "../Resources/app/bin/code").resolve()
    if mac_cli.exists():
        return mac_cli
    return executable_path


def _cli_args(vscode_cli: Path, user_data_dir: Path, extensions_dir: Path) -> list[str]:
    return [
        str(vscode_cli),
        f"--extensions-dir={extensions_dir}",
        f"--user-data-dir={user_data_dir}",
        "--no-sandbox",
        "--disable-gpu",
    ]


def _assert_cli_install(vsix_path: Path) -> None:
    executable_path = _resolve_vscode_executable()
    vscode_cli = _resolve_vscode_cli(executable_path)
    with tempfile.TemporaryDirectory(prefix="doctrine-vscode-user-") as user_data_dir_raw:
        with tempfile.TemporaryDirectory(prefix="doctrine-vscode-ext-") as extensions_dir_raw:
            user_data_dir = Path(user_data_dir_raw)
            extensions_dir = Path(extensions_dir_raw)
            install = _run(
                [
                    *_cli_args(vscode_cli, user_data_dir, extensions_dir),
                    "--install-extension",
                    str(vsix_path),
                    "--force",
                ],
                timeout=60,
            )
            if install.returncode != 0:
                print(install.stdout, end="")
                raise SystemExit(install.returncode)

            installed = _run(
                [
                    *_cli_args(vscode_cli, user_data_dir, extensions_dir),
                    "--list-extensions",
                ],
                timeout=60,
            )
            if installed.returncode != 0:
                print(installed.stdout, end="")
                raise SystemExit(installed.returncode)
            installed_ids = set(installed.stdout.splitlines())
            if PACKAGE_ID not in installed_ids:
                print(installed.stdout, end="")
                raise SystemExit(f"Installed extensions did not include {PACKAGE_ID}.")


def main() -> int:
    vsix_path = _latest_vsix()
    print(f"Running packaged VSIX smoke against {vsix_path.name}")
    _assert_vsix_manifest(vsix_path)
    _assert_cli_install(vsix_path)
    print(f"Packaged VSIX smoke passed for {PACKAGE_ID}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
