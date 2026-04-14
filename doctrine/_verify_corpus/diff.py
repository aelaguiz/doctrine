from __future__ import annotations

from difflib import unified_diff
from pathlib import Path

from doctrine._verify_corpus.manifest import CaseSpec, REPO_ROOT
from doctrine._verify_corpus.report import RefDiff


def _build_contract_ref_diff(
    case: CaseSpec, *, expected_lines: tuple[str, ...], output_label: str
) -> RefDiff | None:
    if case.approx_ref_path is None:
        return None

    ref_lines = tuple(case.approx_ref_path.read_text().splitlines())
    if ref_lines == expected_lines:
        return None

    return RefDiff(
        case=case,
        label=f"{case.approx_ref_path.relative_to(REPO_ROOT)} vs {case.name}",
        diff=_build_diff(
            ref_lines,
            expected_lines,
            fromfile=str(case.approx_ref_path.relative_to(REPO_ROOT)),
            tofile=output_label,
        ),
    )


def _build_diff(
    before_lines: tuple[str, ...],
    after_lines: tuple[str, ...],
    *,
    fromfile: str,
    tofile: str,
) -> str:
    return "".join(
        unified_diff(
            [line + "\n" for line in before_lines],
            [line + "\n" for line in after_lines],
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def _build_tree_diff(*, expected_root: Path, actual_root: Path) -> str | None:
    expected_files = {
        path.relative_to(expected_root): path
        for path in expected_root.rglob("*")
        if path.is_file()
    }
    actual_files = {
        path.relative_to(actual_root): path
        for path in actual_root.rglob("*")
        if path.is_file()
    }

    lines: list[str] = []

    missing = sorted(expected_files.keys() - actual_files.keys())
    if missing:
        lines.append("Missing emitted files:")
        for rel_path in missing:
            lines.append(f"- {rel_path.as_posix()}")

    unexpected = sorted(actual_files.keys() - expected_files.keys())
    if unexpected:
        if lines:
            lines.append("")
        lines.append("Unexpected emitted files:")
        for rel_path in unexpected:
            lines.append(f"- {rel_path.as_posix()}")

    common = sorted(expected_files.keys() & actual_files.keys())
    for rel_path in common:
        expected_bytes = expected_files[rel_path].read_bytes()
        actual_bytes = actual_files[rel_path].read_bytes()
        if expected_bytes == actual_bytes:
            continue
        expected_lines = _decode_utf8_lines(expected_bytes)
        actual_lines = _decode_utf8_lines(actual_bytes)
        if expected_lines is None or actual_lines is None:
            if lines:
                lines.append("")
            rel_label = rel_path.as_posix()
            lines.append(
                "Binary file mismatch: "
                f"{rel_label} (expected {len(expected_bytes)} bytes, emitted {len(actual_bytes)} bytes)"
            )
            continue
        if lines:
            lines.append("")
        rel_label = rel_path.as_posix()
        lines.append(
            _build_diff(
                expected_lines,
                actual_lines,
                fromfile=f"expected://{rel_label}",
                tofile=f"emitted://{rel_label}",
            ).rstrip("\n")
        )

    return "\n".join(lines) if lines else None


def _decode_utf8_lines(payload: bytes) -> tuple[str, ...] | None:
    try:
        return tuple(payload.decode("utf-8").splitlines())
    except UnicodeDecodeError:
        return None


def _build_ref_has_flow_artifacts(expected_root: Path) -> bool:
    return any(
        path.name.endswith(".flow.d2") or path.name.endswith(".flow.svg")
        for path in expected_root.rglob("*")
        if path.is_file()
    )


def _build_ref_has_svg_artifacts(expected_root: Path) -> bool:
    return any(
        path.name.endswith(".flow.svg")
        for path in expected_root.rglob("*")
        if path.is_file()
    )
