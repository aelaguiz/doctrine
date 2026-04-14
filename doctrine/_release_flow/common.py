from __future__ import annotations

from pathlib import Path
import subprocess

from doctrine._compiler.support import path_location
from doctrine.diagnostics import EmitError


def run_checked(
    command: list[str],
    *,
    cwd: Path,
    code: str,
    summary: str,
    detail: str,
    hints: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise release_error(
            code,
            summary,
            f"{detail} Missing command: `{command[0]}`.",
            hints=hints,
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail_lines = [detail]
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        if stderr:
            detail_lines.append(stderr)
        elif stdout:
            detail_lines.append(stdout)
        raise release_error(
            code,
            summary,
            "\n".join(detail_lines),
            hints=hints,
        ) from exc


def release_error(
    code: str,
    summary: str,
    detail: str,
    *,
    location: Path | None = None,
    hints: tuple[str, ...] = (),
) -> EmitError:
    return EmitError.from_parts(
        code=code,
        summary=summary,
        detail=detail,
        location=path_location(location),
        hints=hints,
    )
