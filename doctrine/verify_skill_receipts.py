from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import (
    EmitTarget,
    emit_error,
    load_emit_targets,
    path_location,
    resolve_pyproject_path,
)
from doctrine.emit_skill import emit_target_skill
from doctrine.skill_source_receipts import (
    SkillReceiptCheckResult,
    read_receipt_payload,
    receipt_path_for_target,
    verify_actual_output_tree,
    verify_skill_receipt,
)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        config_path = resolve_pyproject_path(args.pyproject)
        targets = load_emit_targets(config_path)
        selected = args.target or sorted(targets)
        results: list[SkillReceiptCheckResult] = []
        for target_name in selected:
            target = targets.get(target_name)
            if target is None:
                raise emit_error(
                    "E501",
                    "Unknown emit target",
                    f"Emit target `{target_name}` is not defined in `pyproject.toml`.",
                    location=path_location(config_path),
                )
            results.append(verify_target_skill_receipt(target))

        for result in results:
            print(f"{result.target_name}: {result.status} - {result.detail}")
        return 0 if all(result.ok for result in results) else 1
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify emitted skill-package trees against SKILL.source.json receipts."
    )
    parser.add_argument(
        "--pyproject",
        help=(
            "Path to the pyproject.toml that defines [tool.doctrine.emit]. "
            "Defaults to the nearest parent pyproject.toml from the current working directory."
        ),
    )
    parser.add_argument(
        "--target",
        action="append",
        help="Configured skill target name. Repeat to verify multiple targets. Defaults to all targets.",
    )
    return parser


def verify_target_skill_receipt(target: EmitTarget) -> SkillReceiptCheckResult:
    actual_receipt_path = receipt_path_for_target(target)
    if not actual_receipt_path.is_file():
        return SkillReceiptCheckResult(
            target.name,
            "missing_receipt",
            f"Missing emitted source receipt: `{actual_receipt_path}`.",
        )
    actual_payload = read_receipt_payload(actual_receipt_path)
    actual_output_result = verify_actual_output_tree(
        target=target,
        receipt_payload=actual_payload,
    )
    if actual_output_result is not None:
        return actual_output_result

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir).resolve()
        emit_target_skill(target, output_dir_override=temp_root, update_lock=False)
        expected_payload = read_receipt_payload(receipt_path_for_target(target, output_dir_override=temp_root))

    return verify_skill_receipt(
        target=target,
        actual_receipt_payload=actual_payload,
        expected_receipt_payload=expected_payload,
    )


if __name__ == "__main__":
    raise SystemExit(main())
