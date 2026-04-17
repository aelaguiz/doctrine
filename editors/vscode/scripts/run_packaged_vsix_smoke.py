from __future__ import annotations

import os
import subprocess
from pathlib import Path


EXTENSION_DIR = Path(__file__).resolve().parents[1]
PACKAGED_VSIX_ENV = "DOCTRINE_VSCODE_PACKAGED_VSIX"


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


def main() -> int:
    vsix_path = _latest_vsix()
    env = os.environ.copy()
    env[PACKAGED_VSIX_ENV] = str(vsix_path)

    print(f"Running packaged VSIX smoke against {vsix_path.name}")
    result = subprocess.run(
        ["node", "./tests/integration/run.js"],
        cwd=EXTENSION_DIR,
        env=env,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
